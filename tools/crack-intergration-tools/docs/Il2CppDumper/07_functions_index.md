# 07 — 函数索引表

按文件名 + 函数名组织。每个 entry 含：签名、所在行、可见性、调用方（grep 结果）。

> 行号基于实际仓库状态。grep 调用方在源码仓库内执行。

---

## `Il2CppDumper/Program.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Main(string[])` | 14 | private static | runtime entry |
| `ShowHelp()` | 114 | private static | `Main:25,31,86` |
| `Init(string,string,out Metadata, out Il2Cpp)` | 119 | private static | `Main:97` |
| `Dump(Metadata, Il2Cpp, string)` | 254 | private static | `Main:99` |

## `Il2CppDumper/Config.cs`

整个 `Config` 类是一组自动属性 + POCO — 见 `08_functions_detail/core.md`。

## `Il2CppDumper/Il2Cpp/Il2Cpp.cs`

| 函数 / 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `MapVATR(ulong)` (abstract) | 35 | public abstract | 各子类实现 |
| `MapRTVA(ulong)` (abstract) | 36 | public abstract | 各子类实现 |
| `Search()` (abstract) | 37 | public abstract | 各子类实现 |
| `PlusSearch(int,int,int)` (abstract) | 38 | public abstract | 各子类实现 |
| `SymbolSearch()` (abstract) | 39 | public abstract | 各子类实现 |
| `GetSectionHelper(int,int,int)` (abstract) | 40 | public abstract | 各子类实现 |
| `CheckDump()` (abstract) | 41 | public abstract | 各子类实现 |
| ctor `(Stream)` | 43 | protected | 由 PE/ELF/... 调用 |
| `SetProperties(double,long)` | 45 | public | `Program.Init:182,217` |
| `AutoPlusInit(ulong,ulong)` | 51 | protected | `PE.PlusSearch:88`、`Elf.PlusSearch:157`、`Elf64.PlusSearch:97`、`Macho.PlusSearch:182`、`Macho64.PlusSearch:244`、`NSO.PlusSearch:229`、`WebAssemblyMemory.PlusSearch:30` |
| `Init(ulong,ulong)` | 120 | public virtual | `Program.Init:236`、`Macho.Init:72`、`SectionHelper`-无直接调用 |
| `MapVATR<T>(ulong)` | 259 | public | 大量 |
| `MapVATR<T>(ulong,ulong)` | 264 | public | 大量 |
| `MapVATR<T>(ulong,long)` | 269 | public | 大量 |
| `GetFieldOffsetFromIndex(...)` | 274 | public | `DummyAssemblyGenerator:208`、`Il2CppDecompiler:196` |
| `GetIl2CppType(ulong)` | 314 | public | 大量 |
| `GetMethodPointer(string,Il2CppMethodDefinition)` | 323 | public | `DummyAssemblyGenerator:304`、`Il2CppDecompiler:253`、`StructGenerator:89` |
| `GetRVA(ulong)` | 343 | public virtual | 大量 |

## `Il2CppDumper/Il2Cpp/Metadata.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor `(Stream)` | 43 | public | `Program.Init:123` |
| `ReadMetadataClassArray<T>(uint,int)` (private) | 160 | private | ctor 内大量调用 |
| `GetFieldDefaultValueFromIndex(int,out)` | 165 | public | `Il2CppDecompiler:167`、`DummyAssemblyGenerator:191` |
| `GetParameterDefaultValueFromIndex(int,out)` | 170 | public | `Il2CppDecompiler:318`、`DummyAssemblyGenerator:286` |
| `GetDefaultValueFromIndex(int)` | 175 | public | `Il2CppExecutor.TryGetDefaultValue:328` |
| `GetStringFromIndex(uint)` | 180 | public | 整个项目最频繁的调用之一 |
| `GetCustomAttributeIndex(Il2CppImageDefinition,int,uint)` | 190 | public | `Il2CppDecompiler.GetCustomAttribute:403`、`DummyAssemblyGenerator.CreateCustomAttribute:564` |
| `GetStringLiteralFromIndex(uint)` | 209 | public | `StructGenerator.AddMetadataUsageStringLiteral:500` |
| `ProcessingMetadataUsage()` (private) | 216 | private | ctor 内（v19~v26） |
| `GetEncodedIndexType(uint)` (static) | 242 | public static | `StructGenerator:281,782` |
| `GetDecodedMethodIndex(uint)` | 247 | public | `StructGenerator:284,783` |
| `SizeOf(Type)` | 256 | public | `Il2CppExecutor.GetTypeDefinitionFromIl2CppType:298`、`Il2CppExecutor.GetGenericParameteFromIl2CppType:312` |

