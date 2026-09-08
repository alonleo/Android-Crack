#!/usr/bin/env python3
"""step-01-env-init.py — preprocess action step1: 环境初始化(构造 APK 路径 + 验证)。

02-preprocess-build/preprocess action。
极简 os.environ ctx 模式。设置 APK/NAME/TYPE,验证 APK 存在,供后续 step 委托 common 主脚本用。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step, resolve_apk


class EnvInitStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()

        # 用通用 helper 解析 APK
        apk = resolve_apk(name, os.environ.get("APK", ""))

        ok = apk is not None and apk.exists()
        if ok:
            os.environ["APK"] = str(apk)

        apk_size_mb = 0
        if ok:
            apk_size_mb = apk.stat().st_size / 1048576  # type: ignore[union-attr]

        return {
            "rc": 0 if ok else 1,
            "skip": not ok,
            "name": name,
            "type": type_,
            "apk": str(apk) if apk else None,
            "apk_exists": ok,
            "apk_size_mb": apk_size_mb,
        }