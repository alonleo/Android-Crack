#!/usr/bin/env python3
"""
asbuilder-dex-jarify.py — ASBuilder 工程补齐游戏 dex（方案 A）：
将原 APK 的 classes*.dex 转为 .class jar 放入 app/libs/，使游戏类进入最终 APK。

原因: ASBuilder 用标准 AGP 不编译 src/main/smali（FakerAndroid 插件机制丢失），
生成工程 APK 仅含骨架类。本脚本把原 APK 每个 dex 做
  dex → dex2jar → 剔应用包名 BuildConfig/R$* → FixStackmaps(补 StackMapTable)
  → LambdaNameNormalizer(ASM 统一 lambda 类名 '-'→'_')
得到 classes.N.dex.jar 放 app/libs/，由 build.gradle 的
  implementation fileTree(dir:'libs', include:['*.jar'])
原生打进 APK（AGP 自动 multidex）。

用法:
  python3 asbuilder-dex-jarify.py <项目根> [--apk <原apk>]

依赖: JDK + dex2jar(tools/.../execable/dex2jar) + FixStackmaps.jar
       + LambdaNameNormalizer.jar + asm-*.jar。
"""
from __future__ import annotations
import argparse, glob, importlib.util, os, re, shutil, subprocess, sys, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
JAVA = ROOT / "tools" / "environments" / "jdk"
D2J = ROOT / "tools" / "crack-intergration-tools" / "execable" / "dex2jar"
FIX_STACKMAPS = ROOT / "tools" / "crack-intergration-tools" / "execable" / "FixStackmaps.jar"
LAMBDA_NORM = ROOT / "tools" / "crack-intergration-tools" / "execable" / "LambdaNameNormalizer.jar"


def _java() -> str:
    for jd in sorted((JAVA).iterdir(), reverse=True):
        b = jd / "bin" / "java"
        if b.is_file():
            return str(b)
    return "java"


def _asm() -> str:
    """ASM 完整 classpath（asm + asm-commons + asm-tree + asm-analysis），FixStackmaps/LambdaNameNormalizer 均需要。"""
    need = ["asm-", "asm-commons-", "asm-tree-", "asm-analysis-"]
    jars = []
    have = sorted(str(p) for p in D2J.glob("asm-*.jar"))
    for prefix in need:
        m = [j for j in have if j.rsplit("/", 1)[-1].startswith(prefix)]
        if m:
            jars.append(m[0])
    return ":".join(jars) if jars else ""


def _app_pkg(project: Path) -> str:
    bg = project / "app" / "build.gradle"
    if bg.is_file():
        m = re.search(r"applicationId\s+['\"]([^'\"]+)['\"]", bg.read_text(errors="ignore"))
        if m:
            return m.group(1)
    mf = project / "app" / "src" / "main" / "AndroidManifest.xml"
    if mf.is_file():
        m = re.search(r'package="([^"]+)"', mf.read_text(errors="ignore"))
        if m:
            return m.group(1)
    return ""


def _strip_conflict(jar_in, jar_out, app_pkg, filter_prefixes=()):
    """剔 jar 中应用包名的 BuildConfig + R/R$* 类（AGP 会生成同名，重复致 D8 merge 失败）。

    [FLOWFIX 2026-09-05] 增加 SDK 过滤：按 --filter-prefixes 里的类包前缀（registry
    smali_exclude_prefixes）剔除第三方 SDK 类，实现 ASBuilder 架构下的激进 SDK 移除。
    """
    pre = app_pkg.replace(".", "/") + "/" if app_pkg else ""
    fp = [p.replace(".", "/").rstrip("/") + "/" for p in (filter_prefixes or [])]
    zin = zipfile.ZipFile(jar_in)
    infos = [i for i in zin.infolist()
             if not _is_conflict(i.filename, pre) and not _in_filter(i.filename, fp)]
    with zipfile.ZipFile(jar_out, "w", zipfile.ZIP_DEFLATED) as zo:
        for i in infos:
            zo.writestr(i, zin.read(i.filename))
    zin.close()


def _in_filter(fn, filter_prefixes):
    if not fn.endswith(".class"):
        return False
    for p in filter_prefixes:
        if fn.startswith(p):
            return True
    return False


def _is_conflict(fn, pre):
    if not fn.endswith(".class"):
        return False
    base = fn[:-6]
    if base.endswith("BuildConfig"):
        return True
    if base.endswith("/R") or "/R$" in base or base.endswith("R"):
        return bool(pre) and fn.startswith(pre)
    return False


