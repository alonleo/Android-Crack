package com.fakerandroid.decoder.pipeline;

import java.util.ArrayList;
import java.util.List;

/* JADX INFO: loaded from: TransformManager.class */
public class TransformManager {
    TransformInvocation transformInvocation;
    private final List<TransformStream> streams = new ArrayList();
    private final List<Transform> transforms = new ArrayList();

    public TransformManager(TransformInvocation transformInvocation) {
        this.transformInvocation = transformInvocation;
    }

    public void addStream(TransformStream stream) {
        this.streams.add(stream);
    }

    public List<TransformStream> getStreams() {
        return this.streams;
    }

    public void addTransform(Transform transform) {
        this.transforms.add(transform);
    }

    public void action() {
        for (Transform transform : this.transforms) {
            if (!transform.transform(this.transformInvocation)) {
                this.transformInvocation.callBack("finish on " + transform.getClass().getName());
                return;
            }
        }
    }
}
