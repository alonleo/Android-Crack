# 07 — Functions Index

This is the consolidated index of every catalogued function / method. The detailed per-file references (with full caller/callee lists and side effects) live in [08_functions_detail/](./08_functions_detail/). This index is sorted by sub-project, then by file, then by line.

> Format: `ClassName.MemberName(params)` at `path:line` — one-line summary.

## 7.1 `ICSharpCode.Decompiler` — core engine

### `Decompiler.cs`

| Member | Line | Summary |
|---|---:|---|
| `Decompiler.DecompileAsync(...)` | `Decompiler.cs:1` | async facade; orchestrates engine + progress + cancellation |
| `Decompiler.DecompileTypeAsStringAsync(...)` | `Decompiler.cs:1` | per-type async decompile returning text |
| `Decompiler.AssemblyResolver` | `Decompiler.cs:1` | property: `IAssemblyResolver` for AssemblyRef resolution |

### `DecompilerSettings.cs` (2450 LoC — too many properties to enumerate; ~200 settings)

| Member | Line | Summary |
|---|---:|---|
| `DecompilerSettings` ctor | `DecompilerSettings.cs:35` | default settings |
| `DecompilerSettings(LanguageVersion)` ctor | `DecompilerSettings.cs:48` | language-version-aware settings |
| `SetLanguageVersion(LanguageVersion)` | `DecompilerSettings.cs:56` | update language version |
| `GetMinimumRequiredVersion()` | `DecompilerSettings.cs:182` | lowest `LanguageVersion` needed to compile output |
| `NativeIntegers` | `DecompilerSettings.cs:234` | use `nint`/`nuint` for native-size ints |
| `RecordClasses` / `RecordStructs` | `DecompilerSettings.cs:306 / 324` | use C# 9 record syntax |
| `AsyncAwait` | `DecompilerSettings.cs:602` | de-sugar `async`/`await` |
| `YieldReturn` | `DecompilerSettings.cs:566` | de-sugar `yield return` |
| `Dynamic` | `DecompilerSettings.cs:584` | preserve `dynamic` |
| `UseDebugSymbols` | (in `DecompilerSettings.cs`) | consume PDB info to recover names |
| `DecompilationMaxStepCount` | (in `DecompilerSettings.cs`) | raise `StepLimitReachedException` when exceeded |

### `CSharp/CSharpDecompiler.cs` (2517 LoC)

