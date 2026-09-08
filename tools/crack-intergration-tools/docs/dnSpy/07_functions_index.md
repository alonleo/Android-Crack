# 07 — Functions Index

This is the consolidated index of every catalogued function / method. The detailed per-file references (with full caller/callee lists and side effects) live in [08_functions_detail/](./08_functions_detail/). This index is sorted by sub-project, then by file, then by line.

> Format: `ClassName.MemberName(params)` at `path:line` — one-line summary.

## 7.1 `dnSpy/dnSpy/dnSpy` (Main WPF GUI)

### `MainApp/StartUpClass.cs`

| Member | Line | Summary |
|---|---:|---|
| `StartUpClass.Main()` | `MainApp/StartUpClass.cs:33` | `[STAThread]` WPF entry; multicore-JIT + BG JIT profile |

### `MainApp/App.xaml.cs`

| Member | Line | Summary |
|---|---:|---|
| `App` ctor | `MainApp/App.xaml.cs:97` | starts MEF init in background; loads settings |
| `App.InitializeMEF(readSettings, useCache)` | `MainApp/App.xaml.cs:1` | one-time MEF composition (cached or fresh) |
| `App.TryCreateExportProviderFactoryCached(...)` | `MainApp/App.xaml.cs:1` | try cached MEF composition |
| `App.CreateExportProviderFactorySlow(...)` | `MainApp/App.xaml.cs:1` | full MEF composition |
| `App.GetAssemblies()` | `MainApp/App.xaml.cs:1` | list of built-in assemblies |
| `App.LoadExtensionAssemblies()` | `MainApp/App.xaml.cs:316-371` | enumerates `*.x.dll` |
| `App.GetExtensionFiles(string)` | `MainApp/App.xaml.cs:1` | finds `*.x.dll` in a directory |
| `App.CanLoadExtension(string)` | `MainApp/App.xaml.cs:362-401` | reads `<file>.xml` config |
| `App.CanLoadExtension(Assembly)` | `MainApp/App.xaml.cs:1` | checks public key + min version |
| `App.OnStartup(StartupEventArgs)` | `MainApp/App.xaml.cs:521` | awaits MEF, opens main window |
| `App.HandleAppArgs(IAppCommandLineArgs)` | `MainApp/App.xaml.cs:1` | applies CLI args |
| `App.HandleAppArgs2(IAppCommandLineArgs)` | `MainApp/App.xaml.cs:1` | dispatches to `IAppCommandLineArgsHandler`s in `Order` |
| `App.SwitchToOtherInstance()` | `MainApp/App.xaml.cs:411-470` | WM_COPYDATA forward |
| `App.GetDecompiler(string language)` | `MainApp/App.xaml.cs:1` | resolve `IDecompiler` by name/GUID |

### `MainApp/AppCommandLineArgs.cs` (~25 flags)

