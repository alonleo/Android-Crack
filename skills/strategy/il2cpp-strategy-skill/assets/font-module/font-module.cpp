/**
 * Font Module - 中文字体支持模块实现
 * 方案2：使用 FontEngine_LoadFontFace + Font 创建 + TMP_FontAsset_CreateFontAsset_4
 */
#include "font-module.h"
#include "Il2cpp-arm64/il2cpp-appdata.h"  // 必须先包含（定义 DO_APP_FUNC 宏）
#include "include/faker.h"  // 包含 baseImageAddr
#include <jni.h>
#include <string>
#include <android/log.h>

using namespace app;  // 使用 app 命名空间

#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "FontModule", __VA_ARGS__)
#define LOGD(...) __android_log_print(ANDROID_LOG_DEBUG, "FontModule", __VA_ARGS__)

// 手动定义 il2cpp_object_new 函数指针（避免名称冲突）
typedef Il2CppObject* (*il2cpp_object_new_func_t)(const Il2CppClass* klass);
static il2cpp_object_new_func_t g_il2cpp_object_new = nullptr;

namespace FontModule {
    
    // 全局字体资产（TMP_Text 使用）
    static app::TMP_FontAsset* g_chineseFontAsset = nullptr;
    static bool g_fontInitialized = false;
    
    // 全局普通 Font（普通 Text 使用）
    static app::Font* g_chineseFont = nullptr;
    static bool g_fontObjInitialized = false;
    
    // 保存的路径和字符（用于延迟创建）
    static char g_savedTtfPath[512] = {};
    static std::string g_savedChineseChars;
    static bool g_dataSaved = false;
    
    // 辅助函数：C 字符串转 IL2CPP String
    app::String* cStringToIl2cpp(const char* str) {
        if (str == nullptr) return nullptr;
        return reinterpret_cast<app::String*>(il2cpp_string_new(str));
    }
    
    // 初始化 il2cpp_object_new 函数指针
    static void initIl2cppObjectNew() {
        if (g_il2cpp_object_new == nullptr) {
            long base = baseImageAddr("libil2cpp.so") + 0x00004000;
            // 地址 0x03582D54 对应 il2cpp_object_new
            g_il2cpp_object_new = reinterpret_cast<il2cpp_object_new_func_t>(base + (0x03582D54 - 0x00004000));
            LOGE("g_il2cpp_object_new initialized: %p", (void*)g_il2cpp_object_new);
        }
    }
    
    // 初始化中文字体（新方案：创建空 TMP_FontAsset + 设置路径 + LoadFontFace）
    void initChineseFont(const char* ttfPath, const char* chineseChars) {
        LOGE("=== initChineseFont START (新方案：m_SourceFontFilePath) ===");
        LOGE("ttfPath: %s", ttfPath);
        LOGE("chineseChars length: %zu", strlen(chineseChars));
        
        if (g_fontInitialized) {
            LOGD("Font already initialized");
            return;
        }
        
        try {
            initIl2cppObjectNew();
            
            // 打印函数指针地址
            LOGE("=== Function Pointer Addresses ===");
            LOGE("TMP_FontAsset_LoadFontFace: %p", (void*)TMP_FontAsset_LoadFontFace);
            LOGE("TMP_FontAsset_set_atlasPopulationMode: %p", (void*)TMP_FontAsset_set_atlasPopulationMode);
            LOGE("TMP_FontAsset_TryAddCharacters_2: %p", (void*)TMP_FontAsset_TryAddCharacters_2);
            LOGE("TMP_FontAsset_TryAddGlyphsToAtlasTextures: %p", (void*)TMP_FontAsset_TryAddGlyphsToAtlasTextures);
            LOGE("g_il2cpp_object_new: %p", (void*)g_il2cpp_object_new);
            LOGE("il2cpp_string_new: %p", (void*)il2cpp_string_new);
            LOGE("==================================");
            
            // 步骤 1：延迟字体创建
            // TMP_Settings 可能还没有初始化，不能在这里调用 TMP_Settings_get_defaultFontAsset
            // 改为在 Hook_TMP_Text_set_text 第一次触发时再创建字体
            
            LOGE("Step 1: Deferring font creation to first text hook...");
            LOGE("Font creation will be done in Hook_TMP_Text_set_text when first text is captured");
            
            g_fontInitialized = false;  // 标记为未初始化，等待后续创建
            g_chineseFontAsset = nullptr;
            
            // 保存路径信息供后续使用
            strncpy(g_savedTtfPath, ttfPath, sizeof(g_savedTtfPath) - 1);
            g_savedTtfPath[sizeof(g_savedTtfPath) - 1] = '\0';
            g_savedChineseChars = chineseChars;
            g_dataSaved = true;
            
            LOGE("Font path saved: %s", g_savedTtfPath);
            LOGE("Chinese chars saved: %zu bytes", g_savedChineseChars.length());
            
            LOGE("=== initChineseFont deferred (will create on first hook) ===");
            return;
            
        } catch (const std::exception& e) {
            LOGE("initChineseFont exception: %s", e.what());
        } catch (...) {
            LOGE("initChineseFont unknown exception");
        }
    }
    
    // 获取全局中文字体资产
    app::TMP_FontAsset* getChineseFontAsset() {
        return g_chineseFontAsset;
    }
    
    // 检查字体是否已初始化
    bool isFontInitialized() {
        return g_fontInitialized;
    }
    
    // 获取保存的数据状态
    bool hasSavedData() {
        return g_dataSaved;
    }
    
