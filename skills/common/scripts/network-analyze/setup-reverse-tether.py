#!/usr/bin/env python3
import os, sys, subprocess, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = repo_root()

log_info('[*] Checking device connectivity...')
r = subprocess.run([adb(), 'shell', 'ping', '-c', '1', '-W', '1', '8.8.8.8'],
                   capture_output=True)
if r.returncode == 0:
    log_success('[✓] Device already has internet access')
    sys.exit(0)

GNIREHTET = os.path.join(REPO_DIR, 'tools/crack-intergration-tools/execable/gnirehtet/gnirehtet')
GNIREHTET_APK = os.path.join(REPO_DIR, 'tools/crack-intergration-tools/execable/gnirehtet/gnirehtet.apk')

if os.path.isfile(GNIREHTET) and os.path.isfile(GNIREHTET_APK):
    log_info('[*] Found gnirehtet. Installing client APK...')
    subprocess.run([adb(), 'install', '-r', GNIREHTET_APK], capture_output=True)
    log_info('[*] Starting gnirehtet relay...')
    gnirehtet_dir = os.path.dirname(GNIREHTET)
    log_file = open('/tmp/gnirehtet.log', 'w')
    proc = subprocess.Popen([GNIREHTET, 'start'], cwd=gnirehtet_dir,
                            stdout=log_file, stderr=subprocess.STDOUT)
    time.sleep(5)

    r = subprocess.run([adb(), 'shell', 'ping', '-c', '1', '-W', '2', '8.8.8.8'],
                       capture_output=True)
    if r.returncode == 0:
        log_success('[✓] Reverse tethering active via gnirehtet')
        sys.exit(0)

log_error('[!] Could not establish internet access')
log_info('    Options:')
log_info('    1. Connect device to WiFi manually')
log_info('    2. Enable USB tethering from host')
log_info('    3. Use a different device with internet')
sys.exit(1)
