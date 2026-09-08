#!/usr/bin/env python3
"""inject-defold-hook.py — 注入 Defold SDK hook（native-lib.so + smali 加载）到 apktool 目录。

策略: skills/strategy/defold-strategy-skill/strategy.md §7
注入点: com/dynamo/android/DefoldActivity.onCreate 开头（它是 NativeActivity，
onCreate 里才 System.loadLibrary(引擎 .so)）。在其前插入 System.loadLibrary("native-lib")
→ JNI_OnLoad 起线程等引擎 .so 加载后 dlsym hook。

用法:
  python3 inject-defold-hook.py <apktool_root> [--so <libnative-lib.so>] [--abi arm64-v8a]

说明:
  - 把 libnative-lib.so 复制到 <apktool_root>/lib/<abi>/
  - 在 DefoldActivity.smali 的 onCreate 注入 loadLibrary("native-lib")
  - 幂等：已注入过则跳过
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

LOADER_SMALI = """
    # === injected by inject-defold-hook.py: Defold SDK native hook (And64InlineHook) ===
    const-string v1, "native-lib"

    invoke-static {v1}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
"""


def find_defold_activity(apktool_root: Path) -> Path | None:
    p = apktool_root / "smali" / "com" / "dynamo" / "android" / "DefoldActivity.smali"
    return p if p.is_file() else None


def inject(apktool_root: Path, so_path: Path | None, abi: str) -> int:
    # 1. 复制 native-lib.so
    if so_path is not None and so_path.is_file():
        dst_dir = apktool_root / "lib" / abi
        dst_dir.mkdir(parents=True, exist_ok=True)
        dst = dst_dir / "libnative-lib.so"
        shutil.copy2(str(so_path), str(dst))
        print(f"[OK] libnative-lib.so → {dst}")

    # 2. 注入 smali
    act = find_defold_activity(apktool_root)
    if not act:
        print("[ERROR] DefoldActivity.smali 未找到（非 Defold 引擎？）", file=sys.stderr)
        return 1
    text = act.read_text(encoding="utf-8")
    if "injected by inject-defold-hook.py" in text:
        print("[INFO] 已注入过，跳过")
        return 0
    m = re.search(r"\.method public onCreate\(Landroid/os/Bundle;\)V.*?\n(    \.locals \d+)", text)
    if not m:
        print("[ERROR] 未找到 onCreate 方法头", file=sys.stderr)
        return 1
    # 在 .locals 之后插入 loadLibrary
    inject_at = m.end()
    text = text[:inject_at] + "\n" + LOADER_SMALI + text[inject_at:]
    act.write_text(text, encoding="utf-8")
    print(f"[OK] DefoldActivity.smali 注入 loadLibrary(\"native-lib\")")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="注入 Defold SDK hook 到 apktool 目录")
    ap.add_argument("apktool_root", help="apktool 解包目录")
    ap.add_argument("--so", default=None, help="libnative-lib.so 路径（可选，仅拷贝）")
    ap.add_argument("--abi", default="arm64-v8a", help="ABI 目录")
    args = ap.parse_args()

    root = Path(args.apktool_root)
    if not (root / "AndroidManifest.xml").is_file():
        print("[ERROR] 非 apktool 目录", file=sys.stderr)
        return 1
    so = Path(args.so) if args.so else None
    return inject(root, so, args.abi)


if __name__ == "__main__":
    sys.exit(main())
