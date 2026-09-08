#!/usr/bin/env python3
"""Extract original smali, remove third-party SDK packages, and convert to AS jars."""
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]


def _load_exclude_prefixes() -> tuple:
    """[FLOWFIX 2026-08-18] 从 third-party-sdk-removal-registry.yaml 读 smali_exclude_prefixes。
    保留 androidx/compose（历史需要）+ 清单里加 com/google/firebase/crashlytics。
    找不到清单时 raise SystemExit，强制修复清单（不要静默回退到硬编码）。
    """
    import sys
    sys.path.insert(0, str(REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts"))
    try:
        from load_sdk_removal_registry import load_registry
    except ImportError:
        print("[ERR] load_sdk_removal_registry.py 缺失，无法加载 SDK 移除清单", file=sys.stderr)
        raise SystemExit(1)
    reg = load_registry()
    prefixes = list(reg.get("smali_exclude_prefixes", []))
    if not prefixes:
        print("[ERR] 清单文件 smali_exclude_prefixes 为空，至少应有 androidx/compose", file=sys.stderr)
        raise SystemExit(1)
    return tuple(prefixes)


EXCLUDE = _load_exclude_prefixes()


def ignore_sdk(directory: str, names: list[str]) -> set[str]:
    """copytree ignore 回调：按单层目录名过滤（顶层足够）。"""
    root = Path(directory)
    ignored = set()
    for name in names:
        rel = str((root / name).relative_to(root)).replace("\\", "/")
        if any(rel == prefix or rel.startswith(prefix + "/") for prefix in EXCLUDE):
            ignored.add(name)
    return ignored


def purge_excluded(filtered: Path) -> None:
    """复制完成后删除 filtered 下的 EXCLUDE 子树。

    [FLOWFIX]
    copytree ignore 回调无法按多层路径过滤（androidx/compose），
    compose 类混入 jar → D8 desugar "default interface method" 错误。
    改为复制后遍历 smali*/ 下每个 EXCLUDE 前缀目录并删除。
    """
    if not filtered.is_dir():
        return
    for smali_dir in filtered.iterdir():
        if not (smali_dir.is_dir() and smali_dir.name.startswith("smali")):
            continue
        for prefix in EXCLUDE:
            # prefix 如 "androidx/compose" → 删 <smali_dir>/androidx/compose
            target = smali_dir / prefix
            if target.is_dir():
                shutil.rmtree(target, ignore_errors=True)
                print(f"[OK] 过滤: {smali_dir.name}/{prefix}")


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_arg = os.environ.get("TYPE", "").strip()
    if not name or not type_arg:
        raise SystemExit("NAME and TYPE are required")
    source = REPO / "output-projects" / type_arg / name / "app" / "src" / "main"
    libs = REPO / "output-projects" / type_arg / name / "app" / "libs"
    converter = REPO / "skills" / "common" / "third-party-removal-strategy-skill" / "scripts" / "convert-smali-to-jars.py"
    if not source.is_dir():
        raise SystemExit(f"smali source missing: {source}")
    with tempfile.TemporaryDirectory(prefix=f"{name}_filtered_smali_") as temp:
        filtered = Path(temp) / "main"
        for child in source.iterdir():
            # [FLOWFIX] 原版只处理 child.name == "smali"，
            # 漏了 smali_classes2..15。改为所有以 "smali" 开头的目录。
            if child.name.startswith("smali") and child.is_dir():
                shutil.copytree(child, filtered / child.name, ignore=ignore_sdk)
        # [FLOWFIX] 复制后按多层前缀删除 EXCLUDE 子树（compose/androidx/kotlin）
        purge_excluded(filtered)
        for jar in libs.glob("*.jar"):
            jar.unlink()
        cmd = [
            "python3", str(converter), name,
            "--smali-root", str(filtered), "--out", str(libs), "--api", "34",
        ]
        result = subprocess.run(cmd, check=False)
        if result.returncode != 0:
            return result.returncode
    # [FLOWFIX] 同步 jar 到 gradlew 编译入口
    # app/libs/（build.gradle 的 fileTree(dir:'libs') 只认这个目录）。
    gen_libs = REPO / "output-projects" / type_arg / name / "app" / "libs"
    gen_libs.mkdir(parents=True, exist_ok=True)
    for jar in libs.glob("*.jar"):
        dst = gen_libs / jar.name
        if dst.resolve() == jar.resolve():
            continue
        if dst.exists():
            dst.unlink()
        shutil.copy2(jar, dst)
    print(f"[OK] 同步 jar 到 {gen_libs}")
    print("[OK] 原始 smali 已完成 SDK 过滤并转换到 AS app/libs")
    print("[INFO] 保留 Unity player、FMOD、游戏专属 Java；过滤广告/分析/AndroidX/Kotlin SDK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
