package com.fakerandroid.decoder.transforms;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import com.fakerandroid.decoder.pipeline.Transform;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.fakerandroid.decoder.project.ProjectMerge;
import com.fakerandroid.decoder.util.FileUtils;
import com.fakerandroid.decoder.util.TextUtil;
import java.io.File;
import java.io.IOException;

/* JADX INFO: loaded from: Project.class */
public class Project extends Transform {
    public Project(Apk apk, AndroidProject androidProject) {
        super(apk, androidProject);
    }

    @Override // com.fakerandroid.decoder.pipeline.Transform
    public boolean transform(TransformInvocation transformInvocation) {
        transformInvocation.callBack("Android studio project fomarting....");
        try {
            ProjectMerge.copyProject(this.androidProject.getProject());
            // 强制 chmod +x gradlew：PatchUtil.copyJarResources 用 FileOutputStream 新文件会丢可执行位
            File gradlew = new File(this.androidProject.getProject(), "gradlew");
            if (gradlew.exists()) {
                gradlew.setExecutable(true, false);
            }
            boolean hasNativeLibs = Boolean.TRUE.equals(this.androidProject.getIntermediate(AndroidProject.INTERMEDIATE_HAS_NATIVE_LIBS));
            File appBuild = this.androidProject.getAppBuild();
            File simpleBuild = new File(appBuild.getParentFile(), "build.gradle.simple");
            if (hasNativeLibs) {
                // 带 .so 走 build.gradle（cmake hook 版），移除多余的 build.gradle.simple（copyProject 全拷的产物）
                if (simpleBuild.exists()) {
                    simpleBuild.delete();
                }
            } else {
                // 无 .so：用 build.gradle.simple（无 cmake 版）覆盖 build.gradle
                if (simpleBuild.exists()) {
                    appBuild.delete();
                    simpleBuild.renameTo(appBuild);
                    transformInvocation.callBack("No native libs - using ASBuilder build.gradle without cmake.");
                }
            }
            fixProject(this.androidProject);
            transformInvocation.callBack("You have faked a android studio project from apk!");
            transformInvocation.callBack("Generated project path:" + this.androidProject.getProject().getAbsolutePath() + ".");
            return true;
        } catch (IOException e) {
            e.printStackTrace();
            return false;
        }
    }

    private void fixProject(AndroidProject androidProject) {
        AndroidProject.ManifestInfo manifestInfo = (AndroidProject.ManifestInfo) androidProject.getIntermediate(AndroidProject.INTERMEDIATE_MANIFESTINFO);
        File appBuild = androidProject.getAppBuild();
        try {
            FileUtils.autoReplaceStr(appBuild, "{pkg}", manifestInfo.getPakcageName());
        } catch (IOException e) {
            e.printStackTrace();
        }
        String abiStr = "";
        File targetjniLibs = androidProject.getjniLibs();
        File jniLibsARMV7A = new File(targetjniLibs, "armeabi-v7a");
        File armeabi = new File(targetjniLibs, "armeabi");
        if (armeabi.exists() && !jniLibsARMV7A.exists()) {
            armeabi.renameTo(jniLibsARMV7A);
        }
        if (jniLibsARMV7A.exists()) {
            if (TextUtil.isEmpty(abiStr)) {
                abiStr = "'armeabi-v7a'";
            } else {
                abiStr = abiStr + ",'armeabi-v7a'";
            }
        }
        File jniLibsARM64V8A = new File(targetjniLibs, "arm64-v8a");
        if (jniLibsARM64V8A.exists()) {
            if (TextUtil.isEmpty(abiStr)) {
                abiStr = "'arm64-v8a'";
            } else {
                abiStr = abiStr + ",'arm64-v8a'";
            }
        }
        if (!jniLibsARMV7A.exists() && !jniLibsARM64V8A.exists() && !armeabi.exists()) {
            abiStr = "'armeabi-v7a','arm64-v8a'";
        }
        File jniLibsX86 = new File(targetjniLibs, "x86");
        if (jniLibsX86.exists()) {
            abiStr = abiStr + ",'x86'";
        }
        File jniLibsX86_64 = new File(targetjniLibs, "x86_64");
        if (jniLibsX86_64.exists()) {
            abiStr = abiStr + ",'x86_64'";
        }
        try {
            FileUtils.autoReplaceStr(appBuild, "{abi}", abiStr);
        } catch (IOException e2) {
            e2.printStackTrace();
        }
        try {
            FileUtils.autoReplaceStr(appBuild, "{versionCode}", manifestInfo.getVersionCode() != null ? manifestInfo.getVersionCode() : "1");
        } catch (IOException e3) {
            e3.printStackTrace();
        }
        try {
            FileUtils.autoReplaceStr(appBuild, "{versionName}", manifestInfo.getVersionName() != null ? manifestInfo.getVersionName() : "0.01");
        } catch (IOException e4) {
            e4.printStackTrace();
        }
        String minSdkStr = String.valueOf(manifestInfo.getMinSdkVersion());
        if (TextUtil.isEmpty(minSdkStr) || minSdkStr.equals("null")) {
            minSdkStr = "23"; // 默认，兼容模板
        }
        try {
            FileUtils.autoReplaceStr(appBuild, "{minSdkVersion}", minSdkStr);
        } catch (IOException e_min) {
            e_min.printStackTrace();
        }
        String targetSdkVersion = manifestInfo.getTargetSdkVersion();
        if (TextUtil.isEmpty(targetSdkVersion)) {
            try {
                FileUtils.autoReplaceStr(appBuild, "{targetSdkVersion}", "26");
                return;
            } catch (IOException e5) {
                e5.printStackTrace();
                return;
            }
        }
        try {
            FileUtils.autoReplaceStr(appBuild, "{targetSdkVersion}", targetSdkVersion);
        } catch (IOException e6) {
            e6.printStackTrace();
        }
    }
}
