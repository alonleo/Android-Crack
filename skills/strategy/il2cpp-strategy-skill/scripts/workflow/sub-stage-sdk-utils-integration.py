#!/usr/bin/env python3
"""
阶段 14 - 集成 SDKUtils（il2cpp 专用）
=================================================================
原 stage-04-wire-templates.py 拆分：
  - 12 (模板)：MainActivity + App + JniBridge + native-lib.cpp
  - 14 (SDKUtils)：com/android/common/SDKUtils.java

功能：注入 com.android.common.SDKUtils.java 到 AS 工程，提供激励视频三阶段模拟：
- 500ms 加载（loading）
- 1500ms 播放（showing）
- 300ms 关闭（closing）
最终回调 native 触发原始激励函数。

输入：crackings/<type>/<Name>/project/
  （预处理阶段已生成 settings.gradle/gradlew/app/）
输出：app/src/main/java/com/android/common/SDKUtils.java

[FLOWFIX]:
  原实现委托给已删除的旧编号脚本（stage-04-wire-templates.py），
  该脚本已被 REFACTOR 删除，导致 14 阶段实际什么都不做（return 0），
  AS 工程缺少 SDKUtils.java，激励视频/IAP 转发链路不通。

本修复直接拷贝 `skills/common/scripts/template-files/SDKUtils.java` 到 AS 工程。

真机验收：sub-stage-sdk-utils-device-verify.py（stage 15）
"""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
TEMPLATE_DIR = REPO / "tools" / "scripts" / "template-files"


def _resolve_name() -> str:
    name = os.environ.get('NAME', '').strip()
    if not name:
        print("[stage-14] NAME 环境变量未设置", file=sys.stderr)
        sys.exit(1)
    return name


def _app_main(name: str) -> Path:
    type_arg = os.environ.get("TYPE", "").strip()
    if type_arg:
        return REPO / "output-projects" / type_arg / name / "app" / "src" / "main"
    return REPO / "output-projects" / name / "app" / "src" / "main"


def main() -> int:
    name = _resolve_name()
    app_main = _app_main(name)
    app_main.mkdir(parents=True, exist_ok=True)

    src = TEMPLATE_DIR / "SDKUtils.java"
    if not src.exists():
        print(f"[ERROR] [stage-14] SDKUtils 模板缺失: {src}", file=sys.stderr)
        return 1

    dst_dir = app_main / "java" / "com" / "android" / "common"
    dst_dir.mkdir(parents=True, exist_ok=True)
    dst = dst_dir / "SDKUtils.java"
    if dst.exists():
        print(f"[stage-14] SDKUtils.java 已存在，跳过: {dst}")
        return 0
    shutil.copy2(src, dst)
    print(f"[stage-14] 生成 {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
