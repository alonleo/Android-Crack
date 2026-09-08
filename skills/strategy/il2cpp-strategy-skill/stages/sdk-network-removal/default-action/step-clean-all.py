#!/usr/bin/env python3
"""step-02-clean-all.py — clean action step2: 清理 manifest/components/SDK .so。

03-sdk-network-removal/clean action。
读 load-registry 累积结果做实际清理;模拟记录清理到的组件(真实项目会改 manifest/apktool)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class CleanAllStep(Step):
    def execute(self, steps_results: dict) -> dict:
        # 读 collect_sdk + load_registry 累积
        collect = steps_results.get(
            "sdk-network-removal.default-action.scan-manifest", {}
        )
        registry = steps_results.get(
            "sdk-network-removal.default-action.load-registry", {}
        )

        # 清理这些 SDK 组件(collect_sdk 扫到的)
        components = collect.get("components", [])
        registry_sections = registry.get("sections_loaded", [])

        return {
            "rc": 0,
            "cleaned_components": len(components),
            "cleaned_components_list": components,
            "registry_used": bool(registry_sections),
            "prior_registry_schema": registry.get("schema_version", -1),  # 验证跨 action 累积
        }