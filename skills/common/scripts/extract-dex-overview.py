#!/usr/bin/env python3
"""extract-dex-overview.py — 抽取 APK 内所有 dex 的概要信息。

common sub-stage-static-analyze.py 只对 Android/AIR 跑 jadx 反编译，
对 il2cpp/unity-mono 等只抽 libil2cpp.so / global-metadata.dat。本脚本补全
Java/Kotlin 入口概要扫描（无需 jadx 全量反编译，仅 dexdump 抽类名 + 主入口），
适用于所有 type 项目的 03 静态分析补充。

输出：
  - crackings/<type>/<Name>/stages/03-static-analyze/top-dirs.txt
  - crackings/<type>/<Name>/stages/03-static-analyze/poko-classes.txt（如有指定搜索关键词）
  - crackings/<type>/<Name>/stages/03-static-analyze/mainactivity-candidates.txt
  - crackings/<type>/<Name>/stages/03-static-analyze/findings.md

用法（env 准备）：
  source tools/environments/env.sh
  ./skills/common/scripts/extract-dex-overview.py <path/to/apk> --type il2cpp --name DinoBashDinosaurBattle
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

THIS = Path(__file__).resolve()

REPO_ROOT = THIS.parents[2]


def apk_apktool_unzip(apk_path: Path) -> str:
    r = subprocess.run(["unzip", "-l", str(apk_path)], capture_output=True, text=True, timeout=60)
    return r.stdout


def list_dex(apk_path: Path) -> list[str]:
    txt = apk_apktool_unzip(apk_path)
    return re.findall(r"^\s+\d+\s+[\d-]+\s+[\d:]+\s+(.+?\.dex)\s*$", txt, re.M)


def find_dexdump() -> str:
    aapt2 = os.environ.get("ANDROID_HOME") or os.environ.get("AAPT2") or ""
    base = "/home/leo/文档/android-crack/tools/environments/android-sdk/build-tools"
    p = Path(base)
    if p.is_dir():
        candidates = sorted(p.glob("*/dexdump"))
        if candidates:
            return str(candidates[-1])
    which = subprocess.run(["which", "dexdump"], capture_output=True, text=True)
    p = which.stdout.strip()
    if p:
        return p
    sys.exit("[ERROR] dexdump 不在 build-tools 下，也不在 PATH 中")


def scan_apk(apk_path: Path, out_dir: Path, keywords: list[str] | None = None) -> dict:
    dexdump = find_dexdump()
    all_dex = list_dex(apk_path)
    top_dirs: set = set()
    poko_hits: list[tuple[str, str]] = []
    main_candidates_list: list[tuple[str, str]] = []
    sdks: dict[str, int] = {}
    keyword_set = {k.lower() for k in (keywords or [])}

    # 已知 SDK 前缀列表（与 sub-stage-assess.py 一致）
    SDK_PREFIXES = [
        "com/facebook", "com/google/android/gms", "com/google/firebase",
        "com/applovin", "com/ironsource", "com/unity3d/ads",
        "com/amazon/device/ads", "com/mopub", "com/tapjoy",
        "com/vungle", "com/adcolony", "com/inmobi",
        "com/appsflyer", "com/adjust", "com/kochava",
        "com/bytedance", "com/pangle",
        "com/huawei/hms", "com/tencent",
    ]

    tmp = out_dir / "_tmp_dex"
    tmp.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    for dp in all_dex:
        r = subprocess.run(["unzip", "-p", str(apk_path), dp], capture_output=True)
        if not r.stdout:
            continue
        tmpf = tmp / Path(dp).name
        tmpf.write_bytes(r.stdout)
        dump = subprocess.run([dexdump, "-f", str(tmpf)], capture_output=True, timeout=120)
        try:
            txt = dump.stdout.decode("utf-8", errors="replace")
        except Exception:
            txt = dump.stdout.decode("latin-1", errors="replace")
        classes = re.findall(r"Class descriptor\s*:\s*'([^']+)'", txt)
        for c in classes:
            s = c.strip("L")
            parts = s.split("/")
            if len(parts) >= 3:
                top_dirs.add(f"{parts[0]}/{parts[1]}")
            cls_lower = c.lower()
            for kw in keyword_set:
                if kw and kw in cls_lower:
                    poko_hits.append((dp, c))
                    break
            for prefix in SDK_PREFIXES:
                if prefix.replace(".", "/") in s.lower():
                    sdks[prefix] = sdks.get(prefix, 0) + 1
            if any(k in c for k in [
                "/MainActivity;", "/MainActivity$", "UnityPlayerActivity",
                "UnityPlayer$", "Application", "/App;", "/App$",
                "FirebaseInitProvider", "MultiDex", "MainApplication",
            ]):
                main_candidates_list.append((dp, c))
        tmpf.unlink()
    shutil.rmtree(tmp, ignore_errors=True)
    return {
        "dex_files": all_dex,
        "top_dirs": sorted(top_dirs),
        "poko_hits": poko_hits,
        "main_candidates": main_candidates_list,
        "sdks": sdks,
        "elapsed": round(time.time() - t0, 1),
    }


def write_outputs(out_dir: Path, apk_path: Path, summary: dict, type_: str, name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "top-dirs.txt").write_text("\n".join(summary["top_dirs"]), encoding="utf-8")
    (out_dir / "all-dex-files.txt").write_text("\n".join(summary["dex_files"]), encoding="utf-8")
    if summary["poko_hits"]:
        with open(out_dir / "keyword-classes.txt", "w") as f:
            for dp, c in summary["poko_hits"]:
                f.write(f"{dp}\t{c}\n")
    if summary["main_candidates"]:
        with open(out_dir / "mainactivity-candidates.txt", "w") as f:
            for dp, c in summary["main_candidates"]:
                f.write(f"{dp}\t{c}\n")
    with open(out_dir / "sdks.txt", "w") as f:
        for sdk, cnt in sorted(summary["sdks"].items(), key=lambda x: -x[1]):
            f.write(f"{sdk}\t{cnt}\n")
    md = f"""# 03-static-analyze · dex 概要

