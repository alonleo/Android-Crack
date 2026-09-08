#!/usr/bin/env python3
"""inject-native-hook-loader.py — 把 native-lib 加载 + installNativeHooks 注入真实 Application。

背景: FlyingGorillaEndlessRunner (2026-08-02) 的 native hook 从未生效——
FakerAndroid 生成的 `com.android.boot.App`（含 fakeApp → 装 hook）不是 manifest 的
Application；真实 Application 是原游戏的 `com.pairip.application.Application`。
本脚本把「加载 native-lib + 调用 App.installNativeHooks()」注入到真实 Application
的 attachBaseContext，使 native hook 能随应用启动安装。

前置（一次性，脚本外完成）:
  1. `com/android/boot/App.java` 增加 `public static native void installNativeHooks();`
  2. `native-lib.cpp` 实现 `Java_com_android_boot_App_installNativeHooks`（建议后台线程
     轮询 libil2cpp.so，用 dl_iterate_phdr 取真实基址后 setupHooks——见 il2cpp experience）

用法:
  python3 inject-native-hook-loader.py <apktool_root> [--app-class com.android.boot.App]

示例:
  python3 inject-native-hook-loader.py crackings/FlyingGorillaEndlessRunner/raw/01-apktool

说明:
  - 读取 <apktool_root>/AndroidManifest.xml 的 <application android:name>
  - 在 smali_classesN 中找到该类，向 attachBaseContext 注入 loadLibrary + installNativeHooks
  - 幂等：已注入过则跳过
  - 注入后需重跑 inject-smali-dex.py --force 生效
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

LOADER_CODE = """
    # === injected by inject-native-hook-loader.py: 加载 native-lib 并安装 hooks ===
    const-string v0, "native-lib"

    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V

    invoke-static {}, {app_class};->installNativeHooks()V
"""


def find_application_class(manifest: Path) -> str | None:
    text = manifest.read_text(encoding="utf-8")
    m = re.search(r'<application\b[^>]*\bandroid:name="([^"]+)"', text)
    return m.group(1) if m else None


def find_smali_file(smali_root: Path, class_name: str) -> Path | None:
    rel = class_name.replace(".", "/") + ".smali"
    for d in sorted(smali_root.glob("smali*")):
        if not d.is_dir():
            continue
        f = d / rel
        if f.is_file():
            return f
    return None


def inject_attach_base_context(smali_file: Path, app_class: str) -> bool:
    text = smali_file.read_text(encoding="utf-8")
    if "installNativeHooks" in text:
        print(f"[SKIP] {smali_file} 已注入过")
        return False

    # 定位 attachBaseContext 方法体
    m = re.search(r'(\.method[^\n]*attachBaseContext[^\n]*\n)(.*?)(\.end method)',
                  text, re.DOTALL)
    if not m:
        print(f"[WARN] {smali_file} 无 attachBaseContext")
        return False

    sig = m.group(1)
    body = m.group(2)
    end = m.group(3)

    # 确保 .locals >= 1（const-string 需要 v0）
    locals_m = re.search(r'\.locals (\d+)', body)
    if locals_m:
        n = int(locals_m.group(1))
        if n < 1:
            body = body.replace(f".locals {n}", ".locals 1", 1)
    else:
        # 在 body 开头加 .locals 1
        body = "    .locals 1\n" + body

    loader = LOADER_CODE.format(app_class=app_class)
    # 注入到 super.attachBaseContext 调用之前
    new_body = re.sub(r'(\s*invoke-super)',
                      loader.rstrip() + r"\n\1", body, count=1)
    if new_body == body:
        print(f"[WARN] {smali_file} 未找到 invoke-super 锚点")
        return False

    text = text[:m.start()] + sig + new_body + end + text[m.end():]
    smali_file.write_text(text, encoding="utf-8")
    print(f"[OK]   {smali_file} attachBaseContext 已注入 hook 加载")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="注入 native-lib hook 加载到真实 Application")
    parser.add_argument("apktool_root", help="apktool 解包根目录（含 AndroidManifest.xml + smali_classesN/）")
    parser.add_argument("--app-class", default="com.android.boot.App",
                        help="包含 installNativeHooks 的 App 类（默认 com.android.boot.App）")
    args = parser.parse_args()

    root = Path(args.apktool_root)
    manifest = root / "AndroidManifest.xml"
    if not manifest.is_file():
        print(f"[ERROR] AndroidManifest.xml 不存在: {manifest}")
        return 1

    app_cls = find_application_class(manifest)
    if not app_cls:
        print("[WARN] manifest 无 <application android:name>；无法定位真实 Application")
        return 1
    print(f"[INFO] 真实 Application: {app_cls}")

    smali = find_smali_file(root, app_cls)
    if not smali:
        print(f"[ERROR] 未找到 {app_cls}.smali")
        return 1

    ok = inject_attach_base_context(smali, args.app_class)
    if ok:
        print("[INFO] 注入后需: 1) App.java 加 installNativeHooks native 方法 2) native-lib.cpp 实现它 "
              "3) 重跑 inject-smali-dex.py --force")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
