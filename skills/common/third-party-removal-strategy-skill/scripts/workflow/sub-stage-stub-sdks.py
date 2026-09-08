#!/usr/bin/env python3
import sys, os, re, subprocess
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib'))
from common import *

def stub_smali_file(filepath, strategy):
    """Stub a smali file based on strategy A/B/C"""
    if strategy == 'C':
        os.remove(filepath)
        return True

    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        src = f.read()

    if strategy == 'A':
        src = re.sub(
            r'(\.method[^\n]*\n)(?:[^\n]*\n)*?(\.end method)',
            r'\1    return-void\n    nop\n\2',
            src
        )
    elif strategy == 'B':
        src = re.sub(
            r'^(invoke-static.*SDK.*)$',
            r'# REMOVED: \1',
            src,
            flags=re.MULTILINE
        )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(src)
    return True

def main():
    ensure_env()

    if len(sys.argv) > 1:
        setup_paths_from_apk(sys.argv[1])
    else:
        name = os.environ.get('NAME') or die("需要 APK 路径或 NAME 环境变量")
        setup_paths_from_name(name)

    os.environ.setdefault('KEYSTORE', os.path.join(out_dir(), f"{os.environ['NAME']}.keystore"))
    os.environ.setdefault('KS_ALIAS', os.environ['NAME'])
    os.environ.setdefault('FINDINGS', os.path.join(crack_dir(), 'findings.md'))

    OUT = out_dir()
    NAME = os.environ['NAME']
    require_crack_dir()
    require_out()

    log_step("阶段 9: 第三方 SDK 桩化 / 清理")
    ensure_dir(os.path.join(OUT, "09-stub"))

    sdk_list = os.path.join(OUT, "04-findings", "sdks_found.txt")
    if not os.path.isfile(sdk_list) or os.path.getsize(sdk_list) == 0:
        log_warn(f"未发现 SDK；可手动检查 {sdk_list} 后重跑")
        sys.exit(0)

    with open(sdk_list) as f:
        sdk_files = [line.strip() for line in f if line.strip()]

    log_info(f"SDK 文件清单: {len(sdk_files)} 个")

    manifest = os.path.join(OUT, "01-apktool", "AndroidManifest.xml")
    if os.path.isfile(manifest):
        log_info("清理 AndroidManifest.xml 中的第三方 SDK 组件")
        manifest_patterns = [
            r'providers.*umeng\|provider.*umeng',
            r'receiver.*umeng',
            r'service.*push',
            r'meta-data.*JPUSH',
            r'uses-permission.*AD_ID',
            r'uses-permission.*umeng',
        ]
        combined = '|'.join(manifest_patterns)
        import shutil
        shutil.copy2(manifest, os.path.join(OUT, "09-stub", "AndroidManifest.xml.bak"))
        with open(manifest, 'r') as f:
            lines = f.readlines()
        with open(manifest, 'w') as f:
            for line in lines:
                if not re.search(combined, line, re.IGNORECASE):
                    f.write(line)
        log_success("Manifest 清理完成（备份在 AndroidManifest.xml.bak）")

    res_dir = os.path.join(OUT, "01-apktool", "res")
    if os.path.isdir(res_dir):
        log_info("清理第三方 SDK 资源")
        res_patterns = [
            "umeng_*", "bugly_*", "jpush_*",
            "*_umeng*", "UM*",
        ]
        cleaned = 0
        for root, dirs, files in os.walk(res_dir):
            for fn in files:
                for pat in res_patterns:
                    import fnmatch
                    if fnmatch.fnmatch(fn, pat):
                        fp = os.path.join(root, fn)
                        os.remove(fp)
                        cleaned += 1
                        break
        log_info(f"清理了 {cleaned} 个 res 文件")

    stub_count = 0
    strategy = os.environ.get('STUB_STRATEGY', 'A')

    out_jadx = os.path.join(OUT, "02-jadx", "sources") + os.sep
    out_il2cpp = os.path.join(OUT, "03-il2cpp") + os.sep

    for sdk_file in sdk_files:
        if not sdk_file or not os.path.isfile(sdk_file):
            continue
        if os.path.commonpath([sdk_file, out_il2cpp]) == out_il2cpp.rstrip(os.sep):
            continue
        rel = sdk_file.replace(out_jadx, '') if out_jadx in sdk_file else sdk_file

        if strategy == 'A':
            log_info(f"[A 桩化] {rel}")
        elif strategy == 'B':
            log_info(f"[B 注释化] {rel}")
        elif strategy == 'C':
            log_warn(f"[C 删除] {rel}（高风险）")

        stub_smali_file(sdk_file, strategy)
        stub_count += 1

    log_success(f"策略={strategy}; 处理 {stub_count} 个 SDK 文件")

if __name__ == "__main__":
    main()
