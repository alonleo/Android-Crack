#!/usr/bin/env python3
"""Clean stale Gradle/CMake intermediates before rebuilding boot smali changes."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    root = REPO / "output-projects" / type_arg / name
    removed = []
    for path in (root / "app" / "build", root / "app" / ".cxx", root / ".gradle"):
        if path.exists():
            shutil.rmtree(path)
            removed.append(str(path))
    print(f"[OK] 已清理构建缓存 {len(removed)} 项")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
