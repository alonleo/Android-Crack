"""IL2CPP 阶段公共工具：路径、构建、安装、启动验证。

不依赖 `skills/common/scripts/lib/common.py`，避免与全局 common 互相耦合；
阶段脚本可以从 `scripts/lib` 直接 import。
"""

from __future__ import annotations

import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

ROOT_HINT = Path(__file__).resolve().parents[2]  # skills/strategy/il2cpp-strategy-skill


def repo_root() -> Path:
    """从 skill 目录回溯到仓库根（含 `apks/` 与 `tools/` 的目录）。"""
    if "ANDROID_CRACK_REPO" in os.environ:
        candidate = Path(os.environ["ANDROID_CRACK_REPO"]).resolve()
        if (candidate / "apks").is_dir() and (candidate / "tools").is_dir():
            return candidate
    for d in [ROOT_HINT, *ROOT_HINT.parents]:
        if (d / "apks").is_dir() and (d / "tools").is_dir():
            return d
    raise SystemExit("无法定位仓库根目录（缺少 apks/ 或 tools/）")


def tool(name: str) -> str:
    """优先取 env.sh 注入的工具路径，否则回落系统 PATH。"""
    env_key = name.upper()
    return os.environ.get(env_key) or shutil.which(name) or name


def as_dir(name: str, kind: str = "") -> Path:
    """返回 `crackings/<type>/<Name>/project/<kind>` 路径。

    kind 默认空字符串 → 直接指向 crackings/<type>/<Name>/project/
    kind="app" → crackings/<type>/<Name>/project/app/（AS 工程的 app 模块）
    """
    import os as _os
    type_arg = _os.environ.get("TYPE", "").strip()
    if type_arg:
        return repo_root() / "output-projects" / type_arg / name / kind
    return repo_root() / "output-projects" / name / kind


def crack_dir(name: str) -> Path:
    # [FLOWFIX] §3 父目录规则：跟随 TYPE
    import os as _os
    type_arg = _os.environ.get("TYPE", "").strip()
    if type_arg:
        return repo_root() / "crackings" / type_arg / name
    return repo_root() / "crackings" / name


# ── 项目目录索引表（dir-index.yaml） ───────────────────────────────────
# 每个 crackings/<Name>/ 下维护 dir-index.yaml，登记该项目生成的所有目录/文件。
# Agent 处理项目前必须先读该表（AGENTS.md §1.11），了解已生成的产物。
# 脚本通过 register_artifact() 或 stage_out() 自动登记。

_DIR_INDEX_HEADER = """# Dir Index: {name}

> **项目目录索引表**。本表登记该项目生成的所有目录/文件。
> Agent 处理本项目前**必须先读本表**（AGENTS.md §1.11），禁止自行 `ls` 枚举项目目录。
> 由脚本自动维护：`register_artifact()` / `stage_dir()` / `stage_out()`。

## 目录
| 路径 | 类型 | 说明 | 登记时间 |
|------|------|------|---------|
"""


def init_dir_index(name: str) -> Path:
    """项目初始化时创建 dir-index.yaml（幂等）。"""
    p = crack_dir(name) / "dir-index.yaml"
    p.parent.mkdir(parents=True, exist_ok=True)
    if not p.is_file():
        p.write_text(_DIR_INDEX_HEADER.format(name=name), encoding="utf-8")
    return p


def register_artifact(path: Path, kind: str = "dir", desc: str = "", name: str = "") -> None:
    """登记一个生成目录/文件到 dir-index.yaml（幂等，按 rel 去重）。"""
    name = name or os.environ.get("NAME", "unknown")
    root = repo_root()
    try:
        rel = os.path.relpath(str(path), str(root))
    except Exception:
        rel = str(path)
    if rel.startswith(".."):
        rel = str(path)
    p = init_dir_index(name)
    if p.is_file():
        try:
            if f"| `{rel}` |" in p.read_text(encoding="utf-8"):
                return
        except Exception:
            pass
    ts = time.strftime("%Y-%m-%d %H:%M")
    with p.open("a", encoding="utf-8") as f:
        f.write(f"| `{rel}` | {kind} | {desc} | {ts} |\n")


