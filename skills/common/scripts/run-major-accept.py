#!/usr/bin/env python3
"""
run-major-accept.py — 七大主阶段 6：交付前验收（delivery acceptance）。

调用 sub-stage-final-check.py 跑 6 条硬指标验收（OBJECTIVES.md §1）。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-accept.py <name>

参数：
  <name>         必填，项目名

6 条硬指标（OBJECTIVES.md §1）：
  1. 可重建：patched.apk 与 app-release.apk md5 一致
  2. 可二次开发：AS 工程完整（build.gradle + AndroidManifest + Java + Assets + res + jniLibs + libs）
  3. 特征库可追溯：findings.md 记录所有 SDK/.so → sdks.md / native-libs.md
  4. 签名一致：v1+v2+v3 三签齐全 + 本工作区 keystore
  5. 真机可运行：飞行模式 + Activity RESUMED + 渲染帧推进 + 无 FATAL
  6. 进度记录：status.yaml phase = deliver

示例：
  python3 run-major-accept.py FindTheDifferences
"""
from __future__ import annotations

import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "skills/common/scripts/lib"))
from routing import get_script_path  # noqa: E402

# 子阶段路由表驱动（按 name 查，替代硬编码）
FINAL_CHECK_SCRIPT = get_script_path("final-check") or ROOT / "<missing: final-check>"


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    name = sys.argv[1]
    print(f"[七大主阶段 6/7] 交付前验收 → {name}")
    if not FINAL_CHECK_SCRIPT.exists():
        print(f"[ERROR] 缺少脚本: {FINAL_CHECK_SCRIPT}")
        sys.exit(2)
    # 通过环境变量传 NAME，避免 sub-stage-final-check 把 name 当 APK 路径解析
    import os
    env = os.environ.copy()
    env["NAME"] = name
    type_arg = env.get("TYPE", "").strip()
    crack_dir = ROOT / "crackings" / type_arg / name if type_arg else ROOT / "crackings" / name
    out_dir = crack_dir / "raw"
    env["CRACK_DIR"] = str(crack_dir)
    env["OUT"] = str(out_dir)
    env["PATCHED"] = str(ROOT / "output-projects" / type_arg / name / "patched.apk" if type_arg else ROOT / "output-projects" / name / "patched.apk")
    rc = subprocess.run(
        ["python3", str(FINAL_CHECK_SCRIPT)],
        env=env,
        check=False,
    ).returncode
    sys.exit(rc)


if __name__ == "__main__":
    main()