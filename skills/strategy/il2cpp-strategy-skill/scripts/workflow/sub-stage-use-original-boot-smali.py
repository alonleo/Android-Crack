#!/usr/bin/env python3
"""Use original FakerAndroid boot smali instead of reconstructed Java boot classes."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    root = REPO / "output-projects" / type_arg / name
    boot_java = root / "app" / "src" / "main" / "java" / "com" / "android" / "boot"
    removed = 0
    if boot_java.is_dir():
        for path in boot_java.glob("*.java"):
            path.unlink()
            removed += 1
    libs = root / "app" / "libs"
    for jar in libs.glob("*.jar"):
        jar.unlink()
    print(f"[OK] 已移除重构 boot Java 类 {removed} 个，改用原始 boot smali 注入")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
