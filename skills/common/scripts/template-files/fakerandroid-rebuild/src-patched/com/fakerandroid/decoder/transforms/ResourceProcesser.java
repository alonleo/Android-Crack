package com.fakerandroid.decoder.transforms;

import brut.androlib.apk.ApkInfo;
import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import com.fakerandroid.decoder.apktool.Resources;
import com.fakerandroid.decoder.pipeline.Transform;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.fakerandroid.decoder.util.FileUtils;
import com.fakerandroid.decoder.util.ManifestEditor;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import org.dom4j.DocumentException;

/* JADX INFO: loaded from: ResourceProcesser.class */
public class ResourceProcesser extends Transform {
    @Override // com.fakerandroid.decoder.pipeline.Transform
    public boolean transform(TransformInvocation transformInvocation) {
        transformInvocation.callBack("Deocoding the apk file...");
        File out = this.androidProject.getMain();
        if (out.exists()) {
            FileUtils.deleteDir(out);
        }
        out.mkdirs();
        Resources.decode(this.apk.getApkFile(), out);
        project(this.androidProject);
        discard(this.androidProject);
        meta(this.androidProject);
        fixRes(this.androidProject);
        detectNativeLibs(this.androidProject);
        transformInvocation.callBack("native libs present: " + Boolean.TRUE.equals(this.androidProject.getIntermediate(AndroidProject.INTERMEDIATE_HAS_NATIVE_LIBS)));
        return true;
    }

    /**
     * Detects whether the decoded project contains any native libraries (.so).
     * Runs after lib/ has been renamed to jniLibs/. Result is stored as an
     * intermediate so downstream transforms (RuntimeBaseMerge / Project) can
     * skip the native hook runtime when there is nothing to hook.
     */
    private void detectNativeLibs(AndroidProject androidProject) {
        boolean hasNative = containsSoFile(androidProject.getjniLibs());
        androidProject.addIntermediate(AndroidProject.INTERMEDIATE_HAS_NATIVE_LIBS, Boolean.valueOf(hasNative));
    }

    private boolean containsSoFile(File dir) {
        if (dir == null || !dir.exists() || !dir.isDirectory()) {
            return false;
        }
        File[] children = dir.listFiles();
        if (children == null) {
            return false;
        }
        for (File child : children) {
            if (child.isDirectory()) {
                if (containsSoFile(child)) {
                    return true;
                }
            } else if (child.getName().endsWith(".so")) {
                return true;
            }
        }
        return false;
    }

    public ResourceProcesser(Apk apk, AndroidProject androidProject) {
        super(apk, androidProject);
    }

    private void meta(AndroidProject androidProject) {
        File manifest = androidProject.getAndroidManifest();
        AndroidProject.ManifestInfo manifestInfo = new AndroidProject.ManifestInfo();
        ApkInfo metaInfo = null;
        try {
            metaInfo = ApkInfo.load(new FileInputStream(androidProject.getYmlFile()));
        } catch (FileNotFoundException ex) {
            ex.printStackTrace();
        }
        try {
            ManifestEditor manifestEditor = new ManifestEditor(manifest);
            String packageName = manifestEditor.getPackagenName();
            manifestInfo.setPakcageName(packageName);
            String applicationName = manifestEditor.getApplicationName();
            manifestInfo.setApplicationName(applicationName);
        } catch (DocumentException e) {
            e.printStackTrace();
        }
        if (metaInfo != null) {
            manifestInfo.setVersionCode(metaInfo.versionInfo.versionCode);
            manifestInfo.setVersionName(metaInfo.versionInfo.versionName);
            manifestInfo.setMinSdkVersion((String) metaInfo.sdkInfo.get("minSdkVersion"));
            manifestInfo.setTargetSdkVersion((String) metaInfo.sdkInfo.get("targetSdkVersion"));
        }
        androidProject.addIntermediate(AndroidProject.INTERMEDIATE_MANIFESTINFO, manifestInfo);
    }

    private void discard(AndroidProject androidProject) {
        File resources = androidProject.getMain();
        List<File> fs = Arrays.asList(resources.listFiles());
        List<String> dexnames = new ArrayList<>();
        for (File f : fs) {
            String fn = f.getName();
            if (fn.startsWith("classes") && fn.endsWith(".dex")) {
                dexnames.add(fn);
                f.delete();
            }
        }
        androidProject.addIntermediate(AndroidProject.INTERMEDIATE_DEX_NAMES, dexnames);
    }

    private void project(AndroidProject androidProject) {
        File resources = androidProject.getMain();
        if (!resources.exists()) {
            return;
        }
        File libResources = new File(resources, "lib");
        if (libResources.exists()) {
            libResources.renameTo(androidProject.getjniLibs());
        }
        File unknownResources = new File(resources, "unknown");
        if (unknownResources.exists()) {
            unknownResources.renameTo(androidProject.getResources());
        }
        File originalResources = new File(resources, "original");
        if (originalResources.exists()) {
            File assets = androidProject.getAssets();
            if (!assets.exists()) {
                assets.mkdirs();
            }
            originalResources.renameTo(new File(assets, "original"));
        }
    }

    void fixRes(AndroidProject androidProject) {
        try {
            File fileRes = androidProject.getRes();
            func(fileRes, fileRes);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void func(File res, File file) {
        File[] fs = file.listFiles();
        for (File f : fs) {
            if (f.isDirectory()) {
                func(res, f);
            }
            if (f.isFile() && f.getName().startsWith("$")) {
                File fixName = new File(f.getParent(), f.getName().replace("$", ""));
                funcRe(res, getFileNameNoEx(f.getName()), getFileNameNoEx(fixName.getName()));
                f.renameTo(fixName);
            }
        }
    }

    public static String getFileNameNoEx(String filename) {
        int dot;
        if (filename != null && filename.length() > 0 && (dot = filename.lastIndexOf(46)) > -1 && dot < filename.length()) {
            return filename.substring(0, dot);
        }
        return filename;
    }

    private static void funcRe(File file, String oStr, String nStr) {
        File[] fs = file.listFiles();
        for (File f : fs) {
            if (f.isDirectory()) {
                funcRe(f, oStr, nStr);
            }
            if (f.isFile()) {
                try {
                    if (f.getName().endsWith(".xml")) {
                        FileUtils.autoReplaceStr(f, oStr, nStr);
                    }
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}
