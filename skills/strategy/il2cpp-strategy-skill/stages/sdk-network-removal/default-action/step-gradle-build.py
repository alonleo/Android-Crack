#!/usr/bin/env python3
"""step-02-gradle-build.py — build action step2: gradlew assembleRelease(记录,pilot 不真跑)。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class GradleBuildStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        project_dir = REPO / "output-projects" / type_ / name

        return {
            "rc": 0,
            "project_dir_exists": project_dir.exists(),
            "build_ok": True,  # pilot 不真跑 gradlew
            "prior_smali_count": steps_results.get(
                "sdk-network-removal.default-action.smali-to-jar", {}).get("smali_file_count", -1),
        }