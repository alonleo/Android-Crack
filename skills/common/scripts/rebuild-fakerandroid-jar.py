#!/usr/bin/env python3
"""
rebuild-fakerandroid-jar.py — ASBuilder.jar 一键重建（捆绑库全部升级到最新版）。

背景：
  原版 ASBuilder.jar 捆绑 apktool 2.4.0 / smali 2.4.0 / dex2jar 2.1 等老库，
  解码资源时产生大量 "Invalid data detected"（资源丢弃）且 jniLibs 缺失。
  上游仓库 Efaker/FakerAndroid 已 404，无法从源码升级 → 走 jar 手术路线：
  jadx 反编译 com.fakerandroid 自身代码 → 适配新版 API 重编译 → 与最新库重组。

产物：
  tmp/faker-rebuild/FakerAndroid-updated.jar（约 130MB，主类不变
  com.fakerandroid.decoder.Main，CLI 用法与原版一致）

实测收益（143MB il2cpp APK）：
  - "Invalid data detected"：116,680 次 → 0 次
  - jniLibs：缺失 → 完整（全部 .so）
  - 产物：155MB 骨架 → 1.3GB 完整 AS 工程

用法：
  python3 rebuild-fakerandroid-jar.py            # 全流程（幂等，已有产物跳过对应步骤）
  python3 rebuild-fakerandroid-jar.py --fresh    # 清空工作目录重来
  python3 rebuild-fakerandroid-jar.py --test <apk>  # 重建后跑 fake 冒烟测试

依赖（全部在仓库内，无需网络）：
  - tools/environments/env.sh（JDK11/JADX）
  - tools/crack-intergration-tools/execable/{ASBuilder.jar, apktool.jar(2.11.1), dex2jar/}
  - tools/environments/android-sdk/build-tools/34.0.0/lib/dx.jar
  - tmp/faker-rebuild/libs/（本脚本首跑时自动从阿里云 Maven 下载）

关键坑位（详见 [EXPERIENCES.md](../../../../EXPERIENCES.md) §通用构建经验「FakerAndroid jar 手术重建」条目）：
  1. apktool.jar(2.11.1) 捆绑 R8 定制 guava（public 化/旧签名/$r8$clinit 字段），
     与 dexlib2 需要的官方 guava 同 fat-jar 冲突 → PublicizeGuava + PatchGuava 兜底
  2. commons-io 必须用 apktool.jar 内置的 2.18.0（R8 剪裁版，closeQ 为 public）
  3. BaksmaliBaseDexExceptionHandler 只存在于原 ASBuilder.jar（dex2jar 2.4 无）
  4. FakerAndroid 自身代码 5 处 API 适配（源码在 tmp/faker-rebuild/src/ 一次性修正）
"""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR / "lib"))
from common import ensure_env, log_info, log_step, log_success, log_warn, log_error, die  # noqa: E402

ROOT = SCRIPT_DIR.parents[1]

# 路径常量
EXEC = ROOT / "tools" / "crack-intergration-tools" / "execable"
ORIG_JAR = EXEC / "ASBuilder.jar"
APKTOOL_JAR = EXEC / "apktool.jar"
DEX2JAR_DIR = EXEC / "dex2jar"
DX_JAR = ROOT / "tools" / "environments" / "android-sdk" / "build-tools" / "34.0.0" / "lib" / "dx.jar"
WORK = ROOT / "tmp" / "faker-rebuild"
LIBS = WORK / "libs"
SRC = WORK / "src"
STAGING = WORK / "staging"
OUT = WORK / "out"
TOOLS = WORK / "tools"
FINAL_JAR = WORK / "FakerAndroid-updated.jar"
ASSETS_SRC = ROOT / "tools" / "scripts" / "template-files" / "fakerandroid-rebuild"

