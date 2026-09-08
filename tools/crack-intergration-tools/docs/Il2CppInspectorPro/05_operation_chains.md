# 05 · 主要操作链（每条配 mermaid）

> 每条链都标注：输入 → 入口文件 + 函数 → 关键步骤 → 输出。
> 来源已逐条用 `grep -n` 与源文件交叉核对。

---

## 5.1 主 CLI 入口 → 加载 binary + metadata → 输出文件

**入口**：`Il2CppInspector.CLI/Program.cs:Main` → `App.Run(options)` → 全部 emitter

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant P as Program.Main
    participant C as CommandLineParser
    participant PM as PluginManager
    participant IP as Il2CppInspector
    participant FS as FileFormatStream
    participant IB as Il2CppBinary
    participant MD as Metadata
    participant TM as TypeModel
    participant AM as AppModel
    participant EM as Emitter (CSharp/Cpp/JSON/DLL/Py)

    U->>P: dotnet Il2Inspector.dll -i bin -m meta
    P->>C: ParseArguments<Options>(args)
    C-->>P: Options
    P->>PM: PluginManager.EnsureInit()
    PM-->>P: ready
    P->>IP: LoadFromPackage([bin])
    alt 是 APK/AAB/IPA/Zip
        IP->>IP: GetStreamsFromPackage(...)
        IP->>FS: FileFormatStream.Load(binStream)
        IP->>MD: Metadata.FromStream(metaStream)
    else 是裸文件
        IP->>FS: FileFormatStream.Load(binStream)
        IP->>MD: Metadata.FromStream(metaStream)
    end
    FS-->>IP: IFileFormatStream
    MD-->>IP: Metadata
    loop 每个 image
        IP->>IB: Il2CppBinary.Load(image, metadata)
        IB->>IB: FindRegistrationStructs
        IB->>IB: PrepareMetadata
        IB-->>IP: binary
    end
    IP->>IP: new Il2CppInspector(b, m)
    IP-->>P: List<Il2CppInspector>
    P->>TM: new TypeModel(il2cpp)
    P->>AM: new AppModel(model, false)
    P->>AM: AppModel.Build(unityVersion, compiler)
    opt 需要 C# 输出
        P->>EM: new CSharpCodeStubs(model).WriteSingleFile(cs-out)
    end
    opt 需要 C++ 注入工程
        P->>EM: new CppScaffolding(am).Write(cpp-out)
    end
    opt 需要 JSON
        P->>EM: new JSONMetadata(am).Write(json-out)
    end
    opt 需要 Dummy DLL
        P->>EM: new AssemblyShims(model).Write(dll-out)
    end
    opt 需要 Python
        P->>EM: new PythonScript(am).WriteScriptToFile(py-out, target, h, json)
    end
    EM-->>U: 文件落地
```

---

## 5.2 C# 源代码生成（CSharpCodeStubs）

**入口**：`Outputs/CSharpCodeStubs.cs:CSharpCodeStubs(TypeModel)` → 任一 `Write*` 方法

```mermaid
flowchart TD
    Start([CSharpCodeStubs ctor]) --> Choice{选择布局}

    Choice -->|single| WSF[WriteSingleFile outFile]
    Choice -->|namespace| WFN[WriteFilesByNamespace outPath orderBy flatten]
    Choice -->|assembly| WFA[WriteFilesByAssembly outPath orderBy separateAttributes]
    Choice -->|class| WFC[WriteFilesByClass outPath flatten]
    Choice -->|tree| WFCT[WriteFilesByClassTree outPath separateAttributes]
    Choice -->|project| WS[WriteSolution outPath unityPath unityAsm]

    WSF --> Parallel
    WFN --> Parallel
    WFA --> Parallel
    WFC --> Parallel
    WFCT --> Parallel

    Parallel[Parallel.ForEach types] --> Filter{过滤}
    Filter -->|skip Locale + MustCompile| Filter
    Filter -->|skip Nested| Filter
    Filter --> GenType[generateType<br/>usings + fields + properties + methods + events + attributes]

    WS --> WFCT
    WS --> Templates[Resources.SlnProjectDefinition<br/>SlnProjectConfiguration<br/>CsProjTemplate<br/>CsSlnTemplate]
    Templates --> WriteSln[File.WriteAllText .sln]

    GenType --> WriteFile[File.WriteAllText outFile]
    WriteSln --> Done
    WriteFile --> Done([生成完成])
