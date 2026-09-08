#!/usr/bin/env python3
"""
阶段 19 - IAP 真机验收（il2cpp 专用）
=================================================================
验证 IAP（Premium）转发链路：native callJava("processPurchase") + callJava("premiumUnlock") → Java 模拟 → 回调 native。

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
        stage_id="19",
        label="IAP 真机验收",
        focus="IAP（PurchaseSuccessful / ProcessPurchase / UnlockPremium）→ 补全 iap-forwarding 经验",
    )


if __name__ == "__main__":
    sys.exit(main())