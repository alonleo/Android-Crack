#!/usr/bin/env python3
import os, sys, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <Name> [--xvfb]')

name = sys.argv[1]
setup_paths_from_name(name)
require_crack_dir()
require_out()

ffdec_jar = os.path.join(repo_root(), 'tools/environments/ffdec/ffdec.jar')
require_file(ffdec_jar)

swf_dir = os.path.join(out_dir(), '01-apktool/assets')
game_swf = ''
for root, dirs, files in os.walk(swf_dir):
    for fn in files:
        if fn.endswith('.swf') and '/extensions/' not in root:
            game_swf = os.path.join(root, fn)
            break
    if game_swf:
        break
if not game_swf:
    die('找不到 SWF')

xvfb_pid = None
if len(sys.argv) > 2 and sys.argv[2] == '--xvfb':
    xvfb_proc = subprocess.Popen(['Xvfb', ':99', '-screen', '0', '1280x720x24'],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    xvfb_pid = xvfb_proc.pid
    time.sleep(1)
    log_info(f'Xvfb 已启动 (PID {xvfb_pid} on :99)')
    os.environ['DISPLAY'] = ':99'

log_info(f'打开 ffdec GUI: {game_swf}')
log_info('请手动编辑 DefineText 标签:')
log_info('  1. 在左侧树中找到 DefineText 标签')
log_info('  2. 右键 → Edit → 修改文字')
patch_dir_out = os.path.join(out_dir(), '08-swf-patched')
ensure_dir(patch_dir_out)
log_info(f'  3. File → Save → {os.path.join(patch_dir_out, "patched_" + os.path.basename(game_swf))}')
print()

ffdec_proc = subprocess.Popen(['java', '-jar', ffdec_jar, game_swf])

if xvfb_pid:
    log_info('ffdec 已在虚拟显示器中启动')
    log_info(f'关闭 Xvfb: kill {xvfb_pid}')

log_info(f'编辑并保存后运行: {os.path.join(SCRIPT_DIR, "patch-swf-translations.py")} "{name}" --repack')
