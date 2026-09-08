# 02 · 目录树与文件清单

> 路径全部相对 `Il2CppInspectorPro/`。标注 `(*子模块未初始化*)` 的为空目录。

## 2.1 仓库根

```
Il2CppInspectorPro/
├── Directory.Build.props              # 公共 MSBuild：net10.0、Version=2026.1、Authors
├── .editorconfig                      # 编辑器规则
├── .gitmodules                        # 子模块声明：Bin2Object
├── .gitignore / .gitattributes
├── Il2CppInspector.sln                # 解决方案
├── LICENSE                            # AGPL-3.0 (34 KB)
├── README.md                          # 上游的 C++ Mod SDK 营销文档（53 行）
├── docs/                              # 仅预览 PNG，无 .md
├── get-plugins.ps1 / get-plugins.sh   # 下载 djkaty/Il2CppInspectorPlugins/plugins.zip
└── Bin2Object/                        # (*) 子模块未初始化 — 空目录
```

## 2.2 `Il2CppInspector.Common/` — 核心反向工程库

```
Il2CppInspector.Common/
├── Il2CppInspector.csproj             # NoisyCowStudios.Il2CppInspector NuGet 包
├── MultiKeyDictionary.cs              # 复合键字典（Method/FnPtr/AppMethod）
├── ResourceHelper.cs                  # manifest 资源读取
├── ULEB128.cs                         # ULEB128 解码
│
├── IL2CPP/                            # 公开 il2cpp API（依赖图最顶层）
│   ├── Il2CppBinary.cs                # 510 LOC, abstract partial
│   ├── Il2CppInspector.cs             # 611 LOC, 顶层 facade
│   ├── Metadata.cs                    # 451 LOC, global-metadata.dat 解析
│   ├── ImageScan.cs                   # 317 LOC, 二进制扫描启发式
│   ├── CustomAttributeDataReader.cs   # 193 LOC, v29+ 自定义属性
│   ├── MetadataUsage.cs               # 用法索引包装
│   └── Il2CppConstants.cs             # 246 LOC, il2cpp 常量/查表
│
├── Architectures/                     # Il2CppBinary<Arch> 子类
│   ├── Il2CppBinaryARM.cs             # 354 LOC, 32-bit ARM (Thumb/Thumb-2)
│   ├── Il2CppBinaryARM64.cs           # 186 LOC, 64-bit ARM64
│   ├── Il2CppBinaryX86.cs             # 113 LOC
│   └── Il2CppBinaryX64.cs             # 291 LOC, x86-64
│
├── Reflection/                        # 重建 .NET 类型系统
│   ├── TypeModel.cs                   # 398 LOC, 类型图编排
│   ├── TypeInfo.cs                    # 1231 LOC, 单文件最大
│   ├── MethodBase.cs                  # 345 LOC
│   ├── MethodInfo.cs / ConstructorInfo.cs
│   ├── FieldInfo.cs                   # 168 LOC
│   ├── PropertyInfo.cs                # 90 LOC
│   ├── EventInfo.cs                   # 140 LOC
│   ├── ParameterInfo.cs               # 140 LOC
│   ├── CustomAttributeData.cs         # 159 LOC
│   ├── CustomAttributeArgument.cs
│   ├── Assembly.cs                    # 90 LOC
│   ├── MemberInfo.cs                  # 40 LOC, 基类
│   ├── Constants.cs
│   ├── Scope.cs                       # 上下文（当前类型/命名空间缓存）
│   ├── MethodInvoker.cs               # il2cpp_invoke_ret_t 包装
│   └── Extensions.cs                  # 273 LOC, 代码发射 helper
│
├── Model/                             # 复合应用模型
│   ├── AppModel.cs                    # 386 LOC, 顶层
│   ├── AppType.cs                     # 50 LOC
│   ├── AppMethod.cs                   # 50 LOC
│   ├── AppReference.cs                # 30 LOC
│   ├── AppMethodReference.cs
│   ├── AppTypeReference.cs
│   └── AddressMap.cs                  # 167 LOC, IDictionary<ulong, object>
│
├── Cpp/                               # C++ 代码发射
│   ├── CppDeclarationGenerator.cs     # 689 LOC, 类型布局
│   ├── CppTypeCollection.cs           # 611 LOC, 头文件解析
│   ├── CppType.cs                     # 469 LOC, 类型层次
│   ├── CppField.cs                    # 104 LOC
│   ├── CppEnumField.cs
│   ├── CppNamespace.cs                # 89 LOC
│   ├── CppTypeDependencyGraph.cs      # 177 LOC, 拓扑排序
│   ├── CppCompilerType.cs             # enum + GuessFromImage
│   ├── MangledNameBuilder.cs          # 301 LOC, Itanium ABI mangler
│   ├── UnityHeaders/                  # 嵌入式 Unity 头文件
│   │   ├── UnityHeaders.cs            # 220 LOC
│   │   ├── UnityVersion.cs            # 238 LOC
│   │   └── *.h (54 个)                # EmbeddedResource
│   └── Il2CppAPIHeaders/*.h (20 个)   # EmbeddedResource
│
├── Outputs/                           # 代码/文本发射器
│   ├── CSharpCodeStubs.cs             # 726 LOC, C# 发射
│   ├── CppScaffolding.cs              # 458 LOC, C++ 工程
│   ├── AssemblyShims.cs               # 754 LOC, dnlib dummy DLL
│   ├── JSONMetadata.cs                # 306 LOC, JSON dump
│   ├── PythonScript.cs                # 82 LOC, IDA/Ghidra/BN 脚本
│   ├── ScriptResources/               # Python 模板
│   │   ├── shared_base.py             # 13.5 KB
│   │   └── Targets/{IDA,Ghidra,BinaryNinja}.py
│   └── OutputFormatStream.cs
│
├── FileFormatStreams/                 # 文件格式读取器
│   ├── FileFormatStream.cs            # 391 LOC, 接口 + 抽象基类 + Load 工厂
│   ├── PEReader.cs                    # 251 LOC, PE32/PE32+
│   ├── ElfReader.cs                   # 598 LOC, ELF32/ELF64
│   ├── MachOReader.cs                 # 391 LOC, Mach-O32/64 + Fat
│   ├── NsoReader.cs                   # 442 LOC, NSO + LZ4
│   ├── SElfReader.cs                  # 129 LOC, Switch ELF
│   ├── UBReader.cs                    # 46 LOC, Universal Binary
│   ├── APKReader.cs                   # 74 LOC
│   ├── AABReader.cs                   # 74 LOC
│   ├── ProcessMapReader.cs            # 125 LOC, /proc/self/maps
│   ├── LoadOptions.cs                 # 20 LOC
│   ├── Export.cs / Section.cs / Symbol.cs
│   ├── WordConversions.cs             # 57 LOC, 32↔64 bit 适配
│   └── FormatLayouts/                 # Bin2Object 结构定义
│       ├── Elf.cs / MachO.cs / Nso.cs
│       ├── PE.cs / SElf.cs / UB.cs
│
├── Next/                              # VersionedSerialization 化的新一代元数据
│   ├── BinaryObjectStreamReader.cs    # 155 LOC, 含 StructVersion
│   ├── Pointer.cs / PrimitivePointer.cs
│   ├── MetadataVersions.cs            # 55 LOC, V160..V1060
│   ├── Metadata/                      # ~50 个 [VersionedStruct] 类
│   │   ├── Il2CppGlobalMetadataHeader.cs # 351 LOC
│   │   ├── Il2CppAssemblyDefinition.cs
│   │   ├── Il2CppImageDefinition.cs
│   │   ├── Il2CppTypeDefinition.cs
│   │   ├── Il2CppMethodDefinition.cs
│   │   ├── Il2CppFieldDefinition.cs
│   │   ├── Il2CppEventDefinition.cs
│   │   ├── Il2CppPropertyDefinition.cs
│   │   ├── Il2CppParameterDefinition.cs
│   │   ├── Il2CppFieldDefaultValue.cs
│   │   ├── Il2CppParameterDefaultValue.cs
│   │   ├── Il2CppFieldRef.cs
│   │   ├── Il2CppFieldMarshaledSize.cs
│   │   ├── Il2CppMetadataUsageList.cs
│   │   ├── Il2CppMetadataUsagePair.cs
│   │   ├── Il2CppMetadataUsage.cs
│   │   ├── Il2CppMetadataUsageType.cs
│   │   ├── Il2CppMetadataRange.cs
│   │   ├── Il2CppSectionMetadata.cs
│   │   ├── Il2CppGenericContainer.cs
│   │   ├── Il2CppGenericParameter.cs
│   │   ├── Il2CppInterfaceOffsetPair.cs
│   │   ├── Il2CppInlineArrayLength.cs
│   │   ├── Il2CppTypeDefinitionBitfield.cs
│   │   ├── Il2CppWindowsRuntimeTypeNamePair.cs
│   │   ├── Il2CppCustomAttributeDataRange.cs
│   │   ├── Il2CppCustomAttributeTypeRange.cs
│   │   ├── Il2CppStringLiteral.cs
│   │   ├── IIndexType.cs
│   │   └── *Index.cs (DefaultValueDataIndex, EventIndex, FieldIndex, ...)
│   ├── BinaryMetadata/                # ~25 个 Il2Cpp 二进制布局结构
│   │   ├── Il2CppType.cs              # 3.8 KB
│   │   ├── Il2CppArrayType.cs
│   │   ├── Il2CppGenericClass.cs
│   │   ├── Il2CppGenericContext.cs
│   │   ├── Il2CppGenericInst.cs
│   │   ├── Il2CppGenericMethodFunctionsDefinitions.cs
│   │   ├── Il2CppGenericMethodIndices.cs
│   │   ├── Il2CppGuid.cs
│   │   ├── Il2CppInteropData.cs
│   │   ├── Il2CppCodeGenModule.cs
│   │   ├── Il2CppCodeRegistration.cs
│   │   ├── Il2CppMetadataRegistration.cs
│   │   ├── Il2CppMethodPointer.cs
│   │   ├── Il2CppMethodSpec.cs
│   │   ├── Il2CppRange.cs
│   │   ├── Il2CppRgctxConstrainedData.cs
│   │   ├── Il2CppRgctxDataType.cs
│   │   ├── Il2CppRgctxDefinition.cs
│   │   ├── Il2CppRgctxDefinitionData.cs
│   │   ├── Il2CppTokenAdjustorThunkPair.cs
│   │   ├── Il2CppTokenIndexMethodTuple.cs
│   │   ├── Il2CppTokenRangePair.cs
│   │   ├── Il2CppTypeDefinitionSizes.cs
│   │   ├── Il2CppTypeEnum.cs
│   │   └── Il2CppWindowsRuntimeFactoryTableEntry.cs
│   └── NameTranslation/
│       ├── NameTranslationInfo.cs
│       ├── NameTranslationParserContext.cs    # 187 LOC
│       └── NameTranslationApplierContext.cs   # 96 LOC
│
├── Plugins/                           # McMaster.NETCore.Plugins 宿主
│   ├── Internal/
│   │   ├── PluginManager.cs           # 437 LOC, 单例
│   │   ├── PluginHooks.cs             # 65 LOC, hook 转发
│   │   └── ICorePlugin.cs             # 标记接口
│   └── API/
│       ├── V100/
│       │   ├── IPlugin.cs             # 当前激活的插件契约
│       │   ├── ILoadPipeline.cs       # 13 个生命周期 hook
│       │   ├── IPluginOption.cs
│       │   ├── PluginEventInfo.cs
│       │   ├── PluginServices.cs
│       │   └── ReentrantAttribute.cs
│       └── V101/                      # 未来版本占位
│           ├── IPlugin.cs
│           └── Adapter.cs
│
├── Utils/
│   └── BlobReader.cs                  # 180 LOC, metadata blob 段读取
│
└── Properties/
    ├── Resources.resx                 # 文本模板（SlnProjectDefinition, ...）
    └── Resources.Designer.cs          # 546 LOC, 自动生成
```

