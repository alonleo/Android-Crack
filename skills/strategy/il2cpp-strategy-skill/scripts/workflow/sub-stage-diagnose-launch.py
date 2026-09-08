#!/usr/bin/env python3
"""Diagnose an Android launch timeout/crash for the current project APK."""
from __future__ import annotations

import os
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def adb_cmd(*args: str) -> list[str]:
    adb = os.environ.get("ADB_BIN", str(ROOT / "tools/environments/android-sdk/platform-tools/adb"))
    serial = os.environ.get("ANDROID_SERIAL", "")
    return [adb] + (["-s", serial] if serial else []) + list(args)


def run_adb(args: tuple[str, ...], timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(adb_cmd(*args), capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(adb_cmd(*args), 124, "", f"timeout after {timeout}s: {exc}")


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--wait", type=int, default=15)
    args = parser.parse_args()
    apk = ROOT / "output-projects" / type_arg / name / "patched.apk"
    report = ROOT / "crackings" / type_arg / name / "stages" / "runtime-diagnose" / "launch-report.txt"
    screenshot = report.parent / "launch-screenshot.png"
    report.parent.mkdir(parents=True, exist_ok=True)
    if not apk.is_file():
        report.write_text(f"APK missing: {apk}\n", encoding="utf-8")
        return 1
    lines = []
    install = run_adb(("install", "-r", str(apk)), 120)
    if install.returncode != 0:
        report.write_text(f"ADB install failed rc={install.returncode}\n{install.stderr}\n", encoding="utf-8")
        print(f"[ERROR] ADB 安装/设备不可用: {install.stderr.strip()}")
        return 1
    clear = run_adb(("logcat", "-c"), 15)
    if clear.returncode != 0:
        report.write_text(f"ADB logcat unavailable rc={clear.returncode}\n{clear.stderr}\n", encoding="utf-8")
        print(f"[ERROR] ADB logcat 不可用: {clear.stderr.strip()}")
        return 1
    try:
        start = run_adb(("shell", "am", "start", "-W", "-n", "com.pokokostudio.dinobash/com.android.boot.MainActivity"), 45)
        lines.append(f"am_start_rc={start.returncode}\nstdout:\n{start.stdout}\nstderr:\n{start.stderr}")
    except subprocess.TimeoutExpired as exc:
        lines.append(f"am_start_timeout={exc}\nstdout={exc.stdout}\nstderr={exc.stderr}")
    time.sleep(args.wait)
    log = run_adb(("logcat", "-d", "-v", "threadtime"), 30)
    lines.append("\n=== LOGCAT ===\n" + log.stdout)
    activity = run_adb(("shell", "dumpsys", "activity", "activities"), 30)
    lines.append("\n=== ACTIVITY ===\n" + activity.stdout)
    run_adb(("shell", "screencap", "-p", "/sdcard/dino-launch.png"), 20)
    run_adb(("pull", "/sdcard/dino-launch.png", str(screenshot)), 30)
    report.write_text("\n".join(lines), encoding="utf-8")
    fatal = [line for line in log.stdout.splitlines() if re.search(r"FATAL EXCEPTION|AndroidRuntime|UnsatisfiedLinkError|ClassNotFoundException|NoClassDefFoundError|SIGSEGV|signal 11", line)]
    print(f"[OK] 诊断报告: {report}")
    print(f"[OK] adb 截图: {screenshot}")
    print(f"[INFO] fatal_or_class_errors={len(fatal)}")
    for line in fatal[-30:]:
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
