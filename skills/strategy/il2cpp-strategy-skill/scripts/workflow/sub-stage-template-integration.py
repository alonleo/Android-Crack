#!/usr/bin/env python3
"""
阶段 12 - 集成模板文件（il2cpp 专用）
=================================================================
原 stage-04-wire-templates.py 拆分：
  - 12 (模板)：MainActivity + App + JniBridge + AndroidManifest + native-lib.cpp
  - 14 (SDKUtils)：com/android/common/SDKUtils.java

输入：crackings/<type>/<Name>/project/
  （预处理阶段已生成 settings.gradle/gradlew/app/）
输出：
  - app/src/main/java/com/android/boot/{MainActivity,App,JniBridge}.java
  - app/src/main/cpp/native-lib.cpp（A64HookFunction 模式，**非** fakeCpp）
  - app/src/main/AndroidManifest.xml（指向 com.android.boot.MainActivity）

模板源：
  - skills/common/scripts/template-files/MainActivity.template.java
  - skills/common/scripts/template-files/JniBridge.template.java
  - skills/common/scripts/template-files/il2cpp/native-lib.template.cpp
  - App.java（由本脚本生成）

[FLOWFIX]:
  原实现委托给已删除的旧编号脚本（stage-04-wire-templates.py），
  该脚本已被 REFACTOR 删除，导致 12 阶段实际什么都不做（return 0），
  AS 工程中的 native-lib.cpp 停留在 FakerAndroid fake 模式（fakeCpp + 单点 hook），
  patched.apk 启动后 UnityPlayerActivity 段错误（libil2cpp.so 偏移错误 + fakeCpp
  inline hook 写到错误地址导致 SIGSEGV）。

本修复直接内联实现：
  1. 拷贝 MainActivity.template.java → com/android/boot/MainActivity.java
     （替换占位符 {PACKAGE_NAME}/{ORIGINAL_ACTIVITY}/{ORIGINAL_ACTIVITY_IMPORT}/{NATIVE_LIB_LOAD}/{VIDEO_COMPLETE_CALLBACK}）
  2. 拷贝 JniBridge.template.java → com/android/boot/JniBridge.java
  3. 生成 App.java（精简版，含 installNativeHooks/registerCallBack 调用）
  4. 拷贝 native-lib.template.cpp → cpp/native-lib.cpp（A64HookFunction 模式）
  5. 复制 AndroidManifest.xml（如果不存在）

真机验收：sub-stage-template-device-verify.py（stage 13）
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
TEMPLATE_DIR = REPO / "tools" / "scripts" / "template-files"


def _resolve_name() -> str:
    name = os.environ.get('NAME', '').strip()
    if not name:
        print("[stage-12] NAME 环境变量未设置", file=sys.stderr)
        sys.exit(1)
    return name


def _app_main(name: str) -> Path:
    type_arg = os.environ.get("TYPE", "").strip()
    if type_arg:
        return REPO / "output-projects" / type_arg / name / "app" / "src" / "main"
    return REPO / "output-projects" / name / "app" / "src" / "main"


def _crack_raw(name: str) -> Path:
    type_arg = os.environ.get("TYPE", "").strip()
    if type_arg:
        return REPO / "crackings" / type_arg / name / "raw" / "01-apktool"
    return REPO / "crackings" / name / "raw" / "01-apktool"


def _read_text(p: Path) -> str:
    try:
        return p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return p.read_text(encoding="utf-8", errors="ignore")


def _detect_original_activity(raw_dir: Path) -> tuple[str, str]:
    """从 apktool 解包的 AndroidManifest.xml 提取原始 launcher activity 的 name + import。

    返回 (class_name, full_import)。
    class_name = 'UnityPlayerActivity'（短名）
    full_import = 'com.unity3d.player.UnityPlayerActivity'（包名.类名）
    """
    manifest = _read_text(raw_dir / "AndroidManifest.xml")
    # 找 LAUNCHER intent-filter 所在的 activity
    # 简单匹配：<activity ... android:name="X.Y.Z" ...> ... <category android:name="android.intent.category.LAUNCHER"/>
    m = re.search(
        r'<activity[^>]+android:name="([^"]+)"[^>]*>(?:(?!</activity>).)*?<category[^>]+LAUNCHER',
        manifest,
        re.DOTALL,
    )
    if not m:
        return "UnityPlayerActivity", "com.unity3d.player.UnityPlayerActivity"
    full = m.group(1)
    if full.startswith("."):
        # 相对包名 → 拼上 manifest package
        pkg_m = re.search(r'package="([^"]+)"', manifest)
        pkg = pkg_m.group(1) if pkg_m else ""
        full = pkg + full
    short = full.rsplit(".", 1)[-1]
    return short, full


def _copy_manifest(app_main: Path, raw_dir: Path) -> None:
    """复制 AndroidManifest.xml（如果不存在）。"""
    manifest_dst = app_main / "AndroidManifest.xml"
    if manifest_dst.exists():
        return
    manifest_src = raw_dir / "AndroidManifest.xml"
    if manifest_src.exists():
        shutil.copy2(manifest_src, manifest_dst)
        print(f"[stage-12] 复制 AndroidManifest.xml 从 {manifest_src}")


def _copy_main_activity(app_main: Path, original_short: str, original_import: str, native_lib_load: str) -> None:
    """拷贝 MainActivity.template.java → com/android/boot/MainActivity.java，替换占位符。"""
    src = TEMPLATE_DIR / "MainActivity.template.java"
    if not src.exists():
        print(f"[WARN] [stage-12] 模板缺失: {src}", file=sys.stderr)
        return
    dst_dir = app_main / "java" / "com" / "android" / "boot"
    dst_dir.mkdir(parents=True, exist_ok=True)
    text = _read_text(src)
    text = text.replace("{PACKAGE_NAME}", "com.android.boot")
    text = text.replace("{ORIGINAL_ACTIVITY}", original_short)
    text = text.replace("{ORIGINAL_ACTIVITY_IMPORT}", original_import)
    text = text.replace("{NATIVE_LIB_LOAD}", native_lib_load)
    text = text.replace("{VIDEO_COMPLETE_CALLBACK}", "onVideoReward(isSucess)")
    dst = dst_dir / "MainActivity.java"
    dst.write_text(text, encoding="utf-8")
    print(f"[stage-12] 生成 {dst}")


def _copy_jni_bridge(app_main: Path) -> None:
    src = TEMPLATE_DIR / "JniBridge.template.java"
    if not src.exists():
        print(f"[WARN] [stage-12] 模板缺失: {src}", file=sys.stderr)
        return
    dst_dir = app_main / "java" / "com" / "android" / "boot"
    dst_dir.mkdir(parents=True, exist_ok=True)
    text = _read_text(src)
    text = text.replace("{PACKAGE_NAME}", "com.android.boot")
    dst = dst_dir / "JniBridge.java"
    dst.write_text(text, encoding="utf-8")
    print(f"[stage-12] 生成 {dst}")


def _gen_app(app_main: Path) -> None:
    """生成精简版 App.java（FakerAndroid 入口：installNativeHooks + registerCallBack）。"""
    dst_dir = app_main / "java" / "com" / "android" / "boot"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "App.java"
    if dst.exists():
        return  # 不覆盖已有
    text = '''package com.android.boot;

import android.app.Application;
import android.content.Context;

/**
 * App — il2cpp skill 标准 Application 类
 *
 * [FLOWFIX]
 * 原 FakerAndroid 生成版本只有 fakeApp/fakeDex，没有 installNativeHooks，
 * 导致 native-lib.cpp 的 setupHooks 从未被调用（native hook 框架不生效）。
 * 按 il2cpp skill references/native-hook-engine-setup.md §1：
 *   - onCreate 里调用 installNativeHooks()（后台线程轮询 libil2cpp.so
 *     → /proc/self/maps 解析页对齐基址 → setupHooks(base)）
 *   - attachBaseContext 里保留 fakeDex（FakerAndroid 兼容）
 */
public class App extends Application {

    static {
        System.loadLibrary("native-lib");
    }

    @Override
    public void attachBaseContext(Context base) {
        super.attachBaseContext(base);
        fakeDex(base);
    }

    @Override
    public void onCreate() {
        super.onCreate();
        fakeApp(this);
        // il2cpp skill: 触发 native hook 框架（后台线程等待 libil2cpp.so 加载）
        installNativeHooks();
    }

    public native void installNativeHooks();
    private native void fakeApp(Application application);
    private native void fakeDex(Context base);

}
'''
    dst.write_text(text, encoding="utf-8")
    print(f"[stage-12] 生成 {dst}")


def _copy_native_lib(app_main: Path, project_name: str) -> None:
    """拷贝 native-lib.template.cpp → cpp/native-lib.cpp（A64HookFunction 模式，**非** fakeCpp）。"""
    src = TEMPLATE_DIR / "il2cpp" / "native-lib.template.cpp"
    if not src.exists():
        print(f"[WARN] [stage-12] native-lib 模板缺失: {src}", file=sys.stderr)
        return
    dst_dir = app_main / "cpp"
    dst_dir.mkdir(parents=True, exist_ok=True)
    text = _read_text(src)
    # 替换 {PROJECT_NAME} 占位符（如果模板里有）
    text = text.replace("{PROJECT_NAME}", project_name)
    dst = dst_dir / "native-lib.cpp"
    if dst.exists():
        # [FLOWFIX] 必须覆盖：旧版本是 FakerAndroid fakeCpp 模式
        # 会让 patched.apk 启动崩溃（UnityPlayerActivity 段错误）
        backup = dst.with_suffix(".cpp.bak-fakecpp")
        if not backup.exists():
            shutil.copy2(dst, backup)
            print(f"[stage-12] 备份 fakeCpp 版 native-lib.cpp 到 {backup}")
    dst.write_text(text, encoding="utf-8")
    print(f"[stage-12] 生成 {dst}")


def _copy_and64_inline_hook(app_main: Path) -> None:
    """拷贝 And64InlineHook 源码到 cpp/And64InlineHook/（CMake 编译需要）。

    [FLOWFIX]:
    CMakeLists.txt 引用 And64InlineHook.cpp，但 FakerAndroid 重建后没拷贝这个目录，
    导致 native-lib 编译失败（A64HookFunction 未定义）。
    源：tools/crack-intergration-tools/source-projects/And64InlineHook/
    """
    src_dir = REPO / "tools" / "crack-intergration-tools" / "source-projects" / "And64InlineHook"
    if not src_dir.exists():
        print(f"[WARN] [stage-12] And64InlineHook 源码缺失: {src_dir}", file=sys.stderr)
        return
    dst_dir = app_main / "cpp" / "And64InlineHook"
    if dst_dir.exists():
        # 已经存在不覆盖（可能是用户自定义版本）
        return
    shutil.copytree(src_dir, dst_dir)
    print(f"[stage-12] 拷贝 And64InlineHook 到 {dst_dir}")


def _fix_cmake(app_main: Path) -> None:
    """修复 CMakeLists.txt：补全 And64InlineHook 子目录 GLOB。

    [FLOWFIX]:
    FakerAndroid 生成的 CMakeLists.txt 用 `file(GLOB ... "${CMAKE_SOURCE_DIR}/*.cpp")`
    不包含子目录 → And64InlineHook.cpp 不被编译 → A64HookFunction 未定义。
    改为同时 GLOB And64InlineHook/*.cpp，并替换 add_library 的源文件列表用 ${inlinehook_src}。
    """
    cmake = app_main / "cpp" / "CMakeLists.txt"
    if not cmake.exists():
        return
    text = _read_text(cmake)
    # 备份
    bak = cmake.with_suffix(".txt.bak-faker")
    if not bak.exists():
        shutil.copy2(cmake, bak)
    # 替换 GLOB 行
    new_glob = (
        'file(GLOB native_src "${CMAKE_SOURCE_DIR}/*.cpp")\n'
        'file(GLOB inlinehook_src "${CMAKE_SOURCE_DIR}/And64InlineHook/*.cpp")\n'
    )
    if "And64InlineHook/*.cpp" not in text:
        # 替换现有的 file(GLOB ...) 行
        text = re.sub(
            r'file\(GLOB[^)]+\)\n?',
            new_glob,
            text,
            count=1,
        )
    # 把 add_library 的源文件列表替换为 ${native_src} ${inlinehook_src}
    # 匹配 add_library(name SHARED ...files...) → add_library(name SHARED ${native_src} ${inlinehook_src})
    text = re.sub(
        r'add_library\s*\(\s*([\w-]+)\s+SHARED\s+([^)]*)\)',
        lambda m: f"add_library({m.group(1)} SHARED ${{native_src}} ${{inlinehook_src}})",
        text,
    )
    cmake.write_text(text, encoding="utf-8")
    print(f"[stage-12] 修复 CMakeLists.txt: 加 And64InlineHook GLOB + 用变量替换源列表")


def main() -> int:
    name = _resolve_name()
    app_main = _app_main(name)
    app_main.mkdir(parents=True, exist_ok=True)
    raw_dir = _crack_raw(name)

    # 1. 复制 AndroidManifest.xml
    _copy_manifest(app_main, raw_dir)

    # 2. 探测原始 launcher activity（用于 MainActivity 模板占位符）
    original_short, original_import = "UnityPlayerActivity", "com.unity3d.player.UnityPlayerActivity"
    if raw_dir.exists():
        original_short, original_import = _detect_original_activity(raw_dir)
    print(f"[stage-12] 原始 launcher: {original_import}")

    # 3. 复制 MainActivity + JniBridge + App
    # [FLOWFIX]:
    # 第一次修复（extends Activity）解决编译问题但导致黑屏——MainActivity
    # 不加载 Unity 引擎（1 帧渲染，黑屏）。按 skill 第 4 条：
    # launcher 必须 extends 真正的 com.unity3d.player.UnityPlayerActivity。
    # UnityPlayerActivity 在 smali_classes5（注入 dex），libs jar 提供编译期 classpath。
    _copy_main_activity(app_main, "UnityPlayerActivity", "com.unity3d.player.UnityPlayerActivity", 'System.loadLibrary("native-lib")')
    _copy_jni_bridge(app_main)
    _gen_app(app_main)

    # 4. 复制 native-lib.cpp（A64HookFunction 模式）
    _copy_native_lib(app_main, name)

    # 5. 复制 And64InlineHook 源码（CMake 编译需要）
    _copy_and64_inline_hook(app_main)

    # 6. 修复 CMakeLists.txt（补全 And64InlineHook 子目录）
    _fix_cmake(app_main)

    print(f"[stage-12] 阶段 12 完成 → {app_main}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
