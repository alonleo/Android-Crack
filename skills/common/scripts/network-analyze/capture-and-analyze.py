#!/usr/bin/env python3
import os, sys, time, subprocess, signal
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'lib'))
from common import *

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = repo_root()
PKG = sys.argv[1] if len(sys.argv) > 1 else 'com.moonton.rslg.uc'
TIMESTAMP = time.strftime('%Y%m%d_%H%M%S')

pkg_safe = PKG.replace('.', '_')
CAPTURE_DIR = os.path.join(REPO_DIR, 'crackings', pkg_safe, 'capture', TIMESTAMP)
ensure_dir(CAPTURE_DIR)

log_info('=== Game Protocol Capture ===')
log_info(f'Package: {PKG}')
log_info(f'Output: {CAPTURE_DIR}')

log_info('[1/4] Setting up reverse tether...')
r = subprocess.run([adb(), 'shell', 'ping', '-c', '1', '-W', '1', '8.8.8.8'],
                   capture_output=True)
if r.returncode == 0:
    log_success('  [✓] Device has internet')
else:
    setup_script = os.path.join(SCRIPT_DIR, 'setup-reverse-tether.py')
    if os.path.isfile(setup_script):
        subprocess.run([sys.executable, setup_script])
    else:
        log_warn('  [!] No internet, using local capture only')

log_info('[2/4] Starting protocol capture server...')
server_log = os.path.join(CAPTURE_DIR, 'server.log')
mock_server = os.path.join(SCRIPT_DIR, 'mock-server.py')
if os.path.isfile(mock_server):
    with open(server_log, 'w') as lf:
        proc = subprocess.Popen([sys.executable, mock_server, '--ports', '8080,80,443'],
                                stdout=lf, stderr=subprocess.STDOUT)
    time.sleep(2)

    for port in [8080, 80, 443, 7777, 8888, 9999, 4444, 3000, 4000, 5000, 6000, 7000, 9000]:
        subprocess.run([adb(), 'reverse', f'tcp:{port}', f'tcp:{port}'],
                       capture_output=True)
    log_success('  [✓] Port forwarding active')
else:
    log_warn(f'  mock-server.py not found at {mock_server}')

log_info(f'[3/4] Launching {PKG}...')
subprocess.run([adb(), 'shell', 'am', 'force-stop', PKG], capture_output=True)
time.sleep(1)
subprocess.run([adb(), 'logcat', '-c'], capture_output=True)
subprocess.run([adb(), 'shell', 'monkey', '-p', PKG, '-c', 'android.intent.category.LAUNCHER', '1'])

CAPTURE_SECONDS = 60
log_info(f'  Capturing for {CAPTURE_SECONDS} seconds...')
time.sleep(CAPTURE_SECONDS)

log_info('[4/4] Collecting results...')
if 'proc' in dir():
    proc.terminate()
    proc.wait()

logcat_file = os.path.join(CAPTURE_DIR, 'logcat.txt')
with open(logcat_file, 'w') as f:
    subprocess.run([adb(), 'logcat', '-d', '-t', '1000'], stdout=f, stderr=subprocess.STDOUT)

log_info('')
log_info('=== Capture Complete ===')
log_info(f'Logs: {CAPTURE_DIR}')

captures = [f for f in os.listdir(CAPTURE_DIR) if f.endswith('.bin') or f.endswith('.pcap')]
if captures:
    for f in captures:
        fp = os.path.join(CAPTURE_DIR, f)
        size = os.path.getsize(fp)
        log_info(f'  {f} ({size} bytes)')
else:
    log_info('No binary captures')

log_info('')
log_info('To analyze:')
log_info(f'  wireshark -r {CAPTURE_DIR}/*.pcap')
log_info(f'  or: hexdump -C {CAPTURE_DIR}/*.bin | head -50')
