# 06 · 编译与运行

## 6.1 依赖

| 依赖 | 来源 | 必需性 |
|------|------|--------|
| `<inttypes.h>` | NDK 自带 | 必需 |
| `<stdlib.h>` | NDK 自带 | 必需 |
| `<string.h>` | NDK 自带 | 必需 |
| `<errno.h>` | NDK 自带 | 必需 |
| `<sys/mman.h>` | NDK 自带 | 必需（mprotect） |
| `<android/log.h>` | NDK `liblog` | 必需（日志 + Android 平台标识） |
| `__aarch64__` 宏 | 编译器 / 平台 | 必需（整文件被 `#if defined(__aarch64__)` 守护） |
| `__builtin___clear_cache` | GCC / Clang 内建 | 必需（缓存刷新） |
| `__sync_*` 内建 | GCC / Clang 内建 | 必需（CAS） |

## 6.2 编译命令

### 6.2.1 NDK 命令行

```bash
# 把 And64InlineHook.cpp 纳入目标 .so
$NDK/toolchains/llvm/prebuilt/linux-x86_64/bin/clang++ \
    -target aarch64-linux-android21 \
    -O2 -fPIC -shared -std=c++17 \
    -I/path/to/And64InlineHook \
    And64InlineHook.cpp your_code.cpp \
    -llog -ldl \
    -o libyourhook.so
```

### 6.2.2 Android.mk 片段

```makefile
LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)
LOCAL_MODULE    := And64InlineHook
LOCAL_SRC_FILES := And64InlineHook.cpp
LOCAL_C_INCLUDES := $(LOCAL_PATH)/include
LOCAL_LDLIBS    += -llog
include $(BUILD_STATIC_LIBRARY)   # 推荐静态链接, 避免导出符号冲突

include $(CLEAR_VARS)
LOCAL_MODULE    := yourhook
LOCAL_SRC_FILES := your_code.cpp
LOCAL_STATIC_LIBRARIES += And64InlineHook
include $(BUILD_SHARED_LIBRARY)
```

### 6.2.3 CMakeLists.txt 片段

```cmake
add_library(And64InlineHook STATIC And64InlineHook.cpp)
target_include_directories(And64InlineHook PUBLIC ${CMAKE_CURRENT_SOURCE_DIR})
target_link_libraries(And64InlineHook PUBLIC log)

add_library(yourhook SHARED your_code.cpp)
target_link_libraries(yourhook PRIVATE And64InlineHook)
```

## 6.3 编译开关

| 宏 | 效果 | 默认 |
|----|------|------|
| `NDEBUG` | 关闭 `A64_LOGI`（信息日志），保留 `A64_LOGE` | 未定义（开启 INFO） |

`__fix_instructions` 在 `count > A64_MAX_INSTRUCTIONS` 时会 `A64_LOGE("too many fixing instructions!")` 仅在 `NDEBUG` 未定义时（`439-441` 行）。

## 6.4 API 用法

### 6.4.1 `A64HookFunction`（推荐入口）

```c
#include "And64InlineHook.hpp"

// 假设要 hook 的目标函数原型
extern int target_function(int a, int b);

// 替换函数
int my_hook(int a, int b) {
    // 可调用原函数（通过 trampoline）
    // 注: 原 trampoline 由 A64HookFunction 内部生成
    extern int (*orig_target_function)(int, int); // 由 .so 暴露出来
    int orig_result = orig_target_function(a, b);
    return orig_result * 2;
}

void install_hook() {
    void *trampoline = NULL;
    A64HookFunction(
        (void *)target_function,  // 目标地址
        (void *)my_hook,          // 替换函数
        &trampoline               // 输出: 跳转到原函数头的地址
    );
    // 将 trampoline 保存到全局指针, 供 my_hook 调用
    orig_target_function = (int (*)(int, int))trampoline;
}
```

### 6.4.2 `A64HookFunctionV`（高级入口）

