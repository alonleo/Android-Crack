#!/usr/bin/env bash
# ============================================================================
# install-tools.sh — 下载所有 Android 逆向工具项目（Linux / macOS 通用）
# ============================================================================
# 说明：
#   - 读取同目录下的 tools-source-registry.txt，逐个 git clone 到
#     tools/crack-intergration-tools/source-projects/<目标目录>/
#   - 不改动系统环境、不污染 PATH；仅克隆源码项目。
#   - 现有 Hermes 官方 install.sh 与本脚本无关（本脚本不修改它）。
#   - dex2jar / FixStackmaps 为已内置的非 git 项目，不参与克隆（registry 已注明）。
#
# 用法：
#   bash skills/common/scripts/install-tools.sh [--force] [--full] [--only 名称] [--list]
#
#   选项：
#     --list        只打印 registry 中的工具清单，不下载
#     --force       已存在目录也重新克隆（默认已存在则跳过）
#     --full        完整克隆全部历史（默认浅克隆 --depth 1，省流量/磁盘）
#     --only 名称   只克隆指定工具（registry 中第 1 列的名字，可多次指定）
#     --yes         静默跳过确认（配合手动运行）
#
# 环境：
#   中国大陆网络下若直连 GitHub 慢，可在命令前 export GIT_PROXY_URL 指向镜像，
#   脚本会用 ${GIT_PROXY_URL}${url%??} 形式拼接（可选，默认直连）。
# ============================================================================

set -euo pipefail

# 定位脚本所在目录（兼容 symlink 与各 CWD 调用）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REGISTRY="${SCRIPT_DIR}/tools-source-registry.txt"
# 仓库根（skills/common/scripts 的 3 级上 = 仓库根）
REPO_ROOT="$(cd "${SCRIPT_DIR}/../../.." && pwd)"
SRC_DIR="${REPO_ROOT}/tools/crack-intergration-tools/source-projects"

FORCE=0
FULL=0
ONLY=()
DO_LIST=0
ASSUME_YES=0

# ── 颜色（自动关闭当非 TTY）──
if [ -t 1 ]; then
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[0;33m'
    BLUE='\033[0;34m'; CYAN='\033[0;36m'; NC='\033[0m'
else
    RED=''; GREEN=''; YELLOW=''; BLUE=''; CYAN=''; NC=''
fi

log_info()    { echo -e "${CYAN}→${NC} $*"; }
log_ok()      { echo -e "${GREEN}✓${NC} $*"; }
log_warn()    { echo -e "${YELLOW}⚠${NC} $*"; }
log_err()     { echo -e "${RED}✗${NC} $*" >&2; }

print_usage() {
    echo "install-tools.sh — 下载 Android 逆向工具项目源码"
    echo ""
    echo "用法: bash ${BASH_SOURCE[0]##*/} [选项]"
    echo ""
    echo "选项:"
    echo "  --list            列出 registry 中的工具清单（不下载）"
    echo "  --force           已存在目录也重新克隆"
    echo "  --full            完整克隆（默认浅克隆 --depth 1）"
    echo "  --only 名称       只克隆指定工具（可多次）"
    echo "  --yes             跳过开始前的确认提示"
    echo "  -h, --help        显示帮助"
}

# ── 参数解析 ──
while [[ $# -gt 0 ]]; do
    case "$1" in
        --list)      DO_LIST=1; shift ;;
        --force|-f)  FORCE=1; shift ;;
        --full)      FULL=1; shift ;;
        --only)      ONLY+=("$2"); shift 2 ;;
        --yes)       ASSUME_YES=1; shift ;;
        -h|--help)   print_usage; exit 0 ;;
        *) echo "未知选项: $1"; print_usage; exit 1 ;;
    esac
done

if [ ! -f "${REGISTRY}" ]; then
    log_err "找不到工具来源清单: ${REGISTRY}"
    log_err "请确认已将 tools-source-registry.txt 与脚本放在同一目录。"
    exit 1
fi

