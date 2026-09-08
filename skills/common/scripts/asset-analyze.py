#!/usr/bin/env python3
"""
asset-analyze.py — 资源分析脚本

用法:
  asset-analyze.py <name> [--type <text|image|font|all>]

功能:
  - 分析资源中的文本内容，识别需要汉化的非中文文本
  - 分析图片资源，识别包含文字的图片
  - 分析字体资源，识别需要替换的字体
  - 生成汉化映射表（hanization_map.yaml）

示例:
  asset-analyze.py KingdomWars2
  asset-analyze.py KingdomWars2 --type text
  asset-analyze.py KingdomWars2 --type image
"""

import sys
import os
import argparse
import re
import json
import yaml
from pathlib import Path
from datetime import datetime

# 添加 lib 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import repo_root, ensure_env, ensure_dir, log_step, log_info, log_success, log_error, log_warn


def get_crack_dir(name):
    return Path(repo_root()) / "crackings" / name


def get_out_dir(name):
    return get_crack_dir(name) / "raw"


def load_manifest(name):
    """加载资源清单"""
    manifest_path = get_out_dir(name) / "resources" / "resource_manifest.yaml"
    if not manifest_path.exists():
        log_error(f"资源清单不存在: {manifest_path}")
        log_info("请先运行 asset-identify.py")
        return None
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def is_chinese(text):
    """检查文本是否包含中文字符"""
    return bool(re.search(r'[\u4e00-\u9fff]', text))


def is_english(text):
    """检查文本是否包含英文字符"""
    return bool(re.search(r'[a-zA-Z]', text))


def analyze_text_content(text):
    """分析文本内容"""
    # 提取所有字符串（去除标签、属性等）
    strings = re.findall(r'>([^<]+)<', text)
    strings = [s.strip() for s in strings if s.strip()]
    
    # 提取属性值
    attr_strings = re.findall(r'(\w+)="([^"]+)"', text)
    for attr, value in attr_strings:
        if value.strip() and not value.startswith(('@', '$', 'android:', 'http')):
            strings.append(value.strip())
    
    return strings


def analyze_strings_xml(filepath):
    """分析Android strings.xml"""
    strings = []
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        # 匹配 <string name="xxx">value</string>
        pattern = r'<string\s+name="([^"]+)"[^>]*>([^<]+)</string>'
        matches = re.findall(pattern, content)
        
        for name, value in matches:
            value = value.strip()
            if value and not is_chinese(value):
                strings.append({
                    "name": name,
                    "value": value,
                    "type": "english" if is_english(value) else "other",
                    "needs_translation": True
                })
    except Exception as e:
        log_error(f"分析 strings.xml 失败: {e}")
    
    return strings


def analyze_xml_files(name):
    """分析所有XML文件"""
    log_step("分析XML文件中的文本")
    
    apktool_dir = get_out_dir(name) / "01-apktool"
    if not apktool_dir.exists():
        log_error("apktool解包目录不存在")
        return []
    
    all_strings = []
    
    # 优先分析 strings.xml
    for filepath in apktool_dir.rglob("strings.xml"):
        log_info(f"分析: {filepath.relative_to(apktool_dir)}")
        strings = analyze_strings_xml(filepath)
        all_strings.extend(strings)
    
    return all_strings


def analyze_json_files(name):
    """分析JSON文件"""
    log_step("分析JSON文件中的文本")
    
    apktool_dir = get_out_dir(name) / "01-apktool"
    if not apktool_dir.exists():
        return []
    
    all_strings = []
    
    for filepath in apktool_dir.rglob("*.json"):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                data = json.load(f)
            
            # 递归提取字符串
            def extract_strings(obj, path=""):
                if isinstance(obj, dict):
                    for key, value in obj.items():
                        new_path = f"{path}.{key}" if path else key
                        extract_strings(value, new_path)
                elif isinstance(obj, list):
                    for i, item in enumerate(obj):
                        extract_strings(item, f"{path}[{i}]")
                elif isinstance(obj, str):
                    if obj.strip() and not is_chinese(obj) and is_english(obj):
                        all_strings.append({
                            "name": path,
                            "value": obj,
                            "type": "english",
                            "needs_translation": True
                        })
            
            extract_strings(data)
        except Exception:
            pass
    
    return all_strings


def analyze_images(name):
    """分析图片资源"""
    log_step("分析图片资源")
    
    apktool_dir = get_out_dir(name) / "01-apktool"
    if not apktool_dir.exists():
        return []
    
    # 包含文字的图片模式
    text_indicators = [
        'splash', 'title', 'banner', 'logo', 'text', 'font', 'word', 'label',
        'button', 'btn_', 'menu', 'dialog', 'popup', 'tip', 'hint', 'help',
        'instruction', 'guide', 'tutorial', 'notice', 'message', 'confirm',
        'start', 'ok', 'cancel', 'close', 'back', 'next', 'prev',
        'shop', 'store', 'buy', 'sell', 'price', 'gold', 'gem', 'coin',
        'level', 'stage', 'chapter', 'episode', 'mission', 'quest',
        'icon', 'avatar', 'character', 'hero', 'unit', 'card',
        'loading', 'progress', 'bar', 'fill', 'empty'
    ]
    
    image_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp', '.gif']
    
    image_analysis = []
    
    for filepath in apktool_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix.lower() in image_extensions:
            name_lower = filepath.name.lower()
            
            # 检查是否可能是含文字的图片
            likely_text = any(indicator in name_lower for indicator in text_indicators)
            
            if likely_text:
                image_analysis.append({
                    "path": str(filepath.relative_to(apktool_dir)),
                    "full_path": str(filepath),
                    "size": filepath.stat().st_size,
                    "likely_has_text": True,
                    "needs_replacement": True,
                    "matched_keywords": [kw for kw in text_indicators if kw in name_lower]
                })
    
    return image_analysis


