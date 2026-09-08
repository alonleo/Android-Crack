#!/usr/bin/env python3
"""Hook TimeService.HandleTimeSync to complete its existing TCS offline."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected offline time-sync completion ==="
CODE = r'''
// === injected offline time-sync completion ===
using TcsSetResultFn = void (*)(void*, bool);
static void Hooked_TimeService_HandleTimeSync(void* tcs) {
    uintptr_t base = capture_module_base("libil2cpp.so");
    LOGI("[sdk-hook] TimeService.HandleTimeSync -> completed true");
    if (base && tcs) {
        auto set_result = reinterpret_cast<TcsSetResultFn>(base + 0x28328a4);
        set_result(tcs, true);
    }
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
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2d8eae4),\n                    reinterpret_cast<void*>(Hooked_TimeService_HandleTimeSync), nullptr);\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 TimeService.HandleTimeSync 完成旁路: {cpp}")
    print("[INFO] HandleTimeSync RVA=0x2d8eae4; TaskCompletionSource<bool>.SetResult RVA=0x28328a4")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
