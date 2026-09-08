#!/usr/bin/env python3
"""extract-gdpr-hooks.py — 从 Il2CppDumper 的 dump.cs 提取 GDPR/consent 相关函数 RVA，
    并生成可注入 native-lib.cpp 的 A64HookFunction hook 片段。

处理 Unity il2cpp 启动时弹出 GDPR/Privacy Consent 弹窗
（Unity Ads 内置 ConsentPopup / GDPRController，文案 "We use device identifiers..."）。

原理：
- 弹窗由 C# 层 GDPRController.CheckForGDPR() / ConsentPopup 触发
- 若 GDPRConsentWasSet() 返回 true（已同意）→ 弹窗逻辑跳过
- 故 hook 这些函数，让"是否已同意"恒返 true / 弹窗入口 no-op / 广告关闭

用法:
    python3 skills/common/scripts/extract-gdpr-hooks.py \
        --dump crackings/<type>/<name>/stages/03-fn-analyze/step1-signatures/dump/dump.cs \
        [--out /tmp/gdpr-hooks.md]     # 输出 hook 片段（markdown/文本）

输出:
    每个 GDPR 关键函数的 RVA + 建议 Hooked 签名，可直接粘贴到 native-lib.cpp setupHooks()。

依赖:
    - dump.cs（Il2CppDumper 产物，含 "// RVA: 0x..." 注释）
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


# 目标方法 → {说明, 返回类型, 参数, 返回值(bool)}
TARGETS = {
    "GDPRConsentWasSet": {"note": "已同意 → 恒返 true（弹窗不显示）", "ret": "bool", "params": "", "val": "true"},
    "CheckForGDPR": {"note": "弹窗入口 → no-op", "ret": "void", "params": "void*", "val": ""},
    "CanShowAds": {"note": "广告开关 → 恒返 false", "ret": "bool", "params": "", "val": "false"},
    "SetGDPRConsent": {"note": "写入同意 → no-op", "ret": "void", "params": "bool", "val": ""},
    "CCPAConsentWasSet": {"note": "CCPA 已同意 → 恒返 true", "ret": "bool", "params": "", "val": "true"},
    "ShowBuiltInConsentPopup": {"note": "内置弹窗 → no-op", "ret": "void", "params": "void*", "val": ""},
    "HasBuiltInConsentWindow": {"note": "内置弹窗存在 → 恒返 false", "ret": "bool", "params": "", "val": "false"},
}


def extract_rvas(dump_path: Path) -> list[dict]:
    """从 dump.cs 提取各目标方法第一个 static 可见的 RVA（优先 static，因 instance 需 this）。"""
    lines = dump_path.read_text(encoding="utf-8", errors="ignore").splitlines()
    found: dict[str, dict] = {}
    for i, line in enumerate(lines):
        m = re.search(r"// RVA: (0x[0-9A-Fa-f]+)", line)
        if not m:
            continue
        rva = m.group(1)
        for j in range(i + 1, min(i + 4, len(lines))):
            sig = lines[j].strip()
            if not sig or sig.startswith("//"):
                continue
            for name, meta in TARGETS.items():
                if re.search(r"\b" + name + r"\b", sig):
                    is_static = "static" in sig.split("//")[0]
                    if name not in found:
                        found[name] = {
                            "name": name, "rva": rva,
                            "sig": sig.split("//")[0].strip(),
                            "static": is_static, **meta,
                        }
                    elif is_static and not found[name]["static"]:
                        found[name] = {
                            "name": name, "rva": rva,
                            "sig": sig.split("//")[0].strip(),
                            "static": True, **meta,
                        }
                    break
            break
    return [found[n] for n in TARGETS if n in found]


def gen_hook_fragment(entries: list[dict]) -> str:
    """生成 native-lib.cpp 的 hook 片段。"""
    lines = []
    lines.append("// === GDPR/consent 弹窗 hook（默认已同意，弹窗不显示）===")
    for e in entries:
        name = e["name"]
        ret = e["ret"]
        params = e["params"]
        rva = e["rva"]

        if ret == "bool":
            val = e.get("val", "true")
            hooked = f"""// {name}() {e['note']}
static bool (*orig_{name})();
extern "C" bool Hooked_{name}({params}) {{
    LOGI("[hook] {name} → return {val}");
    return {val};
}}"""
        else:  # void
            hooked = f"""// {name}() {e['note']}
static void (*orig_{name})({params});
extern "C" void Hooked_{name}({params}) {{
    LOGI("[hook] {name} → no-op (skip popup)");
}}"""
        lines.append(hooked)
        lines.append("")

    lines.append("// === 在 setupHooks() 注册 ===")
    for e in entries:
        name = e["name"]
        rva = e["rva"]
        lines.append(f"""    {{
        void* target = (void*)(baseAddr + {rva});
        A64HookFunction(target, (void*)Hooked_{name}, (void**)&orig_{name});
        LOGI("[hook] Hooked_{name} installed @ 0x%x", (unsigned)(uintptr_t)target);
    }}""")
        lines.append("")

    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="提取 GDPR/consent hook RVA 并生成 native-lib.cpp 片段")
    p.add_argument("--dump", required=True, help="dump.cs 路径")
    p.add_argument("--out", help="输出文件（默认 stdout）")
    args = p.parse_args()

    dump = Path(args.dump)
    if not dump.is_file():
        sys.exit(f"[ERR] dump.cs 不存在: {dump}")

    entries = extract_rvas(dump)
    if not entries:
        sys.exit(f"[WARN] 未在 dump.cs 找到 GDPR/consent 相关函数: {dump}")

    frag = gen_hook_fragment(entries)
    delim = "#" * 60
    header = f"""# GDPR/consent 弹窗 hook 片段（{dump.name}）
# 来源: extract-gdpr-hooks.py
# 用法: 将以下代码粘贴到 app/src/main/cpp/native-lib.cpp
#       - 函数定义放到 setupHooks() 之前
#       - 注册块放入 setupHooks() 内 "Hook Engine Initialized" 之前

{delim}
# 提取到的 GDPR 函数（RVA）
{delim}
"""
    body_lines = [f"| {e['name']} | {e['rva']} | {'static' if e['static'] else 'instance'} | {e['sig']} | {e['note']} |"
                  for e in entries]
    result = header + "\n".join(body_lines) + "\n\n" + frag

    if args.out:
        Path(args.out).write_text(result, encoding="utf-8")
        print(f"[OK] 写入 {args.out}（提取 {len(entries)} 个 GDPR 函数）")
    else:
        print(result)
    return 0


if __name__ == "__main__":
    sys.exit(main())