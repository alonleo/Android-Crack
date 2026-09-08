#!/usr/bin/env python3
"""init-project-index.py — 为已有 crackings/<Name>/ 项目生成/刷新 dir-index.yaml。

作用：
  遍历项目目录，把顶层文件 + 子目录（含 stages/ 下每个阶段目录）登记到
  crackings/<Name>/dir-index.yaml（项目目录索引表）。

背景：
  新项目在 crack.py 或 setup_paths_* 初始化时自动生成 dir-index.yaml；
  本项目用于**已有项目**补建索引（历史上未登记的项目）。

用法：
  python3 init-project-index.py <Name>            # 按项目名
  python3 init-project-index.py --from-apk <apk>  # 按 APK 路径
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import (  # noqa: E402
    normalize_apk_name,
    register_artifact,
    repo_root,
    setup_paths_from_apk,
    setup_paths_from_name,
)

TOP_FILE_DESC = {
    "status.yaml": "项目状态",
    "findings.md": "结构化知识",
    "difficulty.json": "难度评估产物",
    "source.apk.md5": "源 APK 完整性",
    "tool-calls.md": "工具调用记录",
    "recommendation.txt": "类型路由建议",
    "type.txt": "类型标签",
    "dir-index.yaml": "项目目录索引表（本文件）",
}

DIR_DESC = {
    "raw": "原始/解包产物",
    "keystore": "签名密钥",
    "stages": "阶段产物根目录",
    "deliverables": "交付物",
}


def refresh_project(name: str, type: str = None) -> int:
    setup_paths_from_name(name, type)
    root = repo_root()
    if type:
        proj = os.path.join(root, "crackings", type, name)
    else:
        proj = os.path.join(root, "crackings", name)
    if not os.path.isdir(proj):
        print(f"项目目录不存在: {proj}")
        return 1

    # 顶层文件
    for f, desc in TOP_FILE_DESC.items():
        p = os.path.join(proj, f)
        if os.path.exists(p):
            register_artifact(p, "file", desc, name=name)

    # 子目录 + stages/
    for entry in sorted(os.listdir(proj)):
        full = os.path.join(proj, entry)
        if not os.path.isdir(full):
            continue
        if entry == "stages":
            register_artifact(full, "dir", DIR_DESC["stages"], name=name)
            for st in sorted(os.listdir(full)):
                sf = os.path.join(full, st)
                if os.path.isdir(sf):
                    register_artifact(sf, "dir", f"阶段目录 {st}", name=name)
        elif entry in DIR_DESC:
            register_artifact(full, "dir", DIR_DESC[entry], name=name)

    idx = os.path.join(proj, "dir-index.yaml")
    print(f"已刷新 {idx}")
    return 0


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description="为已有项目生成/刷新 dir-index.yaml")
    parser.add_argument("name", nargs="?", help="项目名（crackings/<type>/<Name>/ 或 crackings/<Name>/）")
    parser.add_argument("--from-apk", dest="apk", help="按 APK 路径推断项目名")
    parser.add_argument("--type", dest="type", default=None, help="引擎类型（il2cpp/android/air/...），使用 crackings/<type>/<Name>/ 路径")
    args = parser.parse_args()

    if args.apk:
        setup_paths_from_apk(args.apk, args.type)
        name = os.environ["NAME"]
        return refresh_project(name, args.type)
    if args.name:
        return refresh_project(args.name, args.type)
    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
