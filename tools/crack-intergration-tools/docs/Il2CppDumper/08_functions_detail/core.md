# 08 — Functions Detail: 核心 (Program/Config/Il2Cpp/Metadata)

本文件覆盖 `Program.cs`、`Config.cs`、`Il2Cpp/Il2Cpp.cs`、`Il2Cpp/Metadata.cs`、`Il2Cpp/Il2CppClass.cs`、`Il2Cpp/MetadataClass.cs` 中的所有 public/internal 函数 / 属性 / 构造器。

---

## `Program` (`Program.cs`)

### `Program.Main(string[] args)`
- **签名**：`[STAThread] static void Main(string[] args)`
- **位置**：`Il2CppDumper/Program.cs:14`
- **可见性**：private static（被 runtime 调用）
- **参数**：`args`：命令行参数
- **副作用**：解析 args → 加载 `config.json` → 调用 `Init` → `Dump`；可能弹 `OpenFileDialog`；写 `Console.WriteLine`
- **调用**：被运行时入口调用
- **调用了**：`Config`（System.Text.Json）、`OpenFileDialog`、`Init:119`、`Dump:254`
- **说明**：CLI/GUI 入口。`STAThread` 启用 COM（OpenFileDialog 需要 STA）。

### `Program.ShowHelp()`
- **签名**：`static void ShowHelp()`
- **位置**：`Il2CppDumper/Program.cs:114`
- **可见性**：private static
- **副作用**：打印 usage
- **调用了**：无
- **说明**：被 `Main` 在 `--help` 等触发。

### `Program.Init(string il2cppPath, string metadataPath, out Metadata metadata, out Il2Cpp il2Cpp)`
- **签名**：`private static bool Init(string il2cppPath, string metadataPath, out Metadata metadata, out Il2Cpp il2Cpp)`
- **位置**：`Il2CppDumper/Program.cs:119`
- **可见性**：private static
- **参数**：il2cppPath、metadataPath、两个 out
- **返回值**：true = 成功
- **抛出**：抛 `NotSupportedException("ERROR: il2cpp file not supported.")` 当 magic 不识别时
- **副作用**：实例化对应格式的 `Il2Cpp` 子类；写 Console；调用 `il2Cpp.SetProperties`、`PlusSearch`、`SymbolSearch`、`Search`、`Init`
- **调用**：被 `Main:97` 调用
- **调用了**：`Metadata` 构造、`WebAssembly/NSO/PE/Elf/Elf64/MachoFat/Macho64/Macho` 构造、`il2Cpp.SetProperties`、`il2Cpp.CheckDump`、`il2Cpp.PlusSearch`、`PELoader.Load`、`il2Cpp.Search`、`il2Cpp.SymbolSearch`、`il2Cpp.Init`
- **说明**：完整 magic 探测 + 自动搜索链。

### `Program.Dump(Metadata metadata, Il2Cpp il2Cpp, string outputDir)`
- **签名**：`private static void Dump(Metadata metadata, Il2Cpp il2Cpp, string outputDir)`
- **位置**：`Il2CppDumper/Program.cs:254`
- **可见性**：private static
- **副作用**：写 `dump.cs`、`il2cpp.h`、`script.json`、`stringliteral.json`、`DummyDll/*.dll`
- **调用**：被 `Main:99` 调用
- **调用了**：`new Il2CppExecutor`、`new Il2CppDecompiler.Decompile`、`new StructGenerator.WriteScript`、`DummyAssemblyExporter.Export`
- **说明**：dump 流程的总调度。

---

## `Config` (`Config.cs`)

`Config` 是 POCO，所有字段都是自动属性（getter/setter），由 `System.Text.Json` 反序列化：

