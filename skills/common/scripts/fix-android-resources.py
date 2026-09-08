#!/usr/bin/env python3
"""fix-android-resources.py — 修复 FakerAndroid 生成的损坏资源文件。

处理问题：
  1. 资源文件名含 '$'（非法字符）→ 替换为 '_'
  2. XML 中对这些文件的引用 → 同步更新
  3. 删除 values-v31/color-v31（Android 12 动态主题，compileSdk 33 不兼容）
  4. 删除引用不存在文件的 animated-vector XML
  5. 删除空 <intent></intent>
+  6. 删除 res/values/public.xml（apktool 解包产物；SDK 资源删除后其声明引用缺失资源，
+     AGP/AAPT2 构建报 "no definition for declared symbol"；AGP 构建不需要 public.xml）

用法：
  python3 fix-android-resources.py --name <Name>
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def _name():
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def fix_dollar_filenames(res_dir: Path) -> int:
    """重命名含 $ 的文件 + 更新 XML 引用。"""
    renamed = 0
    for f in res_dir.rglob("*"):
        if f.is_file() and "$" in f.name:
            new_name = f.name.replace("$", "_")
            f.rename(f.parent / new_name)
            renamed += 1
    # 更新 XML 引用
    for xml in res_dir.rglob("*.xml"):
        try:
            text = xml.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        new_text = re.sub(r'\$mtrl_', 'mtrl_', text)
        new_text = re.sub(r'\$applovin_', 'applovin_', new_text)
        new_text = re.sub(r'\$m3_', 'm3_', new_text)
        new_text = re.sub(r'\$avd_', 'avd_', new_text)
        if new_text != text:
            xml.write_text(new_text, encoding="utf-8")
    return renamed


def remove_v31(res_dir: Path) -> int:
    """删除 values-v31/color-v31（动态主题）。"""
    removed = 0
    for d in (res_dir / "values-v31", res_dir / "color-v31"):
        if d.is_dir():
            import shutil
            shutil.rmtree(d)
            removed += 1
    return removed


def remove_broken_vector_xml(res_dir: Path) -> int:
    """删除引用不存在文件的 animated-vector/vector XML。"""
    removed = 0
    drawable_dirs = [d for d in res_dir.glob("drawable*") if d.is_dir()]
    for dd in drawable_dirs:
        for f in list(dd.glob("*.xml")):
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if "animated-vector" in text or "<vector" in text:
                refs = re.findall(r'@drawable/([^\s"]+)', text)
                broken = False
                for ref in refs:
                    ref = ref.split("/")[0]
                    if not (dd / f"{ref}.xml").exists() and not (dd / f"{ref}.png").exists():
                        broken = True
                        break
                if broken:
                    f.unlink()
                    removed += 1
    return removed


def remove_broken_selector_xml(res_dir: Path) -> int:
    """删除引用不存在 drawable 的 selector XML（多层清理）。"""
    removed = 0
    drawable_dirs = [d for d in res_dir.glob("drawable*") if d.is_dir()]
    changed = True
    while changed:
        changed = False
        for dd in drawable_dirs:
            for f in list(dd.glob("*.xml")):
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                except Exception:
                    continue
                refs = re.findall(r'@drawable/([^\s"]+)', text)
                for ref in refs:
                    ref = ref.split("/")[0]
                    if not (dd / f"{ref}.xml").exists() and not (dd / f"{ref}.png").exists():
                        f.unlink()
                        removed += 1
                        changed = True
                        break
    return removed


def remove_empty_intent(res_dir: Path) -> int:
    """删除空 <intent></intent> 和 <intent-filter></intent-filter>。"""
    removed = 0
    for xml in res_dir.rglob("*.xml"):
        try:
            text = xml.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        new_text = re.sub(r'<intent>\s*</intent>', '', text)
        new_text = re.sub(r'<intent-filter>\s*</intent-filter>', '', new_text)
        if new_text != text:
            xml.write_text(new_text, encoding="utf-8")
            removed += 1
    return removed


def remove_public_xml(res_dir: Path) -> int:
    """删除 res/values/public.xml。

    [FLOWFIX] public.xml 是 apktool 解包产物（资源 ID 固定表），SDK 资源删除后其
    声明仍引用已删资源 → AGP/AAPT2 构建报 "no definition for declared symbol"。
    AGP 构建不需要 public.xml（除非配置 --stable-ids），直接删除。
    """
    p = res_dir / "values" / "public.xml"
    if p.is_file():
        p.unlink()
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    args = parser.parse_args()
    name = args.name

    res_dir = ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "app" / "src" / "main" / "res"
    if not res_dir.is_dir():
        print(f"[ERROR] res 目录缺失: {res_dir}")
        return 1

    n1 = fix_dollar_filenames(res_dir)
    n2 = remove_v31(res_dir)
    n3 = remove_broken_vector_xml(res_dir)
    n4 = remove_broken_selector_xml(res_dir)
    n5 = remove_empty_intent(res_dir)
    n6 = remove_public_xml(res_dir)

    print(f"[OK] 资源修复: $重命名={n1}, v31删除={n2}, 损坏vector={n3}, 损坏selector={n4}, 空intent={n5}, public.xml删除={n6}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
