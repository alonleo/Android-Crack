# 09 · 关键调用栈汇总

## 9.1 完整 Hook 调用栈（`InlineHook` 主入口）

```
[user / __attribute__((constructor)) ModifyIBored]
 └─ InlineHook(pHookAddr, onCallBack)                              Interface/InlineHook.cpp:36
     ├─ LOGI("InlineHook")                                         Interface/InlineHook.cpp:39
     ├─ new INLINE_HOOK_INFO                                       Interface/InlineHook.cpp:46
     ├─ HookArm(pstInlineHook)                                     Interface/InlineHook.cpp:50
     │   ├─ InitArmHookInfo(pstInlineHook)                         InlineHook/Ihook.c:108
     │   │   ├─ LOGI("...")                                        InlineHook/Ihook.c:116, 131-132
     │   │   ├─ memcpy(szbyBackupOpcodes, pHookAddr, 24)           InlineHook/Ihook.c:127
     │   │   ├─ lengthFixArm64(opcode[i]) × 6                      InlineHook/Ihook.c:133
     │   │   │   └─ getTypeInArm64(opcode)                         InlineHook/fixPCOpcode.c:158
     │   │   └─ lengthFixArm32(opcode[i]) × 6 (死代码)             InlineHook/Ihook.c:132
     │   │       └─ getTypeInArm32(opcode)                         InlineHook/fixPCOpcode.c:201
     │   │
     │   ├─ BuildStub(pstInlineHook)                               InlineHook/Ihook.c:145
     │   │   ├─ sShellCodeLength = _shellcode_end_s - _shellcode_start_s   InlineHook/Ihook.c:162
     │   │   ├─ pNewShellCode = malloc(sShellCodeLength)           InlineHook/Ihook.c:164
     │   │   ├─ ChangePageProperty(pNewShellCode, sShellCodeLength, RWX)   InlineHook/Ihook.c:172
     │   │   │   ├─ sysconf(_SC_PAGESIZE)                          InlineHook/Ihook.c:23
     │   │   │   └─ mprotect(...) × N                               InlineHook/Ihook.c:32
     │   │   ├─ memcpy(pNewShellCode, _shellcode_start_s, sShellCodeLength)   InlineHook/Ihook.c:170
     │   │   ├─ *ppHookStubFunctionAddr = onCallBack               InlineHook/Ihook.c:181
     │   │   ├─ ppOldFuncAddr = pNewShellCode + (_old_function_addr_s - _shellcode_start_s)   InlineHook/Ihook.c:186
     │   │   └─ pStubShellCodeAddr = pNewShellCode                 InlineHook/Ihook.c:189
     │   │
     │   ├─ BuildOldFunction(pstInlineHook)                        InlineHook/Ihook.c:263
     │   │   ├─ fixOpcodes = mmap(NULL, PAGE_SIZE, RWX, ANON|PRIVATE)  InlineHook/Ihook.c:271
     │   │   ├─ pNewEntryForOldFunction = malloc(200)              InlineHook/Ihook.c:283
     │   │   ├─ ChangePageProperty(pNewEntryForOldFunction, 200, RWX)   InlineHook/Ihook.c:294
     │   │   ├─ fixLength = fixPCOpcodeArm(fixOpcodes, pstInlineHook)   InlineHook/Ihook.c:301
     │   │   │   ├─ fixOpcodes[0] = LDR X0, [sp, #-0x8]            InlineHook/fixPCOpcode.c:321
     │   │   │   └─ loop: 6 × fixPCOpcodeArm64                      InlineHook/fixPCOpcode.c:331
     │   │   │       ├─ getTypeInArm64(instruction)                 InlineHook/fixPCOpcode.c:413
     │   │   │       ├─ isTargetAddrInBackup(...)                   InlineHook/fixPCOpcode.c:433 (B_COND only)
     │   │   │       └─ 输出 trampoline_instructions (4-32 字节)    InlineHook/fixPCOpcode.c:416-587
     │   │   ├─ memcpy(pNewEntryForOldFunction, fixOpcodes, fixLength)   InlineHook/Ihook.c:302
     │   │   ├─ BuildArmJumpCode(pNewEntryForOldFunction + fixLength,
     │   │   │                  pHookAddr + backUpLength - 4)      InlineHook/Ihook.c:306
     │   │   │   └─ memcpy(pCurAddress, szLdrPCOpcodes, 24)        InlineHook/Ihook.c:242
     │   │   └─ *ppOldFuncAddr = pNewEntryForOldFunction           InlineHook/Ihook.c:313
     │   │
     │   └─ RebuildHookTarget(pstInlineHook)                       InlineHook/Ihook.c:331
     │       ├─ ChangePageProperty(pHookAddr, 24, RWX)             InlineHook/Ihook.c:345
     │       └─ BuildArmJumpCode(pHookAddr, pStubShellCodeAddr)    InlineHook/Ihook.c:352
     │           └─ memcpy(pHookAddr, szLdrPCOpcodes, 24)           InlineHook/Ihook.c:242
     │
     ├─ (失败) delete pstInlineHook                                 Interface/InlineHook.cpp:53
     └─ (成功) gs_vecInlineHookInfo.push_back(pstInlineHook)        Interface/InlineHook.cpp:58
```

