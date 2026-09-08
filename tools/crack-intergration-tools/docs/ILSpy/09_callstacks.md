# 09 — Call Stacks

This document gives text-based call stacks for each of the 12 operation chains in [05_operation_chains.md](./05_operation_chains.md). Each stack shows the actual entry function, the major call sites, and the leaf (terminal) call. Line numbers reference the source tree at `/home/leo/文档/android-crack/tools/source-projects/ILSpy/`.

## Stack 1 — CLI single-file decompile

```
[user shell]
└── ilspycmd sample.dll
    └── ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:71  ILSpyCmdProgram.Main(args)
        └── HostBuilder().RunCommandLineApplicationAsync<ILSpyCmdProgram>(args)
            └── ILSpyCmdProgram.cs:236  ILSpyCmdProgram.OnExecuteAsync(app)
                └── ILSpyCmdProgram.cs:286  PerformPerFileAction(file)
                    └── ILSpyCmdProgram.cs:549  Decompile(fileName, output, TypeName)
                        └── ILSpyCmdProgram.cs:430  GetDecompiler(fileName)
                            ├── PEFile.cs  PEFile(fileName, PEStreamOptions.PrefetchEntireImage)
                            ├── Metadata/UniversalAssemblyResolver.cs  UniversalAssemblyResolver(...)
                            ├── DecompilerSettings.cs:48  new DecompilerSettings(LanguageVersion)
                            └── TypeSystem/DecompilerTypeSystem.cs:127  DecompilerTypeSystem.CreateAsync(peFile, resolver)
                                └── CSharpDecompiler.cs:259  new CSharpDecompiler(module, resolver, settings)
                        └── CSharpDecompiler.cs:835  DecompileWholeModuleAsSingleFile()
                            ├── CSharpDecompiler.cs:758  DecompileModuleAndAssemblyAttributes()
                            ├── CSharpDecompiler.cs:1166  DecompileTypes(types)
                            │   └── CSharpDecompiler.cs:1244  Decompile(handles)
                            │       └── CSharpDecompiler.cs:1993  DoDecompile(IMethod, ...)
                            │           └── CSharpDecompiler.cs:2136  DecompileBody(methodDef, ...)
                            │               ├── IL/ILReader.cs:139  new ILReader(typeSystem.MainModule)
                            │               ├── IL/ILReader.cs:720  ReadIL(methodHandle, methodBody)
                            │               ├── CSharpDecompiler.cs:88  GetILTransforms()
                            │               ├── IL/Transforms/*  ~30 IILTransforms.Run()
                            │               └── CSharp/StatementBuilder.cs  StatementBuilder.ConvertAsBlock(...)
                            └── CSharpDecompiler.cs:727  RunTransforms(syntaxTree, ...)
                                └── CSharp/Transforms/*  ~16 IAstTransforms.Run()
                            └── CSharpDecompiler.cs:740  SyntaxTreeToString(syntaxTree)
                                └── CSharp/OutputVisitor/CSharpOutputVisitor.cs  WriteTo(textWriter)
```

## Stack 2 — CLI whole-project export

```
[user shell]
└── ilspycmd -p -o out sample.dll
    └── ILSpyCmdProgram.cs:71  ILSpyCmdProgram.Main
        └── ILSpyCmdProgram.cs:236  OnExecuteAsync
            └── ILSpyCmdProgram.cs:275  DecompileAsProject(file, projectFileName)
                ├── PEFile + UniversalAssemblyResolver
                ├── new WholeProjectDecompiler(...)  (or BamlAwareWholeProjectDecompiler for --decompile-baml)
                └── WholeProjectDecompiler.DecompileProject(module, dir, writer)
                    ├── ProjectFileWriterSdkStyle.WriteProject
                    │   └── writes <assembly>.csproj
                    ├── for each TypeDefinition:
                    │   └── CSharpDecompiler.Decompile(type)  (→ Stack 1)
                    └── SolutionCreator.WriteSolutionFile  (if multiple inputs)
```

## Stack 3 — Single method body to AST

