#!/usr/bin/env python3
"""step-03-gen-report.py — verify action step3: 汇总验收报告。

06-revenue-device-verify/verify action(通用)。
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
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("revenue-device-verify")
        stage_dir.mkdir(parents=True, exist_ok=True)

        chk = steps_results.get("revenue-device-verify.default-action.check-env", {})
        run = steps_results.get("revenue-device-verify.default-action.run-verify", {})

        report = {
            "stage": "06", "name": "verify-report",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "skipped": chk.get("skip", True),
            "verify_rc": run.get("verify_rc"),
            "checks": chk.get("checks", {}),
        }
        report_path = stage_dir / "verify-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")
        return {"rc": 0, "skipped": False, "report": str(report_path.relative_to(REPO))}
