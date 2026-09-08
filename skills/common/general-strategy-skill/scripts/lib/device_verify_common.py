#!/usr/bin/env python3
"""device_verify_common.py — 通用真机验收库（04/06/08/10/12/14）。

[FLOWFIX 2026-08-30] 原 lib 缺失重建。

核心 API：
    verify_app_alive(device_serial, pkg, apk_path, screen_label) -> dict
        - 安装 + 启动 + 等待 + 截图 + 检查进程 + 无 FATAL 校验

简化实现（满足 OBJECTIVES.md §1.1 验证手段）：
    1) 可编译：略（pre-build 已验证）
    2) 可安装：adb install -r apk_path → 退出码 0
    3) 可启动：adb shell am start → 启动 ActivityManager
    4) 可加载：adb logcat *:E 5 秒内无 FATAL
    5) 可进入游戏：抓屏 + 进程存活 5 秒

返回 dict:
    {
        "passed": bool,
        "install_rc": int,
        "start_rc": int,
        "alive_after_5s": bool,
        "fatal_count": int,
        "screenshot": str (path),
    }
"""
from __future__ import annotations

import os
import re
import subprocess
import sys
import time
from pathlib import Path

# 仓库根：skills/common/general-strategy-skill/scripts/lib/ → parents[5] = android-crack 根
REPO = Path(__file__).resolve().parents[5]


def _adb() -> str:
    return os.environ.get("ADB_BIN") or os.environ.get("ADB") or "adb"


def _pkg_main_activity(pkg: str) -> str:
    """从环境变量 PKG_MAIN_ACTIVITY 拿完整启动 Activity（格式 'pkg/.MainActivity' 或 'pkg/ActName'）。"""
    return os.environ.get("PKG_MAIN_ACTIVITY", f"{pkg}/.MainActivity")


