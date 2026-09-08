#!/usr/bin/env python3
# stage-cocos-03-static-analyze — Cocos2d-x 静态分析
# [FLOWFIX] BigHunter] 重写为兼容 skills/common/scripts/lib/common.py v2 API

import subprocess
import sys
import zipfile
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-cocos-03-static-analyze.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_apk(str(apk_path))
    C.ensure_dir(C.crack_dir())
    C.ensure_dir(C.out_dir())

    name = os.environ.get('NAME', '')
    apk_env = os.environ.get('APK', str(apk_path))
    out_path = Path(C.out_dir())
    repo_root = Path(C.repo_root())

    C.log_step(f"阶段 cocos-03: Cocos2d-x 静态分析 ({name})")

    # 1. jadx
    jadx_out = out_path / "02-jadx"
    jadx_src = jadx_out / "sources"
    C.ensure_dir(str(jadx_src))
    if any(jadx_src.iterdir()):
        C.log_warn("jadx 输出已存在，跳过")
    else:
        C.log_info("jadx 反编译 Java 层...")
        jadx_bin = repo_root / "tools" / "environments" / "bin" / "jadx"
        if jadx_bin.exists():
            subprocess.run(
                [str(jadx_bin), "-d", str(jadx_src), "--no-res", "--threads-count", "8", apk_env],
                capture_output=True, timeout=600
            )
            C.log_success("jadx 完成")
        else:
            C.log_warn(f"jadx 未找到: {jadx_bin}")

    # 2. 提取关键 so
    cocos_dir = out_path / "03-cocos"
    C.ensure_dir(str(cocos_dir))
    C.log_info("提取 lib*.so...")
    with zipfile.ZipFile(apk_env, "r") as z:
        for name_in_zip in z.namelist():
            if not name_in_zip.endswith(".so"):
                continue
            so_name = Path(name_in_zip).name
            if not any(k in so_name.lower() for k in ["cocos", "mygame", "game"]):
                continue
            (cocos_dir / so_name).write_bytes(z.read(name_in_zip))
            size_kb = (cocos_dir / so_name).stat().st_size / 1024
            C.log_info(f"  提取 {so_name} ({size_kb:.0f} KB)")

    # 3. so 字符串扫描
    for so_file in cocos_dir.glob("*.so"):
        C.log_info(f"扫描 {so_file.name}...")
        result = subprocess.run(
            ["strings", "-n", "6", str(so_file)],
            capture_output=True, text=True, timeout=60
        )
        refs = [line for line in result.stdout.splitlines()
                if any(k in line for k in ["Lua", "tolua", "luaL_load", "lua_pcall", "lua_getglobal"])]
        ref_file = cocos_dir / f"{so_file.stem}_lua_refs.txt"
        ref_file.write_text("\n".join(refs[:10]))
        C.log_info(f"  Lua 引用数: {len(refs)}")

    # 4. 提取 Lua 文件
    lua_dir = out_path / "03-cocos-lua"
    C.ensure_dir(str(lua_dir))
    lua_count = 0
    with zipfile.ZipFile(apk_env, "r") as z:
        for name_in_zip in z.namelist():
            if name_in_zip.lower().endswith(".lua"):
                lua_count += 1
                (lua_dir / Path(name_in_zip).name).write_bytes(z.read(name_in_zip))

    if lua_count > 0:
        C.log_success(f"提取 {lua_count} 个 Lua 文件到 {lua_dir}")
    else:
        C.log_info("未找到 .lua 文件")

    summary = f"LUA_FILES={lua_count} SO_COUNT={len(list(cocos_dir.glob('*.so')))}"
    C.log_success("Cocos2d-x 静态分析完成")


if __name__ == "__main__":
    main()
