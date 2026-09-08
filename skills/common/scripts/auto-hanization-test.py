#!/usr/bin/env python3
"""auto-hanization-test.py — 自动化汉化测试流程

完整流程：
  1. 启动游戏，自动探索收集非中文内容
  2. 生成汉化映射表
  3. 应用汉化替换
  4. 重新启动游戏验证汉化效果
  5. 生成测试报告

用法：
  ./auto-hanization-test.py full --package com.example.game --activity .MainActivity
  ./auto-hanization-test.py collect-only --package com.example.game --activity .MainActivity
  ./auto-hanization-test.py verify-only --package com.example.game --mapping hanization_map.json

原理：
  - 使用 HA4T 的 OCR 识别游戏中的文字
  - 使用 uiautomator2 的无障碍服务获取原生 UI 文本
  - 自动滑动探索不同界面
  - 生成汉化映射表供人工翻译
  - 验证汉化后的效果
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
import common


class AutoHanizationTester:
    """自动化汉化测试器"""
    
    def __init__(self, package_name: str, activity_name: str,
                 device_serial: str = None, output_dir: str = None):
        """
        初始化测试器
        
        Args:
            package_name: 包名
            activity_name: Activity 名
            device_serial: 设备序列号
            output_dir: 输出目录
        """
        self.package_name = package_name
        self.activity_name = activity_name
        self.device_serial = device_serial
        self.output_dir = output_dir or f"crackings/{package_name}/hanization"
        
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 延迟加载依赖
        self._u2 = None
        self._ocr = None
        self._device = None
    
    @property
    def u2(self):
        """延迟加载 uiautomator2"""
        if self._u2 is None:
            import uiautomator2 as u2
            self._u2 = u2
        return self._u2
    
    @property
    def ocr(self):
        """延迟加载 OCR"""
        if self._ocr is None:
            from ha4t.orc import OCR
            self._ocr = OCR()
        return self._ocr
    
    @property
    def device(self):
        """延迟加载设备连接"""
        if self._device is None:
            if self.device_serial:
                self._device = self.u2.connect(self.device_serial)
            else:
                self._device = self.u2.connect()
        return self._device
    
    def start_app(self):
        """启动应用"""
        print(f"🚀 启动应用: {self.package_name}")
        self.device.app_start(self.package_name, self.activity_name)
        time.sleep(3)
    
    def stop_app(self):
        """停止应用"""
        print(f"🛑 停止应用: {self.package_name}")
        self.device.app_stop(self.package_name)
    
    def take_screenshot(self, name: str = None) -> str:
        """
        截图
        
        Args:
            name: 截图名称
            
        Returns:
            str: 截图文件路径
        """
        if name is None:
            name = f"screenshot_{int(time.time())}"
        
        screenshot_dir = os.path.join(self.output_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        
        filepath = os.path.join(screenshot_dir, f"{name}.png")
        img = self.device.screenshot()
        img.save(filepath)
        
        return filepath
    
    def collect_accessibility_texts(self) -> List[Dict]:
        """
        通过无障碍服务收集文本
        
        Returns:
            List[Dict]: 文本元素列表
        """
        items = []
        
        try:
            xml_content = self.device.dump_hierarchy()
            
            import xml.etree.ElementTree as ET
            import re
            
            root = ET.fromstring(xml_content)
            
            for elem in root.iter('node'):
                text = elem.get('text', '').strip()
                content_desc = elem.get('content-desc', '').strip()
                bounds_str = elem.get('bounds', '')
                
                display_text = text or content_desc
                
                if not display_text:
                    continue
                
                if bounds_str:
                    match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds_str)
                    if match:
                        x1, y1, x2, y2 = map(int, match.groups())
                        
                        items.append({
                            "text": display_text,
                            "source": "accessibility",
                            "bounds": [x1, y1, x2, y2],
                            "confidence": 1.0
                        })
            
            print(f"  ✅ 无障碍服务: {len(items)} 个文本")
            
        except Exception as e:
            print(f"  ⚠️ 无障碍服务失败: {e}")
        
        return items
    
    def collect_ocr_texts(self, screenshot_path: str = None) -> List[Dict]:
        """
        通过 OCR 收集文本
        
        Args:
            screenshot_path: 截图路径
            
        Returns:
            List[Dict]: 文本元素列表
        """
        items = []
        
        try:
            import numpy as np
            from PIL import Image
            
            if screenshot_path is None:
                screenshot_path = self.take_screenshot("ocr_temp")
            
            img = Image.open(screenshot_path)
            img_array = np.array(img)
            
            result = self.ocr.ocr(img_array)
            
            if result:
                for line in result:
                    if line:
                        for item_data in line:
                            points = item_data[0]
                            text = item_data[1][0]
                            confidence = item_data[1][1]
                            
                            x_coords = [p[0] for p in points]
                            y_coords = [p[1] for p in points]
                            x1, x2 = min(x_coords), max(x_coords)
                            y1, y2 = min(y_coords), max(y_coords)
                            
                            items.append({
                                "text": text,
                                "source": "ocr",
                                "bounds": [int(x1), int(y1), int(x2), int(y2)],
                                "confidence": confidence
                            })
            
            print(f"  ✅ OCR: {len(items)} 个文本")
            
        except Exception as e:
            print(f"  ⚠️ OCR 失败: {e}")
        
        return items
    
    def collect_current_screen(self) -> List[Dict]:
        """
        收集当前屏幕的所有文本
        
        Returns:
            List[Dict]: 去重后的文本元素列表
        """
        # 截图
        screenshot_path = self.take_screenshot()
        
        # 收集无障碍文本
        accessibility_items = self.collect_accessibility_texts()
        
        # 收集 OCR 文本
        ocr_items = self.collect_ocr_texts(screenshot_path)
        
        # 合并去重
        all_items = []
        seen = set()
        
        for item in accessibility_items + ocr_items:
            key = f"{item['text']}_{item['bounds'][0]}_{item['bounds'][1]}"
            if key not in seen:
                seen.add(key)
                all_items.append(item)
        
        return all_items
    
    def explore_and_collect(self, max_screens: int = 10, 
                           swipe_between: bool = True) -> List[Dict]:
        """
        探索应用并收集文本
        
        Args:
            max_screens: 最大探索屏幕数
            swipe_between: 是否在屏幕间滑动
            
        Returns:
            List[Dict]: 所有收集到的文本
        """
        print(f"🔍 开始探索应用 (最多 {max_screens} 个屏幕)")
        
        all_items = []
        seen_texts = set()
        
        self.start_app()
        
        for screen_idx in range(max_screens):
            print(f"\n📱 屏幕 {screen_idx + 1}/{max_screens}")
            
            # 收集当前屏幕
            items = self.collect_current_screen()
            
            # 去重添加
            new_count = 0
            for item in items:
                if item['text'] not in seen_texts:
                    seen_texts.add(item['text'])
                    item['screen_index'] = screen_idx
                    all_items.append(item)
                    new_count += 1
            
            print(f"  📊 新增 {new_count} 个文本 (总计 {len(all_items)})")
            
            # 滑动到下一个屏幕
            if swipe_between and screen_idx < max_screens - 1:
                self.device.swipe(0.5, 0.7, 0.5, 0.3, duration=0.5)
                time.sleep(1)
        
        print(f"\n✅ 探索完成，共收集 {len(all_items)} 个唯一文本")
        
        return all_items
    
    def filter_non_chinese(self, items: List[Dict]) -> List[Dict]:
        """
        过滤非中文文本
        
        Args:
            items: 所有文本元素
            
        Returns:
            List[Dict]: 非中文文本元素
        """
        import re
        
        non_chinese = []
        
        for item in items:
            text = item['text']
            
            # 跳过空文本
            if not text.strip():
                continue
            
            # 计算中文比例
            chinese_chars = len(re.findall(r'[\u4e00-\u9fff]', text))
            total_chars = len(text)
            
            # 如果中文比例小于50%，认为是非中文
            if total_chars > 0 and chinese_chars / total_chars < 0.5:
                non_chinese.append(item)
        
        print(f"🔤 过滤后: {len(non_chinese)} 个非中文文本")
        
        return non_chinese
    
    def generate_mapping(self, items: List[Dict], 
                        output_file: str = None) -> Dict:
        """
        生成汉化映射表
        
        Args:
            items: 非中文文本元素
            output_file: 输出文件路径
            
        Returns:
            Dict: 汉化映射表
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "hanization_map.json")
        
        mapping = {
            "generated_at": datetime.now().isoformat(),
            "package_name": self.package_name,
            "activity_name": self.activity_name,
            "total_items": len(items),
            "translations": []
        }
        
        for item in items:
            entry = {
                "original": item['text'],
                "source": item['source'],
                "bounds": item['bounds'],
                "confidence": item.get('confidence', 1.0),
                "screen_index": item.get('screen_index', 0),
                "translation": "",  # 需要人工填写
                "context": ""
            }
            mapping["translations"].append(entry)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        
        print(f"💾 汉化映射表已保存: {output_file}")
        
        return mapping
    
    def verify_hanization(self, mapping_file: str) -> Dict:
        """
        验证汉化效果
        
        Args:
            mapping_file: 汉化映射表文件
            
        Returns:
            Dict: 验证结果
        """
        print(f"🔍 开始验证汉化效果")
        
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
            self.start_app()
            time.sleep(3)
            
            current_items = self.collect_current_screen()
            current_texts = [item['text'] for item in current_items]
            
            # 验证每个翻译项
            for trans in mapping.get("translations", []):
                original = trans["original"]
                expected_translation = trans["translation"]
                
                if not expected_translation:
                    continue
                
                result["verified"] += 1
                
                # 检查原文是否已被替换
                if original in current_texts:
                    result["details"].append({
                        "original": original,
                        "status": "failed",
                        "reason": "原文仍然存在"
                    })
                    result["failed"] += 1
                elif expected_translation in current_texts:
                    result["details"].append({
                        "original": original,
                        "translation": expected_translation,
                        "status": "passed"
                    })
                    result["passed"] += 1
                else:
                    result["details"].append({
                        "original": original,
                        "translation": expected_translation,
                        "status": "unknown",
                        "reason": "未找到原文或翻译"
                    })
            
            result["success"] = result["failed"] == 0 and result["verified"] > 0
            
            # 截图保存验证结果
            self.take_screenshot("verification_result")
            
        except Exception as e:
            result["message"] = f"验证失败: {str(e)}"
        
        print(f"📊 验证结果: {result['passed']}/{result['verified']} 通过")
        
        return result
    
    def generate_report(self, items: List[Dict], mapping: Dict = None,
                       output_file: str = None) -> str:
        """
        生成测试报告
        
        Args:
            items: 所有收集到的文本
            mapping: 汉化映射表
            output_file: 报告输出文件
            
        Returns:
            str: 报告文件路径
        """
        if output_file is None:
            output_file = os.path.join(self.output_dir, "hanization_report.md")
        
        non_chinese = self.filter_non_chinese(items)
        
        report = f"""# 自动化汉化测试报告

生成时间: {datetime.now().isoformat()}
应用包名: {self.package_name}

## 统计

- 总文本元素: {len(items)}
- 非中文元素: {len(non_chinese)}
- 中文元素: {len(items) - len(non_chinese)}
- 汉化映射条目: {len(mapping.get('translations', [])) if mapping else 0}

## 非中文内容列表

| # | 文本 | 来源 | 屏幕 | 位置 |
|---|------|------|------|------|
"""
        
        for i, item in enumerate(non_chinese[:50], 1):  # 只显示前50个
            bounds = item['bounds']
            bounds_str = f"({bounds[0]},{bounds[1]})-({bounds[2]},{bounds[3]})"
            screen_idx = item.get('screen_index', '-')
            report += f"| {i} | {item['text']} | {item['source']} | {screen_idx} | {bounds_str} |\n"
        
        if len(non_chinese) > 50:
            report += f"\n*（还有 {len(non_chinese) - 50} 个元素未显示）*\n"
        
        report += f"""

## 操作步骤

1. 查看 `{self.output_dir}/hanization_map.json` 汉化映射表
2. 为每个 `translation` 字段填写中文翻译
3. 运行验证: `./auto-hanization-test.py verify-only --package {self.package_name} --activity {self.activity_name} --mapping {self.output_dir}/hanization_map.json`

## 建议

1. 优先翻译游戏主界面的按钮和菜单
2. 注意保持原文的长度和格式
3. 特殊字符和数字通常不需要翻译
4. 翻译后重新验证确保没有破坏游戏功能

"""
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"📄 报告已生成: {output_file}")
        
        return output_file
    
    def run_full_test(self, max_screens: int = 10) -> Dict:
        """
        运行完整的汉化测试流程
        
        Args:
            max_screens: 最大探索屏幕数
            
        Returns:
            Dict: 测试结果
        """
        print("=" * 60)
        print("🎮 自动化汉化测试 - 完整流程")
        print("=" * 60)
        
        # 1. 探索并收集
        print("\n📱 步骤 1: 探索应用并收集文本")
        all_items = self.explore_and_collect(max_screens)
        
        # 2. 过滤非中文
        print("\n🔤 步骤 2: 过滤非中文文本")
        non_chinese = self.filter_non_chinese(all_items)
        
        # 3. 生成映射表
        print("\n💾 步骤 3: 生成汉化映射表")
        mapping = self.generate_mapping(non_chinese)
        
        # 4. 生成报告
        print("\n📄 步骤 4: 生成测试报告")
        report_path = self.generate_report(all_items, mapping)
        
        # 5. 停止应用
        self.stop_app()
        
        result = {
            "success": True,
            "total_items": len(all_items),
            "non_chinese_items": len(non_chinese),
            "mapping_file": os.path.join(self.output_dir, "hanization_map.json"),
            "report_file": report_path,
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "=" * 60)
        print("✅ 测试完成!")
        print(f"📊 总计: {result['total_items']} 个文本, {result['non_chinese_items']} 个非中文")
        print(f"💾 映射表: {result['mapping_file']}")
        print(f"📄 报告: {result['report_file']}")
        print("=" * 60)
        
        return result


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="自动化汉化测试流程")
    subparsers = parser.add_subparsers(dest="action", help="操作类型")
    
    # full 子命令
    full_parser = subparsers.add_parser("full", help="完整测试流程")
    full_parser.add_argument("--package", required=True, help="包名")
    full_parser.add_argument("--activity", required=True, help="主 Activity")
    full_parser.add_argument("--serial", help="设备序列号")
    full_parser.add_argument("--screens", type=int, default=10, help="最大探索屏幕数")
    full_parser.add_argument("--output", help="输出目录")
    
    # collect-only 子命令
    collect_parser = subparsers.add_parser("collect-only", help="仅收集文本")
    collect_parser.add_argument("--package", required=True, help="包名")
    collect_parser.add_argument("--activity", required=True, help="主 Activity")
    collect_parser.add_argument("--serial", help="设备序列号")
    collect_parser.add_argument("--screens", type=int, default=10, help="最大探索屏幕数")
    collect_parser.add_argument("--output", help="输出目录")
    
    # verify-only 子命令
    verify_parser = subparsers.add_parser("verify-only", help="仅验证汉化")
    verify_parser.add_argument("--package", required=True, help="包名")
    verify_parser.add_argument("--activity", required=True, help="主 Activity")
    verify_parser.add_argument("--mapping", required=True, help="汉化映射表文件")
    verify_parser.add_argument("--serial", help="设备序列号")
    verify_parser.add_argument("--output", help="输出目录")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    common.ensure_env()
    
    # 创建测试器
    tester = AutoHanizationTester(
        package_name=args.package,
        activity_name=args.activity,
        device_serial=args.serial,
        output_dir=args.output
    )
    
    if args.action == "full":
        result = tester.run_full_test(args.screens)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
    elif args.action == "collect-only":
        all_items = tester.explore_and_collect(args.screens)
        non_chinese = tester.filter_non_chinese(all_items)
        mapping = tester.generate_mapping(non_chinese)
        tester.generate_report(all_items, mapping)
        tester.stop_app()
        
    elif args.action == "verify-only":
        result = tester.verify_hanization(args.mapping)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        sys.exit(0 if result["success"] else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
