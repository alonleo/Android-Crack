#!/usr/bin/env python3
"""sub-stage-cleanup.py — 主阶段 M4：清理临时空间。

按 OBJECTIVES.md §1：保留最终产物（project/app/ + patched.apk + keystore + gradle 配置），
删除构建中间产物（build/、.gradle/、raw/ 解包中间文件等）。

[FLOWFIX 2026-09-05] 本脚本由 §1.11.1 修复补建（sub-stages.yaml 引用但脚本长期缺失）。

用法:
  NAME=<Name> TYPE=<type> python3 sub-stage-cleanup.py [--keep-raw]
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "skills" / "common" / "scripts" / "lib"))
from common import ensure_env, log_info, log_success, log_warn, log_step


REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    ensure_env()
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "il2cpp").strip()
    keep_raw = "--keep-raw" in sys.argv
    if not name:
        print("[ERROR] 缺 NAME", file=sys.stderr)
        return 2

    crack_dir = REPO / "crackings" / type_ / name
    project = crack_dir / "project"

    log_step(f"清理 {name} 临时空间（保留 final 产物）")

    # 1. project/app/build（构建中间产物）
    build_dir = project / "app" / "build"
    if build_dir.exists():
        shutil.rmtree(build_dir)
        log_info(f"删除 {build_dir.relative_to(REPO)}")
    # 2. project/.gradle
    gradle_dir = project / ".gradle"
    if gradle_dir.exists():
        shutil.rmtree(gradle_dir)
        log_info(f"删除 {gradle_dir.relative_to(REPO)}")
    # 3. project/app/build/intermediates（部分 gradle 子产物）
    intermediates = project / "app" / "intermediates"
    if intermediates.exists():
        shutil.rmtree(intermediates)
        log_info(f"删除 {intermediates.relative_to(REPO)}")
    # 4. crackings/<type>/<name>/raw（解包中间产物；可 --keep-raw 保留）
    raw_dir = crack_dir / "raw"
    if raw_dir.exists() and not keep_raw:
        shutil.rmtree(raw_dir)
        log_info(f"删除 {raw_dir.relative_to(REPO)}")
    elif raw_dir.exists() and keep_raw:
        log_warn(f"保留 raw（--keep-raw）: {raw_dir.relative_to(REPO)}")

    # 5. temp/ 临时目录（best-effort，runtime 调试产物）
    temp = REPO / "temp"
    if temp.exists():
        try:
            shutil.rmtree(temp)
            log_info("删除 temp/")
        except Exception as e:
            log_warn(f"temp/ 部分清理失败: {e}")

    log_success(f"M4 清理完成：保留 crackings/{type_}/{name}/project/ + patched.apk")
    return 0


if __name__ == "__main__":
    sys.exit(main())