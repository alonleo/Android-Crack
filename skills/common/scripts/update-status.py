#!/usr/bin/env python3
"""
update-status.py — Agent 查询/更新 status.yaml 的脚本

用法（Agent 调用）:
  # 查询项目当前状态（打印 human-readable 摘要）
  update-status.py <Name> --show

  # 初始化新项目的 status.yaml
  update-status.py <Name> --init [--type <type>] [--source-apk <path>] [--md5 <hash>]

  # 更新指定字段（dot 路径，如 status.phase / project.name）
  update-status.py <Name> --set status.phase=stages status.stage=07

  # 添加已完成阶段到列表
  update-status.py <Name> --add-completed 07

  # 设置难度评级
  update-status.py <Name> --set-grade B

  # 标记交付 / 归档
  update-status.py <Name> --mark-delivered
  update-status.py <Name> --mark-archived

  # 追加 notes 内容
  update-status.py <Name> --add-note "[FLOWFIX] xxx 修复"

  # 强制重写整个文件（谨慎使用）
  update-status.py <Name> --replace-all "<完整 YAML 文本>"

示例:
  update-status.py KingdomWars2 --show
  update-status.py KingdomWars2 --set status.phase=stages status.stage=07
  update-status.py KingdomWars2 --add-completed 06
  update-status.py MiniCarRacing --init --type il2cpp --source-apk apks/MiniCarRacing.apk --md5 a1b2c3d4
"""
import argparse, re, sys, yaml
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

# ── 路径 ────────────────────────────────────────────────────────────────

def status_path(name):
    p = ROOT / "crackings" / name / "status.yaml"
    if not p.exists():
        # 尝试带 type 的路径
        for type_dir in (ROOT / "crackings").iterdir():
            if type_dir.is_dir():
                p2 = type_dir / name / "status.yaml"
                if p2.exists():
                    return p2
    return p


# ── 读写 ────────────────────────────────────────────────────────────────

def read_status(name):
    path = status_path(name)
    if not path.exists():
        return None, None
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    return data, path


