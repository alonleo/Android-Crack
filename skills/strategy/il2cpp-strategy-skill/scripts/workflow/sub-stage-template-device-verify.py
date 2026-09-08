#!/usr/bin/env python3
"""
阶段 13 - 模板集成真机验收（il2cpp 专用）
=================================================================
验证模板文件（MainActivity + App + JniBridge + native-lib scaffolding）集成后 APK
可正常编译、启动。

调用 device_verify_common.device_verify_run()。
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/workflow/lib"))

from device_verify_common import device_verify_run  # noqa: E402


def main() -> int:
    return device_verify_run(
        stage_id="13",
        label="模板集成真机验收",
        focus="MainActivity/App/JniBridge 模板接入 fakeCpp + callJava 链路 → 补全 template 经验",
    )


if __name__ == "__main__":
    sys.exit(main())