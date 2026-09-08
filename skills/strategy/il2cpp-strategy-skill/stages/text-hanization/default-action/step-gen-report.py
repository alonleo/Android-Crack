#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总文本汉化报告。

11-text-hanization/report action。
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
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)

        collect = steps_results.get("text-hanization.default-action.collect-strings", {})
        build_map = steps_results.get("text-hanization.default-action.build-map", {})

        report = {
            "stage": "11", "name": "text-hanization-report",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "strings_xml_count": collect.get("strings_xml_count", 0),
            "dump_literal_estimate": collect.get("dump_literal_estimate", 0),
            "zh_strings_exists": build_map.get("zh_strings_exists", False),
            "analyze_seen": bool(collect),
        }
        report_path = stage_dir / "text-hanization-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "report": str(report_path.relative_to(REPO)),
        }