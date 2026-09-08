package com.fakerandroid.decoder.util;

import com.android.dex.DexFormat;
import com.fakerandroid.decoder.exception.FileException;
import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.Closeable;
import java.io.File;
import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.nio.file.FileVisitOption;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.attribute.FileAttribute;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.Enumeration;
import java.util.List;
import java.util.Objects;
import java.util.jar.JarEntry;
import java.util.jar.JarOutputStream;
import java.util.logging.Logger;
import java.util.stream.Stream;
import java.util.zip.ZipEntry;
import java.util.zip.ZipFile;
import org.jetbrains.annotations.NotNull;
import org.jetbrains.annotations.Nullable;

/* JADX INFO: loaded from: FileUtils.class */
public class FileUtils {
    public static final int READ_BUFFER_SIZE = 8192;
    private static final int MAX_FILENAME_LENGTH = 128;
    public static final String JADX_TMP_INSTANCE_PREFIX = "jadx-instance-";
    public static final String JADX_TMP_PREFIX = "jadx-tmp-";
    private static final Logger LOG = Logger.getLogger(FileUtils.class.getName());
    private static final Object MKDIR_SYNC = new Object();
    private static final Path TEMP_ROOT_DIR = createTempRootDir();

    private FileUtils() {
    }

    public static void autoReplaceStr(File file, String oldstr, String newStr) throws IOException {
        if (oldstr == null || newStr == null) {
            return;
        }
        Long fileLength = Long.valueOf(file.length());
        byte[] fileContext = new byte[fileLength.intValue()];
        FileInputStream in = new FileInputStream(file);
        in.read(fileContext);
        String str = new String(fileContext, "utf-8");
        String str2 = str.replace(oldstr, newStr);
        PrintWriter out = new PrintWriter(file, "utf-8");
        out.write(str2);
        out.flush();
        out.close();
        in.close();
    }

    public static void addFileToJar(JarOutputStream jar, File source, String entryName) throws IOException {
        BufferedInputStream in = new BufferedInputStream(new FileInputStream(source));
        Throwable th = null;
        try {
            JarEntry entry = new JarEntry(entryName);
            entry.setTime(source.lastModified());
            jar.putNextEntry(entry);
            copyStream(in, jar);
            jar.closeEntry();
            if (in != null) {
                if (0 != 0) {
                    try {
                        in.close();
                        return;
                    } catch (Throwable th2) {
                        th.addSuppressed(th2);
                        return;
                    }
                }
                in.close();
            }
        } catch (Throwable th3) {
            if (in != null) {
                if (0 != 0) {
                    try {
                        in.close();
                    } catch (Throwable th4) {
                        th.addSuppressed(th4);
                    }
                } else {
                    in.close();
                }
            }
            throw th3;
        }
    }

    public static void makeDirsForFile(Path path) {
        if (path != null) {
            makeDirs(path.getParent().toFile());
        }
    }

    public static void makeDirsForFile(File file) {
        if (file != null) {
            makeDirs(file.getParentFile());
        }
    }

    public static void makeDirs(@Nullable File dir) {
        if (dir != null) {
            synchronized (MKDIR_SYNC) {
                if (!dir.mkdirs() && !dir.isDirectory()) {
                    throw new FileException("Can't create directory " + dir);
                }
            }
        }
    }

    public static void makeDirs(@Nullable Path dir) {
        if (dir != null) {
            makeDirs(dir.toFile());
        }
    }

    public static boolean deleteDir(File dir) {
        File[] content = dir.listFiles();
        if (content != null) {
            for (File file : content) {
                deleteDir(file);
            }
        }
        return dir.delete();
    }

    public static void deleteDir(Path dir) {
        try {
            Stream<Path> pathStream = Files.walk(dir, new FileVisitOption[0]);
            Throwable th = null;
            try {
                pathStream.sorted(Comparator.reverseOrder()).map((v0) -> {
                    return v0.toFile();
                }).forEach((v0) -> {
                    v0.delete();
                });
                if (pathStream != null) {
                    if (0 != 0) {
                        try {
                            pathStream.close();
                        } catch (Throwable th2) {
                            th.addSuppressed(th2);
                        }
                    } else {
                        pathStream.close();
                    }
                }
            } catch (Throwable th3) {
                if (pathStream != null) {
                    if (0 != 0) {
                        try {
                            pathStream.close();
                        } catch (Throwable th4) {
                            th.addSuppressed(th4);
                        }
                    } else {
                        pathStream.close();
                    }
                }
                throw th3;
            }
        } catch (Exception e) {
            throw new FileException("Failed to delete directory " + dir, e);
        }
    }

