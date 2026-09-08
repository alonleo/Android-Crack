# 01 · 项目总览

## 1.1 身份

- **仓库**：[`Il2CppInspectorPro`](../../Il2CppInspectorPro/)
- **上游**：Jadis0x/Il2CppInspectorPro ← LukeFZ/Il2CppInspectorRedux ← djkaty/Il2CppInspector（原作者 Katy Coe）
- **版本**：2026.1（`Directory.Build.props:3`）
- **解决方案**：`Il2CppInspector.sln`（VS 18 格式，12 个项目）
- **License**：AGPL-3.0（核心 Common/CLI/GUI）+ MIT（VersionedSerialization）
- **作者**：Katy Coe · LukeFZ · Jadis0x

## 1.2 它做什么

把 Unity 编译产物（il2cpp 后端）解构成可用的高级产物：

```
原始:   GameAssembly.dll  /  libil2cpp.so  /  *.nso  /  APK / AAB / XAPK / IPA / Zip
        + global-metadata.dat
              │
              ▼
        Il2CppInspectorPro
              │
              ├──▶ C# 类型桩 (types.cs)        —— 给反编译端当类型基底
              ├──▶ C++ DLL 注入工程 (.vcxproj) —— 给 modder / hooker 直接编译
              ├──▶ IDA / Ghidra / BinaryNinja 脚本 (il2cpp.py)
              ├──▶ Dummy .NET DLL 集合         —— 给 dnSpy/ILSpy 识别类型
              └──▶ JSON 元数据                 —— 给自动化分析流水线消费
```

## 1.3 技术栈

| 层 | 技术 |
|----|------|
| 语言 | C# 13 (LangVersion=preview) · Rust（Tauri 后端）· TypeScript/Svelte 5 · Python（目标脚本） |
| 运行时 | .NET 10.0 (Common/CLI/Redux), .NET 10.0 Windows (legacy WPF GUI), netstandard2.0 (generator) |
| 关键 NuGet | dnlib 4.4 · K4os.Compression.LZ4 1.3.8 · McMaster.NETCore.Plugins 2.0 · Spectre.Console 0.50 · CommandLineParser 2.9.1 · Microsoft.AspNetCore.SignalR 9.0.7 |
| GUI | WPF（legacy）+ Tauri 2.x + Svelte 5 + Tailwind v4 + shadcn-svelte + bits-ui |
| 子模块 | Bin2Object（`https://github.com/LukeFZ/Bin2Object`）—— 当前为空，需 `git submodule update --init` |
| 代码生成 | 自研 Roslyn `IIncrementalGenerator`（VersionedSerialization）—— 把 `[VersionedStruct]` 编译成版本安全的 `Read<T>` |

## 1.4 子项目清单

| # | 项目 | 路径 | 类型 | 备注 |
|---|------|------|------|------|
| 1 | **Bin2Object** | `Bin2Object/Bin2Object/` | 类库 | git submodule（**空**，未初始化） |
| 2 | **Il2CppInspector.Common** | `Il2CppInspector.Common/` | 类库 | 核心库；NuGet 名 `NoisyCowStudios.Il2CppInspector`；包含全部反向工程逻辑 |
| 3 | **Il2CppInspector.CLI** | `Il2CppInspector.CLI/` | Exe | 单文件发布；AssemblyName=`Il2CppInspector`；win-x64 默认 RID |
| 4 | **Il2CppInspector.GUI** | `Il2CppInspector.GUI/` | WinExe | WPF；net10.0-windows |
| 5 | **Il2CppInspector.Redux.FrontendCore** | `Il2CppInspector.Redux.FrontendCore/` | 类库 (Sdk.Web) | SignalR Hub + 共享 `UiContext` |
| 6 | **Il2CppInspector.Redux.CLI** | `Il2CppInspector.Redux.CLI/` | Exe (Sdk.Web) | 启动 SignalR Hub + Spectre.Console.Cli 命令 |
| 7 | **Il2CppInspector.Redux.GUI** | `Il2CppInspector.Redux.GUI/` | WinExe (Sdk.Web) | C# 后端；`BeforeBuild` 自动 `pnpm tauri build` 然后嵌入 Tauri exe |
| 8 | **Il2CppInspector.Redux.GUI.UI** | `Il2CppInspector.Redux.GUI.UI/` | Tauri+Svelte | 独立运行时；`src-tauri/` Rust 壳 + `src/` Svelte 页面 |
| 9 | **Il2CppTests** | `Il2CppTests/` | Test (NUnit 3.14) | 多架构样本 + 期望产物回归测试 |
| 10 | **VersionedSerialization** | `VersionedSerialization/` | 类库 (MIT) | `[VersionedStruct]` 反射库 + 内嵌生成器 |
| 11 | **VersionedSerialization.Generator** | `VersionedSerialization.Generator/` | Analyzer (netstandard2.0) | Roslyn `IIncrementalGenerator` |

## 1.5 与 Il2CppInspectorRedux 相比的差异（Pro 独有）

> 仓库无明确 CHANGELOG；以下基于代码 diff 与 `inventory.md` 推断。

1. **Tauri/Svelte GUI** —— 取代（并并行存在）WPF GUI；需要 Node + pnpm 构建
2. **SignalR + 前端聚合** —— `FrontendCore` 用 Hub 暴露 `SubmitInputFiles` / `QueueExport` 等 RPC，单后端可服务多前端
3. **`Next/` 元数据层** —— 在原 Redux 之上叠加 VersionedSerialization 化的 `Il2CppGlobalMetadataHeader` + 全套 `Il2CppXxx` 结构，向 v38/v40+ 演进
4. **`IOutputFormat` 抽象** —— 5 个内置输出 (`cs` / `cppscaffolding` / `disassemblermetadata` / `dummydlls` / `vssolution`) 都走同一个 `Export(model, client, path, settings)` 接口
5. **版本号 2026.x**（Redux 上次发布停在 2022.x）
6. **WPF GUI 保留**（仍在 solution 里）

## 1.6 与 Il2CppDumper 的根本区别

| 维度 | Il2CppDumper | Il2CppInspectorPro |
|------|-------------|-------------------|
| 目标产物 | dummy DLL + JSON | C# stub + C++ scaffold + IDA/Ghidra/BinaryNinja 脚本 + dummy DLL + JSON |
| 元数据解析 | 手写 binary 偏移表 | Roslyn 生成器 + `IReadable.Read<TReader>` 版本安全 |
| C++ 输出 | ✗ | 完整 Visual Studio 工程 + ImGui/Detours 模板 |
| GUI | ✗ | Tauri/Svelte + WPF 双前端 |
| Plugin | ✗ | McMaster.NETCore.Plugins + 13 个生命周期 hook |
| 现代 il2cpp (≥v29) | 不支持 | 支持（late-binding metadata usages brute-force 扫描） |