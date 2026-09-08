#!/usr/bin/env python3
"""Reverse-engineering stage: apply explicit SDK/network source plan and build.

Dependencies: standard library, project environment/toolchain via stage_runtime.
JSON contract: see lib/modification_plans.py. Device acceptance is separate.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from modification_plans import apply_plan
from stage_runtime import build_project, run_stage


def execute(ctx):
    result = apply_plan(ctx, 'sdk-network-removal')
    result['build'] = build_project(ctx)
    return result


if __name__ == '__main__':
    raise SystemExit(run_stage('sdk-network-removal', execute))