| Member | Line | Summary |
|---|---:|---|
| `AppCommandLineArgs(string[] args)` | `MainApp/AppCommandLineArgs.cs:61` | parses all flags |
| `SettingsFilename` | `MainApp/AppCommandLineArgs.cs:31` | `--settings-file` |
| `Filenames` | `MainApp/AppCommandLineArgs.cs:32` | positional |
| `SingleInstance` | `MainApp/AppCommandLineArgs.cs:33` | `--multiple` toggle |
| `Activate` | `MainApp/AppCommandLineArgs.cs:34` | `--dont-activate` toggle |
| `Language` | `MainApp/AppCommandLineArgs.cs:35` | `-l`/`--language` |
| `Culture` | `MainApp/AppCommandLineArgs.cs:36` | `--culture` |
| `SelectMember` | `MainApp/AppCommandLineArgs.cs:37` | `--select` |
| `NewTab` | `MainApp/AppCommandLineArgs.cs:38` | `--new-tab` |
| `SearchText` | `MainApp/AppCommandLineArgs.cs:39` | `--search` |
| `SearchFor` | `MainApp/AppCommandLineArgs.cs:40` | `--search-for` |
| `SearchIn` | `MainApp/AppCommandLineArgs.cs:41` | `--search-in` |
| `Theme` | `MainApp/AppCommandLineArgs.cs:42` | `--theme` |
| `LoadFiles` | `MainApp/AppCommandLineArgs.cs:43` | `--dont-load-files` toggle |
| `FullScreen` | `MainApp/AppCommandLineArgs.cs:44` | `--full-screen`/`--not-full-screen` |
| `ShowToolWindow` | `MainApp/AppCommandLineArgs.cs:45` | `--show-tool-window` |
| `HideToolWindow` | `MainApp/AppCommandLineArgs.cs:46` | `--hide-tool-window` |
| `ShowStartupTime` | `MainApp/AppCommandLineArgs.cs:47` | `--show-startup-time` |
| `DebugAttachPid` | `MainApp/AppCommandLineArgs.cs:48` | `-p`/`--pid` |
| `DebugEvent` | `MainApp/AppCommandLineArgs.cs:49` | `-e` |
| `JitDebugInfo` | `MainApp/AppCommandLineArgs.cs:50` | `--jdinfo` |
| `DebugAttachProcess` | `MainApp/AppCommandLineArgs.cs:51` | `-pn`/`--process-name` |
| `ExtraExtensionDirectory` | `MainApp/AppCommandLineArgs.cs:52` | `--extension-directory` |
| `HasArgument(string)` | `MainApp/AppCommandLineArgs.cs:264` | user-args lookup |
| `GetArgumentValue(string)` | `MainApp/AppCommandLineArgs.cs:266` | user-args value |
| `GetArguments()` | `MainApp/AppCommandLineArgs.cs:271` | all user-args |

### `MainApp/AppWindow.cs`

| Member | Line | Summary |
|---|---:|---|
| `AppWindow` (ctor) | `MainApp/AppWindow.cs:1` | `[ImportingConstructor]` w/ all dependencies |
| `AppWindow.InitializeMainWindow()` | `MainApp/AppWindow.cs:1` | constructs `StackedContent` + `MainWindow` + `MainWindowControl` |
| `AppWindow.RefreshToolBar()` | `MainApp/AppWindow.cs:1` | |
| `AppWindow.AddTitleInfo(...)` | `MainApp/AppWindow.cs:1` | |
| `AppWindow.RemoveTitleInfo(...)` | `MainApp/AppWindow.cs:1` | |
| `AppWindow.MainWindowClosing` (event) | `MainApp/AppWindow.cs:1` | |
| `AppWindow.MainWindowClosed` (event) | `MainApp/AppWindow.cs:1` | |

### `MainApp/MainWindowControl.cs`

| Member | Line | Summary |
|---|---:|---|
| `MainWindowControl` ctor | `MainApp/MainWindowControl.cs:1` | dock layout: left/right/top/bottom + horizontal/vertical stacked content |
| `MainWindowControlState` | `MainApp/MainWindowControl.cs:9` | serialized state |

### `MainApp/DsLoaderService.cs`

| Member | Line | Summary |
|---|---:|---|
| `DsLoaderService` ctor | `MainApp/DsLoaderService.cs:1` | `[ImportMany] IEnumerable<Lazy<IDsLoader, IDsLoaderMetadata>>` |
| `DsLoaderService.Initialize(...)` | `MainApp/DsLoaderService.cs:1` | splash-screen loader driver |
| `DsLoaderService.OnAppLoaded` (event) | `MainApp/DsLoaderService.cs:1` | raised when all `IDsLoader`s are done |

### `Extension/ExtensionService.cs`

| Member | Line | Summary |
|---|---:|---|
| `ExtensionService.LoadExtensions(Collection<ResourceDictionary>)` | `Extension/ExtensionService.cs:1` | merges `IExtension.MergedResourceDictionaries` |
| `ExtensionService.NotifyExtensions(ExtensionEvent, object?)` | `Extension/ExtensionService.cs:1` | broadcast to all `IExtension`s |

### `Documents/DsDocumentService.cs`

| Member | Line | Summary |
|---|---:|---|
| `DsDocumentService.GetDocuments()` | `Documents/DsDocumentService.cs:1` | list of `IDsDocument` |
| `DsDocumentService.Add(IDsDocument)` | `Documents/DsDocumentService.cs:1` | guarded by `ReaderWriterLockSlim` |
| `DsDocumentService.DisableAssemblyLoad()` | `Documents/DsDocumentService.cs:1` | `IDisposable` guard |
| `DsDocumentService.CollectionChanged` (event) | `Documents/DsDocumentService.cs:1` | |
| `DsDocumentService.AssemblyResolver` | `Documents/DsDocumentService.cs:1` | |

