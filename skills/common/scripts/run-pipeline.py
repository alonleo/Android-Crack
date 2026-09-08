#!/usr/bin/env python3
"""
run-pipeline.py — 七大主阶段统一驱动器（默认入口）。

按 WORKFLOW.md §1.1 顺序跑完整 7 大主阶段：sniff → assess → strategy → stages → verify → accept → cleanup。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-pipeline.py <apk-path> [name] [--stages "00,00a,...,21"] [--skip 4,7] [--no-cleanup]

参数：
  <apk-path>           必填，APK 路径
  [name]               可选，项目名（默认从 apk 文件名 CamelCase 归一）
  --stages             可选，逗号分隔的子阶段列表（仅主阶段 4 生效）
  --skip               可选，跳过的主阶段编号（逗号分隔，如 "4,7"）
  --no-cleanup         可选，跳过主阶段 7（cleanup）

主阶段 → 驱动脚本映射：
  1 sniff       → run-major-sniff.py
  2 assess      → run-major-assess.py
  3 strategy    → run-major-strategy.py
  4 stages      → 各 type skill 的 stages/sub_stage-dispatcher.py (register 驱动)
  5 verify      → run-major-verify.py
  6 accept      → run-major-accept.py
  7 cleanup     → run-major-cleanup.py

示例：
  python3 run-pipeline.py apks/Find+the+differences_1.2.0_APKPure.apk FindTheDifferences
  python3 run-pipeline.py apks/Find+the+differences_1.2.0_APKPure.apk FindTheDifferences --no-cleanup
  python3 run-pipeline.py apks/Find+the+differences_1.2.0_APKPure.apk FindTheDifferences --skip 4,7 --stages "11,12,15"
"""
from __future__ import annotations

import sys
import os
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parent

DRIVERS = [
    (1, "sniff",    "run-major-sniff.py"),
    (2, "assess",   "run-major-assess.py"),
    (3, "strategy", "run-major-strategy.py"),
    (4, "stages",   "REGISTER"),  # →各 type skill 的 stages/sub_stage-dispatcher.py
    (5, "verify",   "run-major-verify.py"),
    (6, "accept",   "run-major-accept.py"),
    (7, "cleanup",  "run-major-cleanup.py"),
]


