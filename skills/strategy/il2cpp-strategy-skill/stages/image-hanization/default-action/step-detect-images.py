#!/usr/bin/env python3
"""step-01-detect-images.py — analyze action step1: 检测含文字图片。

13-image-hanization/analyze action。
扫描 res/drawable 中含文字图片。绕过 common handler。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

import yaml


class DetectImagesStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        out_proj = REPO / "crackings" / type_ / name / "project"
        images = []
        for drawable in (out_proj / "app/src/main/res/drawable", out_proj / "app/src/main/res/drawable-xxhdpi"):
            if drawable.exists():
                for f in drawable.iterdir():
                    if f.suffix.lower() in (".png", ".jpg", ".webp"):
                        images.append(str(f.relative_to(REPO)))

        detection = {
            "stage": "13", "name": "images-detection",
            "image_count": len(images),
            "images": images[:50],
        }
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("image-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)
        (stage_dir / "images-detection.yaml").write_text(
            yaml.safe_dump(detection, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "image_count": len(images),
            "detection_yaml": str((stage_dir / "images-detection.yaml").relative_to(REPO)),
        }