### `Documents/Tabs/DocumentTabService.cs`

| Member | Line | Summary |
|---|---:|---|
| `DocumentTabService` ctor | `Documents/Tabs/DocumentTabService.cs:1` | `[ImportingConstructor]` |
| `DocumentTabService.DocumentTreeView` | `Documents/Tabs/DocumentTabService.cs:1` | |
| `DocumentTabService.TabGroupService` | `Documents/Tabs/DocumentTabService.cs:1` | |
| `DocumentTabService.SortedTabs` | `Documents/Tabs/DocumentTabService.cs:1` | |
| `DocumentTabService.VisibleFirstTabs` | `Documents/Tabs/DocumentTabService.cs:1` | |
| `DocumentTabService.DocumentTreeView_NodeActivated(...)` | `Documents/Tabs/DocumentTabService.cs:1` | main entry for tab creation |
| `DocumentTabService.ActiveTab` | `Documents/Tabs/DocumentTabService.cs:1` | |

### `Decompiler/DecompilerService.cs`

| Member | Line | Summary |
|---|---:|---|
| `DecompilerService.AllDecompilers` | `Decompiler/DecompilerService.cs:1` | all `IDecompiler`s |
| `DecompilerService.Decompiler` | `Decompiler/DecompilerService.cs:1` | the active one |
| `DecompilerService.DecompilerChanged` (event) | `Decompiler/DecompilerService.cs:1` | |
| `DecompilerService.Find(Guid)` | `Decompiler/DecompilerService.cs:1` | |
| `DecompilerService.FindOrDefault(Guid)` | `Decompiler/DecompilerService.cs:1` | |

### `Search/SearchService.cs` + `Search/DocumentSearcher.cs` + `Search/DocumentSearcherProvider.cs`

| Member | Line | Summary |
|---|---:|---|
| `DocumentSearcher.Start(IEnumerable<DsDocumentNode>)` | `Search/DocumentSearcher.cs:1` | search by document tree |
| `DocumentSearcher.Start(IEnumerable<SearchTypeInfo>)` | `Search/DocumentSearcher.cs:1` | search by type info |
| `DocumentSearcher.Cancel()` | `Search/DocumentSearcher.cs:1` | |
| `DocumentSearcher.OnSearchCompleted` (event) | `Search/DocumentSearcher.cs:1` | |
| `DocumentSearcher.OnNewSearchResults` (event) | `Search/DocumentSearcher.cs:1` | |
| `DocumentSearcher.TooManyResults` | `Search/DocumentSearcher.cs:1` | cancellation signal |
| `FilterSearcher.FilterAsync(...)` | `Search/FilterSearcher.cs:1` | walks trees, applies comparer |
| `SearchControlVM.StartSearch()` | `Search/SearchControlVM.cs:1` | entry from the search box |

## 7.2 `dnSpy.Contracts.DnSpy` (interface-only)

### `App/IAppWindow.cs`, `App/IAppCommandLineArgs.cs`

(See §7.1 entries above.)

### `Documents/IDsDocumentService.cs`

- `IDsDocument[] GetDocuments()`
- `IDisposable DisableAssemblyLoad()`
- `event CollectionChanged`
- `IAssemblyResolver AssemblyResolver`

### `Documents/Tabs/IDocumentTabService.cs`

- `IDocumentTreeView DocumentTreeView`
- `ITabGroupService TabGroupService`
- `IEnumerable<IDocumentTab> SortedTabs`

### `Tabs/ITabGroupService.cs`

- `IEnumerable<ITabGroup> TabGroups`
- `ITabGroup? ActiveTabGroup`
- `bool IsHorizontal`
- `ITabGroup Create()`
- `void Close(ITabGroup)`

### `Extension/IExtension.cs`

- `ExtensionInfo ExtensionInfo`
- `IEnumerable<string> MergedResourceDictionaries`
- `void OnEvent(ExtensionEvent, object?)`
- `[ExportExtension]` — `[MetadataAttribute, Export(typeof(IExtension))]`

### `Decompiler/IDecompilerService.cs`

