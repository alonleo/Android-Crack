# 02 — Directory Tree

This is an annotated view of the dnSpy source layout.

```
dnSpy/
├── dnSpy.sln                                (58 KB; all projects)
├── Directory.Build.props / .targets         (multi-target, signing)
├── DnSpyCommon.props                        (versions: dnlib 3.3.2, Iced 1.9.0, Roslyn 2.10.0, ...)
├── build.ps1 / clean-all.cmd
├── Build/                                   (Common.props, ConvertToNetstandardReferences.tasks)
├── Libraries/                               (ICSharpCode.TreeView vendored)
├── dnSpy/                                   (all main subprojects live here, flat)
├── Extensions/                              (extension plugins, flat)
└── images/, README.md, LICENSE, .github/, .gitmodules
```

## 2.1 `dnSpy/dnSpy/` (main WPF application)

```
dnSpy/dnSpy/
├── dnSpy.csproj                             (WinExe, net48 + net5.0-windows; UseWPF + UseWindowsForms)
├── app.config, app.manifest
├── packages.config
│
├── MainApp/                                 (WPF Application bootstrap)
│   ├── StartUpClass.cs                      (73 LoC - [STAThread] Main)
│   ├── App.xaml + App.xaml.cs               (625 LoC - MEF init, plugin discovery, splash)
│   ├── AppCommandLineArgs.cs                (273 LoC - CLI parser)
│   ├── AppCommandLineArgsHandler.cs
│   ├── AppWindow.cs                         (225 LoC - IAppWindow impl)
│   ├── MainWindow.xaml + MainWindow.xaml.cs
│   ├── MainWindowControl.cs                 (638 LoC - dock layout)
│   ├── AppSettings.cs / AppStatusBar.cs / AppToolBar.cs
│   ├── AboutCommands.cs / AboutScreen.cs
│   ├── AskDlg.xaml* / AskVM.cs
│   ├── MsgBoxDlg.xaml* / MsgBoxVM.cs / MessageBoxService.cs
│   ├── DsLoaderControl.xaml* / DsLoaderService.cs
│   ├── DsToolWindowServiceCommands.cs
│   ├── CachedMefInfo.cs                     (173 LoC - cached MEF blob)
│   ├── BGJitUtils.cs / Constants.cs
│   ├── DotNetAssemblyLoader.cs
│   ├── SavedWindowState.cs / DevBuildWarning.cs
│   ├── ToolBarCommands.cs / ViewCommands.cs
│   ├── DocumentTreeViewWindowContent.cs
│   └── Extension/
│       ├── ExtensionConfig.cs / ExtensionConfigReader.cs
│       ├── ExtensionService.cs              (loads IExtension from *.x.dll)
│       └── LoadedExtension.cs
│
├── Extension/                               (runtime services; mirror of MainApp/Extension)
│
├── Documents/                               (the assembly explorer + tabs)
│   ├── DsDocumentService.cs                 (the model: list of loaded assemblies)
│   ├── DsDocumentServiceProvider.cs / DsDocumentServiceSettings.cs
│   ├── DefaultDsDocumentLoader.cs / DsDocumentLoader.cs / DefaultDsDocumentProvider.cs
│   ├── IDsDocumentLoader.cs / IDsDocumentProvider.cs
│   ├── AssemblyResolver.cs / DotNetPathProvider.cs / FileUtils.cs / FrameworkPath.cs
│   ├── TargetFrameworkAttributeInfo.cs / MethodAnnotations.cs
│   ├── ReferenceNavigatorServiceImpl.cs
│   ├── Tabs/                                (open documents + tab content)
│   │   ├── DocumentTabService.cs            (~600+ LoC)
│   │   ├── DocumentTabServiceSettings.cs / DocumentTabServiceLoader.cs
│   │   ├── DocumentTabContentFactoryService.cs / DocumentTabContentFactoryContext.cs
│   │   ├── DocumentTreeNodeDecompiler.cs
│   │   ├── DocumentTabSerializer.cs / DsDocumentInfoSerializer.cs
│   │   ├── DocumentTabUIContextLocator.cs
│   │   ├── DocumentList.cs / DocumentListLoader.cs / DocumentListService.cs
│   │   ├── AppCommandLineArgsHandler.cs / EntryPointCommands.cs
│   │   ├── Commands.cs / GoToTokenCommand.cs / CopyTokenCommand.cs
│   │   ├── DocTabReferenceNavigator.cs / DefaultDecompileNode.cs
│   │   ├── DecompilationCache.cs
│   │   ├── AsyncShowResult.cs / DefaultDocumentList.cs
│   │   ├── DefaultDocumentTabContentProvider.cs
│   │   ├── Dialogs/ / DocViewer/ / Hex/
│   │   └── Tabs.snk
│   └── TreeView/                            (document tree)
│       ├── DocumentTreeView.cs / DocumentTreeViewSettings.cs
│       └── (resource folders / nodes / providers / filters)
│
├── Tabs/                                    (WPF tab control layer)
│   ├── TabService.cs / TabServiceProvider.cs
│   ├── TabGroup.cs / TabGroupService.cs
│   ├── TabItemImpl.cs / TabElementZoomer.cs / TabUtils.cs
│
├── Decompiler/                              (decompiler service + settings)
│   ├── DecompilerService.cs
│   ├── DecompilerServiceSettings.cs / DecompilerAppSettingsPageContainer.cs
│   ├── MethodDebugService.cs
│   └── DummyDecompiler.cs
│
├── Disassembly/                             (IL / native hex view)
├── Hex/                                     (hex editor; many WPF controls)
├── Text/                                    (AvalonEdit wrapper)
├── Search/                                  (search tool window + filter searcher)
│   ├── SearchService.cs / DocumentSearcher.cs / DocumentSearcherProvider.cs
│   ├── FilterSearcher.cs / FilterSearcherOptions.cs
│   ├── SearchControl.xaml + .cs / SearchControlVM.cs
│   ├── SearchResultContext.cs / SearchResult.cs
│   ├── SearchSettings.cs / SearchType.cs / SearchTypeVM.cs
│   ├── SearchToolWindowContent.cs / FrameworkFileUtils.cs
│   └── AppCommandLineArgsHandler.cs
│
├── ToolWindows/                             (tool window framework)
├── Menus/                                   (menu service impls, context menus, key shortcuts)
├── Commands/                                (IWpfCommands / IWpfCommandService implementation)
├── TreeView/                                (ICSharpCode.TreeView adapter)
├── Metadata/                                (pe/metadata helpers at UI layer)
├── Scripting/                               (script window infrastructure)
├── Settings/                                (XmlSettingsReader/Writer + UI containers)
├── Output/                                  (Output tool window + ETW)
├── Bookmarks/                               (bookmark service + UI)
├── ToolBars/                                (toolbar service)
├── TextView/                                (advanced text view features)
├── Controls/                                (custom WPF controls: MetroWindow, etc.)
├── UI/                                      (image services, dialog helpers, NotifyIcon)
├── Themes/                                  (XAML themes: blue/dark/light/dark-high-contrast)
├── FileLists/                               (DLL enumeration; copy to output)
├── Hex/                                     (hex editor engine — large)
├── LicenseInfo/                             (CREDITS.txt embedded)
├── Images/                                  (image catalog)
├── MVVM/                                    (InitializeDataTemplateContextMenu.cs)
├── Culture/                                 (culture service + per-language resources)
├── Language/                                (language preferences)
├── BackgroundImage/                         (startup background image)
├── Events/                                  (WeakEventList, WeakEventSource)
└── Properties/                              (Resources.resx + Resources.Designer.cs auto-generated)
```

