#!/usr/bin/env python3
"""sub-stage-sniff.py — 类型嗅探主阶段（M1）子脚本。

[FLOWFIX 2026-08-30] 原 sniff 脚本长期缺失；routing.py 找不到 common fallback。
本脚本按 strategy-config.yaml sniff_routing 段（order + patterns）做真实嗅探，
按嗅探顺序首胜原则判定 type；XAPK 内层 split APK 也一并检查（避免漏看 split 里的 lib/）。

用法：
    python3 sub-stage-sniff.py <apk-path> [name]                    # 直接嗅探 fat APK
    # 注：xapk 合并由 run-major-sniff.py 在调用本脚本前先调 sub-stage-xapk-merge.py

输出（stdout）：
    TYPE=<type> SUBTYPE=<subtype> SIZE_MB=<n>
    同时把 sniff 结果落到 crackings/<type>/<Name>/findings.md §1 类型段

环境变量：
    TYPE        已知的 type 提示（driver 调用时传入），仅用于路径

工作区根目录：由本脚本位置 parents[5] 定位。
"""
from __future__ import annotations

import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

# 从集中策略配置读取嗅探规则。
sys.path.insert(0, str(ROOT / "skills/common/scripts/strategy"))
try:
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location(
        "strategy_config_mod",
        str(ROOT / "skills/common/scripts/strategy/strategy-config.py"),
    )
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
    SNIFF_ORDER = _mod.get_sniff_order()
    SNIFF_PATTERNS = _mod.get_sniff_patterns()  # type: ignore[assignment]
except Exception:
    # fallback：硬编码复制（保证脚本独立可用）
    SNIFF_ORDER = [
        "air", "il2cpp", "unreal", "unity-mono", "xamarin",
        "flutter", "cocos-creator", "cocos2dx", "libgdx",
        "defold", "gamemaker", "android",
    ]
    SNIFF_PATTERNS = {
        "air":            [r"META-INF/AIR/application\.xml", r"assets/META-INF/AIR/application\.xml"],
        "il2cpp":         [r"lib/.*/libil2cpp\.so"],
        "unreal":         [r"libUE4\.so", r"libUnreal.*\.so", r"libUnrealEngine.*\.so"],
        "unity-mono":     [r"lib/.*/GameAssembly\.dll"],
        "cocos2dx":       [r"libcocos2d.*\.so", r"libMyGame\.so", r"libgame\.so"],
        "cocos-creator":  [r"libcocos2djs\.so", r"src/settings\.js", r"assets/main/config\.json"],
        "libgdx":         [r"lib/.*/libgdx\.so", r"com/badlogic/gdx/"],
        "defold":         [r"assets/game\.dmanifest", r"assets/game\.projectc", r"assets/game\.arcd"],
        "gamemaker":      [r"assets/game\.droid", r"lib/.*/libyoyo\.so"],
        "android":        [r"classes[0-9]*\.dex"],
        "flutter":        [r"libflutter\.so", r"libapp\.so"],
        "xamarin":        [r"libmonodroid\.so", r"libmono-native\.so", r"libxamarin-app\.so"],
    }


def sniff_inner_apk(path: Path) -> str:
    """嗅探单个 APK/XAPK，返回 type（按 SNIFF_ORDER 首胜原则）。"""
    if not path.exists():
        return ""
    try:
        with zipfile.ZipFile(path) as z:
            names = z.namelist()
    except (zipfile.BadZipFile, OSError):
        return ""
    text = "\n".join(names)
    for t in SNIFF_ORDER:
        for pat in SNIFF_PATTERNS.get(t, []):
            if re.search(pat, text):
                return t
    return ""


