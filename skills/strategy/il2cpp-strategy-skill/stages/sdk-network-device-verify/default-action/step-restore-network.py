#!/usr/bin/env python3
"""step-05-restore-network.py — 恢复网络(关闭飞行模式)。

05 verify step 5/6。
无论成功失败都恢复,避免设备陷入离线状态污染后续 stage。
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


class RestoreNetworkStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env = steps_results.get("sdk-network-device-verify.default-action.check-environment", {})
        if env.get("skip"):
            return {"rc": 0, "skipped": True, "reason": "env incomplete"}

        # 关飞行模式(必须:即使前面 step 失败,也要恢复,否则设备离线)
        r1 = _adb("shell", "settings", "put", "global", "airplane_mode_on", "0", timeout=15)
        r2 = _adb("shell", "am", "broadcast", "-a", "android.intent.action.AIRPLANE_MODE",
                  "--ez", "state", "false", timeout=15)
        time.sleep(2)

        r3 = _adb("shell", "settings", "get", "global", "airplane_mode_on", timeout=10)
        disabled = r3.stdout.strip() == "0"

        return {
            "rc": 0 if disabled else 1,
            "skipped": False,
            "airplane_disabled": disabled,
        }