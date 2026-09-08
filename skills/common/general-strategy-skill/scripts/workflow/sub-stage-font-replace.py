#!/usr/bin/env python3
"""Reverse-engineering stage: replace explicit decoded fonts and rebuild.

Dependencies: shared stage_runtime, Pillow/FreeType; Android environment loaded by
run_stage. Plan replacements require work-relative source, project-relative
target and required_characters. Packed engine fonts require their type handler.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from localization import apply_localization
from stage_runtime import build_project, run_stage


def execute(ctx):
    result = apply_localization(ctx, "font")
    result["build"] = build_project(ctx)
    return result


if __name__ == "__main__":
    raise SystemExit(run_stage("font-replace", execute))
