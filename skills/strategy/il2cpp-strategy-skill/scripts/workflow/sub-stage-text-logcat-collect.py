#!/usr/bin/env python3
"""Collect xTextCapture log lines produced by the A64Hook text collector."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("out", help="JSON output path")
    ap.add_argument("--device", default=os.environ.get("ANDROID_SERIAL", ""))
    ap.add_argument("--wait", type=int, default=0, help="等待游戏刷新文本的秒数")
    args = ap.parse_args()
    if args.wait:
        time.sleep(args.wait)
    adb = os.environ.get("ADB_BIN", str(ROOT / "tools/environments/android-sdk/platform-tools/adb"))
    cmd = [adb]
    if args.device:
        cmd += ["-s", args.device]
    cmd += ["logcat", "-d"]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(result.stderr, flush=True)
        return result.returncode
    values = {}
    diagnostics = []
    for line in result.stdout.splitlines():
        match = re.search(r"xTextCapture:\s*TEXT\\t(.*)$", line)
        if match:
            value = match.group(1).strip()
            if value:
                values.setdefault(value, "")
        if any(token in line for token in ("AndroidRuntime", "FATAL", "xNative", "xTextCapture", "dinobash")):
            diagnostics.append(line)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    existing = {}
    if out.exists():
        try:
            existing = json.loads(out.read_text(encoding="utf-8"))
        except Exception:
            pass
    existing.update(values)
    out.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[OK] 收集文本 {len(values)} 条 → {out}")
    hook_lines = [line for line in result.stdout.splitlines() if "xTextCapture" in line]
    if hook_lines:
        print(f"[OK] 检测到 A64Hook 日志 ({len(hook_lines)} 条)")
        for line in hook_lines[-20:]:
            print(line)
    else:
        print("[WARN] 未检测到 xTextCapture 日志")
        for line in diagnostics[-30:]:
            print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
