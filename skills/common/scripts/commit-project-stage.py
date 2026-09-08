#!/usr/bin/env python3
"""commit-project-stage.py — 每完成一个子阶段，在项目独立 git 仓库内提交一次，支持回滚。

用途:
  - 每完成一个子阶段（或一个主阶段）调用一次，把阶段产物/报告/脚本/state 快照入库，
    形成可回滚的历史节点。
  - 回滚时用 `git -C crackings/<type>/<Name> reset --hard <提交>`（脚本只读、不回写文件，
    避免 git 副作用污染阶段产物；需要回滚请人工执行 reset/revert）。

用法:
  python3 commit-project-stage.py --name <Name> --stage 03-sdk-network-removal [--type <type>] [--message "备注"] [--dry-run]

  --stage 阶段标识（如 03-sdk-network-removal / M2-assess / 09-font-replace），并入提交信息便于定位回滚点。

可选:
  --type <type>      多候选时消歧（crackings/<type>）
  --message "备注"    追加备注
  --dry-run          只预览将提交的变更，不真正提交
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
        log_warn(f"[commit-project-stage] 匹配到多个候选: {found}，请用 --type 消歧")
        return None
    cand = CRACKINGS_DIR / name
    if cand.is_dir():
        return cand
    return None


def git(proj_dir: Path, *args):
    return subprocess.run(["git", "-C", str(proj_dir), *args], capture_output=True, text=True)


def main() -> int:
    ensure_env()
    ap = argparse.ArgumentParser(description="项目独立 git 仓库：阶段提交（回滚节点）")
    ap.add_argument("--name", required=True, help="项目名")
    ap.add_argument("--stage", required=True, help="阶段标识，如 03-sdk-network-removal / M2-assess")
    ap.add_argument("--type", default=None, help="引擎类型父目录（多候选消歧）")
    ap.add_argument("--message", default="", help="追加备注")
    ap.add_argument("--dry-run", action="store_true", help="只预览变更，不提交")
    args = ap.parse_args()

    proj_dir = locate_project(args.name, args.type)
    if not proj_dir:
        log_error(f"未定位到项目: crackings/**/{args.name}")
        return 1
    if not (proj_dir / ".git").exists():
        log_error(f"项目尚无独立 git 仓库: {proj_dir.relative_to(ROOT)}")
        log_error("请先运行: python3 skills/common/scripts/init-project-git.py --name <Name>")
        return 1

    log_step(f"阶段提交预览（{args.stage}）: {proj_dir.relative_to(ROOT)}")
    r = git(proj_dir, "status", "--short")
    changed = [ln for ln in r.stdout.splitlines() if ln.strip()]
    if not changed:
        log_warn("工作区无变更，无需提交")
        return 0

    n = len(changed)
    print(f"将提交 {n} 条变更:")
    for ln in changed[:20]:
        print(f"    {ln}")
    if n > 20:
        print(f"    … 共 {n} 条")

    if args.dry_run:
        log_info("--dry-run: 仅预览，未提交")
        return 0

    # 提交信息
    msg = f"stage: {args.stage}"
    if args.message:
        msg += f" — {args.message}"
    subprocess.run(["git", "-C", str(proj_dir), "add", "-A"], check=True)
    cr = git(proj_dir, "commit", "-m", msg)
    if cr.returncode == 0:
        log_success(f"已提交: {msg}")
        # 显示当前简短 hash + 提交数
        h = git(proj_dir, "rev-parse", "--short", "HEAD").stdout.strip()
        cnt = git(proj_dir, "rev-list", "--count", "HEAD").stdout.strip()
        log_info(f"HEAD={h}  累计提交数={cnt}")
        log_info("回滚方式: "
                 f"git -C {proj_dir.relative_to(ROOT)} reset --hard <commit-hash>")
        return 0
    if cr.returncode == 1 and "no changes" in cr.stderr.lower():
        log_warn("无变更可提交")
        return 0
    log_error(f"提交失败: {cr.stderr.strip()}")
    return 1


if __name__ == "__main__":
    sys.exit(main())