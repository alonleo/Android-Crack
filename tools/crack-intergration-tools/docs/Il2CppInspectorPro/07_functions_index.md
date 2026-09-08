# 07 · 函数索引（总表）

> **覆盖范围**：所有子项目的 `public`/`internal` 函数。
> **行号**：已用 `grep -n` 在仓库根交叉验证。
> **跳转**：详见 `08_functions_detail/`。

> 注：`*.Designer.cs`、`*.g.cs`、`*.g.i.cs`、`Resources.Designer.cs` 自动生成代码已跳过。
> `Bin2Object/` 子模块未初始化，所有 Bin2Object 内符号均跳过。

---

## 7.1 `Il2Inspector.Common/IL2CPP/` —— 核心 il2cpp 抽象

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `Il2CppInspector` | `LoadFromPackage` | `Il2CppInspector.cs:515` | `static List<Il2CppInspector> LoadFromPackage(IEnumerable<string> packageFiles, LoadOptions = null, EventHandler<string> = null, bool silent = false)` |
| `Il2CppInspector` | `LoadFromFile` | `Il2CppInspector.cs:523` | `static List<Il2CppInspector> LoadFromFile(string binaryFile, string metadataFile, LoadOptions = null, EventHandler<string> = null, bool silent = false)` |
| `Il2CppInspector` | `LoadFromStream (Stream, MemoryStream)` | `Il2CppInspector.cs:530` | `static List<Il2CppInspector> LoadFromStream(Stream binaryStream, MemoryStream metadataStream, LoadOptions = null, EventHandler<string> = null, bool silent = false)` |
| `Il2CppInspector` | `LoadFromStream (IFileFormatStream, Metadata)` | `Il2CppInspector.cs:572` | `static List<Il2CppInspector> LoadFromStream(IFileFormatStream stream, Metadata metadata, EventHandler<string> = null)` |
| `Il2CppInspector` | `GetInvokerIndex` | `Il2CppInspector.cs:359` | `int GetInvokerIndex(Il2CppCodeGenModule module, Il2CppMethodDefinition methodDef)` |
| `Il2CppInspector` | `GetMethodPointer` | `Il2CppInspector.cs:~300` | `(ulong, ulong)? GetMethodPointer(Il2CppCodeGenModule, Il2CppMethodDefinition)` |
| `Il2CppInspector` | `GetGenericMethodPointer` | `Il2CppInspector.cs:~330` | `(ulong, ulong)? GetGenericMethodPointer(Il2CppMethodSpec)` |
| `Il2CppInspector` | `GetVTable` | `Il2CppInspector.cs:~375` | `MetadataUsage[] GetVTable(Il2CppTypeDefinition)` |
| `Il2CppInspector` | `GetStreamsFromPackage (ZipArchive)` | `Il2CppInspector.cs:~450` | `static (MemoryStream, MemoryStream)? GetStreamsFromPackage(IEnumerable<ZipArchive>, bool silent = false)` |
| `Il2CppInspector` | `GetStreamsFromPackage (paths)` | `Il2CppInspector.cs:~480` | `static (MemoryStream, MemoryStream)? GetStreamsFromPackage(IEnumerable<string>, bool silent = false)` |
| `Il2CppInspector` | `SaveMetadataToFile` | `Il2CppInspector.cs:607` | `void SaveMetadataToFile(string pathname)` |
| `Il2CppInspector` | `SaveBinaryToFile` | `Il2CppInspector.cs:608` | `void SaveBinaryToFile(string pathname)` |
| `Il2CppBinary` | `Load (stream + version)` | `Il2CppBinary.cs:~80` | `static Il2CppBinary Load(IFileFormatStream, StructVersion metadataVersion, EventHandler<string> = null)` |
| `Il2CppBinary` | `Load (stream + Metadata)` | `Il2CppBinary.cs:~110` | `static Il2CppBinary Load(IFileFormatStream, Metadata, EventHandler<string> = null)` |
| `Il2CppBinary` | `FindRegistrationStructs (Metadata)` | `Il2CppBinary.cs:~150` | `bool FindRegistrationStructs(Metadata metadata)` |
| `Il2CppBinary` | `FindRegistrationStructs (version)` | `Il2CppBinary.cs:~140` | `bool FindRegistrationStructs(StructVersion metadataVersion)` |
| `Il2CppBinary` | `PrepareMetadata` | `Il2CppBinary.cs:~250` | `void PrepareMetadata(ulong codeRegistration, ulong metadataRegistration)` |
| `Il2CppBinary` | `TryPrepareMetadata` | `Il2CppBinary.cs:~230` | `void TryPrepareMetadata(ulong codeRegistration, ulong metadataRegistration)` |
| `Il2CppBinary` | `DiscoverAPIExports` | `Il2CppBinary.cs:~350` | `void DiscoverAPIExports()` |
| `Il2CppBinary` | `SaveToFile` | `Il2CppBinary.cs:~420` | `void SaveToFile(string pathname)` |
| `Il2CppBinary` | `LoadImpl` | `Il2CppBinary.cs:~90` | `static Il2CppBinary LoadImpl(...)`（反射调用具体子类） |
| `Il2CppBinary` | `ConsiderCode` (abstract) | `Il2CppBinary.cs:~200` | `protected abstract (ulong, ulong) ConsiderCode(IFileFormatStream, uint loc)` |
| `Il2CppBinaryARM` | `ConsiderCode` | `Il2CppBinaryARM.cs:~30` | override，ARM Thumb/Thumb-2 处理 |
| `Il2CppBinaryARM64` | `ConsiderCode` | `Il2CppBinaryARM64.cs:~25` | override |
| `Il2CppBinaryX86` | `ConsiderCode` | `Il2CppBinaryX86.cs:~20` | override |
| `Il2CppBinaryX64` | `ConsiderCode` | `Il2CppBinaryX64.cs:~30` | override |
| `Metadata` | `FromStream` | `Metadata.cs:~80` | `static Metadata FromStream(MemoryStream, EventHandler<string> = null)` |
| `Metadata` | `SaveToFile` | `Metadata.cs:~390` | `void SaveToFile(string pathname)` |
| `Metadata` | `ReadMetadataArray` | `Metadata.cs:~330` | `ImmutableArray<T> ReadMetadataArray<T>(int oldOffset, int oldSize, Il2CppSectionMetadata)` |
| `Metadata` | `ReadMetadataPrimitiveArray` | `Metadata.cs:~360` | `ImmutableArray<T> ReadMetadataPrimitiveArray<T>(int oldOffset, int oldSize, Il2CppSectionMetadata)` |
| `Metadata` | `Sizeof` | `Metadata.cs:~395` | `int Sizeof<T>() where T : IReadable` |
| `ImageScan` | `Scan` | `ImageScan.cs:~30` | `void Scan(...)`（Boyer-Moore-Horspool + pointer chain） |
| `CustomAttributeDataReader` | `ReadAttributeDataRange` | `CustomAttributeDataReader.cs:~30` | `List<CustomAttributeData> ReadAttributeDataRange(int rangeIndex, int dataIndex)` |

