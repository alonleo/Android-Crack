/**
 * Font Module - 中文字体支持模块
 * 从 TTF 文件创建 TMP_FontAsset 并添加汉字支持
 */
#pragma once

#include "Il2cpp-arm64/il2cpp-appdata.h"

namespace FontModule {
    
    // 初始化中文字体（从 TTF 创建 TMP_FontAsset 并添加汉字）
    // 注意：此函数会延迟创建，仅保存路径数据
    void initChineseFont(const char* ttfPath, const char* chineseChars);
    
    // 获取全局 TMP_FontAsset（用于 TMP_Text 组件）
    app::TMP_FontAsset* getChineseFontAsset();
    
    // 检查 TMP_FontAsset 是否已初始化
    bool isFontInitialized();
    
    // 检查是否有保存的数据（用于延迟创建）
    bool hasSavedData();
    
    // 按需创建字体（在第一次 Hook 触发时调用）
    // existingFontAsset: 当前 TMP_Text 使用的字体资产，用于获取 Class
    app::TMP_FontAsset* createFontOnDemand(app::TMP_FontAsset* existingFontAsset);
    
    // 获取普通 Font 对象（从 TMP_FontAsset.m_SourceFontFile 获取）
    // 用于普通 Unity Text 组件
    app::Font* getChineseFont();
    
    // 检查普通 Font 是否可用
    bool isFontObjAvailable();
    
}