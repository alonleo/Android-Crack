#!/usr/bin/env python3
"""
用 dx.jar 将多个 jar 合并为一个 classes.dex（绕过 AGP javac/desugar）。
用法：python3 dx-merge-jars.py --dx-jar /path/to/dx.jar --jars-dir libs/split --out build/dx_out/classes.dex
"""
import subprocess, sys, os, shutil, argparse
from pathlib import Path

def merge_jars_to_dex(dx_jar: Path, jars_dir: Path, out_dex: Path):
    jars = sorted(jars_dir.glob('*.jar'))
    if not jars:
        raise RuntimeError(f"No jars in {jars_dir}")

    out_dex.parent.mkdir(parents=True, exist_ok=True)

    # 方案：用 dx --output 逐个处理 jar，输出为 classes.dex
    # dx 接受多个输入 jar，输出单一 dex
    cmd = [
        'java', '-Xmx4096M', '-Xss2M', '-cp', str(dx_jar),
        'com.android.dx.command.dexer.Main', '--dex',
        '--output=' + str(out_dex),
    ]
    for j in jars:
        cmd.append(str(j))
    # dx 的 main class 是 com.android.multidex.DxContext
    print(f"Running: java -Xmx4096M -Xss2M -cp {dx_jar} ...")
    print(f"Input jars: {[j.name for j in jars]}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print("STDOUT:", result.stdout[-500:])
        print("STDERR:", result.stderr[-2000:])
        raise RuntimeError(f"dx failed: {result.stderr}")
    print(f"Output: {out_dex} ({out_dex.stat().st_size // 1024} KB)")
    return out_dex

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--dx-jar', type=Path, required=True)
    ap.add_argument('--jars-dir', type=Path, required=True)
    ap.add_argument('--out', type=Path, required=True)
    args = ap.parse_args()
    merge_jars_to_dex(args.dx_jar, args.jars_dir, args.out)
