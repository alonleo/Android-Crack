#!/usr/bin/env python3
"""
stage-09-remove-sdks-extra.py — RealmDefenseHeroLegendsTD 专项 SDK 清理
针对此 APK 的 Facebook/AppsFlyer/IronSource/Play Games/Play Billing/UniWebView 清理。

用法: python3 stage-09-remove-sdks-extra.py <项目名>
"""
import sys, os, re, shutil

REPO = "/home/leo/文档/android-crack"

def log_info(msg):  print(f"[INFO]  {msg}")
def log_warn(msg):  print(f"[WARN]  {msg}")
def log_ok(msg):    print(f"[OK]    {msg}")
def log_step(msg):  print(f"\n== {msg} ==")

def remove_manifest_entries(name):
    """清理 AndroidManifest.xml 中的 SDK 引用 — 块级删除"""
    log_step("清理 AndroidManifest.xml 块级 SDK 引用")
    manifest = f"{REPO}/crackings/<type>/{name}/project/app/src/main/AndroidManifest.xml"
    if not os.path.isfile(manifest):
        log_warn(f"AndroidManifest.xml 不存在: {manifest}")
        return
    with open(manifest) as f:
        content = f.read()
    original_len = len(content)

    # 块级删除规则（每个块以 <element ...> 开始，/> 或 </element> 结束）
    block_patterns = {
        "Facebook Activities (FBUnity*)": r'<activity[^>]*com\.facebook\.unity\.FB[^>]*(?:/>|</activity>)',
        "Facebook Activities (com.facebook.*)": r'<activity[^>]*com\.facebook\.(?!katana)[^>]*(?:/>|</activity>)',
        "Facebook Providers": r'<provider[^>]*com\.facebook\.[^>]*(?:/>|</provider>)',
        "Facebook Receivers": r'<receiver[^>]*com\.facebook\.[^>]*(?:/>|</receiver>)',
        "Facebook Meta-Data": r'<meta-data[^>]*com\.facebook\.sdk\.[^>]*/>',
        "Facebook Queries": r'<package[^>]*com\.facebook\.katana[^>]*/>',
        "AppsFlyer Receiver": r'<receiver[^>]*com\.appsflyer\.[^>]*(?:/>|</receiver>)',
        "AppsFlyer Action": r'<action[^>]*com\.appsflyer\.referrer\.INSTALL_PROVIDER[^>]*/>',
        "IronSource Activities": r'<activity[^>]*com\.ironsource\.[^>]*(?:/>|</activity>)',
        "IronSource Providers": r'<provider[^>]*com\.ironsource\.[^>]*(?:/>|</provider>)',
        "IronSource Meta-Data": r'<meta-data[^>]*com\.unity3d\.services\.core\.configuration\.AdsSdkInitializer[^>]*/>',
        "Unity Ads Activities": r'<activity[^>]*com\.unity3d\.services\.ads\.adunit\.[^>]*(?:/>|</activity>)',
        "Unity Ads Activity (adplayer)": r'<activity[^>]*com\.unity3d\.ads\.adplayer\.[^>]*(?:/>|</activity>)',
        "Google Play Games Activity (NativeBridge)": r'<activity[^>]*com\.google\.games\.bridge\.NativeBridgeActivity[^>]*(?:/>|</activity>)',
        "Google Play Games Activity (GenericResolution)": r'<activity[^>]*com\.google\.games\.bridge\.GenericResolutionActivity[^>]*</activity>',
        "Google Play Games Meta-Data (APP_ID)": r'<meta-data[^>]*com\.google\.android\.gms\.games\.APP_ID[^>]*/>',
        "Google Play Games Meta-Data (unityVersion)": r'<meta-data[^>]*com\.google\.android\.gms\.games\.unityVersion[^>]*/>',
        "Google Sign-In Activity": r'<activity[^>]*com\.google\.android\.gms\.auth\.api\.signin\.internal\.SignInHubActivity[^>]*(?:/>|</activity>)',
        "Google Sign-In Service": r'<service[^>]*com\.google\.android\.gms\.auth\.api\.signin\.RevocationBoundService[^>]*(?:/>|</service>)',
        "Google Sign-In Permission": r'<uses-permission[^>]*com\.google\.android\.gms\.permission\.AD_ID[^>]*/>',
        "Google Play Billing Activity (ProxyBilling)": r'<activity[^>]*com\.android\.billingclient\.api\.ProxyBillingActivity[^>]*(?:/>|</activity>)',
        "Google Play Billing Meta-Data": r'<meta-data[^>]*com\.google\.android\.play\.billingclient\.version[^>]*/>',
        "Google Play Core Service (AssetPack)": r'<service[^>]*com\.google\.android\.play\.core\.assetpacks\.[^>]*(?:/>|</service>)',
        "Google Play Core Activity (PlayCoreDialog)": r'<activity[^>]*com\.google\.android\.play\.core\.common\.PlayCoreDialogWrapperActivity[^>]*(?:/>|</activity>)',
        "UniWebView Activity": r'<activity[^>]*com\.onevcat\.uniwebview\.UniWebViewProxyActivity[^>]*(?:/>|</activity>)',
        "UniWebView Provider": r'<provider[^>]*com\.onevcat\.uniwebview\.[^>]*(?:/>|</provider>)',
        "Google API Activity (GoogleApiActivity)": r'<activity[^>]*com\.google\.android\.gms\.common\.api\.GoogleApiActivity[^>]*(?:/>|</activity>)',
        "Google Data Transport Service": r'<service[^>]*com\.google\.android\.datatransport\.runtime\.[^>]*(?:/>|</service>)',
        "Google Data Transport Receiver": r'<receiver[^>]*com\.google\.android\.datatransport\.runtime\.[^>]*(?:/>|</receiver>)',
        "Google Play Services Version Meta": r'<meta-data[^>]*com\.google\.android\.gms\.version[^>]*/>',
        "AppsFlyer Backup Rules": r'android:fullBackupContent="[^"]*appsflyer[^"]*"',
        "Google Play Services Referrer Permission": r'<uses-permission[^>]*com\.google\.android\.finsky\.permission\.BIND_GET_INSTALL_REFERRER_SERVICE[^>]*/>',
        "Play Billing Permission": r'<uses-permission[^>]*com\.android\.vending\.BILLING[^>]*/>',
        "Foreground Service Permissions": r'<uses-permission[^>]*android\.permission\.FOREGROUND_SERVICE[^>]*/>',
        "Foreground Service DataSync Permission": r'<uses-permission[^>]*android\.permission\.FOREGROUND_SERVICE_DATA_SYNC[^>]*/>',
        "AdServices Topics Permission": r'<uses-permission[^>]*android\.permission\.ACCESS_ADSERVICES_TOPICS[^>]*/>',
        "AdServices Attribution Permission": r'<uses-permission[^>]*android\.permission\.ACCESS_ADSERVICES_ATTRIBUTION[^>]*/>',
    }

    removed = 0
    for label, pattern in block_patterns.items():
        new_content, n = re.subn(pattern, '', content, flags=re.DOTALL)
        if n > 0:
            log_info(f"  {label}: 删除 {n} 个块")
            content = new_content
            removed += n

    # 清理遗留的 <queries> 空块（含 SDK 引用被删后）
    content = re.sub(r'<queries>\s*(?:<intent>.*?</intent>\s*)*</queries>', '', content, flags=re.DOTALL)
    content = re.sub(r'<intent>\s*<action[^>]*com\.appsflyer\.referrer\.INSTALL_PROVIDER[^>]*/>\s*</intent>', '', content)
    content = re.sub(r'<intent>\s*<action[^>]*com\.android\.vending\.billing\.InAppBillingService\.BIND[^>]*/>\s*</intent>', '', content)
    content = re.sub(r'<intent>\s*<action[^>]*com\.google\.android\.apps\.play\.billingtestcompanion\.BillingOverrideService\.BIND[^>]*/>\s*</intent>', '', content)
    # 清理空 queries 块
    content = re.sub(r'<queries>\s*</queries>', '', content)

    # 清理空行
    content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)

    if content != open(manifest).read():
        with open(manifest, 'w') as f:
            f.write(content)
        log_ok(f"AndroidManifest.xml 清理完成: {original_len - len(content)} bytes removed, {removed} blocks")
    else:
        log_info("AndroidManifest.xml 无需修改")