def sniff_xapk_layers(path: Path) -> tuple[str, str]:
    """嗅探 XAPK：先嗅探外层文件名 + 拆开内层 split APK 嗅探（防漏 split config 里的 .so）。"""
    if path.suffix.lower() != ".xapk":
        return sniff_inner_apk(path), ""
    # 先嗅外层
    outer_type = sniff_inner_apk(path)
    # 拆内层
    import io
    layer_results = []
    try:
        with zipfile.ZipFile(path) as outer:
            for member in outer.infolist():
                if not member.filename.lower().endswith(".apk"):
                    continue
                try:
                    inner_data = outer.read(member)
                    with zipfile.ZipFile(io.BytesIO(inner_data)) as inner:
                        inner_names = inner.namelist()
                except (zipfile.BadZipFile, OSError):
                    continue
                inner_text = "\n".join(inner_names)
                layer_results.append((member.filename, inner_text))
    except (zipfile.BadZipFile, OSError):
        return outer_type, ""
    # 合并所有内层 + 外层，按 SNIFF_ORDER 首胜
    merged = "\n".join(t for _, t in layer_results)
    for t in SNIFF_ORDER:
        for pat in SNIFF_PATTERNS.get(t, []):
            if re.search(pat, merged):
                return t, outer_type or t
    return outer_type, ""


def write_findings_section1(type_: str, name: str, apk_path: Path, md5: str) -> Path:
    """写/追加 findings.md §1 类型段。

    [FLOWFIX 2026-08-30] 原版只在文件不存在时创建，导致已经预填的 findings.md（详细嗅探）
    不会被 sniff 子脚本追加 §1 类型段。修复：文件已存在 → 强制覆盖前 6 行（标题 + 元信息 + §1 标题），
    其余保留（保留 Agent 写的 §0 详细嗅探 / §2 SDK 识别 等）。
    """
    type_hint = os.environ.get("TYPE", "") or type_
    project_dir = ROOT / "crackings" / type_hint / name
    project_dir.mkdir(parents=True, exist_ok=True)
    findings = project_dir / "findings.md"

    header = (
        "# findings.md — 项目调研记录\n\n"
        f"> 类型: {type_}\n> 来源 APK: {apk_path}\n> MD5: {md5}\n\n"
        "## 1. 类型嗅探\n\n"
        f"**type = {type_}**（按 sniff_routing 首胜原则判定，"
        "unzip -l + sniff_patterns 匹配 + XAPK 内层 split 合并嗅探）\n\n"
    )

    if findings.exists():
        existing = findings.read_text()
        # 找到第一个非元数据章节（## 0. / §2 / etc.）之前的标题段
        # 简单方案：找到第一个以 "##" 开头（且非 "## 1. 类型嗅探"）的行，从其开始保留
        lines = existing.splitlines(keepends=True)
        keep_from = 0
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.startswith("## ") and not stripped.startswith("## 1."):
                keep_from = i
                break
        else:
            keep_from = len(lines)
        # 如果整篇都在 §1 之前都没内容，就整段保留；否则丢弃前面被 header 替代的内容
        tail = "".join(lines[keep_from:]) if keep_from < len(lines) else "\n"
        # tail 可能以空行开头 → 移除
        tail = tail.lstrip("\n")
        findings.write_text(header + tail)
    else:
        findings.write_text(header)
    return findings


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    apk = Path(sys.argv[1]).resolve()
    name = sys.argv[2] if len(sys.argv) >= 3 else apk.stem

    if not apk.exists():
        print(f"[ERROR] APK 不存在: {apk}", file=sys.stderr)
        return 2

    size_mb = round(apk.stat().st_size / (1024 * 1024), 2)

    # sniff（XAPK 看 split 内层）
    if apk.suffix.lower() == ".xapk":
        type_, outer = sniff_xapk_layers(apk)
        subtype = "xapk"
    else:
        type_ = sniff_inner_apk(apk)
        subtype = "apk"
        outer = type_

    if not type_:
        type_ = "unknown"
        subtype = "unknown"

    # 写 findings.md §1 类型段（仅当 type 已知）
    if type_ != "unknown":
        # 读 MD5（如有）
        md5 = ""
        if apk.exists():
            import hashlib
            md5 = hashlib.md5(apk.read_bytes()).hexdigest()
        try:
            write_findings_section1(type_, name, apk, md5)
        except Exception as e:
            print(f"[WARN] 写 findings.md 失败: {e}", file=sys.stderr)

    print(f"TYPE={type_} SUBTYPE={subtype} SIZE_MB={size_mb}")
    if outer and outer != type_:
        print(f"[INFO] 外层嗅探 {outer} → 合并内层 split 后修正为 {type_}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
