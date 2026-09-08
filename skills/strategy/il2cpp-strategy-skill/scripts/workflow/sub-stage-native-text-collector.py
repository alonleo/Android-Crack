#!/usr/bin/env python3
"""Inject FakerAndroid A64Hook text capture into an il2cpp native-lib.cpp.

The hook records UnityEngine.UI.Text.set_text and TMPro.TMP_Text.set_text
values through Android logcat. It waits for libil2cpp.so after Application
startup, so no Frida/root support is required.
"""
from __future__ import annotations

import os
import re
import shutil
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]

INJECT = r'''
// === injected by sub-stage-native-text-collector ===
#include <android/log.h>
#include <unistd.h>
#include <thread>
#include <mutex>
#include <unordered_set>
#include <cstdint>

extern "C" void A64HookFunction(void* target, void* hook, void** orig);

struct CaptureIl2CppString {
    void* klass;
    void* monitor;
    int32_t length;
    char16_t chars[0];
};

static std::mutex g_text_capture_mutex;
static std::unordered_set<std::string> g_text_capture_seen;
static bool g_text_capture_installed = false;

static uintptr_t capture_module_base(const char* soname) {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (!fp) return 0;
    char line[512];
    uintptr_t base = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, soname)) {
            unsigned long addr = 0;
            char perms[8] = {0};
            if (sscanf(line, "%lx-%*lx %7s", &addr, perms) == 2 && perms[0] == 'r') {
                base = static_cast<uintptr_t>(addr);
                break;
            }
        }
    }
    fclose(fp);
    return base;
}

static std::string capture_text(CaptureIl2CppString* s) {
    if (!s || s->length <= 0 || s->length > 4096) return {};
    std::string out;
    out.reserve(static_cast<size_t>(s->length));
    for (int32_t i = 0; i < s->length; ++i) {
        uint16_t c = static_cast<uint16_t>(s->chars[i]);
        if (c >= 0x20 && c != 0x7f && c < 0x80) out.push_back(static_cast<char>(c));
        else if (c >= 0x4e00 && c <= 0x9fff) {
            out.push_back(static_cast<char>(0xe0 | (c >> 12)));
            out.push_back(static_cast<char>(0x80 | ((c >> 6) & 0x3f)));
            out.push_back(static_cast<char>(0x80 | (c & 0x3f)));
        } else out.push_back('?');
    }
    return out;
}

static void capture_log_text(CaptureIl2CppString* value) {
    std::string text = capture_text(value);
    if (text.empty()) return;
    std::lock_guard<std::mutex> lock(g_text_capture_mutex);
    if (g_text_capture_seen.insert(text).second) {
        __android_log_print(ANDROID_LOG_INFO, "xTextCapture", "TEXT\\t%s", text.c_str());
    }
}

using CaptureTextFn = void (*)(void*, CaptureIl2CppString*);
static CaptureTextFn g_orig_unity_text = nullptr;
static CaptureTextFn g_orig_tmp_text = nullptr;

static void capture_unity_text(void* self, CaptureIl2CppString* value) {
    capture_log_text(value);
    if (g_orig_unity_text) g_orig_unity_text(self, value);
}

static void capture_tmp_text(void* self, CaptureIl2CppString* value) {
    capture_log_text(value);
    if (g_orig_tmp_text) g_orig_tmp_text(self, value);
}

static void install_text_capture_hooks() {
    if (g_text_capture_installed) return;
    uintptr_t base = capture_module_base("libil2cpp.so");
    if (!base) return;
    A64HookFunction(reinterpret_cast<void*>(base + 0x373964c),
                    reinterpret_cast<void*>(capture_unity_text),
                    reinterpret_cast<void**>(&g_orig_unity_text));
    A64HookFunction(reinterpret_cast<void*>(base + 0x33bf458),
                    reinterpret_cast<void*>(capture_tmp_text),
                    reinterpret_cast<void**>(&g_orig_tmp_text));
    g_text_capture_installed = true;
    __android_log_print(ANDROID_LOG_INFO, "xTextCapture",
                        "installed Text.set_text=0x373964c TMP_Text.set_text=0x33bf458");
}

static void start_text_capture_loader() {
    std::thread([] {
        for (int i = 0; i < 90 && !g_text_capture_installed; ++i) {
            install_text_capture_hooks();
            if (!g_text_capture_installed) sleep(1);
        }
    }).detach();
}
// === end injected text collector ===
'''


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    if not name or not type_arg:
        print("NAME and TYPE are required", file=sys.stderr)
        return 2
    cpp = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "cpp" / "native-lib.cpp"
    if not cpp.is_file():
        print(f"native-lib.cpp not found: {cpp}", file=sys.stderr)
        return 1
    hook_src = REPO / "tools" / "crack-intergration-tools" / "source-projects" / "And64InlineHook" / "And64InlineHook.cpp"
    hook_dst = cpp.parent / "And64InlineHook.cpp"
    header_src = hook_src.with_suffix(".hpp")
    header_dst = cpp.parent / "And64InlineHook.hpp"
    if not hook_dst.exists():
        shutil.copy2(hook_src, hook_dst)
        print(f"[OK] 已加入 A64HookFunction 实现: {hook_dst}")
    if not header_dst.exists():
        shutil.copy2(header_src, header_dst)
        print(f"[OK] 已加入 A64HookFunction 头文件: {header_dst}")
    text = cpp.read_text(encoding="utf-8", errors="ignore")
    marker = "// === injected by sub-stage-native-text-collector ==="
    if marker not in text:
        text = text.replace('#include <sstream>\n', '#include <sstream>\n#include <cstring>\n', 1)
        anchor = 'extern "C"\nJNIEXPORT void JNICALL\nJava_com_android_boot_App_fakeApp'
        text = text.replace(anchor, INJECT + "\n" + anchor, 1)
    text = re.sub(
        r'(Java_com_android_boot_App_fakeApp\([^)]*\) \{).*?\n\}',
        r'\1\n    start_text_capture_loader();\n}',
        text,
        count=1,
        flags=re.DOTALL,
    )
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] A64Hook 文本收集已注入: {cpp}")
    print("[INFO] hook RVAs: UnityEngine.UI.Text.set_text=0x373964c, TMPro.TMP_Text.set_text=0x33bf458")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
