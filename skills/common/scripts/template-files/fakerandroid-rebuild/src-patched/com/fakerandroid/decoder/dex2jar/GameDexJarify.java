package com.fakerandroid.decoder.dex2jar;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.file.Files;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import java.util.zip.ZipOutputStream;

/**
 * GameDexJarify — ASBuilder 生成工程补齐游戏 dex（纯 Java）。
 *
 * 背景: ASBuilder 用标准 AGP 不编译 src/main/smali（FakerAndroid 插件机制丢失），
 * 生成工程 APK 仅含骨架类(com.android.boot) → 游戏类/Firebase 全缺，安装启动即崩。
 *
 * 在 Transfer.translate() 骨架生成后执行：对原 APK 每个 dex
 *   ① 完整 dex2jar(Dex2jarCmd.doMain) 转 .class jar（每 dex 独立，避免 65536）
 *   ② 剔应用包名 BuildConfig/R$*（AGP 会生成同名，重复致 D8 merge 失败）
 *   ③ ASM 归一化 lambda 类名（'-'→'_'，dex2jar 只改了类定义名未改内部引用）
 *   ④ 写入门 app/libs/（build.gradle 的 implementation fileTree 原生打进 APK）
 */
public final class GameDexJarify {
    private final File apkFile;
    private final AndroidProject project;
    private final TransformInvocation cb;

    public GameDexJarify(File apkFile, AndroidProject project, TransformInvocation cb) {
        this.apkFile = apkFile;
        this.project = project;
        this.cb = cb;
    }

    public void run() throws Exception {
        File libs = project.getLibs();
        if (libs == null || !apkFile.isFile()) {
            cb.callBack("GameDexJarify: 跳过（libs 或 apk 不可用）");
            return;
        }
        // 清源 APK 自带的 AGP 构建元数据（resources/META-INF/com/android/build + games 引擎指纹），
        // 否则 AGP 打包时重建同名 entry → packageRelease 报 "cannot overwrite app-metadata.properties"。
        clearAgpMetadata();
        List<String> dexNames = listDex(apkFile);
        if (dexNames.isEmpty()) {
            cb.callBack("GameDexJarify: APK 无 dex");
            return;
        }
        File[] old = libs.listFiles((d, fn) -> fn.startsWith("classes") && fn.endsWith("dex.jar"));
        if (old != null) for (File o : old) o.delete();

        String appPkg = applicationId();
        File tmpDir = Files.createTempDirectory("gdx").toFile();
        // 全量类缓存（所有 dex jar + 目标归一化 jar），供补帧 getCommonSuperClass 解析超类链
        Map<String, byte[]> allClasses = new LinkedHashMap<>();

        // 阶段 1：每 dex 转 class jar + 剔 BuildConfig/R + lambda 归一化（不补帧），先存入 libs
        int idx = 0;
        List<File> stage1Jars = new ArrayList<>();
        for (String dexName : dexNames) {
            idx++;
            File dexFile = new File(tmpDir, dexName);
            try (ZipFile zf = new ZipFile(apkFile)) {
                try (InputStream in = zf.getInputStream(zf.getEntry(dexName));
                     FileOutputStream fo = new FileOutputStream(dexFile)) {
                    byte[] buf = new byte[8192];
                    int n;
                    while ((n = in.read(buf)) > 0) fo.write(buf, 0, n);
                }
            }
            File outJar = new File(libs, "classes." + idx + ".dex.jar");
            File tmpJar = new File(tmpDir, "c" + idx + ".jar");
            try {
                // ① 单 dex → class jar（完整 dex2jar）
                com.googlecode.dex2jar.tools.Dex2jarCmd cmd = new com.googlecode.dex2jar.tools.Dex2jarCmd();
                cmd.doMain("-f", "-o", tmpJar.getAbsolutePath(), dexFile.getAbsolutePath());
                // ② 剔应用包名 BuildConfig/R
                File stripped = new File(tmpDir, "cs" + idx + ".jar");
                stripConflicts(tmpJar, stripped, appPkg);
                // 先只归一化 lambda 名（不补帧，避免跨 jar 超类缺失）
                File normOnly = new File(tmpDir, "cn" + idx + ".jar");
                rewriteJar(stripped, normOnly, false);
                stage1Jars.add(normOnly);
                // 收集类缓存（含归一化后）
                collect(normOnly, allClasses);
            } finally {
                tmpJar.delete();
                dexFile.delete();
            }
            cb.callBack("GameDexJarify: " + outJar.getName() + " <- " + dexName);
        }
        // 阶段 2：统一补 StackMapTable（用全量类缓存解析跨 jar 超类）
        for (int i = 0; i < stage1Jars.size(); i++) {
            File src = stage1Jars.get(i);
            File outJar = new File(libs, "classes." + (i + 1) + ".dex.jar");
            rewriteJarFrames(src, outJar, allClasses);
            int nclass = countClass(outJar);
            cb.callBack("GameDexJarify: frames → " + outJar.getName() + " (" + nclass + " .class)");
        }
        try { for (File f : tmpDir.listFiles()) f.delete(); tmpDir.delete(); } catch (Exception ignored) {}
        cb.callBack("GameDexJarify: 游戏 dex 补齐完成 → " + libs.getAbsolutePath());
    }

