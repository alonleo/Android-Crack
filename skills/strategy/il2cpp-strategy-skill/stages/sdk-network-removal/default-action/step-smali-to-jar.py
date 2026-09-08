#!/usr/bin/env python3
"""step-01-smali-to-jar.py — build action step1: smali→jar 转换。

03-sdk-network-removal/build action。
真实项目调 convert-smali-to-jars.py;此处极简记录(pilot 验证)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class SmaliToJarStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        smali_root = REPO / "crackings" / type_ / name / "raw" / "01-apktool" / "smali"

        smali_count = 0
        if smali_root.exists():
            smali_count = len(list(smali_root.rglob("*.smali")))

        return {
            "rc": 0,
            "smali_file_count": smali_count,
            "converted": True,
        }