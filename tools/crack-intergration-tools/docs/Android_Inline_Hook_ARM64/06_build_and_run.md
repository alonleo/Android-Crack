# 06 · 编译与运行

## 6.1 依赖

| 依赖 | 来源 | 必需性 |
|------|------|--------|
| `<stdio.h>`, `<stdlib.h>`, `<string.h>`, `<errno.h>` | libc | 必需 |
| `<unistd.h>`, `<sys/mman.h>`, `<sys/ptrace.h>` | libc / NDK | 必需（mmap, mprotect, getpid） |
| `<android/log.h>` | NDK `liblog` | 必需 |
| `<stdbool.h>` | libc | 必需 |
| ARM64 交叉编译 | NDK `aarch64-linux-android-*` | 必需 |
| ARM 汇编器 | binutils `aarch64-linux-android-as` | 必需（编译 `ihookstub.s`） |
| C++ STL (`std::vector`) | `gnustl_static` / `c++_static` | Interface 层必需 |

## 6.2 编译命令

### 6.2.1 NDK 标准流程（`ndk-build`）

```bash
cd jni
$NDK/ndk-build
# 输出: ../libs/arm64-v8a/libInlineHook.so
```

### 6.2.2 CMake 移植

```cmake
cmake_minimum_required(VERSION 3.18)
project(InlineHook)

add_library(IHook STATIC
    InlineHook/Ihook.c
    InlineHook/fixPCOpcode.c
    InlineHook/ihookstub.s
)
target_include_directories(IHook PUBLIC InlineHook)
target_link_libraries(IHook PUBLIC log)

add_library(InlineHook SHARED Interface/InlineHook.cpp)
target_link_libraries(InlineHook PRIVATE IHook log)
target_compile_options(InlineHook PRIVATE -fexceptions)
```

## 6.3 编译开关

| 宏 | 效果 | 默认 |
|----|------|------|
| `APP_ABI` | `arm64-v8a` (`Application.mk`) | 必须 |
| `APP_STL` | `gnustl_static` (`Application.mk`) | 必须（C++ STL） |
| `APP_CPPFLAGS` | `-fexceptions` (`Application.mk`) | 必须（异常） |
| `LOCAL_ARM_MODE` | `arm` (`InlineHook/Android.mk`) | 强制 ARM 模式（无关紧要，纯 C） |
| `LOCAL_CXXFLAGS` | `-g -O0` | 调试友好，建议改为 `-O2` 发布 |
| `NDEBUG` | 未使用，本库无 NDEBUG 控制 | - |

## 6.4 API 用法

### 6.4.1 `InlineHook` 主入口

```c
#include <sys/user.h>  // user_pt_regs

// 用户回调签名固定为: void (*)(struct user_pt_regs *)
void my_hook(struct user_pt_regs *regs) {
    // 读取参数: regs->regs[0] = X0, regs->regs[1] = X1, ...
    // 修改返回值: regs->regs[0] = new_value;
    LOGI("hook called: X0=%llu", regs->regs[0]);
}

void install() {
    // 1. 获取目标地址 (用 /proc/self/maps 或 dlopen)
    void *target = (void *)((uint64_t)lib_target_base + 0x600);

    // 2. 安装 hook
    if (!InlineHook(target, my_hook)) {
        LOGE("hook failed");
    }
}
```

### 6.4.2 `UnInlineHook` 取消 hook

```c
void uninstall() {
    if (!UnInlineHook(target)) {
        LOGE("unhook failed or not found");
    }
}
```

> **警告**：当前实现的 `UnInlineHook` **未恢复原指令**，仅释放 malloc 内存。详见 [04_data_flow.md §4.3](04_data_flow.md)。

### 6.4.3 `ModifyIBored` 自动注入示例

```c
// Interface/InlineHook.cpp:117-135
void ModifyIBored() __attribute__((constructor));
void ModifyIBored() {
    int target_offset = 0x600;
    void* pModuleBaseAddr = GetModuleBaseAddr(-1, "libhellojni.so");
    if (!pModuleBaseAddr) return;
    uint64_t uiHookAddr = (uint64_t)pModuleBaseAddr + target_offset;
    InlineHook((void*)uiHookAddr, EvilHookStubFunctionForIBored);
}
```

`__attribute__((constructor))` 让 `ModifyIBored` 在 `main()` 前自动执行。

## 6.5 使用方式

### 6.5.1 Xposed 加载

```bash
# 把编译好的 libInlineHook.so 推入设备
adb push libs/arm64-v8a/libInlineHook.so /data/local/tmp/

# 用 Xposed 注入到目标 app
# (Xposed 模块配置 init.rc / Xposed Installer 加载 .so)
```

### 6.5.2 Frida Gadget 替代方案

可考虑用 Frida 替代本库（更稳定、跨平台），但本库零依赖、可作为 Frida 不可用时的备选。

### 6.5.3 ptrace 注入

```c
// 1. fork + ptrace(PTRACE_ATTACH, target_pid)
// 2. dlopen("libInlineHook.so") 到目标进程
// 3. dlsym 获取 InlineHook 函数指针
// 4. 调用 InlineHook(target_addr_in_target_process, callback_in_target_process)
```

## 6.6 已知限制

| 限制 | 说明 |
|------|------|
| ARMv8.5+ BTI 不兼容 | stub 入口无 `BTI` 指令 |
| PAC 不兼容 | LR/X0 签名会失败 |
| cache flush 未实现 | ARM Cortex-A 部分实现需要显式 `__builtin___clear_cache` |
| mmap 泄漏 | `fixPCOpcodeArm` 每次 hook 泄漏 4 KiB |
| unhook 不完整 | 仅释放内存，未恢复原指令 |
| 备份长度硬编码 24 | 若 hook 点跨 6 条以上指令会截断 |
| CBZ/CBNZ/TBZ/TBNZ 修复缺失 | `fixPCOpcodeArm64` 落到 OTHER 分支，原样拷贝 |
| 并发不安全 | malloc + 修复 + 写 hook 点非原子 |

## 6.7 单元测试框架示例

```c
#include "Ihook.h"
#include <sys/user.h>
#include <dlfcn.h>

typedef int (*add_fn_t)(int, int);
__attribute__((noinline))
int target_add(int a, int b) { return a + b; }
int (*orig_add)(int, int) = NULL;

void test_callback(struct user_pt_regs *regs) {
    LOGI("X0=%lld, X1=%lld", regs->regs[0], regs->regs[1]);
    regs->regs[0] += 100;  // 修改返回值
}

int main() {
    LOGI("before: %d", target_add(1, 2));   // 3

    if (!InlineHook((void *)target_add, test_callback)) {
        LOGE("hook failed");
        return 1;
    }

    LOGI("after:  %d", target_add(1, 2));   // 103 (被 hook 改成 X0+=100)

    UnInlineHook((void *)target_add);
    return 0;
}
```

> **注意**：此测试代码调用 `InlineHook` 自身（修改 `target_add`），编译时需链接 `libInlineHook.so` 或将所有源文件编入同一可执行文件。