#!/usr/bin/env python3
"""step-02-write-detection.py — detect action step2: 校验 revenue-detection.yaml 产物。

05-revenue-forwarding/detect action。
校验 common 主脚本生成的 detection 产物(reward + iap 合并)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step


class WriteDetectionStep(Step):
    def execute(self, steps_results: dict) -> dict:
        scan = steps_results.get("revenue-forwarding.default-action.scan-revenue", {})
        if scan.get("rc") != 0 and not scan.get("skipped"):
            return {"rc": 1, "skipped": True, "reason": "scan-revenue 未成功"}

        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("revenue-forwarding")

        # 找产物(reward-video-detection.yaml + iap-detection.yaml + revenue-detection.yaml)
        yamls = []
        for name_pat in ("reward-video-detection.yaml", "iap-detection.yaml", "revenue-detection.yaml"):
            p = stage_dir / name_pat
            if p.exists():
                yamls.append(name_pat)

        return {
            "rc": 0,
            "skipped": False,
            "detection_yamls_found": yamls,
            "detection_count": len(yamls),
        }