#!/usr/bin/env python3
# stage-air-03-static-analyze — Adobe AIR 静态分析
# 替代通用 stage-03：增加 ffdec SWF 提取 + AIR SDK 元数据解析

import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-air-03-static-analyze.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_raw(str(apk_path))
    C.ensure_cracking_dirs()

    C.log_step(f"阶段 air-03: Adobe AIR 静态分析 ({C.NAME})")

    # 1. jadx
    jadx_out = C.OUT / "02-jadx"
    jadx_src = jadx_out / "sources"
    C.ensure_dir(jadx_src)
    if any(jadx_src.iterdir()):
        C.log_warn("jadx 输出已存在，跳过")
    else:
        C.log_info("jadx 反编译 Java 容器层...")
        jadx_bin = C.REPO_ROOT / "tools" / "environments" / "bin" / "jadx"
        if jadx_bin.exists():
            subprocess.run(
                [str(jadx_bin), "-d", str(jadx_src), "--no-res", "--threads-count", "8", str(C.APK)],
                capture_output=True, timeout=600
            )
            C.log_success("jadx 完成")
        else:
            C.log_warn(f"jadx 未找到: {jadx_bin}")

    # 2. ffdec SWF 提取
    C.log_info("提取 SWF 文件...")
    swf_dir = C.OUT / "03-swf"
    C.ensure_dir(swf_dir)

    import zipfile
    swf_count = 0
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for name in z.namelist():
            if name.lower().endswith(".swf"):
                swf_count += 1
                swf_name = Path(name).name
                C.log_info(f"  [{swf_count}] 提取 {swf_name}")
                swf_dir.joinpath(swf_name).write_bytes(z.read(name))

    if swf_count > 0:
        C.log_success(f"提取 {swf_count} 个 SWF 文件到 {swf_dir}")
    else:
        C.log_warn("未找到 SWF 文件")

    # 3. application.xml
    C.log_info("提取 AIR 应用描述符...")
    with zipfile.ZipFile(str(C.APK), "r") as z:
        for candidate in ["META-INF/AIR/application.xml", "assets/META-INF/AIR/application.xml"]:
            try:
                data = z.read(candidate)
                (C.OUT / "03-air-application.xml").write_bytes(data)
                C.log_success("application.xml 已提取")
                text = data.decode("utf-8", errors="replace")
                for line in text.splitlines()[:30]:
                    print(line)
                break
            except KeyError:
                continue
        else:
            C.log_warn("未找到 application.xml")

    summary = f"SWF_COUNT={swf_count}"
    C.log_success("AIR 静态分析完成")


if __name__ == "__main__":
    main()
