# 08 · 函数详细说明（指令修复层 - fixPCOpcode.h / fixPCOpcode.c）

> 本文件覆盖 `jni/InlineHook/fixPCOpcode.h` + `jni/InlineHook/fixPCOpcode.c` 全部 8 个函数 + 1 个 enum。

---

## `enum INSTRUCTION_TYPE`
- **位置**: `fixPCOpcode.c:5-87`
- **值**:
  - ARM32: `BLX_ARM, BL_ARM, B_ARM, BEQ_ARM..BLE_ARM` (16 个条件分支), `BX_ARM, ADD_ARM, ADR1_ARM, ADR2_ARM, MOV_ARM, LDR_ARM`
  - ARM64: `ADR_ARM64, ADRP_ARM64, LDR_ARM64, B_ARM64, B_COND_ARM64, BR_ARM64, BL_ARM64, BLR_ARM64, CBNZ_ARM64, CBZ_ARM64, TBNZ_ARM64, TBZ_ARM64, LDR_ARM64_32`
  - `UNDEFINE` (兜底)
- **简要说明**: 统一枚举 ARM32 + ARM64 指令类型。`fixPCOpcodeArm64` 只 case 部分类型，其余落到 UNDEFINE。

---

## `lengthFixArm64`
- **签名**: `int lengthFixArm64(uint32_t opcode)`
- **位置**: `fixPCOpcode.h:11`（声明）/ `fixPCOpcode.c:89-120`（定义）
- **可见性**: 普通 extern
- **参数**: `opcode` —— 一条 ARM64 指令
- **返回值**: `int` —— 修复后字节数
- **调用**: 被 `InitArmHookInfo` (`Ihook.c:133`) 调用 6 次
- **调用了**: `getTypeInArm64` (`fixPCOpcode.c:92`)
- **返回值表**:

| 类型 | 返回字节数 |
|------|----------|
| `B_COND_ARM64` | 32 |
| `BEQ_ARM..BLE_ARM` (ARM32 条件) | 12 |
| `BLX_ARM, BL_ARM` | 12 |
| `B_ARM, BX_ARM` | 8 |
| `ADD_ARM` | 24 |
| `ADR1_ARM, ADR2_ARM, LDR_ARM, MOV_ARM` | 12 |
| `UNDEFINE` | 4 |

> **注意**：返回表里**未列出** `B_ARM64, BL_ARM64, ADR_ARM64, ADRP_ARM64, LDR_ARM64, CBZ/CBNZ/TBZ/TBNZ`，但 switch case 也没有对应分支——这些指令会落到 default（无 case），实际会触发**未定义行为**或被编译为"非 B_COND"路径。当前 `InitArmHookInfo` 调用的 `lengthFixArm64` 对大多数 ARM64 指令实际不可靠。

---

## `lengthFixArm32`
- **签名**: `int lengthFixArm32(uint32_t opcode)`
- **位置**: `fixPCOpcode.c:123-154`（定义）
- **可见性**: 普通 extern
- **参数**: `opcode`
- **返回值**: `int`
- **调用**: 被 `InitArmHookInfo` (`Ihook.c:132`) 调用一次（**死代码**，因为结果被忽略）
- **调用了**: `getTypeInArm32` (`fixPCOpcode.c:126`)
- **简要说明**: 同 `lengthFixArm64` 但针对 ARM32 指令。结果未被使用——`InitArmHookInfo` 行 132 调用但丢弃返回值，行 133 才是真正写入 `backUpFixLengthList`。

---

## `getTypeInArm64`
- **签名**: `static int getTypeInArm64(uint32_t instruction)`
- **位置**: `fixPCOpcode.h:13`（声明，static）/ `fixPCOpcode.c:158-199`（定义）
- **可见性**: `static`（文件作用域）
- **参数**: `instruction` —— 一条指令的 32 位编码
- **返回值**: `int` —— `INSTRUCTION_TYPE` 中的一个
- **调用**: 被 `lengthFixArm64` (`:92`) 和 `fixPCOpcodeArm64` (`:413`) 调用
- **调用了**: `__android_log_print` (`:160`)
- **类型识别 mask**:

| 指令类型 | 匹配 mask | 期望值 |
|---------|----------|--------|
| `ADR_ARM64` | `0x9F000000` | `0x10000000` |
| `ADRP_ARM64` | `0x9F000000` | `0x90000000` |
| `B_ARM64` | `0xFC000000` | `0x14000000` |
| `B_COND_ARM64` | `0xFF000010` | `0x54000010` |
| `BL_ARM64` | `0xFC000000` | `0x94000000` |
| `LDR_ARM64` (literal 64) | `0xFF000000` | `0x58000000` |
| `CBNZ_ARM64` | `0x7F000000` | `0x35000000` |
| `CBZ_ARM64` | `0x7F000000` | `0x34000000` |
| `TBNZ_ARM64` | `0x7F000000` | `0x37000000` |
| `TBZ_ARM64` | `0x7F000000` | `0x36000000` |
| `LDR_ARM64_32` | `0xFF000000` | `0x18000000` |