| Member | Line | Summary |
|---|---:|---|
| `CSharpDecompiler` ctor (`string, DecompilerSettings`) | `CSharpDecompiler.cs:243` | open PE + default resolver |
| `CSharpDecompiler` ctor (`string, IAssemblyResolver, DecompilerSettings`) | `CSharpDecompiler.cs:251` | open PE + custom resolver |
| `CSharpDecompiler` ctor (`MetadataFile, IAssemblyResolver, DecompilerSettings`) | `CSharpDecompiler.cs:259` | use pre-loaded `MetadataFile` |
| `CSharpDecompiler` ctor (`IDecompilerTypeSystem, DecompilerSettings`) | `CSharpDecompiler.cs:267` | use pre-built type system |
| `GetILTransforms()` (static) | `CSharpDecompiler.cs:88` | **THE 30-step ILAst pipeline** |
| `GetAstTransforms()` (static) | `CSharpDecompiler.cs:185` | the 16-step AST pipeline |
| `Stepper` (property) | `CSharpDecompiler.cs:180` | step-through hook for debug UI |
| `TypeSystem` (property) | `CSharpDecompiler.cs:214` | `IDecompilerTypeSystem` |
| `DebugInfoProvider` (property) | `CSharpDecompiler.cs:219` | PDB source for variable names |
| `MemberIsHidden(MetadataFile?, EntityHandle, DecompilerSettings)` | `CSharpDecompiler.cs:284` | should this entity be hidden in the tree? |
| `DecompileModuleAndAssemblyAttributes()` | `CSharpDecompiler.cs:758` | just `assembly { ... }` block + module attrs |
| `DecompileWholeModuleAsSingleFile()` | `CSharpDecompiler.cs:835` | entire module in one file |
| `DecompileWholeModuleAsSingleFile(bool sortTypes)` | `CSharpDecompiler.cs:845` | same with sorting |
| `CreateILTransformContext(ILFunction)` | `CSharpDecompiler.cs:869` | build `ILTransformContext` for a function |
| `GetCodeMappingInfo(MetadataFile, EntityHandle)` | `CSharpDecompiler.cs:883` | state-machine / lambda / local-func decomposition |
| `DecompileWholeModuleAsString()` | `CSharpDecompiler.cs:1155` | text-output variant of whole module |
| `DecompileTypes(IEnumerable<TypeDefinitionHandle>)` | `CSharpDecompiler.cs:1166` | multi-type decompile |
| `DecompileType(FullTypeName)` | `CSharpDecompiler.cs:1205` | single-type decompile |
| `Decompile(params EntityHandle[])` | `CSharpDecompiler.cs:1236` | single-entity entry |
| `Decompile(IEnumerable<EntityHandle>)` | `CSharpDecompiler.cs:1244` | single-entity entry (collection) |
| `DecompileExtension(EntityHandle)` | `CSharpDecompiler.cs:1330` | extension-method-group decompile |
| `DecompileAsString(...)` | `CSharpDecompiler.cs:1397 / 1405` | text-output variants |
| `AddPartialTypeDefinition(PartialTypeInfo)` | `CSharpDecompiler.cs:1412` | add partial type info for round-trip |
| `CreateSequencePoints(SyntaxTree)` | `CSharpDecompiler.cs:2509` | map IL offsets to text positions for PDB |

### `CSharp/CallBuilder.cs` (2300 LoC)

| Member | Line | Summary |
|---|---:|---|
| `CallBuilder.Convert(Call, ...)` | `CallBuilder.cs:1` | ILAst `Call`/`CallVirt` -> `InvocationExpression` / `MemberReferenceExpression` |
| `CallBuilder.ConvertAddressOfMember(...)` | `CallBuilder.cs:1` | address-of -> `AddressOfExpression` |

### `CSharp/ExpressionBuilder.cs` (5018 LoC — largest file)

| Member | Line | Summary |
|---|---:|---|
| `ExpressionBuilder.Convert(ILInstruction, ...)` | `ExpressionBuilder.cs:1` | top-level ILAst -> `Expression` |
| `ExpressionBuilder.ConvertLdLoc(...)` | `ExpressionBuilder.cs:1` | local-variable load |
| `ExpressionBuilder.ConvertBinaryOperator(...)` | `ExpressionBuilder.cs:1` | `add`, `sub`, ... |
| (200+ per-instruction visitors) | various | one `Visit*` per ILAst instruction kind |

### `CSharp/StatementBuilder.cs` (1586 LoC)

| Member | Line | Summary |
|---|---:|---|
| `StatementBuilder.ConvertAsBlock(Block)` | `StatementBuilder.cs:1` | ILAst `Block` -> `BlockStatement` |
| `StatementBuilder.Convert(ILInstruction)` | `StatementBuilder.cs:1` | single ILAst instruction -> `Statement` |

### `CSharp/OutputVisitor/CSharpOutputVisitor.cs` (3164 LoC)

| Member | Line | Summary |
|---|---:|---|
| `CSharpOutputVisitor.WriteTo(TextWriter)` | `CSharpOutputVisitor.cs:1` | top-level: write the entire `SyntaxTree` |
| `CSharpOutputVisitor.VisitTypeDeclaration(...)` | `CSharpOutputVisitor.cs:1` | one class/struct/interface |
| `CSharpOutputVisitor.VisitMethodDeclaration(...)` | `CSharpOutputVisitor.cs:1` | one method |
| `CSharpOutputVisitor.VisitExpression(...)` | `CSharpOutputVisitor.cs:1` | generic expression visit |
| (100+ per-AstNode visitors) | various | one `Visit*` per `AstNode` subtype |

