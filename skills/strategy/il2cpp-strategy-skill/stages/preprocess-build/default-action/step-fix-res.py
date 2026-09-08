#!/usr/bin/env python3
"""step-03-fix-res.py — preprocess action step3: 校验资源修复结果。

02-preprocess-build/preprocess action。
step-02 委托 common 完成资源修复,此处校验 res/values 清理 + drawable 完整性。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class FixResStep(Step):
    def execute(self, steps_results: dict) -> dict:
        unpack = steps_results.get("preprocess-build.default-action.unpack", {})
        if unpack.get("rc") != 0:
            return {"rc": 1, "skipped": True, "reason": "unpack 未成功"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "crackings" / type_ / name / "project"

        # 校验 res/values 无 strings-*.xml(common 步骤4 清理)
        values_dir = out_proj / "app/src/main/res/values"
        leftover = []
        if values_dir.exists():
            leftover = [f.name for f in values_dir.glob("strings-*.xml")]

        # 校验 drawable 存在(资源修复后)
        drawable = out_proj / "app/src/main/res/drawable"
        drawable_count = len(list(drawable.glob("*.xml"))) if drawable.exists() else 0

        return {
            "rc": 0 if not leftover else 1,
            "skipped": False,
            "leftover_strings_locale": leftover,
            "drawable_xml_count": drawable_count,
            "values_dir_exists": values_dir.exists(),
        }