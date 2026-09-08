#!/usr/bin/env python3
"""step-05-namespace.py — preprocess action step5: 校验 namespace/工程骨架完整性。

02-preprocess-build/preprocess action。
最后确认 AS 工程骨架(build.gradle 含 namespace / gradlew 存在)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class NamespaceStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "crackings" / type_ / name / "project"

        build_gradle = out_proj / "app/build.gradle"
        gradlew = out_proj / "gradlew"

        namespace = ""
        if build_gradle.exists():
            text = build_gradle.read_text(encoding="utf-8", errors="ignore")
            if "namespace" in text:
                namespace = text.split("namespace")[1].split("\n")[0].strip()

        return {
            "rc": 0,
            "skipped": False,
            "has_namespace": bool(namespace),
            "namespace_value": namespace,
            "gradlew_exists": gradlew.exists(),
            "skel_complete": build_gradle.exists() and gradlew.exists(),
        }