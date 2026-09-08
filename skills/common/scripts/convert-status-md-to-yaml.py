#!/usr/bin/env python3
"""convert-status-md-to-yaml.py — 将所有 status.md 转换为 status.yaml 并删除原文件。"""
import re, sys, yaml
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
# skills/common/scripts/ → tools/ → repo root
assert (ROOT / "AGENTS.md").exists(), f"ROOT 路径错误: {ROOT}"
CRACKINGS = ROOT / "crackings"

# 旧格式阶段编号 → 新编号
STAGE_MAP = {
    "00a-assess": "00a", "00a": "00a",
    "01-record": "01", "01": "01",
    "02-preprocess": "02", "02": "02",
    "03-static-analyze": "03", "03": "03",
    "4-entry-points": "04", "04": "04",
    "05-strings": "05", "05": "05",
    "06-ocr": "06", "06": "06",
    "07-redraw": "07", "07": "07",
    "08-fonts": "08", "08": "08",
    "9-stub-sdks": "09", "09": "09",
    "10-repack-sign": "10", "10": "10",
    "11-runtime-verify": "11", "11": "11",
    "12-as-build": "12", "12": "12",
    "13-final-check": "13", "13": "13",
    "14-device-verify": "14", "14": "14",
    "15-cleanup": "15", "15": "15",
    "16": "16", "17-repack-sign": "17", "17": "17",
    "18": "18", "19-as-build": "19", "19": "19",
    "20-final-check": "20", "20": "20",
    "21-cleanup": "21", "21": "21",
    # il2cpp
    "01-fake-android": "01", "01-fake-android": "01",
    "05-il2cpp-dump": "05", "05-hook-fn-analyze": "05",
    "06-hook-plan": "06", "10-ui-hide": "10",
    "11-ui-hide": "11", "15-hanization": "15",
    "13-feature-removal": "13", "14-device-verify": "14",
    "08-device-verify": "08",
}


def parse_source_apk(text: str) -> str:
    for line in text.splitlines():
        if "源文件" in line or "source_apk" in line.lower() or "source" in line.lower():
            m = re.search(r'[`*"\'"]?([apks/][^`*"\'`\s]+\.apk)', line)
            if m:
                return m.group(1)
    # fallback: glob apks/
    return ""


def parse_type(text: str) -> str:
    for line in text.splitlines():
        if "类型" in line and "type" in line.lower():
            m = re.search(r'[`\*"]?(android|il2cpp|unity-mono|cocos2dx|cocos-creator|unreal|flutter|xamarin|air|defold|gamemaker|libgdx)[`\*"\s,]', line, re.IGNORECASE)
            if m:
                return m.group(1).lower()
    return ""


def parse_md5(text: str) -> str:
    for line in text.splitlines():
        if "md5" in line.lower():
            m = re.search(r'[`\*"]?([a-f0-9]{32})[`\*"\s,]', line, re.IGNORECASE)
            if m:
                return m.group(1)
    return ""


def parse_progress(text: str):
    """从 status.md 提取已完成阶段和当前阶段。"""
    completed = set()
    current_stage = ""
    grade = "D"
    final_pass = final_fail = final_skip = 0

    # 匹配 Agent-script 条目
    agent_pattern = re.compile(
        r'###\s+\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s*Agent-script\s*·\s*阶段\s+(\S+)'
    )
    # 匹配纯阶段条目
    stage_pattern = re.compile(
        r'###\s+(?:\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+)?阶段(\d{2}[a-z]?):'
    )
    # 匹配 PASS/FAIL
    pf_pattern = re.compile(r'PASS=(\d+)\s+FAIL=(\d+)\s+SKIP=(\d+)')
    # 匹配 grade
    grade_pattern = re.compile(r'grade\s*=\s*([A-F])', re.IGNORECASE)

    lines = text.splitlines()
    entries = []

    for i, line in enumerate(lines):
        m = agent_pattern.search(line)
        if m:
            ts, stage = m.group(1), m.group(2)
            entries.append(("agent", ts, stage))
            continue
        m = stage_pattern.search(line)
        if m:
            stage = m.group(1)
            entries.append(("stage", "", stage))
            continue
        m = pf_pattern.search(line)
        if m:
            final_pass = int(m.group(1))
            final_fail = int(m.group(2))
            final_skip = int(m.group(3))
        m = grade_pattern.search(line)
        if m:
            grade = m.group(1).upper()

    # 去重，保留时间顺序
    seen = set()
    for kind, ts, stage in reversed(entries):
        sid = STAGE_MAP.get(stage, stage)
        if sid not in seen:
            seen.add(sid)
            completed.add(sid)

    if entries:
        _, last_ts, last_stage = entries[-1]
        current_stage = STAGE_MAP.get(last_stage, last_stage)

    return {
        "completed_stages": sorted(completed, key=lambda x: (not x.isdigit(), x)),
        "current_stage": current_stage,
        "grade": grade,
        "final_pass": final_pass,
        "final_fail": final_fail,
        "final_skip": final_skip,
    }