## 2.3 `Il2CppInspector.CLI/` — 遗留 CLI

```
Il2CppInspector.CLI/
├── Il2CppInspector.CLI.csproj         # PublishSingleFile=true, RID=win-x64
├── Program.cs                         # 510 LOC, 全部 CLI flag
├── PluginOptions.cs                   # 259 LOC, IL emit 动态生成 CommandLineParser 选项
├── PathUtils.cs                       # 52 LOC, FindPath 通配符
└── Properties/launchSettings.json
```

## 2.4 `Il2CppInspector.GUI/` — 遗留 WPF

```
Il2CppInspector.GUI/
├── Il2CppInspector.GUI.csproj         # UseWPF=true, net10.0-windows
├── App.xaml + App.xaml.cs             # 352 LOC
├── MainWindow.xaml (35 KB) + MainWindow.xaml.cs   # 790 LOC
├── LoadOptionsDialog.xaml + .xaml.cs  # 39 LOC
├── PluginConfigurationDialog.xaml + .xaml.cs       # 320 LOC
├── PluginManagerDialog.xaml + .xaml.cs            # 128 LOC
├── EqualityConverter.cs               # 30 LOC
├── HexStringValueConverter.cs         # 43 LOC
├── User.Designer.cs (75) + User.settings
├── App.config / app.manifest / AssemblyInfo.cs
├── Il2CppInspector.ico
└── Resources/pizza.gif
```

