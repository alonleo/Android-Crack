#!/usr/bin/env python3
"""Probe AdsService async state-machine progress without changing behavior."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
MARKER = "// === injected ads async state probe ==="
CODE = r'''
// === injected ads async state probe ===
using AdsMoveNextFn = void (*)(void*);
static AdsMoveNextFn g_orig_ads_move_next = nullptr;
static void Probed_Ads_Initialize_MoveNext(void* state_machine) {
    int state = state_machine ? *reinterpret_cast<int*>(state_machine) : -999;
    LOGI("[init-probe] AdsService.Initialize.MoveNext state=%d", state);
    if (g_orig_ads_move_next) g_orig_ads_move_next(state_machine);
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
        hook = "    A64HookFunction(reinterpret_cast<void*>(base + 0x2da1218),\n                    reinterpret_cast<void*>(Probed_Ads_Initialize_MoveNext),\n                    reinterpret_cast<void**>(&g_orig_ads_move_next));\n"
        text = text.replace(needle, hook + needle, 1)
    cpp.write_text(text, encoding="utf-8")
    print(f"[OK] 已加入 AdsService async MoveNext 状态探针: {cpp}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
