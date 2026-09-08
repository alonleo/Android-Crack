#!/usr/bin/env python3
"""
将 smali→jar 产物拆分为多个子 jar（每个最多 N 个 class 条目）。
D8 desugaring 对单一超大 jar 递归展开会 StackOverflow，拆小后分批处理可规避。
"""
import zipfile, sys
from pathlib import Path

def split_jar(jar: Path, out_dir: Path, max_per_jar: int = 12000):
    out_dir.mkdir(parents=True, exist_ok=True)
    all_entries = []
    with zipfile.ZipFile(jar) as z:
        for name in z.namelist():
            if name.endswith('.class'):
                all_entries.append((name, z.read(name)))

    total = len(all_entries)
    print(f"总计 {total} 个 .class，拆分为每份最多 {max_per_jar}")

    for i in range(0, total, max_per_jar):
        chunk = all_entries[i:i + max_per_jar]
        part_path = out_dir / f"part{i // max_per_jar + 1}.jar"
        with zipfile.ZipFile(part_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for name, data in chunk:
                zout.writestr(name, data)
        print(f"  part{i // max_per_jar + 1}: {len(chunk)} classes → {part_path.name}")

    print(f"拆分完成: {out_dir}")

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("jar")
    ap.add_argument("--out", required=True)
    ap.add_argument("--max", type=int, default=12000)
    args = ap.parse_args()
    split_jar(Path(args.jar), Path(args.out), args.max)