```
[embedding host]
└── CSharpDecompiler.Decompile(handle)                       (CSharpDecompiler.cs:1244)
    └── CSharpDecompiler.DoDecompile(IMethod, ...)             (CSharpDecompiler.cs:1993)
        └── CSharpDecompiler.DecompileBody(methodDef, ...)     (CSharpDecompiler.cs:2136)
            ├── new ILReader(typeSystem.MainModule)            (ILReader.cs:139)
            ├── ILReader.ReadIL(methodHandle, methodBody)      (ILReader.cs:720)
            │   ├── PeReaderExtensions.DecodeMethod (SRM)
            │   ├── stack-type inference
            │   └── UnionFind<ILVariable> reference merging
            ├── CreateILTransformContext(function)             (CSharpDecompiler.cs:869)
            ├── for each t in GetILTransforms():
            │   └── t.Run(function, context)
            │       ├── IL/Transforms/ControlFlowSimplification.cs
            │       ├── IL/Transforms/SplitVariables.cs
            │       ├── IL/Transforms/ILInlining.cs
            │       ├── IL/Transforms/InlineReturnTransform.cs
            │       ├── IL/Transforms/RemoveInfeasiblePathTransform.cs
            │       ├── IL/Transforms/DetectPinnedRegions.cs
            │       ├── IL/Transforms/YieldReturnDecompiler.cs
            │       ├── IL/Transforms/AsyncAwaitDecompiler.cs
            │       ├── IL/Transforms/DetectCatchWhenConditionBlocks.cs
            │       ├── IL/Transforms/DetectExitPoints.cs
            │       ├── IL/Transforms/LdLocaDupInitObjTransform.cs
            │       ├── IL/Transforms/EarlyExpressionTransforms.cs
            │       ├── IL/Transforms/SplitVariables.cs  (2nd)
            │       ├── IL/Transforms/RemoveDeadVariableInit.cs
            │       ├── IL/Transforms/ControlFlowSimplification.cs  (2nd)
            │       ├── IL/Transforms/DynamicCallSiteTransform.cs
            │       ├── IL/Transforms/SwitchDetection.cs
            │       ├── IL/Transforms/SwitchOnStringTransform.cs
            │       ├── IL/Transforms/SwitchOnNullableTransform.cs
            │       ├── IL/Transforms/SplitVariables.cs  (3rd)
            │       ├── IL/Transforms/IntroduceRefReadOnlyModifierOnLocals.cs
            │       ├── IL/Transforms/BlockILTransform { LoopDetection }
            │       ├── IL/Transforms/DetectExitPoints.cs  (re-run)
            │       ├── IL/Transforms/PatternMatchingTransform.cs
            │       ├── IL/Transforms/BlockILTransform { ConditionDetection, LockTransform, UsingTransform, CachedDelegateInitialization, StatementTransform { ILInlining + ExpressionTransforms + ... } }
            │       ├── IL/Transforms/ProxyCallReplacer.cs
            │       ├── IL/Transforms/FixRemainingIncrements.cs
            │       ├── IL/Transforms/CopyPropagation.cs
            │       ├── IL/Transforms/DelegateConstruction.cs
            │       ├── IL/Transforms/LocalFunctionDecompiler.cs
            │       ├── IL/Transforms/TransformDisplayClassUsage.cs
            │       ├── IL/Transforms/HighLevelLoopTransform.cs
            │       ├── IL/Transforms/ReduceNestingTransform.cs
            │       ├── IL/Transforms/RemoveRedundantReturn.cs
            │       ├── IL/Transforms/IntroduceDynamicTypeOnLocals.cs
            │       ├── IL/Transforms/IntroduceNativeIntTypeOnLocals.cs
            │       └── IL/Transforms/AssignVariableNames.cs
            ├── StatementBuilder.ConvertAsBlock(function.Body) (StatementBuilder.cs)
            ├── RunTransforms(syntaxTree, ...)                  (CSharpDecompiler.cs:727)
            │   └── CSharp/Transforms/*  16 IAstTransforms
            └── SyntaxTreeToString(syntaxTree)                  (CSharpDecompiler.cs:740)
                └── CSharpOutputVisitor.WriteTo(textWriter)    (OutputVisitor/CSharpOutputVisitor.cs)
```

