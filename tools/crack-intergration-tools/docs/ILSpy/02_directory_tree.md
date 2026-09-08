# 02 — Directory Tree

This is an annotated view of the ILSpy source layout. Sub-projects marked **(entry)** are runnable; the rest are libraries consumed by the entry projects.

```
ILSpy/                                         (root)
├── ILSpy.sln                                  (full solution)
├── ILSpy.Desktop.slnf                         (Avalonia UI + tests filter)
├── ILSpy.XPlat.slnf                           (cross-platform libs + ilspycmd + tests; Linux CI target)
├── ILSpy.Installer.sln                        (WiX packaging)
├── ILSpy.VSExtensions.slnx                    (VS 2022 add-in)
├── Directory.Build.props                      (RestorePackagesWithLockFile = true)
├── Directory.Packages.props                   (CPM: every PackageVersion)
├── global.json                                (pin Microsoft.Testing.Platform)
├── restore.ps1 / build.ps1 / publish.ps1      (use these, not raw dotnet)
├── updatedeps.ps1 / clean.ps1
├── BuildTools/                                (update-assemblyinfo.ps1, format.ps1)
├── CLAUDE.md                                  (onboarding guide)
├── editorconfig + .gitattributes              (LF; auto-renormalize)
│
├── ICSharpCode.Decompiler/                    [CORE ENGINE] (entry: library; netstandard2.0)
│   ├── ICSharpCode.Decompiler.csproj          (multi-RID: win-x64, win-arm64, linux-x64, osx-arm64)
│   ├── Decompiler.cs                          (legacy façade; DecompileAsync)
│   ├── DecompilerSettings.cs                  (2450 LoC; ~200 [Serializable] options)
│   ├── DecompilerException.cs                 (structured exception w/ module + method + cause)
│   ├── DecompileRun.cs                        (per-decompilation shared state: settings, cancellation, namespaces)
│   ├── DecompilationProgress.cs               (IProgress<T> hook)
│   ├── PartialTypeInfo.cs                     (collects partial-type members across passes)
│   ├── SingleFileBundle.cs                    (.NET 5+ single-file bundle support)
│   ├── SRMExtensions.cs / SRMHacks.cs         (System.Reflection.Metadata helpers)
│   ├── NRTAttributes.cs / NRExtensions.cs     (nullable-attribute utilities)
│   ├── Properties/DecompilerVersionInfo.cs    (GENERATED at build time)
│   │
│   ├── CSharp/                                [C# AST + Decompiler]
│   │   ├── CSharpDecompiler.cs                (2517 LoC - PUBLIC FACADE)
│   │   ├── CSharpLanguageVersion.cs           (enum CSharp1..CSharp13 + Preview + Latest)
│   │   ├── CallBuilder.cs                     (2300 LoC - ILAst Call -> InvocationExpression)
│   │   ├── ExpressionBuilder.cs               (5018 LoC - ILAst -> Expression, BIGGEST FILE)
│   │   ├── StatementBuilder.cs                (1586 LoC - ILAst Block -> BlockStatement)
│   │   ├── RecordDecompiler.cs                (record primary-constructor flattening)
│   │   ├── SequencePointBuilder.cs            (IL offset -> text position)
│   │   ├── Annotations.cs                     (nullable attribute decoder)
│   │   ├── RequiredNamespaceCollector.cs      (using/import namespace walker)
│   │   ├── TranslatedExpression.cs / TranslatedStatement.cs / TranslationContext.cs
│   │   ├── CSharpSlotInfo.cs / CSharpAmbience.cs
│   │   ├── CSharpFormattingOptions.cs / FormattingOptionsFactory.cs
│   │   ├── ProjectDecompiler/                 (WholeProjectDecompiler + SDK-style .csproj writers)
│   │   ├── Resolver/                          (CSharpResolver 2986 LoC + overload resolution)
│   │   ├── OutputVisitor/                     (CSharpOutputVisitor 3164 LoC + decorators)
│   │   ├── Syntax/                            (NRefactory AST nodes - 100+ classes)
│   │   ├── Transforms/                        (21 AST transforms - post-ILAst)
│   │   └── TypeSystem/                        (C# AST type adapter)
│   │
│   ├── IL/                                    [ILAst abstraction]
│   │   ├── ILReader.cs                        (2191 LoC - CIL -> ILAst)
│   │   ├── Instructions.tt / Instructions.cs  (T4-generated opcode table)
│   │   ├── ILInstruction.cs / Instructions/   (Block, ILFunction, IfInstruction, Call, Branch, ...)
│   │   ├── ILAmbience.cs / ILVariable.cs / BlockBuilder.cs / SemanticHelper.cs
│   │   ├── ILTypeExtensions.cs / InstructionFlags.cs
│   │   ├── ILAstWritingOptions.cs             (Debug Steps pane config)
│   │   ├── Patterns/                          (IL pattern combinators)
│   │   ├── ControlFlow/                       (ControlFlowGraph, AsyncAwait, YieldReturn, ... 11 files)
│   │   └── Transforms/                        (49 IL transforms - the de-sugaring pipeline)
│   │
│   ├── FlowAnalysis/                          (legacy data-flow; used by some transforms)
│   ├── TypeSystem/                            (~60 interface files; ~40 impls)
│   ├── Metadata/                              (PEFile, UniversalAssemblyResolver, DotNetCorePathFinder, ...)
│   ├── Disassembler/                          (IL pretty-printer - ReflectionDisassembler)
│   ├── Output/                                (decoupled ITextOutput token writer abstraction)
│   ├── DebugInfo/                             (IDebugInfoProvider, SequencePoint)
│   ├── Documentation/                         (XmlDocLoader)
│   ├── DebugSteps/                            (per-transform-step hook for the Debug Steps pane)
│   ├── Solution/                              (SolutionCreator for whole-project export)
│   ├── Semantics/                             (ResolveResult hierarchy)
│   ├── Instrumentation/                       (ETW EventSource for telemetry)
│   ├── Humanizer/                             (vendored Humanizer)
│   └── Util/                                  (low-level helpers; FileUtility, CSharpPrimitiveCast 771 LoC)
│
├── ICSharpCode.Decompiler.Generators/         (Roslyn source generator: emits DecompilerVersionInfo.cs)
│
├── ICSharpCode.Decompiler.PowerShell/         (PowerShell cmdlets - netstandard2.0)
│
├── ICSharpCode.Decompiler.Tests/              (NUnit; RoundtripAssembly + ILPretty; tests against ILSpy-tests submodule)
│
├── ICSharpCode.Decompiler.TestRunner/         (out-of-process test runner)
│
├── ICSharpCode.BamlDecompiler/                (BAML -> XAML library; used by ilspycmd --decompile-baml)
│
├── ICSharpCode.ILSpyCmd/                      **(ENTRY: CLI)** `ilspycmd` global tool
│   ├── IlspyCmdProgram.cs                     (~700 LoC; 28 flags)
│   ├── BamlAwareWholeProjectDecompiler.cs     (extends WholeProjectDecompiler to translate .g.resources)
│   ├── TypesParser.cs                         (parses -l c,i,s,d,e)
│   ├── DotNetToolUpdateChecker.cs             (NuGet version probe)
│   └── AsContainer/                           (NuGet .nupkg handling)
│
├── ICSharpCode.ILSpyX/                        [UI-HOST-AGNOSTIC CORE]
│   ├── AssemblyList.cs                        (468 LoC - list of LoadedAssembly)
│   ├── AssemblyListManager.cs                 (316 LoC - CRUD + Undo)
│   ├── AssemblyListSnapshot.cs                (201 LoC - immutable view)
│   ├── LoadedAssembly.cs                      (766 LoC - Lazy<Task<LoadResult>> via FileLoaderRegistry)
│   ├── LoadedAssemblyExtensions.cs / LoadedPackage.cs (368 LoC; .nupkg / .NET bundle)
│   ├── Abstractions/                          (ILanguage, IResourceFileHandler, IResourceNodeFactory, ITreeNode)
│   ├── Analyzers/                             (IAnalyzer + Builtin)
│   ├── Extensions/                            (collection helpers)
│   ├── FileLoaders/                           (PEFileLoader, ArchiveFileLoader, BundleFileLoader, WebCilFileLoader, ...)
│   ├── MermaidDiagrammer/                     (ClassDiagrammer + GenerateHtmlDiagrammer for --generate-diagrammer)
│   ├── PdbProvider/                           (PortableDebugInfoProvider, MonoCecilDebugInfoProvider)
│   ├── Search/                                (9 search strategies; see section 4.2)
│   ├── Settings/                              (DecompilerSettings, ILSpySettings, SettingsServiceBase, MutexProtector)
│   ├── TreeView/                              (SharpTreeNode, SharpTreeNodeCollection, TreeFlattener, FlatListTreeNode)
│   └── Util/                                  (GuessFileType)
│
├── ILSpy/                                     **(ENTRY: Avalonia GUI)**
│   ├── Program.cs                             (52 LoC - STAThread Main, BuildAvaloniaApp)
│   ├── App.axaml + App.axaml.cs               (lifecycle, MEF init, settings path, culture)
│   ├── Entry.cs                               (118 LoC - public API facade for embedding)
│   ├── CompareEngine.cs                       (diff two assemblies)
│   ├── DecompilationOptions.cs                (per-tab settings + formatting)
│   ├── EntityReference.cs / NavigationEntry.cs / NavigationHistory.cs (148 LoC, 2-stack history)
│   ├── SessionSettings.cs / SettingsService.cs / LanguageSettings.cs
│   ├── Analyzers/                             (Avalonia AnalyzerPane)
│   ├── AppEnv/                                (AppComposition, CommandLineArguments, GlobalExceptionHandler, ...)
│   ├── AssemblyTree/                          (AssemblyTreeModel 1013 LoC + Compare/)
│   ├── Bookmarks/                             (BookmarkManager + persistence)
│   ├── Commands/                              (~44 files - one file per menu command)
│   ├── Controls/                              (Avalonia custom controls)
│   ├── Docking/                               (DockFactory, DockWorkspace)
│   ├── Languages/                             (ILanguage impls: CSharpLanguage, ILSpyILLanguage, VBLanguage)
│   ├── Metadata/                              (MetadataTablePage + DecompilerInfoProvider)
│   ├── NuGetFeeds/                            (NuGet v3 search + browse)
│   ├── Options/                               (Avalonia settings dialogs)
│   ├── Search/                                (SearchPane.axaml + .cs, SearchPaneModel, RunningSearch)
│   ├── TextView/                              (decompiled text view)
│   ├── Themes/                                (Simple theme)
│   ├── TreeNodes/                             (~40 SharpTreeNode subclasses)
│   ├── Updates/                               (NuGet feed update check)
│   ├── Util/                                  (WeakEventSource, ETW helpers)
│   ├── ViewModels/                            (MainWindowViewModel, TabPageModel, NuGetPackageViewModel, ...)
│   └── Views/                                 (MainWindow.axaml + .cs, CompareView, ContentTabPageView, ...)
│
├── ILSpy.ReadyToRun/                          (ReadyToRun viewer plugin)
├── ILSpy.Tests/                               (Avalonia.Headless.NUnit tests)
├── ILSpy.Tests.Windows/                       (net11.0-windows-only UI tests)
├── ILSpy.BamlDecompiler.Tests/                (BAML tests - WPF/Windows)
├── ILSpy.AddIn.VS2022/                        (VS extension; net472)
├── ILSpy.Installer/                           (WiX installer)
├── TestFixtures.Resources/                    (generated fixtures for tests)
├── TestPlugin/                                (sample *.Plugin.dll for plugin loading tests)
└── ILSpy-tests/                               [GIT SUBMODULE; not checked out by default]
    └── RoundtripAssembly.cs + ILPrettyTestRunner
```

## File-count / LoC summary

| Bucket | Files | ~LoC |
|---|---:|---:|
| `ICSharpCode.Decompiler` (core) | 578 .cs | ~85,000 |
| `ICSharpCode.ILSpyX` (UI-host core) | ~25 .cs | ~3,500 |
| `ICSharpCode.ILSpyCmd` (CLI) | ~15 .cs | ~1,200 |
| `ILSpy` (Avalonia GUI) | ~120 .cs + 34 .xaml | ~14,000 |
| Others (Generators, BAML, PowerShell, tests, ...) | ~1000 .cs | ~1,300 |
| **Total (excluding `ILSpy-tests/` submodule)** | **~1731 .cs + 34 .xaml** | **~105,000** |