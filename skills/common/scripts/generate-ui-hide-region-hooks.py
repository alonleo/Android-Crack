#!/usr/bin/env python3
"""generate-ui-hide-region-hooks.py — 生成 UIElements 区域容器隐藏 hook（native-lib.cpp）。

背景: FlyingGorillaEndlessRunner (2026-08-02)。设置窗口区域移除——**宿主类字段引用与
显示元素是不同对象**（字段 RemoveFromHierarchy 无效），必须从 rootElement(0x140) 递归
UXML 树，找到内容容器（如 settings-scroll-view），遍历其直接子区域容器：
  - 含 keep-marker 标记元素（如 settings-bgm-slider）的区域 → **保留**
  - 其余区域 → RemoveFromHierarchy()（Gameplay/Cloud/Other/Follow/Music/版本号全移除）

与 generate-ui-hide-hooks.py（按钮字段隐藏）互补——按钮有字段偏移可读，区域无 name/字段，
只能靠树遍历 + 标记元素定位。

用法:
  python3 generate-ui-hide-region-hooks.py \
      --host-class CityHudRoot --host-update-rva 02B9D194 --root-field 0x140 \
      --scroll-view-name settings-scroll-view --keep-marker settings-bgm-slider \
      --get-name-rva 05AA8D30 --get-child-count-rva 05AB17F8 --get-item-rva 05AB177C \
      --remove-rva 05AB1E80 \
      --log-message "settings regions removed (keep Sound/BGM+SE; removed Gameplay/Cloud/Other/Follow/Music/Version)" \
      -o /tmp/ui-hide-region-hooks.txt

前置依赖（native-lib.cpp 已存在）:
  - il2cppStringToUtf8(const void* s)   （Il2CppString → std::string）
  - g_base（libil2cpp.so 基址，dl_iterate_phdr 获得）
  - LOGI(...)、A64HookFunction(...)、setupHooks(baseAddr)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[5] / "tools" / "scripts" / "lib"))
import common  # noqa: E402


def generate(args: argparse.Namespace) -> str:
    cls = args.host_class
    upd_rva = args.host_update_rva
    root_field = args.root_field
    scroll_name = args.scroll_view_name
    keep_marker = args.keep_marker
    name_rva = args.get_name_rva
    cc_rva = args.get_child_count_rva
    item_rva = args.get_item_rva
    remove_rva = args.remove_rva
    msg = args.log_message
    fn = "hideSettingsRegions"
    return f"""// === UIElements 区域容器隐藏 hook（{cls}）===
// 生成自 generate-ui-hide-region-hooks.py
// 说明: 字段引用与显示元素是不同对象 → 从 rootElement 递归 UXML 树，遍历
// {scroll_name} 的直接子区域容器；含 {keep_marker} 的区域保留，其余 RemoveFromHierarchy。
// 依赖: il2cppStringToUtf8 / g_base / LOGI / A64HookFunction 已存在
static int (*get_childCount_fn)(void*) = nullptr;
static void* (*get_Item_fn)(void*, int) = nullptr;
static void* (*get_name_fn)(void*) = nullptr;
static void (*RemoveFromHierarchy_fn)(void*) = nullptr;
static std::string elNameStr(void* el) {{
    if (!get_name_fn) return "";
    void* s = get_name_fn(el);
    return s ? il2cppStringToUtf8(s) : "";
}}
static void* findChildByName(void* el, const std::string& target) {{
    if (!el || !get_childCount_fn) return nullptr;
    int cc = get_childCount_fn(el);
    for (int i = 0; i < cc && i < 100; i++) {{
        void* c = get_Item_fn ? get_Item_fn(el, i) : nullptr;
        if (!c) continue;
        if (elNameStr(c) == target) return c;
        void* r = findChildByName(c, target);
        if (r) return r;
    }}
    return nullptr;
}}
static bool hasChildNamedEl(void* el, const std::string& target) {{
    if (!el || !get_childCount_fn) return false;
    int cc = get_childCount_fn(el);
    for (int i = 0; i < cc && i < 120; i++) {{
        void* c = get_Item_fn ? get_Item_fn(el, i) : nullptr;
        if (!c) continue;
        if (elNameStr(c) == target) return true;
        if (hasChildNamedEl(c, target)) return true;
    }}
    return false;
}}
static bool g_settings_hide_logged = false;
static void {fn}(void* __this) {{
    if (!get_childCount_fn) {{
        get_childCount_fn = (int (*)(void*))(g_base + 0x{cc_rva});
        get_Item_fn = (void* (*)(void*, int))(g_base + 0x{item_rva});
        get_name_fn = (void* (*)(void*))(g_base + 0x{name_rva});
        RemoveFromHierarchy_fn = (void (*)(void*))(g_base + 0x{remove_rva});
    }}
    if (!get_childCount_fn || !RemoveFromHierarchy_fn || g_settings_hide_logged) return;
    void* root = *(void**)((char*)__this + 0x{root_field});  // {cls}.rootElement
    if (!root) return;
    void* scroll = findChildByName(root, "{scroll_name}");
    if (!scroll) return;
    int cc = get_childCount_fn(scroll);
    bool any = false;
    for (int i = 0; i < cc && i < 40; i++) {{
        void* region = get_Item_fn ? get_Item_fn(scroll, i) : nullptr;
        if (!region) continue;
        if (hasChildNamedEl(region, "{keep_marker}")) continue;  // 保留区域
        RemoveFromHierarchy_fn(region);
        any = true;
    }}
    if (any) {{
        LOGI("[ui-hide] {msg}");
        g_settings_hide_logged = true;
    }}
}}

// === 在 setupHooks() 中追加（每帧移除，幂等）===//
static void (*orig_{cls}_{upd_rva}_Update)(void* __this);
static void Hooked{cls}_Update(void* __this) {{
    if (orig_{cls}_{upd_rva}_Update) orig_{cls}_{upd_rva}_Update(__this);
    {fn}(__this);
}}
// 注: 若 {cls}.Update 已被其他 hook 占用（如按钮隐藏），合并到同一 hook 调用 {fn}(__this) 即可
//    A64HookFunction((void*)(baseAddr + 0x{upd_rva}),
//                    (void*)Hooked{cls}_Update,
//                    (void**)&orig_{cls}_{upd_rva}_Update);
"""


def main() -> None:
    common.ensure_env()
    ap = argparse.ArgumentParser(description="生成 UIElements 区域容器隐藏 hook C++")
    ap.add_argument("--host-class", required=True)
    ap.add_argument("--host-update-rva", required=True)
    ap.add_argument("--root-field", required=True)
    ap.add_argument("--scroll-view-name", required=True)
    ap.add_argument("--keep-marker", required=True)
    ap.add_argument("--get-name-rva", required=True)
    ap.add_argument("--get-child-count-rva", required=True)
    ap.add_argument("--get-item-rva", required=True)
    ap.add_argument("--remove-rva", required=True)
    ap.add_argument("--log-message", required=True)
    ap.add_argument("-o", "--output", default="")
    args = ap.parse_args()

    code = generate(args)
    print(code)
    if args.output:
        Path(args.output).write_text(code, encoding="utf-8")
        common.log_info(f"已写入 {args.output}")
    common.append_tool_call("generate-ui-hide-region-hooks", " ".join(sys.argv[1:]))


if __name__ == "__main__":
    main()
