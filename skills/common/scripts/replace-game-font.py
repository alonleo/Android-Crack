#!/usr/bin/env python3
"""replace-game-font.py — 替换 Unity 游戏内嵌字体（⚠️ 方案实测不可行，仅供记录/复用失败路径）。

背景: FlyingGorillaEndlessRunner (2026-08-02) 汉化后疑似豆腐块，尝试静态替换字体。
⚠️ **结论：静态替换 m_FontData 会崩溃（SIGTRAP/libunity.so 断言）**——
Unity 的 legacy Font 对象含 baked 字形数据（m_CharacterRects + m_Texture），
只换 m_FontData 会导致字形数据不一致。

✅ **正确做法（Unity 6）**：**不需要注入字体**。TextCore 动态字体自动 fallback 到
Android 系统 CJK 字体（NotoSansCJK），汉化中文正常显示。先 OCR/截图确认是否真豆腐块，
若现代 Unity 基本都自动 fallback，无需本脚本。

本脚本保留：
  - 记录"静态字体替换不可行"的失败路径
  - 若遇到老 Unity（无 TextCore fallback）确实豆腐块，且必须静态替换：
    需要同时重生成 m_CharacterRects + m_Texture（re-bake），本脚本不够（只换 m_FontData）。

用法（仅当确认需要且能处理 re-bake）:
  python3 replace-game-font.py <assets_file...> --font <中文字体.ttf>
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import UnityPy


def replace_font(assets_file: Path, font_bytes: bytes, name: str) -> int:
    env = UnityPy.load(str(assets_file))
    changed = 0
    for obj in env.objects:
        if obj.type.name != "Font":
            continue
        try:
            tree = obj.read_typetree()
            old_len = len(tree.get("m_FontData") or b"")
            tree["m_FontData"] = font_bytes
            raw = obj.save_typetree(tree)
            if not raw:
                print(f"  [WARN] save_typetree 空: {assets_file.name} Font path={obj.path_id}")
                continue
            obj.set_raw_data(raw)
            changed += 1
            print(f"  [OK] {assets_file.name} Font path={obj.path_id} "
                  f"m_FontData {old_len} → {len(font_bytes)} bytes")
        except Exception as e:
            print(f"  [ERR] {assets_file.name} Font path={obj.path_id}: {e}")
    if changed:
        with open(assets_file, "wb") as fh:
            fh.write(env.file.save())
        print(f"[OK] 已保存 {assets_file}（修改 {changed} 个 Font）")
    else:
        print(f"[WARN] {assets_file} 无 Font 对象，跳过")
    return changed


def main() -> int:
    ap = argparse.ArgumentParser(description="替换 Unity 游戏内嵌字体")
    ap.add_argument("assets", nargs="+", help=".assets 文件（可多个）")
    ap.add_argument("--font", required=True, help="中文字体路径（如 Alibaba.ttf）")
    args = ap.parse_args()

    font = Path(args.font)
    if not font.is_file():
        print(f"[ERROR] 字体不存在: {font}")
        return 1
    font_bytes = font.read_bytes()
    total = 0
    for a in args.assets:
        p = Path(a)
        if not p.is_file():
            print(f"[ERROR] 不存在: {p}")
            return 1
        total += replace_font(p, font_bytes, p.name)
    print(f"[DONE] 共修改 {total} 个 Font 对象")
    print("[INFO] 修改后重跑 gradle 编译（assets 打包进 APK）+ inject-smali-dex.py --force")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
