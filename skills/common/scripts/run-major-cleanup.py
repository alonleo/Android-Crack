#!/usr/bin/env python3
"""
run-major-cleanup.py — 七大主阶段 7：清理临时空间（cleanup）。

调用 sub-stage-cleanup.py 删除中间产物，保留最终交付物。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-cleanup.py <name> [--keep-raw]

参数：
  <name>         必填，项目名
  --keep-raw     可选，保留 raw/ 中间解包产物（默认删除）

清理策略：
  - 删除：/tmp 中间产物、apktool build 缓存、未提交到 AS 工程的中间 .dex/.smali
  - 保留：crackings/<Name>/patched.apk + findings.md + status.yaml
  - 保留：crackings/<type>/<Name>/project/（最终交付 AS 工程）

示例：
  python3 run-major-cleanup.py FindTheDifferences
  python3 run-major-cleanup.py FindTheDifferences --keep-raw
"""
from __future__ import annotations

import sys
import subprocess
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/common/scripts/lib"))
from routing import get_script_path  # noqa: E402

# 子阶段路由表驱动（按 name 查，替代硬编码）
CLEANUP_SCRIPT = get_script_path("cleanup") or ROOT / "<missing: cleanup>"


def main():
    parser = argparse.ArgumentParser(description="七大主阶段 7：清理临时空间")
    parser.add_argument("name", help="项目名（crackings/<Name>/）")
    parser.add_argument("--keep-raw", action="store_true", help="保留 raw/ 中间解包产物")
    args = parser.parse_args()
    name = args.name
    print(f"[七大主阶段 7/7] 清理临时空间 → {name}")
    if not CLEANUP_SCRIPT.exists():
        print(f"[ERROR] 缺少脚本: {CLEANUP_SCRIPT}")
        sys.exit(2)
    extra = ["--keep-raw"] if args.keep_raw else []
    import os as _os
    env = _os.environ.copy()
    env["NAME"] = name
    type_arg = env.get("TYPE", "").strip()
    crack_dir = ROOT / "crackings" / type_arg / name if type_arg else ROOT / "crackings" / name
    env["CRACK_DIR"] = str(crack_dir)
    env["OUT"] = str(crack_dir / "raw")
    env["PATCHED"] = str(ROOT / "output-projects" / type_arg / name / "patched.apk" if type_arg else ROOT / "output-projects" / name / "patched.apk")
    rc = subprocess.run(
        ["python3", str(CLEANUP_SCRIPT), *extra],
        env=env,
        check=False,
    ).returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()