# ── 解析 registry：跳过注释/空行，按 | 拆分 ──
mapfile -t RAW_LINES < "${REGISTRY}"
declare -A NAME_URL=()
declare -A NAME_DESC=()
declare -a NAME_ORDER=()
while IFS= read -r line; do
    line="${line//$'\r'/}"                       # 去 CR（防 Windows 编辑换行）
    [[ -z "${line}" || "${line}" == \#* ]] && continue
    IFS='|' read -r name url desc <<< "${line}"
    [ -z "${name}" ] && continue
    NAME_URL["${name}"]="${url}"
    NAME_DESC["${name}"]="${desc:-}"
    NAME_ORDER+=("${name}")
done < <(printf '%s\n' "${RAW_LINES[@]}")

# ── --list ──
if [ "${DO_LIST}" = "1" ]; then
    echo "共 ${#NAME_ORDER[@]} 个工具项目（registry: ${REGISTRY}）"
    echo ""
    printf "  %-26s %s\n" "目录名" "来源 / 说明"
    printf "  %-26s %s\n" "------" "-----------"
    for name in "${NAME_ORDER[@]}"; do
        printf "  %-26s %s\n" "${name}" "${NAME_DESC[${name}]:-}  (${NAME_URL[${name}]})"
    done
    echo ""
    echo "非 git 项目（已内置，不参与克隆）:"
    echo "  dex2jar      发布版 jar（source-projects/dex2jar/）"
    echo "  FixStackmaps 单个 Java 源文件（source-projects/FixStackmaps/）"
    exit 0
fi

# ── 依赖检查 ──
if ! command -v git >/dev/null 2>&1; then
    log_err "未找到 git，请先安装 git 再运行本脚本。"
    exit 1
fi

# ── 目标目录 ──
[ -d "${SRC_DIR}" ] || mkdir -p "${SRC_DIR}"

# ── 计算将执行的任务 ──
selected=()
for name in "${NAME_ORDER[@]}"; do
    if [ "${#ONLY[@]}" -gt 0 ]; then
        keep=0
        for o in "${ONLY[@]}"; do
            [ "${o}" = "${name}" ] && keep=1
        done
        [ "${keep}" = "1" ] || continue
    fi
    target="${SRC_DIR}/${name}"
    if [ -d "${target}/.git" ] || [ -d "${target}" ]; then
        if [ "${FORCE}" = "1" ]; then
            selected+=("${name}:refresh")
        else
            selected+=("${name}:skip")
        fi
    else
        selected+=("${name}:new")
    fi
done

if [ "${#selected[@]}" -eq 0 ]; then
    log_warn "没有匹配的工具（registry 可能为空，或 --only 名称不存在）。"
    log_info "用 --list 查看可用名称。"
    exit 0
fi

# ── 确认 ──
echo ""
echo "将下载 ${#selected[@]} 个工具项目到: ${SRC_DIR}"
shallow_label="浅克隆"
[ "${FULL}" = "1" ] && shallow_label="完整历史"
echo "  克隆方式: ${shallow_label}"
for item in "${selected[@]}"; do
    name="${item%%:*}"; state="${item##*:}"
    case "${state}" in
        new)     echo "  ${GREEN}●新增${NC} ${name}" ;;
        refresh) echo "  ${YELLOW}●重拉${NC} ${name}" ;;
        skip)    echo "  ${BLUE}○跳过(已存在)${NC} ${name}" ;;
    esac
done
echo ""
if [ "${ASSUME_YES}" != "1" ]; then
    read -r -p "继续? [y/N] " ans
    case "${ans}" in
        [yY]|[yY][eE][sS]) : ;;
        *) echo "已取消。"; exit 0 ;;
    esac
fi

# ── 执行克隆 ──
depth_args=()
[ "${FULL}" = "1" ] || depth_args=(--depth 1)

ok=0; fail=0; used_skip=0; failed_names=()
for item in "${selected[@]}"; do
    name="${item%%:*}"; state="${item##*:}"
    url="${NAME_URL[${name}]:-}"
    desc="${NAME_DESC[${name}]:-}"
    target="${SRC_DIR}/${name}"

    if [ -z "${url}" ]; then
        log_warn "跳过 ${name}: registry 无 URL（可能为非 git 项目）"
        continue
    fi

    if [ "${state}" = "skip" ] && [ "${FORCE}" != "1" ]; then
        log_info "已存在，跳过: ${name}"
        used_skip=$((used_skip + 1))
        continue
    fi

    # 清洗旧目录（--force 或重拉时）
    if [ "${state}" = "refresh" ] || ( [ "${FORCE}" = "1" ] && [ -d "${target}" ] ); then
        rm -rf "${target}"
    fi

    final_url="${url}"
    # 可选镜像前缀（中国大陆网络加速）：export GIT_PROXY_URL='https://ghproxy.com/'
    if [ -n "${GIT_PROXY_URL:-}" ]; then
        final_url="${GIT_PROXY_URL}${url}"
        log_warn "使用镜像: ${final_url}"
    fi

    log_info "克隆 ${name} (${desc})"
    if git clone "${depth_args[@]}" "${final_url}" "${target}"; then
        log_ok "${name} 就绪 → ${target}"
        ok=$((ok + 1))
    else
        log_err "${name} 克隆失败"
        rm -rf "${target}" 2>/dev/null || true
        fail=$((fail + 1)); failed_names+=("${name}")
    fi
done

# ── 汇总 ──
echo ""
echo "═══════════════════════════════════════════════════"
echo "  完成"
echo "  新增/重拉成功: ${ok}"
[ "${used_skip}" -gt 0 ] && echo "  已存在跳过: ${used_skip}"
[ "${fail}" -gt 0 ] && echo "  失败: ${fail} (${failed_names[*]})"
if [ "${fail}" -gt 0 ]; then
    echo ""
    log_err "以下工具克隆失败，可单独重试:"
    for n in "${failed_names[@]}"; do
        echo "    bash ${BASH_SOURCE[0]} --only ${n}"
    done
    exit 1
else
    echo "  全部就绪 ✅"
    exit 0
fi