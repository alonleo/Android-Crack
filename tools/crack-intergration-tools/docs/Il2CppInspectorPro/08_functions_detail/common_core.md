# 08 · `Il2CppInspector.Common` 核心（IL2CPP + Reflection）

> 文件范围：
> - `IL2CPP/Il2CppInspector.cs`
> - `IL2CPP/Il2CppBinary.cs`
> - `IL2CPP/Metadata.cs`
> - `IL2CPP/ImageScan.cs`
> - `IL2CPP/CustomAttributeDataReader.cs`
> - `IL2CPP/Il2CppConstants.cs`
> - `Reflection/TypeModel.cs`
> - `Reflection/TypeInfo.cs`
> - `Reflection/MethodBase.cs`
> - `Reflection/FieldInfo.cs`, `PropertyInfo.cs`, `EventInfo.cs`, `ParameterInfo.cs`, `CustomAttributeData.cs`, `CustomAttributeArgument.cs`, `Assembly.cs`, `MemberInfo.cs`, `MethodInvoker.cs`, `Scope.cs`, `Extensions.cs`, `Constants.cs`

---

## `Il2CppInspector.LoadFromPackage`

- **签名**: `static List<Il2CppInspector> LoadFromPackage(IEnumerable<string> packageFiles, LoadOptions loadOptions = null, EventHandler<string> statusCallback = null, bool silent = false)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:515`
- **可见性**: public static
- **参数**:
  - `packageFiles`: APK/AAB/XAPK/IPA/Zip 候选路径
  - `loadOptions`: ELF 内存转储基址等
  - `statusCallback`: 进度回调
  - `silent`: 是否抑制输出
- **返回值**: 可能为空的 `List<Il2CppInspector>`
- **副作用**: 文件 I/O
- **调用**: 被 `Il2Inspector.CLI/Program.cs:App.Run` 调用；`Il2Inspector.Redux.FrontendCore/UiContext.cs:LoadInputFilesAsync` 调用
- **调用了**: `GetStreamsFromPackage(...)` (`Il2CppInspector.cs:479`) → `LoadFromStream(Stream, MemoryStream)` (`Il2CppInspector.cs:530`)
- **简要说明**: 把压缩包格式解到 binary+metadata 流，再走 LoadFromStream

## `Il2CppInspector.LoadFromFile`

- **签名**: `static List<Il2CppInspector> LoadFromFile(string binaryFile, string metadataFile, LoadOptions = null, EventHandler<string> = null, bool silent = false)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:523`
- **可见性**: public static
- **调用**: CLI / WPF GUI 直接调用
- **调用了**: `LoadFromStream(FileStream, FileStream(metadata), ...)`
- **简要说明**: 文件路径版本，内部打开 FileStream 后委托给 LoadFromStream

## `Il2CppInspector.LoadFromStream (Stream, MemoryStream)`

- **签名**: `static List<Il2CppInspector> LoadFromStream(Stream binaryStream, MemoryStream metadataStream, LoadOptions = null, EventHandler<string> = null, bool silent = false)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:530`
- **可见性**: public static
- **副作用**: 解析两份 stream；会拷贝 stream 到 BinaryObjectStream
- **调用了**:
  - `Metadata.FromStream(metadataStream, ...)` (`Metadata.cs`)
  - `FileFormatStream.Load(binaryStream, loadOptions, statusCallback)` (`FileFormatStream.cs:Load`)
  - `LoadFromStream(IFileFormatStream, Metadata, statusCallback)` (`:572`)
  - `new Il2CppInspector(binary, metadata)` (`:572`)
  - `PluginHooks.PreProcessImage / PostProcessImage` 间接通过 FileFormatStream
- **简要说明**: 二合一入口；对每个 image 调用 `Il2CppBinary.Load`，最终包装成 `Il2CppInspector` 列表

## `Il2CppInspector.LoadFromStream (IFileFormatStream, Metadata)`

