#!/usr/bin/env python3
"""fix-faker-build-gradle.py — 修复 FakerAndroid 输出的 app/build.gradle 到可编译状态。

背景: FakerAndroid fake 生成的 build.gradle 基于 AGP 3.x（compileSdkVersion 29，
useProguard DSL），与 AGP 7.4.2 不兼容（useProguard 不存在 → 编译报错）。
每次 il2cpp 项目都要手工改，固化为脚本（来源 FormulaCarStuntCarGames 2026-08-06）。

修复项:
  1. compileSdkVersion/buildToolsVersion → 34 / 34.0.0
  2. targetSdkVersion 28 → 34
  3. 移除 useProguard（AGP 7.4.2 无此 DSL）
  4. 加 signingConfigs（debug/release → ../my.keystore.jks, jy/Ab123145）
  5. abiFilters → 只保留项目实际 ABI（从 jniLibs 目录推断）
  6. versionCode/versionName 从 APK 原值（--version-code/--version-name 可选）
  7. packagingOptions doNotStrip libil2cpp.so/libunity.so

用法:
  python3 fix-faker-build-gradle.py <project_dir> [--abi arm64-v8a] \
      [--version-code 88] [--version-name 1.8.7]

依赖: 无（纯文本处理）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def _resolve_abi(project_dir: Path) -> str:
    jni = project_dir / "app" / "src" / "main" / "jniLibs"
    if jni.is_dir():
        abis = [p.name for p in jni.iterdir() if p.is_dir()]
        if abis:
            return abis[0]
    return "arm64-v8a"


def fix_build_gradle(project_dir: Path, abi: str, version_code: str = "1", version_name: str = "1.0") -> bool:
    bg = project_dir / "app" / "build.gradle"
    if not bg.is_file():
        print(f"[ERROR] 不存在: {bg}")
        return False
    text = bg.read_text(encoding="utf-8")

    # 1. compileSdkVersion/buildToolsVersion → 33/34.0.0
    text = text.replace("compileSdkVersion 29", "compileSdk 33")
    text = text.replace("compileSdkVersion 28", "compileSdk 33")
    text = text.replace("buildToolsVersion '29.0.3'", "buildToolsVersion '34.0.0'")

    # 2. targetSdkVersion → 34
    text = re.sub(r"targetSdkVersion \d+", "targetSdkVersion 34", text)

    # 3. 移除 useProguard
    text = re.sub(r"\n\s*useProguard false", "", text)

    # 4. signingConfigs 块（若缺失）
    if "signingConfigs {" not in text:
        text = text.replace(
            "    buildToolsVersion '34.0.0'",
            "    buildToolsVersion '34.0.0'\n"
            "    signingConfigs {\n"
            "        debug {\n"
            "            storeFile file(\"../my.keystore.jks\")\n"
            "            storePassword \"Ab123145\"\n"
            "            keyAlias \"jy\"\n"
            "            keyPassword \"Ab123145\"\n"
            "        }\n"
            "        release {\n"
            "            storeFile file(\"../my.keystore.jks\")\n"
            "            storePassword \"Ab123145\"\n"
            "            keyAlias \"jy\"\n"
            "            keyPassword \"Ab123145\"\n"
            "        }\n"
            "    }",
            1,
        )

    # 5. abiFilters → 目标 ABI
    text = re.sub(
        r"abiFilters '[^']*'",
        f"abiFilters '{abi}'",
        text,
    )

    # 6. versionCode/versionName
    text = re.sub(r"versionCode \d+", f"versionCode {version_code}", text)
    text = re.sub(r"versionName '[^']*'", f"versionName '{version_name}'", text)

    # 7. release signingConfig → release（而非 debug）
    text = text.replace(
        "signingConfig signingConfigs.debug\n        }",
        "signingConfig signingConfigs.release\n        }",
    )

    # 8. packagingOptions（若缺失）
    if "packagingOptions {" not in text:
        text = text.replace(
            "    //TODO NOTE This is a FakerAndroid feature",
            "    packagingOptions {\n"
            "        doNotStrip '*/" + abi + "/libil2cpp.so'\n"
            "        doNotStrip '*/" + abi + "/libunity.so'\n"
            "    }\n"
            "    //TODO NOTE This is a FakerAndroid feature",
            1,
        )

    bg.write_text(text, encoding="utf-8")
    print(f"[OK] app/build.gradle 已修复: compileSdk 33 / targetSdk 34 / abi={abi} / "
          f"versionCode={version_code} / versionName={version_name} / signing / packaging")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="修复 FakerAndroid build.gradle")
    parser.add_argument("project_dir", help="crackings/<type>/<Name>/project/ 目录")
    parser.add_argument("--abi", default="", help="目标 ABI（默认从 jniLibs 推断）")
    parser.add_argument("--version-code", default="1")
    parser.add_argument("--version-name", default="1.0")
    args = parser.parse_args()

    pd = Path(args.project_dir)
    abi = args.abi or _resolve_abi(pd)
    return 0 if fix_build_gradle(pd, abi, args.version_code, args.version_name) else 1


if __name__ == "__main__":
    sys.exit(main())
