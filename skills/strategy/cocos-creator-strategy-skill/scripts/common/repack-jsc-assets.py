#!/usr/bin/env python3
"""
Repack JSC assets into a Cocos Creator APK.

Usage:
    python3 repack-jsc-assets.py <apk_path> <modified_js_dir> <output_apk> [--key <xxtea_key>]

Workflow:
    1. For each .js file in <modified_js_dir>, find matching JSC in APK
    2. Encrypt: gzip(level 6) → XXTEA encrypt → JSC
    3. Replace in APK (preserving ALL compression/stored entries exactly)
    4. zipalign → sign

IMPORTANT: This script REPLACES files inside the zip without re-compressing
existing entries. Only modified JSC entries are re-compressed.

Cocos Creator JSC format:
    - cocos2d-jsb / settings / resources / internal: gzip → XXTEA encrypt
    - main/index: zlib.deflate → XXTEA encrypt (NOT gzip!)

JSC encryption (via Node.js + xxtea-node):
    xxtea.encrypt(compressed, key, false)
    - key: 16 bytes
    - rounds: 6 (xxtea-node default)
    - output: raw bytes (no header/magic)

Requirements:
    - xxtea-node (npm install xxtea-node --prefix <cc_reverse_dir>)
    - zipalign + apksigner from Android SDK
    - keystore (generate with keytool or reuse from previous build)
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
import tempfile
import zipfile
import zlib

# ─── Config ───────────────────────────────────────────────────────────────────
XXTEA_KEY = "789713c8-3cd4-47"  # default key; override via --key
NODE_BIN = shutil.which("node") or "node"
CC_REVERSE_DIR = "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/cc-reverse"
XXTEA_MODULE = os.path.join(CC_REVERSE_DIR, "node_modules", "xxtea-node")


def ensure_node_modules():
    """Install xxtea-node if not present."""
    if not os.path.exists(XXTEA_MODULE):
        print(f"[*] Installing xxtea-node to {CC_REVERSE_DIR}")
        subprocess.run(
            ["npm", "install", "xxtea-node", "--prefix", CC_REVERSE_DIR],
            check=True, capture_output=True
        )


def node_encrypt(js_data: bytes, key: str, is_deflate: bool = False) -> bytes:
    """Encrypt JS to JSC via Node.js + xxtea-node."""
    # Compress
    if is_deflate:
        compressed = zlib.compress(js_data, level=6)
    else:
        compressed = zlib.compress(js_data, level=9)

    # Write temp files
    with tempfile.NamedTemporaryFile(suffix=".dat", delete=False, mode="wb") as f:
        f.write(compressed)
        comp_path = f.name

    xxtea_path = XXTEA_MODULE.replace("\\", "/")
    script = """