## `Il2CppDumper/Il2Cpp/Il2CppClass.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Il2CppType.Init(double)` | 151 | public | `Il2Cpp.Init:199` |

其余 POCO class（Il2CppCodeRegistration 等）已在 `08_functions_detail/core.md` 列出。

## `Il2CppDumper/Il2Cpp/MetadataClass.cs`

无函数 — 全部 POD。

## `Il2CppDumper/IO/BinaryStream.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `ReadBoolean()` | 34 | public | 未在仓库 grep 到直接调用（BinaryReader 默认） |
| `ReadByte()` | 36 | public | 大量 |
| `ReadBytes(int)` | 38 | public | 大量 |
| `ReadSByte()` | 40 | public | 间接 |
| `ReadInt16/ReadUInt16` | 42/44 | public | 间接 |
| `ReadInt32/ReadUInt32` | 46/48 | public | 大量 |
| `ReadInt64/ReadUInt64` | 50/52 | public | 大量 |
| `ReadSingle/ReadDouble` | 54/56 | public | 间接 |
| `ReadCompressedUInt32/Int32/ULeb128` | 58/60/62 | public | CustomAttributeReader 等 |
| `Write(...)` 重载 | 64-84 | public | Elf/Elf64 RelocationProcessing、PE 等 |
| `Position` (get/set) | 86 | public | 大量 |
| `Length` | 92 | public | 大量 |
| `ReadPrimitive(Type)` (private) | 94 | private | ReadClass 内部 |
| `ReadClass<T>(ulong)` | 109 | public | 大量 |
| `ReadClass<T>()` | 115 | public | 大量 |
| `ReadClassArray<T>(long)` | 185 | public | 间接 |
| `ReadClassArray<T>(ulong,ulong)` | 195 | public | 大量 |
| `ReadClassArray<T>(ulong,long)` | 200 | public | 大量 |
| `ReadStringToNull(ulong)` | 206 | public | 大量 |
| `ReadIntPtr()` | 216 | public | 间接 |
| `ReadUIntPtr()` | 221 | public virtual | Macho64 override |
| `PointerSize` | 226 | public | 大量 |
| `Dispose(bool)` (protected virtual) | 235 | protected | override |
| `Dispose()` | 245 | public | GC |

## `Il2CppDumper/IO/Lz4DecoderStream.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor `(Stream, long)` | 12 | public | `NSO.UnCompress:280,294,308` |
| `Reset(Stream, long)` (private) | 17 | private | ctor |
| `Dispose(bool)` (override) | 34 | protected override | GC |
| `Read(byte[],int,int)` (override) | 87 | public override | `NSO.UnCompress:282,296,310` |
| `ReadByteCore()` (private) | 377 | private | Read |
| `ReadOffsetCore()` (private) | 400 | private | Read |
| `ReadCore(byte[],int,int)` (private) | 449 | private | Read |
| Stream abstract 成员 overrides | 503-537 | public override | GC |

## `Il2CppDumper/Attributes/`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `ArrayLengthAttribute.Length` | 8 | public | `BinaryStream.ReadClass:163,279`（反射） |
| `VersionAttribute.Min/Max` | 8/9 | public | `BinaryStream.ReadClass:127-149`、`Metadata.SizeOf:261` |

## `Il2CppDumper/ExecutableFormats/PE.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor `(Stream)` | 12 | public | `Program.Init:143` |
| `LoadFromMemory(ulong)` | 47 | public | `PELoader.Load:69` |
| `MapVATR(ulong)` | 57 | public override | 由 `Il2Cpp` 调用 |
| `MapRTVA(ulong)` | 68 | public override | 由 `Il2Cpp` 调用 |
| `Search()` | 78 | public override | `Program.Init:223` |
| `PlusSearch(int,int,int)` | 83 | public override | `Program.Init:210,218` |
| `SymbolSearch()` | 91 | public override | `Program.Init:227` |
| `GetRVA(ulong)` | 96 | public override | 大量 |
| `GetSectionHelper(int,int,int)` | 101 | public override | `PlusSearch:85` |
| `CheckDump()` | 127 | public override | `Program.Init:184` |

