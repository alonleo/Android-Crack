package com.fakerandroid.decoder.dex2jar;

import com.googlecode.d2j.converter.IR2JConverter;
import com.googlecode.d2j.dex.ClassVisitorFactory;
import com.googlecode.d2j.dex.Dex2Asm.ClzCtx;
import com.googlecode.d2j.dex.DexExceptionHandler;
import com.googlecode.d2j.dex.ExDex2Asm;
import com.googlecode.d2j.dex.LambadaNameSafeClassAdapter;
import com.googlecode.d2j.node.DexClassNode;
import com.googlecode.d2j.node.DexFileNode;
import com.googlecode.d2j.node.DexMethodNode;
import com.googlecode.d2j.reader.BaseDexFileReader;
import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.d2j.reader.zip.ZipUtil;
import com.googlecode.dex2jar.ir.IrMethod;
import com.googlecode.dex2jar.ir.stmt.LabelStmt;
import com.googlecode.dex2jar.ir.stmt.Stmt;
import java.io.File;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.file.FileSystem;
import java.nio.file.Files;
import java.nio.file.LinkOption;
import java.nio.file.OpenOption;
import java.nio.file.Path;
import java.nio.file.attribute.FileAttribute;
import java.nio.file.spi.FileSystemProvider;
import java.util.HashMap;
import java.util.Map;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;

/* JADX INFO: loaded from: PatchDex2jar.class */
public class PatchDex2jar {
    private DexExceptionHandler exceptionHandler;
    private final BaseDexFileReader reader;
    private int readerConfig;
    private int v3Config;

    public static PatchDex2jar from(byte[] in) throws IOException {
        return from(new DexFileReader(ZipUtil.readDex(in)));
    }

    public static PatchDex2jar from(ByteBuffer in) throws IOException {
        return from(new DexFileReader(in));
    }

    public static PatchDex2jar from(BaseDexFileReader reader) {
        return new PatchDex2jar(reader);
    }

    public static PatchDex2jar from(File in) throws IOException {
        return from(Files.readAllBytes(in.toPath()));
    }

    public static PatchDex2jar from(InputStream in) throws IOException {
        return from(new DexFileReader(in));
    }

    public static PatchDex2jar from(String in) throws IOException {
        return from(new File(in));
    }

    private PatchDex2jar(BaseDexFileReader reader) {
        this.reader = reader;
        this.readerConfig |= 1;
    }

