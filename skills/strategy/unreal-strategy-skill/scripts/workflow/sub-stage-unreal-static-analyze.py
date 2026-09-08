#!/usr/bin/env python3
# stage-unreal-03-static-analyze — Unreal Engine 静态分析

import re
import subprocess
import sys
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-unreal-03-static-analyze.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_raw(str(apk_path))
    C.ensure_cracking_dirs()

    C.log_step(f"阶段 unreal-03: Unreal Engine 静态分析 ({C.NAME})")

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

    # 2. 提取 UE so
    ue_dir = C.OUT / "03-unreal"
    C.ensure_dir(ue_dir)
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for name in z.namelist():
            basename = Path(name).name
            if any(k in basename for k in ["libUE4", "libUnreal"]):
                (ue_dir / basename).write_bytes(z.read(name))
                size_kb = (ue_dir / basename).stat().st_size / 1024
                C.log_info(f"  提取 {basename} ({size_kb:.0f} KB)")

    # 3. 提取 .pak 资源包
    pak_dir = C.OUT / "03-unreal-pak"
    C.ensure_dir(pak_dir)
    pak_count = 0
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for name in z.namelist():
            if name.lower().endswith(".pak"):
                pak_count += 1
                (pak_dir / Path(name).name).write_bytes(z.read(name))

    if pak_count > 0:
        C.log_success(f"提取 {pak_count} 个 .pak 资源包到 {pak_dir}")
        C.log_info("推荐工具: FModel (https://fmodel.app) 查看 .pak 内容")
    else:
        C.log_info("未找到 .pak 文件")

    # 4. UE 版本识别
    ue_so = list(ue_dir.glob("*.so"))
    if ue_so:
        result = subprocess.run(
            ["strings", str(ue_so[0])],
            capture_output=True, text=True, timeout=60
        )
        versions = [line for line in result.stdout.splitlines()
                    if re.match(r"^\d+\.\d+$", line)]
        C.log_info(f"UE 版本: {versions[:3] if versions else 'unknown'}")

    summary = f"UE_SO={len(ue_so)} PAK_COUNT={pak_count}"
    C.log_success("Unreal Engine 静态分析完成")


if __name__ == "__main__":
    main()
