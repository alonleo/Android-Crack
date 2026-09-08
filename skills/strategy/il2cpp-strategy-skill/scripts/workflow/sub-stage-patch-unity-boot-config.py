#!/usr/bin/env python3
"""Patch Unity boot.config render threading for blank-screen diagnosis."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    path = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "assets" / "bin" / "Data" / "boot.config"
    text = path.read_text(encoding="utf-8")
    text = text.replace("gfx-disable-mt-rendering=1", "gfx-disable-mt-rendering=0")
    text = text.replace("gfx-threading-mode=4", "gfx-threading-mode=0")
    path.write_text(text, encoding="utf-8")
    print(f"[OK] Unity 渲染线程配置已调整: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
