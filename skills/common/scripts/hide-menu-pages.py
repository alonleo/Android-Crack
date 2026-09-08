#!/usr/bin/env python3
"""
hide-menu-pages.py — 静态隐藏 Unity NGUI UI 元素（MenuPage tab / GameObject 按钮）。

背景: Alto's Adventure (il2cpp) 暂停菜单的 tab 由 MenuPage MonoBehaviour 组成。
GuiPauseMenu.Initialise() 运行时收集全部 MenuPage 并按 showOnPlatform 过滤。
把目标 MenuPage 的 showOnPlatform 改为 0（不适用于任何平台）后，
GuipauseMenu 会在收集时跳过它们 → tab 消失。

用法:
  python3 hide-menu-pages.py <data.unity3d> <out.unity3d> \
      --hide "<title1>,<title2>" \
      --hide-go "<path_id1>,<path_id2>" \
      --hide-langs "<keep_idx1>,<keep_idx2>" \
      [--list-pages] \
      [--packer lz4|none]

说明:
  - --list-pages: 只列出所有 MenuPage 的 pageTitle + showOnPlatform，不修改
  - --hide: 逗号分隔的 MenuPage pageTitle（如 "Game Center,Credits"）
  - --hide-go: 逗号分隔的 GameObject path_id（m_IsActive=False，隐藏按钮+子布局，
    用于设置页按钮 / UITable 布局的普通按钮；NGUI UITable 自动跳过 inactive 子项重排）
  - --hide-langs: 语言按钮保留索引（逗号分隔，如 0,6,7 = English/简中/繁中）。
    ⚠️ 语言按钮必须用此方案（裁剪 GuiLanguageSelect.buttonList 数组），
    不能 --hide-go —— GenerateButtons() 运行时动态生成按钮，隐藏模板会被覆盖
  - 输出经 UnityPy 重打包（默认 lz4 压缩，体积更小）

依赖: UnityPy (pip install UnityPy)

案例（Alto's Adventure 2026-08-04）:
  # 移除暂停菜单 tab（Game Center/谷歌应用商店 + Credits/鸣谢）
  --hide "Game Center,Credits"
  # 隐藏设置页按钮（Privacy + More Games，path_id 来自 GameObject 分析）
  --hide-go "2476,2409"
  # 语言 Tab 只保留 English(0) + 简中(6) + 繁中(7)
  --hide-langs "0,6,7"
"""
from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path

import UnityPy

# MenuPage MonoBehaviour 序列化偏移（由 dump.cs 字段偏移 + Unity 序列化推导）
# offset 0x20 = showOnPlatform (int32, Platform flags)
SHOW_ON_PLATFORM_OFFSET = 0x20
# MenuPage MonoScript class 名
MENUPAGE_SCRIPT = "MenuPage"


def list_pages(env, script_map: dict) -> dict:
    """扫描所有引用 MenuPage 脚本的 MonoBehaviour，返回 path_id -> {title, show}"""
    pages = {}
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        try:
            raw = bytes(obj.get_raw_data())
            if len(raw) < 0x40:
                continue
            # m_Script pathID 在 offset 0x14（0x10=fileID, 0x14=pathID）
            spid = struct.unpack_from('<i', raw, 0x14)[0]
            if script_map.get(spid) != MENUPAGE_SCRIPT:
                continue
            show = struct.unpack_from('<i', raw, SHOW_ON_PLATFORM_OFFSET)[0]
            # pageTitle 字符串: 从 0x2c 读取长度，可能因对齐偏移
            # 用 ASCII/UTF-8 扫描 pageTitle
            title = _extract_title(raw)
            pages[obj.path_id] = {"title": title, "showOnPlatform": show}
        except Exception:
            continue
    return pages


def _extract_title(raw: bytes) -> str:
    """从 MenuPage raw 提取 pageTitle 字符串。"""
    # pageTitle 序列化在 showOnPlatform(0x20) + 3 bools(0x24) 之后，
    # 即约 offset 0x28 开始是 string: len(int32) + bytes
    for off in (0x28, 0x2c, 0x30):
        try:
            l = struct.unpack_from('<i', raw, off)[0]
            if 2 <= l <= 64:
                s = raw[off+4:off+4+l].decode('utf-8', 'replace')
                if s and s[0].isalpha():
                    return s
        except Exception:
            break
    return "<unknown>"


def build_script_map(env) -> dict:
    """构建 MonoScript path_id -> class name 映射。"""
    smap = {}
    for obj in env.objects:
        if obj.type.name != "MonoScript":
            continue
        try:
            raw = bytes(obj.get_raw_data())
            # MonoScript: m_ClassName 字符串在 offset 0
            l = struct.unpack_from('<i', raw, 0)[0]
            if 1 <= l <= 128:
                name = raw[4:4+l].decode('utf-8', 'replace')
                smap[obj.path_id] = name
        except Exception:
            continue
    return smap



