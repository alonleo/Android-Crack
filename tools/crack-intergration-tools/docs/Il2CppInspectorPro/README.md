# Il2CppInspectorPro 深度文档

> Source: [`/home/leo/文档/android-crack/tools/source-projects/Il2CppInspectorPro`](../../Il2CppInspectorPro/)
> Version: **2026.1** (per `Directory.Build.props`)
> Target framework: **.NET 10.0** (Common/CLI/Redux); **net10.0-windows** (legacy WPF GUI)
> Authors: Katy Coe · LukeFZ · Jadis0x
> License: AGPL-3.0 (`Il2CppInspector.Common`, CLI/GUI), MIT (`VersionedSerialization*`)
> Inventory baseline: `/tmp/il2cppinspectorpro-inventory/inventory.md` (1377 LOC, verified against source)

## 文档导航

| 文件 | 内容 |
|------|------|
| [01_overview.md](01_overview.md) | 项目定位、与 Il2CppDumper/Il2CppInspectorRedux 的关系、技术栈 |
| [02_directory_tree.md](02_directory_tree.md) | 完整目录树 + 注释 |
| [03_architecture.md](03_architecture.md) | 整体架构（2 张 mermaid：模块依赖 + 启动流程） |
| [04_data_flow.md](04_data_flow.md) | 核心数据结构（Binary/Metadata/TypeModel/TypeInfo）+ 数据生命周期 |
| [05_operation_chains.md](05_operation_chains.md) | 10 条主要操作链（每条配 mermaid） |
| [06_build_and_run.md](06_build_and_run.md) | 编译、运行、CLI 参数、插件加载 |
| [07_functions_index.md](07_functions_index.md) | 函数索引总表（≥ 400 行） |
| `08_functions_detail/` | 按子项目拆分的函数详细说明 |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表 |

### 08 函数详细文档（12 个文件）

| 文件 | 覆盖范围 |
|------|---------|
| [common_core.md](08_functions_detail/common_core.md) | `Il2CppBinary` / `Metadata` / `Il2CppInspector` / `TypeModel` / `TypeInfo` / `ImageScan` |
| [common_outputs.md](08_functions_detail/common_outputs.md) | `CSharpCodeStubs` / `AssemblyShims` / `CppScaffolding` / `JSONMetadata` / `PythonScript` |
| [common_cpp.md](08_functions_detail/common_cpp.md) | `CppDeclarationGenerator` / `CppTypeCollection` / `CppType` / `MangledNameBuilder` / `UnityHeaders` |
| [common_fileformats.md](08_functions_detail/common_fileformats.md) | `FileFormatStream` / `PEReader` / `ElfReader` / `MachOReader` / `NsoReader` / `APKReader` 等 |
| [common_plugins.md](08_functions_detail/common_plugins.md) | `PluginManager` / `PluginHooks` / V100 `IPlugin` / `ILoadPipeline` |
| [cli.md](08_functions_detail/cli.md) | `Il2CppInspector.CLI/Program.cs` + `PluginOptions` + `PathUtils` |
| [gui_legacy.md](08_functions_detail/gui_legacy.md) | WPF `MainWindow.xaml.cs` + `App.xaml.cs` + 对话框 |
| [redux_cli.md](08_functions_detail/redux_cli.md) | Redux CLI host + `CliClient` + `ProcessCommand` |
| [redux_frontendcore.md](08_functions_detail/redux_frontendcore.md) | `UiContext` / `UiClient` / `Il2CppHub` / `IOutputFormat` |
| [redux_gui.md](08_functions_detail/redux_gui.md) | Redux GUI host + `UiProcessService` |
| [redux_gui_ui.md](08_functions_detail/redux_gui_ui.md) | Tauri (Rust) + Svelte/TS 前端 |
| [versioned_serialization.md](08_functions_detail/versioned_serialization.md) | `VersionedSerialization` + Roslyn 生成器 |
| [tests.md](08_functions_detail/tests.md) | `Il2CppTests` 测试集 |

## 一句话定位

Il2CppInspectorPro 是一个 **IL2CPP 二进制 → 反编译辅助产物** 的全链路工具：解析 `libil2cpp.so` / `GameAssembly.dll` / NSO 等原生映像 + `global-metadata.dat` 元数据 → 重建 .NET 类型模型 → 输出 C# 桩代码、C++ DLL 注入骨架、IDA/Ghidra/BinaryNinja 脚本、dummy .NET DLL、JSON 元数据。

## 与同类的对比

| 工具 | 输出 | il2cpp 版本 | plugin | 自带 GUI | C++ 注入模板 |
|------|------|-------------|--------|----------|--------------|
| **Il2CppDumper** (perfare) | dummy DLL + JSON | v16–v24 | × | × | × |
| **Il2CppInspector** (djkaty 原版) | C# stub + IDA.py + JSON | v16–v27 | × | WPF | × |
| **Il2CppInspectorRedux** (LukeFZ) | 上者 + C++ DLL 注入 | v16–v29+ | × | × | √ |
| **Il2CppInspectorPro** (Jadis0x) | 上者 + Tauri UI + 多输出聚合 + 名称混淆复原 | v16–v38+（含 v40/v41 via `Next/`） | √ | Tauri+Svelte | √ |

> 注：`Bin2Object` 是 git submodule，当前工作树未初始化（空目录），文档中相关章节已标注「子模块未初始化，已跳过」。