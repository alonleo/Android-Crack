# 07 · 函数索引总表

> 项目内全部函数 / 方法 / 全局符号清单。详见 [08_functions_detail.md](08_functions_detail.md)。

## 7.1 公开 API（`And64InlineHook.hpp`）

| 函数 | 签名 | 行号 |
|------|------|------|
| `A64HookFunction` | `void(void *const symbol, void *const replace, void **result)` | `.hpp:36` |
| `A64HookFunctionV` | `void *(void *const symbol, void *const replace, void *const rwx, const uintptr_t rwx_size)` | `.hpp:37-38` |

## 7.2 内部函数（`And64InlineHook.cpp`）

### 修复路由（`static`）

| 函数 | 签名 | 行号 |
|------|------|------|
| `__fix_branch_imm` | `bool(instruction, instruction, context *)` | `129-190` |
| `__fix_cond_comp_test_branch` | `bool(instruction, instruction, context *)` | `194-254` |
| `__fix_loadlit` | `bool(instruction, instruction, context *)` | `258-333` |
| `__fix_pcreladdr` | `bool(instruction, instruction, context *)` | `337-426` |
| `__fix_instructions` | `void(uint32_t *__restrict, int32_t, uint32_t *__restrict)` | `430-476` |

### 入口 / 分配（`extern "C"` 块内）

| 函数 / 类 | 签名 | 行号 |
|------|------|------|
| `A64HookInit`（构造器） | `class` 无 public 方法 | `485-494` |
| `__init`（static 实例） | `static A64HookInit` | `494` |
| `FastAllocateTrampoline` | `static uint32_t *()` | `498-510` |
| `A64HookFunctionV` | `void *(symbol, replace, rwx, rwx_size)` | `514-573` |
| `A64HookFunction` | `void(symbol, replace, result)` | `577-593` |

## 7.3 `context::` 方法（`struct` 内）

| 方法 | 签名 | 行号 |
|------|------|------|
| `is_in_fixing_range` | `bool(int64_t)` inline | `74-76` |
| `get_ref_ins_index` | `intptr_t(int64_t)` inline | `77-79` |
| `get_and_set_current_index` | `intptr_t(uint32_t *__restrict, uint32_t *__restrict)` inline | `80-84` |
| `reset_current_ins` | `void(intptr_t, uint32_t *__restrict)` inline | `85-87` |
| `insert_fix_map` | `void(intptr_t, uint32_t *, uint32_t, uint32_t)` | `88-98` |
| `process_fix_map` | `void(intptr_t)` | `99-105` |

## 7.4 宏（预处理期）

| 宏 | 行号 | 作用 |
|----|------|------|
| `A64_MAX_INSTRUCTIONS` | `40` | 单次 hook 最多备份的指令数 = 5 |
| `A64_MAX_REFERENCES` | `41` | `= 2 * A64_MAX_INSTRUCTIONS` = 10 |
| `A64_MAX_BACKUPS` | `30` (hpp) | 同时在线 hook 数 = 256 |
| `A64_NOP` | `42` | `0xd503201f` (NOP) |
| `A64_JNIEXPORT` | `43` | `__attribute__((visibility("default")))` |
| `A64_LOGE` | `44` | 错误日志到 logcat tag `A64_HOOK` |
| `A64_LOGI` | `46`/`48` | 信息日志（NDEBUG 时变空） |
| `__intval(p)` | `110` | `reinterpret_cast<intptr_t>(p)` |
| `__uintval(p)` | `111` | `reinterpret_cast<uintptr_t>(p)` |
| `__ptr(p)` | `112` | `reinterpret_cast<void *>(p)` |
| `__page_size` | `113` | `4096` |
| `__page_align(n)` | `114` | 上对齐到 4K |
| `__ptr_align(x)` | `115` | 向下对齐到页边界 |
| `__align_up(x, n)` | `116` | 通用向上对齐 |
| `__align_down(x, n)` | `117` | 通用向下对齐（要求 n 为 2 的幂） |
| `__countof(x)` | `118` | 数组元素数（signed） |
| `__atomic_increase(p)` | `119` | `__sync_add_and_fetch(p, 1)` |
| `__sync_cmpswap(p, v, n)` | `120` | CAS |
| `__predict_true(exp)` | `121` | `__builtin_expect((exp) != 0, 1)` |
| `__flush_cache(c, n)` | `122` | `__builtin___clear_cache(c, c + n)` |
| `__make_rwx(p, n)` | `123-125` | `mprotect(p & ~0xFFF, ..., RWX)` |

## 7.5 全局符号

| 符号 | 类型 | 行号 | 作用 |
|------|------|------|------|
| `__insns_pool` | `static uint32_t[256][50]` | `481` | 静态 trampoline 池（12.5 页，构造时 mprotect RWX） |
| `__init` | `static A64HookInit` | `494` | 静态触发构造器 |
| `__index` (内嵌于 `FastAllocateTrampoline`) | `static volatile int32_t = -1` | `501` | 槽位计数器 |

## 7.6 类型

| 类型 | 定义 | 行号 |
|------|------|------|
| `instruction` (typedef) | `uint32_t *__restrict *__restrict` | `50` |
| `struct context::fix_info` | `{ uint32_t *bp; uint32_t ls; uint32_t ad; }` | `53-58` |
| `struct context::insns_info` | `{ union { ... }; fix_info fmap[10]; }` | `59-68` |
| `struct context` | 完整修复工作台 | `51-106` |
| `class A64HookInit` | 空体构造器 | `485-494` |

## 7.7 文件统计

| 文件 | 总行数 | 函数 / 类 / 宏条目 |
|------|--------|------------------|
| `And64InlineHook.hpp` | 41 | 2 函数 + 1 宏 |
| `And64InlineHook.cpp` | 596 | 11 函数 + 1 类 + 22 宏 |
| 合计 | 637 | 13 函数 + 1 类 + 23 宏 |