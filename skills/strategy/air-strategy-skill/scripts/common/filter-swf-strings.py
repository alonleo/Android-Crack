#!/usr/bin/env python3
"""
filter-swf-strings.py — 从 SWF 原始字符串中过滤出 UI 文本，生成翻译 TSV

用法:
  python3 filter-swf-strings.py <raw_strings.txt> [-o <output.tsv>]

输出 TSV 格式: 原文<TAB>译文
  译文默认与原文相同（需要人工编辑或调用 baoyu-translate）
"""

import re
import sys
import os


# 常见英文游戏 UI 词汇
UI_WORDS = {
    "play", "start", "game", "level", "menu", "back", "next", "save", "exit",
    "done", "ok", "cancel", "yes", "no", "on", "off", "new", "load", "quit",
    "retry", "resume", "score", "time", "mode", "gold", "coin", "life", "heart",
    "key", "door", "unlock", "open", "close", "enter", "leave", "pause",
    "setting", "option", "help", "info", "about", "shop", "buy", "sell",
    "upgrade", "power", "boost", "speed", "jump", "run", "walk", "hide",
    "find", "search", "collect", "escape", "win", "lose", "die", "dead",
    "level", "stage", "world", "map", "chapter", "mission", "quest", "task",
    "player", "enemy", "friend", "item", "weapon", "armor", "shield", "potion",
    "continue", "restart", "select", "choose", "confirm", "decline", "accept",
    "sound", "music", "volume", "language", "tutorial", "hint", "tip",
    "loading", "connecting", "waiting", "ready", "go", "finish", "complete",
    "victory", "defeat", "gameover", "game over", "you win", "you lose",
    "score", "highscore", "high score", "best", "record", "rank", "rating",
    "facebook", "google", "twitter", "share", "invite", "gift", "reward",
    "daily", "bonus", "free", "premium", "vip", "removeads", "remove ads",
    "no ads", "watch", "video", "interstitial", "banner", "rewarded",
    "privacy", "policy", "terms", "agree", "disagree", "rate", "review",
    "more", "apps", "games", "version", "update", "what's new", "whats new",
    # Can You Escape 2 specific
    "escape", "room", "door", "key", "lock", "box", "puzzle", "hint",
    "tap", "swipe", "drag", "drop", "rotate", "push", "pull", "slide",
}

# 必须排除的模式 (正则)
EXCLUDE_PATTERNS = [
    r'^[^a-zA-Z]*$',                    # 纯非字母
    r'^[A-Z][a-z]{1,3}$',               # 2-4 字母大写开头（变量名）
    r'^[a-z]{2,4}$',                    # 2-4 字母全小写（变量名）
    r'^[a-z]+_[a-z0-9_]+$',             # snake_case
    r'^[a-zA-Z]+([A-Z][a-z]+)+$',       # camelCase 且无空格
    r'^this\.',                          # this.xxx
    r'^//|^/\*|^\*|^#|^<\?|^<!|^\[|^\{', # 代码注释/结构
    r'^[a-z]+\.[A-Z]',                   # Class.Method
    r'^\d+[a-zA-Z]',                     # 数字开头字母 (2d, 3d, 4k)
    r'^[0-9a-fA-F]{8,}$',               # 长十六进制
    r'^.+\\[nr]',                        # 含转义
    r'^[A-Z_]{3,}$',                    # 全大写+下划线 (常量)
    r'^[a-z]+\.[a-z]+\.[a-z]+',         # 包名
    r'\.(js|as|java|xml|json)$',        # 文件名
]


def is_ui_text(s: str) -> bool:
    """判断字符串是否为 UI 文本"""
    if len(s) < 4 or len(s) > 250:
        return False
    if not any(c.isalpha() for c in s):
        return False

    # 排除模式检查
    for pat in EXCLUDE_PATTERNS:
        if re.match(pat, s):
            return False

    # 包含空格 → 很可能是 UI 文本（句子/短语）
    if ' ' in s:
        # 但不是只有标点
        word_count = len([w for w in s.split() if any(c.isalpha() for wc in w for c in wc)])
        if word_count >= 2:
            return True
        # 单个长词含常见 UI 词
        if any(w.lower() in UI_WORDS for w in s.split()):
            return True

    # 无空格但匹配 UI 词汇
    if s.lower() in UI_WORDS:
        return True
    if s.lower().startswith(tuple(w for w in UI_WORDS if len(w) > 4)):
        return True

    # 首字母大写 + 至少 5 字符 + 含常见词
    if s[0].isupper() and len(s) >= 5:
        if any(w in s.lower() for w in ['the', 'you', 'your', 'and', 'for', 'with', 'this', 'that']):
            return True

    return False


def filter_swf_strings(input_file: str, output_file: str):
    """过滤 SWF 字符串并输出翻译 TSV"""
    with open(input_file, 'r', encoding='utf-8', errors='ignore') as f:
        lines = [l.strip() for l in f if l.strip()]

    seen = set()
    ui_strings = []

    for s in lines:
        if s in seen:
            continue
        seen.add(s)

        if is_ui_text(s):
            ui_strings.append(s)

    # 去重并排序
    ui_strings = sorted(set(ui_strings), key=lambda x: (len(x), x))

    # 输出 TSV (译文默认=原文)
    with open(output_file, 'w', encoding='utf-8') as f:
        for s in ui_strings:
            f.write(f'{s}\t{s}\n')

    stats = {
        'total': len(lines),
        'ui': len(ui_strings),
        'short': sum(1 for s in ui_strings if len(s) < 10),
        'medium': sum(1 for s in ui_strings if 10 <= len(s) < 30),
        'long': sum(1 for s in ui_strings if len(s) >= 30),
        'multi_word': sum(1 for s in ui_strings if ' ' in s),
    }

    return stats


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[3] if '-o' in sys.argv and len(sys.argv) > sys.argv.index('-o') + 1 else \
        os.path.join(os.path.dirname(input_file), 'swf_ui_strings.tsv')

    if not os.path.exists(input_file):
        print(f"Error: 文件不存在: {input_file}")
        sys.exit(1)

    stats = filter_swf_strings(input_file, output_file)

    print(f"总字符串:        {stats['total']}")
    print(f"UI 文本:         {stats['ui']}")
    print(f"  短 (<10):      {stats['short']}")
    print(f"  中 (10-29):    {stats['medium']}")
    print(f"  长 (≥30):      {stats['long']}")
    print(f"  多词:          {stats['multi_word']}")
    print(f"输出:            {output_file}")
    print()
    print("提示: 编辑 TSV 的第二列填入中文翻译，然后运行:")
    print(f"  ./skills/common/scripts/air-localization/patch-swf-translations.sh <Name> --tsv {output_file}")
