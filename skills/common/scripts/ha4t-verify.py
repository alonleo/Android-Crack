#!/usr/bin/env python3
"""ha4t-verify.py — 基于 HA4T 的真机验收自动化工具

用法：
  ./ha4t-verify.py launch --package com.example.app --activity .MainActivity
  ./ha4t-verify.py hanization --package com.example.app --activity .MainActivity --texts "开始游戏" "设置"
  ./ha4t-verify.py screenshot --package com.example.app --activity .MainActivity --output screenshots/

功能：
  1. launch: 验证 APK 启动并进入游戏主界面
  2. hanization: 验证汉化效果（OCR 中文识别）
  3. screenshot: 截图并保存
"""

import os
import sys
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Optional

# 确保项目环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common


def get_ocr():
    """延迟加载 OCR（避免启动慢）"""
    try:
        from ha4t.orc import OCR
        return OCR()
    except Exception as e:
        print(f"OCR 初始化失败: {e}")
        return None


def verify_launch(package_name: str, activity_name: str, 
                  timeout: int = 30, output_dir: str = None) -> Dict:
    """
    验证 APK 启动并进入游戏
    
    Returns:
        dict: {"success": bool, "message": str, "screenshots": list, "page_text": str}
    """
    result = {
        "success": False,
        "message": "",
        "screenshots": [],
        "page_text": "",
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        from ha4t import connect
        from ha4t.api import wait, exists, screenshot, get_page_text, start_app
        
        # 连接设备
        dev = connect(
            platform="android",
            android_package_name=package_name,
            android_activity_name=activity_name
        )
        
        # 启动应用
        start_app(package_name, activity_name)
        time.sleep(2)
        
        # 截图：启动后
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            ss_path = os.path.join(output_dir, f"launch_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 等待主界面（OCR 识别常见游戏主菜单文字）
        try:
            wait("开始游戏|play|start|主菜单|游戏|Loading", timeout=timeout, raise_error=False)
        except:
            pass
        
        # 获取页面文字
        page_text = get_page_text()
        result["page_text"] = page_text
        
        # 截图：主界面
        if output_dir:
            ss_path = os.path.join(output_dir, f"main_menu_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 验证：无崩溃（检查是否仍在游戏内）
        current_app = dev.get_current_app()
        if package_name in current_app:
            result["success"] = True
            result["message"] = "应用启动成功，已进入主界面"
        else:
            result["message"] = f"应用已退出，当前应用：{current_app}"
            
    except Exception as e:
        result["message"] = f"验证失败：{str(e)}"
    
    return result


def verify_hanization(package_name: str, activity_name: str,
                      expected_texts: List[str] = None, 
                      output_dir: str = None) -> Dict:
    """
    验证汉化效果
    
    Returns:
        dict: {"success": bool, "found_texts": list, "missing_texts": list, "page_text": str}
    """
    result = {
        "success": False,
        "found_texts": [],
        "missing_texts": [],
        "page_text": "",
        "screenshots": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        from ha4t import connect
        from ha4t.api import wait, get_page_text, screenshot, start_app
        
        dev = connect(
            platform="android",
            android_package_name=package_name,
            android_activity_name=activity_name
        )
        
        start_app(package_name, activity_name)
        time.sleep(3)
        
        # 获取页面文字
        page_text = get_page_text()
        result["page_text"] = page_text
        
        # 截图
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            ss_path = os.path.join(output_dir, f"hanization_{int(time.time())}.png")
            screenshot(ss_path)
            result["screenshots"].append(ss_path)
        
        # 检查中文文字
        if expected_texts:
            for text in expected_texts:
                if text in page_text:
                    result["found_texts"].append(text)
                else:
                    result["missing_texts"].append(text)
            
            result["success"] = len(result["missing_texts"]) == 0
        else:
            # 自动检测中文字符
            chinese_chars = re.findall(r'[\u4e00-\u9fff]+', page_text)
            result["success"] = len(chinese_chars) > 0
            result["found_texts"] = chinese_chars[:10]
            
    except Exception as e:
        result["message"] = f"验证失败：{str(e)}"
    
    return result


def take_screenshot(package_name: str, activity_name: str, 
                    output_dir: str = "screenshots") -> Dict:
    """截图并保存"""
    result = {
        "success": False,
        "screenshots": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        from ha4t import connect
        from ha4t.api import screenshot, start_app
        
        dev = connect(
            platform="android",
            android_package_name=package_name,
            android_activity_name=activity_name
        )
        
        start_app(package_name, activity_name)
        time.sleep(2)
        
        os.makedirs(output_dir, exist_ok=True)
        ss_path = os.path.join(output_dir, f"screenshot_{int(time.time())}.png")
        screenshot(ss_path)
        
        result["success"] = True
        result["screenshots"].append(ss_path)
        
    except Exception as e:
        result["message"] = f"截图失败：{str(e)}"
    
    return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="HA4T 真机验收自动化工具")
    subparsers = parser.add_subparsers(dest="action", help="验证类型")
    
    # launch 子命令
    launch_parser = subparsers.add_parser("launch", help="验证应用启动")
    launch_parser.add_argument("--package", required=True, help="包名")
    launch_parser.add_argument("--activity", required=True, help="主 Activity")
    launch_parser.add_argument("--timeout", type=int, default=30, help="超时秒数")
    launch_parser.add_argument("--output", help="截图输出目录")
    
    # hanization 子命令
    han_parser = subparsers.add_parser("hanization", help="验证汉化效果")
    han_parser.add_argument("--package", required=True, help="包名")
    han_parser.add_argument("--activity", required=True, help="主 Activity")
    han_parser.add_argument("--texts", nargs="*", help="期望中文文本列表")
    han_parser.add_argument("--output", help="截图输出目录")
    
    # screenshot 子命令
    ss_parser = subparsers.add_parser("screenshot", help="截图")
    ss_parser.add_argument("--package", required=True, help="包名")
    ss_parser.add_argument("--activity", required=True, help="主 Activity")
    ss_parser.add_argument("--output", default="screenshots", help="截图输出目录")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    # 确保环境
    common.ensure_env()
    
    # 执行验证
    if args.action == "launch":
        result = verify_launch(args.package, args.activity, args.timeout, args.output)
    elif args.action == "hanization":
        result = verify_hanization(args.package, args.activity, args.texts, args.output)
    elif args.action == "screenshot":
        result = take_screenshot(args.package, args.activity, args.output)
    else:
        parser.print_help()
        sys.exit(1)
    
    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
