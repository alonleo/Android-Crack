#!/usr/bin/env python3
"""Compare Addressables catalog and Android bundles with the merged original APK."""
from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
NAME = "DinoBashDinosaurBattle"
TYPE = "il2cpp"
ORIGINAL = ROOT / "crackings" / TYPE / NAME / "stages" / "runtime-diagnose" / "original-xapk.apk"
PROJECT = ROOT / "output-projects" / TYPE / NAME / "app" / "src" / "main" / "assets"


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> int:
    if not ORIGINAL.is_file() or not PROJECT.is_dir():
        print("[ERROR] original-xapk.apk or project assets missing")
        return 1
    with zipfile.ZipFile(ORIGINAL) as zin:
        original = {n: zin.read(n) for n in zin.namelist() if n.startswith("assets/aa/")}
    compared = 0
    different = []
    missing = []
    for path in PROJECT.joinpath("aa").rglob("*"):
        if not path.is_file():
            continue
        name = "assets/aa/" + str(path.relative_to(PROJECT / "aa"))
        compared += 1
        data = path.read_bytes()
        if name not in original:
            missing.append(name)
        elif digest(data) != digest(original[name]):
            different.append((name, digest(data), digest(original[name])))
    print(f"[INFO] 对比 Addressables 文件: {compared}")
    print(f"[INFO] 原始 APK assets/aa 文件: {len(original)}")
    print(f"[INFO] 当前工程缺少: {len(missing)}，内容不同: {len(different)}")
    for name in missing[:30]:
        print(f"[MISSING] {name}")
    for name, current, source in different[:30]:
        print(f"[DIFF] {name} current={current[:12]} original={source[:12]}")
    return 0 if not missing and not different else 2


if __name__ == "__main__":
    raise SystemExit(main())