def _fixed_jar(tmp, idx, dex_path, out_path, app_pkg, filter_prefixes=()):
    raw = tmp / f"c{idx}.jar"
    stripped = tmp / f"c{idx}.strip.jar"
    java = _java()
    r = subprocess.run([java, "-cp", f"{D2J}/*", "com.googlecode.dex2jar.tools.Dex2jarCmd",
                        "-f", "-o", str(raw), str(dex_path)], capture_output=True, text=True)
    if not (r.returncode == 0 and raw.is_file()):
        print(f"  [ERR] dex2jar {dex_path.name}: {r.stderr[:200]}", file=sys.stderr)
        return False
    _strip_conflict(raw, stripped, app_pkg, filter_prefixes)
    asm = _asm()
    stackmap = tmp / f"c{idx}.stackmap.jar"
    r2 = subprocess.run([java, "-cp", f"{asm}:{FIX_STACKMAPS}", "FixStackmaps",
                         str(stripped), str(stackmap)], capture_output=True, text=True)
    if not (r2.returncode == 0 and stackmap.is_file()):
        print(f"  [WARN] FixStackmaps {raw.name}: {r2.stderr[:150]}", file=sys.stderr)
        shutil.copy(stripped, stackmap)
    # ASM 归一化 lambda 类名（'-'→'_'，dex2jar 只改了类定义名未改内部引用）
    if LAMBDA_NORM.is_file():
        r3 = subprocess.run(
            [java, "-cp", f"{LAMBDA_NORM}:{asm}:{FIX_STACKMAPS}",
             "LambdaNameNormalizer", str(stackmap), str(out_path)],
            capture_output=True, text=True)
        if not (r3.returncode == 0 and out_path.is_file()):
            print(f"  [WARN] LambdaNameNormalizer {stackmap.name}: {r3.stderr[:150]}", file=sys.stderr)
            shutil.copy(stackmap, out_path)
    else:
        shutil.copy(stackmap, out_path)
        print("  [WARN] 缺 LambdaNameNormalizer.jar，跳过 lambda 类名归一化", file=sys.stderr)
    n = sum(1 for _ in zipfile.ZipFile(out_path).namelist() if _.endswith(".class"))
    print(f"  {out_path.name} <- {dex_path.name} ({n} .class)")
    return True


def _load_filter_prefixes():
    """从 SDK 移除 registry 读 smali_exclude_prefixes，作为 jar 内 SDK 类剔除前缀。

    [FLOWFIX 2026-09-05] ASBuilder 架构下 SDK 类经 libs jar 进 APK，这里从
    registry 聚合前缀（含 smali_exclude_prefixes + so_keyword_contains 对应类包），
    供 --filter-prefixes 默认使用。
    """
    try:
        import yaml
        reg = _REGISTRY_PATH
        if reg.is_file():
            data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
            return list(data.get("smali_exclude_prefixes", []) or [])
    except Exception:
        pass
    return []


# registry 路径（与 apply-sdk-removal-from-registry.py / load_sdk_removal_registry.py 一致）
_REGISTRY_PATH = ROOT / "skills" / "common" / "third-party-removal-strategy-skill" / "references/third-party-sdk-removal-registry.yaml"


def run(project: Path, apk: Path = None, filter_prefixes=()) -> bool:
    # 找原 APK
    if apk is None or not apk.is_file():
        # 从 status.yaml(若有) 或 libs 推断跳过; 通常传 --apk
        pass
    if apk is None or not apk.exists():
        print("需 --apk <原apk>", file=sys.stderr)
        return False
    libs = project / "app" / "libs"
    libs.mkdir(parents=True, exist_ok=True)
    for old in glob.glob(str(libs / "classes*.dex.jar")):
        os.remove(old)
    app_pkg = _app_pkg(project)
    fp = list(filter_prefixes or _load_filter_prefixes())
    if fp:
        print(f"SDK 过滤前缀: {len(fp)} 个")
    tmp = Path(__import__("tempfile").mkdtemp(prefix="asbj_"))
    ok = True
    try:
        z = zipfile.ZipFile(apk)
        dexs = sorted(n for n in z.namelist() if n.endswith(".dex"))
        print(f"原 APK dex: {dexs}")
        for idx, name in enumerate(dexs, 1):
            dex_path = tmp / f"c{idx}.dex"
            with open(dex_path, "wb") as f:
                f.write(z.read(name))
            out = libs / f"classes.{idx}.dex.jar"
            if not _fixed_jar(tmp, idx, dex_path, out, app_pkg, fp):
                ok = False
        z.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print("游戏 dex 已补齐 →", libs)
    return ok


def main() -> int:
    p = argparse.ArgumentParser(description="ASBuilder 工程补齐游戏 dex")
    p.add_argument("project", help="生成工程根(含 app/)")
    p.add_argument("--apk", default="", help="原 APK 路径")
    p.add_argument("--filter-prefixes", default=None,
                   help="(可选) 逗号分隔的类包前缀，jar 内剔除这些 SDK 类；缺省用 SDK 移除 registry 的 smali_exclude_prefixes")
    a = p.parse_args()
    pr = Path(a.project)
    apk = Path(a.apk) if a.apk else None
    fpx = ([x.strip() for x in a.filter_prefixes.split(",") if x.strip()]
           if a.filter_prefixes else None)
    return 0 if run(pr, apk, fpx if fpx is not None else _load_filter_prefixes()) else 1


if __name__ == "__main__":
    sys.exit(main())