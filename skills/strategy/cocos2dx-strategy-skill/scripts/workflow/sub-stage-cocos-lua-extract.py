#!/usr/bin/env python3
# stage-cocos-05-lua-extract — Cocos2d-x Lua 脚本提取 + 汉化准备
# [FLOWFIX] BigHunter] 重写为兼容 skills/common/scripts/lib/common.py v2 API
# [BigHunter 本项目无 Lua 脚本] 调整为字符串提取（扫描 libMyGame.so + apktool 全文件）

import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-cocos-05-lua-extract.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_apk(str(apk_path))
    C.require_crack_dir()
    C.require_out()

    name = os.environ.get('NAME', '')
    out_path = Path(C.out_dir())

    C.log_step(f"阶段 cocos-05: 脚本/字符串提取 ({name})")

    apktool_out = out_path / "01-apktool"
    strings_dir = out_path / "05-strings"
    C.ensure_dir(str(strings_dir))

    # 1. 收集 Lua 文件（虽然本项目无 Lua，仍保留兼容）
    lua_files = []
    if (apktool_out / "assets").exists():
        for ext in ["*.lua", "*.luac", "*.bytes"]:
            lua_files.extend((apktool_out / "assets").rglob(ext))
    lua_count = len(lua_files)

    if lua_count > 0:
        C.log_success(f"找到 {lua_count} 个 Lua 相关文件")
        luac_out = out_path / "05-lua-decompiled"
        C.ensure_dir(str(luac_out))
        unluac_jar = (Path(C.repo_root()) / "tools" / "crack-intergration-tools"
                      / "source-projects" / "unluac" / "unluac.jar")
        for f in lua_files:
            if f.suffix == ".luac" and unluac_jar.exists():
                out_name = f"{f.stem}.lua"
                subprocess.run(
                    ["java", "-jar", str(unluac_jar), str(f)],
                    capture_output=True, timeout=60,
                    stdout=(luac_out / out_name).open("w")
                )
    else:
        C.log_info("未在 assets/ 下找到 Lua 文件（本项目预期：无 Lua 脚本）")

    # 2. 扫描 libMyGame.so + apktool 全部文件的字符串（替代 Lua 字符串提取）
    raw_strings = strings_dir / "all_strings_raw.txt"
    all_strings = set()

    # 2a. libMyGame.so 字符串
    so_files = list((out_path / "03-cocos").glob("*.so")) if (out_path / "03-cocos").exists() else []
    for so in so_files:
        result = subprocess.run(
            ["strings", "-n", "6", str(so)],
            capture_output=True, text=True, timeout=120
        )
        for line in result.stdout.splitlines():
            line = line.strip()
            if len(line) >= 6 and any(ch.isalpha() for ch in line):
                all_strings.add(line)

    # 2b. apktool 资产里非二进制文件的字符串
    if apktool_out.exists():
        for asset_dir in [apktool_out / "assets", apktool_out / "res"]:
            if not asset_dir.exists():
                continue
            for f in asset_dir.rglob("*"):
                if not f.is_file() or f.suffix.lower() in (".png", ".jpg", ".mp3", ".ogg", ".so", ".dex"):
                    continue
                try:
                    result = subprocess.run(
                        ["strings", "-n", "6", str(f)],
                        capture_output=True, text=True, timeout=10
                    )
                    for line in result.stdout.splitlines():
                        line = line.strip()
                        if len(line) >= 6 and any(ch.isalpha() for ch in line):
                            all_strings.add(line)
                except Exception:
                    pass

    raw_strings.write_text("\n".join(sorted(all_strings)))
    C.log_success(f"提取 {len(all_strings)} 条字符串到 {raw_strings}")

    summary = f"LUA_FILES={lua_count} SO_STRINGS={sum(1 for _ in so_files)} STRINGS_TOTAL={len(all_strings)}"
    C.log_success("Cocos2d-x 脚本/字符串提取完成")


if __name__ == "__main__":
    main()