const fs = require('fs');
const xxtea = require('{}');
const key = Buffer.from('{}', 'utf8');
const data = fs.readFileSync('{}');
const encrypted = xxtea.encrypt(data, key, false);
fs.writeFileSync('/dev/stdout', encrypted);
""".format(xxtea_path, key, comp_path)

    with tempfile.NamedTemporaryFile(suffix=".js", delete=False, mode="w") as f:
        f.write(script)
        script_path = f.name

    try:
        result = subprocess.run(
            [NODE_BIN, script_path],
            capture_output=True, check=True
        )
        return result.stdout
    finally:
        os.unlink(comp_path)
        os.unlink(script_path)


def guess_jsc_name(js_filename: str) -> list:
    """Map a .js filename back to potential JSC names in the APK."""
    # e.g. "assets_assets_main_index.36277.jsc.js" → ["assets/assets/main/index.36277.jsc", ...]
    # Strip extension suffixes
    base = js_filename
    for suffix in (".jsc.js", ".js", ".raw.bin"):
        if base.endswith(suffix):
            base = base[:-len(suffix)]
            break

    candidates = []

    # Reconstruct paths
    parts = base.split("_")
    if len(parts) >= 3 and parts[0] == "assets":
        # Try original JSC path formats
        if parts[1] == "assets" and "main" in base:
            candidates.append("assets/assets/main/index.36277.jsc")
        elif parts[1] == "assets" and "resources" in base:
            candidates.append("assets/assets/resources/index.75451.jsc")
        elif parts[1] == "assets" and "internal" in base:
            candidates.append("assets/assets/internal/index.60559.jsc")
        elif parts[1] == "src" and "settings" in base:
            candidates.append("assets/src/settings.39ef2.jsc")
        elif parts[1] == "src" and "cocos2d" in base:
            candidates.append("assets/src/cocos2d-jsb.82b72.jsc")

    # Also try direct match
    candidates.append(base.replace("_", "/") + ".jsc")
    candidates.append(base.replace("_", "/") + ".jsc")
    return candidates


def repack_jsc(apk_path: str, js_dir: str, output_apk: str, key: str,
               zipalign_bin: str = None, apksigner_bin: str = None,
               keystore_path: str = None, keystore_pass: str = "123456",
               keystore_alias: str = "joint"):
    """Replace JSC files in APK and repack."""

    # Load APK entries
    entries = {}  # name → (info, data)
    with zipfile.ZipFile(apk_path, "r") as zin:
        for info in zin.infolist():
            entries[info.filename] = (info, zin.read(info.filename))

    # Build JSC name → JS data map from js_dir
    js_map = {}  # jsc_name → encrypted_jsc_data
    for fname in os.listdir(js_dir):
        if not fname.endswith(".js"):
            continue
        js_path = os.path.join(js_dir, fname)
        js_data = open(js_path, "rb").read()

        # Determine if this is main/index JSC (Cocos Creator 3.x deflate)
        is_deflate = "main" in fname and "index" in fname

        # Encrypt
        print(f"[*] Encrypting {fname} (deflate={is_deflate})...")
        try:
            encrypted = node_encrypt(js_data, key, is_deflate=is_deflate)
        except Exception as e:
            print(f"[-] Encryption failed for {fname}: {e}")
            continue

        # Find matching JSC name
        candidates = guess_jsc_name(fname)
        matched = None
        for c in candidates:
            if c in entries:
                matched = c
                break

        if matched:
            js_map[matched] = encrypted
            print(f"[+] {fname} → {matched} ({len(encrypted)} bytes)")
        else:
            print(f"[!] No matching JSC in APK for {fname}, candidates: {candidates}")

    # Write new APK, replacing only modified JSC entries
    tmp_path = output_apk + ".tmp"
    with zipfile.ZipFile(apk_path, "r") as zin:
        with zipfile.ZipFile(tmp_path, "w", compression=zipfile.ZIP_STORED) as zout:
            for info in zin.infolist():
                fname = info.filename
                if fname in js_map:
                    # Replace with encrypted data
                    new_info = zipfile.ZipInfo(fname)
                    new_info.compress_type = zipfile.ZIP_STORED
                    new_info.external_attr = info.external_attr
                    new_info.date_time = info.date_time
                    new_info.CRC = zlib.crc32(js_map[fname]) & 0xffffffff
                    new_info.file_size = len(js_map[fname])
                    new_info.compress_size = len(js_map[fname])
                    zout.writestr(new_info, js_map[fname])
                    print(f"    [*] Replaced {fname}")
                else:
                    # Copy as-is (read data first)
                    data = zin.read(info)
                    new_info = zipfile.ZipInfo(fname)
                    new_info.compress_type = info.compress_type
                    new_info.external_attr = info.external_attr
                    new_info.date_time = info.date_time
                    new_info.CRC = info.CRC
                    new_info.file_size = info.file_size
                    new_info.compress_size = info.compress_size
                    zout.writestr(new_info, data)

    # Move to final path
    shutil.move(tmp_path, output_apk)
    print(f"[*] Written {output_apk}")

    # zipalign
    if zipalign_bin:
        aligned = output_apk + ".aligned"
        r = subprocess.run(
            [zipalign_bin, "-f", "4", output_apk, aligned],
            capture_output=True
        )
        if r.returncode == 0:
            shutil.move(aligned, output_apk)
            print("[*] zipalign done")
        else:
            print(f"[!] zipalign failed: {r.stderr.decode()}")

    # sign
    if apksigner_bin and keystore_path and os.path.exists(keystore_path):
        signed = output_apk + ".signed"
        r = subprocess.run(
            [apksigner_bin, "sign",
             "--ks", keystore_path,
             "--ks-key-alias", keystore_alias,
             "--ks-pass", f"pass:{keystore_pass}",
             "--key-pass", f"pass:{keystore_pass}",
             "--v1-signing-enabled", "true",
             "--v2-signing-enabled", "true",
             "--out", signed,
             output_apk],
            capture_output=True
        )
        if r.returncode == 0:
            shutil.move(signed, output_apk)
            print("[*] Signed OK")
        else:
            print(f"[!] apksigner failed: {r.stderr.decode()}")

    return 0


def main():
    p = argparse.ArgumentParser(description="Repack JSC assets into Cocos Creator APK")
    p.add_argument("apk", help="Source APK")
    p.add_argument("js_dir", help="Directory with decrypted .js files")
    p.add_argument("output", help="Output APK path")
    p.add_argument("--key", default=XXTEA_KEY)
    p.add_argument("--zipalign", default="/home/leo/文档/android-crack/tools/environments/android-sdk/build-tools/34.0.0/zipalign")
    p.add_argument("--apksigner", default="/home/leo/文档/android-crack/tools/environments/android-sdk/build-tools/34.0.0/apksigner")
    p.add_argument("--keystore", default="/home/leo/文档/android-crack/crackings/cocos-creator/KingOfTank/keystore")
    p.add_argument("--ks-pass", default="123456")
    p.add_argument("--ks-alias", default="joint")
    args = p.parse_args()

    ensure_node_modules()
    return repack_jsc(
        args.apk, args.js_dir, args.output, args.key,
        zipalign_bin=args.zipalign if os.path.exists(args.zipalign) else None,
        apksigner_bin=args.apksigner if os.path.exists(args.apksigner) else None,
        keystore_path=args.keystore if os.path.exists(args.keystore) else None,
        keystore_pass=args.ks_pass,
        keystore_alias=args.ks_alias
    )


if __name__ == "__main__":
    sys.exit(main())
