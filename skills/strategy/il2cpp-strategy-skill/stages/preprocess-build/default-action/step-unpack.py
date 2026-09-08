#!/usr/bin/env python3
"""step-02-unpack.py — preprocess action step2: 解包 + 清理 + 资源修复 + namespace 注入。

02-preprocess-build/preprocess action。
委托 common 版 sub-stage-preprocess-build.py 完整执行 10 步流程(解包/清理/修复/manifest/namespace/模板集成/smali→jar/gradle)。
极简 os.environ ctx,带 NAME/TYPE/APK。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class UnpackStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env_init = steps_results.get(
            "preprocess-build.preprocess.env-init", {}
        )
        if env_init.get("skip"):
            return {"rc": 1, "skipped": True, "reason": "env-init failed(无 APK)"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")

        # 委托 common 主脚本(完整 10 步)
        common_script = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py"
        if not common_script.exists():
            return {"rc": 1, "skipped": False, "error": f"缺 common 主脚本: {common_script}"}

        env = dict(os.environ)
        env["NAME"] = name
        env["TYPE"] = type_
        try:
            r = subprocess.run(
                [sys.executable, str(common_script)],
                capture_output=True, text=True, timeout=900, env=env, cwd=str(REPO),
            )
        except subprocess.TimeoutExpired:
            return {"rc": 1, "skipped": False, "error": "common preprocess-build 超时(900s)"}

        return {
            "rc": 0 if r.returncode == 0 else 1,
            "skipped": False,
            "common_script_rc": r.returncode,
            "stdout_tail": r.stdout[-300:],
            "stderr_tail": r.stderr[-300:],
            "output_project_exists": (REPO / "output-projects" / type_ / name).exists(),
        }