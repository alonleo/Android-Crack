# 10 · 术语表

按字母排序；含仓库特定术语与上下文。

---

## A

### APK / AAB / XAPK / IPA / Zip

Android Package / Android App Bundle / 扩展 APK / iOS App Store Package / 通用 zip 归档。`Il2CppInspector` 把这些当作 zip 流扫描，找 `lib/<abi>/libil2cpp.so`（binary）+ `assets/bin/Data/Managed/Metadata/global-metadata.dat`（metadata）。

### AppModel

[`Model/AppModel.cs`] 复合应用模型，叠加 C++ 布局视角。`IEnumerable<CppType>`；`Build()` 触发 `CppDeclarationGenerator` 工作。

### AppType / AppMethod

[`Model/AppType.cs` / `AppMethod.cs`] 复合类型/方法，组合 .NET 反射层 + C++ 层。

### Architecture (ARM / ARM64 / X86 / X64)

`Architectures/Il2CppBinary{ARM,ARM64,X86,X64}.cs` 子类，`ConsiderCode` 各有不同的启发式（Thumb LSB、x64 字宽等）。

---

## B

### Bin2Object

仓库子模块（`LukeFZ/Bin2Object`）。提供 `BinaryObjectStream`（seeka­ble + endian-aware）底层。当前子目录为空 — **未初始化**。

### binary (libil2cpp binary)

`libil2cpp.so` (Android/Linux), `GameAssembly.dll` (Windows), NSO (Switch), Mach-O (iOS/macOS), UB (多架构 Mach-O)。

### Build Pipeline

从 `Il2Inspector.LoadFromPackage` → `Metadata.FromStream` → `Il2CppBinary.Load` → `PrepareMetadata` → 全部 plugin hooks 串联的执行序列。

---

## C

### Code Registration

`Il2CppCodeRegistration` (in `Next/BinaryMetadata/`)—— il2cpp 运行时的代码注册表，包含全局/模块方法指针表、invoker 索引表、codeGenModules 列表、exportedFunctions 等。

### CppDeclarationGenerator

[`Cpp/CppDeclarationGenerator.cs`] 访问者，把 .NET 反射视图转 C++ 结构（含 value/reference/fields/vtable/statics 五种 substruct，按 MSVC vs GCC 继承风格区分）。

### CppTypeCollection

[`Cpp/CppTypeCollection.cs`] 持有所有 `CppType`（从嵌入的 `.h` 解析得到），提供 `GetType/GetComplexType/AddField` 等查询。

### CustomAttributeData

[`Reflection/CustomAttributeData.cs`] 重建的 `[Attribute]` 视图。v29+ 从 `CustomAttributeDataRanges` 解析；早期从 `AttributeTypeRanges` + `AttributeTypeIndices`。

---

## D

### DisassemblerMetadata

`Outputs/DisassemblerMetadataOutput.cs` —— 一组输出 (il2cpp.h + il2cpp.json + il2cpp.py) 给 IDA Pro / Ghidra / Binary Ninja 自动标注类型与方法。

### `dotnet`

运行 CLI 的命令（`dotnet run --project Il2Inspector.CLI -- ...`）。

### Dummy DLL

`Outputs/AssemblyShims.cs` —— 用 dnlib 生成的 `.dll`（不包含 IL 字节码），仅含类型元数据，可被 dnSpy / ILSpy 识别。

---

## E

### Endianness

字节序。`Impl/LittleEndianSeekableReader<T>` / `BigEndianSeekableReader<T>` 区分。`Reader<TReader>` 按流自动选择。

### Embedded Resource

`.h` 文件、Python 脚本、C++ 模板在 `Common/Cpp/UnityHeaders/` / `Outputs/ScriptResources/` / `Properties/Resources.resx` 嵌入，运行时通过 `Assembly.GetManifestResourceStream` 读取。

### Exception Banner

CLI `--banner` —— 异常时把信息写到 stderr。

---

## F

### FieldOffset / FieldOffsetPointer

[`Il2CppInspector.cs:68` / `Il2CppBinary.cs:FieldOffsets / FieldOffsetPointers`] 字段偏移表（`uint`）+ 字段偏移指针表（`long`）。

### FileFormatStream

[`FileFormatStreams/FileFormatStream.cs`] 抽象文件视图接口 + `Load` 静态工厂（反射所有 `IFileFormatStream` 实现）。

