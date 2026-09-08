# 05 操作链

下面用 mermaid 图与文字描述 Il2CppDumper 的 7 条主操作链。

---

## 链 1 — 自动模式完整 Dump 流程

`Program.Main` 入口 → 探测格式 → `Init(cr, mr)` → `Dump(...)` 三输出。

```mermaid
flowchart TD
    Start([Program.Main args/GUI]) --> ParseCfg[加载 config.json]
    ParseCfg --> ReadMeta["ReadAllBytes(metadata.dat)<br/>new Metadata(stream)"]
    ReadMeta --> MetaLoad["Metadata ctor 解析<br/>imageDefs / typeDefs / methodDefs ..."]
    MetaLoad --> ReadBin["ReadAllBytes(il2cpp binary)"]
    ReadBin --> SwitchMagic{"首 4 字节 magic"}
    SwitchMagic -->|"0x6D736100"| WASM[WebAssembly + WebAssemblyMemory]
    SwitchMagic -->|"0x304F534E"| NSO[NSO + UnCompress]
    SwitchMagic -->|"0x905A4D"| PE[PE]
    SwitchMagic -->|"0x464C457F"| ELF{byte 4 == 2?}
    SwitchMagic -->|"0xCAFEBABE / 0xBEBAFECA"| MachoFat[选择切片]
    SwitchMagic -->|"0xFEEDFACE"| Macho32[Macho]
    SwitchMagic -->|"0xFEEDFACF"| Macho64[Macho64]
    ELF -->|是| Elf64[Elf64]
    ELF -->|否| Elf32[Elf]

    WASM --> SetProp[SetProperties version, muCount]
    NSO --> SetProp
    PE --> SetProp
    Elf64 --> SetProp
    Elf32 --> SetProp
    MachoFat --> Macho32
    Macho32 --> SetProp
    Macho64 --> SetProp

    SetProp --> CheckDump{"config.ForceDump OR CheckDump?"}
    CheckDump -->|是 + 是 ELF| PromptELF["prompt user dump addr<br/>可能 Reload()<br/>IsDumped=true"]
    CheckDump -->|是 + 其他| SetDumped[IsDumped=true]
    CheckDump -->|否| Search

    PromptELF --> Search[开始搜索]
    SetDumped --> Search

    Search --> PlusS{PlusSearch OK?}
    PlusS -->|否 + Windows + PE| PELoader["PELoader.Load (LoadLibrary)"]
    PlusS -->|否 + 其他| Search2
    PELoader --> Search2
    PlusS -->|是| Init[Init cr, mr]

    Search2[Search] -->|否| SymS[SymbolSearch]
    SymS -->|否| Manual[用户手动输入 cr, mr]
    SymS -->|是| Init
    Manual --> Init

    Init --> VerFix{"v >= 27 && IsDumped?<br/>image base 反推"}
    VerFix --> Dumping

    Dumping[Dumping ...] --> NewExec[Il2CppExecutor ctor]
    NewExec --> NewDecomp[Il2CppDecompiler ctor]
    NewDecomp --> Decompile[Decompile -> dump.cs]
    Decompile --> CondStruct{config.GenerateStruct?}
    CondStruct -->|是| StructGen[StructGenerator -> il2cpp.h + script.json + stringliteral.json]
    CondStruct -->|否| CondDummy
    StructGen --> CondDummy{config.GenerateDummyDll?}
    CondDummy -->|是| DummyExport["DummyAssemblyExporter.Export -> DummyDll/*.dll"]
    CondDummy -->|否| Done
    DummyExport --> Done([Done!])
```

文字版：

