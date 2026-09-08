#!/usr/bin/env python3
import os, sys, subprocess, glob
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(SCRIPT_DIR, '..', 'lib'))
sys.path.insert(0, os.path.join(repo_root(), 'tools/scripts/lib'))

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <Name> [--swf path/to.swf]')

name = sys.argv[1]
setup_paths_from_name(name)
require_crack_dir()
require_out()

ffdec_jar = os.path.join(repo_root(), 'tools/environments/ffdec/ffdec.jar')
require_file(ffdec_jar)
out_dir_path = os.path.join(out_dir(), '05-strings/swf')
ensure_dir(out_dir_path)

log_step(f'ffdec SWF 文本提取 ({name})')

swf_candidate = os.path.join(out_dir(), '01-apktool/assets')
game_swf = ''
if os.path.isdir(swf_candidate):
    for root, dirs, files in os.walk(swf_candidate):
        depth = root[len(swf_candidate):].count(os.sep)
        if depth > 2:
            continue
        for fn in files:
            if fn.endswith('.swf') and '/extensions/' not in root:
                game_swf = os.path.join(root, fn)
                break
        if game_swf:
            break

if not game_swf:
    original_dir = os.path.join(out_dir_path, 'original')
    ensure_dir(original_dir)
    apk_path_env = os.environ.get('APK', '')
    if apk_path_env:
        subprocess.run(['unzip', '-o', apk_path_env, 'assets/*.swf', '-d', original_dir],
                       capture_output=True)
        for root, dirs, files in os.walk(original_dir):
            for fn in files:
                if fn.endswith('.swf') and '/extensions/' not in root:
                    game_swf = os.path.join(root, fn)
                    break
            if game_swf:
                break

if not game_swf:
    die('找不到 SWF 文件')

swf_name = os.path.basename(game_swf)
log_info(f'SWF: {game_swf}')

text_dir = os.path.join(out_dir_path, 'ffdec_text')
if os.path.isdir(text_dir):
    import shutil
    shutil.rmtree(text_dir)
ensure_dir(text_dir)

r = subprocess.run(['java', '-jar', ffdec_jar, '-export', 'text', text_dir, game_swf],
                   capture_output=True, text=True)
if r.stderr:
    log_info(r.stderr.strip().split('\n')[-1])

seen = set()
strings_file = os.path.join(out_dir_path, f'{swf_name.replace(".swf", "")}_strings.txt')
for f in sorted(glob.glob(os.path.join(text_dir, '*.txt'))):
    with open(f, 'r', encoding='utf-8', errors='ignore') as fh:
        for part in fh.read().split('\x1e'):
            part = part.strip()
            if part and part not in seen:
                seen.add(part)

with open(strings_file, 'w', encoding='utf-8') as f:
    for t in sorted(seen, key=lambda x: (len(x), x)):
        f.write(t + '\n')

text_count = len(seen)
log_success(f'提取完成: {text_count} 条唯一文本 → {strings_file}')
log_warn('注意: 本游戏文本为 DefineText (静态字形)，不可通过 -importText 回灌。')
log_warn('如需修改显示文本，请使用 ffdec GUI 编辑 SWF 后替换 apktool/assets/ 中的文件。')
