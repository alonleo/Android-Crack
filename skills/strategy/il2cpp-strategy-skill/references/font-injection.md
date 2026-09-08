# Unity 中文字体注入方案（font-module，运行时动态创建）

> 来源: 模板项目 tape-thrower | 参考: FlyingGorillaEndlessRunner 汉化调查
> 相比静态替换（崩溃）与依赖系统 fallback（不可控），本方案**运行时用 il2cpp API 动态创建中文字体**并注入 UI 文本，跨设备一致。

## 方案总览

```
assets/Myfont/ALICE.ttf + text.txt（中文字符集）
    │ Java: Translate/build.java 复制到 externalFilesDir
    ▼
JNI nativeInitFont(fontPath, charsPath)  →  FontModule::initChineseFont（保存路径，延迟）
    ▼
Hook_TMP_Text_set_text / Hook_Text_set_text（首次触发）
    ├─ FontModule::createFontOnDemand()
    │    ├─ FontEngine_LoadFontFace(ttf, 90, 0)         # 加载字体数据
    │    ├─ TMP_FontAsset_CreateFontAsset_2(ttf, 0, 90, 5, SDF16, 2048, 2048, Dynamic, true)
    │    ├─ TMP_FontAsset_TryAddCharacters_2(asset, chars, true)   # 添加中文字符
    │    └─ TMP_FontAsset_TryAddGlyphsToAtlasTextures()            # 渲染字形 Atlas
    └─ TMP_Text_set_font(__this, chineseFontAsset)   # 强制用中文字体（TMP）
    └─ Text_set_font(__this, getChineseFont())       # 普通 UI.Text（从 m_SourceFontFile 取 Font）
```

## 关键要点

### 1. 字体与字符集
- `assets/Myfont/ALICE.ttf`：中文字体（任何含 CJK 的 TTF/OTF）
- `assets/Myfont/text.txt`：所需中文字符集（覆盖汉化文本用字）
- Java 复制到 `getExternalFilesDir`（绝对路径，Unity 可读）

### 2. JNI 桥
```java
// FakerApp.java
public static native void nativeInitFont(String fontPath, String charsPath);
```
```cpp
// native-lib.cpp
JNIEXPORT void Java_..._nativeInitFont(JNIEnv* env, jobject, jstring font, jstring chars) {
    FontModule::initChineseFont(fontPath, charsStr);
}
```

### 3. 运行时创建（font-module.cpp）
依赖 `Il2cpp-arm64/il2cpp-appdata.h` 的 `DO_APP_FUNC` 宏定义：
- `FontEngine_LoadFontFace_1`
- `TMP_FontAsset_CreateFontAsset_2`
- `TMP_FontAsset_TryAddCharacters_2`
- `TMP_FontAsset_TryAddGlyphsToAtlasTextures`
- `TMP_Text_set_font` / `Text_set_font`

关键：**延迟到第一次 Hook 触发时创建**（此时 TMP_Settings 已初始化，不能过早创建）。

### 4. Hook 注入
```cpp
// TMP 文本（TextMeshPro / UI Toolkit 底层）
void Hook_TMP_Text_set_text(TMP_Text* __this, String* value, MethodInfo* m) {
    if (!FontModule::isFontInitialized() && FontModule::hasSavedData())
        FontModule::createFontOnDemand(TMP_Text_get_font(__this, nullptr));
    app::TMP_FontAsset* zh = FontModule::getChineseFontAsset();
    if (zh) TMP_Text_set_font(__this, zh, nullptr);
    // ... 汉化替换文本逻辑
}
// 普通 UI.Text
void Hook_Text_set_text(Text* __this, String* value, MethodInfo* m) {
    app::Font* zh = FontModule::getChineseFont();
    if (zh) Text_set_font(__this, zh, nullptr);
    // ... 汉化替换文本逻辑
}
```

### 5. A64HookFunction 注册
```cpp
A64HookFunction((void*)(base + TMP_Text_set_text_rva), (void*)Hook_TMP_Text_set_text, (void**)&orig);
A64HookFunction((void*)(base + Text_set_text_rva), (void*)Hook_Text_set_text, (void**)&orig);
```

## 模板文件（本 skill assets/font-module/）
- `font-module.h` / `font-module.cpp`：完整字体模块（可直接引入）
- `build.java`：Java 侧 assets 复制 + 字符集加载

## 与本项目 FlyingGorilla 的关系
- FlyingGorilla 实测 **Unity 6 TextCore 自动 fallback 系统 CJK，中文已正常显示**（OCR 确认"飞行距离 : 170m"）
- 若目标设备无系统 CJK 或需跨设备一致 → 用本方案（font-module）主动注入
- 模板字体（Alibaba.ttf / LXGWWenKai）可作 `Myfont/` 的字体源（需生成 text.txt 字符集）
