#!/usr/bin/env python3
"""step_base.py — 所有 step 脚本的基类(供 step-NN-*.py 继承)。

sub_stage > action > step 三层架构。

每个 step 是 1 个 .py 文件,通过 step_dispatcher 动态 import + 实例化 + execute() 调用。
step 脚本位于 stages/<sub_stage>/<action>/step-NN-*.py,目录深度可变,
所以 REPO 不再用 parents[N] 硬编码,而是用 _find_repo() 自适应探测。

子类契约:
    class <Name>Step(Step):
        def execute(self, steps_results: dict) -> dict:
            ... 实现真执行逻辑 ...
            return {"key": value}

steps_results 透传:
    - 当前 step 可读前置 step 输出(steps_results["<sub_stage>.<action>.<step>"])
    - 跨 action 也可读(steps_results 由 action dispatcher 累积)
"""
from __future__ import annotations

import os
import sys
from pathlib import Path


def _find_repo(start: Path) -> Path:
    """从 start 向上找包含 AGENTS.md 的目录,作为 REPO 根。

    探测标记优先级:
      1. AGENTS.md(android-crack 工作区根)
      2. .git 目录
      3. 上溯到 / 兜底失败
    """
    p = start.resolve()
    for ancestor in [p, *p.parents]:
        if (ancestor / "AGENTS.md").is_file() and (ancestor / "skills").is_dir():
            return ancestor
        if (ancestor / ".git").is_dir():
            return ancestor
    return p  # 兜底


# 动态探测 REPO(每个 step 脚本 import 时各自探测一次)
REPO = _find_repo(Path(__file__).parent)


class Step:
    """所有 step 的基类。"""

    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, steps_results: dict) -> dict:
        """子类必须重写:返回 dict 结果,会被累积到 steps_results。"""
        raise NotImplementedError(f"{type(self).__name__} 必须重写 execute()")


def resolve_apk(name: str, apk_env: str = "") -> "Path | None":
    """解析源 APK 路径。

    1. 若 apk_env 非空且存在,直接用
    2. 优先用 crackings/*/<name>/raw/<name>.apk（已合并的 fat APK；XAPK 项目必须用它，
       否则 fallback 到外层 .xapk 会让 ASBuilder fake「APK 无 dex」并破坏骨架）
    3. 否则从 REPO/apks 按 name 归一匹配(去版本/源码后缀)
    返回 None 表示无法解析。
    """
    from pathlib import Path
    apk = Path(apk_env) if apk_env and Path(apk_env).exists() else None
    if apk is None:
        # 优先 fat APK（crackings/<type>/<name>/raw/<name>.apk）
        if REPO.joinpath("crackings").is_dir():
            for proj in sorted(REPO.joinpath("crackings").glob(f"*/{name}/raw/{name}.apk")):
                if proj.is_file():
                    apk = proj
                    break
    if apk is None:
        apks_dir = REPO / "apks"
        if apks_dir.exists():
            for c in list(apks_dir.glob("*.apk")) + list(apks_dir.glob("*.xapk")):
                pure = "".join(ch for ch in c.stem if ch.isalnum())
                if name.lower() in pure.lower():
                    apk = c
                    break
    return apk


def _find_register() -> "Path | None":
    """定位当前 type skill 的 sub-stage-register.yaml。

    从 REPO/skills/strategy/<type>-strategy-skill/stages/sub-stage-register.yaml 找。
    REPO 下可能有多个 type skill,取第一个包含该 register 的。
    """
    from pathlib import Path
    for skill_dir in sorted((REPO / "skills/strategy").glob("*-strategy-skill")):
        reg = skill_dir / "stages" / "sub-stage-register.yaml"
        if reg.exists():
            return reg
    return None


_REGISTER_CACHE: dict | None = None


def _load_register() -> dict:
    """加载 sub-stage-register.yaml(带缓存)。"""
    global _REGISTER_CACHE
    if _REGISTER_CACHE is not None:
        return _REGISTER_CACHE
    import yaml
    reg = _find_register()
    if reg is None:
        _REGISTER_CACHE = {"sub_stages": []}
        return _REGISTER_CACHE
    data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
    _REGISTER_CACHE = data
    return data


def stage_path(stage_name: str) -> str:
    """从 sub-stage-register.yaml 查 name 的 id,返回产物目录名 `{id}-{name}`。

    例: stage_path("sdk-network-removal") → "03-sdk-network-removal"(register 里 id=03)。
    产物目录(如 crackings/<type>/<name>/stages/03-sdk-network-removal)统一用此拼接,
    避免 step 里硬编码编号 —— register 的 id/name 是产物目录的唯一规范来源。
    """
    data = _load_register()
    for s in data.get("sub_stages", []):
        if s.get("name") == stage_name:
            return f"{s.get('id')}-{stage_name}"
    return stage_name  # 未找到则原样返回