| 字段 | 类型 | 行 | 默认 |
|------|------|----|------|
| `DumpMethod` | `bool` | 5 | true |
| `DumpField` | `bool` | 6 | true |
| `DumpProperty` | `bool` | 7 | false |
| `DumpAttribute` | `bool` | 8 | false |
| `DumpFieldOffset` | `bool` | 9 | true |
| `DumpMethodOffset` | `bool` | 10 | true |
| `DumpTypeDefIndex` | `bool` | 11 | true |
| `GenerateDummyDll` | `bool` | 12 | true |
| `GenerateStruct` | `bool` | 13 | true |
| `DummyDllAddToken` | `bool` | 14 | true |
| `RequireAnyKey` | `bool` | 15 | true |
| `ForceIl2CppVersion` | `bool` | 16 | false |
| `ForceVersion` | `double` | 17 | 24.3 |
| `ForceDump` | `bool` | 18 | false |
| `NoRedirectedPointer` | `bool` | 19 | false |

---

## `Il2Cpp` (abstract, `Il2Cpp/Il2Cpp.cs`)

### `Il2Cpp` 构造器
- **签名**：`protected Il2Cpp(Stream stream) : base(stream)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:43`
- **可见性**：protected
- **参数**：stream
- **调用**：由 PE/ELF/MachO/NSO/WASM 子类构造器调用
- **调用了**：`BinaryStream(stream)`
- **说明**：基类构造器，转发给 BinaryStream。

### `Il2Cpp.SetProperties(double version, long metadataUsagesCount)`
- **签名**：`public void SetProperties(double version, long metadataUsagesCount)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:45`
- **可见性**：public
- **参数**：`version` — il2cpp 版本；`metadataUsagesCount`
- **副作用**：赋值 `Version`、`metadataUsagesCount`
- **调用**：被 `Program.Init:182` 调用
- **说明**：必须在 `Init(cr, mr)` 之前调用。

### `Il2Cpp.AutoPlusInit(ulong codeRegistration, ulong metadataRegistration)`
- **签名**：`protected bool AutoPlusInit(ulong codeRegistration, ulong metadataRegistration)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:51`
- **可见性**：protected
- **返回值**：true 表示找到且 init 成功
- **副作用**：可能修改 `Version`（版本细分启发式）；写 Console
- **调用**：被 `PE.PlusSearch:88`、`Elf.PlusSearch:157`、`Elf64.PlusSearch:97`、`Macho.PlusSearch:182`、`Macho64.PlusSearch:244`、`NSO.PlusSearch:229` 调用
- **调用了**：`MapVATR`、`Init`
- **说明**：v24.2+ 启发式判断 24.2/24.3/24.4/24.5、27/27.1、29/29.1、31 子版本。

### `Il2Cpp.Init(ulong codeRegistration, ulong metadataRegistration)`
- **签名**：`public virtual void Init(ulong codeRegistration, ulong metadataRegistration)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:120`
- **可见性**：public virtual
- **副作用**：填充 `methodPointers`、`genericMethodPointers`、`invokerPointers`、`customAttributeGenerators`、`reversePInvokeWrappers`、`unresolvedVirtualCallPointers`、`metadataUsages`、`genericInstPointers`、`genericInsts`、`fieldOffsets`、`types`、`codeGenModules`、`codeGenModuleMethodPointers`、`rgctxsDictionary`、`genericMethodTable`、`methodSpecs`、`methodDefinitionMethodSpecs`、`methodSpecGenericMethodPointers`
- **调用**：被 `Program.Init:236`、`Program.Init:243` 和各种 `Search/SymbolSearch/PlusSearch/UnCompress` 调用
- **调用了**：`MapVATR`、`ReadStringToNull`
- **说明**：核心填充函数；Macho 覆盖以修正 methodPointers 偏移。

