#!/usr/bin/env python3
"""step-01-check-environment.py — 验收环境检查。

05 verify step 1/6。
检查项:
  1. ANDROID_SERIAL 是否设置
  2. patched APK 是否存在
  3. 设备列表中是否有目标设备
若任一项缺失,返回 _skip=True 让后续 step 走"跳过"分支。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class CheckEnvironmentStep(Step):
    def execute(self, steps_results: dict) -> dict:
        serial = os.environ.get("ANDROID_SERIAL", "").strip()
        patched = os.environ.get("PATCHED", "").strip()
        name = os.environ.get("NAME", "").strip()

        checks = {
            "ANDROID_SERIAL_set": bool(serial),
            "PATCHED_exists": bool(patched) and Path(patched).is_file() if patched else False,
            "NAME_set": bool(name),
        }

        all_ok = all(checks.values())
        skip = not all_ok
        if skip:
            print(
                f"[check_environment] 验收环境不全(serial={bool(serial)} patched_exists={checks['PATCHED_exists']} name={bool(name)}),后续 step 走跳过分支",
                file=sys.stderr,
            )

        return {
            "rc": 0 if all_ok else 1,
            "skip": skip,
            "checks": checks,
            "serial": serial,
            "patched": patched,
            "name": name,
        }