    private static List<String> listDex(File apk) throws Exception {
        List<String> out = new ArrayList<>();
        try (ZipFile zf = new ZipFile(apk)) {
            long n = 0;
            while (true) {
                n++;
                String name = (n == 1) ? "classes.dex" : "classes" + n + ".dex";
                if (zf.getEntry(name) == null) break;
                out.add(name);
            }
        }
        return out;
    }

    /** 清理源 APK 资源残留，避免 AGP 构建/打包冲突：
     *  ① AGP 构建元数据（resources/META-INF/com/android/build 等，packageRelease 冲突）
     *  ② raw 布尔 item（Adobe AIR raws.xml 的 <item type=raw>true/false>，aapt2 不认 → Can not extract resource）
     *  ③ Unity split APK 的 splits0.xml（AGP 误判工程要 split）
     *  AGP 会在构建时重建 resources.arsc/META-INF 元数据，删源 APK 副本无副作用。 */
    private void clearAgpMetadata() {
        File main = project.getMain();
        File res = new File(main, "resources");
        if (res.isDirectory()) {
            File buildMeta = new File(res, "META-INF/com/android/build");
            deleteTree(buildMeta);
            File gradleMeta = new File(res, "META-INF/com/android/gradle");
            deleteTree(gradleMeta);
            File vci = new File(res, "META-INF/version-control-info.textproto");
            if (vci.isFile()) vci.delete();
            File fp = new File(res, "META-INF/com.android.games.engine.build_fingerprint");
            if (fp.isFile()) fp.delete();
        }
        // 清除所有 raws.xml 里的布尔 raw item（Adobe AIR 调试/配置标志，aapt2 不认 raw 类型布尔值）
        File valuesDir = new File(main, "res/values");
        if (valuesDir.isDirectory()) {
            File[] raws = valuesDir.listFiles((d, n) -> n.startsWith("raws") && n.endsWith(".xml"));
            if (raws != null) for (File rf : raws) stripBoolRawItems(rf);
        }
        // 删除 splits0.xml（Unity split asset pack 配置） + 移除 manifest 对它的引用（splits meta-data）
        File splits = new File(main, "res/xml/splits0.xml");
        boolean hadSplit = splits.isFile();
        if (splits.isFile()) { splits.delete(); System.out.println("I: GameDexJarify: removed res/xml/splits0.xml"); }
        if (hadSplit || hasSplitMetaData(main)) {
            File mf = new File(main, "AndroidManifest.xml");
            if (mf.isFile()) stripSplitMetaData(mf);
        }
    }

