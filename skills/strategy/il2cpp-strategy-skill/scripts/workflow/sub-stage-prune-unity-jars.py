#!/usr/bin/env python3
"""Keep only the smali jar needed to compile UnityPlayerActivity."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    if not name or not type_arg:
        raise SystemExit("NAME and TYPE are required")
    libs = REPO / "output-projects" / type_arg / name / "app" / "libs"
    keep = {libs / "smali.jar", libs / "smali_classes5.jar", libs / "smali_classes6.jar", libs / "smali_classes7.jar"}
    missing = [str(path) for path in keep if not path.is_file()]
    if missing:
        raise SystemExit(f"required jars missing: {missing}")
    removed = 0
    for jar in libs.glob("*.jar"):
        if jar not in keep:
            jar.unlink()
            removed += 1
    print(f"[OK] 保留 UnityPlayerActivity 依赖 smali_classes6/7.jar，删除冲突 jar {removed} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
