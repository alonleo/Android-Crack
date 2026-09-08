#!/usr/bin/env python3
"""
merge-split-apk.py — 合并 split APK（.xapk）到单个 APK
用于处理 APKPure 的 .xapk 格式，其中主 APK 和 config APK 分离。
"""

import os
import sys
import zipfile
import tempfile
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import *


def merge_xapk(xapk_path, output_dir=None):
    """
    合并 .xapk 文件中的主 APK 和 config APK 到单个 APK。
    
    :param xapk_path: .xapk 文件路径
    :param output_dir: 输出目录（默认为 xapk 同级目录）
    :return: 合并后的 APK 路径
    """
    xapk_path = Path(xapk_path)
    if not xapk_path.exists():
        die(f"找不到 .xapk 文件: {xapk_path}")
    
    if output_dir is None:
        output_dir = xapk_path.parent
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    # 读取 xapk 内容
    with zipfile.ZipFile(xapk_path, 'r') as z:
        namelist = z.namelist()
        
        # 找到主 APK（最大的 .apk 文件）
        apk_files = [n for n in namelist if n.endswith('.apk')]
        if not apk_files:
            die("在 .xapk 中找不到 .apk 文件")
        
        # 按文件大小排序，找到主 APK
        apk_sizes = [(n, z.getinfo(n).file_size) for n in apk_files]
        apk_sizes.sort(key=lambda x: x[1], reverse=True)
        main_apk_name = apk_sizes[0][0]
        
        log_info(f"主 APK: {main_apk_name} ({apk_sizes[0][1] / 1024 / 1024:.1f} MB)")
        
        # 提取主 APK 到临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            main_apk_path = Path(temp_dir) / "main.apk"
            with z.open(main_apk_name) as src, open(main_apk_path, 'wb') as dst:
                shutil.copyfileobj(src, dst)
            
            # 检查是否有其他 APK（config APK）
            config_apks = [n for n in apk_files if n != main_apk_name]
            
            if not config_apks:
                # 没有 config APK，直接复制主 APK
                output_name = xapk_path.stem + ".apk"
                output_path = output_dir / output_name
                shutil.copy2(main_apk_path, output_path)
                log_success(f"无 config APK，直接输出: {output_path}")
                return str(output_path)
            
            # 有 config APK，需要合并
            log_info(f"发现 {len(config_apks)} 个 config APK，开始合并...")
            
            # 创建合并后的 APK
            merged_path = Path(temp_dir) / "merged.apk"
            
            with zipfile.ZipFile(main_apk_path, 'r') as main_zip:
                with zipfile.ZipFile(merged_path, 'w', zipfile.ZIP_DEFLATED) as merged_zip:
                    # 复制主 APK 的所有文件
                    for item in main_zip.namelist():
                        data = main_zip.read(item)
                        merged_zip.writestr(item, data)
                    
                    # 合并 config APK 的文件
                    for config_apk_name in config_apks:
                        log_info(f"处理 config APK: {config_apk_name}")
                        config_apk_path = Path(temp_dir) / config_apk_name
                        with z.open(config_apk_name) as src, open(config_apk_path, 'wb') as dst:
                            shutil.copyfileobj(src, dst)
                        
                        with zipfile.ZipFile(config_apk_path, 'r') as config_zip:
                            for item in config_zip.namelist():
                                # 跳过 META-INF 中的签名文件（会冲突）
                                if item.startswith('META-INF/') and item.endswith(('.SF', '.RSA', '.DSA')):
                                    continue
                                data = config_zip.read(item)
                                merged_zip.writestr(item, data)
            
            # 输出合并后的 APK
            output_name = xapk_path.stem + ".apk"
            output_path = output_dir / output_name
            shutil.copy2(merged_path, output_path)
            
            log_success(f"合并完成: {output_path}")
            log_info(f"文件大小: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
            
            return str(output_path)


def main():
    if len(sys.argv) < 2:
        print("用法: merge-split-apk.py <input.xapk> [output_dir]")
        print("  合并 split APK (.xapk) 到单个 APK 文件")
        sys.exit(1)
    
    xapk_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = merge_xapk(xapk_path, output_dir)
    print(result)


if __name__ == "__main__":
    main()