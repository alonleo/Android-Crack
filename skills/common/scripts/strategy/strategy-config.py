#!/usr/bin/env python3
"""
strategy-config.py — 策略路由三层架构 API

═══════════════════════════════════════════════════════════════════════════
三层架构：

  Layer 1  sniff_routing      APK 文件列表 → type          (策略路由表)
  Layer 2  stage_routing      type → [stage_ids]           (策略阶段路由表)
  Layer 3  stage_details      stage_id → {script, function, role, mode, outputs}
                              (子阶段详情表)
  meta     metadata           tools + notes + legacy_stage_map (元数据)

Python API：
    detect_type(apk_path)                                      → Layer 1
    get_sniff_order() / get_sniff_patterns(type)               → Layer 1
    get_stage_routing(type) / get_mandatory_stages(type)       → Layer 2
    get_stage_detail(type, stage_id) / list_stage_details(type) → Layer 3
    get_tools(type) / get_notes(type) / resolve_legacy_stage() → metadata

CLI:
    list                                 列出所有 type
    detect <apk>                         Layer 1: 嗅探 APK
    sniff-order                          Layer 1: 嗅探优先级
    sniff-routing [<type>]               Layer 1: 嗅探模式
    stages <type>                        Layer 2: 阶段列表（兼容）
    mandatory <type>                     Layer 2: 强制阶段
    stage-routing <type>                 Layer 2: 阶段路由详情
    stage-detail <type> <stage_id>      Layer 3: 子阶段详情
    stage-details <type>                 Layer 3: 全部子阶段详情
    tools <type>                         metadata: 工具链
    notes <type>                         metadata: 备注
    resolve-legacy <type> <legacy_id>   metadata: 旧编号映射

═══════════════════════════════════════════════════════════════════════════
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from typing import Any, Dict, List, Optional

import yaml

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "strategy-config.yaml")

# ═══════════════════════════════════════════════════════════════════════════
# 配置加载（带缓存）
# ═══════════════════════════════════════════════════════════════════════════

_CONFIG_CACHE: Optional[Dict[str, Any]] = None


def load_config() -> Dict[str, Any]:
    """加载 strategy-config.yaml（带缓存）。"""
    global _CONFIG_CACHE
    if _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        _CONFIG_CACHE = yaml.safe_load(f)
    return _CONFIG_CACHE


def reset_cache() -> None:
    """重置缓存（用于测试）。"""
    global _CONFIG_CACHE
    _CONFIG_CACHE = None


# ═══════════════════════════════════════════════════════════════════════════
# Layer 1: 策略路由表（APK → type）
# ═══════════════════════════════════════════════════════════════════════════

def get_sniff_order() -> List[str]:
    """返回嗅探优先级（首胜顺序）。"""
    return list(load_config().get("sniff_routing", {}).get("order", []))


def get_sniff_patterns(type_name: Optional[str] = None) -> Dict[str, List[str]] | List[str]:
    """返回嗅探模式。type_name=None 时返回 {type: [patterns]}；否则返回该 type 的 patterns。"""
    patterns = load_config().get("sniff_routing", {}).get("patterns", {})
    if type_name is None:
        return {k: list(v) for k, v in patterns.items()}
    return list(patterns.get(type_name, []))


def detect_type(apk_path: str) -> str:
    """嗅探 APK 返回类型名（Layer 1 主入口）。

    流程：unzip APK → 拼接文件列表 → 按 sniff_order 顺序匹配 → 首胜。
    支持 .xapk（自动递归提取内部 .apk）。
    未命中时 fallback 到 'android'。
    """
    if not os.path.isfile(apk_path):
        return "unknown"

    try:
        with zipfile.ZipFile(apk_path, "r") as z:
            namelist = z.namelist()
    except (zipfile.BadZipFile, OSError) as e:
        print(f"Error reading APK: {e}", file=sys.stderr)
        return "unknown"

    # .xapk 递归合并内部 .apk 文件列表
    if apk_path.endswith(".xapk"):
        try:
            with zipfile.ZipFile(apk_path, "r") as z:
                apk_files = [n for n in z.namelist() if n.endswith(".apk")]
                for apk_name in apk_files:
                    with z.open(apk_name) as apk_data:
                        with zipfile.ZipFile(apk_data, "r") as apk_zip:
                            namelist.extend(apk_zip.namelist())
        except (zipfile.BadZipFile, OSError) as e:
            print(f"Error reading .xapk: {e}", file=sys.stderr)

    text = "\n".join(namelist)
    config = load_config()
    patterns = config.get("sniff_routing", {}).get("patterns", {})

    for type_name in get_sniff_order():
        type_patterns = patterns.get(type_name, [])
        for pat in type_patterns:
            if re.search(pat, text):
                return type_name

    return "android"  # fallback


# 兼容旧 API
def sniff_apk(apk_path: str) -> str:
    """[兼容旧 API] 同 detect_type()。"""
    return detect_type(apk_path)


# ═══════════════════════════════════════════════════════════════════════════
# Layer 2: 策略阶段路由表（type → stage_ids）
# ═══════════════════════════════════════════════════════════════════════════

def get_stage_routing(type_name: str) -> List[str]:
    """返回该 type 的阶段 ID 列表（Layer 2 主入口）。"""
    routes = load_config().get("stage_routing", {})
    info = routes.get(type_name)
    if info:
        return list(info.get("stages", []))
    # fallback 到 android
    return list(routes.get("android", {}).get("stages", []))


def get_mandatory_stages(type_name: str) -> List[str]:
    """返回该 type 的强制阶段（不可跳过）。"""
    routes = load_config().get("stage_routing", {})
    info = routes.get(type_name)
    if info:
        return list(info.get("mandatory", []))
    return []


# 兼容旧 API
def stages(type_name: str) -> List[str]:
    """[兼容旧 API] 同 get_stage_routing()。"""
    return get_stage_routing(type_name)


def mandatory(type_name: str) -> List[str]:
    """[兼容旧 API] 同 get_mandatory_stages()。"""
    return get_mandatory_stages(type_name)


# ═══════════════════════════════════════════════════════════════════════════
# Layer 3: 子阶段详情表（stage_id → {script, function, role}）
# ═══════════════════════════════════════════════════════════════════════════

def get_stage_detail(type_name: str, stage_id: str) -> Dict[str, Any]:
    """返回 stage 的详情（Layer 3 主入口）。

    返回字段：
        script    — 脚本相对路径
        function  — 功能描述
        role      — 角色/验收标准
        mode      — automatic / interactive
        outputs   — 产物路径列表（可无）
    """
    details = load_config().get("stage_details", {})
    type_details = details.get(type_name, {})
    detail = type_details.get(stage_id)
    if detail:
        return dict(detail)
    # 缺失详情：返回通用兜底（仅 script 来自 stage_routing 推断）
    return {}


def list_stage_details(type_name: str) -> Dict[str, Dict[str, Any]]:
    """返回该 type 全部 stage 详情。"""
    details = load_config().get("stage_details", {})
    type_details = details.get(type_name, {})
    return {k: dict(v) for k, v in type_details.items()}


# ═══════════════════════════════════════════════════════════════════════════
# Metadata: 工具链 / 备注 / 旧编号映射
# ═══════════════════════════════════════════════════════════════════════════

def get_tools(type_name: str) -> Dict[str, str]:
    """返回该 type 的工具链描述。"""
    metadata = load_config().get("metadata", {})
    return dict(metadata.get("tools", {}).get(type_name, {}))


def get_notes(type_name: str) -> str:
    """返回该 type 的备注。"""
    metadata = load_config().get("metadata", {})
    return metadata.get("notes", {}).get(type_name, "")


def resolve_legacy_stage(type_name: str, legacy_id: str) -> str:
    """返回旧编号映射后的现代阶段 ID（无映射则原样返回）。"""
    metadata = load_config().get("metadata", {})
    legacy = metadata.get("legacy_stage_map", {}).get(type_name, {})
    return legacy.get(legacy_id, legacy_id)


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

def _print_json(obj: Any) -> None:
    print(json.dumps(obj, ensure_ascii=False, indent=2))


def main() -> int:
    config = load_config()
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cmd = sys.argv[1]

    # ── Layer 1: sniff_routing ──
    if cmd == "list":
        for name in get_sniff_order():
            pats = get_sniff_patterns(name)
            print(f"{name}\t{', '.join(pats)}")
        return 0

    elif cmd == "detect" and len(sys.argv) >= 3:
        print(detect_type(sys.argv[2]))
        return 0

    elif cmd == "sniff-order":
        print(" ".join(get_sniff_order()))
        return 0

    elif cmd == "sniff-routing":
        if len(sys.argv) >= 3:
            type_name = sys.argv[2]
            _print_json({type_name: get_sniff_patterns(type_name)})
        else:
            _print_json(get_sniff_patterns())
        return 0

    # ── Layer 2: stage_routing ──
    elif cmd == "stages" and len(sys.argv) >= 3:
        print(" ".join(get_stage_routing(sys.argv[2])))
        return 0

    elif cmd == "mandatory" and len(sys.argv) >= 3:
        print(" ".join(get_mandatory_stages(sys.argv[2])))
        return 0

    elif cmd == "stage-routing" and len(sys.argv) >= 3:
        type_name = sys.argv[2]
        _print_json({
            "stages": get_stage_routing(type_name),
            "mandatory": get_mandatory_stages(type_name),
        })
        return 0

    # ── Layer 3: stage_details ──
    elif cmd == "stage-detail" and len(sys.argv) >= 4:
        type_name = sys.argv[2]
        stage_id = sys.argv[3]
        detail = get_stage_detail(type_name, stage_id)
        if not detail:
            print(f"ERROR: 未找到 {type_name}/{stage_id} 的详情", file=sys.stderr)
            return 1
        _print_json(detail)
        return 0

    elif cmd == "stage-details" and len(sys.argv) >= 3:
        _print_json(list_stage_details(sys.argv[2]))
        return 0

    # ── metadata ──
    elif cmd == "tools" and len(sys.argv) >= 3:
        _print_json(get_tools(sys.argv[2]))
        return 0

    elif cmd == "notes" and len(sys.argv) >= 3:
        print(get_notes(sys.argv[2]))
        return 0

    elif cmd == "resolve-legacy" and len(sys.argv) >= 4:
        print(resolve_legacy_stage(sys.argv[2], sys.argv[3]))
        return 0

    # 用法
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())