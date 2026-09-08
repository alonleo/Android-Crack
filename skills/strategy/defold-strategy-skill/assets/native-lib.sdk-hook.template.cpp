/**
 * native-lib.cpp — Defold 引擎 SDK native hook（And64InlineHook）
 * 策略: 见 skills/strategy/defold-strategy-skill/strategy.md §7
 *
 * 目标: hook libBananaKong.so 导出的 Java_com_defold_*_addToQueue 符号
 * （Java glue → 引擎 → Lua 的 SDK 命令投递咽喉），使 SDK 命令不排入引擎队列。
 *
 * 定位: 这些符号是 GLOBAL DEFAULT 导出 → dlsym 直接定位（无需 base+RVA）。
 * 时机: JNI_OnLoad 起后台线程轮询 /proc/self/maps 等 libBananaKong.so 出现。
 *
 * 项目: BananaKong (com.fdgentertainment.bananakong) | 2026-08-04
 */
#include <jni.h>
#include <cstring>
#include <cstdlib>
#include <cstdio>
#include <dlfcn.h>
#include <unistd.h>
#include <android/log.h>
#include <string>
#include <thread>
#include <chrono>
#include <link.h>

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "xNative", __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "xNative", __VA_ARGS__)

extern "C" void A64HookFunction(void* target, void* hook, void** orig);

static JavaVM* g_jvm = nullptr;

// 引擎 .so 名（Defold 重命名后的主引擎库）
static const char* kEngineSo = "libBananaKong.so";

// ---- 等待引擎 .so 已加载（dlopen RTLD_NOLOAD 探测，比读 maps 更可靠）----
static bool engineLoaded() {
    void* h = dlopen(kEngineSo, RTLD_NOLOAD);
    if (h) dlclose(h);
    return h != nullptr;
}

// ---- hook 目标（导出符号，dlsym 定位）----
typedef void (*AddToQueueFn)(JNIEnv*, jclass, jint, jstring);

static AddToQueueFn orig_admobAddToQueue = nullptr;
static void hooked_admobAddToQueue(JNIEnv* env, jclass clazz, jint cmd, jstring data) {
    LOGI("[hook] ADMOB AddToQueue BLOCKED cmd=%d", cmd);
    // 不调用原函数 → SDK 命令不投递到 Lua 队列
}

static AddToQueueFn orig_firebaseAddToQueue = nullptr;
static void hooked_firebaseAddToQueue(JNIEnv* env, jclass clazz, jint cmd, jstring data) {
    LOGI("[hook] FIREBASE AddToQueue BLOCKED cmd=%d", cmd);
}

static AddToQueueFn orig_firebaseAnalyticsAddToQueue = nullptr;
static void hooked_firebaseAnalyticsAddToQueue(JNIEnv* env, jclass clazz, jint cmd, jstring data) {
    LOGI("[hook] FIREBASE-ANALYTICS AddToQueue BLOCKED cmd=%d", cmd);
}

static AddToQueueFn orig_gpgsAddToQueue = nullptr;
static void hooked_gpgsAddToQueue(JNIEnv* env, jclass clazz, jint cmd, jstring data) {
    LOGI("[hook] GPGS AddToQueue BLOCKED cmd=%d", cmd);
}

// ---- 安装 hooks ----
static void installHooks() {
    void* handle = dlopen(kEngineSo, RTLD_NOW);
    if (!handle) {
        LOGE("[hook] dlopen %s failed: %s", kEngineSo, dlerror());
        return;
    }
    void* admob = dlsym(handle, "Java_com_defold_admob_AdmobJNI_admobAddToQueue");
    if (admob) {
        A64HookFunction(admob, (void*)hooked_admobAddToQueue, (void**)&orig_admobAddToQueue);
        LOGI("[hook] ADMOB hooked @ %p", admob);
    } else {
        LOGE("[hook] dlsym admob failed");
    }
    void* fb = dlsym(handle, "Java_com_defold_firebase_FirebaseJNI_firebaseAddToQueue");
    if (fb) {
        A64HookFunction(fb, (void*)hooked_firebaseAddToQueue, (void**)&orig_firebaseAddToQueue);
        LOGI("[hook] FIREBASE hooked @ %p", fb);
    }
    void* fba = dlsym(handle, "Java_com_defold_firebase_analytics_FirebaseAnalyticsJNI_firebaseAddToQueue");
    if (fba) {
        A64HookFunction(fba, (void*)hooked_firebaseAnalyticsAddToQueue, (void**)&orig_firebaseAnalyticsAddToQueue);
        LOGI("[hook] FIREBASE-ANALYTICS hooked @ %p", fba);
    }
    void* gpgs = dlsym(handle, "Java_com_defold_gpgs_GpgsJNI_gpgsAddToQueue");
    if (gpgs) {
        A64HookFunction(gpgs, (void*)hooked_gpgsAddToQueue, (void**)&orig_gpgsAddToQueue);
        LOGI("[hook] GPGS hooked @ %p", gpgs);
    }
    LOGI("[hook] installHooks done");
}

// ---- 后台线程：等引擎 .so 出现后装 hook ----
static void hookThread() {
    for (int i = 0; i < 200; i++) {
        if (engineLoaded()) {
            LOGI("[hook] engine %s found (iter=%d), installing...", kEngineSo, i);
            installHooks();
            return;
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(300));
    }
    LOGE("[hook] engine .so not found after timeout");
}

extern "C" JNIEXPORT jint JNICALL JNI_OnLoad(JavaVM* vm, void* reserved) {
    g_jvm = vm;
    LOGI("[hook] JNI_OnLoad: native-lib loaded (Defold SDK hook)");
    std::thread t(hookThread);
    t.detach();
    return JNI_VERSION_1_6;
}

// 供注入宿主调用（方案 B 备用）
extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_App_installNativeHooks(JNIEnv* env, jclass clazz) {
    LOGI("[hook] installNativeHooks() called from Java");
    std::thread t(hookThread);
    t.detach();
}
