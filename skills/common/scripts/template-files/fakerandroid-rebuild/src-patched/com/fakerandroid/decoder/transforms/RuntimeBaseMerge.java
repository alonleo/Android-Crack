package com.fakerandroid.decoder.transforms;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import com.fakerandroid.decoder.pipeline.Transform;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.fakerandroid.decoder.runtime.base.RuntimeBase;
import com.fakerandroid.decoder.util.FileUtils;
import com.fakerandroid.decoder.util.ManifestEditor;
import com.fakerandroid.decoder.util.TextUtil;
import java.io.File;
import java.io.IOException;

/* JADX INFO: loaded from: RuntimeBaseMerge.class */
public class RuntimeBaseMerge extends Transform {
    public RuntimeBaseMerge(Apk apk, AndroidProject androidProject) {
        super(apk, androidProject);
    }

    @Override // com.fakerandroid.decoder.pipeline.Transform
    public boolean transform(TransformInvocation transformInvocation) {
        boolean hasNativeLibs = Boolean.TRUE.equals(this.androidProject.getIntermediate(AndroidProject.INTERMEDIATE_HAS_NATIVE_LIBS));
        if (!hasNativeLibs) {
            // 无 .so：仍注入 com.android.boot Java 骨架（无 native 依赖变体），跳过 cpp/hook 运行库
            transformInvocation.callBack("No native libs (.so) found - injecting com.android.boot java scaffolding only (no hook runtime).");
            try {
                RuntimeBase.mergeRuntimeJavaCodeNonative(this.androidProject.getJava());
                fixTmplCode(this.androidProject);
                return true;
            } catch (IOException e) {
                e.printStackTrace();
                return false;
            }
        }
        transformInvocation.callBack("Rumtime base mereging...");
        try {
            RuntimeBase.mergeRuntimeLibsJava(this.androidProject.getLibs());
            RuntimeBase.mergeRuntimeLibsCpp(this.androidProject.getCppLibs());
            try {
                RuntimeBase.mergeRuntimeJavaCode(this.androidProject.getJava());
                try {
                    RuntimeBase.mergeRuntimeCppCode(this.androidProject.getCpp());
                    fixTmplCode(this.androidProject);
                    return true;
                } catch (IOException e) {
                    return false;
                }
            } catch (IOException e2) {
                return false;
            }
        } catch (IOException e3) {
            e3.printStackTrace();
            return false;
        }
    }

    private void fixTmplCode(AndroidProject androidProject) {
        AndroidProject.ManifestInfo manifestInfo = (AndroidProject.ManifestInfo) androidProject.getIntermediate(AndroidProject.INTERMEDIATE_MANIFESTINFO);
        File fakerActivityFile = new File(androidProject.getJava(), "com/android/boot/MainActivity.java");
        try {
            FileUtils.autoReplaceStr(fakerActivityFile, "{R}", manifestInfo.getPakcageName() + ".R");
        } catch (IOException e) {
            e.printStackTrace();
        }
        File file = new File(androidProject.getJava(), "com/android/boot/App.java");
        String applicationName = manifestInfo.getApplicationName();
        if (!TextUtil.isEmpty(applicationName)) {
            try {
                FileUtils.autoReplaceStr(file, "{APPLICATION_NAME}", applicationName);
            } catch (IOException e2) {
                e2.printStackTrace();
            }
        } else {
            try {
                FileUtils.autoReplaceStr(file, "{APPLICATION_NAME}", "Application");
            } catch (IOException e3) {
                e3.printStackTrace();
            }
        }
        File manifest = androidProject.getAndroidManifest();
        try {
            ManifestEditor manifestEditor = new ManifestEditor(manifest);
            manifestEditor.modApplication("com.android.boot.App");
            manifestEditor.extractNativeLibs();
            manifestEditor.save();
        } catch (Exception e4) {
            e4.printStackTrace();
        }
    }
}
