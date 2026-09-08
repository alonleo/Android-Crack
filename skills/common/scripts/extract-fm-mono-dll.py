#!/usr/bin/env python3
"""
extract-fm-mono-dll.py — 从运行中的 FM 框架（Green Mushroom / rivergame）Unity 游戏
提取解密后的 Mono 程序集（.mdl → .dll）。

背景:
  部分 Unity 游戏（含 libfm_mono_glue.so + assets/Assemblies/*.mdl）把 Mono 程序集
  以自定义加密格式（.mdl）打包，运行时由 libfm_mono_glue.so 解密加载。
  本脚本 hook `LoadAssemblyWithImageBinary` 拿到解密后的 DLL 字节（MZ 头），
  通过 frida send() 传回客户端保存，供 ilspycmd / dnSpy 反编译。

用法:
  python3 extract-fm-mono-dll.py --package com.greenmushroom.boomblitz.gp \
      [--host 127.0.0.1] [--port 27042] [--out /tmp/fm-dlls] [--wait 30]

前置:
  - 设备 root + frida-server（版本与本地 frida 一致）
  - adb forward tcp:<port> tcp:<port>
  - dotnet tool install -g ilspycmd   # 反编译用

产出:
  <out>/*.dll（如 ScriptProj.dll 37MB）

关联文档:
  skills/strategy/il2cpp-strategy-skill/references/fm-mono-mdl-extraction.md
"""

from __future__ import annotations

import argparse
import os
import sys
import time


FRIDA_HOOK_JS = r"""
// FM Mono .mdl 提取: hook LoadAssemblyWithImageBinary 拿解密后的 DLL
function hookGlue() {
    var glue = Process.findModuleByName("libfm_mono_glue.so");
    if (!glue) return false;
    var addr = null;
    glue.enumerateExports().forEach(function (e) {
        if (e.name === "LoadAssemblyWithImageBinary") addr = e.address;
    });
    if (!addr) return false;
    console.log("[+] hooked LoadAssemblyWithImageBinary @ " + addr);
    Interceptor.attach(addr, {
        onEnter: function (args) {
            var name = "";
            try { name = args[0].readCString() || ""; } catch (e) {}
            var p = args[1];
            var len = args[2].toInt32();
            this.safe = (name || "unknown").replace(/[^a-zA-Z0-9_.]/g, "_");
            this.dll = null;
            this.len = 0;
            try {
                if (p.readU16() === 0x5a4d) {  // 'MZ'
                    this.dll = p;
                    this.len = len;
                }
            } catch (e) {}
            console.log("[LOAD] " + name + " len=" + len);
        },
        onLeave: function (ret) {
            if (this.dll && this.len > 0) {
                console.log("[DUMP] sending " + this.safe + " len=" + this.len);
                var chunk = 0x100000;  // 1MB 分块
                var total = 0;
                while (total < this.len) {
                    var sz = Math.min(chunk, this.len - total);
                    var buf = this.dll.add(total).readByteArray(sz);
                    send({ type: "chunk", name: this.safe, offset: total, size: sz, total: this.len }, buf);
                    total += sz;
                }
                send({ type: "done", name: this.safe, total: this.len });
                console.log("[DUMP] done " + this.safe);
            }
        }
    });
    return true;
}
var n = 0;
var timer = setInterval(function () {
    n++;
    try { if (hookGlue()) { clearInterval(timer); } } catch (e) {}
    if (n > 400) { clearInterval(timer); console.log("TIMEOUT"); }
}, 50);
"""


def on_message(message, data, buffers, out_dir):
    if message["type"] == "send":
        payload = message["payload"]
        if payload["type"] == "chunk":
            name = payload["name"]
            total = payload["total"]
            if name not in buffers:
                buffers[name] = bytearray(total)
            off = payload["offset"]
            buffers[name][off:off + payload["size"]] = data
            sys.stdout.write("\r{name}: {cur}/{total}".format(
                name=name, cur=min(off + payload["size"], total), total=total))
            sys.stdout.flush()
        elif payload["type"] == "done":
            name = payload["name"]
            path = os.path.join(out_dir, name + ".dll")
            with open(path, "wb") as f:
                f.write(buffers[name])
            print("\n[SAVED] {path} ({size} bytes)".format(path=path, size=len(buffers[name])))
            del buffers[name]
    elif message["type"] == "error":
        print("[ERR] {msg}".format(msg=message))


def main() -> int:
    parser = argparse.ArgumentParser(description="FM Mono .mdl → DLL 提取")
    parser.add_argument("--package", required=True, help="目标包名（如 com.greenmushroom.boomblitz.gp）")
    parser.add_argument("--host", default="127.0.0.1", help="frida-server 转发地址")
    parser.add_argument("--port", type=int, default=27042, help="frida-server 端口")
    parser.add_argument("--out", default="/tmp/fm-dlls", help="DLL 输出目录")
    parser.add_argument("--wait", type=int, default=30, help="等待秒数（大 assembly 需更长）")
    args = parser.parse_args()

    try:
        import frida
    except ImportError:
        print("缺少 frida 模块: pip install frida", file=sys.stderr)
        return 1

    os.makedirs(args.out, exist_ok=True)
    buffers = {}

    device = frida.get_device_manager().add_remote_device(
        "{host}:{port}".format(host=args.host, port=args.port))
    pid = device.spawn(args.package)
    session = device.attach(pid)
    script = session.create_script(FRIDA_HOOK_JS)
    script.on("message", lambda m, d: on_message(m, d, buffers, args.out))
    script.load()
    device.resume(pid)
    print("等待 dump... 包={pkg} 输出={out}".format(pkg=args.package, out=args.out))
    time.sleep(args.wait)
    print("\n完成。用 ilspycmd 反编译: ilspycmd -t <ClassName> <out>/ScriptProj.dll")
    return 0


if __name__ == "__main__":
    sys.exit(main())
