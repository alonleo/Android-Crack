#!/usr/bin/env python3
import os, sys, subprocess, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
INSTALL_DIR = os.path.join(SCRIPT_DIR, '..', '..', 'environments', 'swfmill')
INSTALL_DIR = os.path.abspath(INSTALL_DIR)
ensure_dir(INSTALL_DIR)

SWFMILL_BIN = os.path.join(INSTALL_DIR, 'swfmill')

log_info('=== swfmill 安装助手 ===')
log_info(f'目标: {INSTALL_DIR}')
print()

os_info = os.uname()
sys_os = os_info.sysname
sys_arch = os_info.machine

if sys_os == 'Linux':
    swfmill_os = 'linux'
elif sys_os == 'Darwin':
    swfmill_os = 'macosx'
else:
    die(f'不支持的系统: {sys_os}')

if sys_arch in ('x86_64', 'amd64'):
    swfmill_arch = 'x86_64'
elif sys_arch in ('aarch64', 'arm64'):
    swfmill_arch = 'arm64'
else:
    die(f'不支持的架构: {sys_arch}')

if os.path.isfile(SWFMILL_BIN):
    r = subprocess.run([SWFMILL_BIN, '--version'], capture_output=True, text=True)
    ver = r.stdout.strip() or r.stderr.strip() or 'unknown'
    log_success(f'swfmill 已安装 ({ver})')
    sys.exit(0)

UBUNTU_DEB = 'http://archive.ubuntu.com/ubuntu/pool/universe/s/swfmill/swfmill_0.3.6-1build1_amd64.deb'
ARCHIVE_URL = 'https://www.swfmill.org/releases/swfmill-0.3.6.tar.gz'

source_names = ['Ubuntu amd64 deb', 'swfmill.org release tar.gz']
source_urls = [UBUNTU_DEB, ARCHIVE_URL]

log_info('尝试下载 swfmill...')
print()

for name, url in zip(source_names, source_urls):
    log_info(f'  [{name}] {url}')
    r = subprocess.run(['curl', '-L', '--connect-timeout', '10', '--max-time', '120',
                        '-o', '/tmp/swfmill_dl', url], capture_output=True)
    if r.returncode == 0:
        size = os.path.getsize('/tmp/swfmill_dl')
        if size > 100000:
            log_info(f'  ✓ 下载成功 ({size} bytes)')
            if url.endswith('.deb'):
                subprocess.run(['dpkg', '-x', '/tmp/swfmill_dl', INSTALL_DIR], capture_output=True)
                for root, dirs, files in os.walk(INSTALL_DIR):
                    for fn in files:
                        if fn == 'swfmill':
                            fp = os.path.join(root, fn)
                            shutil.copy2(fp, SWFMILL_BIN)
                            os.chmod(SWFMILL_BIN, 0o755)
            elif url.endswith('.tar.gz'):
                subprocess.run(['tar', 'xzf', '/tmp/swfmill_dl', '-C', INSTALL_DIR,
                                '--strip-components=1'], capture_output=True)

            if os.path.isfile(SWFMILL_BIN) and os.access(SWFMILL_BIN, os.X_OK):
                log_success('swfmill 安装成功!')
                subprocess.run([SWFMILL_BIN, '--version'], capture_output=True)
                os.remove('/tmp/swfmill_dl')
                sys.exit(0)
    print()

if os.path.isfile('/tmp/swfmill_dl'):
    os.remove('/tmp/swfmill_dl')

print()
log_error('自动下载失败。请手动安装:')
print()
log_info(f'方法 A — 从 Ubuntu 源下载 deb (x86_64):')
log_info(f'  wget {UBUNTU_DEB}')
log_info(f'  dpkg -x swfmill_0.3.6-1build1_amd64.deb {INSTALL_DIR}')
print()
log_info('方法 B — 从 Git 仓库编译:')
log_info('  git clone https://github.com/djcsdy/swfmill.git')
log_info('  cd swfmill')
log_info('  sudo apt install -y libxml2-dev libxslt1-dev autoconf automake libtool')
log_info(f'  ./autogen.sh && ./configure --prefix={INSTALL_DIR}')
log_info('  make && make install')
print()
log_info('方法 C — 从 swfmill.org 下载源码编译:')
log_info(f'  wget {ARCHIVE_URL}')
log_info('  tar xzf swfmill-0.3.6.tar.gz && cd swfmill-0.3.6')
log_info(f'  ./configure --prefix={INSTALL_DIR} && make && make install')
