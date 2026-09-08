# il2cpp Native Hook 引擎设置（native-lib 加载 + 基址解析 + UIElements 隐藏）

> 来源: FlyingGorillaEndlessRunner (Unity 6.3 il2cpp) | 2026-08-02
> 适用: 所有用 FakerAndroid 骨架 + A64HookFunction 做 native hook 的 il2cpp 项目

## 1. native-lib 可能从未被加载（最重要）

FakerAndroid 生成的 `com.android.boot.App`（静态块 `System.loadLibrary("native-lib")` +
`onCreate → fakeApp` 装 hook）**只在它是 manifest 的 `<application android:name>` 时才运行**。

原游戏往往有自己的 Application（如 `com.pairip.application.Application`），
manifest 指向它 → `com.android.boot.App` 从不实例化 → **native hook 全部不生效**。

### 判定

```bash
adb logcat -d | grep "JNI_OnLoad"      # 有 IL2CPP 的但没 xNative 的 = native-lib 没加载
adb logcat -d | grep "xNative.*hook"   # 无输出 = hook 没装
```

### 修复

1. `com/android/boot/App.java` 增加:
   ```java
   public static native void installNativeHooks();
   ```
2. `native-lib.cpp` 实现 `Java_com_android_boot_App_installNativeHooks`（后台线程轮询 libil2cpp + dl_iterate_phdr 取基址 → setupHooks）
3. 注入到真实 Application（脚本 `inject-native-hook-loader.py`）:
   ```bash
   python3 skills/strategy/il2cpp-strategy-skill/scripts/common/inject-native-hook-loader.py <apktool_root>
   ```
   效果: 真实 `Application.attachBaseContext` 里加
   ```
   System.loadLibrary("native-lib")
   App.installNativeHooks()
   ```

## 2. 基址必须用 dl_iterate_phdr（不是 dlopen handle）

`reinterpret_cast<uintptr_t>(dlopen("libil2cpp.so"))` 拿到的是 **soinfo 指针**（非页对齐，
如 0xa574b107），不是 ELF 加载基址 → `base + RVA` 地址错 → A64HookFunction 写 trampoline 时 SIGSEGV。

正确做法（页对齐基址，如 0x46101000）：

```cpp
#include <link.h>
struct BaseCtx { const char* want; uintptr_t base; };
static int phdr_cb(struct dl_phdr_info* info, size_t size, void* data) {
    BaseCtx* ctx = (BaseCtx*)data;
    if (info->dlpi_name && strstr(info->dlpi_name, ctx->want)) { ctx->base = info->dlpi_addr; return 1; }
    return 0;
}
static uintptr_t find_lib_base(const char* want) { BaseCtx c = {want, 0}; dl_iterate_phdr(phdr_cb, &c); return c.base; }
```

后台线程轮询（libil2cpp 在 Application.onCreate 时还没加载）:
```cpp
static void hookInstallThread() {
    for (int i = 0; i < 120; i++) {
        if (dlopen("libil2cpp.so", RTLD_NOW)) {
            uintptr_t base = find_lib_base("libil2cpp.so");
            if (base) { setupHooks(base); return; }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(500));
    }
}
```

## 3. CMake 必须编译 And64InlineHook

`file(GLOB native_src "${CMAKE_SOURCE_DIR}/*.cpp")` 不含子目录 → `A64HookFunction` 未定义。

```cmake
file(GLOB native_src "${CMAKE_SOURCE_DIR}/*.cpp")
file(GLOB inlinehook_src "${CMAKE_SOURCE_DIR}/And64InlineHook/*.cpp")   # 关键
add_library(native-lib SHARED ${native_src} ${inlinehook_src})
```

## 4. UIElements 按钮隐藏（去功能点）

UIElements 的节点移除、布局差异和 click handler 处理统一见 [去功能点 Unity 实现](../../../common/feature-removal-strategy-skill/references/engine-notes.md#il2cpp)。本页只维护 native 加载、基址与链接机制。

## 5. 关键 RVA 查找（metadata.json）

通过正式分析脚本读取当前项目 `metadata.json` 的 `addressMap.methodDefinitions`，核对 mangled C++ 符号和 `virtualAddress`；地址与字段偏移只记入项目记录，不复用其他 APK 的数值。UIElements 目标方法见上面的统一实现说明。
