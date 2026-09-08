#!/usr/bin/env python3
"""Instrument Initializer.OnLoadingComplete without changing its behavior."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected initializer completion probe ==="
CODE = r'''
// === injected initializer completion probe ===
using InitializerCompleteFn = void (*)(void*);
static InitializerCompleteFn g_orig_initializer_complete = nullptr;
static void Probed_Initializer_OnLoadingComplete(void* self) {
    LOGI("[init-probe] Core.Initializer.OnLoadingComplete entered");
    if (g_orig_initializer_complete) g_orig_initializer_complete(self);
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
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2d84d84),\n                    reinterpret_cast<void*>(Probed_Initializer_OnLoadingComplete),\n                    reinterpret_cast<void**>(&g_orig_initializer_complete));\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 Initializer.OnLoadingComplete 探针: {cpp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
