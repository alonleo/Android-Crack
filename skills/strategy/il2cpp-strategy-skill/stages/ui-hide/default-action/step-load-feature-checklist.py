#!/usr/bin/env python3
"""Type-local adapter for the shared feature checklist step."""
from pathlib import Path
import runpy

_api = runpy.run_path(str((Path(__file__).parent / "../../../../../common/feature-removal-strategy-skill/scripts/step-load-feature-checklist.py").resolve()))
LoadFeatureChecklistStep = _api["LoadFeatureChecklistStep"]
