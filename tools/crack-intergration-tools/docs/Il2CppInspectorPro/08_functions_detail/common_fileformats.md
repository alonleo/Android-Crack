# 08 · `Il2CppInspector.Common` 文件格式读取

> 文件范围：
> - `FileFormatStreams/FileFormatStream.cs`
> - `FileFormatStreams/PEReader.cs`
> - `FileFormatStreams/ElfReader.cs`
> - `FileFormatStreams/MachOReader.cs`
> - `FileFormatStreams/NsoReader.cs`
> - `FileFormatStreams/SElfReader.cs`
> - `FileFormatStreams/UBReader.cs`
> - `FileFormatStreams/APKReader.cs`
> - `FileFormatStreams/AABReader.cs`
> - `FileFormatStreams/ProcessMapReader.cs`
> - `FileFormatStreams/LoadOptions.cs`
> - `FileFormatStreams/Export.cs` / `Section.cs` / `Symbol.cs`
> - `FileFormatStreams/WordConversions.cs`
> - `FileFormatStreams/FormatLayouts/{Elf,MachO,Nso,PE,SElf,UB}.cs`（Bin2Object 结构定义）

---

## `FileFormatStream.Load (path)`

- **签名**: `static IFileFormatStream Load(string filename, LoadOptions loadOptions = null, EventHandler<string> statusCallback = null)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/FileFormatStream.cs:~80`
- **可见性**: public static
- **副作用**: 文件 I/O
- **调用了**:
  - `Load(Stream, loadOptions, statusCallback)`
- **简要说明**: 文件路径版本

## `FileFormatStream.Load (stream)`

- **签名**: `static IFileFormatStream Load(Stream stream, LoadOptions loadOptions = null, EventHandler<string> statusCallback = null)`
- **位置**: `FileFormatStream.cs:~110`
- **可见性**: public static
- **调用了**:
  - `stream.CopyTo(BinaryObjectStream)` 拷贝
  - `PluginHooks.PreProcessImage(stream)`
  - **反射遍历所有非 abstract `IFileFormatStream` 实现**
  - 调用每个实现的 `Load(BinaryObjectStream, LoadOptions, EventHandler<string>)` 直到返回一个非 null
- **调用**: `Il2CppInspector.LoadFromStream(Stream, MemoryStream)` 内部
- **简要说明**: 反射式自动识别格式

## `FileFormatStream<T>.MapVATR` / `TryMapVATR` / `MapFileOffsetToVA` / `TryMapFileOffsetToVA`

- **签名**:
  - `uint MapVATR(ulong uiAddr)`
  - `bool TryMapVATR(ulong uiAddr, out uint fileOffset)`
  - `ulong MapFileOffsetToVA(uint offset)`
  - `bool TryMapFileOffsetToVA(uint offset, out ulong va)`
- **位置**: `FileFormatStream.cs:~150-200`
- **可见性**: public abstract (在基类)
- **调用**: `Il2CppBinary.PrepareMetadata`、`CppScaffolding` 写入 `*_ptr` 地址

## `FileFormatStream<T>.ReadMappedWord` / `ReadMappedUWord`

- **签名**: `TWord ReadMappedWord(uint fileOffset)` / `TUWord ReadMappedUWord(uint fileOffset)`
- **位置**: `FileFormatStream.cs:~220`
- **可见性**: public abstract
- **调用**: il2cpp 解析时大量使用

## `FileFormatStream<T>.ReadMappedObject<T>`

- **签名**: `T ReadMappedObject<T>(uint fileOffset) where T : IReadable, new()`
- **位置**: `FileFormatStream.cs:~260`
- **可见性**: public

## `FileFormatStream<T>.ReadMappedVersionedObject<T>`

- **签名**: `T ReadMappedVersionedObject<T>(uint fileOffset, in StructVersion version) where T : IReadable, new()`
- **位置**: `FileFormatStream.cs:~280`
- **可见性**: public
- **调用**: `Il2CppBinary.PrepareMetadata` 内部
- **简要说明**: 把 `IReadable` + 版本信息委托给生成器

## `FileFormatStream<T>.GetSymbolTable` / `GetFunctionTable` / `GetExports` / `GetSections` / `TryGetSections`

- **签名**: `Dictionary<string, Symbol> GetSymbolTable()` / `uint[] GetFunctionTable()` / `IEnumerable<Export> GetExports()` / `IEnumerable<Section> GetSections()` / `bool TryGetSections(out IEnumerable<Section>)`
- **位置**: `FileFormatStream.cs:~300-340`
- **可见性**: public abstract
- **调用**: `Il2CppBinary.FindMetadataFromSymbols` / `DiscoverAPIExports`