- `IEnumerable<IDecompiler> AllDecompilers`
- `IDecompiler Decompiler`
- `event DecompilerChanged`
- `IDecompiler? Find(Guid)`
- `IDecompiler FindOrDefault(Guid)`

### `Decompiler/IDecompiler.cs` (in `dnSpy.Contracts.Logic`)

- `DecompilerSettingsBase Settings`
- `string ContentTypeString`
- `string GenericNameUI` / `string UniqueNameUI`
- `double OrderUI`
- `Guid GenericGuid` / `Guid UniqueGuid`
- `string FileExtension`
- `string? ProjectFileExtension`
- `void Decompile(MethodDef, IDecompilerOutput, DecompilationContext)`
- `void WriteName(...)`, `void WriteType(...)`

### `Search/IDocumentSearcher.cs`

- `bool TooManyResults`
- `bool SyntaxHighlight`
- `IDecompiler Decompiler`
- `ISearchResult? SearchingResult`
- `void Start(...)` (overloads)
- `void Cancel()`
- `event OnSearchCompleted`
- `event OnNewSearchResults`

### `Search/SearchComparers.cs`

- `RegExSearchComparer`
- `AndSearchComparer`
- `OrSearchComparer`
- literal variants

### `Command/IWpfCommandService.cs` / `IWpfCommands.cs`

- `IWpfCommandService.Register(...)`, `GetCommand(...)`, `Remove(...)`
- `IWpfCommands` — registry keyed by `Guid`

### `Settings/ISettingsService.cs`

- `XmlSettingsReader.Read()`
- `XmlSettingsWriter.Write()`
- `ISettingsSection`

### `MVVM/`

- `RelayCommand` — `MVVM/RelayCommand.cs`
- `ListVM` / `EnumVM` / `DataFieldVM` — VM bases

### `ETW/DnSpyEventSource.cs`

- `StartupStart` / `StartupStop` events

### `Menus/IMenuService.cs` etc.

- `IMenuItem`, `IMenuItemProvider`, `IContextMenuProvider`

## 7.3 `dnSpy.Contracts.Debugger*` (debugger contracts)

### `Debugger/DbgManager.cs`

- `DbgDispatcher Dispatcher`
- Events: `Message`, `MessageProcessCreated`, `MessageRuntimeCreated`, `MessageAppDomainLoaded`, `MessageModuleLoaded`, `MessageThreadCreated`, `MessageExceptionThrown`, `MessageEntryPointBreak`, `MessageProgramMessage`
- `void Start(DebugProgramOptions)`, `void Terminate()`, `void Break()`, `void Continue()`

### `Debugger/Engine/DbgEngine.cs`

- `DbgStartKind StartKind`
- `DbgEngineRuntimeInfo RuntimeInfo`
- `string[] DebugTags`, `string[] Debugging`
- `void Start(DebugProgramOptions)`
- `event Message`
- `DbgInternalRuntime CreateInternalRuntime(DbgRuntime)`
- `void OnConnected(DbgObjectFactory, DbgRuntime)`
- `void Stop()`

### `Debugger/DbgRuntime.cs` / `DbgProcess.cs` / `DbgThread.cs` / `DbgModule.cs` / `DbgAppDomain.cs` / `DbgObject.cs`

- live debugger state with `DbgObject.GetOrCreateData<T>()` extension hook

### `Contracts.Debugger.DotNet/DbgDotNetInternalRuntime.cs` etc.

- .NET-flavored internals

### `Contracts.Debugger.DotNet.CorDebug/CorDebugStartDebuggingOptions.cs`

- engine-specific options

## 7.4 `Extensions/dnSpy.Debugger`

### `DbgManagerImpl` (sealed partial class) — `Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs:34`

