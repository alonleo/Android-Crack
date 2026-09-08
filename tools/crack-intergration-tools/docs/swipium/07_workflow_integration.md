# Swipium 嵌入逆向工作流方案分析

## 1. 背景

本项目（android-crack）的核心流程包括多个真机验收阶段（08/10/12/14），当前主要依赖：
- `adb shell am start` 启动应用
- `adb logcat` 检查崩溃
- 人工目测验证 UI

**Swipium 可解决**：
- AI 代理驱动的自动化测试
- 自动生成带证据的测试报告
- 应用知识图谱构建
- 可复用的测试资产生成

## 2. Swipium vs HA4T 定位

| 维度 | HA4T | Swipium |
|------|------|---------|
| **类型** | Python UI 自动化框架 | MCP server（Node.js） |
| **定位** | 底层 UI 操作 | AI 代理 QA 测试 |
| **OCR** | ✅ PaddleOCR 中文识别 | ❌ 视觉断言 |
| **图像匹配** | ✅ aircv 模板匹配 | ✅ 视觉断言 |
| **测试报告** | ❌ 需自建 | ✅ 自动生成 |
| **应用图谱** | ❌ | ✅ 知识图谱 |
| **MCP 集成** | ❌ | ✅ 原生 |
| **真机支持** | ✅ 直接支持 | ⚠️ 需模拟器 |

**建议策略**：
- **HA4T**：用于真机验收、OCR 汉化验证、底层 UI 操作
- **Swipium**：用于模拟器测试、QA 流程管理、报告生成、应用图谱

## 3. 嵌入点分析

### 3.1 真机验收阶段（08/10/12/14）

| 当前流程 | Swipium 增强 |
|---------|-------------|
| `adb shell am start` | `qa_app_control` 启动应用 |
| `adb logcat *:E` 人工检查 | `qa_smoke` 自动冒烟测试 |
| 人工截图 | `qa_screenshot` 自动截图 |
| 人工判断无崩溃 | `qa_check_health` 健康检查 |

**集成方案**：在模拟器中运行 patched APK，使用 Swipium 进行自动化测试。

### 3.2 汉化验证阶段

| 需求 | Swipium 方案 |
|------|-------------|
| 验证中文显示 | `qa_screenshot` + `qa_assert_visual` 视觉断言 |
| 验证无乱码 | `qa_snapshot` UI 树检查 |
| 截图存档 | `qa_report` 自动生成报告 |

### 3.3 功能测试

| 需求 | Swipium 方案 |
|------|-------------|
| 探索性测试 | `qa_explore` 自动探索应用功能 |
| 流程测试 | `qa_flow_run` 运行预定义流程 |
| 测试覆盖 | `qa_app_map_build` 构建应用图谱 |

## 4. 实现方案

### 4.1 MCP 配置

在项目中配置 Swipium MCP server：

```json
// .opencode/mcp.json 或 claude_desktop_config.json
{
  "mcpServers": {
    "swipium": {
      "command": "npx",
      "args": ["-y", "swipium"],
      "cwd": "/home/leo/文档/android-crack",
      "timeout": 600000
    }
  }
}
```

### 4.2 真机验收脚本

创建 `tools/scripts/swipium-verify.py`：

```python
#!/usr/bin/env python3
"""swipium-verify.py — 基于 Swipium 的真机验收自动化工具

用法：
  ./swipium-verify.py smoke --apk crackings/<type>/ProjectName/project/patched.apk
  ./swipium-verify.py explore --apk crackings/<type>/ProjectName/project/patched.apk
  ./swipium-verify.py report --session <session-id>
"""

import os
import sys
import json
import subprocess
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common


def run_smoke_test(apk_path: str, output_dir: str = None) -> dict:
    """
    运行冒烟测试
    
    Args:
        apk_path: APK 文件路径
        output_dir: 报告输出目录
        
    Returns:
        dict: 测试结果
    """
    result = {
        "success": False,
        "message": "",
        "artifacts": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 1. 检查模拟器状态
        doctor_result = subprocess.run(
            ["npx", "swipium", "qa_doctor", "--platform", "android"],
            capture_output=True, text=True, timeout=30
        )
        
        # 2. 启动测试会话
        session_result = subprocess.run(
            ["npx", "swipium", "qa_test_this",
             "--projectRoot", os.path.dirname(apk_path),
             "--mode", "execute",
             "--goal", "smoke"],
            capture_output=True, text=True, timeout=300
        )
        
        # 3. 解析结果
        if session_result.returncode == 0:
            result["success"] = True
            result["message"] = "冒烟测试通过"
        else:
            result["message"] = f"冒烟测试失败: {session_result.stderr}"
            
    except Exception as e:
        result["message"] = f"测试失败: {str(e)}"
    
    return result


def run_explore_test(apk_path: str, output_dir: str = None) -> dict:
    """
    运行探索性测试
    
    Args:
        apk_path: APK 文件路径
        output_dir: 报告输出目录
        
    Returns:
        dict: 测试结果
    """
    result = {
        "success": False,
        "message": "",
        "app_map": {},
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 1. 启动探索性测试
        explore_result = subprocess.run(
            ["npx", "swipium", "qa_explore",
             "--session", "explore-session",
             "--depth", "medium"],
            capture_output=True, text=True, timeout=600
        )
        
        # 2. 构建应用图谱
        map_result = subprocess.run(
            ["npx", "swipium", "qa_app_map_build",
             "--session", "explore-session"],
            capture_output=True, text=True, timeout=120
        )
        
        if explore_result.returncode == 0:
            result["success"] = True
            result["message"] = "探索性测试完成"
            
    except Exception as e:
        result["message"] = f"测试失败: {str(e)}"
    
    return result


def generate_report(session_id: str, output_dir: str = "reports") -> dict:
    """
    生成测试报告
    
    Args:
        session_id: 测试会话 ID
        output_dir: 报告输出目录
        
    Returns:
        dict: 报告结果
    """
    result = {
        "success": False,
        "report_path": "",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        report_result = subprocess.run(
            ["npx", "swipium", "qa_report",
             "--session", session_id,
             "--format", "markdown",
             "--output", os.path.join(output_dir, f"report_{session_id}.md")],
            capture_output=True, text=True, timeout=120
        )
        
        if report_result.returncode == 0:
            result["success"] = True
            result["report_path"] = os.path.join(output_dir, f"report_{session_id}.md")
            
    except Exception as e:
        result["message"] = f"报告生成失败: {str(e)}"
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Swipium 真机验收自动化工具")
    subparsers = parser.add_subparsers(dest="action", help="测试类型")
    
    # smoke 子命令
    smoke_parser = subparsers.add_parser("smoke", help="冒烟测试")
    smoke_parser.add_argument("--apk", required=True, help="APK 文件路径")
    smoke_parser.add_argument("--output", help="报告输出目录")
    
    # explore 子命令
    explore_parser = subparsers.add_parser("explore", help="探索性测试")
    explore_parser.add_argument("--apk", required=True, help="APK 文件路径")
    explore_parser.add_argument("--output", help="报告输出目录")
    
    # report 子命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--session", required=True, help="测试会话 ID")
    report_parser.add_argument("--output", default="reports", help="报告输出目录")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    common.ensure_env()
    
    if args.action == "smoke":
        result = run_smoke_test(args.apk, args.output)
    elif args.action == "explore":
        result = run_explore_test(args.apk, args.output)
    elif args.action == "report":
        result = generate_report(args.session, args.output)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
```

