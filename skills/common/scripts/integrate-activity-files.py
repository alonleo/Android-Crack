#!/usr/bin/env python3
import os, sys, shutil
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = repo_root()

MAIN_ACTIVITY_SRC = os.path.join(REPO_ROOT, 'skills/common/scripts/template-files/MainActivity.template.java')
SDK_UTILS_SRC = os.path.join(REPO_ROOT, 'skills/common/scripts/template-files/SDKUtils.java')

if not os.path.isfile(MAIN_ACTIVITY_SRC) or not os.path.isfile(SDK_UTILS_SRC):
    die('Source files not found at repo root')

output_projects = os.path.join(REPO_ROOT, 'output-projects')
if not os.path.isdir(output_projects):
    log_warn('crackings/<type>/<Name>/project 不存在，跳过')
    sys.exit(0)

for entry in sorted(os.listdir(output_projects)):
    project_dir = os.path.join(output_projects, entry)
    if not os.path.isdir(project_dir):
        continue
    target_base = os.path.join(project_dir, 'app/src/main/java')
    ensure_dir(os.path.join(target_base, 'com/android/boot'))
    ensure_dir(os.path.join(target_base, 'com/android/common'))
    shutil.copy2(MAIN_ACTIVITY_SRC, os.path.join(target_base, 'com/android/boot/MainActivity.java'))
    shutil.copy2(SDK_UTILS_SRC, os.path.join(target_base, 'com/android/common/SDKUtils.java'))
    log_info(f'Integrated activity files into: {entry}')

log_success('Done.')
