/**
 * frida-collect-text.js — Frida agent: 动态收集 Unity il2cpp 文本
 *
 * 用法:
 *   frida -U -l frida-collect-text.js -f <package.name> --no-pause
 *   frida-gadget -l frida-collect-text.js
 *
 * 功能:
 *   1. Hook UnityEngine.UI.Text.set_text / TMPro.TMP_Text.set_text
 *   2. Hook 自定义 set_text 方法（从 dump.cs 获取 RVA）
 *   3. 拦截并发送所有非中文文本到 Python 端
 *   4. 去重显示（仅新字符串发送一次）
 */

'use strict';

// ── 配置 ──────────────────────────────────────────────────────
// 从 dump.cs 获取的 set_text RVAs（Unity 代码段）
const HOOK_RVAS = [
    // UnityEngine.UI.Text.set_text (基础 UI 文本)
    { rva: 0x1F88A64, name: "UI.Text.set_text" },
    // 自定义/overrides
    { rva: 0x2070370, name: "Text.set_text_2" },
    { rva: 0x20750D8, name: "Text.set_text_3" },
    { rva: 0x2076210, name: "Text.set_text_4" },
    { rva: 0x1FDAF88, name: "Text.set_text_5" },
    { rva: 0x1E96D0C, name: "Text.set_text_6" },
    { rva: 0x1F37C4C, name: "Text.set_text_7" },
    { rva: 0x1F52E00, name: "Text.set_text_8" },
];

// 已发送的字符串（去重）
const sentStrings = new Set();

// ── 辅助: Il2CppString → UTF-8 ────────────────────────────────
// Il2CppString 结构: { klass(8), monitor(8), length(4), chars[] }
function il2cppStringToUtf8(addr) {
    if (!addr || addr.isNull()) return null;
    try {
        const len = addr.add(16).readS32(); // offset 16 = length
        if (len <= 0 || len > 2048) return null;
        
        const chars = addr.add(20); // offset 20 = chars (UTF-16)
        let result = '';
        for (let i = 0; i < len; i++) {
            const code = chars.add(i * 2).readU16();
            if (code < 0x80) {
                result += String.fromCharCode(code);
            } else if (code < 0x800) {
                result += String.fromCharCode(0xC0 | (code >> 6));
                result += String.fromCharCode(0x80 | (code & 0x3F));
            } else {
                result += String.fromCharCode(0xE0 | (code >> 12));
                result += String.fromCharCode(0x80 | ((code >> 6) & 0x3F));
                result += String.fromCharCode(0x80 | (code & 0x3F));
            }
        }
        return result;
    } catch (e) {
        return null;
    }
}

// ── 检测是否为中文文本 ──
function hasChinese(text) {
    return /[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]/.test(text);
}

// ── 检测是否为 UI 显示文本 ──
function isUiText(text) {
    if (!text || text.length < 2 || text.length > 500) return false;
    if (hasChinese(text)) return false; // 已有中文就不收集
    // 需要至少包含字母
    if (!/[a-zA-Z]/.test(text)) return false;
    // 排除纯数字/代码
    if (/^[\d\s\-_.,:;!?]+$/.test(text)) return false;
    if (/^0x[0-9a-f]+$/i.test(text)) return false;
    if (/^[a-z_][a-z0-9_]*$/i.test(text) && text.length > 1) return false;
    return true;
}

// ── 创建 set_text hook ──
function hookSetText(targetAddr, name) {
    if (!targetAddr) return;
    
    try {
        Interceptor.attach(targetAddr, {
            onEnter: function (args) {
                // this = thisPtr (args[0]), value = args[1] (Il2CppString*)
                if (args.length < 2) return;
                
                const strAddr = args[1];
                const text = il2cppStringToUtf8(strAddr);
                
                if (text && isUiText(text) && !sentStrings.has(text)) {
                    sentStrings.add(text);
                    
                    // 发送到 Python 端
                    console.log(JSON.stringify({
                        type: 'text',
                        source: 'set_text',
                        name: name,
                        text: text,
                        len: text.length
                    }));
                }
            }
        });
        console.log(`[hook] ${name} @ ${targetAddr} OK`);
    } catch (e) {
        console.log(`[hook] ${name} @ ${targetAddr} FAILED: ${e.message}`);
    }
}

// ── 查找 libil2cpp.so 基址 ──
function findIl2CppBase() {
    return Module.findBaseAddress("libil2cpp.so");
}

// ── 主入口 ──
function main() {
    console.log("[frida] Starting text collector...");
    
    const il2cpp = findIl2CppBase();
    if (!il2cpp) {
        console.log("[frida] ERROR: libil2cpp.so not found!");
        return;
    }
    console.log(`[frida] libil2cpp.so base: ${il2cpp}`);
    
    // Hook 每个 set_text RVA
    for (const h of HOOK_RVAS) {
        const addr = il2cpp.add(h.rva);
        hookSetText(addr, h.name);
    }
    
    // 打印已 hook 的方法数
    console.log(`[frida] Hooked ${HOOK_RVAS.length} set_text methods`);
    console.log(`[frida] Waiting for text...`);
    console.log(`[frida] To stop: Ctrl+C`);
}

// ── 延迟执行，等 Unity 初始化完成 ──
setTimeout(main, 3000);