## 7.2 `Il2Inspector.Common/Reflection/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `TypeModel` | `ctor` | `TypeModel.cs:~60` | `TypeModel(Il2CppInspector package)` |
| `TypeModel` | `GetAssembly` | `TypeModel.cs:~140` | `Assembly GetAssembly(string name)` |
| `TypeModel` | `GetType` | `TypeModel.cs:~150` | `TypeInfo GetType(string fullName)` |
| `TypeModel` | `GetGenericMethod` | `TypeModel.cs:~170` | `MethodBase GetGenericMethod(string fullName, params TypeInfo[] typeArguments)` |
| `TypeModel` | `ApplyNameTranslationFromFile` | `TypeModel.cs:~190` | `void ApplyNameTranslationFromFile(string path)` |
| `TypeModel` | `ApplyNameTranslation` | `TypeModel.cs:~205` | `void ApplyNameTranslation(ReadOnlySpan<string> lines)` |
| `TypeModel` | `ResolveGenericArguments` | `TypeModel.cs:~220` | `TypeInfo[] ResolveGenericArguments(Il2CppGenericInst)` |
| `TypeModel` | `GetTypeDefinitionFromTypeEnum` | `TypeModel.cs:~245` | `TypeInfo GetTypeDefinitionFromTypeEnum(Il2CppTypeEnum t)` |
| `TypeModel` | `GetTypeFromVirtualAddress` | `TypeModel.cs:~260` | `TypeInfo GetTypeFromVirtualAddress(ulong ptr)` |
| `TypeModel` | `GetGenericParameterType` | `TypeModel.cs:~275` | `TypeInfo GetGenericParameterType(int index)` |
| `TypeModel` | `GetCustomAttributeIndex` | `TypeModel.cs:~290` | `int GetCustomAttributeIndex(Assembly asm, int token, int customAttributeIndex)` |
| `TypeModel` | `GetMetadataUsageName` | `TypeModel.cs:~310` | `string GetMetadataUsageName(MetadataUsage usage)` |
| `TypeModel` | `GetMetadataUsageType` | `TypeModel.cs:~330` | `TypeInfo GetMetadataUsageType(MetadataUsage usage)` |
| `TypeModel` | `GetMetadataUsageMethod` | `TypeModel.cs:~350` | `MethodBase GetMetadataUsageMethod(MetadataUsage usage)` |
| `TypeInfo` | `MakeArrayType` | `TypeInfo.cs:~200` | `TypeInfo MakeArrayType(int rank = 1)` |
| `TypeInfo` | `MakeByRefType` | `TypeInfo.cs:~215` | `TypeInfo MakeByRefType()` |
| `TypeInfo` | `MakePointerType` | `TypeInfo.cs:~230` | `TypeInfo MakePointerType()` |
| `TypeInfo` | `MakeGenericType` | `TypeInfo.cs:~245` | `TypeInfo MakeGenericType(params TypeInfo[] typeArguments)` |
| `TypeInfo` | `MakeGenericMethod` | `TypeInfo.cs:~280` | `MethodBase MakeGenericMethod(params TypeInfo[] typeArguments)` |
| `TypeInfo` | `SubstituteGenericArguments` | `TypeInfo.cs:~310` | `TypeInfo SubstituteGenericArguments(TypeInfo[] genericArguments)` |
| `TypeInfo` | `Build` / `BuildBaseType` / `BuildInterfaces` / `BuildGenericArguments` / `BuildDeclaredFields` / `BuildDeclaredMethods` / `BuildDeclaredProperties` / `BuildDeclaredEvents` / `BuildCustomAttributes` | 散落在 `TypeInfo.cs:1-1231` | 私有/internal 构建器 |
| `MethodBase` | `ctor` | `MethodBase.cs:~30` | `MethodBase(MethodInfo def, TypeInfo parent)` |
| `MethodBase` | `GetInvoker` | `MethodBase.cs:~150` | `MethodInvoker GetInvoker()` |
| `FieldInfo` | `ctor` | `FieldInfo.cs:~30` | `FieldInfo(...)` |
| `FieldInfo` | `GetValue` / `SetValue` | `FieldInfo.cs:~80-100` | 访问 FieldRVA 数据 |
| `PropertyInfo` | `ctor` | `PropertyInfo.cs:~20` | |
| `EventInfo` | `ctor` | `EventInfo.cs:~20` | |
| `ParameterInfo` | `ctor` | `ParameterInfo.cs:~20` | |
| `CustomAttributeData` | `ctor` + `ReadAttributeArguments` | `CustomAttributeData.cs:~30-100` | |
| `Assembly` | `ctor` | `Assembly.cs:~25` | `Assembly(TypeModel model, int imageIndex)` |
| `Assembly` | `GetType` | `Assembly.cs:~75` | `TypeInfo GetType(string typeName)` |
| `Extensions` | `ToString(IEnumerable<CustomAttributeData>)` | `Extensions.cs:~20` | |
| `Extensions` | `ToAddressString` | `Extensions.cs:~50` | |
| `Extensions` | `ToCSharpValue` | `Extensions.cs:~80` | |
| `Extensions` | `ToCIdentifier` | `Extensions.cs:~120` | |
| `Extensions` | `ToEscapedString` | `Extensions.cs:~160` | |
| `Scope` | `ctor` | `Scope.cs:~10` | |

## 7.3 `Il2Inspector.Common/Model/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `AppModel` | `ctor` | `AppModel.cs:~50` | `AppModel(TypeModel model, bool makeDefaultBuild = true)` |
| `AppModel` | `Build` | `AppModel.cs:~110` | `AppModel Build(UnityVersion = null, CppCompilerType = BinaryFormat, bool silent = false)` |
| `AppModel` | `GetCppTypeGroup` | `AppModel.cs:~250` | `IEnumerable<CppType> GetCppTypeGroup(string groupName)` |
| `AppModel` | `GetDependencyOrderedCppTypeGroup` | `AppModel.cs:~270` | `IEnumerable<CppType> GetDependencyOrderedCppTypeGroup(string groupName)` |
| `AppModel` | `GetTypeGroup` | `AppModel.cs:~290` | `IEnumerable<AppType> GetTypeGroup(string groupName)` |
| `AppModel` | `GetMethodGroup` | `AppModel.cs:~310` | `IEnumerable<AppMethod> GetMethodGroup(string groupName)` |
| `AppModel` | `GetAddressMap` | `AppModel.cs:~330` | `AddressMap GetAddressMap()` |
| `AppModel` | `GetVTableOffset` | `AppModel.cs:~350` | `int GetVTableOffset()` |
| `AppModel` | `GetVTableIndexFromClassOffset` | `AppModel.cs:~365` | `int GetVTableIndexFromClassOffset(int offset)` |
| `AppModel` | `GetEnumerator` | `AppModel.cs:~380` | `IEnumerator<CppType> GetEnumerator()` |
| `AddressMap` | `ctor` | `AddressMap.cs:~30` | `AddressMap()` |
| `AddressMap` | `Add` / `ContainsKey` / `TryGetValue` / `this[ulong]` | `AddressMap.cs:~50-150` | `IDictionary<ulong, object>` 实现 |

