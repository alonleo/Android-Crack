#!/usr/bin/env python3
"""step-01-smali-to-jar.py — build action step1: 校验 smali→jar 产物。

通用 build action(04/06/08/10/12/14 复用)。
[FLOWFIX] ASBuilder 契约：游戏 dex → app/libs/classes.N.dex.jar（兼兼容 javaScaffoding）。
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
        out_proj = REPO / "crackings" / type_ / name / "project"
        scaffold_jar = out_proj / "app/javaScaffoding/classes.all.dex.jar"
        libs_jars = sorted((out_proj / "app/libs").glob("*.jar")) if (out_proj / "app/libs").is_dir() else []
        jar = scaffold_jar if scaffold_jar.exists() else (libs_jars[0] if libs_jars else None)
        return {
            "rc": 0 if jar and jar.exists() else 1,
            "java_scaffoding_jar_exists": scaffold_jar.exists(),
            "libs_jar_count": len(libs_jars),
            "jar_size_mb": jar.stat().st_size / 1048576 if jar and jar.exists() else 0,
        }