- `Message` (event override), `MessageProcessCreated`/`Exited`, `MessageRuntimeCreated`/`Exited`, `MessageAppDomainLoaded`/`Unloaded`, `MessageModuleLoaded`/`Unloaded`, `MessageThreadCreated`/`Exited`, `MessageExceptionThrown`, `MessageEntryPointBreak`, `MessageProgramMessage`, `MessageBoundBreakpoint`, `MessageProgramBreak`, `MessageStepComplete`, `MessageSetIPComplete`, `MessageUserMessage`, `MessageBreak`, `MessageAsyncProgramMessage` (line 37-57)
- `Dispatcher` override (line 157)
- `Processes` (line 161), `ProcessesChanged` event (line 160)
- `IsDebugging` / `IsDebuggingChanged` (lines 169-170)
- `DelayedIsRunningChanged` / `IsRunningChanged` / `IsRunning` (lines 190-192)
- `DebugTags` / `DebugTagsChanged` (lines 214-215)
- Helper partials: `BoundBreakpointsManager`, `BreakAllHelper`, `CurrentObjects`, `ProcessKey`, `Steppers`, `StopDebuggingHelper`, `TagsCollection`

### `DbgEngineImpl` (abstract partial) — `Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgEngineImpl.cs:1`

- `StartKind`, `DebugTags`, `Message` (event)
- partial files: `DbgEngineImpl.Breakpoints.cs`, `DbgEngineImpl.Evaluation.cs`, `DbgEngineImpl.ModuleDef.cs`, `DbgEngineImpl.Threads.cs`, `DbgEngineImplDependencies.cs`

### `AttachableProcessesServiceImpl` / `AttachableProcessImpl` / `Win32CommandLineProvider`

- `Extensions/dnSpy.Debugger/dnSpy.Debugger/Attach/`
- process attach by PID / process-name / `--jdinfo` JIT-debug-info-token

### `DbgCallStackServiceImpl` / `DbgStackFrameImpl` / `DbgStackWalkerImpl`

- `Extensions/dnSpy.Debugger/dnSpy.Debugger/CallStack/`

## 7.5 `Extensions/dnSpy.Debugger.DotNet.CorDebug`

### `DbgEngineImpl` (CorDebug) — `Extensions/dnSpy.Debugger.DotNet.CorDebug/Impl/DbgEngineImpl.cs:53`

- `abstract partial class DbgEngineImpl : DbgEngine, IClrDacDebugger`
- `StartKind`, `DebugTags`, `Message` (event)
- `ClrDacRunning` / `ClrDacPaused` / `ClrDacTerminated` events
- `DebuggerThread`, `ObjectFactory`, `clrDac`, `stackFrameData`, `DmdDispatcher`, `RawMetadataService`
- `internalRuntime`
- `CheckCorDebugThread()`, `VerifyCorDebugThread()`, `InvokeCorDebugThread<T>(...)`, `CorDebugThread(Action)`
- `DebuggeeVersion`, `IsPaused`
- `GetMessageFlags(bool pause = false)`
- `RaiseModulesRefreshed(DbgModule)`, `GetDynamicModuleHelper(DnModule)`
- `TryGetThread(CorThread?)`, `TryGetModule(CorModule?)`
- Partial files: `DbgEngineImpl.Breakpoints.cs`, `DbgEngineImpl.Evaluation.cs`, `DbgEngineImpl.ModuleDef.cs`, `DbgEngineImpl.Threads.cs`
- `DbgModuleData` (sealed class, line 480)
- `GetModuleId(DbgModule)`, `TryGetDnModuleAndVersion(...)`, `TryGetDnModule(...)`
- `GetDynamicMetadata_EngineThread(DbgModule)`, `TryGetModuleId(DbgModule)`

### `DbgEngineProviderImpl` — `Impl/DbgEngineProviderImpl.cs`

- `DbgEngine Create(...)` — instantiates `CorDebugEngineImpl`

### `DbgCorDebugInternalRuntimeImpl`

- `Impl/Evaluation/DbgCorDebugInternalRuntimeImpl.cs`
- wraps `ICorDebug` runtime

### `DbgDotNetValueImpl` / `DbgCorValueHolder`

- `Impl/Evaluation/`
- expression-evaluation value holders

### `DmdEvaluatorImpl`

- `Impl/Evaluation/DmdEvaluatorImpl.cs`
- DMD-based Roslyn expression evaluator

### `DotNetDbgEngineImpl` / `DotNetFrameworkDbgEngineImpl` / `DotNetDbgProcessStarter`

- `Impl/`
- .NET / .NET Framework / process start

### `CorDebugAttachToProgramOptions` / `DotNetAttachToProgramOptions` / `DotNetFrameworkAttachToProgramOptions`

- `Impl/Attach/`

