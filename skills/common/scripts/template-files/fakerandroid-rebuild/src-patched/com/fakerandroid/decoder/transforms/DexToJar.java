package com.fakerandroid.decoder.transforms;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import com.fakerandroid.decoder.dex2jar.Dex2jar;
import com.fakerandroid.decoder.pipeline.Transform;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import java.io.File;

/* JADX INFO: loaded from: DexToJar.class */
public class DexToJar extends Transform {
    public DexToJar(Apk apk, AndroidProject androidProject) {
        super(apk, androidProject);
    }

    @Override // com.fakerandroid.decoder.pipeline.Transform
    public boolean transform(TransformInvocation transformInvocation) {
        transformInvocation.callBack("Translating dexes to java scaffodding jar....");
        try {
            File javaScaffoding = this.androidProject.getJavaScaffoding();
            if (javaScaffoding.exists()) {
                javaScaffoding.delete();
            }
            javaScaffoding.mkdirs();
            Dex2jar.toJar(this.apk.getApkFile(), javaScaffoding);
            return true;
        } catch (Exception e) {
            transformInvocation.callBack("Translating dexes to java scaffodding jar happen exception....");
            return true;
        }
    }
}
