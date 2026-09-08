#!/usr/bin/env python3
"""
verify-il2cpp-rva.py — 生成 Frida 脚本验证 libil2cpp.so 的 RVA 是否可安全 hook。

背景: [FLOWFIX] il2cpp 项目 hook 前必须验证 RVA 指向
真正的函数入口。若 RVA 指向极短内联函数（如 `mov w0,#1; ret` = 528000xx d65f03c0），
A64HookFunction 覆写首条指令会破坏代码 → SIGSEGV 崩溃。

用法:
  python3 verify-il2cpp-rva.py <dump.cs 片段或 RVA 列表>  # 生成 frida 脚本
  # 或直接:
  python3 verify-il2cpp-rva.py --rva 0x11C9FDC,0x11C9C78,0x11C9098

生成的脚本输出每个 RVA 地址的:
  - 内存保护 (r-x = 可执行, 正常)
  - 前 4 条 AArch64 指令 (4 字节)
判断:
  - 标准 prologue (stp x29,x30,[sp,#N] ≈ f81d0ffe) → 正常函数, 可安全 hook
  - `mov w0,#N; ret` (528000xx d65f03c0) → 极短内联函数, hook 会崩溃, 应排除

依赖: 目标 app 运行中 + frida-server + adb forward
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

FRIDA_TEMPLATE = r"""'use strict';
const il2cpp = Process.findModuleByName('libil2cpp.so');
console.log('il2cpp base:', il2cpp.base, 'size:', il2cpp.size);
const targets = {
%(targets)s
};
for (const [name, rva] of Object.entries(targets)) {
    const addr = il2cpp.base.add(rva);
    let desc = '';
    try {
        const prot = Process.findRangeByAddress(addr);
        desc = prot ? `prot=${prot.protection}` : 'NO RANGE';
    } catch(e) { desc = 'range err'; }
    let insns = '';
    try {
        for (let i = 0; i < 4; i++) {
            insns += ' ' + addr.add(i*4).readU32().toString(16);
        }
    } catch(e) { insns = ' READ FAIL'; }
    console.log(`${name}: addr=${addr} ${desc} insns[${insns}]`);
}
"""


def parse_dump_cs(dump_cs: str) -> dict:
    """从 dump.cs 提取 '方法名 RVA: 0x...' 对。"""
    targets = {}
    for line in dump_cs.splitlines():
        import re
        m = re.search(r'// RVA:\s*0x([0-9A-Fa-f]+).*', line)
        if m:
            # 上一行通常是方法签名
            targets[f'0x{m.group(1)}'] = int(m.group(1), 16)
    return targets


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 Frida 脚本验证 il2cpp RVA 可 hook 性")
    parser.add_argument("--rva", default="", help="逗号分隔的 RVA（如 0x11C9FDC,0x11C9C78）")
    parser.add_argument("--dump", default="", help="dump.cs 路径（提取全部 RVA）")
    parser.add_argument("--serial", default="", help="adb 设备序列号（可选）")
    args = parser.parse_args()

    targets = {}
    if args.rva:
        for r in args.rva.split(","):
            r = r.strip()
            if r:
                targets[r] = int(r, 16)
    if args.dump:
        targets.update(parse_dump_cs(Path(args.dump).read_text(encoding="utf-8")))

    if not targets:
        print("[ERROR] 需指定 --rva 或 --dump")
        return 1

    # 生成 frida JS
    lines = []
    for name, rva in sorted(targets.items()):
        lines.append(f"    '{name}(0x{rva:X})': 0x{rva:X},")
    js = FRIDA_TEMPLATE.replace("%(targets)s", "\n".join(lines))

    tmp = Path(tempfile.gettempdir()) / "verify-il2cpp-rva.js"
    tmp.write_text(js, encoding="utf-8")
    print(f"[OK] Frida 脚本已生成: {tmp}")

    cmd = ["frida"]
    if args.serial:
        cmd += ["-H", "127.0.0.1:27042", "-p"]
    # 附加到运行中的 app
    import os
    if os.environ.get("APP_PID"):
        cmd.append(os.environ["APP_PID"])
        cmd += ["-l", str(tmp)]
        print(f"[INFO] 运行: {' '.join(cmd)}")
        print(f"  （或手动: frida -H 127.0.0.1:27042 -p <pid> -l {tmp}）")
    else:
        print("[INFO] 设置环境变量 APP_PID=<进程号> 自动运行，或手动执行:")
        print(f"  frida -H 127.0.0.1:27042 -p <pid> -l {tmp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
