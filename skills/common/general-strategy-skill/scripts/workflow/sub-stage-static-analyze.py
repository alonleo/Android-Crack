#!/usr/bin/env python3
"""sub-stage-static-analyze.py — 通用静态分析（01）通用骨架。

[FLOWFIX 2026-08-30] 原脚本长期缺失；il2cpp step-scan-entries 委托本脚本。
按 STRATEGY.md §1.3.1 / WORKFLOW.md §1.3.1 01 步骤：jadx 反编译 + smali + SDK 扫描 + 入口定位。

用法：
    NAME=<Name> TYPE=<type> APK=<apk> python3 sub-stage-static-analyze.py
    # 也可省略 APK，从 apks/ 按 name 找
    # 注：il2cpp/unity-mono 等还要额外提取 libil2cpp.so + global-metadata.dat（按 type-specific 分支）

输出：
    - crackings/<type>/<Name>/raw/03-jadx/sources/         # jadx 反编译产物
    - crackings/<type>/<Name>/04-findings/sdks_found.txt   # 扫描出的 SDK
    - crackings/<type>/<Name>/raw/03-static-analyze/original-entry-analysis.md  # 入口定位
    - il2cpp 额外: 提取 libil2cpp.so + global-metadata.dat 到 raw/03-static-analyze/native/
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

# type-specific 提取（il2cpp 额外抽 .so + global-metadata.dat）
TYPE_NATIVE_ASSETS = {
    "il2cpp": [
        "lib/.*/libil2cpp\\.so",
        "assets/bin/Data/Managed/Metadata/global-metadata\\.dat",
    ],
    "unity-mono": [
        "lib/.*/GameAssembly\\.dll",
        "assets/bin/Data/Managed/Metadata/global-metadata\\.dat",
    ],
}


def _jadx() -> str:
    """读 env.sh 设置的 JADX（注意 env.sh 用 JADX 而非 JADX_BIN），否则 PATH 找 jadx。"""
    jadx = os.environ.get("JADX", "").strip()
    return jadx or shutil.which("jadx") or "jadx"


def _log(msg: str) -> None:
    print(f"[static-analyze] {msg}", flush=True)


def run_jadx(apk: Path, out_dir: Path) -> int:
    """跑 jadx 反编译 Java 层（输出 Java 源码）。

    [FLOWFIX 2026-08-30] 不使用 capture_output=True（jadx 输出 >1MB 时 pipe 可能 BrokenPipeError
    被脚本误判 FileNotFoundError）；改为输出到 DEVNULL，退出码即 rc。
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    jadx = _jadx()
    if not jadx or not Path(jadx).exists():
        _log(f"[WARN] jadx 未找到 ({jadx!r})，跳过反编译")
        return 2
    try:
        with open("/dev/null", "wb") as devnull:
            r = subprocess.run(
                [jadx, "-d", str(out_dir), "--no-res", str(apk)],
                stdout=devnull, stderr=devnull, timeout=600,
            )
        # [FLOWFIX 2026-08-30] jadx 即使反编译部分失败也会 exit 3；只要产物生成就视为成功。
        # 产物数 = sources/**/*.java 数量。
        try:
            java_count = sum(1 for _ in out_dir.rglob("*.java"))
        except OSError:
            java_count = 0
        if java_count > 100 and r.returncode != 0:
            _log(f"[INFO] jadx 退出码={r.returncode}（部分 class 反编译失败），但产物={java_count} 个 .java → 视为成功")
            return 0
        return r.returncode
    except subprocess.TimeoutExpired:
        _log("[WARN] jadx 超时（>600s）")
        return 3
    except FileNotFoundError as e:
        _log(f"[WARN] jadx 执行失败: {e}")
        return 4


def scan_sdks(apk: Path, out_file: Path) -> int:
    """扫描 APK 内第三方 SDK 痕迹（粗略：按类名前缀 + AndroidManifest 组件）。"""
    if not apk.exists():
        return 1
    sdks = {
        "Unity LevelPlay": ["com/unity3d/ads-mediation/"],
        "Vungle": ["vungle/"],
        "AdQuality": ["adquality/"],
        "IAB OM SDK": ["omid_session"],
        "iads Unity": ["assets/iads/"],
        "Google Play ads": ["play-services-ads"],
        "Google Play cronet": ["play-services-cronet"],
        "Google Play location": ["play-services-location"],
        "Google Play places": ["play-services-places"],
        "Google Play tasks": ["play-services-tasks"],
        "Google Sign-In": ["common_google_signin_btn"],
        "Firebase": ["firebase-encoders", "com/google/firebase"],
        "Google Play Billing": ["com/android/billingclient"],
        "Unity IAP": ["com/unity/purchasing"],
        "Unity Game Services": ["UnityServicesProjectConfiguration"],
        "AppLovin": ["applovin"],
        "IronSource": ["ironsource"],
        "AppsFlyer": ["appsflyer"],
        "Adjust": ["adjust"],
        "Tencent Bugly": ["bugly"],
        "Facebook SDK": ["com/facebook"],
        "Branch": ["branch.io"],
        "Kochava": ["kochava"],
        "OneTrust": ["onetrust"],
        "Crashlytics": ["crashlytics"],
        "PairIP": ["com/pairip"],
    }
    found: list[str] = []
    try:
        with zipfile.ZipFile(apk) as z:
            text = "\n".join(z.namelist())
            for name, sigs in sdks.items():
                if any(sig.lower() in text.lower() for sig in sigs):
                    found.append(name)
    except (zipfile.BadZipFile, OSError):
        return 2
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text("\n".join(found) + ("\n" if found else ""))
    return 0


