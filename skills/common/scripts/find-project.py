#!/usr/bin/env python3
"""find-project.py — 检索"用户指定的项目"落在 apks/ 还是 crackings/，给出处理入口。

[FLOWFIX 2026-08-19] AGENTS.md §1.15 检索逻辑落地：
- 用户"处理 XX"（新会话/新任务）→ apks/ 优先：命中 APK 则新跑 pipeline；未命中则查 crackings/ 断点续跑
- 用户"继续处理 XX"→ crackings/ 优先：读 status.yaml，从记录的阶段继续走剩下了阶段
- 脚本只做"定位 + 读状态 + 给建议入口"，不直接跑任何阶段（避免主阶段 driver 冒充验收结论）

用法:
  python3 find-project.py --name <关键词>            # 默认模式：apks/ 优先
  python3 find-project.py --name <关键词> --resume   # 继续模式：crackings/ 优先

输出:
  - apks/ 命中的 APK（新项目候选 + run-pipeline 命令）
  - crackings/ 命中的工程（type + status.yaml 断点 + 续跑命令）
  - 结论建议（新跑 / 断点续跑 / 无从判断提示用户）

匹配规则:
  - apks/: normalize_apk_name(文件名) 与关键词 大小写不敏感子串匹配（支持版本/来源后缀自动剔除）
  - crackings/: 目录 basename 与关键词 大小写不敏感子串匹配（含 <type> 父目录与遗留根目录）
"""
from __future__ import annotations

import sys
import argparse
import functools
from pathlib import Path

# 让所有 print 立即 flush，避免与 log_*（stderr）交错时顺序错乱
print = functools.partial(print, flush=True)  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[3]  # 仓库根目录（skills/common/scripts/ 的上级三级）
LIB_DIR = Path(__file__).resolve().parents[0] / "lib"  # skills/common/scripts/lib/
sys.path.insert(0, str(LIB_DIR))
from common import (  # noqa: F403
    ensure_env,
    log_info,
    log_warn,
    log_success,
    log_error,
    log_step,
    normalize_apk_name,
    now_iso,
)

APKS_DIR = ROOT / "apks"
CRACKINGS_DIR = ROOT / "crackings"


def _fold(s: str) -> str:
    """匹配用折叠：小写 + 去除非字母数字（兼容 'Battle Tank' ↔ 'BattleTank'）。"""
    return "".join(ch for ch in s.lower() if ch.isalnum())


def _load_status_yaml(name: str, type_parent: str | None) -> dict:
    if type_parent:
        p = CRACKINGS_DIR / type_parent / name / "status.yaml"
    else:
        p = CRACKINGS_DIR / name / "status.yaml"
    if not p.exists():
        return {}
    try:
        import yaml
        data = yaml.safe_load(p.read_text(encoding="utf-8", errors="ignore"))
        return data if isinstance(data, dict) else {}
    except Exception as e:  # noqa: BLE001
        log_warn(f"[find-project] status.yaml 解析失败 {p}: {e}")
        return {}


def search_apks(keyword: str) -> list[tuple[Path, str]]:
    """返回 [(apk 路径, 归一化名)]，按折叠后子串匹配。"""
    kw = _fold(keyword)
    hits = []
    if not APKS_DIR.exists():
        return hits
    for f in sorted(APKS_DIR.iterdir()):
        if not f.is_file():
            continue
        if f.suffix.lower() not in (".apk", ".xapk"):
            continue
        norm = normalize_apk_name(f.name)
        if kw and kw in _fold(norm + " " + f.name):
            hits.append((f, norm))
    return hits


def search_crackings(keyword: str) -> list[dict]:
    """返回 [{name, type_parent, dir, status}]，递归扫描 type 父目录 + 根目录遗留工程。"""
    kw = _fold(keyword)
    hits = []
    if not CRACKINGS_DIR.exists():
        return hits
    # 1) <type> 父目录下的工程（crackings/<type>/<Name>/）
    for type_dir in sorted(p for p in CRACKINGS_DIR.iterdir() if p.is_dir()):
        # 跳过遗留的"根目录工程"（直接是项目目录而非 type 父目录），type 目录不含 status.yaml 才算
        if (type_dir / "status.yaml").exists() or (type_dir / "findings.md").exists():
            continue  # 这是遗留的根目录工程，不是 type 父目录
        for proj in sorted(p for p in type_dir.iterdir() if p.is_dir()):
            if kw and kw in _fold(proj.name):
                hits.append({
                    "name": proj.name,
                    "type_parent": type_dir.name,
                    "dir": proj,
                })
    # 2) 遗留根目录工程（crackings/<Name>/）
    for proj in sorted(p for p in CRACKINGS_DIR.iterdir() if p.is_dir()):
        if (proj / "status.yaml").exists() or (proj / "findings.md").exists():
            if kw and kw in _fold(proj.name):
                hits.append({
                    "name": proj.name,
                    "type_parent": None,
                    "dir": proj,
                })
    # 3) 去重（type 扫描可能已覆盖根目录工程？不会——根目录工程没有 type 父目录）
    seen = set()
    uniq = []
    for h in hits:
        k = (h["name"], h["type_parent"])
        if k in seen:
            continue
        seen.add(k)
        uniq.append(h)
    return uniq