## 2.5 `Il2CppInspector.Redux.FrontendCore/` — Redux 共享库

```
Il2CppInspector.Redux.FrontendCore/
├── Il2CppInspector.Redux.FrontendCore.csproj     # Sdk.Web, 库
├── UiContext.cs                                 # 272 LOC, SignalR 每连接状态
├── UiClient.cs                                  # 44 LOC, ISingleClientProxy 包装
├── Il2CppHub.cs                                 # 63 LOC, /il2cpp Hub
├── LoadingSession.cs                            # 22 LOC, IAsyncDisposable
├── Extensions.cs                                # 54 LOC, AddFrontendCore / MapFrontendCore
├── PathHeuristics.cs                            # 54 LOC, GameAssembly / il2cpp / UnityFramework
├── FrontendCoreJsonSerializerContext.cs         # 9 LOC, source-gen JSON
├── InspectorSettings.cs                         # 2 LOC, record
└── Outputs/
    ├── IOutputFormat.cs                         # 14 LOC
    ├── OutputFormatRegistry.cs                  # 38 LOC
    ├── CSharpStubOutput.cs                      # 66 LOC, Id="cs"
    ├── VsSolutionOutput.cs                      # 29 LOC, Id="vssolution"
    ├── DummyDllOutput.cs                        # 27 LOC, Id="dummydlls"
    ├── DisassemblerMetadataOutput.cs            # 53 LOC, Id="disassemblermetadata"
    ├── CppScaffoldingOutput.cs                  # 31 LOC, Id="cppscaffolding"
    ├── CSharpLayout.cs                          # 9 LOC, enum
    ├── TypeSortingMode.cs                       # 6 LOC, enum
    └── DisassemblerType.cs                      # 8 LOC, enum
```