def extract_native_assets(apk: Path, out_dir: Path, type_: str) -> list[str]:
    """type-specific：il2cpp 抽 libil2cpp.so + global-metadata.dat 等。"""
    if type_ not in TYPE_NATIVE_ASSETS:
        return []
    out_dir.mkdir(parents=True, exist_ok=True)
    extracted = []
    patterns = TYPE_NATIVE_ASSETS[type_]
    try:
        with zipfile.ZipFile(apk) as z:
            for n in z.namelist():
                for pat in patterns:
                    if re.search(pat, n):
                        # 安全文件名（去 lib/<abi>/ 前缀）
                        safe = re.sub(r"^lib/[^/]+/", "lib/", n).replace("/", "__")
                        target = out_dir / safe
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(z.read(n))
                        extracted.append(n)
                        break
    except (zipfile.BadZipFile, OSError):
        return []
    return extracted


def locate_entry(apk: Path, out_file: Path) -> dict:
    """从 AndroidManifest.xml (二进制) 读 package + MainActivity。

    注：二进制 AndroidManifest.xml 需 aapt / aapt2 才能解。简化处理：直接读 APK 的 manifest.json
    （xapk 提供）或从 jadx 输出里找 com.unity3d.player.UnityPlayerActivity。
    """
    info = {"package": "", "main_activity": "", "application": "", "sdk_int_min": "", "sdk_int_target": ""}
    # 优先从 APK 内的 xapk manifest.json 读 package（但 xapk manifest.json 只在外层）
    # 简化：aapt2 dump
    aapt2 = os.environ.get("AAPT2", "").strip() or shutil.which("aapt2")
    if aapt2 and apk.exists():
        try:
            r = subprocess.run(
                [aapt2, "dump", "badging", str(apk)],
                capture_output=True, text=True, timeout=60,
            )
            if r.returncode == 0:
                for line in (r.stdout or "").splitlines():
                    if line.startswith("package:"):
                        m = re.search(r"name='([^']+)'", line)
                        if m:
                            info["package"] = m.group(1)
                    elif line.startswith("sdkVersion:"):
                        info["sdk_int_min"] = line.split(":", 1)[1].strip()
                    elif line.startswith("targetSdkVersion:"):
                        info["sdk_int_target"] = line.split(":", 1)[1].strip()
                    elif line.startswith("launchable-activity:"):
                        m = re.search(r"name='([^']+)'", line)
                        if m:
                            info["main_activity"] = m.group(1)
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(
        "# original-entry-analysis.md\n\n"
        f"- **package**: {info['package'] or '(unknown)'}\n"
        f"- **main_activity**: {info['main_activity'] or '(unknown)'}\n"
        f"- **min_sdk**: {info['sdk_int_min'] or '(unknown)'}\n"
        f"- **target_sdk**: {info['sdk_int_target'] or '(unknown)'}\n"
    )
    return info


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "android").strip()
    apk_env = os.environ.get("APK", "").strip()
    if not name:
        print("[ERROR] 需要 NAME 环境变量", file=sys.stderr)
        return 2

    project_dir = ROOT / "crackings" / type_ / name
    project_dir.mkdir(parents=True, exist_ok=True)

    # 解析 APK（优先 fat APK 在 raw/<name>.apk，否则 apks/<原文件>）
    apk: Path | None = None
    if apk_env:
        apk = Path(apk_env).resolve()
    else:
        fat = project_dir / "raw" / f"{name}.apk"
        if fat.exists():
            apk = fat
        else:
            # 回退到 apks/<原>.apk
            for cand in (ROOT / "apks").glob(f"*{name}*"):
                if cand.suffix.lower() in (".apk", ".xapk"):
                    apk = cand.resolve()
                    break
    if not apk or not apk.exists():
        print(f"[ERROR] 找不到 APK: name={name} apk_env={apk_env}", file=sys.stderr)
        return 3

    _log(f"APK = {apk} | type = {type_} | name = {name}")

    raw = project_dir / "raw"
    jadx_dir = raw / "03-jadx" / "sources"
    findings_dir = project_dir / "04-findings"
    native_dir = raw / "03-static-analyze" / "native"
    entry_file = raw / "03-static-analyze" / "original-entry-analysis.md"

    # 1. jadx 反编译（不阻塞，非关键）
    jadx_rc = run_jadx(apk, jadx_dir)
    _log(f"jadx rc={jadx_rc} → {jadx_dir}")

    # 2. SDK 扫描
    sdks_file = findings_dir / "sdks_found.txt"
    scan_sdks(apk, sdks_file)
    _log(f"SDKs → {sdks_file}")

    # 3. 入口定位
    info = locate_entry(apk, entry_file)
    _log(f"entry → {entry_file}  pkg={info['package']} main={info['main_activity']}")

    # 4. type-specific native 提取（il2cpp 抽 libil2cpp.so + metadata.dat）
    if type_ in TYPE_NATIVE_ASSETS:
        extracted = extract_native_assets(apk, native_dir, type_)
        _log(f"native assets extracted → {native_dir}: {len(extracted)} files")

    # 写 summary.json（给后续阶段用）
    summary = {
        "name": name,
        "type": type_,
        "apk": str(apk.relative_to(ROOT)),
        "package": info.get("package", ""),
        "main_activity": info.get("main_activity", ""),
        "min_sdk": info.get("sdk_int_min", ""),
        "target_sdk": info.get("sdk_int_target", ""),
        "jadx_dir": str(jadx_dir.relative_to(ROOT)) if jadx_dir.exists() else "",
        "sdks_found_file": str(sdks_file.relative_to(ROOT)),
    }
    (project_dir / "static-analyze-summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False)
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())