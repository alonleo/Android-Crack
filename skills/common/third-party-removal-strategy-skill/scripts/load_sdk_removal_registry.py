#!/usr/bin/env python3
"""load-sdk-removal-registry.py — 加载第三方 SDK 移除清单。

[FLOWFIX 2026-08-18] 集中维护 third-party-sdk-removal-registry.yaml 之后，
3 个脚本（sub-stage-3rd-party-sdk-removal.py、patch-firebase-realme-fix.py、
sub-stage-as-build.py、sub-stage-extract-filtered-smali-jars.py）都从这里读清单，
不再硬编码 SDK 名字。

用法:
  from load_sdk_removal_registry import load_registry
  reg = load_registry()
  early_kill_sos = [item["name"] for item in reg["so_early_kill"]]
  # ...

返回结构 (dict)：
  {
    "schema_version": 1,
    "manifest_drop_exact": [{"name": "FirebaseInitProvider", "why": "..."}, ...],
    "manifest_drop_keyword_contains": [{"name": "vungle", "why": "..."}, ...],
    "so_early_kill": [{"name": "libcrashlytics.so", "why": "..."}, ...],
    "so_keyword_contains": ["applovin", "mbridge", ...],
    "raw_apk_drop_entries": ["lib/arm64-v8a/libcrashlytics.so", ...],
    "build_config_stubs": [{"class_path": "com/facebook/ads/BuildConfig.java", "package": "com.facebook.ads"}, ...],
    "smali_exclude_prefixes": ["androidx/compose", "com/google/firebase/crashlytics"],
    "meta_data_force_value": [{"name": "firebase_crashlytics_collection_enabled", "value": "false", "why": "..."}, ...],
    "engine_so_keep": ["libil2cpp.so", "libunity.so", ...],
  }

约定：
  - 找不到清单文件时 raise SystemExit（必须修复清单而不是静默回退到硬编码）
  - YAML 解析失败 raise SystemExit
  - 列表项是 dict 时 key 固定为 name/why/value/class_path/package
  - 列表项是 str 时（keyword_contains）直接用字符串本身
"""
from __future__ import annotations

import sys
from pathlib import Path

# 不引第三方 yaml 库（PyYAML 不可控）；手写最小子集解析（仅 key: 列表 / 列表项是 dict）
# 但手写太脆，改用项目自带的 lib/common.py 中的 ensure_yaml_reader()
# 这里直接尝试 PyYAML，失败就报错提示安装

try:
    import yaml  # type: ignore
except ImportError:
    print("[ERR] PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    raise SystemExit(1)

REPO = Path(__file__).resolve().parents[4]
# 清单集中在当前 skill 的 references/；各 type 共用，MD 为管理器生成的阅读视图。
# 本加载器只读 YAML，显式 registry_path 可指定项目副本。
DEFAULT_REGISTRY = (
    REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "references/third-party-sdk-removal-registry.yaml"
)


def load_registry(registry_path: Path | None = None) -> dict:
    p = Path(registry_path) if registry_path else DEFAULT_REGISTRY
    if not p.exists():
        print(f"[ERR] 第三方 SDK 移除清单不存在: {p}", file=sys.stderr)
        print("      不要回退到硬编码，先修复清单文件。", file=sys.stderr)
        raise SystemExit(1)
    with open(p, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not isinstance(data, dict):
        print(f"[ERR] 清单文件不是 dict: {p}", file=sys.stderr)
        raise SystemExit(1)
    # 验证 schema_version（PyYAML 把 "1" 解析成 int，所以用宽松比较）
    if str(data.get("schema_version")) != "1":
        print(f"[ERR] 清单文件 schema_version 不匹配 (期望 1，实际 {data.get('schema_version')})", file=sys.stderr)
        raise SystemExit(1)
    # 验证必填节
    required_keys = [
        "manifest_drop_exact", "manifest_drop_keyword_contains",
        "so_early_kill", "so_keyword_contains",
        "raw_apk_drop_entries", "build_config_stubs",
        "smali_exclude_prefixes", "meta_data_force_value",
        "engine_so_keep",
    ]
    missing = [k for k in required_keys if k not in data]
    if missing:
        print(f"[ERR] 清单文件缺节: {missing}", file=sys.stderr)
        raise SystemExit(1)
    return data


def names_only(items: list) -> list[str]:
    """把 [{"name": "x", "why": "..."}, ...] 拍扁为 ['x', ...]"""
    return [item["name"] for item in items if isinstance(item, dict) and "name" in item]


def class_path_pairs(items: list) -> list[tuple[str, str]]:
    """把 build_config_stubs 拍扁为 [(class_path, package), ...]"""
    return [
        (item["class_path"], item["package"])
        for item in items
        if isinstance(item, dict) and "class_path" in item and "package" in item
    ]


if __name__ == "__main__":
    # 简单自检：加载 + 打印
    reg = load_registry()
    print(f"[OK] 加载清单 schema_version={reg['schema_version']}")
    for k in ["manifest_drop_exact", "manifest_drop_keyword_contains", "so_early_kill",
              "so_keyword_contains", "raw_apk_drop_entries", "build_config_stubs",
              "smali_exclude_prefixes", "meta_data_force_value", "engine_so_keep"]:
        v = reg.get(k, [])
        if isinstance(v, list):
            print(f"  {k}: {len(v)} 项")
    print("done")
