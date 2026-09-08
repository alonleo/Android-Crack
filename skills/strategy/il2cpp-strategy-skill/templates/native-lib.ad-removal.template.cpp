/**
 * native-lib.ad-removal.template.cpp — il2cpp 广告移除 hook 模板
 * 项目来源: AltosAdventure (2026-08-04)
 *
 * ⚠️ 使用前必读:
 *  1. 本模板的 RVA 基于 AltosAdventure 的 dump.cs，**其他项目需重新定位**
 *     （用 verify-il2cpp-rva.py 或 Frida 确认目标地址是函数入口）
 *  2. base 地址必须用 /proc/self/maps 解析的 mmap 映射基址，
 *     **不能直接用 dlopen() 返回值**（Android 返回链接地址，可能非页对齐 → SIGSEGV）
 *  3. hook 前 Frida 验证指令：标准 prologue (stp x29,x30 → f81d0ffe) 可 hook；
 *     极短函数 (mov w0,#N; ret → 528000xx d65f03c0) 不可 hook（会破坏指令崩溃）
 *
 * 广告 hook 策略（NoodleAdManager，dump.cs TypeDefIndex 1706）:
 *  - DisplayAd(AdDisplayContext)  → 拦截 → callJava("showVideo") 本地模拟激励视频
 *  - ShowInterstitial()            → 空实现（屏蔽插屏）
 *  - ShouldShowInterstitial()→bool → 返回 false（永不触发插屏）
 *
 * 需结合:
 *  - MainActivity.java 的 onJniCall "showVideo" case（SDKUtils 三阶段模拟）
 *  - CMakeLists.txt: file(GLOB and64_src "${CMAKE_SOURCE_DIR}/And64InlineHook/*.cpp")
 */

#include <jni.h>
#include <cstring>
#include <cstdio>
#include <dlfcn.h>
#include <android/log.h>
#include <string>

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "xNative", __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "xNative", __VA_ARGS__)

extern "C" void A64HookFunction(void* target, void* hook, void** orig);

static JavaVM* g_jvm = nullptr;
static jobject g_callback = nullptr;

static void* orig_DisplayAd = nullptr;
static void* orig_ShowInterstitial = nullptr;

// ── /proc/self/maps 解析模块基址（可靠，页对齐） ─────────────────
// ⚠️ [FLOWFIX] AltosAdventure] 不能用 dlopen() 返回值作 base
// （Android dlopen 返回链接地址，可能含 .text 段偏移 → base+RVA 计算错误 → SIGSEGV）
static uintptr_t find_module_base(const char* soname) {
    FILE* fp = fopen("/proc/self/maps", "r");
    if (!fp) return 0;
    char line[512];
    uintptr_t base = 0;
    while (fgets(line, sizeof(line), fp)) {
        if (strstr(line, soname)) {
            unsigned long addr = 0;
            char perms[8] = {0};
            if (sscanf(line, "%lx-%*lx %7s", &addr, perms) == 2) {
                if (perms[0] == 'r') {  // 首个 r 段（ELF 头）即加载基址
                    base = addr;
                    break;
                }
            }
        }
    }
    fclose(fp);
    return base;
}

// ── callJava: JNI → Java 层事件 ──────────────────────────────────
static void callJava(const char* event) {
    if (g_callback == nullptr) return;
    JNIEnv* env = nullptr;
    if (g_jvm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK || !env) return;
    jclass clazz = env->GetObjectClass(g_callback);
    jmethodID on_call = env->GetMethodID(clazz, "onJniCall", "(Ljava/lang/String;)V");
    jstring evt = env->NewStringUTF(event);
    env->CallVoidMethod(g_callback, on_call, evt);
    env->DeleteLocalRef(evt);
}

// ── Hooked 函数 ──────────────────────────────────────────────────
static bool Hooked_ShouldShowInterstitial() {
    LOGI("[hook] ShouldShowInterstitial → false (ad blocked)");
    return false;
}

static void Hooked_ShowInterstitial() {
    LOGI("[hook] ShowInterstitial blocked");
}

static void Hooked_DisplayAd() {
    LOGI("[hook] DisplayAd intercepted → local reward simulation");
    callJava("showVideo");
}

// ── setupHooks ────────────────────────────────────────────────────
// ⚠️ RVA 为 AltosAdventure 值，其他项目用 dump.cs + verify-il2cpp-rva.py 重新定位
void setupHooks(uintptr_t baseAddr) {
    LOGI("[hook] libil2cpp.so maps base = 0x%x", (unsigned)baseAddr);
    if (!baseAddr) return;

    // NoodleAdManager.DisplayAd → 本地模拟激励视频
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x11C9FDC),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_DisplayAd)),
        &orig_DisplayAd);
    LOGI("[hook] DisplayAd hooked");

    // NoodleAdManager.ShowInterstitial → 屏蔽插屏
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x11C9C78),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_ShowInterstitial)),
        &orig_ShowInterstitial);
    LOGI("[hook] ShowInterstitial hooked");

    // NoodleAdManager.ShouldShowInterstitial → false
    A64HookFunction(
        reinterpret_cast<void*>(baseAddr + 0x11C9098),
        reinterpret_cast<void*>(reinterpret_cast<uintptr_t>(&Hooked_ShouldShowInterstitial)),
        nullptr);
    LOGI("[hook] ShouldShowInterstitial hooked → false");

    LOGI("[hook] === Ad Removal Hooks Initialized ===");
}

// ── JNI 入口 ────────────────────────────────────────────────────
extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    g_jvm = vm;
    LOGI("[hook] JNI_OnLoad: global_jvm=%p", vm);
    return JNI_VERSION_1_6;
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_App_fakeApp(JNIEnv* env, jobject thiz, jobject application) {
    LOGI("[hook] fakeApp() called");
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_App_fakeDex(JNIEnv* env, jobject thiz, jobject base) {
    LOGI("[hook] fakeDex: no-op");
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_retryNativeHooks(JNIEnv* env, jobject thiz) {
    LOGI("[hook] retryNativeHooks() called");
    uintptr_t base = find_module_base("libil2cpp.so");
    if (!base) {
        LOGI("[hook] libil2cpp.so not loaded yet");
        return;
    }
    setupHooks(base);
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_registerCallBack(JNIEnv* env, jobject thiz, jobject object) {
    if (g_callback) env->DeleteGlobalRef(g_callback);
    g_callback = env->NewGlobalRef(object);
    LOGI("[hook] JNI callback registered");
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_onVideoReward(JNIEnv* env, jobject thiz, jboolean success) {
    LOGI("[hook] onVideoReward(%d)", success);
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_onIapSuccess(JNIEnv* env, jobject thiz, jstring productId) {
    const char* pid = productId ? env->GetStringUTFChars(productId, nullptr) : "";
    LOGI("[hook] onIapSuccess(%s)", pid);
    if (productId) env->ReleaseStringUTFChars(productId, pid);
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_onPremiumUnlock(JNIEnv* env, jobject thiz) {
    LOGI("[hook] onPremiumUnlock");
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_onPremiumBuyPass(JNIEnv* env, jobject thiz) {
    LOGI("[hook] onPremiumBuyPass");
}
