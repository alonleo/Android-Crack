package com.fakerandroid.decoder.api;

import java.io.File;
import java.util.HashMap;
import java.util.Map;

/* JADX INFO: loaded from: AndroidProject.class */
public class AndroidProject {
    public static final String INTERMEDIATE_DEX_NAMES = "dexes";
    public static final String INTERMEDIATE_MANIFESTINFO = "manifest-info";
    public static final String INTERMEDIATE_HAS_NATIVE_LIBS = "has-native-libs";
    private Map<String, Object> intermediate = new HashMap();
    private File project;

    public void addIntermediate(String key, Object o) {
        this.intermediate.put(key, o);
    }

    public Object getIntermediate(String key) {
        return this.intermediate.get(key);
    }

    public AndroidProject(File project) {
        this.project = project;
    }

    public File getProject() {
        return this.project;
    }

    public File getProjectBuild() {
        return new File(getProject(), "build.gradle");
    }

    public File getApp() {
        File file = new File(getProject(), "app");
        return file;
    }

    public File getAppBuild() {
        File file = new File(getApp(), "build.gradle");
        return file;
    }

    private File getAppSrc() {
        File file = new File(getApp(), "src");
        return file;
    }

    public File getMain() {
        return new File(getAppSrc(), "main");
    }

    public File getAndroidManifest() {
        File file = new File(getMain(), "AndroidManifest.xml");
        return file;
    }

    public File getSmali() {
        File file = new File(getMain(), "smali");
        return file;
    }

    public File getjniLibs() {
        File file = new File(getMain(), "jniLibs");
        return file;
    }

    public File getAssets() {
        File file = new File(getMain(), "assets");
        return file;
    }

    public File getCpp() {
        File file = new File(getMain(), "cpp");
        return file;
    }

    public File getCppLibs() {
        File file = new File(getCpp(), "libs");
        return file;
    }

    public File getResources() {
        File file = new File(getMain(), "resources");
        return file;
    }

    public File getGradle() {
        File file = new File(getProject(), "gradle");
        return file;
    }

    public File getJava() {
        File file = new File(getMain(), "java");
        return file;
    }

    public File getLibs() {
        File file = new File(getApp(), "libs");
        return file;
    }

    public File getJavaScaffoding() {
        File file = new File(getApp(), "javaScaffoding");
        return file;
    }

    public File getRes() {
        File file = new File(getMain(), "res");
        return file;
    }

    public File getYmlFile() {
        File file = new File(getMain(), "apktool.yml");
        return file;
    }

    /* JADX INFO: loaded from: AndroidProject$ManifestInfo.class */
    public static class ManifestInfo {
        private String minSdkVersion;
        private String targetSdkVersion;
        private String pakcageName;
        private String applicationName;
        private String versionCode;
        private String versionName;

        public String getMinSdkVersion() {
            if (this.minSdkVersion == null) {
                return "23";
            }
            return this.minSdkVersion;
        }

        public void setMinSdkVersion(String minSdkVersion) {
            this.minSdkVersion = minSdkVersion;
        }

        public String getTargetSdkVersion() {
            if (this.targetSdkVersion == null) {
                return "28";
            }
            return this.targetSdkVersion;
        }

        public void setTargetSdkVersion(String targetSdkVersion) {
            this.targetSdkVersion = targetSdkVersion;
        }

        public String getPakcageName() {
            return this.pakcageName;
        }

        public void setPakcageName(String pakcageName) {
            this.pakcageName = pakcageName;
        }

        public String getApplicationName() {
            return this.applicationName;
        }

        public void setApplicationName(String applicationName) {
            this.applicationName = applicationName;
        }

        public String getVersionCode() {
            return this.versionCode;
        }

        public void setVersionCode(String versionCode) {
            this.versionCode = versionCode;
        }

        public String getVersionName() {
            return this.versionName;
        }

        public void setVersionName(String versionName) {
            this.versionName = versionName;
        }

        public String toString() {
            return "ManifestInfo{minSdkVersion='" + this.minSdkVersion + "', targetSdkVersion='" + this.targetSdkVersion + "', pakcageName='" + this.pakcageName + "', applicationName='" + this.applicationName + "', versionCode='" + this.versionCode + "', versionName='" + this.versionName + "'}";
        }
    }
}
