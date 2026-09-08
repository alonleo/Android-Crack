#!/usr/bin/env python3
"""
setup-output-project.py — GameMaker Studio 引擎专用：搭 AS 工程化骨架。

来源: FindTheDifferences (com.TanApps.FindTheDifferences300) | 2026-08-08

用法:
  python3 setup-output-project.py <Name>

功能:
  - 转换 smali → classesN.dex → jars（复用 il2cpp convert-smali-to-jars.py）
  - 拷贝 libyoyo.so 到 jniLibs/arm64-v8a/
  - 拷贝 assets/game.droid + img300_1/ + 其他 assets 到 app/src/main/assets/
  - 拷贝 res 到 app/src/main/res/
  - 生成 build.gradle / settings.gradle / AndroidManifest.xml / PlaceholderActivity
  - 软链接 my.keystore.jks → ../../skills/common/scripts/template-files/my.keystore.jks
  - 拷贝 patched.apk 到 crackings/<type>/<Name>/project/
"""
from __future__ import annotations

import sys
import os
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

# 复用 il2cpp 的 convert-smali-to-jars.py（不依赖 FakerAndroid 特定逻辑）
import importlib.util
_spec = importlib.util.spec_from_file_location(
    "convert_smali_to_jars",
    str(ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts" / "common" / "convert-smali-to-jars.py"),
)
_conv = importlib.util.module_from_spec(_spec)
assert _spec.loader is not None
_spec.loader.exec_module(_conv)


def log_info(msg):  print(f"[INFO]  {msg}")
def log_ok(msg):    print(f"[OK]    {msg}")
def log_warn(msg):  print(f"[WARN]  {msg}")
def log_step(msg):  print(f"\n== {msg} ==")


def aapt2():
    """AAPT2 from env (matches AGENTS.md §1.2)."""
    p = os.environ.get("AAPT2")
    return p if p and Path(p).exists() else "aapt2"


def main():
    if len(sys.argv) < 2:
        print("Usage: setup-output-project.py <Name>")
        sys.exit(1)

    name = sys.argv[1]
    crackings = ROOT / "crackings" / name
    output = ROOT / "output-projects" / name
    apktool_dir = crackings / "raw" / "01-apktool"

    if not apktool_dir.exists():
        log_warn(f"apktool 解包不存在: {apktool_dir}")
        sys.exit(1)

    log_step(f"=== GameMaker Studio 输出项目搭建: {name} ===")

    # 1. 转换 smali → jars（通过 subprocess 调用 convert-smali-to-jars.py CLI，避免 import 内部 Path 处理）
    log_step("1/8 转换 smali → jars + 剥离 R/BuildConfig")
    jars_dir = output / "app" / "libs"
    jars_dir.mkdir(parents=True, exist_ok=True)
    try:
        proc = subprocess.run(
            ["python3",
             str(ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts" / "common" / "convert-smali-to-jars.py"),
             name,
             "--smali-root", str(apktool_dir),
             "--out", str(jars_dir),
             "--api", "34"],
            capture_output=True, text=True, timeout=600,
        )
        if proc.returncode == 0:
            # 剥离 R.class/R$*.class/BuildConfig.class（精确正则，避免误删 Runner*）
            import tempfile
            import zipfile
            for jar_path in jars_dir.glob("*.jar"):
                with tempfile.TemporaryDirectory() as tmp:
                    tmp_dir = Path(tmp)
                    with zipfile.ZipFile(jar_path, "r") as zin:
                        zin.extractall(tmp_dir)
                    # 删除 R.class / R$*.class / BuildConfig.class（精确匹配）
                    for pattern in [r".*/R\.class$", r".*/R\$[^/]*\.class$", r".*/BuildConfig\.class$"]:
                        for f in tmp_dir.rglob("*"):
                            if f.is_file() and __import__("re").match(pattern, str(f)):
                                f.unlink()
                    # 重建 jar
                    jar_path.unlink()
                    with zipfile.ZipFile(jar_path, "w", zipfile.ZIP_DEFLATED) as zout:
                        for f in sorted(tmp_dir.rglob("*")):
                            if f.is_file():
                                zout.write(f, f.relative_to(tmp_dir))
                    log_ok(f"剥离 R/BuildConfig: {jar_path.name}")
            log_ok(f"smali → jars: {jars_dir}")
        else:
            log_warn(f"smali 转换失败（rc={proc.returncode}）: {proc.stderr.strip()[-500:]}")
    except Exception as e:
        log_warn(f"smali 转换异常: {e}")

    # 2. 拷贝 libyoyo.so 到 jniLibs
    log_step("2/8 拷贝 libyoyo.so")
    jni_arch = output / "app" / "src" / "main" / "jniLibs" / "arm64-v8a"
    jni_arch.mkdir(parents=True, exist_ok=True)
    src_so = apktool_dir / "lib" / "arm64-v8a" / "libyoyo.so"
    if src_so.exists():
        shutil.copy2(src_so, jni_arch / "libyoyo.so")
        log_ok(f"libyoyo.so: {jni_arch}")
    else:
        log_warn(f"libyoyo.so 缺失: {src_so}")

    # 3. 拷贝 assets（game.droid, img300_1, options.ini, .ext 等）
    log_step("3/8 拷贝 assets/")
    out_assets = output / "app" / "src" / "main" / "assets"
    out_assets.mkdir(parents=True, exist_ok=True)
    src_assets = apktool_dir / "assets"
    if src_assets.exists():
        for item in src_assets.iterdir():
            dst = out_assets / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        log_ok(f"assets 拷贝完成: {out_assets}")

    # 4. 拷贝 res/
    log_step("4/8 拷贝 res/")
    out_res = output / "app" / "src" / "main" / "res"
    out_res.mkdir(parents=True, exist_ok=True)
    src_res = apktool_dir / "res"
    if src_res.exists():
        for item in src_res.iterdir():
            dst = out_res / item.name
            if item.is_dir():
                shutil.copytree(item, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(item, dst)
        log_ok(f"res 拷贝完成: {out_res}")

    # 5. 生成 AndroidManifest.xml
    log_step("5/8 生成 AndroidManifest.xml")
    package = "com.TanApps.FindTheDifferences300"
    manifest_path = output / "app" / "src" / "main" / "AndroidManifest.xml"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    # 从 apktool 解包 manifest 中提取关键 GameMaker meta-data 标签
    import re as _re
    apktool_manifest = (apktool_dir / "AndroidManifest.xml").read_text(encoding="utf-8")
    all_metas = _re.findall(r'<meta-data [^/]+/>', apktool_manifest)
    # 过滤：只保留 GameMaker 引擎必需 + 已清理 SDK 后残留
    SKIP_META = {
        "com.google.android.gms.ads", "com.google.android.gms.version",
        "firebase_crashlytics", "com.google.android.datatransport",
        "androidx.work.WorkManagerInitializer", "androidx.emoji2",
        "androidx.lifecycle.ProcessLifecycle", "com.google.firebase.components",
        "AdMob_", "com.android.vending", "com.android.stamp",
        "com.android.dynamic.apk", "YYExtensionClass",
    }
    gamemaker_metas = [m for m in all_metas if not any(s in m for s in SKIP_META)]
    metas_block = "\n        ".join(gamemaker_metas)

    manifest_content = f'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="{package}"
    android:versionCode="1002000"
    android:versionName="1.2.0">

    <uses-sdk android:minSdkVersion="19" android:targetSdkVersion="33" />

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.VIBRATE" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <application
        android:label="@string/app_name"
        android:icon="@drawable/icon"
        android:isGame="true"
        android:name="{package}.RunnerApplication">

        <activity
            android:name="{package}.RunnerActivity"
            android:exported="true"
            android:configChanges="density|fontScale|keyboard|keyboardHidden|layoutDirection|locale|mcc|mnc|navigation|orientation|screenLayout|screenSize|smallestScreenSize|touchscreen|uiMode"
            android:launchMode="singleTask"
            android:theme="@android:style/Theme.NoTitleBar.Fullscreen">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <activity
            android:name=".PlaceholderActivity"
            android:exported="false" />

        {metas_block}
    </application>
</manifest>
'''
    manifest_path.write_text(manifest_content, encoding="utf-8")
    log_ok(f"AndroidManifest.xml: {manifest_path} (含 {len(gamemaker_metas)} 个 GameMaker meta-data)")

    # 6. 生成 PlaceholderActivity.java
    log_step("6/8 生成 PlaceholderActivity.java")
    java_dir = output / "app" / "src" / "main" / "java" / "com" / "TanApps" / "FindTheDifferences300"
    java_dir.mkdir(parents=True, exist_ok=True)
    placeholder = java_dir / "PlaceholderActivity.java"
    placeholder.write_text('''package com.TanApps.FindTheDifferences300;

import android.app.Activity;
import android.os.Bundle;

/**
 * 占位 Activity — GameMaker 引擎实际入口为 com.TanApps.FindTheDifferences300.RunnerActivity
 * （已由 smali→jar 引用打包，见 app/libs/）。
 * 本类仅满足 AGP 工程「至少一个 Activity」的构建要求，不参与启动。
 */
public class PlaceholderActivity extends Activity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
''', encoding="utf-8")
    log_ok(f"PlaceholderActivity.java: {placeholder}")

    # 7. 生成 build.gradle / settings.gradle / gradle.properties / gradle wrapper
    log_step("7/8 生成 gradle 配置")
    gradle_root = output
    gradle_root.mkdir(parents=True, exist_ok=True)

    # root build.gradle
    (gradle_root / "build.gradle").write_text('''// Build: AGP 7.4.2 (per OBJECTIVES.md §2.1)
plugins {
    id 'com.android.application' version '7.4.2' apply false
}

allprojects {
    repositories {
        google()
        mavenCentral()
    }
}

task clean(type: Delete) {
    delete rootProject.buildDir
}
''', encoding="utf-8")

    # settings.gradle
    (gradle_root / "settings.gradle").write_text('''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = 'FindTheDifferences'
include ':app'
''', encoding="utf-8")

    # app/build.gradle
    app_gradle = output / "app" / "build.gradle"
    app_gradle.write_text(f'''// FindTheDifferences — Android 应用模块 build.gradle
// GameMaker Studio 引擎游戏；Java 层为 RunnerActivity + RunnerJNILib JNI glue
apply plugin: 'com.android.application'

dependencies {{
    implementation fileTree(dir: 'libs', include: ['*.jar'])
}}

android {{
    compileSdk 33
    buildToolsVersion '34.0.0'
    compileOptions {{
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }}

    signingConfigs {{
        release {{
            storeFile file("../my.keystore.jks")
            storePassword "Ab123145"
            keyAlias "jy"
            keyPassword "Ab123145"
            enableV2Signing true
            enableV3Signing true
        }}
    }}

    defaultConfig {{
        minSdkVersion 19
        targetSdkVersion 33
        applicationId '{package}'
        versionCode 1002000
        versionName '1.2.0'
        multiDexEnabled true
    }}

    aaptOptions {{
        noCompress = ['.so', '.dex', '.png', '.arsc']
        ignoreAssetsPattern = "!.svn:!.git:!.ds_store:!*.scc:.*:!CVS:!thumbs.db:!picasa.ini:!*~"
    }}

    lintOptions {{
        abortOnError false
        checkReleaseBuilds false
    }}

    buildTypes {{
        debug {{
            debuggable true
            minifyEnabled false
            signingConfig signingConfigs.release
        }}
        release {{
            debuggable false
            minifyEnabled false
            signingConfig signingConfigs.release
        }}
    }}

    packagingOptions {{
        doNotStrip '*/arm64-v8a/*.so'
        jniLibs {{
            useLegacyPackaging true
        }}
        pickFirsts += [
            'META-INF/DEPENDENCIES',
            'META-INF/LICENSE',
            'META-INF/LICENSE.txt',
            'META-INF/license.txt',
            'META-INF/NOTICE',
            'META-INF/NOTICE.txt',
            'META-INF/notice.txt',
        ]
    }}

    buildFeatures {{
        buildConfig false
    }}

    // 排除 androidx.multidex（smali.jar 已包含同名类）
    configurations.all {{
        exclude group: 'androidx.multidex', module: 'multidex'
    }}
}}
''', encoding="utf-8")

    # gradle.properties
    (gradle_root / "gradle.properties").write_text('''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
android.enableJetifier=true
''', encoding="utf-8")

    # local.properties
    sdk_root = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT") or "/home/leo/文档/android-crack/tools/environments/android-sdk"
    (gradle_root / "local.properties").write_text(f'sdk.dir={sdk_root}\n', encoding="utf-8")

    log_ok(f"gradle 配置生成: {gradle_root}")

    # 8. 软链接 keystore + 拷贝 patched.apk
    log_step("8/8 链接 keystore + 拷贝 patched.apk")
    src_keystore = ROOT / "tools" / "scripts" / "template-files" / "my.keystore.jks"
    dst_keystore = output / "my.keystore.jks"
    if src_keystore.exists():
        if dst_keystore.is_symlink() or dst_keystore.exists():
            dst_keystore.unlink()
        dst_keystore.symlink_to(src_keystore)
        log_ok(f"keystore 软链接: {dst_keystore} → {src_keystore}")

    src_patched = crackings / "patched.apk"
    dst_patched = output / "patched.apk"
    if src_patched.exists():
        shutil.copy2(src_patched, dst_patched)
        log_ok(f"patched.apk: {dst_patched}")

    log_step(f"=== 完成: {output} ===")
    log_info(f"项目结构: {output}")
    log_info(f"  app/build.gradle + AndroidManifest.xml + src/main/ + assets/ + res/")
    log_info(f"  patched.apk + my.keystore.jks (软链接)")


if __name__ == "__main__":
    main()