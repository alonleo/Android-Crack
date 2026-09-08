#!/usr/bin/env python3
"""fix-fakerandroid-cmakelists.py — 把 FakerAndroid 生成的默认 CMakeLists.txt
替换为通用 file(GLOB) 模式（脱离 FakerAndroid base/tool cmake 包）。

FakerAndroid 默认 CMakeLists.txt 含:
    find_package(base REQUIRED CONFIG)
    target_link_libraries(native-lib base::tool ...)
脱离 FakerAndroid 工程后无法找到 `base` 包 → CMake 报错:
    CMakeLists.txt:7 (find_package): Could not find a config file for package "base"

替代方案（与 Alto's Adventure 一致）:
- 用 file(GLOB) 收集 cpp/*.cpp 和 And64InlineHook/*.cpp
- 仅链接 android/z/log/dl

用法:
    python3 skills/common/scripts/fix-fakerandroid-cmakelists.py <output-dir>
    # output-dir = crackings/<type>/<Name>/project/
"""
from __future__ import annotations

import sys
from pathlib import Path

CMAKE_LISTS = """cmake_minimum_required(VERSION 3.10)
project(native-lib)

set(CMAKE_CXX_STANDARD 11)

include_directories(src/main/cpp/include)

file(GLOB native_src "${CMAKE_SOURCE_DIR}/*.cpp")
file(GLOB and64_src "${CMAKE_SOURCE_DIR}/And64InlineHook/*.cpp")
list(APPEND native_src ${and64_src})

add_library(
        native-lib
        SHARED
        ${native_src}
)

target_link_libraries(
        native-lib
        android
        z
        log
        dl)
"""


def main() -> int:
    if len(sys.argv) != 2:
        print(f"用法: {sys.argv[0]} <crackings/<type>/<Name>/project>", file=sys.stderr)
        return 1
    out_dir = Path(sys.argv[1])
    app_dir = out_dir / "app"
    if not app_dir.is_dir():
        print(f"[ERR] {app_dir} 不存在", file=sys.stderr)
        return 1
    cpp_dir = app_dir / "src" / "main" / "cpp"
    if not cpp_dir.is_dir():
        print(f"[ERR] {cpp_dir} 不存在", file=sys.stderr)
        return 1

    target = cpp_dir / "CMakeLists.txt"
    target.write_text(CMAKE_LISTS, encoding="utf-8")
    print(f"[OK] 写入标准 CMakeLists.txt → {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())