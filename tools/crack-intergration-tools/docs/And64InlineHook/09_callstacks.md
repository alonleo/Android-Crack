# 09 · 关键调用栈汇总

## 9.1 主调用栈（用户调用 `A64HookFunction`）

```
[user code]
 └─ A64HookFunction                                          And64InlineHook.cpp:577
     ├─ FastAllocateTrampoline                               And64InlineHook.cpp:498
     │   ├─ __atomic_increase (__sync_add_and_fetch)        macro
     │   └─ A64_LOGE (on overflow)                          macro
     ├─ __make_rwx(symbol, 5 * sizeof(size_t))              macro → mprotect (Android 10 fix)
     │                                                           And64InlineHook.cpp:587
     └─ A64HookFunctionV                                     And64InlineHook.cpp:589
         ├─ __fix_instructions(original, count, trampoline) And64InlineHook.cpp:430
         │   ├─ __fix_branch_imm(&inp, &outp, &ctx)          And64InlineHook.cpp:447
         │   │   ├─ ctx.get_and_set_current_index(...)      And64InlineHook.cpp:143
         │   │   ├─ ctx.reset_current_ins(...)              And64InlineHook.cpp:153 / :162
         │   │   ├─ ctx.is_in_fixing_range(...)             And64InlineHook.cpp:146
         │   │   ├─ ctx.get_ref_ins_index(...)              And64InlineHook.cpp:172
         │   │   ├─ ctx.insert_fix_map(...)                 And64InlineHook.cpp:176
         │   │   └─ ctx.process_fix_map(...)                And64InlineHook.cpp:186
         │   ├─ __fix_cond_comp_test_branch(...)            And64InlineHook.cpp:448
         │   ├─ __fix_loadlit(...)                          And64InlineHook.cpp:449
         │   ├─ __fix_pcreladdr(...)                        And64InlineHook.cpp:450
         │   └─ ctx.process_fix_map(...); memcpy(outp,...)  And64InlineHook.cpp:453-454
         │                                                       (default branch)
         ├─ __make_rwx(original, ...)                       macro
         │                                                       And64InlineHook.cpp:533 / :559
         ├─ (近跳转) __sync_cmpswap(original, ..., B-encoded) macro
         │                                                       And64InlineHook.cpp:560
         ├─ (远跳转) 直接写 LDR+BR+addr (NOP+memcpy)         And64InlineHook.cpp:535-540
         └─ __flush_cache(symbol, ...)                      macro
                                                                 And64InlineHook.cpp:541 / :561
```

## 9.2 静态初始化栈（`.so` 加载）

```
[_init / .so loader]
 └─ static A64HookInit __init;                              And64InlineHook.cpp:494
     └─ A64HookInit::A64HookInit()                          And64InlineHook.cpp:488
         ├─ __make_rwx(__insns_pool, sizeof(__insns_pool))  macro → mprotect
         │                                                       And64InlineHook.cpp:490
         └─ A64_LOGI("insns pool initialized.")             macro
                                                                 And64InlineHook.cpp:491
```

## 9.3 修复函数内部调用（以 `__fix_branch_imm` 远跳为例）

```
__fix_branch_imm (static)
 ├─ ctx.get_and_set_current_index(inp, outp)               line 143
 ├─ 计算 absolute_addr / new_pc_offset / special_fix_type   line 144-146
 ├─ ctx.is_in_fixing_range(absolute_addr)                   line 146
 ├─ (分支: 远跳膨胀)
 │   ├─ (outp+2 & 7 != 0) outp[0] = NOP; ctx.reset         line 152-153
 │   ├─ outp[0] = LDR X17, #8 (0x58000051)                  line 155
 │   ├─ outp[1] = BR X17 (0xd61f0220)                       line 156
 │   ├─ memcpy(outp+2, &absolute_addr, 8)                   line 157
 │   └─ outp += 4                                           line 158
 ├─ ++inp                                                   line 185
 └─ ctx.process_fix_map(current_idx)                        line 186
     └─ for f in dat[idx].fmap:                             line 100
         └─ *f.bp |= ((dat[idx].ins - f.bp) >> 2 << f.ls) & f.ad   line 102
```