## 9.2 运行时调用栈（被 hook 的函数被调用）

```
[Caller]
 └─ bl target_function
     └─ target_function (hook 点, 24B 已改写)
         └─ STP X1, X0, [SP, #-0x10]            ihookstub.s 入口前的 hook 跳转
             LDR X0, 8                          (BuildArmJumpCode 写入的 24B)
             BR X0
             [8-byte pStubShellCodeAddr]
             LDR X0, [SP, #-0x8]
         └─ [stub shellcode @ pStubShellCodeAddr]   ihookstub.s:8
             ├─ sub sp, sp, #0x20                ihookstub.s:10
             ├─ mrs x0, NZCV                     ihookstub.s:12
             ├─ str x0, [sp, #0x10]              ihookstub.s:13
             ├─ str x30, [sp]                    ihookstub.s:14
             ├─ add x30, sp, #0x20               ihookstub.s:15
             ├─ str x30, [sp, #0x8]              ihookstub.s:16
             ├─ ldr x0, [sp, #0x18]              ihookstub.s:17 (dead)
             ├─ sub sp, sp, #0xf0                ihookstub.s:19
             ├─ stp X0..X29 (15 对, 240B)        ihookstub.s:20-34
             ├─ mov x0, sp                      ihookstub.s:36
             ├─ ldr x3, 8                       ihookstub.s:37
             ├─ b 12                            ihookstub.s:38
             └─ [8-byte onCallBack @ _hookstub_function_addr_s]   ihookstub.s:40-41
                 └─ blr x3                      ihookstub.s:43
                     └─ [onCallBack(regs)]      user code
                         ├─ 读/写 regs->regs[N]
                         └─ return
             ├─ ldr x0, [sp, #0x100]            ihookstub.s:44
             ├─ msr NZCV, x0                    ihookstub.s:45
             ├─ ldp X0..X29 (15 对, 240B)        ihookstub.s:47-61
             ├─ add sp, sp, #0xf0               ihookstub.s:62
             ├─ ldr x30, [sp]                   ihookstub.s:64
             ├─ add sp, sp, #0x20               ihookstub.s:65
             ├─ stp X1, X0, [SP, #-0x10]        ihookstub.s:67
             ├─ ldr x0, 8                       ihookstub.s:68
             ├─ b 12                            ihookstub.s:69
             └─ [8-byte pNewEntryForOldFunction @ _old_function_addr_s]   ihookstub.s:71-72
                 └─ br x0                       ihookstub.s:74
                     └─ [pNewEntryForOldFunction]
                         ├─ LDR X0, [sp, #-0x8]  fixPCOpcodeArm 头部 (fixPCOpcode.c:321)
                         ├─ <修复后 insn 0>      fixPCOpcodeArm64 输出
                         ├─ <修复后 insn 1>
                         ├─ ...
                         ├─ <修复后 insn 5>
                         ├─ LDR X17, 8           BuildArmJumpCode
                         ├─ BR X17
                         └─ [8-byte pHookAddr + 24]
                             └─ 原函数剩余部分 (pHookAddr + 24)
                                 └─ ...
                                 └─ return
```

## 9.3 UnInlineHook 调用栈

```
[user]
 └─ UnInlineHook(pHookAddr)                                    Interface/InlineHook.cpp:67
     ├─ LOGI  (无)
     ├─ gs_vecInlineHookInfo.begin/end                         Interface/InlineHook.cpp:76-77
     ├─ for 循环查找匹配项                                     Interface/InlineHook.cpp:79-97
     │   ├─ pTargetInlineHookInfo = *itr
     │   ├─ gs_vecInlineHookInfo.erase(itr)                    Interface/InlineHook.cpp:85
     │   ├─ delete pTargetInlineHookInfo->pStubShellCodeAddr   Interface/InlineHook.cpp:88
     │   ├─ delete *(pTargetInlineHookInfo->ppOldFuncAddr)     Interface/InlineHook.cpp:92
     │   └─ delete pTargetInlineHookInfo                       Interface/InlineHook.cpp:94
     └─ return true
```

## 9.4 调用栈矩阵

