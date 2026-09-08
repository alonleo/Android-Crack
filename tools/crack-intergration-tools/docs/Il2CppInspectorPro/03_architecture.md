# 03 · 架构总览

## 3.1 分层

```
┌────────────────────────────────────────────────────────────────────┐
│  Frontends (UI)                                                    │
│  ├── WPF MainWindow  (Il2CppInspector.GUI/)                        │
│  └── Tauri+Svelte UI (Il2CppInspector.Redux.GUI.UI/)              │
├────────────────────────────────────────────────────────────────────┤
│  Entry executables                                                 │
│  ├── Il2CppInspector.CLI/Program.cs        (CommandLineParser)     │
│  ├── Il2CppInspector.Redux.CLI/Program.cs  (Spectre + SignalR)    │
│  └── Il2CppInspector.Redux.GUI/Program.cs  (WebApp + Tauri)        │
├────────────────────────────────────────────────────────────────────┤
│  Hub + shared state                                                │
│  └── Il2Inspector.Redux.FrontendCore (UiContext + Il2CppHub +     │
│        IOutputFormat providers)                                    │
├────────────────────────────────────────────────────────────────────┤
│  Core library                                                      │
│  └── Il2CppInspector.Common                                          │
│      ├── IL2CPP/         (Il2CppInspector, Il2CppBinary, Metadata) │
│      ├── Reflection/     (TypeModel, TypeInfo, …)                  │
│      ├── Model/          (AppModel, AppType, AppMethod)            │
│      ├── Cpp/            (CppDeclarationGenerator, CppType…)      │
│      ├── Outputs/        (CSharpCodeStubs, CppScaffolding, …)     │
│      ├── FileFormatStreams/ (PE/ELF/MachO/NSO/APK/…)               │
│      ├── Plugins/        (PluginManager + V100 API)                │
│      └── Next/           (VersionedSerialization-backed structs)   │
├────────────────────────────────────────────────────────────────────┤
│  Plugins                                                            │
│  └── ./plugins/*.dll  (loaded by McMaster.NETCore.Plugins)          │
├────────────────────────────────────────────────────────────────────┤
│  External                                                           │
│  ├── Bin2Object  (submodule, currently empty)                      │
│  ├── dnlib 4.4 · K4os.Compression.LZ4 · Spectre.Console            │
│  └── VersionedSerialization (+ Roslyn generator)                    │
└────────────────────────────────────────────────────────────────────┘
```

## 3.2 模块依赖图

```mermaid
flowchart TD
    subgraph Frontends
        WPF["Il2Inspector.GUI<br/>(WPF MainWindow)"]
        Tauri["Il2Inspector.Redux.GUI.UI<br/>(Tauri + Svelte)"]
    end

    subgraph Entries
        CLI["Il2Inspector.CLI<br/>Program.cs"]
        RCLI["Il2Inspector.Redux.CLI<br/>Program.cs"]
        RGUI["Il2Inspector.Redux.GUI<br/>Program.cs + UiProcessService"]
    end

    subgraph Hub
        FCORE["Il2Inspector.Redux.FrontendCore<br/>Il2CppHub + UiContext<br/>+ OutputFormatRegistry"]
    end

    subgraph Core
        COMMON["Il2Inspector.Common"]
    end

    subgraph ExtDeps
        BIN2["Bin2Object (submodule)"]
        VS["VersionedSerialization"]
        GEN["VersionedSerialization.Generator<br/>(Roslyn analyzer)"]
        PLUG["plugins/*.dll<br/>(McMaster.NETCore.Plugins)"]
    end

    WPF --> COMMON
    CLI --> COMMON
    RCLI --> FCORE
    RGUI --> FCORE
    RGUI -.启动 Tauri 进程.-> Tauri
    Tauri --SignalR RPC--> RGUI
    RCLI --SignalR--> FCORE

    FCORE --> COMMON

    COMMON --> BIN2
    COMMON --> VS
    COMMON -. 嵌入为 analyzer .-> GEN
    COMMON -. 反射加载 .-> PLUG
```

