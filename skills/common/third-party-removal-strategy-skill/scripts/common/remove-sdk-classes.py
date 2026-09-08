#!/usr/bin/env python3
"""remove-sdk-classes.py — 物理删除第三方 SDK 类并排查残留引用。

背景: FlyingGorillaEndlessRunner (2026-08-02) 物理删除 InMobi（1938 文件 + 适配器 + OM SDK）。
关键: C# (libil2cpp) 不引用的 SDK 才能物理删除；删除前必须排查引用，直接类引用需先桩化，
字符串引用（反射/映射）安全。

用法:
  python3 remove-sdk-classes.py <apktool_root> <sdk_package...> [--also-delete "com/iab/omid/library/inmobi" "com/applovin/mediation/adapters/InMobiMediationAdapter*"]
  # 例:
  python3 remove-sdk-classes.py crackings/FlyingGorillaEndlessRunner/raw/01-apktool \
      "com/inmobi" "com/iab/omid/library/inmobi" \
      --also-delete "com/applovin/mediation/adapters/InMobiMediationAdapter*"

输出:
  - 删除的 smali 文件数
  - 残留直接类引用（需人工桩化，用 stub-sdk-methods.py / 改签名）
  - 残留字符串引用（安全，反射/映射）
  - 幂等（重复运行无副作用）

注意:
  - 删除后需重跑 inject-smali-dex.py --force 生效
  - 直接类引用如果不处理就重打包，运行期可能 ClassNotFound/VerifyError
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def collect_files(root: Path, packages: list[str], also_delete: list[str]) -> list[Path]:
    """收集要删除的 smali 文件。packages 为 'com/inmobi' 风格路径；also_delete 支持通配。"""
    targets = []
    for d in sorted(root.glob("smali*")):
        if not d.is_dir():
            continue
        for pkg in packages:
            p = d / pkg
            if p.is_dir():
                targets.extend(p.rglob("*.smali"))
        for pat in also_delete:
            for f in d.glob(pat):
                if f.is_file() and f.suffix == ".smali":
                    targets.append(f)
    return list(set(targets))


def scan_references(root: Path, removed_files: list[Path]) -> tuple[list[str], list[str]]:
    """扫描剩余 smali 中对被删 SDK 的直接类引用 vs 字符串引用。
    removed_files 提供被删类名集合（用于排除自引用）。"""
    # 被删类全名集合（如 Lcom/inmobi/ads/InMobiInterstitial;）
    removed_classes = set()
    for f in removed_files:
        rel = f.as_posix()
        m = re.search(r'/smali[^/]*/com/(.+)\.smali$', rel)
        if m:
            removed_classes.add("Lcom/" + m.group(1) + ";")

    direct = []  # 直接类引用（Lcom/x/y;）
    strings = []  # 字符串引用（"com.x.y"）
    # removed_classes 仅用于判断"被删类自身内部"，本函数扫描的是剩余文件，
    # 剩余文件引用被删类 = 外部悬空引用，全部要报告。
    for d in sorted(root.glob("smali*")):
        if not d.is_dir():
            continue
        for f in d.rglob("*.smali"):
            if f in removed_files:
                continue  # 跳过被删文件自身
            text = f.read_text(encoding="utf-8", errors="ignore")
            for m in re.finditer(r'(Lcom/[A-Za-z0-9_/$]+;)', text):
                cls = m.group(1)
                # 是否命中被删 SDK 前缀（com/inmobi → Lcom/inmobi/）
                if any(cls.startswith(f"L{p.replace('/', '/')}/") for p in removed_prefixes):
                    direct.append(f"{f.relative_to(root)}: {cls}")
            for m in re.finditer(r'"(com\.[A-Za-z0-9_.]+)"', text):
                # p 是 'com/inmobi' → 点分前缀 'com.inmobi'
                if any(m.group(1).startswith(p.replace('/', '.')) for p in removed_prefixes):
                    strings.append(f"{f.relative_to(root)}: {m.group(1)}")
    return list(set(direct)), list(set(strings))


removed_prefixes: list[str] = []


def main() -> int:
    global removed_prefixes
    parser = argparse.ArgumentParser(description="物理删除第三方 SDK 类并排查残留引用")
    parser.add_argument("apktool_root", help="apktool 解包根目录")
    parser.add_argument("packages", nargs="+", help="SDK 包路径（如 com/inmobi）")
    parser.add_argument("--also-delete", action="append", default=[],
                        help="额外删除路径/通配（如 com/iab/omid/library/inmobi 或 *InMobiMediationAdapter*）")
    args = parser.parse_args()

    root = Path(args.apktool_root)
    if not root.is_dir():
        print(f"[ERROR] 目录不存在: {root}")
        return 1
    removed_prefixes = [p for p in args.packages] + [p for p in args.also_delete if "/" in p]

    files = collect_files(root, args.packages, args.also_delete)
    if not files:
        print("[WARN] 未找到要删除的 smali 文件")
        return 0
    print(f"[INFO] 待删除 {len(files)} 个 smali 文件")

    # 先扫描引用（删除前）
    direct, strings = scan_references(root, files)
    print(f"[INFO] 扫描到直接类引用 {len(direct)} 处 / 字符串引用 {len(strings)} 处")

    # 删除
    for f in files:
        f.unlink(missing_ok=True)
    # 清理空目录
    for d in sorted(root.glob("smali*/**"), reverse=True):
        if d.is_dir() and not any(d.iterdir()):
            try:
                d.rmdir()
            except OSError:
                pass

    print(f"[OK] 已删除 {len(files)} 个文件")
    if direct:
        print("\n=== ⚠️ 残留直接类引用（必须处理，否则运行期崩溃）===")
        for x in sorted(direct)[:20]:
            print(f"  {x}")
        print("[建议] 用 stub-sdk-methods.py 桩化引用方法，或改方法签名去掉引用")
    else:
        print("\n[OK] 无残留直接类引用")
    if strings:
        print("\n=== 字符串引用（安全，反射/映射，可忽略）===")
        for x in sorted(strings)[:10]:
            print(f"  {x}")
    print("[INFO] 删除后需重跑 inject-smali-dex.py --force 生效")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
