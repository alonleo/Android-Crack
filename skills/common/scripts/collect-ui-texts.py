#!/usr/bin/env python3
"""collect-ui-texts.py — Frida 收集游戏实际 UI 文本（hook Text.set_text）。

背景: 游戏无 LocalizedString 框架，UI 文本直接经 UnityEngine.UI.Text.set_text 设置。
hook 该函数（RVA 0x26F40B0）收集所有显示的文本 → 用于汉化翻译。

用法:
  python3 collect-ui-texts.py <package> -r <set_text_rva> [--timeout 60] [--serial 712KPDT1165978]

输出:
  <out>.json: {value: count} 实际显示的 UI 字符串
"""
from __future__ import annotations

import argparse
import json
import sys
import time

import frida

JS_TEMPLATE = r"""
function readIl2CppString(p) {
    if (p.isNull()) return null;
    try {
        const len = p.add(0x10).readS32();
        if (len <= 0 || len > 5000) return null;
        return p.add(0x14).readUtf16String(len);
    } catch (e) { return null; }
}
function main() {
    const mod = Process.findModuleByName("libil2cpp.so");
    if (!mod) { console.log("ERR: no libil2cpp"); return; }
    const B = mod.base;
    console.log("HOOKED\t" + B);
    // UnityEngine.UI.Text.set_text(string) — 拦截所有 UI 文本设置
    try {
        Interceptor.attach(B.add(parseInt("__SETTEXT__", 16)), {
            onEnter(args) {
                const v = readIl2CppString(args[1]);
                if (v && v.length > 0 && v.length < 300) {
                    console.log("TEXT\t" + v);
                }
            }
        });
        console.log("OK\thooked Text.set_text @" + "__SETTEXT__");
    } catch (e) {
        console.log("ERR\tset_text hook failed: " + e);
    }
}
setImmediate(main);
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("package")
    ap.add_argument("-r", "--settext-rva", default="0x26F40B0",
                    help="UnityEngine.UI.Text.set_text RVA (hex)")
    ap.add_argument("--timeout", type=int, default=60, help="收集时长(秒)")
    ap.add_argument("--serial", default="712KPDT1165978")
    ap.add_argument("-o", "--out", default="ui-texts.json")
    args = ap.parse_args()

    js = JS_TEMPLATE.replace("__SETTEXT__", str(int(args.settext_rva, 16)))

    texts = {}
    def on_message(message, data):
        if message["type"] != "send":
            return
        payload = message["payload"]
        if isinstance(payload, str) and payload.startswith("TEXT\t"):
            v = payload[5:]
            texts[v] = texts.get(v, 0) + 1

    dev = frida.get_device(args.serial, timeout=10)
    print(f"[INFO] spawn {args.package} ...")
    pid = dev.spawn([args.package])
    session = dev.attach(pid)
    script = session.create_script(js)
    script.on("message", on_message)
    script.load()
    dev.resume(pid)
    print(f"[INFO] collecting UI texts for {args.timeout}s ...")
    time.sleep(args.timeout)
    try:
        session.detach()
    except Exception:
        pass

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(texts, f, ensure_ascii=False, indent=1)
    print(f"[OK] collected {len(texts)} unique texts → {args.out}")
    for k, v in sorted(texts.items(), key=lambda x: -x[1])[:30]:
        print(f"  {v}x {k!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
