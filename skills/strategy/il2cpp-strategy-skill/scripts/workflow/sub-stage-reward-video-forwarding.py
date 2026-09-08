#!/usr/bin/env python3
"""
子阶段 08 - 激励视频转发（il2cpp 专用入口）
=================================================================
委托给 common 版处理（sub-stage-reward-video-forwarding.py），
因为 common 版已根据 TYPE 环境变量自动选择：
  - smali 类型（Android/Unity-Mono/...）→ smali patch 路径
  - il2cpp / unreal 类型 → native hook 路径（Hooked_* + A64HookFunction）

七步流程（与 common 版完全一致）：
  步骤1：从 step1-signatures/ 签名文件收集激励视频方法 → reward-video-detection.yaml
  步骤2：il2cpp → native hook（Hooked_* + callJava("showRewardVideo")）
  步骤3：注入 A64HookFunction 注册（And64InlineHook，Hook Engine Initialized 前）
  步骤4：检查调用链（MainActivity -> SDKUtils.showRewardVideo，函数是否默认返回 true）
  步骤5：生成 reward-video-report.yaml
  步骤6（smali→jar）：Android/Unity-Mono 等 smali patch 类型，将修改后的 smali 转 jar（convert-smali-to-jars.py → app/libs/）
  步骤7（gradlew 构建）：所有类型，执行 gradlew assembleRelease（保留模板注入的 smali2dexApk 任务链）

真机验收：sub-stage-reward-video-device-verify.py
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def main() -> int:
    """委托给 common 版脚本执行。"""
    common_script = REPO / "skills/common/general-strategy-skill/scripts/workflow/sub-stage-reward-video-forwarding.py"
    if not common_script.exists():
        print(f"[ERROR] common 版脚本不存在: {common_script}", file=sys.stderr)
        return 1
    import runpy
    sys.argv = [str(common_script)]
    runpy.run_path(str(common_script), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
