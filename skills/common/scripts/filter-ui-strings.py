#!/usr/bin/env python3
"""filter-ui-strings.py — 从 stringliteral.json 过滤可翻译的英文 UI 字符串。

来源: crackings/<Name>/stages/05-il2cpp-dump/dump/stringliteral.json
输出: 过滤后的 en 字符串清单（唯一、ASCII 英文、合理长度、无路径/格式符噪声）。

过滤规则:
  - 仅含 ASCII 可打印字符
  - 长度 2..120
  - 至少 2 个字母（排除纯数字/符号）
  - 无文件路径 / 无大量 % 占位符 / 无 base64 / 无 URL
  - 排除纯框架噪声（如 "<c# proxy java object>"）
用法:
  python3 filter-ui-strings.py <stringliteral.json> -o <en-strings.txt>
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# 明显非 UI 文本的噪音模式
NOISE = re.compile(
    r"(0x[0-9a-fA-F]{2,}|\.dll|\.so\b|/data/|/system/|/apex/|base64|"
    r"Content-Type|User-Agent|application/json|text/html|multipart|"
    r"http[s]?://|\.unity3d|\.ress\b|\.asset\b|\.prefab\b|\.fbx\b|\.png\b|\.ttf\b|"
    r"il2cpp|mono_|UnityEngine|System\.|^\s*\{|^\s*\}|^\s*\[|^\s*\]|"
    r"\.maxstack|\.locals|\.method|\.end method|\.field|\.property|\.class|"
    r"GetType|ToString|StackTrace|Exception|at System\.)",
    re.IGNORECASE,
)

# 纯框架/代码字符串（常见误报）
FRAMEWORK = {
    "True", "False", "Null", "null", "NULL", "true", "false", "OK", "ok",
    "Cancel", "OK Cancel", "Close", "Open", "Exit", "Quit", "Pause", "Resume",
    "Yes", "No", "None", "All", "On", "Off", "Start", "Stop", "Play", "Stop",
    "Loading...", "Loading", "Save", "Load", "New", "Back", "Next", "Prev",
    "Select", "Deselect", "Remove", "Add", "Edit", "Delete", "Copy", "Paste",
}


def is_ui_string(s: str) -> bool:
    if len(s) < 2 or len(s) > 120:
        return False
    if not all(32 <= ord(c) <= 126 for c in s):
        return False
    if '\n' in s or '\t' in s or '\r' in s:
        return False
    letters = sum(1 for c in s if c.isalpha())
    if letters < 2:
        return False
    if NOISE.search(s):
        return False
    # 排除 JSON/XML/code 片段
    if re.search(r"[{}\[\]<>]", s):
        return False
    # 排除纯空格或单个词加符号
    if re.fullmatch(r"[\s\W_]+", s):
        return False
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input", help="stringliteral.json")
    ap.add_argument("-o", "--out", required=True, help="输出 en 字符串清单")
    ap.add_argument("--max", type=int, default=3000, help="最多输出条数")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    seen: set = set()
    ui: list = []
    for entry in data:
        v = entry.get("value", "") if isinstance(entry, dict) else str(entry)
        if v in seen:
            continue
        if is_ui_string(v):
            seen.add(v)
            ui.append(v)
        if len(ui) >= args.max:
            break
    Path(args.out).write_text("\n".join(ui) + "\n", encoding="utf-8")
    print(f"[OK] {len(ui)} 条 UI 字符串 → {args.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
