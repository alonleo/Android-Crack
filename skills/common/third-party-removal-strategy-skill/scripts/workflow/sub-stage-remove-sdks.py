#!/usr/bin/env python3
"""
stage-09-remove-sdks.py — 阶段 09: 第三方 SDK 移除
清理 AndroidManifest.xml、assets、jniLibs 中的广告/分析 SDK。

用法: python3 stage-09-remove-sdks.py <项目名>
"""
import sys, os, re, shutil, subprocess

REPO = "/home/leo/文档/android-crack"

def log_info(msg):  print(f"[INFO]  {msg}")
def log_warn(msg):  print(f"[WARN]  {msg}")
def log_ok(msg):    print(f"[OK]    {msg}")
def log_step(msg):  print(f"\n== {msg} ==")
def die(msg):       print(f"[ERROR] {msg}"); sys.exit(1)

def remove_sdk_manifest_entries(name):
    """清理 AndroidManifest.xml 中的 SDK 引用"""
    log_step("清理 AndroidManifest.xml SDK 引用")
    
    manifest = f"{REPO}/crackings/<type>/{name}/project/app/src/main/AndroidManifest.xml"
    if not os.path.isfile(manifest):
        die(f"AndroidManifest.xml 不存在: {manifest}")
    
    with open(manifest) as f:
        content = f.read()
    
    original = content
    
    # 要删除的 SDK 条目模式（整行或块）
    remove_patterns = {
        "Unity Ads": [
            r'<activity[^>]*com\.unity3d\.services\.ads\.adunit\.[^>]*>',
            r'<activity[^>]*com\.unity3d\.ads\.adplayer\.[^>]*>',
            r'<provider[^>]*AdsSdkInitializer[^>]*>.*?</provider>',
        ],
        "IronSource": [
            r'<activity[^>]*com\.ironsource\.sdk\.controller\.[^>]*>',
            r'<activity[^>]*com\.ironsource\.mediationsdk\.testSuite\.[^>]*>.*?</activity>',
            r'<provider[^>]*IronsourceLifecycleProvider[^>]*/>',
            r'<provider[^>]*LevelPlayActivityLifecycleProvider[^>]*/>',
        ],
        "Vungle": [
            r'<activity[^>]*com\.vungle\.ads\.internal\.ui\.[^>]*>',
            r'<provider[^>]*com\.vungle\.ads\.VungleProvider[^>]*/>',
        ],
        "InMobi": [
            r'<activity[^>]*com\.inmobi\.ads\.rendering\.[^>]*>',
        ],
        "Google Play Services (保留基础)": [
            r'<meta-data android:name="com\.google\.android\.gms\.version"[^>]*/>',
        ],
    }
    
    for sdk_name, patterns in remove_patterns.items():
        for pattern in patterns:
            content = re.sub(pattern, '', content, flags=re.DOTALL)
    
    # 清理空的 <queries> 块（如果 SDK 删光了引用）
    content = re.sub(r'<queries>\s*</queries>', '', content)
    
    # 清理空行和多余换行
    content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
    
    if content != original:
        with open(manifest, 'w') as f:
            f.write(content)
        log_ok("AndroidManifest.xml SDK 条目已清理")
    else:
        log_info("AndroidManifest.xml 无需修改")

def remove_sdk_assets(name):
    """删除 SDK 关联的 assets 目录"""
    log_step("删除 SDK assets")
    assets_dir = f"{REPO}/crackings/<type>/{name}/project/app/src/main/assets"
    
    if not os.path.isdir(assets_dir):
        log_info("assets 目录不存在，跳过")
        return
    
    # SDK assets 目录模式
    sdk_asset_dirs = [
        "com/applovin",
        "com/appsflyer",
        "ad-viewer",
    ]
    
    for sdk_dir in sdk_asset_dirs:
        d = os.path.join(assets_dir, sdk_dir)
        if os.path.isdir(d):
            shutil.rmtree(d)
            log_info(f"  删除: assets/{sdk_dir}")

