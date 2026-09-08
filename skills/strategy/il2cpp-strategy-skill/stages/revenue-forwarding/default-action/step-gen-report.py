#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总转发报告。

05-revenue-forwarding/report action。
校验 revenue-forwarding-report.yaml + 汇总 detect/forward 前置结果。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

import yaml


class GenReportStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("revenue-forwarding")

        # 读前置 action 结果(跨 action 累积)
        detect = steps_results.get("revenue-forwarding.detect", {})
        forward = steps_results.get("revenue-forwarding.forward", {})

        report = stage_dir / "revenue-forwarding-report.yaml"
        report_content = ""
        if report.exists():
            report_content = report.read_text(encoding="utf-8", errors="ignore")
            try:
                report_content = yaml.safe_load(report_content)
            except Exception:
                pass

        return {
            "rc": 0 if report.exists() else 1,
            "skipped": False,
            "report": str(report.relative_to(REPO)) if report.exists() else None,
            "detect_seen": bool(detect),
            "forward_seen": bool(forward),
            "report_summary": report_content.get("summary") if isinstance(report_content, dict) else None,
        }