## 7.4 `Il2Inspector.Common/Cpp/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `CppDeclarationGenerator` | `ctor` | `CppDeclarationGenerator.cs:~80` | `CppDeclarationGenerator(AppModel appModel)` |
| `CppDeclarationGenerator` | `AsCType` | `CppDeclarationGenerator.cs:~150` | `CppType AsCType(TypeInfo ti)` |
| `CppDeclarationGenerator` | `Reset` | `CppDeclarationGenerator.cs:~220` | `void Reset()` |
| `CppDeclarationGenerator` | `IncludeMethod` | `CppDeclarationGenerator.cs:~250` | `void IncludeMethod(MethodBase method)` |
| `CppDeclarationGenerator` | `IncludeType` | `CppDeclarationGenerator.cs:~330` | `void IncludeType(TypeInfo type)` |
| `CppDeclarationGenerator` | `GenerateRemainingTypeDeclarations` | `CppDeclarationGenerator.cs:~430` | `List<(TypeInfo, CppComplexType valueType, CppComplexType referenceType, CppComplexType fieldsType, CppComplexType vtableType, CppComplexType staticsType)> GenerateRemainingTypeDeclarations()` |
| `CppDeclarationGenerator` | `GenerateMethodDeclaration` | `CppDeclarationGenerator.cs:~520` | `CppFnPtrType GenerateMethodDeclaration(MethodBase method)` |
| `CppDeclarationGenerator` | `GenerateRequiredForwardDefinitions` | `CppDeclarationGenerator.cs:~620` | `List<CppType> GenerateRequiredForwardDefinitions()` |
| `CppTypeCollection` | `ctor` | `CppTypeCollection.cs:~80` | |
| `CppTypeCollection` | `AddFromDeclarationText` | `CppTypeCollection.cs:~150` | `void AddFromDeclarationText(string text)` |
| `CppTypeCollection` | `Add` | `CppTypeCollection.cs:~220` | `void Add(CppType type)` |
| `CppTypeCollection` | `GetType` | `CppTypeCollection.cs:~260` | `CppType GetType(string typeName, bool returnUnaliased = false)` |
| `CppTypeCollection` | `GetComplexType` | `CppTypeCollection.cs:~300` | `CppComplexType GetComplexType(string typeName)` |
| `CppTypeCollection` | `GetTypeGroup` | `CppTypeCollection.cs:~340` | `IEnumerable<CppType> GetTypeGroup(string groupName)` |
| `CppTypeCollection` | `GetTypedefGroup` | `CppTypeCollection.cs:~360` | `IEnumerable<CppType> GetTypedefGroup(string groupName)` |
| `CppTypeCollection` | `AddField` | `CppTypeCollection.cs:~400` | `int AddField(CppComplexType declaringType, string fieldName, string typeName, bool isConst = false)` |
| `CppTypeCollection` | `NewDefaultEnum` | `CppTypeCollection.cs:~430` | `CppEnumType NewDefaultEnum(string name = "")` |
| `CppTypeCollection` | `FromUnityVersion` | `CppTypeCollection.cs:~470` | `static CppTypeCollection FromUnityVersion(UnityVersion, CppDeclarationGenerator = null)` |
| `CppTypeCollection` | `FromUnityHeaders` | `CppTypeCollection.cs:~500` | `static CppTypeCollection FromUnityHeaders(UnityHeaders, CppDeclarationGenerator)` |
| `CppType` | `AsPointer` / `AsArray` / `AsAlias` | `CppType.cs:~80-110` | |
| `CppType` | `ToString` | `CppType.cs:~130` | `virtual string ToString(string format = "")` |
| `CppPointerType` | `ctor` | `CppType.cs:~190` | `CppPointerType(CppType elementType)` |
| `CppArrayType` | `ctor` | `CppType.cs:~230` | `CppArrayType(CppType elementType, int length)` |
| `CppFnPtrType` | `FromSignature` | `CppType.cs:~290` | `static CppFnPtrType FromSignature(CppTypeCollection, string)` |
| `CppComplexType` | `AddField` | `CppType.cs:~360` | `void AddField(CppField)` |
| `CppComplexType` | `GetEnumerator` | `CppType.cs:~400` | `IEnumerator<CppField> GetEnumerator()` |
| `CppEnumType` | `AddField` | `CppType.cs:~440` | `void AddField(string name, object value)` |
| `CppTypeDependencyGraph` | `DeriveDependencyOrderedTypes` | `CppTypeDependencyGraph.cs:~40` | `List<TypeInfo> DeriveDependencyOrderedTypes(TypeInfo)` |
| `CppTypeDependencyGraph` | `Reset` | `CppTypeDependencyGraph.cs:~140` | `void Reset()` |
| `CppCompilerType` (enum) | – | `CppCompilerType.cs:~10` | `{ MSVC, GCC, BinaryFormat }` |
| `CppCompiler` (static) | `GuessFromImage` | `CppCompilerType.cs:~30` | `static CppCompilerType GuessFromImage(IFileFormatStream image)` |
| `MangledNameBuilder` | `Method` / `MethodInfo` / `TypeInfo` / `TypeRef` | `MangledNameBuilder.cs:~50-260` | `static string ...(...)` Itanium mangler |
| `UnityHeaders` | `GuessHeadersForBinary` | `UnityHeaders.cs:~112` | `static UnityHeaders GuessHeadersForBinary(Il2CppBinary)` |
| `UnityHeaders` | `GetHeadersForVersion` | `UnityHeaders.cs:~140` | `static UnityHeaders GetHeadersForVersion(UnityVersion)` |
| `UnityHeaders` | `GetTypeHeaderText` | `UnityHeaders.cs:~170` | `string GetTypeHeaderText(int wordSizeBits)` |
| `UnityHeaders` | `GetApiHeaderText` | `UnityHeaders.cs:~190` | `string GetApiHeaderText(int wordSizeBits)` |
| `UnityHeaders` | `GetTypedefText` | `UnityHeaders.cs:~200` | `string GetTypedefText(int wordSizeBits)` |
| `UnityVersion` | `Parse` / `TryParse` | `UnityVersion.cs:~80` | |

