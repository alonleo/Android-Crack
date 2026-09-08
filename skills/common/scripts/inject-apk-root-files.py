#!/usr/bin/env python3
"""inject-apk-root-files.py — 把根目录文件注入 APK 并重新签名。

背景: 部分 SDK（如 AppsFlyer）用 `Class.getResourceAsStream("/com/appsflyer/internal/a-")`
从 **APK 根目录**（非 assets）读取混淆配置。重打包 APK 丢失这些文件 →
`AFa1vSDK.<clinit>` 读文件 NPE 崩溃。需要把 `extra-root/` 下的文件注入 APK 根
（来源 FormulaCarStuntCarGames 2026-08-06）。

用法:
  python3 inject-apk-root-files.py <apk> --files <src_dir> \
      [--keystore my.keystore.jks --alias jy --pass Ab123145]

依赖:
  - zip（追加条目，保留目录结构）
  - apksigner（重新签名；v1+v2+v3）
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

# 默认 keystore 与 env 提供的一致
KEYSTORE = ROOT / "tools" / "scripts" / "template-files" / "my.keystore.jks"
KEY_ALIAS = "jy"
KEY_PASS = "Ab123145"


def _find_apksigner() -> Path:
    for p in ROOT.glob("tools/environments/android-sdk/build-tools/*/apksigner"):
        return p
    sys.exit("[ERROR] 找不到 apksigner")


def inject(apk: Path, files_dir: Path, keystore: Path, alias: str, password: str) -> bool:
    if not apk.is_file():
        print(f"[ERROR] APK 不存在: {apk}")
        return False
    if not files_dir.is_dir():
        print(f"[WARN] 注入源目录不存在（跳过）: {files_dir}")
        return True
    apksigner = _find_apksigner()

    with tempfile.TemporaryDirectory(prefix="apkroot_") as tmp:
        tmp = Path(tmp)
        staging = tmp / "staging"
        staging.mkdir()
        # 解压原 APK
        subprocess.run(["unzip", "-q", str(apk), "-d", str(staging)], check=True)
        # 复制根文件
        for item in files_dir.rglob("*"):
            if item.is_file():
                rel = item.relative_to(files_dir)
                dst = staging / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(item, dst)
                print(f"[OK] 注入: {rel}")
        # 重新压缩
        new_apk = tmp / apk.name
        subprocess.run(
            ["bash", "-c", f"cd {staging} && zip -qr {new_apk} ."],
            check=True,
        )
        # 删除原签名
        old_signed = tmp / "old_signed.apk"
        old_signed.write_bytes(apk.read_bytes())
        # 签名
        sign_cmd = [
            str(apksigner), "sign",
            "--ks", str(keystore),
            "--ks-key-alias", alias,
            "--ks-pass", f"pass:{password}",
            "--key-pass", f"pass:{password}",
            "--out", str(new_apk),
            str(new_apk),
        ]
        r = subprocess.run(sign_cmd, capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[ERROR] 签名失败:\n{r.stderr[:500]}")
            return False
        # 用新 APK 替换
        shutil.move(str(new_apk), str(apk))
        print(f"[OK] 已注入根文件并重新签名: {apk}")
        return True
    return False


def main() -> int:
    parser = argparse.ArgumentParser(description="注入 APK 根目录文件并重新签名")
    parser.add_argument("apk", help="目标 APK")
    parser.add_argument("--files", default="", help="根文件源目录（默认 output-projects 对应 app/src/main/extra-root）")
    parser.add_argument("--keystore", default=str(KEYSTORE))
    parser.add_argument("--alias", default=KEY_ALIAS)
    parser.add_argument("--pass", default=KEY_PASS)
    args = parser.parse_args()

    apk = Path(args.apk)
    files_dir = Path(args.files) if args.files else apk.parent.parent / "app" / "src" / "main" / "extra-root"
    return 0 if inject(apk, files_dir, Path(args.keystore), args.alias, getattr(args, "pass")) else 1


if __name__ == "__main__":
    sys.exit(main())
