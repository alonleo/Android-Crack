#!/usr/bin/env python3
"""step-02-verify-normal-mode.py — 普通模式真机验收。

05 verify step 2/6。
委托给 common device_verify_run(安装 → 启动 → 多窗口存活 → 截图)。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path



sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

# device_verify_common 在 general-strategy-skill(共享);直接用 REPO 绝对路径避免路径算错
sys.path.insert(0, str(REPO / "skills/common/general-strategy-skill/scripts/lib"))


class VerifyNormalModeStep(Step):
    def execute(self, steps_results: dict) -> dict:
        # 读 step-01 环境检查结果(命名空间前缀:record-project-files.verify)
        env = steps_results.get("sdk-network-device-verify.default-action.check-environment", {})
        if env.get("skip"):
            return {"rc": 0, "skipped": True, "reason": "env incomplete"}

        # 委托 device_verify_run
        from device_verify_common import device_verify_run
        rc = device_verify_run(
            stage_id="04",
            label="04-sdk-network-device-verify 普通模式",
            focus="sdk+network 真机验收经验固化(普通模式段)",
        )

        # 把截图改名为 screenshot-normal(原 device_verify_run 写 verify-screenshot.png)
        stage_dir = Path(os.environ.get("CRACK_DIR", ".")) / "stages" / stage_path("sdk-network-device-verify")
        src = stage_dir / "verify-screenshot.png"
        dst = stage_dir / "screenshot-normal.png"
        if src.exists() and not dst.exists():
            try:
                src.rename(dst)
            except Exception:
                pass

        return {
            "rc": rc,
            "skipped": False,
            "mode": "normal",
            "screenshot": str(dst.relative_to(REPO)) if dst.exists() else None,
        }