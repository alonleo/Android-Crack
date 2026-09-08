# 08 · 函数详细说明（库实现层 - Ihook.h / Ihook.c）

> 本文件覆盖 `jni/InlineHook/Ihook.h` + `jni/InlineHook/Ihook.c` 全部 8 个函数。

---

## `ChangePageProperty`
- **签名**: `bool ChangePageProperty(void *pAddress, size_t size)`
- **位置**: `InlineHook/Ihook.h:54`（声明）/ `InlineHook/Ihook.c:12-42`（定义）
- **可见性**: 普通 extern 函数（无 `static`）
- **参数**:
  - `pAddress`: 待修改属性的内存起始地址
  - `size`: 字节数
- **返回值**: `bool` —— 成功 true，pAddress==NULL 或 mprotect 失败 false
- **副作用**:
  - `sysconf(_SC_PAGESIZE)` 获取页大小（每次调用）
  - `mprotect(...)` 修改页属性为 RWX
  - 循环 `lPageCount = size / page_size + 1` 次 mprotect，每次一页
- **调用**: 被 `BuildStub` (`Ihook.c:172`)、`BuildOldFunction` (`Ihook.c:294`)、`RebuildHookTarget` (`Ihook.c:345`) 调用
- **调用了**: `sysconf` (`Ihook.c:23`), `mprotect` (`:32`), `__android_log_print` (`:35`)
- **简要说明**: 把任意内存区域改为 RWX。**注意**：每次只 mprotect 一页且按 `(size/page_size)+1` 计算，跨页或 size=0 时可能漏改。

---

## `GetModuleBaseAddr`
- **签名**: `void *GetModuleBaseAddr(pid_t pid, char *pszModuleName)`
- **位置**: `InlineHook/Ihook.h:56`（声明）/ `InlineHook/Ihook.c:50-101`（定义）
- **可见性**: `extern`（h 头声明）
- **参数**:
  - `pid`: 目标进程 pid，< 0 时解析自身
  - `pszModuleName`: 目标模块名（如 "libhellojni.so"）
- **返回值**: `void *` —— 模块基址，失败时 0
- **副作用**:
  - 打开 `/proc/<pid>/maps` 或 `/proc/self/maps`
  - 顺序扫描查找模块名（首次匹配）
  - `strtoul` 解析起始地址
  - 特殊处理：值为 0x8000 时归零
- **调用**: 被 `ModifyIBored` (`Interface/InlineHook.cpp:123`) 调用
- **调用了**: `getpid` (`Ihook.c:56`), `snprintf` (`:63`, `:67`), `fopen` (`:70`), `fgets` (`:80`), `strstr` (`:84`), `strtok` (`:87`), `strtoul` (`:90`), `fclose` (`:99`), `__android_log_print` (多处)
- **简要说明**: 通过解析 `/proc/pid/maps` 获取模块加载基址。**已知问题**：找到第一个匹配即返回，多个同名库（如 main + chrome 子进程）会取错。

---

