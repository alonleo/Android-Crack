#!/usr/bin/env python3
"""sub-stage-preprocess-build.py — 子阶段 02 预处理构建（通用主脚本）。

[FLOWFIX 2026-09-04] 该脚本此前长期缺失（REFACTOR 只保留了 il2cpp 转发的
sub-stage-preprocess-build.py，它委托到本路径但本文件从未落地 → stage-02 unpack
step 直接报「缺 common 主脚本」）。本实现落地，并把入口解析统一到 $FAKER_JAR
（默认指 ASBuilder.jar），替代旧的 FakerAndroid-updated.jar 直连。

职责（register 中 stage-02 的 10 步契约）：
  1. 环境初始化（加载 env、解析 APK/NAME/TYPE）
  2. 计算源 APK MD5
  3. 解包：ASBuilder 优先（$FAKER_JAR fake），失败则 apktool 兜底
  4. 输出结构修复（app-as-generated → app 平铺，若存在）
  5+. 资源/manifest/namespace/build.gradle 等细化修复由下游 step（fix-res /
      fix-manifest / namespace / set-gradle-identity）各自执行，本脚本只负责
      AS 骨架生成 + 结构修复 + 记录 build-report。

用法：
    python3 sub-stage-preprocess-build.py          # 从 env NAME/TYPE/APK
    NAME=X TYPE=il2cpp APK=<path> python3 ...

环境变量：
    NAME      项目名（CamelCase）
    TYPE      引擎类型（il2cpp/android/...）
    APK       源 APK 绝对路径（缺省按 NAME 从 apks/ 归一匹配）
    FAKER_JAR ASBuilder 入口 jar（缺省 = execable/ASBuilder.jar；
              兼容回退 execable/FakerAndroid-updated.jar）

输出（stdout 相阶段标记 `I:`，与 faker 日志风格一致）：
    成功：项目骨架在 crackings/<type>/<Name>/project/，
          build-report 落在 stages/02-preprocess-build/build-report.md
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
from pathlib import Path

# REPO = parents[5]（skills/common/general-strategy-skill/scripts/workflow）
REPO = Path(__file__).resolve().parents[5]

sys.path.insert(0, str(REPO / "skills/common/scripts/lib"))
sys.path.insert(0, str(REPO / "skills/common/scripts"))
from common import ensure_env, log_info, log_step, log_success, log_warn, log_error, die  # noqa: E402


# ── 工具解析 ────────────────────────────────────────────────────────────
def _default_faker_jar() -> Path:
    """返回可用的 faker/asbuilder 入口 jar（有缓存顺序：ASBuilder 优先）。"""
    exec_ = REPO / "tools/crack-intergration-tools/execable"
    candidates = [
        exec_ / "ASBuilder.jar",          # ← 当前默认入口
        exec_ / "FakerAndroid-updated.jar",
    ]
    for c in candidates:
        if c.is_file():
            return c
    return candidates[0]


def faker_jar() -> Path:
    """解析 ASBuilder/faker 入口 jar：$FAKER_JAR 显式 → ASBuilder → 兼容回退。"""
    env = os.environ.get("FAKER_JAR", "").strip()
    if env:
        p = Path(env)
        if p.is_file():
            return p
        log_warn(f"$FAKER_JAR 指向不存在的文件，回退默认: {env}")
    return _default_faker_jar()


def _java() -> str:
    """解析 JDK bin/java（env.sh 已把 JAVA_HOME 注入 PATH 则直接用 java）。"""
    ensure_env()
    for cand in ("$JAVA_HOME/bin/java", "java"):
        s = os.path.expandvars(cand)
        if shutil.which(s):
            return s
    return "java"


# ── APK 归一匹配（与 step_base.resolve_apk 同逻辑，避免跨包依赖） ──────
def resolve_apk(name: str, apk_env: str = "") -> "Path | None":
    apk = Path(apk_env) if apk_env and Path(apk_env).exists() else None
    if apk is None:
        # 优先 fat APK（crackings/<type>/<name>/raw/<name>.apk）——XAPK 必须用它
        if (REPO / "crackings").is_dir():
            for proj in sorted((REPO / "crackings").glob(f"*/{name}/raw/{name}.apk")):
                if proj.is_file():
                    apk = proj
                    break
    if apk is None:
        apks_dir = REPO / "apks"
        if apks_dir.exists():
            for c in list(apks_dir.glob("*.apk")) + list(apks_dir.glob("*.xapk")):
                pure = "".join(ch for ch in c.stem if ch.isalnum())
                if name.lower() in pure.lower():
                    apk = c
                    break
    return apk


def _project_dir(type_: str, name: str) -> Path:
    return REPO / "crackings" / type_ / name / "project"


def _fake_asbuilder(apk: Path, proj_dir: Path, jar: Path) -> bool:
    """调 `java -jar $FAKER_JAR fake -o <proj_dir> <apk>` 生成 AS 骨架。

    [FLOWFIX 2026-09-05] 幂等：骨架已完整（settings.gradle + app/libs/*.jar）则跳过重建，
    避免重跑 02 时 rmtree 清掉已生成的 patched.apk。
    """
    if proj_dir.exists():
        libs_dir = proj_dir / "app" / "libs"
        already = (proj_dir / "settings.gradle").is_file() and \
            libs_dir.is_dir() and bool(list(libs_dir.glob("*.jar")))
        if already:
            log_info("骨架已完整（settings.gradle + app/libs/*.jar 存在），跳过 ASBuilder fake 重建")
            return True
        shutil.rmtree(proj_dir)
    proj_dir.mkdir(parents=True, exist_ok=True)
    java = _java()
    cmd = [java, "-jar", str(jar), "fake", "-o", str(proj_dir), str(apk)]

    # 大量 APK 可能 15-20+ 分钟 → stderr 重定向到日志文件读阶段标记
    log = REPO / "temp" / "asbuilder-fake.log"
    log.parent.mkdir(parents=True, exist_ok=True)
    log_info("$ " + " ".join(cmd))
    try:
        with log.open("w") as f:
            r = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT, cwd=str(REPO), timeout=2400)
    except subprocess.TimeoutExpired:
        log_error("ASBuilder fake 超时(2400s)")
        return False

    if log.is_file():
        for line in log.read_text(errors="replace").splitlines():
            if line.startswith("I:") or line.startswith("E:") or line.startswith("W:"):
                print(line)
    # 成功判定：settings.gradle 存在（faker standalone 参考的可靠信号）
    return r.returncode == 0 and (proj_dir / "settings.gradle").is_file()


def _apktool_fallback(apk: Path, proj_dir: Path) -> bool:
    """apktool 兜底解包（ASBuilder 失败时，产出到 proj_dir/raw-apktool）。"""
    ensure_env()
    apktool = os.environ.get("APKTOOL", "apktool")
    out = proj_dir / "raw-apktool"
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)
    cmd = [apktool, "d", str(apk), "-o", str(out), "-f", "--no-res"]
    log_step("ASBuilder 失败 → apktool 兜底解包")
    r = subprocess.run(cmd, cwd=str(REPO))
    return r.returncode == 0 and (out / "AndroidManifest.xml").is_file()


# ── 输出结构修复（app-as-generated → app 平铺） ───────────────────────
def _fix_output_structure(proj_dir: Path) -> bool:
    # 文件名是连字符(fix-fakerandroid-output.py)，不能直接 import → importlib 加载
    fix_py = REPO / "skills/common/scripts/fix-fakerandroid-output.py"
    if not fix_py.is_file():
        log_warn("缺 fix-fakerandroid-output.py，跳过结构修复")
        return True
    import importlib.util as _ilu
    _spec = _ilu.spec_from_file_location("fix_fakerandroid_output_mod", str(fix_py))
    _mod = _ilu.module_from_spec(_spec)
    _spec.loader.exec_module(_mod)  # type: ignore[union-attr]
    try:
        fixed = _mod.fix_fakerandroid_output(str(proj_dir))
    except Exception as e:  # noqa: BLE001
        log_warn(f"fix-fakerandroid-output 执行异常(非致命): {e}")
        fixed = False
    return fixed if fixed is not None else True


def _jarify_project(proj_dir: Path, apk: Path) -> None:
    """用 asbuilder-dex-jarify.py 补齐游戏 dex（ASBuilder 生成工程不含游戏类）。"""
    jarify = REPO / "skills/common/scripts/asbuilder-dex-jarify.py"
    if not jarify.is_file():
        log_warn("缺 asbuilder-dex-jarify.py，跳过游戏 dex 补齐（APK 将仅含骨架类）")
        return
    log_step("补齐游戏 dex（asbuilder-dex-jarify.py）...")
    r = subprocess.run([sys.executable, str(jarify), str(proj_dir), "--apk", str(apk)],
                       cwd=str(REPO), capture_output=True, text=True)
    for line in r.stdout.splitlines():
        print(line)
    if r.returncode != 0:
        log_warn(f"asbuilder-dex-jarify 失败(exit={r.returncode}): {r.stderr[:200]}")


def _build_report(proj_dir: Path, type_: str, name: str, md5: str,
                  stage_id: str, faker_ok: bool) -> Path:
    sd = REPO / "crackings" / type_ / name / "stages" / stage_id
    sd.mkdir(parents=True, exist_ok=True)
    md_path = sd / "build-report.md"
    md = (
        f"# Preprocess-build 报告（{name}）\n\n"
        f"- 源 APK MD5: `{md5}`\n"
        f"- 解包方式: `{'ASBuilder(fake)' if faker_ok else 'apktool(fallback)'}`\n"
        f"- AS 工程目录: `{proj_dir}`\n"
        f"- settings.gradle: `{(proj_dir / 'settings.gradle').is_file()}`\n"
        f"- app/build.gradle: `{(proj_dir / 'app' / 'build.gradle').is_file()}`\n"
    )
    md_path.write_text(md, encoding="utf-8")
    return md_path


def main() -> int:
    ensure_env()
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "il2cpp").strip()
    apk = resolve_apk(name, os.environ.get("APK", ""))
    if not name or not apk or not apk.exists():
        log_error(f"无法解析 APK(name={name}, apk_env={os.environ.get('APK','')})")
        return 1

    md5 = hashlib.md5(apk.read_bytes()).hexdigest()
    jar = faker_jar()
    proj_dir = _project_dir(type_, name)
    log_step(f"preprocess-build: {name} ({type_}), apk={apk.name}, faker={jar.name}")

    # 调用链尽可路由 lib/common.py（AGENTS §1.1：禁止 Agent 手拼命令）
    faker_ok = _fake_asbuilder(apk, proj_dir, jar)
    if not faker_ok:
        faker_ok = False
        if not _apktool_fallback(apk, proj_dir):
            die("ASBuilder fake 与 apktool 兜底均失败")
    _fix_output_structure(proj_dir)

    # ASBuilder 生成工程不含游戏 dex（标准 AGP 不编译 smali）→ 用 jarify 补齐，
    # 使游戏类 + Firebase 等进入最终 APK，避免仅骨架类启动即崩。
    if faker_ok:
        _jarify_project(proj_dir, apk)

    stage_id = "02-preprocess-build"
    md_path = _build_report(proj_dir, type_, name, md5, stage_id, faker_ok)
    settings_ok = (proj_dir / "settings.gradle").is_file()

    log_success(f"preprocess-build 完成: {proj_dir} (settings={settings_ok})")
    print(f"REPORT={md_path}")
    print(f"PROJECT_DIR={proj_dir}")
    return 0 if settings_ok else 1


if __name__ == "__main__":
    sys.exit(main())
