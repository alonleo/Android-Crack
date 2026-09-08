#!/usr/bin/env python3
"""
fix-faker-android-invalid-data.py — FakerAndroid apktool 2.4.0 损坏兜底合并。

触发条件：ASBuilder.jar fake 日志含 "Invalid data detected."，
或 AndroidManifest.xml 含空属性（<uses-permission android:name=""/> 等）。

行为：
  1. 用项目环境 apktool 2.11.1 解 merged APK → raw/01-apktool
  2. 把 apktool 解出的 smali*/ + res/ + jniLibs/ + assets/ 合并到 app/
  3. 用 apktool 解析后的 AndroidManifest.xml 替换 FakerAndroid 损坏的 manifest
  4. 移除 <manifest> 上的 android:requiredSplitTypes / android:splitTypes 属性
     （adb install 会因 INSTALL_FAILED_MISSING_SPLIT 失败）
  5. 删除 FakerAndroid 自带的 app/javaScaffoding/classes.all.dex.jar（82MB）
     和 app/libs/（空目录），后续由 inject-smali-dex.py 注入

约定：
  - <name> 项目名（crackings/<name>/ + crackings/<type>/<name>/project/）
  - APK = crackings/<name>/raw/source-merged.apk
  - app = crackings/<type>/<name>/project/app/
  - raw/01-apktool = crackings/<name>/raw/01-apktool

依赖：env.sh 已 source（含 APKTOOL / JAVA / Python 3）。
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT / "tools" / "scripts" / "lib"))
from common import (
    ensure_dir,
    register_artifact,
    setup_paths_from_apk,
    setup_paths_from_name,
    append_status,
    append_tool_call,
    log_info,
    log_warn,
    log_step,
    log_success,
    log_error,
)

APKTOOL = os.environ.get("APKTOOL") or "apktool"


def _name() -> str:
    return os.environ.get("NAME", "").strip() or (sys.exit("NAME 未设置") or "")


def _merged_apk(name: str) -> Path:
    """查找 merged APK：优先 source-merged.apk，其次 <Name>.apk，最后 raw/ 下第一个 .apk。"""
    raw_dir = ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "raw"
    candidates = [
        raw_dir / "source-merged.apk",
        raw_dir / f"{name}.apk",
    ]
    for c in candidates:
        if c.is_file():
            return c
    # fallback: raw/ 下第一个 .apk
    apks = sorted(raw_dir.glob("*.apk"))
    if apks:
        return apks[0]
    return raw_dir / "source-merged.apk"  # 返回默认路径（不存在时由调用方报错）


def _apktool_out(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "raw" / "01-apktool"


def _app_generated(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name))


def _stage_dir(name: str) -> Path:
    return ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "stages" / "01-fake-android"


def detect_invalid_data(faker_log: Path) -> int:
    """扫描 FakerAndroid 日志中 Invalid data detected 出现次数。"""
    if not faker_log.is_file():
        return 0
    text = faker_log.read_text(encoding="utf-8", errors="replace")
    return text.count("Invalid data detected")


def detect_manifest_corruption(manifest: Path) -> bool:
    """检查 manifest 含空属性（FakerAndroid apktool 2.4.0 bug 标志）。"""
    if not manifest.is_file():
        return False
    text = manifest.read_text(encoding="utf-8", errors="replace")
    return bool(re.search(r'<uses-permission android:name=""\s*/?>', text)
                or re.search(r'<uses-feature android:name=""\s*/?>', text)
                or re.search(r'android:requiredSplitTypes="', text))


def decode_with_apktool(apk: Path, out: Path) -> bool:
    """调用项目环境 apktool 2.11.1 解包 merged APK。"""
    if out.is_dir() and any(out.iterdir()):
        log_info(f"apktool 已解包: {out}（FORCE_FALLBACK=1 强制重建）")
        if os.environ.get("FORCE_FALLBACK") == "1":
            shutil.rmtree(out)
        else:
            return True
    ensure_dir(out)
    log_step(f"apktool d → {out}")
    code = subprocess.run([APKTOOL, "d", "-f", "-o", str(out), str(apk)],
                          capture_output=True, text=True).returncode
    if code != 0:
        log_error(f"apktool 退出码 {code}")
        return False
    return True


def merge_into_app_generated(apktool_out: Path, app_gen: Path) -> None:
    """把 apktool 解出的 smali*/ + res/ + assets/ + jniLibs/ 拷到 app。"""
    src_main = app_gen / "app" / "src" / "main"
    if not src_main.is_dir():
        log_error(f"app 缺失: {src_main}（先跑 stage-01-fake-android）")
        sys.exit(1)

    project_name = app_gen.parent.name
    for sub in ("smali", "smali_classes2", "smali_classes3", "smali_classes4",
                "smali_classes5", "smali_classes6", "smali_classes7",
                "smali_classes8", "smali_classes9", "smali_classes10",
                "smali_classes11", "smali_assets", "res", "assets", "original", "lib"):
        src = apktool_out / sub
        dst = src_main / sub
        if not src.is_dir():
            continue
        if dst.is_dir():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        log_info(f"merge: {sub}/ → {dst.relative_to(ROOT)}")
        register_artifact(str(dst), "dir", f"apktool 解包 {sub}（fallback 修复）",
                           name=project_name)


def strip_split_attributes(manifest: Path) -> None:
    """移除 <manifest> 上 android:requiredSplitTypes / android:splitTypes。"""
    text = manifest.read_text(encoding="utf-8")
    new = re.sub(r'\s+android:requiredSplitTypes="[^"]*"', '', text)
    new = re.sub(r'\s+android:splitTypes="[^"]*"', '', new)
    if new != text:
        manifest.write_text(new, encoding="utf-8")
        log_info("已移除 android:requiredSplitTypes / splitTypes")


def clean_faker_bloat(app_gen: Path) -> None:
    """移除 FakerAndroid 自带的超大 javaScaffoding/classes.all.dex.jar 与空 libs/。"""
    targets = [
        app_gen / "app" / "javaScaffoding",
        app_gen / "app" / "libs",
        app_gen / "app" / "src" / "main" / "lib",
    ]
    for t in targets:
        if t.is_dir():
            shutil.rmtree(t)
            log_info(f"clean: {t.relative_to(ROOT)}")


def fallback_pipeline(name: str, apk: Path, app_gen: Path, stage_dir: Path) -> bool:
    ensure_dir(stage_dir)
    log_step(f"FakerAndroid 兜底合并 → {name}")
    apktool_out = _apktool_out(name)

    if not decode_with_apktool(apk, apktool_out):
        return False

    clean_faker_bloat(app_gen)
    merge_into_app_generated(apktool_out, app_gen)

    # 关键：apktool 解出的 AndroidManifest.xml 才是完整版（FakerAndroid 的 manifest
    # 含空属性 + requiredSplitTypes/splitTypes，编译必失败）。
    src_manifest = apktool_out / "AndroidManifest.xml"
    dst_manifest = app_gen / "app" / "src" / "main" / "AndroidManifest.xml"
    if src_manifest.is_file():
        shutil.copy2(src_manifest, dst_manifest)
        strip_split_attributes(dst_manifest)
        log_info(f"manifest: {src_manifest.relative_to(ROOT)} → {dst_manifest.relative_to(ROOT)}")
        register_artifact(str(dst_manifest), "file", "AndroidManifest（fallback 修复版）",
                           name=app_gen.parent.name)

    # apktool 解 lib/ 但 Gradle Android 期望 jniLibs/；合并后拷一份到 jniLibs
    src_lib = apktool_out / "lib"
    dst_jnilibs = app_gen / "app" / "src" / "main" / "jniLibs"
    if src_lib.is_dir():
        if dst_jnilibs.is_dir():
            shutil.rmtree(dst_jnilibs)
        shutil.copytree(src_lib, dst_jnilibs)
        log_info(f"jniLibs: lib/ → jniLibs/")
        register_artifact(str(dst_jnilibs), "dir", "jniLibs（fallback 拷贝自 lib/）",
                           name=app_gen.parent.name)

    report = stage_dir / "fallback-report.md"
    report.write_text(f"""# FakerAndroid Invalid Data Fallback Report

