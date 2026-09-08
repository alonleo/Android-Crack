#!/usr/bin/env python3
"""[DRIVER] 01-static-analyze/action-driver.py — 执行方案驱动器。

驱动器只做三件事:
1. 加载 action-register.yaml(动作路由/配置表)
2. 从 yaml 获取**当前使用的 action**(run-action 字段)
3. 委托该 action 目录的 step_dispatcher 执行

不遍历全部 action —— 用哪个 action 由 action-register.yaml 的 default 声明决定。
调用方(如 sub_stage-dispatcher 或直接运行本文件)拿到当前 action 后执行。

用法:
    python3 action-driver.py [--action NAME]   # 显式指定;默认用 config 的 default
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
    """加载 action-register.yaml。"""
    if not CONFIG_YAML.exists():
        raise FileNotFoundError(f"缺 action-register.yaml: {CONFIG_YAML}")
    return yaml.safe_load(CONFIG_YAML.read_text(encoding="utf-8")) or {}


def resolve_current_action(config: dict, requested: str = "") -> dict:
    """从 config 获取当前应使用的 action。

    优先级:
      1. requested(命令行显式指定)
      2. config.get("default") / config.get("default-action") / config.get("active")
      3. all-actions 列表第一个
    返回 {name, path, ...} 或 None。
    """
    name = requested or config.get("run-action") or config.get("active")
    all_actions = config.get("all-actions", []) or []

    # 若已有 name,从 all-actions 找匹配项补全 path
    if name:
        for a in all_actions:
            if a.get("name") == name:
                merged = dict(a)
                merged.setdefault("path", f"./{name}")
                return merged
        # 未在 all-actions 列出,但 config 显式给了 default —— 推断 path
        return {"name": name, "path": f"./{name}", "steps": 0, "notes": "default 指定,未列入 all-actions"}

    # 无 default → 用第一个
    if all_actions:
        first = dict(all_actions[0])
        first.setdefault("path", f"./{first.get('name', '')}")
        return first
    return None


def _load_step_dispatcher(action_dir: Path):
    """动态 import action 目录的 step-driver.py。"""
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
    """委托当前 action 的 step_dispatcher 执行。

    :param action_cfg: resolve_current_action 返回的 {name, path, ...}
    :param ctx: StageContext(可传 None,step 用 os.environ)
    :param steps_results: 跨 step 累积 dict(可传 None 初始化为空)
    :return: action 的 step 结果 dict
    """
    action_name = action_cfg.get("name", "")
    action_path = action_cfg.get("path", f"./{action_name}")
    action_dir = Path(action_path)
    if not action_dir.is_absolute():
        action_dir = SUB_STAGE_DIR / action_dir

    if not action_dir.is_dir():
        raise FileNotFoundError(f"缺 action 目录: {action_dir}")

    sub_stage_name = SUB_STAGE_DIR.name  # 如 "01-static-analyze"(含 NN- 前缀)

    step_dispatcher = _load_step_dispatcher(action_dir)
    results = steps_results if steps_results is not None else {}
    result = step_dispatcher.dispatch_steps(
        action_dir, ctx, results,
        sub_stage=sub_stage_name, action_name=action_name,
        steps_order=None,  # 顺序由 step-register.yaml 的 number 决定
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="执行方案驱动器(读 action-register.yaml 选当前 action)")
    parser.add_argument("--action", default="", help="显式指定 action 名(默认用 config 的 default)")
    args = parser.parse_args()

    config = load_config()
    action_cfg = resolve_current_action(config, args.action)
    if action_cfg is None:
        print(f"[action-driver] {CONFIG_YAML} 中无可用 action", file=sys.stderr)
        return 2

    print(f"[action-driver] 当前使用 action: {action_cfg['name']} → {action_cfg.get('path')}")
    result = dispatch(action_cfg, ctx=None, steps_results={})
    print(f"[action-driver] 完成,result keys: {list(result.keys())}")

    # 写到子阶段目录
    out_path = SUB_STAGE_DIR / ".action_result.json"
    out_path.write_text(json.dumps(result, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())