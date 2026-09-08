#!/usr/bin/env python3
"""
阶段 17 - 激励视频真机验收（il2cpp 专用）
=================================================================
验证激励视频 hook 链路：native callJava("showVideo") → Java SDKUtils 三阶段模拟 → 回调 native 触发原始函数。

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
        stage_id="17",
        label="激励视频真机验收",
        focus="激励视频 hook 链路（ShowRewardAd / OnRewardComplete）→ 补全 reward-forwarding 经验",
    )


if __name__ == "__main__":
    sys.exit(main())