### `CSharp/OutputVisitor/CSharpAmbience.cs`

| Member | Line | Summary |
|---|---:|---|
| `CSharpAmbience.ConvertSymbol(ISymbol)` | `CSharpAmbience.cs:1` | symbol -> display string (tooltip) |
| `CSharpAmbience.ConvertType(IType)` | `CSharpAmbience.cs:1` | type -> display string |

### `CSharp/ProjectDecompiler/WholeProjectDecompiler.cs`

| Member | Line | Summary |
|---|---:|---|
| `WholeProjectDecompiler.DecompileProject(MetadataFile, string, TextWriter)` | `WholeProjectDecompiler.cs:1` | entire module -> `.csproj` + per-type `.cs` |
| `WholeProjectDecompiler.CanUseSdkStyleProjectFormat` | `WholeProjectDecompiler.cs:1` | SDK-style proj writer check |

### `CSharp/Resolver/CSharpResolver.cs` (2986 LoC)

| Member | Line | Summary |
|---|---:|---|
| `CSharpResolver.ResolveSimpleName(...)` | `CSharpResolver.cs:1` | identifier -> `ResolveResult` |
| `CSharpResolver.ResolveMemberType(...)` | `CSharpResolver.cs:1` | member access type lookup |
| `CSharpResolver.ResolveIdentifier(...)` | `CSharpResolver.cs:1` | identifier resolution |

### `IL/ILReader.cs` (2191 LoC)

| Member | Line | Summary |
|---|---:|---|
| `ILReader` ctor (`MetadataModule`) | `ILReader.cs:139` | bind to a module |
| `UseDebugSymbols` (property) | `ILReader.cs:124` | honor PDB info |
| `UseRefLocalsForAccurateOrderOfEvaluation` | `ILReader.cs:125` | introduce `ref` locals to model eval order |
| `DebugInfo` (property) | `ILReader.cs:126` | PDB provider |
| `Warnings` (property) | `ILReader.cs:127` | warnings collected during import |
| `SequencePointCandidates` (property) | `ILReader.cs:131` | IL offsets that may be sequence points |
| `WriteTypedIL(MethodDefinitionHandle, MethodBodyBlock, ...)` | `ILReader.cs:688` | debug: emit typed-IL dump |
| `ReadIL(MethodDefinitionHandle, MethodBodyBlock, ...)` | `ILReader.cs:720` | **CIL -> ILFunction** |
| `ILReader.Cast(ILInstruction, StackType, List<string>?, int)` (internal static) | `ILReader.cs:1398` | coerce operand to expected stack type |

### `IL/Instructions/ILFunction.cs`

| Member | Line | Summary |
|---|---:|---|
| `ILFunction.Body` | `ILFunction.cs:1` | root `BlockContainer` |
| `ILFunction.Variables` | `ILFunction.cs:1` | declared locals |
| `ILFunction.IsAsync` | `ILFunction.cs:1` | compiler-emitted state machine? |
| `ILFunction.IsIterator` | `ILFunction.cs:1` | compiler-emitted iterator? |
| `ILFunction.Warnings` | `ILFunction.cs:1` | import warnings |

### `IL/ControlFlow/ControlFlowGraph.cs`

| Member | Line | Summary |
|---|---:|---|
| `ControlFlowGraph` ctor (`BlockContainer, CancellationToken`) | `ControlFlowGraph.cs:69` | build CFG from ILAst block container |
| `Nodes` (property) | `ControlFlowGraph.cs:1` | the `ControlFlowNode` array |
| `HasReachableExit(ControlFlowNode)` | `ControlFlowGraph.cs:1` | is exit reachable? |

### `IL/ControlFlow/AsyncAwaitDecompiler.cs`

