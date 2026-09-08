#!/usr/bin/env python3
"""
run-major-sniff.py — 七大主阶段 1：类型嗅探（sniff）。

调用 sub-stage-sniff.py 嗅探 APK 工程类型，输出到 crackings/<Name>/findings.md §1。
固定入口：tool 套件内任何模块均可直接调用本脚本。

用法：
  python3 run-major-sniff.py <apk-path> [name]

参数：
  <apk-path>     必填，APK 路径（如 apks/Foo.apk 或 apks/Foo.xapk）
  [name]         可选，项目名（默认从 apk 文件名 CamelCase 归一）

预处理（自动）：
  若 <apk-path> 后缀为 .xapk，则先调 sub-stage-xapk-merge.py 合并
  base + split config APKs + preloaded assets 到
  crackings/<Name>/raw/<Name>.apk，再对 fat APK 跑 sniff。
  [FLOWFIX] MiniCarRacingGameLegends：原脚本只看 xapk 顶层
  4 个文件（base.apk/icon.png/config.*.apk/manifest.json），嗅探永远 unknown。

输出：
  - crackings/<Name>/findings.md §1 类型段
  - 终端打印嗅探结果（type / grade / 路由 skill）

示例：
  python3 run-major-sniff.py apks/Find+the+differences_1.2.0_APKPure.apk FindTheDifferences

脚本命名 stage-XX-* → sub-stage-*，路径从
general-strategy-skill/stages/sub-stage-register.yaml 读取。
"""
from __future__ import annotations

import os
import sys
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tools/scripts/lib"))
from routing import get_script_path, get_helper_path  # noqa: E402
from common import setup_paths_from_name  # noqa: E402

# 子阶段路由表驱动（按 name 查，替代硬编码）
SNIFF_SCRIPT = get_script_path("sniff") or ROOT / "<missing: sniff>"
XAPK_MERGE_SCRIPT = get_helper_path("sub-stage-xapk-merge.py") or ROOT / "<missing: xapk-merge>"


def maybe_merge_xapk(apk: Path, name: str, type_arg: str = "") -> Path:
    """若 apk 为 .xapk，先合并到 crackings/<type>/<Name>/raw/<Name>.apk，返回 fat apk 路径。"""
    if apk.suffix.lower() != ".xapk":
        return apk
    if type_arg:
        raw_dir = ROOT / "crackings" / type_arg / name / "raw"
    else:
        raw_dir = ROOT / "crackings" / name / "raw"
    fat_apk = raw_dir / f"{name}.apk"
    raw_dir.mkdir(parents=True, exist_ok=True)
    if fat_apk.exists() and fat_apk.stat().st_size > 0:
        print(f"[INFO] xapk 已合并，跳过: {fat_apk}")
        return fat_apk
    print(f"[INFO] 检测到 .xapk，先合并 → {fat_apk}")
    rc = subprocess.run(
        ["python3", str(XAPK_MERGE_SCRIPT), str(apk), "-o", str(fat_apk)],
        check=False,
    ).returncode
    if rc != 0 or not fat_apk.exists():
        print(f"[ERROR] xapk-merge 失败 rc={rc}")
        sys.exit(2)
    return fat_apk


def guess_xapk_type(apk: Path) -> str:
    """在合并前检查 XAPK 内层 APK，避免产生无 type 的临时项目目录。"""
    import io
    import zipfile

    try:
        with zipfile.ZipFile(apk) as outer:
            for member in outer.infolist():
                if not member.filename.lower().endswith(".apk"):
                    continue
                try:
                    with zipfile.ZipFile(io.BytesIO(outer.read(member))) as inner:
                        names = inner.namelist()
                except (zipfile.BadZipFile, OSError):
                    continue
                if any(n.endswith("/libil2cpp.so") for n in names):
                    return "il2cpp"
                if any(n.endswith("/libUE4.so") or n.endswith("/libUnreal.so") for n in names):
                    return "unreal"
                if any(n.endswith("/libflutter.so") for n in names):
                    return "flutter"
                if any(n.endswith("/libyoyo.so") for n in names):
                    return "gamemaker"
    except (zipfile.BadZipFile, OSError):
        pass
    return ""