- **签名**: `static List<Il2CppInspector> LoadFromStream(IFileFormatStream stream, Metadata metadata, EventHandler<string> statusCallback = null)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:572`
- **调用了**:
  - `Il2CppBinary.Load(stream, metadata)` (`Il2CppBinary.cs:154`)
  - `new Il2CppInspector(b, m)`
- **简要说明**: 已解析好 IFileFormatStream 的版本，常用于 Redux GUI 流水线

## `Il2CppInspector.GetMethodPointer`

- **签名**: `(ulong Start, ulong End)? GetMethodPointer(Il2CppCodeGenModule module, Il2CppMethodDefinition methodDef)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:311`
- **可见性**: public
- **调用了**:
  - `Binary.ModuleMethodPointers[module]` + `Binary.MethodInvokerIndices[module]`
  - `Binary.GlobalMethodPointers`（旧版本）
  - `FunctionAddresses`（已排序 + diff）
- **简要说明**: 给定方法在模块内的全局/局部方法指针表索引，返回方法代码的 VA 区间

## `Il2CppInspector.GetGenericMethodPointer`

- **签名**: `(ulong Start, ulong End)? GetGenericMethodPointer(Il2CppMethodSpec spec)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:351`
- **可见性**: public
- **调用了**: `Binary.GenericMethodPointers[spec]`、`GenericInstances` 反查
- **简要说明**: 泛型实例化后的方法代码 VA 区间

## `Il2CppInspector.GetInvokerIndex`

- **签名**: `int GetInvokerIndex(Il2CppCodeGenModule module, Il2CppMethodDefinition methodDef)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:359`
- **可见性**: public
- **调用了**: `Binary.MethodInvokerIndices[module]`
- **简要说明**: 返回 invoker 数组的索引，用于构建 `MethodInvoker`

## `Il2CppInspector.GetVTable`

- **签名**: `MetadataUsage[] GetVTable(Il2CppTypeDefinition definition)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:369`
- **可见性**: public
- **调用了**: `Binary.VTableMethodReferences` + `Binary.Image.MapVATR` + `Metadata`
- **简要说明**: 取出指定类型的所有虚表条目（指向虚方法的 metadata usage）

## `Il2CppInspector.GetStreamsFromPackage (ZipArchive)`

- **签名**: `static (MemoryStream Metadata, MemoryStream Binary)? GetStreamsFromPackage(IEnumerable<ZipArchive> zipStreams, bool silent = false)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:383`
- **可见性**: public static
- **调用了**: `APKReader/AABReader` 共享的 ZipArchive 扫描逻辑
- **简要说明**: 在已打开的 ZipArchive 中按 `PathHeuristics` 找到 `global-metadata.dat` 与 `libil2cpp.so` 并返回内存流

## `Il2CppInspector.GetStreamsFromPackage (paths)`

- **签名**: `static (MemoryStream Metadata, MemoryStream Binary)? GetStreamsFromPackage(IEnumerable<string> packageFiles, bool silent = false)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppInspector.cs:479`
- **可见性**: public static
- **调用了**:
  - `APKReader.Load(...)` / `AABReader.Load(...)` 间接
  - 内部 `GetStreamsFromPackage(ZipArchive)`
- **简要说明**: 路径级版本；先识别 APK/AAB/XAPK/IPA/Zip 格式，命中后转 ZipArchive 再复用

## `Il2CppInspector.SaveMetadataToFile` / `SaveBinaryToFile`

- **签名**: `void SaveMetadataToFile(string pathname)` / `void SaveBinaryToFile(string pathname)`
- **位置**: `Il2CppInspector.cs:607-608`
- **可见性**: public
- **调用了**: `Metadata.SaveToFile` / `Binary.SaveToFile`
- **简要说明**: 一行 delegation；用于导出解密/解包后的 metadata/binary

## `Il2CppBinary.Load (stream + version)`