## `Il2CppDumper/ExecutableFormats/Elf.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 26 | public | `Program.Init:152` |
| `Load()` (protected override) | 32 | protected override | ctor |
| `CheckSection()` (protected override) | 57 | protected override | `ElfBase.CheckDump` |
| `MapVATR` | 80 | public override | 大量 |
| `MapRTVA` | 86 | public override | 大量 |
| `Search` | 96 | public override | `Program.Init:223` |
| `PlusSearch` | 152 | public override | `Program.Init:210` |
| `SymbolSearch` | 160 | public override | `Program.Init:227` |
| `ReadSymbol` (private) | 190 | private | Load |
| `RelocationProcessing` (private) | 243 | private | Load |
| `CheckProtection` (private) | 275 | private | Load |
| `GetRVA` | 310 | public override | 大量 |
| `FixedProgramSegment` (private) | 319 | private | Load (IsDumped) |
| `FixedDynamicSection` (private) | 335 | private | Load (IsDumped) |
| `GetSectionHelper` | 361 | public override | PlusSearch |

## `Il2CppDumper/ExecutableFormats/Elf64.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 18 | public | `Program.Init:148` |
| `Load()` (protected override) | 23 | protected override | ctor |
| `CheckSection()` (protected override) | 48 | protected override | `ElfBase.CheckDump` |
| `MapVATR` | 71 | public override | 大量 |
| `MapRTVA` | 77 | public override | 大量 |
| `Search` | 87 | public override | `Program.Init:223` |
| `PlusSearch` | 92 | public override | `Program.Init:210` |
| `SymbolSearch` | 100 | public override | `Program.Init:227` |
| `ReadSymbol` (private) | 130 | private | Load |
| `RelocationProcessing` (private) | 183 | private | Load |
| `CheckProtection` (private) | 218 | private | Load |
| `GetRVA` | 253 | public override | 大量 |
| `FixedProgramSegment` (private) | 262 | private | Load (IsDumped) |
| `FixedDynamicSection` (private) | 278 | private | Load (IsDumped) |
| `GetSectionHelper` | 304 | public override | PlusSearch |

## `Il2CppDumper/ExecutableFormats/ElfBase.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 7 | protected | 子类 |
| `Load()` (abstract) | 8 | protected abstract | ctor、Reload |
| `CheckSection()` (abstract) | 9 | protected abstract | CheckDump |
| `CheckDump()` | 11 | public override | `Program.Init:184` |
| `Reload()` | 13 | public | `Program.Init:197` |

## `Il2CppDumper/ExecutableFormats/Macho.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 17 | public | `Program.Init:178` |
| `Init(ulong,ulong)` (override) | 70 | public override | `Search` 内调用 |
| `MapVATR` | 77 | public override | 大量 |
| `MapRTVA` | 83 | public override | 大量 |
| `Search` | 93 | public override | `Program.Init:223` |
| `PlusSearch` | 177 | public override | `Program.Init:210` |
| `SymbolSearch` | 185 | public override | `Program.Init:227`（恒 false） |
| `GetRVA` | 190 | public override | 大量 |
| `GetSectionHelper` | 195 | public override | PlusSearch |
| `CheckDump` | 207 | public override | `Program.Init:184`（恒 false） |

## `Il2CppDumper/ExecutableFormats/Macho64.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 17 | public | `Program.Init:175` |
| `MapVATR` | 69 | public override | 大量 |
| `MapRTVA` | 79 | public override | 大量 |
| `Search` | 93 | public override | `Program.Init:223` |
| `PlusSearch` | 239 | public override | `Program.Init:210` |
| `SymbolSearch` | 247 | public override | `Program.Init:227`（恒 false） |
| `GetRVA` | 252 | public override | 大量 |
| `GetSectionHelper` | 257 | public override | PlusSearch |
| `CheckDump` | 269 | public override | `Program.Init:184`（恒 false） |
| `ReadUIntPtr` (override) | 271 | public override | 大量（VA 回环修正） |

## `Il2CppDumper/ExecutableFormats/MachoFat.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 10 | public | `Program.Init:157` |
| `GetMacho(int)` | 32 | public | `Program.Init:168` |

