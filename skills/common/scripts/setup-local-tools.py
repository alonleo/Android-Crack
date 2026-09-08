#!/usr/bin/env python3
"""setup-local-tools.py — 逆向工具本地安装（Linux / macOS 通用）
用法: python3 skills/common/scripts/setup-local-tools.py [--force]
"""

import argparse
import os
import platform
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
ENV_DIR = REPO / "tools" / "environments"
TOOLS_BIN = ENV_DIR / "bin"
SDK_DIR = ENV_DIR / "android-sdk"
MANIFEST = ENV_DIR / ".manifest"

JAVA_HOME_DIR = ENV_DIR / "jdk"
JADX_DIR = ENV_DIR / "jadx"
CLT_DIR = SDK_DIR / "cmdline-tools" / "latest"
APKTOOL_JAR = REPO / "tools" / "crack-intergration-tools" / "execable" / "apktool.jar"

OK = 0
FAIL = 0
FAILED_TOOLS = []


def header(title):
    w = 56
    line = "─" * w
    print(f"\n\033[1m\033[0;36m┌─{line}─┐\033[0m")
    print(f"\033[1m\033[0;36m│  {title:<{w}} │\033[0m")
    print(f"\033[1m\033[0;36m└─{line}─┘\033[0m")


def info(msg):
    print(f"  \033[0;34mℹ\033[0m  {msg}")


def ok(msg):
    global OK
    OK += 1
    print(f"  \033[0;32m✔\033[0m  {msg}")


def warn(msg):
    print(f"  \033[0;33m⚠\033[0m  {msg}", file=sys.stderr)


def fail(msg):
    global FAIL
    FAIL += 1
    print(f"  \033[0;31m✘\033[0m  {msg}", file=sys.stderr)


def sep(msg):
    print(f"  \033[0;36m──\033[0m {msg} \033[0;36m──\033[0m")


def fmt_size(b):
    if b >= 1073741824:
        return f"{b / 1073741824:.1f} GB"
    elif b >= 1048576:
        return f"{b / 1048576:.1f} MB"
    elif b >= 1024:
        return f"{b / 1024:.1f} KB"
    else:
        return f"{b} B"


def fmt_time(s):
    if s >= 3600:
        return f"{s // 3600}h{(s % 3600) // 60}m"
    elif s >= 60:
        return f"{s // 60}m{s % 60}s"
    else:
        return f"{s}s"


# ── 下载清单管理 ──


def manifest_init():
    if not MANIFEST.exists():
        MANIFEST.write_text("# tool_id|status|verify_path|ts\n")


def manifest_check(tool_id, verify_path):
    vp = str(verify_path)
    if not os.path.lexists(vp):
        return False
    if not MANIFEST.exists():
        return False
    for line in MANIFEST.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 3 and parts[0] == tool_id and parts[1] == "ok":
            return True
    return False


def manifest_mark(tool_id, status, verify_path):
    vp = str(verify_path)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
    lines = MANIFEST.read_text().splitlines() if MANIFEST.exists() else []
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("#") or not line.strip():
            new_lines.append(line)
            continue
        parts = line.split("|")
        if len(parts) >= 1 and parts[0] == tool_id:
            new_lines.append(f"{tool_id}|{status}|{vp}|{ts}")
            found = True
        else:
            new_lines.append(line)
    if not found:
        new_lines.append(f"{tool_id}|{status}|{vp}|{ts}")
    MANIFEST.write_text("\n".join(new_lines) + "\n")


def manifest_clear(tool_id):
    if not MANIFEST.exists():
        return
    lines = MANIFEST.read_text().splitlines()
    new_lines = [l for l in lines if not l.startswith(f"{tool_id}|")]
    MANIFEST.write_text("\n".join(new_lines) + "\n")


def manifest_list():
    if not MANIFEST.exists():
        return 0, 0
    ok_cnt = 0
    fail_cnt = 0
    for line in MANIFEST.read_text().splitlines():
        if line.startswith("#") or not line.strip():
            continue
        parts = line.split("|")
        if len(parts) >= 2:
            if parts[1] == "ok":
                ok_cnt += 1
            else:
                fail_cnt += 1
    return ok_cnt, fail_cnt


# ── 下载 + 解压 ──