| Member | Line | Summary |
|---|---:|---|
| `AsyncAwaitDecompiler.Run(ILFunction)` | `AsyncAwaitDecompiler.cs:1` | state-machine -> `await` |

### `IL/ControlFlow/YieldReturnDecompiler.cs`

| Member | Line | Summary |
|---|---:|---|
| `YieldReturnDecompiler.Run(ILFunction)` | `YieldReturnDecompiler.cs:1` | state-machine -> `yield return` |

### `TypeSystem/DecompilerTypeSystem.cs`

| Member | Line | Summary |
|---|---:|---|
| `DecompilerTypeSystem.CreateAsync(PEFile, IAssemblyResolver)` | `DecompilerTypeSystem.cs:127` | async factory |
| `DecompilerTypeSystem.Create(MetadataFile, IAssemblyResolver, DecompilerSettings)` | `DecompilerTypeSystem.cs:1` | sync factory |
| `GetOptions(DecompilerSettings)` | `DecompilerTypeSystem.cs:1` | extract `TypeSystemOptions` from settings |

### `Metadata/UniversalAssemblyResolver.cs`

| Member | Line | Summary |
|---|---:|---|
| `UniversalAssemblyResolver` ctor | `UniversalAssemblyResolver.cs:1` | set up resolver |
| `AddSearchDirectory(string)` | `UniversalAssemblyResolver.cs:1` | add path |
| `ResolveAsync(IAssemblyReference)` | `UniversalAssemblyResolver.cs:1` | async AssemblyRef -> PEFile |
| `ResolveModuleAsync(ModuleReference)` | `UniversalAssemblyResolver.cs:1` | async ModuleRef -> PEFile |

### `Disassembler/ReflectionDisassembler.cs`

| Member | Line | Summary |
|---|---:|---|
| `ReflectionDisassembler.WriteModuleContents(PEFile)` | `ReflectionDisassembler.cs:1` | entire module -> IL text |
| `ReflectionDisassembler.WriteMember(...)` | `ReflectionDisassembler.cs:1` | one member -> IL text |

## 7.2 `ICSharpCode.ILSpyX`

### `LoadedAssembly.cs`

| Member | Line | Summary |
|---|---:|---|
| `LoadedAssembly` ctor (AssemblyList, fileName, ...) | `LoadedAssembly.cs:92 / 127` | lazy load via `FileLoaderRegistry` |
| `GetLoadResultAsync()` | `LoadedAssembly.cs:195` | awaits the `Lazy<Task<LoadResult>>` |
| `GetMetadataFileAsync()` | `LoadedAssembly.cs:203` | unwrap to `MetadataFile` |
| `GetMetadataFileOrNull()` | `LoadedAssembly.cs:216` | sync |
| `GetMetadataFileOrNullAsync()` | `LoadedAssembly.cs:234` | async |
| `GetTypeSystemOrNull(...)` | `LoadedAssembly.cs:257 / 278` | build / reuse `ICompilation` |
| `Loaded` (event) | `LoadedAssembly.cs:79` | fired when load completes |
| `IsLoaded` (property) | `LoadedAssembly.cs:363` | has the lazy task completed? |
| `Dispose()` | `LoadedAssembly.cs:1` | release resources |
| `loadedAssemblies` (static `ConditionalWeakTable`) | `LoadedAssembly.cs:1` | `MetadataFile` -> `LoadedAssembly` cache |

### `AssemblyList.cs`

| Member | Line | Summary |
|---|---:|---|
| `AssemblyList.OpenAssembly(...)` | `AssemblyList.cs:1` | add a `LoadedAssembly` to the list |
| `AssemblyList.Clear()` | `AssemblyList.cs:1` | remove all |
| `AssemblyList.RefreshAssemblies()` | `AssemblyList.cs:1` | re-load all |
| `AssemblyList.Save(...)` / `AssemblyList.Load(...)` | `AssemblyList.cs:1` | persist to disk |