---

## G

### g_CodeReg / g_MetadataReg

导出符号名 `g_CodeRegistration` / `g_MetadataRegistration`，`FindMetadataFromSymbols` 据此定位注册表。

### GCC vs MSVC

[CppCompilerType] 两种 C++ 编译器风格；影响 `CppDeclarationGenerator` 中值/引用类型的 substruct 布局。PE → MSVC，其他 → GCC（`CppCompiler.GuessFromImage`）。

### Generic

泛型。`Il2CppGenericInst` → `Il2CppGenericClass` → `MakeGenericType`；泛型方法走 `Il2CppMethodSpec`。

---

## H

### Hashed Slot

未在仓库中显著使用，跳过。

---

## I

### ICSharpCode.Decompiler / ILSpy / dnSpy

C# 反编译器；读 dummy DLL 时使用。

### ICorePlugin

[`Plugins/Internal/ICorePlugin.cs`] 标记接口，实现此接口的插件自动启用。

### IDictionary<ulong, object>

`AddressMap` 的代理类型；键是 VA。

### Il2Cpp Inspector / Il2CppInspectorPro / Il2CppInspectorRedux

三代工具名称；本仓库是 Pro 版本。

### il2cpp_version (v24.x / v27.x / v29+ / v38+ / v40+)

il2cpp runtime 的版本号。`StructVersion` 中映射（如 `V240`, `V270`, `V290`, `V380`）。`[VersionCondition(LessThan=...)` 等属性控制不同版本下结构字段的读取。

### `IReader` / `ISeekableReader` / `INonSeekableReader`

[`VersionedSerialization/I*.cs`] reader 接口分层；`ISeekableReader` 知道 `Offset` 与 `Length`。

---

## J

### Jump / jmp / mscorlib.dll pointer chain

`ImageScan.cs` 用于在符号/code 都失败时回溯 metadata 指针链。

---

## L

### LZ4

NSO 内的压缩算法；`K4os.Compression.LZ4 1.3.8` 依赖。

### late-binding metadata usages (v27+)

[`Il2CppInspector.cs:137-175`] v27+ 没有 `MetadataUsageTables`，代码 brute-force 扫描整个 image 找合法编码的 usage 索引。

---

## M

### McMaster.NETCore.Plugins

NuGet 2.0.0；插件加载依赖，提供程序集隔离。

### Metadata

[`IL2CPP/Metadata.cs`] `global-metadata.dat` 的强类型解析结果。所有 typed array 都是 `ImmutableArray<T>`。

### Metadata Registration

`Il2CppMetadataRegistration` —— il2cpp 运行时的元数据注册表，包含 types/methods/fields/strings/token-adjustor-thunks 等的地址表。

### MetadataUsage

[`IL2CPP/MetadataUsage.cs`] 编码后的 usage 索引（`TypeInfo/Type/MethodDef/FieldInfo/StringLiteral/MethodRef/FieldRva`）。`MetadataUsages` 是按使用类型排序后的解码列表。

### MultiKeyDictionary

[`MultiKeyDictionary.cs`] 复合键字典；`AppModel.Methods` 用 `MethodBase → CppFnPtrType → AppMethod` 三键。

---

## N

### Next/

[`Common/Next/`] VersionedSerialization 化的新一代元数据层（`Il2CppGlobalMetadataHeader` / `Il2CppAssemblyDefinition` 等）。`Metadata` 持有这些的 `ImmutableArray`。

### NSO / SElf

Nintendo Switch Object (NSO) + Switch ELF；`NsoReader` 解 LZ4 + NRO/NROD 头；`SElfReader` 解析伴随的 ELF。

---

## O

### OutputFormatRegistry

[`FrontendCore/Outputs/OutputFormatRegistry.cs`] 5 个内置输出 (`cs` / `cppscaffolding` / `disassemblermetadata` / `dummydlls` / `vssolution`) 的静态注册表。

---

## P

### Package

`Inspector.GetStreamsFromPackage` / `LoadFromPackage` 处理 APK/AAB/XAPK/IPA/Zip。

### PathHeuristics

[`FrontendCore/PathHeuristics.cs`] 启发式判断 `global-metadata.dat` / `libil2cpp.so` 等。

### Plugin (V100)

