# 08 · 函数详细说明（汇编 stub 模板 - ihookstub.s）

> 本文件覆盖 `jni/InlineHook/ihookstub.s` 全部指令 + 4 个全局符号。

---

## 文件级信息

- **位置**: `jni/InlineHook/ihookstub.s`
- **总行数**: 82
- **汇编器**: GNU AS（gas）for aarch64-linux-android
- **段**: `.data`（行 6 显式声明，但实际是可执行代码，运行时被 mprotect 为 RWX）
- **汇编模式**: AArch64

### 全局符号导出

```asm
.global _shellcode_start_s           ; 行 1
.global _shellcode_end_s             ; 行 2
.global _hookstub_function_addr_s    ; 行 3
.global _old_function_addr_s         ; 行 4
```

链接器保证这些符号的相对偏移在 stub 内稳定，C 代码用 `&_symbol` 取地址。

---

## `_shellcode_start_s` — Stub 主体

- **位置**: `ihookstub.s:8`
- **作用**: stub 起始标签。被 `BuildStub` 通过 `&_shellcode_start_s` 引用
- **栈帧总大小**: 32B (NZCV+LR+sp 备份) + 240B (GPR) = **272B**

### 指令逐行解读

#### 1. 父栈调整 + NZCV/LR 保存（行 10-17）

```asm
sub  sp, sp, #0x20          ; sp -= 32 (分配 32B 栈帧)
mrs  x0, NZCV                ; x0 = NZCV 标志寄存器
str  x0, [sp, #0x10]         ; [sp+0x10] = NZCV (保存)
str  x30, [sp]               ; [sp+0x00] = LR (caller 的返回地址)
add  x30, sp, #0x20          ; x30 = 父 sp (caller 视角的栈顶)
str  x30, [sp, #0x8]         ; [sp+0x08] = 父 sp
ldr  x0, [sp, #0x18]         ; x0 = [sp+0x18] (parent_sp + 0...?)
```

> **疑点**：行 17 `ldr x0, [sp, #0x18]` 读取 `parent_sp + 0x18`。但此时 sp 已经下移 0x20，所以 `[sp+0x18]` 实际是 `[原 sp - 0x08]`——指向 caller 栈上的某个位置。**注释缺失**，但被后续 `mov x0, sp` 覆盖（行 36）。这一行实际上是**死代码 / 占位**。

#### 2. GPR 保存（行 19-34）

```asm
sub  sp, sp, #0xf0           ; sp -= 240 (分配 240B 栈帧)
stp  X0,  X1,  [SP]              ; [sp+0x00..0x10]
stp  X2,  X3,  [SP, #0x10]       ; [sp+0x10..0x20]
stp  X4,  X5,  [SP, #0x20]
stp  X6,  X7,  [SP, #0x30]
stp  X8,  X9,  [SP, #0x40]
stp  X10, X11, [SP, #0x50]
stp  X12, X13, [SP, #0x60]
stp  X14, X15, [SP, #0x70]
stp  X16, X17, [SP, #0x80]
stp  X18, X19, [SP, #0x90]
stp  X20, X21, [SP, #0xa0]
stp  X22, X23, [SP, #0xb0]
stp  X24, X25, [SP, #0xc0]
stp  X26, X27, [SP, #0xd0]
stp  X28, X29, [SP, #0xe0]       ; [sp+0xe0..0xf0]
```

> **注意**：保存的是 X0–X29，**不保存 X30 (LR)**——因为 X30 已在前面 `str x30, [sp]` 保存。

#### 3. 调用回调（行 36-43）

```asm
mov  x0, sp                 ; x0 = sp (= GPR 栈帧基址 = regs 指针)
ldr  x3, 8                  ; x3 = [PC+8] = _hookstub_function_addr_s 处的 8B (= onCallBack)
b    12                     ; PC += 12 (跳过接下来的 8B 槽)
```

**`_hookstub_function_addr_s` 处**（行 40-41）：

```asm
_hookstub_function_addr_s:
.double 0xffffffffffffffff   ; 8B 占位, 运行时被 onCallBack 地址覆盖
```

```asm
blr  x3                     ; 调用 onCallBack (x0 = regs)
```

> `x3` 作为临时寄存器（AAPCS64 caller-saved）调用约定上没问题；`x0-x7` 是 caller-saved 但用户回调拿到的是 `regs` 指针，所以 X0-X7 也已被保存——可以放心用 x3。

#### 4. NZCV + GPR 恢复（行 44-62）

```asm
ldr  x0, [sp, #0x100]       ; x0 = NZCV (注意: 此时 sp 仍指向 GPR 栈帧底)
                             ; [sp+0x100] = [sp+0xf0 (GPR 结束) + 0x10 (NZCV)]
msr  NZCV, x0               ; 恢复 NZCV

ldp  X0,  X1,  [SP]              ; 恢复 GPR
ldp  X2,  X3,  [SP, #0x10]
... (15 对 ldp)
ldp  X28, X29, [SP, #0xe0]
add  sp, sp, #0xf0          ; 释放 240B
```

#### 5. LR 恢复 + X0/X1 保护（行 64-69）

