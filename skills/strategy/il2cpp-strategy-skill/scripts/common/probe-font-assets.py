#!/usr/bin/env python3
"""probe-font-assets.py — 探查 Unity data.unity3d 的字体资产（Font/TMP_FontAsset）。

用途：判断游戏 UI 汉字是否可显示（决定 09 font-replace 是否需要注入中文字体）。
逻辑：
  1. 扫描 data.unity3d 里 Font/TMP_FontAsset 类对象数量
  2. 读字体对象关键属性（dynamic / fallback / m_FontNames）
  3. 输出诊断

用法：
  python3 probe-font-assets.py <data.unity3d路径>

依赖：pip install UnityPy（中国大陆镜像见 AGENTS §1.8）
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import UnityPy


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    path = Path(sys.argv[1])
    if not path.is_file():
        print(f"[ERR] data.unity3d 不存在: {path}", file=sys.stderr)
        return 2

    env = UnityPy.load(str(path))
    font_types: Counter = Counter()
    for obj in list(env.objects):
        t = obj.type.name
        if "Font" in t:
            font_types[t] += 1
    print("Font 类对象:", dict(font_types) or "无")

    if not font_types:
        print("未发现 Font/TMP_FontAsset 对象（UI 可能走系统字体或 SDF 内置）")
        return 0

    n = 0
    for obj in list(env.objects):
        if "Font" not in obj.type.name:
            continue
        n += 1
        try:
            data = obj.read()
        except Exception as e:
            print(f"  [{obj.type.name}] read ERR: {str(e)[:80]}")
            continue
        d = {}
        for attr in ("m_FontData", "m_FontSize", "m_FontName", "m_Dynamic",
                     "m_IsDynamicEditable", "m_CharacterTable", "m_GlyphTable",
                     "m_FallbackFontAssets", "fallbackFontAssets", "m_CharacterInfo",
                     "m_LineHeight", "m_Name", "name", "m_Script"):
            if hasattr(data, attr):
                v = getattr(data, attr)
                d[attr] = f"{type(v).__name__}:{len(v) if hasattr(v, '__len__') else v}"
        if d:
            print(f"  [{obj.type.name}] {d}")
        if n >= 6:
            print("  ...(仅显示前 6 个)")
            break
    return 0


if __name__ == "__main__":
    sys.exit(main())