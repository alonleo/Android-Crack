#!/usr/bin/env python3
"""Bypass AdsService initialization using the non-generic Task getter."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected safe ads initialization bypass ==="
CODE = r'''
// === injected safe ads initialization bypass ===
using AdsCompletedTaskFn = void* (*)();
static void* Bypassed_Ads_Initialize(void*) {
    uintptr_t base = capture_module_base("libil2cpp.so");
    LOGI("[sdk-hook] AdsService.Initialize -> Task.CompletedTask");
    if (!base) return nullptr;
    auto completed_task = reinterpret_cast<AdsCompletedTaskFn>(base + 0x2bb8238);
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
        needle = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2d85378),"
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2da0920),\n                    reinterpret_cast<void*>(Bypassed_Ads_Initialize), nullptr);\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 AdsService.Task.CompletedTask 旁路: {cpp}")
    print("[INFO] Task.get_CompletedTask RVA=0x2bb8238")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