## Stack 4 — ILAst pipeline (just the list)

See Stack 3 for the full sequence. The pipeline alone is the 30 transforms in `GetILTransforms()` (lines 88-176). Each transform implements `IILTransform.Run(function, context)`.

## Stack 5 — Control-flow graph construction

```
[IL/Transforms/* caller needing dominance info]
└── new ControlFlowGraph(container, ct)                       (IL/ControlFlow/ControlFlowGraph.cs:69)
    ├── allocate cfg[i] for each Block in container
    ├── CreateEdges(ct) — Branch -> edge; Leave -> nodeHasDirectExitOutOfContainer
    ├── Dominance.ComputeDominance(cfg[0], ct)                (FlowAnalysis/Dominance.cs)
    │   └── iterative fixed-point: cfg[n].ImmediateDominator = union of preds' dominators
    ├── Dominance.MarkNodesWithReachableExits
    │   └── propagates exit bit-set from successors
    └── FindNodesWithExitsOutOfContainer
        └── propagates exit bit-set across blocks

[consumer]
└── cfg[i].ImmediateDominator
└── cfg[i].ReachableExit
└── HasReachableExit(cfg[i])
```

## Stack 6 — async/await de-sugaring

```
[ILAst pipeline]
└── AsyncAwaitDecompiler.Run(function)                        (IL/ControlFlow/AsyncAwaitDecompiler.cs)
    ├── find IAsyncStateMachine.MoveNext() method
    ├── walk numeric state labels in the MoveNext switch
    ├── detect AwaitOnCompletion / AwaitUnsafeOnCompletion patterns
    │   └── match state transitions: state = -1 -> state = N -> AwaitOnCompletion -> ...
    ├── convert state-machine switch + `state = -1` initializer into C# await expressions
    │   └── replace MoveNext body with original method body containing `await`
    └── mark `function.IsAsync = true` so subsequent transforms (PatternMatchingTransform, ...) know to use async syntax
```

## Stack 7 — Plugin loading

```
[Avalonia]
└── App.OnFrameworkInitializationCompleted()                  (App.axaml.cs:36)
    └── AppComposition.Initialize()                           (AppEnv/AppComposition.cs:67)
        ├── RegisterPluginResolver()                          (AppComposition.cs:78)
        │   ├── AssemblyLoadContext.Default.Resolving += ResolvePluginDependency
        │   └── LoadPlugins()
        │       └── enumerate *.Plugin.dll in the executable directory
        │           └── AssemblyLoadContext.Default.LoadFromAssemblyPath(file)
        │               └── collect into composedAssemblies
        └── CreateContainer()                                 (AppComposition.cs:99)
            └── ContainerConfiguration().WithAssemblies(composedAssemblies).CreateContainer()
                └── App.Composition = host
    └── desktop.MainWindow = Composition?.GetExport<MainWindow>()
        └── MainWindow (composed) shown via Dock workspace
```

## Stack 8 — Avalonia GUI lifecycle

```
[process start]
└── ILSpy/Program.cs:35  Program.Main(args)
    └── BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)
        └── Avalonia creates App instance
            └── App.Initialize()                              (App.axaml.cs)
                └── AvaloniaXamlLoader.Load(this)             // loads App.axaml
            └── App.OnFrameworkInitializationCompleted()      (App.axaml.cs:36)
                ├── install ILSpyTraceListener
                ├── install GlobalExceptionHandler
                ├── CommandLineArguments.Create(args)
                ├── ILSpySettings.SettingsFilePathProvider   // Settings/ILSpySettings.cs
                ├── AppComposition.Initialize()                // MEF bootstrap (Stack 7)
                ├── ThemeManager.Current.Attach(settingsService.SessionSettings)
                ├── apply culture (--culture)
                └── desktop.MainWindow = Composition.GetExport<MainWindow>()
                    └── MainWindow (Avalonia Window + Dock workspace)
                        └── dock hosts: AssemblyTreePane, ContentTabPane, DebugStepsPane, ...
            └── desktop.Exit += (_,_) => Composition.GetExport<SettingsService>().Save(); Composition.Dispose()
```

