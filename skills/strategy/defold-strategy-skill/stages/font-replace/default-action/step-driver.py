#!/usr/bin/env python3
"""[STEP-DRIVER] 09-font-replace/default-action/step-driver.py — 步骤调度器。

职责:
1. 加载 step-register.yaml(步骤注册表)
2. **按 number 字段顺序**(01/02/...)排列 step
3. 每个 step 按 script 字段匹配脚本文件,动态 import + 实例化同名类 + execute()
"""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))


def _script_to_class_name(script_name: str) -> str:
    base = script_name.replace(".py", "")
    base = re.sub(r"^step-\d+-", "", base)
    base = re.sub(r"^step-", "", base)
    parts = base.split("-")
    return "".join(p.capitalize() for p in parts) + "Step"


def _load_register(action_dir: Path) -> list[dict]:
    register_path = action_dir / "step-register.yaml"
    if not register_path.exists():
        raise FileNotFoundError(f"缺 step-register.yaml: {register_path}")
    register = yaml.safe_load(register_path.read_text(encoding="utf-8"))
    steps = register.get("steps", []) or []

    def _num(s):
        """把 number 统一转 int;None 排最后。YAML 中 01-07 是 int,08+ 带前导零是 str。"""
        n = s.get("number")
        if n is None:
            return (1, 0)  # (is_none, sortkey)
        return (0, int(n))

    return sorted(steps, key=_num)


def dispatch_steps(action_dir: Path, ctx, steps_results: dict,
                  sub_stage: str = "", action_name: str = "",
                  steps_order: list[str] | None = None) -> dict:
    steps = _load_register(action_dir)
    prefix = f"{sub_stage}.{action_name}" if sub_stage else action_name
    action_results: dict = {}
    for step in steps:
        step_name = step.get("name")
        script_name = step.get("script")
        step_num = step.get("number")
        if not script_name or not step_name:
            print(f"[step-driver] step 配置缺 name/script: {step}", file=sys.stderr)
            continue

        script_path = action_dir / script_name
        if not script_path.exists():
            raise FileNotFoundError(f"缺 step 脚本({script_name}): {script_path}")

        class_name = _script_to_class_name(script_name)
        spec = importlib.util.spec_from_file_location(
            f"{action_dir.name}_{step_name}", script_path
        )
        if spec is None or spec.loader is None:
            raise ImportError(f"无法构造 spec: {script_path}")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        step_cls = getattr(mod, class_name, None)
        if step_cls is None:
            raise AttributeError(f"{script_name} 中找不到类 {class_name}")

        instance = step_cls(ctx=ctx)
        print(f"[{prefix}/step-driver] #{step_num} {step_name} → {class_name}")
        result = instance.execute(steps_results)
        action_results[step_name] = result
        steps_results[f"{prefix}.{step_name}"] = result

    return action_results


if __name__ == "__main__":
    print("(此文件由 action driver 委托调用)")
