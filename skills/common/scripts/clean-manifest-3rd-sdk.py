#!/usr/bin/env python3
"""clean-manifest-3rd-sdk.py — 清理 AndroidManifest 中已移除 SDK 的引用。

移除以下内容：
1. 第三方 SDK 的 activity/service/receiver/provider（类不存在）
2. 保留 UnityPlayerActivity（游戏必须）
3. 保留必要的 Firebase/Unity 核心组件
4. 修复 Application 和主 Activity 的继承关系

用法：
  python3 clean-manifest-3rd-sdk.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
from common import (
    ensure_dir,
    setup_paths_from_name,
    setup_paths_from_apk,
    log_info,
    log_warn,
    log_step,
    log_success,
    log_error,
    register_artifact,
    append_status,
)


# 必须保留的 Activity/Application 类（游戏核心）
KEEP_ACTIVITIES = {
    "com.unity3d.player.UnityPlayerActivity",
    "com.android.boot.MainActivity",
}

# 必须保留的 Application 类
KEEP_APPLICATIONS = {
    "android.app.Application",
    "com.android.boot.App",
    "com.safedk.android.SafeDKApplication",  # 保留引用但重写为 com.android.boot.App
}

# 必须保留的 provider（Unity/Google Play 核心）
KEEP_PROVIDERS = {
    "com.android.tools.fd.runtime.BootstrapApplication",
    "androidx.startup.InitializationProvider",
}

# 必须保留的 service
KEEP_SERVICES = set()

# SDK 关键词（类名含任一关键词 → 移除）
SDK_KEYWORDS = [
    "applovin", "ironsource", "vungle", "facebook", "chartboost", "inmobi",
    "fyber", "mbridge", "pangle", "moloco", "yandex", "bytedance", "tapjoy",
    "appsflyer", "adjust", "my.target", "unity3d.services", "unity3d.ads", "digitalturbine",
    "google.android.gms.ads", "com.google.android.gms.ads",
    "google.android.gms.games", "com.google.android.gms.games",
    "google.games.bridge", "google.android.play", "android.billingclient",
    "com.android.billingclient", "unity.androidnotifications", "amazon.privacypass",
    "google.android.datatransport", "google.android.exoplayer", "com.safedk",
]


def _name() -> str:
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def _manifest_path(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "app" / "src" / "main" / "AndroidManifest.xml"


def find_original_app_class(manifest: Path) -> str:
    """从原始 manifest 找出原始 Application 类。"""
    text = manifest.read_text(encoding="utf-8", errors="ignore")
    m = re.search(r'<application[^>]+android:name="([^"]+)"', text)
    return m.group(1) if m else ""


def find_original_activity(manifest: Path) -> str:
    """从原始 manifest 找出原始主 Activity。"""
    text = manifest.read_text(encoding="utf-8", errors="ignore")
    # 查找带 MAIN/LAUNCHER intent-filter 的 activity
    pattern = re.compile(
        r'<activity[^>]+android:name="([^"]+)"[^>]*>.*?<intent-filter>.*?<action\s+android:name="android\.intent\.action\.MAIN"\s*/>.*?<category\s+android:name="android\.intent\.category\.LAUNCHER"\s*/>',
        re.DOTALL,
    )
    m = pattern.search(text)
    if m:
        return m.group(1)
    return "com.unity3d.player.UnityPlayerActivity"


def remove_element(text: str, pattern: re.Pattern, label: str) -> tuple:
    """移除匹配的元素并返回 (新文本, 移除数量)。"""
    new_text, count = pattern.subn("", text)
    if count > 0:
        log_info(f"移除 {label}: {count} 个")
    return new_text, count


def clean_manifest(manifest_path: Path) -> bool:
    """清理 AndroidManifest.xml 中的第三方 SDK 引用。

    移除：SDK 的 activity/service/receiver/provider/meta-data（类名含 SDK_KEYWORDS）
    保留：KEEP_ACTIVITIES / KEEP_PROVIDERS 中的核心类
    """
    if not manifest_path.is_file():
        log_error(f"AndroidManifest.xml 缺失: {manifest_path}")
        return False

    text = manifest_path.read_text(encoding="utf-8", errors="ignore")
    total_removed = 0

    # 保留的关键类
    KEEP_CLASSES = set(KEEP_ACTIVITIES) | set(KEEP_PROVIDERS)

    def is_sdk_class(name: str) -> bool:
        return name and any(kw in name.lower() for kw in SDK_KEYWORDS) and name not in KEEP_CLASSES

    # 1. 移除 SDK 的 activity/service/receiver/provider（含内容）
    for tag in ["activity", "service", "receiver", "provider"]:
        pattern = re.compile(rf'<{tag}\b[^>]*?(/>|>(?:.*?)</{tag}>)', re.DOTALL)
        out = []
        pos = 0
        removed = 0
        for m in pattern.finditer(text):
            block = m.group(0)
            name_m = re.search(r'android:name="([^"]+)"', block)
            name = name_m.group(1) if name_m else ""
            if (tag == "provider" and name not in KEEP_PROVIDERS) or is_sdk_class(name):
                out.append(text[pos:m.start()])
                pos = m.end()
                removed += 1
            else:
                out.append(text[pos:m.end()])
                pos = m.end()
        out.append(text[pos:])
        text = "".join(out)
        if removed:
            log_info(f"移除 {tag}: {removed}")
            total_removed += removed

    # 2. 移除 SDK 的 meta-data
    meta_pattern = re.compile(r'<meta-data\b[^>]*android:name="([^"]+)"[^>]*/>', re.DOTALL)
    def _meta_repl(m):
        return "" if is_sdk_class(m.group(1)) else m.group(0)
    new_text, n = meta_pattern.subn(_meta_repl, text)
    if n:
        log_info(f"处理 meta-data: {n}")
        total_removed += n
    text = new_text

    # 3. 移除 SDK 专用 uses-permission
    sdk_perms = [
        "com.applovin.array.apphub.permission.BIND_APPHUB_SERVICE",
        "com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE",
        "com.samsung.android.mapsagent.permission.READ_APP_INFO",
        "com.huawei.appmarket.service.commondata.permission.GET_COMMON_DATA",
    ]
    for perm in sdk_perms:
        text, n = re.subn(rf'\s*<uses-permission\s+android:name="{re.escape(perm)}"\s*/>', "", text)
        total_removed += n

    # 4. 移除 queries 中的 SDK 包
    sdk_packages = [
        "com.facebook.katana", "com.instagram.android", "com.facebook.lite",
        "com.samsung.android.mapsagent", "com.android.chrome",
        "com.google.android.webview", "com.android.webview", "com.android.vending",
    ]
    for pkg in sdk_packages:
        text, n = re.subn(rf'<package\s+android:name="{re.escape(pkg)}"\s*/>', "", text)
        total_removed += n

    # 5. 移除 SDK 专用 action
    sdk_actions = [
        "com.attribution.REFERRAL_PROVIDER", "com.applovin.am.intent.action.APPHUB_SERVICE",
        "com.appsflyer.referrer.INSTALL_PROVIDER",
        "com.android.vending.billing.InAppBillingService.BIND",
        "com.google.android.apps.play.billingtestcompanion.BillingOverrideService.BIND",
        "com.digitalturbine.ignite.cl.IgniteRemoteService",
        "com.google.android.exoplayer.downloadService.action.RESTART",
        "com.google.android.c2dm.intent.RECEIVE",
        "com.google.firebase.MESSAGING_EVENT",
        "androidx.browser.customtabs.CustomTabsService",
    ]
    for act in sdk_actions:
        text, n = re.subn(rf'\s*<action\s+android:name="{re.escape(act)}"\s*/>', "", text)
        total_removed += n

    # 6. 移除 Android 13+ 不支持的属性
    for attr in (
        "android:appComponentFactory", "android:dataExtractionRules",
        "android:enableOnBackInvokedCallback", "android:fullBackupContent",
    ):
        text, n = re.subn(rf'\s+{attr}="[^"]*"', "", text)
        total_removed += n

    # 7. 移除 configChanges 中的 colorMode/fontWeightAdjustment
    text = re.sub(r'(android:configChanges="[^"]*)colorMode\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?colorMode', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)fontWeightAdjustment\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?fontWeightAdjustment', r'\1', text)

    # 8. 修复 Application 类（SafeDK 等已删 SDK 的 Application → com.android.boot.App）
    text = re.sub(
        r'android:name="com\.safedk\.android\.SafeDKApplication"',
        'android:name="com.android.boot.App"',
        text,
    )
    if 'android:name="com.android.boot.App"' not in text:
        m = re.search(r'<application([^>]+)>', text)
        if m and 'android:name=' not in m.group(1):
            text = text.replace("<application", '<application android:name="com.android.boot.App"', 1)

    # Unity Player 必须启用硬件加速，否则会出现 Activity 存活但纯白屏。
    text = text.replace('android:hardwareAccelerated="false"', 'android:hardwareAccelerated="true"')

    text = text.replace('android:name="unity.splash-enable" android:value="true"', 'android:name="unity.splash-enable" android:value="false"')

    # 9. 移除空的 intent-filter / intent
    # [FLOWFIX] 支持带属性的空 intent-filter（如 FirebaseMessagingService 的
    # <intent-filter android:priority="-500"></intent-filter>），且容忍内部空白/换行。
    # [FLOWFIX 2026-08-20] 原正则 \s* 不跨换行，移除 action 后遗留
    # "<intent-filter>\n            </intent-filter>" 空块未能清除 → Manifest merger 报错。
    text = re.sub(r'<intent-filter[^>]*>\s*?</intent-filter>', '', text, flags=re.S)
    text = re.sub(r'<intent>\s*?</intent>', '', text, flags=re.S)

    manifest_path.write_text(text, encoding="utf-8")
    log_success(f"AndroidManifest.xml 已清理: {manifest_path}（移除 {total_removed} 项）")
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", help="项目名")
    parser.add_argument("--type", default="", help="引擎类型（[FLOWFIX] §3 父目录规则）")
    parser.add_argument("--apk", help="APK 路径")
    args = parser.parse_args()

    if args.apk:
        setup_paths_from_apk(args.apk, type=args.type or os.environ.get("TYPE"))
    elif args.name:
        setup_paths_from_name(args.name, type=args.type or os.environ.get("TYPE"))
    else:
        log_error("需要 --apk 或 --name")
        return 1

    name = _name()
    mp = _manifest_path(name)

    log_step(f"清理 AndroidManifest 第三方 SDK 引用 ({name})")

    if not clean_manifest(mp):
        return 1

    register_artifact(str(mp), "file", "AndroidManifest（清理后）", name=name)
    log_success(f"manifest 清理完成: {mp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
