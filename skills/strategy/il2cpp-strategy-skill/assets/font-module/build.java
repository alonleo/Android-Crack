package Translate;

import android.content.Context;
import android.util.Log;
import java.io.*;

public class build {
    private static Context appContext;
    private static String fontPath;
    private static String charsPath;
    private static String chineseChars;

    // 初始化并提取资源
    public static void init(Context context) {
        appContext = context;
        extractAssets();
        loadChineseChars();
    }

    // 提取资源文件到可访问目录
    private static void extractAssets() {
        String destDir = appContext.getExternalFilesDir(null).getAbsolutePath();
        
        // 提取字体文件
        fontPath = destDir + "/ALICE.ttf";
        copyAsset("Myfont/ALICE.ttf", fontPath);
        
        // 提取汉字文本
        charsPath = destDir + "/chinese_chars.txt";
        copyAsset("Myfont/text.txt", charsPath);
        
        Log.d("FontBuild", "Font path: " + fontPath);
        Log.d("FontBuild", "Chars path: " + charsPath);
    }

    // 复制 assets 文件到目标路径
    private static void copyAsset(String assetPath, String destPath) {
        try {
            InputStream is = appContext.getAssets().open(assetPath);
            FileOutputStream fos = new FileOutputStream(destPath);
            byte[] buffer = new byte[4096];
            int read;
            while ((read = is.read(buffer)) != -1) {
                fos.write(buffer, 0, read);
            }
            is.close();
            fos.close();
            Log.d("FontBuild", "Extracted: " + assetPath + " -> " + destPath);
        } catch (Exception e) {
            Log.e("FontBuild", "Failed to extract: " + assetPath, e);
        }
    }

    // 加载汉字文本内容
    private static void loadChineseChars() {
        try {
            BufferedReader reader = new BufferedReader(new FileReader(charsPath));
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line);
            }
            reader.close();
            chineseChars = sb.toString();
            Log.d("FontBuild", "Chinese chars loaded: " + chineseChars.length() + " characters");
        } catch (Exception e) {
            Log.e("FontBuild", "Failed to load chinese chars", e);
            chineseChars = "";
        }
    }

    // C++ 通过 JNI 调用获取路径
    public static String getFontPath() {
        return fontPath;
    }

    public static String getCharsPath() {
        return charsPath;
    }

    // 直接返回汉字字符串（避免 C++ 文件读取）
    public static String getChineseChars() {
        return chineseChars;
    }
}