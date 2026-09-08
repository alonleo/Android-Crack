#!/usr/bin/env python3
"""
子阶段 20 - 记录工程文件（il2cpp 专用入口）
=================================================================
与 general-strategy-skill 版本完全一致，委托 common 版本执行。
"""
import os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
COMMON_SCRIPT = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py"

def main() -> int:
    os.environ["TYPE"] = os.environ.get("TYPE", "il2cpp").strip() or "il2cpp"
    name = os.environ.get("NAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if name:
        os.environ["NAME"] = name
    os.chdir(str(REPO))
    return os.system(f"python3 {COMMON_SCRIPT}")

if __name__ == "__main__":
    sys.exit(main())