## 9.4 数据反向引用（修复备份内分支）

设 `inp[3]` (B 到 inp[1]) 在修复时遇到：

```
inp[0]: 修复为远跳 (outp+0)
inp[1]: 修复为远跳 (outp+4)
inp[2]: 默认 (outp+8, 但可能 NOP 调整)
inp[3]: B inp[1] (在备份内, ref_idx=1)
```

`__fix_branch_imm` 处理 inp[3] 时：

1. `current_idx = 3`
2. `ctx.dat[3].insp = outp + 12`（登记）
3. `absolute_addr = inp + 3 + imm26*4 = inp[1] 的绝对地址`
4. `ref_idx = 1`
5. 因为 `ref_idx (1) <= current_idx (3)`，`new_pc_offset = (ctx.dat[1].ins - outp) >> 2`
6. 写 B-encoded 到 `outp[0]`, `++outp`

**结果**：跳转到 inp[1] 的 trampoline 位置，而不是原始地址。

## 9.5 前向引用（修复指向未处理指令的备份内分支）

设 `inp[1]` (B 到 inp[4]) 在处理时：

1. `current_idx = 1`
2. `absolute_addr = inp + 4`
3. `ref_idx = 4`
4. 因为 `ref_idx (4) > current_idx (1)`，`ctx.insert_fix_map(ref_idx=4, bp=outp, ls=0, ad=0x03ffffff); new_pc_offset = 0`
5. 写一条 `B #0`（占位），`++outp`

后续处理 inp[4] 时：

1. `current_idx = 4`
2. `ctx.dat[4].insp = outp_now`
3. （本指令可能是普通非 PC-relative 指令）`ctx.process_fix_map(4)` 被调用
4. 遍历 `dat[4].fmap[]`，找到先前登记的 `{bp=outp_old, ls=0, ad=0x03ffffff}`
5. `*bp |= ((dat[4].ins - bp) >> 2 << 0) & 0x03ffffff`
6. `bp = NULL`（防止重复处理）

**结果**：之前占位的 `B #0` 被回填为正确的跳转偏移。

## 9.6 trampoline 末尾跳转栈

```
__fix_instructions                                          And64InlineHook.cpp:430
 ├─ (循环 4 个 fix 函数, 见 9.1)
 ├─ callback = inp                                            line 458
 │   (此时 inp 已前进 count 步, = 备份区间之后的第一条原指令)
 ├─ pc_offset = (callback - outp) >> 2                       line 459
 ├─ 若 |pc_offset| ≥ 2^25:                                   line 460
 │   ├─ (outp+2 & 7 != 0) outp[0] = NOP; ++outp              line 461-464
 │   ├─ outp[0] = LDR X17, #8 (0x58000051)                   line 465
 │   ├─ outp[1] = BR X17 (0xd61f0220)                        line 466
 │   ├─ *(int64_t*)(outp+2) = callback                       line 467
 │   └─ outp += 4                                            line 468
 └─ 否则:
     ├─ outp[0] = B encoded                                  line 470
     └─ ++outp                                               line 471
```

## 9.7 调用栈矩阵

| 入口 | 主要栈深 | 文件:行 |
|------|---------|---------|
| `A64HookFunction` | 3（API → 分配 → 高级 API） | `577 → 498 → 514` |
| `A64HookFunctionV` (远跳) | 5（V → fix → fix_branch_imm → ctx → memcpy） | `514 → 430 → 447 → 143 → 157` |
| `A64HookFunctionV` (近跳) | 3（V → fix → memcpy） | `514 → 430 → 454` |
| `__fix_instructions` | 2（fix → 4 个 fix 子函数） | `430 → 447-450` |
| `__fix_branch_imm` | 2（imm → ctx.*） | `129 → 143/172/176/186` |
| `__fix_cond_comp_test_branch` | 2 | `194 → 222/239/243/253` |
| `__fix_loadlit` | 2 | `258 → 265/301/310/325/332` |
| `__fix_pcreladdr` | 2 | `337 → 356/373/377/390/423` |
| `FastAllocateTrampoline` | 1 | `498` |
| `A64HookInit::A64HookInit` | 1（构造时） | `488` |