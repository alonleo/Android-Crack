#!/usr/bin/env python3
"""
run-major-assess.py — 七大主阶段 2：难度评估（assess）。

调用 sub-stage-assess.py 跑 6 维度加权评分，输出 difficulty.json + assessment.md。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-assess.py <name>

参数：
  <name>         必填，项目名（crackings/<Name>/）

输出：
  - crackings/<Name>/difficulty.json（6 维度评分 + grade + 推荐流水线）
  - crackings/<Name>/raw/assessment.md（人类可读明细）

示例：
  python3 run-major-assess.py FindTheDifferences
"""
from __future__ import annotations

import sys
import os
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/scripts/lib"))
from routing import get_script_path  # noqa: E402
from common import log_warn  # noqa: E402

# 子阶段路由表驱动（按 name 查，替代硬编码）
ASSESS_SCRIPT = get_script_path("assess") or ROOT / "<missing: assess>"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    print(f"[七大主阶段 2/7] 难度评估 → {name}")
    if not ASSESS_SCRIPT.exists():
        print(f"[ERROR] 缺少脚本: {ASSESS_SCRIPT}")
        sys.exit(2)
    env = os.environ.copy()
    env["NAME"] = name
    # 评估脚本依赖 NAME 环境变量；传 name 作为 argv 会被误当成 APK 路径。
    # [FLOWFIX 2026-08-23] status.yaml 是 YAML 格式（`type: il2cpp`），旧正则
    # 找 `key="value"` 永远匹配不到；改为正则匹配 yaml 缩进 + 冒号。
    type_found = False
    for type_dir in (ROOT / "crackings").iterdir():
        if not type_dir.is_dir():
            continue
        status = type_dir / name / "status.yaml"
        if not status.is_file():
            continue
        match = re.search(r"^\s*type\s*:\s*([A-Za-z0-9_\-]+)", status.read_text(), re.MULTILINE)
        if match:
            env["TYPE"] = match.group(1).strip()
            type_found = True
            break
    # CLI --type 参数覆盖 status.yaml 探测
    if "--type" in sys.argv:
        idx = sys.argv.index("--type")
        if idx + 1 < len(sys.argv):
            env["TYPE"] = sys.argv[idx + 1]
            type_found = True
    if not type_found:
        log_warn(f"[WARN] 未找到 crackings/<type>/{name}/status.yaml；TYPE 未注入，"
                 f"assess 会写到 crackings/{name}/（违反 AGENTS.md §3）。")
    rc = subprocess.run(["python3", str(ASSESS_SCRIPT)], env=env, check=False).returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()