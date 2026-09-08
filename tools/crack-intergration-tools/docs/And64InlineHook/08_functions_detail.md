# 08 · 函数详细说明（And64InlineHook.cpp + .hpp）

> 本文件覆盖全部 11 个内部函数、2 个公开 API、1 个辅助类、6 个 `context` 方法。  
> 模板按规范填写：签名 / 位置 / 可见性 / 参数 / 返回值 / 副作用 / 调用 / 调用了 / 简要说明。

---

## 8.1 公开 API

### `A64HookFunction`
- **签名**: `void A64HookFunction(void *const symbol, void *const replace, void **result)`
- **位置**: `And64InlineHook.hpp:36`（声明）/ `And64InlineHook.cpp:577-593`（定义）
- **可见性**: `extern "C"`，`A64_JNIEXPORT` = `__attribute__((visibility("default")))`
- **参数**:
  - `symbol`: 目标函数入口地址
  - `replace`: 替换函数入口地址
  - `result`: 输出参数，保存 trampoline 地址（指向原函数头 1-5 条指令的修复副本），失败时为 NULL
- **返回值**: `void`
- **副作用**:
  - 分配一个 trampoline 槽（修改 `__index`）
  - `mprotect(symbol, 5*sizeof(size_t), RWX)`（Android 10 兼容性，行 587）
  - 通过 `A64HookFunctionV` 写入 trampoline + 改写 hook 点
- **调用**: 用户代码直接调用，无内部调用方
- **调用了**:
  - `FastAllocateTrampoline()` (`And64InlineHook.cpp:581`)
  - `__make_rwx(symbol, 5 * sizeof(size_t))` (宏 → `mprotect`，`And64InlineHook.cpp:587`)
  - `A64HookFunctionV(symbol, replace, trampoline, A64_MAX_INSTRUCTIONS * 10u)` (`And64InlineHook.cpp:589`)
- **简要说明**: 公开主入口；从静态池分配 trampoline，调 `A64HookFunctionV` 完成实际写入。

### `A64HookFunctionV`
- **签名**: `void *A64HookFunctionV(void *const symbol, void *const replace, void *const rwx, const uintptr_t rwx_size)`
- **位置**: `And64InlineHook.hpp:37-38`（声明）/ `And64InlineHook.cpp:514-573`（定义）
- **可见性**: `extern "C"`，`A64_JNIEXPORT`
- **参数**:
  - `symbol`: 目标函数地址
  - `replace`: 替换函数地址
  - `rwx`: 调用者提供的 RWX trampoline 缓冲区，传 NULL 则跳过 trampoline 写入（仅写入 hook 点）
  - `rwx_size`: 缓冲区字节数
- **返回值**: trampoline 指针（即 `rwx`），失败 NULL
- **副作用**:
  - 计算 PC 偏移量并决定走"近跳转"（4 字节 B）或"远跳转"（20 字节 LDR+BR+addr）分支
  - `__fix_instructions(original, count, trampoline)` 写 trampoline
  - `__make_rwx(original, 4 or 20)` 改 hook 点页属性
  - 写 hook 点（CAS 写 B 或 memcpy 写 LDR+BR+addr+NOP）
  - `__flush_cache(symbol, 4 or 20)` 清指令缓存
  - `A64_LOGI` / `A64_LOGE` 输出结果
- **调用**: 被 `A64HookFunction` 调用 (`And64InlineHook.cpp:589`)
- **调用了**:
  - `__intval` (宏，行 522, 540)
  - `__fix_instructions()` (`And64InlineHook.cpp:530`, `:556`)
  - `__make_rwx` (宏，行 533, 559)
  - `__sync_cmpswap` (宏，行 560)
  - `__flush_cache` (宏，行 541, 561)
- **简要说明**: 高级入口；按 PC 偏移决定指令编码，必要时 4 字节对齐再写跳转。

---

## 8.2 修复调度

### `__fix_instructions`
- **签名**: `static void __fix_instructions(uint32_t *__restrict inp, int32_t count, uint32_t *__restrict outp)`
- **位置**: `And64InlineHook.cpp:430-476`
- **可见性**: `static`（文件作用域）
- **参数**:
  - `inp`: 输入指令区（指向原函数开头）
  - `count`: 输入指令数（1 或 4 或 5）
  - `outp`: 输出指令区（指向 trampoline 槽位）
- **返回值**: `void`
- **副作用**:
  - 构造一个局部 `context ctx`
  - 依次尝试 4 个 fix 函数，对每条原指令
  - 未匹配的指令 `*outp++ = *inp++`
  - 末尾追加跳回原函数剩余部分（短 B 或长 LDR+BR+addr）
  - `__flush_cache(outp_base, total)` 清缓存
