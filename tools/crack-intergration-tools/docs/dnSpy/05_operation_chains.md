# 05 — Operation Chains

This document enumerates 12 end-to-end operation chains. Each chain has an input contract, a numbered sequence of file:line references, and a mermaid diagram. The chains come from the inventory report (`/tmp/ilspy-dnspy-inventory/dnSpy.md` §6) and cross-reference [09_callstacks.md](./09_callstacks.md) for the text-based view.

**Chain index:**

| # | Name | Input | Trigger |
|---|---|---|---|
| 1 | Decompile a .NET assembly to a tab | user drops `Foo.dll` on the explorer | `DocumentTreeView.NodeActivated` |
| 2 | Debugger attach (CorDebug) | user picks `Debug > Attach to Process…` | `DbgManager.Start` |
| 3 | Plugin (extension) loading | `*.x.dll` next to `dnSpy.exe` | `App.InitializeMEF` |
| 4 | WPF main window / MVVM | MEF composition complete | `App.OnStartup` |
| 5 | Document / tab management | user clicks a member node | `DocumentTreeView.NodeActivated` |
| 6 | Decompile + edit (Roslyn round-trip) | user edits + clicks Apply | `AsmEditor` save |
| 7 | Roslyn REPL | user types `1 + 2` in C# Interactive | `ScriptControlVM.Submit` |
| 8 | Multi-language decompilation | user changes the language dropdown | `DecompilerService.Decompiler` setter |
| 9 | Static analysis | right-click -> Analyze | `AnalyzerService.GetResults` |
| 10 | Search | user opens Search window | `DocumentSearcherProvider.Create` |
| 11 | BAML -> XAML | user opens a .baml resource | `BamlDecompiler.Decompile` |
| 12 | IL interpreter (no-process debugging) | user picks "Run with IL Interpreter" | `ILVM.Execute` |

---

## Chain 1 — Decompile a .NET assembly to a tab

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant OpenDocs as OpenDocumentsHelper
    participant DocLoader as DefaultDsDocumentLoader
    participant DocSvc as DsDocumentService
    participant TreeView as DocumentTreeView
    participant TabSvc as DocumentTabService
    participant Factory as IDocumentTabContentFactory
    participant Decompiler as IDecompiler
    participant Output as IDecompilerOutput

    User->>OpenDocs: drag Foo.dll onto explorer
    OpenDocs->>DocLoader: Load(filename)
    DocLoader-->>OpenDocs: DsDocument
    OpenDocs->>DocSvc: Add(document)
    DocSvc->>TreeView: CollectionChanged
    TreeView->>TreeView: build nodes via IDocumentTreeNodeProvider
    User->>TreeView: click MethodDef
    TreeView->>TabSvc: NodeActivated
    TabSvc->>Factory: TryCreateAsync(node)
    Factory->>Decompiler: Decompile(MethodDef, output, ctx)
    Decompiler->>Output: WriteName, WriteType, ...
    Output-->>Factory: color-stamped text
    Factory-->>TabSvc: new tab content
    TabSvc->>TreeView: ActiveTabContent = tab
```

Steps:

1. `OpenDocumentsHelper.OpenDocuments(documentTreeView, window, mruList, files, false)` (`MainApp/App.xaml.cs:586`).
2. `DefaultDsDocumentLoader.Load(filename)` creates a `DsDocument` (PE/pe-image/bundle).
3. `DsDocumentService.Add(document)` — guarded by `DisableAssemblyLoad()` pattern; uses `ReaderWriterLockSlim` for perf.
4. `AssemblyResolver` resolves referenced assemblies (NuGet / shared framework / GAC).
5. `DocumentTreeView.DocumentService.CollectionChanged` fires; tree nodes are auto-built via `IDocumentTreeNodeProvider`s.
6. `IDecompilerService.Decompiler` (e.g. C#) decompiles nodes on demand via `IDocumentTreeNodeData.OnRefresh`.
7. `DocumentTabService` opens a tab in the active tab group via `TabGroupService.ActiveTabGroup.ActiveTabContent`.

Output: New tab with C# source for the activated member.

---

## Chain 2 — Debugger attach (CorDebug)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Attachable as AttachableProcessesServiceImpl
    participant DbgMgr as DbgManagerImpl
    participant Engine as DbgEngineImpl
    participant CorDebug as ICorDebug
    participant ToolWindows as ToolWindows

    User->>Attachable: Debug > Attach to Process
    Attachable->>User: process list (PID, arch, title)
    User->>Attachable: select PID 1234
    Attachable->>DbgMgr: Start(DebugProgramOptions)
    DbgMgr->>Engine: DbgEngineProviderImpl.Create + Start(options)
    Engine->>CorDebug: CreateProcess / DebugActiveProcess
    CorDebug-->>Engine: ICorDebugManagedCallback events
    Engine->>Engine: OnConnected(objectFactory, runtime)
    Engine-->>DbgMgr: MessageRuntimeCreated + MessageProcessCreated + MessageModuleLoaded
    DbgMgr->>ToolWindows: dispatch events to UI
    ToolWindows-->>User: CallStack / Locals / Modules / Threads populate
```

