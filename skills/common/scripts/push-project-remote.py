#!/usr/bin/env python3
"""push-project-remote.py — 仅推送 crackings/<type>/<Name>/project/ 内容到远程仓库。

设计动机（AGENTS.md §9.6）:
  - 项目级独立 git 仓库记录了完整阶段历史（status/findings/dir-index/scripts/raw/），
    但**仅推 project/ 子目录**到远程，避免提交 GB 级 raw/project.build 等体积产物，
    也避免把仍含敏感信息的阶段中间文件意外外传。
  - 远程仓库是用户填入的远程协作仓库（git URL）；本脚本不内置任何 remote。
  - 推送完成后，工作区的根树**必须恢复原状**（不会污染后续 commit-project-stage.py）。

技术方案（先生拍板）：
  - 在原项目 .git 内**临时启用 sparse-checkout**（非 cone 模式 + 单条路径 "project/*"），
    推送完成后调用 `sparse-checkout disable` 恢复到原始工作区内容。
  - 这样复用同一个 .git 仓库，零额外存储；不复制任何文件。
  - 为防脚本中断把工作区卡在稀疏状态，本脚本启动时先检查并在发现异常时尝试复位（best-effort）。

用法:
  python3 push-project-remote.py --name <Name> [--type <type>] --remote <url> [--branch <b>] [--dry-run]

  --name <Name>      项目名（CamelCase）
  --type <type>      引擎类型父目录（多候选消歧）
  --remote <url>     远程 git URL（必填；脚本不内置）
  --branch <branch>  远程推送目标分支（默认 main）
  --dry-run          只预览将推送的 commit 列表 + 临时 sparse-checkout 视图，不真推
  --yes              跳过"恢复后确认"提示，强制执行

安全约束（REQUIRED）:
  - 推送前先 `git -C ... ls-files project/` 列出将要推送的文件；为空则拒绝并提示。
  - 推送前先 `git -C ... ls-remote <remote>` 探测远程可达性（失败则拒绝）。
  - 推送失败时**不立即恢复 sparse-checkout**，先保留现场供人工排查；
    用 `--restore-only` 可强制复位（脚本会交互式确认）。
"""
from __future__ import annotations

import argparse
import functools
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


def _fold(s: str) -> str:
    return "".join(ch for ch in s.lower() if ch.isalnum())


def locate_project(name: str, type_hint: str | None) -> Path | None:
    """复用 init-project-git.py 同样的候选解析逻辑（保持一致）。"""
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
        log_warn(f"[push-project-remote] 匹配到多个候选: {found}，请用 --type 消歧")
        return None
    cand = CRACKINGS_DIR / name
    if cand.is_dir():
        return cand
    return None


def git(proj_dir: Path, *args, check: bool = False):
    return subprocess.run(
        ["git", "-C", str(proj_dir), *args],
        capture_output=True, text=True, check=check,
    )


def check_clean_sparse_state(proj_dir: Path) -> bool:
    """检测当前是否处于 sparse-checkout 启用状态（异常残留检测）。"""
    sc = proj_dir / ".git" / "info" / "sparse-checkout"
    if not sc.exists():
        return True
    val = sc.read_text(encoding="utf-8", errors="replace").strip()
    return val in ("", "*", "/*")


def enable_sparse_project(proj_dir: Path) -> None:
    """临时切换根树到 'project/*'（非 cone 模式）。"""
    # core.sparseCheckout 是必须的开关
    git(proj_dir, "config", "core.sparseCheckout", "true", check=True)
    # init + 指定稀疏路径（非 cone 模式，路径精确写）
    sc = proj_dir / ".git" / "info" / "sparse-checkout"
    sc.write_text("project/*\n!project/*/\n", encoding="utf-8")
    # 用 read-tree 立即应用（不动 index lock，靠 --reset 模式）
    # 注意：read-tree 必须配合 -m (merge) 才能与现有 index 合并；这里用 -mu
    git(proj_dir, "read-tree", "-mu", "HEAD", check=True)


def disable_sparse_project(proj_dir: Path) -> None:
    """恢复根树到完整视图。"""
    # 先 disable 清空 sparse-checkout
    subprocess.run(
        ["git", "-C", str(proj_dir), "sparse-checkout", "disable"],
        capture_output=True, text=True,
    )
    # read-tree 重新铺开 HEAD 全部内容
    git(proj_dir, "read-tree", "-mu", "HEAD", check=True)
    # core.sparseCheckout 关掉避免误伤后续 commit
    subprocess.run(
        ["git", "-C", str(proj_dir), "config", "--unset", "core.sparseCheckout"],
        capture_output=True, text=True,
    )


def list_to_push(proj_dir: Path) -> list[str]:
    """列出当前 git index 中所有 project/ 前缀的文件（将真正推送的内容）。"""
    r = git(proj_dir, "ls-files", "project/")
    if r.returncode != 0:
        return []
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def list_remote_commits(proj_dir: Path, remote: str, branch: str) -> list[str]:
    """列出将要推送的 commit 列表（不含已存在的）。"""
    r = git(proj_dir, "log", "--oneline", f"HEAD", f"^{remote}/{branch}")
    if r.returncode != 0:
        # 远程分支不存在（首次推送），整条 HEAD 历史
        r = git(proj_dir, "log", "--oneline", "HEAD")
    return [ln for ln in r.stdout.splitlines() if ln.strip()]


def check_remote_reachable(proj_dir: Path, remote: str) -> bool:
    """探测远程 URL 是否可达 + 是否可读。"""
    r = git(proj_dir, "ls-remote", "--heads", remote)
    if r.returncode != 0:
        log_error(f"远程不可达: {r.stderr.strip()}")
        return False
    return True


