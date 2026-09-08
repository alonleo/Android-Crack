#!/usr/bin/env python3
"""hanize-unity-texts-safe.py — data.unity3d 场景 Text 组件安全汉化（字节级）。

背景: 游戏 UI 文本在 MonoBehaviour 的 m_Text 字段（静态序列化，不经 set_text）。
直接改 m_Text 字符串长度会破坏后续字段（序列化错位 → 崩溃）。
安全策略：
  - m_Text 位于 MB 数据末尾（后面 ≤ 4 字节填充）→ 变长替换安全
  - m_Text 后还有有效字段 → 仅等长替换（或跳过超长）
  - 修改用 set_raw_data + env.file.save()（UnityPy 支持变长 MB）

用法:
  python3 hanize-unity-texts-safe.py <data.unity3d> <translations.json> [-o out] [--dry-run]

翻译表: {"English": "中文"}
"""
from __future__ import annotations

import argparse
import json
import struct
import sys

import UnityPy


def analyze_texts(raw: bytes) -> list[dict]:
    """扫描 MB 中所有 string，返回 {offset, text_bytes, tail_len, safe}"""
    found = []
    i = 0
    while i < len(raw) - 4:
        ln = struct.unpack_from('<i', raw, i)[0]
        if 2 <= ln <= 80 and i + 4 + ln <= len(raw):
            data = raw[i+4:i+4+ln]
            try:
                s = data.decode('utf-8')
                if s.isprintable() and all(32 <= ord(c) < 127 for c in s):
                    end = i + 4 + ln
                    tail = raw[end:]
                    # 安全：后面 ≤ 4 字节且全为 \x00 填充
                    safe = len(tail) <= 4 and all(b == 0 for b in tail)
                    found.append({'off': i, 'text': s, 'end': end, 'tail': tail, 'safe': safe})
                    i = end
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

    total = 0
    for scene in f.files:
        sf = f.files[scene]
        if not hasattr(sf, 'objects'):
            continue
        for obj in sf.objects.values():
            if obj.type.name != 'MonoBehaviour':
                continue
            raw = obj.get_raw_data()
            for item in analyze_texts(raw):
                en = item['text']
                if en not in translations:
                    continue
                zh = translations[en]
                new_bytes = zh.encode('utf-8')
                old_len = len(en.encode())
                off = item['off']
                safe = item['safe']
                if not dry_run:
                    if safe:
                        # 变长安全：头 + 新len + 新str + tail
                        head = bytes(raw[:off])
                        tail = bytes(raw[item['end']:])
                        rebuilt = head + struct.pack('<i', len(new_bytes)) + new_bytes + tail
                        obj.set_raw_data(rebuilt)
                        print(f"[OK-var] {scene} MB{obj.path_id} '{en}'->'{zh}' ({old_len}->{len(new_bytes)})")
                        total += 1
                    else:
                        # 仅等长（不安全，长度必须一致）
                        if len(new_bytes) == old_len:
                            new_raw = bytearray(raw)
                            struct.pack_into('<i', new_raw, off-4, len(new_bytes))
                            new_raw[off:off+old_len] = new_bytes
                            obj.set_raw_data(bytes(new_raw))
                            print(f"[OK-eq]  {scene} MB{obj.path_id} '{en}'->'{zh}' ({old_len}={len(new_bytes)})")
                            total += 1
                        else:
                            print(f"[SKIP]   {scene} MB{obj.path_id} '{en}'->'{zh}' 不安全且不等长")
                else:
                    total += 1
                    print(f"[DRY]    {scene} MB{obj.path_id} '{en}'->'{zh}' safe={safe} ({old_len}->{len(new_bytes)})")

    if total == 0:
        print("[INFO] 无匹配")
        return 1
    if not dry_run:
        target = out or input
        data = env.file.save()
        with open(target, 'wb') as fh:
            fh.write(data)
        print(f"[OK] 已保存 → {target}（{len(data)} bytes，修改 {total} 处）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("translations")
    ap.add_argument("-o", "--out", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    trans = json.load(open(args.translations, encoding='utf-8'))
    return hanize(args.input, trans, args.out, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())
