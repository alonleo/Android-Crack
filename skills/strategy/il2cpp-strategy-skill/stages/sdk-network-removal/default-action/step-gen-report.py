#!/usr/bin/env python3
"""step-01-gen-report.py — report action step1: 汇总所有前置 action 结果,写 sdk-network-report.yaml。

03-sdk-network-removal/report action。
**关键验证:跨 action 累积** —— 读 collect_sdk/clean/stub/build 五个 action 的全部前置 step 结果。
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
        cracking_root = REPO / "crackings" / type_ / name

        # 读所有前置 action 累积(跨 action 累积的终极验证)
        # action 级结果 key = action_name(dispatch 时 steps_results[action_name] = result)
        # step 级结果 key = f"{sub_stage}.{action_name}.{step_name}"
        collect_sdk = steps_results.get("collect_sdk", {})
        collect_manifest = steps_results.get("sdk-network-removal.default-action.scan-manifest", {})
        clean = steps_results.get("clean", {})
        clean_all = steps_results.get("sdk-network-removal.default-action.clean-all", {})
        stub = steps_results.get("sdk-network-removal.default-action.stub-methods", {})
        build = steps_results.get("sdk-network-removal.default-action.gradle-build", {})

        report = {
            "name": name,
            "type": type_,
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "summary": {
                "sdk_components_found": collect_manifest.get("sdk_component_count", 0),
                "cleaned_components": clean_all.get("cleaned_components", 0),
                "stubbed_methods": stub.get("stubbed_method_count", 0),
                "build_ok": build.get("build_ok", False),
            },
            "cross_action_dependencies": {
                "report_sees_collect": bool(collect_sdk),
                "report_sees_clean_all": bool(clean_all),
                "report_sees_stub": bool(stub),
                "report_sees_build": bool(build),
            },
        }

        report_path = cracking_root / "stages" / stage_path("sdk-network-removal") / "sdk-network-report.yaml"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8"
        )

        return {
            "rc": 0,
            "report_path": str(report_path.relative_to(REPO)),
            "summary": report["summary"],
            "cross_action_deps": report["cross_action_dependencies"],
        }