1. `Program.Main:14` 解析 CLI args / 弹 GUI。
2. `Program.Init:119` 加载 metadata → `Metadata` ctor 解析所有 Defs。
3. `Program.Init:127` 读 il2cpp binary，按 magic 实例化格式子类。
4. `Program.Init:181` `il2Cpp.SetProperties(version, metadataUsagesCount)`（来自 `Il2Cpp/Il2Cpp.cs:45`）。
5. `Program.Init:184` 决定是否 IsDumped；ELF 时可能 `Reload()`（`ElfBase.cs:13`）。
6. `Program.Init:210` `PlusSearch` → 失败则尝试 `PELoader.Load`（仅 Windows + PE）。
7. `Program.Init:223` `Search()` → `Program.Init:227` `SymbolSearch()` → `Program.Init:236` 用户手动。
8. `Il2Cpp.Init:120` 填充 methodPointers、genericInsts、types、codeGenModules（v24.2+）等。
9. `Program.Init:238` v>=27 + IsDumped 时用 typeDef[0] 反推 metadata.ImageBase。
10. `Program.Dump:254` 启动 dump：decompiler → struct → DummyDll。

---

## 链 2 — Metadata 解析 + 版本分支

```mermaid
flowchart TD
    Start([new Metadata stream]) --> Sanity{"sanity == 0xFAB11BAF?"}
    Sanity -->|否| InvalidData[throw InvalidDataException]
    Sanity -->|是| VerChk{"version 16~31?"}
    VerChk -->|否| NotSupp[throw NotSupportedException]
    VerChk -->|是| ReadHeader[ReadClass Il2CppGlobalMetadataHeader]
    ReadHeader --> V24br{v == 24 && stringLiteralOffset == 264?}
    V24br -->|是| Ver242[Version = 24.2]
    V24br -->|否| ImageAny
    Ver242 --> ImageAny{imageDefs.Any token != 1?}
    ImageAny -->|是| Ver241[Version = 24.1]
    ImageAny -->|否| ReadImage
    Ver241 --> ReadImage

    ReadImage[ReadClassArray imageDefs] --> AsmSize{Version == 24.2 && assembliesSize/68 < imageDefs.Length?}
    AsmSize -->|是| Ver244[Version = 24.4]
    AsmSize -->|否| V241P{Version == 24.1 && assembliesSize/64 == imageDefs.Length?}
    V241P -->|是| SetV241P[v241Plus=true]
    V241P -->|否| ReadAsm
    SetV241P --> Ver244_2[Version = 24.4]
    Ver244 --> ReadAsm
    Ver244_2 --> ReadAsm[ReadClassArray assemblyDefs]

    ReadAsm --> CondV241P{v241Plus?}
    CondV241P -->|是| Restore241[Version = 24.1]
    CondV241P -->|否| ReadDefs

    ReadDefs[Read all Defs<br/>typeDefs, methodDefs, parameterDefs, fieldDefs, propertyDefs, eventDefs, genericContainers, genericParameters, stringLiterals] --> Vgate{version 范围?}
    Vgate -->|v > 16| ReadFieldRefs[fieldRefs]
    Vgate -->|v < 27 + v > 16| ReadUsage[metadataUsageLists + metadataUsagePairs + ProcessingMetadataUsage]
    Vgate -->|v > 20 && v < 29| ReadAttrRange[attributeTypeRanges + attributeTypes]
    Vgate -->|v >= 29| ReadAttrData[attributeDataRanges]
    Vgate -->|v > 24| BuildAttrDic[attributeTypeRangesDic]
    Vgate -->|v <= 24.1| ReadRGCTX[rgctxEntries]
    Vgate --> End([Metadata 就绪])
    ReadFieldRefs --> Vgate
    ReadUsage --> Vgate
    ReadAttrRange --> Vgate
    ReadAttrData --> Vgate
    BuildAttrDic --> Vgate
    ReadRGCTX --> End
```

`Metadata.cs:43-158` 集中体现了"分支因版本而异"的实现风格：所有数组加载用 `ReadMetadataClassArray<T>`，根据 `Version` 决定 `count / SizeOf`。

---

## 链 3 — PlusSearch → SymbolSearch → Search 兜底链