def write_status(path, data):
    text = yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    path.write_text(f"# {path.name} — 最后更新: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                    + text, encoding="utf-8")


# ── 展示（Agent 查询用） ──────────────────────────────────────────────

def show_status(name):
    data, path = read_status(name)
    if data is None:
        print(f"[ERROR] status.yaml 不存在: {path}")
        return False

    proj = data.get("project", {})
    st    = data.get("status", {})
    arts  = data.get("artifacts", {})
    notes = data.get("notes", "")

    print(f"""
=== {proj.get('name', name)} ===
  源 APK : {proj.get('source_apk', '—')}
  MD5    : {proj.get('md5', '—')}
  类型   : {proj.get('type', '—')}
  创建   : {proj.get('created', '—')}
  更新   : {proj.get('last_updated', '—')}

状态:
  phase  : {st.get('phase', '—')}
  stage  : {st.get('stage', '—')}
  grade  : {st.get('grade', '—')}
  current: {st.get('current_stage', '—')}
  已完成 : {st.get('completed_stages', [])}
  失败   : {st.get('failed_stages', [])}
  跳过   : {st.get('skipped', [])}
  已交付 : {st.get('is_delivered', False)}
  已归档 : {st.get('is_archived', False)}

产物:
  patched.apk : {arts.get('patched_apk', False)}
  AS 工程    : {arts.get('as_project', False)}
  apk 大小   : {arts.get('apk_size_mb', '—')} MB

备注:
{notes if notes else '  (无)'}""")
    return True


# ── 字段更新 ──────────────────────────────────────────────────────────

def set_field(data, key, value):
    """dot 路径写入，如 status.phase → data['status']['phase'] = value"""
    keys = key.split(".")
    d = data
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    last = keys[-1]
    # 布尔值
    if value.lower() in ("true", "yes", "1"):
        value = True
    elif value.lower() in ("false", "no", "0"):
        value = False
    # 列表（逗号分隔）
    elif "," in value:
        value = [v.strip() for v in value.split(",") if v.strip()]
    d[last] = value


def update_status(name, updates):
    data, path = read_status(name)
    if data is None:
        print(f"[ERROR] status.yaml 不存在: {path}")
        return False
    for key, value in updates.items():
        set_field(data, key, value)
    data.setdefault("project", {})["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    write_status(path, data)
    print(f"[OK] 已更新: {path}")
    return True


# ── 初始化 ────────────────────────────────────────────────────────────

def init_status(name, args):
    # [FLOWFIX 2026-08-30] --type 必传；status.yaml 必须落在 crackings/<type>/<Name>/
    # 原 status_path() 在 init 时无 type 时默认 crackings/<Name>/，违反 AGENTS.md §3。
    if args.type:
        path = ROOT / "crackings" / args.type / name / "status.yaml"
    else:
        # 退化路径：保持原 status_path() 行为（先查 crackings/<type>/<Name>/ 再查 crackings/<Name>/）
        path = status_path(name)
    if path.exists():
        print(f"[WARN] status.yaml 已存在，先查看当前内容: {path}")
        show_status(name)
        return False

    parent = path.parent
    if not parent.exists():
        parent.mkdir(parents=True, exist_ok=True)

    now = datetime.now().strftime("%Y-%m-%d")
    data = {
        "project": {
            "name": name,
            "source_apk": f"apks/{args.source_apk}" if args.source_apk else "",
            "md5": args.md5 or "",
            "type": args.type or "",
            "created": now,
            "last_updated": now,
        },
        "status": {
            "phase": "sniff",
            "stage": "",
            "grade": "D",
            "current_stage": "",
            "completed_stages": [],
            "failed_stages": [],
            "skipped": [],
            "is_delivered": False,
            "is_archived": False,
        },
        "artifacts": {
            "patched_apk": False,
            "as_project": False,
            "apk_size_mb": 0,
            "findings_md": False,
            "dir_index_md": False,
        },
        "notes": "",
    }
    write_status(path, data)
    print(f"[OK] 已创建: {path}")
    return True


# ── 追加已完成阶段 ─────────────────────────────────────────────────────

def add_completed(name, stage_id):
    data, path = read_status(name)
    if data is None:
        print(f"[ERROR] status.yaml 不存在: {path}")
        return False
    st = data.setdefault("status", {})
    completed = st.get("completed_stages", [])
    if stage_id not in completed:
        completed.append(stage_id)
        # 排序
        def sort_key(s):
            m = re.match(r"(\d+)", s)
            return int(m.group(1)) if m else 999
        completed.sort(key=sort_key)
        st["completed_stages"] = completed
    st["current_stage"] = stage_id
    data.setdefault("project", {})["last_updated"] = datetime.now().strftime("%Y-%m-%d")
    write_status(path, data)
    print(f"[OK] 已添加 completed_stages += {stage_id}")
    return True


# ── 追加 notes ────────────────────────────────────────────────────────

def add_note(name, note_text):
    data, path = read_status(name)
    if data is None:
        print(f"[ERROR] status.yaml 不存在: {path}")
        return False
    notes = data.get("notes", "")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    if notes:
        notes += f"\n{ts} {note_text}"
    else:
        notes = f"{ts} {note_text}"
    data["notes"] = notes
    data.setdefault("project", {})["last_updated"] = ts
    write_status(path, data)
    print(f"[OK] 备注已追加")
    return True


# ── CLI ────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description="status.yaml 查询与更新 — Agent 专用")
    p.add_argument("name", help="项目名称（目录名）")
    p.add_argument("--show", action="store_true", help="查询并打印项目状态（human-readable）")
    p.add_argument("--init", action="store_true", help="初始化新项目的 status.yaml")
    p.add_argument("--type", help="项目类型（il2cpp / android / cocos2dx 等）")
    p.add_argument("--source-apk", dest="source_apk", help="源 APK 相对路径（相对于 apks/）")
    p.add_argument("--md5", help="源 APK MD5")
    p.add_argument("--set", nargs="+", metavar="KEY=VALUE", help="设置字段，如 status.phase=stages")
    p.add_argument("--add-completed", dest="add_completed", metavar="STAGE_ID",
                   help="添加已完成阶段 ID 到 completed_stages")
    p.add_argument("--set-grade", dest="set_grade", metavar="GRADE",
                   help="设置难度评级 (S/A/B/C/D/F)")
    p.add_argument("--mark-delivered", action="store_true", help="标记 is_delivered = true")
    p.add_argument("--mark-archived", action="store_true", help="标记 is_archived = true")
    p.add_argument("--add-note", dest="add_note", metavar="TEXT", help="追加备注")
    p.add_argument("--replace-all", dest="replace_all", metavar="YAML_TEXT",
                   help="[谨慎] 用完整 YAML 文本替换整个文件")
    args = p.parse_args()

    # --show 优先
    if args.show:
        show_status(args.name)
        return

    # --init
    if args.init:
        ok = init_status(args.name, args)
        sys.exit(0 if ok else 1)

    # --replace-all
    if args.replace_all:
        path = status_path(args.name)
        if not path.exists():
            print(f"[ERROR] 文件不存在: {path}")
            sys.exit(1)
        path.write_text(args.replace_all, encoding="utf-8")
        print(f"[OK] 文件已替换: {path}")
        return

    # 解析 --set
    updates = {}
    if args.set:
        for item in args.set:
            if "=" not in item:
                print(f"[ERROR] --set 参数格式应为 KEY=VALUE，实际: {item}")
                sys.exit(1)
            k, v = item.split("=", 1)
            updates[k.strip()] = v.strip()

    # --set-grade 是 --set status.grade=X 的简写
    if args.set_grade:
        updates["status.grade"] = args.set_grade

    # --mark-delivered / --mark-archived
    if args.mark_delivered:
        updates["status.is_delivered"] = "true"
    if args.mark_archived:
        updates["status.is_archived"] = "true"

    # --add-completed
    if args.add_completed:
        ok = add_completed(args.name, args.add_completed)
        sys.exit(0 if ok else 1)

    # --add-note
    if args.add_note:
        ok = add_note(args.name, args.add_note)
        sys.exit(0 if ok else 1)

    # --set 字段更新
    if updates:
        ok = update_status(args.name, updates)
        sys.exit(0 if ok else 1)
        return

    # 无任何操作
    p.print_help()


if __name__ == "__main__":
    main()