## `Il2CppDumper/ExecutableFormats/NSO.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 21 | public | `Program.Init:139` |
| `ReadSymbol` (private) | 114 | private | ctor (未压缩) |
| `RelocationProcessing` (private) | 167 | private | ctor (未压缩) |
| `MapVATR` | 203 | public override | 大量 |
| `MapRTVA` | 209 | public override | 大量 |
| `Search` | 219 | public override | `Program.Init:223`（恒 false） |
| `PlusSearch` | 224 | public override | `Program.Init:210` |
| `SymbolSearch` | 232 | public override | `Program.Init:227`（恒 false） |
| `UnCompress` | 237 | public | `Program.Init:140` |
| `GetSectionHelper` | 325 | public override | PlusSearch |
| `CheckDump` | 334 | public override | `Program.Init:184`（恒 false） |

## `Il2CppDumper/ExecutableFormats/WebAssembly.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 10 | public | `Program.Init:135` |
| `CreateMemory()` | 47 | public | `Program.Init:136` |

## `Il2CppDumper/ExecutableFormats/WebAssemblyMemory.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 9 | public | `WebAssembly.CreateMemory:57` |
| `MapVATR` | 15 | public override | 大量 |
| `MapRTVA` | 20 | public override | 大量 |
| `PlusSearch` | 25 | public override | `Program.Init:210` |
| `Search` | 33 | public override | `Program.Init:223`（恒 false） |
| `SymbolSearch` | 38 | public override | `Program.Init:227`（恒 false） |
| `GetSectionHelper` | 43 | public override | PlusSearch |
| `CheckDump` | 73 | public override | `Program.Init:184`（恒 false） |

## `Il2CppDumper/Utils/Il2CppExecutor.cs`

| 函数 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 36 | public | `Program.Dump:257` |
| `GetTypeName(Il2CppType,bool,bool)` | 61 | public | 大量（dump.cs / il2cpp.h） |
| `GetTypeDefName(Il2CppTypeDefinition,bool,bool)` | 149 | public | 大量 |
| `GetGenericInstParams(Il2CppGenericInst)` | 181 | public | `GetTypeName:134`、`GetMethodSpecName:213,219` |
| `GetGenericContainerParams(Il2CppGenericContainer)` | 193 | public | `GetTypeName:139`、`GetTypeDefName:175`、`Il2CppDecompiler:276` |
| `GetMethodSpecName(Il2CppMethodSpec,bool)` | 205 | public | `Il2CppDecompiler:377`、`StructGenerator:158,509,849,895` |
| `GetMethodSpecGenericContext(Il2CppMethodSpec)` | 224 | public | `StructGenerator:162` |
| `GetRGCTXDefinition(string,Il2CppTypeDefinition)` | 239 | public | `StructGenerator.AddRGCTX:815` |
| `GetRGCTXDefinition(string,Il2CppMethodDefinition)` | 257 | public | `StructGenerator.GenerateRGCTX:861` |
| `GetGenericClassTypeDefinition(Il2CppGenericClass)` | 275 | public | `GetTypeName:97`、`StructGenerator:62,622,712,942` |
| `GetTypeDefinitionFromIl2CppType(Il2CppType)` | 293 | public | 大量 |
| `GetGenericParameteFromIl2CppType(Il2CppType)` | 307 | public | 大量 |
| `GetSectionHelper()` | 321 | public | `StructGenerator:268` |
| `TryGetDefaultValue(int,int,out object)` | 326 | public | `Il2CppDecompiler:169,320`、`DummyAssemblyGenerator:193,288` |
| `GetConstantValueFromBlob(Il2CppTypeEnum,BinaryReader,out BlobValue)` | 343 | public | `CustomAttributeDataReader.ReadAttributeDataValue:145` |
| `ReadEncodedTypeEnum(BinaryReader,out Il2CppType)` | 464 | public | `CustomAttributeDataReader:144,111` |

## `Il2CppDumper/Utils/DummyAssemblyGenerator.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Assemblies` (List) | 13 | public | `DummyAssemblyExporter:14-20` |
| ctor | 27 | public | `DummyAssemblyExporter.Export:14` |
| `GetTypeReferenceWithByRef` (private) | 451 | private | 内部 |
| `GetTypeReference` (private) | 464 | private | 内部 |
| `CreateCustomAttribute` (private) | 562 | private | pass 4 |
| `TryRestoreCustomAttribute` (private static) | 639 | private static | pass 4 |
| `CreateGenericParameter` (private) | 654 | private | 内部 |
| `CreateCustomAttributeArgument` (private) | 673 | private | pass 4 |
| `GetBlobValueTypeReference` (private) | 709 | private | 内部 |