```

---

## 5.3 C++ scaffolding 生成（CppScaffolding + CppDeclarationGenerator）

**入口**：`Outputs/CppScaffolding.cs:CppScaffolding(AppModel)` → `Write(projectPath)`

```mermaid
flowchart TD
    Start([AppModel 已 Build]) --> Ctor[CppScaffolding model<br/>useBetterArraySize, includeUnresolved]
    Ctor --> WT[WriteTypes appdata/il2cpp-types.h]
    WT --> Banner[Header banner + primitive typedefs +<br/>decompiler guards + better-array-size]
    Banner --> UH[model.UnityHeaders.GetTypeHeaderText WordSizeBits]
    UH --> PragmaWarnings[#pragma warning MSVC 4369/4309/4359]
    PragmaWarnings --> NS[namespace app]
    NS --> Fwd[writeForwardDefinitions]
    Fwd --> Groups[writeTypesForGroup x5<br/>required_forward_definitions<br/>types_from_methods<br/>types_from_generic_methods<br/>types_from_usages<br/>unused_concrete_types]

    Groups --> Write[Write projectPath]
    Write --> APIfn[il2cpp-api-functions.h<br/>filter AvailableAPIs]
    Write --> APIptr[il2cpp-api-functions-ptr.h<br/>#define name_ptr 0xfileOff]
    Write --> TypesPtr[il2cpp-types-ptr.h<br/>DO_TYPEDEF addr, name]
    Write --> Functions[il2cpp-functions.h<br/>DO_APP_FUNC + DO_APP_FUNC_METHODINFO]
    Write --> VerH[il2cpp-metadata-version.h]
    Write --> Frameworks{./libraries/ 存在?}
    Frameworks -->|是| Extract[extract imgui.zip / detours.zip / handlers.zip]
    Frameworks -->|否| Skip[跳过]
    Extract --> Frame[write framework/<br/>dllmain.cpp helpers.cpp/h<br/>il2cpp-appdata.h il2cpp-init.cpp/h<br/>pch-il2cpp.cpp/h version.cpp/h]
    Skip --> Frame
    Frame --> User[user/main.cpp/h settings.cpp/h<br/>仅当不存在]
    User --> Def[definitions/version.def]
    Def --> Proj[Resources.CppProjTemplate → name.vcxproj]
    Proj --> Filters[Resources.CppProjFilters → .vcxproj.filters]
    Filters --> Sln[Resources.CppSlnTemplate → name.sln]
    Sln --> Done([完整 VS C++ 工程就绪])
```

---

## 5.4 Redux GUI 启动流程

**入口**：`Il2CppInspector.Redux.GUI/Program.cs:Main` → `UiProcessService.LaunchUiProcess(port)` → Tauri WebView

```mermaid
sequenceDiagram
    autonumber
    participant U as User
    participant G as Il2Inspector.Redux.GUI.exe
    participant B as WebApplication
    participant H as Il2CppHub /il2cpp
    participant UPS as UiProcessService
    participant T as Tauri exe (Rust+Svelte)
    participant SR as SignalR
    participant FC as FrontendCore UiContext

    U->>G: 双击 exe
    G->>B: WebApplication.CreateSlimBuilder(args)
    B->>B: AddFrontendCore()<br/>Configure JsonHubProtocolOptions
    B->>B: AddSingleton UiProcessService
    B->>H: app.MapFrontendCore()<br/>app.MapHub<Il2CppHub>("/il2cpp")
    B->>B: app.StartAsync()
    B->>B: var port = Uris.First().Port
    B->>UPS: LaunchUiProcess(port)
    UPS->>UPS: ExtractUiExecutable<br/>embedded → %TEMP%/il2cppinspectorredux-ui/
    UPS->>T: Process.Start tauri-exe.exe argv[0]=port
    T->>T: 启动 WebView
    T->>SR: http://localhost:port/il2cpp/negotiate
    SR->>H: connection
    H-->>T: connectionId
    T->>H: OnUiLaunched()
    H->>FC: InitializeAsync(client)
    U->>T: 选择 binary + metadata
    T->>H: SubmitInputFiles paths
    H->>FC: LoadInputFilesAsync client files
    FC-->>T: OnImportCompleted
    U->>T: 选择输出格式 + 参数
    T->>H: QueueExport id path settings
    H->>FC: QueueExportAsync
    U->>T: 点 Start
    T->>H: StartExport
    H->>FC: StartExportAsync
    FC->>FC: IOutputFormat.Export(model, client, ...)
    FC-->>T: ShowSuccessToast + log
```

---

## 5.5 插件加载流程（PluginManager）

**入口**：`Plugins/Internal/PluginManager.cs:EnsureInit` → `Reload(pluginPath)`

```mermaid
flowchart TD
    Start([CLI/GUI 启动]) --> Ensure[PluginManager.EnsureInit]
    Ensure --> IsInit{AsInstance != null?}
    IsInit -->|是| Done1([就绪])
    IsInit -->|否| Reload[Reload pluginPath=null reset=true coreOnly=false]
    Reload --> Reset{singleton.ManagedPlugins.Clear if reset}
    Reset --> Enabled{PluginManager.Enabled?}
    Enabled -->|否| Skip([跳过])
    Enabled -->|是| Folder[pluginFolder = exeDir/plugins]
    Folder --> Exists{Directory.Exists?}
    Exists -->|否| Throw[DirectoryNotFoundException]
    Exists -->|是| Loop[foreach *.dll in plugins/**]
    Loop --> Load[PluginLoader.CreateFromAssemblyFile dll<br/>sharedTypes: V100.IPlugin]
    Load --> Asm[loader.LoadDefaultAssembly]
    Asm --> Types[asm.GetTypes]
    Types --> Assignable{typeof IPlugin && !IsAbstract?}
    Assignable -->|否| Loop
    Assignable -->|是| Create[Activator.CreateInstance type]
    Create --> AsCore{is ICorePlugin?}
    AsCore -->|是| Add1[Add ManagedPlugin Enabled=true]
    AsCore -->|否| Add2[Add ManagedPlugin Enabled=false]
    Add1 --> Loop
    Add2 --> Loop

    Loop -->|完成| CLIOpts[CLI: PluginOptions.GetPluginOptionTypes<br/>IL emit 动态生成 OptionAttribute]
    CLIOpts --> ParseOpts[CommandLineParser 解析 --plugins 'id --opt val']
    ParseOpts --> Hooks[Pipeline 推进时调用 PluginHooks.xxx<br/>PluginManager.Try 转发到每个 Enabled plugin]
    Hooks --> Recurse[栈追踪递归保护<br/>[Reentrant] 可选豁免]
    Recurse --> Done1
```

---

## 5.6 PE/ELF/Mach-O/NSO 分支解析

**入口**：`FileFormatStreams/FileFormatStream.cs:Load`

```mermaid
flowchart TD
    Start([FileFormatStream.Load stream loadOptions]) --> Copy[stream.CopyTo BinaryObjectStream]
    Copy --> PrePlugin[PluginHooks.PreProcessImage]
    PrePlugin --> Probe[反射遍历所有非 abstract 的 IFileFormatStream 实现]
    Probe --> Try1[PEReader.Load<br/>检测 MZ + COFF + Section]
    Try1 -->|成功| Ret1[return PEReader]
    Try1 -->|失败| Try2[ElfReader32/64.Load<br/>检测 ELF magic + PHT/SHT fallback]
    Try2 -->|成功| Rebase{sh_addr == 0?}
    Rebase -->|是| MemDump[内存转储模式<br/>重基址到 LoadOptions.ImageBase<br/>禁用 relocation/symbol]
    Rebase -->|否| Ret2[return ElfReader]
    MemDump --> Ret2
    Try2 -->|失败| Try3[MachOReader32/64.Load<br/>检测 magic + endianness + segment]
    Try3 -->|成功| Ret3[return MachOReader]
    Try3 -->|失败| Try4[NsoReader.Load<br/>NRO/NROD + LZ4]
    Try4 -->|成功| Ret4[return NsoReader]
    Try4 -->|失败| Try5[SElfReader.Load]
    Try5 -->|成功| Ret5[return SElfReader]
    Try5 -->|失败| Try6[UBReader.Load<br/>Fat Mach-O]
    Try6 -->|成功| Ret6[return UBReader 多 image]
    Try6 -->|失败| Try7[APKReader/AABReader<br/>ZipArchive]
    Try7 -->|成功| Ret7[return APKReader]
    Try7 -->|失败| Try8[ProcessMapReader<br/>Linux /proc/self/maps 文本]
    Try8 -->|成功| Ret8[return ProcessMapReader]
    Try8 -->|失败| Null[return null]

    Ret1 --> End([done])
    Ret2 --> End
    Ret3 --> End
    Ret4 --> End
    Ret5 --> End
    Ret6 --> End
    Ret7 --> End
    Ret8 --> End
    Null --> End
```

---

## 5.7 il2cpp 类型重建（TypeModel/TypeInfo 构建）

**入口**：`Reflection/TypeModel.cs:ctor(TypeModel(Il2CppInspector package))`

```mermaid
flowchart TD
    Start([new TypeModel package]) --> Alloc[分配 TypesByDefinitionIndex<br/>TypesByReferenceIndex<br/>GenericParameterTypes<br/>MethodsByDefinitionIndex<br/>MethodInvokers]
    Alloc --> AsmLoop[foreach image in package.Images]
    AsmLoop --> AsmCtor[new Assembly this image<br/>AssemblyDefinition = package.Assemblies idx<br/>ShortName = Strings nameIdx<br/>FullName = Name, Version=..., Culture=..., PKT=...<br/>ModuleDefinition = package.Modules name]
    AsmCtor --> TypesLoop[for t in TypeStart..TypeStart+TypeCount]
    TypesLoop --> TI[new TypeInfo t this]

    AsmLoop --> RefLoop[foreach typeRefIndex in 0..TypeReferences.Length]
    RefLoop --> Resolve[resolveTypeReference Package.TypeReferences idx]
    Resolve --> Switch{Il2CppTypeEnum}
    Switch -->|CLASS/VALUETYPE| K[TypesByDefinitionIndex typeRef.Data.KlassIndex]
    Switch -->|GENERICINST| G[read Il2CppGenericClass + Il2CppGenericInst<br/>MakeGenericType args]
    Switch -->|ARRAY| A[read Il2CppArrayType → MakeArrayType rank]
    Switch -->|SZARRAY/PTR| SP[MakeArrayType 1 / MakePointerType]
    Switch -->|VAR/MVAR| V[GetGenericParameterType idx]
    Switch -->|default| T[GetTypeDefinitionFromTypeEnum enum<br/>primitives via FullNameTypeString]
    K --> AddRef[TypesByReferenceIndex idx = result]
    G --> AddRef
    A --> AddRef
    SP --> AddRef
    V --> AddRef
    T --> AddRef

    AddRef --> SpecLoop[foreach spec in Package.MethodSpecs]
    SpecLoop --> MakeGen[declaringType = declaringType.MakeGenericType genericArgs<br/>method = declaringType.GetMethodByDefinition def<br/>method = method.MakeGenericMethod genericArgs<br/>method.VirtualAddress = Package.GetGenericMethodPointer spec]
    MakeGen --> GenMap[GenericMethods spec = method]

    GenMap --> TIBuild[每个 TypeInfo 重建<br/>BaseType / Interfaces / DeclaringType / NestedTypes<br/>GenericTypeParameters<br/>DeclaredFields 含 FieldRef + FieldOffset<br/>DeclaredMethods 含 Parameters + ReturnType + VirtualAddress<br/>DeclaredProperties 含 Get/SetMethod<br/>DeclaredEvents 含 Add/Remove/RaiseMethod<br/>CustomAttributes via v29 CustomAttributeDataRanges 或 v21 AttributeTypeRanges]
    TIBuild --> AttrGen[CustomAttributeGenerators +<br/>CustomAttributeGeneratorsByAddress<br/>从 AttributesByIndices 填充]
    AttrGen --> Inv[MethodInvokers via Package.GetInvokerIndex]
    Inv --> Names[Namespaces = Assemblies.SelectMany DefinedTypes.GroupBy Namespace]
    Names --> Done([TypeModel ready])
```

---

## 5.8 反汇编 / RGCTX / Generic 处理（DisassemblerMetadata）

**入口**：`FrontendCore/Outputs/DisassemblerMetadataOutput.cs:Export(...)` 间接调用

```mermaid
flowchart TD
    Start([用户在 UI 选 Disassembler IDA/Ghidra/BinaryNinja]) --> Export[DisassemblerMetadataOutput.Export model client outPath settings]
    Export --> Build[AppModel.Build settings.UnityVersion CppCompilerType.GCC]
    Build --> H[CppScaffolding model useBetterArraySize=true.WriteTypes outPath/il2cpp.h]
    H --> J[JSONMetadata model.Write outPath/il2cpp.json]
    J --> Py[PythonScript model.WriteScriptToFile outPath/il2cpp.py target il2cpp.h il2cpp.json]
    Py --> Templates[Template 替换:<br/>shared_base.py + Targets/IDA.py|Ghidra.py|BinaryNinja.py]
    Templates --> Done([输出 il2cpp.h + il2cpp.json + il2cpp.py])

    subgraph 同期: Generic/RGCTX
        GPrep[Il2CppBinary.PrepareMetadata<br/>read CodeRegistration.CodeGenModules<br/>ModuleMethodPointers module = ReadMappedUWordArray ptr count<br/>MethodInvokerIndices module = ReadMappedPrimitiveArray int ptr count<br/>GenericMethodPointers spec = ... tableEntry.Indices.MethodIndex]
        GResolve[Il2Inspector.GetGenericMethodPointer spec → 使用 sorted FunctionAddresses]
        GModel[AppModel.Build: foreach method/usage<br/>CppDeclarationGenerator.IncludeMethod + AddTypes<br/>→ 填充 MangledNameBuilder entries]
        GPrep --> GResolve --> GModel
    end

    subgraph 同期: Metadata Usages
        UBuild[buildMetadataUsages Il2Inspector ctor]
        ULate{v >= v27?}
        ULate -->|否| Direct[直接解析 UsageTables]
        ULate -->|是| Late[buildLateBindingMetadataUsages<br/>暴力扫描整个 image bytes<br/>寻找合法 encoded indices]
        Direct --> AppUses[AppModel 遍历 Package.MetadataUsages 填充 Strings/Fields/FieldRvas/Types/Methods]
        Late --> AppUses
        UBuild --> ULate
    end
```

---

## 5.9 VersionedSerialization 序列化/反序列化路径

**入口**：`Common/Next/Metadata/Il2CppGlobalMetadataHeader.cs:[VersionedStruct]` → Roslyn 生成器

```mermaid
flowchart TD
    Start([源: struct Il2CppGlobalMetadataHeader]) --> Attr[标注 [VersionedStruct] + 字段 [VersionCondition]]
    Attr --> Gen[VersionedSerialization.Generator<br/>IIncrementalGenerator<br/>ForAttributeWithMetadataName]
    Gen --> Parse[ParseSerializationInfo<br/>收集字段 + 条件]
    Parse --> Emit[EmitCode:<br/>追加 Versions static class<br/>+ Read TReader body 含 if version 守卫<br/>+ static int IReadable.Size StructVersion, ReaderConfig]
    Emit --> Comp[编译产物]

    Comp --> Use[运行时: Metadata.FromStream]
    Use --> CreateReader[Reader LittleEndianSeekableReader if Endianness=Little]
    CreateReader --> ReadHdr[Header.Read ref reader, version]
    ReadHdr --> FieldRead[foreach field:<br/>if version == Conditions<br/>read T via reader]
    FieldRead --> TypedArrays[重复 ReadMetadataArray T<br/>ReadMetadataPrimitiveArray T<br/>直到所有 typed array 读完]
    TypedArrays --> Done([Metadata ready])
```

---

## 5.10 SignalR 前后端通信（Redux CLI/GUI）

**入口**：`FrontendCore/Il2CppHub.cs` + `Redux.CLI/CliClient.cs`

```mermaid
sequenceDiagram
    autonumber
    participant FE as Tauri+Svelte 前端
    participant SR as SignalR (/il2cpp)
    participant HUB as Il2CppHub
    participant CTX as UiContext State
    participant MODEL as Il2CppInspector + TypeModel + AppModel
    participant OUT as IOutputFormat.Export

    FE->>SR: connect http://localhost:port/il2cpp
    SR-->>FE: connectionId
    FE->>HUB: invoke OnUiLaunched()
    HUB->>CTX: InitializeAsync(client)
    CTX-->>FE: client.ShowInfoToast('ready')

    FE->>HUB: invoke SubmitInputFiles paths
    HUB->>CTX: LoadInputFilesAsync(client, paths)
    CTX->>MODEL: Inspector.LoadFromStream(...)
    CTX->>MODEL: new TypeModel + new AppModel(makeDefaultBuild:false)
    CTX->>CTX: UnityHeaders.GuessHeadersForBinary
    CTX-->>FE: client.OnImportCompleted()

    FE->>HUB: invoke QueueExport id outPath settings
    HUB->>CTX: QueueExportAsync(client, id, outPath, settings)
    CTX->>CTX: 记录到 _queuedExports

    FE->>HUB: invoke StartExport
    HUB->>CTX: StartExportAsync
    CTX->>CTX: 弹出 LoadingSession
    CTX->>CTX: client.BeginLoading()
    CTX->>CTX: foreach queued: OutputFormatRegistry.GetOutputFormat(id).Export(model, client, outPath, settings)
    OUT-->>CTX: 写文件 + ShowLogMessage
    CTX->>CTX: client.FinishLoading()
    CTX-->>FE: ShowSuccessToast

    FE->>HUB: invoke GetPotentialUnityVersions
    HUB->>CTX: GetPotentialUnityVersionsAsync
    CTX-->>FE: List<string>

    FE->>HUB: invoke SetSettings imageBase, nameMapPath
    HUB->>CTX: SetSettingsAsync
    CTX->>CTX: 应用 name translation map
```

---

## 5.11 名称混淆复原（NameTranslation）

**入口**：`Common/Next/NameTranslation/NameTranslationParserContext.cs` → `TypeModel.ApplyNameTranslation`

```mermaid
flowchart TD
    Start([用户提供 name-translation.txt]) --> Load[FrontendCore.UiContext.SetSettings<br/>nameTranslationMapPath]
    Load --> Parse[NameTranslationParserContext<br/>读每行 'FullName OldName' 形式]
    Parse --> Map[NameTranslationInfo 列表]
    Map --> Apply[TypeModel.ApplyNameTranslation lines]
    Apply --> Loop[foreach entry in lines<br/>TypeInfo in TypesByFullName]
    Loop --> Rename[Reflection.Extensions.ToCIdentifier<br/>+ 重写 Name / FullName]
    Rename --> Done([TypeModel 各类型显示名更新])
    Done --> Next[后续 CSharpCodeStubs / CppScaffolding<br/>使用更新后的 FullName]
```

---

## 5.12 插件 hook 完整生命周期（pipeline 全景）

**入口**：所有 `PluginHooks.*` 调用串联

```mermaid
stateDiagram-v2
    [*] --> LoadPipelineStarting
    LoadPipelineStarting --> PreProcessMetadata
    PreProcessMetadata --> ReadMetadata
    ReadMetadata --> GetStrings
    GetStrings --> GetStringLiterals
    GetStringLiterals --> PostProcessMetadata
    PostProcessMetadata --> PreProcessImage
    PreProcessImage --> LoadImage
    LoadImage --> PostProcessImage
    PostProcessImage --> PreProcessBinary
    PreProcessBinary --> FindRegistration
    FindRegistration --> PrepareMetadata
    PrepareMetadata --> PostProcessBinary
    PostProcessBinary --> PostProcessPackage
    PostProcessPackage --> BuildTypeModel
    BuildTypeModel --> PostProcessTypeModel
    PostProcessTypeModel --> BuildAppModel
    BuildAppModel --> PostProcessAppModel
    PostProcessAppModel --> LoadPipelineEnding
    LoadPipelineEnding --> [*]

    note right of ReadMetadata
      每次 ReadMappedVersionedObject T
      都有 Pre/Post 配对 hook
    end note
```