### `AssemblyListManager.cs`

| Member | Line | Summary |
|---|---:|---|
| `CreateList(string)` | `AssemblyListManager.cs:1` | new list with undo |
| `DeleteList(...)` | `AssemblyListManager.cs:1` | remove with undo |
| `RenameList(...)` | `AssemblyListManager.cs:1` | rename with undo |
| `SetCurrentList(...)` | `AssemblyListManager.cs:1` | switch active list |

### `FileLoaders/FileLoaderRegistry.cs`

| Member | Line | Summary |
|---|---:|---|
| `FileLoaderRegistry.Load(string)` | `FileLoaderRegistry.cs:1` | dispatch to appropriate loader |
| (5 concrete loaders) | each file | `PEFileLoader`, `ArchiveFileLoader`, `BundleFileLoader`, `XamarinCompressedFileLoader`, `WebCilFileLoader`, `MetadataFileLoader` |

### `Search/AbstractEntitySearchStrategy.cs` and 9 concrete strategies

| Type | Line | Summary |
|---|---:|---|
| `AbstractEntitySearchStrategy<T>` | `Search/AbstractEntitySearchStrategy.cs:1` | abstract base |
| `AssemblySearchStrategy` | `Search/AssemblySearchStrategy.cs:1` | `t:List` matches assemblies by name |
| `MemberSearchStrategy` | `Search/MemberSearchStrategy.cs:1` | `m:Foo` matches type members |
| `NamespaceSearchStrategy` | `Search/NamespaceSearchStrategy.cs:1` | matches namespaces |
| `LiteralSearchStrategy` | `Search/LiteralSearchStrategy.cs:1` | plain substring across everything |
| `MetadataTokenSearchStrategy` | `Search/MetadataTokenSearchStrategy.cs:1` | `0x06000001` |
| `ResourceSearchStrategy` | `Search/ResourceSearchStrategy.cs:1` | matches resource names |

### `MermaidDiagrammer/GenerateHtmlDiagrammer.cs`

| Member | Line | Summary |
|---|---:|---|
| `GenerateHtmlDiagrammer.Run()` | `GenerateHtmlDiagrammer.cs:1` | top-level driver |
| `Factory.BuildTypes` | `GenerateHtmlDiagrammer.cs:1` | enumerate types |
| `Factory.Relationships` | `GenerateHtmlDiagrammer.cs:1` | build extends/implements/field edges |
| `ClassDiagrammer.Render` | `MermaidDiagrammer/ClassDiagrammer.cs:1` | emit Mermaid syntax |

### `Settings/DecompilerSettings.cs` (ILSpyX — different from core engine)

| Member | Line | Summary |
|---|---:|---|
| `Load()` (static) | `Settings/DecompilerSettings.cs:1` | restore from XML |
| `Save()` | `Settings/DecompilerSettings.cs:1` | persist to XML |

### `Settings/ILSpySettings.cs`

| Member | Line | Summary |
|---|---:|---|
| `ILSpySettings.Load()` (static) | `Settings/ILSpySettings.cs:1` | read `ILSpy.xml` |
| `SettingsFilePathProvider` | `Settings/ILSpySettings.cs:1` | factory for the settings path |

## 7.3 `ILSpy` (Avalonia GUI)

### `Program.cs`

| Member | Line | Summary |
|---|---:|---|
| `Program.Main(string[])` | `Program.cs:35` | `[STAThread]` Avalonia entry |
| `BuildAvaloniaApp()` | `Program.cs:1` | returns `AppBuilder.Configure<App>().UsePlatformDetect()...` |

### `App.axaml.cs`

| Member | Line | Summary |
|---|---:|---|
| `App.Initialize()` | `App.axaml.cs:1` | XAML load via `AvaloniaXamlLoader.Load(this)` |
| `App.OnFrameworkInitializationCompleted()` | `App.axaml.cs:36` | MEF init, settings path, culture |
| `App.CommandLineArguments` (static) | `App.axaml.cs:1` | parsed CLI |
| `App.Composition` (static) | `App.axaml.cs:1` | `CompositionHost` reference |