def stage_out(name: str, stage_id: str, label: Optional[str] = None) -> Path:
    folder = f"{stage_id}-{label}" if label else stage_id
    out = crack_dir(name) / "stages" / folder
    was_missing = not out.is_dir()
    out.mkdir(parents=True, exist_ok=True)
    if was_missing:
        register_artifact(out, "dir", f"阶段 {stage_id} 产物目录", name=name)
    return out


def run_subprocess(args: Sequence[str], cwd: Optional[Path] = None, timeout: Optional[int] = None) -> Tuple[int, str]:
    """统一的子进程执行器：返回 (returncode, stdout_or_stderr)。"""
    cmd = [str(a) for a in args]
    try:
        result = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
        return result.returncode, (result.stdout or "") + (result.stderr or "")
    except subprocess.TimeoutExpired as exc:
        return 124, f"timeout after {exc.timeout}s: {' '.join(shlex.quote(c) for c in cmd)}"


def gradle_assemble_release(as_root: Path, build_dir: str = "app") -> Tuple[int, str]:
    """调用 `./gradlew assembleRelease`，结果用 (returncode, log) 返回。

    `:app:assembleRelease` 任务更稳，避免 cwd 误判。
    """
    return run_subprocess(
        [str(as_root / "gradlew"), f":{build_dir}:assembleRelease"],
        cwd=as_root,
        timeout=900,
    )


def gradle_build_with_log(name: str, as_root: Path, build_dir: str = "app", stage_id: str = "") -> Tuple[int, Path]:
    """构建并记录日志（覆盖模式，始终保留最后一次）。

    - 调用 `gradlew :<build_dir>:assembleRelease`
    - 输出以覆盖模式写入 `crackings/<Name>/gradle-build.log`
    - 登记到 dir-index.yaml
    - 返回 (returncode, log_path)
    """
    code, output = gradle_assemble_release(as_root, build_dir=build_dir)
    log_path = crack_dir(name) / "gradle-build.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(output, encoding="utf-8")
    desc = f"Gradle 构建日志（{stage_id or build_dir}，覆盖保留最后一次）"
    register_artifact(log_path, "file", desc, name=name)
    if code != 0:
        log_warn(f"assembleRelease 失败；查看 {log_path}")
    else:
        log_success(f"assembleRelease BUILD SUCCESSFUL → {log_path}")
    return code, log_path


# ── 标准 AS 项目结构（参考 template-projects/tape-thrower/） ──────────
# 输出项目须符合 AndroidStudio 标准结构：
#   <Name>/{build.gradle, settings.gradle, gradle.properties, gradlew, gradle/, my.keystore.jks}
#   <Name>/app/{build.gradle, src/main/{AndroidManifest.xml, java, cpp, jniLibs, assets, res}}
# smali 不作为标准结构的一部分（见问题 7：smali 转 jar 引用）。

STANDARD_STRUCTURE_REQUIRED = [
    "build.gradle",
    "settings.gradle",
    "gradle.properties",
    "gradlew",
    "gradle/wrapper/gradle-wrapper.properties",
    "my.keystore.jks",
    "app/build.gradle",
    "app/src/main/AndroidManifest.xml",
    "app/src/main/java",
    "app/src/main/cpp",
    "app/src/main/jniLibs",
    "app/src/main/res",
]

STANDARD_STRUCTURE_OPTIONAL = [
    "gradlew.bat",
    "app/src/main/assets",
    "app/src/main/smali",
]


