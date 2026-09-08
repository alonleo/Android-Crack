#!/usr/bin/env python3
import os, sys, subprocess, shutil, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FFDEC_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'environments', 'ffdec')
FFDEC_DIR = os.path.abspath(FFDEC_DIR)
FFDEC_JAR = os.path.join(FFDEC_DIR, 'ffdec.jar')

log_info('=== JPEXS ffdec 安装助手 ===')
log_info(f'目标目录: {FFDEC_DIR}')
print()

if os.path.isfile(FFDEC_JAR):
    r = subprocess.run(['java', '-jar', FFDEC_JAR, '--version'], capture_output=True, text=True)
    ver = r.stdout.strip() or r.stderr.strip() or 'unknown'
    log_success(f'ffdec 已安装 (ver: {ver})')
    log_info(f'   {FFDEC_JAR}')
    sys.exit(0)

log_info('尝试自动下载...')

urls = [
    'https://github.com/jindrapetrik/jpexs-decompiler/releases/download/version26.2.1/ffdec_26.2.1.zip',
    'https://github.com/jpexs/decompiler/releases/download/v20.1.0/ffdec_20.1.0.zip',
    'https://sourceforge.net/projects/ffdec/files/ffdec/ffdec_20.1.0/ffdec_20.1.0.zip/download',
]

for url in urls:
    log_info(f'  下载: {url}')
    ensure_dir(FFDEC_DIR)
    r = subprocess.run(['curl', '-L', '--connect-timeout', '10', '--max-time', '120',
                        '-o', '/tmp/ffdec_install.zip', url],
                       capture_output=True)
    if r.returncode == 0:
        size = os.path.getsize('/tmp/ffdec_install.zip')
        if size > 100000:
            log_info(f'  下载成功 ({size} bytes)，解压中...')
            subprocess.run(['unzip', '-q', '-o', '/tmp/ffdec_install.zip', '-d', FFDEC_DIR],
                           capture_output=True)
            if os.path.isfile(FFDEC_JAR):
                log_success('安装成功!')
                sys.exit(0)

print()
log_error('自动下载失败。请手动安装:')
print()
log_info('步骤 1: 下载 ffdec')
log_info('  浏览器打开: https://github.com/jpexs/decompiler/releases')
log_info('  下载最新版本: ffdec_20.1.0.zip')
print()
log_info(f'步骤 2: 解压')
log_info(f'  unzip ffdec_20.1.0.zip -d {FFDEC_DIR}')
print()
log_info('步骤 3: 验证')
log_info('  java -jar {FFDEC_JAR} --version')
