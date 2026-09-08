#!/usr/bin/env python3
"""Manage the machine-readable SDK registry: list/get/add/update/delete.

Agent reads Markdown to decide; stage scripts consume schema_version=1 YAML.
No SDK cleaning is performed here. Explicit --registry overrides the shared file.
"""
from __future__ import annotations
import argparse
import json
import html
import os
from pathlib import Path
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT / 'skills/common/scripts/lib'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import common
from load_sdk_removal_registry import DEFAULT_REGISTRY, load_registry
import yaml

KEYS = {'manifest_drop_exact': 'name', 'manifest_drop_keyword_contains': 'name',
        'so_early_kill': 'name', 'build_config_stubs': 'class_path', 'meta_data_force_value': 'name'}
STRINGS = {'so_keyword_contains', 'raw_apk_drop_entries', 'smali_exclude_prefixes', 'engine_so_keep'}
SECTIONS = set(KEYS) | STRINGS


def identity(entry, section):
    return entry[KEYS[section]] if section in KEYS else entry


def validate(data):
    if not isinstance(data, dict) or str(data.get('schema_version')) != '1':
        raise ValueError('Expected schema_version: 1 mapping')
    for section in SECTIONS:
        entries = data.get(section)
        if not isinstance(entries, list):
            raise ValueError(f'{section} must be a list')
        seen = set()
        for item in entries:
            if section in KEYS and not isinstance(item, dict):
                raise ValueError(f'{section} requires mapping entries')
            name = item.get(KEYS[section]) if section in KEYS else item
            if not isinstance(name, str) or not name.strip() or name in seen:
                raise ValueError(f'{section}: invalid or duplicate identity {name!r}')
            seen.add(name)
            required = {'build_config_stubs': 'package', 'meta_data_force_value': 'value'}.get(section)
            if required and (required not in item or item[required] is None or item[required] == ''):
                raise ValueError(f'{section}: {name} requires {required}')


def infer_section(name):
    if name.startswith('lib/'):
        return 'raw_apk_drop_entries'
    if name.endswith('.so'):
        return 'so_keyword_contains'
    if name.endswith('.java'):
        return 'build_config_stubs'
    if '/' in name:
        return 'smali_exclude_prefixes'
    if '.' not in name and name[:1].isupper():
        return 'manifest_drop_exact'
    return 'manifest_drop_keyword_contains'


def render_document(data, filename):
    def cell(value):
        return html.escape(str(value)).replace('|', '&#124;').replace('\n', '<br>')
    lines = ['# 第三方 SDK 执行清单', '',
             f'> 自动生成自 [{filename}]({filename})。请通过 manage-sdk-registry.py 增删改查，勿手工编辑本文件。', '',
             '此表是 YAML 规则的阅读视图；关键词命中不证明可删除。Agent 仍须核对策略、引擎依赖与项目证据。', '']
    for section, entries in data.items():
        if section not in SECTIONS:
            continue
        lines += [f'## {section}', '', f'条目数：{len(entries)}', '', '| 匹配项 / 保留项 | 属性 |', '|---|---|']
        for entry in entries:
            fields = {k: v for k, v in entry.items() if k != KEYS[section]} if section in KEYS else {}
            lines.append(f'| {cell(identity(entry, section))} | {cell(json.dumps(fields, ensure_ascii=False)) if fields else "—"} |')
        lines.append('')
    return '\n'.join(lines) + '\n'