def verify_project_structure(name: str, stage_id: str = "", require_smali_free: bool = False) -> bool:
    """按标准 AS 结构清单逐项校验输出项目，产出检查报告。

    - 必填项缺失 → 记录 FAIL
    - 可选项缺失 → 记录 WARN
    - require_smali_free=True 时，出现任何 smali* 目录 → FAIL（问题 7 目标态）
    - 报告写入 `crackings/<Name>/stages/<stage_id>/project-structure-check.md`
    - 返回是否全部必填项通过
    """
    project = as_dir(name, kind="")
    if stage_id:
        out_dir = stage_out(name, stage_id)
    else:
        out_dir = crack_dir(name)
    report = out_dir / "project-structure-check.md"

    lines = [f"# 项目结构自检 — {name}", "", "> 标准参考: `template-projects/tape-thrower/`", ""]
    failures = []

    for rel in STANDARD_STRUCTURE_REQUIRED:
        p = project / rel
        if p.is_file() or p.is_dir():
            lines.append(f"- [x] {rel}")
        else:
            lines.append(f"- [ ] **FAIL** 缺失: {rel}")
            failures.append(rel)

    for rel in STANDARD_STRUCTURE_OPTIONAL:
        p = project / rel
        if p.is_file() or p.is_dir():
            lines.append(f"- [x] {rel}（可选）")
        else:
            lines.append(f"- [ ] WARN 缺失（可选）: {rel}")

    smali_dirs = [d.name for d in (project / "app" / "src" / "main").glob("smali*")] if (project / "app" / "src" / "main").is_dir() else []
    if smali_dirs:
        if require_smali_free:
            lines.append(f"- [ ] **FAIL** 仍存在 smali 目录: {', '.join(sorted(smali_dirs))}")
            failures.append("smali dirs present")
        else:
            lines.append(f"- [ ] WARN 存在 smali 目录（目标态应无）: {', '.join(sorted(smali_dirs))}")

    ok = not failures
    lines.append("")
    lines.append(f"**结果: {'PASS' if ok else 'FAIL'}**（必填项缺失 {len(failures)} 处）")
    report.write_text("\n".join(lines), encoding="utf-8")
    register_artifact(report, "file", "项目结构自检报告", name=name)
    if ok:
        log_success(f"项目结构自检通过: {report}")
    else:
        log_warn(f"项目结构自检失败（{len(failures)} 处）：{report}")
    return ok


def adb_devices() -> List[dict]:
    raw = run_subprocess([tool("ADB_BIN"), "devices", "-l"])[1]
    devices = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("List of devices"):
            continue
        parts = line.split()
        if len(parts) < 2 or parts[1] != "device":
            continue
        devices.append({"serial": parts[0], "raw": line})
    return devices


def adb_install(serial: str, apk: Path) -> Tuple[int, str]:
    return run_subprocess([tool("ADB_BIN"), "-s", serial, "install", "-r", str(apk)], timeout=240)


def adb_uninstall(serial: str, package: str) -> Tuple[int, str]:
    return run_subprocess([tool("ADB_BIN"), "-s", serial, "uninstall", package], timeout=120)


def adb_launch_activity(serial: str, package: str, activity: str) -> Tuple[int, str]:
    component = f"{package}/{activity}"
    return run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "shell", "am", "start", "-W", "-n", component],
        timeout=60,
    )


def adb_logcat_errors(serial: str, seconds: int = 5) -> List[str]:
    run_subprocess([tool("ADB_BIN"), "-s", serial, "logcat", "-c"], timeout=10)
    time.sleep(seconds)
    code, output = run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "logcat", "-d", "*:E"],
        timeout=30,
    )
    fatal = [
        line
        for line in output.splitlines()
        if "FATAL EXCEPTION" in line or "AndroidRuntime" in line
    ]
    return fatal


