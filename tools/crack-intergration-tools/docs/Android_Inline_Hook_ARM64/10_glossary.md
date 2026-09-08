# 10 · 术语表

## A

### ADR / ADRP
ARM64 PC-relative 地址加载指令。本库的 `fixPCOpcodeArm64` ADR 分支会生成 `LDR Rd, 4 + 双字` 模板。

### ARM64 (AArch64)
ARMv8-A 的 64 位执行状态。本库目标平台。

### ARMv8.5+
引入 BTI / PAC / MTE。本库**不兼容**这些扩展。

### AAPCS64
ARM 64 位过程调用标准。定义 X0-X7 参数/返回值、X8 indirect result、X9-X15 caller-saved temp、X16-X17 intra-procedure-call temp、X18 platform register、X19-X28 callee-saved、X29 FP、X30 LR。

## B

### BACKUP_CODE_NUM_MAX
宏 `= 6`（`Ihook.h:21`）。最多备份 6 条指令 = 24 字节。

### BR / BLR
ARM64 间接跳转 / 带链接间接跳转。本库 stub 用 `blr x3` 调回调，`br x0` 跳旧函数。

### BTI (Branch Target Identification)
ARMv8.5 引入的跳转目标合法性检查。本库 stub 入口无 `BTI` 指令 → 兼容性差。

### BuildOldFunction
本库的核心步骤之一，构造"修复后的旧函数入口"。

### BuildStub
本库的核心步骤之一，复制汇编 stub 到 malloc 内存。

## C

### CBZ / CBNZ / TBZ / TBNZ
ARM64 比较并分支 / 测试位并分支指令。本库**未修复**这些类型，会落到 OTHER 分支原样拷贝。

### ChangePageProperty
`mprotect` 的封装，把任意内存改为 RWX。

### Constructor
`__attribute__((constructor))` 让函数在 main 前自动执行。`before_main` 和 `ModifyIBored` 都用了此特性。

### cache flush
本库**未实现** `__builtin___clear_cache`，ARM Cortex-A 上可能 hook 不立即生效。

## D

### DSB / ISB
ARM64 数据同步屏障 / 指令同步屏障指令。本库未使用。

## E

### EvilHookStubFunctionForIBored
示例用户回调，将 `regs->regs[9]`（X9）设为 `0x333`。

## F

### fixPCOpcodeArm
本库的 ARM 通用修复主循环，调用 `fixPCOpcodeArm64` 处理每条指令。

### fixPCOpcodeArm64
单条 ARM64 指令的修复分派。

### Fixed-Ops Area
修复后指令存放区域 = `pNewEntryForOldFunction`（malloc 200 字节）。

## G

### GAP (gap)
`B_COND_ARM64` 备份内分支时，目标指令与当前指令之间所有"修复后字节数"的累加值，用于计算正确的 B.cond 偏移。

### GPR (General Purpose Register)
X0–X30 共 31 个 64 位通用寄存器。本库 stub 保存全部 GPR。

### GetModuleBaseAddr
通过解析 `/proc/pid/maps` 获取模块加载基址。

## H

### HookArm
本库顶层编排函数（4 步）。

### hookstub_function_addr_s
汇编符号，stub 内的 8B 槽，存 `onCallBack` 地址。

### Hook point (hook_addr)
被改写为跳转指令的原函数入口。

## I

### InlineHook
公开 API。安装一个 inline hook。

### imm14 / imm19 / imm21 / imm26
ARM64 PC-relative 立即数字段位宽（分别对应 TBZ/CBZ/ADR/B）。

### INLINE_HOOK_INFO
本库核心数据结构，包含 hook 所有上下文。

### isTargetAddrInBackup
判断跳转目标是否在备份区间内。

## L

### LDR (literal)
ARM64 `LDR Rt, label` 从 PC-relative 加载常量。本库 `LDR_ARM64` 分支会展开为 `STP + LDR Xn + LDR [Xn,0] + LDR [sp,-8] + B + 双字` 模板。

### LDRSW (literal)
ARM64 有符号字加载。本库未单独处理，会落到 `LDR_ARM64_32`（与 `0x18000000`）同处理。

### lengthFixArm64 / lengthFixArm32
返回某条指令"修复后字节数"的预估函数。

## M

### ModifyIBored
示例 `__attribute__((constructor))` 函数，自动 hook `libhellojni.so + 0x600`。

### mmap
本库 `BuildOldFunction` 用 mmap 分配 4 KiB 修复缓冲区（**泄漏**）。

### MSR / MRS
ARM64 读写系统寄存器。本库 stub 用 `mrs x0, NZCV` / `msr NZCV, x0` 保存恢复标志位。

## N

### NZCV
ARM64 条件标志寄存器。stub 保存恢复它。

### NOP
`0xd503201f`。本库未直接生成 NOP。

## O

### OPCODEMAXLEN
宏 `= 24`（`Ihook.h:20`）。备份区字节数。

### old_function_addr_s
汇编符号，stub 内的 8B 槽，存 `pNewEntryForOldFunction` 地址。

### OTHER
本库 `fixPCOpcodeArm64` 的兜底分支，原样拷贝指令。CBZ/CBNZ/TBZ/TBNZ 等会落到这里。

## P

### pHookAddr
hook 目标地址（`INLINE_HOOK_INFO` 字段）。

### pStubShellCodeAddr
malloc 出的 stub 地址（`INLINE_HOOK_INFO` 字段）。

### pNewEntryForOldFunction
malloc 出的"修复后的旧函数入口"地址（`INLINE_HOOK_INFO` 字段）。

### PC-relative
以当前 PC 为基准寻址的指令。是 inline hook 的修复难点。

### PRFM
ARM64 预取指令。Rprop 库跳过，本库未涉及（UNDEFINE）。

### /proc/pid/maps
Linux 进程虚拟内存映射文件。本库 `GetModuleBaseAddr` 解析它。

## R

### RebuildHookTarget
本库 4 步编排的第 4 步，把 hook 点改写为 24B 长跳转。

### regs
本库 `user_pt_regs` 指针，由 stub 传给用户回调。

### Ret / RET
ARM64 函数返回指令 (`0xd65f03c0`)。本库未特殊处理。

## S

### Shellcode
本库 stub 的本质。

### STP / LDP
ARM64 存储 / 加载寄存器对。本库 stub 用 `stp X0..X29` 保存 GPR。

### stub
执行替换逻辑的代码段。本库的 stub = `_shellcode_start_s.._shellcode_end_s`。

## T

### TBZ / TBNZ
`Test Bit and Branch if Zero / Non-Zero`。本库未修复。

### Trampoline
蹦床，指向修复后原函数头。本库中 `pNewEntryForOldFunction` 即是。

### user_pt_regs
Linux 内核导出的用户态寄存器快照结构。`regs->regs[N]` 对应 X0-X30，`regs->sp` / `regs->pc` 对应 SP / PC。

## U

### UnInlineHook
公开 API。取消一个 inline hook。**已知 Bug**：未恢复原指令。

### UNDEFINE
`INSTRUCTION_TYPE` 中的兜底值，对应"未知指令类型"。

## V

### Vector (std::vector)
本库 `gs_vecInlineHookInfo` 用 `std::vector<INLINE_HOOK_INFO*>` 维护 hook 注册表。

### VMA (Virtual Memory Address)
虚拟内存地址，本库所有 PC 计算都是 VMA。

## X

### X0–X30
ARM64 通用寄存器。X29 是 FP，X30 是 LR。

### X9
示例回调 `EvilHookStubFunctionForIBored` 修改的寄存器。