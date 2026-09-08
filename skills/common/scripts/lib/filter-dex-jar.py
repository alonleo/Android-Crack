#!/usr/bin/env python3
import os, sys, shutil, subprocess, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <input.jar> [output.jar]')

input_jar = sys.argv[1]
output_jar = sys.argv[2] if len(sys.argv) > 2 else (
    input_jar.rsplit('.', 1)[0] + '-filtered.' + input_jar.rsplit('.', 1)[1]
)

require_file(input_jar)

input_size = os.path.getsize(input_jar)
log_info(f'[filter-dex-jar] Input:  {input_jar} ({input_size / 1024 / 1024:.1f} MB)')
log_info(f'[filter-dex-jar] Output: {output_jar}')

workdir = tempfile.mkdtemp(prefix='filter-dex-jar-')
try:
    subprocess.run(['jar', 'xf', input_jar], cwd=workdir, check=True, capture_output=True)

    for root, dirs, files in os.walk(workdir):
        if os.path.basename(root) == '_COROUTINE':
            shutil.rmtree(root)
            continue
        for fn in files:
            if fn in ('R.class', 'BuildConfig.class') or (fn.startswith('R$') and fn.endswith('.class')):
                os.remove(os.path.join(root, fn))

    remaining = sum(1 for _, _, files in os.walk(workdir) for f in files if f.endswith('.class'))
    log_info(f'[filter-dex-jar] Remaining class files: {remaining}')

    subprocess.run(['jar', 'cf', output_jar, '.'], cwd=workdir, check=True, capture_output=True)

    out_size = os.path.getsize(output_jar)
    log_info(f'[filter-dex-jar] Done: {output_jar} ({out_size / 1024 / 1024:.1f} MB)')
finally:
    shutil.rmtree(workdir, ignore_errors=True)
