#!/usr/bin/env python3
"""strip-apk-r-classes.py — 从 smali→jar 剥离 applicationId 的 R/R$/BuildConfig。

背景: 输出项目的 libs/smali*.jar 含原 APK 的 R.class/R$*.class/BuildConfig.class
（applicationId 包下）。AGP 会为 applicationId 自动生成 R，合并 dex 时
"Type X.R$mipmap is defined multiple times" → mergeDexRelease 失败。
修复: 剥离 applicationId 包下的 R.class / R$*/BuildConfig（来源 FormulaCarStuntCarGames 2026-08-06）。

用法:
  python3 strip-apk-r-classes.py <jar_or_dir> <applicationId>

依赖: Python 标准库（zipfile）
"""
from __future__ import annotations

import argparse
import os
import sys
import zipfile
from pathlib import Path


def strip_jar(jar_path: Path, pkg: str) -> int:
    pkg_path = pkg.replace(".", "/") + "/"
    tmp = jar_path.with_name("_strip_r_" + jar_path.name)
    zin = zipfile.ZipFile(jar_path)
    zout = zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED)
    removed = 0
    for item in zin.infolist():
        n = item.filename
        if n.startswith(pkg_path) and (
            n.endswith("/R.class") or "/R$" in n or n.endswith("/BuildConfig.class")
        ):
            removed += 1
            continue
        zout.writestr(item, zin.read(n))
    zin.close()
    zout.close()
    if removed:
        os.replace(tmp, jar_path)
    else:
        tmp.unlink()
    return removed


def main() -> int:
    parser = argparse.ArgumentParser(description="剥离 applicationId 的 R/BuildConfig 类")
    parser.add_argument("input", help="jar 文件或目录")
    parser.add_argument("application_id", help="applicationId（点分）")
    args = parser.parse_args()

    inp = Path(args.input)
    total = 0
    if inp.is_file() and inp.suffix == ".jar":
        total = strip_jar(inp, args.application_id)
    elif inp.is_dir():
        for jar in sorted(inp.glob("*.jar")):
            n = strip_jar(jar, args.application_id)
            if n:
                print(f"{jar.name}: 剥离 {n} 个 R/BuildConfig")
            total += n
    else:
        sys.exit(f"[ERROR] 输入必须是 jar 或目录: {inp}")
    print(f"[OK] 共剥离 {total} 个 R/BuildConfig 类")
    return 0 if total >= 0 else 1


if __name__ == "__main__":
    sys.exit(main())