## `InitArmHookInfo`
- **签名**: `bool InitArmHookInfo(INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `InlineHook/Ihook.h:58`（声明）/ `InlineHook/Ihook.c:108-138`（定义）
- **可见性**: 普通 extern
- **参数**: `pstInlineHook` —— 预填了 `pHookAddr`、`onCallBack` 的结构体指针
- **返回值**: `bool` —— 总是返回 true（除非 pstInlineHook==NULL 走另一路径）
- **副作用**:
  - 把 `pHookAddr` 的 24 字节 memcpy 到 `szbyBackupOpcodes`
  - 6 次循环调用 `lengthFixArm64(*currentOpcode)`，写入 `backUpFixLengthList[i]`
  - 设置 `backUpLength = 24`
- **调用**: 被 `HookArm` (`Ihook.c:389`) 调用
- **调用了**: `lengthFixArm64` (`Ihook.c:133`), `lengthFixArm32` (`Ihook.c:132`, 死代码), `memcpy` (`:127`), `__android_log_print` (多处)
- **简要说明**: 备份 hook 点 24 字节原指令 + 分类每条指令的修复后长度。**注意**：当前代码 `currentOpcode += 1` 实际只前进 4 字节，6 次循环处理 24 字节。代码注释提到 "GToad BUG" 但实际修复了。

---

## `BuildStub`
- **签名**: `bool BuildStub(INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `InlineHook/Ihook.h:60`（声明）/ `InlineHook/Ihook.c:145-198`（定义）
- **可见性**: 普通 extern
- **参数**: `pstInlineHook`
- **返回值**: `bool` —— 成功 true（malloc 失败、mprotect 失败返回 false）
- **副作用**:
  - `malloc(sShellCodeLength)` 分配 stub 内存
  - `ChangePageProperty(stub, RWX)` 改页属性
  - `memcpy(stub, _shellcode_start_s, sShellCodeLength)` 复制汇编模板
  - `*ppHookStubFunctionAddr = onCallBack` 修补回调地址
  - 设置 `pstInlineHook->ppOldFuncAddr`、`pStubShellCodeAddr`
- **调用**: 被 `HookArm` (`Ihook.c:399`) 调用
- **调用了**: `malloc` (`Ihook.c:164`), `ChangePageProperty` (`:172`), `memcpy` (`:170`), `__android_log_print` (多处)
- **简要说明**: 把 ihookstub.s 汇编模板复制到 malloc 内存并修补 callback 槽。

---

## `BuildArmJumpCode`
- **签名**: `bool BuildArmJumpCode(void *pCurAddress, void *pJumpAddress)`
- **位置**: `InlineHook/Ihook.h:62`（声明）/ `InlineHook/Ihook.c:207-253`（定义）
- **可见性**: 普通 extern
- **参数**:
  - `pCurAddress`: 当前地址（要写入跳转的位置）
  - `pJumpAddress`: 目标地址（要跳转过去）
- **返回值**: `bool` —— 成功 true（NULL 参数返回 false）
- **副作用**:
  - 构造 24 字节跳转 `szLdrPCOpcodes[24]`
  - `memcpy(pCurAddress, szLdrPCOpcodes, 24)` 写入
  - **未调用** `__builtin___clear_cache`（已知缺陷，见行 244-246 注释）
- **调用**: 被 `BuildOldFunction` (`Ihook.c:306`)、`RebuildHookTarget` (`Ihook.c:352`) 调用
- **调用了**: `memcpy` (`Ihook.c:234`, `:242`), `__android_log_print` (多处)
- **简要说明**: 写入 24 字节 ARM64 长跳转（STP X1,X0 + LDR X0,8 + BR X0 + addr + LDR X0,[sp,-8]）。

### 24 字节布局

| 偏移 | 指令 / 数据 | 编码 |
|------|-------------|------|
| +0 | STP X1, X0, [SP, #-0x10] | `0xe1 0x03 0x3f 0xa9` |
| +4 | LDR X0, 8 | `0x40 0x00 0x00 0x58` |
| +8 | BR X0 | `0x00 0x00 0x1f 0xd6` |
| +12 | pJumpAddress (8 bytes) | little-endian |
| +20 | LDR X0, [SP, -0x8] | `0xe0 0x83 0x5f 0xf8` |

---

## `BuildOldFunction`
- **签名**: `bool BuildOldFunction(INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `InlineHook/Ihook.h:64`（声明）/ `InlineHook/Ihook.c:263-322`（定义）
- **可见性**: 普通 extern
- **参数**: `pstInlineHook`
- **返回值**: `bool` —— 成功 true（mmap/malloc/mprotect/BuildArmJumpCode 任一失败返回 false）
- **副作用**:
  - `mmap(NULL, PAGE_SIZE, RWX, ANON|PRIVATE)` 分配修复缓冲（**不释放，泄漏**）
  - `malloc(200)` 分配 pNewEntryForOldFunction
  - `ChangePageProperty(..., 200, RWX)` 改页属性
  - `fixPCOpcodeArm(fixOpcodes, pstInlineHook)` 生成修复指令
  - `memcpy(pNewEntryForOldFunction, fixOpcodes, fixLength)` 拷贝
  - `BuildArmJumpCode(pNewEntryForOldFunction + fixLength, pHookAddr + backUpLength - 4)` 追加跳转
  - `*ppOldFuncAddr = pNewEntryForOldFunction` 修补 stub 内的旧函数地址
- **调用**: 被 `HookArm` (`Ihook.c:410`) 调用
- **调用了**: `mmap` (`Ihook.c:271`), `malloc` (`:283`), `ChangePageProperty` (`:294`), `fixPCOpcodeArm` (`:301`), `memcpy` (`:302`), `BuildArmJumpCode` (`:306`), `__android_log_print` (多处)
- **简要说明**: 构造"修复后的旧函数入口"。`pHookAddr + backUpLength - 4` 是因为 BR 跳转会跳到原 insn[6]（即备份区间最后一条指令之后）。

---

## `RebuildHookTarget`
- **签名**: `bool RebuildHookTarget(INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `InlineHook/Ihook.h:66`（声明）/ `InlineHook/Ihook.c:331-364`（定义）
- **可见性**: 普通 extern
- **参数**: `pstInlineHook`
- **返回值**: `bool` —— 成功 true
- **副作用**:
  - `ChangePageProperty(pHookAddr, 24, RWX)` 改 hook 点页属性
  - `BuildArmJumpCode(pHookAddr, pStubShellCodeAddr)` 写入 24 字节跳转
- **调用**: 被 `HookArm` (`Ihook.c:420`) 调用
- **调用了**: `ChangePageProperty` (`Ihook.c:345`), `BuildArmJumpCode` (`:352`), `__android_log_print` (多处)
- **简要说明**: 把 hook 点改写为 24 字节长跳转，跳到 stub。**注意**：调用前**未检查** hook 点是否已被 mmap 别处占用。

---

## `HookArm`
- **签名**: `bool HookArm(INLINE_HOOK_INFO *pstInlineHook)`
- **位置**: `InlineHook/Ihook.h:68`（声明）/ `InlineHook/Ihook.c:372-433`（定义）
- **可见性**: `extern`（头声明）
- **参数**: `pstInlineHook`
- **返回值**: `bool` —— 4 步全部成功 true，任一失败 false
- **副作用**: 调用 4 步（`InitArmHookInfo` → `BuildStub` → `BuildOldFunction` → `RebuildHookTarget`），任一失败 break 出 while 循环
- **调用**: 被 `InlineHook` (`Interface/InlineHook.cpp:50`) 调用
- **调用了**: `InitArmHookInfo` (`Ihook.c:389`), `BuildStub` (`:399`), `BuildOldFunction` (`:410`), `RebuildHookTarget` (`:420`), `__android_log_print` (多处)
- **简要说明**: 顶层编排。4 步顺序执行，任一失败立即中止。失败时不回滚已分配的 stub / old entry（**已知问题**：可能导致泄漏）。