# 04 · 数据流与生命周期

## 4.1 核心数据结构

### `struct context`

定义于 `And64InlineHook.cpp:51-106`，是整个修复调度器的"工作台"：

```cpp
struct context {
    struct fix_info {            // 行 53-58
        uint32_t *bp;            // 指向输出区中"待回填位置"（uint32_t*）
        uint32_t  ls;            // 左移位数（构造时固定）
        uint32_t  ad;            // AND 掩码（构造时固定）
    };
    struct insns_info {          // 行 59-68
        union {
            uint64_t insu;
            int64_t  ins;        // 输出区中该指令对应位置（绝对地址）
            void    *insp;
        };
        fix_info fmap[A64_MAX_REFERENCES];  // 每条 insn 最多 2 个待回填字段
    };
    int64_t    basep;            // 输入指令区起点（inp 的绝对地址）
    int64_t    endp;             // 输入指令区终点
    insns_info dat[A64_MAX_INSTRUCTIONS];   // 每条原指令一个槽
    // ... methods ...
};
```

### 成员函数

| 方法 | 签名 | 作用 | 行号 |
|------|------|------|------|
| `is_in_fixing_range` | `bool(int64_t)` | `absolute_addr ∈ [basep, endp)`？用于判断跳转目标是否落在备份区间内 | `74-76` |
| `get_ref_ins_index` | `intptr_t(int64_t)` | 把绝对地址转成 `(addr - basep) / 4`，即指令序号 | `77-79` |
| `get_and_set_current_index` | `intptr_t(uint32_t*, uint32_t*)` | 计算当前输入/输出指令的序号，把 `insp` 设为输出地址，返回序号 | `80-84` |
| `reset_current_ins` | `void(intptr_t, uint32_t*)` | 插入 NOP 对齐后，重新设置 `insp` | `85-87` |
| `insert_fix_map` | `void(intptr_t, uint32_t*, uint32_t, uint32_t)` | 把"待回填字段"登记到 `fmap` 第一个空槽 | `88-98` |
| `process_fix_map` | `void(intptr_t)` | 把 `dat[idx].ins - bp` 编码到 `bp` 指向的指令字段 | `99-105` |

### 字段用途对照

| 字段 | 何时写入 | 何时读取 |
|------|---------|---------|
| `basep` | `__fix_instructions` 入口 | 各 fix 函数判断"是否在备份区间内" |
| `endp` | `__fix_instructions` 入口 | 同上 |
| `dat[i].insp` | `get_and_set_current_index` / `reset_current_ins` | 后续指令判断"该位置已被定下来"时回填引用 |
| `dat[i].fmap[k]` | 当前指令为分支目标、且目标在更后面 → `insert_fix_map` 登记到"目标的 fmap" | 处理目标指令时 `process_fix_map` 回填 |

## 4.2 trampoline 数据生命周期

```mermaid
stateDiagram-v2
    [*] --> Uninit: __insns_pool 是 .bss 段

    Uninit --> RWX: A64HookInit 构造时<br/>mprotect(pool, RWX)
    note right of RWX
        mprotect(p & ~0xFFF,<br/>(size + 1 page) aligned, RWX)
        失败时 A64_LOGE 但不返回错误
        (后续 hook 仍会 mprotect 自己)
    end note

    RWX --> Allocated: FastAllocateTrampoline<br/>__sync_add_and_fetch(&__index, 1)
    note right of Allocated
        slot = __insns_pool[i]
        i 从 0 开始自增
        永不释放 (no unhook)
    end note

    Allocated --> Filled: __fix_instructions 写入<br/>(约 4-40 字节指令)
    note right of Filled
        末尾追加:
        LDR X17, #8; BR X17; <addr>
        然后 __flush_cache
    end note

    Filled --> [*]: 进程退出 (slot 不归还)
```

## 4.3 hook 点数据生命周期

```mermaid
stateDiagram-v2
    [*] --> OriginalCode: 函数原始指令 (R-X)
    OriginalCode --> RWX: A64HookFunction:<br/>__make_rwx(symbol, 5*sizeof(size_t))
    RWX --> HookWritten: A64HookFunctionV:<br/>mprotect 4B 或 20B, 写跳转
    HookWritten --> CachedCleared: __builtin___clear_cache
    CachedCleared --> Hooked: 持续生效
    note right of Hooked
        不可撤销
        (库无 unhook API)
    end note
```

## 4.4 数据流总图

