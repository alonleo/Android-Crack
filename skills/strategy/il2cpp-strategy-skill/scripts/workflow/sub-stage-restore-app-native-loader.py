#!/usr/bin/env python3
"""Restore FakerAndroid native loader calls in original App smali."""
from __future__ import annotations

import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    path = REPO / "output-projects" / type_arg / name / "app" / "src" / "main" / "smali" / "com" / "android" / "boot" / "App.smali"
    text = path.read_text(encoding="utf-8")
    if "System;->loadLibrary" not in text:
        text = text.replace("# direct methods\n", """# direct methods
.method static constructor <clinit>()V
    .locals 1
    const-string v0, \"native-lib\"
    invoke-static {v0}, Ljava/lang/System;->loadLibrary(Ljava/lang/String;)V
    return-void
.end method

""", 1)
    if "fakeApp(Landroid/app/Application;)V" not in text:
        text = text.replace("# virtual methods\n", """# direct native bridge
.method private native fakeApp(Landroid/app/Application;)V
.end method

# virtual methods
""", 1)
        text = text.replace("    .line 13\n    return-void", """    .line 13
    invoke-direct {p0, p0}, Lcom/android/boot/App;->fakeApp(Landroid/app/Application;)V
    return-void""", 1)
    text = text.replace("    invoke-virtual {p0, p0}, Lcom/android/boot/App;->fakeApp(Landroid/app/Application;)V", "    invoke-direct {p0, p0}, Lcom/android/boot/App;->fakeApp(Landroid/app/Application;)V")
    path.write_text(text, encoding="utf-8")
    print(f"[OK] 已恢复原始 App smali 的 native-lib/fakeApp 调用: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
