#!/usr/bin/env python3
"""fix-android-manifest.py — 修复 FakerAndroid 生成的 AndroidManifest.xml。

处理问题：
  1. 保留/补回 <manifest> 上的 package 属性（值 = 原包名；apktool b 打包必需，
     AGP 7.4.2 中与 namespace 一致时仅 deprecated 警告不报错）
  2. 移除 android:requiredSplitTypes / splitTypes
  3. 移除 Android 13+ 属性（appComponentFactory/dataExtractionRules/enableOnBackInvokedCallback/fullBackupContent）
  4. 移除空的 <intent></intent> 和 <intent-filter></intent-filter>
  5. 修复 configChanges 中不支持的 colorMode/fontWeightAdjustment

用法：
  python3 fix-android-manifest.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def _name():
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def _project_manifest(name: str) -> Path:
    type_arg = os.environ.get("TYPE", "").strip()
    return ((type_arg and (ROOT / "output-projects" / type_arg / name)) or (ROOT / "output-projects" / name)) / "app" / "src" / "main" / "AndroidManifest.xml"


def _real_package(apk: str) -> str:
    """从源 APK 提取真实包名（aapt2 dump packagename）。"""
    aapt2 = os.environ.get("AAPT2", "")
    if aapt2 and os.path.isfile(apk):
        try:
            r = subprocess.run([aapt2, "dump", "packagename", apk],
                               capture_output=True, text=True, timeout=60)
            if r.returncode == 0:
                return r.stdout.strip()
        except Exception:
            pass
    return ""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--apk", default=os.environ.get("APK", ""), help="源 APK（用于提取真实包名）")
    args = parser.parse_args()
    name = args.name

    mp = _project_manifest(name)
    if not mp.is_file():
        print(f"[ERROR] manifest 缺失: {mp}")
        return 1

    text = mp.read_text(encoding="utf-8", errors="ignore")
    orig_len = len(text)

    # 1. 保留/补回 package 属性（值 = 原包名）。
    # [FLOWFIX] AGP 7.4.2 用 namespace 后 apktool b 报 "<manifest> must have a 'package'
    # attribute"。package 与 namespace 一致时 AGP 仅 deprecated 警告不报错；
    # apktool b 依赖 package 打包 smali → 必须保留。
    m = re.search(r'package="([^"]*)"', text)
    if not m or not m.group(1):
        pkg = _real_package(args.apk) if args.apk else ""
        if not pkg:
            # 兜底：从 build.gradle namespace / applicationId 提取
            bg = mp.parent.parent / "build.gradle"
            if bg.is_file():
                bm = re.search(r"(?:namespace|applicationId)\s+['\"]([^'\"]+)['\"]",
                               bg.read_text(encoding="utf-8", errors="ignore"))
                if bm:
                    pkg = bm.group(1)
        if pkg:
            if 'package="' in text:
                text = re.sub(r'package="[^"]*"', f'package="{pkg}"', text, count=1)
            else:
                text = text.replace("<manifest ", f'<manifest package="{pkg}" ', 1)
            print(f"[INFO] manifest: 补回 package=\"{pkg}\"（apktool b 要求）")

    # 2. 移除 requiredSplitTypes / splitTypes
    text = re.sub(r'\s+android:requiredSplitTypes="[^"]*"', '', text)
    text = re.sub(r'\s+android:splitTypes="[^"]*"', '', text)

    # 3. 移除 Android 13+ 属性
    for attr in ("android:appComponentFactory", "android:dataExtractionRules",
                 "android:enableOnBackInvokedCallback", "android:fullBackupContent"):
        text = re.sub(rf'\s+{attr}="[^"]*"', '', text)

    # 4. 移除空 intent / intent-filter
    text = re.sub(r'<intent>\s*</intent>', '', text)
    # [FLOWFIX] 支持带属性的空 intent-filter（如 FirebaseMessagingService 的
    # <intent-filter android:priority="-500"></intent-filter>）
    text = re.sub(r'<intent-filter[^>]*>\s*</intent-filter>', '', text)

    # 5. 修复 configChanges
    text = re.sub(r'(android:configChanges="[^"]*)colorMode\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?colorMode', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)fontWeightAdjustment\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?fontWeightAdjustment', r'\1', text)

    mp.write_text(text, encoding="utf-8")
    print(f"[OK] manifest 修复: {orig_len} → {len(text)} 字节")
    return 0


if __name__ == "__main__":
    sys.exit(main())
