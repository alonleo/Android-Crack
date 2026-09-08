package com.fakerandroid.decoder.apktool;

import brut.androlib.ApkDecoder;
import brut.androlib.Config;
import brut.directory.ExtFile;
import java.io.File;

/* JADX INFO: loaded from: Resources.class */
public class Resources {
    public static void decode(File in, File out) {
        Config config = new Config();
        config.mDecodeSources = 0;
        config.mForceDelete = true;
        ApkDecoder decoder = new ApkDecoder(new ExtFile(in), config);
        try {
            decoder.decode(out);
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}
