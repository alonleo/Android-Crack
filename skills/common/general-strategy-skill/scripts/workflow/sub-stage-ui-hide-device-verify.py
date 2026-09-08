#!/usr/bin/env python3
"""Reverse-project worker: ui-hide-device-verify.

Dependencies: project environment, common.adb(), Pillow, explicit device JSON
plan. The shared runtime loads env.sh, records success/failure and evidence.
See stage_device_verify.py for the assertion/action schema. Missing physical
device or stage assertions fails this stage; never claims final acceptance.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'lib'))
from stage_device_verify import execute
from stage_runtime import run_stage


if __name__ == '__main__':
    raise SystemExit(run_stage('ui-hide-device-verify', execute))
