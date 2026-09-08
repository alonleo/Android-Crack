#!/usr/bin/env python3
"""metadata-patcher.py — IL2CPP global-metadata.dat 字符串字面量提取/回写工具（方案A核心）。

[方案A] 源码参考 jozsefsallai/il2cpp-stringliteral-patcher（MIT），在此独立实现为
工作区自包含单文件（不依赖外部 core/ 包）。专供 il2cpp text-hanization 的
metadata-hanize action 使用。

原理（global-metadata.dat 布局）:
  MAGIC 0xAF1BB1FA（前 4 字节）
  偏移  8  = lookup_table 偏移
  偏移 12  = lookup_table 大小（每项 8 字节: length(4) + index(4)）
  偏移 16  = stringliteral_data 偏移
  偏移 20  = stringliteral_data 大小
  每个字符串字面量位于 stringliteral_data_offset + lookup_table[i].index 处，
  长 lookup_table[i].length 字节，UTF-8 编码。

patch 策略（始终基于原文件复制，勿在原文件上反复改）:
  1. 复制原 metadata 到输出（备份 → 新文件）
  2. 在输出文件末尾依次写入全部替换后的 value（UTF-8）
  3. 在输出文件原 lookup_table 偏移处重写 lookup table（length + 累加 index）
  4. 更新偏移 16 的 stringliteral_data_offset 指向末尾新数据区

用法:
  python3 metadata-patcher.py extract  <global-metadata.dat>              # → stdout JSON
  python3 metadata-patcher.py patch    <orig.dat> <patch.json> <out.dat>  # ← 基于原文件重建
  python3 metadata-patcher.py show     <global-metadata.dat>              # 打印表头信息

patch.json 格式（与 Il2CppDumper 导出的 stringliteral.json 一致）:
  [{"index": 12345, "value": "译文"}, ...]
  index 是字符串字面量的顺序位，永不可改；value 换成目标文本。
"""
from __future__ import annotations

import json
import os
import shutil
import sys

MAGIC_BYTES = b"\xaf\x1b\xb1\xfa"
LOOKUP_TABLE_DEFINITION_OFFSET = 8
LOOKUP_TABLE_SIZE_DEFINITION_OFFSET = 12
STRINGLITERAL_DATA_DEFINITION_OFFSET = 16
STRINGLITERAL_DATA_SIZE_DEFINITION_OFFSET = 20


class MetadataInvalidError(ValueError):
    """global-metadata.dat 头无效（可能被加密/魔改/非法文件）。"""


def _read_meta_header(f) -> tuple[int, int, int, int]:
    """读取 [lookup_table_offset, lookup_table_size, str_data_offset, str_data_size]"""
    f.seek(LOOKUP_TABLE_DEFINITION_OFFSET)
    lt_off = int.from_bytes(f.read(4), "little")
    f.seek(LOOKUP_TABLE_SIZE_DEFINITION_OFFSET)
    lt_size = int.from_bytes(f.read(4), "little")
    f.seek(STRINGLITERAL_DATA_DEFINITION_OFFSET)
    sd_off = int.from_bytes(f.read(4), "little")
    f.seek(STRINGLITERAL_DATA_SIZE_DEFINITION_OFFSET)
    sd_size = int.from_bytes(f.read(4), "little")
    return lt_off, lt_size, sd_off, sd_size


def extract_strings(meta_path: str) -> list[dict]:
    """提取全部字符串字面量，返回 [{index, value}]（index 为顺序位）。"""
    if not os.path.isfile(meta_path):
        raise FileNotFoundError(f"不存在: {meta_path}")
    with open(meta_path, "rb") as f:
        magic = f.read(4)
        if magic != MAGIC_BYTES:
            raise MetadataInvalidError("Invalid global-metadata file (magic 不符，可能加密/魔改)")
        lt_off, lt_size, sd_off, sd_size = _read_meta_header(f)

        f.seek(lt_off)
        lookup: list[tuple[int, int]] = []
        read = 0
        while read < lt_size:
            length = int.from_bytes(f.read(4), "little")
            index = int.from_bytes(f.read(4), "little")
            lookup.append((length, index))
            read += 8

        strings: list[dict] = []
        for i, (length, _index) in enumerate(lookup):
            f.seek(sd_off + _index)
            lit = f.read(length).decode("utf-8", "ignore")
            strings.append({"index": i, "value": lit})
        return strings


