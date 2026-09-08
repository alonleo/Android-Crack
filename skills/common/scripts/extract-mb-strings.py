#!/usr/bin/env python3
"""extract-mb-strings.py — 提取 data.unity3d 中所有 MonoBehaviour 字符串。

游戏 UI 文本通常在 MonoBehaviour 的 m_Text 字段（Unity 标准 Text/TMP 组件），
以及 GameObject.name 等序列化字段。本脚本扫描所有 MB 对象的 string 字段，
输出 {"English": freq} 形式供 translations.json 填充。

背景：HighwayBikeAttackRaceGame (Unity 6.0 il2cpp, 2026-08-09) 验证。
配合 assets-tools-haniz/HanizTool 写入（变长安全，AssetsReplacerFromMemory）。

用法:
  python3 extract-mb-strings.py <data.unity3d> [-o translations_seed.json] [--min-len 2] [--max-len 80]

依赖: pip install UnityPy (项目环境提供)
"""
from __future__ import annotations

import argparse
import json
import struct
import sys
from collections import Counter

import UnityPy


def extract_mb_strings(bundle_path: str) -> Counter:
    """扫描所有 MonoBehaviour 的 string 字段，返回频次 Counter。"""
    counter: Counter = Counter()
    env = UnityPy.load(bundle_path)
    f = env.file
    if not hasattr(f, 'files'):
        print("[ERROR] 不是 BundleFile（仅支持 Unity 序列化 bundle 容器）", file=sys.stderr)
        return counter

    total_objs = 0
    mb_objs = 0
    for scene_name, sf in f.files.items():
        if not hasattr(sf, 'objects'):
            continue
        for obj in sf.objects.values():
            total_objs += 1
            if obj.type.name != 'MonoBehaviour':
                continue
            mb_objs += 1
            try:
                raw = obj.get_raw_data()
            except Exception:
                continue
            i = 0
            while i < len(raw) - 4:
                ln = struct.unpack_from('<i', raw, i)[0]
                if 0 < ln <= 200 and i + 4 + ln <= len(raw):
                    data = raw[i+4:i+4+ln]
                    try:
                        s = data.decode('utf-8')
                        # 过滤：仅可打印 ASCII（英文/标点/数字），跳过中文（已汉化）
                        if s and s.isprintable() and all(32 <= ord(c) < 127 for c in s):
                            counter[s] += 1
                            i += 4 + ln
                            continue
                    except Exception:
                        pass
                i += 1

    print(f"[INFO] {bundle_path}: {total_objs} 对象 / {mb_objs} MonoBehaviour", file=sys.stderr)
    return counter


def filter_strings(counter: Counter, min_len: int, max_len: int, top_n: int) -> list[tuple[str, int]]:
    """过滤 + 排序（按频次降序）。"""
    filtered = [
        (s, c) for s, c in counter.items()
        if min_len <= len(s) <= max_len
        # 过滤噪声：纯数字 / 纯符号 / 全大写短 token / 路径式字符串
        and any(c.isalpha() for c in s)
        and any(c.islower() for c in s)  # 至少一个小写字母（避开 URL/HASH）
        and not s.startswith(('http://', 'https://', 'www.', '/', './', 'm_'))
    ]
    filtered.sort(key=lambda x: (-x[1], x[0]))
    return filtered[:top_n]


def main() -> int:
    parser = argparse.ArgumentParser(description="提取 data.unity3d MonoBehaviour 字符串")
    parser.add_argument("bundle", help="data.unity3d 路径")
    parser.add_argument("-o", "--output", default=None,
                        help="输出 JSON 路径（默认: translations_seed.json = {en: freq}）")
    parser.add_argument("--min-len", type=int, default=2, help="最小字符串长度")
    parser.add_argument("--max-len", type=int, default=60, help="最大字符串长度")
    parser.add_argument("--top-n", type=int, default=500, help="保留 Top-N 高频字符串")
    args = parser.parse_args()

    counter = extract_mb_strings(args.bundle)
    if not counter:
        return 1
    filtered = filter_strings(counter, args.min_len, args.max_len, args.top_n)

    # 输出 seed: {en: freq} 或 {en: ""} 模板形式
    out_path = args.output or "translations_seed.json"
    seed = {s: c for s, c in filtered}
    with open(out_path, "w", encoding="utf-8") as fp:
        json.dump(seed, fp, ensure_ascii=False, indent=2, sort_keys=True)
    print(f"[OK] 提取 {len(filtered)} 字符串 → {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())