    private void doTranslate(final Path dist) throws IOException {
        DexFileNode fileNode = new DexFileNode();
        try {
            this.reader.accept(fileNode, this.readerConfig | 32);
        } catch (Exception var4) {
            this.exceptionHandler.handleFileException(var4);
        }
        ClassVisitorFactory cvf = new ClassVisitorFactory() { // from class: com.fakerandroid.decoder.dex2jar.PatchDex2jar.1
            @Override // com.googlecode.d2j.dex.ClassVisitorFactory
            public ClassVisitor create(String name) {
                final ClassWriter cw = new ClassWriter(1);
                final LambadaNameSafeClassAdapter rca = new LambadaNameSafeClassAdapter(cw);
                return new ClassVisitor(Opcodes.ASM5, rca) { // from class: com.fakerandroid.decoder.dex2jar.PatchDex2jar.1.1
                    @Override // org.objectweb.asm.ClassVisitor
                    public void visitEnd() {
                        super.visitEnd();
                        String className = rca.getClassName();
                        try {
                            byte[] data = cw.toByteArray();
                            try {
                                Path dist1 = dist.resolve(className + ".class");
                                Path parent = dist1.getParent();
                                if (parent != null && !Files.exists(parent, new LinkOption[0])) {
                                    Files.createDirectories(parent, new FileAttribute[0]);
                                }
                                Files.write(dist1, data, new OpenOption[0]);
                            } catch (IOException var5) {
                                var5.printStackTrace(System.err);
                            }
                        } catch (Exception var6) {
                            System.err.println(String.format("ASM fail to generate .class file: %s", className));
                            PatchDex2jar.this.exceptionHandler.handleFileException(var6);
                        }
                    }
                };
            }
        };
        ExDex2Asm converter = new ExDex2Asm(this.exceptionHandler) { // from class: com.fakerandroid.decoder.dex2jar.PatchDex2jar.2
            @Override // com.googlecode.d2j.dex.ExDex2Asm, com.googlecode.d2j.dex.Dex2Asm
            public void convertCode(DexMethodNode methodNode, MethodVisitor mv, ClzCtx clzCtx) {
                if ((PatchDex2jar.this.readerConfig & 4) == 0 || !methodNode.method.getName().equals("<clinit>")) {
                    super.convertCode(methodNode, mv, clzCtx);
                }
            }

            @Override // com.googlecode.d2j.dex.Dex2Asm
            public void optimize(IrMethod irMethod) {
                T_cleanLabel.transform(irMethod);
                if (0 != (PatchDex2jar.this.v3Config & 2)) {
                }
                T_deadCode.transform(irMethod);
                T_removeLocal.transform(irMethod);
                T_removeConst.transform(irMethod);
                T_zero.transform(irMethod);
                if (T_npe.transformReportChanged(irMethod)) {
                    T_deadCode.transform(irMethod);
                    T_removeLocal.transform(irMethod);
                    T_removeConst.transform(irMethod);
                }
                T_new.transform(irMethod);
                T_fillArray.transform(irMethod);
                T_agg.transform(irMethod);
                T_multiArray.transform(irMethod);
                T_voidInvoke.transform(irMethod);
                if (0 != (PatchDex2jar.this.v3Config & 4)) {
                    int i = 0;
                    for (Stmt p : irMethod.stmts) {
                        if (p.st == Stmt.ST.LABEL) {
                            LabelStmt labelStmt = (LabelStmt) p;
                            int i2 = i;
                            i++;
                            labelStmt.displayName = "L" + i2;
                        }
                    }
                    System.out.println(irMethod);
                }
                T_type.transform(irMethod);
                T_unssa.transform(irMethod);
                T_ir2jRegAssign.transform(irMethod);
                T_trimEx.transform(irMethod);
            }

            @Override // com.googlecode.d2j.dex.Dex2Asm
            public void ir2j(IrMethod irMethod, MethodVisitor mv, ClzCtx clzCtx) {
                new IR2JConverter().optimizeSynchronized(0 != (8 & PatchDex2jar.this.v3Config)).ir(irMethod).asm(mv).convert();
            }
        };
        for (DexClassNode classNode : fileNode.clzs) {
            converter.convertClass(classNode, cvf, fileNode);
        }
    }

    public DexExceptionHandler getExceptionHandler() {
        return this.exceptionHandler;
    }

    public BaseDexFileReader getReader() {
        return this.reader;
    }

    public PatchDex2jar reUseReg(boolean b) {
        if (b) {
            this.v3Config |= 1;
        } else {
            this.v3Config &= -2;
        }
        return this;
    }

    public PatchDex2jar topoLogicalSort(boolean b) {
        if (b) {
            this.v3Config |= 2;
        } else {
            this.v3Config &= -3;
        }
        return this;
    }

    public PatchDex2jar noCode(boolean b) {
        if (b) {
            this.readerConfig |= 132;
        } else {
            this.readerConfig &= -133;
        }
        return this;
    }

    public PatchDex2jar optimizeSynchronized(boolean b) {
        if (b) {
            this.v3Config |= 8;
        } else {
            this.v3Config &= -9;
        }
        return this;
    }

    public PatchDex2jar printIR(boolean b) {
        if (b) {
            this.v3Config |= 4;
        } else {
            this.v3Config &= -5;
        }
        return this;
    }

    public PatchDex2jar reUseReg() {
        this.v3Config |= 1;
        return this;
    }

    public PatchDex2jar optimizeSynchronized() {
        this.v3Config |= 8;
        return this;
    }

    public PatchDex2jar printIR() {
        this.v3Config |= 4;
        return this;
    }

    public PatchDex2jar topoLogicalSort() {
        this.v3Config |= 2;
        return this;
    }

    public void setExceptionHandler(DexExceptionHandler exceptionHandler) {
        this.exceptionHandler = exceptionHandler;
    }

