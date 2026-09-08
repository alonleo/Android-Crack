#!/usr/bin/env python3
"""step-02-check-callchain.py — forward action step2: 校验调用链(MainActivity→SDKUtils)。

05-revenue-forwarding/forward action。
校验 SDKUtils.showRewardVideo/processPurchase 存在于 MainActivity 调用链。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class CheckCallchainStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "crackings" / type_ / name / "project"

        # 校验 MainActivity 调 SDKUtils.showRewardVideo
        main_activity = out_proj / "app/src/main/java/com/android/boot/MainActivity.java"
        callchain_ok = False
        if main_activity.exists():
            text = main_activity.read_text(encoding="utf-8", errors="ignore")
            callchain_ok = "showRewardVideo" in text or "processPurchase" in text

        return {
            "rc": 0 if callchain_ok else 1,
            "skipped": False,
            "main_activity_exists": main_activity.exists(),
            "callchain_ok": callchain_ok,
            "call_targets": [t for t in ("showRewardVideo", "processPurchase")
                             if main_activity.exists() and t in main_activity.read_text(encoding="utf-8", errors="ignore")],
        }