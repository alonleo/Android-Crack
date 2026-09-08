# 03 · 架构总览

## 3.1 分层

```
┌──────────────────────────────────────────────────────────────┐
│  用户代码                                                     │
│  void *orig = NULL;                                          │
│  A64HookFunction(target_fn, my_hook, &orig);                  │
│  // 调用 orig(target_fn) 会跳到 trampoline（=原函数头 5 条）  │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  公开 API 层                                                  │
│  ┌─────────────────────┐   ┌──────────────────────────┐      │
│  │ A64HookFunction     │──▶│ A64HookFunctionV         │      │
│  │ (分配 trampoline)   │   │ (写入 hook 点)            │      │
│  └─────────────────────┘   └──────────────────────────┘      │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  核心修复调度层                                                │
│  __fix_instructions(inp, count, outp)                         │
│  ├─ while (count--) {                                        │
│  │    __fix_branch_imm  │ __fix_cond_comp_test_branch        │
│  │    __fix_loadlit     │ __fix_pcreladdr                    │
│  │    // 默认: 原样拷贝                                       │
│  │  }                                                        │
│  // 末尾: 跳回原函数剩余部分                                   │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  上下文管理层 (context)                                       │
│  ├─ fix_info { bp, ls, ad }  → 待回填字段                     │
│  ├─ insns_info { ins, fmap[] }→ 单条指令 + 修复槽              │
│  ├─ basep/endp              → 输入范围                         │
│  └─ 方法: get_ref_ins_index, insert_fix_map, process_fix_map  │
└──────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌──────────────────────────────────────────────────────────────┐
│  平台抽象层（宏）                                              │
│  __make_rwx (mprotect)                                       │
│  __flush_cache (__builtin___clear_cache)                      │
│  __sync_cmpswap (CAS)                                        │
│  __align_up/down                                             │
└──────────────────────────────────────────────────────────────┘
```

## 3.2 内存布局

### 静态 trampoline 池

```cpp
// And64InlineHook.cpp:481
static __attribute__((__aligned__(__page_size))) uint32_t
    __insns_pool[A64_MAX_BACKUPS][A64_MAX_INSTRUCTIONS * 10];
```

- 类型：`uint32_t[A64_MAX_BACKUPS][50]` → 256 × 50 × 4 = **51200 字节 = 12.5 pages**
- 对齐：4 KiB 页对齐（`.bss` 段自动保证）
- 构造时由 `A64HookInit` mprotect 为 RWX
- 分配：`FastAllocateTrampoline()` 用 `__sync_add_and_fetch(&__index, 1)` 自增

### hook 点指令布局

近跳转（`llabs(pc_offset) < (1<<25)`，即 ±128 MiB）：

```
偏移  字节         指令
─────────────────────────────────────────
+0   0x14000000   B <offset>            (4 字节)
```

远跳转（超过 ±128 MiB）：

```
偏移  字节          指令                          含义
─────────────────────────────────────────────────────────────
+0   0xd503201f   NOP                          (仅当 hook 点 4n+2 时插入, 4 字节)
+0   0x58000051   LDR X17, #0x8                (4 字节, PC-relative)
+4   0xd61f0220   BR X17                       (4 字节)
+8   <8 bytes>    绝对地址 (int64_t)             (8 字节)
─────────────────────────────────────────────────────────────
总计：4 条指令 = 20 字节（含 NOP = 24 字节）
```

### trampoline 内容（典型 4 指令备份）

```
偏移  字节          含义
─────────────────────────────────────────────────────────────
+0   <原始 insn 0>  可能为多条（修复后膨胀）
+4   <原始 insn 1>  ...
+8   <原始 insn 2>  ...
+12  <原始 insn 3>  ...
+?   LDR X17, #8    PC-relative load
+?+4 BR X17         跳转到下面 8 字节存的地址
+?+8 <int64>        原函数剩余部分入口（=原始 instr[4..end] 的第一条）
─────────────────────────────────────────────────────────────
```

## 3.3 启动 / 静态初始化时序

