import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassVisitor;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.MethodVisitor;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.FieldVisitor;
import java.nio.file.Files;
import java.nio.file.Paths;

/**
 * PatchGuava — 官方 guava 33.4.0 的 apktool 兼容补丁。
 *
 * apktool 2.11.1 捆绑 R8 定制版 guava 子集（可见性放宽/旧签名/$r8$clinit 合成字段），
 * 而 dexlib2 2.5.2 需要官方完整版 guava。本工具在官方版上补齐 apktool 需要的差异：
 *
 *  1. Maps.capacity(II)I  → public（apktool ResourcesDecoder 跨包调用）
 *  2. ByteStreams 注入 $r8$clinit 静态字段（定制版 LittleEndianDataInputStream 引用它）
 *  3. Preconditions 注入旧版 void 签名桥接（定制版 Splitter/ImmutableList 等调用 (II)V）
 *
 * 用法: java -cp asm-9.5.jar:. PatchGuava <in.class> <out.class>
 */
public class PatchGuava {
    public static void main(String[] args) throws Exception {
        byte[] data = Files.readAllBytes(Paths.get(args[0]));
        ClassReader cr = new ClassReader(data);
        String name = cr.getClassName();
        ClassWriter cw = new ClassWriter(0);
        ClassVisitor cv = new ClassVisitor(Opcodes.ASM9, cw) {
            @Override
            public MethodVisitor visitMethod(int access, String mName, String desc, String sig, String[] ex) {
                // Maps.capacity → public（注意 desc 是 (I)I：单参数）
                if (name.equals("com/google/common/collect/Maps") && mName.equals("capacity") && desc.equals("(I)I")) {
                    access |= Opcodes.ACC_PUBLIC;
                }
                return super.visitMethod(access, mName, desc, sig, ex);
            }

            @Override
            public void visitEnd() {
                // ByteStreams 注入 $r8$clinit 静态字段（幂等：已存在则跳过）
                if (name.equals("com/google/common/io/ByteStreams") && !hasField(cr, "$r8$clinit")) {
                    FieldVisitor fv = super.visitField(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, "$r8$clinit", "I", null, Integer.valueOf(0));
                    if (fv != null) fv.visitEnd();
                }
                // Preconditions 注入 void 桥接
                if (name.equals("com/google/common/base/Preconditions")) {
                    addVoidBridge(cw, "checkPositionIndex", "(II)I", "(II)V");
                    addVoidBridge(cw, "checkElementIndex", "(II)I", "(II)V");
                }
                // ByteStreams 注入 R8 签名桥接（定制 LEDIS 调用 readFully(LEDIS,[B,I,I)V）
                if (name.equals("com/google/common/io/ByteStreams")) {
                    MethodVisitor mv = cw.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC,
                            "readFully", "(Lcom/google/common/io/LittleEndianDataInputStream;[BII)V", null,
                            new String[]{"java/io/IOException"});
                    mv.visitCode();
                    mv.visitVarInsn(Opcodes.ALOAD, 0);
                    mv.visitVarInsn(Opcodes.ALOAD, 1);
                    mv.visitVarInsn(Opcodes.ILOAD, 2);
                    mv.visitVarInsn(Opcodes.ILOAD, 3);
                    mv.visitMethodInsn(Opcodes.INVOKESTATIC, "com/google/common/io/ByteStreams",
                            "readFully", "(Ljava/io/InputStream;[BII)V", false);
                    mv.visitInsn(Opcodes.RETURN);
                    mv.visitMaxs(4, 4);
                    mv.visitEnd();
                }
                super.visitEnd();
            }
        };
        cr.accept(cv, 0);
        Files.write(Paths.get(args[1]), cw.toByteArray());
        System.out.println("Patched: " + args[1] + " (" + name + ")");
    }

    private static boolean hasField(ClassReader cr, String fName) {
        java.util.Set<String> found = new java.util.HashSet<>();
        cr.accept(new ClassVisitor(Opcodes.ASM9) {
            @Override
            public FieldVisitor visitField(int access, String n, String desc, String sig, Object value) {
                found.add(n);
                return null;
            }
        }, ClassReader.SKIP_CODE | ClassReader.SKIP_DEBUG);
        return found.contains(fName);
    }

    private static void addVoidBridge(ClassWriter cw, String mName, String intDesc, String voidDesc) {
        MethodVisitor mv = cw.visitMethod(Opcodes.ACC_PUBLIC | Opcodes.ACC_STATIC, mName, voidDesc, null, null);
        mv.visitCode();
        mv.visitVarInsn(Opcodes.ILOAD, 0);
        mv.visitVarInsn(Opcodes.ILOAD, 1);
        mv.visitMethodInsn(Opcodes.INVOKESTATIC, "com/google/common/base/Preconditions", mName, intDesc, false);
        mv.visitInsn(Opcodes.POP);
        mv.visitInsn(Opcodes.RETURN);
        mv.visitMaxs(2, 2);
        mv.visitEnd();
    }
}
