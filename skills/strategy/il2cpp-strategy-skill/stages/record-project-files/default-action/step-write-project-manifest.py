#!/usr/bin/env python3
"""step-02-write-project-manifest.py — 写 crackings/<type>/<Name>/output-project-manifest.yaml。

从原 sub-stage-record-project-files.py 步骤2 拆出。
依赖 step-01-write-dir-index 的产出路径(可读 steps_results['record.write_dir_index'])。
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import stage_path, REPO, Step


class WriteProjectManifestStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = (self.ctx.name if self.ctx and getattr(self.ctx, "name", None) else os.environ.get("NAME"))
        type_arg = (self.ctx.type if self.ctx and getattr(self.ctx, "type", None) else os.environ.get("TYPE", "android"))

        if not name:
            return {"rc": 1, "error": "缺 NAME"}

        project_root = REPO / "output-projects" / type_arg / name
        cracking_dir = REPO / "crackings" / type_arg / name

        patched_apk = project_root / "patched.apk"
        as_apk = project_root / "app/build/outputs/apk/release/app-release.apk"
        keystore = project_root / "my.keystore.jks"

        manifest = {
            "name": name,
            "type": type_arg,
            "stages_completed": [stage_path("record-project-files")],
            "output_root": str(project_root.relative_to(REPO)),
            "patched_apk": str(patched_apk.relative_to(REPO)) if patched_apk.exists() else None,
            "as_apk": str(as_apk.relative_to(REPO)) if as_apk.exists() else None,
            "keystore_symlink": str(keystore.relative_to(REPO)),
        }

        # 读 step-01 输出(可证明跨 step 累积可用)
        prior = steps_results.get("record-project-files.default-action.write_dir_index", {})

        manifest_path = cracking_dir / "output-project-manifest.yaml"
        manifest_path.write_text(
            yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )

        return {
            "rc": 0,
            "path": str(manifest_path.relative_to(REPO)),
            "patched_apk_exists": patched_apk.exists(),
            "as_apk_exists": as_apk.exists(),
            "prior_dir_index_total_files": prior.get("total_files"),
        }