### `Il2Cpp.MapVATR<T>(ulong addr)`
- **签名**：`public T MapVATR<T>(ulong addr) where T : new()`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:259`
- **可见性**：public
- **参数**：VA 地址
- **返回值**：结构实例
- **调用了**：`MapVATR(addr)` 抽象方法 + `ReadClass<T>`
- **说明**：在子类解析出的 VA 上做 `ReadClass`。

### `Il2Cpp.MapVATR<T>(ulong addr, ulong count)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:264`
- **签名**：`public T[] MapVATR<T>(ulong addr, ulong count) where T : new()`
- **说明**：数组版（ulong count）。

### `Il2Cpp.MapVATR<T>(ulong addr, long count)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:269`
- **签名**：`public T[] MapVATR<T>(ulong addr, long count) where T : new()`
- **说明**：数组版（long count，用于超过 int.MaxValue 的场景）。

### `Il2Cpp.GetFieldOffsetFromIndex(int typeIndex, int fieldIndexInType, int fieldIndex, bool isValueType, bool isStatic)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:274`
- **签名**：`public int GetFieldOffsetFromIndex(int typeIndex, int fieldIndexInType, int fieldIndex, bool isValueType, bool isStatic)`
- **可见性**：public
- **参数**：typeIndex、fieldIndexInType（type 内偏移）、fieldIndex（全局）、isValueType、isStatic
- **返回值**：字段偏移；失败返回 -1
- **调用**：被 `DummyAssemblyGenerator:208`、`Il2CppDecompiler:196` 调用
- **调用了**：`MapVATR`、`ReadInt32`
- **说明**：v>21 时 fieldOffsets 是指针，需 deref；isValueType + 非静态再减 8/16。

### `Il2Cpp.GetIl2CppType(ulong pointer)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:314`
- **签名**：`public Il2CppType GetIl2CppType(ulong pointer)`
- **可见性**：public
- **返回值**：null 若指针不在已读 types 表
- **调用**：被 `Il2CppExecutor.GetTypeName:68,73,78`、`Il2CppExecutor.GetTypeDefName:154` 等大量调用
- **说明**：通过 `typeDic` O(1) 查找。

### `Il2Cpp.GetMethodPointer(string imageName, Il2CppMethodDefinition methodDef)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:323`
- **签名**：`public ulong GetMethodPointer(string imageName, Il2CppMethodDefinition methodDef)`
- **可见性**：public
- **返回值**：方法 RVA；0 表示无
- **调用**：被 `DummyAssemblyGenerator:304`、`Il2CppDecompiler:253`、`StructGenerator:89` 调用
- **说明**：v<24.2 用 `methodPointers[methodIndex]`；v>=24.2 用 `codeGenModuleMethodPointers[imageName][token & 0x00FFFFFF - 1]`。

### `Il2Cpp.GetRVA(ulong pointer)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2Cpp.cs:343`
- **签名**：`public virtual ulong GetRVA(ulong pointer)`
- **可见性**：public virtual
- **返回值**：基类返回 `pointer`（即虚拟地址）；子类覆盖（如 `PE.GetRVA:96` = `pointer - ImageBase`）
- **调用**：被 `Il2CppDecompiler`、`StructGenerator`、`DummyAssemblyGenerator` 大量调用

### 抽象方法（行 35–41）

```csharp
public abstract ulong MapVATR(ulong addr);
public abstract ulong MapRTVA(ulong addr);
public abstract bool Search();
public abstract bool PlusSearch(int methodCount, int typeDefinitionsCount, int imageCount);
public abstract bool SymbolSearch();
public abstract SectionHelper GetSectionHelper(int methodCount, int typeDefinitionsCount, int imageCount);
public abstract bool CheckDump();
```

每个子类（PE/Elf/Elf64/Macho/Macho64/NSO/WebAssemblyMemory）必须实现，详见 `08_functions_detail/executables.md`。

---

## `Metadata` (`Il2Cpp/Metadata.cs`)

### `Metadata` 构造器
- **签名**：`public Metadata(Stream stream) : base(stream)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:43`
- **可见性**：public
- **参数**：stream
- **副作用**：解析整个 metadata 文件；填充所有 Defs；构建 `attributeTypeRangesDic`（v>24）；填充 `metadataUsageDic`（19~26）
- **抛出**：`InvalidDataException`（magic 错或 version 越界）、`NotSupportedException`（version 不在 16~31 范围）
- **调用**：被 `Program.Init:123` 调用
- **说明**：v24 还要额外分支（24.0/24.1/24.2/24.4）。

### `Metadata.ReadMetadataClassArray<T>(uint addr, int count)`
- **签名**：`private T[] ReadMetadataClassArray<T>(uint addr, int count) where T : new()`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:160`
- **可见性**：private
- **参数**：addr, count（字节数）
- **返回值**：`count / SizeOf(T)` 个元素的数组
- **说明**：自动用 `SizeOf(typeof(T))` 算元素个数。