### `TheExtension` — `TheExtension.cs`

- `[ExportExtension] sealed class TheExtension : IExtension`

## 7.6 `Extensions/dnSpy.Scripting.Roslyn`

### `TheExtension.cs`

- `[ExportExtension] sealed class TheExtension : IExtension`

### `Common/ScriptControl.xaml*` + `Common/ScriptControlVM.cs` (~300+ LoC)

#### `ScriptControlVM` (abstract) — `Common/ScriptControlVM.cs:59`

- Implements `IReplCommandHandler, IScriptGlobalsHelper`
- `ResetCommand`, `ClearCommand`, `SaveCommand`, `HistoryPreviousCommand`, `HistoryNextCommand`
- `CanReset`, `CanSaveText`, `CanSaveCode`, `CanClearScreen`
- `SaveText()`, `SaveCode()`, `Reset(bool loadConfig = true)`
- `WordWrap` (property)
- `ReplEditor` (IReplEditor)
- `ScriptCommands`
- `OnVisible()`
- `IsCommand(string text)`

### `Common/UserScriptOptions` (sealed) — `Common/ScriptControlVM.cs:52`

- `References`, `Imports`, `LibPaths`, `LoadPaths`

### `Common/ExecState` (sealed) — `Common/ScriptControlVM.cs:222`

- `ScriptOptions? ScriptOptions`

### `CSharp/`

- `CSharpContent` — `CSharp/CSharpContent.cs`
- `CSharpControlVM` — `CSharp/CSharpControlVM.cs`
- `CSharpToolWindowContent` — `CSharp/CSharpToolWindowContent.cs`
- `CSharpReplSettingsImpl` — `CSharp/CSharpReplSettingsImpl.cs`

### `Common/`

- `HelpCommand` — `#help`
- `ResetCommand` — `#reset`
- `ClearCommand` — `#cls`
- `Commands.cs` — REPL command routing
- `RespFileUtils` / `ResponseFileReader` — parse `*.Interactive.rsp`
- `CachedWriter` — output capture
- `RoslynReplCommandTargetFilter` / `RoslynReplCommandTargetFilterProvider`
- `RoslynReplCommandInfoProvider`
- `RoslynReplEditorUtils`
- `ScriptGlobals` — exposes dnSpy internals

## 7.7 `Extensions/dnSpy.Analyzer`

### `TheExtension.cs`

- `[ExportExtension] sealed class TheExtension : IExtension`

### `AnalyzerService` (public class) — `AnalyzerService.cs`

#### `public IEnumerable<AnalyzerTreeNodeData> GetResults(DsDocumentNode node)`

- **位置**: `AnalyzerService.cs:1`
- **可见性**: public
- **简要说明**: runs registered `IAnalyzer`s on the node

### `AnalyzerSettings` — `AnalyzerSettings.cs`

- persisted options

### `AnalyzerToolWindowContent` — `AnalyzerToolWindowContent.cs`

- the analyzer tool window

### `TreeNodes/` (~40 files, one per analyzer finding)

- `EntityNode.cs` (+ derived `MethodNode`, `TypeNode`, `FieldNode`, `EventNode`, `PropertyNode`, `AssemblyNode`)
- `BaseTypesTreeNode.cs` / `DerivedTypesTreeNode.cs`
- `AttributeAppliedToNode.cs`
- `EventFiredByNode.cs` / `EventAccessorNode.cs` / `EventOverriddenNode.cs` / `EventOverridesNode.cs`
- `FieldAccessNode.cs`
- `InterfaceEventImplementedByNode.cs` / `InterfaceMethodImplementedByNode.cs` / `InterfacePropertyImplementedByNode.cs`
- `MethodOverriddenNode.cs` / `MethodOverridesNode.cs` / `MethodUsedByNode.cs` / `MethodUsesNode.cs`
- `ModuleNode.cs`
- `PropertyAccessorNode.cs` / `PropertyOverriddenNode.cs` / `PropertyOverridesNode.cs`
- `AnalyzerTreeNodeData.cs` (base)
- `AsyncFetchChildrenHelper.cs`
- `ComUtils.cs`
- `Helpers.cs`
- `IAnalyzerTreeNodeDataContext.cs` / `IAsyncCancellable.cs`
- `Commands.cs` / `ContentTypeDefinitions.cs` / `TreeTraversal.cs`

