#!/usr/bin/env python3
"""frida-probe-ui-hierarchy.py — 侦察 UIElements 树（Voodoo/UnityEngine.UI 都可），找出按钮父节点。

纯侦察，不修改任何东西。
"""
from __future__ import annotations
import argparse, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
import common  # noqa: E402


def build_js(args):
    return f"""
const SETACTIVE_RVA = 0x{args.go_setactive_rva};
const GET_NAME_RVA = 0x{args.get_name_rva};
const GET_TRANSFORM = 0x{args.get_transform_rva};
const GET_CHILD = 0x{args.get_child_rva};
const GET_CHILDCOUNT = 0x{args.get_childcount_rva};

let B = null;
function install() {{
    const mod = Process.findModuleByName("{args.libil2cpp_name}");
    if (!mod) return false;
    B = mod.base;

    const get_name = new NativeFunction(B.add(GET_NAME_RVA), 'pointer', ['pointer']);
    const get_transform = new NativeFunction(B.add(GET_TRANSFORM), 'pointer', ['pointer']);
    const get_child = new NativeFunction(B.add(GET_CHILD), 'pointer', ['pointer','int']);
    const get_childcount = new NativeFunction(B.add(GET_CHILDCOUNT), 'int', ['pointer']);

    function readIl2CppStr(p) {{
        if (!p || p.isNull()) return "";
        try {{
            const len = p.add(0x10).readS32();
            if (len <= 0 || len > 4096) return "";
            return p.add(0x14).readUtf16String(len);
        }} catch (e) {{ return ""; }}
    }}

    function pathOf(go) {{
        const parts = [];
        let cur = go;
        for (let d = 0; d < 8 && cur && !cur.isNull(); d++) {{
            const n = readIl2CppStr(get_name(cur));
            if (!n) break;
            parts.unshift(n);
            const tr = get_transform(cur);
            if (!tr || tr.isNull()) break;
            const parentTr = new NativeFunction(B.add(0x03a8e6c4 /* Transform.get_parent Injected */), 'pointer', ['pointer','pointer'])(tr, ptr(0));
            if (!parentTr || parentTr.isNull()) break;
            cur = new NativeFunction(B.add(0x03a7f29c /* GameObject.get_gameObject */), 'pointer', ['pointer','pointer'])(parentTr, ptr(0));
        }}
        return parts.join("/");
    }}

    const seen = new Set();
    Interceptor.attach(B.add(SETACTIVE_RVA), {{
        onEnter(args) {{
            try {{
                const go = args[0];
                const active = args[1].toInt32();
                const n = readIl2CppStr(get_name(go));
                if (!n) return;
                const p = pathOf(go);
                if (p.length < 200 && !seen.has(p)) {{
                    seen.add(p);
                    console.log("NODE " + n + " active=" + active + " path=" + p);
                }}
            }} catch (e) {{ /* ignore */ }}
        }}
    }});
    console.log("[READY] SetActive probe + pathOf installed");
    return true;
}}
let tries = 0;
const t = setInterval(() => {{
    tries++;
    if (install()) {{ clearInterval(t); }}
    else if (tries > 200) {{ console.log("[ERR] lib not loaded"); clearInterval(t); }}
}}, 250);
"""


def main():
    common.ensure_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--go-setactive-rva", required=True)
    ap.add_argument("--get-name-rva", required=True)
    ap.add_argument("--get-transform-rva", default="03a792e4")
    ap.add_argument("--get-child-rva", default="03a791b8")
    ap.add_argument("--get-childcount-rva", default="03a791d4")
    ap.add_argument("--duration", type=int, default=18)
    ap.add_argument("--spawn", action="store_true")
    ap.add_argument("--libil2cpp-name", default="libil2cpp.so")
    args = ap.parse_args()
    adb = common.adb()
    js = build_js(args)
    js_path = Path("/tmp") / f"frida-probe-{int(time.time())}.js"
    log_path = Path("/tmp") / f"frida-probe-log-{int(time.time())}.txt"
    js_path.write_text(js, encoding="utf-8")
    if args.spawn:
        subprocess.Popen(["frida","-U","-f",args.package,"-l",str(js_path),"-o",str(log_path)])
    else:
        r = subprocess.run([adb,"-s",args.device,"shell","pidof",args.package],
                           capture_output=True, text=True)
        pid = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        if not pid:
            common.die(f"进程未运行: {args.package}")
        p = pid[0].strip()
        common.log_info(f"attach pid={p}")
        subprocess.Popen(["frida","-U","-p",p,"-l",str(js_path),"-o",str(log_path)])
    time.sleep(args.duration)
    subprocess.run(["pkill","-f","frida.*"+str(log_path.stem)])
    time.sleep(1)
    if log_path.exists():
        for ln in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip()
            if s.startswith(("READY","NODE")):
                print(s)

if __name__ == "__main__":
    main()