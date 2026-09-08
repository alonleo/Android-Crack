#!/usr/bin/env python3
"""
inject-smali-dex.py — 将 apktool 解包的 smali_classesN 目录编译为 classesN.dex 并注入 APK。

背景: FakerAndroid fake 生成的 AS 工程在去掉其专有 gradle 插件（AGP 7.4.2 兼容）后，
smali_classes2..10 目录不会被 AGP 编译进 dex。原插件通过 SmaliDexArchiveBuilderTask 完成；
本脚本在 assembleRelease 后用 smali 汇编器补齐缺失的 classesN.dex。

用法:
  python3 inject-smali-dex.py --apk <release.apk> --smali-root <src/main> [--api 34]

幂等: 若 APK 已有完整 classesN.dex，跳过对应编译。

依赖: Java + smali jar（自动在 gradle cache / tools 下查找）+ guava + jcommander + antlr-runtime。
"""
import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

SMALI_DIRS = ["smali", "smali_classes2", "smali_classes3", "smali_classes4",
              "smali_classes5", "smali_classes6", "smali_classes7",
              "smali_classes8", "smali_classes9", "smali_classes10",
              # [FLOWFIX] 原版只到 smali_classes10，
              # smali_classes11-15 未注入（UnityPlayer 在 smali_classes14）→
              # VerifyError: Unresolved Reference com.unity3d.player.UnityPlayer。
              "smali_classes11", "smali_classes12", "smali_classes13",
              "smali_classes14", "smali_classes15"]

# dex 编号映射：AGP 产出 classes.dex（含自定义 Java 桥接），故注入从 classes2.dex 起。
# smali/ → classes2.dex, smali_classes2 → classes3.dex, ... smali_classes10 → classes11.dex
def dex_name_for(i: int, dname: str) -> str:
    return f"classes{i + 2}.dex"


def find_jar(home: Path, name: str, fallback_roots=None) -> str:
    roots = [home / ".gradle", home / ".m2"] + (fallback_roots or [])
    for root in roots:
        if not root.is_dir():
            continue
        hits = []
        for p in root.rglob(name):
            if "sources" in str(p) or "javadoc" in str(p):
                continue
            hits.append(str(p))
        if hits:
            hits.sort()
            return hits[0]
    return ""


def build_cp(home: Path) -> str:
    jars = {}
    # smali 3.0.x 的 Main 类为 com.android.tools.smali.smali.Main；
    # 避免误选 jars-9 缓存里的旧版 smali-2.4.0（Main 类不同，且与 dexlib2 3.0.9 不兼容）。
    for jname in ["smali-*.jar", "smali-dexlib2-*.jar", "smali-util-*.jar",
                  "smali-baksmali-*.jar", "guava-31*.jar", "jcommander-*.jar",
                  "antlr-runtime-3.5.2.jar"]:
        hits = sorted(home.rglob(jname), key=lambda p: p.stat().st_mtime, reverse=True)
        # 优先 modules-2（原始 jar）；jars-9 是 gradle 插桩/打包缓存，可能引入
        # org.gradle.internal.classpath.Instrumented 依赖，需避开。
        hits = sorted(hits, key=lambda p: ("jars-9" in str(p),), reverse=False)
        for h in hits:
            if "sources" in str(h) or "javadoc" in str(h):
                continue
            # smali 本体：要求含 com.android.tools.smali.smali.Main，否则跳过
            if jname == "smali-*.jar":
                import zipfile
                try:
                    with zipfile.ZipFile(h) as z:
                        if "com/android/tools/smali/smali/Main.class" not in z.namelist():
                            continue
                except Exception:
                    continue
            jars[jname] = str(h)
            break
    missing = [k for k in ["smali-*.jar", "smali-dexlib2-*.jar", "smali-util-*.jar",
                           "smali-baksmali-*.jar", "guava-31*.jar",
                           "jcommander-*.jar", "antlr-runtime-3.5.2.jar"] if k not in jars]
    if missing:
        print(f"[ERROR] 缺少依赖 jar: {missing}", file=sys.stderr)
        return ""
    return ":".join(jars.values())


def dex_index(apk: Path) -> set:
    with zipfile.ZipFile(apk) as z:
        return {n for n in z.namelist() if n.startswith("classes") and n.endswith(".dex")}


def assemble_dex(cp: str, smali_dir: Path, out_dex: Path, api: int) -> bool:
    cmd = ["java", "-cp", cp, "com.android.tools.smali.smali.Main", "a",
           "--api", str(api), "-o", str(out_dex), str(smali_dir)]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"[ERROR] smali 汇编失败 {smali_dir}:\n{r.stdout}\n{r.stderr}", file=sys.stderr)
        return False
    return True


def inject(apk: Path, smali_root: Path, api: int, java_home: str, force: bool = False) -> bool:
    home = Path(os.path.expanduser("~"))
    cp = build_cp(home)
    if not cp:
        print("[ERROR] 无法定位 smali/guava/jcommander/antlr 依赖", file=sys.stderr)
        return False

    existing = dex_index(apk)
    tmp = Path(tempfile.mkdtemp(prefix="smali_dex_"))
    new_dex = []
    try:
        for i, dname in enumerate(SMALI_DIRS):
            sdir = smali_root / dname
            if not sdir.is_dir():
                continue
            target = dex_name_for(i, dname)
            if not force and target in existing:
                print(f"[SKIP] {target} 已存在")
                continue
            out_dex = tmp / target
            if not assemble_dex(cp, sdir, out_dex, api):
                return False
            new_dex.append((target, out_dex))
            print(f"[ASSEMBLE] {dname} -> {target} ({out_dex.stat().st_size} bytes)")

        if not new_dex:
            print("[INFO] 无需注入 dex")
            return True

        # 注入到 APK
        bak = str(apk) + ".bak"
        shutil.copy2(apk, bak)
        targets = {target for target, _ in new_dex}
        with zipfile.ZipFile(bak, "r") as zin, \
             zipfile.ZipFile(apk, "w", zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                if item.filename in targets:
                    continue
                zout.writestr(item, zin.read(item.filename))
            for target, dex_path in new_dex:
                zout.write(dex_path, target)
        os.remove(bak)
        print(f"[OK] 注入完成: {apk} (新增 {len(new_dex)} 个 dex)")
        return True
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main() -> int:
    p = argparse.ArgumentParser(description="smali → dex 注入 APK（smali 修改后重注入用 --force）")
    p.add_argument("--apk", required=True, help="release APK 路径")
    p.add_argument("--smali-root", required=True, help="app/src/main 目录（含 smali_classesN）")
    p.add_argument("--api", type=int, default=34)
    p.add_argument("--force", action="store_true",
                   help="强制重编所有 smali_classesN（即使 dex 已存在）")
    args = p.parse_args()
    return 0 if inject(Path(args.apk), Path(args.smali_root), args.api, "", args.force) else 1


if __name__ == "__main__":
    sys.exit(main())
