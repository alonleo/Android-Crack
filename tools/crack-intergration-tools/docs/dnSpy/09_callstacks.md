# 09 — Call Stacks

This document gives text-based call stacks for each of the 12 operation chains in [05_operation_chains.md](./05_operation_chains.md). Each stack shows the actual entry function, the major call sites, and the leaf (terminal) call. Line numbers reference the source tree at `/home/leo/文档/android-crack/tools/source-projects/dnSpy/`.

## Stack 1 — Decompile a .NET assembly to a tab

```
[user]
└── drop Foo.dll onto assembly explorer (or pass Foo.dll on CLI)
    └── MainApp/App.xaml.cs:586  OpenDocumentsHelper.OpenDocuments(...)
        └── Documents/DefaultDsDocumentLoader.Load(filename)
            └── creates DsDocument (PE/pe-image/bundle)
        └── Documents/DsDocumentService.cs:103+  Add(document)
            ├── ReaderWriterLockSlim.EnterWriteLock
            └── OnCollectionChanged raised
        └── Documents/AssemblyResolver resolves referenced assemblies (NuGet/shared framework/GAC)
        └── Documents/TreeView/DocumentTreeView  DocumentService.CollectionChanged
            └── IDocumentTreeNodeProvider builds nodes
        └── user clicks MethodDef
            └── DocumentTreeView.NodeActivated raises DocumentTreeNodeActivatedEventArgs
            └── Documents/Tabs/DocumentTabService.cs:1  DocumentTreeView_NodeActivated
                ├── switch on node type:
                │   ├── AssemblyReferenceNode -> resolve ref, navigate tree
                │   ├── DerivedTypeNode / BaseTypeNode -> select target
                │   ├── TypeReferenceNode / MethodReferenceNode / ... -> resolve and select
                │   └── default: TabContentImpl.Show(impl, nodes)
                └── IDocumentTabContentFactory.TryCreateAsync(...)
                    ├── IReferenceDocumentTabContentProvider (Roslyn-based edits)
                    └── IDefaultDocumentTabContentProvider (default decompile tab)
                    └── chosen factory's Create()
                        └── Documents/Tabs/DocumentTreeNodeDecompiler.DecompileAsync(method/type)
                            └── IDecompiler.Decompile(MethodDef, IDecompilerOutput, ctx)
                                └── dnSpy.Decompiler.ILSpy.Core.CSharp.CSharpDecompiler.Decompile
                                    ├── BuilderState (thread-safe via ThreadSafeObjectPool)
                                    ├── RunTransformsAndGenerateCode
                                    ├── AssemblyInfoTransform / DecompileTypeMethodsTransform / DecompilePartialTransform
                                    └── writes to IDecompilerOutput (color-aware)
                                └── IDecompilationCache.GetOrCreateAsync(...)
                        └── Documents/Tabs/TabGroupService.ActiveTabGroup.ActiveTabContent = impl
                            └── raises TabSelectionChanged
```

## Stack 2 — Debugger attach (CorDebug)

```
[user]
└── Debug > Attach to Process
    └── Extensions/dnSpy.Debugger/dnSpy.Debugger/Attach/AttachableProcessesServiceImpl
        └── enumerates Win32 processes (icons, arch, titles)
        └── user picks PID 1234
        └── AttachableProcessImpl -> DotNetAttachToProgramOptions.Create(pid)
            └── Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs:1  DbgManager.Start(DebugProgramOptions)
                └── DbgEngineProviderImpl.Create(manager, options)  (Extensions/dnSpy.Debugger.DotNet.CorDebug/Impl/)
                    └── returns CorDebugEngineImpl
                └── CorDebugEngineImpl.Start(options)
                    ├── launches CoreCLR/CLR hosting via DotNetDbgProcessStarter
                    ├── ICorDebug.CreateProcess / DebugActiveProcess
                    └── subscribe to ICorDebugManagedCallback events
                └── OnConnected(objectFactory, runtime)
                    └── creates DbgRuntime, DbgProcess, DbgThread, DbgModule(s)
                └── MessageRuntimeCreated/MessageProcessCreated/MessageModuleLoaded events fire on dispatcher thread
                └── DbgCallStackServiceImpl, LocalsToolWindow, CallStackToolWindow,
                    ModulesToolWindow, ThreadsToolWindow, WatchToolWindow update via
                    MEF-imported IMessageProcessor
                └── when breakpoint hits:
                    └── DbgBoundCodeBreakpointImpl.Hit()
                        └── BreakAllHelper.Break()
                            └── MessageEntryPointBreak -> UI highlights active frame
```

## Stack 3 — Plugin (extension) loading

