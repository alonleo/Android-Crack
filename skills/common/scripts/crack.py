#!/usr/bin/env python3
"""crack.py — Android 逆向工作流主驱动器（Python 版）"""

import sys, os, subprocess, glob, re, json, shlex
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:  # pragma: no cover
    yaml = None

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "lib"))
from common import *

SCRIPT_DIR = Path(__file__).resolve().parent


def run_by_lang(script, *args):
    ext = os.path.splitext(script)[1].lower()
    cmd_map = {'.py': ['python3'], '.js': ['node'], '.mjs': ['node'], '.rb': ['ruby']}
    interpreter = cmd_map.get(ext, ['bash'])
    full_cmd = interpreter + [script] + list(args)
    log_info(f"执行: {' '.join(shlex.quote(str(a)) for a in full_cmd)}")
    return subprocess.run(full_cmd).returncode


def print_usage():
    print("""crack.py - Android \u9006\u5411\u5de5\u4f5c\u6d41\u4e3b\u9a71\u52a8\u5668

\u7528\u6cd5:
  crack.py <source.apk>            # \u81ea\u52a8\u55c5\u63a2\u7c7b\u578b\uff0c\u9009\u62e9\u5bf9\u5e94\u7b56\u7565\u8dd1\u5b8c\u6240\u6709\u9636\u6bb5
  crack.py <source.apk> stage-N    # \u53ea\u8dd1\u7b2c N \u9636\u6bb5
  crack.py <source.apk> 5-9        # \u8dd1 5~9 \u9636\u6bb5
  crack.py <Name> status           # \u663e\u793a\u8fdb\u5ea6
  crack.py <Name> stop             # \u6807\u8bb0\u9879\u76ee\u4e3a\u5df2\u5e9f\u5f03
  crack.py --help                  # \u672c\u5e2e\u52a9

\u73af\u5883\u53d8\u91cf: APKTOOL, JADX, APKSIGNER, ADB_BIN \u7b49
""")


def resolve_name_from_arg(raw):
    if os.path.isfile(raw):
        return normalize_apk_name(os.path.basename(raw))
    return os.path.basename(raw)


def cmd_status(raw):
    name = resolve_name_from_arg(raw)
    pf = Path(repo_root()) / "crackings" / name / "status.yaml"
    if pf.exists():
        print(pf.read_text())
        return 0
    log_warn(f"未找到 {name} 的 status.yaml")
    return 1


def cmd_stop(raw):
    name = resolve_name_from_arg(raw)
    pf = Path(repo_root()) / "crackings" / name / "status.yaml"
    if not pf.exists():
        die("无 status.yaml")
    import yaml
    data = yaml.safe_load(pf.read_text()) or {}
    data.setdefault("status", {})["phase"] = "stopped"
    data["status"]["last_updated"] = now_iso()
    pf.write_text(yaml.dump(data, allow_unicode=True, sort_keys=False), encoding="utf-8")
    log_warn(f"{name} 已标记为已废弃")


def resolve_stage_script(strategy_type, stage):
    """根据声明式注册表返回阶段脚本的绝对路径。

    兼容：传入旧编号时通过 `legacy_stage_map` 还原成 01–15。
    ⚠️ [FLOWFIX] 直接现代编号优先：legacy map 仅作 fallback。
       否则新骨架中「10/11/12/13/15」等现代阶段会被旧映射（10→17 等）误重定向。
    """
    if not hasattr(resolve_stage_script, "_cache"):
        resolve_stage_script._cache = {}
    cache_key = (strategy_type, stage)
    if cache_key in resolve_stage_script._cache:
        return resolve_stage_script._cache[cache_key]

    registry = load_stage_registry()
    type_info = registry.get(strategy_type) or {}
    scripts = type_info.get("scripts") or []

    # 1) 直接匹配现代阶段（优先）
    for entry in scripts:
        if entry.get("id") == stage:
            script_rel = entry.get("script")
            if not script_rel:
                break
            abs_path = str((Path(repo_root()) / script_rel).resolve())
            resolve_stage_script._cache[cache_key] = abs_path
            return abs_path

    # 2) 无直接匹配 → legacy 映射兜底
    legacy_map = type_info.get("legacy_stage_map") or {}
    modern_stage = legacy_map.get(stage, stage)
    if modern_stage != stage:
        for entry in scripts:
            if entry.get("id") == modern_stage:
                script_rel = entry.get("script")
                if not script_rel:
                    break
                abs_path = str((Path(repo_root()) / script_rel).resolve())
                resolve_stage_script._cache[cache_key] = abs_path
                return abs_path

    resolve_stage_script._cache[cache_key] = ''
    return ''


