#!/usr/bin/env python3
"""
阶段 11 - 去功能点真机验收（il2cpp 专用）
=================================================================
原 stage-12-ui-device-verify.py 改名。

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
        stage_id="08",
        label="去功能点真机验收",
        focus="UI 隐藏 / 区域裁剪（HookedBehaviour_set_isActiveAndEnabled）→ 补全 ui-hide 经验",
    )


if __name__ == "__main__":
    sys.exit(main())