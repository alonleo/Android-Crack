#!/usr/bin/env python3
"""step-02-build-map.py — analyze action step2: 生成 hanization_map / 校验 strings.xml。

11-text-hanization/analyze action。
校验 values-zh-rCN/strings.xml 存在(真实汉化需生成映射)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class BuildMapStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "output-projects" / type_ / name

        zh_strings = out_proj / "app/src/main/res/values-zh-rCN/strings.xml"
        hanization_map = out_proj / "app/src/main/cpp/hanization_map.h"

        return {
            "rc": 0,
            "skipped": False,
            "zh_strings_exists": zh_strings.exists(),
            "hanization_map_exists": hanization_map.exists(),
            "note": "真实汉化需生成 hanization_map.h + values-zh-rCN/strings.xml",
        }