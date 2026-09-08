#!/usr/bin/env python3
"""collect-localization-strings.py — Frida spawn 游戏，hook Unity Localization 收集 key→value。

背景: FlyingGorillaEndlessRunner (2026-08-02) 汉化需要真实 UI 文本。Unity Localization
框架类不在 dump.cs，用 Frida 运行时 hook 收集：
  - `SharedTableData.GetEntry(string)` → 记录 key
  - `LocalizedString.GetLocalizedString()` → 记录 value（英文）

⚠️ 关键 hook 点（本游戏实测）:
  - 返回文本走 `LocalizedString.GetLocalizedString()`（同步），**不走** `StringTableEntry.GetLocalizedString()`
  - 字符串缓存 → attach 会错过已解析文本 → **必须 spawn（-f）时 hook**

用法:
  python3 collect-localization-strings.py <package> <out.json> [seconds] [--device 712KPDT1165978]

输出:
  <out.json>: {key: value}（唯一对）
  同时 stdout 打印 KEY/VAL 流

依赖: frida（python）+ adb；设备需装 frida-server 并 root
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import frida

# Unity Localization / UI 文本关键方法 RVA（libil2cpp.so）
# 不同游戏/Unity 版本需用 metadata.json 重新查:
#   python3 - <<PY
#   md = json.load(open("metadata.json"))["addressMap"]["methodDefinitions"]
#   for i in md:
#       n = i.get("name","")
#       if "SharedTableData" in n and "GetEntry" in n and "String" in n: print(n, i["virtualAddress"])
#       if "LocalizedString" in n and n.endswith("GetLocalizedStringEv"): print(n, i["virtualAddress"])
#   PY
DEFAULT_GETENTRY_RVA = 0x052DE814   # SharedTableData.GetEntry(string)
DEFAULT_GETLOCALIZED_RVA = 0x052D75FC  # LocalizedString.GetLocalizedString()
DEFAULT_SET_TEXT_RVAS = [0x0373964C, 0x033BF458]  # UnityEngine.UI.Text / TMPro.TMP_Text

JS = r"""
function readIl2CppString(p) {
    if (p.isNull()) return null;
    try {
        const len = p.add(0x10).readS32();
        if (len <= 0 || len > 10000) return null;
        return p.add(0x14).readUtf16String(len);
    } catch (e) { return null; }
}
function main() {
    const mod = Process.findModuleByName("libil2cpp.so");
    if (!mod) { console.log("ERR: no libil2cpp"); return; }
    const B = mod.base;
    console.log("HOOKED\t" + B);
    try { Interceptor.attach(B.add(parseInt("__GETENTRY__", 16)), {
        onEnter(a) { const k = readIl2CppString(a[1]); if (k) console.log("KEY\t" + k); }
    }); } catch(e) {}
    try { Interceptor.attach(B.add(parseInt("__GETLOCALIZED__", 16)), {
        onLeave(r) { const s = readIl2CppString(r); if (s) console.log("VAL\t" + s); }
    }); } catch(e) {}
    for (const rva of __SETTEXT__) {
        try { Interceptor.attach(B.add(rva), {
            onEnter(a) { const s = readIl2CppString(a[1]); if (s) console.log("TEXT\t" + s); }
        }); } catch(e) {}
    }
}
setTimeout(main, 300);
"""


STREAM = []


def on_message(message, data):
    if message['type'] == 'send':
        payload = str(message['payload'])
        STREAM.append(payload)
        print(payload)
    elif message['type'] == 'error':
        print(f"JS-ERR: {message.get('description', '')}", file=sys.stderr)


def parse_stream(lines):
    """把 KEY/VAL 流解析为 key→value。"""
    kv = {}
    ck = None
    for l in lines:
        if l.startswith("KEY\t"):
            ck = l[4:]
        elif l.startswith("VAL\t") and ck:
            kv[ck] = l[4:]
            ck = None
    return kv


def main() -> int:
    ap = argparse.ArgumentParser(description="Frida 收集 Unity Localization 字符串")
    ap.add_argument("package", help="目标包名")
    ap.add_argument("out", help="输出 JSON 路径")
    ap.add_argument("seconds", type=int, nargs="?", default=90)
    ap.add_argument("--device", default="")
    ap.add_argument("--getentry-rva", default=f"{DEFAULT_GETENTRY_RVA:x}")
    ap.add_argument("--getlocalized-rva", default=f"{DEFAULT_GETLOCALIZED_RVA:x}")
    ap.add_argument("--set-text-rva", action="append", default=[], help="Text.set_text RVA，可重复")
    args = ap.parse_args()

    set_text_rvas = args.set_text_rva or [f"{rva:x}" for rva in DEFAULT_SET_TEXT_RVAS]
    js = JS.replace("__GETENTRY__", args.getentry_rva).replace("__GETLOCALIZED__", args.getlocalized_rva)
    js = js.replace("__SETTEXT__", "[" + ",".join("0x" + r for r in set_text_rvas) + "]")

    dev = frida.get_usb_device(timeout=10) if args.device else frida.get_usb_device(timeout=10)
    pid = dev.spawn(args.package)
    sess = dev.attach(pid)
    sc = sess.create_script(js)
    sc.on('message', on_message)
    sc.load()
    dev.resume(pid)
    print(f"[*] spawned {args.package} pid={pid}, collecting {args.seconds}s（记得期间操作游戏 UI 触发各界面）", file=sys.stderr)
    # 收集 stdout 里的 KEY/VAL 流
    collected = []
    start = time.time()
    try:
        while time.time() - start < args.seconds:
            time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    try:
        sess.detach()
    except Exception:
        pass
    values = {}
    for line in STREAM:
        if line.startswith("TEXT\t"):
            value = line[5:].strip()
            if value and value not in values:
                values[value] = ""
        elif line.startswith("VAL\t"):
            value = line[4:].strip()
            if value and value not in values:
                values[value] = ""
    out_path = Path(args.out)
    existing = {}
    if out_path.exists():
        try:
            existing = json.loads(out_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    existing.update(values)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(existing, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"[*] 已写入 {len(values)} 条文本到 {out_path}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
