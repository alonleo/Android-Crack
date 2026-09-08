#!/usr/bin/env python3
"""step-01-scan-features.py — analyze action step1: 扫描可隐藏功能点。

07-ui-hide/analyze action。
直接用 os.environ ctx 从 dump.cs 扫描功能点(more_games/rate/leaderboard/share/credits/vip 等)。
绕过 common handler(其依赖有 bug)。
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

# 功能点关键词
import runpy
_CHECKLIST_API = runpy.run_path(str(REPO / "skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py"))


class ScanFeaturesStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        snapshot = steps_results.get("ui-hide.default-action.load-feature-checklist")
        if snapshot is None:
            snapshot = _CHECKLIST_API["load_snapshot"](os.environ.get("FEATURE_REMOVAL_CHECKLIST") or None, type_)
        if snapshot.get("rc", 0) != 0:
            raise ValueError("清单加载失败，禁止继续扫描")

        # 源:dump.cs(03 fn-analyze 产物)
        dump_cs = self._find_dump_cs(type_, name)
        if dump_cs is None:
            return {"rc": 1, "skipped": False, "error": "无 dump.cs,无法扫描功能点"}

        text = dump_cs.read_text(encoding="utf-8", errors="ignore")
        found = {}
        for feature, config in snapshot["targets"].items():
            hits = [kw for kw in config["keywords"] if kw.casefold() in text.casefold()]
            if hits:
                found[feature] = hits

        return {
            "rc": 0,
            "skipped": False,
            "dump_cs": str(dump_cs.relative_to(REPO)),
            "features_found": found,
            "checklist": snapshot,
            "feature_count": len(found),
            "total_hits": sum(len(v) for v in found.values()),
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
