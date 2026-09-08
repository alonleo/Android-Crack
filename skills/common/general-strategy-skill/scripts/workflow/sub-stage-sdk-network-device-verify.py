#!/usr/bin/env python3
"""sub-stage-sdk-network-device-verify.py — 真机验收（SDK + 网络检测合并）。

[FLOWFIX 2026-08-30] 原脚本缺失重建。

按 OBJECTIVES.md §1.1 + §1.5：
    - 普通模式：安装 patched.apk + 启动 + 等待 + 截图 + 进程存活 + 无 FATAL
    - 飞行模式：airplane-mode enable → 启动游戏 → 截图 → 验证无网络检测拦截

环境变量：
    NAME / TYPE / ANDROID_SERIAL / APK (patched.apk 路径) / PKG / PKG_MAIN_ACTIVITY

输出：
    crackings/<type>/<Name>/stages/04-sdk-network-device-verify/
        - verify-report.md
        - screenshot-normal.png
        - screenshot-airplane.png
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "skills/common/general-strategy-skill/scripts/lib"))

from device_verify_common import verify_app_alive, adb_run, _adb


def airplane_mode_set(adb: str, serial_args: list, enable: bool) -> int:
    """设置飞行模式（Android 7+）。"""
    val = "enable" if enable else "disable"
    try:
        r = adb_run(adb, *serial_args, "shell", "cmd", "connectivity", "airplane-mode", val, timeout=15)
        return r.returncode
    except Exception as e:
        print(f"[airplane-mode] 失败: {e}")
        return -1


def write_report(out_dir: Path, normal: dict, airplane: dict, pkg: str, apk_name: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 真机验收报告（SDK + 网络检测合并）",
        "",
        f"- **APK**: {apk_name}",
        f"- **包名**: {pkg}",
        f"- **验收时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## 普通模式（normal）",
        "",
        f"- passed: **{normal.get('passed')}**",
        f"- install_rc: {normal.get('install_rc')}",
        f"- start_rc: {normal.get('start_rc')}",
        f"- 进程存活: {normal.get('alive_after_5s')}",
        f"- FATAL 数: {normal.get('fatal_count')}",
        f"- 截图: `{normal.get('screenshot')}`",
        "",
        "## 飞行模式（airplane）",
        "",
        f"- passed: **{airplane.get('passed')}**",
        f"- start_rc: {airplane.get('start_rc')}",
        f"- 进程存活: {airplane.get('alive_after_5s')}",
        f"- FATAL 数: {airplane.get('fatal_count')}",
        f"- 截图: `{airplane.get('screenshot')}`",
        "",
        "## 验收结论",
        "",
        "PASS" if (normal.get('passed') and airplane.get('passed')) else
        f"FAIL: normal={normal.get('passed')} airplane={airplane.get('passed')}",
        "",
    ]
    (out_dir / "verify-report.md").write_text("\n".join(lines))


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "il2cpp").strip()
    apk_env = os.environ.get("APK", "").strip()
    pkg = os.environ.get("PKG", "").strip()
    main_act = os.environ.get("PKG_MAIN_ACTIVITY", "").strip()
    serial = os.environ.get("ANDROID_SERIAL", "").strip()

    if not name or not apk_env or not pkg:
        print(f"[ERROR] 需要 NAME/TYPE/APK/PKG 环境变量", file=__import__('sys').stderr)
        print(f"  NAME={name} TYPE={type_} APK={apk_env} PKG={pkg}", file=__import__('sys').stderr)
        return 2

    apk_path = Path(apk_env)
    if not apk_path.is_absolute():
        apk_path = ROOT / apk_env
    if not apk_path.exists():
        print(f"[ERROR] APK 不存在: {apk_path}", file=__import__('sys').stderr)
        return 3

    out_dir = ROOT / "crackings" / type_ / name / "stages" / "04-sdk-network-device-verify"
    adb = _adb()
    serial_args = ["-s", serial] if serial else []

    # 1. 普通模式（先卸载确保干净）
    print(f"\n=== 普通模式 ===")
    normal = verify_app_alive(
        apk_path=apk_path,
        pkg=pkg,
        main_activity=main_act,
        device_serial=serial,
        wait_seconds=8,
        screenshot_name="screenshot-normal.png",
        out_dir=out_dir,
    )

    # 2. 飞行模式
    print(f"\n=== 飞行模式 ===")
    airplane_mode_set(adb, serial_args, True)
    time.sleep(3)  # 等飞行模式生效
    airplane = verify_app_alive(
        apk_path=apk_path,
        pkg=pkg,
        main_activity=main_act,
        device_serial=serial,
        wait_seconds=8,
        screenshot_name="screenshot-airplane.png",
        out_dir=out_dir,
    )
    airplane_mode_set(adb, serial_args, False)  # 恢复

    # 3. 写报告
    write_report(out_dir, normal, airplane, pkg, apk_path.name)

    return 0 if (normal.get("passed") and airplane.get("passed")) else 1


if __name__ == "__main__":
    sys.exit(main())
