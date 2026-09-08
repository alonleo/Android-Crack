#!/usr/bin/env python3
"""Reverse-engineering runtime: validated, explicit UTF-8 project modifications.

Dependencies: Python standard library; stage_runtime StageContext supplied by caller.
Plan schema_version=1 accepts edits and (SDK stage only) manifest. Each edit is
{path,before,after,count,before_sha256,after_sha256}; hashes cover complete file
bytes, not snippets. One entry per file. Manifest is
{path,remove:[{tag,name}],before_sha256,after_sha256}; its after digest covers
ElementTree UTF-8 serialization with XML declaration, preserving comments.
No wildcard matching, recursive deletion, inferred patches or skip flags exist.
All requested source states and prospective XML/smali structures are checked
before writes. Only default app/src/main Android source/resource/asset inputs
are supported. Smali, C#, packed and native inputs require type-specific workers.
The required build is followed by separate device acceptance.
"""
from __future__ import annotations
import hashlib
import os
from pathlib import Path
import re
import tempfile
import xml.etree.ElementTree as ET

ANDROID = '{http://schemas.android.com/apk/res/android}'
SOURCE_EXTENSIONS = {'.java', '.kt', '.xml', '.json', '.lua', '.js', '.ts'}


def _keys(value, allowed, required):
    if not isinstance(value, dict) or set(value) - set(allowed) or set(required) - set(value):
        raise ValueError('Invalid plan fields; required: ' + ', '.join(required))


def _hash(data):
    return hashlib.sha256(data).hexdigest()


def _validate_source(path, text):
    if '\x00' in text:
        raise ValueError(f'Binary source is unsupported: {path}')
    if path.suffix == '.xml':
        try:
            ET.fromstring(text)
        except ET.ParseError as exc:
            raise ValueError(f'Invalid XML in {path}: {exc}') from exc
    if path.suffix == '.json':
        import json
        try:
            json.loads(text)
        except ValueError as exc:
            raise ValueError(f'Invalid JSON in {path}: {exc}') from exc


def _source(ctx, relative):
    if not isinstance(relative, str) or not relative or Path(relative).is_absolute() or '..' in Path(relative).parts:
        raise ValueError('Source path must be relative and contained')
    path = ctx.project_path(relative)
    # Validate the resolved target, so a symlink cannot disguise ignored inputs.
    source = path.resolve().relative_to(ctx.project_dir.resolve())
    parts = source.parts
    suffix = source.suffix
    supported = source.as_posix() == 'app/src/main/AndroidManifest.xml'
    if len(parts) >= 5 and parts[:3] == ('app', 'src', 'main'):
        kind = parts[3]
        supported = supported or (
            kind == 'java' and suffix in {'.java', '.kt'} or
            kind == 'kotlin' and suffix == '.kt' or
            kind == 'res' and len(parts) >= 6 and suffix == '.xml' or
            kind == 'assets' and suffix in {'.json', '.lua', '.js', '.ts', '.xml'})
    if not supported:
        raise ValueError(f'Not a default Android build input; requires a type-specific pipeline: {relative}')
    if not path.is_file() or path.suffix not in SOURCE_EXTENSIONS:
        raise ValueError(f'Unsupported source file: {relative}')
    data = path.read_bytes()
    try:
        text = data.decode('utf-8')
    except UnicodeDecodeError as exc:
        raise ValueError(f'Source must be UTF-8: {relative}') from exc
    _validate_source(path, text)
    return path, data, text