- **调用**: 被 `A64HookFunctionV` 调用 (`And64InlineHook.cpp:530`, `:556`)
- **调用了**:
  - `__fix_branch_imm()` (`:447`)
  - `__fix_cond_comp_test_branch()` (`:448`)
  - `__fix_loadlit()` (`:449`)
  - `__fix_pcreladdr()` (`:450`)
  - `ctx.process_fix_map()` / `ctx.get_and_set_current_index()` (`:453`)
  - `__flush_cache()` (宏，`:475`)
- **简要说明**: 调度器；按 B → cond → loadlit → pcreladdr 顺序尝试，每条指令只走一条分支，最后追加返回跳转。

---

## 8.3 四个 PC-relative 修复路由

### `__fix_branch_imm`
- **签名**: `static bool __fix_branch_imm(instruction inpp, instruction outpp, context *ctxp)`
- **位置**: `And64InlineHook.cpp:129-190`
- **可见性**: `static`
- **参数**:
  - `inpp`: 输入指令指针的指针（`uint32_t**`）
  - `outpp`: 输出指令指针的指针
  - `ctxp`: 修复上下文
- **返回值**: `bool` —— 匹配 B/BL 返回 true，否则 false
- **副作用**:
  - 修改 `*inpp`（前进 1）
  - 修改 `*outpp`（前进 1 或 4 或 5）
  - 可能写 NOP 对齐
  - 可能写 4 条或 5 条指令（LDR+BR+addr，必要时保留 LR）
  - 调用 `ctx->get_and_set_current_index`、`ctx->insert_fix_map`、`ctx->process_fix_map`
- **调用**: 被 `__fix_instructions` 调用 (`And64InlineHook.cpp:447`)
- **调用了**:
  - `ctxp->get_and_set_current_index()` (`:143`)
  - `ctxp->reset_current_ins()` (`:153`, `:162`)
  - `ctxp->is_in_fixing_range()` (`:146`)
  - `ctxp->get_ref_ins_index()` (`:172`)
  - `ctxp->insert_fix_map()` (`:176`)
  - `ctxp->process_fix_map()` (`:186`)
  - `memcpy` (`:157`, `:167`)
- **简要说明**: 处理 `B` (`0x14000000`) 和 `BL` (`0x94000000`)。BL 多保留一条 ADR 恢复 LR。

### `__fix_cond_comp_test_branch`
- **签名**: `static bool __fix_cond_comp_test_branch(instruction inpp, instruction outpp, context *ctxp)`
- **位置**: `And64InlineHook.cpp:194-254`
- **可见性**: `static`
- **参数**: 同 `__fix_branch_imm`
- **返回值**: `bool`
- **副作用**: 同 `__fix_branch_imm`，但展开 6 条指令模板
- **调用**: 被 `__fix_instructions` 调用 (`And64InlineHook.cpp:448`)
- **调用了**:
  - `ctxp->get_and_set_current_index()` (`:222`)
  - `ctxp->reset_current_ins()` (`:229`)
  - `ctxp->is_in_fixing_range()` (`:225`)
  - `ctxp->get_ref_ins_index()` (`:239`)
  - `ctxp->insert_fix_map()` (`:243`)
  - `ctxp->process_fix_map()` (`:253`)
  - `memcpy` (`:235`)
  - `__builtin_clz` (`:221`，用于计算 MSB)
- **简要说明**: 处理 `B.cond` (`0x54xxxxxx`)、`CBZ` (`0x34xxxxxx`)、`CBNZ` (`0x35xxxxxx`)、`TBZ` (`0x36xxxxxx`)、`TBNZ` (`0x37xxxxxx`)。条件分支需要"先 B.cond #8，然后 B #20，然后 LDR+BR+addr"共 6 条指令来跳转到任意地址。

### `__fix_loadlit`
- **签名**: `static bool __fix_loadlit(instruction inpp, instruction outpp, context *ctxp)`
- **位置**: `And64InlineHook.cpp:258-333`
- **可见性**: `static`
- **参数**: 同上
- **返回值**: `bool`
- **副作用**:
  - PRFM 直接跳过
  - LDR literal 改为"内嵌常量 + LDR #8 + B #skip"
  - 调用 `memcpy(absolute_addr, ...)` 读取原始常量
- **调用**: 被 `__fix_instructions` 调用 (`And64InlineHook.cpp:449`)
- **调用了**:
  - `ctxp->get_and_set_current_index()` (`:265`, `:301`)
  - `ctxp->reset_current_ins()` (`:310`, `:325`)
  - `ctxp->is_in_fixing_range()` (`:304`)
  - `ctxp->process_fix_map()` (`:265`, `:332`)
  - `memcpy` (`:317`)
