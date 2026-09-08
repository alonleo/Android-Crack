#!/usr/bin/env python3
"""Reverse-engineering stage: apply reviewed UTF-8 translations and rebuild.

Dependencies: shared stage_runtime and project Android environment. Plan files
specify path, format (android-xml/text), and source/target/count replacements.
XML source/target are full string or item inner XML, with markup preserved.
Packed engine text requires a type-specific decoder before this stage.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "lib"))
from localization import apply_localization
from stage_runtime import build_project, run_stage


def execute(ctx):
    result = apply_localization(ctx, "text")
    result["build"] = build_project(ctx)
    return result


if __name__ == "__main__":
    raise SystemExit(run_stage("text-hanization", execute))
