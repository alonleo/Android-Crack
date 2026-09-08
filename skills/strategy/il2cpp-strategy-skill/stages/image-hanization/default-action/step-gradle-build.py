#!/usr/bin/env python3
"""step-02-gradle-build.py — build action step2: 校验 Gradle 构建产物。

通用 build action。
[FLOWFIX] ASBuilder/set-gradle-identity 命名 <Name>-release-<version>.apk，glob 定位。
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
        out_proj = REPO / "crackings" / type_ / name / "project"
        rel_dir = out_proj / "app/build/outputs/apk/release"
        apks = sorted(rel_dir.glob("*.apk")) if rel_dir.is_dir() else []
        release_apk = apks[0] if apks else None
        return {
            "rc": 0 if release_apk and release_apk.exists() else 1,
            "gradle_apk_exists": bool(release_apk and release_apk.exists()),
            "apk_size_mb": release_apk.stat().st_size / 1048576 if release_apk and release_apk.exists() else 0,
        }