Steps:

1. `AttachableProcessesServiceImpl` enumerates Win32 processes (with icons, architectures, titles).
2. `AttachableProcessImpl` -> `DotNetAttachToProgramOptions.Create(pid)`.
3. `DbgManager.Start(DebugProgramOptions)` (`Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs`).
4. `DbgEngineProviderImpl.Create(manager, options)` instantiates `DotNetDbgEngineImpl` -> `DbgEngineImpl` (CorDebug).
5. `DbgEngineImpl.Start(options)` (`dbgEngineImpl.cs:80`):
   - Launches `CoreCLR` / `CLR` hosting via `DotNetDbgProcessStarter`.
   - Calls `ICorDebug.CreateProcess` / `DebugActiveProcess`.
   - Subscribes to `ICorDebugManagedCallback` events.
6. `OnConnected(objectFactory, runtime)` -> creates `DbgRuntime`, `DbgProcess`, `DbgThread`, `DbgModule`s.
7. `MessageRuntimeCreated` / `MessageProcessCreated` / `MessageModuleLoaded` events fire on the dispatcher thread.
8. `DbgCallStackServiceImpl`, `LocalsToolWindow`, `CallStackToolWindow`, `ModulesToolWindow`, `ThreadsToolWindow`, `WatchToolWindow` all update via MEF-imported `IMessageProcessor`s.
9. When a breakpoint hits, `DbgBoundCodeBreakpointImpl.Hit()` -> `BreakAllHelper.Break()` -> `MessageEntryPointBreak` -> UI highlights active frame.

Output: Debugger UI populated; can set breakpoints, step, inspect locals.

---

## Chain 3 — Plugin (extension) loading

```mermaid
sequenceDiagram
    autonumber
    participant StartUp as StartUpClass
    participant App
    participant MEF as VS-MEF
    participant ExtSvc as ExtensionService
    participant Exts as IExtension

    StartUp->>App: new App(readSettings, sw).Run()
    App->>App: initializeMEFTask = Task.Run(InitializeMEF)
    App->>MEF: GetAssemblies + LoadExtensionAssemblies
    MEF->>MEF: enumerate *.x.dll in BinDirectory + Extensions\
    MEF->>MEF: CanLoadExtension(file): reads .xml config + asm check
    MEF->>MEF: Assembly.LoadFrom(file) -> LoadedExtension
    MEF->>MEF: AttributedPartDiscoveryV1 -> ComposableCatalog.Create
    MEF-->>App: ExportProvider
    App->>ExtSvc: LoadExtensions(Resources.MergedDictionaries)
    ExtSvc->>Exts: IAutoLoaded.Before/After/Loaded events
```

Steps:

