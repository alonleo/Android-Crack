#!/usr/bin/env python3
"""step-01-scan-fonts.py — analyze action step1: 扫描字体调用。

09-font-replace/analyze action。
从 dump.cs 扫 Typeface/字体加载调用 + 检查现有中文字体。
绕过 common handler(依赖有 bug)。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
# 兼容读取旧项目分析产物；fn-analyze 已不再参与路由。
from step_base import stage_path, REPO, Step

import yaml

FONT_KEYWORDS = ["Typeface", "createFromAsset", "Font", "setTypeface", "FontAtlas", "font"]


class ScanFontsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        dump_cs = self._find_dump_cs(type_, name)
        font_keywords_hits = []
        if dump_cs and dump_cs.exists():
            text = dump_cs.read_text(encoding="utf-8", errors="ignore")
            font_keywords_hits = [kw for kw in FONT_KEYWORDS if re.search(rf"\b{re.escape(kw)}\b", text)]

        # 检查现有字体文件
        out_proj = REPO / "crackings" / type_ / name / "project"
        existing_fonts = []
        for cand in (out_proj / "app/src/main/res/font", out_proj / "app/src/main/assets/fonts"):
            if cand.exists():
                existing_fonts += [f.name for f in cand.iterdir()]

        detection = {
            "stage": "09", "name": "font-detection",
            "dump_cs": str(dump_cs.relative_to(REPO)) if dump_cs else None,
            "font_keyword_hits": font_keywords_hits,
            "existing_fonts": existing_fonts,
            "needs_replacement": bool(font_keywords_hits),
        }
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("font-replace")
        stage_dir.mkdir(parents=True, exist_ok=True)
        (stage_dir / "font-detection.yaml").write_text(
            yaml.safe_dump(detection, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "font_keyword_hits": font_keywords_hits,
            "existing_fonts": existing_fonts,
            "needs_replacement": detection["needs_replacement"],
            "detection_yaml": str((stage_dir / "font-detection.yaml").relative_to(REPO)),
        }

    @staticmethod
    def _find_dump_cs(type_, name):
        sig_dir = REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures"
        for cand in (sig_dir / "dump" / "dump.cs", sig_dir / "dump.cs",
                     REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "dump" / "dump.cs",
                     REPO / "crackings" / type_ / name / "raw" / "03b-il2cpp-output" / "dump.cs"):
            if cand.exists():
                return cand
        return None