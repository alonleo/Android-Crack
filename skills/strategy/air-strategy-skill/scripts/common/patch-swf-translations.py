#!/usr/bin/env python3
import os, sys, subprocess, shutil, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <Name> [--tsv file.tsv] [--dry-run|--gui|--repack]')

name = sys.argv[1]
setup_paths_from_name(name)
require_crack_dir()
require_out()

mode = 'all'
tsv_file = os.path.join(out_dir(), '05-strings/swf/swf_ui_strings.tsv')
ffdec_jar = os.path.join(repo_root(), 'tools/environments/ffdec/ffdec.jar')
require_file(ffdec_jar)

i = 2
while i < len(sys.argv):
    arg = sys.argv[i]
    if arg == '--dry-run' or arg == 'dry-run':
        mode = 'dry-run'
    elif arg == '--gui' or arg == 'gui':
        mode = 'gui'
    elif arg == '--repack' or arg == 'repack':
        mode = 'repack'
    elif arg.startswith('--tsv='):
        tsv_file = arg.split('=', 1)[1]
    elif arg == '--tsv' and i + 1 < len(sys.argv):
        i += 1
        tsv_file = sys.argv[i]
    i += 1

log_step(f'SWF 翻译回灌 ({name})')

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
    die('找不到 SWF 文件')
swf_name = os.path.basename(game_swf)
log_info(f'SWF: {game_swf}')

if mode == 'gui':
    log_info('=== ffdec GUI 编辑指南 ===')
    print()
    log_info('步骤 1: 启动 ffdec GUI')
    log_info(f'  java -jar {ffdec_jar}')
    log_info('  (或双击 ffdec.jar / ffdec.exe)')
    print()
    log_info('步骤 2: 打开 SWF')
    log_info(f'  File → Open → {game_swf}')
    print()
    log_info('步骤 3: 编辑文本')
    log_info('  在左侧树中找到 DefineText/DefineEditText 标签')
    log_info('  右键 → Edit → 修改文字内容')
    print()
    log_info('步骤 4: 导出修改后的 SWF')
    patch_dir_out = os.path.join(out_dir(), '08-swf-patched')
    ensure_dir(patch_dir_out)
    log_info(f'  File → Save As → {os.path.join(patch_dir_out, "patched_" + swf_name)}')
    print()
    log_info('步骤 5: 替换并重打包')
    log_info(f'  cp {os.path.join(patch_dir_out, "patched_" + swf_name)} {game_swf}')
    log_info(f'  {os.path.join(SCRIPT_DIR, "..", "..", "..", "..", "..", "..", "..", "skills", "common", "general-strategy-skill", "scripts", "workflow", "stage-17-repack-sign.py")} {name}')
    sys.exit(0)

if mode == 'dry-run':
    require_file(tsv_file)
    with open(tsv_file, encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split('\t')
            if len(parts) >= 2 and parts[0].strip():
                orig = parts[0].strip()
                trans = parts[1].strip()
                log_info(f'  {orig[:50]:50s} → {trans[:40]}')
    print()
    log_warn('提示: 本 SWF 文本为 DefineText (静态字形)，')
    log_warn('无法通过 CLI 回灌。请使用 --gui 模式打开 ffdec GUI 手动编辑。')
    sys.exit(0)

log_info('尝试 -importText 回灌 (仅对 DefineEditText 有效)...')
text_dir = os.path.join(out_dir(), '08-swf-patched/text_export')
if os.path.isdir(text_dir):
    shutil.rmtree(text_dir)
ensure_dir(text_dir)

subprocess.run(['java', '-jar', ffdec_jar, '-export', 'text', text_dir, game_swf],
               capture_output=True, text=True)

translations = {}
with open(tsv_file, encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[0].strip() and parts[1].strip():
            translations[parts[0].strip()] = parts[1].strip()

replaced = 0
for fn in sorted(os.listdir(text_dir)):
    fp = os.path.join(text_dir, fn)
    if not os.path.isfile(fp):
        continue
    with open(fp, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    new_content = content
    for orig, trans in translations.items():
        if orig in new_content:
            new_content = new_content.replace(orig, trans)
            replaced += 1
    if new_content != content:
        with open(fp, 'w', encoding='utf-8') as f:
            f.write(new_content)
log_info(f'Applied {replaced} replacements')

patch_dir_out = os.path.join(out_dir(), '08-swf-patched')
ensure_dir(patch_dir_out)
patched_swf = os.path.join(patch_dir_out, f'patched_{swf_name}')
subprocess.run(['java', '-jar', ffdec_jar, '-importText', game_swf, patched_swf, text_dir],
               capture_output=True, text=True)
shutil.rmtree(text_dir, ignore_errors=True)

tmpv = f'/tmp/ffdec_verify_{int(time.time())}'
ensure_dir(tmpv)
subprocess.run(['java', '-jar', ffdec_jar, '-export', 'text', tmpv, patched_swf],
               capture_output=True, text=True)

verify_failed = 0
with open(tsv_file, encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split('\t')
        if len(parts) >= 2 and parts[0].strip() and parts[1].strip():
            orig, trans = parts[0].strip(), parts[1].strip()
            found = False
            for fn in os.listdir(tmpv):
                fp = os.path.join(tmpv, fn)
                if not os.path.isfile(fp):
                    continue
                with open(fp, 'r', encoding='utf-8', errors='ignore') as fh:
                    if trans in fh.read():
                        found = True
                        break
            if not found:
                verify_failed += 1
                log_warn(f"验证失败: '{orig}' → '{trans}'")

shutil.rmtree(tmpv, ignore_errors=True)

if os.path.isfile(patched_swf):
    log_info(f'SWF 已生成: {patched_swf}')
    log_warn('请验证修改是否生效。若文本未变化，请使用 --gui 模式手动编辑。')
    for root, dirs, files in os.walk(os.path.join(out_dir(), '01-apktool')):
        for fn in files:
            if fn == swf_name:
                shutil.copy2(patched_swf, os.path.join(root, fn))
                log_info(f'已替换: {os.path.join(root, fn)}')
                break

    if mode == 'repack':
        for f in ['10-patched-unsigned.apk', '11-patched-aligned.apk', '12-patched-signed.apk']:
            fp = os.path.join(out_dir(), f)
            if os.path.isfile(fp):
                os.remove(fp)
        repack_script = os.path.join(SCRIPT_DIR, '..', 'stage-17-repack-sign.py')
        if os.path.isfile(repack_script):
            subprocess.run(['bash', repack_script, name])

log_success('完成')
log_info(f'验证修改: java -jar {ffdec_jar} -export text /tmp/verify {patched_swf}')
log_info(f'重新打包: {os.path.join(SCRIPT_DIR, "..", "..", "..", "..", "..", "..", "..", "skills", "common", "general-strategy-skill", "scripts", "workflow", "stage-17-repack-sign.py")} {name}')
