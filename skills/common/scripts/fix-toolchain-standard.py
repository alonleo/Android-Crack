#!/usr/bin/env python3
"""
fix-toolchain-standard.py — 工具链标准化（AGP 7.4.2 / Gradle 7.5.1 / compileSdk 33）。

触发条件：preprocess-build 阶段完成后，build.gradle/gradle-wrapper.properties 不符合规范。

标准化配置：
- Gradle: 7.5.1-bin（腾讯镜像）
- AGP: 7.4.2
- compileSdk: 33
- buildToolsVersion: 34.0.0
- CMake: 3.22.1
- Java: 11
- app/build.gradle: implementation fileTree + incremental = true
- gradle.properties: JVM args + 并行/守护/缓存

用法：
  python3 fix-toolchain-standard.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PKG = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts"
sys.path.insert(0, str(SCRIPT_PKG))
import importlib.util as _ilu

_spc = _ilu.spec_from_file_location(
    "stage_common_runtime", str(SCRIPT_PKG / "lib" / "stage_common.py")
)
_sc = _ilu.module_from_spec(_spc)
assert _spc.loader is not None
_spc.loader.exec_module(_sc)

log_info = _sc.log_info
log_warn = _sc.log_warn
log_step = _sc.log_step
log_success = _sc.log_success
log_error = _sc.log_error
append_status = _sc.append_status


def _app_gen(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name))


def fix_gradle_wrapper(app_gen: Path) -> bool:
    """更新 gradle-wrapper.properties 使用 Gradle 7.5.1-bin（腾讯镜像）。"""
    wrapper = app_gen / "gradle" / "wrapper" / "gradle-wrapper.properties"
    if not wrapper.parent.is_dir():
        wrapper.parent.mkdir(parents=True, exist_ok=True)
    wrapper.write_text(
        "distributionBase=GRADLE_USER_HOME\n"
        "distributionPath=wrapper/dists\n"
        "zipStoreBase=GRADLE_USER_HOME\n"
        "zipStorePath=wrapper/dists\n"
        "distributionUrl=https\\://mirrors.cloud.tencent.com/gradle/gradle-7.5.1-bin.zip\n",
        encoding="utf-8",
    )
    log_info(f"gradle-wrapper: Gradle 7.5.1-bin（腾讯镜像）")
    return True


def fix_project_build_gradle(app_gen: Path) -> bool:
    """更新项目级 build.gradle：AGP 7.4.2。"""
    bg = app_gen / "build.gradle"
    bg.write_text(
        '// Toolchain standardized by crack pipeline\n'
        'buildscript {\n'
        '    repositories {\n'
        '        google()\n'
        '        mavenCentral()\n'
        '    }\n'
        '    dependencies {\n'
        "        classpath 'com.android.tools.build:gradle:7.4.2'\n"
        '    }\n'
        '}\n'
        '\n'
        'allprojects {\n'
        '    repositories {\n'
        '        google()\n'
        '        mavenCentral()\n'
        '    }\n'
        '}\n'
        '\n'
        'task clean(type: Delete) {\n'
        '    delete rootProject.buildDir\n'
        '}\n',
        encoding="utf-8",
    )
    log_info("build.gradle: AGP 7.4.2")
    return True


def fix_app_build_gradle(app_gen: Path) -> bool:
    """更新 app/build.gradle：compileSdk 33 / buildTools 30.0.3 / incremental / libs。"""
    bg = app_gen / "app" / "build.gradle"
    if not bg.is_file():
        log_warn(f"app/build.gradle 缺失: {bg}")
        return False

    content = bg.read_text(encoding="utf-8")

    # compileSdkVersion → 33（OBJECTIVES.md §2.1）
    import re
    content = re.sub(
        r'compileSdkVersion\s+\d+',
        'compileSdkVersion 33',
        content,
    )

    # buildToolsVersion → 34.0.0（OBJECTIVES.md §2.1）
    content = re.sub(
        r"buildToolsVersion\s+'[^']*'",
        "buildToolsVersion '34.0.0'",
        content,
    )
    if "buildToolsVersion" not in content:
        content = content.replace(
            "compileSdkVersion 33",
            "compileSdkVersion 33\n    buildToolsVersion '34.0.0'",
        )

    # dependencies: implementation fileTree 包含 *.aar
    content = re.sub(
        r"implementation fileTree\(dir: 'libs', include: \['\*\.jar'\]\)",
        "implementation fileTree(dir: 'libs', include: ['*.jar', '*.aar'])",
        content,
    )
    # 如果没有 fileTree，添加
    if "fileTree(dir: 'libs'" not in content:
        content = content.replace(
            "compileOnly fileTree(dir: 'javaScaffoding'",
            "implementation fileTree(dir: 'libs', include: ['*.jar', '*.aar'])\n    compileOnly fileTree(dir: 'javaScaffoding'",
        )

    # incremental = true（在 compileOptions {} 块内）
    if "incremental" not in content:
        content = content.replace(
            "compileOptions {",
            "compileOptions {\n        incremental true",
        )

    # Java 11
    content = content.replace(
        "JavaVersion.VERSION_1_8",
        "JavaVersion.VERSION_11",
    )
    content = content.replace(
        "JavaVersion.VERSION_11_0",
        "JavaVersion.VERSION_11",
    )

    # CMake version → 3.22.1
    content = re.sub(
        r'version\s+"3\.\d+\.\d+"',
        'version "3.22.1"',
        content,
    )
    if 'version "3.' not in content and 'externalNativeBuild' in content:
        content = content.replace(
            'path "src/main/cpp/CMakeLists.txt"',
            'path "src/main/cpp/CMakeLists.txt"\n            version "3.22.1"',
        )

    # signingConfigs（每个项目自行生成 keystore：Ab123145 / jy）
    if "signingConfigs" not in content:
        # 项目根目录 keystore 不存在则生成（keytool -genkey，Ab123145 / jy）
        import shutil
        import subprocess as _sp
        project_root = app_gen.parent  # crackings/<type>/<Name>/project/
        keystore_path = project_root / "my.keystore.jks"
        if not keystore_path.is_file():
            _sp.run([
                "keytool", "-genkey", "-v",
                "-keystore", str(keystore_path),
                "-alias", "jy",
                "-keyalg", "RSA", "-keysize", "2048", "-validity", "100000",
                "-storepass", "Ab123145", "-keypass", "Ab123145",
                "-dname", "CN=jy, OU=jy, O=jy, L=Unknown, ST=Unknown, C=CN"
            ], capture_output=True)
            log_info(f"keystore: 项目根目录生成 {keystore_path}")
        else:
            check = _sp.run(
                ["keytool", "-list", "-keystore", str(keystore_path), "-storepass", "Ab123145"],
                capture_output=True, text=True
            )
            if check.returncode != 0:
                log_warn("keystore 密码不正确（应 Ab123145），重新生成")
                keystore_path.unlink(missing_ok=True)
                _sp.run([
                    "keytool", "-genkey", "-v",
                    "-keystore", str(keystore_path),
                    "-alias", "jy",
                    "-keyalg", "RSA", "-keysize", "2048", "-validity", "100000",
                    "-storepass", "Ab123145", "-keypass", "Ab123145",
                    "-dname", "CN=jy, OU=jy, O=jy, L=Unknown, ST=Unknown, C=CN"
                ], capture_output=True)
                log_info("keystore: 重新生成完成")
        # app/build.gradle 的 storeFile 相对 app/ 目录 → ../my.keystore.jks（项目根目录）
        signing_block = '''signingConfigs {
        debug {
            storeFile file("../my.keystore.jks")
            storePassword "Ab123145"
            keyAlias "jy"
            keyPassword "Ab123145"
        }
        release {
            storeFile file("../my.keystore.jks")
            storePassword "Ab123145"
            keyAlias "jy"
            keyPassword "Ab123145"
        }
    }

    buildTypes {
        debug {
            debuggable true
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt')
            signingConfig signingConfigs.debug
        }
        release {
            debuggable false
            minifyEnabled false
            proguardFiles getDefaultProguardFile('proguard-android.txt')
            signingConfig signingConfigs.release
        }
    }'''
        content = content.replace("buildTypes {", signing_block)

    # packagingOptions: jniLibs useLegacyPackaging（避免 extractNativeLibs 冲突）
    # [FLOWFIX] FakerAndroid 模板用 `//    packagingOptions {` 注释开括号做 toggle：
    # 换标准 AGP 插件后 android 块内出现裸 pickFirst/jniLibs 语句 → Groovy 语法错误。
    # 先取消开括号注释（块体已存在），再兜底注入。
    content = content.replace("//    packagingOptions {", "    packagingOptions {")
    if "useLegacyPackaging" not in content:
        content = content.replace(
            "packagingOptions {",
            "packagingOptions {\n        pickFirst '**/libc++_shared.so'\n        jniLibs {\n            useLegacyPackaging = true\n        }\n    }",
        )

    # 最低支持 Android 5.0（API 21），与原 APK 一致（用户确认保留低版本支持）
    content = re.sub(r"minSdkVersion\s+\d+", "minSdkVersion 21", content)

    # [FLOWFIX] useProguard 是 AGP <7 的 DSL，AGP 7.4.2 无此方法 → 编译报错。移除之。
    content = re.sub(r"\n\s*useProguard false", "", content)

    # [FLOWFIX] sensitiveOptions 是 FakerAndroid 专有 DSL（隐藏敏感代码），
    # 标准 AGP 插件无此方法 → 编译报错。整块移除。
    content = re.sub(
        r"\n\s*sensitiveOptions\s*\{[^}]*\}",
        "",
        content,
        flags=re.S,
    )

    bg.write_text(content, encoding="utf-8")
    log_info("app/build.gradle: compileSdk 33 / buildTools 30.0.3 / incremental / Java 11 / CMake 3.22.1 / signingConfigs")
    return True


def fix_settings_gradle(app_gen: Path) -> bool:
    """更新 settings.gradle：pluginManagement。"""
    sg = app_gen / "settings.gradle"
    sg.write_text(
        '// Toolchain standardized by crack pipeline\n'
        'pluginManagement {\n'
        '    repositories {\n'
        '        google()\n'
        '        mavenCentral()\n'
        '        gradlePluginPortal()\n'
        '    }\n'
        '}\n'
        '\n'
        "include ':app'\n",
        encoding="utf-8",
    )
    log_info("settings.gradle: pluginManagement 已配置")
    return True


def fix_gradle_properties(app_gen: Path) -> bool:
    """创建/更新 gradle.properties。"""
    gp = app_gen / "gradle.properties"
    gp.write_text(
        '# Toolchain standardized by crack pipeline\n'
        'org.gradle.jvmargs=-Xmx4096M -XX:+HeapDumpOnOutOfMemoryError -Dfile.encoding=UTF-8\n'
        'org.gradle.parallel=true\n'
        'org.gradle.daemon=true\n'
        'org.gradle.caching=true\n'
        'android.useAndroidX=true\n'
        'android.enableJetifier=true\n',
        encoding="utf-8",
    )
    log_info("gradle.properties: JVM 4G + 并行 + 守护 + 缓存")
    return True


def fix_cmake_lists(app_gen: Path) -> bool:
    """更新 CMakeLists.txt：cmake_minimum_required 3.15。"""
    cmake = app_gen / "app" / "src" / "main" / "cpp" / "CMakeLists.txt"
    if not cmake.is_file():
        return False
    content = cmake.read_text(encoding="utf-8")
    import re
    content = re.sub(
        r'cmake_minimum_required\(VERSION\s+\d+\.\d+(\.\d+)?\)',
        'cmake_minimum_required(VERSION 3.15)',
        content,
    )
    cmake.write_text(content, encoding="utf-8")
    log_info("CMakeLists.txt: cmake_minimum_required 3.15")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="工具链标准化")
    parser.add_argument("--name", required=True, help="项目名")
    args = parser.parse_args()

    name = args.name
    app_gen = _app_gen(name)

    if not app_gen.is_dir():
        log_error(f"app 缺失: {app_gen}")
        return 1

    log_step(f"工具链标准化 → {name}")

    fix_gradle_wrapper(app_gen)
    fix_project_build_gradle(app_gen)
    fix_app_build_gradle(app_gen)
    fix_settings_gradle(app_gen)
    fix_gradle_properties(app_gen)
    fix_cmake_lists(app_gen)

    log_success("工具链标准化完成")
    return 0


if __name__ == "__main__":
    sys.exit(main())