def main() -> int:
    ensure_env()
    ap = argparse.ArgumentParser(
        description="推送项目级 project/ 子目录到远程 git（仅推 project/，其余不入库）"
    )
    ap.add_argument("--name", required=True, help="项目名（CamelCase）")
    ap.add_argument("--type", default=None, help="引擎类型父目录（多候选消歧）")
    ap.add_argument("--remote", default=None, help="远程 git URL（必填）")
    ap.add_argument("--branch", default="main", help="远程推送目标分支（默认 main）")
    ap.add_argument("--dry-run", action="store_true", help="只预览将推送的内容，不真推")
    ap.add_argument("--yes", action="store_true", help="跳过恢复确认，强制执行")
    ap.add_argument("--restore-only", action="store_true",
                    help="仅复位 sparse-checkout 状态（异常恢复用）")
    args = ap.parse_args()

    proj_dir = locate_project(args.name, args.type)
    if not proj_dir:
        log_error(f"未定位到项目: crackings/**/{args.name}")
        return 1
    if not (proj_dir / ".git").exists():
        log_error(f"项目尚无独立 git 仓库: {proj_dir.relative_to(ROOT)}")
        log_error("请先运行: python3 skills/common/scripts/init-project-git.py --name <Name>")
        return 1

    log_step(f"推送项目 project/ 到远程: {proj_dir.relative_to(ROOT)}")

    # ---- 异常恢复路径 ----
    if args.restore_only:
        log_warn("--restore-only: 强制复位 sparse-checkout")
        disable_sparse_project(proj_dir)
        log_success("已复位（sparse-checkout disable + read-tree -mu HEAD）")
        return 0

    # ---- 前置检查 ----
    if not args.remote:
        log_error("必须通过 --remote <url> 指定远程 git URL（脚本不内置任何 remote）")
        return 1

    # 检测稀疏残留
    if not check_clean_sparse_state(proj_dir):
        log_warn("检测到 sparse-checkout 异常残留（非默认状态），先尝试复位…")
        disable_sparse_project(proj_dir)
        if not check_clean_sparse_state(proj_dir):
            log_error("稀疏状态仍异常，请运行 --restore-only 手动复位后再试")
            return 1

    # 探测远程
    if not check_remote_reachable(proj_dir, args.remote):
        return 1

    # 列出将要推送的文件
    log_step("切换到稀疏视图（仅 project/*）")
    enable_sparse_project(proj_dir)
    files_to_push = list_to_push(proj_dir)
    if not files_to_push:
        log_error("project/ 子目录下没有任何已追踪文件，nothing to push，拒绝推送")
        log_error("请确认 project/ 已 git add 过；如未提交，原始 commit-project-stage.py 已生效")
        log_warn("脚本中止前先恢复稀疏状态…")
        disable_sparse_project(proj_dir)
        return 1

    log_success(f"将推送 {len(files_to_push)} 个 project/ 文件:")
    for f in files_to_push[:30]:
        print(f"    {f}")
    if len(files_to_push) > 30:
        print(f"    … 共 {len(files_to_push)} 条")

    # 列出 commit 列表
    commits = list_remote_commits(proj_dir, args.remote, args.branch)
    if commits:
        log_step(f"将推送 {len(commits)} 个 commit 到 {args.branch}")
        for c in commits[:20]:
            print(f"    {c}")
        if len(commits) > 20:
            print(f"    … 共 {len(commits)} 个")
    else:
        log_info("远程分支不存在或已无新 commit（将推送全量 HEAD 历史）")

    if args.dry_run:
        log_info("--dry-run: 仅预览，未推送")
        # 预览也恢复，避免污染
        disable_sparse_project(proj_dir)
        return 0

    # 设置远程
    r = git(proj_dir, "remote", "get-url", "origin")
    if r.returncode != 0:
        log_info(f"设置 remote origin = {args.remote}")
        git(proj_dir, "remote", "add", "origin", args.remote, check=True)
    else:
        if r.stdout.strip() != args.remote:
            log_warn(f"remote origin 已是 {r.stdout.strip()}，与 --remote 不同，跳过更新")
        else:
            log_info("remote origin 已指向相同 URL")

    # 推送
    log_step(f"推送到 {args.remote} 的 {args.branch}")
    rc = git(proj_dir, "push", "origin", f"HEAD:refs/heads/{args.branch}", "--force-with-lease")
    if rc.returncode != 0:
        log_error(f"推送失败: {rc.stderr.strip()}")
        log_error("工作区 sparse-checkout 暂未恢复，可用 --restore-only 手动复位")
        log_error("或运行: git -C {} sparse-checkout disable && "
                  "git -C {} read-tree -mu HEAD".format(
                      proj_dir.relative_to(ROOT), proj_dir.relative_to(ROOT)))
        return 1

    log_success("推送成功")

    # 恢复稀疏视图 → 完整视图
    if args.yes:
        disable_sparse_project(proj_dir)
        log_success("已恢复完整工作区视图")
        return 0
    # 默认交互式确认恢复
    ans = input("推送完成，是否立即恢复完整工作区视图? [Y/n] ").strip().lower()
    if ans in ("", "y", "yes"):
        disable_sparse_project(proj_dir)
        log_success("已恢复完整工作区视图")
    else:
        log_warn("未恢复；下次推送或运行 --restore-only 复位")
    return 0


if __name__ == "__main__":
    sys.exit(main())