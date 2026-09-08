#!/usr/bin/env python3
# stage-air-09-fonts — Adobe AIR 字体替换
# AIR APK 的字体嵌入在 SWF 中 + assets/fonts/ 下

import subprocess
import sys
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "lib"))
import common as C


def main():
    if len(sys.argv) < 2:
        C.die("用法: stage-air-09-fonts.py <apk-path>")
    apk_path = Path(sys.argv[1])
    C.setup_paths_from_raw(str(apk_path))
    C.require_crack_dir()
    C.require_out()

    C.log_step(f"阶段 air-09: AIR 字体替换 ({C.NAME})")

    apktool_out = C.OUT / "01-apktool"
    fonts_dir = apktool_out / "assets" / "fonts"
    C.ensure_dir(fonts_dir)
    fonts_out = C.OUT / "08-fonts"
    C.ensure_dir(fonts_out)

    # 1. 列出 SWF 中的嵌入字体
    swf_dir = C.OUT / "03-swf"
    swf_fonts_file = fonts_out / "swf_embedded_fonts.txt"
    swf_fonts_file.write_text("")

    ffdec = subprocess.run(["where", "ffdec"], capture_output=True, shell=True)
    if ffdec.returncode == 0:
        for swf in swf_dir.glob("*.swf"):
            C.log_info(f"检查 SWF 嵌入字体: {swf.name}")
            ffdec_out = fonts_out / "ffdec_fonts"
            C.ensure_dir(ffdec_out)
            subprocess.run(
                ["ffdec", "-export", "font", str(ffdec_out), str(swf)],
                capture_output=True, timeout=120
            )
        fonts = list(ffdec_out.rglob("*.ttf")) + list(ffdec_out.rglob("*.otf"))
        swf_fonts_file.write_text("\n".join(str(f) for f in fonts))
    else:
        C.log_warn("ffdec 未安装，跳过 SWF 字体提取")

    # 2. 列出 assets/fonts 下的 TTF/OTF
    asset_fonts_file = fonts_out / "asset_fonts.txt"
    asset_fonts = list(fonts_dir.rglob("*.ttf")) + list(fonts_dir.rglob("*.otf")) + list(fonts_dir.rglob("*.ttc"))
    asset_fonts_file.write_text("\n".join(str(f) for f in asset_fonts))
    C.log_info(f"assets/fonts 下找到 {len(asset_fonts)} 个字体文件")

    # 3. 中文字体子集化
    noto_src = Path(os.environ.get("NOTO_SRC", "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"))
    if noto_src.exists():
        C.log_info(f"从 {noto_src} 生成子集字体...")
        dst = fonts_out / "NotoSansSC-subset.ttf"
        if dst.exists():
            C.log_warn("子集字体已存在，跳过")
        else:
            try:
                from fontTools.subset import Subsetter
                from fontTools.ttLib import TTFont
                font = TTFont(str(noto_src), fontNumber=0)
                subsetter = Subsetter()
                subsetter.populate(text="".join(chr(c) for c in range(0x4e00, 0x9fff)))
                subsetter.subset(font)
                font.save(str(dst))
                C.log_success(f"子集字体已生成: {dst}")
            except ImportError:
                C.log_warn("fontTools 未安装，跳过字体子集化")
    else:
        C.log_warn(f"NotoSansCJK 未找到 ({noto_src})，跳过字体子集化")

    swf_count = len(swf_fonts_file.read_text().splitlines()) if swf_fonts_file.exists() else 0
    summary = f"SWF_FONTS={swf_count} ASSET_FONTS={len(asset_fonts)}"
    C.log_success("AIR 字体替换分析完成")


if __name__ == "__main__":
    main()
