#!/usr/bin/env python3
"""Validated CRUD for the YAML checklist; every edit regenerates its Markdown.

Use --registry before the subcommand to work on a project/test copy.
add/update accept a YAML or JSON --data-file; stdout is always JSON.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tempfile

import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DEFAULT_REGISTRY = HERE.parent / "references/feature-removal-checklist.yaml"
sys.path.insert(0, str(ROOT / "skills/common/scripts/lib"))
import common

KINDS = {"feature": "F", "popup": "P", "language": "L", "verification": "V"}
FIELDS = {"id", "key", "kind", "name", "keywords", "types", "enabled", "strategy", "notes"}
STRATEGIES = {"review", "hook_container", "hook_method", "hide_node", "static_hide"}


class UniqueLoader(yaml.SafeLoader):
    pass


def _mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise ValueError(f"Invalid or duplicate YAML key: {key!r}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _mapping)


def parse_yaml(text):
    try:
        return yaml.load(text, Loader=UniqueLoader)
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML: {exc}") from exc


def known_types():
    return {p.name.removesuffix("-strategy-skill") for p in (ROOT / "skills/strategy").glob("*-strategy-skill") if p.is_dir()}


def validate_registry(data):
    if not isinstance(data, dict) or set(data) != {"schema_version", "items"}:
        raise ValueError("Expected schema_version and items only")
    if type(data["schema_version"]) is not int or data["schema_version"] != 1 or not isinstance(data["items"], list):
        raise ValueError("Unsupported schema or invalid items")
    ids, keys = set(), set()
    for item in data["items"]:
        if not isinstance(item, dict) or set(item) != FIELDS:
            raise ValueError(f"Each item requires fields: {sorted(FIELDS)}")
        for field in ("id", "key", "kind", "name", "strategy", "notes"):
            if not isinstance(item[field], str) or not item[field].strip():
                raise ValueError(f"Non-empty string required: {field}")
        prefix = KINDS.get(item["kind"])
        if not prefix or not re.fullmatch(prefix + r"\d{2,}", item["id"]):
            raise ValueError("ID prefix must match kind")
        if item["id"] in ids or item["key"] in keys or not re.fullmatch(r"[a-z][a-z0-9_]*", item["key"]):
            raise ValueError("Duplicate ID/key or invalid key")
        ids.add(item["id"])
        keys.add(item["key"])
        if type(item["enabled"]) is not bool or item["strategy"] not in STRATEGIES:
            raise ValueError("Invalid enabled/strategy")
        for field in ("keywords", "types"):
            values = item[field]
            if not isinstance(values, list) or any(not isinstance(v, str) or not v.strip() for v in values):
                raise ValueError(f"Expected string list: {field}")
            if len(values) != len(set(values)):
                raise ValueError(f"Duplicate values: {field}")
        if item["kind"] in ("feature", "popup") and not item["keywords"]:
            raise ValueError("Feature/popup keywords cannot be empty")
        if not item["types"] or not set(item["types"]) <= known_types() | {"*"}:
            raise ValueError("Unknown or missing engine type")
        if "*" in item["types"] and item["types"] != ["*"]:
            raise ValueError("Wildcard type must stand alone")
    return data


def load_registry(path=None):
    source = Path(path) if path else DEFAULT_REGISTRY
    return validate_registry(parse_yaml(source.read_text(encoding="utf-8-sig")))


def select_items(data, type_name=None, kind=None, enabled_only=False):
    validate_registry(data)
    if type_name and type_name not in known_types():
        raise ValueError(f"Unknown type: {type_name}")
    if kind and kind not in KINDS:
        raise ValueError(f"Unknown kind: {kind}")
    return [copy.deepcopy(item) for item in data["items"]
            if (not type_name or "*" in item["types"] or type_name in item["types"])
            and (not kind or item["kind"] == kind) and (not enabled_only or item["enabled"])]


def targets_for_type(data, type_name):
    return {i["key"]: {"id": i["id"], "keywords": i["keywords"], "strategy": i["strategy"],
                       "desc": i["name"], "notes": i["notes"], "requires_review": True}
            for i in select_items(data, type_name, enabled_only=True) if i["kind"] in ("feature", "popup")}


def load_snapshot(path=None, type_name=None):
    source = Path(path) if path else DEFAULT_REGISTRY
    raw = source.read_bytes()
    data = validate_registry(parse_yaml(raw.decode("utf-8-sig")))
    return {"registry_path": str(source.resolve()), "registry_sha256": hashlib.sha256(raw).hexdigest(),
            "schema_version": data["schema_version"], "items": select_items(data, type_name, enabled_only=True),
            "targets": targets_for_type(data, type_name) if type_name else {}}


def _cell(value):
    return str(value).replace("|", r"\|").replace("\r\n", "<br>").replace("\n", "<br>")


def render_markdown(data):
    validate_registry(data)
    lines = ["# 去功能点清单", "", "> 由同名 YAML 自动生成；通过 `manage-feature-checklist.py` 增删改查，禁止分别手改两份清单。", "",
             "YAML 是脚本唯一数据源。每项在项目 hide-plan.yaml / hide-report.yaml 中记录存在性、核心依赖、处理结果和验收证据，不向共享清单写项目状态。", "",
             "状态：待检查 / 不存在 / 保留（注明核心依赖）/ 已处理待验收 / 验收通过 / 阻塞。关键词命中只是候选，不是自动删除指令。", "",
             "核心关卡、HUD、设置、皮肤/角色/进度商店及必要回调须保留。处理非核心入口时同时检查节点、调用链和布局占位；不存在某项不能跳过 08/09 阶段。", "",
             "Frida 仅用于只读查询与侦察；持久修改必须进入工程和 APK，不能依赖 Frida 会话改变游戏状态。", ""]
    for kind, title in (("feature", "功能入口与界面元素"), ("popup", "弹窗"), ("language", "语言选择"), ("verification", "真机验收")):
        items = select_items(data, kind=kind)
        lines += [f"## {title}（{len(items)} 项）", "", "| 编号 | 功能点/检查项 | 关键词 | 适用 type | 启用 | 建议策略 | 检查要点 |", "|---|---|---|---|---|---|---|"]
        for item in items:
            cells = [item["id"], item["name"], " / ".join(item["keywords"]), ", ".join(item["types"]),
                     "是" if item["enabled"] else "否", item["strategy"], item["notes"]]
            lines.append("| " + " | ".join(_cell(c) for c in cells) + " |")
        lines.append("")
    lines += ["实现选择见 [引擎说明](engine-notes.md)，步骤与阻塞处理见 [阶段接口](stage-contract.md)。", "",
              "本清单仅涵盖去功能点与弹窗交互，不引入第三方 SDK 的组件删除、注册表或移除方案。", ""]
    return "\n".join(lines)


def _write_pair(path, data):
    # Prepare both files before replacing either; restore originals on failure.
    document = path.with_suffix(".md")
    outputs = {path: yaml.safe_dump(data, allow_unicode=True, sort_keys=False).encode("utf-8"),
               document: render_markdown(data).encode("utf-8")}
    originals = {p: p.read_bytes() if p.exists() else None for p in outputs}
    pending, replaced = {}, []
    try:
        for target, payload in outputs.items():
            with tempfile.NamedTemporaryFile(dir=target.parent, prefix=target.name + ".", suffix=".tmp", delete=False) as stream:
                stream.write(payload)
                pending[target] = Path(stream.name)
        for target, temporary in pending.items():
            os.replace(temporary, target)
            replaced.append(target)
    except BaseException:
        for target in replaced:
            if originals[target] is None:
                target.unlink(missing_ok=True)
            else:
                target.write_bytes(originals[target])
        raise
    finally:
        for temporary in pending.values():
            temporary.unlink(missing_ok=True)


def change_registry(path, operation, item_id=None, data=None):
    path = Path(path).resolve()
    lock = path.with_suffix(path.suffix + ".lock")
    try:
        handle = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        raise ValueError(f"Checklist is locked; another edit may be running: {lock}") from exc
    try:
        registry = load_registry(path)
        entries = registry["items"]
        index = next((n for n, item in enumerate(entries) if item["id"] == item_id), None)
        if operation == "add":
            if not isinstance(data, dict):
                raise ValueError("add requires an item mapping")
            entries.append(copy.deepcopy(data))
            result = entries[-1]
        elif operation in ("update", "delete"):
            if index is None:
                raise ValueError(f"Unknown ID: {item_id}")
            if operation == "update":
                if not isinstance(data, dict) or not data or "id" in data or not set(data) <= FIELDS:
                    raise ValueError("update requires known fields and cannot change ID")
                entries[index].update(copy.deepcopy(data))
                result = entries[index]
            else:
                result = entries.pop(index)
        elif operation == "sync-doc":
            result = {"markdown": str(path.with_suffix(".md"))}
        else:
            raise ValueError(f"Unknown operation: {operation}")
        validate_registry(registry)
        _write_pair(path, registry)
        return result
    finally:
        os.close(handle)
        lock.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    sub = parser.add_subparsers(dest="command", required=True)
    listing = sub.add_parser("list")
    listing.add_argument("--type", dest="type_name")
    listing.add_argument("--kind", choices=KINDS)
    listing.add_argument("--enabled-only", action="store_true")
    for command in ("get", "delete"):
        sub.add_parser(command).add_argument("id")
    adding = sub.add_parser("add")
    adding.add_argument("--data-file", type=Path, required=True)
    updating = sub.add_parser("update")
    updating.add_argument("id")
    updating.add_argument("--data-file", type=Path, required=True)
    sub.add_parser("validate")
    sub.add_parser("sync-doc")
    args = parser.parse_args()
    try:
        if args.command in ("list", "get", "validate"):
            registry = load_registry(args.registry)
            if args.command == "list":
                result = select_items(registry, args.type_name, args.kind, args.enabled_only)
            elif args.command == "get":
                result = next((i for i in registry["items"] if i["id"] == args.id), None)
                if result is None:
                    raise ValueError(f"Unknown ID: {args.id}")
            else:
                document = args.registry.with_suffix(".md")
                if not document.is_file() or document.read_text(encoding="utf-8") != render_markdown(registry):
                    raise ValueError("Markdown missing or stale; run sync-doc")
                result = {"valid": True, "items": len(registry["items"]), "markdown_synced": True}
        else:
            payload = parse_yaml(args.data_file.read_text(encoding="utf-8-sig")) if hasattr(args, "data_file") else None
            result = change_registry(args.registry, args.command, getattr(args, "id", None), payload)
            common.log_success(f"{args.command}: YAML and Markdown synchronized")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError) as exc:
        common.log_error(str(exc))
        return 1


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    common._REPO_ROOT = ROOT
    common.ensure_env()
    raise SystemExit(main())
