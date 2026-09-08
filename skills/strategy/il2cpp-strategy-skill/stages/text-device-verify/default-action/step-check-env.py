#!/usr/bin/env python3
"""step-01-check-env.py — verify action step1: 验收环境检查。

12-text-device-verify/verify action(通用)。
检查 ANDROID_SERIAL / PATCHED / NAME;缺失则后续 step 走 skip。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class CheckEnvStep(Step):
    def execute(self, steps_results: dict) -> dict:
        serial = os.environ.get("ANDROID_SERIAL", "").strip()
        patched = os.environ.get("PATCHED", "").strip()
        name = os.environ.get("NAME", "").strip()

        checks = {
            "ANDROID_SERIAL_set": bool(serial),
            "PATCHED_exists": bool(patched) and Path(patched).is_file(),
            "NAME_set": bool(name),
        }
        all_ok = all(checks.values())
        skip = not all_ok
        if skip:
            print(
                f"[check-env] 验收环境不全(serial={bool(serial)} patched={bool(patched)} name={bool(name)}),后续 step 跳过",
                file=sys.stderr,
            )
        return {"rc": 0 if all_ok else 1, "skip": skip, "checks": checks}
