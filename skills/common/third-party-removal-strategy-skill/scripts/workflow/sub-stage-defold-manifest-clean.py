#!/usr/bin/env python3
"""stage-09-banana-manifest-clean.py — BananaKong 专用 manifest SDK 清理。

背景: BananaKong (2026-08-04) 是 Defold 引擎游戏：
  - libBananaKong.so (libdmengine.so) 通过 JNI 回调 com.defold.admob.AdmobJNI 等 glue 类
  - glue 类直接引用 ads_mobile_sdk (AppLovin) / com.google.firebase / gms 等 SDK 实现类
  → 物理删除 SDK smali 会造成 NoClassDefFoundError / native JNI 崩溃（OBJECTIVES §4.3 风险表）
  → 采用「manifest 移除自动初始化 + 保留 smali 类」策略：SDK 不再自动启动，
     Java 层 glue 因类仍在不会崩溃，Lua 广告调用静默失败。

清理目标（manifest 级）：
  - 删除 applovin / mbridge / vungle / facebook / firebase / gms ads / gms games /
    gms measurement / datatransport / play core / amazon iap / defold push 的
    activity / service / provider / receiver / meta-data
  - 保留: com.dynamo.android.DefoldActivity、androidx.*、billingclient、gms common
  - 移除受限权限（AD_ID / ADSERVICES / READ_PHONE_STATE / referrer / amazon）
  - 保留 INTERNET / ACCESS_NETWORK_STATE / WAKE_LOCK / VIBRATE / FOREGROUND_SERVICE / BILLING

用法:
  python3 stage-09-banana-manifest-clean.py <AndroidManifest.xml>
"""
from __future__ import annotations

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

NS_ANDROID = "http://schemas.android.com/apk/res/android"
ET.register_namespace("android", NS_ANDROID)

REMOVE_PREFIXES = [
    "com.applovin.",
    "com.mbridge.",
    "com.vungle.",
    "com.facebook.ads",
    "com.google.firebase.",
    "com.google.firebase:",
    "com.google.android.gms.ads.",
    "com.google.android.gms.games.",
    "com.google.android.gms.measurement.",
    "com.google.android.datatransport.",
    "com.google.android.play.core.",
    "com.amazon.device.iap.",
    "com.defold.push.",
    "com.google.android.libraries.ads.",
]

REMOVE_EXACT = [
    "com.google.firebase.provider.FirebaseInitProvider",
    "com.google.firebase.sessions.SessionLifecycleService",
    "com.google.android.gms.ads.APPLICATION_ID",
    "com.google.android.gms.ads.flag.OPTIMIZE_AD_LOADING",
    "com.google.android.gms.ads.flag.OPTIMIZE_INITIALIZATION",
    "com.google.android.gms.games.APP_ID",
    "com.google.android.gms.games.version",
    "com.amazon.privacypass",
]

RESTRICTED_PERMISSIONS = [
    "com.google.android.gms.permission.AD_ID",
    "android.permission.ACCESS_ADSERVICES_AD_ID",
    "android.permission.ACCESS_ADSERVICES_ATTRIBUTION",
    "android.permission.ACCESS_ADSERVICES_TOPICS",
    "android.permission.READ_BASIC_PHONE_STATE",
    "com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE",
    "com.amazon.privacypass.ATTEST",
]


def _aname(child) -> str:
    return child.attrib.get(f"{{{NS_ANDROID}}}name", "")


def _tag(child) -> str:
    return child.tag.split("}")[-1]


def should_remove(name: str) -> bool:
    if not name:
        return False
    if name in REMOVE_EXACT:
        return True
    return any(name.startswith(p) for p in REMOVE_PREFIXES)


def main() -> int:
    if len(sys.argv) < 2:
        print("用法: stage-09-banana-manifest-clean.py <AndroidManifest.xml>")
        return 1
    mp = Path(sys.argv[1])
    tree = ET.parse(str(mp))
    root = tree.getroot()

    # 1. manifest 级 splitTypes 残留清理
    for attr in ("requiredSplitTypes", "splitTypes"):
        if attr in root.attrib:
            del root.attrib[attr]

    # 2. uses-permission
    removed_perm = 0
    for up in list(root.findall("uses-permission")):
        name = _aname(up)
        if name in RESTRICTED_PERMISSIONS:
            root.remove(up)
            removed_perm += 1

    # 3. application 内组件
    app = root.find("application")
    removed_comp = 0
    if app is not None:
        for child in list(app):
            name = _aname(child)
            if should_remove(name):
                app.remove(child)
                removed_comp += 1

    # 4. queries 中 SDK intent（保留系统 action）
    for q in root.findall("queries"):
        for intent in list(q):
            keep = False
            for a in intent.iter():
                nm = _aname(a)
                if nm and any(p in nm for p in REMOVE_PREFIXES):
                    keep = True
                    break
            if keep:
                q.remove(intent)

    tree.write(str(mp), encoding="utf-8", xml_declaration=True)
    ET.parse(str(mp))  # well-formed 校验
    print(f"[OK] 移除权限 {removed_perm} 个，组件 {removed_comp} 个 → {mp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