def analyze_fonts(name):
    """分析字体资源"""
    log_step("分析字体资源")
    
    apktool_dir = get_out_dir(name) / "01-apktool"
    if not apktool_dir.exists():
        return []
    
    font_extensions = ['.ttf', '.otf', '.fnt', '.ttc']
    
    font_analysis = []
    
    for filepath in apktool_dir.rglob("*"):
        if filepath.is_file() and filepath.suffix.lower() in font_extensions:
            name_lower = filepath.name.lower()
            
            # 检查是否需要中文支持
            is_asian_font = any(keyword in name_lower for keyword in ['cjk', 'cn', 'zh', 'chinese', 'han', 'noto'])
            is_latin_font = any(keyword in name_lower for keyword in ['arial', 'helvetica', 'times', 'roboto', 'sans', 'serif'])
            
            font_analysis.append({
                "path": str(filepath.relative_to(apktool_dir)),
                "full_path": str(filepath),
                "size": filepath.stat().st_size,
                "is_asian_font": is_asian_font,
                "is_latin_font": is_latin_font,
                "needs_replacement": is_latin_font,  # 拉丁字体通常需要替换为中文字体
                "recommended_replacement": "LXGWWenKai-Regular.ttf" if is_latin_font else None
            })
    
    return font_analysis


def generate_hanization_map(name, strings, images, fonts):
    """生成汉化映射表"""
    log_step("生成汉化映射表")
    
    hanization_map = {
        "project": name,
        "timestamp": datetime.now().isoformat(),
        "stats": {
            "total_strings": len(strings),
            "total_images": len(images),
            "total_fonts": len(fonts),
            "strings_needing_translation": sum(1 for s in strings if s.get("needs_translation")),
            "images_needing_replacement": sum(1 for i in images if i.get("needs_replacement")),
            "fonts_needing_replacement": sum(1 for f in fonts if f.get("needs_replacement"))
        },
        "text_translations": {
            item["name"]: {
                "original": item["value"],
                "translated": item["value"],  # 占位符，需要人工翻译
                "status": "pending"
            }
            for item in strings
        },
        "image_replacements": {
            item["path"]: {
                "status": "pending",
                "matched_keywords": item.get("matched_keywords", [])
            }
            for item in images
        },
        "font_replacements": {
            item["path"]: {
                "status": "pending",
                "recommended": item.get("recommended_replacement")
            }
            for item in fonts
        }
    }
    
    # 保存YAML
    map_dir = get_out_dir(name) / "hanization"
    ensure_dir(map_dir)
    
    map_path = map_dir / "hanization_map.yaml"
    with open(map_path, 'w', encoding='utf-8') as f:
        yaml.dump(hanization_map, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    log_success(f"汉化映射表已保存: {map_path}")
    
    # 同时保存JSON
    json_path = map_dir / "hanization_map.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(hanization_map, f, indent=2, ensure_ascii=False)
    
    log_success(f"汉化映射表JSON已保存: {json_path}")
    
    # 打印统计
    log_info(f"统计信息:")
    log_info(f"  需要翻译的文本: {hanization_map['stats']['strings_needing_translation']}")
    log_info(f"  需要替换的图片: {hanization_map['stats']['images_needing_replacement']}")
    log_info(f"  需要替换的字体: {hanization_map['stats']['fonts_needing_replacement']}")
    
    return map_path


def main():
    parser = argparse.ArgumentParser(description='资源分析脚本')
    parser.add_argument('name', help='项目名称')
    parser.add_argument('--type', choices=['text', 'image', 'font', 'all'], default='all',
                        help='分析类型 (默认: all)')
    
    args = parser.parse_args()
    
    log_step(f"开始资源分析: {args.name}")
    log_info(f"分析类型: {args.type}")
    
    # 加载资源清单
    manifest = load_manifest(args.name)
    if not manifest:
        return 1
    
    strings = []
    images = []
    fonts = []
    
    # 分析文本
    if args.type in ['text', 'all']:
        strings = analyze_xml_files(args.name)
        strings.extend(analyze_json_files(args.name))
        log_info(f"发现 {len(strings)} 个需要翻译的文本")
    
    # 分析图片
    if args.type in ['image', 'all']:
        images = analyze_images(args.name)
        log_info(f"发现 {len(images)} 个可能含文字的图片")
    
    # 分析字体
    if args.type in ['font', 'all']:
        fonts = analyze_fonts(args.name)
        log_info(f"发现 {len(fonts)} 个字体")
    
    # 生成汉化映射表
    if strings or images or fonts:
        map_path = generate_hanization_map(args.name, strings, images, fonts)
        log_success("资源分析完成")
        return 0
    else:
        log_warn("未发现需要汉化的资源")
        return 0


if __name__ == '__main__':
    ensure_env()
    sys.exit(main())