## `Il2CppDumper/Utils/SectionHelper.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Exec` (property) | 19 | public | 外部几乎不用 |
| `Data` (property) | 20 | public | `StructGenerator:269` |
| `Bss` (property) | 21 | public | 外部几乎不用 |
| ctor | 23 | public | 各格式 `GetSectionHelper` |
| `SetSection(SearchSectionType,Elf32_Phdr[])` | 32 | public | `Elf.GetSectionHelper` |
| `SetSection(SearchSectionType,Elf64_Phdr[])` | 51 | public | `Elf64.GetSectionHelper` |
| `SetSection(SearchSectionType,MachoSection[])` | 70 | public | `Macho.GetSectionHelper` |
| `SetSection(SearchSectionType,MachoSection64Bit[])` | 89 | public | `Macho64.GetSectionHelper` |
| `SetSection(SearchSectionType,ulong,SectionHeader[])` | 108 | public | `PE.GetSectionHelper` |
| `SetSection(SearchSectionType,params NSOSegmentHeader[])` | 127 | public | `NSO.GetSectionHelper` |
| `SetSection(SearchSectionType,params SearchSection[])` | 146 | public | `WebAssemblyMemory.GetSectionHelper` |
| `SetSection(SearchSectionType,List<SearchSection>)` (private) | 151 | private | 内部 |
| `FindCodeRegistration()` | 167 | public | 各格式 PlusSearch |
| `FindMetadataRegistration()` | 198 | public | 各格式 PlusSearch |
| `FindCodeRegistrationOld()` (private) | 211 | private | FindCodeRegistration |
| `FindMetadataRegistrationOld()` (private) | 245 | private | FindMetadataRegistration |
| `FindMetadataRegistrationV21()` (private) | 281 | private | FindMetadataRegistration |
| `CheckPointerRangeDataRa` (private) | 329 | private | FindOld / V21 |
| `CheckPointerRangeExecVa` (private) | 334 | private | FindOld / V21 |
| `CheckPointerRangeDataVa` (private) | 339 | private | V21 |
| `CheckPointerRangeBssVa` (private) | 344 | private | FindOld |
| `FindCodeRegistrationData` (private) | 351 | private | FindCodeRegistration |
| `FindCodeRegistrationExec` (private) | 356 | private | FindCodeRegistration |
| `FindCodeRegistration2019` (private) | 361 | private | FindCodeRegistrationData/Exec |
| `FindReference` (private) | 409 | private | FindCodeRegistration2019 |

## `Il2CppDumper/Utils/CustomAttributeDataReader.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Count` 属性 | 13 | public | `DummyAssemblyGenerator:600`、`Il2CppDecompiler:431` |
| ctor | 15 | public | `Il2CppDecompiler:430`、`DummyAssemblyGenerator:599` |
| `GetStringCustomAttributeData()` | 24 | public | `Il2CppDecompiler:439` |
| `AttributeDataToString(BlobValue)` (private) | 71 | private | GetStringCustomAttributeData |
| `VisitCustomAttributeData()` | 98 | public | `DummyAssemblyGenerator.CreateCustomAttribute:604` |
| `ReadAttributeDataValue()` (private) | 142 | private | Visit/GetString |
| `ReadCustomAttributeNamedArgumentClassAndIndex(Il2CppTypeDefinition)` (private) | 153 | private | Visit/GetString |

## `Il2CppDumper/Utils/PELoader.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `LoadLibrary` (P/Invoke) | 11 | private static extern | `Load:43` |
| `Load(string)` (static) | 14 | public static | `Program.Main:216` |

## `Il2CppDumper/Utils/ArmUtils.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `DecodeMov(byte[])` | 7 | public static | `Macho.Search:114,117,124,154,157,164` |
| `DecodeAdr(ulong,byte[])` | 14 | public static | `Macho64.Search:118,136,179,216` |
| `DecodeAdrp(ulong,byte[])` | 22 | public static | `Macho64.Search:146,149,182,185,219,222` |
| `DecodeAdd(byte[])` | 31 | public static | `Macho64.Search:147,150,183,186,220,223` |
| `IsAdr(byte[])` | 40 | public static | `Macho64.Search:116,134` |

## `Il2CppDumper/Utils/AttributeArgument.cs` / `BlobValue.cs` / `CustomAttributeReaderVisitor.cs`

POCO。无方法（除 `CustomAttributeReaderVisitor` 也无方法，全字段）。

