#!/usr/bin/env python3
"""
run-major-strategy.py — 七大主阶段 3：决定策略（strategy routing）。

调用 strategy-config.py 嗅探 + 列阶段序列 + 路由到对应 type-strategy-skill。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-strategy.py <apk-path>

参数：
  <apk-path>     必填，APK 路径

输出：
  - 终端打印：type / stages / tools / skill / mandatory
  - 用于 crack.py 大阶段 4 自动 dispatch 子阶段脚本

示例：
  python3 run-major-strategy.py apks/Find+the+differences_1.2.0_APKPure.apk
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STRATEGY_DIR = ROOT / "skills/common/scripts/strategy"  # [FLOWFIX 2026-09-02] ROOT 路径错误（parents[2] 指向 skills/），实际策略目录在 skills/common/scripts/strategy/；建议后续改 ROOT=parents[3]


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    apk = sys.argv[1]
    print(f"[七大主阶段 3/7] 决定策略 → {apk}", flush=True)
    cfg_py = STRATEGY_DIR / "strategy-config.py"
    if not cfg_py.exists():
        print(f"[ERROR] 缺少脚本: {cfg_py}", flush=True)
        sys.exit(2)
    for cmd in ["detect", "stages", "tools", "mandatory", "notes"]:
        print(f"\n--- {cmd} ---", flush=True)
        subprocess.run(
            ["python3", "-u", str(cfg_py), cmd, apk],
            check=False,
        )


if __name__ == "__main__":
    main()