```mermaid
flowchart LR
    subgraph In["输入 (原函数头)"]
        I0["insn[0]"]
        I1["insn[1]"]
        I2["insn[2]"]
        I3["insn[3]"]
        I4["insn[4]"]
    end

    subgraph FixFuncs["4 个 fix 函数 (顺序尝试)"]
        FB["__fix_branch_imm<br/>B / BL"]
        FC["__fix_cond_comp_test_branch<br/>B.cond / CBZ / CBNZ / TBZ / TBNZ"]
        FL["__fix_loadlit<br/>LDR / LDRSW / PRFM"]
        FA["__fix_pcreladdr<br/>ADR / ADRP"]
        FD["默认: 原样拷贝"]
    end

    subgraph Ctx["context 工作台"]
        D0["dat[0]<br/>(insp + fmap[])"]
        D1["dat[1]"]
        D2["dat[2]"]
        D3["dat[3]"]
        D4["dat[4]"]
    end

    subgraph Out["输出 (trampoline 槽)"]
        O0["修复后 insn 0 (可能多条)"]
        ON["..."]
        OJ["LDR X17, #8<br/>BR X17<br/>8-byte addr"]
    end

    I0 --> FB
    I0 --> FC
    I0 --> FL
    I0 --> FA
    I0 --> FD
    FB -->|true| D0
    FB -->|false| FC
    FC -->|true| D0
    FC -->|false| FL
    FL -->|true| D0
    FL -->|false| FA
    FA -->|true| D0
    FA -->|false| FD
    FD --> D0

    D0 --> O0
    I1 --> FixFuncs2["FB / FC / FL / FA / FD"]
    FixFuncs2 --> D1
    I2 --> FixFuncs3["FB / FC / FL / FA / FD"]
    FixFuncs3 --> D2
    I3 --> FixFuncs4["..."]
    FixFuncs4 --> D3
    I4 --> FixFuncs5["..."]
    FixFuncs5 --> D4

    O0 --> ON
    ON --> OJ

    D0 -.->|前向引用回填| FixFuncs3
    D1 -.->|前向引用回填| FixFuncs4
```

## 4.5 关键修复决策表

每个 `__fix_*` 函数对指令的决策分支相同：

| 条件 | 处理 |
|------|------|
| 跳转目标在备份区间外 **且** 偏移超过 `±mask>>1` | 膨胀为 `LDR Xn, #8; BR Xn; <addr>` 模式（必要时 NOP 对齐） |
| 跳转目标在备份区间外 **且** 偏移可表达 | 直接写原指令，调整 PC-relative 字段 |
| 跳转目标在备份区间内、且指向已处理过的指令 (`ref_idx <= current_idx`) | 用 `dat[ref_idx].ins - outp` 重算偏移 |
| 跳转目标在备份区间内、且指向未处理的指令 (`ref_idx > current_idx`) | **延迟回填**：把 `{bp, ls, ad}` 登记到 `dat[ref_idx].fmap`，`new_pc_offset = 0`，等 `process_fix_map(current_idx)` 在该指令被处理时填入 |

## 4.6 数据流示例

设原函数前 4 条指令：

```asm
0x1000: LDR X0, =global_var      ; 0x58000040 (LDR literal)
0x1004: CBZ X0, 0x1020           ; 0xb4000010 ...
0x1008: ADD X1, X0, #1           ; 0x91000401
0x100c: B   0x2000               ; 0x140003fc
0x1010: ... (后续)
```

修复后 trampoline（假设 hook 到 0x1000）：

```asm
trampoline+0:  LDR X0, 8            ; LDR literal → 改走下面 8 字节
trampoline+4:  B 12                 ; 跳过 NOP（？）
trampoline+8:  <8-byte addr of global_var>  ; 直接放常量
trampoline+16: B.anti 8             ; CBZ 的反条件 (always-equivalent: skip)
trampoline+20: <原 0x1020 的指令>   ; CBZ 目标直接嵌入
trampoline+24: STP X0, X0, [SP, -0x10]?  ; loadlit 修复模式（取决于模板）
...
trampoline+?:  LDR X17, #8
trampoline+?+4: BR X17
trampoline+?+8: <8-byte addr = 0x100c>  ; 跳到原函数第 4 条之后 (跳过前 4 条)
```

具体布局由每个 fix 函数的膨胀比例决定，**`A64_MAX_INSTRUCTIONS * 10` = 50 uint32 = 200 字节是上限。**