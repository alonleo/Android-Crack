# 10 · 术语表

> 涵盖 ARMv8-A 架构、inline hook、PC-relative 修复等术语。

## A

### A64
ARM64（AArch64）的简称。寄存器宽 64 位，指令固定 32 位。

### AArch64
ARMv8-A 的 64 位执行状态，And64InlineHook 的目标平台。

### ADRP
`ADRP Rd, label`：加载当前 PC 页 + label 的页基址到 Rd。是 page-aligned 的 ADR。

### ADR
`ADR Rd, label`：加载 PC + label（±1 MiB）到 Rd。

### A64_NOP
本库的 NOP 指令编码常量 `0xd503201f`。

### ARMv8.0
本库完全支持。ARMv8.5+ 的 BTI / PAC / MTE 不支持。

## B

### B (Branch)
无条件相对跳转，imm26 字段编码 ±128 MiB 偏移（以指令为单位）。

### BL (Branch with Link)
类似 B，但把 PC+4 写入 X30 (LR)。

### B.cond
条件分支，imm19 编码 ±1 MiB。

### BTI (Branch Target Identification)
ARMv8.5 引入的跳转目标合法性检查指令。本库**不兼容**。

### Bypass
绕过原函数头 4-5 条指令直接跳到 trampoline 的语义。

## C

### CAS (Compare-And-Swap)
本库用 `__sync_bool_compare_and_swap` 原子写 hook 点（仅近跳转分支）。

### CBNZ / CBZ
`Compare and Branch on Non-Zero / Zero`，PC-relative ±1 MiB。

### Cache flush
本库用 `__builtin___clear_cache(start, end)` 清指令缓存。

### context
本库的修复工作台结构体，含 `basep/endp/dat[]/fmap[]`。

## D

### DPR (Data Processing - Register)
非 PC-relative 数据处理指令，本库原样拷贝不修复。

## E

### ERET
异常返回指令，本库不涉及。

## F

### fix_info
`context` 内的子结构，登记延迟回填字段 `{bp, ls, ad}`。

### Forward reference
前向引用：本条指令跳转到尚未处理的备份内指令，需延迟回填。

### fmap
`insns_info` 内 `fix_info[A64_MAX_REFERENCES]` 数组。

## G

### GPR (General Purpose Register)
X0–X30 共 31 个 64 位通用寄存器。

## H

### hook point
被改写为跳转指令的原函数入口（4 或 20 字节）。

### Hot patch
运行时改写可执行代码。

## I

### Inline hook
通过改写函数头几条指令实现劫持，无需 PLT/GOT。

### imm14 / imm19 / imm21 / imm26
PC-relative 立即数字段位宽（分别对应 TBZ/CBZ/ADR/B）。

### instruction (typedef)
本库定义 `uint32_t *__restrict *__restrict`，是"指针的指针"，传给 fix 函数用于读写 inp/outp。

### insns_info
`context` 内的子结构，登记每条原指令的输出位置和回填槽。

### is_in_fixing_range
判断跳转目标是否落在备份区间内（本库用 `[basep, endp)` 半开区间）。

## L

### LDR (literal)
`LDR Rt, label`：`Rt = *(PC + signext(imm19) * 4)`，从 PC-relative 地址加载 32/64 位数据。

### LDRSW (literal)
`LDRSW Xt, label`：加载 32 位有符号数到 64 位寄存器。

## M

### mprotect
修改内存页属性为 `PROT_READ | PROT_WRITE | PROT_EXEC`，本库用此使代码页可写。

### mmap
创建匿名可执行内存区域。本库**不**使用 mmap（静态池代替）。

## N

### NOP
No Operation，本库用 `0xd503201f`。

## P

### PC-relative
以当前 PC 为基准寻址的指令（AArch64 大量使用），是 inline hook 的修复难点。

### PRFM
`Prefetch Memory`，本库在 `__fix_loadlit` 中跳过。

### PAC (Pointer Authentication)
ARMv8.3+ 的指针签名机制。本库**不兼容** PAC 指针。

### PC-relative load
即 `LDR (literal)`。

### Pool
`__insns_pool`：256 × 50 uint32 的静态 trampoline 槽位池。

## R

### RWX
`PROT_READ | PROT_WRITE | PROT_EXEC`，可读写执行内存。

### Relocation
链接器在 ELF 加载时对 PC-relative 指令的重定位。本库的修复发生在 relocation 之后。

### reset_current_ins
在插入 NOP 后更新 `dat[idx].insp`。

## S

### Short branch / Long branch
近跳转（`B`，4 字节）/ 远跳转（`LDR+BR+addr`，20 字节）。本库按 PC 偏移自动选择。

### Stub
执行替换逻辑的短代码段。本库的 stub 即 `replace` 函数本身。

### Shellcode
本项目 B（GToad）使用，本项目（A）不使用此术语。

### Sign-extend
符号扩展，imm26 / imm19 / imm21 在 PC-relative 计算时需先符号扩展到 64 位。

## T

### TBZ / TBNZ
`Test Bit and Branch if Zero / Non-Zero`，PC-relative ±32 KiB。

### Trampoline
蹦床，本库指静态池里保存原函数头 1-5 条修复指令的缓冲区。

### TLS (Thread-Local Storage)
本库无 TLS 依赖，但全局 `__index` 在多线程并发分配时是安全的。

## U

### Unhook
撤销 inline hook。本库**不支持**。

## V

### VMA (Virtual Memory Address)
虚拟内存地址，本库所有 PC 计算都是 VMA。

### Visibility
`__attribute__((visibility("default")))` 让符号在 .so 中默认导出。

## Z

### Zero-page
地址 0 附近。本库的 `new_pc_offset` 比较用 `llabs()` 避免整数下溢。