def summarize_stage(status: dict) -> str:
    """从 status.yaml 提炼断点摘要。"""
    st = status.get("status", {}) if isinstance(status, dict) else {}
    if not st:
        return "无 status.yaml（未初始化 / 结构异常）"
    phase = st.get("phase", "")
    stage = st.get("stage", "")
    current = st.get("current_stage", "")
    completed = st.get("completed_stages", []) or []
    failed = st.get("failed_stages", []) or []
    skipped = st.get("skipped", []) or []
    parts = [f"phase={phase}", f"stage={stage}", f"current_stage={current}"]
    if failed:
        parts.append(f"failed={failed}")
    if skipped:
        parts.append(f"skipped={skipped}")
    parts.append(f"completed({len(completed)})={completed[-6:]}{'…' if len(completed) > 6 else ''}")
    return " | ".join(parts)


def main() -> int:
    ensure_env()
    ap = argparse.ArgumentParser(description="检索用户指定的项目落在 apks/ 还是 crackings/")
    ap.add_argument("--name", required=True, help="项目名/关键词（归一化子串匹配）")
    ap.add_argument("--resume", action="store_true",
                    help="继续模式：以 crackings/ 为优先（对应\"继续处理 XX\"）")
    args = ap.parse_args()

    log_step(f"检索项目: {args.name}" + ("（继续模式：crackings/ 优先）" if args.resume else "（新处理：apks/ 优先）"))

    apks_hits = [] if args.resume else search_apks(args.name)
    proj_hits = search_crackings(args.name)

    # ---- apks/ 命中 ----
    if apks_hits:
        log_info("---- apks/ 命中的 APK（新项目候选） ----")
        for apk, norm in apks_hits:
            print(f"  • {apk.name}  → 归一 [{norm}]"
                  f"\n      新项目入口: python3 skills/common/scripts/run-pipeline.py {apk} {norm}")
    else:
        log_info("---- apks/ 无命中（未找到匹配 APK，转入 crackings/ 断点检索） ----")

    # ---- crackings/ 命中 ----
    if proj_hits:
        log_info("---- crackings/ 命中的工程（已有工程 → 断点续跑） ----")
        for h in proj_hits:
            status = _load_status_yaml(h["name"], h["type_parent"])
            t = h["type_parent"] or "?"
            print(f"  • crackings/{h['type_parent'] + '/' if h['type_parent'] else ''}{h['name']}/"
                  f"  (type={t})")
            print(f"      status.yaml: {summarize_stage(status)}")
            if h["type_parent"] or t != "?":
                if t and t != "?":
                    print(f"      续跑入口: python3 skills/strategy/{t}-strategy-skill/stages/sub_stage-dispatcher.py (TYPE={t})")
                else:
                    print(f"      续跑入口: python3 skills/strategy/<type>-strategy-skill/stages/sub_stage-dispatcher.py [--stage NN]")
            print(f"      状态查看:  python3 skills/common/scripts/crack.py {h['name']} status")
            # 断点建议
            st = status.get("status", {}) if isinstance(status, dict) else {}
            failed = st.get("failed_stages", []) or []
            current = st.get("current_stage", "")
            if failed:
                print(f"      建议: 先重跑失败阶段 {failed}，再继续剩余阶段")
            elif current:
                print(f"      建议: 从 current_stage={current} 继续后续阶段")
    else:
        log_info("---- crackings/ 无命中 ----")

    # ---- 结论 ----
    log_step("结论")
    if args.resume:
        if proj_hits:
            for h in proj_hits:
                print(f"  [继续] crackings/{h['name']}/ → 读 status.yaml，从记录的阶段继续走了剩下的子阶段")
            log_success("继续模式：已定位工程，按 fast-fail 阶段续跑")
        else:
            if apks_hits:
                print("  [降级] crackings/ 无此工程 → 回查 apks/ 命中，按\"处理 XX\"新跑 pipeline")
            else:
                log_warn(f"  apks/ 与 crackings/ 均未找到 [{args.name}]，请核对项目名/APK 池")
    else:
        if apks_hits:
            print("  [新处理] apks/ 命中 APK → 从该 APK 开始走 sniff→assess→strategy→stages→verify→accept→cleanup")
        elif proj_hits:
            print("  [断点] apks/ 无 APK，但 crackings/ 存在工程 → 读 status.yaml 从断点续跑剩余子阶段")
        else:
            log_warn(f"  apks/ 与 crackings/ 均未找到 [{args.name}]，请核对项目名/APK 池")
    log_info(f"[find-project] 检索完成 @ {now_iso()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())