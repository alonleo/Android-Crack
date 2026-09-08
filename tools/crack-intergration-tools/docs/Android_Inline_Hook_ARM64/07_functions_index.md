# 07 · 函数索引总表

> 项目内全部函数 / 全局符号清单。详见 `08_functions_detail/`。

## 7.1 公开 API（`Interface/InlineHook.cpp`）

| 函数 | 签名 | 行号 |
|------|------|------|
| `before_main` | `void ()` (`__attribute__((constructor))`) | `:26-28` |
| `InlineHook` | `bool (void *pHookAddr, void (*onCallBack)(struct user_pt_regs *))` | `:36-60` |
| `UnInlineHook` | `bool (void *pHookAddr)` | `:67-100` |
| `EvilHookStubFunctionForIBored` | `void (user_pt_regs *regs)` | `:107-112` |
| `ModifyIBored` | `void ()` (`__attribute__((constructor))`) | `:117-135` |

## 7.2 库层 API（`InlineHook/Ihook.h` 声明 / `Ihook.c` 实现）

| 函数 | 签名 | 声明行 | 定义行 |
|------|------|--------|--------|
| `ChangePageProperty` | `bool (void *pAddress, size_t size)` | `:54` | `Ihook.c:12-42` |
| `GetModuleBaseAddr` | `void *(pid_t pid, char *pszModuleName)` | `:56` | `Ihook.c:50-101` |
| `InitArmHookInfo` | `bool (INLINE_HOOK_INFO *pstInlineHook)` | `:58` | `Ihook.c:108-138` |
| `BuildStub` | `bool (INLINE_HOOK_INFO *pstInlineHook)` | `:60` | `Ihook.c:145-198` |
| `BuildArmJumpCode` | `bool (void *pCurAddress, void *pJumpAddress)` | `:62` | `Ihook.c:207-253` |
| `BuildOldFunction` | `bool (INLINE_HOOK_INFO *pstInlineHook)` | `:64` | `Ihook.c:263-322` |
| `RebuildHookTarget` | `bool (INLINE_HOOK_INFO *pstInlineHook)` | `:66` | `Ihook.c:331-364` |
| `HookArm` | `bool (INLINE_HOOK_INFO *pstInlineHook)` | `:68` | `Ihook.c:372-433` |

## 7.3 修复函数（`InlineHook/fixPCOpcode.h` 声明 / `.c` 实现）

| 函数 | 签名 | 声明行 | 定义行 |
|------|------|--------|--------|
| `isTargetAddrInBackup` | `bool (uint64_t target_addr, uint64_t hook_addr, int backup_length)` | `:9` | `fixPCOpcode.c:287-292` |
| `lengthFixArm64` | `int (uint32_t opcode)` | `:11` | `fixPCOpcode.c:89-120` |
| `lengthFixArm32` | `int (uint32_t opcode)` | (无声明) | `fixPCOpcode.c:123-154` |
| `getTypeInArm64` | `static int (uint32_t instruction)` | `:13` | `fixPCOpcode.c:158-199` |
| `getTypeInArm32` | `static int (uint32_t instruction)` | `:14` | `fixPCOpcode.c:201-283` |
| `fixPCOpcodeArm` | `int (void *fixOpcodes, INLINE_HOOK_INFO *pstInlineHook)` | `:16` | `fixPCOpcode.c:294-395` |
| `fixBcond` | `int (pc, lr, instruction, trampoline, pstInlineHook)` | (无声明, 死代码) | `fixPCOpcode.c:397-400` |
| `fixPCOpcodeArm64` | `int (uint64_t pc, uint64_t lr, uint32_t instruction, uint32_t *trampoline, INLINE_HOOK_INFO *pstInlineHook)` | `:18` | `fixPCOpcode.c:402-593` |

## 7.4 汇编全局符号（`ihookstub.s`）

| 符号 | 类型 | 行号 | 作用 |
|------|------|------|------|
| `_shellcode_start_s` | `.global` 标签 | `:8` | stub 起始 |
| `_hookstub_function_addr_s` | `.global` 标签 | `:40` | 8-byte 槽, 存 onCallBack 地址 |
| `_old_function_addr_s` | `.global` 标签 | `:71` | 8-byte 槽, 存 pNewEntryForOldFunction 地址 |
| `_shellcode_end_s` | `.global` 标签 | `:80` | stub 结束 |

## 7.5 宏（预处理期）

| 宏 | 位置 | 作用 |
|----|------|------|
| `OPCODEMAXLEN` | `Ihook.h:20` | 备份区大小 = 24 |
| `BACKUP_CODE_NUM_MAX` | `Ihook.h:21` | 最多备份指令数 = 6 |
| `PAGE_START(addr)` | `Ihook.h:26` | `~(PAGE_SIZE-1) & addr` |
| `SET_BIT0(addr)` | `Ihook.h:27` | `addr | 1` |
| `CLEAR_BIT0(addr)` | `Ihook.h:28` | `addr & ~1` |
| `TEST_BIT0(addr)` | `Ihook.h:29` | `addr & 1` |
| `ACTION_ENABLE` / `ACTION_DISABLE` | `Ihook.h:31-32` | 0 / 1（未在代码中使用） |
| `BYTE` | `Ihook.h:17` | `unsigned char` |
| `LOG_TAG` | `Ihook.h:23` | `"GToad"` |
| `LOGI(fmt, args...)` | `Ihook.h:24` | `__android_log_print(INFO, "GToad", ...)` |
| `ALIGN_PC(pc)` | `Ihook.c:4`, `fixPCOpcode.h:7` | `pc & 0xFFFFFFFC` |

## 7.6 数据结构

| 类型 | 定义 | 行号 |
|------|------|------|
| `INLINE_HOOK_INFO` | `struct tagINLINEHOOKINFO` | `Ihook.h:43-52` |
| `INSTRUCTION_TYPE` | `enum` | `fixPCOpcode.c:5-87` |

## 7.7 全局变量

| 符号 | 类型 | 行号 | 作用 |
|------|------|------|------|
| `gs_vecInlineHookInfo` | `static std::vector<INLINE_HOOK_INFO*>` | `InlineHook.cpp:24` | hook 注册表 |

## 7.8 文件统计

| 文件 | 总行数 | 函数 / 全局符号条目 |
|------|--------|------------------|
| `InlineHook/Ihook.h` | 71 | 8 函数声明 + 9 宏 + 1 结构体 |
| `InlineHook/Ihook.c` | 435 | 8 函数 + 1 宏 |
| `InlineHook/fixPCOpcode.h` | 21 | 6 函数声明 + 1 宏 |
| `InlineHook/fixPCOpcode.c` | 594 | 8 函数 + 1 enum |
| `InlineHook/ihookstub.s` | 82 | 4 全局标签 |
| `Interface/InlineHook.cpp` | 135 | 5 函数 + 1 vector |
| 合计 | 1338 | 35 函数 + 4 标签 + 16 宏 + 1 enum + 1 struct + 1 vector |