def download(url, out_path, label):
    sep(f"下载 {label}")
    out_path = Path(out_path)
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=120) as resp:
            total = int(resp.headers.get("Content-Length", 0))
            downloaded = 0
            chunk_size = 8192
            with open(out_path, "wb") as f:
                while True:
                    chunk = resp.read(chunk_size)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total > 0:
                        pct = downloaded * 100 // total
                        bar = "#" * (pct // 2) + " " * (50 - pct // 2)
                        print(f"\r  \033[0;36m──\033[0m  {pct:3d}% [{bar}] {fmt_size(downloaded):>8} / {fmt_size(total):<8}  ", end="", file=sys.stderr)
                    else:
                        print(f"\r  \033[0;36m──\033[0m  {fmt_size(downloaded):>8}  ", end="", file=sys.stderr)
            if total > 0:
                print(file=sys.stderr)
        size = out_path.stat().st_size
        if size > 0:
            ok(f"{label} → {fmt_size(size)}")
            return True
        else:
            out_path.unlink(missing_ok=True)
            fail(f"{label} 下载失败（空文件）")
            return False
    except Exception as e:
        out_path.unlink(missing_ok=True)
        fail(f"{label} 下载失败: {e}")
        return False


def extract(archive, outdir, label):
    sep(f"解压 {label}")
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    archive = Path(archive)
    ext = archive.suffix
    if ext == ".zip" or str(archive).endswith(".zip"):
        result = subprocess.run(
            ["unzip", "-o", str(archive), "-d", str(outdir)],
            capture_output=True, text=True
        )
        lines = result.stdout.splitlines()
        file_count = sum(1 for l in lines if l.endswith(".class") or "inflating" in l or "extracting" in l)
        print(f"  \033[0;36m──\033[0m  解压: {file_count or len(lines)} 文件")
        print(f"  \033[0;36m──\033[0m  解压完成 \033[0;32m✓\033[0m")
    elif ext in (".gz", ".tgz") or str(archive).endswith(".tar.gz"):
        result = subprocess.run(
            ["tar", "-xzf", str(archive), "-C", str(outdir)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            fail(f"tar 解压失败: {result.stderr.strip()}")
        print(f"  \033[0;36m──\033[0m  解压完成 \033[0;32m✓\033[0m")
    else:
        fail(f"不支持的压缩格式: {archive}")


def check_skip(manifest_id, verify_path, label):
    if manifest_check(manifest_id, verify_path):
        info(f"{label} 已完成（清单记录）")
        return True
    if os.path.lexists(verify_path):
        info(f"{label} 已存在（补记清单）")
        manifest_mark(manifest_id, "ok", verify_path)
        return True
    return False


def run(cmd, **kwargs):
    return subprocess.run(cmd, **kwargs)


def ensure_parent(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def main():
    parser = argparse.ArgumentParser(description="Android 逆向工具链 · 本地一键安装")
    parser.add_argument("--force", "-f", action="store_true", help="清除所有已有工具后重新安装")
    args = parser.parse_args()

    # ── 平台检测 ──
    sys_os = platform.system()
    arch = platform.machine()

    if sys_os == "Linux":
        platform_os = "linux"
    elif sys_os == "Darwin":
        platform_os = "macos"
    else:
        print(f"不支持的平台: {sys_os}", file=sys.stderr)
        sys.exit(1)

    if arch in ("x86_64", "amd64"):
        jdk_arch = "x64"
    elif arch in ("aarch64", "arm64"):
        jdk_arch = "aarch64"
    else:
        print(f"不支持的架构: {arch}", file=sys.stderr)
        sys.exit(1)

    jdk_os = "mac" if platform_os == "macos" else platform_os
    sdk_platform = "mac" if platform_os == "macos" else "linux"
    jdk_url = f"https://api.adoptium.net/v3/binary/latest/21/ga/{jdk_os}/{jdk_arch}/jdk/hotspot/normal/eclipse"
    sdk_tools_url = f"https://dl.google.com/android/repository/commandlinetools-{sdk_platform}-11076708_latest.zip"

    # ── --force ──
    if args.force:
        print("\n  \033[0;33m\033[1m--force\033[0m 模式: 清除所有已有工具...")
        for p in [
            APKTOOL_JAR, JADX_DIR, SDK_DIR / "build-tools",
            SDK_DIR / "platform-tools", SDK_DIR / "platforms",
            JAVA_HOME_DIR, SDK_DIR / "cmdline-tools", MANIFEST,
        ]:
            if p.exists():
                if p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
                else:
                    p.unlink(missing_ok=True)
                print(f"  \033[0;31m✘\033[0m  清除 {p.name}")
        print()

    t_start = time.time()
    print("\033[1m\033[0;35m", end="")
    print("╔════════════════════════════════════════╗")
    print("║   Android 逆向工具链 · 本地一键安装    ║")
    print("╚════════════════════════════════════════╝\033[0m")
    print(f"  工作区: \033[1m{REPO}\033[0m")
    print(f"  平台:   \033[1m{platform_os} / {arch}\033[0m")

    manifest_init()

    # ── 依赖检查 ──
    has_dl = None
    for c in ("wget", "curl"):
        if shutil.which(c):
            has_dl = c
            break
    has_dl = has_dl or "urllib"

    if not shutil.which("unzip"):
        fail("需要 unzip")
        sys.exit(1)
    if not shutil.which("python3"):
        warn("python3 未安装（frida 安装会跳过）")
    if platform_os == "macos" and not shutil.which("xz"):
        warn("xz 未安装（JDK 解压可能需要）")

    TOOLS_BIN.mkdir(parents=True, exist_ok=True)
    SDK_DIR.mkdir(parents=True, exist_ok=True)
    JAVA_HOME_DIR.mkdir(parents=True, exist_ok=True)

    # ═══════════════════════ 1/6  JDK ═══════════════════════
    header("1/6  Eclipse Temurin JDK 21")
    jdk_java = JAVA_HOME_DIR / "jdk-21" / "bin" / "java"

    if manifest_check("jdk", jdk_java):
        info("JDK 21 已完成（清单记录）")
    elif jdk_java.exists():
        info(f"本地 JDK 已就绪 → {jdk_java.parent}")
        manifest_mark("jdk", "ok", jdk_java)
    else:
        t0 = time.time()
        if download(jdk_url, "/tmp/jdk.tar.gz", f"Temurin JDK 21 ({jdk_os}/{jdk_arch})"):
            extract("/tmp/jdk.tar.gz", JAVA_HOME_DIR, "JDK 21")

            for d in JAVA_HOME_DIR.iterdir():
                if d.is_dir():
                    java_bin = d / "bin" / "java"
                    if java_bin.exists() and java_bin.is_file() and d.name != "jdk-21":
                        shutil.move(str(d), str(JAVA_HOME_DIR / "jdk-21"))
                        break

            Path("/tmp/jdk.tar.gz").unlink(missing_ok=True)

            if jdk_java.exists():
                manifest_mark("jdk", "ok", jdk_java)
                ok(f"JDK 21 ({fmt_time(time.time() - t0)})")
            else:
                manifest_mark("jdk", "fail", jdk_java)
                fail("JDK 安装失败")

    # 设置 JDK 环境
    jdk_home = None
    for d in JAVA_HOME_DIR.iterdir():
        if d.is_dir() and (d / "bin" / "java").exists():
            jdk_home = str(d)
            os.environ["JAVA_HOME"] = jdk_home
            os.environ["PATH"] = f"{jdk_home}/bin:{os.environ.get('PATH', '')}"
            break

    # ═══════════════════════ 2/6  apktool ═══════════════════════
    header("2/6  apktool")
    if check_skip("apktool", APKTOOL_JAR, "apktool"):
        pass
    else:
        APKTOOL_JAR.parent.mkdir(parents=True, exist_ok=True)
        t0 = time.time()
        if download(
            "https://github.com/iBotPeaches/Apktool/releases/download/v2.11.1/apktool_2.11.1.jar",
            APKTOOL_JAR, "apktool_2.11.1.jar"
        ):
            manifest_mark("apktool", "ok", APKTOOL_JAR)
            ok(f"apktool ({fmt_time(time.time() - t0)})")
        else:
            manifest_mark("apktool", "fail", APKTOOL_JAR)

    # ═══════════════════════ 3/6  jadx ═══════════════════════
    header("3/6  jadx 反编译器")
    jadx_bin = JADX_DIR / "bin" / "jadx"
    if manifest_check("jadx", jadx_bin):
        info("jadx 已完成（清单记录）")
    elif jadx_bin.exists():
        info("jadx 已存在")
        manifest_mark("jadx", "ok", jadx_bin)
    else:
        t0 = time.time()
        JADX_DIR.mkdir(parents=True, exist_ok=True)
        if download(
            "https://github.com/skylot/jadx/releases/download/v1.5.1/jadx-1.5.1.zip",
            "/tmp/jadx.zip", "jadx-1.5.1.zip"
        ):
            extract("/tmp/jadx.zip", JADX_DIR, "jadx")
            for f in [JADX_DIR / "bin" / "jadx", JADX_DIR / "bin" / "jadx-gui"]:
                if f.exists():
                    f.chmod(0o755)
            Path("/tmp/jadx.zip").unlink(missing_ok=True)

            if jadx_bin.exists():
                manifest_mark("jadx", "ok", jadx_bin)
                ok(f"jadx ({fmt_time(time.time() - t0)})")
            else:
                manifest_mark("jadx", "fail", jadx_bin)
                fail("jadx 安装失败")

    # ═══════════════════════ 4/6  Android SDK cmdline-tools ═══════════════════════
    header("4/6  Android SDK 命令行工具")
    sdkmanager = CLT_DIR / "bin" / "sdkmanager"
    if manifest_check("cmdline-tools", sdkmanager):
        info("cmdline-tools 已完成（清单记录）")
    elif sdkmanager.exists():
        info("cmdline-tools 已存在")
        manifest_mark("cmdline-tools", "ok", sdkmanager)
    else:
        t0 = time.time()
        (SDK_DIR / "cmdline-tools").mkdir(parents=True, exist_ok=True)
        if download(sdk_tools_url, "/tmp/cmdline-tools.zip", "cmdline-tools.zip"):
            extract("/tmp/cmdline-tools.zip", SDK_DIR / "cmdline-tools", "cmdline-tools")

            # 整理为 cmdline-tools/latest/
            nested = SDK_DIR / "cmdline-tools" / "cmdline-tools"
            if nested.exists():
                CLT_DIR.mkdir(parents=True, exist_ok=True)
                for item in nested.iterdir():
                    shutil.move(str(item), str(CLT_DIR / item.name))
                shutil.rmtree(nested, ignore_errors=True)
            elif not sdkmanager.exists():
                CLT_DIR.mkdir(parents=True, exist_ok=True)
                for item in (SDK_DIR / "cmdline-tools").iterdir():
                    if item.name != "latest" and item.is_dir():
                        for sub in item.iterdir():
                            shutil.move(str(sub), str(CLT_DIR / sub.name))
                        shutil.rmtree(item, ignore_errors=True)

            Path("/tmp/cmdline-tools.zip").unlink(missing_ok=True)

            if sdkmanager.exists():
                manifest_mark("cmdline-tools", "ok", sdkmanager)
                ok(f"cmdline-tools ({fmt_time(time.time() - t0)})")
            else:
                manifest_mark("cmdline-tools", "fail", sdkmanager)
                fail("cmdline-tools 安装失败")

    # ═══════════════════════ 5/6  SDK 组件 ═══════════════════════
    header("5/6  Android SDK 组件（耗时较长）")
    os.environ["ANDROID_HOME"] = str(SDK_DIR)

    def check_installed(path):
        p = Path(path)
        return p.is_dir() and any(True for _ in p.iterdir())

    sdk_components = [
        ("build-tools;35.0.0", SDK_DIR / "build-tools" / "35.0.0"),
        ("platform-tools", SDK_DIR / "platform-tools"),
        ("platforms;android-35", SDK_DIR / "platforms" / "android-35"),
    ]

    need = []
    for comp_name, comp_path in sdk_components:
        mf_id = f"sdk-{comp_name}"
        if manifest_check(mf_id, comp_path):
            info(f"{comp_name} 已完成（清单记录）")
        elif check_installed(comp_path):
            info(f"{comp_name} 已存在")
            manifest_mark(mf_id, "ok", comp_path)
        else:
            need.append((comp_name, comp_path))

    if need:
        need_names = [n for n, _ in need]
        info(f"需要安装: {' '.join(need_names)}")
        sep("sdkmanager 开始下载（输出为 SDK 自身进度）")
        print("\033[0;33m")
        result = run(
            [str(sdkmanager)] + need_names,
            input="y\n".encode(),
            cwd=str(SDK_DIR),
        )
        print("\033[0m")

        for comp_name, comp_path in need:
            mf_id = f"sdk-{comp_name}"
            if comp_path.is_dir() and any(True for _ in comp_path.iterdir()):
                manifest_mark(mf_id, "ok", comp_path)
                ok(f"{comp_name} 安装完成")
            else:
                manifest_mark(mf_id, "fail", comp_path)
                fail(f"{comp_name} 安装失败")

    # ═══════════════════════ 6/6  frida ═══════════════════════
    header("6/6  frida 动态插桩")
    frida_path = shutil.which("frida")
    if manifest_check("frida", frida_path or "/nonexistent"):
        info("frida 已完成（清单记录）")
    elif frida_path:
        ver = run(["frida", "--version"], capture_output=True, text=True).stdout.strip() or "?"
        manifest_mark("frida", "ok", frida_path)
        ok(f"frida v{ver} 已安装")
    else:
        if shutil.which("python3"):
            sep("pip3 install frida-tools")
            result = run(
                [sys.executable, "-m", "pip", "install", "frida-tools"],
                capture_output=True, text=True
            )
            for line in result.stdout.splitlines():
                if "Downloading" in line:
                    print(f"  \033[0;36m──\033[0m  ⏬  {line.strip()}")
                elif "Installing" in line:
                    print(f"  \033[0;36m──\033[0m  🔧  {line.strip()}")
                elif "Successfully" in line:
                    print(f"  \033[0;32m──\033[0m  ✅  {line.strip()}")
                elif "ERROR" in line or "error" in line.lower():
                    print(f"  \033[0;31m──\033[0m  ✘  {line.strip()}", file=sys.stderr)
            for line in result.stderr.splitlines():
                if "ERROR" in line or "error" in line.lower():
                    print(f"  \033[0;31m──\033[0m  ✘  {line.strip()}", file=sys.stderr)

            frida_path = shutil.which("frida")
            if frida_path:
                ver = run(["frida", "--version"], capture_output=True, text=True).stdout.strip() or "?"
                manifest_mark("frida", "ok", frida_path)
                ok(f"frida v{ver}")
            else:
                manifest_mark("frida", "fail", "")
                warn("frida 安装失败，可稍后手动: pip3 install frida-tools")
        else:
            manifest_mark("frida", "fail", "")
            warn("python3 未安装，跳过 frida")

    # ═══════════════════════ 验证 ═══════════════════════
    header("验证所有工具")

    print(f"\n  \033[1m下载清单:\033[0m {MANIFEST}")
    ok_cnt, fail_cnt = manifest_list()
    print(f"  \033[1m状态:\033[0m  \033[0;32m{ok_cnt} 完成\033[0m", end="")
    if fail_cnt:
        print(f"  \033[0;31m{fail_cnt} 失败\033[0m", end="")
    print("\n")

    errors = 0
    tools_to_check = ["java", "keytool", "apktool", "jadx", "aapt2", "apksigner", "zipalign", "adb", "frida"]
    for tool_name in tools_to_check:
        tp = shutil.which(tool_name)
        if tp:
            print(f"  \033[0;32m{tool_name:<12}\033[0m {tp}")
        else:
            print(f"  \033[0;31m{tool_name:<12}\033[0m \033[0;31m未找到\033[0m")
            errors += 1

    if jdk_home:
        java_ver = run([str(Path(jdk_home) / "bin" / "java"), "-version"],
                       capture_output=True, text=True).stderr.splitlines()[0]
        print(f"  \033[0;32m{'JAVA_HOME':<12}\033[0m {jdk_home}")
        print(f"  \033[0;32m{'java -version':<12}\033[0m {java_ver}")

    t_end = time.time()
    print(f"\n\033[1m\033[0;35m════════════════════════════════════════\033[0m")
    print(f"  总耗时: {fmt_time(t_end - t_start)}")
    if errors == 0:
        print(f"  \033[0;32m\033[1m全部就绪 ✓\033[0m")
    else:
        print(f"  \033[0;31m\033[1m{errors} 个工具未找到\033[0m")
    print(f"\033[1m\033[0;35m════════════════════════════════════════\033[0m")
    print(f"\n  位置:")
    print(f"    \033[0;34mtools/environments/jdk/\033[0m")
    print(f"    \033[0;34mtools/crack-intergration-tools/execable/apktool.jar\033[0m")
    print(f"    \033[0;34mtools/environments/jadx/\033[0m")
    print(f"    \033[0;34mtools/environments/android-sdk/\033[0m")
    print(f"    \033[0;34mtools/environments/bin/\033[0m")
    print(f"\n  使用:")
    print(f"    \033[0;33mbash skills/common/scripts/crack.sh apks/<你的APK>\033[0m")


if __name__ == "__main__":
    main()