    /** 从 raws.xml 移除 <item type="raw" name="...">true|false</item>（布尔 raw，aapt2 拒绝）。 */
    private static void stripBoolRawItems(File f) {
        try {
            String t = new String(Files.readAllBytes(f.toPath()), java.nio.charset.StandardCharsets.UTF_8);
            String o = t;
            t = t.replaceAll("\\s*<item type=\"raw\" name=\"[^\"]*\">(true|false)</item>", "");
            if (!t.equals(o)) {
                Files.write(f.toPath(), t.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                System.out.println("I: GameDexJarify: stripped bool raws.xml " + f.getName());
            }
        } catch (Exception ex) { /* 忽略单个 raws.xml 失败 */ }
    }

    /** 判断 manifest 是否含 split meta-data（引用 @xml/splits0 等）。 */
    private static boolean hasSplitMetaData(File main) {
        File mf = new File(main, "AndroidManifest.xml");
        if (!mf.isFile()) return false;
        try {
            String t = new String(Files.readAllBytes(mf.toPath()), java.nio.charset.StandardCharsets.UTF_8);
            return t.contains("vending.splits") || t.contains("split_types") || t.matches("(?s).*splits\\d*\\.xml.*");
        } catch (Exception ex) { return false; }
    }

    /** 从 manifest 移除所有 split 相关（root 属性 + com.android.vending.splits meta-data）。 */
    private static void stripSplitMetaData(File mf) {
        try {
            String t = new String(Files.readAllBytes(mf.toPath()), java.nio.charset.StandardCharsets.UTF_8);
            String o = t;
            // 移除 root <manifest> 的 split 属性（决定系统是否要求 split）
            t = t.replaceAll("\\s+android:isSplitRequired=\"[^\"]*\"", "");
            t = t.replaceAll("\\s+android:requiredSplitTypes=\"[^\"]*\"", "");
            t = t.replaceAll("\\s+android:splitTypes=\"[^\"]*\"", "");
            // 移除 vending.splits meta-data
            t = t.replaceAll("(?s)\\s*<meta-data\\s+android:name=\"com\\.android\\.vending\\.splits[^\"]*\"\\s+android:(resource|value)=\"[^\"]*\"\\s*/>", "");
            if (!t.equals(o)) {
                Files.write(mf.toPath(), t.getBytes(java.nio.charset.StandardCharsets.UTF_8));
                System.out.println("I: GameDexJarify: stripped splits (attr + meta-data) from manifest");
            } else {
                System.out.println("I: GameDexJarify: manifest no split attr to strip");
            }
        } catch (Exception ex) { /* 忽略 */ }
    }

    private static void deleteTree(File f) {
        if (!f.exists()) return;
        if (f.isDirectory()) {
            File[] ch = f.listFiles();
            if (ch != null) for (File c : ch) deleteTree(c);
        }
        f.delete();
    }

    private String applicationId() {
        try {
            File bg = new File(project.getApp(), "build.gradle");
            if (bg.isFile()) {
                String text = new String(Files.readAllBytes(bg.toPath()), java.nio.charset.StandardCharsets.UTF_8);
                java.util.regex.Matcher m = java.util.regex.Pattern.compile("applicationId\\s+['\"]([^'\"]+)['\"]").matcher(text);
                if (m.find()) return m.group(1);
            }
            File mf = new File(project.getMain(), "AndroidManifest.xml");
            if (mf.isFile()) {
                String text = new String(Files.readAllBytes(mf.toPath()), java.nio.charset.StandardCharsets.UTF_8);
                java.util.regex.Matcher m = java.util.regex.Pattern.compile("package=\"([^\"]+)\"").matcher(text);
                if (m.find()) return m.group(1);
            }
        } catch (Exception ignored) {}
        return "";
    }

    private static boolean isConflict(String fn, String pkgPre) {
        if (!fn.endsWith(".class")) return false;
        String base = fn.substring(0, fn.length() - 6);
        if (base.endsWith("BuildConfig")) return true;
        if (base.endsWith("/R") || base.contains("/R$")) return !pkgPre.isEmpty() && fn.startsWith(pkgPre);
        return false;
    }

    private static void stripConflicts(File in, File out, String appPkg) throws Exception {
        String pre = appPkg.isEmpty() ? "" : appPkg.replace('.', '/') + "/";
        Map<String, byte[]> keep = new LinkedHashMap<>();
        try (ZipFile zf = new ZipFile(in)) {
            java.util.Enumeration<? extends ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                if (!isConflict(e.getName(), pre)) keep.put(e.getName(), zf.getInputStream(e).readAllBytes());
            }
        }
        try (ZipOutputStream zo = new ZipOutputStream(new FileOutputStream(out))) {
            for (Map.Entry<String, byte[]> me : keep.entrySet()) {
                zo.putNextEntry(new ZipEntry(me.getKey()));
                zo.write(me.getValue());
                zo.closeEntry();
            }
        }
    }