## 2.2 `dnSpy/dnSpy/dnSpy.Contracts.DnSpy/` (main app contracts — interface-only)

```
dnSpy.Contracts.DnSpy/
├── App/                                     (IAppWindow, IAppCommandLineArgs, IMessageBoxService, AppDirectories)
├── AsmEditor/                               (interfaces for assembly editor extensions)
├── BackgroundImage/                         (background image provider)
├── Bookmarks/                               (IBookmark, IBookmarkService, IBookmarkListener)
├── Command/                                 (IWpfCommandService, IWpfCommands, etc.)
├── Controls/                                (custom control contracts)
├── Decompiler/                              (IDecompilerService, IMethodDebugService)
├── Disassembly/                             (disassembly view contracts)
├── Documents/                               (IDsDocument, IDsDocumentService, IDsPEDocument, …)
│   ├── Tabs/                                (IDocumentTab, IDocumentTabService, IReferenceDocumentTabContentProvider)
│   ├── TreeView/                            (IDocumentTreeView, IDocumentTreeNodeProvider, DocumentTreeNodeData)
│   └── AnnotationsImpl.cs / DocumentConstants.cs / DotNetReferences.cs / ReferenceNavigator.cs
├── ETW/                                     (DnSpyEventSource)
├── Extension/                               (IExtension, IAutoLoaded, ExportExtensionAttribute, ExtensionInfo)
├── Hex/                                     (hex editor contracts)
├── Images/                                  (IImageService, IImageSource)
├── Language/                                (ILanguageManager, language GUIDs)
├── Menus/                                   (IMenuService, IMenuItem, IMenuItemProvider, IContextMenuProvider)
├── Metadata/                                (UI-layer metadata helpers)
├── MVVM/                                    (IInitializeDataTemplate, RelayCommand, ListVM, EnumVM, …)
├── Output/                                  (IOutputService)
├── Scripting/                               (IScriptService, scripting contract)
├── Search/                                  (IDocumentSearcher, ISearchComparer, ISearchResult, Filters)
├── Settings/                                (ISettingsService, ISettingsSection, XmlSettingsReader/Writer)
├── Tabs/                                    (ITabService, ITabGroupService, ITabGroup, ITabContent)
├── Text/                                    (text editor contracts, classification, projection)
├── Themes/                                  (theme manager)
├── ToolBars/                                (toolbar service contracts)
├── ToolWindows/                             (IToolWindowService, AppToolWindow*)
├── TreeView/                                (sharp tree view contracts)
└── Utilities/                               (helper utilities)
```

