#!/usr/bin/env python3
"""
阶段 26 - AS 工程构建（il2cpp 专用）
===================================
新结构：crackings/<type>/<Name>/project/ 就是 AS 项目根，app/ 是 app 模块。

功能：
1. 配置 signingConfigs.release（统一 keystore）
2. gradlew assembleRelease 编译
3. 验证 v1+v2+v3 签名齐全
4. 生成 patched.apk

输入：crackings/<type>/<Name>/project/{settings.gradle, gradlew, gradle/, app/}
输出：crackings/<type>/<Name>/project/{app/build/outputs/apk/release/app-release.apk, patched.apk}
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "skills/common/scripts/lib"))

from common import ensure_env, apksigner, zipalign, log_info, log_success, log_error, log_step, log_warn  # noqa: E402

STAGE_ID = "26"
STAGE_NAME = "as-build"


def _strip_ad_sdk_providers(manifest_path: Path) -> None:
    """从 manifest 移除第三方广告 SDK 的 provider 声明。

    [FLOWFIX]
    raw manifest 含 16 个广告 SDK provider（vungle/applovin/facebook/google/firebase/
    ironsource/yandex/bigo/bidmachine 等），它们的类在 inject-filtered-original-dex.py
    中被过滤（EXCLUDE 含广告包），导致 AndroidRuntime ClassNotFoundException：
      "Unable to get provider com.vungle.ads.VungleProvider: ClassNotFoundException"
    广告 SDK 不影响游戏主玩法（il2cpp skill 阶段 06 SDK 移除策略），直接从
    manifest 删除这些 provider 声明。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")

    # [FLOWFIX 2026-08-18] 从 third-party-sdk-removal-registry.yaml 读 SDK 移除清单
    # 集中维护 manifest_drop_exact + manifest_drop_keyword_contains 两段
    import sys as _sys
    _sys.path.insert(0, str(REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts"))
    from load_sdk_removal_registry import load_registry, names_only
    _reg = load_registry()
    ad_packages = tuple(names_only(_reg["manifest_drop_exact"]) + names_only(_reg["manifest_drop_keyword_contains"]))
    # [FLOWFIX] 正则必须容忍：
    #  1) android:name 在 provider 属性任意位置（authorities 在前）
    #  2) 包名前缀（com.xxx / io.xxx / sg.xxx）
    #  3) 自闭合 <provider .../> 和带子元素的 <provider>...</provider>
    # 包名前缀正则：容忍 (com.|io.|sg.)(google.|android.|firebase.)?firebase|adjust|vungle 等
    # 直接允许更宽的前缀（com.* .* | io.* .* | sg.* .* | 空）+ 关键字
    pat = "|".join(
        r"(?:[\w]+\.)*[\w]*" + re.escape(pkg) for pkg in ad_packages
    )
    # 5 种 tag 全包：provider / service / receiver / activity / meta-data
    tag_kinds = "provider|service|receiver|activity|meta-data"
    pattern_self = re.compile(
        r'<(?:' + tag_kinds + r')\b[^>]*android:name="(' + pat + r')[^"]*"[^>]*/>'
    )
    pattern_block = re.compile(
        r'<(?:' + tag_kinds + r')\b[^>]*android:name="(' + pat + r')[^"]*"[^>]*>.*?</(?:' + tag_kinds + r')>',
        re.DOTALL,
    )
    n1 = len(pattern_self.findall(text))
    n2 = len(pattern_block.findall(text))
    new_text = pattern_self.sub("", text)
    new_text = pattern_block.sub("", new_text)
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 已移除广告 SDK 声明（自闭合={n1} 块={n2}）")


def _strip_crashlytics_metadata(manifest_path: Path) -> None:
    """移除/改写清单 meta_data_force_value 里列的 meta-data 项。

    [FLOWFIX 2026-08-18] meta_data_force_value 列表里每项含 name + value，
    把 <meta-data name="X" value="OLD"/> 改成 <meta-data name="X" value="NEW"/>。
    例如：firebase_crashlytics_collection_enabled true→false，
    防止 Java 侧 Crashlytics 静态初始化调 native signal handler。
    名单来自 third-party-sdk-removal-registry.yaml。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")

    import sys as _sys
    _sys.path.insert(0, str(REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts"))
    from load_sdk_removal_registry import load_registry
    _reg = load_registry()
    meta_data_force_value = _reg.get("meta_data_force_value", [])

    new_text = text
    changed = 0
    for entry in meta_data_force_value:
        name = entry.get("name", "")
        value = entry.get("value", "")
        if not name or not value:
            continue
        # 匹配 <meta-data ... android:name="X" ... android:value="Y" ... /> 并替换 value
        pat = (
            r'(<meta-data\s+[^>]*android:name="' + re.escape(name) +
            r'"[^>]*android:value=")[^"]*(")'
        )
        new_new = re.sub(pat, r'\g<1>' + value + r'\g<2>', new_text)
        if new_new != new_text:
            new_text = new_new
            changed += 1
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 改写清单 meta_data_force_value: {changed} 个")


def _strip_split_attributes(manifest_path: Path) -> None:
    """清除 AndroidManifest.xml 中 split APK 相关的属性。

    [FLOWFIX]:
    raw APK 是 split APK base（requiredSplitTypes="base__abi"），
    AS 编译后 patched.apk 也带这个属性，导致 adb install 报
    INSTALL_FAILED_MISSING_SPLIT。清除 split 相关属性即可正常安装。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")
    new_text = re.sub(r'\s+android:requiredSplitTypes="[^"]*"', "", text)
    new_text = re.sub(r'\s+android:splitTypes="[^"]*"', "", new_text)
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 已清除 manifest split 属性: {manifest_path.name}")


def _ensure_main_activity_declared(manifest_path: Path, app_main_src: Path) -> None:
    """确保 AS 工程 manifest 声明了 com.android.boot.MainActivity 作为 LAUNCHER。

    [FLOWFIX]:
    raw APK 的 manifest 是游戏的 manifest（application=com.safedk.android.SafeDKApplication，
    只声明 UnityPlayerActivity 作为 LAUNCHER）。FakerAndroid 历史上会自动加
    MainActivity 注册，但 apktool 解包后 manifest 已不含该 activity。
    AS 编译时 manifest 合并器只会保留源 manifest 声明的 activity，导致 patched.apk
    没有 com.android.boot.MainActivity，adb am start 报
    "Activity class does not exist"。

    处理：检测 java/com/android/boot/MainActivity.java 存在但 manifest 未声明时，
    在 <application> 后插入 MainActivity + LAUNCHER intent-filter。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")
    if "com.android.boot.MainActivity" in text:
        return
    main_activity_java = app_main_src / "src" / "main" / "java" / "com" / "android" / "boot" / "MainActivity.java"
    if not main_activity_java.exists():
        return
    insert_block = (
        '\n        <!-- [FLOWFIX] il2cpp skill '
        'MainActivity 注册 -->\n'
        '        <activity android:name="com.android.boot.MainActivity" '
        'android:exported="true" android:launchMode="singleTask">\n'
        '            <intent-filter>\n'
        '                <category android:name="android.intent.category.LAUNCHER"/>\n'
        '                <action android:name="android.intent.action.MAIN"/>\n'
        '            </intent-filter>\n'
        '        </activity>\n'
    )
    new_text = re.sub(r'(<application[^>]*>)', r'\1' + insert_block, text, count=1)
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 已注册 com.android.boot.MainActivity 到 manifest")


def _replace_application_class(manifest_path: Path, app_main_src: Path) -> None:
    """将 manifest 中 application 的 android:name 替换为 com.android.boot.App（如果存在）。

    [FLOWFIX]:
    raw APK 的 application 是 com.safedk.android.SafeDKApplication，apktool 解包
    后 manifest 沿用此值。SafeDKApplication 在 smali_classes4 中，FakerAndroid 编译
    时不打包全部 smali_classesX，导致 SafeDKApplication 类缺失 → AndroidRuntime
    ClassNotFoundException → 应用启动即崩溃。
    处理：检测 java/com/android/boot/App.java 存在时，把 application android:name
    替换为 com.android.boot.App（接管 onCreate，触发 native hook 加载）。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")
    app_java = app_main_src / "src" / "main" / "java" / "com" / "android" / "boot" / "App.java"
    if not app_java.exists():
        return
    new_text = re.sub(
        r'(<application[^>]*?\s+android:name=")[^"]+(")',
        r'\1com.android.boot.App\2',
        text,
    )
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 已替换 application android:name 为 com.android.boot.App")
        return
    # [FLOWFIX 2026-08-20] 原 APK 可能没有 android:name（默认 Application）→ 上述正则不命中。
    # 若 App.java 存在，必须显式插入 android:name="com.android.boot.App"，否则 native hook
    # 加载器（installNativeHooks）永不执行。
    m = re.search(r'<application\b([^>]*)>', new_text)
    if m and 'android:name="com.android.boot.App"' not in new_text[: new_text.find('</application>')]:
        new_text = re.sub(
            r'<application\b([^>]*)>',
            r'<application\1 android:name="com.android.boot.App">',
            new_text, count=1,
        )
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 插入 application android:name=com.android.boot.App（原无 name）")


def _apply_immersive_fullscreen(manifest_path: Path) -> None:
    """沉浸式全屏：application/MainActivity 主题改为 Theme.NoTitleBar.Fullscreen。

    [FLOWFIX 2026-08-18] 解决 Android 11+ 设备底部白色 NavigationBar 横幅。
    在 MainActivity onCreate/onWindowFocusChanged 调 WindowInsetsController.hide(...) 持久化隐藏。
    必须在 manifest 标记 Fullscreen 主题，否则系统会把 status/nav bar inset 留空变白条。
    """
    if not manifest_path.exists():
        return
    text = manifest_path.read_text(encoding="utf-8", errors="ignore")
    new_text = text
    # application android:theme="...Theme.NoTitleBar" -> Theme.NoTitleBar.Fullscreen
    new_text = re.sub(
        r'(<application[^>]*?\s+android:theme=")@android:style/Theme\.NoTitleBar(")',
        r'\1@android:style/Theme.NoTitleBar.Fullscreen\2',
        new_text,
    )
    # MainActivity 显式加 Fullscreen theme（缺失时插入）
    if "com.android.boot.MainActivity" in new_text and 'android:theme="@android:style/Theme.NoTitleBar.Fullscreen"' not in new_text:
        new_text = re.sub(
            r'(<activity\s+android:name="com\.android\.boot\.MainActivity"[^>]*)>',
            r'\1 android:theme="@android:style/Theme.NoTitleBar.Fullscreen">',
            new_text,
        )
    if new_text != text:
        manifest_path.write_text(new_text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 已应用沉浸式全屏主题 (NoTitleBar.Fullscreen)")


def _find_release_apk(app_dir: Path) -> "Path | None":
    """定位 Gradle 生成的 release APK（兼容 set-gradle-identity 自定义 outputFileName）。

    set-gradle-identity 步骤会把 APK 命名为 <Name>-release-<version>.apk，
    而不是固定 app-release.apk。此处按目录 glob *.apk 取第一个，避免硬编码文件名。
    """
    rel = app_dir / "build" / "outputs" / "apk" / "release"
    if not rel.is_dir():
        return None
    apks = sorted(rel.glob("*.apk"))
    return apks[0] if apks else None


def resign_existing(project_root: Path, cracking_dir: Path) -> int:
    """仅对现有 Gradle APK 重新启用 v1/v2/v3，供修复签名时使用。"""
    apk = _find_release_apk(project_root / "app")
    keystore = project_root / "my.keystore.jks"
    if (not apk or not apk.is_file()) or not keystore.is_file():
        log_error(f"[stage-{STAGE_ID}] RESIGN_ONLY 输入缺失: apk={apk} keystore={keystore}")
        return 1
    aligned = apk.with_suffix(".aligned.apk")
    signed = apk.with_suffix(".signed.apk")
    align_result = subprocess.run([zipalign(), "-f", "4", str(apk), str(aligned)], capture_output=True, text=True)
    if align_result.returncode != 0:
        log_error(f"[stage-{STAGE_ID}] zipalign 失败: {align_result.stderr[-1000:]}")
        return 1
    cmd = [
        apksigner(), "sign", "--ks", str(keystore), "--ks-key-alias", "jy",
        "--ks-pass", "pass:Ab123145", "--key-pass", "pass:Ab123145",
        "--v1-signing-enabled", "true", "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true", "--out", str(signed), str(aligned),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_error(f"[stage-{STAGE_ID}] v1/v2/v3 重签名失败: {result.stderr[-1000:]}")
        aligned.unlink(missing_ok=True)
        signed.unlink(missing_ok=True)
        return 1
    shutil.copy2(signed, apk)
    shutil.copy2(signed, project_root / "patched.apk")
    shutil.copy2(signed, cracking_dir / "patched.apk")
    signed.unlink(missing_ok=True)
    aligned.unlink(missing_ok=True)
    log_success(f"[stage-{STAGE_ID}] 已对现有 APK 完成 v1/v2/v3 重签名")
    return 0


def main() -> int:
    ensure_env()
    name = sys.argv[1] if len(sys.argv) > 1 else os.environ.get('NAME')
    if not name:
        log_error("[stage-26] 用法: sub-stage-as-build.py <Name> 或设置 NAME 环境变量")
        return 1

    type_arg = os.environ.get("TYPE", "").strip()
    project_root = REPO / "crackings" / (type_arg or "") / name / "project"
    app_dir = project_root / "app"

    if type_arg:
        cracking_dir = REPO / "crackings" / type_arg / name
    else:
        cracking_dir = REPO / "crackings" / name
    apktool_dir = cracking_dir / "raw" / "01-apktool"

    log_step(f"阶段 {STAGE_ID}: AS 工程构建")

    if os.environ.get("RESIGN_ONLY") == "1":
        return resign_existing(project_root, cracking_dir)

    # 1. 检查必要文件存在
    if not (project_root / "settings.gradle").exists():
        log_error(f"[stage-{STAGE_ID}] settings.gradle 不存在（需要先执行预处理阶段）")
        return 1
    if not (project_root / "gradlew").exists():
        log_error(f"[stage-{STAGE_ID}] gradlew 不存在（需要先执行预处理阶段）")
        return 1
    if not (app_dir / "build.gradle").exists():
        log_error(f"[stage-{STAGE_ID}] app/build.gradle 不存在（需要先执行预处理阶段）")
        return 1

    # 2. 统一 keystore 符号链接
    template_keystore = REPO / "tools" / "scripts" / "template-files" / "my.keystore.jks"
    project_keystore = project_root / "my.keystore.jks"
    if template_keystore.exists() and not project_keystore.exists():
        project_keystore.symlink_to(template_keystore)
        log_info(f"[stage-{STAGE_ID}] 创建统一 keystore 符号链接")

    # 3. Manifest 修复（仅 app/src/main/AndroidManifest.xml）
    #    apktool_dir 可能不存在（cleanup 已删除），fallback 到 app/src/main 的已处理版本
    manifest_src = apktool_dir / "AndroidManifest.xml"
    manifest_dst = app_dir / "src" / "main" / "AndroidManifest.xml"
    if not manifest_src.exists():
        manifest_src = manifest_dst
    if manifest_src.exists() and manifest_dst.exists():
        # 复制最新 manifest（src 与 dst 为同一 file（ASBuilder 已落位）时跳过）
        if manifest_src.resolve() != manifest_dst.resolve():
            shutil.copy2(manifest_src, manifest_dst)
        # 修复 split 属性
        _strip_split_attributes(manifest_dst)
        # 注册 MainActivity
        _ensure_main_activity_declared(manifest_dst, app_dir)
        # 替换 application
        _replace_application_class(manifest_dst, app_dir)
        # 移除广告 SDK provider
        _strip_ad_sdk_providers(manifest_dst)
        # 关闭 Crashlytics 自动收集（防止 native crash handler 自杀）
        _strip_crashlytics_metadata(manifest_dst)
        # 沉浸式全屏主题（隐藏系统 status/nav bar inset 白条）
        _apply_immersive_fullscreen(manifest_dst)
        log_info(f"[stage-{STAGE_ID}] Manifest 修复完成")

    # 4. 交付契约：确保 libs 目录存在
    (app_dir / "libs").mkdir(parents=True, exist_ok=True)

    # 4.5 模板类快速修正 + 强制 manifest 入口
    # [FLOWFIX] 参照模板快速修改已有 MainActivity/App/JniBridge/SDKUtils，
    # 并强制 manifest: MainActivity=LAUNCHER + com.android.boot.App=application。
    tmpl_patch = REPO / "skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-template-patch.py"
    if tmpl_patch.exists():
        r = subprocess.run(
            [sys.executable, str(tmpl_patch)],
            cwd=str(REPO), env={**os.environ, "TYPE": type_arg, "NAME": name},
            capture_output=True, text=True, timeout=120,
        )
        if r.returncode == 0:
            log_info(f"[stage-{STAGE_ID}] 模板类修正 + manifest 入口强制完成")
        else:
            log_warn(f"[stage-{STAGE_ID}] 模板 patch 失败: {(r.stdout + r.stderr)[-300:]}")

    # 5. 确保 gradlew 有执行权限
    gradlew = project_root / "gradlew"
    if gradlew.exists():
        gradlew.chmod(0o755)

    # 6. 修复 app/build.gradle
    build_gradle = app_dir / "build.gradle"
    if build_gradle.exists():
        text = build_gradle.read_text(encoding="utf-8")
        # 统一 namespace
        app_id_match = re.search(r"applicationId\s+['\"]([^'\"]+)['\"]", text)
        if app_id_match:
            text = re.sub(
                r"namespace\s+['\"][^'\"]+['\"]",
                f'namespace "{app_id_match.group(1)}"',
                text,
                count=1,
            )
        # libs/ fileTree 统一为 implementation（运行时 + 编译时同一来源）
        text = re.sub(
            r"compileOnly\s+fileTree\(dir:\s*'libs',\s*include:\s*\['\*\.jar',\s*'\*\.aar'\]\)",
            "implementation fileTree(dir: 'libs', include: ['*.jar', '*.aar'])",
            text,
        )
        text = re.sub(
            r"implementation\s+fileTree\(dir:\s*'libs',\s*include:\s*\['\*\.jar',\s*'\*\.aar'\]\)",
            "implementation fileTree(dir: 'libs', include: ['*.jar', '*.aar'])",
            text,
        )
        # javaScaffoding / libs 的单文件依赖统一为 implementation
        # （runtimeOnly 会触发 desugarReleaseFileDependencies D8 StackOverflowError）
        text = re.sub(
            r"runtimeOnly\s+files\([^)]*\)",
            "", text,
        )
        text = re.sub(
            r"implementation\s+files\([^)]*\)",
            "implementation files('javaScaffoding/classes.all.dex.jar')", text,
        )
        text = re.sub(
            r"compileOnly\s+files\([^)]*\)",
            "implementation files('javaScaffoding/classes.all.dex.jar')", text,
        )
        # [FLOWFIX] 依赖块强制重建：javaScaffoding + libs 的 jar 全部
        # implementation 导入（运行时 + 编译时同一来源），由 AGP 统一 dex 化打包。
        # 不使用 smali2dexApk/apktool b 任务链（用户确认的构建架构）。
        dep_block = (
            "dependencies {\n"
            "    implementation fileTree(dir: 'libs', include: ['*.jar', '*.aar'])\n"
            "    implementation fileTree(dir: 'javaScaffoding', include: ['*.jar'])\n"
            "}"
        )
        if "implementation fileTree(dir: 'javaScaffoding'" not in text:
            text = re.sub(
                r"dependencies\s*\{[^}]*\}",
                dep_block,
                text,
                count=1,
                flags=re.DOTALL,
            )
            if "implementation fileTree(dir: 'javaScaffoding'" not in text:
                text = text.rstrip() + "\n\n" + dep_block + "\n"
        # 归一化 packagingOptions
        malformed_packaging = re.compile(
            r"//\s*packagingOptions\s*\{.*?//\s*\}\s*\n\}",
            re.DOTALL,
        )
        if malformed_packaging.search(text):
            text = malformed_packaging.sub(
                "    packagingOptions {\n"
                "        pickFirst '**/libc++_shared.so'\n"
                "        jniLibs { useLegacyPackaging = true }\n"
                "    }\n}",
                text,
                count=1,
            )
        # 移除 useProguard
        text = text.replace("useProguard false\n", "")
        text = text.replace("useProguard true\n", "")
        # 移除 sensitiveOptions
        text = re.sub(r'\s*sensitiveOptions\s*\{[^}]*\}', '', text, flags=re.DOTALL)
        # 只保留 ARM64
        text = text.replace("abiFilters 'armeabi-v7a','arm64-v8a'", "abiFilters 'arm64-v8a'")
        text = text.replace("abiFilters 'armeabi-v7a', 'arm64-v8a'", "abiFilters 'arm64-v8a'")
        # 统一 SDK 版本
        text = text.replace("compileSdkVersion 29", "compileSdk 33")
        text = text.replace("buildToolsVersion '29.0.3'", "buildToolsVersion '34.0.0'")
        text = text.replace("targetSdkVersion 28", "targetSdkVersion 33")
        # [FLOWFIX] minSdk 21 → 24：implementation 导入的 dex2jar jar 含 Kotlin
        # 默认接口方法（coil/compose 等），minSdk<24 时 D8 desugar 报
        # "One or more instruction is preventing default interface method from being desugared"。
        # minSdk≥24（Android 7.0+）原生支持接口默认方法，无需 desugar。
        text = text.replace("minSdkVersion 21", "minSdkVersion 24")
        text = text.replace("minSdk 21", "minSdk 24")
        # 添加 signingConfigs.release
        if "signingConfigs {" not in text:
            text = text.replace(
                "buildTypes {",
                "    signingConfigs {\n"
                "        release {\n"
                "            storeFile file(\"../my.keystore.jks\")\n"
                "            storePassword \"Ab123145\"\n"
                "            keyAlias \"jy\"\n"
                "            keyPassword \"Ab123145\"\n"
                "        }\n"
                "    }\n\n    buildTypes {",
                1,
            )
        # 替换 release signingConfig
        text = text.replace(
            "signingConfig signingConfigs.debug",
            "signingConfig signingConfigs.release",
        )
        # 添加 lintOptions
        if "lintOptions" not in text:
            text = text.replace(
                "externalNativeBuild {",
                "    lintOptions {\n"
                "        abortOnError false\n"
                "        checkReleaseBuilds false\n"
                "    }\n\n    externalNativeBuild {",
                1,
            )
        build_gradle.write_text(text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 修复 app/build.gradle")

    # 7. 修复根 build.gradle
    root_build_gradle = project_root / "build.gradle"
    if root_build_gradle.exists():
        text = root_build_gradle.read_text(encoding="utf-8")
        if "allprojects" in text and "buildscript" in text:
            text = (
                "buildscript {\n"
                "    repositories {\n"
                "        google()\n"
                "        mavenCentral()\n"
                "    }\n"
                "    dependencies {\n"
                "        classpath 'com.android.tools.build:gradle:7.4.2'\n"
                "    }\n"
                "}\n"
                "\n"
                "allprojects {\n"
                "    repositories {\n"
                "        google()\n"
                "        mavenCentral()\n"
                "    }\n"
                "}\n"
                "\n"
                "task clean(type: Delete) {\n"
                "    delete rootProject.buildDir\n"
                "}\n"
            )
        elif "com.android.tools.build:gradle" not in text:
            if "//classpath 'com.android.tools.build:gradle:" in text:
                text = re.sub(
                    r"//classpath 'com\.android\.tools\.build:gradle:[^']*'",
                    "classpath 'com.android.tools.build:gradle:7.4.2'",
                    text,
                )
            else:
                text = text.replace(
                    "dependencies {",
                    "dependencies {\n            classpath 'com.android.tools.build:gradle:7.4.2'",
                    1,
                )
        root_build_gradle.write_text(text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 修复根 build.gradle")

    # 8. 修复 gradle-wrapper.properties（腾讯云镜像）
    wrapper_props = project_root / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if wrapper_props.exists():
        text = wrapper_props.read_text(encoding="utf-8")
        text = re.sub(
            r'distributionUrl=.*',
            r'distributionUrl=https\://mirrors.cloud.tencent.com/gradle/gradle-7.5.1-bin.zip',
            text,
        )
        wrapper_props.write_text(text, encoding="utf-8")
        log_info(f"[stage-{STAGE_ID}] 修复 gradle-wrapper.properties")

    # 9. 标准化 CMakeLists.txt
    cmake_lists = app_dir / "src" / "main" / "cpp" / "CMakeLists.txt"
    existing_text = cmake_lists.read_text(encoding="utf-8", errors="ignore") if cmake_lists.exists() else ""
    needs_rewrite = (
        not cmake_lists.exists()
        or "find_package(base" in existing_text
        or "native_srcc" in existing_text
        or "And64InlineHook.cpp" not in existing_text
        or "CMAKE_CURRENT_SOURCE_DIR" not in existing_text
    )
    if needs_rewrite:
        cmake_lists.write_text(
            'cmake_minimum_required(VERSION 3.22.1)\n'
            'project("native-lib")\n'
            'set(CMAKE_CURRENT_SOURCE_DIR "${CMAKE_CURRENT_LIST_DIR}")\n'
            'file(GLOB native_src "${CMAKE_CURRENT_SOURCE_DIR}/*.cpp")\n'
            'file(GLOB inlinehook_src "${CMAKE_CURRENT_SOURCE_DIR}/And64InlineHook/*.cpp")\n'
            'add_library(native-lib SHARED ${native_src} ${inlinehook_src})\n'
            'find_library(log-lib log)\n'
            'target_link_libraries(native-lib ${log-lib} android z)\n',
            encoding="utf-8",
        )
        log_info(f"[stage-{STAGE_ID}] 标准化 CMakeLists.txt")
        faker_stub = app_dir / "src" / "main" / "cpp" / "faker-stubs.cpp"
        faker_stub.write_text(
            '#include <jni.h>\n'
            'jint onJniLoad(JavaVM*, void*) { return JNI_VERSION_1_6; }\n'
            'long baseImageAddr(const char*) { return 0; }\n'
            'bool fakeCpp(void*, void*, void**) { return false; }\n'
            'bool fakeDex(JNIEnv*, jobject, const char*) { return false; }\n',
            encoding="utf-8",
        )

    # 10. 删除 FakerAndroid 占位 native-lib.so（与 CMake 目标冲突）
    jni_root = app_dir / "src" / "main" / "jniLibs"
    if jni_root.exists():
        for stale_native in jni_root.glob("*/libnative-lib.so"):
            stale_native.unlink()
            log_info(f"[stage-{STAGE_ID}] 删除占位库: {stale_native}")

    # 10.5 依赖块已在上方强制重建为 implementation fileTree（javaScaffoding + libs）
    # 注：不使用 smali2dexApk / apktool b 任务链——所有 smali 转换的 jar
    # 直接 implementation 导入，由 AGP 统一 dex 化打包进 APK（用户确认的构建架构）。

    # 11. 编译
    log_info(f"[stage-{STAGE_ID}] 编译 {name}...")
    env = os.environ.copy()
    # [FLOWFIX] 使用 env.sh 的 ASCII ANDROID_HOME（否则中文路径触发 AAPT2 mojibake）；
    # 仅当未注入时回退到项目内 SDK。
    if not env.get("ANDROID_HOME"):
        env["ANDROID_HOME"] = str(REPO / "tools" / "environments" / "android-sdk")
    result = subprocess.run(
        [str(gradlew), "assembleRelease"],
        cwd=project_root,
        env=env,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        details = ((result.stdout or "") + "\n" + (result.stderr or ""))[-4000:]
        log_error(f"[stage-{STAGE_ID}] 编译失败: {details}")
        return 1

    apk_path = _find_release_apk(app_dir)
    if not apk_path or not apk_path.exists():
        log_error(f"[stage-{STAGE_ID}] APK 未生成: {app_dir / 'build/outputs/apk/release'}")
        return 1

    # 12. 签名验证 + 生成 patched.apk
    signed = project_root / "patched.apk"
    aligned = apk_path.with_suffix(".aligned.apk")
    subprocess.run([zipalign(), "-f", "4", str(apk_path), str(aligned)], capture_output=True)
    cmd = [
        apksigner(), "sign",
        "--ks", str(project_keystore),
        "--ks-key-alias", "jy",
        "--ks-pass", "pass:Ab123145", "--key-pass", "pass:Ab123145",
        "--v1-signing-enabled", "true",
        "--v2-signing-enabled", "true",
        "--v3-signing-enabled", "true",
        "--out", str(signed),
        str(aligned),
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        log_error(f"[stage-{STAGE_ID}] 签名失败: {result.stderr[-1000:]}")
        return 1
    aligned.unlink(missing_ok=True)
    shutil.copy2(signed, cracking_dir / "patched.apk")
    log_success(f"[stage-{STAGE_ID}] patched.apk 已生成: {signed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())