#!/usr/bin/env python3
"""step-01-collect-strings.py — analyze action step1: 收集待汉化字符串。

11-text-hanization/analyze action。
从 strings.xml + dump.cs 收集英文字符串候选。
绕过 common handler(依赖有 bug)。
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
# 兼容读取旧项目分析产物；fn-analyze 已不再参与路由。
from step_base import stage_path, REPO, Step

import yaml


class CollectStringsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        out_proj = REPO / "output-projects" / type_ / name
        strings_main = out_proj / "app/src/main/res/values/strings.xml"

        strings_count = 0
        sample_strings = []
        if strings_main.exists():
            text = strings_main.read_text(encoding="utf-8", errors="ignore")
            strings_count = text.count("<string")
            # 取前 10 个英文 string
            sample_strings = re.findall(r"<string name=\"([^\"]+)\">([^<]*)</string>", text)[:10]

        # 检查 dump.cs 里可汉化字符串(literal)
        dump_cs = self._find_dump_cs(type_, name)
        literal_count = 0
        if dump_cs and dump_cs.exists():
            text = dump_cs.read_text(encoding="utf-8", errors="ignore")
            # 粗略:英文字符串字面量 { "xxx" }
            literal_count = len(re.findall(r'"[A-Za-z][A-Za-z ]{2,}"', text))

        detection = {
            "stage": "11", "name": "strings-collected",
            "strings_xml_count": strings_count,
            "sample_strings": [{"name": n, "text": t} for n, t in sample_strings],
            "dump_literal_estimate": literal_count,
        }
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)
        (stage_dir / "strings-collected.yaml").write_text(
            yaml.safe_dump(detection, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0,
            "skipped": False,
            "strings_xml_count": strings_count,
            "dump_literal_estimate": literal_count,
            "detection_yaml": str((stage_dir / "strings-collected.yaml").relative_to(REPO)),
        }

    @staticmethod
    def _find_dump_cs(type_, name):
        sig_dir = REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures"
        for cand in (sig_dir / "dump" / "dump.cs", sig_dir / "dump.cs",
                     REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "dump" / "dump.cs",
                     REPO / "crackings" / type_ / name / "raw" / "03b-il2cpp-output" / "dump.cs"):
            if cand.exists():
                return cand
        return None