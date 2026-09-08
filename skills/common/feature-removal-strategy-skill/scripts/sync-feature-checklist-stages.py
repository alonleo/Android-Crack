#!/usr/bin/env python3
"""Register the shared YAML loading step in each type's ui-hide action.

Default previews. --apply updates registers and type-local delegation wrappers.
Other steps retain their relative execution order and implementation.
"""
import argparse
import ast
import os
from pathlib import Path
import re
import sys

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "skills/common/scripts/lib"))
import common


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    writes = {}
    for folder in sorted((ROOT / "skills/strategy").glob("*-strategy-skill")):
        register_path = folder / "stages/ui-hide/default-action/step-register.yaml"
        register = yaml.safe_load(register_path.read_text(encoding="utf-8"))
        steps = sorted(register["steps"], key=lambda step: int(step["number"]))
        steps = [step for step in steps if step["name"] != "load-feature-checklist"]
        steps.insert(0, {"number": 1, "name": "load-feature-checklist", "script": "step-load-feature-checklist.py",
                         "notes": "读取并校验统一 YAML；异常立即阻断，输出候选项与清单 SHA-256"})
        for number, step in enumerate(steps, 1):
            step["number"] = number
        register["steps"] = steps
        writes[register_path] = yaml.safe_dump(register, allow_unicode=True, sort_keys=False)
        wrapper = register_path.parent / "step-load-feature-checklist.py"
        relative = os.path.relpath(HERE / "step-load-feature-checklist.py", wrapper.parent).replace("\\", "/")
        writes[wrapper] = ('#!/usr/bin/env python3\n"""Type-local adapter for the shared feature checklist step."""\n'
                          'from pathlib import Path\nimport runpy\n\n'
                          f'_api = runpy.run_path(str((Path(__file__).parent / "{relative}").resolve()))\n'
                          'LoadFeatureChecklistStep = _api["LoadFeatureChecklistStep"]\n')
        action_path = folder / "stages/ui-hide/action-register.yaml"
        actions = yaml.safe_load(action_path.read_text(encoding="utf-8"))
        for action in actions["all-actions"]:
            if action["name"] == "default-action":
                action["steps"] = len(steps)
        writes[action_path] = yaml.safe_dump(actions, allow_unicode=True, sort_keys=False)
        readme = folder / "scripts/README.md"
        text = readme.read_text(encoding="utf-8") if readme.exists() else f"# {folder.name} 脚本索引\n"
        if "step-load-feature-checklist.py" not in text:
            text += ("\n## 去功能点清单\n\n"
                     "`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。\n")
        writes[readme] = text
    for path, content in writes.items():
        if path.is_file() and path.read_text(encoding="utf-8") == content:
            continue
        if not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Outside workspace: {path}")
        common.log_info("WRITE", path.relative_to(ROOT))
        if args.apply:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            if path.suffix == ".py":
                path.chmod(path.stat().st_mode | 0o111)
                ast.parse(content)
    return 0


if __name__ == "__main__":
    common._REPO_ROOT = ROOT
    common.ensure_env()
    raise SystemExit(main())
