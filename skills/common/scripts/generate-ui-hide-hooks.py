#!/usr/bin/env python3
"""generate-ui-hide-hooks.py — 生成 UIElements 按钮隐藏 hook 代码（native-lib.cpp）。

背景: FlyingGorillaEndlessRunner (2026-08-02) 隐藏 HUD 里 Settings 同级的 Achievements/Skin
按钮。按钮是 UIElements（非 MonoBehaviour），stage-13 的 HookedBehaviour_set_isActiveAndEnabled
不适用。本脚本生成 native hook 代码：
  - 显示: Hook 宿主方法 → 读按钮字段 → VisualElement::RemoveFromHierarchy() 彻底移除
    （set_visible(false) 只隐藏不释放布局，会留空隙）
    两种 hook 点: --host-update-rva（有 Update 的类，每帧移除）/ --host-trigger-rva（无 Update 的类，
    用 UI 出现时的触发方法如 ShowResultShell，一次性移除）
  - 调用链: Hook 按钮 click handler → return 切断

用法:
  python3 generate-ui-hide-hooks.py \
      --host-class CityHudRoot --host-update-rva 02B9D194 \
      --remove-from-hierarchy-rva 05AB1E80 \
      --button "achievements:3B0:02BD5694" \
      --button "skin:3B8:02BD6A2C" \
      -o /tmp/ui-hide-hooks.txt

参数 --button 格式: <name>:<field_offset_hex>:<click_handler_rva_hex>
  name        日志用名（如 achievements）
  field_offset 宿主类里按钮字段的 il2cpp 对象偏移（dump.cs 的 // 0x3B0）
  click_rva   点击 handler 的 RVA（hook 后 return 切断调用链）
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path


def generate(host: str, hook_rva: str, hook_name: str, remove_rva: str,
             buttons: list[tuple[str, str, str]]) -> str:
    """hook_rva/hook_name: 显示移除的 hook 点。
    - Update 模式: hook_rva=Update RVA, hook_name='Update'（每帧）
    - 触发方法模式: hook_rva=ShowResultShell 等 RVA, hook_name='ShowResultShell'（UI 出现时一次性）
      （非 Update 类，如 GameplayHudRoot 没有 Update 时用）
    """
    lines = []
    lines.append(f"// === UIElements 按钮隐藏 hook（{host}）===")
    lines.append("// 生成自 generate-ui-hide-hooks.py")
    lines.append("")

    # 1) 调用链切断（每个按钮一个）
    for name, _, click_rva in buttons:
        lines.append(f"static void (*orig_Handle_{name})(void* __this);")
        lines.append(f"static void HookedHandle_{name}(void* __this) {{")
        lines.append(f"    LOGI(\"[ui-hide] {name} button click BLOCKED\");")
        lines.append("    return; // 切断调用链")
        lines.append("}")
    lines.append("")

    # 2) 显示移除 hook（RemoveFromHierarchy）
    lines.append("static uintptr_t g_base = 0;")
    lines.append("static bool g_ui_hide_logged = false;")
    lines.append(f"static void (*orig_{host}_{hook_name})(void* __this);")
    lines.append(f"static void Hooked{host}_{hook_name}(void* __this) {{")
    lines.append(f"    if (orig_{host}_{hook_name}) orig_{host}_{hook_name}(__this);")
    lines.append(f"    void (*RemoveFromHierarchy)(void*) = (void (*)(void*))(g_base + 0x{remove_rva});")
    for name, field, _ in buttons:
        lines.append(f"    void* {name}Btn = *(void**)((char*)__this + 0x{field});")
        lines.append(f"    if ({name}Btn && RemoveFromHierarchy) RemoveFromHierarchy({name}Btn);")
    cond = " || ".join(f"{n}Btn" for n, _, _ in buttons)
    lines.append(f"    if (({cond}) && !g_ui_hide_logged) {{")
    names = "/".join(n for n, _, _ in buttons)
    lines.append(f"        LOGI(\"[ui-hide] {names} buttons removed from hierarchy (once)\");")
    lines.append("        g_ui_hide_logged = true;")
    lines.append("    }")
    lines.append("}")
    lines.append("")

    # 3) setupHooks 注入块
    lines.append("// === 在 setupHooks() 中追加 ===//")
    for name, _, click_rva in buttons:
        lines.append(f"    A64HookFunction((void*)(baseAddr + 0x{click_rva}),")
        lines.append(f"                    (void*)HookedHandle_{name},")
        lines.append(f"                    (void**)&orig_Handle_{name});")
    lines.append(f"    A64HookFunction((void*)(baseAddr + 0x{hook_rva}),")
    lines.append(f"                    (void*)Hooked{host}_{hook_name},")
    lines.append(f"                    (void**)&orig_{host}_{hook_name});")
    lines.append(f"    LOGI(\"[ui-hide] {host} button hooks installed (display via {hook_name})\");")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="生成 UIElements 按钮隐藏 hook 代码")
    parser.add_argument("--host-class", required=True, help="宿主 MonoBehaviour 类名")
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--host-update-rva", help="宿主 Update 方法 RVA (hex)，每帧移除（有 Update 的类）")
    g.add_argument("--host-trigger-rva", help="宿主触发方法 RVA (hex)，如 ShowResultShell（无 Update 的类，UI 出现时一次性移除）")
    parser.add_argument("--trigger-name", default="Trigger",
                        help="--host-trigger-rva 时的方法名（用于生成 hook 函数名，默认 Trigger）")
    parser.add_argument("--remove-from-hierarchy-rva", required=True, default="05AB1E80",
                        help="VisualElement::RemoveFromHierarchy RVA (hex)")
    parser.add_argument("--button", action="append", required=True,
                        help="name:field_offset_hex:click_handler_rva_hex，可多次")
    parser.add_argument("-o", "--out", default=None, help="输出文件（缺省 stdout）")
    args = parser.parse_args()

    buttons = []
    for b in args.button:
        parts = b.split(":")
        if len(parts) != 3:
            print(f"[ERROR] --button 格式错误: {b}（应为 name:field:click_rva）")
            return 1
        buttons.append((parts[0], parts[1].lower(), parts[2].lower()))

    if args.host_update_rva:
        hook_rva, hook_name = args.host_update_rva.lower(), "Update"
    else:
        hook_rva, hook_name = args.host_trigger_rva.lower(), args.trigger_name

    code = generate(args.host_class, hook_rva, hook_name,
                    args.remove_from_hierarchy_rva.lower(), buttons)
    if args.out:
        Path(args.out).write_text(code, encoding="utf-8")
        print(f"[OK] 已写入 {args.out}")
    else:
        print(code)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
