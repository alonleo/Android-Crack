#!/usr/bin/env python3
# stage-flutter-03-static-analyze — Flutter 静态分析

import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-flutter-03-static-analyze.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_raw(str(apk_path))
    C.ensure_cracking_dirs()

    C.log_step(f"阶段 flutter-03: Flutter 静态分析 ({C.NAME})")

    # 1. jadx
    jadx_out = C.OUT / "02-jadx"
    jadx_src = jadx_out / "sources"
    C.ensure_dir(jadx_src)
    if any(jadx_src.iterdir()):
        C.log_warn("jadx 输出已存在，跳过")
    else:
        C.log_info("jadx 反编译 Java 壳层...")
        jadx_bin = C.REPO_ROOT / "tools" / "environments" / "bin" / "jadx"
        if jadx_bin.exists():
            subprocess.run(
                [str(jadx_bin), "-d", str(jadx_src), "--no-res", "--threads-count", "8", str(C.APK)],
                capture_output=True, timeout=600
            )
            C.log_success("jadx 完成")
        else:
            C.log_warn(f"jadx 未找到: {jadx_bin}")

    # 2. 提取 Flutter so
    flutter_dir = C.OUT / "03-flutter"
    C.ensure_dir(flutter_dir)
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for name in z.namelist():
            if "libflutter.so" in name or "libapp.so" in name:
                so_name = Path(name).name
                (flutter_dir / so_name).write_bytes(z.read(name))
                size_kb = (flutter_dir / so_name).stat().st_size / 1024
                C.log_info(f"  {so_name}: {size_kb:.0f} KB")

    # 3. Flutter 引擎版本
    flutter_engine = flutter_dir / "libflutter.so"
    if flutter_engine.exists():
        result = subprocess.run(
            ["strings", str(flutter_engine)],
            capture_output=True, text=True, timeout=60
        )
        versions = [line for line in result.stdout.splitlines()
                    if re.match(r"^\d+\.\d+\.\d+", line)]
        for v in versions[:3]:
            C.log_info(f"  Flutter 版本: {v}")

    # 4. libapp.so Dart 快照分析
    dart_snapshot = flutter_dir / "libapp.so"
    dart_symbols_file = flutter_dir / "dart_symbols.txt"
    if dart_snapshot.exists():
        C.log_info("分析 libapp.so Dart AOT 快照...")
        result = subprocess.run(
            ["strings", "-n", "6", str(dart_snapshot)],
            capture_output=True, text=True, timeout=120
        )
        symbols = sorted(set(
            line for line in result.stdout.splitlines()
            if re.match(r"^_?[A-Z][a-z]|^[A-Z][a-z]+\.|^dart:", line)
        ))
        dart_symbols_file.write_text("\n".join(symbols))
        C.log_success(f"提取 {len(symbols)} 个 Dart 符号到 {dart_symbols_file}")

        # blutter
        blutter = subprocess.run(["where", "blutter"], capture_output=True, shell=True)
        if blutter.returncode == 0:
            C.log_info("blutter 可用，执行 libapp.so 分析...")
            blutter_out = flutter_dir / "blutter_output"
            C.ensure_dir(blutter_out)
            subprocess.run(
                ["blutter", str(dart_snapshot), str(blutter_out)],
                capture_output=True, timeout=300
            )
        else:
            C.log_warn("blutter 未安装，Dart 分析受限")

    has_flutter = flutter_engine.exists()
    has_app = dart_snapshot.exists()
    sym_count = len(dart_symbols_file.read_text().splitlines()) if dart_symbols_file.exists() else 0

    summary = f"FLUTTER_SO={'y' if has_flutter else 'n'} APP_SO={'y' if has_app else 'n'} DART_SYMBOLS={sym_count}"
    C.log_success("Flutter 静态分析完成")


if __name__ == "__main__":
    main()