```asm
ldr  x30, [sp]              ; 恢复 LR (caller 的返回地址)
add  sp, sp, #0x20          ; 释放 32B

stp  X1, X0, [SP, #-0x10]   ; 暂存 X0/X1 到 caller 的栈顶 (因为接下来 LDR X0 会改 X0)
ldr  x0, 8                  ; x0 = [PC+8] = _old_function_addr_s 处的 8B (= pNewEntryForOldFunction)
b    12                     ; 跳过 8B 槽
```

**`_old_function_addr_s` 处**（行 71-72）：

```asm
_old_function_addr_s:
.double 0xffffffffffffffff   ; 8B 占位, 运行时被 pNewEntryForOldFunction 覆盖
```

#### 6. 跳到旧函数（行 74）

```asm
br   x0                     ; 跳到 pNewEntryForOldFunction
```

---

## `_hookstub_function_addr_s` — 回调地址槽

- **位置**: `ihookstub.s:40-41`
- **大小**: 8 字节（`.double 0xffffffffffffffff` 占位）
- **运行时**: 被 `BuildStub` (`:181`) 改写为 `pstInlineHook->onCallBack`
- **跳转关系**: stub 主体用 `ldr x3, 8; b 12` 加载并跳到此地址

### 二进制布局

```
addr+0:  .double 0xffffffffffffffff  ← 占位 (8B)
addr+8:  blr x3                      ← 跳到这里执行 onCallBack
```

---

## `_old_function_addr_s` — 旧函数入口槽

- **位置**: `ihookstub.s:71-72`
- **大小**: 8 字节
- **运行时**: 被 `BuildOldFunction` (`:313`) 改写为 `pNewEntryForOldFunction`
- **跳转关系**: stub 主体用 `ldr x0, 8; b 12` 加载并用 `br x0` 跳转

### 二进制布局

```
addr+0:  .double 0xffffffffffffffff  ← 占位 (8B)
addr+8:  br x0                       ← 跳到这里执行旧函数
```

---

## `_shellcode_end_s` — Stub 结束标签

- **位置**: `ihookstub.s:80`
- **作用**: stub 结束标签。`BuildStub` 通过 `p_shellcode_end_s - p_shellcode_start_s` 计算 stub 总长度用于 malloc

---

## 完整布局图

```
偏移  指令/数据                                     注释
─────────────────────────────────────────────────────────────────────
+0    sub sp, sp, #0x20                           ; sp -= 32
+4    mrs x0, NZCV
+8    str x0, [sp, #0x10]
+12   str x30, [sp]
+16   add x30, sp, #0x20
+20   str x30, [sp, #0x8]
+24   ldr x0, [sp, #0x18]                         ; (dead)
+28   sub sp, sp, #0xf0                           ; sp -= 240
+32   stp X0, X1, [SP]                            ┐
+36   stp X2, X3, [SP, #0x10]                     │
...  (15 对 stp)                                  │ 保存 GPR (240B)
+148  stp X28, X29, [SP, #0xe0]                   ┘
+152  mov x0, sp                                  ; x0 = regs
+156  ldr x3, 8                                   ┐ 加载 onCallBack
+160  b 12                                        │
+164  .double 0xffffffffffffffff   _hookstub_function_addr_s
+172  blr x3                                      ┘ 调回调
+176  ldr x0, [sp, #0x100]
+180  msr NZCV, x0
+184  ldp X0, X1, [SP]                            ┐
...  (15 对 ldp)                                  │ 恢复 GPR
+296  ldp X28, X29, [SP, #0xe0]                   ┘
+300  add sp, sp, #0xf0                           ; sp += 240
+304  ldr x30, [sp]
+308  add sp, sp, #0x20                           ; sp += 32
+312  stp X1, X0, [SP, #-0x10]                    ; 保存 X0/X1
+316  ldr x0, 8                                   ┐ 加载 old_func
+320  b 12                                        │
+324  .double 0xffffffffffffffff   _old_function_addr_s
+332  br x0                                       ┘ 跳旧函数
+336  (_shellcode_end_s 在此)
─────────────────────────────────────────────────────────────────────
总大小 ≈ 82 字节（汇编器实际可能略有 padding）
```

---

## 已知设计缺陷

| 缺陷 | 位置 | 影响 |
|------|------|------|
| `ldr x0, [sp, #0x18]` 行 17 是死代码 | 行 17 | 被行 36 `mov x0, sp` 覆盖 |
| 行 36-37 不重置 x3 / sp 等临时值 | 行 36 | 用户回调看到的是被 hook 跳转污染的寄存器 |
| 未在入口加 `BTI` 指令 | 行 8 | ARMv8.5+ BTI 启用时会触发异常 |
| 未在 NZCV 之前保存 FPCR/FPSR | 行 10 | 浮点标志位不恢复（与 stub 主要处理整数上下文一致，但浮点 hook 会有问题） |
| 未保存 X30 (LR) 到 GPR 栈帧 | 行 11-12 vs 19-34 | LR 在 32B 栈帧中，调用约定上不安全（caller-saved）——但这里 X30 已被显式保存到 [sp]，可接受 |
| 行 67 `stp X1, X0, [SP, #-0x10]` 使用 caller 栈 | 行 67 | 调用方栈大小限制未知，可能溢出 |