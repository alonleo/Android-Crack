#!/usr/bin/env python3
"""sub-stage-assess.py — 难度评估主阶段（M2）子脚本。

[FLOWFIX 2026-08-30] 原脚本长期缺失；routing.py 找不到 common fallback。
按 STRATEGY.md §2.2 6 维度加权评分（满分 100）→ grade S/A/B/C/D/F + 推荐流水线。

用法：
    python3 sub-stage-assess.py
    # 依赖环境变量 NAME + TYPE；缺一会退出非 0
    NAME=ViragoHerstory112 TYPE=il2cpp python3 sub-stage-assess.py

输出：
    - crackings/<type>/<Name>/difficulty.json（机器可读：6 维度 + grade + recommended_stages）
    - crackings/<type>/<Name>/raw/assessment.md（人类可读）

6 维度评分：
    1. 代码复杂度 (type-driven): 20
    2. 代码体积: 15
    3. 加密/加固: 25
    4. 反调试: 15
    5. 第三方 SDK 数: 10
    6. 运行时约束: 15
"""
from __future__ import annotations

import json
import os
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

# type → 代码复杂度（满分 20）
CODE_COMPLEXITY = {
    "android": 5,
    "unity-mono": 10,
    "air": 14,
    "il2cpp": 16,        # 中间值，metadata 不强加密 +14；强加密 +18
    "cocos2dx": 16,
    "cocos-creator": 15,
    "unreal": 18,
    "flutter": 15,
    "xamarin": 12,
    "libgdx": 8,
    "defold": 10,
    "gamemaker": 10,
    "corona": 10,
    "unknown": 15,
}


def score_code_volume(apk_path: Path) -> tuple[int, str]:
    """评分依据：<30 MB(3) / 30-80 MB(7) / 80-200 MB(11) / >200 MB(15)"""
    if not apk_path.exists():
        return 0, "apk 不存在"
    size_mb = apk_path.stat().st_size / (1024 * 1024)
    if size_mb < 30:
        return 3, f"{size_mb:.1f}MB (<30MB)"
    if size_mb < 80:
        return 7, f"{size_mb:.1f}MB (30-80MB)"
    if size_mb < 200:
        return 11, f"{size_mb:.1f}MB (80-200MB)"
    return 15, f"{size_mb:.1f}MB (>200MB)"


def score_encryption(apk_path: Path) -> tuple[int, list[str]]:
    """检测 il2cpp metadata 缺失 / 加固特征 / PairIP。"""
    notes = []
    score = 0
    if not apk_path.exists():
        return 0, ["apk 不存在"]
    try:
        with zipfile.ZipFile(apk_path) as z:
            names = z.namelist()
            text = "\n".join(names)
            # PairIP（com/pairip + libpairipcore.so）：强签名绑定，重签必崩，只能 LSPosed
            if "com/pairip" in text and "libpairipcore.so" in text:
                score = 20
                notes.append("PairIP 绑定签名（重签必崩）")
                return score, notes
            # il2cpp metadata 缺失
            if "global-metadata.dat" not in text and any("libil2cpp.so" in n for n in names):
                score = 18
                notes.append("il2cpp metadata 缺失（加密）")
                return score, notes
            # 加固特征
            hardened_signals = ["com/secneo", "libDexHelper", "libsecexe", "libexecChecker", "360MobileSafe", "tencent/tp"]
            if any(s in text for s in hardened_signals):
                score = 18
                notes.append("加固特征（360/腾讯/梆梆）")
                return score, notes
            # ProGuard 强混淆（间接：smali 数少 + 类名奇短）
            if any(re.search(r"/[a-z]{1,3}/[a-z]{1,2}\.smali$", n) for n in names):
                score = 5
                notes.append("ProGuard 强混淆迹象")
                return score, notes
    except (zipfile.BadZipFile, OSError):
        notes.append("APK 读取失败")
    return score, notes


def score_anti_debug(apk_path: Path) -> tuple[int, list[str]]:
    """检测 anti-debug 字符串 + smali 检测函数 + READ_LOGS。"""
    notes = []
    score = 0
    if not apk_path.exists():
        return 0, ["apk 不存在"]
    try:
        with zipfile.ZipFile(apk_path) as z:
            names = z.namelist()
            text = "\n".join(names)
            # .so anti-debug 字符串命中（常见关键字）
            # 注：仅当 lib/ 下 .so 含 ptrace/TracerPid 字符串 → 但 strings 在 .so 里，
            # 我们只看到 .so 存在。粗略按 .so 数量计；后续静态分析时用 strings 精查。
            so_count = sum(1 for n in names if n.endswith(".so"))
            if so_count >= 5:
                score += 5
                notes.append(f"含 {so_count} 个 .so（待 strings 精查 anti-debug）")
            elif so_count >= 1:
                score += 3
                notes.append(f"含 {so_count} 个 .so")
            # READ_LOGS 权限（间接信号）
            # 注：apk 解压后无 AndroidManifest.xml 的明文，需 aapt；这里跳过
    except (zipfile.BadZipFile, OSError):
        notes.append("APK 读取失败")
    return score, notes


