#!/usr/bin/env python3
"""Disable the optional Java callback in original boot smali.

The callback is not needed for A64 text capture and its descriptor can differ
across generated JNI builds; Unity itself must be allowed to continue startup.
"""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    path = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "smali" / "com" / "android" / "boot" / "MainActivity.smali"
    text = path.read_text(encoding="utf-8")
    old = "    invoke-virtual {p0, v0}, Lcom/android/boot/MainActivity;->registerCallBack(Lcom/android/boot/JniBridge;)V\n"
    if old in text:
        text = text.replace(old, "    # callback disabled; A64Hook collector does not require Java bridge\n", 1)
    path.write_text(text, encoding="utf-8")
    print(f"[OK] 已禁用原始 boot smali 的可选 callback: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
