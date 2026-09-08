package com.fakerandroid.decoder.transforms;

import com.fakerandroid.decoder.api.AndroidProject;
import com.fakerandroid.decoder.api.Apk;
import com.fakerandroid.decoder.pipeline.Transform;
import com.fakerandroid.decoder.pipeline.TransformInvocation;
import com.fakerandroid.decoder.smali.DexToSmaliException;
import com.fakerandroid.decoder.smali.SmaliDecoder;
import java.util.List;

/* JADX INFO: loaded from: DexToSmali.class */
public class DexToSmali extends Transform {
    public DexToSmali(Apk apk, AndroidProject androidProject) {
        super(apk, androidProject);
    }

    @Override // com.fakerandroid.decoder.pipeline.Transform
    public boolean transform(TransformInvocation transformInvocation) {
        transformInvocation.callBack("Translating dexes to smali files....");
        List<String> names = (List) this.androidProject.getIntermediate(AndroidProject.INTERMEDIATE_DEX_NAMES);
        AndroidProject.ManifestInfo s = (AndroidProject.ManifestInfo) this.androidProject.getIntermediate(AndroidProject.INTERMEDIATE_MANIFESTINFO);
        for (String name : names) {
            try {
                SmaliDecoder.decode(this.apk.getApkFile(), this.androidProject.getSmali(), name, true, Integer.valueOf(s.getMinSdkVersion()).intValue());
            } catch (DexToSmaliException e) {
                e.printStackTrace();
            }
        }
        return true;
    }
}
