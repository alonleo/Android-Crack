#!/usr/bin/env python3
"""
frida-cocos-text-capture.py — Cocos2d-x 游戏文本捕获工具（通用）

用途: 捕获 Cocos2d-x (C++) 游戏运行时所有 Label::setString / MenuItemLabel::setString /
      LabelAtlas::setString 动态文本，用于：
        - 汉化文本清单收集（评估哪些文本是动态可 hook）
        - 场景切换探测（配合点击/交互观察文本流）
        - 语言验证（确认游戏显示语言）

用法（需 root + frida-server）:
  python3 frida-cocos-text-capture.py <device_serial> <pid> [--dump-json file.json]

原理:
  - attach 目标进程，hook libMyGame.so / libgame.so 的导出符号
  - std::string 读取: 参数是 const std::string&，offset+8 是 size，SSO(<16) 时字符串在
    offset+16，堆分配时 offset+0 是指针
  - 每个 setString 调用打印去重文本

注意:
  - 游戏标题/主菜单常是图片(Spine PNG)，无 setString 调用——只有进入有动态文本的场景才有输出
  - 触摸触发: 可配合 adb input tap/swipe 触发场景切换
"""
import argparse
import json
import time

DEFAULT_EXPORTS = [
    "_ZN7cocos2d5Label9setStringERKNSt6__ndk112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEE",       # Label::setString
    "_ZN7cocos2d13MenuItemLabel9setStringERKNSt6__ndk112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEE",  # MenuItemLabel::setString
    "_ZN7cocos2d10LabelAtlas9setStringERKNSt6__ndk112basic_stringIcNS1_11char_traitsIcEENS1_9allocatorIcEEEE",    # LabelAtlas::setString
]

SCRIPT = r"""
var libname = "%s";
var seen = {};
function hookSetString(exportName, tag) {
    var m = Process.findModuleByName(libname);
    if (!m) return;
    var addr = m.findExportByName(exportName);
    if (!addr) { console.log("[!] no export " + exportName); return; }
    Interceptor.attach(addr, {
        onEnter: function(args) {
            try {
                var sp = args[1];
                var len = sp.add(8).readU64();
                if (len <= 0 || len > 512) return;
                var s;
                if (len <= 15) s = sp.add(16).readUtf8String(len);
                else s = sp.readPointer().readUtf8String(len);
                if (!s || !s.length) return;
                if (!seen[s]) { seen[s] = true; console.log("[TEXT] " + JSON.stringify(s)); }
            } catch(e) {}
        }
    });
}
function poll() {
    var m = Process.findModuleByName(libname);
    if (!m) { setTimeout(poll, 300); return; }
    %s
}
setTimeout(poll, 200);
console.log("[*] text capture ready (lib=" + libname + ")");
"""

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("device")
    ap.add_argument("pid", type=int)
    ap.add_argument("--lib", default="libMyGame.so")
    ap.add_argument("--dump-json", default=None)
    a = ap.parse_args()

    hook_calls = "\n".join(
        '    hookSetString("%s", "%s");' % (e, e.split("setString")[0].split("::")[-1])
        for e in DEFAULT_EXPORTS
    )
    script = SCRIPT % (a.lib, hook_calls)

    import frida
    dev = frida.get_device(a.device, timeout=10)
    session = dev.attach(a.pid)
    result = {"texts": []}

    def on_message(msg, data):
        if msg["type"] == "send":
            result["texts"].append(msg["payload"])
            print(msg["payload"])

    script_obj = session.create_script(script)
    script_obj.on("message", on_message)
    script_obj.load()
    print("[*] attached to PID %d, capturing texts (Ctrl+C to stop)..." % a.pid)
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        session.detach()
        if a.dump_json:
            with open(a.dump_json, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print("[*] texts dumped to " + a.dump_json)

if __name__ == "__main__":
    main()