## 2.3 `dnSpy/dnSpy/dnSpy.Contracts.Debugger*/` (debugger contracts)

```
dnSpy.Contracts.Debugger/
├── DbgManager.cs                            (abstract - manages DbgEngine, processes, runtimes)
├── DbgDispatcher.cs / DbgMessageEventArgs.cs / DbgCollectionChangedEventArgs.cs
├── DbgAppDomain.cs / DbgRuntime.cs / DbgProcess.cs / DbgThread.cs / DbgModule.cs
├── DbgStateInfo.cs / DbgInternalRuntime.cs / DbgInternalAppDomain.cs / DbgInternalModule.cs
├── DbgImageLayout.cs / DbgEnvironment.cs / DbgObject.cs
├── DbgModuleMemoryRefreshedNotifier.cs / IDbgManagerStartListener.cs
├── DebuggerSettings.cs / DebugProgramOptions.cs / RuntimeId.cs / StartDebuggingOptions.cs
├── PredefinedDebugTags.cs / PredefinedDbgRuntimeGuids.cs
├── PredefinedDbgRuntimeKindGuids.cs / PredefinedThreadKinds.cs
├── AntiAntiDebug/, Attach/, Breakpoints/, CallStack/, Code/, Disassembly/
├── Engine/, Evaluation/, Exceptions/, References/, StartDebugging/, Steppers/

dnSpy.Contracts.Debugger.DotNet/             (.NET-specific debugger contracts)
├── DbgDotNetInternalRuntime.cs / DbgDotNetInternalAppDomain.cs / DbgDotNetInternalModule.cs
├── Breakpoints/, Code/, Disassembly/, Evaluation/, Extensions/, Metadata/
├── Modules/, Runtimes/, Steppers/, Text/

dnSpy.Contracts.Debugger.DotNet.CorDebug/    (CorDebug-only contracts)
├── CorDebugRuntimeKind.cs / CorDebugRuntimeVersion.cs
├── CorDebugStartDebuggingOptions.cs / DotNetFrameworkStartDebuggingOptions.cs
├── DotNetStartDebuggingOptions.cs
├── CorThreadUserStates.cs / DbgCorDebugInternalRuntime.cs

dnSpy.Contracts.Debugger.DotNet.Mono/        (Mono-only contracts)
```

## 2.4 `dnSpy/dnSpy/dnSpy.Decompiler/`