def remove_sdk_smali_dirs(name):
    """删除 smali 中的 SDK 目录"""
    log_step("删除 smali 中 SDK 目录")
    out_dir = f"{REPO}/crackings/<type>/{name}/project/app/src/main"
    smali_dirs = ['smali', 'smali_classes2', 'smali_classes3', 'smali_classes4', 'smali_classes5']
    sdk_paths = [
        'com/facebook',
        'com/appsflyer',
        'com/amplitude',
        'com/SmileSoft',
        'com/babeltimeus',  # may keep some
        'com/google/ads',
        'com/google/android/gms/ads',
        'com/google/android/gms/games',
        'com/google/android/gms/auth',
        'com/google/android/gms/signin',
        'com/google/firebase',
        'com/google/android/gms/tasks',
        'com/google/android/gms/measurement',
        'com/google/android/gms/internal',
        'com/google/android/gms/common/internal',
        'com/google/android/gms/flags',
        'com/google/android/gms/dynamite',
        'com/google/android/gms/oss',
        'com/google/android/gms/base',
        'com/google/android/gms/clearcut',
        'com/google/android/gms/location',
        'com/google/android/gms/maps',
        'com/google/android/gms/measurement',
        'com/google/android/gms/phenotype',
        'com/google/android/gms/recaptcha',
        'com/google/android/gms/remote',
        'com/google/android/gms/security',
        'com/google/android/gms/stats',
        'com/google/android/gms/tagmanager',
        'com/google/android/gms/vision',
        'com/google/android/gms/wallet',
        'com/ironsource',
        'com/iab',
        'com/onevcat',
        'com/unity3d/ads',
        'com/unity3d/services',
        'com/unity3d/ironsourceads',
        'com/unity3d/mediation',
        'com/unity3d/scar',
        'com/unity3d/purchasing',
        'com/unity3d/androidnotifications',
        'androidx/room',
    ]
    keep_paths = [
        'com/google/android/gms/common',  # 保留基础
    ]
    removed_count = 0
    for sd in smali_dirs:
        full = f"{out_dir}/{sd}"
        if not os.path.isdir(full):
            continue
        for p in sdk_paths:
            target = f"{full}/{p}"
            if os.path.isdir(target):
                shutil.rmtree(target)
                log_info(f"  删除: {sd}/{p}")
                removed_count += 1
    log_ok(f"共删除 {removed_count} 个 SDK smali 目录")

