#!/usr/bin/env python3
"""step-01-load-registry.py — clean action step1: 加载第三方 SDK 移除清单。

03-sdk-network-removal/clean action。
加载 skills/common/third-party-removal-strategy-skill/references/third-party-sdk-removal-registry.yaml,供 clean-all 使用。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step

import yaml


class LoadRegistryStep(Step):
    def execute(self, steps_results: dict) -> dict:
        # 读 collect_sdk 累积结果
        collect = steps_results.get(
            "sdk-network-removal.default-action.scan-manifest", {}
        )

        registry_path = REPO / "skills/common/third-party-removal-strategy-skill/references/third-party-sdk-removal-registry.yaml"
        registry = {}
        if registry_path.exists():
            try:
                registry = yaml.safe_load(registry_path.read_text(encoding="utf-8"))
            except Exception:
                registry = {}

        return {
            "rc": 0,
            "registry_exists": registry_path.exists(),
            "schema_version": registry.get("schema_version"),
            "sections_loaded": list(registry.keys()) if registry else [],
            "prior_sdk_count": collect.get("sdk_component_count", -1),  # 验证跨 action 累积
        }