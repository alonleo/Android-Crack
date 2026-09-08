#!/usr/bin/env python3
"""
analyze-hook-points.py — il2cpp Hook 点启发式分析

当 Il2CppDumper 因 metadata 版本过新无法生成 dump.cs 时，
用 MonoScript 类名 + metadata 字符串做启发式匹配，输出结构化候选报告。

用法:
  python3 analyze-hook-points.py <Name>                     # 自动从 crackings/<Name>/ 读取数据
  python3 analyze-hook-points.py <Name> --output <path>     # 指定输出路径

依赖:
  - crackings/<Name>/raw/05-strings/mono_scripts_classes.txt
  - crackings/<Name>/raw/05-strings/metadata-strings.txt

产出:
  crackings/<Name>/stages/04b-hook-analysis/il2cpp-hook-points.md
"""
import sys, os, re
from pathlib import Path

REPO = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(REPO / "tools" / "scripts" / "lib"))
import common

HOOK_PATTERNS = {
    "IAP/购买": [
        r"Purchase.*Initiate", r"Purchase.*Confirm", r"ProcessPurchase",
        r"OnPurchase(Failed|Succeeded)", r"BillingClient", r"BillingResult",
        r"ConsumePurchase", r"AcknowledgePurchase", r"StoreController",
        r"IStoreListener", r"GooglePurchase", r"InAppPurchase",
    ],
    "广告": [
        r"IronSource", r"LevelPlay", r"UnityAds", r"Reward.*Video",
        r"ShowReward", r"LoadReward", r"OnAdRewarded", r"OnAdLoaded",
        r"OnAdFailed", r"Interstitial", r"ShowAd", r"LoadAd",
        r"AppLovin", r"MaxSdk", r"AudienceNetwork",
    ],
    "Premium/Pro": [
        r"Premium", r"VIP", r"Subscription", r"RemoveAd", r"NoAd",
    ],
    "本地化/语言": [
        r"Localiz", r"Translate", r"GetText", r"SetText",
        r"Localize", r"FormatString",
    ],
    "Unity 文本": [
        r"set_text", r"TextMeshProUGUI", r"TextMeshPro\b",
        r"UnityEngine\.UI\.Text",
    ],
    "SDK 回调": [
        r"FacebookInit", r"FacebookLog", r"AppsFlyer",
        r"TrackEvent", r"Analytics",
    ],
    "反调试/安全": [
        r"AntiDebug", r"RootDetect", r"SafetyNet",
        r"Signature.*Verify", r"CheckIntegrity",
    ],
}


def find_hook_points(mono_classes_path, metadata_strings_path):
    classes = []
    with open(mono_classes_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                classes.append(line)
    common.log_info(f"MonoScript 类: {len(classes)}")

    meta_strings = []
    with open(metadata_strings_path, errors="replace") as f:
        for line in f:
            s = line.strip()
            if s:
                meta_strings.append(s)
    common.log_info(f"metadata 字符串: {len(meta_strings)}")

    results = {cat: [] for cat in HOOK_PATTERNS}
    seen = {cat: set() for cat in HOOK_PATTERNS}

    for c in sorted(classes):
        for cat, patterns in HOOK_PATTERNS.items():
            for p in patterns:
                if re.search(p, c, re.IGNORECASE):
                    if c not in seen[cat]:
                        seen[cat].add(c)
                        results[cat].append({"name": c, "source": "class"})
                    break

    for s in meta_strings:
        if not s[0].isupper():
            continue
        for cat, patterns in HOOK_PATTERNS.items():
            for p in patterns:
                if re.search(p, s, re.IGNORECASE):
                    if s not in seen[cat]:
                        seen[cat].add(s)
                        results[cat].append({"name": s, "source": "string"})
                    break

    for cat in results:
        seen_dedup = set()
        results[cat] = [r for r in results[cat] if r["name"] not in seen_dedup and not seen_dedup.add(r["name"])]

    return results


def write_report(name, results, output_path):
    lines = [f"# Il2Cpp Hook 点分析报告 — {name}"]
    lines.append(f"\n> 模式: **heuristic**")
    lines.append(f"> 日期: {common.now_iso()}")

    lines.append("\n## 汇总\n")
    lines.append("| 类别 | 候选数 |")
    lines.append("|------|--------|")
    total = 0
    for cat in HOOK_PATTERNS:
        c = len(results[cat])
        total += c
        lines.append(f"| {cat} | {c} |")
    lines.append(f"| **合计** | **{total}** |\n")

    for cat in HOOK_PATTERNS:
        items = results[cat]
        if not items:
            continue
        lines.append(f"\n## {cat}（{len(items)} 个候选）\n")
        lines.append("| 来源 | 名称 |")
        lines.append("|------|------|")
        for item in items[:80]:
            lines.append(f"| {item['source']} | `{item['name']}` |")
        if len(items) > 80:
            lines.append(f"| ... | 还有 {len(items) - 80} 个 |")

    with open(output_path, "w") as f:
        f.write("\n".join(lines))
    common.log_success(f"报告: {output_path}")
    return output_path


def main():
    if len(sys.argv) < 2:
        print("用法: python3 analyze-hook-points.py <Name> [--output <path>]")
        sys.exit(1)

    name = sys.argv[1]
    common.setup_paths_from_name(name)
    common.require_crack_dir()

    mono_classes = os.path.join(common.out_dir(), "05-strings", "mono_scripts_classes.txt")
    meta_strings = os.path.join(common.out_dir(), "05-strings", "metadata-strings.txt")
    for f in [mono_classes, meta_strings]:
        common.require_file(f)

    results = find_hook_points(mono_classes, meta_strings)

    if "--output" in sys.argv:
        idx = sys.argv.index("--output")
        output_path = sys.argv[idx + 1]
        common.ensure_dir(os.path.dirname(output_path))
    else:
        output_dir = common.stage_dir("04b", "hook-analysis")
        output_path = os.path.join(output_dir, "il2cpp-hook-points.md")

    write_report(name, results, output_path)
    print(f"\n候选总计: {sum(len(v) for v in results.values())}")
    print(f"详情: {output_path}")


if __name__ == "__main__":
    main()
