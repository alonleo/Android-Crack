#!/usr/bin/env python3
"""step-01-smali-to-jar.py — build action step1: 校验 smali→jar 产物。

通用 build action(04/06/08/10/12/14 复用)。
校验 crackings/<type>/<Name>/project/app/javaScaffoding/classes.all.dex.jar。
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
        jar = REPO / "output-projects" / type_ / name / "app/javaScaffoding/classes.all.dex.jar"
        return {
            "rc": 0 if jar.exists() else 1,
            "java_scaffoding_jar_exists": jar.exists(),
            "jar_size_mb": jar.stat().st_size / 1048576 if jar.exists() else 0,
        }