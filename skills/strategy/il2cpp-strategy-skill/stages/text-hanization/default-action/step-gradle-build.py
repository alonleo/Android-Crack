#!/usr/bin/env python3
"""step-02-gradle-build.py — build action step2: 校验 Gradle 构建产物。

通用 build action。
校验 crackings/<type>/<Name>/project/app/build/outputs/apk/release/app-release.apk。
"""
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
        release_apk = REPO / "output-projects" / type_ / name / "app/build/outputs/apk/release/app-release.apk"
        return {
            "rc": 0 if release_apk.exists() else 1,
            "gradle_apk_exists": release_apk.exists(),
            "apk_size_mb": release_apk.stat().st_size / 1048576 if release_apk.exists() else 0,
        }