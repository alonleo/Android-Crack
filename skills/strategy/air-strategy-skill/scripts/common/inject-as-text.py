#!/usr/bin/env python3
import os, sys, subprocess, shutil, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <Name> [--tsv file.tsv] [--dry-run]')

name = sys.argv[1]
setup_paths_from_name(name)
require_crack_dir()
require_out()

tsv_file = os.path.join(out_dir(), '05-strings/swf/swf_ui_strings.tsv')
ffdec_jar = os.path.join(repo_root(), 'tools/environments/ffdec/ffdec.jar')
require_file(ffdec_jar)

dry_run = False
for arg in sys.argv[2:]:
    if arg == '--dry-run':
        dry_run = True
    elif arg.startswith('--tsv='):
        tsv_file = arg.split('=', 1)[1]

log_step(f'AS3注入覆盖DefineText ({name})')

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
    die('找不到游戏SWF')
swf_name = os.path.basename(game_swf)
log_info(f'SWF: {game_swf}')

if dry_run:
    log_info('[DRY RUN] 注入代码预览:')
    if os.path.isfile(tsv_file):
        with open(tsv_file, encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('\t')
                if len(parts) >= 2 and parts[0].strip() and parts[1].strip():
                    log_info(f'  "{parts[0][:50]}" → "{parts[1][:50]}"')
    sys.exit(0)

tmp_dir = f'/tmp/as_inject_{int(time.time())}'
scripts_tmp = os.path.join(tmp_dir, 'scripts')
ensure_dir(scripts_tmp)

subprocess.run(['java', '-jar', ffdec_jar, '-export', 'script', scripts_tmp, game_swf],
               capture_output=True, text=True)

mt_file = ''
for root, dirs, files in os.walk(scripts_tmp):
    for fn in files:
        if fn == 'MainTimeline.as':
            mt_file = os.path.join(root, fn)
            break
    if mt_file:
        break
if not mt_file:
    die('找不到MainTimeline.as')

log_info('注入AS3代码...')

translations = []
with open(tsv_file, encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[0].strip() and parts[1].strip() and parts[0].strip() != parts[1].strip():
            translations.append((parts[0].strip(), parts[1].strip()))

if not translations:
    log_info('No translations to inject')
    sys.exit(0)

with open(mt_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

ctor_start = ctor_end = None
for i, line in enumerate(lines):
    if 'public function MainTimeline()' in line:
        ctor_start = i
    if ctor_start is not None and i > ctor_start and line.strip() == '}':
        ctor_end = i
        break

if ctor_start is None or ctor_end is None:
    die('ERROR: no constructor found')

w, h = 2880, 1440
positions = [
    (w//2 - 400, 50), (w//2 - 400, 200), (w//2 - 400, 400),
    (w//2 - 400, 600), (w//2 - 400, 800), (w//2 - 400, 1000),
    (50, 50), (50, h-80), (w-500, 50), (w-500, h-80),
    (w//2 - 300, h//2 - 20), (w//2 - 300, h//2 + 60),
]

call_code = '        _injectTexts();\n'
helper_code = '''    // === injected by inject-as-text.py ===
    private function _injectTexts():void {
        var _tf:TextField;
'''

for i, (orig, trans) in enumerate(translations):
    trans_esc = trans.replace('"', '\\"').replace('\n', '\\n').replace('\r', '')
    px, py = positions[i % len(positions)]
    px += (i // len(positions)) * 30
    helper_code += f'''
        _tf = new TextField();
        _tf.text = "{trans_esc}";
        _tf.x = {px}; _tf.y = {py};
        _tf.width = 800; _tf.height = 80;
        _tf.textColor = 0xFFFF00;
        _tf.selectable = false;
        _tf.mouseEnabled = false;
        addChild(_tf);'''

helper_code += '    }\n'

lines.insert(ctor_end, call_code)
pkg_end = len(lines) - 1
while pkg_end >= 0 and lines[pkg_end].strip() == '':
    pkg_end -= 1
class_end = pkg_end - 1
while class_end >= 0 and lines[class_end].strip() != '}':
    class_end -= 1

lines.insert(class_end, helper_code)

with open(mt_file, 'w', encoding='utf-8') as f:
    f.writelines(lines)

log_info(f'Injected {len(translations)} texts')

patch_dir = os.path.join(out_dir(), '08-swf-patched')
patched_swf = os.path.join(patch_dir, f'patched_{swf_name}')
ensure_dir(patch_dir)

log_info('importScript...')
subprocess.run(['java', '-jar', ffdec_jar, '-importScript', game_swf, patched_swf, scripts_tmp],
               capture_output=True, text=True)

if os.path.isfile(patched_swf):
    log_success(f'AS3注入完成: {patched_swf}')
    for root, dirs, files in os.walk(os.path.join(out_dir(), '01-apktool')):
        for fn in files:
            if fn == swf_name:
                shutil.copy2(patched_swf, os.path.join(root, fn))
                log_info(f'已替换 SWF: {os.path.join(root, fn)}')
    log_info('重打包: rm -f $OUT/17-*.apk && stage-17-repack-sign.py')
else:
    log_error('回灌失败')

shutil.rmtree(tmp_dir, ignore_errors=True)
