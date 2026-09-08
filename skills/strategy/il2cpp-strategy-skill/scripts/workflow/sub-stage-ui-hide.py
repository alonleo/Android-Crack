#!/usr/bin/env python3
"""
sub-stage-ui-hide.py — 阶段 07：去功能点（UI 隐藏 + 区域裁剪）。

流程（重新设计 2026-08-13）：
  1. 通过清单管理器读取 feature-removal-checklist.yaml
  2. 根据清单表内容读取 dump.cs，匹配目标类/方法
  3. 根据实际情况选择隐藏策略（分析 dump.cs 中的类结构/方法签名）
  4. 生成 hide-plan.yaml（含策略的完整隐藏计划）
  5. 注入 native-lib.cpp 进行实际隐藏
  6. 验证产物
  7. 写入项目状态文档

产物契约：
- native-lib.cpp 含 ≥1 处 UI 隐藏 hook
- crackings/<Name>/stages/10-ui-hide/hide-plan.yaml 记录目标列表
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
SCRIPT_PKG = ROOT / "skills" / "strategy" / "il2cpp-strategy-skill" / "scripts"
sys.path.insert(0, str(SCRIPT_PKG))
import importlib.util as _ilu

_spc = _ilu.spec_from_file_location(
    "stage_common_runtime", str(SCRIPT_PKG / "lib" / "stage_common.py")
)
_sc = _ilu.module_from_spec(_spc)
assert _spc.loader is not None
_spc.loader.exec_module(_sc)

ensure_dir = _sc.ensure_dir
fatal = _sc.fatal
log_step = _sc.log_step
log_info = _sc.log_info
log_warn = _sc.log_warn
log_success = _sc.log_success
append_status = _sc.append_status
append_tool_call = _sc.append_tool_call
stage_out = _sc.stage_out

# ============================================================
# 1. 去功能点清单表（唯一数据源：统一 YAML）
# ============================================================
import runpy as _runpy
_CHECKLIST_API = _runpy.run_path(str(ROOT / "skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py"))


def load_feature_targets():
    global _FEATURE_SNAPSHOT
    _FEATURE_SNAPSHOT = _CHECKLIST_API["load_snapshot"](os.environ.get("FEATURE_REMOVAL_CHECKLIST") or None, os.environ.get("TYPE") or "il2cpp")
    return _FEATURE_SNAPSHOT["targets"]


# Loaded from YAML, never maintained as a second hardcoded list.
FEATURE_REMOVAL_TARGETS = load_feature_targets()


def _resolve_name() -> str:
    name = os.environ.get("NAME", "").strip()
    if not name:
        fatal("环境变量 NAME 未设置；请通过 crack.py 调度")
    return name


def _app_main(name: str) -> Path:
    type_arg = os.environ.get("TYPE", "").strip()
    if type_arg:
        base = ROOT / "output-projects" / type_arg / name
    else:
        base = ROOT / "output-projects" / name
    return base / "app" / "src" / "main"


# ============================================================
# 2. 读取 dump.cs 匹配目标
# ============================================================
def scan_dump_for_targets(dump_path: Path) -> dict[str, list[dict]]:
    """扫描 dump.cs，按功能点分类返回匹配的类/方法。

    匹配规则：
    - 仅匹配含 RVA 的行（有实际地址的方法/字段）
    - 关键词必须作为完整单词匹配（避免 "Rate" 匹配 "Generate"）
    - 优先匹配方法定义（含括号）而非字段/注释
    """
    global FEATURE_REMOVAL_TARGETS
    FEATURE_REMOVAL_TARGETS = load_feature_targets()
    if not dump_path.is_file():
        log_warn(f"dump.cs 缺失: {dump_path}")
        return {}

    text = dump_path.read_text(encoding="utf-8", errors="ignore")
    lines = text.splitlines()
    results: dict[str, list[dict]] = {}

    for feature_id, config in FEATURE_REMOVAL_TARGETS.items():
        matches = []
        keywords = config["keywords"]
        for idx, line in enumerate(lines):
            # 仅匹配含 RVA 的行（有实际地址）
            rva_match = re.search(r"//\s*(?:RVA:\s*)?0x([0-9A-Fa-f]+)", line)
            if not rva_match:
                continue

            # 关键词必须作为完整单词匹配
            matched_kw = None
            for kw in keywords:
                # [FLOWFIX] 改用 substring 匹配（word boundary 会漏掉如 "ShowMoreGames" 中的 "MoreGames"）
                if kw.lower() in line.lower():
                    matched_kw = kw
                    break

            if not matched_kw:
                continue

            # 提取方法名/类名
            rva = f"0x{rva_match.group(1)}"
            sig_match = re.search(r"(public|private|internal|static)\s+([\w<>\[\],\s]+)\s+(\w+)\s*\(", line)
            method_name = sig_match.group(3) if sig_match else matched_kw
            class_match = re.search(r"class\s+(\w+)", line)
            class_name = class_match.group(1) if class_match else None

            # 过滤掉明显不是目标的匹配（如 RVA 太小的系统地址）
            rva_int = int(rva_match.group(1), 16)
            if rva_int < 0x1000:  # 跳过系统保留地址
                continue

            matches.append({
                "keyword": matched_kw,
                "line_num": idx + 1,
                "rva": rva,
                "method": method_name,
                "class": class_name,
                "signature": line.strip()[:200],
            })

        if matches:
            # 去重（按 RVA）
            seen_rvas = set()
            unique_matches = []
            for m in matches:
                if m["rva"] not in seen_rvas:
                    seen_rvas.add(m["rva"])
                    unique_matches.append(m)
            results[feature_id] = unique_matches

    return results


# ============================================================
# 3. 根据实际情况选择隐藏策略
# ============================================================
def analyze_and_select_strategy(
    scan_results: dict[str, list[dict]],
    dump_path: Path,
) -> dict[str, dict]:
    """分析 dump.cs 中的类结构/方法签名，为每个功能点选择最佳隐藏策略。

    策略选择规则：
    - hook_container: 有 Manager/Controller 类，且含 Open/Show/Display 等入口方法
    - hook_method: 有明确的单个方法（Rate/Share/Restore 等）
    - hide_node: 是 UI 节点属性（Version/Avatar 等文本/图标）
    - static_hide: 是 NGUI MenuPage 或 GameObject（需静态改 data.unity3d）
    - skip: 匹配结果不相关（系统方法/非 UI 元素）
    """
    strategy_map: dict[str, dict] = {}

    # 读取 dump.cs 上下文（用于分析类结构）
    dump_text = ""
    if dump_path.is_file():
        dump_text = dump_path.read_text(encoding="utf-8", errors="ignore")

    for feature_id, matches in scan_results.items():
        config = FEATURE_REMOVAL_TARGETS[feature_id]
        default_strategy = config["strategy"]
        if config.get("requires_review", True) or default_strategy == "review":
            strategy_map[feature_id] = {"strategy": "review", "reason": config["notes"],
                                        "suggested_strategy": default_strategy, "requires_review": True,
                                        "matches": matches, "total_matches": len(matches),
                                        "valid_matches": len(matches)}
            continue

        # 分析每个匹配，判断最佳策略
        best_strategy = default_strategy
        best_matches = []
        reason = ""

        for m in matches:
            sig = m["signature"].lower()
            method = m["method"]
            rva = m["rva"]

            # 跳过系统方法（Version 的 get/set/Compare 等）
            if feature_id == "version_text":
                # 只保留 UI 相关的 Version（如 ShowVersion/VersionText）
                if any(x in sig for x in ["get;", "set;", "compare", "getplatform", "getsdkversion"]):
                    continue
                # 如果是 Version 属性，可能是 UI 文本
                if "version" in method.lower() and "text" in sig:
                    best_strategy = "hide_node"
                    reason = "Version 文本节点"

            # 检查是否是 Manager/Controller 类的入口方法
            if any(x in sig for x in ["manager", "controller", "service"]):
                if any(x in sig for x in ["open(", "show(", "display(", "initialize("]):
                    best_strategy = "hook_container"
                    reason = f"容器入口方法: {method}"

            # 检查是否是明确的单个方法
            if any(x in method.lower() for x in ["rate", "share", "restore", "delete", "consent"]):
                if "(" in sig:  # 是方法而非属性
                    best_strategy = "hook_method"
                    reason = f"独立方法: {method}"

            # 检查是否是 UI 节点
            if any(x in sig for x in ["button", "text", "image", "toggle", "slider"]):
                best_strategy = "hide_node"
                reason = f"UI 节点: {method}"

            # 只保留有 RVA 的匹配
            if rva and rva != "N/A":
                best_matches.append(m)

        # 如果没有有效匹配，跳过
        if not best_matches:
            best_strategy = "skip"
            reason = "无有效 RVA 目标"

        strategy_map[feature_id] = {
            "strategy": best_strategy,
            "reason": reason or f"默认策略: {default_strategy}",
            "matches": best_matches,
            "total_matches": len(matches),
            "valid_matches": len(best_matches),
        }

    return strategy_map


# ============================================================
# 4. 生成 hide-plan.yaml（含策略的完整隐藏计划）
# ============================================================
def generate_hide_plan(name: str, strategy_map: dict[str, dict], sd: Path) -> Path:
    """Serialize reviewed/unreviewed candidates without interpolating YAML."""
    import yaml

    plan_path = sd / "hide-plan.yaml"
    ensure_dir(sd)
    targets = {}
    for feature_id, info in strategy_map.items():
        config = FEATURE_REMOVAL_TARGETS[feature_id]
        targets[feature_id] = {
            "id": config["id"],
            "strategy": info["strategy"],
            "suggested_strategy": info.get("suggested_strategy", config["strategy"]),
            "requires_review": info.get("requires_review", True),
            "reason": info["reason"],
            "desc": config["desc"],
            "hooks": [{"method": m["method"], "rva": m["rva"],
                       "class": m.get("class", "N/A"), "signature": m["signature"]}
                      for m in info["matches"]],
        }
    plan = {
        "stage": "07", "name": name,
        "checklist_path": _FEATURE_SNAPSHOT["registry_path"],
        "checklist_sha256": _FEATURE_SNAPSHOT["registry_sha256"],
        "targets": targets,
    }
    plan_path.write_text(yaml.safe_dump(plan, allow_unicode=True, sort_keys=False), encoding="utf-8")
    log_success(f"hide-plan.yaml 已生成: {plan_path} ({len(targets)} 个候选功能点)")
    return plan_path


# ============================================================
# 5. 注入 native-lib.cpp
# ============================================================
def inject_ui_hide_hooks(
    name: str,
    strategy_map: dict[str, dict],
    plan_path: Path,
) -> bool:
    """根据 hide-plan.yaml 注入 UI 隐藏 hook 到 native-lib.cpp。"""
    cpp = _app_main(name) / "cpp" / "native-lib.cpp"
    if not cpp.is_file():
        log_warn("native-lib.cpp 缺失；阶段 04 必须先执行")
        return False

    text = cpp.read_text(encoding="utf-8")
    if "ui-hide" in text:
        log_info("native-lib.cpp 已含 UI 隐藏 hook；跳过注入")
        return True

    # 按策略分组
    hook_methods = []
    hook_containers = []
    hide_nodes = []
    for feature_id, info in strategy_map.items():
        if info["strategy"] == "skip":
            continue
        config = FEATURE_REMOVAL_TARGETS[feature_id]
        for m in info["matches"]:
            if not m["rva"]:
                continue
            entry = {
                "feature": feature_id,
                "method": m["method"],
                "rva": m["rva"],
                "desc": config["desc"],
                "strategy": info["strategy"],
            }
            if info["strategy"] == "hook_container":
                hook_containers.append(entry)
            elif info["strategy"] == "hook_method":
                hook_methods.append(entry)
            elif info["strategy"] == "hide_node":
                hide_nodes.append(entry)

    if not hook_methods and not hook_containers and not hide_nodes:
        log_warn("无有效 RVA 目标，跳过 hook 注入")
        return False

    # 生成 hook 代码
    hook_code = "\n// === injected by stage-10-ui-hide ===\n"

    # 容器入口 hook（MenuManager.Open 等 no-op）
    if hook_containers:
        hook_code += "// 容器入口 hook（no-op 模式）\n"
        for h in hook_containers:
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", h["method"])
            hook_code += f"""