### 4.3 集成到 crack.py

在真机验收阶段调用 Swipium：

```python
# 在 stage-08-device-verify.py 等脚本中
from swipium_verify import run_smoke_test, run_explore_test, generate_report

def run_device_verify(project_name, apk_path):
    """执行真机验收"""
    output_dir = f"crackings/{project_name}/stages/08-device-verify"
    
    # 1. 冒烟测试
    smoke_result = run_smoke_test(apk_path, output_dir)
    
    # 2. 探索性测试（可选）
    if smoke_result["success"]:
        explore_result = run_explore_test(apk_path, output_dir)
    
    # 3. 生成报告
    report_path = generate_report("verify-session", output_dir)
    
    return smoke_result["success"]
```

## 5. 优势与风险

### 优势

| 优势 | 说明 |
|------|------|
| **AI 代理集成** | MCP 原生支持，AI 代理可直接调用 |
| **自动化报告** | 自动生成带证据的测试报告 |
| **应用图谱** | 构建应用知识图谱，便于后续测试 |
| **测试资产** | 生成可复用的测试流程和用例 |
| **标准化** | 基于 MCP 协议，易于集成 |

### 风险

| 风险 | 缓解措施 |
|------|---------|
| 需要模拟器 | 与 HA4T 互补，真机用 HA4T，模拟器用 Swipium |
| iOS 需要 WDA | 优先使用 Android 模拟器 |
| Node.js 依赖 | 项目已有 Node.js 环境 |
| 视觉断言精度 | 结合 HA4T OCR 验证 |

## 6. 实施步骤

### 第一阶段：基础集成（1-2 天）

1. ✅ 安装 Swipium：`npm install swipium`
2. 配置 MCP server（`.opencode/mcp.json`）
3. 创建 `tools/scripts/swipium-verify.py` 核心脚本
4. 更新 `tools/scripts/SCRIPTS-INDEX.md`

### 第二阶段：流程嵌入（2-3 天）

1. 修改 `stage-08-device-verify.py` 调用 Swipium
2. 修改 `stage-10-cleanup-device-verify.py` 调用 Swipium
3. 修改 `stage-12-ui-device-verify.py` 调用 Swipium
4. 修改 `stage-14-hanization-device-verify.py` 调用 Swipium

### 第三阶段：高级功能（3-5 天）

1. 集成 `qa_explore` 探索性测试
2. 集成 `qa_app_map_build` 应用图谱
3. 集成 `qa_generate` 测试资产生成
4. 创建测试流程模板

### 第四阶段：经验沉淀（持续）

1. 记录 Swipium 使用经验到 `skills/common/general-strategy-skill/experience.md`
2. 优化测试流程模板
3. 收集测试用例库

## 7. 与现有工具的关系

| 现有工具 | Swipium 关系 |
|---------|-------------|
| `HA4T` | 互补：HA4T 用于真机，Swipium 用于模拟器 |
| `adb` | Swipium 底层依赖 adb |
| `logcat` | Swipium 可收集日志作为证据 |
| `apksigner` | 无直接关系 |

## 8. 结论

Swipium 是一个强大的 MCP server，专为 AI 代理设计的移动 QA 测试工具。它与 HA4T 形成互补：

- **HA4T**：底层 UI 操作、OCR 识别、真机支持
- **Swipium**：高层 QA 流程、报告生成、应用图谱、测试资产

建议按上述步骤分阶段集成，优先在真机验收阶段使用 Swipium 的报告生成功能，逐步扩展到探索性测试和应用图谱构建。
