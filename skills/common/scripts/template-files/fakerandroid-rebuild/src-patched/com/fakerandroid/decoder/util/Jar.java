package com.fakerandroid.decoder.util;

import com.fakerandroid.decoder.exception.FileException;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.ThreadLocalRandom;
import org.apache.commons.io.IOUtils;

/* JADX INFO: loaded from: Jar.class */
public abstract class Jar {
    private static final Set<String> mLoaded = new HashSet();
    private static final Map<String, File> mExtracted = new HashMap();

    public static File getResourceAsFile(String name, Class clazz) throws FileException {
        File file = mExtracted.get(name);
        if (file == null) {
            file = extractToTmp(name, clazz);
            mExtracted.put(name, file);
        }
        return file;
    }

    public static File getResourceAsFile(String name) throws FileException {
        return getResourceAsFile(name, Class.class);
    }

    public static void load(String libPath) {
        if (mLoaded.contains(libPath)) {
            return;
        }
        try {
            File libFile = getResourceAsFile(libPath);
            System.load(libFile.getAbsolutePath());
        } catch (FileException ex) {
            throw new UnsatisfiedLinkError(ex.getMessage());
        }
    }

    public static File extractToTmp(String resourcePath) throws FileException {
        return extractToTmp(resourcePath, Class.class);
    }

    public static File extractToTmp(String resourcePath, Class clazz) throws FileException {
        return extractToTmp(resourcePath, "brut_util_Jar_", clazz);
    }

    public static File extractToTmp(String resourcePath, String tmpPrefix) throws FileException {
        return extractToTmp(resourcePath, tmpPrefix, Class.class);
    }

    public static File extractToTmp(String resourcePath, String tmpPrefix, Class clazz) throws FileException {
        try {
            InputStream in = clazz.getResourceAsStream(resourcePath);
            if (in == null) {
                throw new FileNotFoundException(resourcePath);
            }
            long suffix = ThreadLocalRandom.current().nextLong();
            File fileOut = File.createTempFile(tmpPrefix, (suffix == Long.MIN_VALUE ? 0L : Math.abs(suffix)) + ".tmp");
            fileOut.deleteOnExit();
            OutputStream out = new FileOutputStream(fileOut);
            in.transferTo(out);
            in.close();
            out.close();
            return fileOut;
        } catch (IOException ex) {
            throw new FileException("Could not extract resource: " + resourcePath, ex);
        }
    }
}