def adb_run(adb: str, *args: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run([adb, *args], capture_output=True, text=True, timeout=timeout)


def verify_app_alive(
    apk_path: Path,
    pkg: str,
    main_activity: str = "",
    device_serial: str = "",
    wait_seconds: int = 8,
    screenshot_name: str = "verify-screenshot.png",
    out_dir: Path | None = None,
    extra_args: tuple = (),
) -> dict:
    """安装 + 启动 + 验证 + 截图。

    :param apk_path: 待装 APK 路径
    :param pkg: 应用 package name
    :param main_activity: 启动 Activity 完整名（如 com.unity3d.player.UnityPlayerActivity）；
                         空时尝试常见 Android 默认（UnityPlayerActivity）
    :param device_serial: adb -s 设备 serial；空时用默认设备
    :param wait_seconds: 启动后等待秒数（5~10）
    :param screenshot_name: 截图文件名
    :param out_dir: 截图输出目录（None = 当前目录）
    :param extra_args: 额外的 install/start 参数
    :return: dict 含 passed/install_rc/start_rc/alive/fatal_count/screenshot
    """
    adb = _adb()
    serial_args = ["-s", device_serial] if device_serial else []
    result = {
        "passed": False,
        "install_rc": -1,
        "start_rc": -1,
        "alive_after_5s": False,
        "fatal_count": 0,
        "screenshot": "",
    }

    if not apk_path.exists():
        print(f"[verify_app_alive] APK 不存在: {apk_path}")
        return result

    # 1. 卸载旧版本（避免 INSTALL_FAILED_UPDATE_INCOMPATIBLE）
    try:
        adb_run(adb, *serial_args, "uninstall", pkg, timeout=30)
    except subprocess.TimeoutExpired:
        pass

    # 2. 安装（用 -r -d 兼容低 sdk）
    print(f"[verify_app_alive] install {apk_path.name} → {pkg}")
    try:
        r = adb_run(adb, *serial_args, "install", "-r", "-d", str(apk_path), *extra_args, timeout=300)
        result["install_rc"] = r.returncode
        if r.returncode != 0:
            print(f"[verify_app_alive] install 失败: {r.stderr or r.stdout}")
            return result
    except subprocess.TimeoutExpired:
        print(f"[verify_app_alive] install 超时")
        return result

    # 3. 清 logcat
    try:
        adb_run(adb, *serial_args, "logcat", "-c", timeout=10)
    except subprocess.TimeoutExpired:
        pass

    # 4. 启动
    if not main_activity:
        # 默认尝试 UnityPlayerActivity
        main_activity = "com.unity3d.player.UnityPlayerActivity"
    print(f"[verify_app_alive] start {pkg}/{main_activity}")
    try:
        r = adb_run(
            adb, *serial_args, "shell", "am", "start", "-n", f"{pkg}/{main_activity}",
            timeout=30,
        )
        result["start_rc"] = r.returncode
    except subprocess.TimeoutExpired:
        print(f"[verify_app_alive] start 超时")
        return result

    # 5. 等待 + 查进程
    time.sleep(wait_seconds)
    try:
        r = adb_run(adb, *serial_args, "shell", "pidof", pkg, timeout=10)
        result["alive_after_5s"] = bool(r.stdout.strip())
    except subprocess.TimeoutExpired:
        pass

    # 6. 抓 E/F 日志（只统计本应用进程的 FATAL，避免其它 app 历史崩溃误报）
    try:
        r = adb_run(adb, *serial_args, "logcat", "-d", "-v", "time", "*:E", "*:F", timeout=30)
        log_text = r.stdout or ""
        fatal_patterns = ["FATAL EXCEPTION", "AndroidRuntime.*FATAL", "SIGSEGV", "SIGABRT", "tombstone"]
        # 仅统计与当前 pkg 相关联的 FATAL 行（日志在 install/am start 之后，含 pkg 的才算本应用）
        app_fatals = [
            line for line in log_text.splitlines()
            if any(p in line for p in fatal_patterns) and pkg in line
        ]
        result["fatal_count"] = len(app_fatals)
        if result["fatal_count"] > 0:
            print(f"[verify_app_alive] 发现 {result['fatal_count']} 个本应用 FATAL")
            for line in app_fatals[:50]:
                print(f"  {line.strip()}")
    except subprocess.TimeoutExpired:
        pass

    # 7. 截图
    if out_dir is None:
        out_dir = Path(".")
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        r = adb_run(adb, *serial_args, "shell", "screencap", "-p", "/sdcard/v.png", timeout=30)
        if r.returncode == 0:
            pull_r = adb_run(adb, *serial_args, "pull", "/sdcard/v.png",
                             str(out_dir / screenshot_name), timeout=30)
            if pull_r.returncode == 0:
                result["screenshot"] = str(out_dir / screenshot_name)
    except subprocess.TimeoutExpired:
        pass

    # 8. 判定
    result["passed"] = (
        result["install_rc"] == 0
        and result["start_rc"] == 0
        and result["alive_after_5s"]
        and result["fatal_count"] == 0
    )
    print(f"[verify_app_alive] passed={result['passed']} install={result['install_rc']} "
          f"start={result['start_rc']} alive={result['alive_after_5s']} "
          f"fatal={result['fatal_count']} screenshot={result['screenshot']}")
    return result


def _load_pkg_activity() -> tuple[str, str]:
    """从 env/产物解析 (pkg, main_activity)。

    优先顺序：
      PKG / MAIN_ACTIVITY 环境变量
      → apk 的 -s 信息（跳过，需 aapt）
      → crackings/<type>/<name>/stages/*-apk-info/apk-info.yaml 的 package/launchable_activity
      → 默认 UnityPlayerActivity
    """
    name = os.environ.get("NAME", "")
    type_ = os.environ.get("TYPE", "il2cpp")
    pkg = os.environ.get("PKG", "").strip()
    activity = os.environ.get("MAIN_ACTIVITY", "").strip()

    if (not pkg or not activity) and name and type_:
        # 从 apk-info.yaml 解析（03 阶段产物）；glob 任意层 apk-info.yaml
        info_files = sorted(REPO.glob(f"crackings/{type_}/{name}/**/apk-info.yaml"))
        import yaml as _yaml
        for f in info_files[:1]:
            try:
                data = _yaml.safe_load(f.read_text(encoding="utf-8"))
                pkg = pkg or data.get("package", "")
                activity = activity or data.get("launchable_activity", "")
            except Exception:
                pass
    if not pkg:
        pkg = os.environ.get("PKG_DEFAULT", "")
    if not activity:
        activity = "com.unity3d.player.UnityPlayerActivity"  # il2cpp 默认
    return pkg, activity


def device_verify_run(stage_id: str = "05", label: str = "", focus: str = "",
                      screenshot_name: str = "") -> int:
    """兼容包装：供 04/06/08/10/12/14 的 verify step 调用。

    从 env NAME/TYPE/PATCHED/ANDROID_SERIAL/CRACK_DIR 解析输入，
    调 verify_app_alive 做「安装+启动+存活+无FATAL+截图」，返回 rc(0=通过)。

    输出截图写到 <crack_dir>/stages/<stage_id>-<name>/ ，并写 verify-report.md。
    """
    import json

    name = os.environ.get("NAME", "")
    type_ = os.environ.get("TYPE", "il2cpp")
    patched = os.environ.get("PATCHED", "")
    serial = os.environ.get("ANDROID_SERIAL", "")
    crack_dir = os.environ.get("CRACK_DIR", "")

    if not patched or not Path(patched).is_file():
        print(f"[device_verify_run] 缺 PATCHED APK: {patched}")
        return 1
    pkg, activity = _load_pkg_activity()
    if not pkg:
        print("[device_verify_run] 无法解析 PKG（无 PKG 环境变量/apk-info）")
        return 1

    # 输出目录
    if not crack_dir:
        crack_dir = str(REPO / "crackings" / type_ / name)
    sd = Path(crack_dir) / "stages"
    sd.mkdir(parents=True, exist_ok=True)
    shot = screenshot_name or "verify-screenshot.png"
    out_dir = sd

    r = verify_app_alive(
        Path(patched), pkg, main_activity=activity,
        device_serial=serial, wait_seconds=10, screenshot_name=shot, out_dir=out_dir,
    )

    # 写 verify-report.md（append 到 <stage>-verify/ 目录,若存在）
    report = sd / f"{stage_id}-sdk-network-device-verify" / "verify-report.md"
    report.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# verify-report — {label or stage_id}",
        "",
        f"- **package**: {pkg}",
        f"- **main_activity**: {activity}",
        f"- **serial**: {serial}",
        f"- **passed**: {r['passed']}",
        f"- **install_rc**: {r['install_rc']}",
        f"- **start_rc**: {r['start_rc']}",
        f"- **alive_after_5s**: {r['alive_after_5s']}",
        f"- **fatal_count**: {r['fatal_count']}",
        f"- **screenshot**: {r['screenshot']}",
        f"- **focus**: {focus}",
        "",
    ]
    report.write_text("\n".join(lines), encoding="utf-8")
    print(f"[device_verify_run] 报告 → {report}")
    return 0 if r["passed"] else 1