## 7.5 `Il2Inspector.Common/Outputs/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `CSharpCodeStubs` | `ctor` | `CSharpCodeStubs.cs:~50` | `CSharpCodeStubs(TypeModel model)` |
| `CSharpCodeStubs` | `GetAndClearLastException` | `CSharpCodeStubs.cs:~110` | `Exception GetAndClearLastException()` |
| `CSharpCodeStubs` | `WriteSingleFile` | `CSharpCodeStubs.cs:~140` | `void WriteSingleFile(string outFile)` |
| `CSharpCodeStubs` | `WriteSingleFile<TKey>` | `CSharpCodeStubs.cs:~170` | `void WriteSingleFile<TKey>(string outFile, Func<TypeInfo, TKey> orderBy)` |
| `CSharpCodeStubs` | `WriteFilesByNamespace<TKey>` | `CSharpCodeStubs.cs:~220` | `void WriteFilesByNamespace<TKey>(string outPath, Func<TypeInfo, TKey> orderBy, bool flattenHierarchy)` |
| `CSharpCodeStubs` | `WriteFilesByAssembly<TKey>` | `CSharpCodeStubs.cs:~280` | `void WriteFilesByAssembly<TKey>(string outPath, Func<TypeInfo, TKey> orderBy, bool separateAttributes)` |
| `CSharpCodeStubs` | `WriteFilesByClass` | `CSharpCodeStubs.cs:~350` | `void WriteFilesByClass(string outPath, bool flattenHierarchy)` |
| `CSharpCodeStubs` | `WriteFilesByClassTree` | `CSharpCodeStubs.cs:~420` | `HashSet<Assembly> WriteFilesByClassTree(string outPath, bool separateAttributes)` |
| `CSharpCodeStubs` | `WriteSolution` | `CSharpCodeStubs.cs:~580` | `void WriteSolution(string outPath, string unityPath, string unityAssembliesPath)` |
| `CppScaffolding` | `ctor` | `CppScaffolding.cs:~50` | `CppScaffolding(AppModel model, bool useBetterArraySize = false, bool includeUnresolvedCppTypes = false)` |
| `CppScaffolding` | `Write` | `CppScaffolding.cs:~120` | `void Write(string projectPath, string projectName = null)` |
| `CppScaffolding` | `WriteTypes` | `CppScaffolding.cs:~250` | `void WriteTypes(string typeHeaderFile)` |
| `AssemblyShims` | `ctor` | `AssemblyShims.cs:~60` | `AssemblyShims(TypeModel model)` |
| `AssemblyShims` | `Write` | `AssemblyShims.cs:~120` | `void Write(string outPath, EventHandler<string> statusCallback = null)` |
| `JSONMetadata` | `ctor` | `JSONMetadata.cs:~40` | `JSONMetadata(AppModel model)` |
| `JSONMetadata` | `Write` | `JSONMetadata.cs:~100` | `void Write(string filePath)` |
| `PythonScript` | `ctor` | `PythonScript.cs:~30` | `PythonScript(AppModel model)` |
| `PythonScript` | `WriteScriptToFile` | `PythonScript.cs:~50` | `void WriteScriptToFile(string outFile, string target, string cppHeaderFile, string jsonMetadataFile)` |
| `PythonScript` | `GetAvailableTargets` | `PythonScript.cs:~75` | `static IEnumerable<string> GetAvailableTargets()` |
| `dnlibExtensions` | `AddDefaultConstructor` | `AssemblyShims.cs:~700` | `static MethodDef AddDefaultConstructor(this TypeDef, IMethod @base)` |
| `dnlibExtensions` | `AddAttribute` | `AssemblyShims.cs:~720` | `static CustomAttribute AddAttribute(this IHasCustomAttribute, ModuleDef, TypeDef, params (string, object)[])` |

## 7.6 `Il2Inspector.Common/FileFormatStreams/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `FileFormatStream` | `Load (path)` | `FileFormatStream.cs:~80` | `static IFileFormatStream Load(string filename, LoadOptions = null, EventHandler<string> = null)` |
| `FileFormatStream` | `Load (stream)` | `FileFormatStream.cs:~110` | `static IFileFormatStream Load(Stream stream, LoadOptions = null, EventHandler<string> = null)` |
| `FileFormatStream<T>` | `MapVATR` / `TryMapVATR` | `FileFormatStream.cs:~150-170` | 抽象方法 |
| `FileFormatStream<T>` | `MapFileOffsetToVA` / `TryMapFileOffsetToVA` | `FileFormatStream.cs:~180-200` | |
| `FileFormatStream<T>` | `ReadMappedWord` / `ReadMappedUWord` | `FileFormatStream.cs:~220` | |
| `FileFormatStream<T>` | `ReadMappedObject<T>` | `FileFormatStream.cs:~260` | |
| `FileFormatStream<T>` | `ReadMappedVersionedObject<T>` | `FileFormatStream.cs:~280` | |
| `FileFormatStream<T>` | `GetSymbolTable` / `GetFunctionTable` / `GetExports` / `GetSections` | `FileFormatStream.cs:~300-340` | |
| `PEReader` | `Load` | `PEReader.cs:~30` | `static IFileFormatStream Load(...)` |
| `PEReader` | `Init` | `PEReader.cs:~80` | `protected override void Init(...)` |
| `ElfReader32/64` | `Load` | `ElfReader.cs:~100` | |
| `ElfReader<TWord,...>` | `Init` | `ElfReader.cs:~180` | |
| `MachOReader32/64` | `Load` | `MachOReader.cs:~50` | |
| `MachOReader<TWord,...>` | `Init` | `MachOReader.cs:~120` | |
| `NsoReader` | `Load` | `NsoReader.cs:~60` | |
| `NsoReader` | `Init` | `NsoReader.cs:~150` | |
| `NsoReader` | `Decompress` | `NsoReader.cs:~250` | LZ4 解压 |
| `SElfReader` | `Load` | `SElfReader.cs:~30` | |
| `UBReader` | `Load` | `UBReader.cs:~15` | |
| `APKReader` | `Load` | `APKReader.cs:~25` | |
| `AABReader` | `Load` | `AABReader.cs:~25` | |
| `ProcessMapReader` | `Load` | `ProcessMapReader.cs:~30` | |
| `LoadOptions` | `ctor` | `LoadOptions.cs:~5` | `(string BinaryFilePath, ulong ImageBase)` |
| `WordConversions` | `Convert` 系列 | `WordConversions.cs:~15-50` | 32↔64 |

