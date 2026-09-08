#!/usr/bin/env python3
"""init-status-yaml.py - init status.yaml."""
import argparse, hashlib, os, re, sys
from datetime import datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[3]


def scan_status_md(name, type=None):
    if type:
        p = ROOT / "crackings" / type / name / "status.yaml"
    else:
        p = ROOT / "crackings" / name / "status.yaml"
    if not p.is_file():
        return {}
    text = p.read_text(encoding="utf-8", errors="ignore")
    fm = re.search(r"PASS=(\d+)\s+FAIL=(\d+)\s+SKIP=(\d+)", text)
    ls = "unknown"
    lm = re.search(r"### \[(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\]\s+([^\n]+)", text)
    if lm:
        ls = lm.group(2).strip()
    return {
        "fp": int(fm.group(1)) if fm else 0,
        "ff": int(fm.group(2)) if fm else 0,
        "fs": int(fm.group(3)) if fm else 0,
        "ls": ls,
    }


def scan_stages(name, type=None):
    if type:
        d = ROOT / "crackings" / type / name / "stages"
    else:
        d = ROOT / "crackings" / name / "stages"
    if not d.is_dir():
        return []
    return sorted([x.name for x in d.iterdir() if x.is_dir()])


def get_apk(name, type=None):
    if type:
        md5_file = ROOT / "crackings" / type / name / "source.apk.md5"
        if md5_file.is_file():
            for line in md5_file.read_text(encoding="utf-8", errors="ignore").splitlines():
                if line.startswith("source="):
                    source = Path(line.split("=", 1)[1].strip())
                    if source.is_file():
                        digest = hashlib.md5(source.read_bytes()).hexdigest()
                        return str(source.relative_to(ROOT)), digest
    d = ROOT / "apks"
    apks = list(d.glob("*.apk")) + list(d.glob("*.xapk"))
    f = ""
    for a in apks:
        if name.lower() in a.name.lower():
            f = a.name
            break
    if not f and apks:
        f = apks[0].name
    md5 = ""
    if f:
        md5 = hashlib.md5((d / f).read_bytes()).hexdigest()
    return f, md5


def get_output(name, type=None):
    r = {"pa": False, "as": False, "sz": 0}
    if type:
        d = ROOT / "output-projects" / type / name
    else:
        d = ROOT / "output-projects" / name
    if not d.is_dir():
        return r
    a = d / "patched.apk"
    if a.is_file():
        r["pa"] = True
        r["sz"] = round(a.stat().st_size / 1024 / 1024, 1)
    if (d / "app-as-generated").is_dir() or (d / "app").is_dir():
        r["as"] = True
    return r


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--name", required=True)
    p.add_argument("--type", default=None)
    a = p.parse_args()
    n = a.name
    t = a.type
    if t:
        cd = ROOT / "crackings" / t / n
    else:
        cd = ROOT / "crackings" / n
    yp = cd / "status.yaml"
    if not cd.is_dir():
        print(f"missing: {cd}")
        return 1
    af, md5 = get_apk(n, t)
    oi = get_output(n, t)
    si = scan_status_md(n, t)
    ss = scan_stages(n, t)
    cmp, skp, fad = [], [], []
    smap = {
        "01-fake-android": "sniff",
        "06-hook-plan": "3rd-party-sdk-removal",
        "09-third-party-cleanup": "3rd-party-sdk-removal",
        "10-ui-hide": "ui-hide",
        "11-ui-hide": "ui-hide-device-verify",
        "15-hanization": "text-hanization",
    }
    for sd in ss:
        for k, v in smap.items():
            if sd.startswith(k):
                if "failed" in sd.lower():
                    fad.append(v)
                else:
                    cmp.append(v)
                break
    cs = si.get("ls", "unknown")
    now = datetime.now().strftime("%Y-%m-%d")
    data = {
        "project": {
            "name": n,
            "source_apk": f"apks/{af}",
            "md5": md5,
            "type": a.type or "",
            "created": a.type or "",
            "last_updated": now,
        },
        "status": {
            "phase": "deliver",
            "stage": cs,
            "grade": "D",
            "is_delivered": oi["pa"],
            "final_pass": si.get("fp", 0),
            "final_fail": si.get("ff", 0),
            "final_skip": si.get("fs", 0),
            "completed_stages": cmp,
            "skipped": skp,
            "failed_stages": fad,
            "current_stage": cs,
        },
        "artifacts": {
            "patched_apk": oi["pa"],
            "as_project": oi["as"],
            "apk_size_mb": oi["sz"],
            "findings_md": True,
            "dir_index_md": True,
        },
        "stages_detail": {
            "stages_dirs": ss,
        },
    }
    yp.write_text("# auto-generated\n" + yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"OK: {yp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
