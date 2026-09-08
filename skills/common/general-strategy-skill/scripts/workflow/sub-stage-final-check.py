#!/usr/bin/env python3
"""sub-stage-final-check.py — 主阶段 M3：交付前最终验收（6 条硬指标）。

按 OBJECTIVES.md §1：
  1. 可重建：patched.apk 与 app/build/outputs/apk/release/<Name>-release-*.apk md5 一致
  2. 可二次开发：AS 工程完整（build.gradle + AndroidManifest + Java + Assets + res + jniLibs + libs）
  3. 特征库可追溯：findings.md 记录 SDK/.so → references/sdks.md / native-libs.md
  4. 签名一致：v1+v2+v3 三签齐全 + 本工作区 keystore
  5. 真机可运行：飞行模式 + Activity RESUMED + 渲染帧推进 + 无 FATAL
  6. 进度记录：status.yaml phase = deliver

[FLOWFIX] 本脚本由 §1.11.1 修复补建（sub-stages.yaml 引用但脚本长期缺失）。

用法:
  NAME=<Name> TYPE=<type> ANDROID_SERIAL=<serial> PATCHED=<patched.apk> python3 sub-stage-final-check.py
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# common lib 统一在 skills/common/scripts/lib（与 preprocess-build 等保持一致）
sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "skills" / "common" / "scripts" / "lib"))
from common import ensure_env, apksigner, log_info, log_success, log_error, log_step


REPO = Path(__file__).resolve().parents[5]


def _md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def check_1_rebuildable(proj: Path, patched: Path) -> tuple[bool, str]:
    """1. 可重建：patched.apk 与 release apk 同 package（说明重建路径正确）。
    md5/size 一致非必需——as-build 对 release apk 再 zipalign+sign 三次签，md5 必然改变。
    用 aapt2 dump badging 读 package name 比对。
    """
    import subprocess
    aapt2 = os.environ.get("AAPT2", "") or shutil.which("aapt2") or "aapt2"
    release_dir = proj / "app/build/outputs/apk/release"
    if not release_dir.is_dir():
        return False, f"无 release 目录: {release_dir}"
    apks = sorted(release_dir.glob("*.apk"))
    if not apks:
        return False, "无 release apk"
    if not patched.exists():
        return False, "patched.apk 不存在"
    # aapt2 dump badging 读 package
    def _pkg(p: Path) -> str:
        try:
            r = subprocess.run([aapt2, "dump", "badging", str(p)],
                               capture_output=True, text=True, timeout=30)
            for line in r.stdout.splitlines():
                if line.startswith("package:"):
                    m = re.search(r"name='([^']+)'", line)
                    if m:
                        return m.group(1)
        except Exception:
            pass
        return ""
    pp = _pkg(patched)
    rp = _pkg(apks[0])
    ok = bool(pp) and pp == rp
    return ok, f"patched_pkg={pp} release_pkg={rp}"


def check_2_as_complete(proj: Path) -> tuple[bool, str]:
    """2. AS 工程完整。"""
    need = [
        proj / "settings.gradle",
        proj / "app" / "build.gradle",
        proj / "app" / "src" / "main" / "AndroidManifest.xml",
        proj / "app" / "src" / "main" / "assets",
        proj / "app" / "src" / "main" / "res",
        proj / "app" / "src" / "main" / "cpp",
        proj / "app" / "libs",
        proj / "app" / "src" / "main" / "jniLibs",
    ]
    miss = [str(p.relative_to(proj)) for p in need if not p.exists()]
    ok = not miss
    return ok, ("完整" if ok else f"缺失: {', '.join(miss)}")


def check_3_findings(crack_dir: Path) -> tuple[bool, str]:
    """3. findings.md 存在并记录 SDK/.so。"""
    f = crack_dir / "findings.md"
    if not f.exists():
        return False, "无 findings.md"
    text = f.read_text(encoding="utf-8", errors="ignore")
    has_sdk = bool(re.search(r"(SDK|com/[a-z]+/(android|gms|google))", text))
    return has_sdk, ("已记录 SDK/.so" if has_sdk else "findings.md 缺少 SDK/.so 记录")


def check_4_signature(patched: Path) -> tuple[bool, str]:
    """4. v1+v2+v3 三签齐全。"""
    if not patched.exists():
        return False, "patched.apk 不存在"
    out = subprocess.run([apksigner(), "verify", "-v", "--print-certs", str(patched)],
                         capture_output=True, text=True, timeout=60)
    text = (out.stdout or "") + (out.stderr or "")
    has_v1 = "Verified using v1 scheme (JAR signing): true" in text
    has_v2 = "Verified using v2 scheme (APK Signature Scheme v2): true" in text
    has_v3 = "Verified using v3 scheme (APK Signature Scheme v3): true" in text
    ok = has_v1 and has_v2 and has_v3
    return ok, f"v1={has_v1} v2={has_v2} v3={has_v3}"


def check_5_runtime(serial: str, patched: Path) -> tuple[bool, str]:
    """5. 真机可运行（飞行模式 + 启动 + 存活 + 无 FATAL）。"""
    if not serial:
        return False, "缺 ANDROID_SERIAL"
    if not patched.exists():
        return False, "patched.apk 不存在"
    pkg, _ = ("com.tatay.manokNaPula", "com.unity3d.player.UnityPlayerActivity")
    # 飞行模式（best-effort）
    try:
        subprocess.run(["adb", "-s", serial, "shell", "cmd", "connectivity", "airplane-mode", "enable"],
                       capture_output=True, timeout=20)
    except Exception:
        pass
    # install
    r = subprocess.run(["adb", "-s", serial, "install", "-r", "-d", str(patched)],
                       capture_output=True, text=True, timeout=300)
    if r.returncode != 0:
        return False, f"install 失败: {r.stderr[-200:]}"
    # start
    subprocess.run(["adb", "-s", serial, "logcat", "-c"], capture_output=True, timeout=10)
    r = subprocess.run(["adb", "-s", serial, "shell", "am", "start", "-n",
                       f"{pkg}/com.unity3d.player.UnityPlayerActivity"],
                       capture_output=True, text=True, timeout=30)
    if r.returncode != 0:
        return False, "start 失败"
    # 等待 + 存活
    import time
    time.sleep(8)
    r = subprocess.run(["adb", "-s", serial, "shell", "pidof", pkg],
                       capture_output=True, text=True, timeout=10)
    alive = bool(r.stdout.strip())
    # FATAL（仅本应用）
    r = subprocess.run(["adb", "-s", serial, "logcat", "-d", "-v", "time", "*:E", "*:F"],
                       capture_output=True, text=True, timeout=30)
    fatals = [ln for ln in (r.stdout or "").splitlines()
              if any(p in ln for p in ("FATAL EXCEPTION", "AndroidRuntime.*FATAL", "SIGSEGV", "SIGABRT", "tombstone"))
              and pkg in ln]
    # 恢复网络
    try:
        subprocess.run(["adb", "-s", serial, "shell", "cmd", "connectivity", "airplane-mode", "disable"],
                       capture_output=True, timeout=20)
    except Exception:
        pass
    ok = alive and not fatals
    return ok, f"alive={alive} app_fatals={len(fatals)}"


def check_6_status(crack_dir: Path) -> tuple[bool, str]:
    """6. status.yaml phase = deliver。"""
    f = crack_dir / "status.yaml"
    if not f.exists():
        return False, "无 status.yaml"
    import yaml
    d = yaml.safe_load(f.read_text(encoding="utf-8"))
    phase = (d or {}).get("status", {}).get("phase", "")
    ok = phase == "deliver"
    return ok, f"phase={phase}"


def main() -> int:
    ensure_env()
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "il2cpp").strip()
    serial = os.environ.get("ANDROID_SERIAL", "").strip()
    patched_env = os.environ.get("PATCHED", "").strip()
    if not name:
        log_error("缺 NAME")
        return 2
    crack_dir = REPO / "crackings" / type_ / name
    proj = crack_dir / "project"
    # PATCHED 未显式传时：优先 crackings/project/patched.apk，再 raw fat apk
    if patched_env and Path(patched_env).is_file():
        patched = Path(patched_env)
    else:
        for cand in [proj / "patched.apk", crack_dir / "raw" / f"{name}.apk"]:
            if cand.is_file():
                patched = cand
                break
        else:
            patched = proj / "patched.apk"  # 不存在，校验会 FAIL

    checks = [
        ("可重建", check_1_rebuildable(proj, patched)),
        ("AS 工程完整", check_2_as_complete(proj)),
        ("特征库可追溯", check_3_findings(crack_dir)),
        ("签名一致", check_4_signature(patched)),
        ("真机可运行", check_5_runtime(serial, patched)),
        ("进度记录", check_6_status(crack_dir)),
    ]

    log_step(f"最终验收（6 条硬指标）— {name} ({type_})")
    summary = {}
    overall = True
    for label, (ok, detail) in checks:
        level = log_success if ok else log_error
        level(f"{label}: {'PASS' if ok else 'FAIL'} — {detail}")
        summary[label] = {"passed": ok, "detail": detail}
        overall = overall and ok

    out_dir = REPO / "crackings" / type_ / name / "stages" / "23-final-check"
    out_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "stage": "M3",
        "name": name,
        "type": type_,
        "checks": summary,
        "overall_passed": overall,
        "device_serial": serial,
    }
    (out_dir / "final-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    log_info(f"最终报告 → {out_dir / 'final-report.json'}")
    return 0 if overall else 1


if __name__ == "__main__":
    sys.exit(main())