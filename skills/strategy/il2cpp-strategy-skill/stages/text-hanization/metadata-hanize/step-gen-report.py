#!/usr/bin/env python3
"""step-06-gen-report.py — [方案A] metadata-hanize step6: yaml 报告(最后一步)。

汇总前几步关键产物(字符串数/译文条目/回写统计 + smali/gradle 产物),写
text-hanization-report.yaml。
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
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        prep = steps_results.get("text-hanization.metadata-hanize.prepare-metadata", {})
        trans = steps_results.get("text-hanization.metadata-hanize.load-translations", {})
        patch = steps_results.get("text-hanization.metadata-hanize.patch-metadata", {})
        smali = steps_results.get("text-hanization.metadata-hanize.smali-to-jar", {})
        gradle = steps_results.get("text-hanization.metadata-hanize.gradle-build", {})

        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)

        report = {
            "stage": "11", "name": "text-hanization-report",
            "approach": "A-metadata-static",
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "string_count": prep.get("string_count", 0),
            "stringliteral_reused": prep.get("stringliteral_reused", False),
            "metadata_path": prep.get("metadata_path"),
            "translation_entries": trans.get("patch_entries", 0),
            "valid_entries": trans.get("valid_entries", 0),
            "invalid_entries": trans.get("invalid_entries", []),
            "needs_translation": trans.get("needs_translation", True),
            "patched_count": patch.get("patched", 0),
            "patched_out_bytes": patch.get("out_bytes", 0),
            "patched_out_path": patch.get("out_path"),
            "smali_to_jar_exists": smali.get("java_scaffoding_jar_exists", False),
            "gradle_apk_exists": gradle.get("gradle_apk_exists", False),
        }
        report_path = stage_dir / "text-hanization-report.yaml"
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0, "skipped": False,
            "report": str(report_path.relative_to(REPO)),
            "patched": patch.get("patched", 0),
            "needs_translation": trans.get("needs_translation", True),
        }