    // 按需创建字体（在第一次 Hook 触发时调用）
    // 使用 TMP_FontAsset_CreateFontAsset_2 直接从 TTF 文件路径创建（memory 中建议的首选方法）
    app::TMP_FontAsset* createFontOnDemand(app::TMP_FontAsset* existingFontAsset) {
        if (!g_dataSaved) {
            LOGE("ERROR: No saved font data, cannot create on demand");
            return nullptr;
        }
        
        if (g_fontInitialized && g_chineseFontAsset != nullptr) {
            return g_chineseFontAsset;
        }
        
        LOGE("=== createFontOnDemand START ===");
        LOGE("ttfPath: %s", g_savedTtfPath);
        LOGE("chineseChars length: %zu", g_savedChineseChars.length());
        LOGE("existingFontAsset: %p", (void*)existingFontAsset);
        
        try {
            initIl2cppObjectNew();
            
            // 步骤 1：使用 FontEngine_LoadFontFace_1 加载字体数据到引擎
            LOGE("Step 1: Loading font face with FontEngine_LoadFontFace_1...");
            String* ttfPathStr = cStringToIl2cpp(g_savedTtfPath);
            if (ttfPathStr == nullptr) {
                LOGE("ERROR: Failed to create ttfPathStr");
                return nullptr;
            }
            
            FontEngineError__Enum loadResult = FontEngine_LoadFontFace_1(ttfPathStr, 90.0f, 0, nullptr);
            LOGE("FontEngine_LoadFontFace_1 result: %d", (int)loadResult);
            if ((int)loadResult != 0) {
                LOGE("WARNING: FontEngine_LoadFontFace_1 returned error %d", (int)loadResult);
            }
            
            // 步骤 2：使用 TMP_FontAsset_CreateFontAsset_2 从 TTF 文件路径创建字体资产
            // 参数: (fontFilePath, faceIndex, samplingPointSize, atlasPadding, renderMode, atlasWidth, atlasHeight, atlasPopulationMode, enableMultiAtlasSupport, method)
            LOGE("Step 2: Creating TMP_FontAsset with CreateFontAsset_2...");
            TMP_FontAsset* fontAsset = TMP_FontAsset_CreateFontAsset_2(
                ttfPathStr,
                0,      // faceIndex
                90,     // samplingPointSize
                5,      // atlasPadding
                (GlyphRenderMode__Enum)0x00004026,  // SDF16
                2048,   // atlasWidth
                2048,   // atlasHeight
                (AtlasPopulationMode__Enum_1)1,     // Dynamic
                true,   // enableMultiAtlasSupport
                nullptr // method
            );
            LOGE("TMP_FontAsset_CreateFontAsset_2 result: %p", (void*)fontAsset);
            if (fontAsset == nullptr) {
                LOGE("ERROR: TMP_FontAsset_CreateFontAsset_2 returned null");
                return nullptr;
            }
            
            // 步骤 3：添加汉字字符
            LOGE("Step 3: Adding Chinese characters...");
            String* charsString = cStringToIl2cpp(g_savedChineseChars.c_str());
            if (charsString == nullptr) {
                LOGE("ERROR: Failed to create charsString");
                return nullptr;
            }
            
            bool addResult = TMP_FontAsset_TryAddCharacters_2(
                fontAsset,
                charsString,
                true,       // includeFontFeatures
                nullptr     // MethodInfo
            );
            LOGE("TryAddCharacters_2 result: %d", addResult);
            
            // 步骤 4：渲染字形到 Atlas
            LOGE("Step 4: Rendering glyphs to atlas...");
            TMP_FontAsset_TryAddGlyphsToAtlasTextures(fontAsset, nullptr);
            LOGE("Step 4 DONE");
            
            // 步骤 5：保存全局字体资产
            g_chineseFontAsset = fontAsset;
            g_fontInitialized = true;
            
            LOGE("=== createFontOnDemand SUCCESS ===");
            LOGE("Chinese font created, g_chineseFontAsset: %p", (void*)g_chineseFontAsset);
            
            return g_chineseFontAsset;
            
        } catch (const std::exception& e) {
            LOGE("createFontOnDemand exception: %s", e.what());
        } catch (...) {
            LOGE("createFontOnDemand unknown exception");
        }
        
        return nullptr;
    }
    
    // 获取普通 Font 对象（从 TMP_FontAsset 的 m_SourceFontFile 获取）
    // 用于普通 Unity Text 组件
    app::Font* getChineseFont() {
        // 如果已经有缓存的 Font，直接返回
        if (g_fontObjInitialized && g_chineseFont != nullptr) {
            return g_chineseFont;
        }
        
        // 从 TMP_FontAsset 获取 Font 对象
        if (g_fontInitialized && g_chineseFontAsset != nullptr) {
            g_chineseFont = g_chineseFontAsset->m_SourceFontFile;
            if (g_chineseFont != nullptr) {
                g_fontObjInitialized = true;
                LOGE("Got Font from TMP_FontAsset.m_SourceFontFile: %p", (void*)g_chineseFont);
                return g_chineseFont;
            } else {
                LOGE("WARNING: TMP_FontAsset.m_SourceFontFile is null");
            }
        }
        
        LOGE("Font not available yet, TMP_FontAsset not initialized");
        return nullptr;
    }
    
    // 检查普通 Font 是否可用
    bool isFontObjAvailable() {
        return g_fontObjInitialized && g_chineseFont != nullptr;
    }
    
}