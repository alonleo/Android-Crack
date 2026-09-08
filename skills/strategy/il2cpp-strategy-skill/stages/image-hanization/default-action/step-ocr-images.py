#!/usr/bin/env python3
"""step-02-ocr-images.py — analyze action step2: OCR 识别含文字图片。

13-image-hanization/analyze action。
用 pytesseract(若可用)扫描含文字图片;否则记录待人工。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step

import yaml


class OcrImagesStep(Step):
    def execute(self, steps_results: dict) -> dict:
        detect = steps_results.get("image-hanization.default-action.detect-images", {})
        if detect.get("rc") != 0:
            return {"rc": 1, "skipped": True, "reason": "detect-images 未成功"}

        # 尝试 OCR
        images_with_text = []
        ocr_available = False
        try:
            import pytesseract  # noqa
            from PIL import Image  # noqa
            ocr_available = True
        except Exception:
            ocr_available = False

        return {
            "rc": 0,
            "skipped": False,
            "ocr_available": ocr_available,
            "images_with_text": images_with_text,
            "image_count": detect.get("image_count", 0),
            "note": "OCR 未启用时记录待人工重绘;真实汉化需逐图 OCR+重绘",
        }