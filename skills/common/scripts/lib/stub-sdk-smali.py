#!/usr/bin/env python3
"""Robust smali method stubber - replace body completely."""
import re
import sys
from pathlib import Path

crack_root = Path(sys.argv[1])
pkgs_file = Path(sys.argv[2])
pkgs = [p for p in pkgs_file.read_text().splitlines() if p]

smali_dirs = sorted([p for p in crack_root.iterdir() if p.is_dir() and p.name.startswith('smali')])

files = []
for sdir in smali_dirs:
    for pkg in pkgs:
        pkg_dir = sdir / pkg
        if pkg_dir.exists():
            for sm in pkg_dir.rglob("*.smali"):
                files.append(sm)
print(f"Found {len(files)} files", flush=True)


def min_registers(header):
    """Compute minimum required registers based on parameter count."""
    is_static = bool(re.search(r'\bstatic\b', header))
    is_abstract = bool(re.search(r'\babstract\b', header))
    is_native = bool(re.search(r'\bnative\b', header))
    if is_abstract or is_native:
        return None
    m = re.search(r'\(([^)]*)\)', header)
    if not m:
        return 1
    params_str = m.group(1)
    count = 0
    # Parse: types are L<name>; or [arraytype or primitive (B/C/D/F/I/J/S/V/Z)
    # We iterate char by char
    i = 0
    while i < len(params_str):
        c = params_str[i]
        if c == 'L':
            # Object type: ends at ;
            end = params_str.find(';', i)
            if end == -1:
                break
            count += 1
            i = end + 1
        elif c == '[':
            # Array type: [ followed by type
            i += 1
            continue
        elif c in 'VZCBSIFJD':
            # Primitive type
            if c in 'JD':
                count += 2
            else:
                count += 1
            i += 1
        else:
            i += 1
    return max(count + (0 if is_static else 1), 1)


def fix_file(content):
    lines = content.split('\n')
    new_lines = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped.startswith('.method'):
            new_lines.append(line)
            i += 1
            continue

        # We found a .method line
        method_header = line
        new_lines.append(line)
        i += 1

        # Process the body until .end method
        mr = min_registers(method_header)

        # Add .registers if method is non-abstract/non-native
        if mr is not None:
            new_lines.append(f"    .registers {mr}")
            new_lines.append("    return-void")

        # Skip all body lines until .end method
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            if stripped.startswith('.end method'):
                new_lines.append(line)
                i += 1
                break
            # Drop any existing .registers, .locals, .line, body instructions
            i += 1

    return '\n'.join(new_lines)


count = 0
errors = 0
for f in files:
    try:
        content = f.read_text(encoding='utf-8', errors='ignore')
        if '.method' not in content:
            continue
        new_content = fix_file(content)
        if new_content != content:
            f.write_text(new_content, encoding='utf-8')
            count += 1
    except Exception as e:
        errors += 1
        if errors < 3:
            print(f"ERR {f}: {e}", file=sys.stderr)
    if count % 1000 == 0 and count > 0:
        print(f"processed {count}", flush=True)
print(f"Modified {count}/{len(files)} files (errors={errors})", flush=True)