static void (*orig_{safe_name})(void* __this);
static void Hooked_{safe_name}(void* __this) {{
    LOGI("[ui-hide] {h['desc']}: {h['method']} blocked (RVA {h['rva']})");
    // no-op: 不调用原函数
}}
"""

    # 方法 hook（评分/隐私等 → 桩化）
    if hook_methods:
        hook_code += "// 方法 hook（桩化模式）\n"
        for h in hook_methods:
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", h["method"])
            hook_code += f"""
static void (*orig_{safe_name})(void* __this);
static void Hooked_{safe_name}(void* __this) {{
    LOGI("[ui-hide] {h['desc']}: {h['method']} stubbed (RVA {h['rva']})");
    // 桩化：不执行原逻辑
}}
"""

    # UI 节点 hook（隐藏/移除）
    if hide_nodes:
        hook_code += "// UI 节点 hook（隐藏模式）\n"
        for h in hide_nodes:
            safe_name = re.sub(r"[^a-zA-Z0-9]", "_", h["method"])
            hook_code += f"""
static void (*orig_{safe_name})(void* __this);
static void Hooked_{safe_name}(void* __this) {{
    LOGI("[ui-hide] {h['desc']}: {h['method']} hidden (RVA {h['rva']})");
    // 隐藏：不渲染/不显示
}}
"""

    # setupHooks 调用
    all_hooks = hook_containers + hook_methods + hide_nodes
    hook_code += "\n// UI 隐藏 hook 注册（在 setupHooks 中调用）\n"
    hook_code += "static void setupUIHideHooks(uintptr_t base) {\n"
    for h in all_hooks:
        safe_name = re.sub(r"[^a-zA-Z0-9]", "_", h["method"])
        hook_code += f'    A64HookFunction((void*)(base + {h["rva"]}), (void*)Hooked_{safe_name}, (void**)&orig_{safe_name});\n'
        hook_code += f'    LOGI("[ui-hide] {h["method"]} @ {h["rva"]} installed");\n'
    hook_code += "}\n"

    # 注入到 native-lib.cpp
    cpp.write_text(text + hook_code, encoding="utf-8")
    log_success(f"native-lib.cpp 已注入 {len(all_hooks)} 个 UI 隐藏 hook")
    return True


# ============================================================
# 6. 验证
# ============================================================
def verify(name: str, plan_path: Path) -> bool:
    """验证产物完整性。"""
    cpp_path = _app_main(name) / "cpp" / "native-lib.cpp"
    if not cpp_path.is_file():
        log_warn("native-lib.cpp 缺失")
        return False
    cpp = cpp_path.read_text(encoding="utf-8")
    if "ui-hide" not in cpp:
        log_warn("native-lib.cpp 未含 UI 隐藏 hook")
        return False
    if not plan_path.is_file():
        log_warn("hide-plan.yaml 缺失")
        return False
    log_success("阶段 10 契约校验通过")
    return True


# ============================================================
# 7. 主流程
# ============================================================
def main() -> int:
    parser = argparse.ArgumentParser(description="IL2CPP 阶段 07：去功能点")
    args = parser.parse_args()
    name = _resolve_name()
    sd = stage_out(name, "10", label="ui-hide")

    log_step("阶段 07：去功能点（UI 隐藏）")

    # 1. 加载去功能点清单表
    log_info("步骤 1/7: 加载去功能点清单表...")
    checklist_path = Path(os.environ.get("FEATURE_REMOVAL_CHECKLIST") or _CHECKLIST_API["DEFAULT_REGISTRY"])
    targets = load_feature_targets()
    log_info(f"YAML 清单已加载: {checklist_path} ({len(targets)} 个候选功能点)")

    # 2. 根据清单表内容读取 dump.cs，匹配目标类/方法
    log_info("步骤 2/7: 扫描 dump.cs 匹配目标...")
    dump_path = ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "stages" / "05-il2cpp-dump" / "dump" / "dump.cs"
    if not dump_path.is_file():
        dump_path = ((os.environ.get("TYPE", "").strip() and (ROOT / "crackings" / os.environ.get("TYPE", "").strip() / name)) or (ROOT / "crackings" / name)) / "stages" / "05-hook-fn-analyze" / "dump" / "dump.cs"
    scan_results = scan_dump_for_targets(dump_path)
    if not scan_results:
        log_warn("dump.cs 中未匹配到任何功能点目标")
        return 1
    log_info(f"匹配到 {len(scan_results)} 个功能点: {', '.join(scan_results.keys())}")

    # 3. 根据实际情况选择隐藏策略
    log_info("步骤 3/7: 分析 dump.cs 选择隐藏策略...")
    strategy_map = analyze_and_select_strategy(scan_results, dump_path)
    for feature_id, info in strategy_map.items():
        if info["strategy"] != "skip":
            log_info(f"  {feature_id}: 策略={info['strategy']}, 原因={info['reason']}, 有效={info['valid_matches']}/{info['total_matches']}")

    # 4. 生成 hide-plan.yaml（含策略的完整隐藏计划）
    log_info("步骤 4/7: 生成 hide-plan.yaml...")
    plan_path = generate_hide_plan(name, strategy_map, sd)

    if any(info.get("requires_review", False) for info in strategy_map.values()):
        log_warn("候选计划已生成，需 Agent 核查核心依赖并通过当前 type 实施方案处理；未审核不注入，阶段未通过。")
        return 1

    # 5. 注入 native-lib.cpp
    log_info("步骤 5/7: 注入 native-lib.cpp...")
    if not inject_ui_hide_hooks(name, strategy_map, plan_path):
        log_warn("hook 注入失败或无有效目标")
        return 1

    # 6. 验证
    log_info("步骤 6/7: 验证产物...")
    if not verify(name, plan_path):
        return 1

    # 7. 写入项目状态文档
    log_info("步骤 7/7: 写入项目状态文档...")
    active_features = sum(1 for v in strategy_map.values() if v["strategy"] != "skip")
    total_hooks = sum(len(v["matches"]) for v in strategy_map.values() if v["strategy"] != "skip")
    log_success(f"阶段 10 完成: {active_features} 个功能点, {total_hooks} 个 hook")
    return 0


if __name__ == "__main__":
    sys.exit(main())
