#!/usr/bin/env python3
"""Probe AdsService.Initialize while preserving the original Task result."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected ads initialize probe ==="
CODE = r'''
// === injected ads initialize probe ===
using AdsInitializeFn = void* (*)(void*);
static AdsInitializeFn g_orig_ads_initialize = nullptr;
static void* Probed_Ads_Initialize(void* cancellation_token) {
    LOGI("[init-probe] AdsService.Initialize entered");
    return g_orig_ads_initialize ? g_orig_ads_initialize(cancellation_token) : nullptr;
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
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2da0920),\n                    reinterpret_cast<void*>(Probed_Ads_Initialize),\n                    reinterpret_cast<void**>(&g_orig_ads_initialize));\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 AdsService.Initialize 保留原调用探针: {cpp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