```
[process start]
└── MainApp/StartUpClass.cs:33  StartUpClass.Main()
    └── new App(readSettings, sw).Run()
        └── MainApp/App.xaml.cs:97  App ctor
            └── initializeMEFTask = Task.Run(() => InitializeMEF(readSettings, useCache: readSettings))
                └── GetAssemblies() -> LoadExtensionAssemblies()
                    └── GetExtensionFiles(BinDirectory) enumerates *.x.dll in BinDirectory, Extensions\, subdirs
                        └── args.ExtraExtensionDirectory also scanned
                    └── CanLoadExtension(file): reads <file>.xml ExtensionConfig (OS/Framework/App version check)
                    └── CanLoadExtension(asm): checks public key + minimum reference version 5.0.0.0
                    └── Assembly.LoadFrom(file) -> loadedExtensions.Add(new LoadedExtension(asm))
                └── Assembly[] -> AttributedPartDiscoveryV1 (MainApp/App.xaml.cs:155)
                └── ComposableCatalog.Create(resolver).AddParts(parts).CreateExportProvider()
                    └── returns VS-MEF ExportProvider
        └── MainApp/Extension/ExtensionService.cs  extensionService.LoadExtensions(Resources.MergedDictionaries)
            └── merges plugin MergedResourceDictionaries XAML files
        └── IAutoLoaded.BeforeExtensions / .AfterExtensions / .AfterExtensionsLoaded triggered
            └── via IAutoLoadedMetadata
```

## Stack 4 — WPF main window / MVVM

```
[WPF lifecycle]
└── StartUpClass.Main()
    └── new App(readSettings, startupStopwatch).Run()
        └── OnStartup(StartupEventArgs)    (MainApp/App.xaml.cs:521)
            └── blocks on initializeMEFTask.GetAwaiter().GetResult()
            └── if args.SingleInstance && !AppSettingsImpl.AllowMoreThanOneInstance:
                └── SwitchToOtherInstance()     (MainApp/App.xaml.cs:411-470)
                    └── enumerates windows; forwards args via WM_COPYDATA (header 0x11C9B152)
            └── cultureService.Initialize(args)
                └── sets Thread.CurrentThread.CurrentUICulture per --culture
            └── exportProvider.GetExportedValue<IDpiService>()   (init DPI early)
            └── exportProvider.GetExportedValue<AppWindow>()
                └── [ImportingConstructor] ctor pulls all MEF dependencies
            └── appWindow.InitializeMainWindow()    (MainApp/AppWindow.cs:1)
                └── constructs StackedContent (toolbar/center/status),
                    MainWindow (MetroWindow), MainWindowControl (dock layout)
            └── dsLoaderService.OnAppLoaded += DsLoaderService_OnAppLoaded
            └── extensionService.LoadExtensions(Resources.MergedDictionaries)
            └── win.Show()
            └── DsLoaderService.OnAppLoaded event:
                └── DnSpyEventSource.Log.StartupStop()   (MainApp/ETW)
                └── HandleAppArgs(args)
                    └── applies --language, --new-tab, --full-screen
                    └── opens files via OpenDocumentsHelper
                └── HandleAppArgs2(args)
                    └── dispatches to all IAppCommandLineArgsHandler exports in Order ascending
```

## Stack 5 — Document / tab management

```
[user clicks a member node]
└── DocumentTreeView.NodeActivated raises DocumentTreeNodeActivatedEventArgs
    └── Documents/Tabs/DocumentTabService.cs:1  DocumentTreeView_NodeActivated
        └── switch on node type:
            ├── AssemblyReferenceNode -> resolve ref, navigate tree
            ├── DerivedTypeNode / BaseTypeNode -> select target type
            ├── TypeReferenceNode / MethodReferenceNode / PropertyReferenceNode /
            │   EventReferenceNode / FieldReferenceNode -> resolve and select target
            └── default -> ActiveTabContentImpl
                └── TabContentImpl.Show(impl, nodes)
                    └── creates new TabContentImpl if none; reuses if same content
        └── IDocumentTabContentFactory.TryCreateAsync(...)
            ├── enumerates IReferenceDocumentTabContentProvider (Roslyn-based edits) by Order
            └── enumerates IDefaultDocumentTabContentProvider (default decompile tab) by Order
        └── DocumentTreeNodeDecompiler.DecompileAsync(method/type)
            └── IDecompiler.Decompile(MethodDef, IDecompilerOutput, ctx)
                └── writes to IDecompilerOutput (color-aware)
        └── IDecompilationCache.GetOrCreateAsync(...)   memoizes
        └── TabGroupService.ActiveTabGroup.ActiveTabContent = impl
            └── raises TabSelectionChanged
```

## Stack 6 — Decompile + edit (Roslyn round-trip)

```
[user edits a C# method and presses Apply]
└── RoslynLanguageCompiler                (Roslyn/Compiler/)
    └── parses editor buffer -> SyntaxTree
    └── CSharpCompilation.Create with project references (resolved by AssemblyResolver)
    └── Emit -> PE blob
    └── AsmEditor saves blob back to original DsDocument     (Extensions/dnSpy.AsmEditor/)
        └── writes metadata tokens via dnlib
        └── DocumentTreeView.DocumentService.CollectionChanged raises NotifyDocumentCollectionChangedEventArgs
        └── tree nodes refresh
```

