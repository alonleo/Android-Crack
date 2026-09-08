#!/usr/bin/env python3
"""step-02-gen-findings.py — analyze action step2: 校验 findings.md 含入口/SDK 信息。

01-static-analyze/analyze action。
校验 findings.md 生成且含 MainActivity/SDK 入口关键信息。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class GenFindingsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        scan = steps_results.get("static-analyze.default-action.scan-entries", {})
        if scan.get("rc") != 0:
            return {"rc": 1, "skipped": True, "reason": "scan-entries 未成功"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        findings = REPO / "crackings" / type_ / name / "findings.md"

        content = ""
        keywords_found = []
        if findings.exists():
            content = findings.read_text(encoding="utf-8", errors="ignore").lower()
            for kw in ("mainactivity", "application", "sdk", "入口", "launchable"):
                if kw.lower() in content:
                    keywords_found.append(kw)

        return {
            "rc": 0 if findings.exists() else 1,
            "skipped": False,
            "findings": str(findings.relative_to(REPO)) if findings.exists() else None,
            "findings_size_b": findings.stat().st_size if findings.exists() else 0,
            "keywords_found": keywords_found,
            "looks_complete": bool(keywords_found),
        }