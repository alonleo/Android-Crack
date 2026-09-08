#!/usr/bin/env python3
"""Regression checks for YAML CRUD, generated Markdown and stage consumption."""
import copy
import json
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "skills/common/scripts/lib"))
import common


class ChecklistTests(unittest.TestCase):
    def setUp(self):
        self.assertTrue((HERE / "manage-feature-checklist.py").is_file(), "Missing YAML checklist CRUD implementation")
        self.api = runpy.run_path(str(HERE / "manage-feature-checklist.py"))
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "features.yaml"
        self.item = {"id": "F01", "key": "contact", "kind": "feature", "name": "联系我们",
                     "keywords": ["Contact"], "types": ["*"], "enabled": True,
                     "strategy": "review", "notes": "保留核心依赖"}
        self.data = {"schema_version": 1, "items": [self.item]}
        self.path.write_text(yaml.safe_dump(self.data, allow_unicode=True), encoding="utf-8")

    def test_crud_persists_and_synchronizes_agent_document(self):
        change = self.api["change_registry"]
        new = dict(self.item, id="F02", key="credits", name="鸣谢", keywords=["Credits"])
        change(self.path, "add", data=new)
        change(self.path, "update", "F02", {"keywords": ["About"], "notes": "布局 | 回调"})
        data = self.api["load_registry"](self.path)
        self.assertEqual(data["items"][1]["keywords"], ["About"])
        rendered = self.path.with_suffix(".md").read_text(encoding="utf-8")
        self.assertIn("About", rendered)
        self.assertNotIn("Credits", rendered)
        self.assertIn("布局 \\| 回调", rendered)
        change(self.path, "delete", "F02")
        self.assertEqual(len(self.api["load_registry"](self.path)["items"]), 1)
        self.assertNotIn("F02", self.path.with_suffix(".md").read_text(encoding="utf-8"))

    def test_rejected_edits_leave_registry_unchanged(self):
        baseline = self.path.read_bytes()
        for op, ident, patch in [("add", None, self.item), ("update", "F99", {"name": "不存在"}),
                                 ("update", "F01", {"enabled": "false"}),
                                 ("update", "F01", {"id": "F02"}),
                                 ("update", "F01", {"keyword": ["typo"]}),
                                 ("delete", "F99", None)]:
            with self.subTest(op=op, patch=patch):
                with self.assertRaises(ValueError):
                    self.api["change_registry"](self.path, op, ident, patch)
                self.assertEqual(self.path.read_bytes(), baseline)

    def test_duplicate_yaml_keys_and_invalid_schema_fail_closed(self):
        self.path.write_text("schema_version: 1\nschema_version: 2\nitems: []\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.api["load_registry"](self.path)
        for changes in ({"types": ["unknown-engine"]}, {"keywords": []}, {"id": "P01"}):
            item = dict(self.item, **changes)
            self.path.write_text(yaml.safe_dump({"schema_version": 1, "items": [item]}), encoding="utf-8")
            with self.assertRaises(ValueError):
                self.api["load_registry"](self.path)

    def test_stage_filters_type_and_disabled_items_after_updates(self):
        change = self.api["change_registry"]
        change(self.path, "add", data=dict(self.item, id="F02", key="unity_only", types=["il2cpp"]))
        change(self.path, "add", data=dict(self.item, id="P01", key="dialog", kind="popup", enabled=False))
        data = self.api["load_registry"](self.path)
        self.assertEqual(set(self.api["targets_for_type"](data, "android")), {"contact"})
        self.assertEqual(set(self.api["targets_for_type"](data, "il2cpp")), {"contact", "unity_only"})
        change(self.path, "update", "F01", {"keywords": ["FreshKeyword"]})
        self.assertEqual(self.api["targets_for_type"](self.api["load_registry"](self.path), "android")["contact"]["keywords"], ["FreshKeyword"])

    def test_cli_query_and_failure_exit_code(self):
        cmd = [sys.executable, str(HERE / "manage-feature-checklist.py"), "--registry", str(self.path)]
        result = subprocess.run(cmd + ["get", "F01"], capture_output=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["name"], "联系我们")
        failure = subprocess.run(cmd + ["delete", "F99"], capture_output=True, encoding="utf-8")
        self.assertNotEqual(failure.returncode, 0)

    def test_shipped_registry_has_synchronized_agent_document(self):
        data = self.api["load_registry"]()
        registry = self.api["DEFAULT_REGISTRY"]
        self.assertEqual(registry.with_suffix(".md").read_text(encoding="utf-8"), self.api["render_markdown"](data))

    def test_step_scanner_and_plan_use_the_same_current_snapshot(self):
        folder = ROOT / "skills/strategy/il2cpp-strategy-skill/stages/ui-hide/default-action"
        scan_module = runpy.run_path(str(folder / "step-scan-features.py"))
        plan_module = runpy.run_path(str(folder / "step-gen-hide-plan.py"))
        source = self.path.parent / "dump.cs"
        source.write_text("public void Contact() {}", encoding="utf-8")
        snapshot = self.api["load_snapshot"](self.path, "il2cpp")
        with patch.dict(os.environ, {"NAME": "Fixture", "TYPE": "il2cpp", "FEATURE_REMOVAL_CHECKLIST": str(self.path)}):
            scan_type = scan_module["ScanFeaturesStep"]
            with patch.object(scan_type, "_find_dump_cs", return_value=source), patch.dict(scan_type.execute.__globals__, {"REPO": self.path.parent}):
                scan = scan_type(ctx=None).execute({"ui-hide.default-action.load-feature-checklist": snapshot})
            self.assertEqual(scan["features_found"], {"contact": ["Contact"]})
            # Changing the global definition after scanning must not mix versions.
            self.api["change_registry"](self.path, "update", "F01", {"keywords": ["NewContact"]})
            plan_type = plan_module["GenHidePlanStep"]
            with patch.dict(plan_type.execute.__globals__, {"REPO": self.path.parent, "stage_path": lambda name: "07-ui-hide"}):
                result = plan_type(ctx=None).execute({"ui-hide.default-action.scan-features": scan})
            generated = yaml.safe_load((self.path.parent / result["hide_plan"]).read_text(encoding="utf-8"))
            self.assertEqual(generated["checklist_sha256"], snapshot["registry_sha256"])
            self.assertEqual(generated["items"][0]["keywords"], ["Contact"])
            self.assertEqual(generated["items"][0]["id"], "F01")

    def test_all_types_load_yaml_as_first_stage_step(self):
        for engine in self.api["known_types"]():
            with self.subTest(engine=engine):
                folder = ROOT / "skills/strategy" / f"{engine}-strategy-skill/stages/ui-hide/default-action"
                driver = runpy.run_path(str(folder / "step-driver.py"))
                first = driver["_load_register"](folder)[0]
                self.assertEqual(first["name"], "load-feature-checklist")
                module = runpy.run_path(str(folder / first["script"]))
                with patch.dict(os.environ, {"TYPE": engine, "FEATURE_REMOVAL_CHECKLIST": str(self.path)}):
                    result = module["LoadFeatureChecklistStep"](ctx=None).execute({})
                self.assertEqual(set(result["targets"]), {"contact"})
                self.assertEqual(result["items"][0]["id"], "F01")
                self.assertEqual(len(result["registry_sha256"]), 64)

    def test_legacy_scanner_reads_updated_yaml_instead_of_embedded_keywords(self):
        script = ROOT / "skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-ui-hide.py"
        with patch.dict(os.environ, {"TYPE": "il2cpp", "FEATURE_REMOVAL_CHECKLIST": str(self.path)}):
            module = runpy.run_path(str(script))
            self.assertIn("load_feature_targets", module, "Legacy worker still uses embedded target data")
            self.assertEqual(set(module["load_feature_targets"]()), {"contact"})
            self.api["change_registry"](self.path, "update", "F01", {"keywords": ["ChangedContact"]})
            self.assertEqual(module["load_feature_targets"]()["contact"]["keywords"], ["ChangedContact"])

    def test_legacy_candidates_require_review_and_plan_escapes_strings(self):
        self.api["change_registry"](self.path, "update", "F01", {"name": '关于 "Game"', "notes": '检查 "布局"\n和回调', "strategy": "hook_method"})
        script = ROOT / "skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-ui-hide.py"
        with patch.dict(os.environ, {"TYPE": "il2cpp", "FEATURE_REMOVAL_CHECKLIST": str(self.path)}):
            module = runpy.run_path(str(script))
            scan = {"contact": [{"signature": "void Contact()", "method": "Contact", "rva": "0x1234", "class": "Menu"}]}
            strategies = module["analyze_and_select_strategy"](scan, self.path.parent / "absent-dump.cs")
            self.assertEqual(strategies["contact"]["strategy"], "review")
            self.assertTrue(strategies["contact"]["requires_review"])
            generated = module["generate_hide_plan"]("Fixture", strategies, self.path.parent)
            plan = yaml.safe_load(generated.read_text(encoding="utf-8"))
            self.assertEqual(plan["targets"]["contact"]["desc"], '关于 "Game"')
            self.assertEqual(plan["targets"]["contact"]["reason"], '检查 "布局"\n和回调')


if __name__ == "__main__":
    common._REPO_ROOT = ROOT
    common.ensure_env()
    common.log_info("Checking feature checklist behavior using isolated YAML fixtures")
    unittest.main(verbosity=2)
