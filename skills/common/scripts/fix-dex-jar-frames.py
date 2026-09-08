#!/usr/bin/env python3
"""fix-dex-jar-frames.py — 修复 dex2jar 产出的 .class 缺少 StackMapTable 问题。

背景: `convert-smali-to-jars.py` 用 dex2jar v2.4 把 dex → 真 .class jar，
但非线形控制流（switch/try-catch）的方法缺少 StackMapTable，
AGP 的 D8 `desugarReleaseFileDependencies` 报:
  "D8: Expected stack map table for method with non-linear control flow."
  "ERROR:D8: com.android.tools.r8.kotlin.H"
本脚本用 ASM 重算每个类的 StackMapTable（COMPUTE_FRAMES），修复 D8 消费。

用法:
  python3 fix-dex-jar-frames.py <input.jar> -o <output.jar>
  python3 fix-dex-jar-frames.py <dir/>            # 批量处理目录内 *.jar → <dir>_fixed/

依赖:
  - JDK 11（环境变量 JAVA_HOME 或 tools/environments/jdk/）
  - ASM 9.x jar（tools/crack-intergration-tools/execable/dex2jar/asm-*.jar）
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

ASM_JARS = [
    "asm-util", "asm-analysis", "asm", "asm-commons", "asm-tree",
]

FIXFRAMES_JAVA = r"""
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*;
import java.util.*;
import java.util.jar.*;

public class FixFrames {
    public static void main(String[] args) throws Exception {
        JarFile in = new JarFile(args[0]);
        JarOutputStream out = new JarOutputStream(new FileOutputStream(args[1]));
        Enumeration<JarEntry> entries = in.entries();
        int fixed = 0, failed = 0;
        while (entries.hasMoreElements()) {
            JarEntry e = entries.nextElement();
            byte[] data = in.getInputStream(e).readAllBytes();
            JarEntry ne = new JarEntry(e.getName());
            if (e.getName().endsWith(".class")) {
                try {
                    ClassReader cr1 = new ClassReader(data);
                    ClassWriter cw1 = new ClassWriter(0);
                    cr1.accept(cw1, 0);
                    ClassReader cr2 = new ClassReader(cw1.toByteArray());
                    ClassWriter cw2 = new ClassWriter(cr2, ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);
                    cr2.accept(cw2, 0);
                    out.putNextEntry(ne);
                    out.write(cw2.toByteArray());
                    out.closeEntry();
                    fixed++;
                    continue;
                } catch (Exception ex) {
                    failed++;
                }
            }
            out.putNextEntry(ne);
            out.write(data);
            out.closeEntry();
        }
        in.close();
        out.close();
        System.err.println("Fixed: " + fixed + ", failed: " + failed);
    }
}
"""


def _java_bin(name: str) -> str:
    jh = os.environ.get("JAVA_HOME")
    cand = []
    if jh:
        cand.append(Path(jh) / "bin" / name)
    cand.append(ROOT / "tools/environments/jdk/jdk-11.0.31+11/bin" / name)
    for c in cand:
        if c.is_file():
            return str(c)
    sys.exit(f"[ERROR] 找不到 {name}（JAVA_HOME 未设置）")


def _asm_classpath() -> str:
    d2j = ROOT / "tools/crack-intergration-tools/execable/dex2jar"
    paths = [str(d2j / f"{n}-9.5.jar") for n in ASM_JARS]
    return ":".join(p for p in paths if Path(p).is_file())


def fix_jar(in_jar: Path, out_jar: Path) -> bool:
    java = _java_bin("java")
    javac = _java_bin("javac")
    asm_cp = _asm_classpath()
    with tempfile.TemporaryDirectory(prefix="fixframes_") as tmp:
        tmp = Path(tmp)
        src = tmp / "FixFrames.java"
        src.write_text(FIXFRAMES_JAVA, encoding="utf-8")
        r = subprocess.run([javac, "--release", "11", "-cp", asm_cp, "-d", str(tmp), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[ERROR] javac 编译失败:\n{r.stderr[:500]}")
            return False
        r = subprocess.run([java, "-cp", f"{tmp}:{asm_cp}", "FixFrames", str(in_jar), str(out_jar)],
                           capture_output=True, text=True)
        print(r.stderr.strip())
        if r.returncode != 0:
            print(f"[ERROR] FixFrames 执行失败:\n{r.stdout[:400]}\n{r.stderr[:400]}")
            return False
    return out_jar.is_file() and out_jar.stat().st_size > 0


def main() -> int:
    parser = argparse.ArgumentParser(description="修复 dex2jar 产出的 StackMapTable 缺失")
    parser.add_argument("input", help="jar 文件或包含 *.jar 的目录")
    parser.add_argument("-o", "--out", default=None, help="输出 jar（单文件模式）")
    args = parser.parse_args()

    inp = Path(args.input)
    if inp.is_file() and inp.suffix == ".jar":
        out = Path(args.out) if args.out else inp.with_name(inp.stem + "_fixed.jar")
        return 0 if fix_jar(inp, out) else 1

    if inp.is_dir():
        out_dir = Path(args.out) if args.out else inp.with_name(inp.name + "_fixed")
        out_dir.mkdir(parents=True, exist_ok=True)
        ok = True
        for jar in sorted(inp.glob("*.jar")):
            out = out_dir / jar.name
            print(f"== {jar.name} ==")
            ok = fix_jar(jar, out) and ok
        return 0 if ok else 1

    sys.exit(f"[ERROR] 输入必须是 jar 文件或目录: {inp}")


if __name__ == "__main__":
    sys.exit(main())