def remove_sdk_so_files(name):
    """删除 SDK 关联的 .so 文件"""
    log_step("删除 SDK .so 文件")
    jnilibs = f"{REPO}/crackings/<type>/{name}/project/app/src/main/jniLibs"
    
    if not os.path.isdir(jnilibs):
        log_info("jniLibs 不存在，跳过")
        return
    
    # SDK .so 文件模式
    sdk_so_patterns = [
        "*applovin*",
        "*FirebaseCpp*",
        "*firebase*",
        "*tapjoy*",
        "*inmobi*",
        "*vungle*",
    ]
    
    for arch in os.listdir(jnilibs):
        arch_dir = os.path.join(jnilibs, arch)
        if not os.path.isdir(arch_dir):
            continue
        for pattern in sdk_so_patterns:
            import glob
            for f in glob.glob(os.path.join(arch_dir, pattern)):
                os.remove(f)
                log_info(f"  删除: jniLibs/{arch}/{os.path.basename(f)}")

def cleanup_multi_language(name):
    """清理多语言资源，只保留 values/ 和 values-zh-rCN/"""
    log_step("清理多语言资源")
    res_dir = f"{REPO}/crackings/<type>/{name}/project/app/src/main/res"
    
    if not os.path.isdir(res_dir):
        log_info("res 目录不存在，跳过")
        return
    
    for d in os.listdir(res_dir):
        # 只处理 values-* 目录
        if not d.startswith("values-"):
            continue
        
        # 保留配置限定符目录（land, night, v*, sw*, h*, xlarge, large, watch, port, hdpi 等）
        if re.search(r'values-(land|night|v\d|sw\d|h\d{2,}|xlarge|large|watch|port|hdpi|x?hdpi|mdpi|ldpi|anydpi)', d):
            continue
        
        # 保留简体中文
        if d == "values-zh-rCN":
            continue
        
        # 删除其他语言
        full_path = os.path.join(res_dir, d)
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
            log_info(f"  删除: {d}")

def remove_residual_manifest_entries(name):
    """检查并删除残留的 SDK manifest 条目"""
    log_step("检查残留 SDK manifest 条目")
    
    manifest = f"{REPO}/crackings/<type>/{name}/project/app/src/main/AndroidManifest.xml"
    if not os.path.isfile(manifest):
        return
    
    with open(manifest) as f:
        content = f.read()
    
    # 检查残留的 SDK 引用
    residual_checks = [
        "com.yasirkula", "com.appsflyer", "com.tapjoy", "com.applovin",
        "ironsource", "vungle", "inmobi", "unity3d.services", "unity3d.ads",
        "firebase", "playgenesis", "applovin",
    ]
    
    found_any = False
    for check in residual_checks:
        if re.search(check, content, re.I):
            log_warn(f"  残留: {check}")
            found_any = True
    
    if not found_any:
        log_ok("无残留 SDK manifest 条目")
    
    # 验证 delete operations
    log_info("执行验证:")
    for check in residual_checks:
        count = len(re.findall(check, content, re.I))
        if count == 0:
            continue
        log_info(f"  grep '{check}': {count} 个（已处理）")

def _resolve_name(arg):
    """兼容：crack.py 传入 APK 路径 或 直接传项目名。"""
    import os as _os
    base = _os.path.basename(arg)
    if base.endswith('.apk') or _os.path.isfile(arg):
        name = base.replace('.apk', '').replace('.xapk', '')
        for suf in ['_APKPure', '_apkpure', '_ApkPure']:
            name = name.replace(suf, '')
        import re
        name = re.sub(r'_[0-9]+(\.[0-9]+)+$', '', name)
        name = re.sub(r'_v[0-9]+(\.[0-9]+)*$', '', name)
        name = re.sub(r'[^a-zA-Z0-9]+', ' ', name)
        name = ''.join(p if re.fullmatch(r'[A-Z]{2,}', p) else p.title() for p in name.split())
        return name or base
    return arg


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 stage-09-remove-sdks.py <项目名|APK路径>")
        sys.exit(1)
    
    name = _resolve_name(sys.argv[1])
    
    remove_sdk_manifest_entries(name)
    remove_sdk_assets(name)
    remove_sdk_so_files(name)
    cleanup_multi_language(name)
    remove_residual_manifest_entries(name)
    
    log_ok("\n✅ 阶段 09 完成")
