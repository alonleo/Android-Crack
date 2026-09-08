#!/usr/bin/env python3
"""
convert-smali-to-jars.py — smali → dex → jar(.class) 转换（问题 7：输出项目无 smali）。

背景: 标准 AGP 不支持 smali 源集，FakerAndroid 工程去除其专有 gradle 插件后，
smali 目录不会参与编译。方案 B：将 apktool 解包的 `smali{,classesN}` 目录经
smali 汇编器转 `classesN.dex`，再用 dex2jar 转成真 `.class` jar，输出到
`crackings/<type>/<Name>/project/app/libs/`，由 app/build.gradle 的
`implementation fileTree(dir: 'libs', include: ['*.jar'])` 原生引用。

原 inject-smali-dex.py（smali 后注入 APK）保留作回退路径。

用法:
  python3 convert-smali-to-jars.py <Name> [--smali-root <path>] [--out <dir>] [--api 34]

依赖: Java + smali jar（gradle cache 自动查找）+ dex2jar（tools/crack-intergration-tools/execable/dex2jar/）。
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PKG = ROOT / "skills" / "common" / "scripts"

# 复用 inject-smali-dex.py 的 smali 依赖定位与汇编逻辑
_SPEC = importlib.util.spec_from_file_location(
    "inject_smali_dex", str(SCRIPT_PKG / "inject-smali-dex.py")
)
_inj = importlib.util.module_from_spec(_SPEC)
assert _SPEC.loader is not None
_SPEC.loader.exec_module(_inj)

_stage_spec = importlib.util.spec_from_file_location(
    "stage_common_runtime", str(ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts" / "lib" / "stage_common.py")
)
_sc = importlib.util.module_from_spec(_stage_spec)
assert _stage_spec.loader is not None
_stage_spec.loader.exec_module(_sc)

log_info = _sc.log_info
log_warn = _sc.log_warn
log_success = _sc.log_success
fatal = _sc.fatal
register_artifact = _sc.register_artifact

D2J_DIR = ROOT / "tools" / "crack-intergration-tools" / "execable" / "dex2jar"
DEX2JAR_MAIN = "com.googlecode.dex2jar.tools.Dex2jarCmd"
FIX_STACKMAPS_JAR = ROOT / "tools" / "crack-intergration-tools" / "execable" / "FixStackmaps.jar"
ASM_JAR = next(iter(sorted(
    (Path.home() / ".gradle" / "caches").rglob("modules-2/files-2.1/org.ow2.asm/asm/*/*/asm-*.jar")
)), None) if (Path.home() / ".gradle" / "caches").exists() else None


def _smali_dirs(smali_root: Path) -> list:
    """按优先级返回 smali, smali_classes2, smali_classes3, ... 存在的目录。

    [FLOWFIX]: 原版 range(2, 11) 只处理 smali_classes10，
    smali_classes11+ 被忽略，导致 VungleProvider 等类缺失 → AndroidRuntime ClassNotFoundException。
    扩展到 range(2, 30) 覆盖所有 smali_classesX 目录。
    """
    out = []
    if (smali_root / "smali").is_dir():
        out.append(smali_root / "smali")
    for n in range(2, 30):
        d = smali_root / f"smali_classes{n}"
        if d.is_dir():
            out.append(d)
    return out


def dex2jar(dex_path: Path, out_jar: Path) -> bool:
    """dex → 真 .class jar（dex2jar v2.4 + ASM 补 StackMapTable）。

    [FLOWFIX] 用户确认的构建架构：运行时 + 编译时都用 implementation 导入
    dex2jar 转出的 .class jar（javac 编译需要 .class，不能是 dex-in-jar）。
    dex2jar class 缺 StackMapTable → D8 desugar 报 "Expected stack map table"，
    dex2jar 后调用 FixStackmaps（ASM COMPUTE_FRAMES）补齐。
    """
    cp = f"{D2J_DIR}/*"
    cmd = ["java", "-cp", cp, DEX2JAR_MAIN, "-f", "-o", str(out_jar), str(dex_path)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not (r.returncode == 0 and out_jar.is_file()):
        log_warn(f"dex2jar 失败 {dex_path}: {r.stdout[:400]} {r.stderr[:400]}")
        return False
    # 补 StackMapTable（D8 desugar 要求）
    if FIX_STACKMAPS_JAR.is_file() and ASM_JAR and ASM_JAR.is_file():
        fixed = out_jar.with_suffix(".fixed.jar")
        r2 = subprocess.run(
            ["java", "-cp", f"{ASM_JAR}:{FIX_STACKMAPS_JAR}", "FixStackmaps",
             str(out_jar), str(fixed)],
            capture_output=True, text=True)
        if r2.returncode == 0 and fixed.is_file():
            fixed.replace(out_jar)
            log_info(f"  StackMapTable: {r2.stdout.strip()}")
        else:
            log_warn(f"  FixStackmaps 失败: {r2.stdout[:200]} {r2.stderr[:200]}")
    else:
        log_warn("  FixStackmaps.jar / ASM 缺失，跳过 stackmap 修复（D8 desugar 可能报错）")
    return True


def _jar_has_class(apath: Path) -> bool:
    try:
        with zipfile.ZipFile(apath) as z:
            return any(n.endswith(".class") for n in z.namelist())
    except Exception:
        return False


def convert(name: str, smali_root: Path, out_dir: Path, api: int) -> bool:
    """将所有 smali 目录合并为一个 classes.all.dex.jar（合并所有 dex 后转 jar）。

    流程：smali_dir → dex → 合并所有 dex → classes.dex → classes.all.dex.jar
    """
    dirs = _smali_dirs(smali_root)
    if not dirs:
        log_warn(f"{smali_root} 下无 smali 目录，跳过转换")
        return False

    cp = _inj.build_cp(Path(os.path.expanduser("~")))
    if not cp:
        fatal("无法定位 smali/guava/jcommander/antlr 依赖（gradle cache）")
    if not D2J_DIR.is_dir():
        fatal(f"dex2jar 缺失: {D2J_DIR}")

    # 应用包名（仅剔除其 R/BuildConfig，第三方 SDK R 类保留）
    app_pkg = ""
    bg = out_dir.parent / "build.gradle"  # app/build.gradle
    if bg.is_file():
        m = re.search(r"(?:applicationId|namespace)\s+['\"]([^'\"]+)['\"]",
                      bg.read_text(encoding="utf-8", errors="ignore"))
        if m:
            app_pkg = m.group(1)
    if not app_pkg:
        mf = out_dir.parent / "src" / "main" / "AndroidManifest.xml"
        if mf.is_file():
            m = re.search(r'package="([^"]+)"', mf.read_text(encoding="utf-8", errors="ignore"))
            if m:
                app_pkg = m.group(1)

    out_dir.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="smali2jar_"))
    ok_all = True
    try:
        all_dex_files = []
        for sdir in dirs:
            dname = sdir.name
            dex = tmp / f"{dname}.dex"
            if not _inj.assemble_dex(cp, sdir, dex, api):
                log_warn(f"smali 汇编失败: {sdir}")
                ok_all = False
                continue
            all_dex_files.append(dex)
            log_info(f"  汇编 {dname} -> {dex.name} ({dex.stat().st_size / 1024:.0f} KB)")

        # 多 dex 逐个转 jar（不合并）：DexMerger 合并超过 65536 类型会失败，
        # 每个 dex 独立 jar（jar 内直接放 classes.dex，不经 dex2jar）。
        # [FLOWFIX] 原实现合并失败后回退"第一个 dex"，导致 smali_classes2+ 的类
        # （UnityPlayerActivity/androidx.startup 等）缺失 → MainActivity 编译失败。
        if len(all_dex_files) == 1:
            out_jar = out_dir / "classes.all.dex.jar"
            if not dex2jar(all_dex_files[0], out_jar):
                ok_all = False
            else:
                _strip_buildconfig(out_jar, app_pkg)
                n = sum(1 for _ in zipfile.ZipFile(out_jar).namelist() if _.endswith(".class"))
                log_success(f"classes.all.dex.jar <- 1 个 dex（{n} 个 .class）")
                register_artifact(out_jar, "file", "smali 合并 jar（所有 smali 目录）", name=name)
        else:
            for idx, dex in enumerate(all_dex_files, start=1):
                out_jar = out_dir / f"classes.{idx}.dex.jar"
                if not dex2jar(dex, out_jar):
                    ok_all = False
                    log_warn(f"dex2jar 失败: {dex.name}")
                    continue
                _strip_buildconfig(out_jar, app_pkg)
                n = sum(1 for _ in zipfile.ZipFile(out_jar).namelist() if _.endswith(".class"))
                log_info(f"classes.{idx}.dex.jar <- {dex.name}（{n} 个 .class）")
            # [FLOWFIX] 不再生成 classes.all.dex.jar 兼容副本——它是 classes.1.dex.jar
            # 的复制，implementation fileTree 会同时导入两份 → checkReleaseDuplicateClasses
            # 报 "Duplicate class ... found in classes.1.dex.jar and classes.all.dex.jar"。
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return ok_all


def _strip_buildconfig(jar: Path, app_pkg: str = "") -> None:
    """从 jar 剔除应用自身包名的 BuildConfig/R 类（与 AGP 自动生成的类冲突）。

    [FLOWFIX]
    - BuildConfig：AGP 为 applicationId 生成同名 BuildConfig，D8 合并报
      "Type is defined multiple times"。
    - R/R$*：AGP 为应用包名生成 R 类，smali jar 中游戏自带同名 R → 重复。
    - 仅剔除应用自身包名（app_pkg）下的 R/BuildConfig；第三方 SDK
      （GMS/Firebase/compose 等）的 R 类是运行时常量（如
      com.google.android.gms.common.R$string），删除会导致
      NoClassDefFoundError → Firebase 初始化崩溃。
    """
    import tempfile as _tf
    pkg_prefix = app_pkg.replace(".", "/") + "/" if app_pkg else ""
    with zipfile.ZipFile(jar) as zin:
        def _is_conflict(fn: str) -> bool:
            if not fn.endswith(".class"):
                return False
            base = fn[:-6]  # 去掉 .class
            if base.endswith("BuildConfig"):
                return True
            if "/R" == base or "/R$" in base or base.endswith("/R"):
                # 仅应用自身包名下的 R 类与 AGP 冲突
                return bool(pkg_prefix) and fn.startswith(pkg_prefix)
            return False
        hits = [i.filename for i in zin.infolist() if _is_conflict(i.filename)]
        if not hits:
            return
        tmp = jar.with_suffix(".jar.tmp")
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in zin.infolist():
                if _is_conflict(info.filename):
                    continue
                zout.writestr(info, zin.read(info.filename))
    tmp.replace(jar)
    log_info(f"{jar.name}: 剔除冲突 BuildConfig/R × {len(hits)}（仅应用包名，防 D8 duplicate type）")


def main() -> int:
    parser = argparse.ArgumentParser(description="smali → dex → jar(.class) 转换")
    parser.add_argument("name", help="项目名（crackings/<Name> 与 crackings/<type>/<Name>/project）")
    parser.add_argument("--smali-root", default="", help="apktool 解包目录（默认 crackings/<Name>/raw/01-apktool）")
    parser.add_argument("--out", default="", help="jar 输出目录（默认 crackings/<type>/<Name>/project/app/libs）")
    parser.add_argument("--api", type=int, default=34)
    args = parser.parse_args()

    name = args.name
    smali_root = Path(args.smali_root) if args.smali_root else ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "raw" / "01-apktool"
    out_dir = Path(args.out) if args.out else ((os.environ.get("TYPE", "").strip() and (ROOT / "output-projects" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "output-projects" / name)) / "app" / "libs"
    return 0 if convert(name, smali_root, out_dir, args.api) else 1


if __name__ == "__main__":
    sys.exit(main())