    public PatchDex2jar skipDebug(boolean b) {
        if (b) {
            this.readerConfig |= 1;
        } else {
            this.readerConfig &= -2;
        }
        return this;
    }

    public PatchDex2jar skipDebug() {
        this.readerConfig |= 1;
        return this;
    }

    /* JADX WARN: Bottom block not found for handler: all -> 0x005c */
    /*
        Code decompiled incorrectly, please refer to instructions dump.
        To view partially-correct add '--show-bad-code' argument
    */
    public void to(java.nio.file.Path r6) throws java.io.IOException {
        /*
            r5 = this;
            r0 = r6
            r1 = 0
            java.nio.file.LinkOption[] r1 = new java.nio.file.LinkOption[r1]
            boolean r0 = java.nio.file.Files.exists(r0, r1)
            if (r0 == 0) goto L1e
            r0 = r6
            r1 = 0
            java.nio.file.LinkOption[] r1 = new java.nio.file.LinkOption[r1]
            boolean r0 = java.nio.file.Files.isDirectory(r0, r1)
            if (r0 == 0) goto L1e
            r0 = r5
            r1 = r6
            r0.doTranslate(r1)
            goto L7f
        L1e:
            r0 = r6
            java.nio.file.FileSystem r0 = createZip(r0)
            r7 = r0
            r0 = 0
            r8 = r0
            r0 = r5
            r1 = r7
            java.lang.String r2 = "/"
            r3 = 0
            java.lang.String[] r3 = new java.lang.String[r3]     // Catch: java.lang.Throwable -> L54 java.lang.Throwable -> L5c
            java.nio.file.Path r1 = r1.getPath(r2, r3)     // Catch: java.lang.Throwable -> L54 java.lang.Throwable -> L5c
            r0.doTranslate(r1)     // Catch: java.lang.Throwable -> L54 java.lang.Throwable -> L5c
            r0 = r7
            if (r0 == 0) goto L7f
            r0 = r8
            if (r0 == 0) goto L4d
            r0 = r7
            r0.close()     // Catch: java.lang.Throwable -> L42
            goto L7f
        L42:
            r9 = move-exception
            r0 = r8
            r1 = r9
            r0.addSuppressed(r1)
            goto L7f
        L4d:
            r0 = r7
            r0.close()
            goto L7f
        L54:
            r9 = move-exception
            r0 = r9
            r8 = r0
            r0 = r9
            throw r0     // Catch: java.lang.Throwable -> L5c
        L5c:
            r10 = move-exception
            r0 = r7
            if (r0 == 0) goto L7c
            r0 = r8
            if (r0 == 0) goto L78
            r0 = r7
            r0.close()     // Catch: java.lang.Throwable -> L6d
            goto L7c
        L6d:
            r11 = move-exception
            r0 = r8
            r1 = r11
            r0.addSuppressed(r1)
            goto L7c
        L78:
            r0 = r7
            r0.close()
        L7c:
            r0 = r10
            throw r0
        L7f:
            return
        */
        throw new UnsupportedOperationException("Method not decompiled: com.fakerandroid.decoder.dex2jar.PatchDex2jar.to(java.nio.file.Path):void");
    }

    private static FileSystem createZip(Path output) throws IOException {
        Map<String, Object> env = new HashMap<>();
        env.put("create", "true");
        Path parent = output.getParent();
        if (parent != null && !Files.exists(parent, new LinkOption[0])) {
            Files.createDirectories(parent, new FileAttribute[0]);
        }
        for (FileSystemProvider p : FileSystemProvider.installedProviders()) {
            String s = p.getScheme();
            if ("jar".equals(s) || "zip".equalsIgnoreCase(s)) {
                return p.newFileSystem(output, (Map<String, ?>) env);
            }
        }
        throw new IOException("cant find zipfs support");
    }

    public PatchDex2jar withExceptionHandler(DexExceptionHandler exceptionHandler) {
        this.exceptionHandler = exceptionHandler;
        return this;
    }

    public PatchDex2jar skipExceptions(boolean b) {
        if (b) {
            this.readerConfig |= 256;
        } else {
            this.readerConfig &= -257;
        }
        return this;
    }
}