## 元信息
- **type**: `{type_}`
- **name**: `{name}`
- **apk**: `{apk_path.relative_to(REPO_ROOT) if str(apk_path).startswith(str(REPO_ROOT)) else apk_path}`
- **dex 文件数**: {len(summary['dex_files'])}
- **扫描耗时**: {summary['elapsed']}s

## 顶层 package 目录（com/*）
{chr(10).join(['- `' + d + '`' for d in summary['top_dirs']])}

## 第三方 SDK（来自 dex 类路径前缀）
{chr(10).join([f'- `{sdk}`: {cnt} 个类' for sdk, cnt in sorted(summary['sdks'].items(), key=lambda x: -x[1])])}

## MainActivity / Unity 入口候选（{len(summary['main_candidates'])} 个）
{chr(10).join(['- `' + dp + '`: `' + c + '`' for dp, c in summary['main_candidates'][:30]])}

{'## 关键词命中的类（' + str(len(summary['poko_hits'])) + '）' + chr(10) + chr(10).join(['- `' + dp + '`: `' + c + '`' for dp, c in summary['poko_hits'][:30]]) if summary['poko_hits'] else '## 关键词命中的类：无'}

## dex 文件清单
{chr(10).join(['- `' + d + '`' for d in summary['dex_files']])}
"""
    (out_dir / "findings.md").write_text(md, encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("apk", help="APK 路径")
    p.add_argument("--name", required=True)
    p.add_argument("--type", default="il2cpp")
    p.add_argument("--keywords", nargs="*", default=[], help="额外关键词（如游戏包名前缀）")
    args = p.parse_args()

    apk = Path(args.apk).resolve()
    if not apk.is_file():
        sys.exit(f"[ERROR] {apk} 不存在")

    crack = REPO_ROOT / "crackings" / args.type / args.name
    out = crack / "stages" / "03-static-analyze"
    out.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] 扫描 {apk} → {out}")
    summary = scan_apk(apk, out, keywords=args.keywords)
    write_outputs(out, apk, summary, args.type, args.name)
    print(f"[OK] {len(summary['top_dirs'])} 顶层目录 / "
          f"{len(summary['sdks'])} SDK / {len(summary['main_candidates'])} MainActivity 候选")
    print(f"[OK] {out / 'findings.md'}")


if __name__ == "__main__":
    import shutil  # 收尾放在末尾保证可用
    main()