- 项目: {name}
- APK: {apk.relative_to(ROOT)}
- apktool 输出: {apktool_out.relative_to(ROOT)}
- app: {app_gen.relative_to(ROOT)}

## 已修复
1. apktool 2.4.0 损坏（Invalid data detected + 空属性）→ 改用项目 apktool 2.11.1
2. smali* + res + assets + jniLibs 已合并
3. AndroidManifest.xml 已清理 requiredSplitTypes / splitTypes
4. javaScaffoding/classes.all.dex.jar（82MB）已删除（后续 inject-smali-dex.py 注入）

## 后续
- 阶段 02 工具链规范化（AGP 7.4.2 / Gradle 7.5.1 / compileSdk 33）
- 阶段 03 ./gradlew assembleRelease 编译验证
""", encoding="utf-8")
    register_artifact(str(report), "file", "fallback 报告", name=app_gen.parent.name)
    log_success(f"fallback 完成: {report}")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="FakerAndroid Invalid Data 兜底")
    parser.add_argument("--apk", help="merged APK（默认 raw/source-merged.apk）")
    parser.add_argument("--name", help="项目名")
    parser.add_argument("--force", action="store_true", help="强制重建 apktool 缓存")
    args = parser.parse_args()

    if args.name:
        setup_paths_from_name(args.name)
        if args.apk:
            os.environ['APK'] = str(Path(args.apk).resolve())
    elif args.apk:
        setup_paths_from_apk(args.apk)
    name = _name()

    # [FLOWFIX] 统一转绝对路径，防止 report 中 relative_to(ROOT) 崩溃（相对路径不在 ROOT 子路径下）
    apk = Path(args.apk).resolve() if args.apk else _merged_apk(name)
    app_gen = _app_generated(name)
    stage_dir = _stage_dir(name)

    if not apk.is_file():
        log_error(f"merged APK 缺失: {apk}")
        return 1
    if not app_gen.is_dir():
        log_error(f"FakerAndroid 产物缺失: {app_gen}（先跑 stage-01-fake-android）")
        return 1

    if args.force:
        os.environ["FORCE_FALLBACK"] = "1"

    return 0 if fallback_pipeline(name, apk, app_gen, stage_dir) else 1


if __name__ == "__main__":
    sys.exit(main())
