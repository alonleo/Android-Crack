#!/usr/bin/env python3
"""
generate-hanization-translations.py — 用「通用游戏关键字→中文」字典生成汉化译文表。

[方案A metadata 静态替换] 文本汉化子阶段的前置生成器：
  1. 读共享字典 skills/common/scripts/hanization-common-keywords.yaml（objects + type_extra）
  2. 读 stringliteral.json（crackings/<type>/<Name>/stages/11-text-hanization/step1-stringliterals/）
  3. 按每条规则的 match(exact|contains) 对字符串字面量做「大小写不敏感」匹配，
     命中且不在引擎/.NET 排除集内 → 产出 [{index, value}] 译文
  4. 写 cracks 阶段目录 translations.json（与 step-load-translations.py 约定格式一致）

安全护栏：
  - index 永远不改；value 换成中文
  - 占位符 %s / %d / {0} / <color> 保留（透传）
  - 引擎/.NET 样板串排除（Unity/System/Il2Cpp/photon/Http 等）
  - 同一 index 多规则命中时：exact 优先于 contains，靠前规则优先
  - --dry-run 只预览不写盘

用法（NAME/TYPE 走环境变量，与 sub_stage-dispatcher 一致）：
  source tools/environments/env.sh
  python3 skills/common/scripts/generate-hanization-translations.py \
      --name <Name> --type <type> [--dict <yaml元路径>] [--out <相对REPO路径>] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    print("[ERROR] 需要 pyyaml：pip install -i https://pypi.tuna.tsinghua.edu.cn/simple pyyaml", file=sys.stderr)
    sys.exit(1)

REPO = Path(__file__).resolve().parents[3]
DEFAULT_DICT = REPO / "skills" / "common" / "scripts" / "hanization-common-keywords.yaml"

# 引擎 / .NET / 网络 样板串排除（命中即不翻，避免破坏运行期行为）
EXCLUDE = re.compile(
    r"(Exception|Error|Invalid|namespace|System\.|UnityEngine|Il2Cpp|\.dll|\.cs\b|"
    r"Photon|RPC|Http|WebSocket|Socket|ServicesCore|Content-|Header|Xml|Json|"
    r"Serialize|Deserialize|Marshal|Reflection|Assembly|Thread|Task|Process\b|"
    r"NotSupported|not supported|Sys\.|Libc|Glob|Windows|registry|Unicode|"
    r"RFC|DNS|Auth|Token|base64|collection|enumerable|attribute|XmlSchema|"
    r"StatusCode|Proxy|Certificate|encrypt|decrypt|SHA|MD5|var\b|int\b|float\b|"
    r"\bvoid\b|UnityLimited|unity-|UIR\.|UIElements|@{2,}|<b>|</color>|\\u|\\x00)"
    , re.I)


def load_dict(dict_path: Path, type_: str) -> list[dict]:
    """对象：objects[] 全量 + type_extra[type_] 追加；每条带 match 默认 exact。"""
    data = yaml.safe_load(dict_path.read_text(encoding="utf-8"))
    entries = []
    for e in data.get("objects", []):
        entries.append({"en": e["en"], "zh": e["zh"], "match": e.get("match", "exact")})
    extra = (data.get("type_extra") or {}).get(type_) or []
    for e in extra:
        entries.append({"en": e["en"], "zh": e["zh"], "match": e.get("match", "exact")})
    return entries


def match_string(value: str, en: str, mode: str) -> bool:
    v = value.lower()
    k = en.lower()
    if mode == "contains":
        return k in v
    # exact：整串相等（去掉首尾空白后）
    return v.strip() == k.strip()


def _remove_substr(lower_value: str, lower_key: str) -> str:
    """从(已小写)value 中移除第一处 key 子串，返回剩余（用于 contains 安全护栏）。"""
    idx = lower_value.find(lower_key)
    if idx < 0:
        return lower_value
    return lower_value[:idx] + lower_value[idx + len(lower_key):]


def build_translations(
    literals: list[dict], entries: list[dict]
) -> tuple[list[dict], int, list[str]]:
    """返回 (translations, 命中num, 警告)。exact 优先于 contains，逐条首次命中即定。"""
    # 预分组：exact 规则优先
    exacts = [e for e in entries if e["match"] == "exact"]
    contains = [e for e in entries if e["match"] == "contains"]
    trans: list[dict] = []
    hit = 0
    warns: list[str] = []
    for i, item in enumerate(literals):
        v = item.get("value", "")
        if not v or not v.strip():
            continue
        if EXCLUDE.search(v):
            continue
        chosen = None
        for e in exacts:
            if match_string(v, e["en"], "exact"):
                chosen = e
                break
        if chosen is None:
            for e in contains:
                if not match_string(v, e["en"], "contains"):
                    continue
                # contains 安全护栏：整串可翻译仅当去掉关键字后剩余只是空白/标点，
                # 否则会破坏带上下文的串（如 "ALL CHICKEN LEVEL 20 COUNT:"）。
                remainder = _remove_substr(v.lower(), e["en"].lower())
                if remainder.strip() and any(ch.isalnum() or ch in "%{}<>" for ch in remainder):
                    continue  # 有实质内容 → 不整串覆盖
                chosen = e
                break
        if chosen is None:
            continue
        trans.append({"index": item.get("index", i), "value": chosen["zh"]})
        hit += 1
    return trans, hit, warns


def main() -> int:
    ap = argparse.ArgumentParser(description="用关键字字典生成汉化译文表")
    ap.add_argument("--name", default=os.environ.get("NAME", "").strip())
    ap.add_argument("--type", default=os.environ.get("TYPE", "android").strip())
    ap.add_argument("--dict", default=str(DEFAULT_DICT))
    ap.add_argument("--out", default="")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    if not args.name:
        print("[ERROR] 缺 --name（或用环境变量 NAME）", file=sys.stderr)
        return 1

    stage_dir = REPO / "crackings" / args.type / args.name / "stages"
    # 兼容 11-text-hanization 与 15-text-hanization（register id 历史差异）
    sl_cands = [
        stage_dir / "11-text-hanization" / "step1-stringliterals" / "stringliteral.json",
        stage_dir / "15-text-hanization" / "step1-stringliterals" / "stringliteral.json",
        stage_dir / "11-text-hanization" / "stringliterals" / "stringliteral.json",
    ]
    sl_path = next((p for p in sl_cands if p.exists()), None)
    if sl_path is None:
        print(f"[ERROR] 未找到 stringliteral.json: {stage_dir}/{'{13,15}?-text-hanization'}", file=sys.stderr)
        return 1

    dict_path = Path(args.dict)
    if not dict_path.exists():
        print(f"[ERROR] 字典不存在: {dict_path}", file=sys.stderr)
        return 1

    literals = json.loads(sl_path.read_text(encoding="utf-8"))
    entries = load_dict(dict_path, args.type)
    trans, hit, warns = build_translations(literals, entries)

    for w in warns[:10]:
        print(f"[WARN] {w}")
    print(f"[INFO] {args.type}/{args.name}: stringcount={len(literals)} 匹配命中={hit}")

    if args.dry_run:
        for t in trans[:60]:
            print(f"    idx={t['index']}  ->  {t['value']}")
        print(f"[DRY-RUN] 共 {len(trans)} 条译文（未写盘）")
        return 0

    # 默认落到汉化子阶段目录（12/15-text-hanization）translations.json（load-translations 读取）
    stage_dir = sl_path.parent.parent  # .../stages/<text-hanization>/
    trans_out = REPO / args.out if args.out else (stage_dir / "translations.json")
    trans_out.parent.mkdir(parents=True, exist_ok=True)
    trans_out.write_text(json.dumps(trans, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] 已写入 {trans_out.relative_to(REPO)}  (共 {len(trans)} 条译文)")
    print("[HINT] 下一步跑 load-translations → patch-metadata → smali-to-jar → gradle-build")
    return 0


if __name__ == "__main__":
    sys.exit(main())