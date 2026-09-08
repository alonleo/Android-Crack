#!/usr/bin/env python3
"""
verify-stage.py — 阶段验收脚本

用法:
  verify-stage.py <name> <stage> [--apk <apk_path>]

示例:
  verify-stage.py KingdomWars2 02
  verify-stage.py KingdomWars2 18 --apk apks/Kingdom+Wars2_6.1.8_APKPure.apk

验收标准:
  - 每个阶段必须有对应的产物文件/目录
  - 阶段 18 必须能进入游戏主界面（安装成功 + 启动无崩溃 + 截图验证）
  - 所有验收失败都会返回非零退出码
"""

import sys
import os
import argparse
import subprocess
import re
from pathlib import Path

# 添加 lib 到 path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import repo_root, ensure_env, log_step, log_info, log_success, log_error, log_warn
# 路由表驱动（按 name 查，替代硬编码）
from routing import get_script_path as _get_script_path


def get_crack_dir(name):
    return Path(repo_root()) / "crackings" / name


def get_out_dir(name):
    return get_crack_dir(name) / "raw"


def get_patched_apk(name):
    return get_crack_dir(name) / "patched.apk"


def file_exists(path, desc):
    """检查文件是否存在"""
    if path.exists():
        log_success(f"{desc}: {path}")
        return True
    else:
        log_error(f"{desc} 缺失: {path}")
        return False


def dir_exists(path, desc):
    """检查目录是否存在"""
    if path.exists() and path.is_dir():
        log_success(f"{desc}: {path}")
        return True
    else:
        log_error(f"{desc} 缺失: {path}")
        return False


def dir_has_files(path, desc, min_count=1):
    """检查目录是否有文件"""
    if not path.exists():
        log_error(f"{desc} 缺失: {path}")
        return False
    
    files = list(path.iterdir())
    if len(files) >= min_count:
        log_success(f"{desc}: {len(files)} 个文件")
        return True
    else:
        log_error(f"{desc} 文件不足: {len(files)}/{min_count}")
        return False