```mermaid
flowchart TD
    Start([PlusSearch methodCount typeDefCount imageCount]) --> SH[GetSectionHelper]
    SH --> FCR[FindCodeRegistration]
    FCR --> CR24{"Version >= 24.2?"}
    CR24 -->|否| FindOld[FindCodeRegistrationOld<br/>data section 扫描 intptr == methodCount]
    CR24 -->|是| FormatB{是 ElfBase?}
    FormatB -->|是| TryExec[FindCodeRegistrationExec 先 exec 段]
    FormatB -->|否| TryData[FindCodeRegistrationData 先 data 段]
    TryExec --> R1{找到?}
    TryExec -->|否| TryData
    TryData --> R2{找到?}
    R1 -->|是| SetExec[pointerInExec=true]
    R2 -->|是 + 是 ElfBase| FMR
    R2 -->|否| FMR
    R1 -->|否| FMR
    SetExec --> FMR

    FMR[FindMetadataRegistration] --> FMRV{Version?}
    FMRV -->|< 19| Zero[return 0]
    FMRV -->|>= 27| V21[FindMetadataRegistrationV21]
    FMRV -->|19~26.999| OldMR[FindMetadataRegistrationOld]

    OldMR --> ScanData[data section 扫描 intptr == typeDefCount]
    ScanData --> ValidMR{指针指向 data 段? + 后续 metadataUsages 全部在 bss?}
    ValidMR -->|是| ReturnMR[return addr - ptr*12]
    ValidMR -->|否| Cont[继续扫描]

    V21 --> ScanV21["data 扫描，连续两个 intptr == typeDefCount"]
    ScanV21 --> ValidV21{指针指向 data 段?}
    ValidV21 -->|是 + Exec| ReturnExec[Exec range 检查]
    ValidV21 -->|是 + Data| ReturnData[Data range 检查]
    ValidV21 -->|否| Cont

    ReturnMR --> AutoPlus[AutoPlusInit cr, mr]
    ReturnExec --> AutoPlus
    ReturnData --> AutoPlus

    AutoPlus --> VerInit{"Version >= 24.2?<br/>用 CodeRegistration 启发式细分 24.x / 27.x / 29.x"}
    VerInit --> Init[Il2Cpp.Init cr, mr]
    Init --> End([return true])

    Init -.失败.-> SymSearch[SymbolSearch]
    SymSearch -.失败.-> SearchFallback[Search]
    SearchFallback -.失败.-> Manual[用户手动输入]
```

`PlusSearch` 在 PE/ELF/MachO/NSO/WASM 各自子类中实现，但都委托给同一 `SectionHelper`（`Utils/SectionHelper.cs`）的 `FindCodeRegistration/FindMetadataRegistration`。`Search()` 是 MachO/Macho64/Elf32 的 ARM 字节模式扫描；`SymbolSearch()` 仅 Elf/Elf64 实现了基于 ELF `.dynsym` 的符号表查找。

---

## 链 4 — `dump.cs` 生成

```mermaid
sequenceDiagram
    autonumber
    participant U as Program.Dump
    participant Dec as Il2CppDecompiler
    participant Exe as Il2CppExecutor
    participant Meta as Metadata
    participant I as Il2Cpp
    participant FW as StreamWriter

    U->>Dec: Decompile(config, outputDir)
    Dec->>FW: new StreamWriter(dump.cs)
    loop imageIndex in imageDefs
        Dec->>FW: "// Image N: <name> - <typeStart>"
    end
    loop imageDef in imageDefs
        Dec->>Exe: 解析 parent/interfaces
        Dec->>FW: 写 namespace
        Dec->>Dec: visibility/static/abstract/sealed 决定
        Dec->>Exe: GetTypeDefName(typeDef, false, true)
        Dec->>FW: 写 class Foo : Parent, IFoo // TypeDefIndex: N {
        opt config.DumpField
            loop fieldDef
                Dec->>Meta: GetFieldDefaultValueFromIndex
                Dec->>Exe: TryGetDefaultValue
                Dec->>I: GetFieldOffsetFromIndex
                Dec->>FW: "  public int x = 5; // 0x10"
            end
        end
        opt config.DumpProperty
            loop propertyDef
                Dec->>FW: "  int Bar { get; set; }"
            end
        end
        opt config.DumpMethod
            loop methodDef
                opt config.DumpMethodOffset
                    Dec->>I: GetMethodPointer(imageName, methodDef)
                    Dec->>I: GetRVA(pointer)
                    Dec->>FW: "// RVA: 0x... Offset: 0x... VA: 0x... Slot: N"
                end
                Dec->>Exe: GetModifiers
                Dec->>FW: "  public int M(int p) { }"
                opt methodDefinitionMethodSpecs 命中
                    Dec->>FW: GenericInstMethod 注释块
                end
            end
        end
        Dec->>FW: "}"
    end
    Dec->>FW: Close()
```

