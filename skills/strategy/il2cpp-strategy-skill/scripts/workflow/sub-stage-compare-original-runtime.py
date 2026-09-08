#!/usr/bin/env python3
"""Compare original and patched launch behavior on the connected device."""
from __future__ import annotations

import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
PKG = "com.pokokostudio.dinobash"
ACTIVITY = f"{PKG}/com.android.boot.MainActivity"


def adb(*args: str, timeout: int = 90) -> subprocess.CompletedProcess[str]:
    binary = os.environ.get("ADB_BIN", str(ROOT / "tools/environments/android-sdk/platform-tools/adb"))
    serial = os.environ.get("ANDROID_SERIAL", "")
    cmd = [binary] + (["-s", serial] if serial else []) + list(args)
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def run_case(label: str, apk: Path, out: Path) -> None:
    adb("install", "-r", str(apk), timeout=120)
    adb("shell", "am", "force-stop", PKG, timeout=20)
    adb("logcat", "-c", timeout=20)
    start = adb("shell", "am", "start", "-W", "-n", ACTIVITY, timeout=60)
    time.sleep(20)
    log = adb("logcat", "-d", "-v", "threadtime", timeout=40)
    adb("shell", "screencap", "-p", f"/sdcard/{label}.png", timeout=20)
    adb("pull", f"/sdcard/{label}.png", str(out / f"{label}.png"), timeout=40)
    (out / f"{label}.log").write_text(
        f"=== START ===\n{start.stdout}\n{start.stderr}\n=== LOGCAT ===\n{log.stdout}",
        encoding="utf-8",
    )
    print(f"[OK] {label}: screenshot={out / f'{label}.png'} log={out / f'{label}.log'}")


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    root = ROOT / "output-projects" / type_arg / name
    raw = Path(os.environ.get("ORIGINAL_APK", "").strip()) if os.environ.get("ORIGINAL_APK", "").strip() else ROOT / "crackings" / type_arg / name / "raw" / "DinoBashDinosaurBattle.apk"
    out = ROOT / "crackings" / type_arg / name / "stages" / "runtime-diagnose"
    out.mkdir(parents=True, exist_ok=True)
    if not raw.is_file() or not (root / "patched.apk").is_file():
        print("[ERROR] original or patched APK missing")
        return 1
    run_case("original", raw, out)
    run_case("patched-final", root / "patched.apk", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
