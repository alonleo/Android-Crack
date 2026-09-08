#!/usr/bin/env python3
"""
阶段 15 - SDKUtils 真机验收（il2cpp 专用）
=================================================================
验证 SDKUtils 三阶段模拟（500ms 加载 / 1500ms 播放 / 300ms 关闭）能正常回调 native。

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
        stage_id="15",
        label="SDKUtils 真机验收",
        focus="com.android.common.SDKUtils 三阶段模拟 + JNI 回调链路 → 补全 sdk-utils 经验",
    )


if __name__ == "__main__":
    sys.exit(main())