---

## `PEReader.Load` / `Init`

- **签名**: `static new IFileFormatStream Load(...)` / `protected override void Init(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/PEReader.cs:30 / :80`
- **可见性**: public static new + protected override
- **调用了**:
  - MZ 头检测
  - COFF header / Section table / IAT 解析
  - Themida 检测与 section rename
- **调用**: `FileFormatStream.Load` 反射遍历时
- **简要说明**: 32/64-bit PE，包括 `GameAssembly.dll`

---

## `ElfReader32/64.Load` / `Init`

- **签名**: `static new IFileFormatStream Load(...)` / `protected override void Init(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/ElfReader.cs:100 / :180`
- **可见性**: public static new + protected override
- **调用了**:
  - ELF magic 检查 + ELF header 解析
  - PHT/SHT 双 fallback（若 SHT 无效用 PHT）
  - 动态符号表解析
  - code segment = PF_X
  - **内存转储模式**：SHT 全 0 / 段重叠时用 `LoadOptions.ImageBase` 重新基址化，禁用 relocation/symbol/decryption（见 inventory §8.5）
- **调用**: `FileFormatStream.Load`

---

## `MachOReader32/64.Load` / `Init`

- **签名**: `static new IFileFormatStream Load(...)` / `protected override void Init(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/MachOReader.cs:50 / :120`
- **可见性**: public static new + protected override
- **调用了**:
  - magic + endianness + header
  - segment / section 解析
  - LC_FUNCTION_STARTS 函数表

---

## `NsoReader.Load` / `Init` / `Decompress`

- **签名**: `static new IFileFormatStream Load(...)` / `protected override void Init(...)` / `void Decompress(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/NsoReader.cs:60 / :150 / :250`
- **可见性**: public static new + protected override + private
- **调用了**: `K4os.Compression.LZ4`
- **简要说明**: NSO + LZ4 解压

---

## `SElfReader.Load`

- **签名**: `static new IFileFormatStream Load(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/SElfReader.cs:30`
- **可见性**: public static new
- **简要说明**: Switch ELF，NSO 配套

## `UBReader.Load`

- **签名**: `static new IFileFormatStream Load(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/UBReader.cs:15`
- **可见性**: public static new
- **简要说明**: 多架构 Mach-O，包装为多个 MachOReader

## `APKReader.Load` / `AABReader.Load`

- **签名**: `static new IFileFormatStream Load(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/APKReader.cs:25` / `AABReader.cs:25`
- **可见性**: public static new
- **简要说明**: ZipArchive 找 libil2cpp.so + global-metadata.dat

## `ProcessMapReader.Load`

- **签名**: `static new IFileFormatStream Load(...)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/ProcessMapReader.cs:30`
- **可见性**: public static new
- **简要说明**: Linux `/proc/self/maps` 文本格式

---

## `LoadOptions`

- **签名**: `record LoadOptions(string BinaryFilePath, ulong ImageBase)`
- **位置**: `Il2CppInspector.Common/FileFormatStreams/LoadOptions.cs:~5`
- **可见性**: public

## `WordConversions`

- **签名**: `static class WordConversions`（含 `Convert<T>`、`ConvertArray<T>`、`ConvertMap<T>`）
- **位置**: `FileFormatStreams/WordConversions.cs:15-50`
- **可见性**: public static
- **简要说明**: 32↔64-bit 字适配

## `Export` / `Section` / `Symbol`

- **签名**:
  - `record Export(string Name, ulong Address)`
  - `record Section(string Name, ulong VirtualAddress, ulong VirtualSize, uint FileOffset, uint FileSize)`
  - `record Symbol(string Name, ulong Value, ulong Size)`
- **位置**: `Export.cs:5` / `Section.cs:5` / `Symbol.cs:5`
- **可见性**: public

## `FormatLayouts/*`（Bin2Object 结构定义）

- **位置**: `FileFormatStreams/FormatLayouts/{Elf,MachO,Nso,PE,SElf,UB}.cs`
- **可见性**: internal（属于 Bin2Object 风格的结构标记）
- **简要说明**: 这些 .cs 仅包含 `[StructLayout]` / `Bin2Object` 属性标记，**子模块 Bin2Object 未初始化，因此这些文件实际依赖缺失。** 编译时需要先执行 `git submodule update --init` 才能正常工作。
- **跳过理由**：依赖 Bin2Object 子模块