def parse_timeline(text: str):
    """从 status.md 提取时间线作为 yaml 列表。"""
    entries = []
    # 匹配所有条目
    patterns = [
        re.compile(r'###\s+\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\]\s*(.+?)(?=\n###|\n##|\Z)'),
        re.compile(r'###\s+(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})\s+阶段(\S+):?\s*(.*?)(?=\n###|\n##|\Z)'),
    ]
    for p in patterns:
        for m in p.finditer(text):
            if len(m.groups()) >= 3:
                ts = m.group(1)
                rest = m.group(2) + m.group(3) if p == patterns[1] else m.group(2)
                entries.append({"timestamp": ts, "description": rest.strip()})
    # 去重按时间排序
    seen = set()
    unique = []
    for e in reversed(entries):
        key = e["timestamp"]
        if key not in seen:
            seen.add(key)
            unique.append(e)
    return list(reversed(unique))


def convert_file(md_path: Path) -> bool:
    text = md_path.read_text(encoding="utf-8", errors="ignore")
    proj = parse_progress(text)

    # 提取项目名
    name = md_path.parent.name
    proj_type = parse_type(text)
    if not proj_type:
        # 尝试从父目录名
        proj_type = md_path.parent.parent.name

    source_apk = parse_source_apk(text)
    md5 = parse_md5(text)

    # 判定是否交付
    patched = md_path.parent / "patched.apk"
    is_delivered = patched.exists()

    # 判定 phase
    phase = "stages"
    if is_delivered:
        phase = "deliver"
    if "as_project" in text.lower() or (md_path.parent / "app").exists():
        phase = "verify"

    data = {
        "project": {
            "name": name,
            "source_apk": source_apk,
            "type": proj_type,
            "created": "",
            "last_updated": proj.get("last_updated", ""),
        },
        "status": {
            "phase": phase,
            "stage": proj.get("current_stage", ""),
            "grade": proj.get("grade", "D"),
            "is_delivered": is_delivered,
            "is_archived": False,
            "completed_stages": proj.get("completed_stages", []),
            "skipped": [],
            "failed_stages": [],
            "current_stage": proj.get("current_stage", ""),
            "final_pass": proj.get("final_pass", 0),
            "final_fail": proj.get("final_fail", 0),
            "final_skip": proj.get("final_skip", 0),
        },
        "artifacts": {
            "patched_apk": is_delivered,
            "as_project": (md_path.parent / "app-as-generated").exists() or (md_path.parent / "app").exists(),
            "findings_md": (md_path.parent / "findings.md").exists(),
            "dir_index_md": (md_path.parent / "dir-index.yaml").exists(),
        },
        "timeline": parse_timeline(text)[:50],  # 最多保留最近50条
    }

    yaml_path = md_path.with_suffix(".yaml")
    yaml_path.write_text(
        "# auto-generated from status.md\n" + yaml.dump(data, allow_unicode=True, sort_keys=False, width=200),
        encoding="utf-8",
    )
    print(f"  {yaml_path.relative_to(ROOT)} ← {md_path.relative_to(ROOT)}")
    return True


def main():
    status_files = list(CRACKINGS.glob("**/status.md"))
    if not status_files:
        print("未找到 status.md 文件")
        return

    print(f"找到 {len(status_files)} 个 status.md，开始转换...\n")
    converted = 0
    for md_path in sorted(status_files):
        try:
            convert_file(md_path)
            md_path.unlink()
            print(f"  删除 {md_path.relative_to(ROOT)}")
            converted += 1
        except Exception as e:
            print(f"  错误 {md_path}: {e}")

    print(f"\n完成：{converted}/{len(status_files)} 个 status.md → status.yaml")


if __name__ == "__main__":
    sys.exit(main())
