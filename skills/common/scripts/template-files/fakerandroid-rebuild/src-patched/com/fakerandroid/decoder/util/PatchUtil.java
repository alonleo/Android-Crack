package com.fakerandroid.decoder.util;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.JarURLConnection;
import java.net.URL;
import java.net.URLConnection;
import java.util.Enumeration;
import java.util.jar.JarEntry;
import java.util.jar.JarFile;
import javax.xml.XMLConstants;

/* JADX INFO: loaded from: PatchUtil.class */
public class PatchUtil {
    public static void copyDirFromJar(String folderPath, String toFolderPath) throws IOException {
        loadRecourseFromJarByFolder(folderPath, toFolderPath, PatchUtil.class, null);
    }

    public static void loadRecourseFromJarByFolder(String folderPath, String targetFolderPath, Class clazz, String basePath) throws IOException {
        URL url = clazz.getResource(folderPath);
        if (basePath == null) {
            basePath = url.getPath();
        }
        URLConnection urlConnection = url.openConnection();
        if (urlConnection instanceof JarURLConnection) {
            copyJarResources((JarURLConnection) urlConnection, folderPath, targetFolderPath, clazz, basePath);
        } else {
            copyFileResources(url, folderPath, targetFolderPath, clazz, basePath);
        }
    }

    private static void copyFileResources(URL url, String folderPath, String targetFolderPath, Class clazz, String basePath) throws IOException {
        File root = new File(url.getPath());
        System.out.println("basePath" + basePath);
        if (root.isDirectory()) {
            File[] files = root.listFiles();
            for (File file : files) {
                if (file.isDirectory()) {
                    loadRecourseFromJarByFolder(folderPath + XMLConstants.XPATH_SEPARATOR + file.getName(), targetFolderPath, clazz, basePath);
                } else {
                    String toPath = file.getPath().replace(new File(basePath).getAbsolutePath(), targetFolderPath);
                    loadRecourseFromJar(folderPath + XMLConstants.XPATH_SEPARATOR + file.getName(), toPath, clazz);
                }
            }
        }
    }

    private static void copyJarResources(JarURLConnection jarURLConnection, String folderPath, String targetFolderPath, Class clazz, String basePath) throws IOException {
        JarFile jarFile = jarURLConnection.getJarFile();
        Enumeration<JarEntry> entrys = jarFile.entries();
        while (entrys.hasMoreElements()) {
            JarEntry entry = entrys.nextElement();
            if (entry.getName().startsWith(jarURLConnection.getEntryName()) && !entry.getName().endsWith(XMLConstants.XPATH_SEPARATOR)) {
                String target = (XMLConstants.XPATH_SEPARATOR + entry.getName()).replace(folderPath, "");
                File file = new File(targetFolderPath, target);
                String toPath = file.getAbsolutePath();
                loadRecourseFromJar(XMLConstants.XPATH_SEPARATOR + entry.getName(), toPath, clazz);
            }
        }
        jarFile.close();
    }

    public static void loadRecourseFromJar(String path, String toPath, Class clazz) throws IOException {
        if (!path.startsWith(XMLConstants.XPATH_SEPARATOR)) {
            throw new IllegalArgumentException("The path has to be absolute (start with '/').");
        }
        if (path.endsWith(XMLConstants.XPATH_SEPARATOR)) {
            throw new IllegalArgumentException("The path has to be absolute (cat not end with '/').");
        }
        String folderPath = new File(toPath).getParent();
        File dir = new File(folderPath);
        if (!dir.exists()) {
            dir.mkdirs();
        }
        if (toPath.endsWith(".tmpl")) {
            toPath = getFileNameNoEx(toPath);
        }
        File file = new File(toPath);
        if (!file.exists() && !file.createNewFile()) {
            return;
        }
        byte[] buffer = new byte[1024];
        URL url = clazz.getResource(path);
        URLConnection urlConnection = url.openConnection();
        InputStream is = urlConnection.getInputStream();
        if (is == null) {
            throw new FileNotFoundException("File " + path + " was not found inside JAR.");
        }
        OutputStream os = new FileOutputStream(file);
        while (true) {
            try {
                int readBytes = is.read(buffer);
                if (readBytes != -1) {
                    os.write(buffer, 0, readBytes);
                } else {
                    os.close();
                    is.close();
                    return;
                }
            } catch (Throwable th) {
                os.close();
                is.close();
                throw th;
            }
        }
    }

    public static String getExtensionName(String filename) {
        int dot;
        if (filename != null && filename.length() > 0 && (dot = filename.lastIndexOf(46)) > -1 && dot < filename.length() - 1) {
            return filename.substring(dot + 1);
        }
        return filename;
    }

    public static String getFileNameNoEx(String filename) {
        int dot;
        if (filename != null && filename.length() > 0 && (dot = filename.lastIndexOf(46)) > -1 && dot < filename.length()) {
            return filename.substring(0, dot);
        }
        return filename;
    }
}