## 2.6 `Il2CppInspector.Redux.CLI/` — Redux CLI

```
Il2CppInspector.Redux.CLI/
├── Il2CppInspector.Redux.CLI.csproj # Sdk.Web, SingleFile=true
├── Program.cs                       # 46 LOC, WebApplication 启动 + Spectre
├── CliClient.cs                     # 141 LOC, SignalR 客户端
├── PortProvider.cs                  # 5 LOC
├── ServiceTypeRegistrar.cs          # 29 LOC
├── ServiceTypeResolver.cs           # 12 LOC
├── Commands/
│   ├── BaseCommand.cs               # 38 LOC, AsyncCommand<T>
│   ├── InteractiveCommand.cs        # 15 LOC
│   ├── ManualCommand.cs             # 20 LOC
│   ├── ManualCommandSettings.cs     # 14 LOC
│   └── ProcessCommand.cs            # 197 LOC, 全部选项
├── appsettings.json + appsettings.Development.json
└── Properties/launchSettings.json
```

## 2.7 `Il2CppInspector.Redux.GUI/` — Redux GUI 宿主

```
Il2CppInspector.Redux.GUI/
├── Il2CppInspector.Redux.GUI.csproj # Sdk.Web, WinExe (Release), BeforeBuild: pnpm tauri build
├── Program.cs                       # 38 LOC
├── UiProcessService.cs              # 71 LOC, 启动 Tauri 进程
├── appsettings.json + appsettings.Development.json
└── Properties/launchSettings.json
```

## 2.8 `Il2CppInspector.Redux.GUI.UI/` — Tauri/Svelte 前端（独立运行时）

