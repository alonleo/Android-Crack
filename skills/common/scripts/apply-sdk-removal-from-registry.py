#!/usr/bin/env python3
"""apply-sdk-removal-from-registry.py — 按 third-party-sdk-removal-registry.yaml
对 crackings/<type>/<Name>/project/ 工程做 SDK 移除（阶段 04 子动作）。

替代缺失的 sub-stage-sdk-network-removal.py 中 SDK 移除段
（其依赖的 load_sdk_removal_registry.py + common 脚本都不存在）。

动作清单（按清单 YAML 段）:
1. smali_exclude_prefixes → 删除 app/src/main/smali/<prefix>/*
2. so_early_kill + so_keyword_contains → 删除 app/src/main/jniLibs/<abi>/<lib>.so
3. raw_apk_drop_entries → 删除 app/src/main/<entry> (如 lib/arm64-v8a/libcrashlytics.so)
4. engine_so_keep → 白名单（保留），仅校验 libil2cpp.so/libunity.so/libmain.so 仍存在
5. manifest_drop_exact / manifest_drop_keyword_contains → 标记 AndroidManifest 中匹配组件，
   Agent 手工 patch manifest（不在本脚本范围，避免误删引擎 launcher）

注意: 此脚本**仅删文件**，不重写 manifest/smali 内容。
smali→jar 重建需另跑 dex-dex2jar-classpath.py。

用法:
    python3 skills/common/scripts/apply-sdk-removal-from-registry.py \
        --name NinjaArashi --type il2cpp
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[3]
DEFAULT_REGISTRY = REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "references/third-party-sdk-removal-registry.yaml"


def _load_registry(path: Path) -> dict:
    if not path.is_file():
        sys.exit(f"[ERR] 清单不存在: {path}")
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _delete(path: Path, dry_run: bool, verbose: bool) -> int:
    if not path.exists():
        return 0
    if dry_run:
        print(f"[dry-run] would delete: {path}")
        return 1  # counted as hit
    if verbose:
        print(f"[delete] {path}")
    if path.is_dir():
        shutil.rmtree(path, ignore_errors=True)
    else:
        path.unlink()
    return 1


def main() -> int:
    p = argparse.ArgumentParser(description="按 SDK 移除清单对 output-projects 工程做删除")
    p.add_argument("--name", required=True)
    p.add_argument("--type", default="il2cpp")
    p.add_argument("--out", help="output-projects 根（默认 crackings/<type>/<Name>/project）")
    p.add_argument("--registry", default=str(DEFAULT_REGISTRY))
    p.add_argument("--dry-run", action="store_true", help="只列出待删，不实际删除")
    args = p.parse_args()

    out_dir = Path(args.out) if args.out else REPO / "crackings" / args.type / args.name / "project"
    if not out_dir.is_dir():
        sys.exit(f"[ERR] output dir 不存在: {out_dir}")
    src_main = out_dir / "app" / "src" / "main"
    smali_dir = src_main / "smali"
    if not smali_dir.is_dir():
        sys.exit(f"[ERR] smali dir 不存在: {smali_dir}")

    reg = _load_registry(Path(args.registry))

    hits = 0

    # 1. smali_exclude_prefixes
    print("\n=== smali_exclude_prefixes ===")
    for prefix in reg.get("smali_exclude_prefixes", []):
        target = smali_dir / prefix
        if _delete(target, args.dry_run, verbose=True):
            hits += 1

    # 2. so_early_kill + so_keyword_contains (跨 ABI 删除)
    print("\n=== so (early_kill + keyword_contains) ===")
    jni_libs = src_main / "jniLibs"
    so_names: set[str] = set()
    for entry in reg.get("so_early_kill", []):
        name = entry if isinstance(entry, str) else entry.get("name", "")
        so_names.add(name)
    for name in reg.get("so_keyword_contains", []):
        # 模糊匹配所有变种（lib<keyword>*.so）
        so_names.add(name)  # 完整路径
    for ab_dir in jni_libs.iterdir() if jni_libs.is_dir() else []:
        if not ab_dir.is_dir():
            continue
        for lib in ab_dir.glob("*.so"):
            lib_name = lib.name
            lib_key = f"lib/{ab_dir.name}/{lib_name}"
            if lib_key in so_names or lib_name in so_names:
                if _delete(lib, args.dry_run, verbose=True):
                    hits += 1
                continue
            for kw in so_names:
                if kw in lib_name:
                    if _delete(lib, args.dry_run, verbose=True):
                        hits += 1
                    break

    # 3. raw_apk_drop_entries (相对 src/main 删)
    print("\n=== raw_apk_drop_entries ===")
    for entry in reg.get("raw_apk_drop_entries", []):
        target = src_main / entry
        if _delete(target, args.dry_run, verbose=True):
            hits += 1

    # 4. engine_so_keep 白名单校验（保留，不删）
    print("\n=== engine_so_keep (校验保留) ===")
    keep_names = reg.get("engine_so_keep", [])
    arm_dir = jni_libs / "arm64-v8a" if jni_libs.is_dir() else None
    if arm_dir and arm_dir.is_dir():
        for keep in keep_names:
            if not (arm_dir / keep).is_file():
                print(f"[WARN] engine_so_keep 缺失: {arm_dir / keep}")

    print(f"\n[{'DRY-RUN ' if args.dry_run else ''}DONE] 共命中 {hits} 个路径")
    return 0


if __name__ == "__main__":
    sys.exit(main())