#!/usr/bin/env python3
"""hanize-unity-texts.py — data.unity3d 场景 Text 组件静态汉化（不依赖 hook）。

背景: Unity il2cpp 游戏场景中 Text/TextMeshPro 组件的 m_Text 是英文。
用字节级补丁将 m_Text 字符串替换为中文（UnityPy set_raw_data + env.file.save()）。
本方案是"非 hook 汉化"，ARM32/ARM64 均适用，静态修改 data.unity3d。

原理:
  - 扫描 BundleFile 各场景（level0/1/2/3）所有 MonoBehaviour
  - 匹配 m_Text 字符串（int32 len + utf8）到翻译表
  - 用 set_raw_data 重写该 MB（支持变长，保存后生效）
  - env.file.save() 重打包

用法:
  python3 hanize-unity-texts.py <data.unity3d> <translations.json> [-o out] [--dry-run]

翻译表格式 (translations.json):
  {"Free Coins": "免费金币", "Cash Reward": "现金奖励", ...}
"""
from __future__ import annotations

import argparse
import json
import re
import struct
import sys

import UnityPy

# 翻译表键的精确匹配（避免误替换脚本名/按钮状态等）
# 需配合 find_text_strings 提取的真实 UI 文本


def find_text_strings(raw: bytes) -> list[tuple[int, bytes]]:
    """扫描 MB 数据中的 string（int32 len + utf8），返回 (offset, bytes) 列表。"""
    found = []
    i = 0
    while i < len(raw) - 4:
        ln = struct.unpack_from('<i', raw, i)[0]
        if 2 <= ln <= 60 and i + 4 + ln <= len(raw):
            data = raw[i+4:i+4+ln]
            # 可打印文本（ASCII 或 UTF-8）
            try:
                s = data.decode('utf-8')
                if all(32 <= ord(c) < 127 for c in s) and s.strip():
                    found.append((i+4, data))
                    i += 4 + ln
                    continue
            except Exception:
                pass
        i += 1
    return found


def hanize(input: str, translations: dict, out: str | None, dry_run: bool = False) -> int:
    env = UnityPy.load(input)
    f = env.file
    if not hasattr(f, 'files'):
        print("[ERROR] 不是 BundleFile")
        return 1

    # 过滤：只处理可打印英文（翻译表键），排除脚本引用噪声
    total_changed = 0
    for scene in f.files:
        sf = f.files[scene]
        if not hasattr(sf, 'objects'):
            continue
        for obj in sf.objects.values():
            if obj.type.name != 'MonoBehaviour':
                continue
            raw = obj.get_raw_data()
            # 扫描所有 string，找匹配翻译表的
            for off, data in find_text_strings(raw):
                s = data.decode('utf-8', errors='replace')
                if s in translations:
                    zh = translations[s]
                    new_bytes = zh.encode('utf-8')
                    old_len = struct.unpack_from('<i', raw, off-4)[0]
                    if not dry_run:
                        new_raw = bytearray(raw)
                        # 变长重写：头 + 新len + 新str + 尾
                        head = bytes(new_raw[:off-4])
                        tail = bytes(new_raw[off+old_len:])
                        rebuilt = head + struct.pack('<i', len(new_bytes)) + new_bytes + tail
                        obj.set_raw_data(bytes(rebuilt))
                    total_changed += 1
                    print(f"[OK] {scene} MB {obj.path_id} '{s}' -> '{zh}' ({old_len}->{len(new_bytes)})")

    if total_changed == 0:
        print("[INFO] 无匹配翻译")
        return 1

    if not dry_run:
        target = out or input
        data = env.file.save()
        with open(target, 'wb') as fh:
            fh.write(data)
        print(f"[OK] 已保存 → {target}（{len(data)} bytes，修改 {total_changed} 处）")
    else:
        print(f"[DRY-RUN] 将修改 {total_changed} 处")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="data.unity3d 路径")
    ap.add_argument("translations", help="translations.json（en→zh）")
    ap.add_argument("-o", "--out", default=None, help="输出路径（默认覆盖）")
    ap.add_argument("--dry-run", action="store_true", help="只预览不写")
    args = ap.parse_args()

    trans = json.load(open(args.translations, encoding='utf-8'))
    return hanize(args.input, trans, args.out, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
