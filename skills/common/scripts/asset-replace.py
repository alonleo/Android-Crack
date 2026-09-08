#!/usr/bin/env python3
"""
asset-replace.py — 资源替换脚本

用法:
  asset-replace.py <name> [--type <text|image|font|all>]

功能:
  - 替换图片资源（汉化图片）
  - 替换文本资源（汉化非中文文本）
  - 替换字体资源（替换为中文字体）
  - 根据 hanization_map.yaml 或 hanization_map.json 进行替换

示例:
  asset-replace.py KingdomWars2
  asset-replace.py KingdomWars2 --type text
  asset-replace.py KingdomWars2 --type image
  asset-replace.py KingdomWars2 --type font
"""

import sys
import os
import argparse
import shutil
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


def get_apktool_dir(name):
    return get_out_dir(name) / "01-apktool"


def load_hanization_map(name):
    """加载汉化映射表"""
    map_dir = get_out_dir(name) / "hanization"
    
    # 优先加载JSON
    json_path = map_dir / "hanization_map.json"
    if json_path.exists():
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    # 其次加载YAML
    yaml_path = map_dir / "hanization_map.yaml"
    if yaml_path.exists():
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    log_error("汉化映射表不存在")
    log_info("请先运行 asset-analyze.py")
    return None


def replace_text(name, map_data):
    """替换文本资源"""
    log_step("替换文本资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error("apktool解包目录不存在")
        return 0
    
    text_translations = map_data.get("text_translations", {})
    if not text_translations:
        log_warn("无文本翻译数据")
        return 0
    
    replaced_count = 0
    
    # 替换 strings.xml
    for strings_file in apktool_dir.rglob("strings.xml"):
        try:
            with open(strings_file, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            original = content
            
            for key, info in text_translations.items():
                if info.get("status") != "translated":
                    continue
                
                translated = info.get("translated", "")
                if not translated or translated == info.get("original"):
                    continue
                
                # 替换 <string name="key">value</string>
                pattern = f'<string name="{re.escape(key)}"[^>]*>{re.escape(info["original"])}</string>'
                replacement = f'<string name="{key}">{translated}</string>'
                content = re.sub(pattern, replacement, content)
            
            if content != original:
                with open(strings_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                replaced_count += 1
                log_info(f"已替换: {strings_file.relative_to(apktool_dir)}")
        except Exception as e:
            log_error(f"替换 {strings_file} 失败: {e}")
    
    log_success(f"共替换 {replaced_count} 个 strings.xml 文件")
    return replaced_count


def replace_images(name, map_data):
    """替换图片资源"""
    log_step("替换图片资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error("apktool解包目录不存在")
        return 0
    
    # 替换图片目录
    replacements_dir = get_out_dir(name) / "06-images" / "replacements"
    if not replacements_dir.exists():
        log_warn("图片替换目录不存在")
        log_info(f"请将翻译后的图片放入: {replacements_dir}")
        return 0
    
    replaced_count = 0
    
    # 查找替换目录中的所有图片
    for replacement_file in replacements_dir.rglob("*"):
        if replacement_file.is_file() and replacement_file.suffix.lower() in ['.png', '.jpg', '.jpeg', '.webp', '.bmp']:
            # 计算相对路径
            rel_path = replacement_file.relative_to(replacements_dir)
            
            # 目标文件路径
            target_file = apktool_dir / rel_path
            
            if target_file.exists():
                # 备份原文件
                backup_file = target_file.with_suffix(target_file.suffix + ".bak")
                if not backup_file.exists():
                    shutil.copy2(target_file, backup_file)
                
                # 替换文件
                shutil.copy2(replacement_file, target_file)
                replaced_count += 1
                log_info(f"已替换: {rel_path}")
            else:
                log_warn(f"目标文件不存在: {rel_path}")
    
    log_success(f"共替换 {replaced_count} 个图片")
    return replaced_count


def replace_fonts(name, map_data):
    """替换字体资源"""
    log_step("替换字体资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error("apktool解包目录不存在")
        return 0
    
    font_replacements = map_data.get("font_replacements", {})
    if not font_replacements:
        log_warn("无字体替换数据")
        return 0
    
    # 查找中文字体文件
    chinese_font_candidates = [
        Path(repo_root()) / "skills/common/scripts/template-files/LXGWWenKai-Regular.ttf",
        Path(repo_root()) / "tools/assets/fonts/LXGWWenKai-Regular.ttf",
        Path(repo_root()) / "fonts/LXGWWenKai-Regular.ttf",
    ]
    
    chinese_font = None
    for candidate in chinese_font_candidates:
        if candidate.exists():
            chinese_font = candidate
            break
    
    if not chinese_font:
        log_warn("未找到中文字体文件 LXGWWenKai-Regular.ttf")
        log_info("请从 https://github.com/lxgw/LxgwWenKai 下载并放到 fonts/ 目录")
        return 0
    
    replaced_count = 0
    
    for font_path, info in font_replacements.items():
        if info.get("status") != "translated":
            continue
        
        target_file = apktool_dir / font_path
        if not target_file.exists():
            log_warn(f"字体文件不存在: {font_path}")
            continue
        
        # 备份原文件
        backup_file = target_file.with_suffix(target_file.suffix + ".bak")
        if not backup_file.exists():
            shutil.copy2(target_file, backup_file)
        
        # 替换字体
        shutil.copy2(chinese_font, target_file)
        replaced_count += 1
        log_info(f"已替换字体: {font_path}")
    
    log_success(f"共替换 {replaced_count} 个字体")
    return replaced_count


def main():
    parser = argparse.ArgumentParser(description='资源替换脚本')
    parser.add_argument('name', help='项目名称')
    parser.add_argument('--type', choices=['text', 'image', 'font', 'all'], default='all',
                        help='替换类型 (默认: all)')
    
    args = parser.parse_args()
    
    log_step(f"开始资源替换: {args.name}")
    log_info(f"替换类型: {args.type}")
    
    # 加载汉化映射表
    map_data = load_hanization_map(args.name)
    if not map_data:
        return 1
    
    total_replaced = 0
    
    # 替换文本
    if args.type in ['text', 'all']:
        count = replace_text(args.name, map_data)
        total_replaced += count
    
    # 替换图片
    if args.type in ['image', 'all']:
        count = replace_images(args.name, map_data)
        total_replaced += count
    
    # 替换字体
    if args.type in ['font', 'all']:
        count = replace_fonts(args.name, map_data)
        total_replaced += count
    
    if total_replaced > 0:
        log_success(f"资源替换完成，共替换 {total_replaced} 个资源")
        log_info("下一步：")
        log_info("  1. 运行 sub-stage-as-build.py 重打包（gradle assembleRelease）")
        log_info("  2. 运行 sub-stage-final-check.py 真机验证")
        return 0
    else:
        log_warn("未替换任何资源")
        return 0


if __name__ == '__main__':
    ensure_env()
    sys.exit(main())