`Outputs/Il2CppDecompiler.cs:25` 入口。详细字段规则见 `08_functions_detail/output.md`。

---

## 链 5 — `il2cpp.h` + scripts 生成

```mermaid
flowchart TD
    Start([StructGenerator.WriteScript outDir]) --> InitDic[遍历 imageDef.typeDefs<br/>填 typeDefImageNames + structNameDic]
    InitDic --> GenInst[遍历 IL2CPP_TYPE_GENERICINST 的 type<br/>填 nameGenericClassDic + genericClassStructNameDic]
    GenInst --> Loop[遍历每个 typeDef 方法]
    Loop --> PerMethod[Per-method 生成 ScriptMethod<br/>含 Address / Name / Signature / TypeSignature]
    PerMethod --> PerSpec[methodSpecs 的每个 instance<br/>生 MethodInfo_{addr:X} 结构]
    PerSpec --> OrderPtr[合并 codeGenModuleMethodPointers / genericMethodPointers / invokerPointers / customAttributeGenerators / reversePInvokeWrappers / unresolvedVirtualCallPointers -> 去重 + 排序 + 去 0]
    OrderPtr --> Addrs[填 json.Addresses]
    Addrs --> MU{Version >= 27?}
    MU -->|是| ScanData["data section 扫描 encoded token<br/>调 AddMetadataUsage* 写入 ScriptMetadata/Method/String"]
    MU -->|否| MU19{Version > 16?}
    MU19 -->|是| LookupMU["遍历 metadataUsageDic[Usage]<br/>填 Script* via metadataUsages[i.Key]"]
    MU19 -->|否| Skip[跳过]
    ScanData --> StrLit[写 stringliteral.json]
    LookupMU --> StrLit
    Skip --> StrLit

    StrLit --> ScriptJSON[写 script.json]
    ScriptJSON --> GenStruct[遍历 genericClassList 添加 generic class struct]
    GenStruct --> Recurse[RecursionStructInfo 递归输出 _Fields/_RGCTXs/_VTable/_c/_o/_StaticFields]
    Recurse --> HeaderV{"Version?"}
    HeaderV -->|22| H22[HeaderV22]
    HeaderV -->|23/24| H240[HeaderV240]
    HeaderV -->|24.1| H241[HeaderV241]
    HeaderV -->|24.2~24.5| H242[HeaderV242]
    HeaderV -->|27/27.1/27.2| H27[HeaderV27]
    HeaderV -->|29/29.1/31| H29[HeaderV29]
    HeaderV -->|其他| Warn[WARNING: 不支持生成 .h]
    H22 --> WriteH[写 il2cpp.h]
    H240 --> WriteH
    H241 --> WriteH
    H242 --> WriteH
    H27 --> WriteH
    H29 --> WriteH
    Warn --> End
    WriteH --> End([结束])
```

`Outputs/StructGenerator.cs:42` 入口；关键策略：

- 每个 typeDef 对应一个 `TypeName_o` C struct，内嵌 `TypeName_c`（类常量）和 `TypeName_Fields`（实例字段）。
- v24.2+ 用 `codeGenModuleMethodPointers`；v<24.2 用 `methodPointers`。
- MetadataUsage 还原成 IDA 可读的 `Method$<FullName>()`、`Field$<FullName>`、`String$...`。

---

## 链 6 — DummyDll 生成