def load_stage_registry():
    """加载 strategy-config.yaml 的 type → scripts 声明式注册表（三层架构）。

    数据源：stage_details（Layer 3）+ metadata.legacy_stage_map（兼容旧编号）。
    返回结构：
        {
            "<type>": {
                "scripts": [{"id": "01", "script": "...", "function": "...", "role": "...", "mode": "..."}, ...],
                "legacy_stage_map": {"00": "01", ...}
            }
        }
    """
    if hasattr(load_stage_registry, "_cache"):
        return load_stage_registry._cache
    cfg_path = SCRIPT_DIR / "strategy" / "strategy-config.yaml"
    if not cfg_path.is_file():
        load_stage_registry._cache = {}
        return load_stage_registry._cache
    with open(cfg_path, "r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}

    # 三层架构：Layer 3 stage_details + metadata.legacy_stage_map
    stage_details = data.get("stage_details", {}) or {}
    metadata = data.get("metadata", {}) or {}
    legacy_stage_map = metadata.get("legacy_stage_map", {}) or {}

    registry = {}
    for type_name, type_details in stage_details.items():
        scripts = []
        for stage_id, detail in type_details.items():
            scripts.append({
                "id": stage_id,
                "script": detail.get("script", ""),
                "function": detail.get("function", ""),
                "role": detail.get("role", ""),
                "mode": detail.get("mode", "automatic"),
            })
        registry[type_name] = {
            "scripts": scripts,
            "legacy_stage_map": legacy_stage_map.get(type_name, {}) or {},
        }
    load_stage_registry._cache = registry
    return registry


def resolve_legacy_stage(strategy_type, stage):
    """返回旧编号映射后的现代阶段 ID（无映射则原样返回）。"""
    registry = load_stage_registry()
    legacy = registry.get(strategy_type, {}).get("legacy_stage_map", {})
    return legacy.get(stage, stage)


def run_stage(name, stage, src_apk, strategy_type=None):
    if strategy_type is None:
        strategy_type = os.environ.get("STRATEGY_TYPE", "")
    script = resolve_stage_script(strategy_type, stage)
    if not script or not os.path.isfile(script):
        log_error(f"找不到 stage 脚本: type={strategy_type} stage={stage}")
        return 127
    log_step(f"[{name}] 阶段 {stage}（{os.path.basename(script)}）")
    # [FLOWFIX] type-skill 阶段脚本通过 env
    # (APK/NAME) 取参（argparse 只收 --out/--apk 等选项），统一传位置参数会触发
    # "unrecognized arguments"。仅 general-strategy-skill 脚本接受 <apk> 位置参数。
    is_skill_script = "skills/strategy" in script and "strategy-skill/scripts" in script
    ret = run_by_lang(script) if is_skill_script else run_by_lang(script, src_apk)
    if ret != 0:
        log_error(f"阶段 {stage} 失败；可单独重跑: crack.py <apk> stage-{stage}")
        return 1
    return 0


def run_stage_range(name, range_str, src_apk, strategy_type=None):
    parts = range_str.split('-')
    start, end = parts[0], parts[1] if len(parts) > 1 else parts[0]
    for s in range(int(start), int(end) + 1):
        stage = f'{s:02d}'
        if run_stage(name, stage, src_apk, strategy_type=strategy_type) != 0:
            return 1
    return 0


def run_pipeline(strategy_type, stages, src_apk=None, name=None):
    """按声明式注册表顺序执行各阶段。

    :param strategy_type: 嗅探/路由得到的类型，例如 'il2cpp'
    :param stages: 阶段 ID 列表（已使用 `01`-`15`）
    :param src_apk: 源 APK 路径；为 None 时从环境变量 `APK` 读取
    :param name: 项目名；为 None 时从环境变量 `NAME` 读取
    :return: 失败时返回 1，全部成功返回 0
    """
    if src_apk is None:
        src_apk = os.environ.get("APK", "")
    if name is None:
        name = os.environ.get("NAME", "")
    failed_at = None
    for stage in stages:
        if run_stage(name, stage, src_apk, strategy_type=strategy_type) != 0:
            failed_at = stage
            log_error(f"流水线在阶段 {stage} 中断")
            return 1
    return 0


def sniff_fallback(apk_path):
    result = subprocess.run(['unzip', '-l', apk_path], capture_output=True, text=True)
    out = result.stdout
    if re.search(r'lib/.*/libil2cpp\.so', out):
        return 'il2cpp'
    if re.search(r'META-INF/AIR/application\.xml', out):
        return 'air'
    return 'unknown'


def main():
    ensure_env()

    args = sys.argv[1:]

    if not args or args[0] in ('--help', '-h'):
        print_usage()
        sys.exit(0)

    if args[0] == '--version':
        print("crack.py v1.0 (android-crack workspace)")
        sys.exit(0)

    if args[0] == '--list':
        stages = sorted(glob.glob(str(SCRIPT_DIR / "stage-*-*")))
        for s in stages:
            print(os.path.basename(s))
        sys.exit(0)

    if args[0] == '--strategies':
        sp = str(SCRIPT_DIR / "strategy" / "strategy-config.py")
        if os.path.isfile(sp):
            subprocess.run(['python3', sp, 'list'], check=False)
        else:
            die("strategy-config.py 不存在")
        sys.exit(0)

    raw_arg = args[0]
    arg2 = args[1] if len(args) > 1 else ''

    if arg2 == 'status':
        sys.exit(cmd_status(raw_arg))
    if arg2 == 'stop':
        cmd_stop(raw_arg)
        sys.exit(0)

    apk_path = raw_arg
    if not os.path.isfile(apk_path):
        candidate = os.path.join(repo_root(), 'apks', raw_arg)
        if os.path.isfile(candidate):
            apk_path = candidate
        else:
            die(f"找不到 APK: {raw_arg}（也不在 apks/）")

    setup_paths_from_apk(apk_path)
    src_apk = os.environ['APK']
    name = os.environ['NAME']

    # 检测类型（用于单阶段运行）
    strategy_py = str(SCRIPT_DIR / "strategy" / "strategy-config.py")
    if os.path.isfile(strategy_py) and not os.environ.get('STRATEGY_TYPE'):
        strategy_type = subprocess.run(
            ['python3', strategy_py, 'detect', src_apk],
            capture_output=True, text=True).stdout.strip()
        os.environ['STRATEGY_TYPE'] = strategy_type

    if re.match(r'^stage-(?:[0-9]{2}[a-z]|[0-9]{2})$', arg2):
        stage_id = arg2[len('stage-'):]
        ret = run_stage(name, stage_id, src_apk)
        sys.exit(0 if ret == 0 else 1)

    if re.match(r'^[0-9]{1,2}-[0-9]{1,2}$', arg2):
        ret = run_stage_range(name, arg2, src_apk)
        sys.exit(0 if ret == 0 else 1)

    if re.match(r'^[0-9]{1,2}$', arg2):
        stage_id = f'{int(arg2):02d}'
        ret = run_stage(name, stage_id, src_apk)
        sys.exit(0 if ret == 0 else 1)

    if arg2 == '':
        log_step(f"启动完整流水线（默认走 run-pipeline.py 七大主阶段）: {apk_path}")

        # 默认调用七大主阶段统一驱动器 run-pipeline.py
        pipeline_py = SCRIPT_DIR / "run-pipeline.py"
        if pipeline_py.exists():
            cmd = ["python3", str(pipeline_py), apk_path, name]
            ret = subprocess.run(cmd, check=False).returncode
            if ret != 0:
                log_warn(f"✗ 流水线中断（rc={ret}）；可单独重跑失败的主阶段")
            else:
                log_success(f"✓ 七大主阶段全部完成；产物: {os.environ.get('PATCHED', 'N/A')}")
            sys.exit(ret)

        # 降级路径：直接跑 strategy 路由的子阶段（兼容老行为）
        log_warn("run-pipeline.py 不存在，降级到旧子阶段直跑")
        strategy_py = str(SCRIPT_DIR / "strategy" / "strategy-config.py")
        if os.path.isfile(strategy_py):
            strategy_type = subprocess.run(
                ['python3', strategy_py, 'detect', src_apk],
                capture_output=True, text=True).stdout.strip()
            stages_raw = subprocess.run(
                ['python3', strategy_py, 'stages', strategy_type],
                capture_output=True, text=True).stdout.strip()
            strategy_notes = subprocess.run(
                ['python3', strategy_py, 'notes', strategy_type],
                capture_output=True, text=True).stdout.strip()
            mandatory = subprocess.run(
                ['python3', strategy_py, 'mandatory', strategy_type],
                capture_output=True, text=True).stdout.strip()
        else:
            log_warn("strategy-config.py 不可用，降级到嗅探模式")
            strategy_type = sniff_fallback(src_apk)
            stages_raw = "00 00a 01 02 03 04 05 06 07 08 09 10 11 12 13"
            mandatory = ""
            strategy_notes = ""

        stages_list = stages_raw.split()
        log_info(f"检测类型: {strategy_type}")
        log_info(f"阶段序列: {' '.join(stages_list)}")
        if strategy_notes:
            log_info(f"策略备注: {strategy_notes}")
        if mandatory:
            log_info(f"强制入口: {mandatory}")

        os.environ['STRATEGY_TYPE'] = strategy_type

        ret = run_pipeline(strategy_type=strategy_type, stages=stages_list, src_apk=src_apk, name=name)
        if ret != 0:
            log_warn("✗ 流水线中断；可单独重跑失败的阶段")
            sys.exit(ret)

        log_success(f"✓ 主干阶段完成；产物: {os.environ.get('PATCHED', 'N/A')}")
        log_info(f"更多详情: crack.py {raw_arg} status")
        diff_json = Path(repo_root()) / "crackings" / name / "difficulty.json"
        if diff_json.exists():
            try:
                with open(diff_json) as fh:
                    diff_data = json.load(fh)
                grade = diff_data.get('grade', 'N/A')
                total = diff_data.get('total_score', 'N/A')
                log_info(f"难度评级: **{grade}** (总分 {total} / 100)")
            except Exception:
                pass
        sys.exit(0)

    die(f"未知命令: {arg2}（试试 --help）")


if __name__ == "__main__":
    main()