## 7.8 `Extensions/dnSpy.AsmEditor`

### `TheExtension.cs`

- `[ExportExtension] sealed class TheExtension : IExtension`

### Sub-directories (23)

- `Assembly/` — module-level edits
- `Commands/` — command registry
- `Compiler/` — Roslyn compilation glue
- `Converters/` — value converters
- `DnlibDialogs/` — dialog helpers
- `Event/` — event member edits
- `Field/` — field member edits
- `Hex/` — hex-aware edits
- `Method/` — method body edits (largest sub-directory)
- `MethodBody/` — IL body editor
- `Module/` — module-level metadata edits
- `Namespace/` — namespace edits
- `Property/` — property edits
- `Resources/` — string + resource edits
- `SaveModule/` — save changes back via dnlib
- `Themes/` — AsmEditor XAML themes
- `Types/` — type-declaration edits
- `UndoRedo/` — undo/redo stack
- `Utilities/` — helpers
- `ViewHelpers/` — VM helpers
- (etc.)

## 7.9 `Extensions/dnSpy.BamlDecompiler`

### `TheExtension.cs`

- `[ExportExtension] sealed class TheExtension : IExtension`

### `BamlDecompiler` (public class) — `BamlDecompiler.cs`

- parses BAML records into a structured form

### `BamlDisassembler` / `BamlElement` / `BamlResourceElementNode` / `BamlResourceNodeProvider`

- low-level BAML parser

### `XamlDecompiler` / `XamlOutputCreator` / `XamlOutputOptionsProvider` / `XmlnsDictionary` / `XamlContext`

- BAML -> XAML emission

### `BamlSettings` / `BamlSettings.xaml`

- settings page

### `IRewritePass` / `Handlers/` / `IHandlers.cs` / `Rewrite/` / `RecursionCounter`

- rewrite passes for field references, type lookups, etc.

### `MenuCommands.cs`

- context-menu entries

## 7.10 `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core`

### `CSharp/CSharpDecompiler.cs` (525 LoC)

#### `CSharpDecompiler` (sealed class) — `CSharp/CSharpDecompiler.cs`

- `: DecompilerBase`
- `public override DecompilerSettingsBase Settings => langSettings`
- `public override void Decompile(MethodDef, IDecompilerOutput, DecompilationContext)`
- `public override void Decompile(PropertyDef, ...)`
- `public override void Decompile(FieldDef, ...)`
- `public override void Decompile(EventDef, ...)`
- `public override void Decompile(TypeDef, ...)`
- `void RunTransformsAndGenerateCode(ref BuilderState, IDecompilerOutput, DecompilationContext, IAstTransform?)`

### `BuilderState` / `BuilderCache` / `ThreadSafeObjectPool`

- `CSharp/` — thread-safe builder pooling

### `AssemblyInfoTransform` / `DecompileTypeMethodsTransform` / `DecompilePartialTransform`

- `CSharp/` — legacy NRefactory AST transforms

### `VisualBasic/VBDecompiler.cs` / `VBTextOutputFormatter.cs` / `ILSpyEnvironmentProvider.cs`

- VB backend

### `IL/ILDecompiler.cs` / `ILDecompilerUtils.cs`

- IL backend (flat + structured modes)

### `Settings/`

- `DecompilerSettingsService`
- `ILSettings`
- `CSharpVBDecompilerSettings`
- `ILDecompilerSettings`
- `ILAstDecompilerSettings`

## Coverage summary

| Bucket | Function entries |
|---|---:|
| Main WPF app (`dnSpy/`) | ~50 |
| Contracts (`dnSpy.Contracts.DnSpy`) | ~30 |
| Debugger contracts (`dnSpy.Contracts.Debugger*`) | ~25 |
| Generic debugger (`dnSpy.Debugger`) | ~30 |
| CorDebug (`dnSpy.Debugger.DotNet.CorDebug`) | ~25 |
| Roslyn REPL | ~25 |
| Analyzer | ~40 (one per node kind) |
| AsmEditor | ~30 (catalogued) |
| ILSpy decompiler wrapper | ~10 |
| BAML decompiler | ~10 |
| **Total catalogued in 07 + 08** | **~275 entries** |