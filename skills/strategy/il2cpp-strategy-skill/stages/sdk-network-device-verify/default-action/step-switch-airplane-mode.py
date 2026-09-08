#!/usr/bin/env python3
"""step-03-switch-airplane-mode.py — 切换到飞行模式。

05 verify step 3/6。
通过 adb shell settings put global airplane_mode_on 1 + 广播 Intent。
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


def _adb(*args, timeout=30):
    cmd = [os.environ.get("ADB", "adb")]
    serial = os.environ.get("ANDROID_SERIAL", "").strip()
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


class SwitchAirplaneModeStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env = steps_results.get("sdk-network-device-verify.default-action.check-environment", {})
        if env.get("skip"):
            return {"rc": 0, "skipped": True, "reason": "env incomplete"}

        # 1. 设置 airplane_mode_on=1
        r1 = _adb("shell", "settings", "put", "global", "airplane_mode_on", "1", timeout=15)
        # 2. 广播 ACTION_AIRPLANE_MODE(Android 14+ 必须广播触发)
        r2 = _adb("shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE",
                  "--ez", "state", "true", timeout=15)
        # 3. 等待生效
        time.sleep(3)

        # 验证当前状态
        r3 = _adb("shell", "settings", "get", "global", "airplane_mode_on", timeout=10)
        enabled = r3.stdout.strip() == "1"

        return {
            "rc": 0 if enabled else 1,
            "skipped": False,
            "airplane_enabled": enabled,
            "settings_rc": r1.returncode,
            "broadcast_rc": r2.returncode,
        }