1. `StartUpClass.Main` -> `new App(readSettings, sw).Run()` (`MainApp/StartUpClass.cs:21`).
2. `App` ctor calls `initializeMEFTask = Task.Run(() => InitializeMEF(readSettings, useCache: readSettings))` (`MainApp/App.xaml.cs:114`).
3. `InitializeMEF` -> `GetAssemblies()` -> `LoadExtensionAssemblies()` -> `GetExtensionFiles(BinDirectory)` enumerates `*.x.dll` in `BinDirectory`, `Extensions\`, and each subdir of `Extensions\` (also from `args.ExtraExtensionDirectory`).
4. `CanLoadExtension(file)` reads `<file>.xml` `ExtensionConfig` (OS / Framework / App version check); `CanLoadExtension(asm)` checks public key + minimum reference version 5.0.0.0.
5. `Assembly.LoadFrom(file)` -> `loadedExtensions.Add(new LoadedExtension(asm))`.
6. `assembly[]` passed to `AttributedPartDiscoveryV1` (`App.xaml.cs:155`).
7. `ComposableCatalog.Create(resolver).AddParts(parts).CreateExportProvider()` returns VS-MEF `ExportProvider`.
8. `extensionService.LoadExtensions(Resources.MergedDictionaries)` merges plugin `MergedResourceDictionaries` XAML files.
9. `IAutoLoaded.BeforeExtensions` / `.AfterExtensions` / `.AfterExtensionsLoaded` triggered (via `IAutoLoadedMetadata`).

Output: Extension's `[Export]` types visible via MEF; `[ExportExtension] IExtension.OnEvent` called with `Loaded`.

---

## Chain 4 — WPF main window / MVVM

```mermaid
sequenceDiagram
    autonumber
    participant StartUp as StartUpClass
    participant App
    participant MEF as ExportProvider
    participant AppWindow as AppWindow
    participant Culture as CultureService
    participant Loader as DsLoaderService
    participant ExtSvc as ExtensionService

    StartUp->>App: new App(readSettings, sw).Run()
    App->>App: OnStartup awaits initializeMEFTask
    App->>App: if SingleInstance -> SwitchToOtherInstance (WM_COPYDATA 0x11C9B152)
    App->>Culture: Initialize(args) -- set Thread.CurrentUICulture
    App->>MEF: GetExportedValue<IDpiService>()
    App->>MEF: GetExportedValue<AppWindow>()
    AppWindow->>AppWindow: InitializeMainWindow -> StackedContent + MainWindow + MainWindowControl
    App->>Loader: OnAppLoaded += DsLoaderService_OnAppLoaded
    App->>ExtSvc: LoadExtensions(Resources.MergedDictionaries)
    App->>AppWindow: win.Show()
    App->>App: DsLoaderService.OnAppLoaded -> HandleAppArgs(args) + HandleAppArgs2(args)
```

Steps:

1. `OnStartup(StartupEventArgs)` blocks on `initializeMEFTask.GetAwaiter().GetResult()` (`App.xaml.cs:521`).
2. If `args.SingleInstance && !AppSettingsImpl.AllowMoreThanOneInstance`, `SwitchToOtherInstance()` enumerates windows and forwards args via `WM_COPYDATA` (header `0x11C9B152`).
3. `cultureService.Initialize(args)` — sets `Thread.CurrentThread.CurrentUICulture` per `--culture`.
4. `exportProvider.GetExportedValue<IDpiService>()` to init DPI early.
5. `appWindow = exportProvider.GetExportedValue<AppWindow>()` (created by `[ImportingConstructor]` w/ all dependencies).
6. `appWindow.InitializeMainWindow()` constructs `StackedContent` (toolbar / center / status), `MainWindow` (`MetroWindow`), `MainWindowControl` (dock layout).
7. `dsLoaderService.OnAppLoaded += DsLoaderService_OnAppLoaded`; `extensionService.LoadExtensions(Resources.MergedDictionaries)`; `win.Show()`.
8. `DsLoaderService.OnAppLoaded` -> `DnSpyEventSource.Log.StartupStop()`; `HandleAppArgs(args)` — applies `--language`, `--new-tab`, `--full-screen`, opens files via `OpenDocumentsHelper`.
9. `HandleAppArgs2(args)` dispatches to all `IAppCommandLineArgsHandler` exports in `Order` ascending.

Output: dnSpy main window visible; all tool windows docked per saved state.

---

## Chain 5 — Document / tab management

```mermaid
flowchart TD
    A[User clicks MethodDef node] --> B[DocumentTreeView.NodeActivated]
    B --> C[DocumentTabService.DocumentTreeView_NodeActivated]
    C --> D{switch on node type}
    D -- AssemblyReferenceNode --> E[resolve reference, navigate tree]
    D -- DerivedTypeNode / BaseTypeNode --> F[select target type]
    D -- TypeReferenceNode / ... --> G[resolve and select]
    D -- default --> H[ActiveTabContentImpl -> TabContentImpl.Show]
    H --> I[IDocumentTabContentFactory.TryCreateAsync]
    I --> J{which factory?}
    J -- default --> K[DefaultDocumentTabContentProvider]
    J -- Roslyn edit --> L[IReferenceDocumentTabContentProvider]
    K --> M[DocumentTreeNodeDecompiler.DecompileAsync]
    L --> N[RoslynLanguageCompiler edit round-trip]
    M --> O[IDecompiler.Decompile(MethodDef, IDecompilerOutput, ctx)]
    N --> O
    O --> P[IDecompilationCache.GetOrCreateAsync]
    P --> Q[TabGroupService.ActiveTabGroup.ActiveTabContent = impl]
    Q --> R[TabSelectionChanged raised]