## 7.7 `Il2Inspector.Common/Plugins/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `PluginManager` | `EnsureInit` | `Internal/PluginManager.cs:~60` | `static PluginManager EnsureInit()` |
| `PluginManager` | `Reload` | `Internal/PluginManager.cs:~110` | `static void Reload(string pluginPath = null, bool reset = true, bool coreOnly = false)` |
| `PluginManager` | `Reset(IPlugin)` | `Internal/PluginManager.cs:~200` | `static IPlugin Reset(IPlugin)` |
| `PluginManager` | `OptionsChanged(IPlugin)` | `Internal/PluginManager.cs:~225` | `static PluginOptionsChangedEventInfo OptionsChanged(IPlugin)` |
| `PluginManager` | `ValidateAllOptions` | `Internal/PluginManager.cs:~250` | `static PluginOptionsChangedEventInfo ValidateAllOptions()` |
| `PluginManager` | `Try<I, E>` | `Internal/PluginManager.cs:~290` | `internal static E Try<I, E>(Action<I, E>, [CallerMemberName] string = null) where E : PluginEventInfo, new()` |
| `PluginHooks` | `LoadPipelineStarting` | `Internal/PluginHooks.cs:~15` | `static PluginLoadPipelineStartingEventInfo LoadPipelineStarting()` |
| `PluginHooks` | `PreProcessMetadata` / `PostProcessMetadata` / `GetStrings` / `GetStringLiterals` | `Internal/PluginHooks.cs:~20-35` | |
| `PluginHooks` | `PreProcessImage` / `PostProcessImage` | `Internal/PluginHooks.cs:~40-45` | |
| `PluginHooks` | `PreProcessBinary` / `PostProcessBinary` | `Internal/PluginHooks.cs:~50-55` | |
| `PluginHooks` | `PostProcessPackage` | `Internal/PluginHooks.cs:~58` | |
| `PluginHooks` | `LoadPipelineEnding` | `Internal/PluginHooks.cs:~60` | |
| `PluginHooks` | `PostProcessTypeModel` / `PostProcessAppModel` | `Internal/PluginHooks.cs:~62-64` | |
| `IPlugin` (V100) | `Id` / `Name` / `Author` / `Description` / `Version` / `Options` / `OptionsChanged` | `API/V100/IPlugin.cs` | |
| `ILoadPipeline` (V100) | 13 hook 方法 | `API/V100/ILoadPipeline.cs` | |

## 7.8 `Il2Inspector.CLI/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `App` | `Main` | `Program.cs:~30` | `static int Main(string[] args)` |
| `App` | `Run` | `Program.cs:~80` | `static int Run(Options options)` |
| `App` | `RunPlugin` | `Program.cs:~250` | 内部 helper |
| `App` | `getOutputPath` | `Program.cs:~440` | `string getOutputPath(string basePath, string defaultExt, int idx)` |
| `Options` | （CommandLineParser `Options` 类，含所有 `[Option]` 字段） | `Program.cs:~50-300` | 见 §6.3 |
| `PluginOptions` | `CreateOptionsFromPlugin` | `PluginOptions.cs:~40` | `static Type[] CreateOptionsFromPlugin(IPlugin plugin)` |
| `PluginOptions` | `GetPluginOptionTypes` | `PluginOptions.cs:~80` | `static IEnumerable<Type> GetPluginOptionTypes()` |
| `PluginOptions` | `ParsePluginOptions` | `PluginOptions.cs:~170` | `static void ParsePluginOptions(...)` |
| `PathUtils` | `FindPath` | `PathUtils.cs:~20` | `static IEnumerable<string> FindPath(string searchPattern)` |

## 7.9 `Il2Inspector.GUI/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `App` | `OnStartup` | `App.xaml.cs:~50` | `void OnStartup(StartupEventArgs e)` |
| `App` | `LoadPackageAsync` | `App.xaml.cs:~120` | `Task LoadPackageAsync(...)` |
| `App` | `LoadMetadataAsync` | `App.xaml.cs:~170` | `Task LoadMetadataAsync(...)` |
| `App` | `LoadBinaryAsync` | `App.xaml.cs:~210` | `Task LoadBinaryAsync(...)` |
| `MainWindow` | `ctor` | `MainWindow.xaml.cs:~50` | |
| `MainWindow` | `OnLoaded` | `MainWindow.xaml.cs:~90` | |
| `MainWindow` | `SelectBinary_Click` / `SelectMetadata_Click` | `MainWindow.xaml.cs:~150-200` | |
| `MainWindow` | `Analyze_Click` | `MainWindow.xaml.cs:~280` | |
| `MainWindow` | `GenerateCSharp_Click` / `GenerateCpp_Click` 等 | `MainWindow.xaml.cs:~400-600` | |
| `MainWindow` | `RunAnalysis` | `MainWindow.xaml.cs:~340` | 核心：调用 `Il2Inspector.LoadFromFile` + `TypeModel` + `AppModel.Build` |
| `PluginConfigurationDialog` | `ctor` / `Ok_Click` | `PluginConfigurationDialog.xaml.cs:~30-300` | |
| `PluginManagerDialog` | `ctor` / `Refresh_Click` | `PluginManagerDialog.xaml.cs:~30-120` | |
| `LoadOptionsDialog` | `ctor` | `LoadOptionsDialog.xaml.cs:~15` | |
| `EqualityConverter` | `Convert` / `ConvertBack` | `EqualityConverter.cs:~10-25` | |
| `HexStringValueConverter` | `Convert` / `ConvertBack` | `HexStringValueConverter.cs:~15-40` | |

