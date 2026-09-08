#!/usr/bin/env python3
"""Reverse-engineering stage: copy reviewed localized image assets and rebuild.

Dependencies: shared stage_runtime, Pillow, project Android environment. Plan
replacements specify work-relative source and existing project-relative target.
Requires matching PNG/JPEG/WebP format, geometry, mode and color profile;
animation, nine-patch, packed textures need a type-specific handler.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from localization import apply_localization
from stage_runtime import build_project, run_stage


def execute(ctx):
    result = apply_localization(ctx, "image")
    result["build"] = build_project(ctx)
    return result


if __name__ == "__main__":
    raise SystemExit(run_stage("image-hanization", execute))
