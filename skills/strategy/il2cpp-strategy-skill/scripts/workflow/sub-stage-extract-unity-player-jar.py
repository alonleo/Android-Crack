#!/usr/bin/env python3
"""Extract only Unity player classes from converted smali jars for javac."""
from __future__ import annotations

import os
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    if not name or not type_arg:
        raise SystemExit("NAME and TYPE are required")
    libs = REPO / "output-projects" / type_arg / name / "app" / "libs"
    jars = sorted(libs.glob("smali*.jar"))
    if not jars:
        raise SystemExit(f"no converted jars in {libs}")
    out = libs / "unity-player.jar"
    entries = {}
    for jar in jars:
        with zipfile.ZipFile(jar) as source:
            for info in source.infolist():
                if (info.filename.startswith("com/unity3d/player/") or info.filename.startswith("org/fmod/")) and info.filename.endswith(".class"):
                    entries.setdefault(info.filename, source.read(info))
    if not entries:
        raise SystemExit("no com/unity3d/player classes found")
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as dest:
        for path, data in sorted(entries.items()):
            dest.writestr(path, data)
    for jar in jars:
        jar.unlink()
    print(f"[OK] 生成精简 Unity player jar: {out}（{len(entries)} 个 class）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