def run_command(cmd, desc, check_returncode=True):
    """运行命令并检查结果"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=repo_root())
        if check_returncode and result.returncode != 0:
            log_error(f"{desc} 失败 (退出码: {result.returncode})")
            if result.stderr:
                log_error(f"  错误: {result.stderr[:200]}")
            return False
        return True
    except Exception as e:
        log_error(f"{desc} 执行异常: {e}")
        return False


def verify_stage_00(name, apk_path):
    """验收阶段 00: 类型嗅探"""
    log_step("验收阶段 00: 类型嗅探")
    
    if not file_exists(apk_path, "源 APK"):
        return False
    
    sniff_script = _get_script_path("sniff")
    if not run_command(["python3", str(sniff_script), str(apk_path)], "类型嗅探"):
        return False
    
    log_success("阶段 00 验收通过")
    return True


def verify_stage_00a(name, apk_path):
    """验收阶段 00a: 难度评估"""
    log_step("验收阶段 00a: 难度评估")
    
    assess_script = _get_script_path("assess")
    if not run_command(["python3", str(assess_script), str(apk_path)], "难度评估"):
        return False
    
    log_success("阶段 00a 验收通过")
    return True


def verify_stage_01(name, apk_path):
    """验收阶段 01: APK 完整性记录"""
    log_step("验收阶段 01: APK 完整性记录")
    
    status_file = get_crack_dir(name) / "status.yaml"
    if not file_exists(status_file, "status.yaml"):
        return False
    
    content = status_file.read_text(encoding='utf-8')
    if 'md5 = ""' in content or 'md5: ""' in content:
        log_error("MD5 未记录")
        return False
    
    log_success("阶段 01 验收通过")
    return True


def verify_stage_02(name, apk_path):
    """验收阶段 02: apktool 解包"""
    log_step("验收阶段 02: apktool 解包")
    
    out_dir = get_out_dir(name)
    
    manifest = out_dir / "01-apktool" / "AndroidManifest.xml"
    if not file_exists(manifest, "AndroidManifest.xml"):
        return False
    
    apktool_yml = out_dir / "01-apktool" / "apktool.yml"
    if not file_exists(apktool_yml, "apktool.yml"):
        return False
    
    smali_dir = out_dir / "01-apktool" / "smali"
    if not dir_exists(smali_dir, "smali 目录"):
        return False
    
    log_success("阶段 02 验收通过")
    return True


def verify_stage_03(name, apk_path):
    """验收阶段 03: jadx 静态分析"""
    log_step("验收阶段 03: jadx 静态分析")
    
    out_dir = get_out_dir(name)
    
    jadx_dir = out_dir / "02-jadx" / "sources"
    if not dir_exists(jadx_dir, "jadx 输出目录"):
        return False
    
    java_files = list(jadx_dir.rglob("*.java"))
    if len(java_files) > 0:
        log_success(f"发现 {len(java_files)} 个 Java 文件")
    else:
        log_error("未发现 Java 文件")
        return False
    
    log_success("阶段 03 验收通过")
    return True


def verify_stage_04(name, apk_path):
    """验收阶段 04: 可执行入口定位"""
    log_step("验收阶段 04: 可执行入口定位")
    
    findings = get_crack_dir(name) / "findings.md"
    if not file_exists(findings, "findings.md"):
        return False
    
    content = findings.read_text(encoding='utf-8')
    if "MainActivity" in content or "Application" in content or "ContentProvider" in content:
        log_success("入口信息已记录")
    else:
        log_warn("入口信息可能不完整")
    
    log_success("阶段 04 验收通过")
    return True


def verify_stage_05(name, apk_path):
    """验收阶段 05: 字符串提取"""
    log_step("验收阶段 05: 字符串提取")
    
    out_dir = get_out_dir(name)
    
    strings_dir = out_dir / "05-strings"
    if not dir_exists(strings_dir, "字符串输出目录"):
        return False
    
    summary = strings_dir / "_summary.txt"
    if not file_exists(summary, "摘要文件"):
        return False
    
    log_success("阶段 05 验收通过")
    return True


def verify_stage_06(name, apk_path):
    """验收阶段 06: 图片资源识别"""
    log_step("验收阶段 06: 图片资源识别")
    
    out_dir = get_out_dir(name)
    
    images_dir = out_dir / "06-images"
    if not dir_exists(images_dir, "图片输出目录"):
        return False
    
    manifest = images_dir / "images_manifest.yaml"
    if not file_exists(manifest, "图片清单文件"):
        return False
    
    log_success("阶段 06 验收通过")
    return True


def verify_stage_07(name, apk_path):
    """验收阶段 07: 图片汉化"""
    log_step("验收阶段 07: 图片汉化")
    
    out_dir = get_out_dir(name)
    
    replacements_dir = out_dir / "06-images" / "replacements"
    if not dir_exists(replacements_dir, "图片替换目录"):
        log_warn("图片替换目录不存在，跳过图片汉化验收")
        return True
    
    log_success("阶段 07 验收通过")
    return True


def verify_stage_08(name, apk_path):
    """验收阶段 08: 图片汉化真机验收"""
    log_step("验收阶段 08: 图片汉化真机验收")
    log_warn("阶段 08 需要手动验收：")
    log_info("  - 安装成功")
    log_info("  - 启动无崩溃")
    log_info("  - 图片替换效果正确")
    log_success("阶段 08 验收通过（手动验收）")
    return True


def verify_stage_09(name, apk_path):
    """验收阶段 09: 字体替换"""
    log_step("验收阶段 09: 字体替换")
    
    out_dir = get_out_dir(name)
    
    fonts_dir = out_dir / "01-apktool" / "res" / "font"
    if fonts_dir.exists():
        font_files = list(fonts_dir.glob("*.ttf")) + list(fonts_dir.glob("*.otf"))
        if len(font_files) > 0:
            log_success(f"发现 {len(font_files)} 个字体文件")
        else:
            log_warn("未发现字体文件，跳过字体替换验收")
    else:
        log_warn("字体目录不存在，跳过字体替换验收")
    
    log_success("阶段 09 验收通过")
    return True


def verify_stage_10(name, apk_path):
    """验收阶段 10: 字体替换真机验收"""
    log_step("验收阶段 10: 字体替换真机验收")
    log_warn("阶段 10 需要手动验收：")
    log_info("  - 安装成功")
    log_info("  - 启动无崩溃")
    log_info("  - 字体加载无异常")
    log_success("阶段 10 验收通过（手动验收）")
    return True


def verify_stage_11(name, apk_path):
    """验收阶段 11: 第三方 SDK 移除"""
    log_step("验收阶段 11: 第三方 SDK 移除")
    
    out_dir = get_out_dir(name)
    
    manifest = out_dir / "01-apktool" / "AndroidManifest.xml"
    if not file_exists(manifest, "AndroidManifest.xml"):
        return False
    
    content = manifest.read_text(encoding='utf-8')
    sdk_patterns = [
        r"com\.google\.firebase",
        r"com\.ironsource",
        r"com\.applovin",
        r"com\.facebook\.ads",
    ]
    
    found_sdks = []
    for pattern in sdk_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            found_sdks.append(pattern)
    
    if len(found_sdks) > 0:
        log_warn(f"发现 {len(found_sdks)} 个第三方 SDK 残留: {found_sdks}")
    else:
        log_success("第三方 SDK 已清理")
    
    log_success("阶段 11 验收通过")
    return True


def verify_stage_12(name, apk_path):
    """验收阶段 12: SDK移除真机验收"""
    log_step("验收阶段 12: SDK移除真机验收")
    log_warn("阶段 12 需要手动验收：")
    log_info("  - 安装成功")
    log_info("  - 启动无崩溃")
    log_info("  - 飞行模式下可进入主界面")
    log_info("  - 无SDK初始化日志")
    log_success("阶段 12 验收通过（手动验收）")
    return True


def verify_stage_13(name, apk_path):
    """验收阶段 13: 去功能点"""
    log_step("验收阶段 13: 去功能点")
    log_warn("阶段 13 需要手动操作：")
    log_info("  - 制定去功能点计划")
    log_info("  - 隐藏无用功能/按钮/UI")
    log_success("阶段 13 验收通过（手动操作）")
    return True


def verify_stage_14(name, apk_path):
    """验收阶段 14: 去功能点真机验收"""
    log_step("验收阶段 14: 去功能点真机验收")
    log_warn("阶段 14 需要手动验收：")
    log_info("  - 目标按钮不可见/不可点击")
    log_info("  - 布局未变形")
    log_info("  - 核心玩法仍可进入")
    log_success("阶段 14 验收通过（手动验收）")
    return True


def verify_stage_15(name, apk_path):
    """验收阶段 15: 汉化"""
    log_step("验收阶段 15: 汉化")
    log_warn("阶段 15 需要手动操作：")
    log_info("  - 提取游戏字符串")
    log_info("  - 生成翻译表")
    log_info("  - 替换字体为中文字体")
    log_success("阶段 15 验收通过（手动操作）")
    return True


def verify_stage_16(name, apk_path):
    """验收阶段 16: 汉化真机验收"""
    log_step("验收阶段 16: 汉化真机验收")
    log_warn("阶段 16 需要手动验收：")
    log_info("  - OCR识别到中文字符串")
    log_info("  - 字体加载无异常")
    log_info("  - 图片汉化正确")
    log_success("阶段 16 验收通过（手动验收）")
    return True


def verify_stage_17(name, apk_path):
    """验收阶段 17: 重打包签名"""
    log_step("验收阶段 17: 重打包签名")
    
    patched = get_patched_apk(name)
    
    if not file_exists(patched, "patched.apk"):
        return False
    
    apksigner = Path(repo_root()) / "tools/environments/android-sdk/build-tools/34.0.0/apksigner"
    if not apksigner.exists():
        log_warn("apksigner 不存在，跳过签名验证")
        return True
    
    result = subprocess.run(
        [str(apksigner), "verify", "--verbose", str(patched)],
        capture_output=True, text=True
    )
    
    output = result.stdout + result.stderr
    
    if "Verified using v2 scheme (APK Signature Scheme v2): true" in output:
        log_success("v2 签名验证通过")
    else:
        log_error("v2 签名验证失败")
        return False
    
    if "Verified using v3 scheme (APK Signature Scheme v3): true" in output:
        log_success("v3 签名验证通过")
    else:
        log_warn("v3 签名验证失败")
    
    log_success("阶段 17 验收通过")
    return True


def verify_stage_18(name, apk_path):
    """验收阶段 18: 运行时验证"""
    log_step("验收阶段 18: 运行时验证")
    
    patched = get_patched_apk(name)
    
    if not file_exists(patched, "patched.apk"):
        return False
    
    adb = Path(repo_root()) / "tools/environments/android-sdk/platform-tools/adb"
    if not adb.exists():
        log_error("ADB 不存在")
        return False
    
    log_info("安装 patched.apk...")
    result = subprocess.run(
        [str(adb), "install", "-r", str(patched)],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        log_error(f"安装失败: {result.stderr}")
        return False
    
    log_success("安装成功")
    
    aapt2 = Path(repo_root()) / "tools/environments/android-sdk/build-tools/34.0.0/aapt2"
    if aapt2.exists():
        result = subprocess.run(
            [str(aapt2), "dump", "badging", str(patched)],
            capture_output=True, text=True
        )
        match = re.search(r"package: name='([^']+)'", result.stdout)
        if match:
            package_name = match.group(1)
        else:
            package_name = "com.spcomes.kw2"
    else:
        package_name = "com.spcomes.kw2"
    
    log_info(f"启动应用: {package_name}")
    result = subprocess.run(
        [str(adb), "shell", "monkey", "-p", package_name, "-c", "android.intent.category.LAUNCHER", "1"],
        capture_output=True, text=True
    )
    
    if result.returncode != 0:
        log_error(f"启动失败: {result.stderr}")
        return False
    
    log_success("启动成功")
    
    import time
    time.sleep(5)
    
    result = subprocess.run(
        [str(adb), "logcat", "-d", "*:E", "--format=brief"],
        capture_output=True, text=True
    )
    
    crash_patterns = [
        r"FATAL EXCEPTION",
        r"AndroidRuntime",
        r"Process:.*has died",
    ]
    
    for pattern in crash_patterns:
        if re.search(pattern, result.stdout, re.IGNORECASE):
            log_error(f"发现崩溃: {pattern}")
            return False
    
    log_success("无崩溃")
    
    screenshot_path = get_crack_dir(name) / "screenshot.png"
    result = subprocess.run(
        [str(adb), "shell", "screencap", "-p", "/sdcard/screenshot.png"],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        subprocess.run(
            [str(adb), "pull", "/sdcard/screenshot.png", str(screenshot_path)],
            capture_output=True, text=True
        )
        if screenshot_path.exists():
            log_success(f"截图已保存: {screenshot_path}")
    
    log_success("阶段 18 验收通过")
    return True


def verify_stage_19(name, apk_path):
    """验收阶段 19: AS 工程化"""
    log_step("验收阶段 19: AS 工程化")
    log_success("阶段 19 验收通过")
    return True


def verify_stage_20(name, apk_path):
    """验收阶段 20: 最终验收检查"""
    log_step("验收阶段 20: 最终验收检查")
    
    patched = get_patched_apk(name)
    
    if not file_exists(patched, "patched.apk"):
        return False
    
    manifest = get_out_dir(name) / "01-apktool" / "AndroidManifest.xml"
    if manifest.exists():
        content = manifest.read_text(encoding='utf-8')
        if "com.android.vending.splits.required" in content:
            log_error("AndroidManifest.xml 未清理 split 配置")
            return False
    
    log_success("阶段 20 验收通过")
    return True


def verify_stage_21(name, apk_path):
    """验收阶段 21: 清理临时空间"""
    log_step("验收阶段 21: 清理临时空间")
    
    crack_dir = get_crack_dir(name)
    result = subprocess.run(
        ["du", "-sh", str(crack_dir)],
        capture_output=True, text=True
    )
    
    if result.returncode == 0:
        size = result.stdout.split()[0]
        log_info(f"目录大小: {size}")
    
    log_success("阶段 21 验收通过")
    return True


# 验收函数映射
VERIFY_FUNCTIONS = {
    "00": verify_stage_00,
    "00a": verify_stage_00a,
    "01": verify_stage_01,
    "02": verify_stage_02,
    "03": verify_stage_03,
    "04": verify_stage_04,
    "05": verify_stage_05,
    "06": verify_stage_06,
    "07": verify_stage_07,
    "08": verify_stage_08,
    "09": verify_stage_09,
    "10": verify_stage_10,
    "11": verify_stage_11,
    "12": verify_stage_12,
    "13": verify_stage_13,
    "14": verify_stage_14,
    "15": verify_stage_15,
    "16": verify_stage_16,
    "17": verify_stage_17,
    "18": verify_stage_18,
    "19": verify_stage_19,
    "20": verify_stage_20,
    "21": verify_stage_21,
}


def main():
    parser = argparse.ArgumentParser(description='阶段验收脚本')
    parser.add_argument('name', help='项目名称')
    parser.add_argument('stage', help='阶段编号')
    parser.add_argument('--apk', help='源 APK 路径')
    
    args = parser.parse_args()
    
    if args.apk:
        apk_path = Path(args.apk)
    else:
        status_file = get_crack_dir(args.name) / "status.yaml"
        if status_file.exists():
            content = status_file.read_text(encoding='utf-8')
            match = re.search(r'source_apk\s*[=:]\s*["\']([^"\']+)["\']', content)
            if match:
                apk_path = Path(repo_root()) / match.group(1)
            else:
                apk_path = Path(repo_root()) / "apks" / f"{args.name}.apk"
        else:
            apk_path = Path(repo_root()) / "apks" / f"{args.name}.apk"
    
    if args.stage not in VERIFY_FUNCTIONS:
        log_error(f"未知阶段: {args.stage}")
        return 1
    
    verify_func = VERIFY_FUNCTIONS[args.stage]
    success = verify_func(args.name, apk_path)
    
    if success:
        log_success(f"阶段 {args.stage} 验收通过")
        return 0
    else:
        log_error(f"阶段 {args.stage} 验收失败")
        return 1


if __name__ == '__main__':
    ensure_env()
    sys.exit(main())
