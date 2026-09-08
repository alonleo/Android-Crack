#!/usr/bin/env python3
from __future__ import annotations
import os
"""frida-disable-gameobjects.py — 运行时禁用 Unity GameObject（无需修改 data.unity3d）。

背景: StickFightShadowWarrior (2026-08-06)。需要隐藏主页的奖杯 + Menu 图标，但：
  - native hook MenuManager.Open no-op 让菜单永不打开（layout 已隐藏）
  - 但 trophy/menu 图标 GameObject 本身仍可见
  - 直接修改 data.unity3d 用 UnityPy save 后游戏崩溃（UI 全部丢失）
  - 解法：Frida attach → hook MenuManager.Update（每帧调用，可靠）→
    一次性调用 il2cpp_string_new + GameObject_Find + GameObject_SetActive(false)
    把目标 GameObject 设为 inactive

**为何 hook MenuManager.Update 而不是 Awake/Start**：
  - MenuManager.Awake/Start 可能在 hook 安装前已触发（场景预加载）
  - Update 每帧调用，hook 安装后第一次调用即可执行一次性逻辑
  - 用 done 标志保证只执行一次

**为何用 il2cpp_string_new 而不是普通字符串**：
  - Unity 用自己的 Il2CppString 内存布局（klass + monitor + length + chars）
  - 普通 UTF8 字符串传给 GameObject_Find 会导致读取失败
  - 必须用 il2cpp_string_new 包装成 Il2CppString

**已知 RVAs（来自 Unity 2022.x + il2cpp.h，需 verify-il2cpp-rva.py 适配）**:
  - il2cpp_string_new    : 0x0103FBD8
  - GameObject_Find       : 0x0235363C
  - GameObject_SetActive  : 0x023532BC
  - MenuManager.Update    : 0x01158250（每个项目不同，需从 dump.cs 查）

用法:
  python3 frida-disable-gameobjects.py \\
      --device 712KPDT1165978 --package com.oguztecimer.stickfightshadowwarrior \\
      --update-rva 01158250 \\
      --target "Leaderboards,Menu" \\
      --spawn  # 默认 attach 模式

参数:
  --device            adb device serial
  --package           目标包名
  --update-rva         每帧调用的 hook 点 RVA（如 MenuManager.Update）
  --target             逗号分隔 GameObject 名称列表
  --il2cpp-string-new-rva  il2cpp_string_new RVA（默认 0x0103FBD8）
  --go-find-rva        GameObject.Find RVA（默认 0x0235363C）
  --go-setactive-rva   GameObject.SetActive RVA（默认 0x023532BC）
  --spawn              spawn 模式（默认 attach 已运行进程）
  --libil2cpp-name     libil2cpp.so 名称（默认 libil2cpp.so）
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
import common  # noqa: E402


def build_js(args: argparse.Namespace) -> str:
    targets = [t.strip() for t in args.target.split(",") if t.strip()]
    target_js = "[" + ",".join(f'"{t}"' for t in targets) + "]"
    return f"""
const TARGETS = {target_js};
const IL2CPP_STRING_NEW_RVA  = 0x{args.il2cpp_string_new_rva};
const GAMEOBJECT_FIND_RVA    = 0x{args.go_find_rva};
const GAMEOBJECT_SETACTIVE_RVA = 0x{args.go_setactive_rva};
const UPDATE_HOOK_RVA = 0x{args.update_rva};

const mod = Process.findModuleByName("{args.libil2cpp_name}");
if (!mod) {{ console.log("ERR: no {args.libil2cpp_name}"); return; }}
const B = mod.base;

const stringNew     = new NativeFunction(B.add(IL2CPP_STRING_NEW_RVA),    'pointer', ['pointer']);
const goFind        = new NativeFunction(B.add(GAMEOBJECT_FIND_RVA),      'pointer', ['pointer', 'pointer']);
const goSetActive   = new NativeFunction(B.add(GAMEOBJECT_SETACTIVE_RVA), 'void',    ['pointer', 'int',   'pointer']);

let done = false;
let found = 0;

Interceptor.attach(B.add(UPDATE_HOOK_RVA), {{
    onEnter(args) {{
        if (done) return;
        done = true;
        console.log("[HOOK] first call → disabling " + TARGETS.length + " GameObjects");

        for (const name of TARGETS) {{
            try {{
                const s = stringNew(Memory.allocUtf8String(name));
                const go = goFind(s, ptr(0));
                if (go && !go.equals(ptr(0))) {{
                    goSetActive(go, 0, ptr(0));   // 0 = false = inactive
                    console.log("[OK] disabled: " + name + " @ " + go);
                    found++;
                }} else {{
                    console.log("[--] not found: " + name);
                }}
            }} catch (e) {{
                console.log("[ERR] " + name + ": " + e.message);
            }}
        }}
        console.log("[DONE] disabled " + found + "/" + TARGETS.length);
    }}
}});
console.log("[READY] waiting for hook...");
"""


def main() -> None:
    common.ensure_env()
    ap = argparse.ArgumentParser(description="运行时禁用 Unity GameObject（Frida 一次性）")
    ap.add_argument("--device", required=True)
    ap.add_argument("--package", required=True)
    ap.add_argument("--update-rva", required=True, help="每帧调用的 hook 点 RVA")
    ap.add_argument("--target", required=True, help='逗号分隔 GameObject 名')
    ap.add_argument("--il2cpp-string-new-rva", default="0103FBD8")
    ap.add_argument("--go-find-rva", default="0235363C")
    ap.add_argument("--go-setactive-rva", default="023532BC")
    ap.add_argument("--spawn", action="store_true")
    ap.add_argument("--libil2cpp-name", default="libil2cpp.so")
    args = ap.parse_args()

    adb = common.adb()
    js = build_js(args)
    js_path = Path("/tmp") / f"frida-disable-{int(time.time())}.js"
    js_path.write_text(js, encoding="utf-8")
    common.log_info(f"JS 脚本 → {js_path}")

    if args.spawn:
        proc = subprocess.Popen(
            ["frida", "-U", "-n", args.package, "-l", str(js_path), "-q"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
    else:
        pid = common.call([adb, "-s", args.device, "shell", "pidof", args.package],
                          capture=True).strip().splitlines()
        if not pid:
            common.die(f"进程未运行: {args.package}（加 --spawn 或先启动）")
        p = pid[0].strip()
        common.log_info(f"attach pid={p}")
        proc = subprocess.Popen(
            ["frida", "-U", "-p", p, "-l", str(js_path), "-q"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )

    try:
        out, _ = proc.communicate(timeout=15)
    except subprocess.TimeoutExpired:
        proc.kill()
        out, _ = proc.communicate()

    for ln in out.splitlines():
        if any(tag in ln for tag in ("[OK]", "[--]", "[ERR]", "[HOOK]", "[READY]", "[DONE]")):
            print(ln)

    common.append_tool_call(
        "frida-disable-gameobjects",
        f"frida -U -p <pid> -l {js_path.name} --target {args.target}",
    )


if __name__ == "__main__":
    main()