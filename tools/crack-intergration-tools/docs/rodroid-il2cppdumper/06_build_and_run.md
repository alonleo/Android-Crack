# 06 构建、运行与配置

## 桌面开发

```bash
cd rodroid-il2cppdumper
pnpm install
pnpm tauri dev        # 打开桌面窗口
```

## 桌面打包

```bash
pnpm tauri build      # 输出到 src-tauri/target/release/bundle/
```

产物：
- Windows：`Rodroid-Il2CppDumper-setup.exe`
- macOS：`.dmg`
- Linux：`.AppImage`

## 移动开发

```bash
pnpm tauri android init
pnpm tauri android dev     # Android 模拟器/真机
pnpm tauri android build   # 出 .apk / .aab

pnpm tauri ios init
pnpm tauri ios dev
pnpm tauri ios build       # 出 .ipa
```

## CLI 模式

rodroid 本仓库**仅 GUI**。Rust 库 `rodroid_il2cppdumper_lib` 暴露 `run()`，被 `main.rs` 调用。如果需要 CLI，复用 `lib.rs` 内部的 `run_dump` 写一个独立的 CLI 包装即可（社区常见做法）。

## 配置（Rust）

`src-tauri/config.json` 是默认 dump 配置（仅在 CLI 调用时使用，GUI 通过 `start_dump` 的 `configJson` 参数覆盖）。完整字段见 `07_functions_index.md` 与 `config.rs:5`。

前端 `src/lib/types.ts` 的 `DumperConfig` 镜像 Rust `Config` 结构（camelCase）。

## Tauri 命令

通过 `@tauri-apps/api` 在前端调用：

```ts
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';

await invoke('detect_binary', { path: '/path/to/binary' });
// 返回 { format: 'ELF', unity_version: '2021.3.16f1' }

await invoke('start_dump', {
    binaryPath: '/path/to/libil2cpp.so',
    metadataPath: '/path/to/global-metadata.dat',
    outputDir: '/path/to/output',
    configJson: JSON.stringify(config),
});

// 订阅事件
const unlistenLog = await listen<{ message: string }>('dump-log', (e) => {
    logs.update(arr => [...arr, e.payload.message]);
});

await invoke('submit_input', { response: '0x1234' });

const defaultConfig = await invoke('get_default_config');
```

## Tauri 事件订阅

```ts
// dumpEvents.ts
import { listen, emit } from '@tauri-apps/api/event';

listen<{ message: string }>('dump-log', (e) => { /* append */ });
listen<{ prompt_type: string }>('dump-input-request', (e) => { /* show dialog */ });
listen<{ success, output_path, error_message }>('dump-complete', (e) => { /* result */ });
listen<{ crash_log: string }>('dump-crash', (e) => { /* crash screen */ });
```

## Capabilities（`src-tauri/capabilities/default.json`）

Tauri 2 的权限声明。默认包含：
- `core:default`
- `dialog:default`（文件选择）
- `fs:default`（读 metadata / 写 output）
- `opener:default`（打开生成的文件夹）
- `os:default`

## 输出目录结构

```
<outputDir>/Dump<N>/
├── dump.cs                          C# 反编译（若 splitDumpPerType=true 时为空或只含注释）
├── DiffableCs/
│   ├── <TypeName>.cs                每个类型一个文件
│   └── ...
├── il2cpp.h                         C 结构
├── script.json
├── stringliteral.json
├── generics_dump.txt                7 个子段
├── static_metadata.json             若 dumpStaticFieldMetadata=true
├── cpp_scaffold/                    若 generateCppScaffold=true
│   ├── UnityApi.hpp
│   ├── UnityTypes.hpp
│   ├── UnityStructs.hpp
│   ├── UnityEnums.hpp
│   ├── GameClasses.hpp
│   └── ForwardDeclarations.hpp
├── unity-types.h                    若 generateUnityHeaders=true（嵌入资源）
├── unity-api.h                      同上
├── DummyDll/                        若 generateDummyDll=true
│   ├── Assembly-CSharp.dll
│   └── ...
└── ida.py / ghidra.py               embedded_scripts
```

## 主要 Config 字段速查

| 字段 | 默认 | 效果 |
|------|------|------|
| `dumpMethod` | true | 输出方法 |
| `dumpField` | true | 输出字段 |
| `dumpProperty` | true | 输出属性（不同于 C# 版默认 false） |
| `dumpAttribute` | true | 还原 attribute |
| `dumpMethodOffset` | true | RVA/Offset 注释 |
| `dumpFieldOffset` | true | 字段偏移 |
| `dumpTypeDefIndex` | true | TypeDefIndex 注释 |
| `dumpAssemblyName` | true | assembly 注释 |
| `generateStruct` | true | 写 il2cpp.h |
| `generateDummyDll` | true | 写 DummyDll |
| `dummyDllAddToken` | true | 加 [Token(...)] |
| `requireAnyKey` | true | （CLI 才用） |
| `forceIl2CppVersion` | false | 强制版本 |
| `forceVersion` | 24.3 | |
| `forceDump` | false | dump 模式 |
| `noRedirectedPointer` | false | 不重写 ELF pointer |
| `splitDumpPerType` | true（GUI） | DiffableCs 拆分 |
| `generateGenericsDump` | true | 写 generics_dump.txt |
| `dumpGenericsRgctx` | true | |
| `dumpGenericsMethodSpecs` | true | |
| `dumpGenericsCustomAttributes` | true | |
| `dumpGenericsStringLiterals` | true | |
| `dumpGenericsMetadataUsages` | true | |
| `dumpGenericsVtables` | true | |
| `dumpGenericsInterfaces` | true | |
| `dumpDisassembly` | false | 启用 V5 disassembler |
| `dumpDisassemblyTarget` | 0 | 0=Both, 1=Flat, 2=Split |
| `dumpDisassemblyHexBytes` | true | 十六进制字节 |
| `dumpDisassemblyFieldNames` | true | 字段名 |
| `dumpDisassemblyAnnotations` | true | 注解 |
| `dumpDisassemblyCfg` | true | CFG |
| `maxDisassemblyInstructions` | 512 | |
| `generateCppScaffold` | true | 写 C++ headers |
| `mangleNames` | true | GCC/Itanium mangling |
| `enhancedIdaMetadata` | true | |
| `generateUnityHeaders` | true | |
| `compilerLayout` | "GCC" | GCC / MSVC |
| `useTopologicalSort` | true | C++ header dep 排序 |
| `codm` | false | CODM 模式 |
| `dumpStaticFieldMetadata` | false | |
| `dumpFieldRvaData` | false | |
| `maxFieldRvaDumpBytes` | 4096 | |