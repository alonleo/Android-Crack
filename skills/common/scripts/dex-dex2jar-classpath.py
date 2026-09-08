#!/usr/bin/env python3
"""dex-dex2jar-classpath.py — 把原始 APK 的 classes*.dex 用 dex2jar 转成 class jar，
   放入 app/libs/ 作为 javac 编译期 classpath。

替代缺失的 `skills/strategy/scripts/convert-smali-to-jars.py`。
原 convert-smali-to-jars.py 通过 smali 汇编器把 smali/ 转 dex/ 再 d8 转 jar；
本脚本绕开 smali 汇编（SDK smali 库依赖 guava 等，且依赖清单依赖清单不全），
直接对原始 APK 的 dex 用 dex2jar (d2j-dex2jar) 转 class jar。

关键步骤:
1. 提取 source.apk 内 classes*.dex 到临时目录
2. 对每个 dex 用 d2j-dex2jar 转 .jar
4. 从 jar 中剔除 com/<package>/** 类（避免与 Gradle 生成的 R 类重复导致 D8 StackOverflow）
5. 按 dex 索引重命名为 smali_classes{2,3}.jar 等，放入 app/libs/

依赖:
- 原始 APK: apks/<name>.apk
- dex2jar 全套 jar: tools/crack-intergration-tools/execable/dex2jar/*.jar
- 包名: 通过 aapt2 dump badging 自动检测（也可 --package 指定）

用法:
    python3 skills/common/scripts/dex-dex2jar-classpath.py --apk path/to/source.apk \
        --libs crackings/il2cpp/<name>/project/app/libs --aapt2 $AAPT2
    # 或自动检测:
    python3 skills/common/scripts/dex-dex2jar-classpath.py --name NinjaArashi \
        --type il2cpp
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEX2JAR_DIR = REPO / "tools" / "crack-intergration-tools" / "execable" / "dex2jar"


def _dex2jar_classpath() -> str:
    """dex2jar 全套 jar 的 classpath。"""
    if not DEX2JAR_DIR.is_dir():
        sys.exit(f"[ERR] 缺失 dex2jar 目录: {DEX2JAR_DIR}")
    jars = sorted(DEX2JAR_DIR.glob("*.jar"))
    if not jars:
        sys.exit(f"[ERR] dex2jar 目录无 jar: {DEX2JAR_DIR}")
    return ":".join(str(j) for j in jars)


def _detect_package(aapt2: str, apk: Path) -> str:
    """aapt2 dump badging 取 package name。"""
    try:
        r = subprocess.run(
            [aapt2, "dump", "badging", str(apk)],
            capture_output=True, text=True, timeout=60,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as e:
        sys.exit(f"[ERR] aapt2 执行失败: {e}")
    for line in r.stdout.splitlines():
        if line.startswith("package:"):
            # package: name='com.foo.bar' versionCode='1' versionName='1.0'
            for kv in line.split():
                if kv.startswith("name="):
                    return kv.split("'")[1]
    sys.exit(f"[ERR] 无法从 aapt2 解析 package name: {apk}")


def _extract_dex(apk: Path, work: Path) -> list[Path]:
    """unzip 提取 classes*.dex 到 work。"""
    dex_files = []
    with zipfile.ZipFile(apk) as z:
        for n in z.namelist():
            if n.startswith("classes") and n.endswith(".dex"):
                # 安全路径（防 zip slip）
                dest = work / Path(n).name
                with z.open(n) as src, dest.open("wb") as out:
                    shutil.copyfileobj(src, out)
                dex_files.append(dest)
    return sorted(dex_files, key=lambda p: p.name)


def _dex2jar(dex_files: list[Path], dex2jar_cp: str, work: Path) -> list[Path]:
    """每个 dex 单独用 d2j-dex2jar 转 .jar。返回 jar 列表（按 dex 顺序）。"""
    jars = []
    for dex in dex_files:
        out_jar = work / (dex.stem + ".jar")  # classes.jar / classes2.jar / classes3.jar
        cmd = [
            "java", "-cp", dex2jar_cp,
            "com.googlecode.dex2jar.tools.Dex2jarCmd",
            "--force", "-o", str(out_jar), str(dex),
        ]
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode != 0 or not out_jar.is_file():
            sys.exit(f"[ERR] dex2jar 转换失败: {dex.name}\n{r.stderr[-500:]}")
        jars.append(out_jar)
    return jars


def _strip_package(jars: list[Path], package: str, libs_dir: Path, extra_strip_prefixes: list[str] | None = None) -> list[Path]:
    """剔除每个 jar 中 com/<package>/** 类（避免 R 类重复 → D8 StackOverflow）。
    按 dex 序号重命名 smali_classes{2,3}.jar 等放入 libs。

    extra_strip_prefixes: 额外剔除的前缀列表（如 com/applovin、com/ironsource 等），
    防止 SDK 类被 Gradle 合入运行期 APK。
    """
    libs_dir.mkdir(parents=True, exist_ok=True)
    # 清理已有 smali_classes*.jar
    for old in libs_dir.glob("smali_classes*.jar"):
        old.unlink()

    pkg_prefix = f"{package.replace('.', '/')}/"
    strip_set = {pkg_prefix}
    if extra_strip_prefixes:
        for p in extra_strip_prefixes:
            p = p.rstrip("/")
            # 同时支持 "com/applovin" 和 "com.applovin"
            strip_set.add(p.replace('.', '/') + "/")
            strip_set.add(p + "/")  # 原样
    out_jars = []
    for jar in jars:
        # classes.jar → smali_classes.jar (含 com/blackpanther R 类，已剔除)
        # classes2.jar / classes3.jar → smali_classes2.jar / smali_classes3.jar
        if jar.stem == "classes":
            target_name = "smali_classes.jar"
        else:
            num = jar.stem[len("classes"):]
            target_name = f"smali_classes{num}.jar" if num else "smali_classes.jar"

        keep = []
        removed = 0
        removed_by_prefix: dict[str, int] = {}
        with zipfile.ZipFile(jar) as z:
            for n in z.namelist():
                stripped = False
                for prefix in strip_set:
                    if n.startswith(prefix):
                        removed += 1
                        removed_by_prefix[prefix] = removed_by_prefix.get(prefix, 0) + 1
                        stripped = True
                        break
                if stripped:
                    continue
                keep.append((n, z.read(n)))

        target = libs_dir / target_name
        with zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as zout:
            for n, data in keep:
                zout.writestr(n, data)
        prefix_summary = ", ".join(f"{p}={c}" for p, c in removed_by_prefix.items())
        print(f"[OK] {jar.name} → {target_name} (剔除 {removed} 类: {prefix_summary})")
        out_jars.append(target)
    return out_jars


def main() -> int:
    p = argparse.ArgumentParser(description="原始 APK dex → class jar 放入 libs（替代 convert-smali-to-jars.py）")
    p.add_argument("--apk", help="源 APK 路径")
    p.add_argument("--name", help="项目名（与 crackings/<type>/<name>/ 一致；与 --apk 二选一）")
    p.add_argument("--type", default="il2cpp", help="项目 type（apks/ 搜索时父目录）")
    p.add_argument("--libs", help="libs 输出目录（默认 crackings/<type>/<Name>/project/app/libs）")
    p.add_argument("--aapt2", help="aapt2 路径（默认 $AAPT2）")
    p.add_argument("--package", help="手动指定包名（跳过 aapt2 检测）")
    p.add_argument("--strip", action="append", default=[], help="额外剔除的前缀（可多次），如 com/applovin")
    args = p.parse_args()

    # 解析 APK
    if args.apk:
        apk = Path(args.apk).resolve()
    elif args.name:
        type_ = args.type
        apk_dir = REPO / "apks"
        # 归一匹配（去版本/来源后缀）
        candidates = list(apk_dir.glob("*.apk")) + list(apk_dir.glob("*.xapk"))
        norm = "".join(c for c in args.name if c.isalnum()).lower()
        apk = None
        for c in candidates:
            cnorm = "".join(ch for ch in c.stem if ch.isalnum()).lower()
            if norm in cnorm or cnorm in norm:
                apk = c.resolve()
                break
        if apk is None:
            sys.exit(f"[ERR] apks/ 下未找到匹配 {args.name} 的 APK")
    else:
        sys.exit("[ERR] 必须指定 --apk 或 --name")

    if not apk.is_file():
        sys.exit(f"[ERR] APK 不存在: {apk}")

    # 解析 libs 输出目录
    if args.libs:
        libs = Path(args.libs).resolve()
    elif args.name:
        libs = REPO / "output-projects" / args.type / args.name / "app" / "libs"
    else:
        sys.exit("[ERR] 必须指定 --libs 或 --name")

    # 检测包名
    if args.package:
        pkg = args.package
    else:
        aapt2 = args.aapt2 or os.environ.get("AAPT2")
        if not aapt2 or not Path(aapt2).is_file():
            sys.exit("[ERR] 需 --aapt2 或 $AAPT2 环境变量")
        pkg = _detect_package(aapt2, apk)

    print(f"[INFO] APK: {apk}")
    print(f"[INFO] package: {pkg}")
    print(f"[INFO] libs: {libs}")

    dex2jar_cp = _dex2jar_classpath()
    print(f"[INFO] dex2jar cp 已就绪 ({len(dex2jar_cp.split(':'))} jars)")

    with tempfile.TemporaryDirectory(prefix="dex2jar_classpath_") as tmp:
        work = Path(tmp)
        dex_files = _extract_dex(apk, work)
        if not dex_files:
            sys.exit(f"[ERR] APK 中无 classes*.dex: {apk}")
        print(f"[INFO] 提取 {len(dex_files)} 个 dex: {[d.name for d in dex_files]}")

        jars = _dex2jar(dex_files, dex2jar_cp, work)
        print(f"[INFO] dex2jar 完成 {len(jars)} 个 jar")

        out_jars = _strip_package(jars, pkg, libs, extra_strip_prefixes=args.strip)
        print(f"[OK] 共生成 {len(out_jars)} 个 class jar: {[j.name for j in out_jars]}")
        print(f"[DONE] {libs}")
    return 0


if __name__ == "__main__":
    sys.exit(main())