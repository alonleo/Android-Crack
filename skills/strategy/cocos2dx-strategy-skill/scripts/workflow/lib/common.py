#!/usr/bin/env python3
"""
公共函数库 — 替代 common.sh + paths.sh
所有 stage-*.py 脚本 source 此模块获取路径、日志、工具函数。
"""
import os, sys, subprocess, datetime, re, shlex, shutil
from pathlib import Path

_REPO_ROOT = None
_CRACK_DIR = None
_OUT = None

def repo_root():
    global _REPO_ROOT
    if _REPO_ROOT:
        return _REPO_ROOT
    d = Path.cwd().resolve()
    while d != d.parent:
        if (d / "apks").is_dir() and (d / "tools").is_dir():
            _REPO_ROOT = d
            return _REPO_ROOT
        d = d.parent
    sys.exit("无法定位仓库根目录（缺少 apks/ 或 tools/）")

def ensure_env():
    """加载 tools/environments/env.sh（导出变量到 os.environ）"""
    env_file = Path(repo_root()) / "tools" / "environments" / "env.sh"
    if env_file.exists():
        # Run env.sh in a sub-shell and capture the output
        import tempfile
        result = subprocess.run(
            ["bash", "-c", f"source {env_file} && env"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            if '=' in line:
                k, v = line.split('=', 1)
                if not k.startswith('BASH') and k not in ('SHLVL', '_'):
                    os.environ.setdefault(k, v)

# ── 颜色 / 日志 ──────────────────────────────────────────────────────
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[0;33m'
    BLUE = '\033[0;34m'
    GREY = '\033[0;90m'
    RESET = '\033[0m'

def _ts(): return datetime.datetime.utcnow().strftime("%H:%M:%S")

def log_info(*a):
    print(f"{Colors.BLUE}[INFO]{Colors.RESET}", *a, file=sys.stderr)
def log_warn(*a):
    print(f"{Colors.YELLOW}[WARN]{Colors.RESET}", *a, file=sys.stderr)
def log_error(*a):
    print(f"{Colors.RED}[ERROR]{Colors.RESET}", *a, file=sys.stderr)
def log_success(*a):
    print(f"{Colors.GREEN}[OK]{Colors.RESET}", *a, file=sys.stderr)
def log_step(msg):
    print(f"\n{Colors.GREEN}== {msg} =={Colors.RESET}", file=sys.stderr)

def die(msg):
    log_error(msg); sys.exit(1)

def require_cmd(cmd, hint=""):
    from shutil import which
    if not which(cmd):
        die(f"缺少必要命令: {cmd} ({hint or '请安装后重试'})")

def require_file(f):
    if not os.path.isfile(f):
        die(f"缺少文件: {f}")

def ensure_dir(d):
    os.makedirs(d, exist_ok=True)
    # 自动登记到项目 dir-index.yaml（仅当 CRACK_DIR 已设置时）
    # 覆盖未走 stage_dir() 的脚本（如 common-stage 直接用 ensure_dir 建目录）
    # 跳过项目根目录本身（crackings/<Name>）与 dir-index 所在目录，避免递归/重复
    if os.environ.get('CRACK_DIR') and d and os.path.isdir(d):
        try:
            root = repo_root()
            rel = os.path.relpath(str(d), root)
            crack_rel = os.path.relpath(crack_dir(), root)
            if (not rel.startswith('..')
                    and '/crackings/' in '/' + rel
                    and rel != crack_rel
                    and not rel.endswith('/dir-index.yaml')):
                register_artifact(d, 'dir', '', name=os.environ.get('NAME', 'unknown'))
        except Exception:
            pass

def now_iso(): return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M")

def call(*args, **kwargs):
    print(f"$ {' '.join(shlex.quote(str(a)) for a in args)}", file=sys.stderr)
    return subprocess.run(args, **kwargs)

# ── 路径 / 命名 ──────────────────────────────────────────────────────
def normalize_apk_name(raw_name: str) -> str:
    name = raw_name.replace(".apk", "").replace(".xapk", "")
    for suffix in ["_APKPure", "_apkpure", "_ApkPure"]:
        name = name.replace(suffix, "")
    # [FLOWFIX 2026-08-23] 剥离 _merged 后缀（XAPK 合并产物标记），否则
    # 经过 CamelCase 归一后变 BmxcycleextremebicyclegameMerged，覆盖
    # driver 传入的 NAME，导致子阶段写错目录。
    if name.endswith("_merged") or name.endswith("-merged") or name.endswith(" Merged"):
        name = name.rsplit("_", 1)[0]
    import re
    name = re.sub(r'_[0-9]+(\.[0-9]+)+$', '', name)
    name = re.sub(r'_v[0-9]+(\.[0-9]+)*$', '', name)
    # [FLOWFIX] 已经 CamelCase 的名字（无
    # `_`/`+`/`-`/空格分隔符）跳过 token 化 + .title()，否则 "HighwayBikeAttackRaceGame"
    # 会被 .title() 错误地变成 "Highwaybikeattackracegame"（后续字母全部小写）。
    if not re.search(r'[ _+\-]', name):
        return name or "UnknownApk"
    name = re.sub(r'[^a-zA-Z0-9]+', ' ', name)
    # [FLOWFIX] .title() 会把 "TD"/"USA" 等连续大写变成 "Td"/"Usa"
    # 修复: 对每个单词，若全部为大写（≥2 字符）则保留原样；其余走 .title()
    parts = name.split()
    titled = [p if re.fullmatch(r'[A-Z]{2,}', p) else p.title() for p in parts]
    name = ''.join(titled)
    return name or "UnknownApk"

def setup_paths_from_apk(apk_path: str, type: str = None):
    """从 APK 路径设置项目路径。
    
    :param apk_path: APK 文件路径
    :param type: 引擎类型（sniff 后已知），不提供则用旧路径 crackings/<Name>/
    """
    global _CRACK_DIR, _OUT
    apk_path = str(apk_path)
    if not os.path.isfile(apk_path):
        apk_path = str(Path(repo_root()) / "apks" / apk_path)
    require_file(apk_path)
    name = normalize_apk_name(os.path.basename(apk_path))
    root = repo_root()
    os.environ['APK'] = apk_path
    os.environ['NAME'] = name
    if type:
        os.environ['TYPE'] = type
        crack_dir_path = Path(root) / "crackings" / type / name
        out_dir_path = crack_dir_path / "raw"
        patched_path = Path(root) / "output-projects" / type / name / "patched.apk"
    else:
        crack_dir_path = Path(root) / "crackings" / name
        out_dir_path = crack_dir_path / "raw"
        patched_path = Path(root) / "output-projects" / name / "patched.apk"
    os.environ['CRACK_DIR'] = str(crack_dir_path)
    os.environ['OUT'] = str(out_dir_path)
    os.environ['PATCHED'] = str(patched_path)
    _CRACK_DIR = str(crack_dir_path)
    _OUT = str(out_dir_path)
    init_dir_index(name)
    return name

def setup_paths_from_name(name: str, type: str = None):
    """设置项目路径（支持 type 父目录）。
    
    :param name: 项目名（CamelCase）
    :param type: 引擎类型（il2cpp/android/air/defold/...），sniff 后已知。
                 提供 → crackings/<type>/<Name>/ + crackings/<type>/<Name>/project/
                 不提供 → crackings/<Name>/ + crackings/<type>/<Name>/project/（过渡期兼容）
    """
    global _CRACK_DIR, _OUT
    root = repo_root()
    os.environ['NAME'] = name
    if type:
        os.environ['TYPE'] = type
        crack_dir_path = Path(root) / "crackings" / type / name
        out_dir_path = crack_dir_path / "raw"
        patched_path = Path(root) / "output-projects" / type / name / "patched.apk"
    else:
        crack_dir_path = Path(root) / "crackings" / name
        out_dir_path = crack_dir_path / "raw"
        patched_path = Path(root) / "output-projects" / name / "patched.apk"
    os.environ['CRACK_DIR'] = str(crack_dir_path)
    os.environ['OUT'] = str(out_dir_path)
    os.environ['PATCHED'] = str(patched_path)
    _CRACK_DIR = str(crack_dir_path)
    _OUT = str(out_dir_path)
    init_dir_index(name)

def crack_dir(): return os.environ.get('CRACK_DIR', '')
def out_dir(): return os.environ.get('OUT', '')

require_crack_dir = lambda: (os.path.isdir(crack_dir()) or die(f"crackings/{os.environ.get('TYPE','')}/{os.environ.get('NAME','?')}/ 不存在（或旧路径 crackings/{os.environ.get('NAME','?')}/ 也不存在）"))
require_out = lambda: (os.path.isdir(out_dir()) or die("raw/ 不存在"))

# ── per-stage 目录约定（WORKFLOW.md §1.4） ───────────────────────────
# 每个 stage 的输出记录目录统一在 crackings/<Name>/stages/<stage-id>/
# 用法：
#   sd = stage_dir('02b')                 # 返回路径，自动 ensure_dir
#   sd = stage_dir('02b', label='fake-android')  # 自定义后缀
#   sd = stage_dir('02b', create=False)   # 不自动创建（只返回路径）
_STAGES_ROOT = lambda: str(Path(crack_dir()) / "stages")

# ── 项目目录索引表（dir-index.yaml） ───────────────────────────────────
# 每个 crackings/<Name>/ 下维护 dir-index.yaml，登记该项目生成的所有目录/文件。
# Agent 处理项目前必须先读该表（AGENTS.md §1.11），了解已生成的产物。
# 脚本通过 register_artifact() 或 stage_dir()/stage_out() 自动登记。

DIR_INDEX_HEADER = """# Dir Index: {name}

> **项目目录索引表**。本表登记该项目生成的所有目录/文件。
> Agent 处理本项目前**必须先读本表**（AGENTS.md §1.11），禁止自行 `ls` 枚举项目目录。
> 由脚本自动维护：`register_artifact()` / `stage_dir()` / `stage_out()`。

## 目录
| 路径 | 类型 | 说明 | 登记时间 |
|------|------|------|---------|
"""

def dir_index_path():
    return str(Path(crack_dir()) / "dir-index.yaml")

def init_dir_index(name=None):
    """项目初始化时创建 dir-index.yaml（幂等）。"""
    name = name or os.environ.get('NAME', 'unknown')
    p = dir_index_path()
    os.makedirs(os.path.dirname(p), exist_ok=True)
    if not os.path.isfile(p):
        with open(p, 'w', encoding='utf-8') as f:
            f.write(DIR_INDEX_HEADER.format(name=name))

def register_artifact(path, kind='dir', desc='', name=None):
    """登记一个生成目录/文件到 dir-index.yaml。

    :param path: 绝对路径或相对 repo 根路径（统一转相对 repo 记录）
    :param kind: 'dir' | 'file'
    :param desc: 说明（阶段/用途）
    :param name: 项目名（默认取环境变量 NAME）
    """
    name = name or os.environ.get('NAME', 'unknown')
    root = repo_root()
    rel = os.path.relpath(str(path), root)
    if rel.startswith('..'):
        rel = str(path)
    # 幂等：已登记的路径不重复追加（按 rel 去重）
    p = dir_index_path()
    if os.path.isfile(p):
        try:
            existing = open(p, encoding='utf-8').read()
            if f"| `{rel}` |" in existing:
                return
        except Exception:
            pass
    init_dir_index(name)
    ts = now_iso()
    line = f"| `{rel}` | {kind} | {desc} | {ts} |\n"
    with open(p, 'a', encoding='utf-8') as f:
        f.write(line)

def stage_dir(stage_id, label=None, create=True):
    """per-stage 目录约定：crackings/<Name>/stages/<stage-id>[-<label>]/

    :param stage_id: 阶段 ID（如 '00', '00a', '02b', '04c'）
    :param label: 可选后缀（如 'fake-android' → '02b-fake-android'）
    :param create: 是否自动创建目录（默认 True）
    :return: 绝对路径字符串
    """
    name = f"{stage_id}-{label}" if label else stage_id
    d = os.path.join(_STAGES_ROOT(), name)
    if create:
        was_missing = not os.path.isdir(d)
        ensure_dir(d)
        if was_missing:
            register_artifact(d, 'dir', f'阶段 {stage_id} 产物目录', name=os.environ.get('NAME', 'unknown'))
    return d

# ── 进度 / 工具调用记录 ──────────────────────────────────────────────
def append_status(stage, summary):
    """状态写入由 Agent 人工完成；本函数不再修改任何文件，仅保留签名兼容。"""
    pass


def update_status_toml():
    """状态文件更新由 Agent 人工完成；本函数不再修改任何文件。"""
    pass


def append_tool_call(stage, cmd_line):
    name = os.environ.get('NAME', 'unknown')
    f = Path(crack_dir()) / "tool-calls.md"
    ensure_dir(f.parent)
    entry = f"\n## [{now_iso()}] {stage}\n```bash\n{cmd_line}\n```\n"
    with open(f, 'a', encoding='utf-8') as fh:
        fh.write(entry)

# ── 工具路径（从 env.sh 获取）──
_tool_cache = {}
def tool_path(name):
    if name not in _tool_cache:
        p = os.environ.get(name.upper(), shutil.which(name) or "")
        _tool_cache[name] = p
    return _tool_cache[name]

adb = lambda: tool_path('ADB_BIN') or 'adb'
apktool = lambda: tool_path('APKTOOL') or 'apktool'
aapt2 = lambda: tool_path('AAPT2') or 'aapt2'
jarsigner = lambda: tool_path('JARSIGNER') or 'jarsigner'
zipalign = lambda: tool_path('ZIPALIGN') or 'zipalign'
apksigner = lambda: tool_path('APKSIGNER') or 'apksigner'
keytool = lambda: tool_path('KEYTOOL') or 'keytool'
jadx = lambda: tool_path('JADX') or 'jadx'
