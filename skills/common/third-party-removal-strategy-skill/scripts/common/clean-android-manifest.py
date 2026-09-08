#!/usr/bin/env python3
"""clean-android-manifest.py — 用 ElementTree 清理 AndroidManifest.xml 中的第三方 SDK 组件。

背景: FlyingGorillaEndlessRunner (2026-08-02) 中发现旧 regex 清理方案缺陷：
  1. 嵌套多行 <provider>/<service> 块（含 13 个 Firebase component meta-data）regex 匹配不完整
     → 留下孤儿 `</service>` 闭合标签 → XML 损坏 → AGP 编译失败
  2. 误删 `com.google.firebase.components.ComponentDiscoveryService` → Firebase 组件全部
     无法注册 → RemoteConfigComponent 为 null → 加载页卡死
  3. 漏删 `<manifest>` 上的 `requiredSplitTypes/splitTypes` → INSTALL_FAILED_MISSING_SPLIT

本脚本用 ElementTree 精确按类名/权限名删除，**强制保留** Firebase 注册关键项。

用法:
  python3 clean-android-manifest.py <AndroidManifest.xml> [--sdk-prefixes "com.applovin.,com.google.android.play.core."] [--preserve-firebase]

规则:
  - 删除 SDK_PREFIXES 匹配的 <activity>/<service>/<provider>/<receiver>/<meta-data>/<package>
  - 删除受限 uses-permission
  - 移除 <manifest> 的 requiredSplitTypes / splitTypes 属性
  - --preserve-firebase 时跳过 FirebaseInitProvider / ComponentDiscoveryService / firebase.components meta-data
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path

NS_ANDROID = "http://schemas.android.com/apk/res/android"

# 默认删除的 SDK 前缀（不含 Firebase 注册关键项）
SDK_PREFIXES_DEFAULT = [
    "com.applovin.",
    "com.appsflyer.",
    "com.facebook.",
    "com.squareup.picasso.",
    "com.google.android.play.core.",
    "com.google.android.gms.ads.",
]

# 受限权限（删除）
RESTRICTED_PERMISSIONS = [
    "com.android.vending.BILLING",
    "com.android.vending.CHECK_LICENSE",
    "com.google.android.gms.permission.AD_ID",
    "com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE",
    "com.samsung.android.mapsagent.permission.READ_APP_INFO",
    "com.huawei.appmarket.service.commondata.permission.GET_COMMON_DATA",
]

# Firebase 注册关键项（preserve 时不可删）
FIREBASE_CRITICAL = [
    "com.google.firebase.provider.FirebaseInitProvider",
    "com.google.firebase.components.ComponentDiscoveryService",
]


def _aname(child) -> str:
    return child.attrib.get(f"{{{NS_ANDROID}}}name", "")


def _tag(child) -> str:
    return child.tag.split("}")[-1]


def clean(manifest_path: Path, sdk_prefixes: list[str], preserve_firebase: bool) -> int:
    ET.register_namespace("android", NS_ANDROID)
    tree = ET.parse(str(manifest_path))
    root = tree.getroot()

    # 1. 移除 splitTypes 属性
    for attr in ("requiredSplitTypes", "splitTypes"):
        if attr in root.attrib:
            del root.attrib[attr]

    # 2. 删除 uses-permission
    removed = 0
    for up in list(root.findall("uses-permission")):
        name = _aname(up)
        if name in RESTRICTED_PERMISSIONS or any(name.startswith(p) for p in sdk_prefixes):
            root.remove(up)
            removed += 1

    # 3. 删除 application 内 SDK 组件
    app = root.find("application")
    if app is not None:
        for child in list(app):
            name = _aname(child)
            if not name:
                continue
            # 保留 Firebase 关键项
            if preserve_firebase and any(name == crit for crit in FIREBASE_CRITICAL):
                continue
            # 保留 Firebase component registrar meta-data（ComponentDiscoveryService 子项）
            if preserve_firebase and _tag(child) == "meta-data" and name.startswith("com.google.firebase.components:"):
                continue
            if any(name.startswith(p) for p in sdk_prefixes):
                app.remove(child)
                removed += 1

    tree.write(str(manifest_path), encoding="utf-8", xml_declaration=True)
    # 校验 XML 良构
    ET.parse(str(manifest_path))
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="ElementTree 清理 AndroidManifest 第三方 SDK")
    parser.add_argument("manifest", help="AndroidManifest.xml 路径")
    parser.add_argument("--sdk-prefixes", default=",".join(SDK_PREFIXES_DEFAULT),
                        help="逗号分隔的 SDK 类名前缀")
    parser.add_argument("--preserve-firebase", action="store_true",
                        help="保留 FirebaseInitProvider / ComponentDiscoveryService / registrar meta-data")
    args = parser.parse_args()

    mp = Path(args.manifest)
    if not mp.is_file():
        print(f"[ERROR] manifest 不存在: {mp}")
        return 1
    prefixes = [p for p in args.sdk_prefixes.split(",") if p]
    n = clean(mp, prefixes, args.preserve_firebase)
    print(f"[OK]   移除 {n} 个 SDK 元素 → {mp}")
    print(f"[OK]   XML 良构校验通过")
    if args.preserve_firebase:
        print("[INFO] 已保留 FirebaseInitProvider / ComponentDiscoveryService / registrar meta-data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
