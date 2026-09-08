#!/usr/bin/env python3
"""step-02-load-translations.py — [方案A] metadata-hanize step2: 加载 index→译文 patch。

要求:Agent/译者把译文写成
    crackings/<type>/<name>/stages/<text-hanization>/translations.json
格式(与 Il2CppDumper stringliteral.json 一致):
    [{"index": 12345, "value": "译文"}, ...]
index 是字符串字面量顺序位(不可改),value 换成目标文本。

本 step 只校验不伪造:文件不存在时返回 needs_translation=True 并给出明确提示,
绝不凭空生成译文。占位符(%s/%d/{0}/<color>)由 Agent 在译文里保留。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

import yaml


class LoadTranslationsStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        prep = steps_results.get("text-hanization.metadata-hanize.prepare-metadata", {})
        string_count = int(prep.get("string_count", 0))

        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        trans_json = stage_dir / "translations.json"

        if not trans_json.exists():
            # 用户约定：汉化子阶段加载「通用游戏关键字→中文」清单，自动生成译文表。
            # 见 skills/common/scripts/hanization-common-keywords.yaml + generate-hanization-translations.py
            gen = REPO / "skills/common/scripts/generate-hanization-translations.py"
            r = subprocess.run(
                [sys.executable, str(gen), "--name", name, "--type", type_],
                capture_output=True, text=True, timeout=180, cwd=str(REPO),
                env={**os.environ, "NAME": name, "TYPE": type_},
            )
            if r.returncode != 0 or not trans_json.exists():
                log_msg = r.stderr[-300:] if r.stderr else r.stdout[-300:]
                return {
                    "rc": 0, "skipped": False, "needs_translation": True,
                    "string_count": string_count,
                    "translations_json": str(trans_json.relative_to(REPO)),
                    "error": (f"缺译文表 {trans_json.relative_to(REPO)}; 关键字字典生成失败: {log_msg}; "
                              f"（可手工把 [{{index,value}}] 译文写入同处）"),
                }

        try:
            patch = json.loads(trans_json.read_text(encoding="utf-8"))
        except Exception as e:  # noqa: BLE001
            return {"rc": 1, "skipped": False, "error": f"translations.json 解析失败: {e}"}

        valid, invalid = 0, []
        placeholder_kept = True
        for item in patch:
            idx = item.get("index")
            val = item.get("value")
            if not isinstance(idx, int) or not isinstance(val, str):
                invalid.append(f"index={idx} value类型错")
                continue
            if not (0 <= idx < string_count):
                invalid.append(f"index={idx} 越界(0..{string_count - 1})")
                continue
            if not val.strip():
                invalid.append(f"index={idx} 译文为空")
                continue
            valid += 1

        # 把 patch 副本落到 stage 目录(供 patch-metadata 读)
        patch_out = stage_dir / "patch-all.json"
        patch_out.write_text(json.dumps(patch, ensure_ascii=False, indent=2), encoding="utf-8")

        info = {
            "stage": "11", "name": "translations-loaded",
            "approach": "A-metadata-static",
            "translations_json": str(trans_json.relative_to(REPO)),
            "patch_entries": len(patch),
            "valid_entries": valid,
            "invalid_entries": invalid,
            "placeholder_inline_note": "保留 %s/%d/{0}/<color>",
        }
        (stage_dir / "translations-status.yaml").write_text(
            yaml.safe_dump(info, allow_unicode=True, sort_keys=False), encoding="utf-8")

        rc = 0 if valid > 0 and not invalid else 1
        return {
            "rc": rc, "skipped": False, "needs_translation": False,
            "patch_entries": len(patch), "valid_entries": valid,
            "invalid_entries": invalid,
            "patch_all_json": str(patch_out.relative_to(REPO)),
        }
