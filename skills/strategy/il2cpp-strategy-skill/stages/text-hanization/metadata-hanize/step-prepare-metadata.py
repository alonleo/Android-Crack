#!/usr/bin/env python3
"""step-01-prepare-metadata.py — [方案A] metadata-hanize step1: 定位 global-metadata.dat + 提取/复用 stringliteral.json。

[方案A] 字符串字面量静态替换的前置:找到原 global-metadata.dat,并准备一份
[{index,value}] 的 stringliteral.json(复用 fn-analyze 产物优先,否则用
metadata-patcher.extract 从 metadata 即时提取)。

数据流:
  1. 定位 global-metadata.dat(output-projects assets 树优先,回退 raw 解包树)
  2. 输出 stringliteral.json 到 stages/<text-hanization>/step1-stringliterals/
  3. 写 strings-collected.yaml(登记字符串数与路径)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
# 兼容读取旧项目分析产物；fn-analyze 已不再参与路由。
from step_base import stage_path, REPO, Step

import yaml

META_REL = "assets/bin/Data/Managed/Metadata/global-metadata.dat"
PATCHER = "skills/strategy/il2cpp-strategy-skill/scripts/common/metadata-patcher.py"


class PrepareMetadataStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "").strip()
        type_ = os.environ.get("TYPE", "il2cpp").strip()
        if not name:
            return {"rc": 1, "skipped": False, "error": "缺 NAME"}

        meta_path, meta_src = self._find_metadata(type_, name)
        if meta_path is None:
            return {"rc": 1, "skipped": False,
                    "error": f"未找到 global-metadata.dat（{META_REL}）",
                    "hint": "先跑 preprocess-build(解包到 output-projects assets 树) 或确认 raw 解包树存在"}

        stage_dir = REPO / "crackings" / type_ / name / "stages" / stage_path("text-hanization")
        sl_dir = stage_dir / "step1-stringliterals"
        sl_dir.mkdir(parents=True, exist_ok=True)

        # 1) stringliteral.json: 复用 fn-analyze 产物 > 即时 extract(CLI)
        sl_json = self._reuse_stringliteral(type_, name, sl_dir / "stringliteral.json")
        reused = sl_json is not None
        if sl_json is None:
            strings = self._extract_cli(meta_path)
            sl_json = sl_dir / "stringliteral.json"
            sl_json.write_text(json.dumps(strings, ensure_ascii=False, indent=2), encoding="utf-8")
            string_count = len(strings)
        else:
            string_count = len(json.loads(sl_json.read_text(encoding="utf-8")))

        # 2) 备份原 metadata 到 stage 目录(供 patch 基于备份重建)
        backup = stage_dir / "metadata.original.dat"
        if not backup.exists() and meta_path.exists():
            backup.write_bytes(meta_path.read_bytes())

        detection = {
            "stage": "11", "name": "strings-collected",
            "approach": "A-metadata-static",
            "metadata_path": str(meta_path.relative_to(REPO)) if _is_under(meta_path, REPO) else str(meta_path),
            "metadata_source": meta_src,
            "stringliteral_json": str(sl_json.relative_to(REPO)),
            "stringliteral_reused": reused,
            "string_count": string_count,
            "backup_metadata": str(backup.relative_to(REPO)) if backup.exists() else None,
        }
        (stage_dir / "strings-collected.yaml").write_text(
            yaml.safe_dump(detection, allow_unicode=True, sort_keys=False), encoding="utf-8")

        return {
            "rc": 0, "skipped": False,
            "metadata_path": detection["metadata_path"],
            "metadata_source": meta_src,
            "stringliteral_json": detection["stringliteral_json"],
            "stringliteral_reused": reused,
            "string_count": string_count,
            "backup_metadata": detection["backup_metadata"],
        }

    def _extract_cli(self, meta_path) -> list[dict]:
        """经 metadata-patcher.py 的 extract 子命令提取字符串(CLI, 规避连字符 import)。"""
        patcher = REPO / PATCHER
        r = subprocess.run(
            [sys.executable, str(patcher), "extract", str(meta_path)],
            capture_output=True, text=True, timeout=300, cwd=str(REPO),
        )
        if r.returncode != 0:
            raise RuntimeError(f"提取失败: {r.stderr[-400:]}")
        return json.loads(r.stdout)

    @staticmethod
    def _find_metadata(type_, name):
        cands = [
            (REPO / "crackings" / type_ / name / "project/app/src/main" / META_REL, "project(app/src/main)"),
            (REPO / "output-projects" / type_ / name / "app/src/main/assets" / META_REL, "output-projects(app/src/main/assets)"),
            (REPO / "output-projects" / type_ / name / "assets" / META_REL, "output-projects(assets)"),
            (REPO / "crackings" / type_ / name / "raw" / "01-apktool" / "assets" / META_REL, "raw(apktool)"),
            (REPO / "crackings" / type_ / name / "raw" / "03-il2cpp" / "global-metadata.dat", "raw(03-il2cpp)"),
            (REPO / "crackings" / type_ / name / "raw" / "03b-il2cpp-output" / "global-metadata.dat", "raw(03b)"),
            (REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures" / "dump" / "global-metadata.dat", "fn-analyze dump"),
        ]
        for p, src in cands:
            if p.exists():
                return p, src
        return None, None

    @staticmethod
    def _reuse_stringliteral(type_, name, out_path):
        cands = [
            REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures" / "dump" / "stringliteral.json",
            REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "step1-signatures" / "stringliteral.json",
            REPO / "crackings" / type_ / name / "stages" / "03-fn-analyze" / "dump" / "stringliteral.json",
        ]
        for c in cands:
            if c.exists() and c.stat().st_size > 0:
                try:
                    out_path.write_bytes(c.read_bytes())
                    return out_path
                except Exception:
                    return None
        return None


def _is_under(p: Path, root: Path) -> bool:
    try:
        p.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False
