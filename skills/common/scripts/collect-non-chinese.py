#!/usr/bin/env python3
"""collect-non-chinese.py — 自动收集游戏中的非中文内容和位置

功能：
  1. 通过无障碍服务获取原生 UI 文本
  2. 通过 OCR 获取游戏渲染的文本
  3. 识别非中文内容并记录位置
  4. 生成汉化映射表
  5. 汉化替换后重新测试

用法：
  ./collect-non-chinese.py collect --package com.example.game --activity .MainActivity
  ./collect-non-chinese.py verify --package com.example.game --mapping hanization_map.json
  ./collect-non-chinese.py report --output report.md

原理：
  - 原生 UI（按钮、菜单、对话框）：通过无障碍服务获取文本和位置
  - 游戏引擎渲染（Unity/Cocos/il2cpp）：通过 OCR 识别文本和位置
  - 图片中的文字：通过 OCR 识别
"""

import os
import sys
import json
import re
import subprocess
import time
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common


@dataclass
class TextItem:
    """文本元素数据结构"""
    text: str
    source: str  # 'accessibility' | 'ocr' | 'image'
    bounds: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    confidence: float = 1.0
    is_chinese: bool = False
    translation: str = ""
    context: str = ""  # 所在界面/场景


def is_chinese(text: str) -> bool:
    """判断文本是否主要是中文"""
    if not text.strip():
        return True
    
    # 计算中文字符比例
    chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
    total_chars = len(text.strip())
    
    if total_chars == 0:
        return True
    
    return chinese_chars / total_chars > 0.5


