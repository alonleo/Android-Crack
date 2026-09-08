#!/usr/bin/env python3
"""Reverse-engineering runtime: preflight and apply decoded-asset localization.

Dependencies: Python 3; Pillow (including FreeType) for fonts and images.
This module does not unpack engine containers or infer translations. Plans must
name existing, editable files. Every input is validated before any write.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
from pathlib import Path
import re
import struct
import tempfile
from xml.parsers import expat


def _items(plan, key):
    values = plan.get(key)
    if not isinstance(values, list) or not values or any(not isinstance(v, dict) for v in values):
        raise ValueError(f"plan.{key} must be a nonempty list of objects")
    return values


def _string(item, key):
    value = item.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"{key} must be a nonempty string")
    return value


def _path(ctx, value, project):
    if not isinstance(value, str) or not value or Path(value).is_absolute() or ".." in Path(value).parts:
        raise ValueError("asset paths must be relative and cannot traverse parents")
    path = ctx.project_path(value) if project else ctx.input_path(value)
    root = ctx.project_dir if project else ctx.work_dir
    if not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError(f"asset is outside its root or not a file: {value}")
    if project:
        parts = path.resolve().relative_to(root.resolve()).parts
        if len(parts) < 5 or parts[:3] != ("app", "src", "main") or parts[3] not in ("assets", "res"):
            raise ValueError("editable localization targets must be app/src/main/assets or app/src/main/res build inputs")
    return path


_TOKENS = re.compile(r"%(?:\d+\$)?[-#+ 0,(<]*\d*(?:\.\d+)?(?:[tT][a-zA-Z]|[a-zA-Z%])|\{[^{}\r\n]+\}|\\(?:u[0-9a-fA-F]{4}|.)|</?[^>]+>")


def _preserve_tokens(source, target):
    if _TOKENS.findall(source) != _TOKENS.findall(target):
        raise ValueError("translation changes placeholder order, escapes, or markup")


def _xml_spans(data):
    """Expat byte positions retain original XML comments, attributes and whitespace."""
    if b"<!DOCTYPE" in data or b"<!ENTITY" in data:
        raise ValueError("DTD/entity declarations require an engine-specific resource handler")
    parser = expat.ParserCreate()
    stack, spans = [], []

    def start(name, attrs):
        offset = parser.CurrentByteIndex
        quote = None
        for index in range(offset, len(data)):
            char = data[index]
            if quote:
                if char == quote:
                    quote = None
            elif char in (34, 39):
                quote = char
            elif char == 62:
                break
        else:
            raise ValueError("unterminated XML tag")
        eligible = (name == "string" and len(stack) == 1 and stack[0][0] == "resources") or (
            name == "item" and len(stack) == 2 and stack[0][0] == "resources" and stack[-1][0] in ("string-array", "plurals"))
        eligible = eligible and attrs.get("translatable") != "false" and all(s[3].get("translatable") != "false" for s in stack)
        stack.append((name, index + 1, eligible, attrs, data[index - 1:index] == b"/"))

    def end(name):
        _, begin, eligible, _, self_closing = stack.pop()
        if eligible and not self_closing:
            spans.append((begin, parser.CurrentByteIndex))

    parser.StartElementHandler = start
    parser.EndElementHandler = end
    try:
        parser.Parse(data, True)
    except expat.ExpatError as exc:
        raise ValueError(f"invalid decoded Android XML: {exc}") from exc
    return sorted(spans)


def _prepare_text(ctx, plan):
    prepared = []
    for item in _items(plan, "files"):
        path = _path(ctx, _string(item, "path"), True)
        data = path.read_bytes()
        baseline = data
        try:
            text = data.decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("text must be decoded UTF-8; packed/encoded resources need their type handler") from exc
        if "\x00" in text:
            raise ValueError("binary resources need their type-specific decoder")
        mode = item.get("format")
        if mode not in ("android-xml", "text"):
            raise ValueError("text format must explicitly be android-xml or text")
        if path.suffix.lower() == ".xml" and mode != "android-xml":
            raise ValueError("XML targets require android-xml resource mode")
        if path.suffix.lower() == ".json":
            json.loads(text)
        rules = _items(item, "replacements")
        normalized = []
        for rule in rules:
            source, target = _string(rule, "source"), _string(rule, "target")
            count = rule.get("count")
            if type(count) is not int or count < 1 or source == target:
                raise ValueError("replacement requires a positive integer count and distinct source/target")
            _preserve_tokens(source, target)
            normalized.append((source, target, count))
        # Overlapping rules make retries ambiguous and can silently undo prior translations.
        for index, (source, target, _) in enumerate(normalized):
            for other_source, other_target, _ in normalized[index + 1:]:
                if any(a in b or b in a for a in (source, target) for b in (other_source, other_target)):
                    raise ValueError("overlapping translation rules are not safely idempotent")
        if mode == "android-xml":
            spans = _xml_spans(data)
            contents = [data[start:end].decode("utf-8") for start, end in spans]
            for source, target, count in normalized:
                old_count, new_count = contents.count(source), contents.count(target)
                if old_count == count and new_count == 0:
                    contents = [target if content == source else content for content in contents]
                elif old_count != 0 or new_count != count:
                    raise ValueError(f"XML source/target count mismatch: {source!r}; require full string/item inner XML")
            for (start, end), content in reversed(list(zip(spans, contents))):
                data = data[:start] + content.encode("utf-8") + data[end:]
            _xml_spans(data)
        else:
            for source, target, count in normalized:
                # A target containing the original fragment cannot distinguish original text from a retry.
                if source in target or target in source:
                    raise ValueError("plain-text source/target overlap is ambiguous")
                old_count, new_count = text.count(source), text.count(target)
                if old_count == count and new_count == 0:
                    text = text.replace(source, target)
                elif old_count != 0 or new_count != count:
                    raise ValueError(f"text source/target count mismatch: {source!r}")
            data = text.encode("utf-8")
        if path.suffix.lower() == ".json":
            json.loads(data.decode("utf-8"))
        prepared.append((path, data, {"target": item["path"], "format": mode, "rules": len(rules)}, baseline))
    return prepared


def _font_glyphs(data, characters):
    if len(data) < 12 or data[:4] not in (b"\x00\x01\x00\x00", b"OTTO"):
        raise ValueError("expected standalone TTF/OTF; packed fonts and collections need their type handler")
    table_count = struct.unpack_from(">H", data, 4)[0]
    tables = {}
    if not table_count or 12 + table_count * 16 > len(data):
        raise ValueError("invalid SFNT directory")
    for index in range(table_count):
        tag, _, offset, length = struct.unpack_from(">4sIII", data, 12 + index * 16)
        if tag in tables or offset < 12 + table_count * 16 or offset + length > len(data):
            raise ValueError("invalid SFNT table bounds")
        tables[tag] = data[offset:offset + length]
    if not all(tag in tables for tag in (b"head", b"maxp", b"cmap")):
        raise ValueError("font lacks head/maxp/cmap tables")
    if len(tables[b"head"]) < 54 or tables[b"head"][12:16] != b"_\x0f<\xf5" or len(tables[b"maxp"]) < 6:
        raise ValueError("invalid font header")
    glyph_count = struct.unpack_from(">H", tables[b"maxp"], 4)[0]
    cmap = tables[b"cmap"]
    wanted = {ord(c) for c in characters if not c.isspace()}
    if not wanted:
        raise ValueError("required_characters must contain visible glyphs")
    covered = set()
    try:
        count = struct.unpack_from(">H", cmap, 2)[0]
        records = []
        for index in range(count):
            platform, encoding, offset = struct.unpack_from(">HHI", cmap, 4 + index * 8)
            if platform != 0 and not (platform == 3 and encoding in (1, 10)):
                continue
            fmt = struct.unpack_from(">H", cmap, offset)[0]
            records.append((fmt == 12, fmt, offset))
        # Full Unicode cmap takes precedence; large fonts may retain a truncated
        # legacy BMP subtable which FreeType does not select.
        for _, fmt, offset in sorted(records, reverse=True):
            if fmt == 12:
                length, _, groups = struct.unpack_from(">III", cmap, offset + 4)
                if offset + length > len(cmap) or 16 + groups * 12 > length:
                    raise ValueError("invalid format 12 cmap bounds")
                for group in range(groups):
                    start, end, glyph = struct.unpack_from(">III", cmap, offset + 16 + group * 12)
                    if start > end or end > 0x10ffff:
                        raise ValueError("invalid format 12 cmap group")
                    covered.update(cp for cp in wanted if start <= cp <= end and 0 < glyph + cp - start < glyph_count)
            elif fmt == 4:
                length = struct.unpack_from(">H", cmap, offset + 2)[0]
                sub = cmap[offset:offset + length]
                segments = struct.unpack_from(">H", sub, 6)[0] // 2
                if not segments or len(sub) != length or 16 + segments * 8 > length:
                    raise ValueError(f"invalid format 4 cmap bounds: length={length}, available={len(sub)}, segments={segments}")
                for segment in range(segments):
                    end = struct.unpack_from(">H", sub, 14 + segment * 2)[0]
                    start = struct.unpack_from(">H", sub, 16 + segments * 2 + segment * 2)[0]
                    delta = struct.unpack_from(">h", sub, 16 + segments * 4 + segment * 2)[0]
                    range_pos = 16 + segments * 6 + segment * 2
                    range_offset = struct.unpack_from(">H", sub, range_pos)[0]
                    for cp in wanted:
                        if start <= cp <= end:
                            glyph = struct.unpack_from(">H", sub, range_pos + range_offset + (cp - start) * 2)[0] if range_offset else cp
                            glyph = (glyph + delta) & 0xffff if glyph or not range_offset else 0
                            if 0 < glyph < glyph_count:
                                covered.add(cp)
            if wanted <= covered:
                break
    except (struct.error, IndexError) as exc:
        raise ValueError("truncated font cmap") from exc
    missing = wanted - covered
    if missing:
        raise ValueError("font is missing required glyphs: " + ", ".join(f"U+{cp:04X}" for cp in sorted(missing)))
    return "".join(dict.fromkeys(c for c in characters if not c.isspace()))


def _prepare_assets(ctx, plan, kind):
    try:
        from PIL import Image, ImageFont
    except ImportError as exc:
        raise ValueError("Pillow with FreeType is required for font/image validation") from exc
    prepared = []
    for item in _items(plan, "replacements"):
        source = _path(ctx, _string(item, "source"), False)
        target = _path(ctx, _string(item, "target"), True)
        data, original = source.read_bytes(), target.read_bytes()
        details = {"target": item["target"], "source": item["source"]}
        if kind == "font":
            characters = _string(item, "required_characters")
            verified = _font_glyphs(data, characters)
            if original[:4] != data[:4]:
                raise ValueError("font replacement must preserve standalone SFNT format")
            try:
                ImageFont.truetype(io.BytesIO(original), 16)
                ImageFont.truetype(io.BytesIO(data), 16)
            except (OSError, ValueError) as exc:
                raise ValueError(f"font cannot be loaded by FreeType: {exc}") from exc
            details["verified_characters"] = verified
        else:
            if source.name.endswith(".9.png") or target.name.endswith(".9.png"):
                raise ValueError("nine-patch images need a dedicated resource handler")
            try:
                with Image.open(io.BytesIO(original)) as old, Image.open(io.BytesIO(data)) as new:
                    old.load()
                    new.load()
                    if old.format not in ("PNG", "JPEG", "WEBP") or old.format != new.format or old.size != new.size or old.mode != new.mode:
                        raise ValueError("image format, dimensions and pixel mode must match")
                    if getattr(old, "n_frames", 1) != 1 or getattr(new, "n_frames", 1) != 1:
                        raise ValueError("animated images need a dedicated resource handler")
                    if ("transparency" in old.info) != ("transparency" in new.info):
                        raise ValueError("image transparency representation must match")
                    if old.info.get("icc_profile") != new.info.get("icc_profile"):
                        raise ValueError("image color profile must match")
                    if b"npTc" in original or b"npTc" in data:
                        raise ValueError("compiled nine-patch requires a dedicated handler")
                    details.update(format=new.format, dimensions=list(new.size), mode=new.mode)
            except (OSError, SyntaxError) as exc:
                raise ValueError(f"image cannot be decoded: {exc}") from exc
        prepared.append((target, data, details, original))
    return prepared


def _atomic_write(path, data):
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".localization-", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(data)
        os.chmod(temporary, path.stat().st_mode)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def apply_localization(ctx, kind):
    """Return artifact evidence after full validation and reversible file writes."""
    if kind not in ("text", "font", "image"):
        raise ValueError(f"unknown localization kind: {kind}")
    plan = ctx.load_plan()
    if not isinstance(plan, dict):
        raise ValueError("localization plan must be an object")
    prepared = _prepare_text(ctx, plan) if kind == "text" else _prepare_assets(ctx, plan, kind)
    paths = [path.resolve() for path, _, _, _ in prepared]
    if len(set(paths)) != len(paths):
        raise ValueError("plan repeats a destination file")
    for path, _, _, baseline in prepared:
        if path.read_bytes() != baseline:
            raise ValueError(f"target changed during preflight: {path}")
    changed, backups, assets = [], [], []
    try:
        for path, data, details, original in prepared:
            if original != data:
                backups.append((path, original))
                _atomic_write(path, data)
                changed.append(details["target"])
            assets.append(dict(details, sha256=hashlib.sha256(data).hexdigest(), changed=original != data))
    except OSError:
        for path, original in reversed(backups):
            _atomic_write(path, original)
        raise
    return {"changed_files": changed, "assets": assets, "scope": "decoded editable assets; device rendering remains unverified"}
