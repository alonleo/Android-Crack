package com.fakerandroid.decoder.util;

import com.fakerandroid.decoder.exception.FakerAndroidException;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.util.Arrays;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.logging.Logger;
import org.apache.commons.io.IOUtils;

/* JADX INFO: loaded from: OS.class */
public class OS {
    private static final Logger LOGGER = Logger.getLogger("");

    public static void rmdir(File dir) throws FakerAndroidException {
        if (!dir.exists()) {
            return;
        }
        File[] files = dir.listFiles();
        for (File file : files) {
            if (file.isDirectory()) {
                rmdir(file);
            } else {
                file.delete();
            }
        }
        dir.delete();
    }

    public static void rmfile(String file) throws FakerAndroidException {
        File del = new File(file);
        del.delete();
    }

    public static void rmdir(String dir) throws FakerAndroidException {
        rmdir(new File(dir));
    }

    public static void cpdir(File src, File dest) throws FakerAndroidException {
        dest.mkdirs();
        File[] files = src.listFiles();
        for (File file : files) {
            File destFile = new File(dest.getPath() + File.separatorChar + file.getName());
            if (file.isDirectory()) {
                cpdir(file, destFile);
            } else {
                try {
                    InputStream in = new FileInputStream(file);
                    OutputStream out = new FileOutputStream(destFile);
                    in.transferTo(out);
                    in.close();
                    out.close();
                } catch (IOException ex) {
                    throw new FakerAndroidException("Could not copy file: " + file, ex);
                }
            }
        }
    }

    public static void cpdir(String src, String dest) throws FakerAndroidException {
        cpdir(new File(src), new File(dest));
    }

    public static void exec(String[] cmd) throws Exception {
        try {
            ProcessBuilder builder = new ProcessBuilder(cmd);
            Process ps = builder.start();
            new StreamForwarder(ps.getErrorStream(), "ERROR").start();
            new StreamForwarder(ps.getInputStream(), "OUTPUT").start();
            int exitValue = ps.waitFor();
            if (exitValue != 0) {
                throw new FakerAndroidException("could not exec (exit code = " + exitValue + "): " + Arrays.toString(cmd));
            }
        } catch (IOException ex) {
            throw new FakerAndroidException("could not exec: " + Arrays.toString(cmd), ex);
        } catch (InterruptedException ex2) {
            throw new FakerAndroidException("could not exec : " + Arrays.toString(cmd), ex2);
        }
    }

    public static String execAndReturn(String[] cmd) {
        ExecutorService executor = Executors.newCachedThreadPool();
        try {
            ProcessBuilder builder = new ProcessBuilder(cmd);
            builder.redirectErrorStream(true);
            Process process = builder.start();
            StreamCollector collector = new StreamCollector(process.getInputStream());
            executor.execute(collector);
            process.waitFor();
            if (!executor.awaitTermination(15L, TimeUnit.SECONDS)) {
                executor.shutdownNow();
                if (!executor.awaitTermination(5L, TimeUnit.SECONDS)) {
                    System.err.println("Stream collector did not terminate.");
                }
            }
            return collector.get();
        } catch (IOException | InterruptedException e) {
            return null;
        }
    }

    public static File createTempDirectory() throws FakerAndroidException {
        try {
            File tmp = File.createTempFile("BRUT", null);
            tmp.deleteOnExit();
            if (!tmp.delete()) {
                throw new FakerAndroidException("Could not delete tmp file: " + tmp.getAbsolutePath());
            }
            if (!tmp.mkdir()) {
                throw new FakerAndroidException("Could not create tmp dir: " + tmp.getAbsolutePath());
            }
            return tmp;
        } catch (IOException ex) {
            throw new FakerAndroidException("Could not create tmp dir", ex);
        }
    }

    /* JADX INFO: loaded from: OS$StreamForwarder.class */
    static class StreamForwarder extends Thread {
        private final InputStream mIn;
        private final String mType;

        StreamForwarder(InputStream is, String type) {
            this.mIn = is;
            this.mType = type;
        }

        @Override // java.lang.Thread, java.lang.Runnable
        public void run() {
            try {
                BufferedReader br = new BufferedReader(new InputStreamReader(this.mIn));
                while (true) {
                    String line = br.readLine();
                    if (line != null) {
                        if (this.mType.equals("OUTPUT")) {
                            OS.LOGGER.info(line);
                        } else {
                            OS.LOGGER.warning(line);
                        }
                    } else {
                        return;
                    }
                }
            } catch (IOException ex) {
                ex.printStackTrace();
            }
        }
    }

    /* JADX INFO: loaded from: OS$StreamCollector.class */
    static class StreamCollector implements Runnable {
        private final StringBuffer buffer = new StringBuffer();
        private final InputStream inputStream;

        public StreamCollector(InputStream inputStream) {
            this.inputStream = inputStream;
        }

        /* JADX WARN: Code duplicated, block: B:20:0x005e  */
        /* JADX WARN: Code duplicated, block: B:25:0x0074 A[Catch: IOException -> 0x007e, TryCatch #3 {IOException -> 0x007e, blocks: (B:2:0x0000, B:3:0x0015, B:5:0x001e, B:10:0x0037, B:13:0x0049, B:12:0x0040, B:16:0x0057, B:22:0x0062, B:25:0x0074, B:24:0x006b, B:27:0x007a), top: B:36:0x0000, inners: #0, #2, #4 }] */
        /* JADX WARN: Code duplicated, block: B:37:0x0062 A[EXC_TOP_SPLITTER, SYNTHETIC] */
        @Override // java.lang.Runnable
        public void run() {
            try {
                BufferedReader reader = new BufferedReader(new InputStreamReader(this.inputStream));
                Throwable th = null;
                while (true) {
                    try {
                        try {
                            String line = reader.readLine();
                            if (line == null) {
                                break;
                            } else {
                                this.buffer.append(line).append('\n');
                            }
                        } catch (Throwable th2) {
                            th = th2;
                            throw th2;
                        }
                    } catch (Throwable th3) {
                        if (reader != null) {
                            if (th != null) {
                                try {
                                    reader.close();
                                } catch (Throwable th4) {
                                    th.addSuppressed(th4);
                                }
                            } else {
                                reader.close();
                            }
                        }
                        throw th3;
                    }
                    if (reader != null) {
                        if (th != null) {
                            reader.close();
                        } else {
                            reader.close();
                        }
                    }
                }
                if (reader != null) {
                    if (0 != 0) {
                        try {
                            reader.close();
                        } catch (Throwable th5) {
                            th.addSuppressed(th5);
                        }
                    } else {
                        reader.close();
                    }
                }
            } catch (IOException e) {
            }
        }

        public String get() {
            return this.buffer.toString();
        }
    }
}
