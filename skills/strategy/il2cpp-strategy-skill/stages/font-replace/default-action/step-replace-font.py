#!/usr/bin/env python3
"""step-02-replace-font.py — analyze action step2: 校验/注入中文字体。

09-font-replace/analyze action。
检查 notosanssc.ttf 是否已注入 res/font/(真实游戏汉化需注入)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class ReplaceFontStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        out_proj = REPO / "crackings" / type_ / name / "project"

        font_dir = out_proj / "app/src/main/res/font"
        chinese_font = font_dir / "notosanssc.ttf"

        return {
            "rc": 0,
            "skipped": False,
            "chinese_font_injected": chinese_font.exists(),
            "font_dir": str(font_dir.relative_to(REPO)) if font_dir.exists() else None,
            "note": "真实汉化需复制中文字体到 res/font/notosanssc.ttf",
        }