def score_third_party_sdks(apk_path: Path) -> tuple[int, list[str]]:
    """第三方 SDK 数：0(0) / 1-3(3) / 4-7(6) / ≥8(10)"""
    notes = []
    score = 0
    if not apk_path.exists():
        return 0, ["apk 不存在"]
    try:
        with zipfile.ZipFile(apk_path) as z:
            text = "\n".join(z.namelist())
            # 常见 SDK 标志
            sdk_signals = {
                "Unity LevelPlay": "com/unity3d/ads-mediation/",
                "Vungle": "vungle",
                "AdQuality": "adquality",
                "IAB OM SDK": "omid",
                "iads Unity": "iads/",
                "Google Play ads": "play-services-ads",
                "Google Play cronet": "play-services-cronet",
                "Google Play location": "play-services-location",
                "Google Play places": "play-services-places",
                "Google Play tasks": "play-services-tasks",
                "Google Sign-In": "common_google_signin_btn",
                "Firebase": "firebase",
                "Google Play Billing": "com.android.billingclient",
                "Unity IAP": "com.unity.purchasing",
                "Unity Game Services": "UnityServicesProjectConfiguration",
                "AppsFlyer": "appsflyer",
                "Adjust": "adjust",
                "Tencent Bugly": "bugly",
                "AppLovin": "applovin",
                "IronSource": "ironsource",
                "Facebook SDK": "com/facebook",
                "AppsFlyer": "appsflyer",
                "Branch": "branch.io",
                "Kochava": "kochava",
                "GameAnalytics": "gameanalytics",
                "Amplitude": "amplitude",
                "Mixpanel": "mixpanel",
                "Sentry": "sentry",
                "Crashlytics": "crashlytics",
                "OneTrust": "onetrust",
                "UMP": "UserMessagingPlatform",
                "PairIP": "com/pairip",
            }
            hits = [name for name, sig in sdk_signals.items() if sig.lower() in text.lower()]
            if hits:
                notes.append(f"命中 {len(hits)} 个独立第三方包: {', '.join(hits)}")
            n = len(hits)
            if n == 0:
                score = 0
            elif n <= 3:
                score = 3
            elif n <= 7:
                score = 6
            else:
                score = 10
    except (zipfile.BadZipFile, OSError):
        notes.append("APK 读取失败")
    return score, notes


def score_runtime_constraints(apk_path: Path) -> tuple[int, list[str]]:
    """运行时约束：INTERNET(2) / 网络检测 smali(6) / 设备 ID(4) / native 协议加密(3)"""
    notes = []
    score = 0
    if not apk_path.exists():
        return 0, ["apk 不存在"]
    try:
        with zipfile.ZipFile(apk_path) as z:
            text = "\n".join(z.namelist())
            # INTERNET（粗略信号：okhttp + play-services-ads）
            if "okhttp3" in text or "play-services-ads" in text:
                score += 2
                notes.append("INTERNET 权限迹象")
            # 设备 ID（Google Play ads-identifier）
            if "play-services-ads-identifier" in text:
                score += 4
                notes.append("设备 ID（ads-identifier）")
            # native 协议加密（libil2cpp + global-metadata）
            if "libil2cpp.so" in text and "global-metadata.dat" in text:
                score += 3
                notes.append("native 协议加密（il2cpp）")
            # 网络检测 smali（暂无静态线索，需 aapt 解 AndroidManifest）
            # 这里跳过；可在 04 阶段补
    except (zipfile.BadZipFile, OSError):
        notes.append("APK 读取失败")
    return score, notes


def calc_grade(score: int) -> tuple[str, list[str]]:
    """STRATEGY.md §2.1: S≥80 / A≥60 / B≥40 / C≥20 / D≥10 / F<10"""
    if score >= 80:
        return "S", ["01-15 全跑"]
    if score >= 60:
        return "A", ["01-15 全跑"]
    if score >= 40:
        return "B", ["01-15 全跑（可跳 09）"]
    if score >= 20:
        return "C", ["精简：01-04, 08, 09, 10, 12, 14, 16"]
    if score >= 10:
        return "D", ["精简：01-04, 09, 10, 12, 14, 16"]
    return "F", ["极简：01-03, 09, 10, 14, 16"]