```

Steps:

1. `DocumentTreeView.NodeActivated` raises `DocumentTreeNodeActivatedEventArgs`.
2. `DocumentTabService.DocumentTreeView_NodeActivated` switches on the node type:
   - `AssemblyReferenceNode` -> resolves the reference, navigates tree
   - `DerivedTypeNode` / `BaseTypeNode` -> selects the target type
   - `TypeReferenceNode` / `MethodReferenceNode` / `PropertyReferenceNode` / `EventReferenceNode` / `FieldReferenceNode` -> resolves and selects the target
   - otherwise: `ActiveTabContentImpl` -> `TabContentImpl.Show(impl, nodes)` -> creates new `TabContentImpl` if none; reuses existing tab if same content
3. `IDocumentTabContentFactory.TryCreateAsync(...)` enumerates `IReferenceDocumentTabContentProvider`s (Roslyn-based edits) and `IDefaultDocumentTabContentProvider`s (the default decompile tab) in `Order` ascending.
4. `DocumentTreeNodeDecompiler.DecompileAsync(method/type)` calls `IDecompiler.Decompile(MethodDef, IDecompilerOutput, DecompilationContext)` -> writes to `IDecompilerOutput` (color-aware).
5. `IDecompilationCache.GetOrCreateAsync(...)` memoizes results.
6. `TabGroupService.ActiveTabGroup.ActiveTabContent = impl` -> raises `TabSelectionChanged`.

Output: Decompiled C# / VB / IL visible in the tab; syntax highlighting active.

---

## Chain 6 — Decompile + edit (Roslyn round-trip)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Roslyn as RoslynLanguageCompiler
    participant Compilation as CSharpCompilation
    participant AsmEditor as dnSpy.AsmEditor
    participant Dnlib as dnlib
    participant DocSvc as DsDocumentService

    User->>Roslyn: edit C# method, click Apply
    Roslyn->>Roslyn: SyntaxTree from buffer
    Roslyn->>Compilation: CSharpCompilation.Create with project refs
    Compilation->>Roslyn: Emit PE blob
    Roslyn->>AsmEditor: hand over PE blob
    AsmEditor->>Dnlib: write metadata tokens to original DsDocument
    AsmEditor->>DocSvc: NotifyDocumentCollectionChangedEventArgs
    DocSvc->>User: tree nodes refresh
```

Steps:

1. `RoslynLanguageCompiler` (`dnSpy.Roslyn/Compiler/`) creates a `SyntaxTree` from the editor buffer.
2. `CSharpCompilation.Create(...)` with project references (resolved by `AssemblyResolver`).
3. `Emit` produces a new `PE` blob.
4. `AsmEditor` saves the blob back to the original `DsDocument` (writes metadata tokens via dnlib).
5. `DocumentTreeView.DocumentService.CollectionChanged` raises `NotifyDocumentCollectionChangedEventArgs`; tree nodes refresh.

Output: Compiled assembly updated in-memory.

---