### `Metadata.GetFieldDefaultValueFromIndex(int index, out Il2CppFieldDefaultValue value)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:165`
- **签名**：`public bool GetFieldDefaultValueFromIndex(int index, out Il2CppFieldDefaultValue value)`
- **可见性**：public
- **调用**：被 `Il2CppDecompiler:167`、`DummyAssemblyGenerator:191` 调用

### `Metadata.GetParameterDefaultValueFromIndex(int index, out Il2CppParameterDefaultValue value)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:170`
- **签名**：`public bool GetParameterDefaultValueFromIndex(int index, out Il2CppParameterDefaultValue value)`
- **可见性**：public
- **调用**：被 `Il2CppDecompiler:318`、`DummyAssemblyGenerator:286` 调用

### `Metadata.GetDefaultValueFromIndex(int index)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:175`
- **签名**：`public uint GetDefaultValueFromIndex(int index)`
- **返回值**：默认值的绝对 metadata 内 offset
- **调用**：被 `Il2CppExecutor.TryGetDefaultValue:328` 调用

### `Metadata.GetStringFromIndex(uint index)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:180`
- **签名**：`public string GetStringFromIndex(uint index)`
- **可见性**：public
- **返回值**：UTF-8 字符串；缓存于 `stringCache`
- **调用**：整个项目最频繁的调用之一（dump.cs / il2cpp.h / DummyDll 都依赖）

### `Metadata.GetCustomAttributeIndex(Il2CppImageDefinition imageDef, int customAttributeIndex, uint token)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:190`
- **签名**：`public int GetCustomAttributeIndex(Il2CppImageDefinition imageDef, int customAttributeIndex, uint token)`
- **可见性**：public
- **返回值**：attribute 在 attributeTypeRanges/attributeDataRanges 中的索引；-1 表示无
- **调用**：被 `Il2CppDecompiler.GetCustomAttribute:403`、`DummyAssemblyGenerator.CreateCustomAttribute:564` 调用

### `Metadata.GetStringLiteralFromIndex(uint index)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:209`
- **签名**：`public string GetStringLiteralFromIndex(uint index)`
- **可见性**：public
- **调用**：被 `StructGenerator.AddMetadataUsageStringLiteral:500` 调用

### `Metadata.ProcessingMetadataUsage()`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:216`
- **签名**：`private void ProcessingMetadataUsage()`
- **可见性**：private
- **副作用**：填充 `metadataUsageDic`、`metadataUsagesCount`
- **调用**：被 ctor 中 `Version < 27` 时调用
- **说明**：把 19~26 的 metadataUsageLists + metadataUsagePairs 展平为 per-usage SortedDictionary。

### `Metadata.GetEncodedIndexType(uint index)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:242`
- **签名**：`public static uint GetEncodedIndexType(uint index)`
- **可见性**：public static
- **返回值**：(index & 0xE0000000) >> 29
- **调用**：被 `StructGenerator:281,782`、`StructGenerator.AddVTableMethod:782` 等多处调用

### `Metadata.GetDecodedMethodIndex(uint index)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:247`
- **签名**：`public uint GetDecodedMethodIndex(uint index)`
- **可见性**：public
- **返回值**：v>=27 时 (index & 0x1FFFFFFEU) >> 1；否则 index & 0x1FFFFFFFU
- **调用**：被 `StructGenerator:284`、`StructGenerator.AddVTableMethod:783` 调用

### `Metadata.SizeOf(Type type)`
- **位置**：`Il2CppDumper/Il2Cpp/Metadata.cs:256`
- **签名**：`public int SizeOf(Type type)`
- **可见性**：public
- **返回值**：按 `[VersionAttribute]` 过滤后的字段字节总数
- **调用**：被 `Il2CppExecutor.GetTypeDefinitionFromIl2CppType:298`、`Il2CppExecutor.GetGenericParameteFromIl2CppType:312` 调用
- **说明**：通过反射遍历字段，primitive/array/struct 三类分别累积大小。

