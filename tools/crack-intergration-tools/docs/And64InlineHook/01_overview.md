# 01 · 项目概览

## 1.1 定位

`And64InlineHook` 是 Rprop 在 2018 年 4 月发布的一个**ARMv8-A (AArch64) 架构上的 inline hook 库**，专门为 Android 平台设计（依赖 `<android/log.h>`）。它以两个公开 C API 的形式提供：

- `A64HookFunction(symbol, replace, &result)` —— 主入口，自动从静态 trampoline 池分配
- `A64HookFunctionV(symbol, replace, rwx, rwx_size)` —— 高级入口，调用者提供 RWX 缓冲区

库实现只有一个 `.cpp` 文件、约 600 行，**纯头文件依赖**，无运行时第三方库，可直接纳入任意 NDK / CMake / Makefile 项目。

## 1.2 设计理念

| 维度 | 决策 |
|------|------|
| **trampoline 分配** | 编译期静态池 `static uint32_t __insns_pool[A64_MAX_BACKUPS][A64_MAX_INSTRUCTIONS * 10]`，按 `__sync_add_and_fetch` 原子自增分配槽位 |
| **修复函数调度** | 4 个 `__fix_*` 静态函数**链式调用**（非 switch-case on opcode mask），按 B/cond/LDR-literal/ADR 顺序尝试，匹配则跳过后续 |
| **Hook 点写入** | 近跳转（距离 ≤ ±128 MiB）：单条 `B`；远跳转：`LDR X17, #8; BR X17; <8-byte addr>` 20 字节（必要时加 NOP 对齐） |
| **PC-relative 修复** | 通过 `context::insns_info` 的 `fmap` 数组延迟回填前向引用（即"backpatch"模式），可处理备份区间内的循环分支 |
| **缓存同步** | `__builtin___clear_cache` 在写完代码后立即调用 |
| **页属性** | `mprotect(PROT_READ\|PROT_WRITE\|PROT_EXEC)` 显式按页改 RWX |
| **原子性** | 写 hook 点用 `__sync_bool_compare_and_swap`（仅近跳转分支使用） |
| **unhook** | **不支持**（一旦 hook 永久生效） |
| **ARMv8.5+ 特性** | **不支持** BTI（Branch Target Identification）、PAC（Pointer Authentication）、MTE（Memory Tagging Extension） |

## 1.3 适用场景

- **游戏修改**：HOOK `libunity.so` 中的函数、修改返回值
- **逆向调试**：在原生代码中插入断点 / 输出寄存器
- **Android 10+ 兼容性**：作者专门加了 `__make_rwx(symbol, 5 * sizeof(size_t))` 处理 Android 10 默认 .text 只读
- **轻量集成**：只需要 hook 几十个函数、不需要 unhook、不需要并发

## 1.4 不适用场景

- 需要运行时取消 hook（unhook）→ 改用 [Android_Inline_Hook_ARM64](../Android_Inline_Hook_ARM64/)
- 需要支持 ARMv8.5+ BTI/PAC（Android 11+ 上 ART JIT 代码可能 BTI-enable）→ 需要更现代的库
- 多线程并发 hook 同地址 → 本库原子性只覆盖单条 `B` 写入，远跳转分支非原子
- hook 点不在前 4 条指令边界 → 调大 `A64_MAX_INSTRUCTIONS`（但要重新编译）

## 1.5 与同类项目的对比

| 维度 | And64InlineHook (Rprop) | Android_Inline_Hook_ARM64 (GToad) |
|------|------------------------|-----------------------------------|
| 代码量 | 596 行单文件 | 1300+ 行 6 文件 |
| 公开 API | `A64HookFunction` (C) | `InlineHook(pHookAddr, onCallBack)` (C++) |
| 回调签名 | **无回调**（仅跳转到 replace） | `void onCallBack(user_pt_regs *regs)` |
| unhook | ❌ 不支持 | ✅ 支持 |
| trampoline 分配 | 静态池 + 原子自增 | malloc + mmap |
| 寄存器保存 | 不需要 | 完整 GPR + NZCV 栈帧 |
| 修复后指令长度上限 | A64_MAX_INSTRUCTIONS = 5 (~40 字节) | 24 字节（6 条指令） |
| 模块基址解析 | 无（用户传入绝对地址） | `/proc/pid/maps` 解析 |
| ARM32 支持 | ❌ | ✅ 兼容 ARM32 (本仓库 ARM64 专用，源码支持) |
| 链接可见性 | `__attribute__((visibility("default")))` | 默认（需 `LOCAL_LDLIBS += -llog`） |

详见 [`../ARMT64_HOOK_COMPARISON.md`](../ARMT64_HOOK_COMPARISON.md)。

## 1.6 关键源码坐标

| 角色 | 文件:行 |
|------|--------|
| 公开 API 声明 | `And64InlineHook.hpp:36-38` |
| 常量定义 | `And64InlineHook.cpp:40-49` |
| `context` 结构体 | `And64InlineHook.cpp:51-106` |
| 宏（页对齐 / 缓存刷新 / CAS） | `And64InlineHook.cpp:110-125` |
| `__fix_branch_imm` | `And64InlineHook.cpp:129-190` |
| `__fix_cond_comp_test_branch` | `And64InlineHook.cpp:194-254` |
| `__fix_loadlit` | `And64InlineHook.cpp:258-333` |
| `__fix_pcreladdr` | `And64InlineHook.cpp:337-426` |
| `__fix_instructions`（调度） | `And64InlineHook.cpp:430-476` |
| `__insns_pool` 静态池 | `And64InlineHook.cpp:481` |
| `A64HookInit`（构造时 mprotect） | `And64InlineHook.cpp:485-494` |
| `FastAllocateTrampoline` | `And64InlineHook.cpp:498-510` |
| `A64HookFunctionV`（高级入口） | `And64InlineHook.cpp:514-573` |
| `A64HookFunction`（公开入口） | `And64InlineHook.cpp:577-593` |