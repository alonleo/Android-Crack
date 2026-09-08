#!/usr/bin/env python3
"""generate-stable-ids.py — 从 apktool 解码的 public.xml 生成 AGP stable-ids 表。

背景: il2cpp APK 的 dex 内引用原始资源 ID（如 Firebase 的 google_app_id=0x7f0d0042），
AGP 重建 resources.arsc 时会重排资源 ID → 运行期 `Resources$NotFoundException`
(如 FirebaseOptions.fromResource 找不到 0x7f0d0024)。用 apktool public.xml 派生
`pkg:type/name = 0xID` 表，写入 `app/stable_ids.txt`，并在 app/build.gradle:
  aaptOptions { additionalParameters '--stable-ids', file('stable_ids.txt').absolutePath }

用法:
  python3 generate-stable-ids.py <raw/01-apktool/res/values/public.xml> -o <app/stable_ids.txt> [--package jp.pinbit.flygorilla]

产物格式（AGP 7.4 aapt2 消费）:
  jp.pinbit.flygorilla:string/google_app_id = 0x7f0d0042
"""
from __future__ import annotations

import argparse
import xml.etree.ElementTree as ET
from pathlib import Path


def generate(public_xml: Path, package: str) -> list[str]:
    tree = ET.parse(str(public_xml))
    root = tree.getroot()
    lines = []
    for pub in root.findall("public"):
        typ = pub.attrib.get("type")
        name = pub.attrib.get("name")
        rid = pub.attrib.get("id")
        if not (typ and name and rid):
            continue
        lines.append(f"{package}:{typ}/{name} = {rid}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser(description="public.xml → stable_ids.txt")
    parser.add_argument("public_xml", help="apktool 解码的 res/values/public.xml")
    parser.add_argument("-o", "--out", default="stable_ids.txt", help="输出路径")
    parser.add_argument("--package", default="", help="包名（缺省从 public.xml 上级推断或提示）")
    args = parser.parse_args()

    xml = Path(args.public_xml)
    if not xml.is_file():
        print(f"[ERROR] public.xml 不存在: {xml}")
        return 1

    package = args.package
    if not package:
        # 尝试从 AndroidManifest.xml 同级推断
        manifest = xml.parents[2] / "AndroidManifest.xml"
        if manifest.is_file():
            import re
            m = re.search(r'package="([^"]+)"', manifest.read_text(encoding="utf-8"))
            if m:
                package = m.group(1)
    if not package:
        print("[WARN] 未指定 --package，stable_ids 将无包名前缀（aapt2 可能拒绝）")
        package = "UNKNOWN"

    lines = generate(xml, package)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"[OK]   生成 {len(lines)} 条 → {out}（package={package}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