def remove_sdk_assets(name):
    """删除 SDK 关联的 assets 目录"""
    log_step("删除 SDK assets")
    assets = f"{REPO}/crackings/<type>/{name}/project/app/src/main/assets"
    if not os.path.isdir(assets):
        log_info("assets 目录不存在")
        return
    sdk_dirs = [
        'com/applovin', 'com/appsflyer', 'com/facebook',
        'com/unity3d', 'com/ironsource', 'ad-viewer',
    ]
    removed = 0
    for d in sdk_dirs:
        target = f"{assets}/{d}"
        if os.path.isdir(target):
            shutil.rmtree(target)
            log_info(f"  删除: assets/{d}")
            removed += 1
    log_ok(f"共删除 {removed} 个 SDK assets 目录")

def remove_sdk_so(name):
    """删除 SDK 关联的 .so 文件"""
    log_step("删除 SDK .so 文件")
    jnilibs = f"{REPO}/crackings/<type>/{name}/project/app/src/main/jniLibs"
    if not os.path.isdir(jnilibs):
        log_info("jniLibs 不存在")
        return
    patterns = ['*applovin*', '*Firebase*', '*firebase*', '*tapjoy*', '*inmobi*', '*vungle*', '*adcolony*']
    removed = 0
    import glob
    for arch in os.listdir(jnilibs):
        arch_dir = f"{jnilibs}/{arch}"
        if not os.path.isdir(arch_dir):
            continue
        for p in patterns:
            for f in glob.glob(f"{arch_dir}/{p}"):
                os.remove(f)
                log_info(f"  删除: jniLibs/{arch}/{os.path.basename(f)}")
                removed += 1
    log_ok(f"共删除 {removed} 个 .so 文件")

def cleanup_multi_language(name):
    """清理多语言资源，只保留 values/ 和 values-zh-rCN/"""
    log_step("清理多语言资源")
    res_dir = f"{REPO}/crackings/<type>/{name}/project/app/src/main/res"
    if not os.path.isdir(res_dir):
        return
    keep_re = re.compile(r'values-(land|night|v\d|sw\d|h\d{2,}|xlarge|large|watch|port|hdpi|x?hdpi|mdpi|ldpi|anydpi|tvdpi|nn\d|car|desktop|notnight)')
    removed = 0
    for d in os.listdir(res_dir):
        if not d.startswith('values-'):
            continue
        if keep_re.match(d):
            continue
        if d == 'values-zh-rCN':
            continue
        target = f"{res_dir}/{d}"
        if os.path.isdir(target):
            shutil.rmtree(target)
            log_info(f"  删除: {d}")
            removed += 1
    log_ok(f"共删除 {removed} 个多语言目录")

def verify(name):
    """验证残留 SDK 引用"""
    log_step("验证残留 SDK 引用")
    manifest = f"{REPO}/crackings/<type>/{name}/project/app/src/main/AndroidManifest.xml"
    if not os.path.isfile(manifest):
        return
    with open(manifest) as f:
        content = f.read()
    checks = [
        'com.facebook', 'com.appsflyer', 'com.tapjoy', 'com.applovin',
        'com.ironsource', 'com.vungle', 'com.inmobi',
        'com.unity3d.ads', 'com.unity3d.services', 'com.unity3d.ironsourceads',
        'com.onevcat', 'com.google.android.gms.games', 'com.google.firebase',
        'com.android.billingclient', 'com.google.android.play.core',
    ]
    issues = 0
    for c in checks:
        n = len(re.findall(c, content, re.I))
        if n > 0:
            log_warn(f"  残留: {c} ({n} 处)")
            issues += 1
    if issues == 0:
        log_ok("✅ 无残留 SDK 引用")
    else:
        log_warn(f"⚠️ 残留 {issues} 类 SDK 引用")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 stage-09-remove-sdks-extra.py <项目名>")
        sys.exit(1)
    name = sys.argv[1]
    remove_manifest_entries(name)
    remove_sdk_smali_dirs(name)
    remove_sdk_assets(name)
    remove_sdk_so(name)
    cleanup_multi_language(name)
    verify(name)
    log_ok("\n✅ 阶段 09 增强清理完成")
