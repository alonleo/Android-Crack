#!/usr/bin/env python3
import os, sys, subprocess
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'lib'))
from common import *

if len(sys.argv) < 2:
    die(f'Usage: {sys.argv[0]} <path/to/librslg.so>\nPatches socket_connect to return success immediately')

so_file = sys.argv[1]
require_file(so_file)

backup = f'{so_file}.bak'
if not os.path.isfile(backup):
    import shutil
    shutil.copy2(so_file, backup)
    log_info(f'[*] Backup saved: {backup}')

# Try readelf first
offset = None
try:
    r = subprocess.run(['readelf', '-s', so_file], capture_output=True, text=True)
    for line in r.stdout.splitlines():
        if 'socket_connect' in line:
            parts = line.split()
            if len(parts) >= 2:
                offset_str = parts[1].lstrip('0x') or '0'
                offset = int(offset_str, 16)
                break
except FileNotFoundError:
    pass

if offset is not None:
    offset_aligned = offset & ~1
    log_info(f'[*] socket_connect @ 0x{offset_aligned:x}')
    log_info('[*] Patching...')
    with open(so_file, 'rb') as f:
        so = bytearray(f.read())
    patch = bytes([0x00, 0x20, 0x08, 0xb0, 0xf0, 0x8f, 0xbd, 0xe8])
    so[offset_aligned:offset_aligned + 8] = patch
    with open(so_file, 'wb') as f:
        f.write(so)
    log_success(f'Patched socket_connect at 0x{offset_aligned:x}')
    log_info('    socket_connect now returns 0 immediately')
else:
    log_warn('[-] socket_connect symbol not found via readelf')
    log_info('    Trying alternative: searching for push pattern...')
    with open(so_file, 'rb') as f:
        data = f.read()
    sig = bytes.fromhex('2de9f341')
    idx = data.find(sig)
    if idx >= 0:
        even_off = idx
        so = bytearray(data)
        patch = bytes([0x00, 0x20, 0x08, 0xb0, 0xf0, 0x8f, 0xbd, 0xe8])
        so[even_off:even_off + 8] = patch
        with open(so_file, 'wb') as f:
            f.write(so)
        log_success(f'[+] Patched socket_connect at 0x{even_off:x}')
    else:
        die('Could not find socket_connect function signature')