## 7.10 `Il2Inspector.Redux.FrontendCore/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `UiContext` | `ctor` | `UiContext.cs:~50` | `UiContext(...)` |
| `UiContext` | `InitializeAsync` | `UiContext.cs:~80` | `Task InitializeAsync(UiClient client, CancellationToken = default)` |
| `UiContext` | `LoadInputFilesAsync` | `UiContext.cs:~120` | `Task LoadInputFilesAsync(UiClient, List<string>, CancellationToken = default)` |
| `UiContext` | `QueueExportAsync` | `UiContext.cs:~170` | `Task QueueExportAsync(UiClient, string exportFormatId, string outputDirectory, Dictionary<string, string> settings, CancellationToken = default)` |
| `UiContext` | `StartExportAsync` | `UiContext.cs:~200` | `Task StartExportAsync(UiClient, CancellationToken = default)` |
| `UiContext` | `GetPotentialUnityVersionsAsync` | `UiContext.cs:~225` | `Task<List<string>> GetPotentialUnityVersionsAsync()` |
| `UiContext` | `ExportIl2CppFilesAsync` | `UiContext.cs:~245` | `Task ExportIl2CppFilesAsync(UiClient, string outputDirectory, CancellationToken = default)` |
| `UiContext` | `GetInspectorVersionAsync` | `UiContext.cs:~265` | `static Task<string> GetInspectorVersionAsync()` |
| `UiContext` | `SetSettingsAsync` | `UiContext.cs:~270` | `Task SetSettingsAsync(UiClient, InspectorSettings settings)` |
| `UiClient` | `ctor` | `UiClient.cs:~20` | `UiClient(ISingleClientProxy proxy)` |
| `UiClient` | `ShowLogMessage` | `UiClient.cs:~25` | `Task ShowLogMessage(string, CancellationToken = default)` |
| `UiClient` | `BeginLoading` / `FinishLoading` | `UiClient.cs:~28-30` | |
| `UiClient` | `ShowInfoToast` / `ShowSuccessToast` / `ShowErrorToast` | `UiClient.cs:~32-38` | |
| `UiClient` | `OnImportCompleted` | `UiClient.cs:~40` | |
| `Il2CppHub` | `OnUiLaunched` / `SubmitInputFiles` / `QueueExport` / `StartExport` / `GetPotentialUnityVersions` / `ExportIl2CppFiles` / `GetInspectorVersion` / `SetSettings` | `Il2CppHub.cs:~10-60` | SignalR Hub 方法 |
| `LoadingSession` | `Start` | `LoadingSession.cs:~10` | `static Task<LoadingSession> Start(UiClient)` |
| `Extensions` | `AddFrontendCore` / `MapFrontendCore` | `Extensions.cs:~15-30` | |
| `PathHeuristics` | `IsMetadataPath` / `IsBinaryPath` | `PathHeuristics.cs:~10-50` | `static bool ...(string)` |
| `IOutputFormat` | `Export` | `Outputs/IOutputFormat.cs:~5` | `Task Export(AppModel model, UiClient client, string outputPath, Dictionary<string, string> settingsDict)` |
| `IOutputFormatProvider` | `Id` | `Outputs/IOutputFormat.cs:~10` | `static abstract string Id` |
| `OutputFormatRegistry` | `AvailableOutputFormats` / `GetOutputFormat` | `Outputs/OutputFormatRegistry.cs:~10-30` | |
| `CSharpStubOutput` | `Export` | `Outputs/CSharpStubOutput.cs:~15` | |
| `VsSolutionOutput` | `Export` | `Outputs/VsSolutionOutput.cs:~10` | |
| `DummyDllOutput` | `Export` | `Outputs/DummyDllOutput.cs:~10` | |
| `DisassemblerMetadataOutput` | `Export` | `Outputs/DisassemblerMetadataOutput.cs:~15` | |
| `CppScaffoldingOutput` | `Export` | `Outputs/CppScaffoldingOutput.cs:~10` | |

## 7.11 `Il2Inspector.Redux.CLI/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `Program` | `Main` | `Program.cs:~10` | `static void Main(string[] args)` |
| `Program` | `MainAsync` | `Program.cs:~20` | `static async Task MainAsync(string[] args)` |
| `CliClient` | `ctor` | `CliClient.cs:~20` | `CliClient(string url)` |
| `CliClient` | `ConnectAsync` / `Dispose` | `CliClient.cs:~40-50` | |
| `CliClient` | `OnUiLaunched` / `SubmitInputFiles` / `QueueExport` / `StartExport` / `GetPotentialUnityVersions` / `ExportIl2CppFiles` / `GetInspectorVersion` / `SetSettings` / `WaitForLoadingToFinishAsync` | `CliClient.cs:~55-140` | |
| `PortProvider` | `ctor` | `PortProvider.cs:~3` | `PortProvider(int port)` |
| `ServiceTypeRegistrar` | `ctor` / `Build` / `Register` / `RegisterInstance` | `ServiceTypeRegistrar.cs:~5-29` | |
| `ServiceTypeResolver` | `ctor` / `Resolve` | `ServiceTypeResolver.cs:~3-12` | |
| `BaseCommand<T>` | `ctor` / `ExecuteAsync` | `Commands/BaseCommand.cs:~15-37` | |
| `InteractiveCommand` | `ExecuteAsync` | `Commands/InteractiveCommand.cs:~5-15` | |
| `ManualCommand<T>` | `ctor` | `Commands/ManualCommand.cs:~10-20` | |
| `ManualCommand` (concrete) | `ExecuteAsync` | `Commands/ManualCommand.cs:~30` | |
| `ManualCommandSettings` | – | `Commands/ManualCommandSettings.cs:~5-14` | |
| `ProcessCommand` | `ExecuteAsync` | `Commands/ProcessCommand.cs:~40-197` | |

## 7.12 `Il2Inspector.Redux.GUI/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `Program` | `Main` | `Program.cs:~10` | `static void Main(string[] args)` |
| `Program` | `MainAsync` | `Program.cs:~20` | `static async Task MainAsync(string[] args)` |
| `UiProcessService` | `ctor` | `UiProcessService.cs:~15` | `UiProcessService(...)` |
| `UiProcessService` | `ExecuteAsync` | `UiProcessService.cs:~30` | `override Task ExecuteAsync(CancellationToken stoppingToken)` |
| `UiProcessService` | `LaunchUiProcess` | `UiProcessService.cs:~40` | `void LaunchUiProcess(int port)` |
| `UiProcessService` | `ExtractUiExecutable` | `UiProcessService.cs:~50` | `string ExtractUiExecutable()` |
| `UiProcessService` | `StopAsync` | `UiProcessService.cs:~65` | `override Task StopAsync(CancellationToken)` |

## 7.13 `Il2Inspector.Redux.GUI.UI/`（Tauri + Svelte，非 C#）

| 类型 | 函数 | 行 | 说明 |
|------|------|----|------|
| `tauri::Builder` | `main` | `src-tauri/src/main.rs:5` | Tauri 入口 |
| `lib::run` | `run` | `src-tauri/src/lib.rs:10` | Tauri lib 入口 |
| Svelte `routes/+page.svelte` | onMount → api | `src/routes/+page.svelte` | 主页 |
| Svelte `routes/advanced/+page.svelte` | onMount → api | `src/routes/advanced/+page.svelte` | 高级设置 |
| Svelte `routes/export/[formatId]/+page.svelte` | onMount → api | | 导出页 |
| `client-api.ts` | `submitInputFiles` / `queueExport` / `startExport` / ... | `src/lib/signalr/client-api.ts` | SignalR 客户端 |
| `api.svelte.ts` | 响应式 store | `src/lib/signalr/api.svelte.ts` | Svelte 5 runes |

