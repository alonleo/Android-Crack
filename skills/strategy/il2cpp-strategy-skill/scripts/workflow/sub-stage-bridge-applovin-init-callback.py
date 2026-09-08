#!/usr/bin/env python3
"""Fire AppLovin's managed SDK-initialized delegate immediately after registration."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected sdk initialized callback bridge ==="
CODE = r'''
// === injected sdk initialized callback bridge ===
#include <dlfcn.h>
using AddSdkEventFn = void (*)(void*);
using ObjectGetClassFn = void* (*)(void*);
using ClassGetMethodFn = const void* (*)(void*, const char*, int);
using RuntimeInvokeFn = void* (*)(const void*, void*, void**, void**);
using MethodGetParamFn = const void* (*)(const void*, unsigned int);
using ClassFromTypeFn = void* (*)(const void*);
using ObjectNewFn = void* (*)(void*);
static AddSdkEventFn g_orig_add_sdk_event = nullptr;
static void FireSdkInitializedDelegate(void* value) {
    if (!value) return;
    void* il2cpp = dlopen("libil2cpp.so", RTLD_NOW | RTLD_NOLOAD);
    auto object_get_class = reinterpret_cast<ObjectGetClassFn>(dlsym(il2cpp, "il2cpp_object_get_class"));
    auto class_get_method = reinterpret_cast<ClassGetMethodFn>(dlsym(il2cpp, "il2cpp_class_get_method_from_name"));
    auto runtime_invoke = reinterpret_cast<RuntimeInvokeFn>(dlsym(il2cpp, "il2cpp_runtime_invoke"));
    auto method_get_param = reinterpret_cast<MethodGetParamFn>(dlsym(il2cpp, "il2cpp_method_get_param"));
    auto class_from_type = reinterpret_cast<ClassFromTypeFn>(dlsym(il2cpp, "il2cpp_class_from_il2cpp_type"));
    auto object_new = reinterpret_cast<ObjectNewFn>(dlsym(il2cpp, "il2cpp_object_new"));
    if (!object_get_class || !class_get_method || !runtime_invoke || !method_get_param || !class_from_type || !object_new) {
        LOGI("[sdk-hook] IL2CPP delegate bridge symbols unavailable");
        return;
    }
    void* klass = object_get_class(value);
    const void* method = klass ? class_get_method(klass, "Invoke", 1) : nullptr;
    if (!method) {
        LOGI("[sdk-hook] AppLovin delegate Invoke method unavailable");
        return;
    }
    const void* parameter_type = method_get_param(method, 0);
    void* configuration = parameter_type ? object_new(class_from_type(parameter_type)) : nullptr;
    void* args[1] = {configuration};
    void* exception = nullptr;
    runtime_invoke(method, value, args, &exception);
    LOGI("[sdk-hook] AppLovin OnSdkInitializedEvent fired exception=%p", exception);
}
static void Probed_MaxSdkCallbacks_add_OnSdkInitializedEvent(void* value) {
    if (g_orig_add_sdk_event) g_orig_add_sdk_event(value);
    FireSdkInitializedDelegate(value);
}
'''


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    cpp = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "cpp" / "native-lib.cpp"
    text = cpp.read_text(encoding="utf-8")
    if MARKER not in text:
        anchor = "static void install_text_capture_hooks() {"
        text = text.replace(anchor, CODE + "\n" + anchor, 1)
        needle = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2d85378),"
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2983d58),\n                    reinterpret_cast<void*>(Probed_MaxSdkCallbacks_add_OnSdkInitializedEvent),\n                    reinterpret_cast<void**>(&g_orig_add_sdk_event));\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 AppLovin 初始化回调桥接探针: {cpp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
