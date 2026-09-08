#!/usr/bin/env python3
"""sub_stage-dispatcher.py — 子阶段总调度器(读 sub-stage-register.yaml 按 id 顺序动态加载)。

sub_stage > action > step 三层架构(register 驱动)。

放在 il2cpp-strategy-skill/stages/ 目录,与 sub-stage-register.yaml、各子阶段目录同级。

职责:
  1. 读 sub-stage-register.yaml(子阶段注册表),拿全部子阶段条目(id/name/actions)
  2. **按 register 里 sub_stages 列表的书写顺序**遍历子阶段 —— 调整 register 条目排列(/改 id)即可动态改执行顺序
  3. 子阶段目录 = stages/<name>/(纯名, 无序号前缀)
  4. 委托子阶段目录的 action-driver.py 执行(它内部读 action-register 选 action)

调用入口:
    python3 sub_stage-dispatcher.py                       # 全跑(按 register id 顺序)
    python3 sub_stage-dispatcher.py --stage 04            # 单子阶段(按 id)
    python3 sub_stage-dispatcher.py --stage sdk-network-removal    # 单子阶段(按 name)
    python3 sub_stage-dispatcher.py --action default-action  # 传给每个子阶段的 action(-driver 显式)

环境变量:NAME / TYPE / ANDROID_SERIAL / PATCHED / CRACK_DIR
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import yaml

STAGES_DIR = Path(__file__).resolve().parent
REGISTER_YAML = STAGES_DIR / "sub-stage-register.yaml"
# [FLOWFIX 2026-08-30] parents[3] = skills/；实际 ROOT 是 parents[5] = 工作区根。
REPO = Path(__file__).resolve().parents[5]


def _load_register() -> list[dict]:
    """读 sub-stage-register.yaml,返回子阶段条目列表。

    顺序 = register 里 `sub_stages:` 列表的**书写顺序**(用户调整条目排列/改 id 即可动态改执行顺序)。
    不强制按 id sort —— 让用户在 register 里拖动/调整顺序即生效。
    id 仅作标识(--stage 匹配用),执行顺序以书写顺序为准。
    """
    if not REGISTER_YAML.exists():
        raise FileNotFoundError(f"缺 sub-stage-register.yaml: {REGISTER_YAML}")
    data = yaml.safe_load(REGISTER_YAML.read_text(encoding="utf-8"))
    stages = data.get("sub_stages", []) or []
    return stages


def _get_actions(sub_stage: dict) -> list[str]:
    """从子阶段条目拿 actions 列表(默认 [default-action])。"""
    actions = sub_stage.get("actions", []) or []
    return actions if actions else ["default-action"]


def dispatch_sub_stage(sub_stage: dict, ctx=None, requested_action: str = "") -> dict:
    """跑单个子阶段:委托其 action-driver.py。

    :param sub_stage: register 中的子阶段条目
    :param ctx: StageContext(可传 None, step 用 os.environ)
    :param requested_action: 要传给 action-driver 的 --action 参数(空则用 config 默认)
    :return: action-driver 的返回 dict
    """
    stage_id = sub_stage.get("id") or "?"
    stage_name = sub_stage.get("name") or ""
    if not stage_name:
        return {"_error": "sub-stage-register 条目缺 name", "_stage": stage_id}
    stage_dir = STAGES_DIR / stage_name
    if not stage_dir.is_dir():
        print(f"[sub_stage-dispatcher] 缺子阶段目录: {stage_dir}", file=sys.stderr)
        return {"_error": f"missing stage dir: {stage_dir}", "_stage": stage_name}

    driver_path = stage_dir / "action-driver.py"
    if not driver_path.exists():
        print(f"[sub_stage-dispatcher] 缺 action-driver.py: {driver_path}", file=sys.stderr)
        return {"_error": f"missing action-driver: {driver_path}", "_stage": stage_name}

    actions = _get_actions(sub_stage)
    print(f"[sub_stage-dispatcher] #id={stage_id} {stage_name} → action-driver(actions={actions})")

    # 用 subprocess 调用 action-driver.py(独立进程, 避免 import/argv 副作用)
    cmd = [sys.executable, str(driver_path)]
    if requested_action:
        cmd += ["--action", requested_action]
    import subprocess
    import os
    # [FLOWFIX 2026-08-30] 转发环境变量 (NAME / TYPE / ANDROID_SERIAL / PATCHED / CRACK_DIR)
    # 给子进程。原版 env=None 导致 step-* 脚本 os.environ.get("NAME") 拿到空字符串失败。
    env = os.environ.copy()
    # [FLOWFIX 2026-08-30] 删除旧 .action_result.json 缓存,避免读到上次结果。
    cache = stage_dir / ".action_result.json"
    if cache.exists():
        cache.unlink()
    r = subprocess.run(cmd, capture_output=True, text=True, env=env, cwd=str(REPO), timeout=600)
    if r.returncode != 0:
        print(f"[sub_stage-dispatcher] {stage_name} action-driver 失败(rc={r.returncode}):\n{r.stderr[-300:]}",
              file=sys.stderr)
        return {"_error": f"action-driver rc={r.returncode}", "_stage": stage_name}

    # 读 action-driver 写到子阶段目录的 .action_result.json
    result_path = stage_dir / ".action_result.json"
    if result_path.exists():
        try:
            return json.loads(result_path.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {"_done": True, "_stage": stage_name, "stdout_tail": r.stdout[-200:]}


def main() -> int:
    parser = argparse.ArgumentParser(description="子阶段调度器(读 register 按 id 顺序)")
    parser.add_argument("--stage", help="只跑指定子阶段(id 或 name);默认按 register 顺序全跑")
    parser.add_argument("--action", default="", help="传给 action-driver 的 --action(可覆盖 config default)")
    args = parser.parse_args()

    sub_stages = _load_register()
    if args.stage:
        target = args.stage
        matched = [s for s in sub_stages
                   if str(s.get("id")) == target or s.get("name") == target]
        if not matched:
            print(f"[sub_stage-dispatcher] 未找到子阶段: {target}", file=sys.stderr)
            return 2
        sub_stages = matched

    all_results: dict = {}
    failed = []
    for sub_stage in sub_stages:
        stage_name = sub_stage.get("name")
        stage_id = sub_stage.get("id")
        print(f"\n=== 子阶段 id={stage_id} {stage_name} ===")
        result = dispatch_sub_stage(sub_stage, ctx=None, requested_action=args.action)
        all_results[stage_name] = result
        if "_error" in result:
            failed.append({"stage": stage_name, "error": result["_error"]})
            break  # 一个失败即停

    print(f"\n[sub_stage-dispatcher] 全部完成。子阶段失败: {len(failed)}")
    for f in failed:
        print(f"  - {f['stage']}: {f['error']}", file=sys.stderr)

    out_path = STAGES_DIR / ".sub_stage_results.json"
    out_path.write_text(json.dumps(all_results, ensure_ascii=False, indent=2, default=str),
                        encoding="utf-8")

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())