def extract_chinese(text: str) -> bool:
    """判断是否包含中文"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def collect_accessibility_texts(device_serial: str = None) -> List[TextItem]:
    """
    通过无障碍服务收集原生 UI 文本
    
    Args:
        device_serial: 设备序列号
        
    Returns:
        List[TextItem]: 文本元素列表
    """
    items = []
    
    try:
        # 使用 uiautomator2 获取 UI 树
        import uiautomator2 as u2
        
        if device_serial:
            d = u2.connect(device_serial)
        else:
            d = u2.connect()
        
        # 获取 UI 层次结构
        xml_content = d.dump_hierarchy()
        
        # 解析 XML 提取文本和位置
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_content)
        
        for elem in root.iter('node'):
            text = elem.get('text', '').strip()
            content_desc = elem.get('content-desc', '').strip()
            bounds_str = elem.get('bounds', '')
            
            # 优先使用 text，其次使用 content-desc
            display_text = text or content_desc
            
            if not display_text:
                continue
            
            # 解析 bounds [x1,y1][x2,y2]
            if bounds_str:
                match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
                if match:
                    x1, y1, x2, y2 = map(int, match.groups())
                    
                    item = TextItem(
                        text=display_text,
                        source='accessibility',
                        bounds=(x1, y1, x2, y2),
                        confidence=1.0,
                        is_chinese=is_chinese(display_text)
                    )
                    items.append(item)
        
        print(f"✅ 无障碍服务收集到 {len(items)} 个文本元素")
        
    except Exception as e:
        print(f"⚠️ 无障碍服务收集失败: {e}")
    
    return items


def collect_ocr_texts(device_serial: str = None, 
                      screenshots_dir: str = None) -> List[TextItem]:
    """
    通过 OCR 收集游戏渲染的文本
    
    Args:
        device_serial: 设备序列号
        screenshots_dir: 截图目录
        
    Returns:
        List[TextItem]: 文本元素列表
    """
    items = []
    
    try:
        # 延迟加载 OCR
        from ha4t.orc import OCR
        import numpy as np
        from PIL import Image
        
        ocr = OCR()
        
        # 获取截图
        if screenshots_dir and os.path.exists(screenshots_dir):
            # 使用已有截图
            screenshots = [f for f in os.listdir(screenshots_dir) if f.endswith('.png')]
            if not screenshots:
                print("⚠️ 截图目录为空")
                return items
            
            # 使用最新的截图
            screenshot_path = os.path.join(screenshots_dir, sorted(screenshots)[-1])
            img = Image.open(screenshot_path)
        else:
            # 通过 adb 截图
            import uiautomator2 as u2
            if device_serial:
                d = u2.connect(device_serial)
            else:
                d = u2.connect()
            
            img = d.screenshot()
        
        # OCR 识别
        img_array = np.array(img)
        result = ocr.ocr(img_array)
        
        if result:
            for line in result:
                if line:
                    for item_data in line:
                        # item_data: [[x1,y1], [x2,y2], [x3,y3], [x4,y4]], (text, confidence)
                        points = item_data[0]
                        text = item_data[1][0]
                        confidence = item_data[1][1]
                        
                        # 计算边界框
                        x_coords = [p[0] for p in points]
                        y_coords = [p[1] for p in points]
                        x1, x2 = min(x_coords), max(x_coords)
                        y1, y2 = min(y_coords), max(y_coords)
                        
                        item = TextItem(
                            text=text,
                            source='ocr',
                            bounds=(int(x1), int(y1), int(x2), int(y2)),
                            confidence=confidence,
                            is_chinese=is_chinese(text)
                        )
                        items.append(item)
        
        print(f"✅ OCR 收集到 {len(items)} 个文本元素")
        
    except Exception as e:
        print(f"⚠️ OCR 收集失败: {e}")
    
    return items


def collect_all_texts(package_name: str, activity_name: str,
                      device_serial: str = None,
                      screenshots_dir: str = None) -> List[TextItem]:
    """
    收集所有文本（无障碍 + OCR）
    
    Args:
        package_name: 包名
        activity_name: Activity 名
        device_serial: 设备序列号
        screenshots_dir: 截图目录
        
    Returns:
        List[TextItem]: 去重后的文本元素列表
    """
    print(f"🔍 开始收集文本: {package_name}")
    
    # 启动应用
    try:
        import uiautomator2 as u2
        if device_serial:
            d = u2.connect(device_serial)
        else:
            d = u2.connect()
        
        d.app_start(package_name, activity_name)
        time.sleep(3)  # 等待应用启动
    except Exception as e:
        print(f"⚠️ 启动应用失败: {e}")
    
    # 收集无障碍文本
    accessibility_items = collect_accessibility_texts(device_serial)
    
    # 收集 OCR 文本
    ocr_items = collect_ocr_texts(device_serial, screenshots_dir)
    
    # 合并去重
    all_items = []
    seen_texts = set()
    
    for item in accessibility_items + ocr_items:
        # 使用文本 + 位置作为去重键
        key = f"{item.text}_{item.bounds[0]}_{item.bounds[1]}"
        if key not in seen_texts:
            seen_texts.add(key)
            all_items.append(item)
    
    print(f"📊 总计收集到 {len(all_items)} 个唯一文本元素")
    
    return all_items


def filter_non_chinese(items: List[TextItem]) -> List[TextItem]:
    """过滤出非中文文本"""
    non_chinese = [item for item in items if not item.is_chinese]
    print(f"🔤 找到 {len(non_chinese)} 个非中文文本元素")
    return non_chinese


def generate_translation_mapping(items: List[TextItem], 
                                 output_file: str = None) -> Dict:
    """
    生成汉化映射表
    
    Args:
        items: 非中文文本元素列表
        output_file: 输出文件路径
        
    Returns:
        Dict: 汉化映射表
    """
    mapping = {
        "generated_at": datetime.now().isoformat(),
        "total_items": len(items),
        "translations": []
    }
    
    for item in items:
        entry = {
            "original": item.text,
            "source": item.source,
            "bounds": list(item.bounds),
            "confidence": item.confidence,
            "translation": "",  # 需要人工填写或机器翻译
            "context": item.context
        }
        mapping["translations"].append(entry)
    
    if output_file:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f"💾 汉化映射表已保存: {output_file}")
    
    return mapping


def verify_hanization(package_name: str, activity_name: str,
                      mapping_file: str, device_serial: str = None) -> Dict:
    """
    验证汉化效果
    
    Args:
        package_name: 包名
        activity_name: Activity 名
        mapping_file: 汉化映射表文件
        device_serial: 设备序列号
        
    Returns:
        Dict: 验证结果
    """
    result = {
        "success": False,
        "verified": 0,
        "passed": 0,
        "failed": 0,
        "details": [],
        "timestamp": datetime.now().isoformat()
    }
    
    try:
        # 加载映射表
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        # 重新收集文本
        items = collect_all_texts(package_name, activity_name, device_serial)
        
        # 验证每个翻译项
        for trans in mapping.get("translations", []):
            original = trans["original"]
            expected_translation = trans["translation"]
            
            if not expected_translation:
                continue
            
            result["verified"] += 1
            
            # 检查原文是否已被替换
            found = False
            for item in items:
                if item.text == original:
                    # 原文仍然存在，汉化失败
                    result["details"].append({
                        "original": original,
                        "status": "failed",
                        "reason": "原文仍然存在"
                    })
                    result["failed"] += 1
                    found = True
                    break
            
            if not found:
                # 检查翻译是否出现
                for item in items:
                    if expected_translation in item.text:
                        result["details"].append({
                            "original": original,
                            "translation": expected_translation,
                            "status": "passed"
                        })
                        result["passed"] += 1
                        found = True
                        break
            
            if not found:
                result["details"].append({
                    "original": original,
                    "translation": expected_translation,
                    "status": "unknown",
                    "reason": "未找到原文或翻译"
                })
        
        result["success"] = result["failed"] == 0 and result["verified"] > 0
        
    except Exception as e:
        result["message"] = f"验证失败: {str(e)}"
    
    return result


def generate_report(items: List[TextItem], output_file: str = "report.md") -> str:
    """
    生成收集报告
    
    Args:
        items: 文本元素列表
        output_file: 输出文件路径
        
    Returns:
        str: 报告文件路径
    """
    non_chinese = filter_non_chinese(items)
    
    report = f"""# 非中文内容收集报告

