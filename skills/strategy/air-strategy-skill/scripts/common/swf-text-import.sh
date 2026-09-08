#!/usr/bin/env bash
# swf-text-import.sh — 把 zh-CN.tsv 写回 ffdec 格式的文本目录
# 用法：swf-text-import.sh <zh-CN.tsv> <ffdec-export-dir>
#
# 输出：<ffdec-export-dir>/<chid>.txt（中文译文）
#       同时打印 覆盖率统计

set -eu
TSV="$1"
DIR="$2"
mkdir -p "$DIR"

if [[ ! -f "$TSV" ]]; then
    echo "tsv not found: $TSV" >&2
    exit 1
fi

total_zh=0
written=0
while IFS=$'\t' read -r chid en zh; do
    [[ "$chid" =~ ^# ]] && continue
    [[ -z "$chid" ]] && continue
    [[ "$en" == "$zh" ]] && continue   # 没翻译的跳过
    total_zh=$((total_zh + 1))
    out="$DIR/$chid.txt"
    if [[ -n "$zh" ]]; then
        printf '%s' "$zh" > "$out"
        written=$((written + 1))
    fi
done < "$TSV"

echo "[+] $written/$total_zh 个 chid 写入到 $DIR"
