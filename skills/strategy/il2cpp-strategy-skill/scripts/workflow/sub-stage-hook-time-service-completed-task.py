#!/usr/bin/env python3
"""Bypass TimeService initialization with non-generic Task.CompletedTask."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected safe time-service bypass ==="
CODE = r'''
// === injected safe time-service bypass ===
using CompletedTaskFn = void* (*)();
static void* Hooked_TimeService_Initialize(void*) {
    uintptr_t base = capture_module_base("libil2cpp.so");
    LOGI("[sdk-hook] TimeService.Initialize -> CompletedTask");
    if (!base) return nullptr;
    auto completed_task = reinterpret_cast<CompletedTaskFn>(base + 0x2bb4c5c);
    return completed_task();
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
        needle = "    A64HookFunction(reinterpret_cast<void*>(base + 0x297ebd8),"
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2d8ea08),\n                    reinterpret_cast<void*>(Hooked_TimeService_Initialize), nullptr);\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入安全 TimeService 初始化旁路: {cpp}")
    print("[INFO] TimeService.Initialize RVA=0x2d8ea08; Task.CompletedTask RVA=0x2bb4c5c")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
