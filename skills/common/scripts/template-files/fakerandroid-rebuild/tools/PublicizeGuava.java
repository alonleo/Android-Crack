import org.objectweb.asm.ClassReader;
import org.objectweb.asm.ClassWriter;
import org.objectweb.asm.Opcodes;
import org.objectweb.asm.commons.ClassRemapper;
import org.objectweb.asm.commons.Remapper;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.stream.Stream;

/**
 * PublicizeGuava — 把官方 guava 33.4.0 指定包下所有类的可见性提升为 public。
 *
 * 背景：apktool 2.11.1 的 R8 定制 guava 放宽了大量 package-private 类的可见性
 * （brut.androlib.* 跨包直接访问 guava 内部类）。官方版保持 package-private，
 * 导致运行时 IllegalAccessError。本工具对 com/google/common/** 全量 public 化，
 * 一次性消除所有此类冲突。
 *
 * 用法: java -cp asm-commons-9.5.jar:asm-9.5.jar:. PublicizeGuava <root-dir>
 */
public class PublicizeGuava {
    public static void main(String[] args) throws Exception {
        Path root = Paths.get(args[0]);
        int count = 0;
        try (Stream<Path> files = Files.walk(root.resolve("com/google/common"))) {
            for (Path p : (Iterable<Path>) files.filter(x -> x.toString().endsWith(".class"))::iterator) {
                byte[] data = Files.readAllBytes(p);
                ClassReader cr = new ClassReader(data);
                ClassWriter cw = new ClassWriter(0);
                cr.accept(new org.objectweb.asm.ClassVisitor(Opcodes.ASM9, cw) {
                    @Override
                    public void visit(int version, int access, String name, String signature, String superName, String[] interfaces) {
                        access = (access & ~Opcodes.ACC_PRIVATE & ~Opcodes.ACC_PROTECTED) | Opcodes.ACC_PUBLIC;
                        super.visit(version, access, name, signature, superName, interfaces);
                    }

                    @Override
                    public void visitInnerClass(String name, String outerName, String innerName, int access) {
                        access = (access & ~Opcodes.ACC_PRIVATE & ~Opcodes.ACC_PROTECTED) | Opcodes.ACC_PUBLIC;
                        super.visitInnerClass(name, outerName, innerName, access);
                    }

                    @Override
                    public org.objectweb.asm.MethodVisitor visitMethod(int access, String name, String desc, String signature, String[] exceptions) {
                        if (!"<clinit>".equals(name)) {
                            access = (access & ~Opcodes.ACC_PRIVATE & ~Opcodes.ACC_PROTECTED) | Opcodes.ACC_PUBLIC;
                        }
                        return super.visitMethod(access, name, desc, signature, exceptions);
                    }

                    @Override
                    public org.objectweb.asm.FieldVisitor visitField(int access, String name, String desc, String signature, Object value) {
                        access = (access & ~Opcodes.ACC_PRIVATE & ~Opcodes.ACC_PROTECTED) | Opcodes.ACC_PUBLIC;
                        return super.visitField(access, name, desc, signature, value);
                    }
                }, 0);
                Files.write(p, cw.toByteArray());
                count++;
            }
        }
        System.out.println("Publicized " + count + " classes under " + root);
    }
}
