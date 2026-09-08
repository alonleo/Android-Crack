#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总图片汉化报告。

13-image-hanization/report action。
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
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("image-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)

        detect = steps_results.get("image-hanization.default-action.detect-images", {})
        ocr = steps_results.get("image-hanization.default-action.ocr-images", {})

        report = {
            "stage": "13", "name": "image-hanization-report",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "image_count": detect.get("image_count", 0),
            "ocr_available": ocr.get("ocr_available", False),
            "analyze_seen": bool(detect),
        }
        report_path = stage_dir / "image-hanization-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "report": str(report_path.relative_to(REPO)),
        }