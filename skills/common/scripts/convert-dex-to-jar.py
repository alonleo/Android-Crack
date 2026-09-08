#!/usr/bin/env python3
"""convert-dex-to-jar.py — DEX/APK → JAR 转换脚本。

修复 dex-tools BASEDIR bug 后，使用 Java -cp 直接调用
dex2jar，避免脚本 classpath 解析问题。
"""
import subprocess
import sys
from pathlib import Path

TOOL_DIR = Path(__file__).parent.parent / "crack-intergration-tools/execable/dex2jar"
CP = ":".join(str(j) for j in TOOL_DIR.glob("*.jar") if j.name not in ("d2j-smali-v2.4.jar",))


def dex_to_jar(apk_or_dex: Path, out_jar: Path) -> Path:
    cmd = [
        "java",
        "-cp", CP,
        "com.googlecode.dex2jar.tools.Dex2jarCmd",
        "-f", "-o", str(out_jar), str(apk_or_dex)
    ]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        print(f"STDERR: {r.stderr}", file=sys.stderr)
        r.check_returncode()
    return out_jar


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <input.apk|input.dex> <output.jar>", file=sys.stderr)
        sys.exit(1)
    inp = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve()
    result = dex_to_jar(inp, out)
    print(f"{inp} -> {result} ({result.stat().st_size / 1024 / 1024:.1f} MB)")
