#!/usr/bin/env python3
"""step-04-verify-airplane-mode.py — 飞行模式真机验收。

05 verify step 4/6。
委托 device_verify_run(飞行模式下重跑),截图为 screenshot-airplane.png。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

# device_verify_common 在 general-strategy-skill(共享);直接用 REPO 绝对路径避免路径算错
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/lib"))


class VerifyAirplaneModeStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env = steps_results.get("sdk-network-device-verify.default-action.check-environment", {})
        if env.get("skip"):
            return {"rc": 0, "skipped": True, "reason": "env incomplete"}

        # 飞行模式下重跑 device_verify_run
        from device_verify_common import device_verify_run
        rc = device_verify_run(
            stage_id="04",
            label="04-sdk-network-device-verify 飞行模式",
            focus="sdk+network 真机验收经验固化(飞行模式段)",
        )

        # 重命名截图
        stage_dir = Path(os.environ.get("CRACK_DIR", ".")) / "stages" / stage_path("sdk-network-device-verify")
        src = stage_dir / "verify-screenshot.png"
        dst = stage_dir / "screenshot-airplane.png"
        if src.exists() and not dst.exists():
            try:
                src.rename(dst)
            except Exception:
                pass

        return {
            "rc": rc,
            "skipped": False,
            "mode": "airplane",
            "airplane_was_enabled": steps_results.get("sdk-network-device-verify.default-action.switch-airplane-mode", {}).get("airplane_enabled"),
            "screenshot": str(dst.relative_to(REPO)) if dst.exists() else None,
        }