```mermaid
sequenceDiagram
    autonumber
    participant P as Program.Dump
    participant Ex as DummyAssemblyExporter.Export
    participant Gen as DummyAssemblyGenerator ctor
    participant Dag as DummyAssemblyGenerator.CreateCustomAttribute
    participant Cdr as CustomAttributeDataReader
    participant Cecil as Mono.Cecil

    P->>Ex: Export(executor, outDir, addToken)
    Ex->>Ex: 创建 DummyDll/ 目录
    Ex->>Gen: new DummyAssemblyGenerator(executor, addToken)
    Gen->>Cecil: ReadAssembly(Il2CppDummyDll resource)
    Gen->>Cecil: AddressAttribute / FieldOffsetAttribute / TokenAttribute / MetadataOffsetAttribute references
    Gen->>Gen: pass1 - 创建 assemblyDefinition + 类型外壳
    Gen->>Gen: pass1 - nested types
    Gen->>Gen: pass2 - genericContainer / parent / interfaces (Cecil)
    Gen->>Gen: pass3 - fields + defaults + offsets
    Gen->>Gen: pass3 - methods (空 stub body)
    Gen->>Gen: pass3 - properties + events
    opt Version > 20
        Gen->>Gen: pass4 - custom attributes
        alt Version < 29
            Gen->>Cecil: 写 AttributeAttribute stub (RVA/Offset/VA)
        else Version >= 29
            Gen->>Cdr: new CustomAttributeDataReader(executor, blob)
            Cdr->>Gen: VisitCustomAttributeData -> Arguments/Fields/Properties
            Gen->>Cecil: 真正构造 [Foo(arg=...)]
        end
    end
    Ex->>Cecil: assembly.Write(stream)
    Ex->>Ex: File.WriteAllBytes(<imageName>.dll, ...)
```

`Utils/DummyAssemblyGenerator.cs:27` 入口。stub body：

- `void` 方法：单条 `ret`
- 值类型方法：`initobj` + `ldloc.0` + `ret`
- 引用类型方法：`ldnull` + `ret`

---

## 链 7 — v29+ Custom Attribute 恢复

```mermaid
sequenceDiagram
    autonumber
    participant Dec as Il2CppDecompiler.GetCustomAttribute
    participant Meta as Metadata
    participant Cdr as CustomAttributeDataReader
    participant Exe as Il2CppExecutor
    participant I as Il2CppType

    Dec->>Meta: GetCustomAttributeIndex(imageDef, customAttributeIndex, token)
    alt 命中
        alt Version < 29
            Dec->>Meta: attributeTypeRanges[i]
            Dec->>Exe: customAttributeGenerators[attributeIndex]
            Dec->>I: GetTypeName(attributeType, false, false)
            Dec-->>Dec: "[FooAttribute] // RVA: 0xN Offset: 0xN VA: 0xN"
        else Version >= 29
            Dec->>Meta: attributeDataRanges[i]
            Dec->>Meta: ReadBytes(endOffset - startOffset)
            Dec->>Cdr: new CustomAttributeDataReader(executor, blob)
            loop count 次
                Dec->>Cdr: VisitCustomAttributeData
                Cdr->>Meta: ReadCompressedUInt32 (ctorIndex)
                Cdr->>Meta: ReadCompressedUInt32 x3 (arg/field/prop counts)
                loop arg
                    Cdr->>Exe: ReadEncodedTypeEnum
                    Cdr->>Exe: GetConstantValueFromBlob
                end
                loop field/prop
                    Cdr->>Meta: ReadCompressedInt32 (memberIndex)
                    Cdr->>Meta: typeDefs[typeIndex] (跨类 field/prop)
                    Cdr->>Exe: ReadAttributeDataValue
                end
                Dec-->>Dec: "[Foo(arg1, fieldName=value, propName=value)]"
            end
        end
    else 未命中
        Dec-->>Dec: 返回 string.Empty
    end
```

`Utils/CustomAttributeDataReader.cs:98` `VisitCustomAttributeData` 是核心；`AttributeDataToString:71` 把 BlobValue 转字符串。枚举值的处理走 `ReadEncodedTypeEnum:464` (`Il2CppExecutor.cs:464`)。