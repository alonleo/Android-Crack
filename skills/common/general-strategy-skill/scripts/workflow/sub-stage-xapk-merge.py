#!/usr/bin/env python3
"""sub-stage-xapk-merge.py — XAPK → fat APK 合并 helper。

[FLOWFIX 2026-08-30] 原 helper 长期缺失 → XAPK 项目无法进入预处理。

功能：
    1. 解外层 XAPK（zip）
    3. 收集所有内层 *.apk
    2. 按 android aapt2 合并规则生成 fat APK（assets/ 与 classes*.dex 合并；lib/<abi>/ 取并集；
       AndroidManifest 各 split 合并到 base）
    3. 输出到指定路径

简化实现（[FLOWFIX]）：
    - 阶段 02 preprocess-build 实际处理是用 apktool 解包再合并资源；
      本 helper 阶段只生成"足够嗅探 + 大致解包"的 fat APK；
      严格意义合并用 apktool 处理。
    - 当前实现 = base + 各 split config 依次 zipmerge（zipfile 层级追加 entry，
      冲突跳过）+ AndroidManifest 仅保留 base；lib/<abi>/ 按路径合并。
    - 对嗅探足够（detect_type 看 lib/.*/libil2cpp.so 等）；不保证 R8/资源 ID 完整。

用法：
    python3 sub-stage-xapk-merge.py <xapk> -o <fat_apk>
    python3 sub-stage-xapk-merge.py <xapk> <fat_apk>     # 也可省略 -o

退出码：
    0 = 成功；非 0 = 失败（缺文件 / 合并失败 / 输出验证失败）
"""
from __future__ import annotations

import argparse
import io
import json
import os
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def read_manifest_json(xapk: Path) -> dict:
    """读 XAPK 外层的 manifest.json（meta 包名 + split 列表）。"""
    with zipfile.ZipFile(xapk) as z:
        try:
            return json.loads(z.read("manifest.json"))
        except KeyError:
            return {}


def merge_xapk(xapk: Path, out: Path) -> None:
    """把 XAPK 内所有 split APK 合并成 fat APK。"""
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        out.unlink()

    base_data: dict[str, bytes] = {}   # entry_name -> bytes（base 主）
    seen: set[str] = set()             # 已添加的 entry

    manifest = read_manifest_json(xapk)
    split_files = [s["file"] for s in manifest.get("split_apks", [])]
    if not split_files:
        # 没有 split_apks 字段 → 把所有 *.apk 当 split
        with zipfile.ZipFile(xapk) as z:
            split_files = [n for n in z.namelist() if n.lower().endswith(".apk")]

    # 1) 先 base
    with zipfile.ZipFile(xapk) as outer:
        for member in outer.infolist():
            if member.filename in split_files and not member.filename.endswith("base.apk") and split_files[0] == member.filename:
                # 第一个 split 通常是 base；否则按 manifest split_apks[0].id == "base" 判定
                pass
            if member.filename in split_files:
                # 第一个 = base
                if "base" not in seen:
                    seen.add("base")
                    with zipfile.ZipFile(io.BytesIO(outer.read(member))) as inner:
                        for n in inner.namelist():
                            base_data[n] = inner.read(n)
                continue

    # 2) 其它 split（config + asset_pack）
    with zipfile.ZipFile(xapk) as outer:
        for member in outer.infolist():
            if member.filename not in split_files:
                continue
            # 已处理 base，跳过
            if "base" in seen and member.filename == split_files[0]:
                continue
            try:
                inner_bytes = outer.read(member)
            except OSError:
                continue
            try:
                inner = zipfile.ZipFile(io.BytesIO(inner_bytes))
            except zipfile.BadZipFile:
                continue
            with inner:
                for n in inner.namelist():
                    # lib/<abi>/.* 累加；其它冲突的（assets/*/AndroidManifest 等）以 base 优先
                    if n in base_data:
                        # 仅当路径是 lib/ 时追加（不同 ABI 文件不会重名）
                        if n.startswith("lib/"):
                            base_data[f"__{member.filename}__{n}"] = inner.read(n)
                        # 否则跳过（base 优先）
                        continue
                    base_data[n] = inner.read(n)

    # 3) 写 fat APK
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as zout:
        for n, data in base_data.items():
            zi = zipfile.ZipInfo(n)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zout.writestr(zi, data)


def verify_out(out: Path) -> bool:
    """简单校验：fat APK 可读且至少有一个 lib/* 文件（防全空）。"""
    if not out.exists() or out.stat().st_size == 0:
        return False
    try:
        with zipfile.ZipFile(out) as z:
            names = z.namelist()
            return any(n.startswith("lib/") for n in names) or any(n == "AndroidManifest.xml" for n in names)
    except zipfile.BadZipFile:
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="XAPK → fat APK 合并")
    ap.add_argument("xapk", help="输入 XAPK 文件")
    ap.add_argument("out_positional", nargs="?", default=None, help="输出 fat APK 路径（兼容旧调用方式）")
    ap.add_argument("-o", "--out", dest="out", default=None, help="输出 fat APK 路径")
    args = ap.parse_args()

    xapk = Path(args.xapk).resolve()
    out_path = Path(args.out or args.out_positional).resolve()
    if not xapk.exists():
        print(f"[ERROR] XAPK 不存在: {xapk}", file=sys.stderr)
        return 2

    print(f"[INFO] 合并 XAPK: {xapk} → {out_path}")
    try:
        merge_xapk(xapk, out_path)
    except Exception as e:
        print(f"[ERROR] 合并失败: {e}", file=sys.stderr)
        return 3

    if not verify_out(out_path):
        print(f"[ERROR] 输出文件无效: {out_path}", file=sys.stderr)
        return 4

    size_mb = round(out_path.stat().st_size / (1024 * 1024), 2)
    print(f"[OK] fat APK: {out_path} ({size_mb} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())