- **签名**: `static Il2CppBinary Load(IFileFormatStream stream, StructVersion metadataVersion, EventHandler<string> statusCallback = null)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:140`
- **可见性**: public static
- **调用了**:
  - `LoadImpl(...)`（反射调具体子类 ctor）
  - `LoadImpl` 内部 `FindRegistrationStructs(metadataVersion)`
- **简要说明**: 不知 metadata 内容时的入口；之后会调用 metadata-less 路径

## `Il2CppBinary.Load (stream + Metadata)`

- **签名**: `static Il2CppBinary Load(IFileFormatStream stream, Metadata metadata, EventHandler<string> statusCallback = null)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:154`
- **可见性**: public static
- **调用了**:
  - `LoadImpl(...)`（反射）
  - `new Il2CppBinary(...)` 两条重载
  - `FindRegistrationStructs(metadata)`
- **简要说明**: 已知 metadata 时使用；会触发 `PrepareMetadata`

## `Il2CppBinary.FindRegistrationStructs (Metadata)`

- **签名**: `public bool FindRegistrationStructs(Metadata metadata)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:184`
- **可见性**: public
- **调用了**:
  - `FindMetadataFromSymbols()`
  - `FindMetadataFromCode()`
  - `FindMetadataFromData()`
  - `TryPrepareMetadata`
- **简要说明**: 启发式查找 CodeRegistration + MetadataRegistration 指针

## `Il2CppBinary.FindRegistrationStructs (StructVersion)`

- **签名**: `public bool FindRegistrationStructs(StructVersion metadataVersion)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:172`
- **可见性**: public
- **调用了**: 私有 `FindMetadataFrom*` + `TryPrepareMetadata`
- **简要说明**: metadata 缺失版本

## `Il2CppBinary.SaveToFile`

- **签名**: `public void SaveToFile(string pathname)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:165`
- **可见性**: public
- **调用了**: `Image.GetStream()` + 写 `pathname`
- **简要说明**: 重新落盘二进制

## `Il2CppBinary.PrepareMetadata` (private)

- **签名**: `private void PrepareMetadata(ulong codeRegistration, ulong metadataRegistration)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:271`
- **可见性**: private
- **调用了**:
  - `Image.ReadMappedVersionedObject<Il2CppCodeRegistration>(...)`
  - `Image.ReadMappedVersionedObject<Il2CppMetadataRegistration>(...)`
  - `Modules`、`MethodInvokerIndices`、`MethodPointers` 按版本分支
  - `FieldOffsets / FieldOffsetPointers`
  - `TypeReferences + TypeReferenceIndicesByAddress`
  - `MethodSpecs`、`GenericInstances`、`GenericMethodPointers`
  - `PluginHooks.PostProcessBinary(this)`
- **简要说明**: 把 Registration 指针表展开为强类型字段

## `Il2CppBinary.TryPrepareMetadata` (private)

- **签名**: `private void TryPrepareMetadata(ulong codeRegistration, ulong metadataRegistration)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:261`
- **可见性**: private
- **调用了**: `PrepareMetadata`（try/catch）
- **简要说明**: 包装 + 异常时回退到 ImageScan

## `Il2CppBinary.DiscoverAPIExports` (private)