def apply_plan(ctx, stage):
    """Prepare every mutation first, then atomically replace each changed file.

    Writes are atomic per file; interruption between files is recoverable by the
    full-file after hashes. Build failures retain changes for diagnosis/retry.
    """
    if stage not in {'sdk-network-removal', 'revenue-forwarding', 'ui-hide'}:
        raise ValueError('Unsupported modification stage')
    plan = ctx.load_plan()
    allowed = {'schema_version', 'edits'}
    if stage == 'sdk-network-removal':
        allowed.add('manifest')
    _keys(plan, allowed, {'schema_version'})
    if type(plan['schema_version']) is not int or plan['schema_version'] != 1:
        raise ValueError('schema_version must be 1')
    edits = plan.get('edits', [])
    if not isinstance(edits, list) or not edits and 'manifest' not in plan:
        raise ValueError('Plan requires explicit edits or manifest removals')
    pending = {}
    evidence = []
    def remember(path, relative, old, new, operation):
        if path in pending:
            raise ValueError(f'Duplicate target: {relative}')
        pending[path] = (relative, old, new)
        evidence.append({'path': relative, 'operation': operation,
                         'before_sha256': _hash(old), 'after_sha256': _hash(new),
                         'changed': old != new})
    for item in edits:
        _keys(item, {'path', 'before', 'after', 'count', 'before_sha256', 'after_sha256'},
              {'path', 'before', 'after', 'count', 'before_sha256', 'after_sha256'})
        before, after = item['before'], item['after']
        if not isinstance(before, str) or not before or not isinstance(after, str) or before == after:
            raise ValueError('Edits require distinct before/after text and nonempty before')
        if type(item['count']) is not int or item['count'] < 1:
            raise ValueError('Edit count must be a positive integer')
        for key in ('before_sha256', 'after_sha256'):
            if not isinstance(item[key], str) or not re.fullmatch('[0-9a-f]{64}', item[key]):
                raise ValueError(f'{key} must be a lowercase SHA-256 digest')
        if item['before_sha256'] == item['after_sha256']:
            raise ValueError('Edit hashes must differ')
        path, old, text = _source(ctx, item['path'])
        if _hash(old) == item['after_sha256']:
            new = old
        elif _hash(old) == item['before_sha256']:
            if text.count(before) != item['count']:
                raise ValueError(f'Exact replacement count mismatch: {item["path"]}')
            updated = text.replace(before, after)
            _validate_source(path, updated)
            new = updated.encode('utf-8')
            if _hash(new) != item['after_sha256']:
                raise ValueError(f'Prospective after hash mismatch: {item["path"]}')
        else:
            raise ValueError(f'Source hash matches neither planned state: {item["path"]}')
        remember(path, item['path'], old, new, 'exact-edit')
    if 'manifest' in plan:
        item = plan['manifest']
        fields = {'path', 'remove', 'before_sha256', 'after_sha256'}
        _keys(item, fields, fields)
        for key in ('before_sha256', 'after_sha256'):
            if not isinstance(item[key], str) or not re.fullmatch('[0-9a-f]{64}', item[key]):
                raise ValueError(f'{key} must be a lowercase SHA-256 digest')
        if item['before_sha256'] == item['after_sha256']:
            raise ValueError('Manifest before and after hashes must differ')
        if not isinstance(item['remove'], list) or not item['remove']:
            raise ValueError('Manifest remove list must be nonempty')
        path, old, text = _source(ctx, item['path'])
        if path.resolve().relative_to(ctx.project_dir.resolve()).as_posix() != 'app/src/main/AndroidManifest.xml':
            raise ValueError('Manifest operation requires app/src/main/AndroidManifest.xml')
        current_hash = _hash(old)
        if current_hash not in {item['before_sha256'], item['after_sha256']}:
            raise ValueError('Manifest hash matches neither planned state')
        tree = ET.fromstring(text, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True)))
        if tree.tag != 'manifest':
            raise ValueError('Manifest root is required')
        seen, removed = set(), []
        for selector in item['remove']:
            _keys(selector, {'tag', 'name'}, {'tag', 'name'})
            tag, name = selector['tag'], selector['name']
            if tag not in {'activity', 'activity-alias', 'service', 'receiver', 'provider', 'meta-data', 'uses-permission', 'uses-permission-sdk-23'} or not isinstance(name, str) or not name or '*' in name:
                raise ValueError('Manifest selectors require supported exact tag/name')
            if (tag, name) in seen:
                raise ValueError('Duplicate manifest selector')
            seen.add((tag, name))
            parents = [tree] if tag.startswith('uses-permission') else tree.findall('application')
            matches = [(parent, node) for parent in parents for node in list(parent) if node.tag == tag and node.get(ANDROID + 'name') == name]
            if len(matches) > 1:
                raise ValueError('Ambiguous duplicate manifest component')
            for parent, node in matches:
                parent.remove(node)
                removed.append({'tag': tag, 'name': name})
        ET.register_namespace('android', ANDROID[1:-1])
        new = ET.tostring(tree, encoding='utf-8', xml_declaration=True) if removed else old
        if current_hash == item['after_sha256'] and removed:
            raise ValueError('Manifest after-state still contains requested removals')
        if current_hash == item['before_sha256'] and not removed:
            raise ValueError('Manifest removal matched no selectors in before-state')
        if _hash(new) != item['after_sha256']:
            raise ValueError('Manifest prospective after hash mismatch')
        _validate_source(path, new.decode('utf-8'))
        remember(path, item['path'], old, new, {'manifest_removed': removed, 'absent_selectors': item['remove']})
    # Recheck all bytes before the first write to catch concurrent source edits.
    for path, (_, old, _) in pending.items():
        if path.read_bytes() != old:
            raise ValueError(f'Source changed during validation: {path}')
    for path, (_, old, new) in pending.items():
        if old == new:
            continue
        fd, temporary = tempfile.mkstemp(prefix='.stage-write-', dir=path.parent)
        try:
            with os.fdopen(fd, 'wb') as stream:
                stream.write(new)
            os.chmod(temporary, path.stat().st_mode)
            os.replace(temporary, path)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    return {'changed_files': [relative for relative, old, new in pending.values() if old != new],
            'source_checks': evidence, 'device_acceptance': 'required'}
