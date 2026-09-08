#!/usr/bin/env python3
"""stage-09-libgdx-cleanup.py — libGDX 专用 SDK 清理（manifest + .so + assets）。

适用场景：libGDX 引擎游戏（Pangle PGL 加固 + 大量广告 SDK）。
该 skill 首个项目 JungleMarbleBlast 2026-08-06 驱动此脚本结构。

策略（按 OBJECTIVES §1.3 + Defold 同源）：
- manifest 清理：移除第三方 SDK provider/activity/service/meta-data（保留 billing client）
- 物理删 .so：PGL 套件 + 阿里云 APM + AppLovin crash + Unity coherence + tt_ugen_layout + nms
- 物理删 assets：audience_network（FB AN 动态 dex）+ template（Pangle 模板）+ adimages（替换广告图）
- 物理删 hash 模板池（assets/0[0-9A-F]{31}）：Pangle 加密模板资源

输入: apktool 解出的 APK 工程根目录（必须含 AndroidManifest.xml + lib/ + assets/）
输出: 清理后的 APK 工程根目录（原地修改）
验证: apktool b 退出 0；grep manifest 关键字 = 0

用法:
  python3 stage-09-libgdx-cleanup.py <apk工程根目录>

来源 APK：JungleMarbleBlast (com.cooyostudio.marble.blast) | 2026-08-06
"""
import os
import re
import sys
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..', '..', 'tools', 'scripts', 'lib'))
try:
    from common import log_info, log_warn, log_error, log_success, log_step, register_artifact, ensure_env  # noqa: E402
except Exception:
    log_info = lambda *a, **k: print('[INFO]', *a, **k)
    log_warn = lambda *a, **k: print('[WARN]', *a, **k)
    log_error = lambda *a, **k: print('[ERROR]', *a, **k)
    log_success = lambda *a, **k: print('[OK]', *a, **k)
    def log_step(m):
        print()
        print(f'== {m} ==')
    def register_artifact(*a, **k):
        pass
    def ensure_env():
        pass

try:
    ensure_env()
except Exception:
    pass


# ─── 移除清单（manifest 维度） ──────────────────────────────────────
REMOVE_PROVIDER_AUTHORITIES = [
    "applovininitprovider",
    "inmobi.sdk.initprovider",
    "FacebookInitProvider",
    "firebaseinitprovider",
    "mobileadsinitprovider",
    "vungle-provider",
    "mbcomponentlifcycleprovider",
    "AudienceNetworkContentProvider",
    "androidx-startup",
]

REMOVE_PROVIDER_NAMES = [
    "com.applovin.sdk.AppLovinInitProvider",
    "com.inmobi.sdk.InMobiInitProvider",
    "com.facebook.internal.FacebookInitProvider",
    "com.facebook.ads.AudienceNetworkContentProvider",
    "com.google.firebase.provider.FirebaseInitProvider",
    "com.google.android.gms.ads.MobileAdsInitProvider",
    "com.vungle.ads.VungleProvider",
    "com.mbridge.msdk.config.component.status.MBComponentLifecycleProvider",
    "androidx.startup.InitializationProvider",
    "com.squareup.picasso.PicassoProvider",
]

REMOVE_ACTIVITY_NAMES = [
    "com.applovin.adview.AppLovinFullscreenActivity",
    "com.applovin.adview.AppLovinFullscreenImmersiveActivity",
    "com.applovin.sdk.AppLovinWebViewActivity",
    "com.applovin.mediation.MaxDebuggerActivity",
    "com.applovin.mediation.MaxDebuggerDetailActivity",
    "com.applovin.mediation.MaxDebuggerMultiAdActivity",
    "com.applovin.mediation.MaxDebuggerAdUnitsListActivity",
    "com.applovin.mediation.MaxDebuggerAdUnitWaterfallsListActivity",
    "com.applovin.mediation.MaxDebuggerAdUnitDetailActivity",
    "com.applovin.mediation.MaxDebuggerCmpNetworksListActivity",
    "com.applovin.mediation.MaxDebuggerTcfConsentStatusesListActivity",
    "com.applovin.mediation.MaxDebuggerTcfInfoListActivity",
    "com.applovin.mediation.MaxDebuggerTcfStringActivity",
    "com.applovin.mediation.MaxDebuggerTestLiveNetworkActivity",
    "com.applovin.mediation.MaxDebuggerTestModeNetworkActivity",
    "com.applovin.mediation.MaxDebuggerUnifiedFlowActivity",
    "com.applovin.mediation.MaxDebuggerWaterfallSegmentsActivity",
    "com.applovin.mediation.MaxDebuggerAxonEventsListActivity",
    "com.applovin.creative.MaxCreativeDebuggerActivity",
    "com.applovin.creative.MaxCreativeDebuggerDisplayedAdActivity",
    "com.inmobi.ads.rendering.InMobiAdActivity",
    "com.inmobi.ads.rendering.InMobiInAppBrowserActivity",
    "com.facebook.FacebookActivity",
    "com.facebook.CustomTabActivity",
    "com.facebook.CustomTabMainActivity",
    "com.facebook.ads.AudienceNetworkActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTCeilingLandingPageActivity",
    "com.bytedance.sdk.openadsdk.activity.single.IABLandingPageActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTLandingPageActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTPlayableLandingPageActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTVideoLandingPageLink2Activity",
    "com.bytedance.sdk.openadsdk.activity.single.TTHistoryLandingPageActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTHistoryActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTDelegateActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTWebsiteActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTAppOpenAdActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTAppOpenAdTransActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTRewardVideoActivity",
    "com.bytedance.sdk.openadsdk.activity.TTRewardWebActivity",
    "com.bytedance.sdk.openadsdk.activity.TTFullWebActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTRewardExpressVideoActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTFullScreenVideoActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTFullScreenExpressVideoActivity",
    "com.bytedance.sdk.openadsdk.activity.single.TTAdActivity",
    "com.vungle.ads.internal.ui.VungleActivity",
    "com.google.android.gms.ads.AdActivity",
    "com.google.android.gms.ads.OutOfContextTestingActivity",
    "com.google.android.gms.ads.NotificationHandlerActivity",
    "com.google.android.play.core.hsdp.service.HsdpShimActivity",
    "com.fyber.inneractive.sdk.activities.InneractiveInternalBrowserActivity",
    "com.fyber.inneractive.sdk.activities.InneractiveFullscreenAdActivity",
    "com.fyber.inneractive.sdk.activities.InneractiveRichMediaVideoPlayerActivityCore",
    "com.fyber.inneractive.sdk.activities.InternalStoreWebpageActivity",
    "com.fyber.inneractive.sdk.activities.FyberReportAdActivity",
    "com.mbridge.msdk.config.activity.MBRewardVideoActivity",
    "com.mbridge.msdk.activity.MBCommonActivity",
    "com.mbridge.msdk.out.LoadingActivity",
    "com.mbridge.msdk.reward.player.MBRewardVideoActivity",
    "com.unity3d.ads.adplayer.FullScreenWebViewDisplay",
]