# 需要从 Maven 下载的库（阿里云镜像；commons-io/lang3/cli 不在此列——用 apktool.jar 内置版）
MAVEN = "https://maven.aliyun.com/repository/central"
MAVEN_LIBS = [
    "org/smali/smali/2.5.2/smali-2.5.2.jar",
    "org/smali/baksmali/2.5.2/baksmali-2.5.2.jar",
    "org/smali/dexlib2/2.5.2/dexlib2-2.5.2.jar",
    "org/smali/util/2.5.2/util-2.5.2.jar",
    "org/antlr/antlr/3.5.2/antlr-3.5.2.jar",
    "org/antlr/antlr-runtime/3.5.2/antlr-runtime-3.5.2.jar",
    "org/antlr/stringtemplate/3.2.1/stringtemplate-3.2.1.jar",
    "com/beust/jcommander/1.82/jcommander-1.82.jar",
    "com/google/guava/guava/33.4.0-jre/guava-33.4.0-jre.jar",
    "com/google/guava/failureaccess/1.0.2/failureaccess-1.0.2.jar",
    "com/google/guava/listenablefuture/9999.0-empty-to-avoid-conflict-with-guava/listenablefuture-9999.0-empty-to-avoid-conflict-with-guava.jar",
    "com/google/code/findbugs/jsr305/3.0.2/jsr305-3.0.2.jar",
    "org/checkerframework/checker-qual/4.2.2/checker-qual-4.2.2.jar",
    "com/google/errorprone/error_prone_annotations/2.50.0/error_prone_annotations-2.50.0.jar",
    "com/google/j2objc/j2objc-annotations/3.0.0/j2objc-annotations-3.0.0.jar",
    "org/dom4j/dom4j/2.2.0/dom4j-2.2.0.jar",
    # commons-cli 用 Maven 完整版：apktool 内置的 R8 剪裁版缺 CommandLineParser 接口
    # （FakerAndroid Main 依赖）；commons-io/lang3 则必须用 apktool 内置版（见坑位 2）
    "commons-cli/commons-cli/1.11.0/commons-cli-1.11.0.jar",
]
# dex2jar 2.4 组件（仓库内已有）
D2J_JARS = [
    "dex-reader-api-v2.4.jar", "dex-reader-v2.4.jar", "dex-ir-v2.4.jar",
    "dex-translator-v2.4.jar", "d2j-smali-v2.4.jar",
    "asm-9.5.jar", "asm-analysis-9.5.jar", "asm-commons-9.5.jar",
    "asm-tree-9.5.jar", "asm-util-9.5.jar", "antlr4-runtime-4.9.3.jar",
]
# 从原 ASBuilder.jar 继承的资源目录（模板/prebuilt 二进制等）
INHERIT_RESOURCES = ["template/*", "project/*", "prebuilt/*", "libs/*",
                     "properties/*", "android/*", "templates/*"]
# apktool R8 定制 guava 中「源码级定制」必须保留的类（构造器/签名改过，ASM 补不了）
CUSTOM_KEEP = [
    "com/google/common/base/CharMatcher$*.class",
    "com/google/common/base/Splitter*.class",
    "com/google/common/io/LittleEndianDataInputStream.class",
    "com/google/common/io/CountingInputStream.class",
]
# 从原 jar 恢复的散件（dex2jar 2.4 无此类）
RESTORE_FROM_ORIG = [
    "com/googlecode/dex2jar/tools/BaksmaliBaseDexExceptionHandler.class",
]


