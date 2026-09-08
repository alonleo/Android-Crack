#!/usr/bin/env python3
"""stub-applovin-consent.py — 移除 AppLovin MAX 隐私/同意弹窗（smali 桩化）。

背景: FlyingGorillaEndlessRunner (2026-08-02) 启动弹 "AppLovin MAX Terms and
Privacy Policy Flow" 同意/隐私政策弹窗。根因: `AppLovinSdk.initializeSdk()` 在
`AppLovinPrivacySettings.isUserConsentSet()==false` 时显示 CMP/TOS-PP 弹窗。

方案（双保险，smali 桩化而非删除类——C# libil2cpp 引用 AppLovin 类时物理删除会崩）:
  1. `com.applovin.sdk.AppLovinPrivacySettings.{isUserConsentSet, hasUserConsent}`
     （含 Context 变体，共 4 方法）→ return true（默认已同意 → 跳过整个流程）
  2. `com.applovin.impl.privacy.cmp.CmpServiceImpl.{showCmp, showCmpForExistingUser}`
     → no-op（即使 consent 逻辑被绕过也直接不显示 CMP 弹窗）

用法:
  python3 stub-applovin-consent.py <apktool_smali_root>
  # 例: python3 stub-applovin-consent.py crackings/<Name>/raw/01-apktool

输出:
  - 就地修改 smali 文件
  - 打印每个被桩化的方法

注意:
  - 依赖 smali 目录结构（apktool 解包产物：smali_classesN/com/applovin/...）
  - 桩化后需重新走 inject-smali-dex.py --force 或 convert-smali-to-jars.py 生效
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# 桩化为 return true 的方法签名（AppLovinPrivacySettings）
CONSENT_TRUE_METHODS = [
    ".method public static isUserConsentSet()Z",
    ".method public static isUserConsentSet(Landroid/content/Context;)Z",
    ".method public static hasUserConsent()Z",
    ".method public static hasUserConsent(Landroid/content/Context;)Z",
]

# 桩化为 no-op 的方法签名（CmpServiceImpl）
CMP_NOOP_METHODS = [
    ".method public showCmp(Landroid/app/Activity;Lcom/applovin/impl/privacy/cmp/CmpServiceImpl$f;)V",
    ".method public showCmpForExistingUser(Landroid/app/Activity;Lcom/applovin/sdk/AppLovinCmpService$OnCompletedListener;)V",
]

# ⭐ 桩化为 no-op 的弹窗显示方法（TOS/PP AlertDialog，a1 类）
# [FLOWFIX] consent public API 会被 SDK 内部状态检查绕过（"Has User Consent - No value set"），
# 必须直接桩化弹窗显示类才能 100% 阻止。logcat "kfzzs=activityName=android.app.AlertDialog" 定位。
DIALOG_NOOP_METHODS = [
    ".method public a(Landroid/app/Activity;Lcom/applovin/impl/v0$c;)V",
    ".method public a(ILandroid/app/Activity;Lcom/applovin/impl/v0$c;)V",
]

STUB_TRUE_TEMPLATE = (
    "{sig}\n"
    "    .locals 1\n\n"
    "    # === STUBBED by stub-applovin-consent.py: 默认已同意，跳过 AppLovin 隐私/TOS 弹窗 ===\n"
    "    const/4 v0, 0x1\n\n"
    "    return v0\n"
    ".end method"
)

STUB_NOOP_TEMPLATE = (
    "{sig}\n"
    "    .locals 2\n\n"
    "    # === STUBBED by stub-applovin-consent.py: 跳过 CMP 同意弹窗 ===\n"
    "    const-string v0, \"AppLovinSdk\"\n\n"
    "    const-string v1, \"STUB: CMP consent dialog skipped\"\n\n"
    "    invoke-static {{v0, v1}}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I\n\n"
    "    return-void\n"
    ".end method"
)


def _find_smali_files(smali_root: Path, rel: str) -> list[Path]:
    """在所有 smali_classesN 下找指定相对路径的 .smali。"""
    hits = []
    for d in sorted(smali_root.glob("smali*")):
        if not d.is_dir():
            continue
        f = d / rel
        if f.is_file():
            hits.append(f)
    return hits


def _replace_method(text: str, sig: str, template: str) -> tuple[str, bool]:
    start = text.find(sig)
    if start < 0:
        return text, False
    end = text.find(".end method", start)
    if end < 0:
        print(f"  [ERROR] 无 .end method: {sig}")
        return text, False
    end += len(".end method")
    new_body = template.format(sig=sig)
    return text[:start] + new_body + text[end:], True


def stub_privacy_settings(smali_root: Path) -> int:
    """桩化 AppLovinPrivacySettings → return true。返回处理文件数。"""
    files = _find_smali_files(smali_root, "com/applovin/sdk/AppLovinPrivacySettings.smali")
    if not files:
        print("[WARN] 未找到 AppLovinPrivacySettings.smali")
        return 0
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        changed = 0
        for sig in CONSENT_TRUE_METHODS:
            text, ok = _replace_method(text, sig, STUB_TRUE_TEMPLATE)
            if ok:
                print(f"  [OK] {f} :: {sig.split('(')[0]}")
                changed += 1
        if changed:
            f.write_text(text, encoding="utf-8")
            total += 1
    return total


def stub_cmp_service(smali_root: Path) -> int:
    """桩化 CmpServiceImpl → no-op。返回处理文件数。"""
    files = _find_smali_files(smali_root, "com/applovin/impl/privacy/cmp/CmpServiceImpl.smali")
    if not files:
        print("[WARN] 未找到 CmpServiceImpl.smali")
        return 0
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        changed = 0
        for sig in CMP_NOOP_METHODS:
            text, ok = _replace_method(text, sig, STUB_NOOP_TEMPLATE)
            if ok:
                print(f"  [OK] {f} :: {sig.split('(')[0]}")
                changed += 1
        if changed:
            f.write_text(text, encoding="utf-8")
            total += 1
    return total


def stub_dialog_shower(smali_root: Path) -> int:
    """桩化 TOS/PP 弹窗显示类 a1 → no-op（关键，SDK 内部 consent 绕过 public API）。

    [FLOWFIX] consent public API 桩化可能被 SDK 内部状态检查绕过，
    必须直接桩化弹窗显示类。定位: logcat "kfzzs=activityName=android.app.AlertDialog"。
    """
    files = _find_smali_files(smali_root, "com/applovin/impl/a1.smali")
    if not files:
        print("[WARN] 未找到 com/applovin/impl/a1.smali（TOS/PP 弹窗显示类）")
        return 0
    total = 0
    for f in files:
        text = f.read_text(encoding="utf-8")
        changed = 0
        for sig in DIALOG_NOOP_METHODS:
            text, ok = _replace_method(text, sig, STUB_NOOP_TEMPLATE)
            if ok:
                print(f"  [OK] {f} :: {sig.split('(')[0]} (TOS/PP dialog)")
                changed += 1
        if changed:
            f.write_text(text, encoding="utf-8")
            total += 1
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description="移除 AppLovin MAX 隐私/同意弹窗（smali 桩化）")
    parser.add_argument("smali_root", help="apktool 解包根目录（含 smali_classesN/）")
    args = parser.parse_args()

    root = Path(args.smali_root)
    if not root.is_dir():
        print(f"[ERROR] 目录不存在: {root}")
        return 1

    n1 = stub_privacy_settings(root)
    n2 = stub_cmp_service(root)
    n3 = stub_dialog_shower(root)
    print(f"[OK] 桩化完成: AppLovinPrivacySettings {n1} / CmpServiceImpl {n2} / TOS-PP dialog a1 {n3}")
    print("[INFO] 桩化后需重跑 inject-smali-dex.py --force 或 convert-smali-to-jars.py 生效")
    return 0 if (n1 or n2 or n3) else 1


if __name__ == "__main__":
    raise SystemExit(main())