def _normalize_patch(patch: list[dict]) -> dict[int, str]:
    """把 patch 列表归一化为 {index: value}。index 必须是 int。"""
    out: dict[int, str] = {}
    for item in patch:
        idx = item.get("index")
        val = item.get("value")
        if idx is None or val is None:
            raise ValueError("patch 条目缺 index/value")
        out[int(idx)] = str(val)
    return out


def patch_metadata(orig_path: str, patch: list[dict], out_path: str) -> dict:
    """基于原 global-metadata.dat 重建，把 patch 中的译文写回，输出到 out_path。

    必须基于原文件（orig_path）复制重建；out_path != orig_path（防在原文件上反复改）。
    返回统计 {total: N, patched: M, out_bytes: B}。
    """
    if not os.path.isfile(orig_path):
        raise FileNotFoundError(f"原 metadata 不存在: {orig_path}")
    if os.path.abspath(orig_path) == os.path.abspath(out_path):
        raise ValueError("out_path 不能等于 orig_path（务必基于备份重建）")

    strings = extract_strings(orig_path)
    trans = _normalize_patch(patch)

    shutil.copy2(orig_path, out_path)

    # 组装新的 (length, value)
    new_entries: list[tuple[int, str]] = []
    patched = 0
    for i, s in enumerate(strings):
        original: str = s.get("value", "") if isinstance(s, dict) else ""
        val: str = trans.get(i, original)
        new_entries.append((len(val.encode("utf-8")), val))
        if i in trans:
            patched += 1

    with open(orig_path, "rb") as r, open(out_path, "rb+") as w:
        r.seek(LOOKUP_TABLE_DEFINITION_OFFSET)
        lt_off = int.from_bytes(r.read(4), "little")
        # 文件末尾 = 新 string literal 数据区起点
        w.seek(0, os.SEEK_END)
        base = w.tell()
        for _ln, val in new_entries:
            w.write(val.encode("utf-8"))
        # 重写 lookup table（length + 累加 index）
        w.seek(lt_off)
        offset = 0
        for ln, _val in new_entries:
            w.write(ln.to_bytes(4, "little"))
            w.write(offset.to_bytes(4, "little"))
            offset += ln
        # 更新 stringliteral_data_offset → 文件末尾新数据区
        w.seek(STRINGLITERAL_DATA_DEFINITION_OFFSET)
        w.write(base.to_bytes(4, "little"))

    return {
        "total": len(strings),
        "patched": patched,
        "out_bytes": os.path.getsize(out_path),
        "out_path": out_path,
    }


def _cmd_extract(path: str):
    strings = extract_strings(path)
    print(json.dumps(strings, ensure_ascii=False, indent=2))


def _cmd_patch(orig: str, patch_path: str, out: str):
    with open(patch_path, "r", encoding="utf-8") as f:
        patch = json.load(f)
    stats = patch_metadata(orig, patch, out)
    print(json.dumps(stats, ensure_ascii=False, indent=2))


def _cmd_show(path: str):
    with open(path, "rb") as f:
        lt_off, lt_size, sd_off, sd_size = _read_meta_header(f)
    print(json.dumps({
        "lookup_table_offset": lt_off,
        "lookup_table_size": lt_size,
        "string_data_offset": sd_off,
        "string_data_size": sd_size,
        "entry_count": int(lt_size / 8) if lt_size else 0,
    }, indent=2))


def main(argv: list[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[0]
    if cmd == "extract" and len(argv) == 2:
        _cmd_extract(argv[1])
    elif cmd == "patch" and len(argv) == 4:
        _cmd_patch(argv[1], argv[2], argv[3])
    elif cmd == "show" and len(argv) == 2:
        _cmd_show(argv[1])
    else:
        print("用法: metadata-patcher.py [extract|show] <meta>  |  patch <orig> <patch.json> <out>")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
