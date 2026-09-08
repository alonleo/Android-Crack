#!/usr/bin/env python3
"""Inject SDK-filtered original smali as dex into the built AS APK."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
EXCLUDE = (
    # [FLOWFIX]
    # 只过滤纯广告 SDK 的 Java 类（不影响 Unity C# JNI 调用的桥接类）。
    # ⚠️ 不得过滤：
    #   - com/appsflyer（AppsFlyerAndroidWrapper 被 Unity C# AndroidJavaClass 硬调用）
    #   - com/google（FirebaseApp / Firebase 类被 Unity Firebase SDK 硬调用）
    #   - com/unity3d/player（UnityPlayer 等引擎类）
    #   - com/applovin（MaxUnityPlugin 被 Unity C# AndroidJavaClass 硬调用）
    # 否则 Unity C# 层 ClassNotFoundException → 初始化链断裂 → 卡加载。
    "com/facebook", "com/adjust", "com/squareup",
    "com/inmobi", "com/bumptech", "com/cleveradssolutions", "com/ogury",
    "com/unity3d/ads", "com/unity3d/services", "com/ironsource", "com/vungle",
    "com/chartboost", "com/amazon/device/ads",
)
EXCLUDE_PARTS = {
    # [FLOWFIX] "ads"/"services" 等宽泛词会误伤
    # com/appsflyer、com/google/firebase、com/applovin 等游戏 JNI 依赖 → 全部移除。
    "facebook", "adjust", "squareup", "inmobi",
    "bumptech", "cleveradssolutions", "ogury",
    "ironsource", "vungle", "chartboost", "amazon",
}


def ignore_sdk(directory: str, names: list[str]) -> set[str]:
    root = Path(directory)
    ignored = set()
    for item in names:
        rel = str((root / item).relative_to(root)).replace("\\", "/")
        if item in EXCLUDE_PARTS or any(rel == p or rel.startswith(p + "/") for p in EXCLUDE):
            ignored.add(item)
    return ignored


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    root = REPO / "output-projects" / type_arg / name
    source = root / "app" / "src" / "main"
    apk = root / "app" / "build" / "outputs" / "apk" / "release" / "app-release.apk"
    injector = REPO / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts" / "common" / "inject-smali-dex.py"
    if not source.is_dir() or not apk.is_file():
        raise SystemExit("source smali or release APK missing")
    with tempfile.TemporaryDirectory(prefix=f"{name}_filtered_dex_") as temp:
        filtered = Path(temp) / "main"
        for child in source.iterdir():
            if child.name.startswith("smali"):
                shutil.copytree(child, filtered / child.name, ignore=ignore_sdk)
        result = subprocess.run([
            "python3", str(injector), "--apk", str(apk), "--smali-root", str(filtered),
            "--api", "34", "--force",
        ], check=False)
        if result.returncode != 0:
            return result.returncode
    print(f"[OK] 已将过滤 SDK 后的原始 smali dex 注入: {apk}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