## Chain 7 — Roslyn REPL

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant ScriptCtrl as ScriptControlVM
    participant Roslyn as CSharpScript
    participant Globals as ScriptGlobals
    participant Writer as CachedWriter

    User->>ScriptCtrl: type "1 + 2", press Enter
    ScriptCtrl->>Roslyn: RunAsync(text, ScriptOptions.Default.WithReferences(...).WithImports(...))
    Roslyn-->>ScriptCtrl: ScriptState
    ScriptCtrl->>Globals: expose dnSpy internals (assembly list, debugger)
    ScriptCtrl->>Writer: capture output
    Writer-->>User: print result
```

Steps:

1. `ScriptControl.axaml.cs` -> `ScriptControlVM.Submit(text)` (`Common/ScriptControlVM.cs`).
2. `CSharpScript.RunAsync(text, ScriptOptions.Default.WithReferences(...).WithImports(...))` (`Microsoft.CodeAnalysis.Scripting`).
3. `ScriptState` returned; `ScriptGlobals` exposes dnSpy internals (current assembly list, debugger, ...) to user code.
4. Output captured by `CachedWriter` and `ScriptControl.WriteOutput`.
5. State (globals, references, imports, lib paths) persisted in `ReplSettings`.

Output: Evaluated result printed in REPL; state persists for next submission.

---

## Chain 8 — Multi-language decompilation

```mermaid
flowchart LR
    A[User changes language dropdown] --> B[DecompilerService.Decompiler = newLanguage]
    B --> C[DecompilerChanged event fires]
    C --> D[Tab content invalidates]
    D --> E{which backend?}
    E -- C# --> F[CSharpDecompiler<br/>dnSpy.Decompiler.ILSpy.Core]
    E -- VB --> G[VBDecompiler<br/>dnSpy.Decompiler.ILSpy.Core]
    E -- IL flat --> H[ILDecompiler flat]
    E -- IL structured --> I[ILDecompiler structured]
    F --> J[Tab re-renders]
    G --> J
    H --> J
    I --> J
```

Steps:

1. `DecompilerService.Decompiler = newLanguage` (`DecompilerService.cs`).
2. `DecompilerChanged` event fires; tab content invalidates.
3. Next decompile request calls `IDecompiler.Decompile(...)` on the new backend:
   - `CSharpDecompiler` (NRefactory-based via `dnSpy.Decompiler.ILSpy.Core`) -> `IDecompilerOutput` colored text
   - `VBDecompiler` -> VB.NET text
   - `ILDecompiler` (flat or structured) -> IL text
   - Decompiler GUIDs in `dnSpy.Decompiler.ILSpy.Core/DecompilerConstants`: `LANGUAGE_CSHARP`, `LANGUAGE_CSHARP_ILSPY`, `LANGUAGE_VB`, `LANGUAGE_IL`, etc.

Output: Tab re-renders in the chosen language; selection preserved via `Decompiler.UniqueGuid`.

---

## Chain 9 — Static analysis (Analyzer)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant AnSvc as AnalyzerService
    participant Analyzer as IAnalyzer
    participant ToolWindow as AnalyzerToolWindowContent

    User->>AnSvc: right-click type, Analyze -> Used By
    AnSvc->>Analyzer: GetResults(node)
    Analyzer-->>AnSvc: AnalyzerTreeNodeData stream
    AnSvc->>ToolWindow: Add(node)
    ToolWindow-->>User: tree populates
    User->>ToolWindow: double-click result
    ToolWindow->>User: navigate to that member
```

Steps:

1. `AnalyzerService.GetResults(node)` (`AnalyzerService.cs`) iterates registered `IAnalyzer`s.
2. Each analyzer yields `AnalyzerTreeNodeData` instances (e.g. `MethodUsedByNode`, `BaseTypeTreeNode`, `DerivedTypeTreeNode`, `AttributeAppliedToNode`, `FieldAccessNode`, ...).
3. Nodes are streamed to the analyzer tool window via `AnalyzerToolWindowContent.Add(node)`.
4. Async fetch uses `AsyncFetchChildrenHelper` for expensive resolution (cross-assembly references).
5. Double-clicking a result navigates the assembly explorer to that member (`DocumentTreeView.SelectItems`).

Output: Tree of "used by" / "inherits from" / ... results.

---

