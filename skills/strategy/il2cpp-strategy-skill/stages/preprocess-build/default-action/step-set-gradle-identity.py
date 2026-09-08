#!/usr/bin/env python3
"""step-set-gradle-identity.py — preprocess action step: 设置 Gradle 项目名 + APK 输出文件名。

[2026-09-02 新增] 在预处理子阶段添加函数，实现两个操作：
1. settings.gradle → rootProject.name = '<Name>'（Gradle 项目标识）
2. app/build.gradle → applicationVariants.all { variant -> variant.outputs.all { outputFileName = '<Name>-<versionName>.apk' } }
   （AGP 8.x 语法；老 AGP 也兼容）

插入位置：step 05 namespace 之后、step 07 smali-to-jar 之前。
命名规范：原 step-register 的 06/07 顺延为 07/08；action-register steps 计数 7→8。

调用入口：python3 sub_stage-dispatcher.py --stage preprocess-build
环境依赖：NAME（项目 CamelCase 名）/ TYPE（il2cpp/android/...）/ VERSION（可选，覆盖 versionName）
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from step_base import REPO, Step


SETTINGS_FILE = "settings.gradle"
BUILD_FILE = "app/build.gradle"


def _project_dir() -> Path:
    """crackings/<type>/<Name>/project/ —— 移植 output-projects 后的标准 AS 工程根。"""
    name = os.environ.get("NAME", "")
    type_ = os.environ.get("TYPE", "il2cpp")
    return REPO / "crackings" / type_ / name / "project"


def set_root_project_name(settings_path: Path, name: str) -> dict:
    """写入/更新 rootProject.name = '<name>' 到 settings.gradle。

    返回 {"applied": bool, "old": str|None, "new": str}。
    不存在文件时返回 applied=False。
    """
    if not settings_path.exists():
        return {"applied": False, "old": None, "new": name, "reason": "settings.gradle 不存在"}

    text = settings_path.read_text(encoding="utf-8", errors="ignore")
    pattern = re.compile(r"^\s*rootProject\.name\s*=\s*[\'\"][^\'\"]*[\'\"]\s*$", re.MULTILINE)

    m = pattern.search(text)
    if m:
        old_line = m.group(0)
        new_line = f"rootProject.name = '{name}'"
        new_text = text.replace(old_line, new_line, 1)
        settings_path.write_text(new_text, encoding="utf-8")
        return {"applied": True, "old": old_line, "new": new_line}
    else:
        # 没有 rootProject.name 行 → 在文件末尾追加
        new_line = f"\nrootProject.name = '{name}'\n"
        if f"rootProject.name = '{name}'" not in text:
            settings_path.write_text(text.rstrip() + new_line, encoding="utf-8")
        return {"applied": True, "old": None, "new": new_line.strip()}


def _find_android_block_end(lines: list[str]) -> tuple[int | None, int | None]:
    """找顶层 android { ... } 块的起止行号。

    返回 (block_start, block_end)；都不存在则 (None, None)。
    行维度计数 { 和 }（忽略纯注释行）—— 因为文件可能有多处 "android {"，
    此函数返回**第一个** android 块的边界。
    """
    block_start = None
    for idx, line in enumerate(lines):
        if re.match(r"^\s*android\s*\{", line):
            block_start = idx
            break
    if block_start is None:
        return None, None

    depth = 1
    for j in range(block_start + 1, len(lines)):
        line = lines[j]
        stripped = line.lstrip()
        # 跳过纯注释行（避免误算 { 或 }）
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        opens = line.count("{")
        closes = line.count("}")
        depth += opens - closes
        if depth <= 0:
            return block_start, j
    return block_start, None  # 块未闭合（极少见）


def set_apk_output_filename(build_gradle_path: Path, name: str, version_name: str = "") -> dict:
    """在 app/build.gradle 的 android { ... } 块内注入 applicationVariants.all { ... outputFileName = ... }。

    AGP 8.x 推荐写法（兼容 AGP 7.x）：
        android {
            // ... 其他配置
            applicationVariants.all { variant ->
                variant.outputs.all {
                    def pName = '<Name>'
                    def vName = variant.versionName ?: '<versionName>'
                    outputFileName = "${pName}-${variant.buildType.name}-${vName}.apk"
                }
            }
            // ... 其他配置
        }

    若已存在 applicationVariants.all 块，跳过不重复插入。
    """
    if not build_gradle_path.exists():
        return {"applied": False, "reason": "app/build.gradle 不存在"}

    text = build_gradle_path.read_text(encoding="utf-8", errors="ignore")
    if "applicationVariants.all" in text:
        return {"applied": False, "reason": "已存在 applicationVariants.all 块（不重复插入）"}

    v_name = version_name or os.environ.get("VERSION", "")
    v_part = f" ?: '{v_name}'" if v_name else " ?: '1.0'"

    # 只注入内部块（不带外层 android { ... } 包装）
    inner_block = (
        "\n"
        "    // [AGENTS §1.1/§1.13] gradle identity 自动注入（步骤 06 set-gradle-identity）\n"
        "    applicationVariants.all { variant ->\n"
        "        variant.outputs.all {\n"
        f"            def pName = '{name}'\n"
        f"            def vName = variant.versionName{v_part}\n"
        "            outputFileName = \"${pName}-${variant.buildType.name}-${vName}.apk\"\n"
        "        }\n"
        "    }\n"
    )

    lines = text.split("\n")
    block_start, block_end = _find_android_block_end(lines)

    if block_start is not None and block_end is not None:
        # 在 android 块结束 '}' 之前插入内部块
        new_lines = lines[:block_end] + inner_block.split("\n") + lines[block_end:]
        new_text = "\n".join(new_lines)
    else:
        # 没有完整的 android { ... } 块，追加完整块
        full_block = (
            "\nandroid {\n"
            "    // [AGENTS §1.1/§1.13] gradle identity 自动注入（步骤 06 set-gradle-identity）\n"
            "    applicationVariants.all { variant ->\n"
            "        variant.outputs.all {\n"
            f"            def pName = '{name}'\n"
            f"            def vName = variant.versionName{v_part}\n"
            "            outputFileName = \"${pName}-${variant.buildType.name}-${vName}.apk\"\n"
            "        }\n"
            "    }\n"
            "}\n"
        )
        new_text = text.rstrip() + full_block

    build_gradle_path.write_text(new_text, encoding="utf-8")
    return {"applied": True, "name": name, "version_name": v_name}


class SetGradleIdentityStep(Step):
    def execute(self, steps_results: dict) -> dict:
        name = os.environ.get("NAME", "")
        if not name:
            return {"rc": 1, "skipped": False, "error": "环境变量 NAME 未设置"}

        proj = _project_dir()
        if not proj.exists():
            return {"rc": 1, "skipped": False, "error": f"项目目录不存在: {proj}"}

        settings_path = proj / SETTINGS_FILE
        build_gradle_path = proj / BUILD_FILE

        settings_res = set_root_project_name(settings_path, name)
        build_res = set_apk_output_filename(build_gradle_path, name)

        rc = 0
        if settings_res.get("applied") is False and "reason" in settings_res:
            # 已存在 rootProject.name 的不重复重写：视为成功（幂等）
            if "不存在" in settings_res.get("reason", ""):
                rc = 1
        if build_res.get("applied") is False and "reason" in build_res:
            # 已存在 applicationVariants.all 块：幂等跳过视为成功
            if "不存在" in build_res.get("reason", ""):
                rc = 1

        return {
            "rc": rc,
            "skipped": False,
            "project_dir": str(proj),
            "settings_gradle": settings_res,
            "build_gradle": build_res,
        }