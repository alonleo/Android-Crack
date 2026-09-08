#!/usr/bin/env python3
"""Add A64 no-op hook for the missing AppLovin Max Java bootstrap."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected AppLovin bootstrap no-op ==="
CODE = r'''
// === injected AppLovin bootstrap no-op ===
using VoidInitFn = void (*)();
static void Hooked_MaxCmpService_cctor() {
    LOGI("[sdk-hook] AppLovin MaxCmpService bootstrap suppressed");
}
static void Hooked_MaxSdkAndroid_SetExtraParameter() {
    LOGI("[sdk-hook] AppLovin SetExtraParameter suppressed");
}
static bool Hooked_MaxSdkAndroid_IsVerboseLoggingEnabled() {
    LOGI("[sdk-hook] AppLovin IsVerboseLoggingEnabled -> false");
    return false;
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
        needle = "    uintptr_t base = capture_module_base(\"libil2cpp.so\");\n    if (!base) return;\n"
        repl = needle + "    A64HookFunction(reinterpret_cast<void*>(base + 0x297ebd8),\n                    reinterpret_cast<void*>(Hooked_MaxCmpService_cctor), nullptr);\n    A64HookFunction(reinterpret_cast<void*>(base + 0x297ef0c),\n                    reinterpret_cast<void*>(Hooked_MaxCmpService_cctor), nullptr);\n    A64HookFunction(reinterpret_cast<void*>(base + 0x297f158),\n                    reinterpret_cast<void*>(Hooked_MaxCmpService_cctor), nullptr);\n    A64HookFunction(reinterpret_cast<void*>(base + 0x297fb10),\n                    reinterpret_cast<void*>(Hooked_MaxSdkAndroid_SetExtraParameter), nullptr);\n    A64HookFunction(reinterpret_cast<void*>(base + 0x297fa10),\n                    reinterpret_cast<void*>(Hooked_MaxSdkAndroid_IsVerboseLoggingEnabled), nullptr);\n"
        text = text.replace(needle, repl, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 AppLovin bootstrap A64 no-op hook: {cpp}")
    print("[INFO] MaxCmpService..cctor RVA=0x297ebd8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
