#!/usr/bin/env python3
"""step-01-scan-entries.py — analyze action step1: jadx 反编译 + SDK 扫描 + 入口定位。

01-static-analyze/analyze action。
委托 common sub-stage-static-analyze.py(env NAME/TYPE)完成静态分析。
极简 os.environ ctx。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step, resolve_apk


class ScanEntriesStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        # 解析 APK(若未设,从 apks/ 按 name 找)
        apk = resolve_apk(name, os.environ.get("APK", ""))
        if apk is None:
            return {"rc": 1, "skipped": False, "error": "缺 APK 且无法从 apks/ 解析"}
        os.environ["APK"] = str(apk)

        main_script = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py"
        if not main_script.exists():
            return {"rc": 1, "skipped": False, "error": f"缺主脚本: {main_script}"}

        env = dict(os.environ)
        env["NAME"] = name
        env["TYPE"] = type_
        try:
            r = subprocess.run(
                [sys.executable, str(main_script)],
                capture_output=True, text=True, timeout=900, env=env, cwd=str(REPO),
            )
        except subprocess.TimeoutExpired:
            return {"rc": 1, "skipped": False, "error": "static-analyze 超时(900s)"}

        return {
            "rc": 0 if r.returncode == 0 else 1,
            "skipped": False,
            "main_script_rc": r.returncode,
            "findings_exists": (REPO / "crackings" / type_ / name / "findings.md").exists(),
            "stdout_tail": r.stdout[-200:],
            "stderr_tail": r.stderr[-200:],
        }