    private static Path createTempRootDir() {
        Path dir;
        try {
            String jadxTmpDir = System.getenv("JADX_TMP_DIR");
            if (jadxTmpDir != null) {
                dir = Files.createTempDirectory(Paths.get(jadxTmpDir, new String[0]), JADX_TMP_INSTANCE_PREFIX, new FileAttribute[0]);
            } else {
                dir = Files.createTempDirectory(JADX_TMP_INSTANCE_PREFIX, new FileAttribute[0]);
            }
            dir.toFile().deleteOnExit();
            return dir;
        } catch (Exception e) {
            throw new FileException("Failed to create temp root directory", e);
        }
    }

    public static void deleteTempRootDir() {
        deleteDir(TEMP_ROOT_DIR);
    }

    public static void clearTempRootDir() {
        deleteDir(TEMP_ROOT_DIR);
        makeDirs(TEMP_ROOT_DIR);
    }

    public static Path createTempDir(String prefix) {
        try {
            Path dir = Files.createTempDirectory(TEMP_ROOT_DIR, prefix, new FileAttribute[0]);
            dir.toFile().deleteOnExit();
            return dir;
        } catch (Exception e) {
            throw new FileException("Failed to create temp directory with suffix: " + prefix, e);
        }
    }

    public static Path createTempFile(String suffix) {
        try {
            Path path = Files.createTempFile(TEMP_ROOT_DIR, JADX_TMP_PREFIX, suffix, new FileAttribute[0]);
            path.toFile().deleteOnExit();
            return path;
        } catch (Exception e) {
            throw new FileException("Failed to create temp file with suffix: " + suffix, e);
        }
    }

    public static Path createTempFileNoDelete(String suffix) {
        try {
            return Files.createTempFile(TEMP_ROOT_DIR, JADX_TMP_PREFIX, suffix, new FileAttribute[0]);
        } catch (Exception e) {
            throw new FileException("Failed to create temp file with suffix: " + suffix, e);
        }
    }

    public static void copyStream(InputStream input, OutputStream output) throws IOException {
        byte[] buffer = new byte[8192];
        while (true) {
            int count = input.read(buffer);
            if (count != -1) {
                output.write(buffer, 0, count);
            } else {
                return;
            }
        }
    }

    public static byte[] streamToByteArray(InputStream input) throws IOException {
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        Throwable th = null;
        try {
            copyStream(input, out);
            byte[] byteArray = out.toByteArray();
            if (out != null) {
                if (0 != 0) {
                    try {
                        out.close();
                    } catch (Throwable th2) {
                        th.addSuppressed(th2);
                    }
                } else {
                    out.close();
                }
            }
            return byteArray;
        } catch (Throwable th3) {
            if (out != null) {
                if (0 != 0) {
                    try {
                        out.close();
                    } catch (Throwable th4) {
                        th.addSuppressed(th4);
                    }
                } else {
                    out.close();
                }
            }
            throw th3;
        }
    }

    public static void close(Closeable c) {
        if (c == null) {
            return;
        }
        try {
            c.close();
        } catch (IOException e) {
        }
    }

    @NotNull
    public static File prepareFile(File file) {
        File saveFile = cutFileName(file);
        makeDirsForFile(saveFile);
        return saveFile;
    }

    private static File cutFileName(File file) {
        String name;
        String name2 = file.getName();
        if (name2.length() <= 128) {
            return file;
        }
        int dotIndex = name2.indexOf(46);
        int cutAt = ((128 - name2.length()) + dotIndex) - 1;
        if (cutAt <= 0) {
            name = name2.substring(0, 127);
        } else {
            name = name2.substring(0, cutAt) + name2.substring(dotIndex);
        }
        return new File(file.getParentFile(), name);
    }

    private static String bytesToHex(byte[] bytes) {
        char[] hexArray = "0123456789abcdef".toCharArray();
        if (bytes == null || bytes.length <= 0) {
            return null;
        }
        char[] hexChars = new char[bytes.length * 2];
        for (int j = 0; j < bytes.length; j++) {
            int v = bytes[j] & 255;
            hexChars[j * 2] = hexArray[v >>> 4];
            hexChars[(j * 2) + 1] = hexArray[v & 15];
        }
        return new String(hexChars);
    }