## Stack 7 — Roslyn REPL

```
[user opens C# Interactive window and types "1 + 2"]
└── ScriptControl.axaml.cs
    └── ScriptControlVM.Submit(text)        (Common/ScriptControlVM.cs)
        └── CSharpScript.RunAsync(text, ScriptOptions.Default
                                            .WithReferences(...).WithImports(...))
                                            (Microsoft.CodeAnalysis.Scripting)
        └── returns ScriptState
        └── ScriptGlobals exposes dnSpy internals (current assembly list, debugger, ...) to user code
        └── output captured by CachedWriter
        └── ScriptControl.WriteOutput(...)
        └── state (globals, references, imports, lib paths) persisted in ReplSettings
```

## Stack 8 — Multi-language decompilation

```
[user selects a different language in the decompiler dropdown]
└── Decompiler/DecompilerService.cs
    └── Decompiler = newLanguage
        └── DecompilerChanged event fires
            └── tab content invalidates
            └── next decompile request calls IDecompiler.Decompile(...) on new backend:
                ├── CSharpDecompiler (NRefactory via dnSpy.Decompiler.ILSpy.Core) -> IDecompilerOutput colored text
                ├── VBDecompiler -> VB.NET text
                ├── ILDecompiler (flat) -> IL text
                └── ILDecompiler (structured) -> IL text
            └── selection preserved via Decompiler.UniqueGuid
```

## Stack 9 — Static analysis (Analyzer)

```
[user right-clicks a type, picks Analyze -> Used By]
└── AnalyzerService.GetResults(node)            (AnalyzerService.cs)
    └── iterates registered IAnalyzers
        └── each analyzer yields AnalyzerTreeNodeData instances:
            ├── MethodUsedByNode
            ├── BaseTypesTreeNode
            ├── DerivedTypesTreeNode
            ├── AttributeAppliedToNode
            ├── FieldAccessNode
            └── ... (~40 kinds)
    └── streamed to AnalyzerToolWindowContent via Add(node)
        └── each node async-fetches children via AsyncFetchChildrenHelper (cross-assembly)
    └── double-click result -> DocumentTreeView.SelectItems(target) (navigate)
```

## Stack 10 — Search (text / type / method / constant / metadata-token / resource)

```
[user opens Search tool window, picks Methods, types "GetCustomer"]
└── SearchControlVM.StartSearch()          (Search/SearchControlVM.cs)
    └── DocumentSearcherProvider.Create(searchOptions)   (Search/DocumentSearcherProvider.cs)
        └── SearchComparerFactory.Create(text, caseSensitive, matchWholeWords, matchAnyWords)
            └── builds RegExSearchComparer / AndSearchComparer / OrSearchComparer / literal variants
        └── DocumentSearcher.Start(IEnumerable<DsDocumentNode>)    (Search/DocumentSearcher.cs)
            └── FilterSearcher walks each document's type/method trees
                └── decompiles bodies
                └── applies the comparer
            └── OnNewSearchResults fires per batch
                └── SearchResult produced
                └── matched source lines highlighted via SyntaxHighlight
            └── TooManyResults triggers cancellation
            └── OnSearchCompleted fires
    └── user double-clicks result -> navigate to matching member
```

## Stack 11 — BAML -> XAML

```
[user opens a WPF assembly, selects a .baml resource, asks to decompile]
└── BamlResourceNodeProvider                (Extensions/dnSpy.BamlDecompiler/)
    └── creates BamlResourceElementNodes
    └── BamlDecompiler.Decompile(bamlStream)   (Baml/BamlDecompiler.cs)
        └── BamlDisassembler parses records (IL-style list)
        └── IRewritePass chain (field reference resolution, type lookup) via RecursionCounter
        └── XamlDecompiler.Emit(xamlContext, outputCreator)
            └── XamlOutputCreator writes into text editor
                └── XmlnsDictionary handles namespaces
        └── Readable XAML tab
```

## Stack 12 — IL interpreter (no-process debugging)

```
[user picks a method on a PE file with no live process and chooses "Run with IL Interpreter"]
└── Extensions/dnSpy.Debugger.DotNet.Interpreter engine activates via DbgEngineProviderImpl.Create
    └── ILVMFactory.Create(dmdRuntime)            (ILVMFactory.cs)
        └── ILVM instance created
    └── ILVM.Execute(method, ...)                  (ILVM.cs)
        └── walks IL byte-by-byte
        └── breakpoints trigger DbgBoundCodeBreakpointImpl.Hit()
            └── standard message pump
        └── locals/watches read from ILValue holders
    └── method executed in-process; breakpoints honored; no external runtime needed
```