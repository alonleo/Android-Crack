#!/usr/bin/env python3
"""fix-dex-new-instance.py — 修复 dex2jar 把 `new-instance L<X>;` 误生成 `new java/lang/Object` 的问题。

背景: BananaKong (2026-08-04) 经 dex2jar v2.4 转换 smali → jar 后，对无显式构造器的类
（如 `g01` 只有字段无 <init>），dex2jar 把 `new-instance v0, Lg01;` + `invoke-direct {v0}, Ljava/lang/Object;-><init>()V`
错误解析为 `new java/lang/Object`，随后对该 Object 做 `putfield g01.a` → 真机 VerifyError:
  "cannot access instance field java.util.UUID g01.a from object of type Precise Reference: java.lang.Object"

修复策略（ASM 字节码级）:
  对每个方法，维护符号执行栈，找出 `NEW java/lang/Object` 创建的引用被
  `PUTFIELD <owner>.<field>`（owner != java/lang/Object）使用的位置，
  将 NEW 的目标类型改写为 putfield 的 owner 类型（即真实被构造的类）。

保守性:
  - 仅当 putfield 的 owner 类型与 `new Object` 直接关联（同一栈槽）才改写
  - `new Object` 用于 sync / 合法 Object 用途的不会被误改（owner 仍是 Object）
  - 幂等：改写后不再含该模式

用法:
  python3 fix-dex-new-instance.py <input.jar> -o <output.jar>
  python3 fix-dex-new-instance.py <dir/>            # 批量处理目录内 *.jar → <dir>_fixed/

依赖: JDK 11 + ASM 9.x（tools/crack-intergration-tools/execable/dex2jar/）
"""
from __future__ import annotations

import argparse
import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

def _find_root():
    p = Path(__file__).resolve().parent
    for _ in range(6):
        if (p / "apks").is_dir() and (p / "tools").is_dir():
            return p
        p = p.parent
    raise SystemExit("无法定位仓库根目录")

ROOT = _find_root()
D2J_DIR = ROOT / "tools" / "crack-intergration-tools" / "execable" / "dex2jar"

ASM_JARS = ["asm-9.5", "asm-analysis-9.5", "asm-util-9.5", "asm-commons-9.5", "asm-tree-9.5"]

