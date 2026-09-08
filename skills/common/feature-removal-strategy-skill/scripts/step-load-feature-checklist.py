#!/usr/bin/env python3
"""Shared first step for ui-hide: read and validate the current YAML snapshot."""
import os
from pathlib import Path
import runpy

API = runpy.run_path(str(Path(__file__).with_name("manage-feature-checklist.py")))


class LoadFeatureChecklistStep:
    def __init__(self, ctx=None):
        self.ctx = ctx

    def execute(self, steps_results):
        # Raise on invalid data: legacy step drivers do not stop on an rc field.
        engine = os.environ.get("TYPE", "").strip()
        if not engine:
            raise ValueError("TYPE is required to select the feature checklist")
        snapshot = API["load_snapshot"](os.environ.get("FEATURE_REMOVAL_CHECKLIST") or None, engine)
        API["common"].log_info(f"ui-hide: loaded {len(snapshot['items'])} checklist items for {engine}")
        return {"rc": 0, "skipped": False, **snapshot}


if __name__ == "__main__":
    API["common"]._REPO_ROOT = API["ROOT"]
    API["common"].ensure_env()
    raise SystemExit("Use the current type ui-hide action driver to load this step")
