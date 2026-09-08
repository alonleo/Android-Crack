#!/usr/bin/env python3
"""
sub-stage-template-patch.py — 基于模板快速修改已有 MainActivity/JniBridge/App/SDKUtils，
并强制 manifest 入口（MainActivity 替换原游戏入口，App 替换原 Application）。

[FLOWFIX] 用户确认的构建架构补充：
  模板类（MainActivity/JniBridge/App/SDKUtils）不是覆盖式生成，而是"参照模板快速修改
  已有类"，并强制在 AndroidManifest.xml 声明：
    - MainActivity 为 LAUNCHER（替换原游戏入口）
    - com.android.boot.App 为 application android:name（替换原 Application）
  避免原 APK 入口类（如 Firebase MessagingPlayerActivity / SafeDKApplication）残留导致
  ClassNotFoundException / 初始化崩溃。

用法：
  TYPE=il2cpp NAME=xx python3 sub-stage-template-patch.py

产出：
  - app/src/main/java/com/android/boot/{MainActivity,App,JniBridge}.java（修正）
  - app/src/main/java/com/android/common/SDKUtils.java（已存在时修正）
  - app/src/main/AndroidManifest.xml（强制入口声明）
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
TEMPLATE_DIR = REPO / "tools" / "scripts" / "template-files"

# 模板要求 MainActivity 必须包含的 native 方法（缺失则补齐）
_REQUIRED_MA_NATIVE = [
    ("registerCallBack", "registerCallBack(JniBridge bridge);"),
    ("retryNativeHooks", "retryNativeHooks();"),
    ("onVideoReward", "onVideoReward(boolean isSucess);"),
    ("onIapSuccess", "onIapSuccess(String productId);"),
    ("onPremiumUnlock", "onPremiumUnlock();"),
    ("onPremiumBuyPass", "onPremiumBuyPass();"),
]


def _resolve() -> tuple[str, Path, Path]:
    name = os.environ.get("NAME", "").strip()
    if not name:
        sys.exit("[stage-template-patch] NAME 环境变量未设置")
    type_arg = os.environ.get("TYPE", "").strip()
    app_main = (REPO / "output-projects" / (type_arg or "") / name / "app" / "src" / "main")
    crack_raw = (REPO / "crackings" / (type_arg or "") / name / "raw" / "01-apktool")
    return name, app_main, crack_raw


def _read(p: Path) -> str:
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


def _patch_main_activity(app_main: Path) -> int:
    """修正 MainActivity：确保 extends UnityPlayerActivity + native 方法齐全。"""
    dst = app_main / "java" / "com" / "android" / "boot" / "MainActivity.java"
    text = _read(dst)
    if not text:
        print("[WARN] MainActivity.java 不存在，跳过")
        return 0

    # 1. 确保 extends UnityPlayerActivity
    if "extends UnityPlayerActivity" not in text:
        if "extends Activity" in text:
            text = text.replace("extends Activity", "extends UnityPlayerActivity", 1)
            # 补 import
            if "import com.unity3d.player.UnityPlayerActivity;" not in text:
                text = re.sub(r"(package\s+[^;]+;)", r"\1\nimport com.unity3d.player.UnityPlayerActivity;", text, count=1)
            print("[OK] MainActivity: extends Activity -> UnityPlayerActivity")

    # 2. 补齐缺失的 native 方法
    added = 0
    for method_name, decl in _REQUIRED_MA_NATIVE:
        if f" {method_name}(" in text:
            continue
        # 追加到 class 末尾（最后一个 } 前）
        text = text.rstrip()
        if text.endswith("}"):
            text = text[:-1]
        text += f"\n    public native {decl}\n}}\n"
        added += 1
    if added:
        print(f"[OK] MainActivity: 补齐 {added} 个 native 方法")

    dst.write_text(text, encoding="utf-8")
    return added


def _patch_app(app_main: Path) -> int:
    """修正 App：确保 extends Application + onCreate 调 installNativeHooks。"""
    dst = app_main / "java" / "com" / "android" / "boot" / "App.java"
    text = _read(dst)
    if not text:
        print("[WARN] App.java 不存在，跳过")
        return 0
    changed = 0
    if "installNativeHooks" not in text:
        # 在 class 内补 native 方法 + onCreate 调用
        if "public void onCreate" not in text:
            # 无 onCreate → 插入
            text = text.rstrip()
            if text.endswith("}"):
                text = text[:-1]
            text += (
                "\n    @Override\n    protected void attachBaseContext(android.content.Context base) {\n"
                "        super.attachBaseContext(base);\n    }\n"
                "\n    @Override\n    public void onCreate() {\n"
                "        super.onCreate();\n        installNativeHooks();\n    }\n"
                "\n    public native void installNativeHooks();\n}\n"
            )
        else:
            # onCreate 存在 → 在 super.onCreate(); 后插入调用
            text = re.sub(
                r"(super\.onCreate\(\);)",
                r"\1\n        installNativeHooks();",
                text,
                count=1,
            )
        # 确保 native 声明存在
        if "public native void installNativeHooks" not in text:
            text = text.rstrip()
            if text.endswith("}"):
                text = text[:-1]
            text += "\n    public native void installNativeHooks();\n}\n"
        changed += 1
        print("[OK] App: 补 installNativeHooks")

    dst.write_text(text, encoding="utf-8")
    return changed


def _patch_jni_bridge(app_main: Path) -> int:
    dst = app_main / "java" / "com" / "android" / "boot" / "JniBridge.java"
    if not dst.exists():
        # 从模板生成
        src = TEMPLATE_DIR / "JniBridge.template.java"
        if src.exists():
            text = _read(src).replace("{PACKAGE_NAME}", "com.android.boot")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(text, encoding="utf-8")
            print("[OK] JniBridge: 从模板生成")
            return 1
    return 0


def _patch_sdkutils(app_main: Path) -> int:
    dst = app_main / "java" / "com" / "android" / "common" / "SDKUtils.java"
    if not dst.exists():
        src = TEMPLATE_DIR / "SDKUtils.java"
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(_read(src), encoding="utf-8")
            print("[OK] SDKUtils: 从模板生成")
    return 0


def _force_manifest_entry(app_main: Path, app_pkg: str) -> None:
    """强制 manifest：MainActivity=LAUNCHER，com.android.boot.App=application。"""
    manifest = app_main / "AndroidManifest.xml"
    if not manifest.exists():
        print("[WARN] AndroidManifest.xml 不存在，跳过入口强制")
        return
    text = _read(manifest)
    orig = text

    # 1. application android:name → com.android.boot.App
    text = re.sub(
        r'(<application\b[^>]*?\s+android:name=")[^"]+(")',
        r'\1com.android.boot.App\2',
        text,
        count=1,
    )

    # 2. MainActivity 设为 LAUNCHER：确保有 android.intent.category.LAUNCHER + MAIN
    if "com.android.boot.MainActivity" in text:
        # 若已有 MainActivity 声明但无 launcher filter，补一个
        if not re.search(
                r'<activity\b[^>]*com\.android\.boot\.MainActivity[^>]*>.*?LAUNCHER',
                text, re.DOTALL):
            # 在 <application> 后插入带 launcher 的 MainActivity 声明
            insert = (
                '\n        <activity android:name="com.android.boot.MainActivity" '
                'android:exported="true" android:launchMode="singleTask">\n'
                '            <intent-filter>\n'
                '                <action android:name="android.intent.action.MAIN"/>\n'
                '                <category android:name="android.intent.category.LAUNCHER"/>\n'
                '            </intent-filter>\n'
                '        </activity>\n'
            )
            text = re.sub(r'(<application[^>]*>)', r'\1' + insert, text, count=1)
    else:
        # 无 MainActivity → 插入带 launcher 的声明
        insert = (
            '\n        <activity android:name="com.android.boot.MainActivity" '
            'android:exported="true" android:launchMode="singleTask">\n'
            '            <intent-filter>\n'
            '                <action android:name="android.intent.action.MAIN"/>\n'
            '                <category android:name="android.intent.category.LAUNCHER"/>\n'
            '            </intent-filter>\n'
            '        </activity>\n'
        )
        text = re.sub(r'(<application[^>]*>)', r'\1' + insert, text, count=1)

    # 3. 移除其他 activity 的 LAUNCHER filter（防止多入口）
    text = re.sub(
        r'(<activity\b(?:(?!com\.android\.boot\.MainActivity)[^>])*?>)'
        r'(.*?<action android:name="android\.intent\.action\.MAIN"/>'
        r'.*?<category android:name="android\.intent\.category\.LAUNCHER"/>.*?</intent-filter>)',
        lambda m: m.group(1) + re.sub(
            r'<action android:name="android\.intent\.action\.MAIN"/>.*?</intent-filter>',
            '<intent-filter></intent-filter>',
            m.group(2),
            count=1, flags=re.DOTALL),
        text,
        count=1,
        flags=re.DOTALL,
    )

    if text != orig:
        manifest.write_text(text, encoding="utf-8")
        print("[OK] AndroidManifest: 强制 MainActivity=LAUNCHER + App=application")


def main() -> int:
    name, app_main, _ = _resolve()
    app_main.mkdir(parents=True, exist_ok=True)

    # 包名用于 manifest package 解析（可有可无）
    app_pkg = os.environ.get("PKG", "")

    _patch_main_activity(app_main)
    _patch_app(app_main)
    _patch_jni_bridge(app_main)
    _patch_sdkutils(app_main)
    _force_manifest_entry(app_main, app_pkg)

    print(f"[stage-template-patch] 完成 → {app_main}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
