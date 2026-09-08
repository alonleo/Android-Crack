#!/usr/bin/env python3
"""rebuild-apk-from-apktool.py — apktool 重新打包流程固化。

适用场景：模板继承问题（原始 APK 含 UnityPlayerActivity / com.unity3d.player 等
原生 smali 类，但 FakerAndroid 编译不包含）。此时不应使用 FakerAndroid → Gradle
路径，而是直接基于原始 APK 用 apktool 解包 → 清理 manifest → 重新打包 → 签名。

流程：
  1. apktool d -f <原 APK> → <work_dir>
  2. 修复 AndroidManifest.xml（Application class、移除 SDK 引用、Android 13+ 属性、splits）
  3. apktool b <work_dir> → unsigned APK
  4. zipalign + apksigner → signed patched.apk

修复点（已验证 [FLOWFIX]）：
  - android:name="com.safedk.android.SafeDKApplication" → "android.app.Application"
    （SafeDK SDK 已删，原始 Application 引用必崩）
  - 删除所有第三方 SDK 的 activity/service/receiver/provider（类不存在）
  - 删除 Android 13+ 属性（appComponentFactory、dataExtractionRules、enableOnBackInvokedCallback）
  - 删除 splits 相关（requiredSplitTypes="base__abi"、splits.meta-data）
  - 删除空的 <intent></intent>、<intent-filter></intent-filter>

用法：
  python3 rebuild-apk-from-apktool.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
from common import (
    setup_paths_from_apk,
    setup_paths_from_name,
    ensure_dir,
    log_info,
    log_warn,
    log_step,
    log_success,
    log_error,
    register_artifact,
    append_status,
)


# 必须保留的 Activity
KEEP_ACTIVITIES = {"com.unity3d.player.UnityPlayerActivity"}


def _name() -> str:
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def _source_apk(name: str) -> Path:
    """返回可用于 apktool 重打包的源 APK 路径。

    优先: raw/{name}.apk（xapk 合并后）→ source.apk.md5 记录的原始 APK → raw/source-merged.apk
    """
    # [FLOWFIX] 优先从 source.apk.md5 解析原始 APK（适用于非 xapk 的单文件 APK）
    type_arg = os.environ.get("TYPE", "").strip()
    if type_arg:
        crack_dir = ROOT / "crackings" / type_arg / name
    else:
        crack_dir = ROOT / "crackings" / name
    md5_file = crack_dir / "source.apk.md5"
    if md5_file.is_file():
        for line in md5_file.read_text(encoding="utf-8").splitlines():
            if line.startswith("source="):
                src = line.split("=", 1)[1].strip()
                p = Path(src) if Path(src).is_absolute() else ROOT / src
                if p.is_file():
                    return p
    # raw/{name}.apk
    fat = crack_dir / "raw" / f"{name}.apk"
    if fat.is_file():
        return fat
    # raw/source-merged.apk
    merged = crack_dir / "raw" / "source-merged.apk"
    if merged.is_file():
        return merged
    # fallback: apks/ glob
    for apk in (ROOT / "apks").glob(f"*{name}*"):
        if apk.suffix.lower() == ".apk":
            return apk
    return Path()


def _apktool_cmd() -> str:
    return os.environ.get("APKTOOL") or shutil.which("apktool") or "apktool"


def _zipalign_cmd() -> str:
    return os.environ.get("ZIPALIGN") or shutil.which("zipalign") or "zipalign"


def _apksigner_cmd() -> str:
    return os.environ.get("APKSIGNER") or shutil.which("apksigner") or "apksigner"


def _keystore(name: str) -> Path:
    for candidate in (
        ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "my.keystore.jks",
        ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "my.keystore.jks",
    ):
        if candidate.is_file():
            return candidate
    sys.exit("my.keystore.jks 缺失，请先执行阶段26生成 keystore")


def apktool_decode(src: Path, work: Path) -> bool:
    """调用 apktool d 解包 APK。"""
    if work.is_dir() and any(work.iterdir()):
        shutil.rmtree(work)
    ensure_dir(work)
    cmd = [_apktool_cmd(), "d", "-f", "-o", str(work), str(src)]
    log_info(f"apktool d: {src.name} → {work}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log_error(f"apktool 解包失败: {res.stderr[-500:] if res.stderr else res.stdout[-500:]}")
        return False
    return (work / "AndroidManifest.xml").is_file()


def fix_manifest(manifest: Path) -> dict:
    """修复 AndroidManifest.xml，返回修复统计。"""
    if not manifest.is_file():
        log_error(f"AndroidManifest.xml 缺失: {manifest}")
        return {"removed": 0}

    text = manifest.read_text(encoding="utf-8", errors="ignore")
    stats = {"removed": 0, "fixed": 0}

    # 1. 移除第三方 SDK 的 activity/service/receiver/provider
    def remove_elements_with_content(text, tag, keep_names):
        pattern = re.compile(
            rf'<{tag}\b[^>]*?android:name="([^"]+)"[^>]*?(/>|>(?:.*?)</{tag}>)',
            re.DOTALL
        )
        matches = list(pattern.finditer(text))
        if not matches:
            return text, 0
        out = []
        pos = 0
        removed = 0
        for m in matches:
            name = m.group(1)
            if name not in keep_names:
                out.append(text[pos:m.start()])
                pos = m.end()
                removed += 1
        out.append(text[pos:])
        return "".join(out), removed

    # [FLOWFIX] 启动 Activity（MAIN+LAUNCHER intent-filter）必须保留，
    # 否则清 SDK 时把游戏入口（如 com.google.firebase.MessagingUnityPlayerActivity）删掉 → 无法启动。
    launcher_acts = set()
    for m in re.finditer(
        r'<activity\b[^>]*?android:name="([^"]+)"[^>]*>(?:(?!</activity>).)*?'
        r'android\.intent\.action\.MAIN(?:(?!</activity>).)*?</activity>',
        text,
        re.DOTALL,
    ):
        launcher_acts.add(m.group(1))
    keep_activities = KEEP_ACTIVITIES | launcher_acts
    log_info(f"保留 activity: {sorted(keep_activities)}")

    for tag in ("activity", "service", "receiver", "provider"):
        text, n = remove_elements_with_content(
            text, tag, keep_activities if tag == "activity" else set())
        stats["removed"] += n

    # 2. 移除 SDK 专用 uses-permission
    sdk_perms = [
        "com.applovin.array.apphub.permission.BIND_APPHUB_SERVICE",
        "com.google.android.finsky.permission.BIND_GET_INSTALL_REFERRER_SERVICE",
        "com.samsung.android.mapsagent.permission.READ_APP_INFO",
        "com.huawei.appmarket.service.commondata.permission.GET_COMMON_DATA",
    ]
    for perm in sdk_perms:
        text, n = re.subn(rf'\s*<uses-permission\s+android:name="{re.escape(perm)}"\s*/>', "", text)
        stats["removed"] += n

    # 3. 移除 SDK 专用 uses-feature
    sdk_features = ["android.hardware.vulkan", "android.hardware.touchscreen"]
    for feat in sdk_features:
        text, n = re.subn(rf'<uses-feature\s+android:name="{re.escape(feat)}"[^>]*/>', "", text)
        stats["removed"] += n

    # 4. 移除 queries 中的 SDK 包
    sdk_packages = [
        "com.facebook.katana", "com.instagram.android", "com.facebook.lite",
        "com.samsung.android.mapsagent", "com.android.chrome",
        "com.google.android.webview", "com.android.webview", "com.android.vending",
    ]
    for pkg in sdk_packages:
        text, n = re.subn(rf'<package\s+android:name="{re.escape(pkg)}"\s*/>', "", text)
        stats["removed"] += n

    # 5. 移除 meta-data 中的 SDK meta
    sdk_meta = [
        "com.google.android.gms.ads.APPLICATION_ID",
        "com.google.android.gms.ads.flag.OPTIMIZE_INITIALIZATION",
        "com.google.android.gms.ads.flag.OPTIMIZE_AD_LOADING",
        "com.my.target.autoInitMode", "com.oculus.always_draw_view_root",
        "com.bytedance.sdk.pangle.version", "com.google.unity.ads.UNITY_VERSION",
        "com.google.android.gms.version", "com.android.vending.splits.required",
        "com.android.stamp.source", "com.android.stamp.type",
        "com.android.vending.splits", "com.android.vending.derived.apk.id",
        "com.android.play.billingclient.version",
        "com.google.firebase.components:",
        "com.unity3d.services.core.configuration.AdsSdkInitializer",
    ]
    for meta in sdk_meta:
        text, n = re.subn(rf'<meta-data\s+android:name="{re.escape(meta)}"[^>]*/>', "", text)
        stats["removed"] += n

    # 6. 移除 SDK 专用 action
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
        text, n = re.subn(rf'<action\s+android:name="{re.escape(act)}"\s*/>', "", text)
        stats["removed"] += n

    # 7. 移除 Android 13+ 不支持的属性
    for attr in (
        "android:appComponentFactory",
        "android:dataExtractionRules",
        "android:enableOnBackInvokedCallback",
        "android:fullBackupContent",
    ):
        text, n = re.subn(rf'\s+{attr}="[^"]*"', "", text)
        stats["fixed"] += n

    # 8. 移除 configChanges 中的 colorMode/fontWeightAdjustment（API 23+ 不支持）
    text = re.sub(r'(android:configChanges="[^"]*)colorMode\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?colorMode', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)fontWeightAdjustment\|?', r'\1', text)
    text = re.sub(r'(android:configChanges="[^"]*)\|?fontWeightAdjustment', r'\1', text)

    # 9. 移除 splits 相关（关键修复：requiredSplitTypes 缺失会导致 INSTALL_FAILED_MISSING_SPLIT）
    text = text.replace(' android:requiredSplitTypes="base__abi"', '')
    text = text.replace(' android:splitTypes=""', '')

    # 10. 修复 Application 类（SafeDKApplication 等已删 SDK 的 Application 必须替换）
    text = re.sub(
        r'android:name="com\.safedk\.android\.SafeDKApplication"',
        'android:name="android.app.Application"',
        text,
    )

    # 11. 移除空的 intent/intent-filter
    text = re.sub(r'<intent>\s*</intent>', '', text)
    text = re.sub(r'<intent-filter>\s*</intent-filter>', '', text)

    # 12. 移除 standalone lib 属性
    text = re.sub(r'\s+android:fullBackupContent="[^"]*"', '', text)

    manifest.write_text(text, encoding="utf-8")
    return stats


def remove_unsafe_assets(work: Path) -> int:
    """移除已删 SDK 的 assets（Facebook audience_network 等）。"""
    removed = 0
    unsafe_dirs = ["audience_network", "vungle"]
    for d in unsafe_dirs:
        p = work / "assets" / d
        if p.is_dir():
            shutil.rmtree(p)
            log_info(f"移除 assets/{d}")
            removed += 1
    return removed


def apktool_build(work: Path, unsigned: Path) -> bool:
    """调用 apktool b 重新打包。"""
    cmd = [_apktool_cmd(), "b", str(work), "-o", str(unsigned)]
    log_info(f"apktool b: {work} → {unsigned.name}")
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        log_error(f"apktool 打包失败: {res.stderr[-500:] if res.stderr else res.stdout[-500:]}")
        return False
    return unsigned.is_file()


def zipalign_and_sign(unsigned: Path, signed: Path, keystore: Path) -> bool:
    """zipalign + apksigner 签名。

    [FLOWFIX] 每个项目自行生成 keystore（别名 jy / 密码 Ab123145），
    不再依赖统一模板 keystore 的 android 密码。
    """
    aligned = unsigned.parent / (unsigned.stem + "_aligned.apk")
    res = subprocess.run([_zipalign_cmd(), "-f", "4", str(unsigned), str(aligned)],
                         capture_output=True, text=True)
    if res.returncode != 0:
        log_error(f"zipalign 失败: {res.stderr}")
        return False

    res = subprocess.run(
        [_apksigner_cmd(), "sign",
         "--ks", str(keystore), "--ks-pass", "pass:Ab123145",
         "--key-pass", "pass:Ab123145", "--ks-key-alias", "jy",
         "--v1-signing-enabled", "true",
         "--v2-signing-enabled", "true",
         "--v3-signing-enabled", "true",
         "--out", str(signed), str(aligned)],
        capture_output=True, text=True
    )
    if res.returncode != 0:
        log_error(f"apksigner 失败: {res.stderr}")
        aligned.unlink(missing_ok=True)
        return False

    aligned.unlink(missing_ok=True)
    unsigned.unlink(missing_ok=True)
    return signed.is_file()


def rebuild(name: str) -> bool:
    """完整的重新打包流程。"""
    src = _source_apk(name)
    if not src.is_file():
        log_error(f"源 APK 缺失: {src}")
        return False

    keystore = _keystore(name)
    out_dir = ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name))
    ensure_dir(out_dir)
    unsigned = out_dir / "patched-unsigned.apk"
    signed = out_dir / "patched.apk"

    with tempfile.TemporaryDirectory(prefix=f"{name}_apktool_") as td:
        work = Path(td) / "work"
        log_step(f"重建 APK: {name}")

        # 1. 解包
        if not apktool_decode(src, work):
            return False

        # 2. 修复 manifest
        manifest = work / "AndroidManifest.xml"
        stats = fix_manifest(manifest)
        log_info(f"manifest 修复: 移除 {stats['removed']} 项, 修复 {stats['fixed']} 项")

        # 3. 移除不安全 assets
        remove_unsafe_assets(work)

        # 4. 重新打包
        if not apktool_build(work, unsigned):
            return False

        # 5. zipalign + 签名
        if not zipalign_and_sign(unsigned, signed, keystore):
            return False

        register_artifact(str(signed), "file", f"patched.apk（apktool 重建）", name=name)
        log_success(f"重建完成: {signed} ({signed.stat().st_size // 1024 // 1024} MB)")
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

    if not rebuild(name):
        return 1

    log_success("apktool 重建完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
