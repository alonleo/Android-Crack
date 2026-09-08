#!/usr/bin/env python3
"""step-01-stub-methods.py — stub action step1: 桩化网络检测方法。

03-sdk-network-removal/stub action。
读 collect_sdk 扫到的网络方法,对 strategy=stub 的做桩化(记录,真实项目改 smali)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


class StubMethodsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        network = steps_results.get(
            "sdk-network-removal.default-action.scan-network", {}
        )
        methods = network.get("methods", [])

        stub_count = sum(1 for m in methods if m.get("strategy") == "stub")
        kept = [m for m in methods if m.get("strategy") != "stub"]

        return {
            "rc": 0,
            "stubbed_method_count": stub_count,
            "kept_method_count": len(kept),
            "stubbed_strategies": sorted({m.get("strategy", "") for m in methods}),
            "prior_network_count": network.get("network_method_count", -1),  # 验证跨 action 累积
        }