#!/usr/bin/env python3
"""Toggle the A64 text collector call for isolation testing."""
from __future__ import annotations

import argparse
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disable", action="store_true")
    args = ap.parse_args()
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    cpp = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "cpp" / "native-lib.cpp"
    text = cpp.read_text(encoding="utf-8")
    if args.disable:
        text = text.replace("    start_text_capture_loader();", "    // start_text_capture_loader();")
        print("[OK] 已禁用 A64 文本 hook loader（隔离测试）")
    else:
        text = text.replace("    // start_text_capture_loader();", "    start_text_capture_loader();")
        print("[OK] 已启用 A64 文本 hook loader")
    cpp.write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
