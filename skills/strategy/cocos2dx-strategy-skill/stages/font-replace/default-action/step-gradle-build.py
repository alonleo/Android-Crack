#!/usr/bin/env python3
"""cocos2dx font-replace step 2 gradle-build: 调用脚本.

cocos2dx 子阶段 font-replace default-action。
调用该 type 该子阶段的脚本: skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py。
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class GradleBuildStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "cocos2dx").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        script = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py"
        if not script.exists():
            return {"rc": 1, "skipped": False, "error": f"缺脚本: {script}"}

        env = dict(os.environ)
        env["NAME"] = name
        env["TYPE"] = type_
        try:
            r = subprocess.run(
                [sys.executable, str(script)],
                capture_output=True, text=True, timeout=900, env=env, cwd=str(REPO),
            )
        except subprocess.TimeoutExpired:
            return {"rc": 1, "skipped": False, "error": "script 超时"}

        return {
            "rc": 0 if r.returncode == 0 else 1,
            "skipped": False,
            "script": "skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py",
            "script_rc": r.returncode,
            "stdout_tail": r.stdout[-200:],
            "stderr_tail": r.stderr[-200:],
        }