---

## `getTypeInArm32`
- **签名**: `static int getTypeInArm32(uint32_t instruction)`
- **位置**: `fixPCOpcode.h:14`（声明，static）/ `fixPCOpcode.c:201-283`（定义）
- **可见性**: `static`
- **参数**: `instruction`
- **返回值**: `int`
- **调用**: 被 `lengthFixArm32` (`:126`) 调用
- **调用了**: `__android_log_print` (`:203`)
- **简要说明**: ARM32 指令分类。本项目仅 ARM64，但代码保留 ARM32 兼容。

---

## `isTargetAddrInBackup`
- **签名**: `bool isTargetAddrInBackup(uint64_t target_addr, uint64_t hook_addr, int backup_length)`
- **位置**: `fixPCOpcode.h:9`（声明）/ `fixPCOpcode.c:287-292`（定义）
- **可见性**: 普通 extern
- **参数**:
  - `target_addr`: 跳转目标绝对地址
  - `hook_addr`: hook 点地址
  - `backup_length`: 备份长度
- **返回值**: `bool` —— `[hook_addr, hook_addr + backup_length]` 闭区间包含
- **调用**: 被 `fixPCOpcodeArm64` 的 `B_COND_ARM64` 路径 (`:433`) 调用
- **调用了**: 无
- **简要说明**: 判断跳转目标是否在备份区间内（决定走 backup-to-backup 或 backup-to-outside 分支）。

---

