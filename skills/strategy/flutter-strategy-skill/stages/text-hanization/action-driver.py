#!/usr/bin/env python3
"""[DRIVER] 11-text-hanization/action-driver.py — 执行方案驱动器。

驱动器只做三件事:
1. 加载 action-register.yaml(动作路由/配置表)
2. 从 yaml 获取**当前使用的 action**(run-action 字段)
3. 委托该 action 目录的 step-driver 执行

用法:
    python3 action-driver.py [--action NAME]
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import yaml

SUB_STAGE_DIR = Path(__file__).resolve().parent
CONFIG_YAML = SUB_STAGE_DIR / "action-register.yaml"


def load_config() -> dict:
    if not CONFIG_YAML.exists():
        raise FileNotFoundError(f"缺 action-register.yaml: {CONFIG_YAML}")
    return yaml.safe_load(CONFIG_YAML.read_text(encoding="utf-8")) or {}


def resolve_current_action(config: dict, requested: str = "") -> dict:
    name = requested or config.get("run-action") or config.get("active")
    all_actions = config.get("all-actions", []) or []
    if name:
        for a in all_actions:
            if a.get("name") == name:
                merged = dict(a)
                merged.setdefault("path", f"./{name}")
                return merged
        return {"name": name, "path": f"./{name}", "steps": 0, "notes": "default 指定"}
    if all_actions:
        first = dict(all_actions[0])
        first.setdefault("path", f"./{first.get('name', '')}")
        return first
    return None


def _load_step_dispatcher(action_dir: Path):
    path = action_dir / "step-driver.py"
    if not path.exists():
        raise FileNotFoundError(f"action 缺 step-driver.py: {path}")
    spec = importlib.util.spec_from_file_location(
        f"step_dispatcher_{action_dir.parent.name}_{action_dir.name}", path
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"无法构造 spec: {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def dispatch(action_cfg: dict, ctx=None, steps_results: dict | None = None) -> dict:
    action_name = action_cfg.get("name", "")
    action_path = action_cfg.get("path", f"./{action_name}")
    action_dir = Path(action_path)
    if not action_dir.is_absolute():
        action_dir = SUB_STAGE_DIR / action_dir
    if not action_dir.is_dir():
        raise FileNotFoundError(f"缺 action 目录: {action_dir}")

    sub_stage_name = SUB_STAGE_DIR.name
    step_dispatcher = _load_step_dispatcher(action_dir)
    results = steps_results if steps_results is not None else {}
    result = step_dispatcher.dispatch_steps(
        action_dir, ctx, results,
        sub_stage=sub_stage_name, action_name=action_name,
        steps_order=None,
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="执行方案驱动器")
    parser.add_argument("--action", default="")
    args = parser.parse_args()

    config = load_config()
    action_cfg = resolve_current_action(config, args.action)
    if action_cfg is None:
        print(f"[action-driver] {CONFIG_YAML} 中无可用 action", file=sys.stderr)
        return 2

    print(f"[action-driver] 当前使用 action: {action_cfg['name']} → {action_cfg.get('path')}")
    result = dispatch(action_cfg, ctx=None, steps_results={})
    print(f"[action-driver] 完成,result keys: {list(result.keys())}")

    out_path = SUB_STAGE_DIR / ".action_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
