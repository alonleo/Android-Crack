#!/usr/bin/env python3
"""verify-commit-push-major-stage.py — 主阶段提交/推送校验器。

校验两个事:
  1. **每个子阶段都至少有 1 次 commit**
     （从子阶段注册表读取阶段列表，对比项目 .git log 中是否每个 <stage-id> 都有对应提交）
  2. **remote 已设置 + 本地分支已成功推送过**
     （git remote get-url origin 成功 + git rev-list --count origin/<branch> >= 1）
     → 否则只是 commit 还不够，必须真的推送到用户填入的 remote

用途:
  - 在主阶段（M1/M2/M3/M4）结束时跑一次，给出"本主阶段所有子阶段都已 git 提交 + 已推送"的总账
  - 替代手工 git log 比对；失败时给出每个缺失 stage + 修复命令

用法:
  python3 verify-commit-push-major-stage.py --name <Name> [--type <type>] [--branch <branch>]

  --branch 默认 main；推送脚本 push-project-remote.py 的默认分支一致
"""
from __future__ import annotations

import argparse
import functools
import re
import subprocess
import sys
from pathlib import Path

print = functools.partial(print, flush=True)  # type: ignore[assignment]

ROOT = Path(__file__).resolve().parents[3]
LIB_DIR = Path(__file__).resolve().parents[0] / "lib"
sys.path.insert(0, str(LIB_DIR))
from common import (  # noqa: F403
    ensure_env,
    log_info,
    log_warn,
    log_success,
    log_error,
    log_step,
)

CRACKINGS_DIR = ROOT / "crackings"


def _read_register_stages_regex(reg: Path) -> list[str]:
    """YAML 解析失败/缺库的兜底：正则抠 sub_stages: 段下的 - id: 行。"""
    text = reg.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"^sub_stages:\s*\n((?:[ \t]+-.*\n?)+)", text, re.MULTILINE)
    if not m:
        return []
    return re.findall(r"^\s*-\s*id:\s*([^\s#]+)", m.group(1), re.MULTILINE)


def _fold(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def locate_project(name: str, type_hint: str | None) -> Path | None:
    kw = _fold(name)
    hits: list[Path] = []
    if not CRACKINGS_DIR.exists():
        return None
    for type_dir in sorted(p for p in CRACKINGS_DIR.iterdir() if p.is_dir()):
        if (type_dir / "status.yaml").exists() or (type_dir / "findings.md").exists():
            if kw and kw in _fold(type_dir.name):
                hits.append(type_dir)
            continue
        if type_hint and _fold(type_hint) != _fold(type_dir.name):
            continue
        for proj in sorted(p for p in type_dir.iterdir() if p.is_dir()):
            if kw and kw in _fold(proj.name):
                hits.append(proj)
    if len(hits) == 1:
        return hits[0]
    if len(hits) > 1:
        found = ", ".join(str(h.relative_to(CRACKINGS_DIR)) for h in hits)
        log_warn(f"[verify-commit-push] 匹配到多个候选: {found}，请用 --type 消歧")
        return None
    cand = CRACKINGS_DIR / name
    if cand.is_dir():
        return cand
    return None


def locate_project_type(proj_dir: Path) -> str | None:
    """从 crackings/<type>/<Name>/ 反推 <type>，用于推断策略 skill。"""
    try:
        rel = proj_dir.relative_to(CRACKINGS_DIR)
    except ValueError:
        return None
    parts = rel.parts
    if len(parts) >= 2:
        return parts[0]
    return None


def locate_skill_dir(project_type: str) -> Path | None:
    """skills/strategy/<type>-strategy-skill/stages/sub-stage-register.yaml"""
    cand = ROOT / "skills" / "strategy" / f"{project_type}-strategy-skill"
    if cand.is_dir():
        return cand
    return None


def git(proj_dir: Path, *args) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", "-C", str(proj_dir), *args],
        capture_output=True, text=True,
    )


def read_register_stages(skill_dir: Path) -> list[str]:
    """从 stages/sub-stage-register.yaml 读 sub_stages 阶段 id 列表（书写顺序 = 执行顺序）。

    容忍:
      - YAML 不存在 / 格式异常 → 返回空列表（提示人工核对）
      - sub_stages 段为空 → 返回空列表
    """
    reg = skill_dir / "stages" / "sub-stage-register.yaml"
    if not reg.exists():
        return []
    try:
        import yaml  # noqa
    except ImportError:
        return _read_register_stages_regex(reg)
    try:
        data = yaml.safe_load(reg.read_text(encoding="utf-8")) or {}
    except Exception as e:
        log_warn(f"解析 {reg} 失败: {e}（尝试正则解析兜底）")
        return _read_register_stages_regex(reg)
    items = (data.get("sub_stages") or [])
    ids: list[str] = []
    for it in items:
        if isinstance(it, dict) and "id" in it:
            ids.append(str(it["id"]))
        elif isinstance(it, str):
            ids.append(it)
    return ids


