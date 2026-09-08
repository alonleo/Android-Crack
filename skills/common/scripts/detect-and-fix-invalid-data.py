#!/usr/bin/env python3
"""
detect-and-fix-invalid-data.py — 检测 FakerAndroid "Invalid data detected" 问题并自动修复。

触发条件（满足任一即执行修复）：
1. FakerAndroid 日志含 "Invalid data detected" ≥ 10 次
2. AndroidManifest.xml 含空属性（<uses-permission android:name=""/>）
3. AndroidManifest.xml 含 requiredSplitTypes/splitTypes

修复策略：
  调用 fix-faker-android-invalid-data.py 执行 apktool 2.11.1 兜底合并。

用法：
  python3 detect-and-fix-invalid-data.py --name <Name> [--apk <merged.apk>]

返回码：
  0 = 无需修复 或 修复成功
  1 = 检测到问题但修复失败
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PKG = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts"
sys.path.insert(0, str(SCRIPT_PKG))
import importlib.util as _ilu

_spc = _ilu.spec_from_file_location(
    "stage_common_runtime", str(SCRIPT_PKG / "lib" / "stage_common.py")
)
_sc = _ilu.module_from_spec(_spc)
assert _spc.loader is not None
_spc.loader.exec_module(_sc)

log_info = _sc.log_info
log_warn = _sc.log_warn
log_step = _sc.log_step
log_success = _sc.log_success
log_error = _sc.log_error
append_status = _sc.append_status


def detect_from_log(log_path: Path) -> tuple[int, bool]:
    """扫描 FakerAndroid 日志，返回 (Invalid data 次数, 是否含 manifest 异常)。"""
    if not log_path.is_file():
        return 0, False
    text = log_path.read_text(encoding="utf-8", errors="replace")
    invalid_count = text.count("Invalid data detected")
    has_manifest_issue = (
        "NullPointerException" in text
        and "ManifestEditor" in text
    ) or "没有那个文件或目录" in text
    return invalid_count, has_manifest_issue


def detect_from_manifest(manifest: Path) -> tuple[bool, list[str]]:
    """检查 manifest 是否含空属性或 splitTypes。返回 (有问题, 问题列表)。"""
    if not manifest.is_file():
        return False, []
    text = manifest.read_text(encoding="utf-8", errors="replace")
    issues = []
    if re.search(r'<uses-permission android:name=""\s*/?>', text):
        issues.append("空 uses-permission")
    if re.search(r'<uses-feature android:name=""\s*/?>', text):
        issues.append("空 uses-feature")
    if re.search(r'android:requiredSplitTypes="', text):
        issues.append("含 requiredSplitTypes")
    if re.search(r'android:splitTypes="', text):
        issues.append("含 splitTypes")
    # 检查属性值为空字符串的通用模式
    empty_attrs = re.findall(r'(android:\w+)=""', text)
    if empty_attrs:
        issues.append(f"空属性: {', '.join(set(empty_attrs))}")
    return bool(issues), issues


def detect_invalid_data_ratio(log_path: Path) -> float:
    """计算日志中 "Invalid data detected" 行占比。"""
    if not log_path.is_file():
        return 0.0
    text = log_path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    if not lines:
        return 0.0
    invalid_lines = sum(1 for l in lines if "Invalid data detected" in l)
    return invalid_lines / len(lines)


def run_fix(name: str, apk: Path | None = None) -> bool:
    """调用 fix-faker-android-invalid-data.py 执行修复。"""
    fix_script = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts" / "common" / "fix-faker-android-invalid-data.py"
    if not fix_script.is_file():
        log_error(f"修复脚本缺失: {fix_script}")
        return False

    cmd = [sys.executable, str(fix_script), "--name", name]
    if apk:
        cmd.extend(["--apk", str(apk)])

    log_step(f"调用修复脚本: {fix_script.name}")
    result = subprocess.run(cmd, cwd=str(ROOT))
    return result.returncode == 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="检测 FakerAndroid Invalid Data 问题并自动修复"
    )
    parser.add_argument("--name", required=True, help="项目名")
    parser.add_argument("--apk", help="merged APK 路径（默认自动查找）")
    parser.add_argument("--threshold", type=int, default=10,
                        help="Invalid data 次数阈值（默认 10）")
    parser.add_argument("--force", action="store_true",
                        help="强制执行修复（跳过检测）")
    args = parser.parse_args()

    name = args.name
    apk = Path(args.apk) if args.apk else None
    threshold = args.threshold

    # 定位日志和 manifest
    stage_dir = ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "stages" / "01-fake-android"
    log_path = stage_dir / "fake-android.log"
    manifest = ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "app" / "src" / "main" / "AndroidManifest.xml"

    if args.force:
        log_info("强制模式：跳过检测，直接执行修复")
        return 0 if run_fix(name, apk) else 1

    # 检测阶段
    needs_fix = False
    reasons = []

    # 检测 1: 日志中 Invalid data 次数
    invalid_count, has_manifest_issue = detect_from_log(log_path)
    ratio = detect_invalid_data_ratio(log_path)
    if invalid_count >= threshold:
        needs_fix = True
        reasons.append(f"Invalid data detected × {invalid_count}（占比 {ratio:.1%}）")
    elif invalid_count > 0:
        log_info(f"Invalid data detected × {invalid_count}（低于阈值 {threshold}，跳过修复）")

    if has_manifest_issue:
        needs_fix = True
        reasons.append("FakerAndroid 日志含 ManifestEditor NullPointerException")

    # 检测 2: manifest 空属性
    manifest_bad, manifest_issues = detect_from_manifest(manifest)
    if manifest_bad:
        needs_fix = True
        reasons.append(f"AndroidManifest.xml 异常: {'; '.join(manifest_issues)}")

    if not needs_fix:
        log_success("未检测到 Invalid Data 问题，无需修复")
        return 0

    # 修复阶段
    log_warn(f"检测到问题（{'; '.join(reasons)}），开始自动修复...")

    if run_fix(name, apk):
        log_success("Invalid Data 自动修复完成")
        return 0
    else:
        log_error("Invalid Data 自动修复失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())