```
dnSpy.Decompiler/
├── DecompilerBase.cs                        (base class for language backends)
├── CSharp/CSharpFormatter.cs                (~900 LoC - struct-based C# text formatter)
├── IL/                                      (ILLanguageHelper, InstructionBytesReader, ModifiedInstructionBytesReader, OriginalInstructionBytesReader, InstructionUtils)
├── MSBuild/                                 (MSBuild SDK resolver for project export)
├── Settings/                                (decompiler settings page UI)
├── TargetFrameworkInfo.cs / TargetFrameworkUtils.cs
├── FilenameUtils.cs / FormatterMethodInfo.cs / TypeFormatterUtils.cs
└── Utils/
```

## 2.5 `Extensions/ILSpy.Decompiler/` (embedded ILSpy 5 decompiler)

```
Extensions/ILSpy.Decompiler/
├── dnSpy.Decompiler.ILSpy/                  (dnSpy plugin wrapper)
│   ├── TheExtension.cs / dnSpy.Decompiler.ILSpy.csproj
│   ├── ContentTypeDefinitions.cs / Themes/ / Properties/ / Settings/
│   ├── CSharp/                              (CSharpDecompiler adapter + settings)
│   ├── IL/                                  (ILDecompiler; flat + structured modes)
│   ├── ILAst/                               (legacy NRefactory ILAst)
│   └── VisualBasic/                         (VBDecompiler)
├── dnSpy.Decompiler.ILSpy.Core/             (actual decompiler engine)
│   ├── CSharp/                              (CSharpDecompiler.cs 525 LoC, BuilderCache, BuilderState, ThreadSafeObjectPool, transforms)
│   ├── VisualBasic/                         (VBDecompiler.cs, VBTextOutputFormatter.cs, ILSpyEnvironmentProvider.cs)
│   ├── IL/                                  (ILDecompiler.cs, ILDecompilerUtils.cs)
│   ├── ILAst/                               (legacy NRefactory ILAst)
│   ├── Settings/                            (DecompilerSettingsService, ILSettings, ...)
│   ├── Text/                                (content types internal)
│   └── XmlDoc/                              (XML doc-comment providers)
├── ICSharpCode.Decompiler/                  (vendored legacy ILSpy decompiler, pre-8)
└── NRefactory/                              (vendored NRefactory 5)
```

## 2.6 `Extensions/dnSpy.Debugger/`