生成时间: {datetime.now().isoformat()}

## 统计

- 总文本元素: {len(items)}
- 非中文元素: {len(non_chinese)}
- 中文元素: {len(items) - len(non_chinese)}

## 非中文内容列表

| # | 文本 | 来源 | 位置 | 置信度 |
|---|------|------|------|--------|
"""
    
    for i, item in enumerate(non_chinese, 1):
        bounds_str = f"({item.bounds[0]},{item.bounds[1]})-({item.bounds[2]},{item.bounds[3]})"
        report += f"| {i} | {item.text} | {item.source} | {bounds_str} | {item.confidence:.2f} |\n"
    
    report += f"""

## 建议

1. 优先处理高频出现的非中文文本
2. 关注游戏主界面、菜单、按钮等关键位置
3. 注意保留特殊字符和数字
4. 翻译时保持原文的长度和格式

"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📄 报告已生成: {output_file}")
    return output_file


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动收集游戏中的非中文内容")
    subparsers = parser.add_subparsers(dest="action", help="操作类型")
    
    # collect 子命令
    collect_parser = subparsers.add_parser("collect", help="收集非中文内容")
    collect_parser.add_argument("--package", required=True, help="包名")
    collect_parser.add_argument("--activity", required=True, help="主 Activity")
    collect_parser.add_argument("--serial", help="设备序列号")
    collect_parser.add_argument("--screenshots", help="截图目录")
    collect_parser.add_argument("--output", default="hanization_map.json", help="输出文件")
    collect_parser.add_argument("--report", help="报告输出文件")
    
    # verify 子命令
    verify_parser = subparsers.add_parser("verify", help="验证汉化效果")
    verify_parser.add_argument("--package", required=True, help="包名")
    verify_parser.add_argument("--activity", required=True, help="主 Activity")
    verify_parser.add_argument("--mapping", required=True, help="汉化映射表文件")
    verify_parser.add_argument("--serial", help="设备序列号")
    
    # report 子命令
    report_parser = subparsers.add_parser("report", help="生成报告")
    report_parser.add_argument("--input", required=True, help="汉化映射表文件")
    report_parser.add_argument("--output", default="report.md", help="报告输出文件")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    common.ensure_env()
    
    if args.action == "collect":
        # 收集文本
        items = collect_all_texts(args.package, args.activity, args.serial, args.screenshots)
        
        # 过滤非中文
        non_chinese = filter_non_chinese(items)
        
        # 生成映射表
        generate_translation_mapping(non_chinese, args.output)
        
        # 生成报告
        if args.report:
            generate_report(items, args.report)
        
        print(f"\n✅ 完成! 找到 {len(non_chinese)} 个非中文文本元素")
        print(f"💾 映射表: {args.output}")
        
    elif args.action == "verify":
        result = verify_hanization(args.package, args.activity, args.mapping, args.serial)
        
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)
        
    elif args.action == "report":
        with open(args.input, 'r', encoding='utf-8') as f:
            mapping = json.load(f)
        
        # 重建 TextItem 列表
        items = []
        for trans in mapping.get("translations", []):
            item = TextItem(
                text=trans["original"],
                source=trans["source"],
                bounds=tuple(trans["bounds"]),
                confidence=trans["confidence"],
                is_chinese=False
            )
            items.append(item)
        
        generate_report(items, args.output)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
