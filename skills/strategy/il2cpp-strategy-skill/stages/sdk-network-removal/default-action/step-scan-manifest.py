#!/usr/bin/env python3
"""step-01-scan-manifest.py — collect_sdk action step1: 扫描 manifest + lib/.so SDK 组件。

03-sdk-network-removal/collect_sdk action。跨 action 累积验证。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step

SDK_KEYWORDS = [
    "applovin", "ironsource", "vungle", "facebook", "chartboost",
    "inmobi", "mbridge", "pangle", "appsflyer", "adjust", "tapjoy",
    "bytedance", "yandex", "digitalturbine", "safedk", "google.android.gms.ads",
    "firebase", "moloco", "pubnative", "adjoe", "adn", "bugly", "hms",
]


class ScanManifestStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        type_ = os.environ.get("TYPE", "il2cpp")
        apktool_root = REPO / "crackings" / type_ / name / "raw" / "01-apktool"

        components = []
        sos = []
        smali_prefixes = []

        manifest = apktool_root / "AndroidManifest.xml"
        if manifest.exists():
            text = manifest.read_text(encoding="utf-8", errors="ignore")
            for kw in SDK_KEYWORDS:
                for m in re.finditer(rf'android:name="([^"]*{re.escape(kw)}[^"]*)"', text, re.IGNORECASE):
                    components.append(m.group(1))
        lib_dir = apktool_root / "lib"
        if lib_dir.exists():
            for so in lib_dir.rglob("*.so"):
                if any(kw in so.name.lower() for kw in SDK_KEYWORDS):
                    sos.append(so.name)
        smali_dir = apktool_root / "smali"
        if smali_dir.exists():
            for pkg in smali_dir.iterdir():
                if pkg.is_dir() and any(kw in pkg.name.lower() for kw in SDK_KEYWORDS):
                    smali_prefixes.append(pkg.name)

        components = sorted(set(components))
        sos = sorted(set(sos))
        smali_prefixes = sorted(set(smali_prefixes))

        return {
            "rc": 0,
            "apktool_root_ok": apktool_root.exists(),
            "components": components,
            "sos": sos,
            "smali_prefixes": smali_prefixes,
            "sdk_component_count": len(components),
            "sdk_so_count": len(sos),
        }