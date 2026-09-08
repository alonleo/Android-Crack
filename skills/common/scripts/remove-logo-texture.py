#!/usr/bin/env python3
"""remove-logo-texture.py — 移除 Unity 游戏的 Logo/游戏名纹理。

背景: Unity il2cpp 游戏的主菜单游戏名标题通常是一张 Texture2D（如 "logo"）。
将目标纹理内容替换为全透明，即可在场景中隐藏标题（无需 native hook，ARM32 兼容）。

用法:
  python3 remove-logo-texture.py <data.unity3d> <texture_name> [-o <out>]
  # texture_name 匹配 Texture2D 的 m_Name（如 "logo"）

原理:
  - UnityPy 加载 data.unity3d
  - 匹配 m_Name == texture_name 的 Texture2D（通常 1 个）
  - 把 image 替换为全透明 RGBA
  - 用 env.file.save() 写回（沿用原压缩格式 m_TextureFormat）

参考: replace-game-font.py 的保存方式（save_typetree + set_raw_data + env.file.save）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import UnityPy


def remove_texture(src: str, name: str, out: str | None = None) -> int:
    env = UnityPy.load(src)
    target = out or src

    removed = 0
    for obj in env.objects:
        if obj.type.name != 'Texture2D':
            continue
        try:
            tree = obj.read_typetree()
            if tree.get('m_Name') != name:
                continue
            t = obj.read()
            img = t.image
            if img is None:
                print(f"[SKIP] {name} (path_id={obj.path_id}) 无 image 数据")
                continue
            # 全透明替换
            transparent = img.convert('RGBA')
            px = transparent.load()
            w, h = transparent.size
            for y in range(h):
                for x in range(w):
                    px[x, y] = (0, 0, 0, 0)
            t.image = transparent  # image setter 编码回原 m_TextureFormat
            raw = obj.save_typetree(obj.read_typetree())
            if not raw:
                print(f"[WARN] {name} save_typetree 空")
                continue
            obj.set_raw_data(raw)
            removed += 1
            print(f"[OK] {name} (path_id={obj.path_id}, {w}x{h}) → 全透明")
        except Exception as e:
            print(f"[ERR] path_id={obj.path_id}: {e}")

    if removed == 0:
        print(f"[ERROR] 未找到名为 {name!r} 的 Texture2D")
        return 1

    data = env.file.save()
    with open(target, 'wb') as fh:
        fh.write(data)
    print(f"[OK] 已保存 → {target}（{len(data)} bytes）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="data.unity3d 路径")
    ap.add_argument("name", help="Texture2D m_Name（如 logo）")
    ap.add_argument("-o", "--out", default=None, help="输出路径（默认覆盖）")
    args = ap.parse_args()
    return remove_texture(args.input, args.name, args.out)


if __name__ == "__main__":
    sys.exit(main())