def list_commits_with_stage_id(proj_dir: Path, stage_ids: list[str]) -> dict[str, int]:
    """对每个 stage_id 统计 commit 数（按提交信息首段 'stage: <id>' 匹配）。

    返回 {stage_id: count}，count=0 表示该子阶段未提交过。
    """
    result = {sid: 0 for sid in stage_ids}
    r = git(proj_dir, "log", "--pretty=%s")
    if r.returncode != 0 or not r.stdout.strip():
        return result
    for line in r.stdout.splitlines():
        line = line.strip()
        # commit-project-stage.py 的格式: "stage: <id>" 或 "stage: <id> — 备注"
        m = re.match(r"^stage:\s+(\S+)", line)
        if m and m.group(1) in result:
            result[m.group(1)] += 1
    return result


def check_remote_and_push(proj_dir: Path, branch: str) -> tuple[bool, bool, str]:
    """返回 (has_remote, has_pushed, remote_url)。"""
    r = git(proj_dir, "remote", "get-url", "origin")
    if r.returncode != 0 or not r.stdout.strip():
        return False, False, ""
    url = r.stdout.strip()
    # 是否已经推到过该分支（origin/<branch> 存在 + 至少 1 个 commit）
    r2 = git(proj_dir, "rev-parse", "--verify", f"origin/{branch}", "--quiet")
    if r2.returncode != 0:
        return True, False, url
    r3 = git(proj_dir, "rev-list", "--count", f"origin/{branch}")
    cnt = int(r3.stdout.strip()) if r3.returncode == 0 and r3.stdout.strip().isdigit() else 0
    return True, cnt > 0, url


def main() -> int:
    ensure_env()
    ap = argparse.ArgumentParser(
        description="主阶段提交/推送校验：每子阶段至少 1 commit + 已设 remote + 已推送"
    )
    ap.add_argument("--name", required=True, help="项目名")
    ap.add_argument("--type", default=None, help="引擎类型父目录（多候选消歧）")
    ap.add_argument("--branch", default="main", help="远程推送目标分支")
    args = ap.parse_args()

    proj_dir = locate_project(args.name, args.type)
    if not proj_dir:
        log_error(f"未定位到项目: crackings/**/{args.name}")
        return 1
    if not (proj_dir / ".git").exists():
        log_error(f"项目尚无独立 git 仓库: {proj_dir.relative_to(ROOT)}")
        return 1

    log_step(f"校验: {proj_dir.relative_to(ROOT)}")

    # ---- 1. 子阶段提交完整性 ----
    project_type = args.type or locate_project_type(proj_dir)
    stage_ids: list[str] = []
    if project_type:
        skill_dir = locate_skill_dir(project_type)
        if skill_dir:
            stage_ids = read_register_stages(skill_dir)
            log_info(f"读取 register 阶段列表: {skill_dir.relative_to(ROOT)} (count={len(stage_ids)})")
        else:
            log_warn(f"未找到 {project_type}-strategy-skill，无法读 register，校验跳过阶段完整性")
    else:
        log_warn("无法推断项目 type，校验跳过阶段完整性")

    failed_stages: list[str] = []
    if stage_ids:
        counts = list_commits_with_stage_id(proj_dir, stage_ids)
        log_step(f"阶段 commit 统计 ({len(stage_ids)} 个子阶段)")
        max_id_len = max((len(s) for s in stage_ids), default=8)
        for sid in stage_ids:
            cnt = counts.get(sid, 0)
            tag = "✓" if cnt > 0 else "✗"
            line = f"    {tag} {sid.ljust(max_id_len)}  commits={cnt}"
            if cnt > 0:
                log_info(line)
            else:
                log_warn(line)
                failed_stages.append(sid)

    # ---- 2. remote & push 校验 ----
    log_step("remote + 推送 校验")
    has_remote, has_pushed, remote_url = check_remote_and_push(proj_dir, args.branch)
    if not has_remote:
        log_error(f"remote origin 未设置；请运行:\n"
                  f"    python3 skills/common/scripts/push-project-remote.py "
                  f"--name {args.name} --remote <url>")
    else:
        log_success(f"remote origin = {remote_url}")
        if has_pushed:
            log_success(f"已成功推送到 origin/{args.branch}")
        else:
            log_error(f"origin/{args.branch} 不存在或为空；尚未推送任何 commit\n"
                      f"    python3 skills/common/scripts/push-project-remote.py "
                      f"--name {args.name} --remote {remote_url} [--branch {args.branch}]")

    # ---- 总结 ----
    log_step("总结")
    issues = list(failed_stages)
    if not has_remote:
        issues.append("[NO-REMOTE]")
    if has_remote and not has_pushed:
        issues.append("[NOT-PUSHED]")
    if not issues:
        log_success("全部通过: 每子阶段都已 commit + remote 已设置 + 已推送")
        return 0
    log_error(f"校验失败 {len(issues)} 项: {', '.join(issues)}")
    if failed_stages:
        log_error("缺失 commit 的子阶段修复命令（逐个跑）:")
        for sid in failed_stages:
            log_error(f"    python3 skills/common/scripts/commit-project-stage.py "
                      f"--name {args.name} --stage {sid}")
    return 1


if __name__ == "__main__":
    sys.exit(main())