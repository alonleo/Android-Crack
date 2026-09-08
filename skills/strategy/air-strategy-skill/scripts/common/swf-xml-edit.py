#!/usr/bin/env python3
import os, sys, subprocess, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 3:
    die(f'Usage: {sys.argv[0]} <Name> {{export|import|edit|find|info}} [text]')

name = sys.argv[1]
action = sys.argv[2]
setup_paths_from_name(name)
require_crack_dir()
require_out()

swfmill = os.path.join(repo_root(), 'tools/environments/swfmill/swfmill')
require_file(swfmill)

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
swf_stem = os.path.basename(game_swf).replace('.swf', '')

xml_dir = os.path.join(out_dir(), '05-strings/swf/swfmill_xml')
ensure_dir(xml_dir)
xml_file = os.path.join(xml_dir, f'{swf_stem}.xml')

if action == 'export':
    log_info(f'swfmill swf2xml → {xml_file}')
    subprocess.run([swfmill, 'swf2xml', game_swf, xml_file], check=True)
    size = os.path.getsize(xml_file)
    log_success(f'XML 生成: {size} bytes')

elif action == 'import':
    log_info(f'swfmill xml2swf ← {xml_file}')
    patch_dir_out = os.path.join(out_dir(), '08-swf-patched')
    ensure_dir(patch_dir_out)
    out_swf = os.path.join(patch_dir_out, f'{swf_stem}_from_xml.swf')
    subprocess.run([swfmill, 'xml2swf', xml_file, out_swf])
    if os.path.isfile(out_swf):
        shutil.copy2(out_swf, os.path.join(out_dir(), '01-apktool/assets', f'{swf_stem}.swf'))
        log_success(f'SWF 已替换: {out_swf}')
        log_info(f'运行重打包: stage-17-repack-sign.py {name}')

elif action == 'edit':
    log_info('导出 XML...')
    subprocess.run([swfmill, 'swf2xml', game_swf, xml_file])
    log_info(f'打开编辑器: {xml_file}')
    editor = os.environ.get('EDITOR', 'vi')
    subprocess.run([editor, xml_file])
    log_info('导入 XML...')
    patch_dir_out = os.path.join(out_dir(), '08-swf-patched')
    ensure_dir(patch_dir_out)
    out_swf = os.path.join(patch_dir_out, f'{swf_stem}_from_xml.swf')
    subprocess.run([swfmill, 'xml2swf', xml_file, out_swf])

elif action == 'find':
    if len(sys.argv) < 4:
        die('请指定搜索文本')
    search = ' '.join(sys.argv[3:])
    log_info(f'在 XML 中搜索: {search}')
    if not os.path.isfile(xml_file):
        log_info('先导出 XML...')
        subprocess.run([swfmill, 'swf2xml', game_swf, xml_file])
    r = subprocess.run(['grep', '-n', search, xml_file], capture_output=True, text=True)
    for line in r.stdout.splitlines()[:30]:
        log_info(line)

elif action == 'info':
    swf_size = os.path.getsize(game_swf)
    log_info(f'SWF: {game_swf} ({swf_size} bytes)')
    log_info(f'XML: {xml_file}')
    print()
    log_info('DefineText 编辑说明:')
    log_info('  DefineText 存为 glyph 索引 (非字符串), 不易直接编辑')
    log_info('  DefineEditText 的 variableName 属性可直接修改')
    print()
    log_info('查看 DefineText 数量:')
    if os.path.isfile(xml_file):
        r = subprocess.run(['grep', '-c', 'DefineText objectID=', xml_file], capture_output=True, text=True)
        count = r.stdout.strip()
        log_info(f'  {count} 个 DefineText 标签' if count else '  (0 个)')
    else:
        log_info('  (需先 export)')

else:
    print(f'用法: {sys.argv[0]} <Name> {{export|import|edit|find|info}}')
    print()
    log_info('  export     SWF → XML')
    log_info('  import     XML → SWF (替换 apktool)')
    log_info('  edit       export → editor → import')
    log_info('  find text  在 XML 中搜索文本')
    log_info('  info       查看 SWF/XML 信息')
