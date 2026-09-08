#!/usr/bin/env python3
"""
子阶段 02 - 预处理构建（il2cpp 专用入口）
=================================================================
委托 general-strategy-skill 版本执行，il2cpp 类型通过 TYPE=il2cpp 环境变量路由。
"""
import os, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
COMMON_SCRIPT = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py"

def main() -> int:
    os.environ["TYPE"] = os.environ.get("TYPE", "il2cpp").strip() or "il2cpp"
    name = os.environ.get("NAME") or (sys.argv[1] if len(sys.argv) > 1 else None)
    if name:
        os.environ["NAME"] = name
    os.chdir(str(REPO))
    return os.system(f"python3 {COMMON_SCRIPT}")

if __name__ == "__main__":
    sys.exit(main())
