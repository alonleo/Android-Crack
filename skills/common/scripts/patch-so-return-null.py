#!/usr/bin/env python3
"""patch-so-return-null.py — 二进制 patch ELF .so 的某个函数，使其直接返回指定值。

背景: FlyingGorillaEndlessRunner (2026-08-02) 的 Firebase C++ 库 `libFirebaseCppApp-12_10_1.so`
中 `firebase::crashlytics::Crashlytics::GetInstance` 在 Google Play Services 过期时
进入 `CrashlyticsInternal` 构造函数 → JNI `GetObjectField(obj==null)` → SIGABRT。
patch 该函数前两条指令为 `mov x0,#0; ret`，返回 null，绕过 Crashlytics 初始化。

[FLOWFIX 2026-08-30 ViragoHerstory112] 扩展到 armeabi-v7a (ARM32):
  - 支持 `mov r0,#imm; bx lr`（返回值立即数）。用于 patch
    `LanguageManager.get_CurrentLanguage` 强制返回 Chinese(7) —— 方案2（不在 Java 层）。
  - armv7 ARM 指令:
      mov r0, #imm  = 0xE3A000<imm>
      bx lr         = 0xE12FFF1E

用法:
  python3 patch-so-return-null.py <lib.so> <rva_hex> [-o <out.so>] [--imm N]

示例:
  python3 patch-so-return-null.py libil2cpp.so 131b684 --imm 7 -o libil2cpp.patched.so

注意:
  - RVA 按"文件偏移 == vaddr"的 LOAD 段假设（offset-0 映射）；il2cpp 段 vaddr==file offset。
  - 建议先 `cp <lib.so> <lib.so>.bak`。
"""
from __future__ import annotations

import argparse
import shutil
import struct
import sys
from pathlib import Path

ELF_MAGIC = b"\x7fELF"


def _machine(path: Path) -> str:
    data = path.read_bytes()
    if not data.startswith(ELF_MAGIC):
        sys.exit(f"[ERROR] 不是 ELF 文件: {path}")
    e_machine = int.from_bytes(data[18:20], "little")
    # 183 = EM_AARCH64, 40 = EM_ARM, 62 = EM_X86_64
    return {183: "aarch64", 40: "arm", 62: "x86_64"}.get(e_machine, "unknown")


def _arm_mov_r0_imm(imm: int) -> bytes:
    """ARM32: mov r0, #imm; bx lr (小端). imm 0-255."""
    imm = imm & 0xFF
    mov = 0xE3A00000 | imm  # mov r0, #imm
    bx = 0xE12FFF1E          # bx lr
    return struct.pack("<II", mov, bx)


def _aarch64_mov_x0_imm(imm: int) -> bytes:
    """AArch64: mov x0, #imm; ret. 仅 imm=0 常用."""
    if imm != 0:
        # mov x0,#imm (正立即数, 简化处理, 仅支持 0)
        sys.exit(f"[ERROR] aarch64 暂只支持 imm=0 (收到 {imm})")
    mov = 0xD2800000          # mov x0, #0
    ret = 0xD65F03C0          # ret
    return struct.pack("<II", mov, ret)


def patch(path: Path, rva: int, imm: int, out: Path | None) -> None:
    machine = _machine(path)
    data = bytearray(path.read_bytes())

    if rva + 8 > len(data):
        sys.exit(f"[ERROR] RVA 0x{rva:x} 超出文件范围 {len(data)}")

    orig = bytes(data[rva:rva + 8])
    if machine == "arm":
        patch_bytes = _arm_mov_r0_imm(imm)
        desc = f"mov r0,#{imm}; bx lr"
    elif machine == "aarch64":
        patch_bytes = _aarch64_mov_x0_imm(imm)
        desc = f"mov x0,#{imm}; ret"
    else:
        sys.exit(f"[ERROR] 不支持的架构 {machine}（仅支持 aarch64 / arm）")

    data[rva:rva + 8] = patch_bytes

    target = out or path
    if target.resolve() == path.resolve():
        bak = path.with_suffix(path.suffix + ".bak")
        if not bak.exists():
            shutil.copy2(path, bak)
            print(f"[INFO] 备份 → {bak}")
    target.write_bytes(bytes(data))
    print(f"[OK]   patch {path.name} @ 0x{rva:x}")
    print(f"      原字节: {orig.hex()}")
    print(f"      新字节: {patch_bytes.hex()} ({desc})")
    print(f"      → {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="二进制 patch ELF .so 函数返回指定值")
    parser.add_argument("so", help="目标 .so 路径")
    parser.add_argument("rva", help="目标函数 RVA（十六进制，如 131b684）")
    parser.add_argument("-o", "--out", default=None, help="输出路径（缺省就地 patch）")
    parser.add_argument("--imm", type=int, default=0, help="返回值立即数（armv7 mov r0,#imm; arm64 仅支持 0）")
    args = parser.parse_args()

    so = Path(args.so)
    if not so.is_file():
        sys.exit(f"[ERROR] 文件不存在: {so}")
    rva = int(args.rva, 16)
    out = Path(args.out) if args.out else None
    patch(so, rva, args.imm, out)


if __name__ == "__main__":
    main()
