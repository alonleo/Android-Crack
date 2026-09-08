#!/usr/bin/env python3
import os, sys, re, zlib
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <Name> [--all]')

name = sys.argv[1]
setup_paths_from_name(name)
require_crack_dir()
require_out()

mode = 'check'
if len(sys.argv) > 2:
    mode_arg = sys.argv[2]
    if mode_arg in ('--all', 'all'):
        mode = 'all'

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

log_step(f'SWF 文本验证 ({os.path.basename(game_swf)})')
print()

with open(game_swf, 'rb') as f:
    raw = f.read()

sig = raw[:3]
if sig == b'CWS':
    data = zlib.decompress(raw[8:])
elif sig == b'FWS':
    data = raw[8:]
else:
    data = raw

cjk = re.findall(r'[\u4e00-\u9fff]+', data.decode('utf-8', errors='ignore'))
cjk_unique = sorted(set(cjk), key=lambda x: -len(x))

log_info(f'SWF size:       {len(raw)} bytes (compressed)')
log_info(f'               {len(data)} bytes (decompressed)')
log_info(f'Chinese chars:  {len(cjk_unique)} unique strings')
print()

if mode == 'all':
    log_info('=== All Chinese strings ===')
    for s in cjk_unique:
        if len(s) >= 2:
            count = data.count(s.encode('utf-8'))
            log_info(f'  x{count:3d}: {s}')
    print()

translations = [
    "需要帮助", "游戏目标", "干得好", "请给我们评分",
    "请为游戏评分", "电池", "平板碎片", "小齿轮",
    "电梯卡", "链条", "磁铁", "中齿轮", "推式磁铁",
    "大齿轮", "齿轮完成",
]

found = 0
for t in translations:
    c = data.count(t.encode('utf-8'))
    if c > 0:
        found += 1
        log_info(f'  ✅ x{c:3d}: {t}')

if found > 0:
    log_success(f'{found}/{len(translations)} Chinese translations FOUND in SWF')
else:
    log_error(f'No Chinese translations found in SWF')
    log_info('   (AS3 injection may have failed or SWF is original)')
