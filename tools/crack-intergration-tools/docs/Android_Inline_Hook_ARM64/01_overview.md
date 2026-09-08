# 01 · 项目概览

## 1.1 定位

`Android_Inline_Hook_ARM64` 是 GToad 在 2018 年发布的 Android inline hook 库 ARM64 版本（在原 ARM32/Thumb-2 仓库基础上扩展）。它通过 JNI 暴露两个公开 API：

- `InlineHook(void *pHookAddr, void (*onCallBack)(struct user_pt_regs *))` —— 安装 hook
- `UnInlineHook(void *pHookAddr)` —— 取消 hook

核心思路：

1. 把 hook 点原始 24 字节（最多 6 条 ARM64 指令）备份
2. 把 ARM64 汇编 stub（保存全部 GPR + NZCV → 调用户回调 → 恢复 → 跳回原函数）拷贝到 `malloc` 出的内存，并 `mprotect` 为 RWX
3. 在 `malloc` 出的另一段内存里构造"修复后的旧函数入口"（处理 PC-relative 指令）
4. 最后在 hook 点写入 24 字节长跳转（`STP X1,X0 + LDR X0,8 + BR X0 + <addr> + LDR X0,[sp,-8]`）

## 1.2 设计理念

| 维度 | 决策 |
|------|------|
| **回调模型** | 类 x86 hook：用户拿到 `user_pt_regs *regs` 可读/写全部寄存器 |
| **寄存器保存** | 完整保存 X0–X29 + NZCV（共 240 字节栈帧） |
| **trampoline 分配** | `malloc`（stub）+ `malloc`（旧函数入口），运行时分配 |
| **unhook 支持** | ✅ 通过 `gs_vecInlineHookInfo` 注册表，按 `pHookAddr` 查找并释放 |
| **ARM32 兼容** | 修复函数支持 ARM32 + ARM64 两套（本仓库仅 ARM64，但代码保留） |
| **自动执行** | `__attribute__((constructor))` 在 main() 前自动 hook（示例） |
| **模块基址解析** | 通过 `/proc/pid/maps` 解析（不依赖 dlopen） |
| **PC-relative 修复** | 按指令类型枚举分发：ADR/ADRP/LDR-literal/B/B.cond 等，每类生成独立的 trampoline 序列 |
| **cache flush** | **未调用** `__builtin___clear_cache`（注释行 244-246 提到，但代码里没做——见 `04_data_flow.md` 已知问题） |

## 1.3 与 Rprop 库的关键差异

| 维度 | Android_Inline_Hook_ARM64 (GToad) | And64InlineHook (Rprop) |
|------|----------------------------------|------------------------|
| 回调签名 | `void onCallBack(user_pt_regs *regs)`（可读写寄存器） | **无回调**（直接跳到 replace） |
| 寄存器保存 | stub 汇编栈帧 | 不需要 |
| unhook | ✅ 完整支持 | ❌ 不支持 |
| trampoline 分配 | 每次 `malloc`（无上限） | 静态池（256 上限） |
| hook 长度 | 固定 24 字节（最多 6 条指令） | 1 条（近跳）或 5 条（远跳） |
| 模块基址 | `/proc/pid/maps` | 用户传入绝对地址 |
| cache flush | ❌（已知缺陷） | ✅ |
| ARM32 兼容 | ✅ | ❌ |

## 1.4 适用场景

- **游戏逆向**：在 ART/Unity 原生层 hook 函数并修改寄存器（如改 `r0` 模拟受伤判定）
- **自动化测试**：hook 关键函数做 mock、spy
- **需要 unhook 的场景**：插件按需启用/禁用
- **教学**：完整的汇编 stub、PC-relative 修复示例代码

## 1.5 不适用场景

- Android 11+ 上有 BTI 的代码段（stub 入口无 `BTI` 指令会触发 BTI fault）
- PAC 签名的指针
- 多线程同时 hook 同一地址（分配 + 修复非原子）

## 1.6 关键源码坐标

| 角色 | 文件:行 |
|------|--------|
| 公开 API（用户接口） | `Interface/InlineHook.cpp:36-60`, `:67-100` |
| 库入口 | `InlineHook/Ihook.c:372-433` (`HookArm`) |
| 数据结构 | `InlineHook/Ihook.h:43-52` (`INLINE_HOOK_INFO`) |
| 修复主循环 | `InlineHook/fixPCOpcode.c:294-395` (`fixPCOpcodeArm`) |
| 修复分派 | `InlineHook/fixPCOpcode.c:402-593` (`fixPCOpcodeArm64`) |
| 汇编 stub 模板 | `InlineHook/ihookstub.s:8-80` |
| 长跳转构造 | `InlineHook/Ihook.c:207-253` (`BuildArmJumpCode`) |
| 模块基址 | `InlineHook/Ihook.c:50-101` (`GetModuleBaseAddr`) |