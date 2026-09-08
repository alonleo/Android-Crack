#!/usr/bin/env python3
"""Reverse-project library: explicit, evidence-producing device verification.

Dependencies: configured project ADB/AAPT2, Python 3, Pillow. execute accepts runner and
sleeper injection for offline regression. Plan: apk (project-relative), package,
activity, optional serial/settle_seconds, checkpoints (name, purpose, actions,
assertions). UI assertions use exact attribute/value and a boolean present;
screenshot assertions require a workdir-relative reference and max_mean_error
in [0, .1]. Font/image assertions also require a focused region [x,y,width,height].
References must be independently reviewed expected screenshots.
No uninstall, network setting changes, log clearing, or arbitrary shell actions.
"""
from __future__ import annotations

import hashlib
import io
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import time
import uuid
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / 'skills/common/scripts/lib'))
import common
from stage_runtime import tool_command, contained, atomic_write


def _number(value, low, high):
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value) or not low <= value <= high:
        raise ValueError(f'Expected number in [{low}, {high}], got {value!r}')
    return value


def _validate(ctx, plan):
    if not isinstance(plan, dict):
        raise ValueError('Device plan must be an object')
    package = plan.get('package', '')
    activity = plan.get('activity', '')
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]*(?:\.[A-Za-z][A-Za-z0-9_]*)+', package):
        raise ValueError('Valid explicit package required')
    if not re.fullmatch(r'\.?[A-Za-z][A-Za-z0-9_.]*', activity):
        raise ValueError('Valid explicit activity required')
    _number(plan.get('settle_seconds', 3), 0, 60)
    checkpoints = plan.get('checkpoints')
    if not isinstance(checkpoints, list) or not checkpoints:
        raise ValueError('At least one target checkpoint is required')
    names = set()
    for point in checkpoints:
        name = point.get('name', '')
        if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', name) or name in names:
            raise ValueError('Checkpoint names must be unique safe basenames')
        names.add(name)
        if not isinstance(point.get('purpose'), str) or not point['purpose'].strip():
            raise ValueError('Each checkpoint requires a concrete purpose')
        assertions = point.get('assertions')
        if not isinstance(assertions, list) or not assertions:
            raise ValueError('Explicit assertions required; alive alone is not verification')
        positive = negative = visual = False
        for check in assertions:
            if check.get('kind') == 'ui':
                if check.get('attribute') not in ('text', 'resource-id', 'content-desc') or not isinstance(check.get('value'), str) or not check['value']:
                    raise ValueError('UI assertion requires a supported attribute and nonempty exact value')
                if type(check.get('present')) is not bool:
                    raise ValueError('UI assertion present must be boolean')
                positive |= check['present']
                negative |= not check['present']
            elif check.get('kind') == 'screenshot':
                ctx.input_path(check['reference'])
                _number(check.get('max_mean_error'), 0, 0.1)
                region = check.get('region')
                if region is not None:
                    if not isinstance(region, list) or len(region) != 4:
                        raise ValueError('Screenshot region must be [x,y,width,height]')
                    for index, value in enumerate(region):
                        _number(value, 0 if index < 2 else 1, 100000)
                        if type(value) is not int:
                            raise ValueError('Screenshot region values must be integers')
                if ctx.stage in ('font-device-verify', 'image-device-verify') and region is None:
                    raise ValueError('Font/image verification requires a focused screenshot region')
                visual = True
            else:
                raise ValueError('Unknown assertion kind')
        if not positive and not visual:
            raise ValueError('A positive target-page assertion is required')
        if ctx.stage in ('font-device-verify', 'image-device-verify') and not visual:
            raise ValueError('Font/image rendering requires an independently reviewed reference screenshot')
        if ctx.stage == 'ui-hide-device-verify' and not negative:
            raise ValueError('UI hide verification requires an absent target assertion')
        if ctx.stage == 'revenue-device-verify' and point['purpose'] not in ('reward', 'purchase', 'local-state'):
            raise ValueError('Revenue checkpoint purpose must identify reward, purchase, or local-state')
        if ctx.stage == 'text-device-verify' and not any(c.get('kind') == 'ui' and c.get('attribute') == 'text' and c.get('present') for c in assertions) and not visual:
            raise ValueError('Text verification requires expected displayed text or visual reference')
        for action in point.get('actions', []):
            _action_args(action)
    return package, activity, checkpoints


def _action_args(action):
    kind = action.get('kind')
    if kind == 'wait':
        _number(action.get('seconds'), 0, 60)
        return None
    fields = {'tap': ('x', 'y'), 'swipe': ('x1', 'y1', 'x2', 'y2', 'duration_ms'), 'keyevent': ('code',)}
    if kind not in fields:
        raise ValueError('Only tap, swipe, numeric keyevent and wait actions are supported')
    numbers = []
    for key in fields[kind]:
        value = _number(action.get(key), 0, 60000 if key == 'duration_ms' else 10000)
        if int(value) != value:
            raise ValueError('Input coordinates/key codes must be integers')
        numbers.append(str(int(value)))
    return ['shell', 'input', kind, *numbers]