### `AppEnv/AppComposition.cs`

| Member | Line | Summary |
|---|---:|---|
| `AppComposition.Initialize()` | `AppComposition.cs:67` | discover plugins + create MEF container |
| `AppComposition.Current` | `AppComposition.cs:47` | the live container |
| `AppComposition.TryGetExport<T>()` | `AppComposition.cs:57` | one export lookup |
| `AppComposition.TryGetExports<T>()` | `AppComposition.cs:64` | many-export enumeration |
| `RegisterPluginResolver()` | `AppComposition.cs:78` | hooks `AssemblyLoadContext` |
| `CreateContainer()` | `AppComposition.cs:99` | builds MEF container |

### `AppEnv/CommandLineArguments.cs`

| Member | Line | Summary |
|---|---:|---|
| `CommandLineArguments.Create(IEnumerable<string>)` | `CommandLineArguments.cs:40-103` | parse all flags |
| properties for each flag | `CommandLineArguments.cs:1` | `--newinstance`, `-n`, `-s`, `-l`, `-c`, `--noactivate` |

### `Entry.cs`

| Member | Line | Summary |
|---|---:|---|
| `Entry` ctor | `Entry.cs:1` | public facade for embedding |
| `ShowAssemblies(IEnumerable<string>)` | `Entry.cs:1` | load + display |

### `NavigationHistory.cs`

| Member | Line | Summary |
|---|---:|---|
| `NavigationHistory<T>.Record(T)` | `NavigationHistory.cs:1` | push current |
| `GoBack()` / `GoForward()` | `NavigationHistory.cs:1` | move between stacks |
| `CanNavigateBack` / `CanNavigateForward` | `NavigationHistory.cs:1` | test stack state |

### `Commands/CommandManager.cs`

| Member | Line | Summary |
|---|---:|---|
| `CommandManager.InvalidateRequerySuggested()` | `Commands/CommandManager.cs:1` | weak-event re-query signal |
| `CommandManager.RequerySuggested` (event) | `Commands/CommandManager.cs:1` | weak `RequerySuggested` analog |

### `Commands/...` (~44 files, one per command)

| File | Purpose |
|---|---|
| `FileCommands.cs` | open, save, recent files, exit |
| `ViewCommands.cs` | toggle tool panes, font size |
| `WindowCommands.cs` | new window, close |
| `HelpCommands.cs` | about, docs |
| `MainMenuCommandRegistry.cs` | assembles main menu |
| `ToolbarCommandRegistry.cs` | assembles toolbar |
| `ToolPaneRegistry.cs` | tool pane provider registry |
| `AboutCommand.cs` | About dialog |
| `DecompileAllCommand.cs` | decompile all loaded assemblies |
| `BrowseBackCommand.cs` / `BrowseForwardCommand.cs` | history nav |
| `ProjectExport.cs` / `ProjectExporter.cs` / `ProjectExportOptions.cs` | `-p` GUI equivalent |
| `FilePickers.cs` | file / folder picker helpers |
| `PdbGenerator.cs` | `-genpdb` GUI equivalent |
| `ResourceLinkGenerator.cs` | resource-link resolution for tree nodes |

### `Search/SearchPaneModel.cs`

| Member | Line | Summary |
|---|---:|---|
| `SearchPaneModel.StartSearch()` | `SearchPaneModel.cs:1` | entry point |
| `SearchPaneModel.Cancel()` | `SearchPaneModel.cs:1` | abort |

### `Search/RunningSearch.cs`

| Member | Line | Summary |
|---|---:|---|
| `RunningSearch.Start(strategy)` | `RunningSearch.cs:1` | pick strategy + run |

### `ViewModels/MainWindowViewModel.cs`