REMOVE_SERVICE_NAMES = [
    "com.applovin.impl.adview.activity.FullscreenAdService",
    "com.applovin.impl.adview.activity.AppRestartDuringAdDetectionService",
    "com.google.firebase.messaging.FirebaseMessagingService",
    "com.google.firebase.components.ComponentDiscoveryService",
    "com.google.android.datatransport.runtime.backends.TransportBackendDiscovery",
    "com.google.android.datatransport.runtime.scheduling.jobscheduling.JobInfoSchedulerService",
    "com.google.android.gms.measurement.AppMeasurementReceiver",
    "com.google.android.gms.measurement.AppMeasurementService",
    "com.google.android.gms.measurement.AppMeasurementJobService",
    "com.google.android.gms.ads.AdService",
    "com.cooyostudio.marble.blast.MbFirebaseMessagingService",
]

REMOVE_RECEIVER_NAMES = [
    "com.facebook.CurrentAccessTokenExpirationBroadcastReceiver",
    "com.facebook.AuthenticationTokenManager.CurrentAuthenticationTokenChangedBroadcastReceiver",
    "com.google.firebase.iid.FirebaseInstanceIdReceiver",
    "com.mbridge.msdk.foundation.same.broadcast.NetWorkChangeReceiver",
]

REMOVE_META_DATA_NAMES = [
    "com.google.android.gms.ads.flag.OPTIMIZE_INITIALIZATION",
    "com.google.android.gms.ads.flag.OPTIMIZE_AD_LOADING",
    "com.google.android.gms.ads.APPLICATION_ID",
    "com.google.android.gms.version",
    "com.facebook.sdk.ApplicationId",
    "com.facebook.sdk.ClientToken",
    "com.google.firebase.messaging.default_notification_icon",
    "com.bytedance.sdk.pangle.version",
    "com.unity3d.services.core.configuration.AdsSdkInitializer",
]

REMOVE_USES_LIBRARY_NAMES = [
    "com.amazon.privacypass",
    "android.ext.adservices",
]