def execute(ctx, runner=subprocess.run, sleeper=time.sleep):
    """Verify one stage, returning evidence; raise on any incomplete verification."""
    from PIL import Image, ImageChops, ImageStat
    plan = ctx.load_plan()
    package, activity, points = _validate(ctx, plan)
    filenames = ['install.txt', 'start.txt', 'experience-sync-task.json']
    filenames.extend(f"{point['name']}.{extension}" for point in points for extension in ('log', 'png', 'xml'))
    outputs = {}
    for filename in filenames:
        raw_path = ctx.output_dir / filename
        if raw_path.is_symlink() or raw_path.with_name(raw_path.name + '.writing').is_symlink():
            raise ValueError(f'Unsafe evidence symlink: {raw_path}')
        outputs[filename] = contained(ctx.output_dir, filename, False)
    def evidence_write(filename, data):
        raw_path = ctx.output_dir / filename
        if raw_path.is_symlink():
            raise ValueError(f'Unsafe evidence symlink: {raw_path}')
        path = contained(ctx.output_dir, filename, False)
        atomic_write(path, data.encode('utf-8') if isinstance(data, str) else data)
    apk = ctx.project_path(plan['apk'])
    if not apk.is_file() or not apk.stat().st_size:
        raise ValueError('Installable APK file required')
    apk_hash = hashlib.sha256(apk.read_bytes()).hexdigest()
    release_dir = ctx.project_path('app/build/outputs/apk/release', must_exist=False)
    releases = [p for p in release_dir.glob('*.apk') if p.is_file() and not p.is_symlink()]
    if len(releases) != 1 or hashlib.sha256(releases[0].read_bytes()).hexdigest() != apk_hash:
        raise ValueError('Verification APK must match the single project release output by SHA256')
    aapt_command = tool_command('AAPT2', common.aapt2)
    badging = runner([*aapt_command, 'dump', 'badging', str(apk)], capture_output=True,
                     text=True, encoding='utf-8', errors='replace', timeout=120)
    if badging.returncode:
        raise ValueError(f'APK package inspection failed: {badging.stderr}')
    package_matches = re.findall(r"^package: name='([^']+)'", badging.stdout, re.M)
    if package_matches != [package]:
        raise ValueError('APK manifest package does not match the device plan package')
    # Decode all references before modifying the device.
    for point in points:
        for check in point['assertions']:
            if check['kind'] == 'screenshot':
                with Image.open(ctx.input_path(check['reference'])) as expected:
                    if 'region' in check:
                        x, y, width, height = check['region']
                        if x + width > expected.width or y + height > expected.height:
                            raise ValueError('Screenshot region exceeds reference image bounds')
                    expected.verify()
    command = tool_command('ADB_BIN', common.adb)
    common.log_info(f'Verifying {ctx.stage} against explicit device assertions')
    def call(args, serial=None, binary=False):
        result = runner([*command, *(['-s', serial] if serial else []), *args],
                        capture_output=True, text=not binary, timeout=120,
                        **({} if binary else {'encoding': 'utf-8', 'errors': 'replace'}))
        if result.returncode:
            raise ValueError(f'ADB {args[0]} failed ({result.returncode}): {result.stderr!r}')
        return result.stdout
    connected = []
    for line in call(['devices']).splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[1] == 'device':
            connected.append(parts[0])
    selected = plan.get('serial') or os.environ.get('ANDROID_SERIAL')
    if selected:
        if selected not in connected:
            raise ValueError('Requested device is not online')
    elif len(connected) == 1:
        selected = connected[0]
    else:
        raise ValueError('Exactly one online device or an explicit online serial is required')
    ctx.output_dir.mkdir(parents=True, exist_ok=True)
    install = call(['install', '-r', str(apk)], selected)
    evidence_write('install.txt', install)
    if not re.search(r'^Success\s*$', install, re.M):
        raise ValueError('ADB did not confirm install success')
    call(['shell', 'am', 'force-stop', package], selected)
    started_at = call(['shell', 'date', '+%m-%d_%H:%M:%S.000'], selected).strip().replace('_', ' ')
    if not re.fullmatch(r'\d\d-\d\d \d\d:\d\d:\d\d\.\d{3}', started_at):
        raise ValueError('Device log timestamp unavailable')
    started = call(['shell', 'am', 'start', '-W', '-n', f'{package}/{activity}'], selected)
    evidence_write('start.txt', started)
    if not re.search(r'^Status:\s*ok\s*$', started, re.M) or re.search(r'Error|Exception', started):
        raise ValueError('Activity launch did not report Status: ok')
    sleeper(plan.get('settle_seconds', 3))
    first_pid = call(['shell', 'pidof', package], selected).strip()
    if not re.fullmatch(r'[1-9][0-9]*', first_pid):
        raise ValueError('Target process absent or ambiguous after startup')
    evidence = []
    for point in points:
        for action in point.get('actions', []):
            args = _action_args(action)
            if args is None:
                sleeper(action['seconds'])
            else:
                call(args, selected)
        pid = call(['shell', 'pidof', package], selected).strip()
        if not re.fullmatch(r'[1-9][0-9]*', pid):
            raise ValueError('Target process absent or ambiguous')
        if first_pid is not None and first_pid != pid:
            raise ValueError('Target process restarted during verification')
        first_pid = pid
        logs = call(['logcat', '-d', '-v', 'threadtime', '-T', started_at, f'--pid={pid}'], selected)
        evidence_write(f"{point['name']}.log", logs)
        if re.search(r'FATAL EXCEPTION|Fatal signal|JNI DETECTED ERROR|\bANR in\b', logs):
            raise ValueError('Current target process has fatal runtime errors')
        screenshot = call(['exec-out', 'screencap', '-p'], selected, binary=True)
        if not screenshot.startswith(b'\x89PNG\r\n\x1a\n'):
            raise ValueError('Device screenshot is not PNG binary')
        image_path = outputs[f"{point['name']}.png"]
        evidence_write(f"{point['name']}.png", screenshot)
        with Image.open(io.BytesIO(screenshot)) as decoded:
            actual = decoded.convert('RGB')
        remote = f'/data/local/tmp/codex-verify-{uuid.uuid4().hex}.xml'
        try:
            call(['shell', 'uiautomator', 'dump', remote], selected)
            xml = call(['exec-out', 'cat', remote], selected, binary=True)
        finally:
            call(['shell', 'rm', '-f', remote], selected)
        evidence_write(f"{point['name']}.xml", xml)
        tree = ET.fromstring(xml)
        nodes = [node for node in tree.iter('node') if node.get('package') == package]
        if not nodes:
            raise ValueError('No target-app UI hierarchy; target page cannot be established')
        checks = []
        for check in point['assertions']:
            if check['kind'] == 'ui':
                found = any(node.get(check['attribute']) == check['value'] for node in nodes)
                if found != check['present']:
                    raise ValueError(f"UI assertion failed: {check}")
                checks.append(dict(check, matched=True))
            else:
                reference = ctx.input_path(check['reference'])
                with Image.open(reference) as decoded:
                    expected = decoded.convert('RGB')
                if expected.size != actual.size:
                    raise ValueError('Reference/device screenshot dimensions differ')
                actual_region = actual
                if 'region' in check:
                    x, y, width, height = check['region']
                    if x + width > actual.width or y + height > actual.height:
                        raise ValueError('Screenshot region exceeds image bounds')
                    box = (x, y, x + width, y + height)
                    actual_region = actual.crop(box)
                    expected = expected.crop(box)
                error = sum(ImageStat.Stat(ImageChops.difference(actual_region, expected)).mean) / (3 * 255)
                if error > check['max_mean_error']:
                    raise ValueError(f"Visual reference mismatch: {error} > {check['max_mean_error']}")
                checks.append(dict(check, mean_error=error, reference_sha256=hashlib.sha256(reference.read_bytes()).hexdigest()))
        if call(['shell', 'pidof', package], selected).strip() != pid:
            raise ValueError('Target died or restarted while collecting evidence')
        final_logs = call(['logcat', '-d', '-v', 'threadtime', '-T', started_at, f'--pid={pid}'], selected)
        evidence_write(f"{point['name']}.log", final_logs)
        if re.search(r'FATAL EXCEPTION|Fatal signal|JNI DETECTED ERROR|\bANR in\b', final_logs):
            raise ValueError('Target process failed while collecting evidence')
        evidence.append({'name': point['name'], 'purpose': point['purpose'], 'pid': pid,
                         'screenshot': str(image_path), 'screenshot_sha256': hashlib.sha256(screenshot).hexdigest(),
                         'ui_dump': str(ctx.output_dir / f"{point['name']}.xml"), 'checks': checks})
    task = {'stage': ctx.stage, 'action': 'Agent must review device evidence and extract reusable scripts/experience under AGENTS.md §1.6', 'completed': False}
    evidence_write('experience-sync-task.json', json.dumps(task, ensure_ascii=False, indent=2))
    return {'apk': str(apk), 'apk_sha256': apk_hash, 'device_serial': selected,
            'package': package, 'checkpoints': evidence, 'experience_sync_task': task,
            'scope': 'Declared stage assertions only; final project acceptance remains separate'}