| Member | Line | Summary |
|---|---:|---|
| `MainWindowViewModel` (ctor) | `ViewModels/MainWindowViewModel.cs:1` | `[ImportingConstructor]`; pulls dependencies |
| `[Export][Shared]` attribute | `ViewModels/MainWindowViewModel.cs:1` | MEF singleton |

## 7.4 `ICSharpCode.ILSpyCmd`

### `IlspyCmdProgram.cs` (~700 LoC, 28 flags)

| Member | Line | Summary |
|---|---:|---|
| `ILSpyCmdProgram.Main(string[])` | `IlspyCmdProgram.cs:71` | `HostBuilder().RunCommandLineApplicationAsync` entry |
| `OnExecuteAsync(CommandLineApplication)` | `IlspyCmdProgram.cs:236` | dispatch on flags |
| `PerformPerFileAction(file)` | `IlspyCmdProgram.cs:286` | dispatch per input file |
| `Decompile(fileName, output, typeName)` | `IlspyCmdProgram.cs:1` | build `CSharpDecompiler` + decompile |
| `DecompileAsProject(...)` | `IlspyCmdProgram.cs:275` | `-p` branch |
| `GeneratePdbForAssembly(...)` | `IlspyCmdProgram.cs:330` | `-genpdb` branch |
| `GetDecompiler(fileName)` | `IlspyCmdProgram.cs:430-510` | build `CSharpDecompiler` (PE + resolver + settings) |
| `ApplySettingOverride(...)` | `IlspyCmdProgram.cs:1` | `-ds name=value` reflection on `DecompilerSettings` |
| 28 `[Option]` properties | `IlspyCmdProgram.cs:1` | one per CLI flag |

### `BamlAwareWholeProjectDecompiler.cs`

| Member | Line | Summary |
|---|---:|---|
| `BamlAwareWholeProjectDecompiler.DecompileProject(...)` | override | extends `WholeProjectDecompiler` to translate `.g.resources` BAML |

### `DotNetToolUpdateChecker.cs`

| Member | Line | Summary |
|---|---:|---|
| `DotNetToolUpdateChecker.CheckForUpdateAsync()` | `DotNetToolUpdateChecker.cs:1` | NuGet version probe (skipped with `--disable-updatecheck`) |

### `TypesParser.cs`

| Member | Line | Summary |
|---|---:|---|
| `TypesParser.Parse(string)` | `TypesParser.cs:1` | `-l c,i,s,d,e` -> `TypeKind` set |

## 7.5 Other sub-projects

### `ICSharpCode.Decompiler.Generators`

| Type | Line | Summary |
|---|---:|---|
| `DecompilerVersionInfoGenerator` | `ICSharpCode.Decompiler.Generators/...:1` | Roslyn `ISourceGenerator` emitting `Properties/DecompilerVersionInfo.cs` |

### `ICSharpCode.BamlDecompiler`

| Member | Line | Summary |
|---|---:|---|
| `BamlDecompiler.Decompile(...)` | `ICSharpCode.BamlDecompiler/...:1` | BAML -> XAML |

### `ICSharpCode.Decompiler.PowerShell`

| Member | Line | Summary |
|---|---:|---|
| (cmdlets) | `ICSharpCode.Decompiler.PowerShell/...:1` | `Get-DecompiledCSharp`, `Export-DecompiledProject`, ... |

## Coverage summary

| Bucket | Function entries |
|---|---:|
| Core engine (`ICSharpCode.Decompiler`) | ~40 |
| C# AST layer (`CSharpDecompiler`, builders, visitors) | ~80 (with sub-visitors aggregated) |
| ILSpyX (UI-host core) | ~30 |
| Avalonia GUI (`ILSpy/`) | ~60 (including command handlers) |
| CLI (`ICSharpCode.ILSpyCmd`) | ~30 |
| Other sub-projects | ~5 |
| **Total catalogued in 07 + 08** | **~250 entries** |