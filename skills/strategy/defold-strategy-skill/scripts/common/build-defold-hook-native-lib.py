#!/usr/bin/env python3
"""build-defold-hook-native-lib.py — 编译 Defold SDK hook native-lib.so（And64InlineHook）。

策略: skills/strategy/defold-strategy-skill/strategy.md §7
目标: hook lib<game>.so 导出的 Java_com_defold_*_addToQueue 符号（SDK 命令咽喉）。

用法:
  python3 build-defold-hook-native-lib.py <src-cpp-dir> -o <out>/libnative-lib.so
  # src-cpp-dir 须含 native-lib.cpp + And64InlineHook/{And64InlineHook.cpp,.hpp}

说明:
  - 用 tools/environments 的 NDK aarch64 clang++ 编译
  - -static-libstdc++（否则运行时 UnsatisfiedLinkError: libc++_shared.so not found）
  - 输出 arm64-v8a 的 libnative-lib.so
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


def _find_root():
    p = Path(__file__).resolve().parent
    for _ in range(7):
        if (p / "apks").is_dir() and (p / "tools").is_dir():
            return p
        p = p.parent
    raise SystemExit("无法定位仓库根目录")


ROOT = _find_root()
NDK_VER = "25.2.9519653"


def find_clang() -> str:
    ndk = ROOT / "tools" / "environments" / "android-sdk" / "ndk"
    if not ndk.is_dir():
        raise SystemExit("NDK 未安装")
    cand = ndk / NDK_VER / "toolchains" / "llvm" / "prebuilt" / "linux-x86_64"
    if not cand.is_dir():
        # 自动探测任意已装 NDK
        vers = sorted(ndk.iterdir(), reverse=True)
        cand = vers[0] / "toolchains" / "llvm" / "prebuilt" / "linux-x86_64" if vers else None
    clang = cand / "bin" / "aarch64-linux-android21-clang++"
    if not clang.is_file():
        raise SystemExit(f"clang 未找到: {clang}")
    return str(clang)


def main() -> int:
    ap = argparse.ArgumentParser(description="编译 Defold SDK hook native-lib.so")
    ap.add_argument("src", help="cpp 源码目录（含 native-lib.cpp + And64InlineHook/）")
    ap.add_argument("-o", "--output", default="libnative-lib.so", help="输出 .so 路径")
    args = ap.parse_args()

    src = Path(args.src)
    native_cpp = src / "native-lib.cpp"
    inline_cpp = src / "And64InlineHook" / "And64InlineHook.cpp"
    if not native_cpp.is_file() or not inline_cpp.is_file():
        print(f"[ERROR] 缺少 native-lib.cpp 或 And64InlineHook/And64InlineHook.cpp in {src}", file=sys.stderr)
        return 1

    clang = find_clang()
    sysroot = str(Path(clang).parent.parent / "sysroot")
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = [
        clang, f"--sysroot={sysroot}", "-std=c++11", "-fPIC", "-shared", "-O2",
        "-static-libstdc++",
        str(native_cpp), str(inline_cpp),
        "-o", str(out), "-llog", "-ldl",
    ]
    print(f"[INFO] {' '.join(cmd)}")
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        return 1
    # 校验动态依赖不含 libc++_shared.so
    ldd = subprocess.run(["readelf", "-d", str(out)], capture_output=True, text=True)
    if "libc++_shared.so" in ldd.stdout:
        print("[ERROR] 仍链接 libc++_shared.so（需 -static-libstdc++）", file=sys.stderr)
        return 1
    print(f"[OK] {out} ({out.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
