#!/usr/bin/env python3
# stage-mono-03-static-analyze — Unity Mono / .NET 静态分析

import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-mono-03-static-analyze.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_raw(str(apk_path))
    C.ensure_cracking_dirs()

    C.log_step(f"阶段 mono-03: Unity Mono / .NET 静态分析 ({C.NAME})")

    # 1. jadx
    jadx_out = C.OUT / "02-jadx"
    jadx_src = jadx_out / "sources"
    C.ensure_dir(jadx_src)
    if any(jadx_src.iterdir()):
        C.log_warn("jadx 输出已存在，跳过")
    else:
        C.log_info("jadx 反编译 Java 层...")
        jadx_bin = C.REPO_ROOT / "tools" / "environments" / "bin" / "jadx"
        if jadx_bin.exists():
            subprocess.run(
                [str(jadx_bin), "-d", str(jadx_src), "--no-res", "--threads-count", "8", str(C.APK)],
                capture_output=True, timeout=600
            )
            C.log_success("jadx 完成")
        else:
            C.log_warn(f"jadx 未找到: {jadx_bin}")

    # 2. 提取 .NET DLL
    dll_dir = C.OUT / "03-dll"
    C.ensure_dir(dll_dir)
    C.log_info("提取 .NET DLL...")
    dll_count = 0
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for name in z.namelist():
            if name.lower().endswith(".dll") and "managed" in name.lower():
                dll_name = Path(name).name
                (dll_dir / dll_name).write_bytes(z.read(name))
                dll_count += 1
    C.log_success(f"提取 {dll_count} 个 DLL 到 {dll_dir}")

    # 3. ILSpy 反编译
    ilspy_out_dir = C.OUT / "03-ilspy"
    C.ensure_dir(ilspy_out_dir)
    ilspy_bin = C.REPO_ROOT / "tools" / "crack-intergration-tools" / "source-projects" / "ILSpy" / "artifacts" / "ILSpy" / "ilspy.dll"

    dotnet_ret = subprocess.run(["where", "dotnet"], capture_output=True, shell=True)
    if dotnet_ret.returncode == 0 and ilspy_bin.exists():
        C.log_info("通过 dotnet 运行 ILSpy...")
        for dll in dll_dir.glob("*.dll"):
            dll_out = ilspy_out_dir / dll.stem
            C.ensure_dir(dll_out)
            subprocess.run(
                ["dotnet", str(ilspy_bin), str(dll), "-o", str(dll_out)],
                capture_output=True, timeout=120
            )
        C.log_success("ILSpy 反编译完成")
    else:
        C.log_warn("ILSpy 未安装，DLL 已提取到 {dll_dir}")
        C.log_info("可用 dnSpy/ILSpy GUI 手动分析")

    summary = f"DLL_COUNT={dll_count}"
    C.log_success("Unity Mono / .NET 静态分析完成")


if __name__ == "__main__":
    main()
