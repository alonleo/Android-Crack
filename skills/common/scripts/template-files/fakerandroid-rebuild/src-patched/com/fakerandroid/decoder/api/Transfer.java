package com.fakerandroid.decoder.api;

import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.fakerandroid.decoder.pipeline.TransformManager;
import com.fakerandroid.decoder.transforms.DexToJar;
import com.fakerandroid.decoder.transforms.DexToSmali;
import com.fakerandroid.decoder.transforms.Il2cppDumper;
import com.fakerandroid.decoder.transforms.Project;
import com.fakerandroid.decoder.transforms.ResourceProcesser;
import com.fakerandroid.decoder.transforms.RuntimeBaseMerge;
import com.fakerandroid.decoder.transforms.RuntimeIl2cppMerge;
import java.io.File;

/* JADX INFO: loaded from: Transfer.class */
public class Transfer {
    private File in;
    private File out;
    TransformInvocation transformInvocation;

    public Transfer(String inPath, String outPath, TransformInvocation transformInvocation) {
        this.in = new File(inPath);
        this.out = new File(outPath);
        this.transformInvocation = transformInvocation;
    }

    public void translate() {
        TransformManager transformManager = new TransformManager(this.transformInvocation);
        Apk apk = new Apk(this.in);
        AndroidProject androidProject = new AndroidProject(this.out);
        System.out.println(apk.getApkFile().getAbsolutePath());
        if (!this.in.exists()) {
            this.transformInvocation.callBack("In file not exist..");
            return;
        }
        if (!this.in.getAbsolutePath().endsWith(".apk")) {
            this.transformInvocation.callBack("not a apk file..");
        }
        transformManager.addTransform(new ResourceProcesser(apk, androidProject));
        transformManager.addTransform(new DexToSmali(apk, androidProject));
        transformManager.addTransform(new DexToJar(apk, androidProject));
        transformManager.addTransform(new Il2cppDumper(apk, androidProject));
        transformManager.addTransform(new RuntimeBaseMerge(apk, androidProject));
        transformManager.addTransform(new RuntimeIl2cppMerge(apk, androidProject));
        transformManager.addTransform(new Project(apk, androidProject));
        transformManager.action();
        // 补齐游戏 dex：标准 AGP 不编译 smali，ASBuilder 骨架 APK 仅含骨架类。
        // 对原 APK 每个 dex 单独 jar 化（避免 65536）→ 剔 BuildConfig → FixStackmaps
        // → ASM lambda 类名归一化 → 放 app/libs/，使游戏类进入最终 APK。
        try {
            com.fakerandroid.decoder.dex2jar.GameDexJarify jarify =
                new com.fakerandroid.decoder.dex2jar.GameDexJarify(this.in, androidProject, this.transformInvocation);
            jarify.run();
        } catch (Exception ex) {
            this.transformInvocation.callBack("ASBuilder: 游戏 dex 补齐异常(非致命): " + ex);
            ex.printStackTrace();
        }
    }
}