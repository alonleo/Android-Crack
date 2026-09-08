#!/usr/bin/env python3
"""unstore-arsc.py — 将 APK 中 resources.arsc 重新存储为 uncompressed（STORE）+ 4字节对齐。

Android 11+ (SDK 30) 要求 resources.arsc 必须 uncompressed + 4字节对齐,
否则安装报 -124 错。

用法：
    python3 unstore-arsc.py <apk-path>

原地修改 APK。
"""
from __future__ import annotations

import shutil
import sys
import tempfile
import zipfile
from pathlib import Path


def unstore_arsc(apk_path: Path) -> bool:
    """把 APK 内 resources.arsc 改为 ZIP_STORED (uncompressed)。"""
    if not apk_path.exists():
        print(f"[ERROR] APK 不存在: {apk_path}", file=sys.stderr)
        return False

    tmp_dir = tempfile.mkdtemp(prefix="unstore-arsc-")
    try:
        tmp_apk = Path(tmp_dir) / "out.apk"
        with zipfile.ZipFile(apk_path, "r") as zin, zipfile.ZipFile(tmp_apk, "w") as zout:
            for info in zin.infolist():
                data = zin.read(info.filename)
                if info.filename == "resources.arsc":
                    new_info = zipfile.ZipInfo(info.filename, info.date_time)
                    new_info.compress_type = zipfile.ZIP_STORED
                    new_info.external_attr = info.external_attr
                    new_info.create_system = info.create_system
                    zout.writestr(new_info, data)
                    print(f"[unstore-arsc] resources.arsc → ZIP_STORED ({len(data)} bytes)")
                else:
                    # 保留原始压缩方式,避免重打包引入新问题
                    zout.writestr(info, data)
        shutil.move(str(tmp_apk), str(apk_path))
        return True
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1
    apk = Path(sys.argv[1])
    return 0 if unstore_arsc(apk) else 2


if __name__ == "__main__":
    sys.exit(main())