def _sniff_type_quickly(apk_path: Path) -> str:
    """轻量嗅探 APK 类型（不写文件，只返回归一化后的 type string）。
    用于 driver 在调子脚本前先拿到 TYPE，避免 sniff 子脚本写到错位置。
    """
    import re
    import zipfile
    if not apk_path.exists() or apk_path.suffix.lower() != ".apk":
        return ""
    try:
        with zipfile.ZipFile(apk_path) as z:
            names = z.namelist()
    except Exception:
        return ""
    text = "\n".join(names)
    raw_type = "unknown"
    if "META-INF/AIR/application.xml" in text or "assets/META-INF/AIR/application.xml" in text:
        raw_type = "air"
    elif any("resource.car" in n or "libcorona.so" in n for n in names):
        raw_type = "corona"
    elif any("libil2cpp.so" in n for n in names):
        raw_type = "il2cpp"
    elif any("GameAssembly.dll" in n for n in names):
        raw_type = "unity-mono"
    elif any(re.match(r"classes\d*\.dex$", n) for n in names):
        raw_type = "android"
    mapping = {
        "air": "air", "AIR": "air",
        "corona": "corona", "Corona": "corona",
        "il2cpp": "il2cpp",
        "unity-mono": "unity-mono", "UnityMono": "unity-mono",
        "android": "android", "Android": "android",
    }
    return mapping.get(raw_type, "")


def _parse_type_from_substage_output(stdout: str) -> str:
    """从 sub-stage-sniff.py 输出 parse TYPE=xxx；用于 [FLOWFIX] 修复 sniff 路径 bug。

    sniff 子脚本输出 'TYPE=il2cpp SUBTYPE=...'，parse 出 type 以调用 setup_paths_from_name。
    """
    import re
    m = re.search(r"TYPE=(\S+)", stdout)
    if not m:
        return ""
    raw = m.group(1).strip()
    # 内部 type 名归一：il2cpp→il2cpp；AIR/Air→air；Android→android；UnityMono→unity-mono；Corona→corona
    mapping = {
        "il2cpp": "il2cpp",
        "AIR": "air", "Air": "air",
        "Android": "android", "android": "android",
        "UnityMono": "unity-mono",
        "Corona": "corona",
    }
    return mapping.get(raw, raw.lower())


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    apk = Path(sys.argv[1])
    name = sys.argv[2] if len(sys.argv) >= 3 else apk.stem
    print(f"[七大主阶段 1/7] 类型嗅探 → {name}")
    if not SNIFF_SCRIPT.exists():
        print(f"[ERROR] 缺少脚本: {SNIFF_SCRIPT}")
        sys.exit(2)
    if not apk.exists():
        print(f"[ERROR] APK 不存在: {apk}")
        sys.exit(2)
    # [FLOWFIX] XAPK 合并前先识别内层 APK，确保整个 sniff 产物都落在
    # crackings/<type>/<Name>/，不再先创建违反 §3 的 crackings/<Name>/ 临时目录。
    type_hint = guess_xapk_type(apk) if apk.suffix.lower() == ".xapk" else ""
    sniff_target = maybe_merge_xapk(apk, name, type_hint)
    if type_hint:
        os.environ["TYPE"] = type_hint
    else:
        # [FLOWFIX 2026-08-23] 普通 APK（非 .xapk）也必须先嗅探拿 TYPE，
        # 否则子脚本的 _write_findings_section1/_write_source_md5 写错位置
        # （crackings/<Name>/ 而非 crackings/<type>/<Name>/，违反 AGENTS.md §3）。
        sniffed_type = _sniff_type_quickly(sniff_target)
        if sniffed_type:
            os.environ["TYPE"] = sniffed_type
    # [FLOWFIX 2026-08-23] sniff 子脚本必须收到 TYPE 环境变量才能把
    # findings.md / source.apk.md5 写到 crackings/<type>/<Name>/（AGENTS.md §3），
    # 否则会落到 crackings/<Name>/（违反 type 父目录规则）。在 subprocess.run 中
    # 显式注入 env=os.environ.copy() 把当前进程的 TYPE 传给子进程。
    proc = subprocess.run(
        ["python3", str(SNIFF_SCRIPT), str(sniff_target), name],
        check=False, capture_output=True, text=True,
        env=os.environ.copy(),
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    if proc.returncode != 0:
        sys.stderr.write(combined)
        sys.exit(proc.returncode)
    # 把 sniff 输出透传到 stderr（保留色彩）
    sys.stderr.write(combined)
    type_arg = _parse_type_from_substage_output(combined)
    if type_arg:
        os.environ["TYPE"] = type_arg
        # 调 setup_paths_from_name 让 CRACK_DIR/OUT/PATCHED 指向 crackings/<type>/<Name>/
        # 此时 source.apk.md5 已在 crackings/<type>/<Name>/（[FLOWFIX] sniff 已支持 TYPE 环境变量）
        try:
            setup_paths_from_name(name, type_arg)
            print(f"[OK] 项目路径已设置: crackings/{type_arg}/{name}/")
        except Exception as e:
            print(f"[WARN] setup_paths_from_name 失败: {e}")
    sys.exit(proc.returncode)


if __name__ == "__main__":
    main()