def save(path, data, original, write_registry=True):
    # Serialize/validate before replacing the shared input; retain initial comments.
    header = []
    for line in original.decode('utf-8-sig').splitlines():
        if line.startswith('#') or not line.strip():
            header.append(line)
        else:
            break
    output = ('\n'.join(header) + '\n' if header else '') + yaml.safe_dump(data, allow_unicode=True, sort_keys=False)
    validate(yaml.safe_load(output))
    lock = path.with_name(path.name + '.lock')
    descriptor = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    temporary = None
    try:
        os.close(descriptor)
        if path.read_bytes() != original:
            raise ValueError('Registry changed while editing; reload and retry')
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.sdk-registry-', suffix='.yaml', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(output.encode('utf-8'))
            stream.flush()
            os.fsync(stream.fileno())
        validate(load_registry(temporary))
        if write_registry:
            os.replace(temporary, path)
        else:
            temporary.unlink()
        document = path.with_suffix('.md')
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.sdk-document-', suffix='.md', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(render_document(data, path.name).encode('utf-8'))
        os.replace(temporary, document)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()
        lock.unlink()


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    common._REPO_ROOT = ROOT
    common.ensure_env()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['list', 'get', 'add', 'update', 'delete', 'validate', 'sync-doc'])
    parser.add_argument('--registry', type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument('--section', choices=sorted(SECTIONS))
    parser.add_argument('--name')
    parser.add_argument('--new-name')
    parser.add_argument('--why')
    parser.add_argument('--value')
    parser.add_argument('--package')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args(argv)
    try:
        path = args.registry.expanduser().resolve()
        original = path.read_bytes()
        data = yaml.safe_load(original)
        validate(data)
        if args.operation in ('validate', 'sync-doc'):
            if any(v is not None for v in (args.section, args.name, args.new_name, args.why, args.value, args.package)) or args.dry_run:
                raise ValueError('validate/sync-doc accept only --registry')
            document = path.with_suffix('.md')
            if args.operation == 'sync-doc':
                save(path, data, original, write_registry=False)
            elif not document.exists() or document.read_text(encoding='utf-8') != render_document(data, path.name):
                raise ValueError('Generated Markdown is missing or stale; run sync-doc')
            print(json.dumps({'operation': args.operation, 'valid': True, 'registry': str(path), 'document': str(document)}, ensure_ascii=False))
            return 0
        name = args.name.strip() if args.name is not None else None
        if args.operation != 'list' and not name:
            raise ValueError('--name must be non-empty')
        section = args.section
        if args.operation == 'add' and not section:
            section = infer_section(name)
        if args.operation not in ('list', 'add') and not section:
            raise ValueError('--section is required')
        if args.operation == 'list':
            if any(v is not None for v in (args.name, args.new_name, args.why, args.value, args.package)) or args.dry_run:
                raise ValueError('list accepts only --section and --registry')
            result = {'registry': str(path), 'section': section, 'entries': data[section] if section else data}
        else:
            if args.new_name is not None and args.operation != 'update':
                raise ValueError('--new-name is only valid for update')
            if args.operation in ('get', 'delete') and any(v is not None for v in (args.why, args.value, args.package)):
                raise ValueError('get/delete do not accept entry fields')
            entries = data[section]
            index = next((i for i, item in enumerate(entries) if identity(item, section) == name), None)
            changed = False
            if args.operation == 'get':
                if index is None:
                    raise ValueError(f'Entry not found: {section}/{name}')
                result = {'section': section, 'entry': entries[index]}
            else:
                if args.operation == 'delete':
                    if index is None:
                        raise ValueError(f'Entry not found: {section}/{name}')
                    entry = entries.pop(index)
                    changed = True
                elif args.operation == 'add' and index is not None:
                    entry = entries[index]  # Idempotent; never silently update.
                else:
                    if args.operation == 'update' and index is None:
                        raise ValueError(f'Entry not found: {section}/{name}')
                    new_name = args.new_name.strip() if args.new_name is not None else name
                    if not new_name:
                        raise ValueError('--new-name must be non-empty')
                    if section in STRINGS:
                        if args.package is not None or args.value is not None:
                            raise ValueError('String sections do not accept --package/--value')
                        entry = new_name
                    else:
                        entry = dict(entries[index]) if index is not None else {}
                        entry[KEYS[section]] = new_name
                        for field in ('why', 'package', 'value'):
                            value = getattr(args, field)
                            if value is not None:
                                if field == 'package' and section != 'build_config_stubs' or field == 'value' and section != 'meta_data_force_value':
                                    raise ValueError(f'{field} is not supported by {section}')
                                entry[field] = value
                    if index is None:
                        entries.append(entry)
                        changed = True
                    elif entries[index] != entry:
                        entries[index] = entry
                        changed = True
                validate(data)
                if not args.dry_run:
                    save(path, data, original, write_registry=changed)
                result = {'operation': args.operation, 'section': section, 'entry': entry,
                          'changed': changed, 'dry_run': args.dry_run, 'registry': str(path)}
                common.log_info(args.operation, section, name, 'preview' if args.dry_run else ('written' if changed else 'unchanged'))
        print(json.dumps(result, ensure_ascii=False))
        return 0
    except (OSError, ValueError, yaml.YAMLError) as error:
        common.log_error(str(error))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
