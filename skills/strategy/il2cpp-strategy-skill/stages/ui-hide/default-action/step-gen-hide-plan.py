#!/usr/bin/env python3
"""step-02-gen-hide-plan.py — analyze action step2: 生成 hide-plan.yaml。

07-ui-hide/analyze action。
从 step-01 扫描结果生成 hide-plan.yaml(策略/关键词/隐藏方式)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

import yaml


class GenHidePlanStep(Step):
    def execute(self, steps_results: dict) -> dict:
        scan = steps_results.get("ui-hide.default-action.scan-features", {})
        if scan.get("rc") != 0:
            return {"rc": 1, "skipped": True, "reason": "scan-features 未成功"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("ui-hide")
        stage_dir.mkdir(parents=True, exist_ok=True)

        features = scan.get("features_found", {})
        checklist = scan.get("checklist", steps_results.get("ui-hide.default-action.load-feature-checklist"))
        if not checklist:
            raise ValueError("缺少清单快照，禁止用内置候选列表生成计划")
        targets = checklist["targets"]
        plan = {
            "stage": "07",
            "name": name, "type": type_,
            "checklist_path": checklist["registry_path"],
            "checklist_sha256": checklist["registry_sha256"],
            "checklist_items": checklist["items"],
            "features_to_hide": features,
            "strategy": "hook_container" if type_ in ("il2cpp", "defold") else "smali_patch",
            "items": [
                {"feature": f, "id": targets[f]["id"], "keywords": kws,
                 "strategy": "verify", "suggested_strategy": targets[f]["strategy"],
                 "notes": targets[f]["notes"], "requires_review": True}
                for f, kws in features.items()
            ],
        }
        plan_path = stage_dir / "hide-plan.yaml"
        plan_path.write_text(
            yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "hide_plan": str(plan_path.relative_to(REPO)),
            "feature_count": len(features),
        }