- **简要说明**: 处理 `PRFM` (跳过)、`LDR (literal)` (`0x18xxxxxx`)、`LDR St/Dt/Qt (literal)` (`0x1cxxxxxx`)、`LDRSW (literal)` (`0x98xxxxxx`)。不展开为远跳转，而是把 literal 数据直接拷贝到 trampoline 中。

### `__fix_pcreladdr`
- **签名**: `static bool __fix_pcreladdr(instruction inpp, instruction outpp, context *ctxp)`
- **位置**: `And64InlineHook.cpp:337-426`
- **可见性**: `static`
- **参数**: 同上
- **返回值**: `bool`
- **副作用**:
  - ADR 处理：可内联或展开 LDR #8 + B #0xc + 8-byte addr
  - ADRP 处理：**目标在备份区间内时直接拷贝原指令（已知缺陷，行 404）**；目标在外时展开同 ADR
  - `A64_LOGI` / `A64_LOGE` 调试输出
- **调用**: 被 `__fix_instructions` 调用 (`And64InlineHook.cpp:450`)
- **调用了**:
  - `ctxp->get_and_set_current_index()` (`:356`, `:390`)
  - `ctxp->reset_current_ins()` (`:364`, `:409`)
  - `ctxp->is_in_fixing_range()` (`:360`, `:395`)
  - `ctxp->get_ref_ins_index()` (`:373`, `:396`)
  - `ctxp->insert_fix_map()` (`:377`)
  - `ctxp->process_fix_map()` (`:423`)
  - `A64_LOGI` (宏，`:393`, `:404`)
  - `A64_LOGE` (宏，`:400`)
  - `memcpy` (`:369`, `:414`)
- **简要说明**: 处理 `ADR` (`0x10xxxxxx`)、`ADRP` (`0x90xxxxxx`)。ADR 完全修复，ADRP 对"目标在备份内"的情况未处理（见 `04_data_flow.md`）。

---

## 8.4 入口辅助

### `FastAllocateTrampoline`
- **签名**: `static uint32_t *FastAllocateTrampoline()`
- **位置**: `And64InlineHook.cpp:498-510`
- **可见性**: `static`（extern "C" 块内）
- **参数**: 无
- **返回值**: 池中的下一个槽位指针；池耗尽返回 NULL
- **副作用**:
  - `__atomic_increase(&__index)`（原子自增计数器，初始 -1）
  - 越界 `A64_LOGE("failed to allocate trampoline!")`
- **调用**: 被 `A64HookFunction` 调用 (`And64InlineHook.cpp:581`)
- **调用了**:
  - `__atomic_increase` (宏，`:503`)
  - `__predict_true` (宏，`:504`)
  - `__countof` (宏，`:504`)
  - `A64_LOGE` (宏，`:508`)
- **简要说明**: 原子地从 `__insns_pool` 分配下一个槽位。

### `A64HookInit`（类）
- **签名**: `class A64HookInit { public: A64HookInit(); };`
- **位置**: `And64InlineHook.cpp:485-494`
- **可见性**: 类内 public 构造器，无继承
- **构造函数**: 
  - 调用 `__make_rwx(__insns_pool, sizeof(__insns_pool))`（把整个 12.5 页池设为 RWX）
  - `A64_LOGI("insns pool initialized.")`
- **副作用**: 修改 `__insns_pool` 页表项
- **调用**: 全局 `static A64HookInit __init` (`And64InlineHook.cpp:494`) 在 `.so` 加载时自动触发
- **调用了**:
  - `__make_rwx` (宏，`:490`)
  - `A64_LOGI` (宏，`:491`)
- **简要说明**: 利用 C++ 静态初始化机制，在 main() 之前完成 trampoline 池的 RWX 配置。

---

## 8.5 `context::` 方法（`struct context` 内联成员）

### `context::is_in_fixing_range`
- **签名**: `inline bool is_in_fixing_range(const int64_t absolute_addr)`
- **位置**: `And64InlineHook.cpp:74-76`
- **可见性**: public（struct 默认）
- **参数**: `absolute_addr` —— 待判断的绝对地址
- **返回值**: `bool` —— `addr ∈ [basep, endp)` 时 true
- **副作用**: 无
- **调用**: 被所有 4 个 fix 函数调用，判断目标是否在备份区间
- **调用了**: 无
- **简要说明**: 半开区间判断 `[basep, endp)`。

### `context::get_ref_ins_index`
- **签名**: `inline intptr_t get_ref_ins_index(const int64_t absolute_addr)`
- **位置**: `And64InlineHook.cpp:77-79`
- **可见性**: public
- **参数**: `absolute_addr` —— 原指令的绝对地址
- **返回值**: `intptr_t` —— 指令在 `dat[]` 中的下标 `(addr - basep) / 4`
- **副作用**: 无
- **调用**: 被 `__fix_branch_imm` (`:172`)、`__fix_cond_comp_test_branch` (`:239`)、`__fix_pcreladdr` (`:373`, `:396`) 调用
- **调用了**: 无
- **简要说明**: 地址 → 指令序号映射。

