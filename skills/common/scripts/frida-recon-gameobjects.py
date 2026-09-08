#!/usr/bin/env python3
"""
frida-recon-gameobjects.py — 侦察 Unity GameObject 名（查询/检索专用，不隐藏、不持久化）。

用途: 去功能点前，检索按钮对应的 GameObject 名字（严格「只查不改」：
      仅 hook GameObject.SetActive 并记录被启用对象的 name，绝不调用 SetActive 生效码）。
      （用户约定：frida 仅用于查询/搜索/检索，持久化隐藏一律走 APK 内 native hook。）

获取真实 RVA: 来自对应项目的 script.json ScriptMethod.Address —
  UnityEngine.GameObject$$SetActive / UnityEngine.Object$$get_name。
  示例（需按项目替换）:
    --go-setactive-rva 03A7D908
    --get-name-rva     03A838A4

输出: 打印 `SETACTIVE <name> active=<0|1>`，按关键字过滤；同时收集去重全名写入 stdout 供分析。

用法:
  python3 frida-recon-gameobjects.py --device <serial> --package <pkg> \
      --go-setactive-rva <RVA> --get-name-rva <RVA> [--spawn] \
      [--keywords noads,settings,privacy,leader,...] [--duration 15]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
import common  # noqa: E402

DEFAULT_KEYWORDS = [
    "noads", "no_ads", "settings", "setting", "privacy", "policy",
    "restore", "revive", "offer", "shop", "skin", "leaderboard", "leader",
    "watch", "morefollower", "rvbtn", "gem", "coin", "premium", "vip",
]


def build_js(args: argparse.Namespace) -> str:
    kw = args.keywords or ",".join(DEFAULT_KEYWORDS)
    keywords = [k.strip().lower() for k in kw.split(",") if k.strip()]
    kw_js = "[" + ",".join('"%s"' % k for k in keywords) + "]"
    return f"""
const KEYWORDS = {kw_js};
const SETACTIVE_RVA = 0x{args.go_setactive_rva};
const GET_NAME_RVA  = 0x{args.get_name_rva};

let B = null;
function install() {{
    const mod = Process.findModuleByName("{args.libil2cpp_name}");
    if (!mod) return false;   // 尚未加载，稍后再试（spawn 初期）
    B = mod.base;
    const get_name = new NativeFunction(B.add(GET_NAME_RVA), 'pointer', ['pointer']);

    function readIl2CppStr(p) {{
        if (!p || p.isNull()) return "";
        try {{
            const len = p.add(0x10).readS32();
            if (len <= 0 || len > 4096) return "";
            return p.add(0x14).readUtf16String(len);
        }} catch (e) {{ return ""; }}
    }}

    const seen = new Set();
    Interceptor.attach(B.add(SETACTIVE_RVA), {{
        onEnter(args) {{
            try {{
                const go = args[0];
                const active = args[1].toInt32();
                const name = readIl2CppStr(get_name(go));
                if (!name) return;
                const low = name.toLowerCase();
                const hit = KEYWORDS.some(k => low.indexOf(k) >= 0);
                if (hit && !seen.has(name)) {{
                    seen.add(name);
                    console.log("SETACTIVE " + name + " active=" + active);
                }}
            }} catch (e) {{ /* 忽略单例读取失败 */ }}
        }}
    }});
    console.log("[READY] SetActive logger installed (query-only).");
    return true;
}}
let tries = 0;
const timer = setInterval(() => {{
    tries++;
    if (install()) {{ clearInterval(timer); }}
    else if (tries > 160) {{ console.log("[ERR] {args.libil2cpp_name} not loaded"); clearInterval(timer); }}
}}, 250);
"""


def main() -> None:
    common.ensure_env()
    ap = argparse.ArgumentParser(description="侦察 Unity GameObject 名（查询专用）")
    ap.add_argument("--device", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--go-setactive-rva", required=True)
    ap.add_argument("--get-name-rva", required=True)
    ap.add_argument("--keywords", default="")
    ap.add_argument("--duration", type=int, default=15)
    ap.add_argument("--spawn", action="store_true")
    ap.add_argument("--libil2cpp-name", default="libil2cpp.so")
    args = ap.parse_args()

    adb = common.adb()
    js = build_js(args)
    js_path = Path("/tmp") / f"frida-recon-{int(time.time())}.js"
    log_path = Path("/tmp") / f"frida-recon-log-{int(time.time())}.txt"
    js_path.write_text(js, encoding="utf-8")

    if args.spawn:
        proc = subprocess.Popen(
            ["frida", "-U", "-f", args.package, "-l", str(js_path), "-o", str(log_path)],
        )
    else:
        r = subprocess.run([adb, "-s", args.device, "shell", "pidof", args.package],
                           capture_output=True, text=True)
        pid = [l.strip() for l in r.stdout.strip().splitlines() if l.strip()]
        if not pid:
            common.die(f"进程未运行: {args.package}（加 --spawn 或先启动）")
        p = pid[0].strip()
        common.log_info(f"attach pid={p}")
        proc = subprocess.Popen(
            ["frida", "-U", "-p", p, "-l", str(js_path), "-o", str(log_path)],
        )

    time.sleep(args.duration)
    proc.kill()
    time.sleep(1)
    if log_path.exists():
        for ln in log_path.read_text(encoding="utf-8", errors="replace").splitlines():
            s = ln.strip()
            if s.startswith(("[READY]", "SETACTIVE")):
                print(s)


if __name__ == "__main__":
    main()