## Chain 10 — Search (text / type / method / constant / metadata-token / resource)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant SearchVM as SearchControlVM
    participant Provider as DocumentSearcherProvider
    participant Comparer as SearchComparerFactory
    participant Searcher as DocumentSearcher
    participant Filter as FilterSearcher

    User->>SearchVM: pick "Methods", type "GetCustomer"
    SearchVM->>Provider: DocumentSearcherProvider.Create(searchOptions)
    Provider->>Comparer: SearchComparerFactory.Create(text, caseSensitive, ...)
    Comparer-->>Provider: RegExSearchComparer / AndSearchComparer / OrSearchComparer
    Provider->>Searcher: DocumentSearcher.Start(documents)
    Searcher->>Filter: walk each document's type/method trees
    Filter->>Filter: decompile bodies, apply comparer
    Filter-->>User: SearchResult stream
    User->>Searcher: double-click result
    Searcher->>User: navigate to member
```

Steps:

1. `SearchControlVM.StartSearch()` -> `DocumentSearcherProvider.Create(searchOptions)`.
2. `SearchComparerFactory.Create(searchText, caseSensitive, matchWholeWords, matchAnyWords)` builds `RegExSearchComparer` / `AndSearchComparer` / `OrSearchComparer` / literal variants.
3. `DocumentSearcher.Start(IEnumerable<DsDocumentNode>)` (`Search/DocumentSearcher.cs`).
4. `FilterSearcher` walks each document's type/method trees, decompiles bodies, applies the comparer.
5. `OnNewSearchResults` fires for each batch; `SearchResult` produced; matched source lines highlighted via `SyntaxHighlight`.
6. `TooManyResults` triggers cancellation; `OnSearchCompleted` fires.
7. User double-clicks a result -> navigates to the matching member.

Output: Result list; clicking opens the member in a tab.

---

## Chain 11 — BAML -> XAML

```mermaid
flowchart LR
    A[User opens WPF assembly, selects .baml] --> B[BamlResourceNodeProvider creates nodes]
    B --> C[BamlDecompiler.Decompile(bamlStream)]
    C --> D[BamlDisassembler parses records]
    D --> E[IRewritePass chain via RecursionCounter]
    E --> F[XamlDecompiler.Emit(xamlContext, outputCreator)]
    F --> G[XamlOutputCreator writes to TextEditor]
    G --> H[XmlnsDictionary handles namespaces]
    H --> I[Readable XAML tab]
```

Steps:

1. `BamlResourceNodeProvider` creates `BamlResourceElementNode`s.
2. `BamlDecompiler.Decompile(bamlStream)` parses BAML records (`BamlDisassembler` for IL-style list).
3. `IRewritePass` chain (e.g. field reference resolution, type lookup) applied via `RecursionCounter` to avoid infinite loops.
4. `XamlDecompiler.Emit(xamlContext, outputCreator)` produces XAML.
5. `XamlOutputCreator` writes into the text editor with proper namespace handling (`XmlnsDictionary`).

Output: Readable XAML tab.

---

## Chain 12 — IL interpreter (no-process debugging)

```mermaid
sequenceDiagram
    autonumber
    participant User
    participant Engine as InterpreterEngine
    participant Factory as ILVMFactory
    participant VM as ILVM
    participant Value as ILValue

    User->>Engine: pick method on PE file with no live process, "Run with IL Interpreter"
    Engine->>Factory: ILVMFactory.Create(dmdRuntime)
    Factory->>VM: ILVM instance
    VM->>VM: Execute(method, ...)
    VM->>VM: walk IL byte-by-byte
    VM-->>User: breakpoint hit -> DbgBoundCodeBreakpointImpl.Hit()
    User->>VM: inspect locals
    VM->>Value: read ILValue holders
    Value-->>User: locals/watches
```

Steps:

1. `dnSpy.Debugger.DotNet.Interpreter` engine activates via `DbgEngineProviderImpl.Create`.
2. `ILVMFactory.Create(dmdRuntime)` creates a virtual machine.
3. `ILVM.Execute(method, ...)` walks the IL byte-by-byte.
4. Breakpoints trigger `DbgBoundCodeBreakpointImpl.Hit()` -> standard message pump.
5. Locals/watches read from `ILValue` holders.

Output: Method executed in-process; breakpoints honored; no external runtime needed.