## 3.3 启动流程（CLI + Redux GUI）

```mermaid
flowchart TD
    Start([用户执行 exe / dotnet run])

    Start --> CLIType{哪种入口?}

    CLIType -->|Il2Inspector.CLI| CLIMain[Program.Main]
    CLIType -->|Il2Inspector.Redux.CLI| RCLIMain[Program.Main]
    CLIType -->|Il2Inspector.Redux.GUI| RGUIMain[Program.Main]
    CLIType -->|Il2Inspector.GUI| WPFMain[App.xaml.cs]

    CLIMain --> Parse[CommandLineParser.ParseArguments<Options>]
    Parse --> PluginInit[PluginManager.EnsureInit]
    PluginInit --> LoadIns[Il2Inspector.LoadFromPackage / LoadFromFile]
    LoadIns --> TypeModel[TypeModel 构造]
    TypeModel --> AppModel[AppModel.Build]
    AppModel --> Emit[选择输出: CSharp / CppScaffolding / JSON / DLL / Python]
    Emit --> Done([ExitCode=0])

    RCLIMain --> WebApp[WebApplication.CreateSlimBuilder]
    WebApp --> MapHub[MapHub<Il2CppHub>('/il2cpp')]
    MapHub --> SpectreRun[CommandApp<InteractiveCommand>.RunAsync]
    SpectreRun --> Connect[CliClient.Connect localhost:port/il2cpp]
    Connect --> ProcessCmd[ProcessCommand.ExecuteAsync]
    ProcessCmd --> SignalRPC[hub.SubmitInputFiles / QueueExport / StartExport]
    SignalRPC --> Done

    RGUIMain --> WebApp
    WebApp --> MapHub
    MapHub --> UiService[UiProcessService.LaunchUiProcess port]
    UiService --> ExtractTauri[ExtractUiExecutable → %TEMP%/il2cppinspectorredux-ui/]
    ExtractTauri --> SpawnTauri[Process.Start tauri-exe.exe argv[0]=port]
    SpawnTauri --> TauriUI([Tauri WebView 用户交互])
    TauriUI --SignalR RPC--> MapHub

    WPFMain --> WPFWindow[MainWindow.xaml.cs]
    WPFWindow --> ClickLoad[用户点击 Load]
    ClickLoad --> PluginInit
    PluginInit --> LoadIns
```

## 3.4 核心类型关系

