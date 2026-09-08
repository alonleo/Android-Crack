#!/usr/bin/env python3
"""
asset-identify.py — 资源识别脚本

用法:
  asset-identify.py <name> [--type <android|unity>]

功能:
  - 识别APK中的所有资源（图片、文本、字体、音频等）
  - 支持Android APK（apktool解包产物）和Unity资源（data.unity3d）
  - 集成AssetRipper工具用于Unity资源提取
  - 生成资源清单（resource_manifest.yaml）

示例:
  asset-identify.py KingdomWars2
  asset-identify.py MyUnityProject --type unity
"""

import sys
import os
import argparse
import subprocess
import re
import json
import yaml
from pathlib import Path
from datetime import datetime

# 添加 lib 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import repo_root, ensure_env, ensure_dir, log_step, log_info, log_success, log_error, log_warn


# 资源类型定义
RESOURCE_TYPES = {
    "image": {
        "extensions": [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif", ".tga", ".tif"],
        "description": "图片资源",
        "indicator_keywords": ["icon", "image", "bg", "background", "splash", "title", "logo", "banner"]
    },
    "text": {
        "extensions": [".xml", ".json", ".txt", ".properties", ".yaml", ".yml"],
        "description": "文本资源",
        "indicator_keywords": ["string", "strings", "text", "locale", "lang", "translation"]
    },
    "font": {
        "extensions": [".ttf", ".otf", ".fnt", ".ttc"],
        "description": "字体资源",
        "indicator_keywords": ["font", "typeface"]
    },
    "audio": {
        "extensions": [".mp3", ".ogg", ".wav", ".flac", ".m4a", ".aac"],
        "description": "音频资源",
        "indicator_keywords": ["audio", "sound", "music", "bgm", "sfx"]
    },
    "video": {
        "extensions": [".mp4", ".avi", ".mov", ".mkv", ".webm"],
        "description": "视频资源",
        "indicator_keywords": ["video", "movie", "clip", "cutscene"]
    },
    "model": {
        "extensions": [".mesh", ".asset", ".unity3d", ".prefab", ".fbx", ".obj"],
        "description": "3D模型资源",
        "indicator_keywords": ["mesh", "model", "character", "prefab"]
    },
    "shader": {
        "extensions": [".shader", ".compute", ".hlsl", ".glsl", ".cginc"],
        "description": "着色器资源",
        "indicator_keywords": ["shader", "compute"]
    }
}


def get_crack_dir(name):
    return Path(repo_root()) / "crackings" / name


def get_out_dir(name):
    return get_crack_dir(name) / "raw"


def get_apktool_dir(name):
    return get_out_dir(name) / "01-apktool"


def get_assets_dir(name):
    return get_apktool_dir(name) / "assets"


def get_res_dir(name):
    return get_apktool_dir(name) / "res"


def identify_asset_type(filepath):
    """识别资源类型"""
    ext = filepath.suffix.lower()
    name_lower = filepath.name.lower()
    
    for res_type, info in RESOURCE_TYPES.items():
        if ext in info["extensions"]:
            return res_type, info["description"]
    
    # 根据文件名关键词识别
    for res_type, info in RESOURCE_TYPES.items():
        for keyword in info["indicator_keywords"]:
            if keyword in name_lower:
                return res_type, info["description"]
    
    return "unknown", "未知资源"


def find_resources_in_dir(directory, recursive=True):
    """查找目录中的所有资源"""
    resources = []
    
    if not directory.exists():
        return resources
    
    if recursive:
        for filepath in directory.rglob("*"):
            if filepath.is_file():
                res_type, desc = identify_asset_type(filepath)
                if res_type != "unknown":
                    resources.append({
                        "path": str(filepath.relative_to(directory)),
                        "full_path": str(filepath),
                        "type": res_type,
                        "description": desc,
                        "size": filepath.stat().st_size
                    })
    else:
        for filepath in directory.iterdir():
            if filepath.is_file():
                res_type, desc = identify_asset_type(filepath)
                if res_type != "unknown":
                    resources.append({
                        "path": str(filepath.relative_to(directory)),
                        "full_path": str(filepath),
                        "type": res_type,
                        "description": desc,
                        "size": filepath.stat().st_size
                    })
    
    return resources


def scan_android_resources(name):
    """扫描Android资源"""
    log_step("扫描Android资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error(f"apktool解包目录不存在: {apktool_dir}")
        return None
    
    resources = {
        "android_resources": [],
        "assets": [],
        "raw": []
    }
    
    # 扫描 res/ 目录
    res_dir = apktool_dir / "res"
    if res_dir.exists():
        log_info(f"扫描 res/ 目录: {res_dir}")
        resources["android_resources"] = find_resources_in_dir(res_dir)
    
    # 扫描 assets/ 目录
    assets_dir = apktool_dir / "assets"
    if assets_dir.exists():
        log_info(f"扫描 assets/ 目录: {assets_dir}")
        resources["assets"] = find_resources_in_dir(assets_dir)
    
    # 扫描 raw/ 目录
    raw_dir = res_dir / "raw"
    if raw_dir.exists():
        log_info(f"扫描 raw/ 目录: {raw_dir}")
        resources["raw"] = find_resources_in_dir(raw_dir)
    
    return resources


def scan_unity_resources(name):
    """扫描Unity资源"""
    log_step("扫描Unity资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error(f"apktool解包目录不存在: {apktool_dir}")
        return None
    
    resources = {
        "unity_data": [],
        "unity_assets": [],
        "unity_cache": []
    }
    
    # 扫描 data.unity3d
    data_unity3d = apktool_dir / "assets" / "bin" / "Data" / "data.unity3d"
    if data_unity3d.exists():
        log_info(f"找到 data.unity3d: {data_unity3d}")
        resources["unity_data"].append({
            "path": str(data_unity3d.relative_to(apktool_dir)),
            "full_path": str(data_unity3d),
            "type": "model",
            "description": "Unity 主资源包",
            "size": data_unity3d.stat().st_size
        })
    
    # 扫描 sharedassets*.resource
    for filepath in (apktool_dir / "assets").rglob("sharedassets*.resource"):
        if filepath.is_file():
            resources["unity_assets"].append({
                "path": str(filepath.relative_to(apktool_dir)),
                "full_path": str(filepath),
                "type": "model",
                "description": "Unity 场景资源",
                "size": filepath.stat().st_size
            })
    
    # 扫描 resources.resource
    res_resource = apktool_dir / "assets" / "resources.resource"
    if res_resource.exists():
        resources["unity_cache"].append({
            "path": str(res_resource.relative_to(apktool_dir)),
            "full_path": str(res_resource),
            "type": "model",
            "description": "Unity Resources 缓存",
            "size": res_resource.stat().st_size
        })
    
    return resources


def extract_unity_with_assetripper(name, output_dir):
    """使用AssetRipper提取Unity资源"""
    log_step("使用AssetRipper提取Unity资源")
    
    apktool_dir = get_apktool_dir(name)
    if not apktool_dir.exists():
        log_error(f"apktool解包目录不存在: {apktool_dir}")
        return False
    
    # 查找AssetRipper可执行文件
    assetripper_path = Path(repo_root()) / "tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free"
    if not assetripper_path.exists():
        log_warn("AssetRipper可执行文件不存在")
        log_info("请从 https://github.com/AssetRipper/AssetRipper 下载")
        return False
    
    # 查找Unity资源包
    data_unity3d = apktool_dir / "assets" / "bin" / "Data" / "data.unity3d"
    if not data_unity3d.exists():
        log_warn("data.unity3d 不存在")
        return False
    
    log_info(f"使用AssetRipper提取: {data_unity3d}")
    log_info(f"输出目录: {output_dir}")
    
    ensure_dir(output_dir)
    
    # AssetRipper CLI模式（headless）
    # 注意：AssetRipper需要导出整个项目，这里我们只导出资源
    cmd = [
        str(assetripper_path),
        "--headless",
        "--input", str(data_unity3d),
        "--output", str(output_dir),
        "--log",
        "--log-path", str(output_dir / "assetripper.log")
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            log_success("AssetRipper提取成功")
            return True
        else:
            log_error(f"AssetRipper提取失败: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        log_error("AssetRipper提取超时")
        return False
    except Exception as e:
        log_error(f"AssetRipper执行异常: {e}")
        return False


def save_manifest(name, resources, assetripper_dir=None):
    """保存资源清单"""
    log_step("保存资源清单")
    
    manifest_dir = get_out_dir(name) / "resources"
    ensure_dir(manifest_dir)
    
    # 统计信息
    stats = {
        "total": 0,
        "by_type": {}
    }
    
    for category, items in resources.items():
        if isinstance(items, list):
            stats["total"] += len(items)
            for item in items:
                res_type = item.get("type", "unknown")
                stats["by_type"][res_type] = stats["by_type"].get(res_type, 0) + 1
    
    # 清单数据
    manifest = {
        "project": name,
        "timestamp": datetime.now().isoformat(),
        "stats": stats,
        "resources": resources,
        "assetripper_output": str(assetripper_dir) if assetripper_dir else None
    }
    
    # 保存为YAML
    manifest_path = manifest_dir / "resource_manifest.yaml"
    with open(manifest_path, 'w', encoding='utf-8') as f:
        yaml.dump(manifest, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
    
    log_success(f"资源清单已保存: {manifest_path}")
    
    # 同时保存为JSON
    json_path = manifest_dir / "resource_manifest.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    log_success(f"资源清单JSON已保存: {json_path}")
    
    # 打印统计
    log_info(f"总资源数: {stats['total']}")
    log_info("按类型统计:")
    for res_type, count in stats["by_type"].items():
        log_info(f"  {res_type}: {count}")
    
    return manifest_path


def main():
    parser = argparse.ArgumentParser(description='资源识别脚本')
    parser.add_argument('name', help='项目名称')
    parser.add_argument('--type', choices=['android', 'unity', 'auto'], default='auto',
                        help='APK类型 (默认: auto自动判断)')
    parser.add_argument('--use-assetripper', action='store_true',
                        help='使用AssetRipper提取Unity资源')
    
    args = parser.parse_args()
    
    # 自动判断类型
    if args.type == 'auto':
        apktool_dir = get_apktool_dir(args.name)
        data_unity3d = apktool_dir / "assets" / "bin" / "Data" / "data.unity3d"
        if data_unity3d.exists():
            args.type = 'unity'
        else:
            args.type = 'android'
    
    log_step(f"开始资源识别: {args.name}")
    log_info(f"APK类型: {args.type}")
    
    # 扫描资源
    if args.type == 'unity':
        resources = scan_unity_resources(args.name)
    else:
        resources = scan_android_resources(args.name)
    
    if not resources:
        log_error("资源扫描失败")
        return 1
    
    # 如果是Unity且需要使用AssetRipper
    assetripper_dir = None
    if args.type == 'unity' and args.use_assetripper:
        assetripper_dir = get_out_dir(args.name) / "unity_extracted"
        extract_unity_with_assetripper(args.name, assetripper_dir)
    
    # 保存清单
    manifest_path = save_manifest(args.name, resources, assetripper_dir)
    
    if manifest_path:
        log_success("资源识别完成")
        return 0
    else:
        log_error("资源识别失败")
        return 1


if __name__ == '__main__':
    ensure_env()
    sys.exit(main())
