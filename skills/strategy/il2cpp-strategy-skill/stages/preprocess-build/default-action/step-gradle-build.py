#!/usr/bin/env python3
"""step-02-gradle-build.py — build action step2: 校验 Gradle 构建产物(release APK)。

02-preprocess-build/build action。
gradlew 构建已在 sub-stage-as-build.py 完成;此处校验产出 APK。

[FLOWFIX 2026-09-05] set-gradle-identity 会把 APK 命名为 <Name>-release-<version>.apk，
非固定 app-release.apk；此处按 release 目录 glob *.apk 定位，兼容自定义命名。
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
            "gradlew_exists": (out_proj / "gradlew").exists(),
        }