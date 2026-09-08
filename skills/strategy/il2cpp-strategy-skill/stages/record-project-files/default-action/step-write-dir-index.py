#!/usr/bin/env python3
"""step-01-write-dir-index.py — 写 crackings/<type>/<Name>/dir-index.yaml。

从原 sub-stage-record-project-files.py 步骤1 拆出。
逻辑等价;索引粒度:目录到 3 级包目录(带文件计数),文件只记浅层交付物/配置。
"""
from __future__ import annotations

import collections
import datetime
import os
import sys
from pathlib import Path


import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step

EXCLUDED_DIRS = {
    ".gradle", "build", ".idea", ".cxx", ".kotlin",
    ".externalNativeBuild", ".transforms", ".navigation",
}
MAX_DIR_DEPTH = 7   # 目录到 3 级包目录
MAX_FILE_DEPTH = 5  # 文件只记浅层


def _is_transient(rel_parts) -> bool:
    return any(p in EXCLUDED_DIRS for p in rel_parts)


def _rel_depth(rel_parts) -> int:
    try:
        base = rel_parts.index("output-projects")
    except ValueError:
        return len(rel_parts)
    return len(rel_parts) - (base + 3)


class WriteDirIndexStep(Step):
    def execute(self, steps_results: dict) -> dict:
        # ctx 试点阶段可能为 None,兜底走环境变量
        name = (self.ctx.name if self.ctx and getattr(self.ctx, "name", None) else os.environ.get("NAME"))
        type_arg = (self.ctx.type if self.ctx and getattr(self.ctx, "type", None) else os.environ.get("TYPE", "android"))

        if not name:
            return {"rc": 1, "error": "缺 NAME"}

        project_root = REPO / "output-projects" / type_arg / name
        cracking_dir = REPO / "crackings" / type_arg / name

        if not project_root.exists():
            return {"rc": 1, "error": f"项目不存在: {project_root}"}

        all_items = []
        dir_counts = collections.Counter()
        for p in sorted(project_root.rglob("*")):
            rel = p.relative_to(REPO).parts
            if _is_transient(rel):
                continue
            if p.is_file():
                kind = "file"
                for k in range(3, len(rel)):
                    dir_counts["/".join(rel[:k])] += 1
            elif p.is_dir():
                kind = "dir"
            else:
                continue
            all_items.append((Path(*rel), kind, _rel_depth(rel)))

        real_files = sum(1 for _, k, _ in all_items if k == "file")
        real_dirs = sum(1 for _, k, _ in all_items if k == "dir")

        files_list = []
        for rel, kind, depth in all_items:
            if kind == "file":
                if depth <= MAX_FILE_DEPTH:
                    files_list.append({"path": str(rel), "kind": "file"})
            else:
                if depth <= MAX_DIR_DEPTH:
                    files_list.append({
                        "path": str(rel), "kind": "dir",
                        "count": dir_counts.get(str(rel), 0),
                    })

        files_list.sort(key=lambda e: e["path"])

        dir_index_data = {
            "name": name,
            "type": type_arg,
            "generated_at": datetime.datetime.now().isoformat(timespec="seconds"),
            "stage": stage_path("record-project-files"),
            "index_granularity": f"dirs<=depth{MAX_DIR_DEPTH} (3级包目录,带文件计数), files<=depth{MAX_FILE_DEPTH} (浅层交付物/配置)",
            "files": files_list,
            "total_files": real_files,
            "total_dirs": real_dirs,
            "indexed_dirs": sum(1 for e in files_list if e["kind"] == "dir"),
            "indexed_files": sum(1 for e in files_list if e["kind"] == "file"),
        }

        dir_index_path = cracking_dir / "dir-index.yaml"
        dir_index_path.write_text(
            yaml.safe_dump(dir_index_data, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        return {
            "rc": 0,
            "path": str(dir_index_path.relative_to(REPO)),
            "total_files": real_files,
            "total_dirs": real_dirs,
            "indexed_files": sum(1 for e in files_list if e["kind"] == "file"),
            "indexed_dirs": sum(1 for e in files_list if e["kind"] == "dir"),
        }