[`Plugins/API/V100/IPlugin.cs`] 当前插件契约。13 个生命周期 hook；通过 `PluginManager.Try<IPlugin, EventInfo>(action)` 转发。

### Pre/Post-Process hooks

12 个 `PluginHooks.*`：每个 Read/Build 步骤前后给插件修改流的机会。

### Process Map

`/proc/self/maps` 风格的 Linux 进程内存映射文本；`ProcessMapReader` 解析。

---

## R

### ReentrantAttribute

[`Plugins/API/V100/ReentrantAttribute.cs`] 标记某 hook 允许重入（不受栈追踪递归守卫限制）。

### Reduce

未在仓库中显著使用，跳过。

### Redux

本仓库特指 SignalR + Tauri 重组版本（区别于旧 WPF GUI）。

### RGCTX

Runtime Generic Context —— `Il2CppRgctxDefinition/DefinitionData/ConstrainedData` 等 (`Next/BinaryMetadata/`)。在生成 C++ 时通过 `MangledNameBuilder` 表达。

---

## S

### Scaffold / Scaffolding

C++ DLL 注入工程模板。`CppScaffolding.Write` 输出完整 VS 工程。

### SignalR

ASP.NET Core 实时通信；本仓库后端用 `Microsoft.AspNetCore.SignalR 9.0.7`，前端用 `Microsoft.AspNetCore.SignalR.Client`。

### Source Generator

Roslyn `IIncrementalGenerator`（`VersionedSerialization.Generator`），把 `[VersionedStruct]` 编译为版本安全的 `Read<TReader>`。

### StructVersion

[`VersionedSerialization/StructVersion.cs`] 版本 (major, minor, tag) 值对象，可比较、可解析。

### System.Reflection-style surface

仓库重建的 .NET 类型系统 API：`TypeInfo.BaseType` / `DeclaredMethods` / `GenericTypeParameters` 等。仿 System.Reflection 但 il2cpp 内部。

---

## T

### Tauri

Rust + WebView 桌面应用框架。`Il2Inspector.Redux.GUI.UI` 用 Tauri 2.x；`UiProcessService` 提取并启动嵌入的 Tauri exe。

### Tauri.localhost

Tauri 默认允许的跨域 host；在 CORS 中显式列出。

### Thumb / Thumb-2

ARM 指令编码子集；`Il2CppBinaryARM.ConsiderCode` 处理 LSB。

### Token Range

`Il2CppMetadataRange`、`Il2CppCustomAttributeDataRange`、`Il2CppCustomAttributeTypeRange` 等。

### TypeReference

`Il2CppType`（位于 `Next/BinaryMetadata/`），是 metadata 中实际存储的「类型引用」—— 编码了类型枚举 + data klass/generic class/array type/var/mvar 等子结构。

### TypeModel

[`Reflection/TypeModel.cs`] .NET 反射视图的根；持有 `Package` (`Il2Inspector`)、`Assemblies`、`TypesByDefinitionIndex`、`TypesByReferenceIndex`、`GenericMethods` 等。

---

## U

### ULEB128

Unsigned Little-Endian Base 128。`ULEB128.cs` 实现；metadata 中所有索引字段都用此编码。

### Unity Headers

[`Cpp/UnityHeaders/*.h`] 嵌入的 Unity 头文件（~54 个），`UnityHeaders.cs` 通过 `GuessHeadersForBinary` 选择哪一组。

### Unity Version

[`Cpp/UnityHeaders/UnityVersion.cs`] `major.minor.update.buildType.buildNumber`；仓库版本解析支持范围比较。

---

## V

### V100 / V101

插件 API 版本；V100 当前激活；V101 为占位（注释标注未来）。

### VTable

虚函数表；`MetadataUsage[] GetVTable(typeDef)` 返回。

---

## W

### WPF

Windows Presentation Foundation。`Il2Inspector.GUI`（旧 GUI）使用。

### Workspace

Tauri 概念；指 WebView 加载的 Svelte 资源目录。

---

## X

### XAPK

扩展 APK；多 APK 文件归档。

---

## Y

### YAML

未在仓库中显著使用，跳过。

---

## Z

### ZIP

`ZipArchive` 是 APK/AAB/XAPK/IPA 的内部格式。`APKReader` / `AABReader` 使用 `System.IO.Compression.ZipFile`。