def adb_activity_state(serial: str, package: str) -> str:
    """查询目标进程前台 Activity 的 Resumed/ResumedActivity 状态。

    返回 ''（未在前台）/ 'RESUMED'（顶层 resumed）/ '其他状态'。
    若 Activity 已退出回桌面，mResumedActivity 不会指向本包。
    """
    code, output = run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "shell",
         "dumpsys", "activity", "activities"],
        timeout=30,
    )
    if code != 0:
        return ""
    for line in output.splitlines():
        line = line.strip()
        if "mResumedActivity:" in line and package in line:
            return "RESUMED"
        if "topResumedActivity:" in line and package in line:
            return "RESUMED"
        if line.startswith("Resumed") and package in line:
            return "RESUMED"
    return ""


def adb_gfx_frames(serial: str, package: str, seconds: int = 3) -> int:
    """统计窗口期内渲染活跃度，用于判断是否卡加载/黑屏。

    ⚠️ Unity 游戏用 SurfaceView 渲染，不走 ViewRootImpl，`dumpsys gfxinfo`
    无 'Total frames rendered' 行（返回 -1）。改用 SurfaceFlinger --latency：
    该 SurfaceView layer 的帧时间戳行数 > 阈值即表示渲染持续推进。
    返回帧时间戳行数（>0 活跃；-1 无法检测）。
    """
    # 先找该 package 的 SurfaceView layer
    code, out = run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "shell", "dumpsys", "SurfaceFlinger", "--list"],
        timeout=30,
    )
    layer = ""
    for line in out.splitlines():
        if "SurfaceView" in line and package in line:
            layer = line.strip()
            break
    if not layer:
        return -1
    # ⚠️ layer 名含空格，subprocess list 形式执行 `adb shell dumpsys ... --latency <layer>`
    # 会把 layer 拆成多个参数。必须用 shlex.quote 在 shell 侧加引号。
    code, out = run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "shell", "dumpsys", "SurfaceFlinger", "--latency", shlex.quote(layer)],
        timeout=30,
    )
    if code != 0:
        return -1
    count = 0
    for line in out.splitlines():
        line = line.strip()
        if line and line[0].isdigit():
            count += 1
    return count


def adb_pid(serial: str, package: str) -> Optional[str]:
    """返回目标进程 pid；进程不存在（已崩溃/被回收）返回 None。"""
    code, output = run_subprocess(
        [tool("ADB_BIN"), "-s", serial, "shell", "pidof", package],
        timeout=15,
    )
    if code != 0 or not output.strip():
        return None
    return output.strip().splitlines()[0].strip()


def verify_app_alive(
    serial: str,
    package: str,
    windows: int = 3,
    window_gap: int = 6,
    require_frames: bool = True,
    label: str = "",
) -> Tuple[bool, dict]:
    """验证应用在多个采样窗口内持续存活且渲染推进（防「卡加载误判成功」）。

    - 每个窗口：Activity 状态 RESUMED + 进程 pid 存在
    - 最后：gfxinfo 渲染帧数 > 0（证明画面在推进，非黑屏/卡加载）
    - 全部通过才判定成功。

    :return: (ok, metrics) metrics 含 samples / frames / pid。
    """
    samples = []
    for w in range(1, windows + 1):
        time.sleep(window_gap)
        state = adb_activity_state(serial, package)
        pid = adb_pid(serial, package)
        samples.append({"window": w, "state": state, "pid": pid})
        if not pid:
            break
        if state != "RESUMED":
            break
    frames = adb_gfx_frames(serial, package, seconds=3) if require_frames else -1
    metrics = {"samples": samples, "frames": frames, "windows_ok": len(samples) == windows}
    ok = True
    if len(samples) < windows:
        log_warn(f"{label}Activity 未在全部 {windows} 个窗口保持存活（可能卡加载/被覆盖）")
        ok = False
    if require_frames and frames <= 0:
        log_warn(f"{label}渲染帧数={frames}（≤0，疑似卡加载/黑屏）")
        ok = False
    return ok, metrics