---

## `Il2CppType` (`Il2Cpp/Il2CppClass.cs:139`)

### `Il2CppType.Init(double version)`
- **位置**：`Il2CppDumper/Il2Cpp/Il2CppClass.cs:151`
- **签名**：`public void Init(double version)`
- **可见性**：public
- **副作用**：从 `bits` 拆出 `attrs/type/num_mods/byref/pinned/valuetype`；初始化 `data`
- **调用**：被 `Il2Cpp.Init:199` 对每个 `Il2CppType` 调用
- **说明**：v>=27.2 用 5-bit num_mods，否则 6-bit。

---

## `Metadata` 中的数据类（无方法）

`Il2CppClass.cs` 与 `MetadataClass.cs` 中除上述函数外，其余都是 POD：

- `Il2CppCodeRegistration` (`Il2CppClass.cs:5`)
- `Il2CppMetadataRegistration` (`Il2CppClass.cs:68`)
- `Il2CppTypeEnum` 枚举 (`Il2CppClass.cs:96`)
- `Il2CppType` (`Il2CppClass.cs:139`) + 内部 `Union` (`Il2CppClass.cs:171`)
- `Il2CppGenericClass` (`Il2CppClass.cs:205`)
- `Il2CppGenericContext` (`Il2CppClass.cs:215`)
- `Il2CppGenericInst` (`Il2CppClass.cs:223`)
- `Il2CppArrayType` (`Il2CppClass.cs:229`)
- `Il2CppGenericMethodFunctionsDefinitions` (`Il2CppClass.cs:239`)
- `Il2CppGenericMethodIndices` (`Il2CppClass.cs:245`)
- `Il2CppMethodSpec` (`Il2CppClass.cs:254`)
- `Il2CppCodeGenModule` (`Il2CppClass.cs:261`)
- `Il2CppRange` (`Il2CppClass.cs:292`)
- `Il2CppTokenRangePair` (`Il2CppClass.cs:298`)
- `Il2CppGlobalMetadataHeader` (`MetadataClass.cs:5`)
- `Il2CppAssemblyDefinition` (`MetadataClass.cs:111`)
- `Il2CppAssemblyNameDefinition` (`MetadataClass.cs:125`)
- `Il2CppImageDefinition` (`MetadataClass.cs:143`)
- `Il2CppTypeDefinition` (`MetadataClass.cs:166`) + `IsValueType`、`IsEnum` 派生属性
- `Il2CppMethodDefinition` (`MetadataClass.cs:235`)
- `Il2CppParameterDefinition` (`MetadataClass.cs:263`)
- `Il2CppFieldDefinition` (`MetadataClass.cs:272`)
- `Il2CppFieldDefaultValue` (`MetadataClass.cs:282`)
- `Il2CppPropertyDefinition` (`MetadataClass.cs:289`)
- `Il2CppCustomAttributeTypeRange` (`MetadataClass.cs:301`)
- `Il2CppMetadataUsageList` (`MetadataClass.cs:309`)
- `Il2CppMetadataUsagePair` (`MetadataClass.cs:315`)
- `Il2CppStringLiteral` (`MetadataClass.cs:321`)
- `Il2CppParameterDefaultValue` (`MetadataClass.cs:327`)
- `Il2CppEventDefinition` (`MetadataClass.cs:334`)
- `Il2CppGenericContainer` (`MetadataClass.cs:347`)
- `Il2CppFieldRef` (`MetadataClass.cs:358`)
- `Il2CppGenericParameter` (`MetadataClass.cs:364`)
- `Il2CppRGCTXDataType` 枚举 (`MetadataClass.cs:374`)
- `Il2CppRGCTXDefinitionData` (`MetadataClass.cs:384`)
- `Il2CppRGCTXDefinition` (`MetadataClass.cs:391`) + 动态属性 `type`
- `Il2CppMetadataUsage` 枚举 (`MetadataClass.cs:404`)
- `Il2CppCustomAttributeDataRange` (`MetadataClass.cs:415`)