## `Il2CppDumper/Outputs/Il2CppDecompiler.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| ctor | 17 | public | `Program.Dump:258` |
| `Decompile(Config,string)` | 25 | public | `Program.Dump:259` |
| `GetCustomAttribute(Il2CppImageDefinition,int,uint,string)` | 399 | public | `Decompile:65,126,211,249` |
| `GetModifiers(Il2CppMethodDefinition)` | 451 | public | `Decompile:217,224,270` |

## `Il2CppDumper/Outputs/StructGenerator.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `methodInfoCache` (static) | 28 | private static | WriteScript |
| `keyword` (static) | 29 | private static | FixName |
| `specialKeywords` (static) | 32 | private static | FixName |
| ctor | 35 | public | `Program.Dump:264` |
| `WriteScript(string)` | 42 | public | `Program.Dump:265` |
| `AddMetadataUsageTypeInfo` (private) | 434 | private | WriteScript |
| `AddMetadataUsageIl2CppType` (private) | 453 | private | WriteScript |
| `AddMetadataUsageMethodDef` (private) | 464 | private | WriteScript |
| `AddMetadataUsageFieldInfo` (private) | 482 | private | WriteScript |
| `AddMetadataUsageStringLiteral` (private) | 495 | private | WriteScript |
| `AddMetadataUsageMethodRef` (private) | 503 | private | WriteScript |
| `FixName(string)` (private static) | 521 | private static | 大量 |
| `ParseType(Il2CppType,Il2CppGenericContext)` (private) | 542 | private | 大量 |
| `GetMethodTypeSignature(List<Il2CppTypeEnum>)` (public static) | 678 | public static | `WriteScript:137,223` |
| `AddStruct(Il2CppTypeDefinition)` (private) | 697 | private | WriteScript |
| `AddGenericClassStruct(ulong)` (private) | 709 | private | WriteScript |
| `AddParents(Il2CppTypeDefinition,StructInfo)` (private) | 722 | private | AddStruct |
| `AddFields(Il2CppTypeDefinition,StructInfo,Il2CppGenericContext)` (private) | 737 | private | AddStruct |
| `AddVTableMethod(StructInfo,Il2CppTypeDefinition)` (private) | 775 | private | AddStruct |
| `AddRGCTX(StructInfo,Il2CppTypeDefinition)` (private) | 812 | private | AddStruct |
| `GenerateRGCTX(string,Il2CppMethodDefinition)` (private) | 858 | private | WriteScript |
| `ParseArrayClassStruct(Il2CppType,Il2CppGenericContext)` (private) | 905 | private | ParseType/GetIl2CppStructName |
| `GetTypeDefinition(Il2CppType)` (private) | 916 | private | AddMetadataUsageFieldInfo |
| `CreateStructNameDic(Il2CppTypeDefinition)` (private) | 949 | private | WriteScript |
| `GetUniqueName(string)` (private) | 957 | private | CreateStructNameDic |
| `RecursionStructInfo(StructInfo)` (private) | 968 | private | WriteScript |
| `GetIl2CppStructName(Il2CppType,Il2CppGenericContext)` (private) | 1128 | private | AddStruct/ParseType/... |
| `IsValueType(Il2CppType,Il2CppGenericContext)` (private) | 1224 | private | AddFields |
| `IsCustomType(Il2CppType,Il2CppGenericContext)` (private) | 1270 | private | AddFields |
| `GenerateMethodInfo(string,string,List<StructRGCTXInfo>)` (private) | 1336 | private | WriteScript |

## `Il2CppDumper/Outputs/DummyAssemblyExporter.cs`

| 成员 | 行 | 可见性 | 调用方 |
|------|----|----|----|
| `Export(Il2CppExecutor,string,bool)` (static) | 7 | public static | `Program.Dump:271` |

## `Il2CppDumper/Outputs/ScriptJson.cs`

POCO，无方法。

## `Il2CppDumper/Outputs/StructInfo.cs`

POCO，无方法。

## `Il2CppDumper/Outputs/Il2CppConstants.cs`

POCO 常量，无方法。

## `Il2CppDumper/Outputs/HeaderConstants.cs`

静态字符串字段：
- `GenericHeader` :5
- `HeaderV29` :45
- `HeaderV27` :154
- `HeaderV240` (~280)
- `HeaderV241` (~350)
- `HeaderV242` (~420)
- `HeaderV22` (~540)