def package_from_manifest(apk: Path) -> Optional[str]:
    code, output = run_subprocess(
        [tool("AAPT2"), "dump", "packagename", str(apk)],
        timeout=60,
    )
    if code == 0 and output.strip():
        return output.strip().splitlines()[0]
    return None


def launchable_activity(apk: Path) -> Optional[str]:
    code, output = run_subprocess(
        [
            tool("AAPT2"),
            "dump",
            "badging",
            str(apk),
        ],
        timeout=60,
    )
    for line in output.splitlines():
        if line.startswith("launchable-activity:"):
            # aapt2 输出: launchable-activity: name='com.foo.Bar' label='' icon=''
            # 必须解析 name='...' 的值，不能直接 split 取 token（会把 label='' 等一起带出）。
            m = re.search(r"name='([^']+)'", line)
            if m:
                return m.group(1)
            parts = line.split()
            if len(parts) >= 2:
                return parts[1].strip("'")
    return None


def ensure_dir(d):
    os.makedirs(d, exist_ok=True)


def require_cmd(cmd, hint=""):
    from shutil import which
    if not which(cmd):
        raise SystemExit(f"缺少命令: {cmd}")
    return True


def require_file(f):
    if not os.path.isfile(f):
        raise SystemExit(f"缺少文件: {f}")
    return True


def log_info(*args, **kwargs):
    print("[INFO] ", *args, file=sys.stderr)


def log_warn(*args, **kwargs):
    print("[WARN] ", *args, file=sys.stderr)


def log_error(*args, **kwargs):
    print("[ERROR]", *args, file=sys.stderr)


def log_step(msg: str):
    print(f"\n== {msg} ==", file=sys.stderr)


def log_success(*args, **kwargs):
    print("[OK]   ", *args, file=sys.stderr)


def fatal(message: str):
    log_error(message)
    raise SystemExit(1)


def append_status(name: str, stage: str, summary: str) -> None:
    """状态写入由 Agent 人工完成；本函数不再修改任何文件，仅保留签名兼容。"""
    pass


def update_status_toml(name: str) -> None:
    """状态文件更新由 Agent 人工完成；本函数不再修改任何文件。"""
    pass


def append_tool_call(name: str, stage: str, cmd_line: str) -> None:
    """工具调用记录由 Agent 人工写入；本函数不再修改任何文件，仅保留签名兼容。"""
    # 恢复完整实现：追加到 tool-calls.md（Agent 人工维护的状态文件）
    from datetime import datetime, timezone
    from pathlib import Path
    import os

    _crack_base = os.environ.get("CRACK_DIR", "")
    if not _crack_base:
        _type_arg = os.environ.get("TYPE", "").strip()
        _crack_base = str(
            Path(__file__).resolve().parents[4] / "crackings" / (_type_arg if _type_arg else "") / name
        )
    f = Path(_crack_base) / "tool-calls.md"
    f.parent.mkdir(parents=True, exist_ok=True)
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    entry = f"\n## [{now_iso}] {stage}\n```bash\n{cmd_line}\n```\n"
    with open(f, "a", encoding="utf-8") as fh:
        fh.write(entry)


def append_experience_sync_task(name: str, stage: str, focus: str) -> None:
    """提示 Agent 人工完成经验固化；本函数不写入任何文件。"""
    import sys
    sys.stderr.write(
        f"[提示] 经验固化待办（{stage}）：提炼本阶段经验与脚本，重点：{focus}\n"
        f"  流程：① 盘点会话新增/修复的脚本 → ② 落位对应 skill\n"
        f"  ③ 命名 <verb>-<scope>.py → ④ 登记 SCRIPTS-INDEX + skill scripts/README + tools-index\n"
        f"  ⑤ 追加经验到 [EXPERIENCES.md](../../../../EXPERIENCES.md) 对应节 / references/\n"
    )


def fatal(message: str) -> None:
    log_error(message)
    raise SystemExit(1)