def main() -> int:
    name = os.environ.get("NAME", "").strip()
    type_ = os.environ.get("TYPE", "").strip()
    if not name or not type_:
        print(f"[ERROR] 需要 NAME 和 TYPE 环境变量", file=sys.stderr)
        print(f"  当前: NAME={name!r} TYPE={type_!r}", file=sys.stderr)
        return 2

    project_dir = ROOT / "crackings" / type_ / name
    raw_apk = project_dir / "raw" / f"{name}.apk"
    if not raw_apk.exists():
        # 退化：取 crackings/<type>/<name>/ 任意 *.apk
        candidates = list((project_dir / "raw").glob("*.apk"))
        if candidates:
            raw_apk = candidates[0]
        else:
            print(f"[ERROR] fat APK 不存在: {raw_apk}", file=sys.stderr)
            return 3

    # 1. 代码复杂度（type-driven）
    cc_score = CODE_COMPLEXITY.get(type_, 15)

    # 2. 代码体积
    cv_score, cv_note = score_code_volume(raw_apk)

    # 3. 加密/加固
    enc_score, enc_notes = score_encryption(raw_apk)

    # 4. 反调试
    ad_score, ad_notes = score_anti_debug(raw_apk)

    # 5. 第三方 SDK 数
    sdk_score, sdk_notes = score_third_party_sdks(raw_apk)

    # 6. 运行时约束
    rt_score, rt_notes = score_runtime_constraints(raw_apk)

    total = cc_score + cv_score + enc_score + ad_score + sdk_score + rt_score
    grade, recommended = calc_grade(total)

    # il2cpp mandatory
    mandatory = ["01", "02", "03", "04", "06", "08", "10", "12", "14", "16"]

    result = {
        "project": {"name": name, "type": type_},
        "apk_path": str(raw_apk.relative_to(ROOT)) if raw_apk.exists() else "",
        "dimensions": {
            "code_complexity": {"score": cc_score, "max": 20, "reason": f"type={type_}"},
            "code_volume":     {"score": cv_score, "max": 15, "reason": cv_note},
            "encryption":      {"score": enc_score, "max": 25, "notes": enc_notes},
            "anti_debug":      {"score": ad_score, "max": 15, "notes": ad_notes},
            "third_party_sdks":{"score": sdk_score, "max": 10, "notes": sdk_notes},
            "runtime":         {"score": rt_score, "max": 15, "notes": rt_notes},
        },
        "total_score": total,
        "max_score": 100,
        "grade": grade,
        "mandatory_stages": mandatory,
        "recommended_stages": recommended,
    }

    # 写 difficulty.json
    out_json = project_dir / "difficulty.json"
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f"[OK] {out_json} (total={total} grade={grade})")

    # 写 assessment.md（人类可读）
    out_md = project_dir / "raw" / "assessment.md"
    out_md.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Assessment — {name} ({type_})",
        "",
        f"- **总评分**: {total} / 100",
        f"- **grade**: {grade}",
        f"- **apk**: {raw_apk.name} ({cv_note})",
        f"- **推荐流水线**: {', '.join(recommended)}",
        "",
        "## 6 维度评分明细",
        "",
        f"| # | 维度 | 得分 | 满分 | 依据 |",
        f"|---|------|------|------|------|",
        f"| 1 | 代码复杂度 (type-driven) | {cc_score} | 20 | type={type_} |",
        f"| 2 | 代码体积 | {cv_score} | 15 | {cv_note} |",
        f"| 3 | 加密/加固 | {enc_score} | 25 | {'; '.join(enc_notes) or '无特征'} |",
        f"| 4 | 反调试 | {ad_score} | 15 | {'; '.join(ad_notes) or '无特征'} |",
        f"| 5 | 第三方 SDK 数 | {sdk_score} | 10 | {'; '.join(sdk_notes) or '无特征'} |",
        f"| 6 | 运行时约束 | {rt_score} | 15 | {'; '.join(rt_notes) or '无特征'} |",
        "",
        f"## il2cpp mandatory 阶段",
        "",
        ", ".join(mandatory),
        "",
    ]
    out_md.write_text("\n".join(lines))
    print(f"[OK] {out_md}")

    return 0


if __name__ == "__main__":
    sys.exit(main())