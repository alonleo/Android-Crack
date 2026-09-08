#!/usr/bin/env python3
"""swipium-verify.py — 基于 Swipium 的 QA 测试自动化工具

用法：
  ./swipium-verify.py smoke --apk crackings/<type>/ProjectName/project/patched.apk
  ./swipium-verify.py explore --apk crackings/<type>/ProjectName/project/patched.apk
  ./swipium-verify.py report --session <session-id>
  ./swipium-verify.py doctor --platform android

功能：
  1. doctor: 检查工具链就绪状态
  2. smoke: 运行冒烟测试
  3. explore: 运行探索性测试
  4. report: 生成测试报告
"""

import os
import sys
import json
import subprocess
from datetime import datetime
from typing import Dict, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common


def run_doctor(platform: str = "android") -> Dict:
    """
    检查工具链就绪状态
    
    Args:
        platform: 平台（android/ios/both）
        
    Returns:
        dict: 检查结果
    """
    result = {
        "success": False,
        "message": "",
        "tools": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 检查 Swipium 安装
        swipium_path = os.path.expanduser("~/tools/swipium/node_modules/.bin/swipium")
        if not os.path.exists(swipium_path):
            result["message"] = "Swipium 未安装，请运行: cd ~/tools/swipium && npm install swipium"
            return result
        
        # 运行 doctor
        doctor_result = subprocess.run(
            [swipium_path, "verify"],
            capture_output=True, text=True, timeout=60,
            cwd=os.path.expanduser("~/tools/swipium")
        )
        
        if doctor_result.returncode == 0:
            result["success"] = True
            result["message"] = "工具链就绪"
            # 解析工具列表
            output = doctor_result.stdout
            if "tools:" in output:
                tools_str = output.split("tools:")[1].split("\n")[0]
                result["tools"] = [t.strip() for t in tools_str.split(",")]
        else:
            result["message"] = f"工具链检查失败: {doctor_result.stderr}"
            
    except Exception as e:
        result["message"] = f"检查失败: {str(e)}"
    
    return result


def run_smoke_test(apk_path: str, output_dir: str = None) -> Dict:
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
        swipium_path = os.path.expanduser("~/tools/swipium/node_modules/.bin/swipium")
        project_root = os.path.dirname(apk_path)
        
        # 运行冒烟测试
        smoke_result = subprocess.run(
            [swipium_path, "qa_test_this",
             "--projectRoot", project_root,
             "--mode", "execute",
             "--goal", "smoke"],
            capture_output=True, text=True, timeout=300,
            cwd=os.path.expanduser("~/tools/swipium")
        )
        
        if smoke_result.returncode == 0:
            result["success"] = True
            result["message"] = "冒烟测试通过"
            # 解析产物
            try:
                output_json = json.loads(smoke_result.stdout)
                result["artifacts"] = output_json.get("artifacts", [])
            except:
                pass
        else:
            result["message"] = f"冒烟测试失败: {smoke_result.stderr}"
            
    except Exception as e:
        result["message"] = f"测试失败: {str(e)}"
    
    return result


def run_explore_test(apk_path: str, depth: str = "medium", 
                     output_dir: str = None) -> Dict:
    """
    运行探索性测试
    
    Args:
        apk_path: APK 文件路径
        depth: 探索深度（shallow/medium/deep）
        output_dir: 报告输出目录
        
    Returns:
        dict: 测试结果
    """
    result = {
        "success": False,
        "message": "",
        "app_map": {},
        "screens": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        swipium_path = os.path.expanduser("~/tools/swipium/node_modules/.bin/swipium")
        project_root = os.path.dirname(apk_path)
        
        # 运行探索性测试
        explore_result = subprocess.run(
            [swipium_path, "qa_explore",
             "--session", f"explore-{int(datetime.now().timestamp())}",
             "--depth", depth],
            capture_output=True, text=True, timeout=600,
            cwd=os.path.expanduser("~/tools/swipium")
        )
        
        if explore_result.returncode == 0:
            result["success"] = True
            result["message"] = "探索性测试完成"
            
            # 构建应用图谱
            map_result = subprocess.run(
                [swipium_path, "qa_app_map_build",
                 "--session", f"explore-{int(datetime.now().timestamp())}"],
                capture_output=True, text=True, timeout=120,
                cwd=os.path.expanduser("~/tools/swipium")
            )
            
            if map_result.returncode == 0:
                try:
                    result["app_map"] = json.loads(map_result.stdout)
                except:
                    pass
        else:
            result["message"] = f"探索性测试失败: {explore_result.stderr}"
            
    except Exception as e:
        result["message"] = f"测试失败: {str(e)}"
    
    return result


def generate_report(session_id: str, output_dir: str = "reports") -> Dict:
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
        swipium_path = os.path.expanduser("~/tools/swipium/node_modules/.bin/swipium")
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, f"report_{session_id}.md")
        
        report_result = subprocess.run(
            [swipium_path, "qa_report",
             "--session", session_id,
             "--format", "markdown",
             "--output", report_path],
            capture_output=True, text=True, timeout=120,
            cwd=os.path.expanduser("~/tools/swipium")
        )
        
        if report_result.returncode == 0:
            result["success"] = True
            result["report_path"] = report_path
        else:
            result["message"] = f"报告生成失败: {report_result.stderr}"
            
    except Exception as e:
        result["message"] = f"报告生成失败: {str(e)}"
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Swipium QA 测试自动化工具")
    subparsers = parser.add_subparsers(dest="action", help="测试类型")
    
    # doctor 子命令
    doctor_parser = subparsers.add_parser("doctor", help="检查工具链就绪状态")
    doctor_parser.add_argument("--platform", default="android", choices=["android", "ios", "both"],
                              help="平台")
    
    # smoke 子命令
    smoke_parser = subparsers.add_parser("smoke", help="冒烟测试")
    smoke_parser.add_argument("--apk", required=True, help="APK 文件路径")
    smoke_parser.add_argument("--output", help="报告输出目录")
    
    # explore 子命令
    explore_parser = subparsers.add_parser("explore", help="探索性测试")
    explore_parser.add_argument("--apk", required=True, help="APK 文件路径")
    explore_parser.add_argument("--depth", default="medium", choices=["shallow", "medium", "deep"],
                               help="探索深度")
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
    
    if args.action == "doctor":
        result = run_doctor(args.platform)
    elif args.action == "smoke":
        result = run_smoke_test(args.apk, args.output)
    elif args.action == "explore":
        result = run_explore_test(args.apk, args.depth, args.output)
    elif args.action == "report":
        result = generate_report(args.session, args.output)
    else:
        parser.print_help()
        sys.exit(1)
    
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":
    main()