    public static boolean isZipFile(File file) {
        try {
            InputStream is = new FileInputStream(file);
            Throwable th = null;
            try {
                byte[] headers = new byte[4];
                int read = is.read(headers, 0, 4);
                if (read == headers.length) {
                    String headerString = bytesToHex(headers);
                    if (Objects.equals(headerString, "504b0304")) {
                        if (is != null) {
                            if (0 != 0) {
                                try {
                                    is.close();
                                } catch (Throwable th2) {
                                    th.addSuppressed(th2);
                                }
                            } else {
                                is.close();
                            }
                        }
                        return true;
                    }
                    return false;
                }
                if (is != null) {
                    if (0 != 0) {
                        try {
                            is.close();
                        } catch (Throwable th3) {
                            th.addSuppressed(th3);
                        }
                    } else {
                        is.close();
                    }
                }
                return false;
            } catch (Throwable th4) {
                if (is != null) {
                    if (0 != 0) {
                        try {
                            is.close();
                        } catch (Throwable th5) {
                            th.addSuppressed(th5);
                        }
                    } else {
                        is.close();
                    }
                }
                throw th4;
            }
        } catch (Exception e) {
            return false;
        }
    }

    private static List<String> getZipFileList(File file) {
        List<String> filesList = new ArrayList<>();
        try {
            ZipFile zipFile = new ZipFile(file);
            Throwable th = null;
            try {
                try {
                    Enumeration<? extends ZipEntry> entries = zipFile.entries();
                    while (entries.hasMoreElements()) {
                        ZipEntry entry = entries.nextElement();
                        filesList.add(entry.getName());
                    }
                    if (zipFile != null) {
                        if (0 != 0) {
                            try {
                                zipFile.close();
                            } catch (Throwable th2) {
                                th.addSuppressed(th2);
                            }
                        } else {
                            zipFile.close();
                        }
                    }
                    return filesList;
                } catch (Throwable th3) {
                    th = th3;
                    throw th3;
                }
            } catch (Throwable th4) {
                if (zipFile != null) {
                    if (th != null) {
                        try {
                            zipFile.close();
                        } catch (Throwable th5) {
                            th.addSuppressed(th5);
                        }
                    } else {
                        zipFile.close();
                    }
                }
                throw th4;
            }
        } catch (Exception e) {
            LOG.warning(String.format("Error read zip file '{%s}' e:%s", file.getAbsolutePath(), e));
        }
        return filesList;
    }

    public static boolean isApkFile(File file) {
        if (!isZipFile(file)) {
            return false;
        }
        List<String> filesList = getZipFileList(file);
        return filesList.contains("AndroidManifest.xml") && filesList.contains(DexFormat.DEX_IN_JAR_NAME);
    }

    public static boolean isZipDexFile(File file) {
        if (!isZipFile(file) || !isZipFileCanBeOpen(file)) {
            return false;
        }
        List<String> filesList = getZipFileList(file);
        return filesList.contains(DexFormat.DEX_IN_JAR_NAME);
    }

    private static boolean isZipFileCanBeOpen(File file) {
        try {
            ZipFile zipFile = new ZipFile(file);
            Throwable th = null;
            try {
                boolean zHasMoreElements = zipFile.entries().hasMoreElements();
                if (zipFile != null) {
                    if (0 != 0) {
                        try {
                            zipFile.close();
                        } catch (Throwable th2) {
                            th.addSuppressed(th2);
                        }
                    } else {
                        zipFile.close();
                    }
                }
                return zHasMoreElements;
            } catch (Throwable th3) {
                if (zipFile != null) {
                    if (0 != 0) {
                        try {
                            zipFile.close();
                        } catch (Throwable th4) {
                            th.addSuppressed(th4);
                        }
                    } else {
                        zipFile.close();
                    }
                }
                throw th3;
            }
        } catch (Exception e) {
            return false;
        }
    }

    public static String getPathBaseName(Path file) {
        String fileName = file.getFileName().toString();
        int extEndIndex = fileName.lastIndexOf(46);
        if (extEndIndex == -1) {
            return fileName;
        }
        return fileName.substring(0, extEndIndex);
    }

    public static File toFile(String path) {
        if (path == null) {
            return null;
        }
        return new File(path);
    }
}
