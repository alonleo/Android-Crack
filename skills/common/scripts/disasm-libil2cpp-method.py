#!/usr/bin/env python3
"""disasm-libil2cpp-method.py — 反汇编 libil2cpp.so 指定 RVA 的 ARM64 指令。

用途：诊断 il2cpp 方法的前置检查逻辑（如 BTSplash.OnStartGame 为何短路）。
用法: python3 disasm-libil2cpp-method.py --so <path> --rva 0x93F288 [--count 60]
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path


def find_libil2cpp(repo: str) -> str:
    for root, _dirs, files in os.walk(repo):
        if 'libil2cpp.so' in files:
            return os.path.join(root, 'libil2cpp.so')
    return ''


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument('--so', default='')
    parser.add_argument('--rva', required=True, help='hex RVA, e.g. 0x93F288')
    parser.add_argument('--count', type=int, default=60)
    args = parser.parse_args()

    so = args.so
    if not so or not os.path.exists(so):
        repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # 尝试从工作区 crackings 下找
        repo = '/home/leo/文档/android-crack'
        so = find_libil2cpp(repo)
    if not so:
        print('[ERROR] 未找到 libil2cpp.so')
        return 1

    import capstone
    data = open(so, 'rb').read()
    rva = int(args.rva, 16)
    md = capstone.Cs(capstone.CS_ARCH_ARM64, capstone.CS_MODE_ARM)
    md.detail = True
    code = data[rva:rva + args.count * 8]
    n = 0
    for ins in md.disasm(code, rva):
        print(f'0x{ins.address:X}: {ins.mnemonic:<10} {ins.op_str}')
        n += 1
        if n >= args.count:
            break
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