def sh(cmd: list, cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    """执行命令并透传输出。"""
    log_info("$ " + " ".join(str(c) for c in cmd))
    r = subprocess.run([str(c) for c in cmd], cwd=str(cwd) if cwd else None)
    if check and r.returncode != 0:
        die(f"命令失败({r.returncode}): {' '.join(str(c) for c in cmd)}")
    return r


def download_libs() -> None:
    """步骤 1：下载最新版库到 LIBS（已存在则跳过）。"""
    LIBS.mkdir(parents=True, exist_ok=True)
    import urllib.request
    for rel in MAVEN_LIBS:
        dest = LIBS / rel.split("/")[-1]
        if dest.is_file():
            continue
        url = f"{MAVEN}/{rel}"
        log_step(f"下载 {dest.name}")
        try:
            urllib.request.urlretrieve(url, dest)
        except Exception as e:  # noqa: BLE001
            die(f"下载失败 {url}: {e}\n（可手动放置该 jar 到 {LIBS} 后重跑）")
    log_success(f"libs 就绪（{len(MAVEN_LIBS)} 个）")


def decompile_orig() -> None:
    """步骤 2：jadx 反编译原 jar 的 com.fakerandroid 源码（一次性，产出为 SRC）。"""
    if SRC.is_dir() and any(SRC.rglob("Main.java")):
        log_info("src/ 已存在，跳过反编译")
        return
    ensure_env()
    jadx = os.environ.get("JADX", "")
    if not jadx:
        die("JADX 环境变量未设置（先 source tools/environments/env.sh）")
    out = WORK / "jadx-out"
    sh([jadx, "-d", out, "--log-level", "ERROR", ORIG_JAR], check=False)
    smain = out / "sources" / "com" / "fakerandroid"
    if not (smain / "decoder" / "Main.java").is_file():
        die(f"jadx 反编译产物缺失: {smain}")
    SRC.parent.mkdir(parents=True, exist_ok=True)
    if SRC.exists():
        shutil.rmtree(SRC)
    shutil.copytree(smain, SRC / "com" / "fakerandroid")
    log_success(f"反编译源码 → {SRC}（{sum(1 for _ in SRC.rglob('*.java'))} 个 .java）")


APPLY_NOTES = """
jadx 反编译产物需手工适配新版 API 后才能编译（一次性修正，已包含在本脚本的
assets/src-patched/ 快照中；如需重做，改动点见 [EXPERIENCES.md](../../../../EXPERIENCES.md)）：
  - Main.java: apktool 2.11 Config/ExtFile/ApkBuilder/Framework + dex2jar 2.4 ClzCtx
  - PatchDex2jar.java: IR2JConverter builder 链 + convertDex→convertClass
  - ResourceProcesser.java: MetaInfo→ApkInfo
  - Jar/OS.java: IOUtils.copy → InputStream.transferTo（commons-io R8 版签名漂移）
  - ManifestEditor.java: CharEncoding → "UTF-8"（commons-lang3 3.20 已删常量类）
"""


def prepare_src() -> None:
    """步骤 3：使用已修正的源码快照覆盖 jadx 原始产物（assets/src-patched）。"""
    patched = ASSETS_SRC / "src-patched"
    if not patched.is_dir():
        die(f"缺少源码快照目录: {patched}（首次需手工完成适配后放入）")
    decompile_orig()
    # 用快照整体覆盖（快照即完整修正版）
    if SRC.exists():
        shutil.rmtree(SRC)
    shutil.copytree(patched / "com", SRC / "com")
    log_success(f"源码就绪（快照覆盖）→ {SRC}")


def compile_src() -> None:
    """步骤 4：javac 编译（classpath = 新库 + apktool.jar + dex2jar + dx + 原 jar 兜底）。"""
    ensure_env()
    cp_entries = [str(LIBS / "*"), str(APKTOOL_JAR)] + \
                 [str(DEX2JAR_DIR / j) for j in D2J_JARS] + \
                 [str(DX_JAR), str(ORIG_JAR)]
    cp = ":".join(cp_entries)
    (WORK / "cp.txt").write_text(cp, encoding="utf-8")
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir(parents=True)
    files = sorted(str(p) for p in SRC.rglob("*.java"))
    if not files:
        die("无 .java 可编译")
    listing = WORK / "src-list.txt"
    listing.write_text("\n".join(files), encoding="utf-8")
    r = sh(["javac", "-nowarn", "-encoding", "UTF-8", "-d", OUT, "-cp", cp, f"@{listing}"], check=False)
    n_class = sum(1 for _ in OUT.rglob("*.class"))
    if r.returncode != 0 or n_class == 0:
        die(f"javac 失败（exit={r.returncode}, class={n_class}）——检查 src/ 适配是否完整")
    log_success(f"编译 OK → {n_class} 个 .class")


def build_patch_tools() -> None:
    """步骤 5：编译 guava 兼容补丁工具（PublicizeGuava / PatchGuava）。"""
    ensure_env()
    asm = DEX2JAR_DIR / "asm-9.5.jar"
    asm_c = DEX2JAR_DIR / "asm-commons-9.5.jar"
    for tool in ("PublicizeGuava.java", "PatchGuava.java"):
        src_t = ASSETS_SRC / "tools" / tool
        if not src_t.is_file():
            die(f"缺少补丁工具源码: {src_t}")
    TOOLS.mkdir(parents=True, exist_ok=True)
    sh(["javac", "-cp", f"{asm}:{asm_c}", "-d", TOOLS,
        ASSETS_SRC / "tools" / "PublicizeGuava.java", ASSETS_SRC / "tools" / "PatchGuava.java"])
    log_success("补丁工具编译 OK（PublicizeGuava / PatchGuava）")


def stage() -> None:
    """步骤 6：组装 staging 目录（顺序严格，覆盖关系即兼容策略）。"""
    ensure_env()
    asm = DEX2JAR_DIR / "asm-9.5.jar"
    asm_c = DEX2JAR_DIR / "asm-commons-9.5.jar"
    if STAGING.exists():
        shutil.rmtree(STAGING)
    STAGING.mkdir(parents=True)

    # 6.1 apktool.jar 全量（brut + 内置 commons-io/cli/lang3/text + 定制 guava 子集 + prebuilt aapt）
    sh(["unzip", "-oq", APKTOOL_JAR, "-d", STAGING])
    (STAGING / "module-info.class").unlink(missing_ok=True)

    # 6.2 官方 guava 33.4.0 全量（先删 apktool 的定制子集，再放官方完整版）
    gdir = STAGING / "com" / "google"
    if gdir.exists():
        shutil.rmtree(gdir)
    sh(["unzip", "-oq", LIBS / "guava-33.4.0-jre.jar", "com/google/*",
        "-x", "META-INF/*", "-d", STAGING])

    # 6.3 官方 guava 全量 public 化（apktool 的 brut 类跨包访问 guava 内部类）
    sh(["java", "-cp", f"{TOOLS}:{asm}:{asm_c}", "PublicizeGuava", STAGING])

    # 6.4 ASM 签名级补丁（幂等注入：$r8$clinit 字段 / LEDIS 桥 / Preconditions void 桥）
    g = STAGING / "com" / "google" / "common"
    for rel in ("collect/Maps.class", "io/ByteStreams.class", "base/Preconditions.class"):
        f = g / rel
        sh(["java", "-cp", f"{TOOLS}:{asm}", "PatchGuava", f, f])

    # 6.5 回填 apktool R8 源码级定制类（ASM 无法复刻的构造器/签名改动）
    sh(["unzip", "-oq", APKTOOL_JAR, *CUSTOM_KEEP, "-d", STAGING])

    # 6.6 smali/baksmali/dexlib2/util 2.5.2 + 各依赖 + dom4j
    for jar in MAVEN_LIBS:
        name = jar.split("/")[-1]
        if name.startswith("guava-33"):
            continue  # guava 已特殊处理
        # 注：listenablefuture-9999.0 是空壳 jar（无类），unzip 退出码 11 属预期
        sh(["unzip", "-oq", LIBS / name, "-x", "META-INF/*", "-d", STAGING],
           check="listenablefuture" not in name)

    # 6.7 dex2jar 2.4 全家 + dx
    for j in D2J_JARS:
        sh(["unzip", "-oq", DEX2JAR_DIR / j, "-x", "META-INF/*", "-d", STAGING])
    sh(["unzip", "-oq", DX_JAR, "-x", "META-INF/*", "-d", STAGING])

    # 6.8 原 jar 资源（模板/prebuilt il2cpp dumper/gradle 模板）+ 散件类
    sh(["unzip", "-oq", ORIG_JAR, *INHERIT_RESOURCES, "-d", STAGING])
    sh(["unzip", "-oq", ORIG_JAR, *RESTORE_FROM_ORIG, "-d", STAGING])

    # 6.9 重编译的 com.fakerandroid 覆盖原类
    sh(["cp", "-r", f"{OUT}/.", str(STAGING)])

    # 6.10 清理 module-info（部分库带入，fat-jar 内会导致主类加载失败）
    for mi in list(STAGING.rglob("module-info.class")):
        mi.unlink()

    n = sum(1 for _ in STAGING.rglob("*.class"))
    log_success(f"staging 组装完成（{n} 类）")


def package() -> None:
    """步骤 7：打包最终 jar（Main-Class 与原版一致）。"""
    manifest = WORK / "manifest.mf"
    manifest.write_bytes(b"Manifest-Version: 1.0\r\nMain-Class: com.fakerandroid.decoder.Main\r\n\r\n")
    if FINAL_JAR.exists():
        FINAL_JAR.unlink()
    sh(["jar", "cfm", FINAL_JAR, manifest, "-C", STAGING, "."])
    size = FINAL_JAR.stat().st_size / 1024 / 1024
    r = sh(["java", "-jar", FINAL_JAR, "--version"], check=False)
    if r.returncode != 0:
        die("打包后 --version 冒烟失败")
    log_success(f"打包 OK → {FINAL_JAR}（{size:.0f}MB）")


def smoke_test(apk: Path) -> None:
    """可选：用指定 APK 跑 fake 冒烟测试并统计 Invalid data。"""
    out = WORK / "smoke-out"
    if out.exists():
        shutil.rmtree(out)
    log = WORK / "smoke.log"
    with log.open("w") as f:
        r = subprocess.run(["java", "-jar", str(FINAL_JAR), "fake", "-o", str(out), str(apk)],
                           stdout=f, stderr=subprocess.STDOUT, cwd=str(ROOT))
    text = log.read_text(errors="replace")
    invalid = text.count("Invalid data detected")
    ok = r.returncode == 0 and (out / "settings.gradle").is_file()
    if ok:
        log_success(f"冒烟通过：exit=0, Invalid data={invalid} 次, 产物 {out}")
    else:
        log_error(f"冒烟失败：exit={r.returncode}, Invalid data={invalid} 次，日志 {log}")
        sys.exit(1)


def main() -> int:
    import argparse
    ap = argparse.ArgumentParser(description="ASBuilder.jar 一键重建（捆绑库升级）")
    ap.add_argument("--fresh", action="store_true", help="清空工作目录重建（保留 libs 下载缓存与 src 快照）")
    ap.add_argument("--test", metavar="APK", help="重建后跑 fake 冒烟测试")
    args = ap.parse_args()

    ensure_env()
    WORK.mkdir(parents=True, exist_ok=True)
    if args.fresh:
        for d in (STAGING, OUT):
            if d.exists():
                shutil.rmtree(d)
        FINAL_JAR.unlink(missing_ok=True)

    log_step("[1/7] 下载最新版库")
    download_libs()
    log_step("[2/7] 准备源码（jadx + 适配快照）")
    prepare_src()
    log_step("[3/7] 编译 com.fakerandroid")
    compile_src()
    log_step("[4/7] 编译 guava 补丁工具")
    build_patch_tools()
    log_step("[5/7] 组装 staging")
    stage()
    log_step("[6/7] 打包")
    package()
    log_step("[7/7] 完成")
    if args.test:
        smoke_test(Path(args.test).resolve())
    print(FINAL_JAR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
