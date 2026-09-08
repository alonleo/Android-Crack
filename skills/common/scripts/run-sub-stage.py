#!/usr/bin/env python3
"""run-sub-stage.py — 总子阶段驱动器。

[FLOWFIX 2026-08-16] 子阶段体系重构后的统一执行入口：
  通过「策略类型 + 子阶段名称」查询对应策略 skill 中的子阶段脚本信息，
  然后执行该子阶段脚本进行处理。

流程：
  1. 解析参数：--type <type> + --name <sub-stage-name>（或 --id <01-20>）
  2. routing.get_script_path(name, type_name) 查脚本路径
     （type-specific 优先，common fallback，主阶段自动路由）
  3. 以子进程执行脚本，透传环境变量与附加参数

用法：
  # 按 name 执行（推荐）
  python3 run-sub-stage.py --type il2cpp --name static-analyze
  python3 run-sub-stage.py --type il2cpp --name preprocess-build

  # 按 id 执行（01-20 子阶段 / M1 等主阶段）
  python3 run-sub-stage.py --type il2cpp --id 01

  # 透传附加参数（脚本自定义参数）
  python3 run-sub-stage.py --type il2cpp --name reward-video-forwarding -- --max 12

  # 列出某 type 的全部子阶段
  python3 run-sub-stage.py --type il2cpp --list
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))

from routing import (  # noqa: E402
    get_script_path,
    get_script_path_by_id,
    id_to_name,
    is_major_stage,
    list_all_stages,
    list_major_stages,
)


def _list_stages(type_name: str) -> int:
    print(f"=== {type_name or 'common'} 子阶段（{len(list_all_stages(type_name))} 个）:")
    for s in list_all_stages(type_name):
        print(f"  {s.get('id','?'):>4}  {s.get('name','?'):35s} {s.get('name_zh','')}")
    print("=== 主阶段（独立于子阶段排序）:")
    for m in list_major_stages():
        print(f"  {m.get('id','?'):>4}  {m.get('name','?'):35s} {m.get('name_zh','')}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="总子阶段驱动器")
    parser.add_argument("--type", default="", help="策略类型（如 il2cpp/android/air）")
    parser.add_argument("--name", default="", help="子阶段名称（如 static-analyze）")
    parser.add_argument("--id", default="", help="子阶段 id（01-20）或主阶段 id（M1/M2/M6/M7）")
    parser.add_argument("--list", action="store_true", help="列出全部子阶段")
    parser.add_argument("--dry-run", action="store_true", help="只显示脚本路径不执行")
    parser.add_argument("extra", nargs="*", help="透传给子阶段脚本的附加参数")
    args = parser.parse_args()

    if args.list:
        return _list_stages(args.type)

    # 确定 name（--name 或 --id 转换）
    name = args.name
    if not name and args.id:
        name = id_to_name(args.id)
        if name == args.id:
            print(f"[ERROR] id '{args.id}' 不在总路由表（子阶段 01-20 / 主阶段 M1 M2 M6 M7）")
            return 1
        print(f"[INFO] id {args.id} → name {name}")

    if not name:
        print("[ERROR] 必须提供 --name 或 --id（或 --list）")
        parser.print_help()
        return 1

    # 查脚本路径（type-specific → common → major）
    script = get_script_path(name, type_name=args.type)
    if not script:
        print(f"[ERROR] 找不到子阶段 '{name}' 的脚本（type={args.type or 'common'}）")
        return 1

    major = is_major_stage(name)
    print(f"[RUN] {'主阶段' if major else '子阶段'} '{name}' (type={args.type or 'common'})")
    print(f"  script: {script}")

    if args.dry_run:
        print("[DRY-RUN] 未执行")
        return 0

    # 执行：透传当前环境（含 $NAME/$TYPE/$APK 等）+ 附加参数
    cmd = [sys.executable, str(script)] + list(args.extra)
    try:
        result = subprocess.run(cmd, env=os.environ.copy())
        return result.returncode
    except KeyboardInterrupt:
        print("\n[ABORT] 用户中断")
        return 130
    except Exception as e:
        print(f"[ERROR] 执行失败: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
