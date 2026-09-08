#!/usr/bin/env python3
"""
device-swipe.py — 真机模拟滑动/点击手势（通用）
=================================================
用途：真机验收时需要模拟用户手势（滑动开始游戏 / 点击按钮）时使用。

用法：
  python3 device-swipe.py <x1> <y1> <x2> <y2> [duration_ms]
  python3 device-swipe.py tap <x> <y>          # 点击

环境变量：
  ANDROID_SERIAL — 目标设备（默认 adb 第一台）

示例：
  python3 device-swipe.py 720 2000 720 800 300   # 上滑（开始游戏常见）
  python3 device-swipe.py tap 720 1400           # 点击
"""
from __future__ import annotations

import os
import subprocess
import sys
import time

ADB = os.environ.get("ADB_BIN", "adb")


def adb(*args: str, timeout: int = 30) -> subprocess.CompletedProcess:
    serial = os.environ.get("ANDROID_SERIAL", "")
    cmd = [ADB]
    if serial:
        cmd += ["-s", serial]
    cmd += list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def main() -> int:
    if len(sys.argv) < 3:
        print(__doc__)
        return 1

    if sys.argv[1] == "tap":
        x, y = sys.argv[2], sys.argv[3]
        print(f"[swipe] tap ({x},{y})")
        r = adb("shell", "input", "tap", x, y)
    else:
        x1, y1, x2, y2 = sys.argv[1:5]
        dur = sys.argv[5] if len(sys.argv) > 5 else "300"
        print(f"[swipe] ({x1},{y1}) → ({x2},{y2}) {dur}ms")
        r = adb("shell", "input", "swipe", x1, y1, x2, y2, dur)

    if r.returncode != 0:
        print(f"[swipe] FAIL: {r.stderr}", file=sys.stderr)
        return 1
    print("[swipe] OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
