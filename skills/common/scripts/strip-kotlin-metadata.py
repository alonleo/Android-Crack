#!/usr/bin/env python3
"""strip-kotlin-metadata.py — 剥离 .class 的 kotlin.Metadata 注解

背景: `convert-smali-to-jars.py` 用 dex2jar 转出的 .class 中 Kotlin 类的
`@kotlin.Metadata` 注解（d1/d2 数组）常被 dex2jar 损坏（深嵌套/异常长度），
AGP 的 D8 `desugarReleaseFileDependencies` 解析 Kotlin metadata 时报
  "com.android.tools.r8.kotlin.H" / "java.lang.StackOverflowError"
修复方式: 用 ASM 移除所有 descriptor == "Lkotlin/Metadata;" 的类级注解。
Kotlin metadata 仅供反射/IDE 使用，剥离后 D8/R8 不再触碰，可正常 dex。

用法:
  python3 strip-kotlin-metadata.py <input.jar> -o <output.jar>
  python3 strip-kotlin-metadata.py <dir/>            # 批量处理目录内 *.jar → <dir>_stripped/

依赖: 同 fix-dex-jar-frames.py（JDK 11 + ASM 9.x）
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]

ASM_JARS = [
    "asm-util", "asm-analysis", "asm", "asm-commons", "asm-tree",
]

STRIPMETADATA_JAVA = r"""
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*;
import java.util.*;
import java.util.jar.*;

public class StripKotlinMetadata {
    public static void main(String[] args) throws Exception {
        JarFile in = new JarFile(args[0]);
        JarOutputStream out = new JarOutputStream(new FileOutputStream(args[1]));
        Enumeration<JarEntry> entries = in.entries();
        int stripped = 0, failed = 0;
        while (entries.hasMoreElements()) {
            JarEntry e = entries.nextElement();
            byte[] data = in.getInputStream(e).readAllBytes();
            JarEntry ne = new JarEntry(e.getName());
            if (e.getName().endsWith(".class")) {
                try {
                    ClassReader cr = new ClassReader(data);
                    ClassNode cn = new ClassNode();
                    cr.accept(cn, 0);
                    boolean removed = false;
                    if (cn.visibleAnnotations != null) {
                        removed |= cn.visibleAnnotations.removeIf(
                            a -> a.desc.equals("Lkotlin/Metadata;"));
                    }
                    if (cn.invisibleAnnotations != null) {
                        removed |= cn.invisibleAnnotations.removeIf(
                            a -> a.desc.equals("Lkotlin/Metadata;"));
                    }
                    ClassWriter cw = new ClassWriter(0);
                    cn.accept(cw);
                    byte[] result = cw.toByteArray();
                    if (removed) stripped++;
                    out.putNextEntry(ne);
                    out.write(result);
                    out.closeEntry();
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
        System.err.println("Stripped kotlin.Metadata: " + stripped + ", failed: " + failed);
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


def strip_jar(in_jar: Path, out_jar: Path) -> bool:
    java = _java_bin("java")
    javac = _java_bin("javac")
    asm_cp = _asm_classpath()
    with tempfile.TemporaryDirectory(prefix="stripmeta_") as tmp:
        tmp = Path(tmp)
        src = tmp / "StripKotlinMetadata.java"
        src.write_text(STRIPMETADATA_JAVA, encoding="utf-8")
        r = subprocess.run([javac, "--release", "11", "-cp", asm_cp, "-d", str(tmp), str(src)],
                           capture_output=True, text=True)
        if r.returncode != 0:
            print(f"[ERROR] javac 编译失败:\n{r.stderr[:500]}")
            return False
        r = subprocess.run([java, "-cp", f"{tmp}:{asm_cp}", "StripKotlinMetadata",
                            str(in_jar), str(out_jar)],
                           capture_output=True, text=True)
        print(r.stderr.strip())
        if r.returncode != 0:
            print(f"[ERROR] StripKotlinMetadata 执行失败:\n{r.stdout[:400]}\n{r.stderr[:400]}")
            return False
    return out_jar.is_file() and out_jar.stat().st_size > 0


def main() -> int:
    parser = argparse.ArgumentParser(description="剥离 kotlin.Metadata 注解（修复 D8 StackOverflowError）")
    parser.add_argument("input", help="jar 文件或包含 *.jar 的目录")
    parser.add_argument("-o", "--out", default=None, help="输出 jar（单文件模式）")
    args = parser.parse_args()

    inp = Path(args.input)
    if inp.is_file() and inp.suffix == ".jar":
        out = Path(args.out) if args.out else inp.with_name(inp.stem + "_stripped.jar")
        return 0 if strip_jar(inp, out) else 1

    if inp.is_dir():
        out_dir = Path(args.out) if args.out else inp.with_name(inp.name + "_stripped")
        out_dir.mkdir(parents=True, exist_ok=True)
        ok = True
        for jar in sorted(inp.glob("*.jar")):
            out = out_dir / jar.name
            print(f"== {jar.name} ==")
            ok = strip_jar(jar, out) and ok
        return 0 if ok else 1

    sys.exit(f"[ERROR] 输入必须是 jar 文件或目录: {inp}")


if __name__ == "__main__":
    sys.exit(main())
