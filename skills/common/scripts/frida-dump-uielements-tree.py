#!/usr/bin/env python3
"""frida-dump-uielements-tree.py — 从 UIElements rootElement 递归 dump UXML 树（定位 UI 元素/区域）。

背景: FlyingGorillaEndlessRunner (2026-08-02)。设置窗口等 UI 的显示元素与宿主类字段引用
**是不同对象**（改字段引用无效），必须从 rootElement 遍历真实 UXML 树，按元素 name 定位
目标区域/容器（如 settings-shelf / settings-bgm-slider）。本脚本生成并执行 Frida 探针，
dump 元素 name + 层级。

用法:
  python3 frida-dump-uielements-tree.py \
      --device 712KPDT1165978 --package jp.pinbit.flygorilla \
      --host-update-rva 02B9D194 --root-field 0x140 \
      --get-name-rva 05AA8D30 --get-child-count-rva 05AB17F8 --get-item-rva 05AB177C \
      --tap "1300,200" --filter settings -o /tmp/uielements-tree.log

参数（RVA/offset 均为 il2cpp dump 十六进制，不带 0x 前缀）:
  --host-update-rva  宿主类 Update 方法 RVA（hook 点，每帧读 rootElement）
  --root-field       宿主类 rootElement 字段偏移（hex）
  --get-name-rva     VisualElement::get_name RVA
  --get-child-count-rva  VisualElement::get_childCount RVA
  --get-item-rva      VisualElement::get_Item(int) RVA
  --tap "x,y"        dump 前点击屏幕（打开目标 UI，如设置按钮）
  --filter KEYWORDS 只打印 name 含任一关键词的元素（逗号分隔）
  --spawn            spawn 模式（默认 attach 已运行进程）
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools" / "scripts" / "lib"))
import common  # noqa: E402


def build_js(args: argparse.Namespace) -> str:
    name_rva = args.get_name_rva
    cc_rva = args.get_child_count_rva
    item_rva = args.get_item_rva
    host_update = args.host_update_rva
    root_field = args.root_field
    flt = args.filter or ""
    return f"""
function readIl2CppString(p) {{
    if (p.isNull()) return null;
    try {{ const len = p.add(0x10).readS32(); if (len<=0||len>300) return null;
          return p.add(0x14).readUtf16String(len); }} catch(e){{ return null; }}
}}
function main() {{
    const mod = Process.findModuleByName("libil2cpp.so");
    if (!mod) {{ console.log("ERR: no libil2cpp.so"); return; }}
    const B = mod.base;
    const get_name = new NativeFunction(B.add(0x{name_rva}), 'pointer', ['pointer']);
    const get_childCount = new NativeFunction(B.add(0x{cc_rva}), 'int', ['pointer']);
    const get_Item = new NativeFunction(B.add(0x{item_rva}), 'pointer', ['pointer', 'int']);
    const filter = "{flt}".toLowerCase();
    const seen = new Set();
    function name(el) {{ try {{ return readIl2CppString(get_name(el)) || ""; }} catch(e){{ return ""; }} }}
    function walk(el, depth) {{
        if (depth > 15 || el.isNull() || seen.has(el.toString())) return;
        seen.add(el.toString());
        const n = name(el);
        if (!filter || filter.split(",").some(k => k.trim() && n.toLowerCase().includes(k.trim())))
            console.log("TREE\\t" + "  ".repeat(depth) + (n || "(unnamed)"));
        try {{
            const cc = get_childCount(el);
            for (let i = 0; i < cc && i < 80; i++) {{
                try {{ walk(get_Item(el, i), depth+1); }} catch(e) {{}}
            }}
        }} catch(e) {{}}
    }}
    let started = false;
    Interceptor.attach(B.add(0x{host_update}), {{
        onEnter(a) {{
            if (started) return; started = true;
            const root = a[0].add(0x{root_field}).readPointer();
            console.log("=== TREE START ===");
            walk(root, 0);
            console.log("=== TREE END ===");
        }}
    }});
    console.log("HOOKED");
}}
setTimeout(main, 300);
"""


def main() -> None:
    common.ensure_env()
    ap = argparse.ArgumentParser(description="UXML 树 dump 探针")
    ap.add_argument("--device", required=True, help="adb device serial")
    ap.add_argument("--package", required=True, help="目标包名")
    ap.add_argument("--host-update-rva", required=True)
    ap.add_argument("--root-field", required=True)
    ap.add_argument("--get-name-rva", required=True)
    ap.add_argument("--get-child-count-rva", required=True)
    ap.add_argument("--get-item-rva", required=True)
    ap.add_argument("--tap", default="", help='"x,y" 打开目标 UI')
    ap.add_argument("--filter", default="", help="逗号分隔关键词，只打印命中元素")
    ap.add_argument("--spawn", action="store_true")
    ap.add_argument("-o", "--output", default="")
    args = ap.parse_args()

    adb = common.adb()
    js = build_js(args)
    js_path = Path("/tmp") / f"uielements-dump-{int(time.time())}.js"
    js_path.write_text(js, encoding="utf-8")

    if args.spawn:
        proc = subprocess.Popen(["frida", "-U", "-n", args.package, "-l", str(js_path), "-q"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    else:
        pid = common.call([adb, "-s", args.device, "shell", "pidof", args.package],
                          capture=True).strip().splitlines()
        if not pid:
            common.die(f"进程未运行: {args.package}")
        p = pid[0].strip()
        common.log_info(f"attach pid={p}")
        proc = subprocess.Popen(["frida", "-U", "-p", p, "-l", str(js_path), "-q"],
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

    time.sleep(3)
    if args.tap:
        x, y = args.tap.split(",")
        common.call([adb, "-s", args.device, "shell", "input", "tap", x.strip(), y.strip()])
        time.sleep(6)
    try:
        out, _ = proc.communicate(timeout=25)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()

    lines = [ln for ln in out.splitlines() if "TREE" in ln or "HOOKED" in ln or "TREE START" in ln or "TREE END" in ln]
    if not lines:
        common.log_warn("无 TREE 输出（hook 未触发或 UI 未构建）")
    else:
        for ln in lines:
            print(ln)
    if args.output:
        Path(args.output).write_text("\n".join(out.splitlines()), encoding="utf-8")
        common.log_info(f"完整输出 → {args.output}")

    common.append_tool_call("frida-dump-uielements-tree",
                            f"frida -U -p <pid> -l {js_path.name} [--tap {args.tap} --filter {args.filter}]")


if __name__ == "__main__":
    main()
