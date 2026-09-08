#!/usr/bin/env python3
"""
Corona SDK resource.car extractor.
Extracts .lu files from Corona Archive (CAR) format.
"""
import struct
import os
import sys
import zipfile

CAR_HEADER_MAGIC = b'rac\x01'

def parse_car(car_data):
    """Parse CAR directory and return list of (name, abs_offset) tuples."""
    if car_data[:4] != CAR_HEADER_MAGIC:
        raise ValueError('Not a valid CAR file (bad magic)')
    
    data_start = struct.unpack_from('<I', car_data, 20)[0]
    
    off = 24
    entries = []
    while off < data_start:
        name_len = struct.unpack_from('<I', car_data, off)[0]
        if name_len == 0 or name_len > 500:
            break
        pad = ((name_len + 4) // 4) * 4 - name_len
        padded_len = name_len + pad
        if off + 4 + padded_len + 8 > len(car_data):
            break
        name = car_data[off+4:off+4+name_len].decode('utf-8', errors='replace').rstrip('\x00')
        rel_off = struct.unpack_from('<I', car_data, off+4+padded_len+4)[0]
        entries.append((name, data_start + rel_off))
        off += 4 + padded_len + 8
    
    return sorted(entries, key=lambda e: e[1])

def extract_strings_from_block(block):
    """Extract all readable strings from a data block."""
    strings = []
    i = 0
    while i < len(block):
        c = block[i]
        if 32 <= c < 127:
            j = i
            while j < len(block) and 32 <= block[j] < 127:
                j += 1
            s = block[i:j].decode('ascii')
            if len(s) >= 4:
                strings.append(s)
            i = j
        else:
            i += 1
    return strings

def extract_lua_bytecode(block):
    """Extract Lua 5.1 bytecode from a data block if present."""
    pos = block.find(b'\x1bLua')
    if pos < 0:
        return None, pos
    return block[pos:], pos

def extract_all_strings(car_path, out_dir):
    """Extract all string constants from .lu files in a CAR archive."""
    # Read CAR from APK or standalone
    if car_path.endswith('.apk') or car_path.endswith('.xapk'):
        with zipfile.ZipFile(car_path, 'r') as z:
            car_data = z.read('assets/resource.car')
    else:
        with open(car_path, 'rb') as f:
            car_data = f.read()
    
    entries = parse_car(car_data)
    
    os.makedirs(out_dir, exist_ok=True)
    
    for i in range(len(entries)):
        name, abs_off = entries[i]
        next_off = entries[i+1][1] if i+1 < len(entries) else len(car_data)
        block = car_data[abs_off:next_off]
        
        safe_name = name.replace('/', '_').replace('\\', '_')
        
        # Extract strings
        strings = extract_strings_from_block(block)
        
        # Extract Lua bytecode if present
        lua_data, lua_pos = extract_lua_bytecode(block)
        
        # Write strings
        strings_path = os.path.join(out_dir, safe_name + '.strings.txt')
        with open(strings_path, 'w', encoding='utf-8') as f:
            f.write(f'# File: {name}\n')
            f.write(f'# Block size: {len(block)}\n')
            f.write(f'# Lua at offset: {lua_pos}\n')
            f.write(f'# Strings found: {len(strings)}\n\n')
            for s in strings:
                f.write(f'{s}\n')
        
        # Write Lua bytecode if found
        if lua_data:
            lua_path = os.path.join(out_dir, safe_name + '.lu')
            with open(lua_path, 'wb') as f:
                f.write(lua_data)
        
        # Write raw block for reference
        raw_path = os.path.join(out_dir, safe_name + '.raw')
        with open(raw_path, 'wb') as f:
            f.write(block)
    
    return entries

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: extract-corona-car.py <apk_or_car_path> [output_dir]')
        sys.exit(1)
    
    car_path = sys.argv[1]
    out_dir = sys.argv[2] if len(sys.argv) > 2 else 'car_extracted'
    
    entries = extract_all_strings(car_path, out_dir)
    print(f'Extracted {len(entries)} files from CAR archive to {out_dir}')
