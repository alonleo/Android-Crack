/**
 * native-lib.cpp — il2cpp skill 标准 hook 入口（A64HookFunction + JNI 回调）
 *
 * 模板来源：il2cpp 项目实测提取，作为 il2cpp skill 通用骨架。
 * sub-stage-template-integration.py 会用本文件覆盖 AS 工程中的
 * native-lib.cpp（之前是 FakerAndroid fakeCpp 模式，会破坏 UnityPlayerActivity）。
 *
 * ## 关键函数
 * - `setupHooks(baseAddr)`：由 retryNativeHooks() 通过 /proc/self/maps 解析
 *   libil2cpp.so 真实基址（页对齐，非 dlopen 返回值）后调用。
 *   子阶段 sub-stage-hook-plan / sub-stage-hook-fn-analyze 会按
 *   hook-plan.yaml 中的 rva 填充 A64HookFunction 调用。
 * - `callJava(event)`：通过 JNI 调用 Java 层 JniBridge.onJniCall(event)，
 *   实现 native → Java 事件传递（激励视频/IAP/Premium/网络检测）。
 * - `JNI_OnLoad`：保存 JavaVM* 指针供 callJava 使用。
 *
 * ## 模板占位符（脚本替换）
 * - `{PROJECT_NAME}`：项目名
 *
 * ## 关联脚本
 * - 模板来源：crackings/<type>/<Name>/project/app/src/main/cpp/native-lib.cpp
 * - 模板消费：skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-template-integration.py
 * - 注入 hook：sub-stage-hook-plan.py / sub-stage-hook-fn-analyze.py
 */
#include <jni.h>
#include <cstring>
#include <cstdio>
#include <dlfcn.h>
#include <android/log.h>
#include <string>
#include <thread>   // [FLOWFIX] std::thread 用于 installNativeHooks 后台线程
#include <chrono>   // [FLOWFIX] std::this_thread::sleep_for

#define LOGI(...) __android_log_print(ANDROID_LOG_INFO, "xNative", __VA_ARGS__)
#define LOGE(...) __android_log_print(ANDROID_LOG_ERROR, "xNative", __VA_ARGS__)

extern "C" void A64HookFunction(void* target, void* hook, void** orig);

static JavaVM* g_jvm = nullptr;
static jobject g_callback = nullptr;



// Il2CppString 布局: klass(0x00) + monitor(0x08) + length(0x10) + chars(0x14, UTF-16LE)
static std::string il2cppStringToUtf8(const void* s) {
    if (!s) return "";
    const char* p = static_cast<const char*>(s);
    int32_t len = *reinterpret_cast<const int32_t*>(p + 0x10);
    if (len <= 0) return "";
    const uint16_t* u = reinterpret_cast<const uint16_t*>(p + 0x14);
    std::string out;
    out.reserve(static_cast<size_t>(len) * 2);
    for (int32_t i = 0; i < len; i++) {
        uint32_t cp = u[i];
        if (cp >= 0xD800 && cp <= 0xDBFF && i + 1 < len) {
            uint16_t lo = u[i + 1];
            if (lo >= 0xDC00 && lo <= 0xDFFF) {
                cp = 0x10000 + ((cp - 0xD800) << 10) + (lo - 0xDC00);
                i++;
            }
        }
        if (cp < 0x80) out += static_cast<char>(cp);
        else if (cp < 0x800) {
            out += static_cast<char>(0xC0 | (cp >> 6));
            out += static_cast<char>(0x80 | (cp & 0x3F));
        } else if (cp < 0x10000) {
            out += static_cast<char>(0xE0 | (cp >> 12));
            out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
            out += static_cast<char>(0x80 | (cp & 0x3F));
        } else {
            out += static_cast<char>(0xF0 | (cp >> 18));
            out += static_cast<char>(0x80 | ((cp >> 12) & 0x3F));
            out += static_cast<char>(0x80 | ((cp >> 6) & 0x3F));
            out += static_cast<char>(0x80 | (cp & 0x3F));
        }
    }
    return out;
}

static void callJava(const char* event) {
    if (g_callback == nullptr) {
        return;
    }
    JNIEnv* env = nullptr;
    if (g_jvm->GetEnv(reinterpret_cast<void**>(&env), JNI_VERSION_1_6) != JNI_OK || !env) {
        return;
    }
    jclass clazz = env->GetObjectClass(g_callback);
    jmethodID on_call = env->GetMethodID(clazz, "onJniCall", "(Ljava/lang/String;)V");
    jstring evt = env->NewStringUTF(event);
    env->CallVoidMethod(g_callback, on_call, evt);
    env->DeleteLocalRef(evt);
}



void setupHooks(uintptr_t baseAddr) {
    LOGI("[hook] baseImageAddr: libil2cpp.so = 0x%x", (unsigned)baseAddr);
    if (!baseAddr) return;

    LOGI("[hook] === Hook Engine Initialized ===");
}



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

// [FLOWFIX] installNativeHooks：
// App.onCreate 调用，后台线程等待 libil2cpp.so 加载后通过 /proc/self/maps
// 解析页对齐基址（非 dlopen soinfo 指针）→ setupHooks(base)。
extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_App_installNativeHooks(JNIEnv* env, jobject thiz) {
    LOGI("[hook] installNativeHooks() called");
    std::thread([] {
        for (int i = 0; i < 120; i++) {
            if (dlopen("libil2cpp.so", RTLD_NOW)) {
                uintptr_t base = 0;
                FILE* fp = fopen("/proc/self/maps", "r");
                if (fp) {
                    char line[1024];
                    while (fgets(line, sizeof(line), fp)) {
                        if (strstr(line, "libil2cpp.so") && strchr(line, 'r')) {
                            base = strtoull(line, nullptr, 16);
                            break;
                        }
                    }
                    fclose(fp);
                }
                if (base) {
                    LOGI("[hook] libil2cpp.so base = 0x%lx", (unsigned long)base);
                    setupHooks(base);
                    return;
                }
            }
            std::this_thread::sleep_for(std::chrono::milliseconds(500));
        }
        LOGE("[hook] libil2cpp.so not loaded after 60s");
    }).detach();
}

extern "C" JNIEXPORT void JNICALL
Java_com_android_boot_MainActivity_retryNativeHooks(JNIEnv* env, jobject thiz) {
    LOGI("[hook] retryNativeHooks() called");
    // [FLOWFIX]
    // dlopen() 返回 soinfo 指针（非页对齐，如 0xbc9f896f），与 RVA 相加 → SIGSEGV。
    // 必须用 /proc/self/maps 解析 mmap 真实基址（页对齐，如 0x7048f40000）。
    uintptr_t base = 0;
    FILE* fp = fopen("/proc/self/maps", "r");
    if (fp) {
        char line[1024];
        while (fgets(line, sizeof(line), fp)) {
            if (strstr(line, "libil2cpp.so") && strchr(line, 'r')) {
                base = strtoull(line, nullptr, 16);
                break;
            }
        }
        fclose(fp);
    }
    if (!base) {
        void* handle = dlopen("libil2cpp.so", RTLD_NOW);
        if (!handle) {
            LOGI("[hook] libil2cpp.so not loaded yet");
            return;
        }
        Dl_info info;
        if (dladdr(handle, &info) && info.dli_fbase) {
            base = reinterpret_cast<uintptr_t>(info.dli_fbase);
        }
    }
    LOGI("[hook] libil2cpp.so base = 0x%lx", (unsigned long)base);
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
