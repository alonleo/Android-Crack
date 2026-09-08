# 10 — 术语表

## Rust / Tauri

| 术语 | 含义 |
|------|------|
| **Tauri 2** | Rust 后端 + Web 前端的桌面/移动端 shell |
| **`#[tauri::command]`** | 把 Rust 函数注册为可被前端 `invoke()` 调用的命令 |
| **`tauri::Emitter`** | 用来 emit 事件到前端 |
| **`AppHandle`** | Tauri 句柄，用来 emit / 获取 state |
| **`tauri::State<'_, T>`** | 通过 `manage()` 注册的共享状态 |
| **`Mutex`** | 同步原语 |
| **`mpsc::channel`** | 多生产者单消费者 channel，用于 `input_sender` |
| **`catch_unwind`** | panic-safe wrapper，跨 panic boundary 把 panic 转为 `Result` |
| **`AssertUnwindSafe`** | 标注 `catch_unwind` 内部 unsafe 访问合法 |
| **RAII (`impl Drop`)** | 资源获取即初始化；本项目 `DumpGuard` 用 RAII 自动清 `dump_running` 标志 |

## Svelte 5

| 术语 | 含义 |
|------|------|
| **Runes** | Svelte 5 新响应式 API（`$state`、`$derived`、`$effect`、`$props`） |
| **`$state<T>(initial)`** | 声明组件局部响应式状态 |
| **`$derived(expr)`** | 派生值（computed） |
| **`$effect(() => { ... })`** | 副作用（onMount 等价物） |
| **Svelte stores** | `writable` / `readable` / `derived`，跨组件共享状态 |
| **`subscribe`** | 监听 store 变化 |
| **`bind:`** | 双向绑定 |
| **`onclick={...}`** | Svelte 5 风格事件处理器 |

## Binary Format

| 术语 | 含义 |
|------|------|
| **VA / RVA** | 虚拟地址 / 相对虚拟地址（VA = RVA + ImageBase） |
| **PT_LOAD / PT_DYNAMIC** | ELF PHDR 类型 |
| **R_ARM_ABS32 / R_AARCH64_ABS64 / R_AARCH64_RELATIVE** | ELF relocation |
| **R_386_32 / R_X86_64_64 / R_X86_64_RELATIVE** | x86/x64 relocation |
| **GNU_HASH** | ELF 动态哈希表 |
| **__mod_init_func** | Mach-O section：模块初始化函数数组 |
| **CODE/DATA signature** | Mach-O LC_CODE_SIGNATURE / LC_DYLD_INFO |
| **NSO LZ4** | NSO 三段可独立 LZ4 压缩 |
| **WASM data section (id=11)** | WASM 线性内存数据 |

## il2cpp 概念

参见 Il2CppDumper 文档的 `10_glossary.md`。本项目关键新增：

| 术语 | 含义 |
|------|------|
| **v104 / v106 CODM** | CODM 内部混淆 il2cpp 版本；rodroid 自动检测 |
| **CODM diag** | `Elf::new_with_codm_diag` — 容忍坏指针的 ELF 解析模式 |
| **CODM fixups** | `MachO::new_with_codm_fixups` — 应用 iOS chained fixups |
| **Auto-XOR** | 自动尝试 7 种 XOR 方案解密 metadata |
| **genericAdjustorThunks** | v24.5/v27.1 新增；为泛型方法提供 adjustor thunk |
| **typeHandle (v27+)** | Runtime pointer to Il2CppClass，从 typeHandle 反推 typeDef index |
| **FieldRVA** | 字段的 RVA，直接指向 binary 数据（如 byte[] 常量） |
| **thread-static** | [ThreadStatic] 标记的静态字段，运行时存放在独立 slot |

## 配置 (Config)

| 字段 | 类型 | 默认 | 效果 |
|------|------|------|------|
| `splitDumpPerType` | bool | true（GUI） | dump.cs 拆为 `DiffableCs/<Type>.cs` |
| `generateGenericsDump` | bool | true | 写 `generics_dump.txt` |
| `dumpGenerics{Rgctx,MethodSpecs,CustomAttributes,StringLiterals,MetadataUsages,Vtables,Interfaces}` | bool | true | 7 个子段开关 |
| `dumpDisassembly` | bool | false | 启用 V5 disassembler |
| `dumpDisassemblyTarget` | u8 | 0 | 0=Both, 1=Flat, 2=Split |
| `maxDisassemblyInstructions` | usize | 512 | 每个方法最多反汇编指令数 |
| `generateCppScaffold` | bool | true | C++ headers |
| `mangleNames` | bool | true | MSVC/GCC mangling |
| `enhancedIdaMetadata` | bool | true | 增强 IDA 元数据 |
| `generateUnityHeaders` | bool | true | 用嵌入的 Unity 原生头 |
| `compilerLayout` | String | "GCC" | GCC / MSVC |
| `useTopologicalSort` | bool | true | C++ header 拓扑排序 |
| `codm` | bool | false | CODM 模式 |
| `dumpStaticFieldMetadata` | bool | false | `static_metadata.json` |
| `dumpFieldRvaData` | bool | false | hex dump FieldRVA |
| `maxFieldRvaDumpBytes` | usize | 4096 | cap |

## 输出

```
Dump<N>/
├── dump.cs                          C# 反编译
├── DiffableCs/<Type>.cs             splitDumpPerType
├── il2cpp.h                         C 结构
├── script.json
├── stringliteral.json
├── generics_dump.txt                7 子段
├── static_metadata.json             thread-static + FieldRVA
├── unity-types.h / unity-api.h      generateUnityHeaders
├── cpp_scaffold/*.hpp               generateCppScaffold
├── CMakeLists.txt                   cpp_scaffolding::write_project
└── DummyDll/<ImageName>.dll         generateDummyDll
```

## V5 Disassembler Annotations

| 注解 | 触发条件 |
|------|---------|
| string literal | RVA 在 string literal 表中 |
| method ref | RVA 命中 method pointer |
| field ref | RVA 命中 field ref |
| type info | RVA 命中 Il2CppClass handle |
| boxing | 调用 String.Concat / Box helper |
| unboxing | 调用 Unbox helper |
| static field | 读写 static 字段 |
| object new | 调用 Object..ctor / GC.Alloc |
| switch table | 多分支跳转 |

## CODM (Call of Duty: Mobile)

CODM 内部对 il2cpp 做额外混淆：
- 部分 metadata 字段被 XOR
- 部分指针被加密
- 部分 layout 大小有微调

rodroid 通过 `MetadataVariant::Codm` 自动识别并切换到 `load_metadata_codm` + `new_with_codm_diag` + `new_with_codm_fixups` 三套兼容路径。

## Tauri 事件

| 事件 | Payload | 触发时机 |
|------|---------|---------|
| `dump-log` | `{ message }` | 每条日志 |
| `dump-input-request` | `{ prompt_type }` | 需要用户输入 |
| `dump-complete` | `{ success, output_path, error_message }` | 结束（正常） |
| `dump-crash` | `{ crash_log }` | panic 捕获 |

## 常见 Pitfall

1. **dump.cs 为空但 DiffableCs 有内容**：`splitDumpPerType=true` 时 dump.cs 只含注释；需要看 `DiffableCs/`。
2. **V5 disassembler 慢**：`dumpDisassembly=true` + `maxDisassemblyInstructions=512` 在大项目下显著拖慢。
3. **C++ scaffold 编译错**：`compilerLayout=GCC` 默认；如用 MSVC，需要切到 `"MSVC"`。
4. **CODM dump 卡住**：`codm=true` 应仅在 CODM 二进制上启用；其他游戏可能误判。