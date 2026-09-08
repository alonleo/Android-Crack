package com.fakerandroid.decoder.pipeline;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;

/* JADX INFO: loaded from: Transform.class */
public abstract class Transform {
    protected Apk apk;
    protected AndroidProject androidProject;

    public abstract boolean transform(TransformInvocation transformInvocation);

    public Transform(Apk apk, AndroidProject androidProject) {
        this.apk = apk;
        this.androidProject = androidProject;
    }
}
