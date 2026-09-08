package com.fakerandroid.decoder.runtime.base;

import com.fakerandroid.decoder.util.PatchUtil;
import java.io.File;
import java.io.IOException;

/* JADX INFO: loaded from: RuntimeBase.class */
public class RuntimeBase {
    /** 注入 FakerAndroid 原版 base::tool（hook 引擎）到 cpp/libs/：来源 com.fakerandroid.tools.build:support:1.0.38.aar
     * 的 prefab（多 ABI libtool.a + faker.h + baseConfig.cmake），供 CMakeLists include(.../libs/baseConfig.cmake) + base::tool 链接。 */
    public static void mergeRuntimeLibsCpp(File out) throws IOException {
        PatchUtil.copyDirFromJar("/template/cpp/libs", out.getAbsolutePath());
    }

    public static void mergeRuntimeLibsJava(File out) throws IOException {
        PatchUtil.copyDirFromJar("/libs/java", out.getAbsolutePath());
    }

    public static void mergeRuntimeJavaCode(File out) throws IOException {
        PatchUtil.copyDirFromJar("/template/java", out.getAbsolutePath());
    }

    /** 注入「无 native 依赖」的 com.android.boot 骨架（APK 无 .so 时用，避免 loadLibrary/native 崩溃）。
     * 模板目录叫 template-nonative，避免与 template/java 前缀冲突（PatchUtil.copyJarResources 用 startsWith 前缀匹配，
     * template/java-nonative 会被 /template/java 误配 → 产物 java/-nonative/...）。 */
    public static void mergeRuntimeJavaCodeNonative(File out) throws IOException {
        PatchUtil.copyDirFromJar("/template-nonative", out.getAbsolutePath());
    }

    public static void mergeRuntimeCppCode(File out) throws IOException {
        PatchUtil.copyDirFromJar("/template/cpp", out.getAbsolutePath());
    }
}