## Stack 9 — Search

```
[user]
└── type "t:List" into SearchPane, press Enter
    └── SearchPane.axaml.cs  SearchPane.StartSearch
        └── SearchPaneModel.StartSearch()                     (Search/SearchPaneModel.cs)
            └── RunningSearch.Start(strategy)                  (Search/RunningSearch.cs)
                └── pick strategy from prefix:
                    ├── t:  AssemblySearchStrategy             (Search/AssemblySearchStrategy.cs)
                    ├── m:  MemberSearchStrategy               (Search/MemberSearchStrategy.cs)
                    ├── ns: NamespaceSearchStrategy            (Search/NamespaceSearchStrategy.cs)
                    ├── c:  LiteralSearchStrategy              (Search/LiteralSearchStrategy.cs)
                    ├── 0x: MetadataTokenSearchStrategy        (Search/MetadataTokenSearchStrategy.cs)
                    └── r:  ResourceSearchStrategy             (Search/ResourceSearchStrategy.cs)
                └── strategy.Search(args, ...)
                    └── iterate LoadedAssembly.TypeSystem.MainModule.TypeDefinitions
                    └── yield SearchResult per match
                        └── AvaloniaSearchResultFactory       (Search/AvaloniaSearchResultFactory.cs)
                            └── SharpTreeNode
                                └── SearchPane.TreeView.Items.Add
```

## Stack 10 — Multi-language output

```
[user selects language in dropdown]
└── LanguageSettings.SetLanguage(...)                         (ILSpy/LanguageSettings.cs)
    └── ContentTabPageModel.Decompile(member)                 (ViewModels/ContentTabPageModel.cs)
        ├── if CSharpLanguage:
        │   └── new CSharpDecompiler(module, resolver, settings).Decompile(member)
        │       └── CSharpOutputVisitor.WriteTo
        ├── if ILSpyILLanguage:
        │   └── new ReflectionDisassembler(...).WriteModuleContents(peFile) or .WriteMember
        └── if VBLanguage:
            └── legacy NRefactory VBDecompiler.Decompile(member)
```

## Stack 11 — HTML diagrammer

```
[user shell]
└── ilspycmd sample.dll --generate-diagrammer
    └── ILSpyCmdProgram.cs:71  Main
        └── ILSpyCmdProgram.cs:236  OnExecuteAsync
            └── ILSpyCmdProgram.cs  (GenerateDiagrammer == true) → command.Run()
                └── GenerateHtmlDiagrammer.Run()               (ICSharpCode.ILSpyX/MermaidDiagrammer/GenerateHtmlDiagrammer.cs)
                    ├── Factory.BuildTypes                     (MermaidDiagrammer/Factory.cs)
                    │   └── enumerate types from the assembly
                    ├── Factory.Relationships                  (MermaidDiagrammer/Factory.cs)
                    │   └── walk extends/implements/fields/properties/methods
                    ├── ClassDiagrammer.Render                 (MermaidDiagrammer/ClassDiagrammer.cs)
                    │   └── emit Mermaid `classDiagram` syntax
                    └── write diagrammer/index.html (+ model.json if --generate-diagrammer-json-only)
```

## Stack 12 — PDB generation

```
[user shell]
└── ilspycmd sample.dll -genpdb -o out
    └── ILSpyCmdProgram.cs:71  Main
        └── ILSpyCmdProgram.cs:236  OnExecuteAsync
            └── ILSpyCmdProgram.cs:330  GeneratePdbForAssembly(fileName, pdbFileName, app)
                ├── open PEFile + load each method body
                ├── new CSharpDecompiler(...).Decompile(member)  with DecompileMemberBodies = false
                │   └── short-circuits after AsyncAwaitDecompiler; only sets IsAsync/IsIterator
                └── CSharpDecompiler.CreateSequencePoints(syntaxTree)   (CSharpDecompiler.cs:2509)
                    └── walk ILInstruction.AddAnnotation(SequencePoint)
                └── PortablePdbBuilder (System.Reflection.Metadata) emits portable PDB
                └── write out/sample.pdb
```