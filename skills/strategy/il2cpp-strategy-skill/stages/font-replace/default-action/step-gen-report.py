#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总字体替换报告。

09-font-replace/report action。
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

import yaml


class GenReportStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("font-replace")
        stage_dir.mkdir(parents=True, exist_ok=True)

        font_data = steps_results.get("font-replace.default-action.font-detection", {})
        scan = steps_results.get("font-replace.default-action.scan-fonts", {})
        replace = steps_results.get("font-replace.default-action.replace-font", {})

        report = {
            "stage": "09", "name": "font-report",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "font_keyword_hits": scan.get("font_keyword_hits", []),
            "chinese_font_injected": replace.get("chinese_font_injected", False),
            "analyze_seen": bool(font_data),
        }
        report_path = stage_dir / "font-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "report": str(report_path.relative_to(REPO)),
        }