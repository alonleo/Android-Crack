#!/usr/bin/env python3
"""
assetripper-extract.py — AssetRipper 封装脚本

用法:
  assetripper-extract.py <apk_path> <output_dir> [--lib <il2cpp_so>] [--metadata <metadata_dat>]

功能:
  - 封装 AssetRipper 工具调用
  - 从 Unity APK 中提取资源（纹理、音频、动画、模型等）
  - 如果是 IL2CPP 游戏，同时提取 libil2cpp.so + global-metadata.dat
  - 生成提取报告

示例:
  assetripper-extract.py app.apk ./output
  assetripper-extract.py app.apk ./output --lib libil2cpp.so --metadata global-metadata.dat
"""

import sys
import os
import argparse
import subprocess
import json
import platform
from pathlib import Path
from datetime import datetime

# 添加 lib 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import repo_root, ensure_env, ensure_dir, log_step, log_info, log_success, log_error, log_warn


def get_assetripper_path():
    """获取AssetRipper可执行文件路径"""
    assetripper_path = Path(repo_root()) / "tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free"
    
    if not assetripper_path.exists():
        return None
    
    # 在Linux/Mac上确保有执行权限
    if not os.access(assetripper_path, os.X_OK):
        os.chmod(assetripper_path, 0o755)
    
    return assetripper_path


def extract_assets(apk_path, output_dir, assetripper_path):
    """使用AssetRipper提取资源"""
    log_step("使用AssetRipper提取资源")
    
    ensure_dir(output_dir)
    
    # AssetRipper CLI模式
    # AssetRipper.GUI.Free 支持以下参数：
    # --input <input_path>     输入文件或目录
    # --output <output_path>   输出目录
    # --log                    启用日志
    # --log-path <path>        日志路径
    # --headless               无头模式
    # --port <port>            GUI端口
    
    cmd = [
        str(assetripper_path),
        "--headless",
        "--input", str(apk_path),
        "--output", str(output_dir),
        "--log",
        "--log-path", str(output_dir / "assetripper.log")
    ]
    
    log_info(f"执行命令: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        if result.returncode == 0:
            log_success("AssetRipper提取成功")
            return True
        else:
            log_error(f"AssetRipper提取失败 (退出码: {result.returncode})")
            if result.stderr:
                log_error(f"错误: {result.stderr[:500]}")
            return False
    except subprocess.TimeoutExpired:
        log_error("AssetRipper提取超时（>10分钟）")
        return False
    except Exception as e:
        log_error(f"AssetRipper执行异常: {e}")
        return False


def extract_il2cpp_files(apk_path, output_dir):
    """提取libil2cpp.so和global-metadata.dat"""
    log_step("提取IL2CPP文件")
    
    ensure_dir(output_dir)
    
    # libil2cpp.so 路径
    lib_paths = [
        "lib/arm64-v8a/libil2cpp.so",
        "lib/armeabi-v7a/libil2cpp.so",
        "lib/x86_64/libil2cpp.so",
        "lib/x86/libil2cpp.so",
    ]
    
    # global-metadata.dat 路径
    metadata_paths = [
        "assets/bin/Data/Managed/Metadata/global-metadata.dat",
        "assets/global-metadata.dat",
        "assets/Metadata/global-metadata.dat",
    ]
    
    extracted = {
        "libil2cpp": None,
        "global_metadata": None
    }
    
    try:
        import zipfile
        
        with zipfile.ZipFile(apk_path, 'r') as z:
            for lib_path in lib_paths:
                if lib_path in z.namelist():
                    output_file = output_dir / Path(lib_path).name
                    with z.open(lib_path) as src, open(output_file, 'wb') as dst:
                        dst.write(src.read())
                    log_info(f"已提取: {lib_path} → {output_file}")
                    extracted["libil2cpp"] = str(output_file)
                    break
            
            for metadata_path in metadata_paths:
                if metadata_path in z.namelist():
                    output_file = output_dir / "global-metadata.dat"
                    with z.open(metadata_path) as src, open(output_file, 'wb') as dst:
                        dst.write(src.read())
                    log_info(f"已提取: {metadata_path} → {output_file}")
                    extracted["global_metadata"] = str(output_file)
                    break
    except Exception as e:
        log_error(f"提取IL2CPP文件失败: {e}")
    
    return extracted


def generate_report(apk_path, output_dir, extracted, il2cpp_files):
    """生成提取报告"""
    log_step("生成提取报告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "apk_path": str(apk_path),
        "output_dir": str(output_dir),
        "platform": platform.platform(),
        "assetripper_success": extracted,
        "il2cpp_files": il2cpp_files
    }
    
    # 统计提取的资源
    if Path(output_dir).exists():
        stats = {
            "textures": 0,
            "audio": 0,
            "meshes": 0,
            "animations": 0,
            "other": 0
        }
        
        for filepath in Path(output_dir).rglob("*"):
            if filepath.is_file():
                ext = filepath.suffix.lower()
                if ext in ['.png', '.jpg', '.jpeg', '.tga', '.psd', '.bmp']:
                    stats["textures"] += 1
                elif ext in ['.wav', '.mp3', '.ogg', '.flac', '.aiff']:
                    stats["audio"] += 1
                elif ext in ['.obj', '.fbx', '.mesh', '.asset']:
                    stats["meshes"] += 1
                elif ext in ['.anim', '.controller']:
                    stats["animations"] += 1
                else:
                    stats["other"] += 1
        
        report["stats"] = stats
    
    # 保存报告
    report_path = Path(output_dir) / "extraction_report.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    log_success(f"提取报告已保存: {report_path}")
    
    return report


def main():
    parser = argparse.ArgumentParser(description='AssetRipper 封装脚本')
    parser.add_argument('apk', help='Unity APK 文件路径')
    parser.add_argument('output', help='输出目录')
    parser.add_argument('--skip-il2cpp', action='store_true',
                        help='跳过IL2CPP文件提取')
    
    args = parser.parse_args()
    
    # 检查 APK 文件
    apk_path = Path(args.apk)
    if not apk_path.exists():
        log_error(f"APK 文件不存在: {apk_path}")
        return 1
    
    output_dir = Path(args.output)
    ensure_dir(output_dir)
    
    log_step("AssetRipper 资源提取")
    log_info(f"APK: {apk_path}")
    log_info(f"输出: {output_dir}")
    
    # 获取 AssetRipper 路径
    assetripper_path = get_assetripper_path()
    if not assetripper_path:
        log_error("AssetRipper 未安装")
        log_info("请从 https://github.com/AssetRipper/AssetRipper 下载")
        log_info("并放到 tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free")
        return 1
    
    log_info(f"AssetRipper: {assetripper_path}")
    
    # 提取资源
    extracted = extract_assets(apk_path, output_dir, assetripper_path)
    
    # 提取 IL2CPP 文件（如果不是 skip）
    il2cpp_files = {}
    if not args.skip_il2cpp:
        il2cpp_files = extract_il2cpp_files(apk_path, output_dir)
    
    # 生成报告
    report = generate_report(apk_path, output_dir, extracted, il2cpp_files)
    
    if extracted:
        log_success("资源提取完成")
        log_info(f"输出目录: {output_dir}")
        log_info(f"提取报告: {output_dir / 'extraction_report.json'}")
        return 0
    else:
        log_error("资源提取失败")
        return 1


if __name__ == '__main__':
    ensure_env()
    sys.exit(main())
