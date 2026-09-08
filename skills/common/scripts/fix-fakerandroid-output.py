#!/usr/bin/env python3
"""
fix-fakerandroid-output.py — 修复 FakerAndroid 输出结构
将 app-as-generated/ 下的文件提到上一级，使其符合后续阶段的期望。
"""

import os
import sys
import shutil
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import *


def fix_fakerandroid_output(project_root):
    """
    修复 FakerAndroid 输出结构。
    
    :param project_root: 项目根目录（crackings/<type>/<Name>/project/）
    """
    project_root = Path(project_root)
    if not project_root.exists():
        die(f"项目根目录不存在: {project_root}")
    
    app_as_generated = project_root / "app-as-generated"
    if not app_as_generated.exists():
        log_info("app-as-generated 目录不存在，跳过修复")
        return True
    
    # 检查是否已经修复过
    if (project_root / "app").exists() and (project_root / "build.gradle").exists():
        log_info("项目结构已修复，跳过")
        return True
    
    log_step("修复 FakerAndroid 输出结构")
    
    # 1. 移动根文件
    root_files = ["build.gradle", "settings.gradle", "gradlew", "gradlew.bat", "gradle.properties"]
    for f in root_files:
        src = app_as_generated / f
        dst = project_root / f
        if src.exists() and not dst.exists():
            shutil.move(str(src), str(dst))
            log_info(f"移动: {f}")
    
    # 2. 移动 gradle 目录
    src_gradle = app_as_generated / "gradle"
    dst_gradle = project_root / "gradle"
    if src_gradle.exists() and not dst_gradle.exists():
        shutil.move(str(src_gradle), str(dst_gradle))
        log_info("移动: gradle/")
    
    # 3. 移动 app 目录
    src_app = app_as_generated / "app"
    dst_app = project_root / "app"
    if src_app.exists():
        if dst_app.exists():
            # 合并目录
            for item in src_app.iterdir():
                dst_item = dst_app / item.name
                if item.is_dir():
                    if dst_item.exists():
                        # 合并子目录
                        for sub_item in item.iterdir():
                            dst_sub_item = dst_item / sub_item.name
                            if not dst_sub_item.exists():
                                shutil.move(str(sub_item), str(dst_sub_item))
                    else:
                        shutil.move(str(item), str(dst_item))
                else:
                    if not dst_item.exists():
                        shutil.move(str(item), str(dst_item))
        else:
            shutil.move(str(src_app), str(dst_app))
        log_info("移动: app/")
    
    # 4. 清理空的 app-as-generated 目录
    try:
        if app_as_generated.exists() and not any(app_as_generated.iterdir()):
            app_as_generated.rmdir()
            log_info("删除空目录: app-as-generated/")
    except Exception:
        pass
    
    log_success("FakerAndroid 输出结构修复完成")
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: fix-fakerandroid-output.py <project_root>")
        print("  修复 FakerAndroid 输出结构")
        print("  project_root: crackings/<type>/<Name>/project/")
        sys.exit(1)
    
    project_root = sys.argv[1]
    fix_fakerandroid_output(project_root)


if __name__ == "__main__":
    main()