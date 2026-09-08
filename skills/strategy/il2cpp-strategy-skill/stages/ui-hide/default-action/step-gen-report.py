#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总阶段报告。

通用 report action(08 等)。
汇总 analyze 前置结果,写 <stage>-report.yaml。
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
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("ui-hide")
        stage_dir.mkdir(parents=True, exist_ok=True)

        # 汇总前置
        analyze = steps_results.get("ui-hide.analyze", {})
        plan = steps_results.get("ui-hide.default-action.gen-hide-plan", {})
        plan_data = {}
        if plan.get("hide_plan"):
            try:
                plan_data = yaml.safe_load(Path(REPO, plan["hide_plan"]).read_text(encoding="utf-8"))
            except Exception:
                plan_data = {}

        report = {
            "stage": "07", "name": "ui-hide-report",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "features_to_hide": plan_data.get("features_to_hide", {}),
            "feature_count": plan_data.get("item_count", plan.get("feature_count", 0)),
            "analyze_seen": bool(analyze),
        }
        report_path = stage_dir / "ui-hide-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "report": str(report_path.relative_to(REPO)),
            "feature_count": report["feature_count"],
        }