| 入口 | 主要栈深 | 文件:行 |
|------|---------|---------|
| `InlineHook` | 5 (API → HookArm → Init/Stub/Old/Rebuild → ChangePageProperty → mprotect) | `Interface/InlineHook.cpp:36 → Ihook.c:372 → 145 → 12 → sys/mman` |
| `HookArm` | 5 (HookArm → 4 步 → 各步 helper) | `Ihook.c:372 → 389/399/410/420 → 各种` |
| `BuildStub` | 4 (BuildStub → ChangePageProperty → sysconf → mprotect) | `Ihook.c:145 → 172 → 23 → 32` |
| `BuildOldFunction` | 6 (BuildOldFunction → fixPCOpcodeArm → fixPCOpcodeArm64 → getTypeInArm64 → LOGI → __android_log_print) | `Ihook.c:263 → fixPCOpcode.c:294 → 331 → 158 → 160 → liblog` |
| `RebuildHookTarget` | 4 (Rebuild → BuildArmJumpCode → memcpy → __android_log_print) | `Ihook.c:331 → 207 → 242 → liblog` |
| `fixPCOpcodeArm` | 2 (Arm → Arm64) | `fixPCOpcode.c:294 → 331` |
| `fixPCOpcodeArm64` | 3 (Arm64 → getTypeInArm64 + isTargetAddrInBackup + LOGI) | `fixPCOpcode.c:402 → 413/433 + 408/412/etc.` |
| `UnInlineHook` | 1 (vector 遍历 + delete ×3) | `Interface/InlineHook.cpp:67 → 79-97` |

## 9.5 关键数据流反向引用

设 hook 点为 `pHookAddr`，原函数头 6 条指令：

```
insn[0] = ADR X0, some_label        ← ADR_ARM64
insn[1] = ADD X1, X0, #1            ← default (其他)
insn[2] = B somewhere              ← B_ARM64
insn[3] = LDR X2, other_label       ← LDR_ARM64
insn[4] = CBZ X2, somewhere2       ← CBZ_ARM64 (落到 OTHER 分支, 原样拷贝)
insn[5] = RET                      ← UNDEFINE (落到 OTHER 分支, 原样拷贝)
```

`BuildOldFunction` → `fixPCOpcodeArm` 流程：

```
fixOpcodes[0] = 0xf85f83e0 (LDR X0, [sp, #-0x8])      fixPCOpcode.c:321
fixPos = 4

# iter 1: insn[0] ADR_ARM64
fixPCOpcodeArm64 → ADR 分支
trampoline[0] = LDR X0, 4 (0x58000020 + 0 = 0x58000020)
trampoline[1] = value >> 32
trampoline[2] = value & 0xffffffff
memcpy(fixOpcodes+4, trampoline, 12)
fixPos = 16

# iter 2: insn[1] ADD X1, X0, #1 (OTHER)
fixPCOpcodeArm64 → OTHER 分支
trampoline[0] = 0x91000401 (原样)
memcpy(fixOpcodes+16, trampoline, 4)
fixPos = 20

# iter 3: insn[2] B_ARM64 → 备份外分支
fixPCOpcodeArm64 → B_ARM64 分支
trampoline[0] = STP X0,X0 (0xa93f03e0)
trampoline[1] = LDR X0, 16 (0x58000080)
trampoline[2] = *value (目标 insn)
trampoline[3] = BR X0 (0xd61f0000)
trampoline[4] = B 8 (0x14000002)
trampoline[5] = value >> 32
trampoline[6] = value & 0xffffffff
memcpy(fixOpcodes+20, trampoline, 28)
fixPos = 48

# iter 4: insn[3] LDR_ARM64
fixPCOpcodeArm64 → LDR 分支
trampoline[0] = STP X2, X1 (选 X1 因为 rt=2) 0xa93f03e0 + 2 + (1<<10) = 0xa93f07e2
... (7 条, 28 字节)
memcpy(fixOpcodes+48, trampoline, 28)
fixPos = 76

# iter 5: insn[4] CBZ_ARM64 → 落到 OTHER (原样拷贝)
memcpy(fixOpcodes+76, insn[4], 4)
fixPos = 80

# iter 6: insn[5] RET → 落到 OTHER
memcpy(fixOpcodes+80, insn[5], 4)
fixPos = 84

return 84
```

`BuildOldFunction` 后续：

```
memcpy(pNewEntryForOldFunction, fixOpcodes, 84)
BuildArmJumpCode(pNewEntryForOldFunction + 84, pHookAddr + 20)
  → 写入 24B 跳转 (LDR X17,8; BR X17; <addr>)

*ppOldFuncAddr = pNewEntryForOldFunction
```