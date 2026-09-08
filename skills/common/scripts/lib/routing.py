"""子阶段路由表查询库。

替代 driver 脚本中的硬编码路径常量。
[FLOWFIX 2026-08-16] 子阶段体系重构：
  - 总子阶段路由表 skills/common/scripts/strategy/sub-stages.yaml = 通用信息唯一事实来源
    （id/name/name_zh/function/verify，无时间信息；含 major_stages 主阶段段）
  - 各策略 skill 的 stages/sub-stage-register.yaml = type 特有配置（script/outputs/notes 覆盖）
  - 主阶段（sniff/assess/final-check/cleanup）独立于子阶段排序（id M1/M2/M6/M7）

数据源：
  - skills/common/scripts/strategy/sub-stages.yaml            总路由表（通用信息）
  - skills/common/general-strategy-skill/stages/sub-stage-register.yaml 通用骨架（默认脚本路径 fallback）
  - skills/strategy/<type>-strategy-skill/stages/sub-stage-register.yaml  type-specific 覆盖

设计原则：
  - **name 为主键**：API 主要按英文 name（如 'sniff' / 'preprocess-build'）查询
  - id 转换：register 调度器接收 stage_id（'01'~'15'），用 id_to_name() 转 name 再查
  - 主阶段 name 查询自动路由到 major_stages 段

用法：
    from routing import get_script_path, get_helper_path, id_to_name, is_major_stage

    sniff = get_script_path("sniff")                              # 主阶段脚本
    fn    = get_script_path("preprocess-build", type_name="il2cpp")
    xapk  = get_helper_path("sub-stage-xapk-merge.py")
    name  = id_to_name("01")                                       # → 'static-analyze'
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[4]

# 总路由表（通用信息唯一事实来源）
MASTER_TABLE = "skills/common/scripts/strategy/sub-stages.yaml"


@lru_cache(maxsize=32)
def _load_table(yaml_rel: str) -> dict:
    """读 <yaml_rel> 路由表。返回 dict（{sub_stages: [...], major_stages: [...], helpers: [...]}）。"""
    p = ROOT / yaml_rel
    if not p.exists():
        return {"sub_stages": [], "major_stages": [], "helpers": []}
    try:
        data = yaml.safe_load(p.read_text()) or {}
    except Exception:
        return {"sub_stages": [], "major_stages": [], "helpers": []}
    for k in ("sub_stages", "major_stages", "helpers"):
        if k not in data:
            data[k] = []
    return data


def _master_table() -> dict:
    return _load_table(MASTER_TABLE)


def _common_table_path() -> str:
    return "skills/common/general-strategy-skill/stages/sub-stage-register.yaml"


def _type_table_path(type_name: str) -> str:
    """type 的路由表路径 —— 迁到 register。

    各 type skill 已迁移到 register 驱动: 子阶段路由表 = stages/sub-stage-register.yaml。
    """
    if not type_name:
        return _common_table_path()
    return f"skills/strategy/{type_name}-strategy-skill/stages/sub-stage-register.yaml"


@lru_cache(maxsize=1)
def _master_name_index() -> dict[str, dict]:
    """总路由表 name → entry（sub_stages + major_stages）。"""
    table = _master_table()
    idx: dict[str, dict] = {}
    for s in table.get("sub_stages", []):
        if s.get("name"):
            idx[s["name"]] = s
    for s in table.get("major_stages", []):
        if s.get("name"):
            idx[s["name"]] = s
    return idx


@lru_cache(maxsize=1)
def _master_id_index() -> dict[str, str]:
    """总路由表 id → name（子阶段 01-20 + 主阶段 M1/M2/M6/M7）。"""
    table = _master_table()
    idx: dict[str, str] = {}
    for s in table.get("sub_stages", []) + table.get("major_stages", []):
        if s.get("id"):
            idx[str(s["id"])] = s["name"]
    return idx


@lru_cache(maxsize=1)
def _common_name_index() -> dict[str, dict]:
    """common 表 name → entry（脚本路径 fallback）。"""
    table = _load_table(_common_table_path())
    return {s["name"]: s for s in table.get("sub_stages", []) if s.get("name")}


def id_to_name(stage_id: str) -> str:
    """把子阶段 ID（'01'~'20'）或主阶段 ID（M1/M2/M6/M7）转成 name。

    总路由表为唯一事实来源。若 ID 不在表内，原样返回。
    """
    return _master_id_index().get(str(stage_id), str(stage_id))


def is_major_stage(name: str) -> bool:
    """判断 name 是否为主阶段脚本（sniff/assess/final-check/cleanup）。"""
    entry = _master_name_index().get(name)
    if not entry:
        return False
    return str(entry.get("id", "")).startswith("M")


def get_script_path(name: str, type_name: str = "") -> Path | None:
    """按子阶段/主阶段 name 查脚本绝对路径。

    查找顺序：
      1) type-specific 表（若 type_name 非空），按 name 匹配 sub_stages
      2) common 默认表，按 name 匹配 sub_stages
      3) common 注册表 major_stages（主阶段脚本，按 name 匹配）

    返回：Path 绝对路径；若 name 不在路由表中，返回 None。
    """
    if not name:
        return None
    # 1) type-specific
    if type_name:
        table = _load_table(_type_table_path(type_name))
        for entry in table.get("sub_stages", []):
            if entry.get("name") == name and entry.get("script"):
                return ROOT / entry["script"]
    # 2) common fallback
    entry = _common_name_index().get(name)
    if entry and entry.get("script"):
        return ROOT / entry["script"]
    # 3) 主阶段脚本（common 表的 major_stages 段）
    common = _load_table(_common_table_path())
    for m in common.get("major_stages", []):
        if m.get("name") == name and m.get("script"):
            return ROOT / m["script"]
    return None


def get_script_path_by_id(stage_id: str, type_name: str = "") -> Path | None:
    """按子阶段 ID（'01'~'20'）或主阶段 ID（M1/M2/M6/M7）查脚本路径。"""
    name = id_to_name(stage_id)
    if name == stage_id:
        return None  # ID 不在总路由表
    return get_script_path(name, type_name=type_name)


def get_helper_path(helper_filename: str, type_name: str = "") -> Path | None:
    """查 helper 脚本路径（如 sub-stage-xapk-merge.py）。

    查 type-specific 的 helpers 列表（若提供 type_name），未命中则查 common。
    """
    if type_name:
        table = _load_table(_type_table_path(type_name))
        for h in table.get("helpers", []):
            if helper_filename in h.get("script", ""):
                return ROOT / h["script"]
    table = _load_table(_common_table_path())
    for h in table.get("helpers", []):
        if helper_filename in h.get("script", ""):
            return ROOT / h["script"]
    return None


def list_all_stages(type_name: str = "") -> list[dict]:
    """列出所有 sub-stage 元数据（按 ID 排序）。type-specific 优先于 common。"""
    tables = [_load_table(_type_table_path(type_name))] if type_name else []
    tables.append(_load_table(_common_table_path()))
    merged: dict[str, dict] = {}
    for t in tables:
        for s in t.get("sub_stages", []):
            sid = str(s.get("id", ""))
            if sid:
                merged[sid] = s
    return [merged[k] for k in sorted(merged.keys(), key=lambda x: (len(x), x))]


def list_major_stages() -> list[dict]:
    """列出主阶段脚本元数据（总路由表 major_stages）。"""
    return _master_table().get("major_stages", [])


def clear_cache() -> None:
    """清空 LRU 缓存（测试用）。"""
    _load_table.cache_clear()
    _master_name_index.cache_clear()
    _master_id_index.cache_clear()
    _common_name_index.cache_clear()
