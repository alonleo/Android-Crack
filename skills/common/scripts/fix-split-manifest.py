#!/usr/bin/env python3
"""
fix-split-manifest.py — 修复 AndroidManifest.xml 中的 split 配置

用法:
  fix-split-manifest.py <manifest_path> [--res-dir <res_path>]

功能:
  - 移除 android:requiredSplitTypes 属性
  - 移除 android:splitTypes 属性
  - 移除 android:isSplitRequired 属性
  - 移除 com.android.vending.splits.required meta-data
  - 移除 com.android.vending.splits meta-data
  - 删除 res/xml/splits0.xml（Unity split APK 的 asset pack 配置，ASBuilder 合并成 fat 后 AGP 误判会 split）
"""

import sys
import re
from pathlib import Path


def fix_manifest(manifest_path, res_dir=None):
    """修复 AndroidManifest.xml"""
    path = Path(manifest_path)
    
    if not path.exists():
        print(f"[ERROR] 文件不存在: {path}")
        return False
    
    content = path.read_text(encoding='utf-8')
    original = content
    
    # 移除 requiredSplitTypes 属性
    content = re.sub(r'\s+android:requiredSplitTypes="[^"]*"', '', content)
    
    # 移除 splitTypes 属性
    content = re.sub(r'\s+android:splitTypes="[^"]*"', '', content)

    # 移除 isSplitRequired 属性（AGP 误判 split 工程，导致 Unity split 内容被剔除）
    content = re.sub(r'\s+android:isSplitRequired="[^"]*"', '', content)
    
    # 移除 com.android.vending.splits.required meta-data
    content = re.sub(
        r'\s*<meta-data\s+android:name="com\.android\.vending\.splits\.required"\s+android:value="[^"]*"\s*/>',
        '',
        content
    )
    
    # 移除 com.android.vending.splits meta-data
    content = re.sub(
        r'\s*<meta-data\s+android:name="com\.android\.vending\.splits"\s+android:resource="[^"]*"\s*/>',
        '',
        content
    )
    
    if content != original:
        path.write_text(content, encoding='utf-8')
        print(f"[OK] 已修复 manifest: {path}")
    else:
        print(f"[INFO] manifest 无需修复: {path}")
    
    # 删除 res/xml/splits0.xml (Unity asset pack split 配置)
    if res_dir:
        splits_file = Path(res_dir) / 'xml' / 'splits0.xml'
        if splits_file.exists():
            splits_file.unlink()
            print(f"[OK] 已删除 split 配置: {splits_file}")
        else:
            print(f"[INFO] 无 splits0.xml: {splits_file}")
    
    return True


def main():
    if len(sys.argv) < 2:
        print("用法: fix-split-manifest.py <manifest_path> [--res-dir <res_path>]")
        return 1
    
    manifest_path = sys.argv[1]
    res_dir = None
    if '--res-dir' in sys.argv:
        idx = sys.argv.index('--res-dir')
        res_dir = sys.argv[idx + 1] if len(sys.argv) > idx + 1 else None
    
    if fix_manifest(manifest_path, res_dir):
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