def main():
    parser = argparse.ArgumentParser(
        description="七大主阶段统一驱动器（默认入口）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("apk", help="APK 路径")
    parser.add_argument("name", nargs="?", default="", help="项目名（默认从 APK 文件名 CamelCase 归一）")
    parser.add_argument("--stages", default="", help="主阶段 4 的子阶段列表（逗号分隔）")
    parser.add_argument("--skip", default="", help="跳过的主阶段编号（逗号分隔，如 '4,7'）")
    parser.add_argument("--no-cleanup", action="store_true", help="跳过主阶段 7（cleanup）")
    args = parser.parse_args()

    name = args.name or Path(args.apk).stem

    skip_set = set()
    if args.skip:
        skip_set = {int(s) for s in args.skip.split(",") if s.strip()}
    if args.no_cleanup:
        skip_set.add(7)

    print(f"=" * 60)
    print(f"  APK:  {args.apk}")
    print(f"  Name: {name}")
    print(f"  Skip: {sorted(skip_set) or 'none'}")
    print(f"=" * 60)

    failed = []
    for stage_num, stage_name, driver in DRIVERS:
        if stage_num in skip_set:
            print(f"\n[跳过] 主阶段 {stage_num}/7: {stage_name}")
            continue
        # stage 4 (stages) → 各 type skill 的 register 调度器
        if driver == "REGISTER":
            type_for_stages = os.environ.get("TYPE", "")
            if not type_for_stages:
                print("\n[ERROR] stages 阶段需要 TYPE(未从 status.yaml 解析)", flush=True)
                failed.append(stage_num)
                continue
            driver_path = ROOT.parent.parent / "skills/strategy" / f"{type_for_stages}-strategy-skill" / "stages" / "sub_stage-dispatcher.py"
        else:
            driver_path = ROOT / driver
        if not driver_path.exists():
            print(f"\n[ERROR] 缺驱动脚本: {driver_path}")
            failed.append(stage_num)
            continue
        print(f"\n[主阶段 {stage_num}/7] {stage_name} → {driver_path}", flush=True)
        cmd = ["python3", "-u", str(driver_path)]
        if stage_num == 1:
            cmd += [args.apk, name]
        elif stage_num == 3:
            cmd += [args.apk]
        elif stage_num == 4:
            # register 调度器用环境变量 NAME(不传位置参数); --stage 逐个跑
            stages_arg = [s.strip() for s in (args.stages or "").split(",") if s.strip()]
            if not stages_arg:
                pass  # 无 --stage → 全跑(register 默认全跑)
            elif len(stages_arg) == 1:
                cmd += ["--stage", stages_arg[0]]
            else:
                cmd += ["--stage", stages_arg[0]]  # 多子阶段:下方循环处理剩余
        else:
            cmd += [name]
        # [FLOWFIX] 向子进程传递 NAME/TYPE/CRACK_DIR/OUT 环境变量
        child_env = {**os.environ, "NAME": name}
        if stage_num > 1 and os.environ.get("TYPE"):
            child_env["TYPE"] = os.environ["TYPE"]
        if stage_num > 1 and os.environ.get("CRACK_DIR"):
            child_env["CRACK_DIR"] = os.environ["CRACK_DIR"]
        if stage_num > 1 and os.environ.get("OUT"):
            child_env["OUT"] = os.environ["OUT"]
        rc = subprocess.run(cmd, check=False, env=child_env).returncode
        # stage 4 多子阶段: 剩余 --stage 逐个跑
        if rc == 0 and stage_num == 4:
            stages_arg = [s.strip() for s in (args.stages or "").split(",") if s.strip()]
            for sid in stages_arg[1:]:
                sub_rc = subprocess.run(
                    [sys.executable, "-u", str(driver_path), "--stage", sid],
                    check=False, env=child_env,
                ).returncode
                if sub_rc != 0:
                    print(f"\n[ERROR] 子阶段 {sid} 退出码 {sub_rc}", flush=True)
                    rc = sub_rc
                    break
        if rc != 0:
            print(f"\n[ERROR] 主阶段 {stage_num}/7 ({stage_name}) 退出码 {rc}", flush=True)
            failed.append(stage_num)
        elif stage_num == 1:
            # [FLOWFIX] sniff 成功后用 setup_paths_from_name 把 TYPE/CRACK_DIR/OUT 写入父进程环境
            import yaml
            repo = ROOT.parent.parent
            detected_type = ""
            for type_dir in (repo / "crackings").iterdir():
                typed_status = type_dir / name / "status.yaml"
                if not typed_status.exists():
                    continue
                try:
                    data = yaml.safe_load(typed_status.read_text(encoding="utf-8"))
                    t = (data or {}).get("project", {}).get("type", "")
                    if t:
                        detected_type = t
                        os.environ["TYPE"] = t
                        print(f"[FLOWFIX] 后续主阶段使用 TYPE={t}", flush=True)
                        break
                except Exception:
                    pass
            # 把 NAME/CRACK_DIR/OUT/PATCHED 全部写入父进程环境
            try:
                from routing import get_script_path
                import sys as _sys
                _sys.path.insert(0, str(ROOT / "lib"))
                from common import setup_paths_from_name
                setup_paths_from_name(name, detected_type)
            except Exception as e:
                print(f"[WARN] setup_paths_from_name 失败: {e}")

    print(f"\n" + "=" * 60)
    if failed:
        print(f"  [FAIL] 失败主阶段: {failed}")
        sys.exit(3)
    print(f"  [OK] 七大主阶段全部完成 → {name}")
    print(f"=" * 60)


if __name__ == "__main__":
    main()