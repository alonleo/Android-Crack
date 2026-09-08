#!/usr/bin/env python3
"""step-02-run-verify.py — verify action step2: 真机验收(单段)。

14-image-device-verify/verify action(通用)。
委托 device_verify_run(安装→启动→存活→截图→无FATAL)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step

# device_verify_common 路径(general-strategy-skill)
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/lib"))


class RunVerifyStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env = steps_results.get("image-device-verify.default-action.check-env", {})
        if env.get("skip"):
            return {"rc": 0, "skipped": True, "reason": "env incomplete"}

        from device_verify_common import device_verify_run
        rc = device_verify_run(
            stage_id="14",
            label="15 真机验收(图片)",
            focus="image 真机验收经验固化",
        )
        return {"rc": rc, "skipped": False, "verify_rc": rc}
