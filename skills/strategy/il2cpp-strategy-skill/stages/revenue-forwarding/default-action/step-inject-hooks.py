#!/usr/bin/env python3
"""step-01-inject-hooks.py — forward action step1: 校验 native hook 注入。

05-revenue-forwarding/forward action。
校验 native-lib.cpp 注入(Hooked_* + A64HookFunction)。已在 scan-revenue(委托主脚本)完成。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class InjectHooksStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        native_lib = REPO / "crackings" / type_ / name / "project/app/src/main/cpp/native-lib.cpp"

        hooks_found = []
        if native_lib.exists():
            text = native_lib.read_text(encoding="utf-8", errors="ignore")
            if "A64HookFunction" in text:
                hooks_found.append("A64HookFunction")
            if "showRewardVideo" in text:
                hooks_found.append("showRewardVideo")
            if "processPurchase" in text:
                hooks_found.append("processPurchase")

        return {
            "rc": 0 if native_lib.exists() else 1,
            "skipped": False,
            "native_lib": str(native_lib.relative_to(REPO)) if native_lib.exists() else None,
            "hooks_found": hooks_found,
        }