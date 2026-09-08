#!/usr/bin/env python3
"""step-03-patch-metadata.py — [方案A] metadata-hanize step3: 基于原 metadata 重建。

经 metadata-patcher.patch_metadata(orig, patch, out) 把译文写回 global-metadata.dat:
  orig = 备份的原始 metadata(step1 prepare-metadata 已拷到 metadata.original.dat),
        若没有备份则用首个定位到的 metadata 路径。
  out  = 定位到的 metadata 路径(即 output-projects assets 树),供 gradle 重打包。
  约束: out != orig(禁止在原文件上反复改)。

产物: patched-metadata.yaml(统计: total/patched/out_bytes/out_path)。
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts/common"))
from step_base import stage_path, REPO, Step

import yaml


class PatchMetadataStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        prep = steps_results.get("text-hanization.metadata-hanize.prepare-metadata", {})
        trans = steps_results.get("text-hanization.metadata-hanize.load-translations", {})
        metadata_path = prep.get("metadata_path")
        backup = prep.get("backup_metadata")
        patch_all = trans.get("patch_all_json")

        if not metadata_path:
            return {"rc": 1, "skipped": False, "error": "缺 metadata_path(未跑 prepare-metadata 或未找到)"}
        if not patch_all:
            return {"rc": 1, "skipped": False, "error": "缺 patch_all_json(未跑 load-translations 或无译文)"}

        meta_path = REPO / metadata_path
        orig = REPO / backup if backup else meta_path
        if not orig.exists():
            return {"rc": 1, "skipped": False, "error": f"缺少可基于的 metadata: {orig}"}
        if not meta_path.exists():
            return {"rc": 1, "skipped": False, "error": f"写回目标 metadata 不存在: {meta_path}"}
        if orig == meta_path:
            return {"rc": 1, "skipped": False, "error": "orig==out(需先备份再基于备份重建)"}

        patch = json.loads((REPO / patch_all).read_text(encoding="utf-8"))

        # 调 metadata-patcher 重建(子进程,隔离核心工具)
        patcher = REPO / "skills/common/scripts/metadata-patcher.py"
        r = subprocess.run(
            [sys.executable, str(patcher), "patch", str(orig), str(REPO / patch_all), str(meta_path)],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )
        if r.returncode != 0:
            return {"rc": 1, "skipped": False, "error": f"patch 失败: {r.stderr[-400:]}",
                    "stdout_tail": r.stdout[-200:]}

        stats: dict = dict(
            json.loads(r.stdout) if r.stdout.strip() else {},
            orig=str(orig.relative_to(REPO)),
            out=str(meta_path.relative_to(REPO)),
        )
        report = {"stage": "11", "name": "patched-metadata", **stats}
        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        stage_dir.mkdir(parents=True, exist_ok=True)
        (stage_dir / "patched-metadata.yaml").write_text(
            yaml.safe_dump(report, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0, "skipped": False,
            "metadata_total": stats.get("total", 0),
            "patched": stats.get("patched", 0),
            "out_bytes": stats.get("out_bytes", 0),
            "out_path": stats.get("out"),
            "report": str((stage_dir / "patched-metadata.yaml").relative_to(REPO)),
        }
