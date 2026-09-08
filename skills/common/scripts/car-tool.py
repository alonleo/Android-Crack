#!/usr/bin/env python3
"""
Corona SDK resource.car repacker.
Can extract and repack .car archives for APK modification.
"""
import struct
import os
import sys
import zipfile
import shutil

CAR_MAGIC = b'rac\x01'
HEADER_SIZE = 24

class CarArchive:
    def __init__(self, data=None):
        self.entries = []  # (name, offset_in_data_section)
        self.data_blocks = {}  # name -> raw bytes
        self.header_data = None
        self.original_data = data
        if data:
            self._parse(data)
    
    def _parse(self, data):
        if data[:4] != CAR_MAGIC:
            raise ValueError('Not a valid CAR file')
        
        data_start = struct.unpack_from('<I', data, 20)[0]
        self.header_data = data[:data_start]
        
        # Parse directory entries
        off = HEADER_SIZE
        temp_entries = []
        while off < data_start:
            name_len = struct.unpack_from('<I', data, off)[0]
            if name_len == 0 or name_len > 500:
                break
            pad = ((name_len + 4) // 4) * 4 - name_len
            padded_len = name_len + pad
            if off + 4 + padded_len + 8 > len(data):
                break
            name = data[off+4:off+4+name_len].decode('utf-8', errors='replace').rstrip('\x00')
            rel_off = struct.unpack_from('<I', data, off+4+padded_len+4)[0]
            temp_entries.append((name, data_start + rel_off))
            off += 4 + padded_len + 8
        
        # Sort by offset and extract blocks
        temp_entries.sort(key=lambda e: e[1])
        for i in range(len(temp_entries)):
            name, abs_off = temp_entries[i]
            end_off = temp_entries[i+1][1] if i+1 < len(temp_entries) else len(data)
            self.data_blocks[name] = data[abs_off:end_off]
        
        self.entries = [(name, off) for name, off in temp_entries]
    
    def extract_all(self, out_dir):
        os.makedirs(out_dir, exist_ok=True)
        for name, _ in self.entries:
            safe_name = name.replace('/', '_').replace('\\', '_')
            path = os.path.join(out_dir, safe_name)
            with open(path, 'wb') as f:
                f.write(self.data_blocks.get(name, b''))
        return out_dir
    
    def set_block(self, name, new_data):
        self.data_blocks[name] = new_data
    
    def get_block(self, name):
        return self.data_blocks.get(name, b'')
    
    def repack(self):
        """Repack into CAR file format."""
        # Sort entries by name for deterministic output
        sorted_names = sorted(self.data_blocks.keys())
        
        # Build directory entries
        dir_data = b''
        data_section = b''
        current_data_offset = 0
        
        for name in sorted_names:
            block = self.data_blocks[name]
            name_bytes = name.encode('utf-8') + b'\x00'
            name_len = len(name_bytes)
            pad = ((name_len + 4) // 4) * 4 - name_len
            padded_len = name_len + pad
            
            # Directory entry
            dir_data += struct.pack('<I', name_len)
            dir_data += name_bytes
            dir_data += b'\x00' * pad
            dir_data += struct.pack('<I', 1)  # count
            dir_data += struct.pack('<I', current_data_offset)
            
            # Data
            data_section += block
            current_data_offset += len(block)
        
        dir_size = len(dir_data)
        data_start = HEADER_SIZE + dir_size
        
        # Build header
        header = struct.pack('<IIIIII',
            0x01636172,  # magic 'car\x01'
            1,           # count
            HEADER_SIZE, # dir offset
            dir_size,    # dir size
            1,           # unknown
            data_start   # data start
        )
        
        return header + dir_data + data_section
    
    def patch_lua_bool(self, name, var_name, new_value):
        """Binary-patch a boolean constant in a .lu file."""
        block = self.data_blocks.get(name)
        if not block:
            return False
        
        # Find Lua bytecode
        lua_pos = block.find(b'\x1bLua')
        if lua_pos < 0:
            return False
        
        lua_data = bytearray(block[lua_pos:])
        
        # Parse constants to find the variable name and its boolean value
        pos = 12  # After Lua header
        src_size = struct.unpack_from('<I', lua_data, pos)[0]
        pos += 4
        if src_size > 0:
            pos += src_size
        
        pos += 8  # line numbers
        pos += 4  # flags
        
        # Skip code
        code_size = struct.unpack_from('<I', lua_data, pos)[0]
        pos += 4 + code_size * 4
        
        # Parse constants recursively to find var_name and change its boolean
        def find_and_patch(data, start, target_name, new_val):
            """Find target_name constant and patch its next boolean sibling."""
            const_count = struct.unpack_from('<I', data, start)[0]
            p = start + 4
            found_name = False
            
            for _ in range(const_count):
                if p >= len(data):
                    break
                ctype = data[p]
                p += 1
                
                if ctype == 4:  # String
                    slen = struct.unpack_from('<I', data, p)[0]
                    p += 4
                    s = data[p:p+slen-1].decode('utf-8', errors='replace')
                    if s == target_name:
                        found_name = True
                    p += slen
                
                elif ctype == 1:  # Boolean
                    if found_name:
                        data[p] = 1 if new_val else 0
                        return True, p
                    p += 1
                
                elif ctype == 3:  # Number
                    p += 8
                elif ctype == 0:  # Nil
                    pass
                else:
                    break
            
            return False, p
        
        # First check main function's constants
        const_start = pos
        patched, _ = find_and_patch(lua_data, const_start, var_name, new_value)
        
        if patched:
            new_block = block[:lua_pos] + bytes(lua_data)
            self.data_blocks[name] = new_block
            return True
        
        return False
    
    def patch_lua_string(self, name, old_str, new_str):
        """Binary-patch a string constant in a .lu file (must be same length)."""
        if len(old_str) != len(new_str):
            print(f'  ERROR: String lengths differ ({len(old_str)} vs {len(new_str)})')
            return False
        
        block = self.data_blocks.get(name)
        if not block:
            return False
        
        if old_str.encode() not in block:
            return False
        
        new_block = block.replace(old_str.encode(), new_str.encode(), 1)
        self.data_blocks[name] = new_block
        return True


def main():
    if len(sys.argv) < 2:
        print('Usage:')
        print('  car-tool.py extract <apk_or_car> <out_dir>')
        print('  car-tool.py repack <apk_or_car> <in_dir> <output_car>')
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == 'extract':
        src = sys.argv[2]
        out = sys.argv[3] if len(sys.argv) > 3 else 'car_out'
        
        if src.endswith('.apk') or src.endswith('.xapk'):
            with zipfile.ZipFile(src, 'r') as z:
                car_data = z.read('assets/resource.car')
        else:
            with open(src, 'rb') as f:
                car_data = f.read()
        
        car = CarArchive(car_data)
        car.extract_all(out)
        print(f'Extracted {len(car.entries)} files to {out}')
    
    elif cmd == 'repack':
        src = sys.argv[2]
        in_dir = sys.argv[3]
        out_car = sys.argv[4] if len(sys.argv) > 4 else 'resource.car'
        
        if src.endswith('.apk') or src.endswith('.xapk'):
            with zipfile.ZipFile(src, 'r') as z:
                car_data = z.read('assets/resource.car')
        else:
            with open(src, 'rb') as f:
                car_data = f.read()
        
        car = CarArchive(car_data)
        
        # Replace blocks from in_dir
        for fname in os.listdir(in_dir):
            # Try to find matching entry
            name = fname.replace('_', '/', 1) if '/' not in fname else fname
            # Also try matching without extension change
            for entry_name in car.data_blocks:
                safe_entry = entry_name.replace('/', '_')
                if safe_entry == fname or entry_name == fname:
                    with open(os.path.join(in_dir, fname), 'rb') as f:
                        car.set_block(entry_name, f.read())
                    break
        
        new_car = car.repack()
        with open(out_car, 'wb') as f:
            f.write(new_car)
        print(f'Repacked {len(car.entries)} files to {out_car} ({len(new_car)} bytes)')


if __name__ == '__main__':
    main()
