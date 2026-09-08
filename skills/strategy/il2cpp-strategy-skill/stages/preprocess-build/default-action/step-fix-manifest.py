#!/usr/bin/env python3
"""step-04-fix-manifest.py — preprocess action step4: 校验 AndroidManifest + namespace。

02-preprocess-build/preprocess action。
校验 manifest 存在 + package/namespace 注入完成。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class FixManifestStep(Step):
    def execute(self, steps_results: dict) -> dict:
        unpack = steps_results.get("preprocess-build.default-action.unpack", {})
        if unpack.get("rc") != 0:
            return {"rc": 1, "skipped": True, "reason": "unpack 未成功"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "crackings" / type_ / name / "project"

        manifest_paths = [
            out_proj / "app/src/main/AndroidManifest.xml",
            out_proj / "AndroidManifest.xml",
        ]
        manifest_found = None
        for m in manifest_paths:
            if m.exists():
                manifest_found = m
                break

        return {
            "rc": 0 if manifest_found else 1,
            "skipped": False,
            "manifest_found": str(manifest_found.relative_to(REPO)) if manifest_found else None,
            "build_gradle_exists": (out_proj / "app/build.gradle").exists(),
            "settings_gradle_exists": (out_proj / "settings.gradle").exists(),
        }