#!/usr/bin/env python3
"""
Decrypt JSC assets from a Cocos Creator APK.

Usage:
    python3 decrypt-jsc-assets.py <apk_path> [--key <xxtea_key>] [--out <output_dir>]

Workflow:
    1. Extract all JSC files from APK (assets/**/*.jsc)
    2. For each JSC: XXTEA decrypt → decompress → save .js file
    3. Detect compression type: gzip (cocos2d-jsb/settings/internal/resources) or deflate (main/index)
    4. Output: <out_dir>/<jsc_path>.js

Requirements:
    - xxtea-node (via Node.js): npm install xxtea-node --prefix <tools_dir>
    - Node.js runtime

Cocos Creator JSC format:
    - Encrypted: XXTEA-encrypted (16-byte key, 6 rounds, little-endian)
    - cocos2d-jsb.jsc: encrypted → gzip → JS bytecode
    - main/index.jsc:  encrypted → deflate/zlib → JS source
    - settings/resources/internal JSC: encrypted → gzip → JSON/JS
    - ALL JSC files share the SAME XXTEA key (extracted via Frida)

Frida hook to extract key (attach to running process):
    var base = Module.findBaseAddress("libcocos2djs.so");
    Interceptor.attach(base.add(0x9541cc), {
        onLeave: function(retval) {
            var key = Memory.readCString(retval.toString(), 16);
            console.log("XXTEA Key: " + key);
        }
    });
"""
import argparse
import json
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


def node_decrypt(jsc_data: bytes, key: str, is_deflate: bool = False) -> bytes:
    """Decrypt JSC via Node.js + xxtea-node + zlib."""
    del is_deflate  # unused; compression auto-detected
    # Write JSC to temp file
    with tempfile.NamedTemporaryFile(suffix=".jsc", delete=False) as f:
        f.write(jsc_data)
        jsc_path = f.name

    xxtea_path = XXTEA_MODULE.replace("\\", "/")
    script = """
const fs = require('fs');
const zlib = require('zlib');
const xxtea = require('{}');

const key = Buffer.from('{}', 'utf8');
const data = fs.readFileSync('{}');
const decrypted = xxtea.decrypt(data, key, false);

fs.writeFileSync('/dev/stdout', decrypted);
""".format(xxtea_path, key, jsc_path)
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
        os.unlink(jsc_path)
        os.unlink(script_path)


def detect_compression(decrypted_data: bytes) -> str:
    """Detect decompression type from decrypted data header."""
    if len(decrypted_data) < 2:
        return "none"
    # Gzip magic: 0x1f 0x8b
    if decrypted_data[0] == 0x1f and decrypted_data[1] == 0x8b:
        return "gzip"
    # Zlib magic: 0x78 0x9c / 0x78 0x01 / 0x78 0xda
    if decrypted_data[0] == 0x78 and decrypted_data[1] in (0x9c, 0x01, 0xda):
        return "deflate"
    return "none"


def decompress(decrypted_data: bytes, comp_type: str) -> bytes:
    """Decompress decrypted data."""
    if comp_type == "none":
        return decrypted_data
    if comp_type == "gzip":
        return zlib.decompress(decrypted_data, 16 + zlib.MAX_WBITS)
    else:  # deflate
        return zlib.decompress(decrypted_data, -zlib.MAX_WBITS)


def decrypt_jsc(jsc_data: bytes, key: str, is_deflate: bool = False) -> bytes:
    """Full decrypt pipeline: XXTEA decrypt → decompress."""
    decrypted = node_decrypt(jsc_data, key, is_deflate)
    comp = detect_compression(decrypted)
    if comp == "none":
        return decrypted
    return decompress(decrypted, comp)


def extract_jsc_from_apk(apk_path: str, out_dir: str):
    """Extract all JSC files from APK."""
    jsc_files = {}
    with zipfile.ZipFile(apk_path, "r") as z:
        for name in z.namelist():
            if name.endswith(".jsc"):
                data = z.read(name)
                jsc_files[name] = data
    return jsc_files


def main():
    parser = argparse.ArgumentParser(description="Decrypt JSC assets from Cocos Creator APK")
    parser.add_argument("apk", help="Path to APK file")
    parser.add_argument("--key", default=XXTEA_KEY, help="XXTEA encryption key (16 bytes)")
    parser.add_argument("--out", default="/tmp/jsc_extract", help="Output directory")
    parser.add_argument("--manifest", help="Write file list to JSON")
    args = parser.parse_args()

    ensure_node_modules()

    print(f"[*] Extracting JSC files from {args.apk}")
    jsc_files = extract_jsc_from_apk(args.apk, args.out)
    print(f"[*] Found {len(jsc_files)} JSC files")

    # Heuristic: main/index JSC uses deflate; all others use gzip
    # But we auto-detect via header magic
    results = {}
    for rel_path, data in jsc_files.items():
        # Determine if this is a main/index JSC (Cocos Creator 3.x uses deflate)
        is_deflate = "main/index" in rel_path or "main\\index" in rel_path

        try:
            decrypted = decrypt_jsc(data, args.key, is_deflate=is_deflate)
            # Save with .js extension
            safe_name = rel_path.replace("/", "_").replace("\\", "_")
            out_path = os.path.join(args.out, f"{safe_name}.js")
            os.makedirs(args.out, exist_ok=True)
            with open(out_path, "wb") as f:
                f.write(decrypted)
            results[rel_path] = {"status": "ok", "size": len(decrypted), "out": out_path, "compression": detect_compression(data[:20]) if is_deflate else "gzip"}
            print(f"[+] {rel_path} → {len(decrypted)} bytes ({os.path.basename(out_path)})")
        except Exception as e:
            results[rel_path] = {"status": "error", "error": str(e)}
            print(f"[-] {rel_path}: {e}")

    if args.manifest:
        with open(args.manifest, "w") as f:
            json.dump(results, f, indent=2)
        print(f"[*] Manifest saved to {args.manifest}")

    print(f"\n[*] Done. {sum(1 for v in results.values() if v['status']=='ok')}/{len(results)} decrypted")
    return 0 if all(v["status"] == "ok" for v in results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