## 7.14 `Il2Tests/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `TestRunner` | `Run` | `TestRunner.cs:~30` | 跨样本驱动 |
| `TestRunner` | `RunSingle` | `TestRunner.cs:~80` | 单样本 |
| `TestCppTypeDeclarations` | `[TestCase]` | `TestCppTypeDeclarations.cs:~30-200` | |
| `TestAppModelQueries` | `[TestCase]` | `TestAppModelQueries.cs:~15-130` | |
| `TestGenerics` | `[TestCase]` | `TestGenerics.cs:~20-400` | |
| `TestNames` | `[TestCase]` | `TestNames.cs:~10-100` | |
| `TestUnityVersion` | `[TestCase]` | `TestUnityVersion.cs:~10-50` | |

## 7.15 `VersionedSerialization/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `StructVersion` | `TryParse` / `Parse` | `StructVersion.cs:~40-65` | `static bool TryParse(string?, IFormatProvider?, out StructVersion)` |
| `StructVersion` | `HasTag` | `StructVersion.cs:~30` | `bool HasTag(string tag)` |
| `StructVersion` | `AsDouble` | `StructVersion.cs:~25` | `double AsDouble => Major + Minor/10.0` |
| `StructVersion` | operator | `StructVersion.cs:~75-90` | `== != > < >= <=` |
| `Reader<TReader>` | `ReadVersionedObject<T>` | `Reader\`1.cs:~40` | `T ReadVersionedObject<T>(...) where T : IReadable, new()` |
| `Reader` | static helpers | `Reader.cs:~20-90` | 入口 |
| `IReadable` | `Read` / `Size` | `IReadable.cs:~10-20` | |
| `LittleEndianSeekableReader<T>` | – | `Impl/EndianReader.cs:~40` | |
| `BigEndianSeekableReader<T>` | – | `Impl/EndianReader.cs:~120` | |
| `SpanReader` | – | `Impl/SpanReader.cs:~15` | |
| `ReadableExtensions` | extension methods | `ReadableExtensions.cs:~10-50` | |
| `SeekableReaderExtensions` | extension methods | `SeekableReaderExtensions.cs:~10-50` | |
| `VersionedStructAttribute` | ctor | `Attributes/VersionedStructAttribute.cs:~5` | |
| `VersionConditionAttribute` | props | `Attributes/VersionConditionAttribute.cs:~5-20` | LessThan/GreaterThan/EqualTo/... |
| `NativeIntegerAttribute` | ctor | `Attributes/NativeIntegerAttribute.cs:~5` | |
| `ReaderConfig` | ctor | `ReaderConfig.cs:~5` | `ReaderConfig(bool is32Bit)` |

## 7.16 `VersionedSerialization.Generator/`

| 类型 | 函数 | 行 | 关键签名 |
|------|------|----|---------|
| `ObjectSerializationGenerator` | `Initialize` | `ObjectSerializationGenerator.cs:~30` | `void Initialize(IncrementalGeneratorInitializationContext context)` |
| `ObjectSerializationGenerator` | `ParseSerializationInfo` | `ObjectSerializationGenerator.cs:~80` | 内部 |
| `ObjectSerializationGenerator` | `EmitCode` | `ObjectSerializationGenerator.cs:~250` | 内部 |
| `InvalidVersionAnalyzer` | `Initialize` | `Analyzer/InvalidVersionAnalyzer.cs:~15` | `override void Initialize(AnalysisContext context)` |
| `ObjectSerializationInfo` | props | `Models/ObjectSerializationInfo.cs` | |
| `PropertySerializationInfo` | props | `Models/PropertySerializationInfo.cs` | |
| `PropertyType` | enum/struct | `Models/PropertyType.cs` | |
| `VersionCondition` | – | `Models/VersionCondition.cs` | |
| `CodeGenerator` | – | `Utils/CodeGenerator.cs` | |
| `HashCode` | static helpers | `Utils/HashCode.cs` | Burst 友好 |
| `ImmutableEquatableArray<T>` | ctor / `Equals` / `GetHashCode` | `Utils/ImmutableEquatableArray.cs` | |

---

**总计**：约 **350+ 函数**（不含 `*.Designer.cs`、子模块 Bin2Object）。

> 详细函数说明（包含 caller/callee 验证）见 `08_functions_detail/*.md`。

---

## 7.17 `TypeInfo` 反射辅助方法（增量）

| 函数 | 位置 | 签名 |
|------|------|------|
| `GetField` | `Reflection/TypeInfo.cs:204` | `FieldInfo GetField(string name)` |
| `GetMethod` | `TypeInfo.cs:246` | `MethodInfo GetMethod(string name)` |
| `GetMethods` | `TypeInfo.cs:249` | `MethodInfo[] GetMethods(string name)` |
| `GetAllMethods` | `TypeInfo.cs:252` | `MethodInfo[] GetAllMethods()` |
| `GetProperty` | `TypeInfo.cs:263` | `PropertyInfo GetProperty(string name)` |
| `GetVTable` | `TypeInfo.cs:265` | `MethodBase[] GetVTable()` |
| `GetGenericTypeDefinition` | `TypeInfo.cs:214` | `TypeInfo GetGenericTypeDefinition()` |
| `GetConstructorByDefinition` | `TypeInfo.cs:222` | `ConstructorInfo GetConstructorByDefinition(ConstructorInfo definition)` |
| `GetMethodByDefinition` | `TypeInfo.cs:234` | `MethodInfo GetMethodByDefinition(MethodInfo definition)` |
| `GetGenericParameterConstraints` | `TypeInfo.cs:209` | `TypeInfo[] GetGenericParameterConstraints()` |
| `GetGenericArguments` | `TypeInfo.cs:676` | `TypeInfo[] GetGenericArguments()` |
| `GetArrayRank` | `TypeInfo.cs:752` | `int GetArrayRank()` |
| `GetEnumNames` | `TypeInfo.cs:754` | `string[] GetEnumNames()` |
| `GetEnumUnderlyingType` | `TypeInfo.cs:759` | `TypeInfo GetEnumUnderlyingType()` |
| `GetEnumValues` | `TypeInfo.cs:765` | `Array GetEnumValues()` |
| `GetCSharpTypeDeclarationName` | `TypeInfo.cs:342` | `string GetCSharpTypeDeclarationName(bool includeVariance = false)` |
| `GetScopedCSharpName` | `TypeInfo.cs:590` | `string GetScopedCSharpName(Scope usingScope = null, bool omitRef = false, bool isPartOfTypeDeclaration = false)` |
| `GetAllTypeReferences` | `TypeInfo.cs:1035` | `List<TypeInfo> GetAllTypeReferences()` |
| `GetAccessModifierString` | `TypeInfo.cs:1131` | `string GetAccessModifierString()` |
| `GetModifierString` | `TypeInfo.cs:1145` | `string GetModifierString()` |
| `GetTypeConstraintsString` | `TypeInfo.cs:1183` | `string GetTypeConstraintsString(Scope scope)` |
| `CSharpBaseName` | `TypeInfo.cs:313` | `string CSharpBaseName => unmangleName(base.Name).ToCIdentifier()` |