### `context::get_and_set_current_index`
- **签名**: `inline intptr_t get_and_set_current_index(uint32_t *__restrict inp, uint32_t *__restrict outp)`
- **位置**: `And64InlineHook.cpp:80-84`
- **可见性**: public
- **参数**:
  - `inp`: 当前输入指令指针
  - `outp`: 当前输出位置
- **返回值**: `intptr_t` —— 当前指令序号
- **副作用**: 把 `dat[current_idx].insp = outp`（让前向引用知道当前指令的最终位置）
- **调用**: 所有 fix 函数入口
- **调用了**: `get_ref_ins_index`
- **简要说明**: 双重作用：返回序号 + 注册当前位置。

### `context::reset_current_ins`
- **签名**: `inline void reset_current_ins(const intptr_t idx, uint32_t *__restrict outp)`
- **位置**: `And64InlineHook.cpp:85-87`
- **可见性**: public
- **参数**: `idx`, `outp` —— 序号 + 新的输出位置
- **返回值**: `void`
- **副作用**: 更新 `dat[idx].insp = outp`
- **调用**: 各 fix 函数插入 NOP 对齐后调用
- **调用了**: 无
- **简要说明**: 因为 NOP 改变了输出位置，前向引用需要重新定位。

### `context::insert_fix_map`
- **签名**: `void insert_fix_map(const intptr_t idx, uint32_t *bp, uint32_t ls = 0u, uint32_t ad = 0xffffffffu)`
- **位置**: `And64InlineHook.cpp:88-98`
- **可见性**: public
- **参数**:
  - `idx`: 目标指令的序号
  - `bp`: 指向输出区中需要回填的 uint32_t*（即某条待写指令的字段）
  - `ls`: 左移位数
  - `ad`: AND 掩码
- **返回值**: `void`
- **副作用**: 写入 `dat[idx].fmap[k]` 的第一个空槽
- **调用**: `__fix_branch_imm` (`:176`)、`__fix_cond_comp_test_branch` (`:243`)、`__fix_pcreladdr` (`:377`)
- **调用了**: 无
- **简要说明**: 延迟回填登记。当分支目标在更后面尚未处理时，先把"回填公式"记下来。

### `context::process_fix_map`
- **签名**: `void process_fix_map(const intptr_t idx)`
- **位置**: `And64InlineHook.cpp:99-105`
- **可见性**: public
- **参数**: `idx` —— 当前指令的序号
- **返回值**: `void`
- **副作用**: 遍历 `dat[idx].fmap[]`，对每个非空项执行 `*bp |= ((dat[idx].ins - bp) >> 2 << ls) & ad`，然后清空
- **调用**: 所有 fix 函数完成当前指令后
- **调用了**: 无
- **简要说明**: 把"指向本指令"的延迟回填执行掉（`dat[idx].ins` 是输出区绝对地址，`bp` 是输出区中待写字段）。

---

## 8.6 关键指令编码对照（用于读懂二进制）

| 助记符 | 编码 | 含义 |
|--------|------|------|
| `NOP` | `0xd503201f` | `A64_NOP` |
| `B imm` | `0x14000000 \| (imm26 & 0x03ffffff)` | ±128 MiB 相对跳转 |
| `BL imm` | `0x94000000 \| (imm26 & 0x03ffffff)` | ±128 MiB 相对链接跳转 |
| `LDR X17, #8` | `0x58000051` | 从 PC+8 加载 8 字节到 X17 |
| `LDR X17, #12` | `0x58000071` | 从 PC+12 加载 8 字节到 X17 |
| `LDR X0, #8` | `0x58000040` | 从 PC+8 加载 8 字节到 X0（BL 远跳转里 ADR X30 用） |
| `BR X17` | `0xd61f0220` | 间接跳转 X17 |
| `ADR X30, #16` | `0x1000009e` | 把 PC+16 写入 LR（BL 远跳转恢复 LR） |
| `B.cond #8` | `(8 >> 2) << 5 = 0x40` 编码到 imm19 字段 | 条件分支跳过 LDR+BR |
| `B #0x14` | `0x14000005` | 条件分支模板中跳过 5 条指令 |
| `B #0x10` | `0x14000004` | LDR+BR+addr 模板中跳过 4 条 |
| `B #0xc` | `0x14000003` | ADRP/loadlit 模板中跳过 3 条 |
| `B #0x8` | `0x14000002` | LDR+addr 模板中跳过 2 条 |