```mermaid
sequenceDiagram
    autonumber
    participant Loader as Android Dynamic Linker
    participant Lib as And64InlineHook.cpp
    participant Ctor as A64HookInit::A64HookInit()
    participant Pool as __insns_pool
    participant User as 用户 main()

    Loader->>Lib: dlopen / static link
    Note over Lib: __init 是 static A64HookInit
    Lib->>Ctor: 构造（.so 加载时 / 程序启动时）
    Ctor->>Pool: mprotect(12 pages, RWX)
    Ctor-->>Lib: LOGI("insns pool initialized.")
    Loader->>User: main() 开始
    User->>Lib: A64HookFunction(target, hook, &trampoline)
    Lib->>Pool: FastAllocateTrampoline() → 第 N 槽
    Lib->>Lib: mprotect(target, RWX)
    Lib->>Lib: __fix_instructions → 写 trampoline
    Lib->>Lib: 写 hook 点（4 或 20 字节）
    Lib->>Lib: __builtin___clear_cache(...)
    Lib-->>User: result = trampoline
```

## 3.4 类图（context 结构体）

```mermaid
classDiagram
    class context {
        +int64_t basep
        +int64_t endp
        +insns_info dat[A64_MAX_INSTRUCTIONS]
        +is_in_fixing_range(addr) bool
        +get_ref_ins_index(addr) intptr_t
        +get_and_set_current_index(inp, outp) intptr_t
        +reset_current_ins(idx, outp) void
        +insert_fix_map(idx, bp, ls, ad) void
        +process_fix_map(idx) void
    }

    class fix_info {
        +uint32_t* bp
        +uint32_t ls
        +uint32_t ad
    }

    class insns_info {
        +union insu/ins/insp
        +fix_info fmap[A64_MAX_REFERENCES]
    }

    context "1" *-- "A64_MAX_INSTRUCTIONS" insns_info
    insns_info "1" *-- "A64_MAX_REFERENCES" fix_info

    class A64HookInit {
        +A64HookInit()
    }

    class A64HookFunctionV {
        <<extern C>>
        +void* A64HookFunctionV(symbol, replace, rwx, rwx_size)
    }

    class A64HookFunction {
        <<extern C>>
        +void A64HookFunction(symbol, replace, result)
    }

    A64HookFunction ..> A64HookFunctionV : 调用
    A64HookFunction ..> FastAllocateTrampoline : 调用
```

## 3.5 控制流（hook 时）

```mermaid
flowchart TD
    Start[用户调用<br/>A64HookFunction] --> A{FastAllocateTrampoline}
    A -->|成功| B["mprotect(symbol, RWX)<br/>(Android 10 兼容)"]
    A -->|失败| End1[return]

    B --> C[A64HookFunctionV]
    C --> D{PC 偏移 vs ±128 MiB}
    D -->|远跳转| E[count = 4 或 5]
    D -->|近跳转| F[count = 1]

    E --> G["__fix_instructions(original, count, trampoline)"]
    F --> G
    G --> H["mprotect(original, RWX)"]
    H --> I{远跳转?}
    I -->|是| J["写 LDR+BR+addr (20 B)"]
    I -->|否| K["CAS 写 B (4 B)"]
    J --> L["__builtin___clear_cache"]
    K --> L
    L --> M[返回 trampoline]
```

## 3.6 调用时控制流（被 hook 的函数被调用时）

```mermaid
sequenceDiagram
    autonumber
    participant Caller as 调用方代码
    participant Target as 原函数头
    participant Hook as 替换函数
    participant Tram as trampoline (静态池)
    participant Rest as 原函数剩余部分

    Caller->>Target: bl target
    Target->>Target: 执行写入的跳转指令<br/>(B 或 LDR+BR+addr)
    alt B 形式
        Target->>Hook: pc ± offset → Hook
    else LDR+BR 形式
        Target->>Hook: 加载 8 字节 addr → BR
    end
    Hook->>Hook: 执行替换函数逻辑
    Hook-->>Caller: 返回 (或 bl trampoline 续跑)
    Note over Hook,Tram: 若需"先调原函数再调替换"<br/>应直接调用 trampoline()
    Tram->>Tram: 执行修复后的 1-5 条原指令
    Tram->>Rest: 末尾 LDR X17 → BR X17 → 跳到原函数第 5 条之后
    Rest-->>Caller: 正常返回
```

> **设计意图**：And64InlineHook **不提供回调机制**，只把 `target` 替换为 `replace`。若要"插入式"hook（先调原函数再调替换），调用方应在 `replace` 中显式调用保存下来的 trampoline。