```
Extensions/dnSpy.Debugger/
├── dnSpy.Debugger/                          (generic, UI + framework — 27 Impl files, 1234 LoC DbgManagerImpl)
│   ├── TheExtension.cs / dnSpy.Debugger.csproj
│   ├── AntiAntiDebug/                       (anti-anti-debug hooks)
│   ├── Attach/                              (AttachableProcessesServiceImpl, AttachableProcessImpl, Win32CommandLineProvider, AppCommandLineArgsHandler)
│   ├── Breakpoints/                         (Code/, Modules/)
│   ├── CallStack/                           (DbgCallStackServiceImpl, DbgStackFrameImpl, DbgStackWalkerImpl)
│   ├── Code/                                (code location contracts)
│   ├── DbgUI/                               (debugger UI service)
│   ├── Dialogs/                             (Attach to Process, Breakpoint settings)
│   ├── Disassembly/                         (native disassembly view)
│   ├── Evaluation/                          (expression evaluation)
│   ├── Exceptions/                          (exception settings)
│   ├── Impl/                                (27 files: DbgManagerImpl.cs, DbgEngineImpl*, DbgProcessImpl, DbgThreadImpl, DbgModuleImpl, DbgAppDomainImpl, DbgRuntimeImpl, DbgBoundCodeBreakpointImpl, DbgBreakInfoCollectionBuilder, DbgDispatcherImpl, ...)
│   ├── Modules/                             (module window)
│   ├── Native/                              (native process/threads)
│   ├── Settings/                            (debugger settings UI)
│   ├── Shared/                              (Dispatcher, FileUtilities — included by other projects)
│   ├── Steppers/                            (step engine)
│   ├── Text/                                (debugger text adornments, current-line highlight)
│   ├── Themes/                              (debugger xaml themes)
│   ├── ToolWindows/                         (Autos, CallStack, CodeBreakpoints, Exceptions, Locals, Logger, Memory, ModuleBreakpoints, Modules, Processes, Threads, Watch, ...)
│   ├── UI/                                  (debugger UI helpers)
│   └── Utilities/                           (debugger-side utilities)
│
├── dnSpy.Debugger.DotNet/                   (.NET-specific debugger glue)
│   ├── TheExtension.cs / dnSpy.Debugger.DotNet.csproj
│   ├── Attach/, Breakpoints/, CallStack/, Code/, Disassembly/, Evaluation/
│   ├── Exceptions/, Modules/, Properties/, Settings/, Steppers/, UI/, Utilities/
│
├── dnSpy.Debugger.DotNet.CorDebug/          (CorDebug implementation — biggest extension)
│   ├── TheExtension.cs / dnSpy.Debugger.DotNet.CorDebug.csproj
│   ├── AntiAntiDebug/                       (P/Invoke patches to bypass managed anti-debug)
│   ├── Breakpoints/, CallStack/, Code/, DAC/ (crash dumps)
│   ├── dndbg/                               (raw CorDebug COM interop)
│   ├── Dialogs/, Impl/, Metadata/, Native/, Properties/, Steppers/, Themes/, UI/, Utilities/
│   ├── Impl/                                (36 files: DbgEngineImpl.cs 974 LoC, .Breakpoints.cs, .Evaluation.cs, .ModuleDef.cs, .Threads.cs, DbgEngineImplDependencies, DbgEngineProviderImpl, DbgCorDebugInternalRuntimeImpl, DmdRuntime, DmdDispatcherImpl, ...)
│
├── dnSpy.Debugger.DotNet.Mono/              (Mono soft-debugger implementation)
│   ├── TheExtension.cs / dnSpy.Debugger.DotNet.Mono.csproj
│   ├── AntiAntiDebug/, CallStack/, Dialogs/, Impl/, Metadata/, Properties/, Steppers/, Themes/
│
├── dnSpy.Debugger.DotNet.Interpreter/       (pure-IL interpreter)
│   ├── TheExtension.cs / DebuggerRuntime.cs, ILValue.cs, ILVM.cs, ILVMFactory.cs
│   ├── InterpreterException.cs, InterpreterMessageException.cs, InterpreterThrownExceptionException.cs
│   ├── Impl/, NRT.cs
│
├── dnSpy.Debugger.DotNet.Metadata/          (DmdRuntime abstraction)
│   ├── DmdRuntime.cs / DmdModule.cs / DmdTypeDef.cs / ...
│
├── AppHostInfoGenerator/                    (rewrites apphost.exe for attach)
├── Mono.Debugger.Soft/                      (vendored Mono soft-debugger protocol client)
└── netcorefiles/                            (x86/x64 .NET debug files)
```

## 2.7 `Extensions/dnSpy.Scripting.Roslyn/` (REPL)

```
Extensions/dnSpy.Scripting.Roslyn/
├── TheExtension.cs / dnSpy.Scripting.Roslyn.csproj
├── ContentTypeDefinitions.cs
├── CSharpInteractive.rsp / VisualBasicInteractive.rsp
├── Commands/                                (commands shown in the script window)
├── Common/                                  (ScriptControl, ScriptControlVM, ScriptToolWindowContent, ScriptContent, ScriptGlobals, IScriptCommand, IScriptGlobalsHelper, RoslynReplCommandInfoProvider, RoslynReplCommandTargetFilter[Provider], ReplSettings, ResetCommand, ClearCommand, HelpCommand, Commands, PrintOptionsImpl, RespFileUtils, ResponseFileReader, CachedWriter)
├── CSharp/                                  (CSharpContent, CSharpControlVM, CSharpToolWindowContent, CSharpReplSettingsImpl, ReplOptionsDefinitions)
├── VisualBasic/                             (VB equivalents)
└── Properties/
```

## 2.8 Other Extensions

