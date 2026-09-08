#!/usr/bin/env python3
"""merge-multidex-into-apk.py — 把 apktool 构建的多 dex 合并进 gradle 构建的 APK。

背景：gradle 构建的 APK 只含主 dex（Java 类），Unity 类在 apktool 构建的多 dex 中。
本脚本把 apktool 构建 APK 的 15 个 classes*.dex 合并进 gradle APK。

用法：
  python3 merge-multidex-into-apk.py --gradle-apk <path> --apktool-apk <path> --out <path>
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import zipfile
from pathlib import Path


def merge(gradle_apk: Path, apktool_apk: Path, out_apk: Path) -> int:
    """合并多 dex。"""
    tmp_dir = out_apk.parent / "_dex_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)

    # 1. 从 apktool APK 提取 15 个 dex
    dex_files = []
    with zipfile.ZipFile(apktool_apk) as zf:
        for name in sorted(zf.namelist()):
            if name.startswith("classes") and name.endswith(".dex") and "audience" not in name:
                target = tmp_dir / os.path.basename(name)
                with zf.open(name) as src, target.open("wb") as dst:
                    shutil.copyfileobj(src, dst)
                dex_files.append(target)

    # 2. 合并进 gradle APK
    with zipfile.ZipFile(gradle_apk) as zin, zipfile.ZipFile(out_apk, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            # 跳过 gradle 的 classes2+ dex（保留 classes.dex 主 dex）
            if item.filename.startswith("classes") and item.filename.endswith(".dex") and item.filename != "classes.dex":
                continue
            # 跳过签名
            if item.filename.startswith("META-INF/") and (
                item.filename.endswith(".SF") or item.filename.endswith(".RSA")
                or item.filename.endswith(".MF") or "MANIFEST" in item.filename):
                continue
            zout.writestr(item, zin.read(item.filename))

        # 3. 加入 apktool 的 dex（含 apktool 的 classes.dex 作为 classes16+，避免与 gradle 主 dex 冲突）
        idx = 2
        # 先数 gradle APK 已有的 dex 数（classes.dex 除外），后续编号避开
        existing_max = 1
        for item in zin.infolist():
            m = re.match(r'classes(\d+)\.dex$', item.filename)
            if m and int(m.group(1)) > existing_max:
                existing_max = int(m.group(1))
        idx = existing_max + 1
        for df in sorted(dex_files):
            zout.write(df, f"classes{idx}.dex")
            print(f"加入 {df.name} → classes{idx}.dex")
            idx += 1

    # 清理
    shutil.rmtree(tmp_dir, ignore_errors=True)
    print(f"合并完成: {out_apk}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gradle-apk", required=True)
    parser.add_argument("--apktool-apk", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    return merge(Path(args.gradle_apk), Path(args.apktool_apk), Path(args.out))


if __name__ == "__main__":
    raise SystemExit(main())