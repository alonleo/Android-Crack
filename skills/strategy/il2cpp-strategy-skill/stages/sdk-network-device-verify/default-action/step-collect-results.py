#!/usr/bin/env python3
"""step-06-collect-results.py — 汇总两段验证结果。

05 verify step 6/6。
读前 5 个 step 累积结果,产出最终判定 + verify-report.md。
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step


class CollectResultsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        env = steps_results.get("sdk-network-device-verify.default-action.check-environment", {})
        normal = steps_results.get("sdk-network-device-verify.default-action.verify-normal-mode", {})
        airplane = steps_results.get("sdk-network-device-verify.default-action.verify-airplane-mode", {})

        # 跳过场景(环境不全)
        if env.get("skip"):
            summary = {
                "skipped": True,
                "reason": "验收环境不全(无设备/无 patched.apk),已按约定跳过",
                "normal_mode": "skipped",
                "airplane_mode": "skipped",
            }
            overall_rc = 0  # 跳过 = 不算失败
        else:
            normal_ok = normal.get("rc") == 0 and not normal.get("skipped")
            airplane_ok = airplane.get("rc") == 0 and not airplane.get("skipped")
            both_ok = normal_ok and airplane_ok
            summary = {
                "skipped": False,
                "normal_mode": "PASS" if normal_ok else "FAIL",
                "airplane_mode": "PASS" if airplane_ok else "FAIL",
                "overall": "PASS" if both_ok else "FAIL",
            }
            overall_rc = 0 if both_ok else 1

        # 写 verify-report.md
        stage_dir = Path(os.environ.get("CRACK_DIR", ".")) / "stages" / stage_path("sdk-network-device-verify")
        report_path = stage_dir / "verify-report.md"
        report_path.parent.mkdir(parents=True, exist_ok=True)

        report_lines = [
            "# 04-sdk-network-device-verify 真机验收报告",
            "",
            f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            f"项目: {os.environ.get('NAME', '')}",
            f"类型: {os.environ.get('TYPE', '')}",
            "",
            "## 汇总",
            "",
            f"- 跳过: {summary['skipped']}",
            f"- 普通模式: {summary['normal_mode']}",
            f"- 飞行模式: {summary['airplane_mode']}",
            f"- 总体: {summary.get('overall', summary.get('reason', ''))}",
            "",
            "## step 执行明细",
            "",
        ]
        for step_key in ("check_environment", "verify_normal_mode",
                         "switch_to_airplane_mode", "verify_airplane_mode",
                         "restore_network"):
            data = steps_results.get(f"sdk-network-device-verify.default-action.{step_key}", {})
            report_lines.append(f"### {step_key}")
            report_lines.append("")
            report_lines.append("```yaml")
            report_lines.append(yaml.safe_dump(data, allow_unicode=True, sort_keys=False).rstrip())
            report_lines.append("```")
            report_lines.append("")

        report_path.write_text("\n".join(report_lines), encoding="utf-8")

        # 用 REPO/绝对路径避免相对路径 relative_to 报错
        try:
            report_rel = str(report_path.relative_to(REPO))
        except ValueError:
            report_rel = str(report_path)

        return {
            "rc": overall_rc,
            "summary": summary,
            "report_path": report_rel,
        }