```
Extensions/dnSpy.Analyzer/                  (static analyzer)
├── TheExtension.cs / dnSpy.Analyzer.csproj / AnalyzerService.cs / AnalyzerSettings.cs
├── AnalyzerToolWindowContent.cs / AnalyzerTreeNodeDataContext.cs
├── Commands.cs / ContentTypeDefinitions.cs / TreeTraversal.cs
├── TreeNodes/                               (EntityNode, TypeNode, MethodNode, FieldNode, EventNode, PropertyNode, AssemblyNode, BaseTypesTreeNode, DerivedTypesTreeNode, AttributeAppliedToNode, EventFiredByNode, EventAccessorNode, EventOverriddenNode, EventOverridesNode, FieldAccessNode, InterfaceEventImplementedByNode, InterfaceMethodImplementedByNode, InterfacePropertyImplementedByNode, …)

Extensions/dnSpy.AsmEditor/                 (assembly editor — 23 directories; largest extension)
├── TheExtension.cs / dnSpy.AsmEditor.csproj
├── Assembly/, Commands/, Compiler/, Converters/, DnlibDialogs/, Event/, ExtensionMethods.cs, Field/, Hex/, ...

Extensions/dnSpy.BamlDecompiler/            (BAML→XAML)
├── TheExtension.cs / dnSpy.BamlDecompiler.csproj
├── Baml/, BamlDecompiler.cs, BamlDisassembler.cs, BamlElement.cs, BamlResourceElementNode.cs, BamlResourceNodeProvider.cs, BamlSettings.cs, BamlSettings.xaml, BamlToolTipProvider.cs, ContentTypeDefinitions.cs
├── Handlers/, IHandlers.cs, IRewritePass.cs, MenuCommands.cs, RecursionCounter.cs, Rewrite/
├── Xaml/, XamlContext.cs, XamlDecompiler.cs, XamlOutputCreator.cs, XamlOutputOptionsProvider.cs, XmlnsDictionary.cs, Annotations.cs

Extensions/Examples/
├── Example1.Extension/                     (minimal MEF plugin sample)
└── Example2.Extension/                     (tool-window sample)
```

## 2.9 `dnSpy/dnSpy/Roslyn/` (Roslyn embedding — 7 subprojects)

```
dnSpy/Roslyn/
├── dnSpy.Roslyn/                            (core: workspace, syntax tree, classification, scripting, debug info)
│   ├── Compiler/                            (CSharpCompiler, VBCompiler, CommandLineParser wrappers)
│   ├── Debugger/                            (Roslyn debug-info bridge to DbgLanguage)
│   ├── Documentation/, Glyphs/, Intellisense/, Optimizations/, Properties/, Text/, Themes/
├── dnSpy.Roslyn.Internal/                   (internal access — Microsoft.CodeAnalysis.Internal)
├── dnSpy.Roslyn.EditorFeatures/             (shared editor features)
├── dnSpy.Roslyn.CSharp.EditorFeatures/      (C# editor features)
├── dnSpy.Roslyn.CSharp.Internal/            (C# internal API)
├── dnSpy.Roslyn.VisualBasic.EditorFeatures/ (VB editor features)
├── dnSpy.Roslyn.VisualBasic.Internal/       (VB internal API)
└── Roslyn.ExpressionCompiler/               (expression compiler fork)
```

## File-count / LoC summary

| Bucket | Files | ~LoC |
|---|---:|---:|
| Main WPF app (`dnSpy/dnSpy/dnSpy`) | ~800 | ~70,000 |
| Contracts (`dnSpy.Contracts.DnSpy`) | 870 | ~80,000 |
| Debugger contracts (`dnSpy.Contracts.Debugger*`) | 145 | ~15,000 |
| Generic debugger (`dnSpy.Debugger`) | ~250 | ~12,000 |
| CorDebug (`dnSpy.Debugger.DotNet.CorDebug`) | ~300 | ~25,000 |
| Mono debugger | ~50 | ~4,000 |
| Interpreter | ~20 | ~1,500 |
| AsmEditor | ~400 | ~72,000 (largest extension) |
| Analyzer | ~50 | ~3,000 |
| Scripting REPL | ~30 | ~2,500 |
| BAML | ~40 | ~3,500 |
| Decompiler glue (`dnSpy.Decompiler`) | ~30 | ~3,000 |
| Vendored ILSpy 5 (`Extensions/ILSpy.Decompiler/*`) | ~700 | ~50,000 |
| Vendored Roslyn 2.10.0 (`dnSpy.Roslyn.*`) | ~700 | vendored |
| Misc (console, images, hex, search, contracts.*) | ~250 | ~25,000 |
| **Total (incl. vendored / generated)** | **~4119 .cs + 232 .xaml** | **~127,000** |