```
Il2CppInspector.Redux.GUI.UI/
├── package.json, pnpm-lock.yaml
├── vite.config.js, svelte.config.js
├── tailwind.config.ts, tsconfig.json
├── postcss.config.js, components.json
├── .prettierrc, .gitignore
├── static/
├── src/
│   ├── app.html, app.css
│   ├── lib/
│   │   ├── tauri.ts (444 B), export.svelte.ts (606 B)
│   │   ├── settings.ts (643 B), utils.ts (168 B)
│   │   ├── signalr/
│   │   │   ├── server-api.ts (1.3 KB)
│   │   │   ├── client-api.ts (1.75 KB)
│   │   │   └── api.svelte.ts (1.4 KB)
│   │   ├── components/
│   │   │   ├── Footer.svelte, Header.svelte, loading.svelte
│   │   │   ├── settings/{combobox,option,path-selector}.svelte
│   │   │   └── ui/                       # shadcn-svelte 原语
│   │   │       ├── button/, card/, checkbox/, command/
│   │   │       ├── dialog/, label/, popover/, select/
│   │   │       └── separator/, sonner/, tooltip/
│   └── routes/
│       ├── +layout.svelte, +layout.ts
│       ├── +page.svelte
│       ├── advanced/+page.svelte
│       ├── export/+page.svelte, +page.ts
│       ├── export/[formatId]/+page.svelte, +page.ts
│       └── options/+page.svelte
└── src-tauri/
    ├── Cargo.toml, Cargo.lock
    ├── build.rs
    ├── tauri.conf.json
    ├── capabilities/default.json
    ├── src/main.rs (6 LOC), lib.rs (20 LOC)
    └── icons/ (icns, ico, Square*Logo.png)
```

## 2.9 `Il2CppTests/` — NUnit 测试集

```
Il2CppTests/
├── Il2CppTests.csproj                # NUnit 3.14.0, Adapter 3.17.0
├── TestRunner.cs                     # 13.3 KB, 主回归
├── TestRunnerConfig.cs
├── TestCppTypeDeclarations.cs        # 4.2 KB
├── TestAppModelQueries.cs            # 2.8 KB
├── TestGenerics.cs                   # 8.7 KB
├── TestNames.cs                      # 2.0 KB
├── TestUnityVersion.cs               # 1.1 KB
├── TestSources/*.cs                  # Compile Remove（仅作为 Content）
├── TestExpectedResults/*.{cs,json,h} # 同上
├── generate-tests.ps1 (997 B)
├── il2cpp.ps1 (12.2 KB)
└── update-expected-results.ps1 (2.8 KB)
```

## 2.10 `VersionedSerialization/` — 独立 Roslyn 友好库

```
VersionedSerialization/
├── VersionedSerialization.csproj     # net10.0, MIT, 携带 Generator 作为 analyzer
├── IReadable.cs / IReader.cs
├── ISeekableReader.cs / INonSeekableReader.cs
├── ReadableExtensions.cs / SeekableReaderExtensions.cs
├── ReaderConfig.cs / ReaderExtensions.cs
├── Reader.cs                         # 98 LOC, 通用入口
├── Reader`1.cs                       # 107 LOC, 版本分发
├── StructVersion.cs                  # 103 LOC
├── Impl/
│   ├── EndianReader.cs               # 181 LOC, Little/Big EndianSeekableReader
│   └── SpanReader.cs                 # 68 LOC
└── Attributes/
    ├── VersionedStructAttribute.cs
    ├── VersionConditionAttribute.cs
    └── NativeIntegerAttribute.cs
```

## 2.11 `VersionedSerialization.Generator/` — Roslyn 生成器

```
VersionedSerialization.Generator/
├── VersionedSerialization.Generator.csproj # netstandard2.0
├── ObjectSerializationGenerator.cs          # 415 LOC, IIncrementalGenerator
├── StructVersion.cs                         # 51 LOC
├── Analyzer/
│   └── InvalidVersionAnalyzer.cs            # 69 LOC, DiagnosticAnalyzer
├── Models/
│   ├── ObjectSerializationInfo.cs
│   ├── PropertySerializationInfo.cs
│   ├── PropertyType.cs                      # 76 LOC
│   └── VersionCondition.cs
└── Utils/
    ├── CodeGenerator.cs (54)
    ├── HashCode.cs                          # 453 LOC
    ├── ImmutableEquatableArray.cs           # 114 LOC
    └── Constants.cs                         # 20 LOC
```