## `fixPCOpcodeArm`
- **签名**: `int fixPCOpcodeArm(void *fixOpcodes, INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `fixPCOpcode.h:16`（声明）/ `fixPCOpcode.c:294-395`（定义）
- **可见性**: 普通 extern
- **参数**:
  - `fixOpcodes`: 输出缓冲区（mmap 的 PAGE）
  - `pstInlineHook`
- **返回值**: `int` —— 写入 fixOpcodes 的总字节数（fixPos）
- **副作用**:
  - 在 fixOpcodes 头部写 `LDR X0, [sp, #-0x8]` (4 字节, 恢复被 hook 跳转覆盖的 X0)
  - 循环 6 次调用 `fixPCOpcodeArm64`，把每条原指令的修复版本拼到 fixOpcodes
  - **不释放** fixOpcodes（泄漏 4 KiB）
- **调用**: 被 `BuildOldFunction` (`Ihook.c:301`) 调用
- **调用了**: `fixPCOpcodeArm64` (`:331`), `memcpy` (`:323`, `:334`), `__android_log_print` (多处)
- **简要说明**: ARM 通用修复主循环。**注意**：行 311 `LOGI("sizeof(uint8_t) : %D", sizeof(uint8_t))` 是格式串错误（应为 `%d`），编译会警告。

### 算法流程

```c
fixOpcodes[0] = 0xf85f83e0;  // LDR X0, [sp, #-0x8] (4 字节)
fixPos = 4;
backUpPos = 0;
pc = pHookAddr;
while (backUpPos < backUpLength) {
    offset = fixPCOpcodeArm64(pc, lr, *currentOpcode, tmpFixOpcodes, pstInlineHook);
    memcpy(fixOpcodes + fixPos, tmpFixOpcodes, offset);
    backUpPos += 4;
    pc += 4;
    fixPos += offset;
    currentOpcode += 1;
}
return fixPos;
```

---

## `fixBcond`
- **签名**: `int fixBcond(uint64_t pc, uint64_t lr, uint32_t instruction, uint32_t *trampoline_instructions, INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `fixPCOpcode.c:397-400`（定义）
- **可见性**: 普通 extern（h 无声明）
- **参数**: 同 `fixPCOpcodeArm64`
- **返回值**: `int`
- **副作用**: 无（函数体为空）
- **调用**: 无（**死代码**，搜索未发现调用方）
- **简要说明**: 空实现。作者预留的位置，未完成。

---

## `fixPCOpcodeArm64`
- **签名**: `int fixPCOpcodeArm64(uint64_t pc, uint64_t lr, uint32_t instruction, uint32_t *trampoline_instructions, INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `fixPCOpcode.h:18`（声明）/ `fixPCOpcode.c:402-593`（定义）
- **可见性**: 普通 extern
- **参数**:
  - `pc`: 当前指令的 PC 值
  - `lr`: 备份区间结束的地址 (pHookAddr + 24)
  - `instruction`: 当前指令
  - `trampoline_instructions`: 输出缓冲区（`uint32_t[40]`，由 `fixPCOpcodeArm` 分配）
  - `pstInlineHook`
- **返回值**: `int` —— 写入 trampoline 的字节数
- **副作用**: 修改 trampoline_instructions
- **调用**: 被 `fixPCOpcodeArm` (`fixPCOpcode.c:331`) 调用
- **调用了**: `getTypeInArm64` (`:413`), `isTargetAddrInBackup` (`:433`), `__android_log_print` (多处)
- **简要说明**: 单条 ARM64 指令的修复主入口，按类型分派。

### 分派表

| `getTypeInArm64` 返回 | 处理分支 | 字节数 | 行号 |
|---------------------|---------|--------|------|
| `B_COND_ARM64` | 备份内: B.XX (gap+32) + B 28<br>备份外: B.anti_cond 32 + target_ins + STP + LDR + BR + B 8 + 双字 | 8 / 32 | `:416-461` |
| `ADR_ARM64` | LDR Rd, 4 + 双字 | 12 | `:462-484` |
| `ADRP_ARM64` | LDR Rd, 8 + B 12 + 双字 | 16 | `:485-514` |
| `LDR_ARM64` | STP Xt,Xn + LDR Xn,16 + LDR Xt,[Xn,0] + LDR Xn,[sp,-8] + B 8 + 双字 | 28 | `:515-552` |
| `B_ARM64` | STP X0,X0 + LDR X0,16 + target_ins + BR X0 + B 8 + 双字 | 28 | `:553-582` |
| **其它 (CBZ/CBNZ/TBZ/TBNZ/UNDEFINE)** | 原样拷贝 | 4 | `:583-587` |

### 详细指令编码

#### B_COND_ARM64 备份内分支（行 `:441-446`）

```c
int target_idx = (int)((value - hook_addr) / 4);    // 目标指令序号
int bc_ins_idx = (int)((pc - hook_addr) / 4);       // 当前指令序号
int gap = 0;
for (idx = bc_ins_idx + 1; idx < target_idx; idx++) {
    gap += backUpFixLengthList[idx];   // 累加中间指令的修复后字节数
}
trampoline[pos++] = (instruction & 0xff00000f) | ((gap + 32) << 3);  // B.XX (gap+32)
trampoline[pos++] = 0x14000007;  // B 28
```

#### ADR_ARM64（行 `:478-483`）

```c
uint32_t imm21 = ((instruction & 0xFFFFE0) >> 3) + ((instruction & 0x60000000) >> 29);
uint64_t value = pc + 4 * imm21;
if ((imm21 & 0x100000) == 0x100000) value = pc - 4 * (0x1fffff - imm21 + 1);  // 符号扩展

uint32_t rd = instruction & 0x1f;
trampoline[pos++] = 0x58000020 + rd;          // LDR Rd, 4
trampoline[pos++] = (uint32_t)(value >> 32);  // 高 32 位
trampoline[pos++] = (uint32_t)(value & 0xffffffff);  // 低 32 位
```

#### LDR_ARM64（行 `:527-551`）

```c
uint32_t rt = instruction & 0x1f;
int rn;
for (i = 0; i < 31; i++) {        // 找一个不等于 rt 的临时寄存器
    if (i != rt) { rn = i; break; }
}
uint32_t imm19 = (instruction & 0xFFFFE0) >> 5;
trampoline[pos++] = 0xa93f03e0 + rt + (rn << 10);       // STP Xt, Xn, [SP, #-0x10]
trampoline[pos++] = 0x58000080 + rn;                    // LDR Xn, 16
trampoline[pos++] = 0xf9400000 + (rn << 5);             // LDR Xt, [Xn, 0]
trampoline[pos++] = 0xf85f83e0 + rn;                    // LDR Xn, [sp, #-0x8]
trampoline[pos++] = 0x14000002;                         // B 8
trampoline[pos++] = (uint32_t)(value >> 32);
trampoline[pos++] = (uint32_t)(value & 0xffffffff);
```

> **隐患**：`for (i = 0; i < 31; i++) if (i != rt) { rn = i; break; }` 当 rt=0 时 rn=1，但 rt=1 时 rn=0（看似无冲突）；但若 rt=30，rn=0 → 后续 STP 会破坏 X0 的旧值。这个临时寄存器选择**没有考虑 X0 可能正在被 hook 跳转使用**。

#### 关键指令编码速查

| 助记符 | 编码 | 说明 |
|--------|------|------|
| `NOP` | `0xd503201f` | - |
| `LDR Rd, #4` | `0x58000020 + rd` | 加载 PC+8 处的 8 字节 |
| `LDR Rd, #8` | `0x58000040 + rd` | 加载 PC+8 处的 8 字节 |
| `LDR Rd, #12` | `0x58000060 + rd` | 加载 PC+12 处的 8 字节 |
| `LDR Rd, #16` | `0x58000080 + rd` | 加载 PC+16 处的 8 字节 |
| `BR Xn` | `0xd61f0000` | 间接跳转 |
| `B #8` | `0x14000002` | 跳过 8 字节 |
| `B #12` | `0x14000003` | 跳过 12 字节 |
| `B #28` | `0x14000007` | 跳过 28 字节 |
| `B #32` | `0x14000008` | 跳过 32 字节 |
| `STP X0, X0, [SP, #-0x10]` | `0xa93f03e0` | 默认占位 STP |
| `LDR X0, [SP, -0x8]` | `0xf85f83e0` | 恢复 X0 |
| `LDR X0, [Xn, 0]` | `0xf9400000 + (rn << 5)` | 间接加载 |