## 7.18 `MethodBase` 反射辅助

| 函数 | 位置 | 签名 |
|------|------|------|
| `GetGenericArguments` | `Reflection/MethodBase.cs:69` | `TypeInfo[] GetGenericArguments()` |
| `GetGenericMethodDefinition` | `MethodBase.cs:76` | `MethodBase GetGenericMethodDefinition()` |
| `GetMethodBody` | `MethodBase.cs:90` | `byte[] GetMethodBody()` |
| `MakeGenericMethod` | `MethodBase.cs:199` | `MethodBase MakeGenericMethod(params TypeInfo[] typeArguments)` |
| `GetAccessModifierString` | `MethodBase.cs:214` | `string GetAccessModifierString()` |
| `GetModifierString` | `MethodBase.cs:233` | `string GetModifierString()` |
| `GetParametersString` | `MethodBase.cs:276` | `string GetParametersString(Scope usingScope, bool emitPointer = false, bool commentAttributes = false)` |
| `GetTypeParametersString` | `MethodBase.cs:279` | `string GetTypeParametersString(Scope usingScope)` |
| `GetFullTypeParametersString` | `MethodBase.cs:282` | `string GetFullTypeParametersString()` |
| `SignatureEquals` | `MethodBase.cs:285` | `bool SignatureEquals(MethodBase other)` |

## 7.19 `FieldInfo` / `ParameterInfo` / `CustomAttributeData` 辅助

| 函数 | 位置 | 签名 |
|------|------|------|
| `FieldInfo.GetDefaultValueString` | `Reflection/FieldInfo.cs:42` | `string GetDefaultValueString(Scope usingScope = null)` |
| `FieldInfo.RequiresUnsafeContext` | `FieldInfo.cs:93` | `bool RequiresUnsafeContext { get; }` |
| `FieldInfo.GetAccessModifierString` | `FieldInfo.cs:140` | `string GetAccessModifierString()` |
| `FieldInfo.GetModifierString` | `FieldInfo.cs:150` | `string GetModifierString()` |
| `ParameterInfo.SubstituteGenericArguments` | `Reflection/ParameterInfo.cs:113` | `ParameterInfo SubstituteGenericArguments(MethodBase declaringMethod, TypeInfo[] typeArguments, TypeInfo[] methodArguments = null)` |
| `ParameterInfo.GetModifierString` | `ParameterInfo.cs:121` | `string GetModifierString()` |
| `ParameterInfo.GetSignatureString` | `ParameterInfo.cs:128` | `string GetSignatureString()` |
| `ParameterInfo.GetParameterString` | `ParameterInfo.cs:130` | `string GetParameterString(Scope usingScope, bool emitPointer = false, bool compileAttributes = false)` |
| `ParameterInfo.GetReturnParameterString` | `ParameterInfo.cs:137` | `string GetReturnParameterString(Scope scope)` |
| `CustomAttributeData.GetMethodBody` | `Reflection/CustomAttributeData.cs:44` | `byte[] GetMethodBody()` |
| `CustomAttributeData.GetAllTypeReferences` | `CustomAttributeData.cs:46` | `IEnumerable<TypeInfo> GetAllTypeReferences()` |
| `CustomAttributeData.GetCustomAttributes` (8 overloads) | `CustomAttributeData.cs:143-155` | `static IList<CustomAttributeData> GetCustomAttributes(Assembly/EventInfo/FieldInfo/MethodBase/ParameterInfo/PropertyInfo/TypeInfo)` |

## 7.20 `TypeRef`（辅助类）

| 函数 | 位置 | 签名 |
|------|------|------|
| `TypeRef.FromReferenceIndex` | `Reflection/TypeRef.cs:31` | `static TypeRef FromReferenceIndex(TypeModel model, int index)` |
| `TypeRef.FromDefinitionIndex` | `TypeRef.cs:34` | `static TypeRef FromDefinitionIndex(TypeModel model, int index)` |
| `TypeRef.FromTypeInfo` | `TypeRef.cs:37` | `static TypeRef FromTypeInfo(TypeInfo type)` |

## 7.21 `MethodInvoker` / `Scope`

| 函数 | 位置 | 签名 |
|------|------|------|
| `MethodInvoker.GetMethodBody` | `Reflection/MethodInvoker.cs:61` | `byte[] GetMethodBody()` |
| `MethodInvoker.GetSignature` | `MethodInvoker.cs:67` | `string GetSignature(UnityVersion version)` |
| `Scope.Empty` (static) | `Reflection/Scope.cs:15` | `public static Scope Empty = new Scope()` |

## 7.22 `Extensions`（`Reflection/Extensions.cs`）

| 函数 | 位置 | 签名 |
|------|------|------|
| `ToString(IEnumerable<CustomAttributeData>)` | `Extensions.cs:19` | `static string ToString(this IEnumerable<CustomAttributeData>, Scope = null, ...)` |
| `ToAddressString (ulong)` | `Extensions.cs:114` | `static string ToAddressString(this ulong)` |
| `ToAddressString (long)` | `Extensions.cs:118` | `static string ToAddressString(this long)` |
| `ToAddressString (range)` | `Extensions.cs:120-122` | `static string ToAddressString(this (ulong, ulong)? / (ulong, ulong))` |
| `ToEscapedString` | `Extensions.cs:141` | `static string ToEscapedString(this string)` |
| `ToCIdentifier` | `Extensions.cs:162` | `static string ToCIdentifier(this string, bool allowScopeQualifiers = false)` |
| `ToCSharpValue` | `Extensions.cs:182` | `static string ToCSharpValue(this object value, TypeInfo type, Scope usingScope = null)` |

## 7.23 `MetadataVersions`（`Next/MetadataVersions.cs`）

| 字段 | 位置 | 签名 |
|------|------|------|
| `V160`..`V1060` 等 21 个常量 | `MetadataVersions.cs:~10-55` | `static readonly StructVersion` |

## 7.24 `MemberInfo` 基类

| 函数 | 位置 | 签名 |
|------|------|------|
| `GetCustomAttributes(fullTypeName)` | `Reflection/MemberInfo.cs:20` | `CustomAttributeData[] GetCustomAttributes(string fullTypeName)` |
| `ToString()` | `MemberInfo.cs:46` | `override string ToString() => Name` |