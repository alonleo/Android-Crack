#!/usr/bin/env python3
"""step-01-scan-revenue.py — detect action step1: 直接扫描 reward+iap 转发方法。

05-revenue-forwarding/detect action。
不依赖 buggy 的 common handler 层;直接用 os.environ ctx 从 step1-signatures/dump.cs 扫 reward/iap 方法。
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

# reward + iap 方法关键字
REWARD_KEYWORDS = ["showRewardVideo", "showRewardedVideo", "RewardVideo", "showRewarded"]
IAP_KEYWORDS = ["processPurchase", "ProcessPurchase", "queryPurchases", "BillingClient", "Purchase", "Buy", "UnlockPremium"]


class ScanRevenueStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        # 扫描源:step1-signatures/dump.cs(03 fn-analyze 产物)或 raw dump.cs
        sig_dir = REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures"
        dump_cs = sig_dir / "dump" / "dump.cs"
        if not dump_cs.exists():
            for cand in (sig_dir / "dump.cs", REPO / "crackings" / type_ / name / "raw" / "03b-il2cpp-output" / "dump.cs",
                         REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "dump" / "dump.cs"):
                if cand.exists():
                    dump_cs = cand
                    break

        if not dump_cs.exists():
            return {"rc": 1, "skipped": False, "error": "无 dump.cs,无法扫描转发方法", "dump_cs": None}

        text = dump_cs.read_text(encoding="utf-8", errors="ignore")
        reward_methods = []
        iap_methods = []
        for kw in REWARD_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                reward_methods.append(kw)
        for kw in IAP_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", text):
                iap_methods.append(kw)

        # 写检测 yaml
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("revenue-forwarding")
        stage_dir.mkdir(parents=True, exist_ok=True)
        detection = {
            "stage": "05", "name": "revenue-detection",
            "source": str(dump_cs.relative_to(REPO)),
            "reward_methods": sorted(set(reward_methods)),
            "iap_methods": sorted(set(iap_methods)),
            "total_reward": len(set(reward_methods)),
            "total_iap": len(set(iap_methods)),
        }
        (stage_dir / "revenue-detection.yaml").write_text(
            yaml.safe_dump(detection, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "dump_cs": str(dump_cs.relative_to(REPO)),
            "reward_methods": detection["reward_methods"],
            "iap_methods": detection["iap_methods"],
            "total_reward": detection["total_reward"],
            "total_iap": detection["total_iap"],
            "detection_yaml": str((stage_dir / "revenue-detection.yaml").relative_to(REPO)),
        }