- **签名**: `private void DiscoverAPIExports()`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:495`
- **可见性**: private
- **调用了**: `Image.GetExports()` + 过滤 `il2cpp_*`
- **简要说明**: 收集所有 `il2cpp_*` 导出符号

## `Il2CppBinary.ConsiderCode` (abstract)

- **签名**: `protected abstract (ulong, ulong) ConsiderCode(IFileFormatStream image, uint loc)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Il2CppBinary.cs:257`
- **可见性**: protected abstract
- **调用**: 各 `Architectures/Il2CppBinary{ARM,ARM64,X86,X64}.cs` 各自 override
- **调用了**: arch-specific 启发式（Thumb LSB strip / 64-bit 字读取）
- **简要说明**: 给定 RVA，尝试解出 (CodeReg, MetadataReg) 候选

## `Metadata.FromStream`

- **签名**: `static Metadata FromStream(MemoryStream stream, EventHandler<string> statusCallback = null)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Metadata.cs:~80`
- **可见性**: public static
- **调用了**:
  - `PluginHooks.PreProcessMetadata`
  - `Header.Read(...)` + 子版本探测
  - `ReadMetadataArray<T>` / `ReadMetadataPrimitiveArray<T>` 几十次
  - `PluginHooks.GetStrings` / `GetStringLiterals`
  - `PluginHooks.PostProcessMetadata`
- **简要说明**: 读 header → 按版本分支读各 typed array → 回调 plugin 注入字符串/字面量

## `Metadata.ReadMetadataArray`

- **签名**: `ImmutableArray<T> ReadMetadataArray<T>(int oldOffset, int oldSize, Il2CppSectionMetadata)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Metadata.cs:~330`
- **可见性**: public
- **调用了**: `Reader<TReader>.ReadVersionedObject<T>()`
- **简要说明**: 通用 typed array 读取；用 `oldOffset/oldSize` 与 section offset 校正

## `Metadata.ReadMetadataPrimitiveArray`

- **签名**: `ImmutableArray<T> ReadMetadataPrimitiveArray<T>(int oldOffset, int oldSize, Il2CppSectionMetadata)`
- **位置**: `Il2CppInspector.Common/IL2CPP/Metadata.cs:~360`
- **可见性**: public
- **调用了**: `Reader<TReader>.ReadPrimitive<T>()`
- **简要说明**: 原始类型数组

## `Metadata.Sizeof<T>`

- **签名**: `int Sizeof<T>() where T : IReadable`
- **位置**: `Il2CppInspector.Common/IL2CPP/Metadata.cs:~395`
- **可见性**: public
- **调用了**: `T.Size(StructVersion, ReaderConfig)`
- **简要说明**: 由 Roslyn 生成器合成的静态 Size

## `ImageScan.Scan`

- **签名**: `void Scan(...)`
- **位置**: `Il2CppInspector.Common/IL2CPP/ImageScan.cs:~30`
- **可见性**: partial class Il2CppBinary 的方法
- **调用了**: Boyer-Moore-Horspool 签名搜索；指针链回溯
- **简要说明**: 符号/code 启发式都失败时的最后手段

## `CustomAttributeDataReader.ReadAttributeDataRange`

- **签名**: `List<CustomAttributeData> ReadAttributeDataRange(int rangeIndex, int dataIndex)`
- **位置**: `Il2CppInspector.Common/IL2CPP/CustomAttributeDataReader.cs:~30`
- **可见性**: public
- **调用了**: `BlobReader` 读取 data blob + 解析 ctor args
- **简要说明**: v29+ CustomAttribute 还原

## `TypeModel` 构造

- **签名**: `public TypeModel(Il2CppInspector package)`
- **位置**: `Il2CppInspector.Common/Reflection/TypeModel.cs:~60`
- **可见性**: public
- **副作用**: 大内存分配（每个 image 全部 typeInfo）
- **调用了**:
  - `new Assembly(this, image)` 对每个 image
  - `new TypeInfo(def, this)` 对每个 typeDef
  - 内部 `resolveTypeReference(...)`
- **简要说明**: 把 il2cpp 原始数据物化为完整 .NET 反射图

## `TypeModel.GetType`

- **签名**: `public TypeInfo GetType(string fullName)`
- **位置**: `TypeModel.cs:~150`
- **可见性**: public
- **调用了**: `TypesByFullName.TryGetValue`
- **简要说明**: 按完整名查找类型

## `TypeModel.GetGenericMethod`

- **签名**: `public MethodBase GetGenericMethod(string fullName, params TypeInfo[] typeArguments)`
- **位置**: `TypeModel.cs:~170`
- **可见性**: public
- **调用了**: `GenericMethods` + `MakeGenericMethod`
- **简要说明**: 获取泛型方法

## `TypeModel.ApplyNameTranslation`

- **签名**: `void ApplyNameTranslation(ReadOnlySpan<string> lines)`
- **位置**: `TypeModel.cs:~205`
- **可见性**: public
- **调用了**: `NameTranslationParserContext` + `NameTranslationApplierContext`
- **简要说明**: 应用名称混淆复原

## `TypeModel.ResolveGenericArguments`

- **签名**: `TypeInfo[] ResolveGenericArguments(Il2CppGenericInst)`
- **位置**: `TypeModel.cs:~220`
- **可见性**: public
- **调用了**: `MakeGenericType` 递归
- **简要说明**: 解析泛型实例

## `TypeInfo.MakeGenericType` / `MakeGenericMethod` / `SubstituteGenericArguments`

- **签名**:
  - `TypeInfo MakeGenericType(params TypeInfo[] typeArguments)`
  - `MethodBase MakeGenericMethod(params TypeInfo[] typeArguments)`
  - `TypeInfo SubstituteGenericArguments(TypeInfo[] genericArguments)`
- **位置**: `TypeInfo.cs:245 / :280 / :310`
- **可见性**: public
- **调用了**: `Scope.Namer` / `Extensions.ToCIdentifier` 等
- **简要说明**: 把泛型参数替换到类型/方法骨架

## `Assembly.ctor`

- **签名**: `Assembly(TypeModel model, int imageIndex)`
- **位置**: `Il2CppInspector.Common/Reflection/Assembly.cs:~25`
- **可见性**: public
- **调用了**: `Strings[]` 查找名
- **简要说明**: 由 image 重建 Assembly 视图

## `MethodBase.GetInvoker`

- **签名**: `MethodInvoker GetInvoker()`
- **位置**: `Il2CppInspector.Common/Reflection/MethodBase.cs:~150`
- **可见性**: public
- **调用了**: `TypeModel.MethodInvokers[GetInvokerIndex(...)]`
- **简要说明**: 取方法的 invoker 包装

## `Extensions.ToCSharpValue` / `ToAddressString` / `ToCIdentifier` / `ToEscapedString`

- **签名**:
  - `string ToCSharpValue(this object value, TypeInfo type)`
  - `string ToAddressString(this ulong addr)`
  - `string ToCIdentifier(this string s)`
  - `string ToEscapedString(this string s)`
- **位置**: `Il2CppInspector.Common/Reflection/Extensions.cs:80 / :50 / :120 / :160`
- **可见性**: public static extension
- **调用**: `CSharpCodeStubs` / `CppScaffolding` 内部密集调用
- **简要说明**: 代码发射辅助；C# 字面量、VA→hex、C++ 标识符转义

## `TypeInfo.Build*` 系列 (private)

- **签名**: 大量 `void BuildBaseType()`, `BuildInterfaces()`, `BuildGenericArguments()`, `BuildDeclaredFields()`, `BuildDeclaredMethods()`, `BuildDeclaredProperties()`, `BuildDeclaredEvents()`, `BuildCustomAttributes()`
- **位置**: `TypeInfo.cs` 全文件
- **可见性**: private
- **调用了**: `Package.Metadata.Types` / `Fields` / `Methods` / `Properties` / `Events` / `AttributeTypeRanges`
- **简要说明**: 按字段/方法/属性等分类构建 TypeInfo 的反射面

## `CustomAttributeData.ReadAttributeArguments`

- **签名**: `void ReadAttributeArguments(BinaryReader reader, ...)`
- **位置**: `Il2CppInspector.Common/Reflection/CustomAttributeData.cs:~50`
- **可见性**: internal
- **调用了**: `BlobReader` 解码
- **简要说明**: 还原 attribute 构造器实参

---

## 未找到明确调用方的项

- `Il2CppBinary.FindMetadataFromSymbols/Code/Data` (private helpers) —— 仅在 `FindRegistrationStructs` 内部被引用，没有外部调用
- `CppNamespace` 内的 `Namer<T>` —— 静态内部类，未被项目外引用
- `Scope.Current` 字段 setter —— 在各 emitter 的临时状态切换中使用