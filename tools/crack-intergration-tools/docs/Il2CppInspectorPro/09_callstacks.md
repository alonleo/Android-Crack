# 09 · 关键调用栈汇总

> 所有栈均经过 `grep -n` 交叉验证。深度从外层用户入口到内层 helper。

---

## 9.1 CLI 主调用栈（`dotnet run --project Il2Inspector.CLI` → 所有输出）

```
Program.Main(args)                                                            [Il2Inspector.CLI/Program.cs:~30]
└─ App.Run(options)                                                           [Program.cs:~80]
   ├─ PluginManager.EnsureInit()                                              [PluginManager.cs:~60]
   │  └─ Reload(pluginPath=null)                                              [PluginManager.cs:~110]
   │     ├─ Directory.GetFiles(plugins, *.dll, AllDirectories)
   │     └─ foreach dll: PluginLoader.CreateFromAssemblyFile → Activator.CreateInstance
   ├─ PluginManager.ErrorHandler += OnError
   ├─ PluginManager.StatusHandler += OnStatus
   ├─ inspectors = Il2Inspector.LoadFromPackage([bin])                       [Il2Inspector.cs:515]
   │  └─ GetStreamsFromPackage(paths)                                         [Il2Inspector.cs:479]
   │     └─ GetStreamsFromPackage(zipStreams)                                [Il2Inspector.cs:383]
   ├─ if inspectors empty: Il2Inspector.LoadFromFile(bin, meta)              [Il2Inspector.cs:523]
   │  └─ LoadFromStream(FileStream, FileStream)                              [Il2Inspector.cs:530]
   │     ├─ Metadata.FromStream(metadataStream)                              [Metadata.cs:~80]
   │     │  ├─ PluginHooks.PreProcessMetadata                                 [PluginHooks.cs:~20]
   │     │  ├─ Header.Read(...)
   │     │  ├─ ReadMetadataArray<T>(...) x N (所有 typed array)
   │     │  │  └─ Reader<TReader>.ReadVersionedObject<T>()                   [Reader`1.cs:~40]
   │     │  ├─ PluginHooks.GetStrings / GetStringLiterals                     [PluginHooks.cs:~28-32]
   │     │  └─ PluginHooks.PostProcessMetadata                                [PluginHooks.cs:~25]
   │     ├─ FileFormatStream.Load(binaryStream)                              [FileFormatStream.cs:~110]
   │     │  └─ foreach 实现: PEReader.Load / ElfReader.Load / ...            [FileFormatStream.cs:~110]
   │     ├─ foreach image: Il2CppBinary.Load(stream, metadata)               [Il2CppBinary.cs:154]
   │     │  ├─ LoadImpl (反射) → new Il2CppBinary<Arch>                      [Architectures/*.cs]
   │     │  ├─ FindRegistrationStructs(metadata)                             [Il2CppBinary.cs:184]
   │     │  │  ├─ FindMetadataFromSymbols                                    [Il2CppBinary.cs:~200]
   │     │  │  ├─ FindMetadataFromCode (→ ConsiderCode)                       [Il2CppBinary.cs:~220-228]
   │     │  │  └─ FindMetadataFromData (→ ImageScan)                          [Il2CppBinary.cs:~235]
   │     │  ├─ TryPrepareMetadata                                             [Il2CppBinary.cs:261]
   │     │  │  └─ PrepareMetadata                                             [Il2CppBinary.cs:271]
   │     │  │     ├─ Image.ReadMappedVersionedObject<Il2CppCodeRegistration> [FileFormatStream.cs:280]
   │     │  │     ├─ Image.ReadMappedVersionedObject<Il2CppMetadataRegistration>
   │     │  │     ├─ foreach module: ModuleMethodPointers / MethodInvokerIndices
   │     │  │     ├─ FieldOffsets / FieldOffsetPointers
   │     │  │     ├─ TypeReferences + TypeReferenceIndicesByAddress
   │     │  │     ├─ MethodSpecs, GenericInstances, GenericMethodPointers
   │     │  │     └─ PluginHooks.PostProcessBinary
   │     │  └─ DiscoverAPIExports                                             [Il2CppBinary.cs:495]
   │     │     └─ Image.GetExports()
   │     └─ new Il2CppInspector(binary, metadata)
   ├─ foreach inspector:
   │   model = new TypeModel(il2cpp)                                         [TypeModel.cs:~60]
   │   ├─ new Assembly(this, image)                                          [Assembly.cs:~25]
   │   └─ new TypeInfo(def, this)                                             [TypeInfo.cs:~200]
   ├─ am = new AppModel(model, false)                                        [AppModel.cs:~50]
   └─ am.Build(unityVersion, cppCompiler)                                    [AppModel.cs:~110]
      ├─ UnityHeaders.GuessHeadersForBinary                                  [UnityHeaders.cs:112]
      ├─ new CppDeclarationGenerator(this)                                   [CppDeclarationGenerator.cs:~80]
      ├─ CppTypeCollection.FromUnityHeaders                                  [CppTypeCollection.cs:~500]
      ├─ foreach method in Methods: IncludeMethod                            [CppDeclarationGenerator.cs:~250]
      ├─ foreach generic method: IncludeMethod
      ├─ foreach usage: include corresponding types
      ├─ foreach unused value type: IncludeType                              [CppDeclarationGenerator.cs:~330]
      └─ GenerateRequiredForwardDefinitions                                  [CppDeclarationGenerator.cs:~620]
   └─ if cs: CSharpCodeStubs(model).WriteSingleFile(cs-out)                   [CSharpCodeStubs.cs:55]
   │           └─ Parallel.ForEach types → generateType
   └─ if cpp: CppScaffolding(am).Write(cpp-out)                              [CppScaffolding.cs:~120]
   │           └─ WriteTypes → forward defs + 5 groups + headers/...
   └─ if json: JSONMetadata(am).Write(json-out)                              [JSONMetadata.cs:~100]
   └─ if dll: AssemblyShims(model).Write(dll-out)                            [AssemblyShims.cs:~120]
   └─ if py: PythonScript(am).WriteScriptToFile(py-out, target, h, json)     [PythonScript.cs:~50]
```

## 9.2 Redux GUI 启动栈

```
双击 Il2Inspector.Redux.GUI.exe
└─ Program.Main(args)                                                        [Redux.GUI/Program.cs:~10]
   └─ MainAsync(args)                                                        [Program.cs:~20]
      ├─ WebApplication.CreateSlimBuilder(args)
      ├─ services.AddFrontendCore()                                          [FrontendCore/Extensions.cs:~15]
      │  └─ AddSignalR().AddJsonProtocol(...)
      ├─ services.AddSingleton<UiProcessService>()
      ├─ app = builder.Build()
      ├─ app.UseCors(...)
      ├─ app.MapFrontendCore()                                               [Extensions.cs:~25]
      │  └─ app.MapHub<Il2CppHub>("/il2cpp")                                 [Il2CppHub.cs]
      ├─ app.StartAsync()
      ├─ port = new Uri(app.Urls.First()).Port
      └─ #if Release:
         app.Services.GetRequiredService<UiProcessService>().LaunchUiProcess(port)
            └─ UiProcessService.LaunchUiProcess                              [UiProcessService.cs:~40]
               ├─ ExtractUiExecutable()                                       [UiProcessService.cs:~50]
               │  └─ Assembly.GetManifestResourceStream("...il2cppinspectorredux.exe")
               │     └─ File.WriteAllBytes(%TEMP%/il2cppinspectorredux-ui/)
               └─ Process.Start(tauri-exe, argv=[port.ToString()])
                  └─ _uiProcess.WaitForExitAsync(stoppingToken) → lifetime.StopApplication()

Tauri exe (Rust + Svelte) 启动:
└─ tauri::Builder::default().setup → il2cpp_inspector_redux_lib::run         [src-tauri/src/lib.rs:~10]
   └─ WebView 显示 Svelte bundle

Svelte onMount → api.getInspectorVersion()
└─ client-api.ts.getInspectorVersion → SignalR invoke
   └─ HttpConnection → ws://localhost:{port}/il2cpp
      └─ Il2CppHub.GetInspectorVersion                                       [Il2CppHub.cs:~50]
         └─ State.GetInspectorVersionAsync                                   [UiContext.cs:~265]
            └─ return Assembly.GetExecutingAssembly().GetName().Version.ToString()
```

## 9.3 Redux GUI 用户提交文件栈

```
Svelte page → api.submitInputFiles(paths)                                    [client-api.ts]
└─ SignalR invoke SubmitInputFiles(paths)                                    [Il2CppHub.cs:~15]
   └─ State.LoadInputFilesAsync(client, paths)                               [UiContext.cs:~120]
      ├─ foreach path:
      │  if PathHeuristics.IsMetadataPath → TryLoadMetadataFromStreamAsync
      │  if PathHeuristics.IsBinaryPath → TryLoadBinaryFromStreamAsync
      │  if ext in [apk,aab,ipa,zip,xapk] → Inspector.GetStreamsFromPackage
      ├─ if both loaded → TryInitializeInspectorAsync
      │  ├─ Inspector.LoadFromStream(fileFormatStream, metadata)             [Il2CppInspector.cs:572]
      │  │  └─ Il2CppBinary.Load(stream, metadata) + new Il2CppInspector
      │  ├─ model = new TypeModel(il2cpp)
      │  ├─ am = new AppModel(model, false)
      │  └─ UnityHeaders.GuessHeadersForBinary
      └─ client.OnImportCompleted()
```

## 9.4 Redux GUI 用户触发导出栈

```
Svelte page → api.queueExport(id, path, settings) + api.startExport()
├─ Il2CppHub.QueueExport → State.QueueExportAsync                            [UiContext.cs:~170]
│  └─ _queuedExports.Add(...)
└─ Il2CppHub.StartExport → State.StartExportAsync                            [UiContext.cs:~200]
   ├─ using LoadingSession.Start(client)
   │  └─ client.BeginLoading()
   ├─ foreach queued: OutputFormatRegistry.GetOutputFormat(id)               [OutputFormatRegistry.cs:~20]
   │  └─ IOutputFormat.Export(model, client, path, settings)
   │     ├─ if "cs"           → CSharpStubOutput.Export                       [CSharpStubOutput.cs]
   │     │                       └─ CSharpCodeStubs(model).Write*...
   │     ├─ if "cppscaffolding" → CppScaffoldingOutput.Export
   │     │                       └─ CppScaffolding(model).Write(...)
   │     ├─ if "disassemblermetadata" → DisassemblerMetadataOutput.Export
   │     │                       └─ CppScaffolding.WriteTypes + JSONMetadata.Write + PythonScript.WriteScriptToFile
   │     ├─ if "dummydlls"    → DummyDllOutput.Export
   │     │                       └─ AssemblyShims(model).Write(...)
   │     └─ if "vssolution"   → VsSolutionOutput.Export
   │                             └─ CSharpCodeStubs(model).WriteSolution(...)
   ├─ client.FinishLoading()
   └─ client.ShowSuccessToast(...)
```

## 9.5 插件加载栈

```
App.Main (CLI/GUI)
└─ PluginManager.EnsureInit()
   └─ if AsInstance == null:
      Reload(pluginPath=null, reset=true)
      ├─ pluginPath ??= Path.GetFullPath(exeDir + "/plugins")
      ├─ if !Directory.Exists → throw
      ├─ foreach dll in plugins/**/*.dll:
      │  ├─ loader = PluginLoader.CreateFromAssemblyFile(dll, sharedTypes=[IPlugin])
      │  ├─ asm = loader.LoadDefaultAssembly()
      │  ├─ foreach type in asm.GetTypes():
      │  │  if typeof(IPlugin).IsAssignableFrom(type) && !type.IsAbstract:
      │  │     plugin = (IPlugin)Activator.CreateInstance(type)
      │  │     ManagedPlugins.Add(new ManagedPlugin { Plugin, Available, Enabled = isCorePlugin })
      │  └─ (on ReflectionTypeLoadException → add InvalidPlugin placeholder)
      └─ (CLI only) PluginOptions.GetPluginOptionTypes
         └─ foreach plugin: CreateOptionsFromPlugin → AssemblyBuilder.DefineType + [Option] attribute
```

## 9.6 Metadata 读取栈（`Metadata.FromStream`）

```
Metadata.FromStream(stream)                                                   [Metadata.cs:~80]
├─ PluginHooks.PreProcessMetadata(stream)                                     [PluginHooks.cs:~20]
│  └─ PluginManager.Try<ILoadPipeline, ...>(...)
├─ reader = new Reader<LittleEndianSeekableReader<BinaryObjectStream>>(...)
├─ Header.Read(ref reader, version)
│  └─ T.Read(...) (由生成器合成; 含 [VersionCondition] 分支)
├─ foreach typed array:
│  ReadMetadataArray<T>(offset, size, section)
│  └─ Reader<TReader>.ReadVersionedObject<T>()                                 [Reader`1.cs:~40]
│     └─ T.Read(ref reader, version)
├─ ReadMetadataPrimitiveArray<T>(...) (基础类型数组)
├─ PluginHooks.GetStrings(metadata)                                           [PluginHooks.cs:~28]
├─ PluginHooks.GetStringLiterals(metadata)                                    [PluginHooks.cs:~32]
└─ PluginHooks.PostProcessMetadata(metadata)                                  [PluginHooks.cs:~25]
```

## 9.7 `Il2CppBinary.PrepareMetadata` 栈

```
Il2CppBinary.Load(stream, metadata) → new Il2CppBinary                          [Il2CppBinary.cs:154]
└─ FindRegistrationStructs(metadata)                                          [Il2CppBinary.cs:184]
   ├─ Try symbols → FindMetadataFromSymbols
   ├─ Try code    → FindMetadataFromCode
   │  └─ ConsiderCode (per-arch)
   ├─ Try data    → FindMetadataFromData (→ ImageScan.Scan)
   └─ TryPrepareMetadata(code, meta)                                           [Il2CppBinary.cs:261]
      └─ PrepareMetadata(code, meta)                                          [Il2CppBinary.cs:271]
         ├─ Image.ReadMappedVersionedObject<Il2CppCodeRegistration>          [FileFormatStream.cs:280]
         ├─ Image.ReadMappedVersionedObject<Il2CppMetadataRegistration>
         ├─ foreach codeGenModule in CodeRegistration.CodeGenModules:
         │  ModuleMethodPointers[mod] = Image.ReadMappedUWordArray(ptr, count)
         │  MethodInvokerIndices[mod] = Image.ReadMappedPrimitiveArray<int>(...)
         ├─ FieldOffsets = Image.ReadMappedPrimitiveArray<uint>(...)
         ├─ FieldOffsetPointers = Image.ReadMappedPrimitiveArray<long>(...)
         ├─ TypeReferences = Image.ReadMappedObjectArray<Il2CppType>(...)
         ├─ TypeReferenceIndicesByAddress (memory-dump 重映射)
         ├─ MethodSpecs = Image.ReadMappedObjectArray<Il2CppMethodSpec>(...)
         ├─ GenericInstances = ...
         ├─ foreach spec: GenericMethodPointers[spec] = ...
         └─ PluginHooks.PostProcessBinary(this)
```

## 9.8 TypeModel 类型构建栈

```
new TypeModel(il2cpp)                                                        [TypeModel.cs:~60]
├─ Assemblies.Add(new Assembly(this, image)) × N
│  └─ Assembly.ctor → 解析 Strings[] → ModuleDefinition
├─ TypesByDefinitionIndex[i] = new TypeInfo(def, this) × N
├─ foreach typeRefIndex:
│  resolveTypeReference(Package.TypeReferences[i])
│  ├─ IL2CPP_TYPE_CLASS/VALUETYPE → TypesByDefinitionIndex[klass]
│  ├─ IL2CPP_TYPE_GENERICINST → MakeGenericType
│  ├─ IL2CPP_TYPE_ARRAY → MakeArrayType(rank)
│  ├─ IL2CPP_TYPE_VAR/MVAR → GetGenericParameterType(idx)
│  └─ default → GetTypeDefinitionFromTypeEnum (FullNameTypeString)
├─ foreach spec in MethodSpecs:
│  declaringType.MakeGenericType(...).GetMethodByDefinition(def).MakeGenericMethod(...)
│  method.VirtualAddress = GetGenericMethodPointer(spec)
│  GenericMethods[spec] = method
├─ Namespaces = ...Distinct().ToList()
├─ CustomAttributeGenerators (via AttributesByIndices)
└─ MethodInvokers (via GetInvokerIndex)
```

每个 TypeInfo 同时调用 `BuildBaseType`, `BuildInterfaces`, `BuildGenericArguments`, `BuildDeclaredFields`, `BuildDeclaredMethods`, `BuildDeclaredProperties`, `BuildDeclaredEvents`, `BuildCustomAttributes` — 私有 helper，无外部调用方。

## 9.9 C++ scaffolding 写入栈（最深的资源访问）

```
new CppScaffolding(model, useBetterArraySize, includeUnresolved).Write(path)   [CppScaffolding.cs:~120]
├─ WriteTypes(appdata/il2cpp-types.h)
│  ├─ _model.UnityHeaders.GetTypeHeaderText(WordSizeBits)                      [UnityHeaders.cs:~170]
│  │  └─ Resources.Cpp_Il2CppAppDataH (内嵌 resx)
│  ├─ writeForwardDefinitions
│  └─ writeTypesForGroup × 5
│     ├─ "Required forward definitions"
│     ├─ "Application types from method calls"
│     ├─ "Application types from generic methods"
│     ├─ "Application types from usages"
│     └─ "Application unused value types"
├─ il2cpp-api-functions.h
├─ il2cpp-api-functions-ptr.h (#define ptr 0xfileOff)
├─ il2cpp-types-ptr.h (DO_TYPEDEF)
├─ il2cpp-functions.h
├─ il2cpp-metadata-version.h
├─ if libraries/: extract imgui.zip / detours.zip / handlers.zip
├─ framework/dllmain.cpp + helpers.cpp/h + il2cpp-appdata.h + il2cpp-init.cpp/h + pch + version
├─ user/main.cpp/h, settings.cpp/h (if not exists)
├─ definitions/version.def
├─ Resources.CppProjTemplate → name.vcxproj
├─ Resources.CppProjFilters → name.vcxproj.filters
└─ Resources.CppSlnTemplate → name.sln
```

## 9.10 VersionedSerialization 编译期 + 运行期

```
// 编译期:
[VersionedStruct] struct Il2CppGlobalMetadataHeader { ... }
                  +
[VersionCondition(...)] on each field
                  │
                  ▼
VersionedSerialization.Generator (IIncrementalGenerator)
                  │
                  ▼
生成代码 (嵌入到 Il2CppInspector.Common.dll):
    static class Versions { static readonly StructVersion V240 = ...; ... }
    public void Read<TReader>(ref Reader<TReader>, in StructVersion) {
        if (version >= V240 && version < V270) field1.Read(...);
        ...
    }
    public static int Size(in StructVersion, in ReaderConfig) {
        int size = 0;
        if (...) size += ...;
        return size;
    }

// 运行期:
Metadata.FromStream(stream)
   └─ new Reader<LittleEndianSeekableReader<BinaryObjectStream>>(_stream, config)
      └─ Header.Read(ref reader, metadata.Version)
         └─ Reader<TReader>.ReadVersionedObject<T>()   (见 9.6)
```