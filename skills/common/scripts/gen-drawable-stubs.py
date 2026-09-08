#!/usr/bin/env python3
"""gen-drawable-stubs.py — 为 styles.xml/其他 XML 引用但缺失的 drawable 生成 stub。

用法：
  python3 gen-drawable-stubs.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

STUB = '<?xml version="1.0" encoding="utf-8"?>\n<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">\n    <solid android:color="#00000000" />\n</shape>\n'


def _name():
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    name = args.name

    main_dir = ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "app" / "src" / "main"
    res_dir = main_dir / "res"
    if not res_dir.is_dir():
        print(f"[ERROR] res 目录缺失: {res_dir}")
        return 1

    drawable_dirs = [d for d in res_dir.glob("drawable*") if d.is_dir()]
    base_drawable = res_dir / "drawable"
    if not base_drawable.is_dir():
        base_drawable.mkdir()

    # 收集所有 drawable 引用
    refs = set()
    for xml in res_dir.rglob("*.xml"):
        try:
            text = xml.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        # 只提取合法资源名 [a-z0-9_]
        for m in re.finditer(r'@drawable/([A-Za-z0-9_.]+)', text):
            refs.add(m.group(1))
        for m in re.finditer(r'@android:drawable/([A-Za-z0-9_.]+)', text):
            refs.add(m.group(1))

    # 已有的 drawable 资源名
    existing = set()
    for dd in drawable_dirs:
        for f in dd.iterdir():
            existing.add(f.stem)

    # values/drawables.xml 中已定义的资源（不能生成 stub 冲突）
    for val in res_dir.glob("values*/drawables.xml"):
        try:
            text = val.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'name="([^"]+)"', text):
                existing.add(m.group(1))
        except Exception:
            pass

    # 生成 stub
    created = 0
    for ref in sorted(refs):
        if not ref or ref in existing:
            continue
        stub_file = base_drawable / f"{ref}.xml"
        if not stub_file.exists():
            stub_file.write_text(STUB, encoding="utf-8")
            created += 1
            existing.add(ref)

    print(f"[OK] drawable stub 生成: {created} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
