#!/usr/bin/env python3
"""stage-05-il2cpp-dump.py — 阶段 05：IL2CPP dump + 头文件接入。

职责：
- 从 APK 提取 libil2cpp.so + global-metadata.dat
- 调用 Il2CppDumper/rodroid-il2cppdumper 导出 dump.cs / il2cpp.h / DummyDll
- 把 il2cpp.h 复制到 `crackings/<type>/<Name>/project/app/src/main/cpp/il2cpp-arm64/`
- 在 `app/src/main/cpp/common.h` 中 include 导出头文件
- 写入 `crackings/<Name>/stages/05-il2cpp-dump/` 报告

产物契约：
- `crackings/<Name>/stages/05-il2cpp-dump/dump/dump.cs`（≥1000 行）
- `crackings/<Name>/stages/05-il2cpp-dump/dump/il2cpp.h`
- `crackings/<Name>/stages/05-il2cpp-dump/dump/DummyDll/*.dll`（≥1）
- `crackings/<type>/<Name>/project/app/src/main/cpp/il2cpp-arm64/*.h`
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PKG = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts"
sys.path.insert(0, str(SCRIPT_PKG))
import importlib.util as _ilu

_spc = _ilu.spec_from_file_location(
    "stage_common_runtime", str(SCRIPT_PKG / "lib" / "stage_common.py")
)
_sc = _ilu.module_from_spec(_spc)
assert _spc.loader is not None
_spc.loader.exec_module(_sc)

ensure_dir = _sc.ensure_dir
fatal = _sc.fatal
log_step = _sc.log_step
log_info = _sc.log_info
log_warn = _sc.log_warn
log_success = _sc.log_success
append_status = _sc.append_status
append_tool_call = _sc.append_tool_call
stage_out = _sc.stage_out
run_subprocess = _sc.run_subprocess

DUMPER_CANDIDATES = [
    # ELF pre-built binary (writes to CWD inside dumper directory)
    ROOT / "tools" / "crack-intergration-tools" / "source-projects" / "Il2CppDumper" / "Il2CppDumper" / "bin" / "Release" / "net8.0" / "Il2CppDumper",
    # dotnet — pass the DLL directly
    ROOT / "tools" / "crack-intergration-tools" / "source-projects" / "Il2CppDumper" / "Il2CppDumper" / "bin" / "Release" / "net8.0" / "Il2CppDumper.dll",
    # Legacy paths
    ROOT / "tools" / "crack-intergration-tools" / "execable" / "Il2CppDumper" / "Il2CppDumper",
    ROOT / "tools" / "crack-intergration-tools" / "source-projects" / "Il2CppDumper" / "Il2CppDumper",
    ROOT / "tools" / "crack-intergration-tools" / "source-projects" / "Il2CppDumper" / "Il2CppDumper.exe",
]

# Il2CppInspectorRedux（metadata v39 / Unity 6.3 等新版本专用，Il2CppDumper 只支持 v16-31）
INSPECTOR_REDUX = ROOT / "tools" / "crack-intergration-tools" / "execable" / "Il2CppInspectorRedux" / "Il2CppInspector"


def _resolve_name() -> str:
    name = os.environ.get("NAME", "").strip()
    if not name:
        fatal("环境变量 NAME 未设置；请通过 crack.py 调度")
    return name


def _resolve_apk() -> Path:
    apk = os.environ.get("APK", "").strip()
    if not apk:
        fatal("环境变量 APK 未设置；请通过 crack.py 调度")
    p = Path(apk)
    if not p.is_file():
        fatal(f"APK 缺失: {apk}")
    return p


def _crack_dir(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name))


def _project_app_main(name: str) -> Path:
    # [FLOWFIX] 修复 §1.1 父目录规则：与 stage 04 (sub-stage-preprocess-build.py)
    # 输出对齐到 `crackings/<type>/<Name>/project/app/src/main/`
    type_arg = os.environ.get("TYPE", "").strip()
    base = ROOT / "output-projects" / (type_arg or name.split("/", 1)[0]) / name
    # 当 TYPE 缺失时 base = crackings/<type>/<Name>/project；有 TYPE 时按 type 子目录
    if type_arg:
        return base / "app" / "src" / "main"
    return base / "app" / "src" / "main"


def _locate_dumper() -> Path | None:
    for cand in DUMPER_CANDIDATES:
        if cand.is_file() and os.access(cand, os.X_OK):
            return cand
    return None


def _extract_libs_from_apk(apk_path: Path, out_dir: Path) -> tuple[Path | None, Path | None]:
    import zipfile

    ensure_dir(out_dir)
    so_target = out_dir / "libil2cpp.so"
    meta_target = out_dir / "global-metadata.dat"
    if so_target.is_file() and meta_target.is_file():
        return so_target, meta_target

    with zipfile.ZipFile(apk_path) as zf:
        so_member = next((n for n in zf.namelist() if n.endswith("libil2cpp.so")), None)
        meta_member = next((n for n in zf.namelist() if n.endswith("global-metadata.dat")), None)
        if not so_member or not meta_member:
            return None, None
        with zf.open(so_member) as src, so_target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        with zf.open(meta_member) as src, meta_target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
    return so_target, meta_target


def _run_dumper(dumper: Path, so: Path, meta: Path, dump_dir: Path) -> tuple[int, str]:
    ensure_dir(dump_dir)
    # Il2CppDumper 写入 CWD/dump/ 而不是第三个参数路径。
    # 因此把 CWD 设为 dump_dir 的父目录，第三个参数为目录名 "dump"。
    # 这样 dumper 会把产物写到 dump_dir/dump/。
    # 但 dumper 实际把 dump/ 写到 CWD，所以我们直接用 dump_dir 父目录 + 子目录名。
    parent = dump_dir.parent
    sub = dump_dir.name
    parent.mkdir(parents=True, exist_ok=True)
    cmd = [str(dumper), str(so), str(meta), sub]
    code, output = run_subprocess(cmd, cwd=parent, timeout=300)
    return code, output


def run_inspector_redux(so: Path, meta: Path, apk: Path, sd: Path) -> bool:
    """Il2CppInspectorRedux fallback（metadata v39+ / Unity 6.x）。

    [FLOWFIX]:
      - Il2CppDumper 只支持 metadata v16-31，Unity 6.3 (6000.3.0b1) 的 v39 报
        "Metadata file supplied is not a supported version[39]"
      - Il2CppInspectorRedux 的 plugins/ 子目录存在时启动即崩
        `System.ArgumentNullException: Value cannot be null. Parameter 'con'`
        → 运行前必须临时移走 plugins/，跑完恢复
      - 输出格式与 Il2CppDumper 不同：
        dump.cs / metadata.json（含 addressMap.stringLiterals）/ cpp-out/
      - 不产出 stringliteral.json → 从 metadata.json 提取后生成，供 stage-09 使用
    """
    import json as _json
    import shutil as _shutil
    inspector = INSPECTOR_REDUX
    if not inspector.is_file():
        return False
    plugins_dir = inspector.parent / "plugins"
    tmp_plugins = inspector.parent / "plugins.__disabled"
    if plugins_dir.is_dir() and not tmp_plugins.exists():
        _shutil.move(str(plugins_dir), str(tmp_plugins))
        log_warn("Il2CppInspectorRedux: plugins/ 已临时移走（启动 bug workaround）")
    try:
        dump_dir = sd / "dump"
        ensure_dir(dump_dir)
        in_apk = apk if apk.is_file() else so
        cmd = [
            str(inspector), "-i", str(in_apk),
            "--select-outputs",
            "--cs-out", str(dump_dir / "dump.cs"),
            "--json-out", str(dump_dir / "metadata.json"),
            "--cpp-out", str(dump_dir / "cpp-out"),
        ]
        code, output = run_subprocess(cmd, timeout=900)
        log_path = sd / "il2cpp-inspector.log"
        log_path.write_text(output, encoding="utf-8")
        if not (dump_dir / "dump.cs").is_file():
            log_warn(f"InspectorRedux 未产出 dump.cs；code={code} log={log_path}")
            return False
        # 从 metadata.json 提取 stringLiterals → stringliteral.json（stage-09 兼容）
        meta_json = dump_dir / "metadata.json"
        if meta_json.is_file():
            try:
                data = _json.loads(meta_json.read_text(encoding="utf-8"))
                sl = (data.get("addressMap") or {}).get("stringLiterals") or []
                entries = [{"value": e.get("string", "")} for e in sl if isinstance(e, dict)]
                (dump_dir / "stringliteral.json").write_text(
                    _json.dumps(entries, ensure_ascii=False), encoding="utf-8")
                log_success(f"stringliteral.json 提取 {len(entries)} 条")
            except Exception as e:
                log_warn(f"metadata.json → stringliteral.json 提取失败: {e}")
        return True
    finally:
        if tmp_plugins.exists():
            _shutil.move(str(tmp_plugins), str(plugins_dir))
            log_info("Il2CppInspectorRedux: plugins/ 已恢复")


def _stage_dir_for(name: str) -> Path:
    sd = stage_out(name, "05", label="il2cpp-dump")
    return sd


def verify_dump(name: str, dump_dir: Path) -> bool:
    cs = dump_dir / "dump.cs"
    h = dump_dir / "il2cpp.h"
    dummy = dump_dir / "DummyDll"
    if not cs.is_file() or cs.stat().st_size < 1000:
        log_warn(f"dump.cs 缺失或小于 1000 字节: {cs}")
        return False
    # Il2CppDumper: il2cpp.h + DummyDll；Il2CppInspectorRedux: cpp-out/appdata/*.h（无 il2cpp.h/DummyDll）
    has_il2cpp_h = h.is_file()
    has_dummy = dummy.is_dir() and any(dummy.glob("*.dll"))
    has_appdata = (dump_dir / "cpp-out" / "appdata").is_dir()
    if not (has_il2cpp_h or has_appdata):
        log_warn(f"头文件缺失（il2cpp.h 或 cpp-out/appdata/）: {dump_dir}")
        return False
    log_success(f"dump.cs={cs.stat().st_size}B  头文件={'il2cpp.h' if has_il2cpp_h else 'cpp-out/appdata'}  DummyDll={'≥1' if has_dummy else 'N/A'}")
    return True


# Il2CppInspectorRedux 的 C++ 头文件（位于 cpp-out/appdata/），无 il2cpp.h 聚合头
_INSPECTOR_HEADERS = [
    "il2cpp-functions.h", "il2cpp-types.h", "il2cpp-api-functions.h",
    "il2cpp-api-functions-ptr.h", "il2cpp-types-ptr.h", "il2cpp-metadata-version.h",
]


def install_headers(name: str, dump_dir: Path) -> bool:
    arm64_dir = _project_app_main(name) / "cpp" / "il2cpp-arm64"
    ensure_dir(arm64_dir)
    # Il2CppDumper 风格
    for header in ("il2cpp.h", "il2cpp-types.h", "il2cpp-functions.h"):
        src = dump_dir / header
        if src.is_file():
            shutil.copy2(src, arm64_dir / header)
    # Il2CppInspectorRedux 风格（cpp-out/appdata/）
    appdata = dump_dir / "cpp-out" / "appdata"
    if appdata.is_dir():
        for header in _INSPECTOR_HEADERS:
            src = appdata / header
            if src.is_file():
                shutil.copy2(src, arm64_dir / header)
    common_h = _project_app_main(name) / "cpp" / "common.h"
    if common_h.is_file():
        text = common_h.read_text(encoding="utf-8")
        if "il2cpp" not in text:
            addition = (
                "\n// === injected by stage-05-il2cpp-dump ===\n"
                '#include "il2cpp-arm64/il2cpp-functions.h"\n'
                '#include "il2cpp-arm64/il2cpp-types.h"\n'
                '#include "il2cpp-arm64/il2cpp-api-functions.h"\n'
                '#include "il2cpp-arm64/il2cpp-api-functions-ptr.h"\n'
                '#include "il2cpp-arm64/il2cpp-types-ptr.h"\n'
                '#include "il2cpp-arm64/il2cpp-metadata-version.h"\n'
            )
            common_h.write_text(text + addition, encoding="utf-8")
            log_success("common.h 已注入 il2cpp-arm64 include")
    else:
        common_h.write_text(
            '#pragma once\n'
            '#include "il2cpp-arm64/il2cpp-functions.h"\n'
            '#include "il2cpp-arm64/il2cpp-types.h"\n'
            '#include "il2cpp-arm64/il2cpp-api-functions.h"\n'
            '#include "il2cpp-arm64/il2cpp-api-functions-ptr.h"\n'
            '#include "il2cpp-arm64/il2cpp-types-ptr.h"\n'
            '#include "il2cpp-arm64/il2cpp-metadata-version.h"\n',
            encoding="utf-8",
        )
        log_success(f"已生成 common.h: {common_h}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="IL2CPP 阶段 05：dump.cs + il2cpp.h")
    parser.add_argument("--apk", default=os.environ.get("APK", ""), help="源 APK 路径")
    parser.add_argument("--dumper", default="", help="显式 Il2CppDumper 路径")
    args = parser.parse_args()

    name = _resolve_name()
    apk_path = Path(args.apk) if args.apk else _resolve_apk()
    if not apk_path.is_file():
        fatal(f"找不到源 APK: {apk_path}")

    dumper_path = Path(args.dumper) if args.dumper else _locate_dumper()
    if dumper_path is None:
        log_warn("未找到 Il2CppDumper 可执行；阶段 05 标记 SKIPPED，等待阶段 04c 已完成的 dump.cs")
        return 0

    sd = _stage_dir_for(name)
    inputs_dir = sd / "input"
    dump_dir = sd / "dump"
    log_step(f"阶段 05：IL2CPP dump ({name})")
    so, meta = _extract_libs_from_apk(apk_path, inputs_dir)
    if so is None or meta is None:
        log_warn("APK 中未找到 libil2cpp.so / global-metadata.dat")
        return 1

    log_info(f"调用 dumper: {dumper_path}")
    code, output = _run_dumper(dumper_path, so, meta, dump_dir)
    log_path = sd / "il2cpp-dumper.log"
    log_path.write_text(output, encoding="utf-8")
    ok = (code == 0 and verify_dump(name, dump_dir)) or (code != 0 and verify_dump(name, dump_dir))

    # [FLOWFIX] metadata v39+ (Unity 6.x) Il2CppDumper 不支持 → 回退 Il2CppInspectorRedux
    if not ok:
        log_warn("Il2CppDumper 失败或产物缺失；尝试 Il2CppInspectorRedux（metadata v39+ 专用）")
        if run_inspector_redux(so, meta, apk_path, sd):
            ok = verify_dump(name, dump_dir)
        else:
            log_warn("Il2CppInspectorRedux 亦失败；查看 il2cpp-inspector.log")
            return 1

    if not verify_dump(name, dump_dir):
        return 1
    install_headers(name, dump_dir)
    log_success(f"阶段 05 完成 → {dump_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())