```c
// 调用者自行准备 RWX 缓冲区
static uint32_t my_rwx_buffer[50] __attribute__((aligned(4096)));

void install_hook_v() {
    void *trampoline = A64HookFunctionV(
        (void *)target_function,
        (void *)my_hook,
        my_rwx_buffer,         // 调用者提供
        sizeof(my_rwx_buffer)
    );
    if (trampoline == NULL) {
        // 缓冲区太小或 mprotect 失败
    }
}
```

> **适用场景**：用户希望 hook 的 trampoline 在自己控制的内存区域（便于反调试、加密、自定义 mprotect）。

### 6.4.3 无 unhook

库的公开 API 中**没有 unhook 函数**。若必须撤销：

1. 保留 `szbyBackupOpcodes` 副本（库不提供，但 `__fix_instructions` 写之前已经 memcpy 过）
2. `mprotect(symbol, RWX)` + `memcpy(symbol, backup, 20)` + `__builtin___clear_cache(symbol, 20)`

但**库不保证 trampoline 后续仍可用**——若 trampoline 已被其他函数占用，直接跳转会执行新内容。

## 6.5 运行时注意事项

### 6.5.1 ARMv8.x 子特性

| 特性 | 兼容性 | 后果 |
|------|--------|------|
| ARMv8.0 基础 | ✅ | 设计目标 |
| ARMv8.1 / 8.2 (LSE atomics 等) | ✅ | 不涉及指令修复范围 |
| ARMv8.3 (PAUTH/LDAPR) | ⚠️ | PAUTH 签名的指针在 trampoline 中无效 |
| ARMv8.5 (BTI) | ❌ | hook 点若在 BTI `bti` 指令后，跳入会触发 BTI 异常 |
| ARMv8.5 (MTE) | ❌ | trampoline 写入未打 tag 的内存可能触发 MTE fault |
| PAC (Pointer Authentication) | ❌ | trampoline 存的 8-byte 绝对地址未被签名，跳转可能失败 |

### 6.5.2 线程安全

- `FastAllocateTrampoline` 用 `__sync_add_and_fetch` → **分配线程安全**
- `A64HookFunctionV` 的远跳转分支：写 5 条指令**非原子**，正在执行的线程可能读到部分写入的乱码指令
- `A64HookFunctionV` 的近跳转分支：用 `__sync_bool_compare_and_swap`，**原子**改写 1 条指令
- **结论**：生产环境建议**先暂停所有线程**（ptrace attach 或其他手段）再 hook

### 6.5.3 Android 版本

| Android 版本 | `.text` 默认属性 | 库的兼容性 |
|--------------|-----------------|-----------|
| ≤ 9 | R-X | OK（库会 mprotect 为 RWX） |
| ≥ 10 | R-- | OK（库专门加了 `__make_rwx(symbol, 5 * sizeof(size_t))`，行 587） |

### 6.5.4 SELinux

Android 9+ 默认不允许 app 进程 mprotect 任意页面为可执行。需要：

1. root 设备
2. 或 `setenforce 0`
3. 或用 `dlopen` + 注入到目标进程（zygote 注入）

库本身**不做任何提权**，仅依赖调用进程的权限。

## 6.6 单元测试 / 示例

仓库未自带测试代码。建议参考：

- Ele7enxxh 的 [Android Inline Hook](http://ele7enxxh.com/Android-Arm-Inline-Hook.html) —— 同源设计思路
- Rprop 的仓库根目录 README 提及 `https://github.com/Rprop/And64InlineHook`

最小测试代码框架：

```c
#include "And64InlineHook.hpp"
#include <stdio.h>

__attribute__((noinline))
int target_add(int a, int b) { return a + b; }

int (*orig_target_add)(int, int);

int hook_add(int a, int b) {
    LOGI("hook_add called: a=%d b=%d", a, b);
    return orig_target_add(a, b) + 1000;
}

int main() {
    LOGI("before hook: %d", target_add(1, 2));   // 3
    void *trampoline = NULL;
    A64HookFunction((void *)target_add, (void *)hook_add, &trampoline);
    orig_target_add = trampoline;
    LOGI("after hook:  %d", target_add(1, 2));   // 1003
    return 0;
}
```