package com.fakerandroid.decoder.dex2jar;

import com.googlecode.d2j.reader.DexFileReader;
import com.googlecode.d2j.util.zip.AccessBufByteArrayOutputStream;
import com.googlecode.d2j.util.zip.ZipEntry;
import com.googlecode.d2j.util.zip.ZipFile;
import java.io.IOException;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.util.TreeMap;

/* JADX INFO: loaded from: PatchMultiDexFileReader.class */
public class PatchMultiDexFileReader {
    public static TreeMap<String, DexFileReader> open(byte[] data) throws IOException {
        TreeMap<String, DexFileReader> dexFileReaders = new TreeMap<>();
        if (data.length < 3) {
            throw new IOException("File too small to be a dex/zip");
        }
        if (!"PK".equals(new String(data, 0, 2, StandardCharsets.ISO_8859_1))) {
            throw new IOException("the src file not a .dex or zip file");
        }
        ZipFile zipFile = new ZipFile(data);
        Throwable var3 = null;
        try {
            for (ZipEntry e : zipFile.entries()) {
                String entryName = e.getName();
                if (entryName.startsWith("classes") && entryName.endsWith(".dex") && !dexFileReaders.containsKey(entryName)) {
                    dexFileReaders.put(entryName, new DexFileReader(toByteArray(zipFile.getInputStream(e))));
                }
            }
            if (zipFile != null) {
                if (0 != 0) {
                    try {
                        zipFile.close();
                    } catch (Throwable var13) {
                        var3.addSuppressed(var13);
                    }
                } else {
                    zipFile.close();
                }
            }
            if (dexFileReaders.size() == 0) {
                throw new IOException("Can not find classes.dex in zip file");
            }
            return dexFileReaders;
        } catch (Throwable th) {
            if (zipFile != null) {
                if (0 != 0) {
                    try {
                        zipFile.close();
                    } catch (Throwable var14) {
                        var3.addSuppressed(var14);
                    }
                } else {
                    zipFile.close();
                }
            }
            throw th;
        }
    }

    private static byte[] toByteArray(InputStream is) throws IOException {
        AccessBufByteArrayOutputStream out = new AccessBufByteArrayOutputStream();
        byte[] buff = new byte[1024];
        int i = is.read(buff);
        while (true) {
            int c = i;
            if (c > 0) {
                out.write(buff, 0, c);
                i = is.read(buff);
            } else {
                return out.getBuf();
            }
        }
    }
}
