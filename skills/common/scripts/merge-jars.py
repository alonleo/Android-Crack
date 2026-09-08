#!/usr/bin/env python3
"""合并多个 jar 为单一 jar（去重，保留所有 class/resource）。"""
import zipfile, sys, shutil
from pathlib import Path

def merge_jars(jars: list[Path], out: Path):
    seen = set()
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as zout:
        for jar in sorted(jars):
            with zipfile.ZipFile(jar) as zin:
                for item in zin.namelist():
                    if item in seen:
                        continue
                    seen.add(item)
                    data = zin.read(item)
                    zout.writestr(item, data)
    print(f"合并 {len(jars)} 个 jar → {out} ({out.stat().st_size // 1024} KB)")

if __name__ == '__main__':
    libs_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else libs_dir / 'classes.all.jar'
    jars = sorted(libs_dir.glob('classes.*.dex.jar'))
    if not jars:
        jars = sorted(libs_dir.glob('*.jar'))
    merge_jars(jars, out_path)