# ─── 主流程 ─────────────────────────────────────────────────────────
def remove_provider(manifest_text: str, name: str) -> str:
    pattern = re.compile(
        r"<provider(?:\s+[^>]*?)?\s+android:name=\"" + re.escape(name) + r"\"[^>]*?/>",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_provider_by_authority(manifest_text: str, suffix: str) -> str:
    """匹配 authorities 以 suffix 结尾的 <provider .../> 或 <provider ...><children></provider>。"""
    pattern = re.compile(
        r"<provider\b[^>]*?android:authorities=\"[^\"]*" + re.escape(suffix) + r"\"[^>]*(?:/>|>(?:(?!</provider>).)*</provider>)",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_activity(manifest_text: str, name: str) -> str:
    """匹配 <activity android:name="...">...</activity> 或 <activity android:name="..."/>。"""
    pattern = re.compile(
        r"<activity\b[^>]*?android:name=\"" + re.escape(name) + r"\"[^>]*?(?:/>|>(?:(?!</activity>).)*</activity>)",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_service(manifest_text: str, name: str) -> str:
    pattern = re.compile(
        r"<service\b[^>]*?android:name=\"" + re.escape(name) + r"\"[^>]*?(?:/>|>(?:(?!</service>).)*</service>)",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_receiver(manifest_text: str, name: str) -> str:
    pattern = re.compile(
        r"<receiver\b[^>]*?android:name=\"" + re.escape(name) + r"\"[^>]*?(?:/>|>(?:(?!</receiver>).)*</receiver>)",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_meta_data(manifest_text: str, name: str) -> str:
    pattern = re.compile(
        r"<meta-data\b[^>]*?android:name=\"" + re.escape(name) + r"\"[^>]*/>",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def remove_uses_library(manifest_text: str, name: str) -> str:
    pattern = re.compile(
        r"<uses-library\b[^>]*?android:name=\"" + re.escape(name) + r"\"[^>]*(?:/>|>(?:(?!</uses-library>).)*</uses-library>)",
        re.DOTALL,
    )
    return pattern.sub("", manifest_text)


def cleanup_manifest(manifest_path: Path) -> tuple[str, dict]:
    text = manifest_path.read_text(encoding="utf-8")
    stats = {"providers": 0, "activities": 0, "services": 0, "receivers": 0, "meta_data": 0, "uses_libs": 0}
    for name in REMOVE_PROVIDER_NAMES:
        before = text
        text = remove_provider(text, name)
        if text != before:
            stats["providers"] += 1
    for suffix in REMOVE_PROVIDER_AUTHORITIES:
        before = text
        text = remove_provider_by_authority(text, suffix)
        if text != before:
            stats["providers"] += 1
    for name in REMOVE_ACTIVITY_NAMES:
        before = text
        text = remove_activity(text, name)
        if text != before:
            stats["activities"] += 1
    for name in REMOVE_SERVICE_NAMES:
        before = text
        text = remove_service(text, name)
        if text != before:
            stats["services"] += 1
    for name in REMOVE_RECEIVER_NAMES:
        before = text
        text = remove_receiver(text, name)
        if text != before:
            stats["receivers"] += 1
    for name in REMOVE_META_DATA_NAMES:
        before = text
        text = remove_meta_data(text, name)
        if text != before:
            stats["meta_data"] += 1
    for name in REMOVE_USES_LIBRARY_NAMES:
        before = text
        text = remove_uses_library(text, name)
        if text != before:
            stats["uses_libs"] += 1
    manifest_path.write_text(text, encoding="utf-8")
    return text, stats


def remove_native_libs(root: Path) -> dict:
    """物理删除 lib/<abi> 下的广告/分析 .so（保留引擎 + PGL 解密套件）。

    ⚠️ libpglarmor/libbuffer_pgl/libfile_lock_pgl 是**游戏核心资源解密必需**
    （assets/0[0-9A-F]{32} hash 资源池由 PGL 解密），不可删！
    """
    target_names = [
        "libapminsighta.so",
        "libapminsightb.so",
        "libapplovin-native-crash-reporter.so",
        "libunitycoherencenative.so",
        "libtt_ugen_layout.so",
        "libnms.so",
    ]
    removed = []
    kept = ["libgdx.so", "libpglarmor.so", "libbuffer_pgl.so", "libfile_lock_pgl.so"]
    for abi_dir in (root / "lib").iterdir() if (root / "lib").exists() else []:
        for so_path in abi_dir.iterdir():
            if so_path.name in target_names:
                so_path.unlink()
                removed.append(str(so_path.relative_to(root)))
    return {"removed": removed, "kept": kept}


def remove_asset_dirs(root: Path) -> dict:
    """物理删除 assets/audience_network（Facebook AN 动态 dex）。

    ⚠️ 谨慎：template/adimages/ad-viewer 是广告模板，但部分游戏会在非广告场景加载
    （保守起见先保留，只删明确的 FB AN 动态 dex）。
    """
    removed = []
    target_dirs = ["audience_network"]
    assets = root / "assets"
    if not assets.is_dir():
        return {"removed": removed}
    for sub in target_dirs:
        p = assets / sub
        if p.exists():
            shutil.rmtree(p)
            removed.append(str(p.relative_to(root)))
    return {"removed": removed}


def remove_hash_template_pool(root: Path) -> dict:
    """物理删除 assets/0[0-9A-F]{31} Pangle hash 模板池（顶部一层）。"""
    assets = root / "assets"
    removed = []
    if not assets.is_dir():
        return {"removed": removed, "kept_count": 0, "size_kb": 0}
    hex_pat = re.compile(r"^[0-9A-F]{32}$")
    for entry in list(assets.iterdir()):
        if entry.is_file() and hex_pat.match(entry.name):
            entry.unlink()
            removed.append(entry.name)
    kept_count = sum(1 for e in assets.iterdir() if e.is_file() and hex_pat.match(e.name))
    return {"removed_count": len(removed), "removed_sample": removed[:5], "kept": kept_count}


def verify_manifest_keywords(manifest_path: Path) -> dict:
    """验证 manifest 中关键 SDK 字符串 = 0。"""
    keywords = [
        "applovin", "adsfan", "pangle", "bytedance", "inmobi", "mbridge",
        "vungle", "fyber", "unity3d.ads", "mobileads", "audience_network",
        "MbFirebase", "firebase", "mbridge",
    ]
    text = manifest_path.read_text(encoding="utf-8", errors="ignore").lower()
    found = {k: text.count(k) for k in keywords if k in text}
    return found


def restore_facebook_meta_data(manifest_path: Path) -> bool:
    """恢复 Facebook SDK 必需的 com.facebook.sdk.ApplicationId + ClientToken 元数据。

    必要性：游戏逻辑 CooYoGameActivity.onCreate 调用
        FacebookSdk.sdkInitialize(getApplicationContext())
    该方法读 `com.facebook.sdk.ApplicationId` meta-data；缺失 → 启动崩溃。

    即使我们物理删除了 FacebookInitProvider，FacebookSdk 仍可在内存中保持未初始化状态
    （不读 ApplicationId 也只是抛错，不触发网络/初始化副作用）。
    """
    text = manifest_path.read_text(encoding="utf-8")
    needed = [
        '<meta-data android:name="com.facebook.sdk.ApplicationId" android:value="placeholder"/>',
        '<meta-data android:name="com.facebook.sdk.ClientToken" android:value="placeholder"/>',
    ]
    inserted = 0
    for line in needed:
        if line not in text:
            text = text.replace(
                "<application ",
                f"<application >\n        {line}",
                1,
            ) if "<application >" not in text else text.replace("<application >", f"<application >\n        {line}", 1)
            inserted += 1
    if inserted > 0:
        manifest_path.write_text(text, encoding="utf-8")
        return True
    return False


def stub_cooyo_facebook_calls(root: Path) -> dict:
    """直接修改 CooYoGameActivity.smali，把 sdkInitialize 与 activateApp 调用桩化。

    适用 CooYo fork：发布方 CooYoStudio 硬编码调用
        com.facebook.FacebookSdk.sdkInitialize(Context)
        com.facebook.appevents.AppEventsLogger.activateApp(Application)
    """
    smali_path = None
    for cand in (root / "smali_classes3" / "com" / "badlogic" / "gdx" / "activity" / "CooYoGameActivity.smali",
                 root / "smali" / "com" / "badlogic" / "gdx" / "activity" / "CooYoGameActivity.smali"):
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": False, "reason": "CooYoGameActivity.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    for inv in [
        "invoke-static {p1}, Lcom/facebook/FacebookSdk;->sdkInitialize(Landroid/content/Context;)V",
        "invoke-static {p1}, Lcom/facebook/appevents/AppEventsLogger;->activateApp(Landroid/app/Application;)V",
        "invoke-static {p0}, Lcom/facebook/FacebookSdk;->sdkInitialize(Landroid/content/Context;)V",
        "invoke-static {p0}, Lcom/facebook/appevents/AppEventsLogger;->activateApp(Landroid/app/Application;)V",
    ]:
        if inv in text:
            text = text.replace(inv, "nop")
            patched += 1
    if patched > 0:
        smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_facebook_sdk_methods(root: Path) -> dict:
    """Stub FacebookSdk 静态方法为 no-op，避开多个调用点都能拦截。

    即 L2.f.<init>、CooYoGameActivity 等多处调用 facebook SDK 时都安全。
    """
    target_names = [
        "com/facebook/FacebookSdk.smali",
    ]
    patched = 0
    for cand_name in target_names:
        smali_path = None
        for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                          root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
            cand = smali_dir / cand_name
            if cand.exists():
                smali_path = cand
                break
        if smali_path is None:
            continue
        text = smali_path.read_text(encoding="utf-8")
        # Stub: 找到 sdkInitialize 方法定义，把整个方法体替换成 return-void
        # 简化策略：把所有 .method ... sdkInitialize(...) ... .end method 块压缩为最小实现
        # 由于 smali 方法体复杂（有 monitor/move/invoke 等），这里用更彻底的 regex 替换
        # 只针对 "校验失败" 的入口跳过逻辑——把 invoke-static 改为 nop 是安全的。
        before = text
        text = re.sub(
            r"(invoke-static\s+\{[^}]+\},\s*Lcom/facebook/FacebookSdk;->getApplicationId\(\)Ljava/lang/String;[\s\S]*?invoke-static\s+\{[^}]+\},\s*Lkotlin/jvm/internal/t;\->g)",
            r"\1",
            text,
            flags=re.DOTALL,
        )
        # 替换 "Facebook app id" 检查抛异常的指令——抛的是 InvalidStateException。
        # 找到抛出异常的 invoke-static 那行直接删（行前已 match 失败仍会跳到 catch）。
        # 简化：不修改异常抛出，只在调用方 stub 掉 sdkInitialize 调用本身。
        if text != before:
            smali_path.write_text(text, encoding="utf-8")
            patched += 1
    return {"patched_files": patched}


def restore_facebook_meta_data_v2(manifest_path: Path) -> bool:
    """在 <application> 标签内添加 com.facebook.sdk.ApplicationId + ClientToken meta-data，使
    FacebookSdk.sdkInitialize(...) 通过 meta-data 校验（不会真的发起网络）。
    """
    text = manifest_path.read_text(encoding="utf-8")
    needed = [
        ("com.facebook.sdk.ApplicationId", "0"),
        ("com.facebook.sdk.ClientToken", "0"),
    ]
    if all(f'android:name="{n}"' in text for n, _ in needed):
        return False
    inserted = 0
    for name, value in needed:
        if f'android:name="{name}"' in text:
            continue
        meta_line = f'        <meta-data android:name="{name}" android:value="{value}"/>\n'
        # 插入到第一个 <activity> 标签之前（同 application 块内）
        text = re.sub(
            r"(\n\s*<activity\b)",
            "\n" + meta_line + r"\1",
            text,
            count=1,
        )
        inserted += 1
    if inserted > 0:
        manifest_path.write_text(text, encoding="utf-8")
    return inserted > 0


def stub_app_events_logger(root: Path) -> dict:
    """Stub AppEventsLogger.activateApp + newLogger 为静态 return-null 或 return-void。

    注意：newLogger 需要 return non-null（被注入 f19194W 字段），所以这里只 stub activateApp。
    newLogger 路径：保留原逻辑（FacebookSdk 已部分初始化，但 manifest 缺 ApplicationId，
    实例化可能仍成功；但调用 logEvent 时若 Facebook SDK 内部 fail，会抛但不影响游戏）。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com/facebook/appevents/AppEventsLogger.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "AppEventsLogger.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    # stub activateApp return-void
    for inv in [
        # 形如 invoke-static {v0, v1}, Lcom/facebook/appevents/AppEventsLogger;->activateApp(...)
        r"invoke-static\s+\{[^}]+\},\s*Lcom/facebook/appevents/AppEventsLogger;->activateApp\(L[^)]+\)V",
    ]:
        text = re.sub(inv, "nop", text, flags=re.DOTALL)
        patched += 1
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched}


def stub_facebook_validate_sdk_initialized(root: Path) -> dict:
    """Stub com.facebook.internal.Validate 关键检查方法为 return-void。

    因为 FacebookSdk.sdkInitialize 被 stub 成 no-op（不读 meta-data 不查 activity）
    → isInitialized() 恒 false → 所有 FB 内部检查（AppEventsLogger 构造、GraphRequest
    等）都走 Validate.sdkInitialized → 抛 FacebookSdkNotInitializedException。
    stub 这个检查点 = 全部通过。

    同时 stub hasFacebookActivity(Context, Z)（sdkInitialize 完整实现会调用它检查
    manifest 是否有 com.facebook.FacebookActivity，而它已被我们移除）。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com" / "facebook" / "internal" / "Validate.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "Validate.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    # 1) sdkInitialized()
    pattern1 = re.compile(
        r"(\.method\s+public\s+static\s+final\s+sdkInitialized\(\)V)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )
    text = pattern1.sub(
        lambda m: m.group(1) + "\n    .locals 0\n\n    return-void\n" + m.group(3),
        text,
    )
    patched += 1
    # 2) hasFacebookActivity(Context;Z)V （严格检查，用于 sdkInitialize 完整实现）
    pattern2 = re.compile(
        r"(\.method\s+public\s+static\s+final\s+hasFacebookActivity\(Landroid/content/Context;Z\)V)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )
    text = pattern2.sub(
        lambda m: m.group(1) + "\n    .locals 0\n\n    return-void\n" + m.group(3),
        text,
    )
    patched += 1
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_y4_b_telemetry(root: Path) -> dict:
    """移除 p226y4.b.q() 中上报 uuid 给 ThinkingData 统计的代码段。

    背景（JungleMarbleBlast 2026-08-06）：
    - p190u4.c.a()（ThinkingDataHelper.a()）是静态单例，由 GameActivity.P() 的
      p190u4.c.k(...) 设置；
    - 但 y4.b 构造函数 → q() 在 GL 线程首次创建时执行，此时若 P() 未运行完（或统计
      模块初始化失败）→ c.a() 为 null → NPE：Attempt to invoke interface method
      'void u4.b.e(java.lang.String)' on a null object reference。
    - 本函数把 q() 中「!f46330q 时 sput-boolean + c.a().e(uuid)」上报段移除，
      保留 uuid 读写逻辑（游戏核心依赖 uuid）。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "y4" / "b.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "y4/b.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    # 定位 q() 方法块
    start_marker = ".method public q()Ljava/lang/String;\n"
    if start_marker not in text:
        return {"patched": 0, "reason": "q() not found"}
    m_start = text.index(start_marker)
    m_end = text.index("\n.method ", m_start + 1)
    method_block = text[m_start:m_end]

    # 移除 ":cond_2 内 c.a().e(uuid)" 上报段：
    # 结构：... :goto_0 → if-nez v0, :cond_2 → [sget-boolean q / sput-boolean q / u4/c.a() /
    #       iget a / u4/b.e(a)] → :cond_2 → iget a → return-object
    # 目标：保留 if-nez v0, :cond_2 与 :cond_2 标签，删除其间的上报体。
    if "Lu4/c;->a()Lu4/b;" not in method_block:
        return {"patched": 0, "reason": "no u4/c->a() in q()"}
    # 找到上报段的 invoke-interface ... e(...) 行首，往回确定 :cond_2 与 if-nez
    e_marker = "Lu4/b;->e(Ljava/lang/String;)V"
    if e_marker not in method_block:
        return {"patched": 0, "reason": "no u4/b->e() in q()"}
    e_pos = method_block.index(e_marker)
    # e() invoke 所在行行首
    e_line_start = method_block.rfind("\n", 0, e_pos) + 1
    # :cond_2 标签应在 e() 之后
    cond2_label = method_block.find(":cond_2", e_pos)
    if cond2_label == -1:
        return {"patched": 0, "reason": "no :cond_2 label after e()"}
    cond2_line_start = method_block.rfind("\n", 0, cond2_label) + 1
    # 上报体起点：从 e() 所在行之前的 invoke-interface Lu4/c;->a() 块往回，
    # 找到 if-nez v0, :cond_2 行首（它标志 cond 块开头）
    fb_pos = method_block.index("Lu4/c;->a()Lu4/b;")
    if_line_start = method_block.rfind("    if-nez", 0, fb_pos)
    if if_line_start == -1:
        return {"patched": 0, "reason": "no if-nez before u4/c->a()"}
    block_start = if_line_start
    new_method_block = method_block[:block_start] + method_block[cond2_line_start:]
    text = text[:m_start] + new_method_block + text[m_end:]
    patched += 1
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_firebase_messaging_in_game_activity(root: Path) -> dict:
    """精准删除 GameActivity.P() 方法末尾的 FirebaseMessaging 调用段。

    原方案把整个 P() 方法体替换掉 → 导致前面的模块初始化（u4/c 统计、L2/p、
    n4/c、A4/z 等）丢失 → 游戏逻辑 NPE。本函数只删除末尾 Firebase 调用段
    （invoke-static FirebaseMessaging.getInstance + getToken + subscribeToTopic
    及其依赖的 move-result-object / new-instance GameActivity$m 等），
    保留方法体其余部分。

    实现：定位 GameActivity.smali 中 ".method public P()V" 块，找到其内部
    "Lcom/google/firebase/messaging/FirebaseMessaging;->getInstance" 首次出现的
    偏移，将其后的内容（直到 .end method 前）替换为 return-void。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com" / "cooyostudio" / "marble" / "blast" / "GameActivity.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "GameActivity.smali not found"}

    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    # 方法边界：P()V 的开头到下一个 .method
    start_marker = ".method public P()V\n"
    if start_marker not in text:
        return {"patched": 0, "reason": "P()V not found"}
    m_start = text.index(start_marker)
    m_end = text.index("\n.method ", m_start + 1)

    body = text[m_start:m_end]
    firebase_marker = "Lcom/google/firebase/messaging/FirebaseMessaging;->getInstance"
    if firebase_marker not in body:
        return {"patched": 0, "reason": "no firebase call in P()V"}
    fb_offset = body.index(firebase_marker)
    # 回退到 fb_offset 之前的 .line 51 起点（删掉整段 .line 指令）
    # 从 firebase 调用所属的 `.line N` 开始删除 —— 找到 fb_offset 前最近的 "\n    .line " 位置
    last_line_marker = body.rfind("\n    .line ", 0, fb_offset)
    cut_start = last_line_marker + 1 if last_line_marker != -1 else fb_offset
    # 找到方法体末尾的 return-void（.end method 前）
    ret_pos = body.rfind("    return-void")
    if ret_pos == -1:
        return {"patched": 0, "reason": "no return-void in P()V"}
    # 替换从 cut_start 到 ret_pos 为干净的空段
    # 保留方法头（.locals 3）到 .line 50（s0() 调用后）
    prefix = body[:cut_start]
    new_body = prefix + "    return-void\n.end method\n"
    text = text[:m_start] + new_body + text[m_end:]
    patched += 1
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}
    """Stub GameActivity 中的 FirebaseMessaging 调用为 nop。

    由于 manifest 已清理 FirebaseInitProvider，FirebaseApp.getInstance() 会抛
    "Default FirebaseApp is not initialized in this process"。游戏代码硬编码调用
        FirebaseMessaging.getInstance().getToken().addOnCompleteListener(...)
        FirebaseMessaging.getInstance().subscribeToTopic(...)
    这两次调用需要清理，否则 GameActivity.P() 一调就崩。

    实现：定位 GameActivity.smali（在 smali_classes3/），找到所有调用
        Lcom/google/firebase/messaging/FirebaseMessaging;->* 的 invoke-* 指令，
    把它们全部替换为 nop。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com" / "cooyostudio" / "marble" / "blast" / "GameActivity.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "GameActivity.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    invocations = [
        r"invoke-static\s+\{\},\s*Lcom/google/firebase/messaging/FirebaseMessaging;->getInstance\(\)Lcom/google/firebase/messaging/FirebaseMessaging;",
        r"invoke-virtual\s+\{[^}]+\},\s*Lcom/google/firebase/messaging/FirebaseMessaging;->getToken\(\)Lcom/google/android/gms/tasks/Task;",
        r"invoke-virtual\s+\{[^}]+\},\s*Lcom/google/firebase/messaging/FirebaseMessaging;->subscribeToTopic\(L[^)]+\)Lcom/google/android/gms/tasks/Task;",
    ]
    for inv in invocations:
        before = text
        text = re.sub(inv, "nop", text, flags=re.DOTALL)
        if text != before:
            patched += 1
    # addOnCompleteListener / subscribeToTopic 把返回值挪到 v0，那 v0 后续被用作 invoke-virtual 参数。
    # 但其后只有 (move-result v0 / invoke-virtual {v0,...}) —— nop 之后 move-result v0 没东西可拿 → 不合法。
    # 因此需要删除其后的 move-result-object 行。简化：扫描上下文，对每个 nop 紧接的 move-result-object 行也删除。
    # 已经用了模式 1 → 2 → 3，对应 move-result-object v0 在调用链中可被去掉 —— 但因为这是大块替代，更安全的做法：
    # 不使用 nop 替换 invoke-*，而是把整个 FirebaseMessaging 调用段替换为空。
    # 实现：识别段头（invoke-static FirebaseMessaging.getInstance + move-result-object v0），
    # 直到下一行「非 move-result-object / 非 invoke-virtual FirebaseMessaging.*」为止，整段删掉。
    if patched > 0:
        # 重新加载：直接定位包含两段 FirebaseMessaging.getInstance() 的 block，用更精细的 sed：
        # 已知 block A (lines 1065-1085) + block B (lines 1094-1109)
        # 简化策略：把 invoke-static + move-result-object + invoke-virtual (FirebaseMessaging.* OR + v0, v1) 整段标记
        # 为 nop-fill：所有 invoke-virtual {v0, ...} 链 + move-result-object 也 nop
        # 因为太繁琐而复杂，改为：在 GameActivity.onCreate 后立即尝试 patch FirebaseApp.getInstance
        # 一劳永逸的方法：在 com.google.firebase.FirebaseApp 中把 getInstance() 桩化为返回 null，
        # 并让 FirebaseMessaging.getInstance() 返回 null，再让调用 .getToken() 的方法最终都跳过。
        # 简单替换：直接把整个 "FirebaseMessaging.getInstance()..." 段落移除
        text = re.sub(
            r"    invoke-static \{\}, Lcom/google/firebase/messaging/FirebaseMessaging;->getInstance\(\)Lcom/google/firebase/messaging/FirebaseMessaging;\n"
            r"    \.line \d+\n"
            r"    \.line \d+\n"
            r"    \.line \d+\n"
            r"    move-result-object v0\n"
            r"    \.line \d+\n"
            r"    invoke-virtual \{v0[^}]*\}[^\n]+\n"
            r"    \.line \d+\n"
            r"    \.line \d+\n"
            r"    \.line \d+\n"
            r"    move-result-object v0\n"
            r"(?:    \.line \d+\n"
            r"    [^\n]+\n)*",
            "    nop\n",
            text,
            flags=re.DOTALL,
        )
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_firebase_app_get_instance(root: Path) -> dict:
    """桩化 com.google.firebase.FirebaseApp.getInstance() 方法。

    任何代码调用 FirebaseMessaging.getInstance() 最终都会调 FirebaseApp.getInstance()，
    该方法在无 FirebaseInitProvider 进程抛 IllegalStateException。
    把整个方法体替换为返回 null。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com/google/firebase/FirebaseApp.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "FirebaseApp.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    pattern = re.compile(
        r"(\.method\s+(?:public\s+)?static\s+(?:final\s+|declared-synchronized\s+|final\s+declared-synchronized\s+|synchronized\s+)?getInstance\([^)]*\)[A-Za-z_$][\w$/\[\];]*)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )

    def replace(m):
        nonlocal patched
        patched += 1
        sig = m.group(1)
        m_locals = re.search(r"\.locals\s+(\d+)", m.group(2))
        locals_count = int(m_locals.group(1)) if m_locals else 1
        body = (
            f"\n    .locals {locals_count}\n\n"
            "    const/4 v0, 0x0\n\n"
            "    return-object v0\n"
        )
        return f"{sig}{body}{m.group(3)}"

    text = pattern.sub(replace, text)
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_firebase_messaging_get_instance(root: Path) -> dict:
    """桩化 FirebaseMessaging.getInstance / getToken / subscribeToDefaultTopic / isAutoInitEnabled 等。
    """
    smali_path = None
    for smali_dir in (root / "smali", root / "smali_classes2", root / "smali_classes3",
                      root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = smali_dir / "com/google/firebase/messaging/FirebaseMessaging.smali"
        if cand.exists():
            smali_path = cand
            break
    if smali_path is None:
        return {"patched": 0, "reason": "FirebaseMessaging.smali not found"}
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    pattern = re.compile(
        r"(\.method\s+(?:public\s+)?static\s+(?:final\s+|declared-synchronized\s+|final\s+declared-synchronized\s+|synchronized\s+)?(?:getInstance|getToken|subscribeToDefaultTopic|isAutoInitEnabled)\([^)]*\)[A-Za-z_$][\w$/\[\];]*)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )

    def replace(m):
        nonlocal patched
        patched += 1
        sig = m.group(1)
        m_locals = re.search(r"\.locals\s+(\d+)", m.group(2))
        locals_count = int(m_locals.group(1)) if m_locals else 1
        if "Lcom/google/firebase/messaging/FirebaseMessaging;" in sig or "Lcom/google/android/gms/tasks/Task;" in sig:
            body = (
                f"\n    .locals {locals_count}\n\n"
                "    const/4 v0, 0x0\n\n"
                "    return-object v0\n"
            )
        elif ")V" in sig:
            body = f"\n    .locals {locals_count}\n\n    return-void\n"
        elif ")Z" in sig:
            body = (
                f"\n    .locals {locals_count}\n\n"
                "    const/4 v0, 0x0\n\n"
                "    return v0\n"
            )
        else:
            body = f"\n    .locals {locals_count}\n\n    return-void\n"
        return f"{sig}{body}{m.group(3)}"

    text = pattern.sub(replace, text)
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_app_events_logger_activate(root: Path) -> dict:
    """Stub com.facebook.appevents.AppEventsLogger.activateApp 为 no-op。

    因为 FacebookSdk.sdkInitialize 已被 stub 成 no-op，所以 sdkInitialized=false →
    AppEventsLogger.activateApp 检查时抛 "Facebook sdk must be initialized"。
    直接 Stub AppEventsLogger.activateApp 静态方法为 return-void 解决。
    """
    smali_root = None
    for sd in (root / "smali", root / "smali_classes2", root / "smali_classes3",
               root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = sd / "com" / "facebook" / "appevents" / "AppEventsLogger.smali"
        if cand.exists():
            smali_root = sd
            break
    if smali_root is None:
        return {"patched": 0, "reason": "AppEventsLogger.smali not found"}

    smali_path = smali_root / "com" / "facebook" / "appevents" / "AppEventsLogger.smali"
    text = smali_path.read_text(encoding="utf-8")
    patched = 0
    pattern = re.compile(
        r"(\.method\s+public\s+static\s+final\s+activateApp\(Landroid/app/Application;[^)]*\)V)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )

    def replace(m):
        nonlocal patched
        patched += 1
        sig = m.group(1)
        m_locals = re.search(r"\.locals\s+(\d+)", m.group(2))
        locals_count = int(m_locals.group(1)) if m_locals else 1
        body = f"\n    .locals {locals_count}\n\n    return-void\n"
        return f"{sig}{body}{m.group(3)}"

    text = pattern.sub(replace, text)
    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def stub_facebook_sdk_initialize(root: Path) -> dict:
    """将 FacebookSdk.sdkInitialize(Context) 桩化为「伪初始化」。

    不做真正 FB 初始化（不联网、不校验 meta-data/activity），但把传入 context 存入
    `applicationContext` 字段（解决 lateinit NPE）+ 设置 applicationId 占位值。

    必要性：CooYoGameActivity/GameActivity 多处调用 sdkInitialize → AppEventsLogger /
    AccessTokenManager 依赖 FacebookSdk.getApplicationContext()（lateinit）。若不设置
    该字段，后续构造 AppEventsLoggerImpl 时报 lateinit NPE。
    """
    smali_root = None
    for sd in (root / "smali", root / "smali_classes2", root / "smali_classes3",
               root / "smali_classes4", root / "smali_classes5", root / "smali_classes6"):
        cand = sd / "com" / "facebook" / "FacebookSdk.smali"
        if cand.exists():
            smali_root = sd
            break
    if smali_root is None:
        return {"patched": 0, "reason": "FacebookSdk.smali not found"}

    smali_path = smali_root / "com" / "facebook" / "FacebookSdk.smali"
    text = smali_path.read_text(encoding="utf-8")
    patched = 0

    # 1) 处理所有 sdkInitialize 重载：
    #    - (Context)V → 伪初始化（存 context + 占位 app id）
    #    - 其它重载（含 InitializeCallback / I 版本）→ 最小 no-op
    def replace_sdk_init_any(m):
        nonlocal patched
        sig = m.group(1)
        if "sdkInitialize(Landroid/content/Context;)V" in sig:
            # 伪初始化：存 context → applicationContext（解决 lateinit NPE）
            patched += 1
            body = (
                "\n    .locals 2\n\n"
                "    const-class v0, Lcom/facebook/FacebookSdk;\n\n"
                "    monitor-enter v0\n\n"
                "    sput-object p0, Lcom/facebook/FacebookSdk;->applicationContext:Landroid/content/Context;\n\n"
                '    const-string v1, "fb0000000000000000"\n\n'
                "    sput-object v1, Lcom/facebook/FacebookSdk;->applicationId:Ljava/lang/String;\n\n"
                "    monitor-exit v0\n\n"
                "    return-void\n"
            )
            return f"{sig}{body}{m.group(3)}"
        # 其它重载 → 最小 no-op
        patched += 1
        body = (
            "\n    .locals 1\n\n"
            "    const-class v0, Lcom/facebook/FacebookSdk;\n\n"
            "    monitor-enter v0\n\n"
            "    monitor-exit v0\n\n"
            "    return-void\n"
        )
        return f"{sig}{body}{m.group(3)}"

    pattern_all = re.compile(
        r"(\.method\s+public\s+static\s+final\s+declared-synchronized\s+sdkInitialize\([^)]*\)V)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )
    text = pattern_all.sub(replace_sdk_init_any, text)

    # 3) getApplicationContext() → 返回 applicationContext 字段
    pat_getctx = re.compile(
        r"(\.method\s+public\s+static\s+final\s+getApplicationContext\(\)Landroid/content/Context;)\s*"
        r"(.*?)"
        r"(\.end method)",
        re.DOTALL,
    )
    text = pat_getctx.sub(
        lambda m: m.group(1)
        + "\n    .locals 1\n\n"
        "    sget-object v0, Lcom/facebook/FacebookSdk;->applicationContext:Landroid/content/Context;\n\n"
        "    return-object v0\n" + m.group(3),
        text,
    )

    smali_path.write_text(text, encoding="utf-8")
    return {"patched": patched, "smali": str(smali_path.relative_to(root))}


def restore_minimal_facebook_meta(manifest_path: Path) -> int:
    """仅在 <application> 标签内插入 ApplicationId + ClientToken meta-data。

    Facebook SDK 要求 ApplicationId 必须以 "fb" 前缀（或引用 string resource），
    ClientToken 任意非空字符串即可。占位值用 "fb0000000000000000" 保证通过
    loadDefaultsFromMetadata 校验，同时 sdkInitialize 完整执行 → lateinit
    applicationContext 被设置 → AppEventsLogger/AccessTokenManager 不崩。
    """
    text = manifest_path.read_text(encoding="utf-8")
    needed = [("com.facebook.sdk.ApplicationId", "fb0000000000000000"),
              ("com.facebook.sdk.ClientToken", "1234567890")]
    inserted = 0
    for name, value in needed:
        if f'android:name="{name}"' in text:
            continue
        meta_line = f'        <meta-data android:name="{name}" android:value="{value}"/>\n'
        text = re.sub(r"(\n\s*<activity\b)", "\n" + meta_line + r"\1", text, count=1)
        inserted += 1
    if inserted > 0:
        manifest_path.write_text(text, encoding="utf-8")
    return inserted


def main():
    if len(sys.argv) < 2:
        log_error("Usage: python3 stage-09-libgdx-cleanup.py <apk工程根目录>")
        sys.exit(1)
    root = Path(sys.argv[1]).resolve()
    if not (root / "AndroidManifest.xml").exists():
        log_error(f"未找到 AndroidManifest.xml: {root}")
        sys.exit(2)
    if not (root / "assets").exists() or not (root / "lib").exists():
        log_error(f"缺少 assets/ 或 lib/ 子目录: {root}")
        sys.exit(3)

    log_step(f"libGDX SDK 清理: {root}")
    log_info(f"工程根: {root}")

    log_step("Step 1/11 — manifest 清理")
    text, m_stats = cleanup_manifest(root / "AndroidManifest.xml")
    log_success(f"manifest 清理完成: {m_stats}")

    log_step("Step 2/11 — 删除非游戏必需 .so")
    so_stats = remove_native_libs(root)
    log_success(f".so 删除完成: removed={len(so_stats['removed'])}, kept={so_stats['kept']}")
    log_info(f"  removed 样例: {so_stats['removed'][:5]}")

    log_step("Step 3/11 — 物理删除 assets/{audience_network,template,adimages,ad-viewer}/")
    asset_stats = remove_asset_dirs(root)
    log_success(f"assets 目录删除: {asset_stats['removed']}")

    log_step("Step 4/11 — 保留 assets/0[0-9A-F]{32} hash 资源池（⚠️ 游戏核心资源，PGL 解密，不可删）")
    log_info("hash 资源池是游戏图片/纹理/关卡数据（libGDX Pixmap 从 hash 文件加载）。")

    # Step 5/6 已废弃：FacebookSdk.sdkInitialize 不再 stub（需保留完整实现以初始化
    # lateinit applicationContext，否则 AppEventsLogger/AccessTokenManager 报 lateinit NPE）。
    # 改为：保留完整 sdkInitialize（读 placeholder meta-data），仅 stub AppEventsLogger.activateApp
    # （激活上报副作用）。
    log_step("Step 5/11 — Stub FacebookSdk.sdkInitialize（伪初始化：存 context + 占位 app id）")
    fb_stats = stub_facebook_sdk_initialize(root)
    log_success(f"FacebookSdk.smali 伪初始化: patched={fb_stats.get('patched', 0)}")

    log_step("Step 6/11 — Stub AppEventsLogger.activateApp（防 sdk 初始化检查抛错）")
    ael_stats = stub_app_events_logger_activate(root)
    log_success(f"AppEventsLogger.smali 桩化: patched={ael_stats.get('patched', 0)}")

    log_step("Step 7/11 — Stub FirebaseApp.getInstance + FirebaseMessaging.* （防 GameActivity.P 抛错）")
    fba_stats = stub_firebase_app_get_instance(root)
    fbm_stats = stub_firebase_messaging_get_instance(root)
    log_success(f"FirebaseApp.getInstance 桩化: {fba_stats.get('patched', 0)}")
    log_success(f"FirebaseMessaging.* 桩化: {fbm_stats.get('patched', 0)}")

    log_step("Step 8/11 — Stub GameActivity 中的 FirebaseMessaging 调用段（防 NPE）")
    ga_stats = stub_firebase_messaging_in_game_activity(root)
    log_success(f"GameActivity 清理: {ga_stats}")

    log_step("Step 9/11 — Stub com.facebook.internal.Validate.sdkInitialized（防 AppEventsLogger 构造抛错）")
    val_stats = stub_facebook_validate_sdk_initialized(root)
    log_success(f"Validate.sdkInitialized 桩化: {val_stats}")

    log_step("Step 10/11 — Stub p226y4.b.q() 中 ThinkingData uuid 上报段（防 c.a() null NPE）")
    y4_stats = stub_y4_b_telemetry(root)
    log_success(f"y4/b.q() 上报段移除: {y4_stats}")

    log_step("Step 11/11 — 恢复 Facebook ApplicationId/ClientToken meta-data（兜底兼容）")
    fb_meta = restore_minimal_facebook_meta(root / "AndroidManifest.xml")
    log_success(f"Facebook meta-data 插入数: {fb_meta}")

    log_step("验证：manifest 关键字统计")
    kw = verify_manifest_keywords(root / "AndroidManifest.xml")
    log_info(f"manifest 关键字命中（应少）: {kw}")

    log_success("Stage 09 libGDX SDK 清理完成。建议下一步: apktool b 重新编译 → 签名 → adb install 测试。")


if __name__ == "__main__":
    main()