    private static int countClass(File jar) throws Exception {
        int n = 0;
        try (ZipFile zf = new ZipFile(jar)) {
            java.util.Enumeration<? extends ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) if (en.nextElement().getName().endsWith(".class")) n++;
        }
        return n;
    }

    /** 归一化 lambda 类名（'-'→'_'，不补帧）。 */
    private static void rewriteJar(File inJar, File outJar, boolean ignore) throws Exception {
        Map<String, byte[]> entries = new LinkedHashMap<>();
        try (ZipFile zf = new ZipFile(inJar)) {
            java.util.Enumeration<? extends ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                byte[] data = zf.getInputStream(e).readAllBytes();
                if (e.getName().endsWith(".class")) {
                    try {
                        org.objectweb.asm.ClassReader cr = new org.objectweb.asm.ClassReader(data);
                        org.objectweb.asm.ClassWriter cw = new org.objectweb.asm.ClassWriter(0);
                        org.objectweb.asm.commons.ClassRemapper remap =
                            new org.objectweb.asm.commons.ClassRemapper(cw, new LambdaNameMapper());
                        cr.accept(remap, org.objectweb.asm.ClassReader.EXPAND_FRAMES);
                        data = cw.toByteArray();
                    } catch (Exception ex) { /* 保留原始 */ }
                }
                entries.put(e.getName(), data);
            }
        }
        try (ZipOutputStream zo = new ZipOutputStream(new FileOutputStream(outJar))) {
            for (Map.Entry<String, byte[]> me : entries.entrySet()) {
                zo.putNextEntry(new ZipEntry(me.getKey()));
                zo.write(me.getValue());
                zo.closeEntry();
            }
        }
    }

    /** 收集 jar 内所有 .class 到类缓存（供补帧解析跨 jar 超类链）。 */
    private static void collect(File jar, Map<String, byte[]> cache) throws Exception {
        try (ZipFile zf = new ZipFile(jar)) {
            java.util.Enumeration<? extends ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                if (e.getName().endsWith(".class")) cache.put(e.getName(), zf.getInputStream(e).readAllBytes());
            }
        }
    }

    /** 补 StackMapTable（COMPUTE_FRAMES），getCommonSuperClass 用全量类缓存解析跨 jar 超类链。 */
    private static void rewriteJarFrames(File inJar, File outJar, Map<String, byte[]> allClasses) throws Exception {
        Map<String, byte[]> entries = new LinkedHashMap<>();
        try (ZipFile zf = new ZipFile(inJar)) {
            java.util.Enumeration<? extends ZipEntry> en = zf.entries();
            while (en.hasMoreElements()) {
                ZipEntry e = en.nextElement();
                byte[] data = zf.getInputStream(e).readAllBytes();
                if (e.getName().endsWith(".class")) {
                    try {
                        org.objectweb.asm.ClassReader cr = new org.objectweb.asm.ClassReader(data);
                        org.objectweb.asm.ClassWriter cw = new SuperClassAwareCW(org.objectweb.asm.ClassWriter.COMPUTE_FRAMES, allClasses);
                        cr.accept(cw, org.objectweb.asm.ClassReader.EXPAND_FRAMES);
                        data = cw.toByteArray();
                    } catch (Exception ex) { /* 无法补帧则保留(缺帧需避免,但单个失败可接受) */ }
                }
                entries.put(e.getName(), data);
            }
        }
        try (ZipOutputStream zo = new ZipOutputStream(new FileOutputStream(outJar))) {
            for (Map.Entry<String, byte[]> me : entries.entrySet()) {
                zo.putNextEntry(new ZipEntry(me.getKey()));
                zo.write(me.getValue());
                zo.closeEntry();
            }
        }
    }

    /** 自定义 ClassWriter：getCommonSuperClass 纯字节码解析跨 jar/缓存类的超类链，失败退回 Object。 */
    static final class SuperClassAwareCW extends org.objectweb.asm.ClassWriter {
        private final Map<String, byte[]> allClasses;
        SuperClassAwareCW(int flags, Map<String, byte[]> allClasses) { super(flags); this.allClasses = allClasses; }
        @Override protected String getCommonSuperClass(String type1, String type2) {
            if (type1.equals(type2)) return type1;
            java.util.List<String> a = ancestors(type1), b = ancestors(type2);
            for (String x : a) if (b.contains(x)) return x;
            return "java/lang/Object";
        }
        private java.util.List<String> ancestors(String type) {
            java.util.List<String> r = new java.util.ArrayList<>();
            java.util.Set<String> seen = new java.util.HashSet<>();
            String cur = type;
            for (int i = 0; i < 40 && cur != null && seen.add(cur); i++) {
                r.add(cur);
                byte[] c = allClasses.get(cur + ".class");
                if (c == null) break;
                try { cur = new org.objectweb.asm.ClassReader(c).getSuperName(); }
                catch (Exception ex) { break; }
            }
            return r;
        }
    }

    static final class LambdaNameMapper extends org.objectweb.asm.commons.Remapper {
        @Override public String map(String internalName) {
            return internalName.indexOf('-') >= 0 ? internalName.replace('-', '_') : internalName;
        }
        @Override public String mapFieldName(String owner, String name, String desc) { return name; }
        @Override public String mapMethodName(String owner, String name, String desc) { return name; }
        @Override public String mapDesc(String desc) {
            if (desc.indexOf('-') < 0) return desc;
            StringBuilder sb = new StringBuilder();
            int i = 0;
            while (i < desc.length()) {
                char c = desc.charAt(i);
                if (c == 'L') {
                    int j = desc.indexOf(';', i);
                    String inner = desc.substring(i + 1, j);
                    if (inner.indexOf('-') >= 0) inner = inner.replace('-', '_');
                    sb.append('L').append(inner).append(';');
                    i = j + 1;
                } else { sb.append(c); i++; }
            }
            return sb.toString();
        }
    }
}