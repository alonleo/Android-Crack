package com.fakerandroid.decoder.pipeline;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import java.util.List;
import java.util.logging.Logger;

/* JADX INFO: loaded from: Context.class */
public class Context {
    TransformManager transformManager;
    AndroidProject androidProject;
    List<Apk> apks;
    Logger logger = Logger.getLogger(getClass().getName());

    public List<Apk> getApks() {
        return this.apks;
    }

    public TransformManager getTransformManager() {
        return this.transformManager;
    }

    public AndroidProject getAndroidProject() {
        return this.androidProject;
    }

    public Logger getLogger() {
        return this.logger;
    }

    public Context(TransformManager transformManager, List<Apk> apks, AndroidProject androidProject) {
        this.transformManager = transformManager;
        this.apks = apks;
        this.androidProject = androidProject;
    }
}