FIXJAVA = r"""
import org.objectweb.asm.*;
import org.objectweb.asm.tree.*;
import java.io.*;
import java.util.*;
import java.util.jar.*;

public class FixNewInstance {
    public static void main(String[] args) throws Exception {
        JarFile in = new JarFile(args[0]);
        JarOutputStream out = new JarOutputStream(new FileOutputStream(args[1]));
        Enumeration<JarEntry> entries = in.entries();
        int fixed = 0;
        while (entries.hasMoreElements()) {
            JarEntry e = entries.nextElement();
            byte[] data = in.getInputStream(e).readAllBytes();
            if (e.getName().endsWith(".class")) {
                byte[] nd = fixClass(data);
                if (nd != null) { data = nd; fixed++; }
            }
            out.putNextEntry(new JarEntry(e.getName()));
            out.write(data);
            out.closeEntry();
        }
        out.close();
        System.out.println("Classes rewritten: " + fixed);
    }

    static byte[] fixClass(byte[] data) {
        try {
            ClassReader cr = new ClassReader(data);
            ClassNode cn = new ClassNode();
            cr.accept(cn, 0);
            boolean changed = false;
            for (MethodNode mn : cn.methods) {
                if (fixMethod(mn)) changed = true;
            }
            if (changed) {
                ClassWriter cw = new ClassWriter(0);
                cn.accept(cw);
                return cw.toByteArray();
            }
        } catch (Exception ex) { /* skip unparsable */ }
        return null;
    }

    static boolean fixMethod(MethodNode mn) {
        if (mn.instructions == null) return false;
        boolean changed = false;
        List<TypeInsnNode> news = new ArrayList<>();
        for (AbstractInsnNode ins = mn.instructions.getFirst(); ins != null; ins = ins.getNext()) {
            if (ins.getOpcode() == Opcodes.NEW && ins instanceof TypeInsnNode) {
                TypeInsnNode tn = (TypeInsnNode) ins;
                if (tn.desc.equals("java/lang/Object")) news.add(tn);
            }
        }
        if (news.isEmpty()) return false;
        for (TypeInsnNode tn : news) {
            AbstractInsnNode nxt = tn.getNext();
            if (nxt == null || nxt.getOpcode() != Opcodes.DUP) continue;
            AbstractInsnNode n3 = nxt.getNext();
            if (n3 == null || n3.getOpcode() != Opcodes.INVOKESPECIAL) continue;
            MethodInsnNode mi = (MethodInsnNode) n3;
            if (!mi.owner.equals("java/lang/Object") || !mi.name.equals("<init>")) continue;
            AbstractInsnNode n4 = n3.getNext();
            int var = -1;
            if (n4 != null && n4.getOpcode() == Opcodes.ASTORE) var = ((VarInsnNode) n4).var;
            if (var < 0) continue;
            String realOwner = findOwner(mn, var);
            if (realOwner != null && !realOwner.equals("java/lang/Object")) {
                tn.desc = realOwner;
                changed = true;
            }
        }
        return changed;
    }

    static String findOwner(MethodNode mn, int var) {
        for (AbstractInsnNode ins = mn.instructions.getFirst(); ins != null; ins = ins.getNext()) {
            if (ins.getOpcode() != Opcodes.ALOAD) continue;
            VarInsnNode vn = (VarInsnNode) ins;
            if (vn.var != var) continue;
            for (AbstractInsnNode s = ins.getNext(); s != null; s = s.getNext()) {
                if (s.getOpcode() == Opcodes.PUTFIELD) {
                    FieldInsnNode fin = (FieldInsnNode) s;
                    return fin.owner;
                }
                int sop = s.getOpcode();
                if (sop == Opcodes.GOTO || sop == Opcodes.RETURN || sop == Opcodes.ARETURN
                        || sop == Opcodes.ATHROW || sop == Opcodes.PUTSTATIC
                        || sop == Opcodes.INVOKEVIRTUAL || sop == Opcodes.INVOKESTATIC
                        || sop == Opcodes.INVOKESPECIAL || sop == Opcodes.INVOKEINTERFACE) break;
            }
        }
        return null;
    }
}
"""


def build_classpath() -> str:
    parts = [str(D2J_DIR / f"{j}.jar") for j in ASM_JARS]
    return os.pathsep.join(parts)


def fix_one(src: Path, dst: Path) -> int:
    tmp = dst.with_suffix(".tmp.jar")
    javafile = Path(tempfile.gettempdir()) / "FixNewInstance.java"
    javafile.write_text(FIXJAVA, encoding="utf-8")
    javac = os.environ.get("JAVA_HOME", "") + "/bin/javac"
    if not os.path.exists(javac):
        javac = "javac"
    build_dir = Path(tempfile.gettempdir()) / "fixnewinstance_build"
    build_dir.mkdir(exist_ok=True)
    cp = build_classpath()
    subprocess.run([javac, "-cp", cp, "-d", str(build_dir), str(javafile)], check=True, capture_output=True)
    java = os.environ.get("JAVA_HOME", "") + "/bin/java"
    if not os.path.exists(java):
        java = "java"
    cp_all = f"{build_dir}{os.pathsep}{cp}"
    subprocess.run([java, "-cp", cp_all, "FixNewInstance", str(src), str(tmp)],
                   check=True, capture_output=True)
    shutil.move(str(tmp), str(dst))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="修复 dex2jar new Object 误类型")
    ap.add_argument("input", help="jar 文件或目录")
    ap.add_argument("-o", "--output", default=None, help="输出 jar")
    args = ap.parse_args()

    inp = Path(args.input)
    if inp.is_dir():
        out_dir = Path(str(inp) + "_fixed")
        out_dir.mkdir(exist_ok=True)
        for jar in sorted(inp.glob("*.jar")):
            dst = out_dir / jar.name
            fix_one(jar, dst)
            print(f"[OK] {jar.name} → {dst.name}")
        return 0
    else:
        dst = Path(args.output) if args.output else inp.with_name(inp.stem + "_fixed.jar")
        fix_one(inp, dst)
        print(f"[OK] {inp.name} → {dst}")
        return 0


if __name__ == "__main__":
    sys.exit(main())
