package com.fakerandroid.decoder.dex2jar;

import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.dex2jar.tools.BaksmaliBaseDexExceptionHandler;
import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Map;
import java.util.TreeMap;
import java.util.logging.Logger;

/* JADX INFO: loaded from: Dex2jar.class */
public class Dex2jar {
    private static Logger logger = Logger.getLogger("Dex2jar");

    public static void toJar(File apk, File out) {
        TreeMap<String, DexFileReader> fileReaderTreeMap = null;
        try {
            fileReaderTreeMap = PatchMultiDexFileReader.open(Files.readAllBytes(apk.toPath()));
        } catch (IOException e) {
            e.printStackTrace();
        }
        BaksmaliBaseDexExceptionHandler handler = new BaksmaliBaseDexExceptionHandler();
        File outPath = new File(out, "classes.all.dex.jar");
        if (outPath.exists()) {
            outPath.delete();
        }
        for (Map.Entry<String, DexFileReader> entry : fileReaderTreeMap.entrySet()) {
            DexFileReader dexFileReader = entry.getValue();
            try {
                PatchDex2jar.from(dexFileReader).withExceptionHandler(handler).reUseReg(false).topoLogicalSort().skipDebug(false).optimizeSynchronized(false).printIR(false).noCode(false).skipExceptions(false).to(outPath.toPath());
            } catch (IOException e2) {
                logger.info("dex2jar fail :" + dexFileReader.getClassSize());
                e2.printStackTrace();
            }
        }
    }
}