```mermaid
classDiagram
    class Il2CppBinary {
        <<abstract partial>>
        +IFileFormatStream Image
        +Metadata Metadata
        +Dictionary~string,ulong~ APIExports
        +Il2CppCodeRegistration CodeRegistration
        +Il2CppMetadataRegistration MetadataRegistration
        +Load(stream, metadata) Il2CppBinary$
        +FindRegistrationStructs(metadata) bool
        +PrepareMetadata(code, meta) void
    }

    class Il2CppBinaryARM64
    class Il2CppBinaryARM
    class Il2CppBinaryX64
    class Il2CppBinaryX86

    Il2CppBinary <|-- Il2CppBinaryARM
    Il2CppBinary <|-- Il2CppBinaryARM64
    Il2CppBinary <|-- Il2CppBinaryX64
    Il2CppBinary <|-- Il2CppBinaryX86

    class Metadata {
        +Il2CppGlobalMetadataHeader Header
        +ImmutableArray~Il2CppAssemblyDefinition~ Assemblies
        +ImmutableArray~Il2CppImageDefinition~ Images
        +ImmutableArray~Il2CppTypeDefinition~ Types
        +ImmutableArray~Il2CppMethodDefinition~ Methods
        +FromStream(MemoryStream)$ Metadata
    }

    class Il2CppInspector {
        +Il2CppBinary Binary
        +Metadata Metadata
        +Dictionary~ulong,ulong~ FunctionAddresses
        +List~MetadataUsage~ MetadataUsages
        +LoadFromPackage(paths)$
        +LoadFromFile(bin, meta)$
        +LoadFromStream(stream, meta)$
        +GetMethodPointer(module, def)
        +GetGenericMethodPointer(spec)
    }

    Il2CppInspector o-- Il2CppBinary
    Il2CppInspector o-- Metadata

    class TypeModel {
        +Il2CppInspector Package
        +List~Assembly~ Assemblies
        +TypeInfo[] TypesByDefinitionIndex
        +TypeInfo[] TypesByReferenceIndex
        +MethodBase[] MethodsByDefinitionIndex
        +TypeInfo GetType(string)
        +TypeInfo[] ResolveGenericArguments(Il2CppGenericInst)
    }

    TypeModel o-- Il2CppInspector

    class Assembly {
        +TypeModel Model
        +Il2CppImageDefinition ImageDefinition
        +List~TypeInfo~ DefinedTypes
    }

    class TypeInfo {
        +Il2CppTypeDefinition Definition
        +TypeInfo BaseType
        +TypeInfo[] GenericTypeParameters
        +TypeInfo[] Interfaces
        +FieldInfo[] DeclaredFields
        +MethodBase[] DeclaredMethods
        +bool IsClass/IsValueType/IsEnum
        +MakeGenericType(TypeInfo[]) TypeInfo
        +SubstituteGenericArguments(TypeInfo[]) TypeInfo
    }

    class MethodBase {
        <<abstract>>
        +ParameterInfo[] DeclaredParameters
        +MethodInvoker Invoker
        +ulong VirtualAddress
        +TypeInfo ReturnType
    }

    class FieldInfo {
        +TypeInfo FieldType
        +bool IsStatic / HasFieldRVA
        +ulong DefaultValueMetadataAddress
    }

    Assembly o-- TypeInfo
    TypeInfo o-- TypeInfo : BaseType/Interfaces
    TypeInfo o-- FieldInfo
    TypeInfo o-- MethodBase
    MethodBase <|-- MethodInfo
    MethodBase <|-- ConstructorInfo

    class AppModel {
        +TypeModel TypeModel
        +UnityVersion UnityVersion
        +CppTypeCollection CppTypeCollection
        +MultiKeyDictionary Methods
        +MultiKeyDictionary Types
        +Build(UnityVersion, CppCompilerType) AppModel
    }

    AppModel o-- TypeModel
    AppModel o-- CppTypeCollection

    class CSharpCodeStubs {
        +WriteSingleFile(outFile)
        +WriteFilesByNamespace(outPath, orderBy, flatten)
        +WriteFilesByClassTree(outPath, sepAttr)
        +WriteSolution(outPath, unityPath, unityAsm)
    }

    class CppScaffolding {
        +Write(projectPath, projectName)
        +WriteTypes(typeHeaderFile)
    }

    class AssemblyShims {
        +Write(outPath, statusCallback)
    }

    CSharpCodeStubs --> TypeModel
    CppScaffolding --> AppModel
    AssemblyShims --> TypeModel

    class PluginManager {
        <<singleton>>
        +ObservableCollection~ManagedPlugin~ ManagedPlugins
        +EnsureInit()$
        +Reload(pluginPath, reset, coreOnly)$
        +ValidateAllOptions()
    }

    class IPlugin {
        <<interface, V100>>
        +Id / Name / Version
        +Options List~IPluginOption~
        +OptionsChanged(info)
    }

    class ILoadPipeline {
        <<interface, V100>>
        +PreProcessMetadata / PostProcessMetadata
        +PreProcessImage / PostProcessImage
        +PreProcessBinary / PostProcessBinary
        +PostProcessPackage
        +PostProcessTypeModel / PostProcessAppModel
    }

    PluginManager --> IPlugin
    IPlugin --|> ILoadPipeline
```