# === 追加: GameObject 隐藏功能 ===
def hide_gameobjects(env, go_ids, labels):
    """把指定 GameObject 的 m_IsActive 设为 False（隐藏按钮及子对象）。"""
    hidden = 0
    for obj in env.objects:
        if obj.type.name == "GameObject" and obj.path_id in go_ids:
            tree = obj.read_typetree()
            old = tree['m_IsActive']
            tree['m_IsActive'] = False
            obj.save_typetree(tree)
            print(f"  [HIDE-GO] '{tree['m_Name']}' ({obj.path_id}) m_IsActive {old} → False")
            hidden += 1
    return hidden


def crop_language_buttons(env, keep_indices, script_map):
    """裁剪 GuiLanguageSelect 的 buttonList 数组（保留指定索引）。

    ⚠️ [FLOWFIX] 语言按钮不能靠隐藏 GameObject：
    `GuiLanguageSelect.GenerateButtons()` 运行时用 `buttonList`(ChangeLanguage[] 数组)
    动态实例化按钮，隐藏场景模板对象会被重新生成覆盖。
    正确方案：修改 buttonList 数组 count + 元素，让 GenerateButtons 只生成保留的语言。

    序列化布局（GuiLanguageSelect MonoBehaviour）:
      count @0x44, 元素 @0x48 起每个 12 字节 (fileID + pathID + extra)
    """
    modified = 0
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        raw = bytearray(obj.get_raw_data())
        if len(raw) < 0x4c:
            continue
        # 只处理 GuiLanguageSelect 脚本（script_map pathID → "GuiLanguageSelect"）
        spid = struct.unpack_from('<i', raw, 0x14)[0]
        if script_map.get(spid) != "GuiLanguageSelect":
            continue
        count = struct.unpack_from('<i', raw, 0x44)[0]
        if not (1 <= count <= 64):
            continue
        # 读取保留元素
        elems = []
        for idx in keep_indices:
            off = 0x48 + idx * 12
            if off + 12 > len(raw):
                continue
            elems.append(bytes(raw[off:off + 12]))
        if not elems:
            continue
        struct.pack_into('<i', raw, 0x44, len(elems))
        for i, e in enumerate(elems):
            raw[0x48 + i * 12:0x48 + i * 12 + 12] = e
        for i in range(len(elems), max(count, len(elems))):
            off = 0x48 + i * 12
            if off + 12 <= len(raw):
                raw[off:off + 12] = b'\x00' * 12
        obj.set_raw_data(bytes(raw))
        print(f"  [LANG] GuiLanguageSelect({obj.path_id}) buttonList count {count} → {len(elems)}（保留索引 {keep_indices}）")
        modified += 1
    return modified


def main() -> int:
    parser = argparse.ArgumentParser(description="隐藏 Unity MenuPage tab / GameObject")
    parser.add_argument("input", help="源 data.unity3d")
    parser.add_argument("output", help="输出 data.unity3d")
    parser.add_argument("--hide", default="", help="逗号分隔的 pageTitle 列表（MenuPage tab）")
    parser.add_argument("--hide-go", default="", help="逗号分隔的 GameObject path_id（隐藏按钮+布局）")
    parser.add_argument("--hide-langs", default="", help="语言按钮保留索引（逗号分隔，如 0,6,7 = English/简中/繁中）")
    parser.add_argument("--list-pages", action="store_true", help="仅列出页面")
    parser.add_argument("--packer", default="lz4", choices=["lz4", "none"])
    args = parser.parse_args()

    env = UnityPy.load(args.input)
    smap = build_script_map(env)
    pages = list_pages(env, smap)

    print(f"=== MenuPage 列表 ({len(pages)} 个) ===")
    for pid, info in sorted(pages.items()):
        print(f"  path_id={pid}: '{info['title']}' showOnPlatform={info['showOnPlatform']} (0x{info['showOnPlatform'] & 0xffffffff:x})")

    if args.list_pages:
        return 0

    modified = 0
    hide = [t.strip() for t in args.hide.split(",") if t.strip()]
    if hide:
        for pid, info in pages.items():
            if info["title"] in hide:
                for obj in env.objects:
                    if obj.path_id == pid:
                        raw = bytearray(obj.get_raw_data())
                        old = struct.unpack_from('<i', raw, SHOW_ON_PLATFORM_OFFSET)[0]
                        struct.pack_into('<i', raw, SHOW_ON_PLATFORM_OFFSET, 0)
                        obj.set_raw_data(bytes(raw))
                        print(f"  [MODIFIED] '{info['title']}' showOnPlatform {old} → 0")
                        modified += 1
                        break

    hide_go = [int(t.strip()) for t in args.hide_go.split(",") if t.strip()]
    if hide_go:
        modified += hide_gameobjects(env, set(hide_go), hide_go)

    hide_langs = [int(t.strip()) for t in args.hide_langs.split(",") if t.strip()]
    if hide_langs:
        modified += crop_language_buttons(env, hide_langs, smap)

    if modified == 0:
        print(f"[WARN] 没有匹配要隐藏的页面: hide={hide} hide_go={hide_go} hide_langs={hide_langs}")
        return 1

    for fitem in env.files.values():
        fitem.is_changed = True
    outdir = Path(args.output).parent
    outdir.mkdir(parents=True, exist_ok=True)
    for fname, fitem in env.files.items():
        data = fitem.save(packer=args.packer)
        Path(args.output).write_bytes(data)
        print(f"[OK] 已输出 {args.output} ({len(data)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
