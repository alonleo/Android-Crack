# 08 — `ICSharpCode.Decompiler` Core Engine

This file documents every catalogued function in `ICSharpCode.Decompiler/` (the core engine, 578 .cs files, ~85K LoC). The engine is `netstandard2.0` and ships as a NuGet package; consumers include `ICSharpCode.ILSpyX`, `ICSharpCode.ILSpyCmd`, the `ILSpy` GUI, the VS AddIn, the PowerShell cmdlets, and third parties (including dnSpy).

## `Decompiler.cs`

### `Decompiler` (public class)

- **位置**: `ICSharpCode.Decompiler/Decompiler.cs`
- **可见性**: public
- **简要说明**: Async facade over `CSharpDecompiler`; orchestrates engine + progress + cancellation.

#### `public Task<SyntaxTree> DecompileAsync(...)`

- **签名**: `Task<SyntaxTree> DecompileAsync(...)` (params vary by overload)
- **位置**: `ICSharpCode.Decompiler/Decompiler.cs:1` (specific line varies by overload)
- **可见性**: public
- **参数**: `DecompilerSettings settings`, `IProgress<DecompilationProgress> progress`, `CancellationToken cancellationToken`
- **返回值**: `Task<SyntaxTree>` — the decompiled NRefactory tree
- **抛出/异常**: `DecompilerException`, `OperationCanceledException`
- **副作用**: file I/O via `PEFile` ctor; emits progress events
- **调用**: 被 `ICSharpCode.Decompiler.PowerShell` cmdlet `DecompileAsync` 调用
- **调用了**: `CSharpDecompiler.DecompileWholeModuleAsSingleFile` (`CSharpDecompiler.cs:835`)

#### `public Task<string> DecompileTypeAsStringAsync(...)`

- **签名**: `Task<string> DecompileTypeAsStringAsync(...)`
- **位置**: `Decompiler.cs`
- **可见性**: public
- **简要说明**: text-output variant for a single type; uses `CSharpDecompiler.DecompileTypeAsString` internally

#### `public IAssemblyResolver AssemblyResolver { get; }`

- **位置**: `Decompiler.cs`
- **可见性**: public
- **简要说明**: the resolver instance held by this facade

## `DecompilerSettings.cs` (2450 LoC — property-heavy)

The settings class is `[Serializable] INotifyPropertyChanged` with ~200 properties. Every property is a toggle for one or more transforms in the pipeline. Listing every property exhaustively would be noise; the catalogued members below are the non-property API.

### `DecompilerSettings` (public class)

- **位置**: `ICSharpCode.Decompiler/DecompilerSettings.cs:30`
- **可见性**: public, `[Serializable]`
- **简要说明**: every decompiler option, observable; consumers bind via `INotifyPropertyChanged`.

#### `public DecompilerSettings()`

- **签名**: `DecompilerSettings()`
- **位置**: `DecompilerSettings.cs:35`
- **可见性**: public
- **简要说明**: default settings (`LanguageVersion = Latest`, all transforms enabled where reasonable)

#### `public DecompilerSettings(CSharp.LanguageVersion languageVersion)`

- **签名**: `DecompilerSettings(LanguageVersion)`
- **位置**: `DecompilerSettings.cs:48`
- **可见性**: public
- **简要说明**: settings pinned to a specific C# version (1..13, Preview, Latest)

#### `public void SetLanguageVersion(CSharp.LanguageVersion languageVersion)`

- **签名**: `void SetLanguageVersion(LanguageVersion)`
- **位置**: `DecompilerSettings.cs:56`
- **可见性**: public
- **抛出/异常**: none directly; raises `PropertyChanged`
- **调用了**: sets `LanguageVersion` + adjusts dependent toggles (e.g. `RecordClasses` for C# 9+)
- **简要说明**: update language version; may enable/disable dependent toggles

#### `public CSharp.LanguageVersion GetMinimumRequiredVersion()`

- **签名**: `LanguageVersion GetMinimumRequiredVersion()`
- **位置**: `DecompilerSettings.cs:182`
- **可见性**: public
- **返回值**: lowest `LanguageVersion` that can compile the output
- **简要说明**: computed from the currently enabled toggles; lets the GUI show a hint ("requires C# 9 or later")

#### `public bool NativeIntegers { get; set; }`

- **位置**: `DecompilerSettings.cs:234`
- **可见性**: public
- **简要说明**: use C# 9 `nint`/`nuint` for native-size integers

#### `public bool NumericIntPtr { get; set; }`

- **位置**: `DecompilerSettings.cs:252`
- **可见性**: public
- **简要说明**: use numeric `IntPtr`/`UIntPtr` (legacy)

#### `public bool RecordClasses { get; set; }`

- **位置**: `DecompilerSettings.cs:306`
- **可见性**: public
- **简要说明**: emit C# 9 record syntax for reference types

#### `public bool RecordStructs { get; set; }`

- **位置**: `DecompilerSettings.cs:324`
- **可见性**: public
- **简要说明**: emit C# 10 record syntax for value types

#### `public bool AsyncAwait { get; set; }`

- **位置**: `DecompilerSettings.cs:602`
- **可见性**: public
- **简要说明**: de-sugar async state machines to `async`/`await` (default true)

#### `public bool YieldReturn { get; set; }`

- **位置**: `DecompilerSettings.cs:566`
- **可见性**: public
- **简要说明**: de-sugar iterator state machines to `yield return`

#### `public bool Dynamic { get; set; }`

- **位置**: `DecompilerSettings.cs:584`
- **可见性**: public
- **简要说明**: preserve `dynamic` instead of downcasting to `object`

### Key settings properties (subset, alphabetical by name)

| Property | Line | Purpose |
|---|---:|---|
| `NativeIntegers` | 234 | use `nint`/`nuint` |
| `NumericIntPtr` | 252 | numeric `IntPtr`/`UIntPtr` |
| `CovariantReturns` | 270 | C# 9 covariant return types |
| `InitAccessors` | 288 | C# 9 `init`-only setters |
| `RecordClasses` | 306 | reference-type record syntax |
| `RecordStructs` | 324 | value-type record syntax |
| `StructDefaultConstructorsAndFieldInitializers` | 342 | C# 10 parameterless struct ctor |
| `WithExpressions` | 360 | C# 9 `with` expressions |
| `UsePrimaryConstructorSyntax` | 378 | C# 12 primary constructors |
| `FunctionPointers` | 397 | C# 9 function pointers |
| `ScopedRef` | 415 | C# 11 `scoped ref` |
| `LifetimeAnnotations` | 428 | experimental |
| `RequiredMembers` | 440 | C# 11 `required` |
| `SwitchExpressions` | 458 | C# 8 switch expression |
| `FileScopedNamespaces` | 476 | C# 10 file-scoped namespace |
| `AnonymousMethods` | 494 | `delegate { ... }` |
| `AnonymousTypes` | 512 | anonymous types |
| `UseLambdaSyntax` | 530 | prefer lambda over anonymous method |
| `ExpressionTrees` | 548 | preserve `Expression<T>` |
| `YieldReturn` | 566 | iterator de-sugaring |
| `Dynamic` | 584 | preserve `dynamic` |
| `AsyncAwait` | 602 | async/await de-sugaring |
| `AwaitInCatchFinally` | 621 | C# await in catch/finally |
| `AsyncEnumerator` | 640 | C# 8 `IAsyncEnumerable` |
| `DecimalConstants` | 658 | use `decimal` literals |

(The remaining ~140 properties live in the same file; consult `ICSharpCode.Decompiler/DecompilerSettings.cs` for the full list.)

### Other public API on `DecompilerSettings`

- `public bool UseDebugSymbols { get; set; }` — passes PDB info into `ILReader`
- `public bool ThrowOnAssemblyResolveErrors { get; set; }` — fail vs render `unknown` for missing refs
- `public int DecompilationMaxStepCount { get; set; }` — raises `StepLimitReachedException`
- `public bool RemoveDeadCode` / `RemoveDeadStores` — toggle dead-code / dead-store transforms
- `public bool UseSdkStyleProjectFormat` / `UseNestedDirectoriesForNamespaces` — project-export layout
- `public string? UserDefinedDebugInfoProviderAssembly` — pluggable `IDebugInfoProvider` (used by dnSpy)
- `public static List<IAssemblyResolver> AssemblyResolvers { get; }` — global resolver registration

## `CSharp/CSharpDecompiler.cs` (2517 LoC)

### `CSharpDecompiler` (public class) — `ICSharpCode.Decompiler/CSharp/CSharpDecompiler.cs:61`

- **可见性**: public
- **简要说明**: The main C# decompiler facade. Holds the `IDecompilerTypeSystem`, the `DecompilerSettings`, the `Stepper`, and the static pipeline definitions.

#### `public static List<IILTransform> GetILTransforms()`

- **签名**: `static List<IILTransform> GetILTransforms()`
- **位置**: `ICSharpCode.Decompiler/CSharp/CSharpDecompiler.cs:88-176`
- **可见性**: public, static
- **返回值**: 30 `IILTransform`s in execution order
- **抛出/异常**: none
- **副作用**: allocates fresh instances each call (so consumers can mutate / inspect)
- **调用**: 被 `CSharpDecompiler.ctor` 调用 (`CSharpDecompiler.cs:69`), `DecompileBody` 调用 (`CSharpDecompiler.cs:2156`), public API for plugins to extend
- **调用了**: ctor of every IILTransform in `ICSharpCode.Decompiler/IL/Transforms/`
- **简要说明**: **THE** 30-step ILAst pipeline. Order is documented inline; comments above each `new` call explain ordering constraints.

#### `public static List<IAstTransform> GetAstTransforms()`

- **签名**: `static List<IAstTransform> GetAstTransforms()`
- **位置**: `ICSharpCode.Decompiler/CSharp/CSharpDecompiler.cs:185`
- **可见性**: public, static
- **返回值**: 16 `IAstTransform`s
- **简要说明**: AST-layer pipeline (post-ILAst). See [08 ICSharpCode.Decompiler.CSharp](./02_ICSharpCode.Decompiler.CSharp.md) for the per-transform list.

#### `public Stepper Stepper { get; set; }`

- **位置**: `CSharpDecompiler.cs:180`
- **可见性**: public
- **简要说明**: pause / step hook for the Debug Steps pane

#### `public IDecompilerTypeSystem TypeSystem => typeSystem;`

- **位置**: `CSharpDecompiler.cs:214`
- **可见性**: public
- **简要说明**: the underlying type system

#### `public IDebugInfoProvider? DebugInfoProvider { get; set; }`

- **位置**: `CSharpDecompiler.cs:219`
- **可见性**: public
- **简要说明**: PDB provider

#### `public IDocumentationProvider? DocumentationProvider { get; set; }`

- **位置**: `CSharpDecompiler.cs:224`
- **可见性**: public
- **简要说明**: XML doc-comment provider

#### `public IList<IILTransform> ILTransforms`

- **位置**: `CSharpDecompiler.cs:229`
- **可见性**: public
- **简要说明**: the live list of IILTransforms (mutate to add / remove before decompiling)

#### `public IList<IAstTransform> AstTransforms`

- **位置**: `CSharpDecompiler.cs:236`
- **可见性**: public
- **简要说明**: the live list of IAstTransforms

#### `public CSharpDecompiler(string fileName, DecompilerSettings settings)`

- **签名**: `CSharpDecompiler(string fileName, DecompilerSettings settings)`
- **位置**: `CSharpDecompiler.cs:243`
- **可见性**: public
- **参数**: file name (any path that `FileLoaderRegistry` understands), settings
- **抛出/异常**: `FileNotFoundException`, `BadImageFormatException`, `DecompilerException`
- **副作用**: file I/O via PE loader
- **调用了**: `PEFile` ctor, `UniversalAssemblyResolver` ctor, `DecompilerTypeSystem.CreateAsync`

#### `public CSharpDecompiler(string fileName, IAssemblyResolver assemblyResolver, DecompilerSettings settings)`

- **位置**: `CSharpDecompiler.cs:251`
- **可见性**: public
- **参数**: file name, custom resolver, settings

#### `public CSharpDecompiler(MetadataFile module, IAssemblyResolver assemblyResolver, DecompilerSettings settings)`

- **位置**: `CSharpDecompiler.cs:259`
- **可见性**: public
- **参数**: pre-loaded `MetadataFile`, resolver, settings
- **简要说明**: for embedding hosts that already loaded the module

#### `public CSharpDecompiler(IDecompilerTypeSystem typeSystem, DecompilerSettings settings)`

- **位置**: `CSharpDecompiler.cs:267`
- **可见性**: public
- **参数**: pre-built type system, settings
- **简要说明**: skip type-system build entirely

#### `public static bool MemberIsHidden(MetadataFile? module, EntityHandle member, DecompilerSettings settings)`

- **签名**: `static bool MemberIsHidden(MetadataFile?, EntityHandle, DecompilerSettings)`
- **位置**: `CSharpDecompiler.cs:284`
- **可见性**: public, static
- **返回值**: should the tree hide this member?
- **简要说明**: applies `DecompilerSettings.MemberHider` heuristics (compiler-generated, special-name, ...)

#### `public SyntaxTree DecompileModuleAndAssemblyAttributes()`

- **签名**: `SyntaxTree DecompileModuleAndAssemblyAttributes()`
- **位置**: `CSharpDecompiler.cs:758`
- **可见性**: public
- **返回值**: tree containing only `[assembly: ...]` attributes and module-level custom attributes
- **简要说明**: cheap pre-pass for the assembly explorer header

#### `public string DecompileModuleAndAssemblyAttributesToString()`

- **位置**: `CSharpDecompiler.cs:773`
- **可见性**: public
- **简要说明**: text variant of the above

#### `public SyntaxTree DecompileWholeModuleAsSingleFile()`

- **签名**: `SyntaxTree DecompileWholeModuleAsSingleFile()`
- **位置**: `CSharpDecompiler.cs:835`
- **可见性**: public
- **返回值**: one `SyntaxTree` with all types in the module
- **抛出/异常**: `DecompilerException`, `OperationCanceledException`
- **副作用**: significant memory allocation; large modules may take seconds
- **调用**: 被 `IlspyCmdProgram.Decompile` 调用 (`ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:1`), `ContentTabPageModel.Decompile` (GUI)
- **调用了**: `DecompileModuleAndAssemblyAttributes`, `DoDecompileTypes`, `RunTransforms`
- **简要说明**: the whole-module entry point used by `-o out.cs`

#### `public SyntaxTree DecompileWholeModuleAsSingleFile(bool sortTypes)`

- **位置**: `CSharpDecompiler.cs:845`
- **可见性**: public
- **参数**: `sortTypes` — when true, types are sorted by name; when false, original order
- **简要说明**: same as above, with optional sorting

#### `public ILTransformContext CreateILTransformContext(ILFunction function)`

- **签名**: `ILTransformContext CreateILTransformContext(ILFunction function)`
- **位置**: `CSharpDecompiler.cs:869`
- **可见性**: public
- **简要说明**: builds the context object passed to every IILTransform.Run

#### `public static CodeMappingInfo GetCodeMappingInfo(MetadataFile module, EntityHandle member)`

- **签名**: `static CodeMappingInfo GetCodeMappingInfo(MetadataFile, EntityHandle)`
- **位置**: `CSharpDecompiler.cs:883`
- **可见性**: public, static
- **简要说明**: returns the decompilation sub-pieces (lambdas, FSMs, local funcs) that compose a logical method

#### `public string DecompileWholeModuleAsString()`

- **位置**: `CSharpDecompiler.cs:1155`
- **可见性**: public
- **简要说明**: text variant of `DecompileWholeModuleAsSingleFile`

#### `public SyntaxTree DecompileTypes(IEnumerable<TypeDefinitionHandle> types)`

- **位置**: `CSharpDecompiler.cs:1166`
- **可见性**: public
- **简要说明**: multi-type decompile (used by `WholeProjectDecompiler`)

#### `public SyntaxTree DecompileType(FullTypeName fullTypeName)`

- **位置**: `CSharpDecompiler.cs:1205`
- **可见性**: public
- **简要说明**: single-type decompile by name (used by GUI tree-node click)

#### `public SyntaxTree Decompile(params EntityHandle[] definitions)`

- **位置**: `CSharpDecompiler.cs:1236`
- **可见性**: public
- **简要说明**: single-entity entry, convenience overload

#### `public SyntaxTree Decompile(IEnumerable<EntityHandle> definitions)`

- **位置**: `CSharpDecompiler.cs:1244`
- **可见性**: public
- **抛出/异常**: `DecompilerException`, `OperationCanceledException`
- **调用**: 被 `ContentTabPageModel.Decompile` (GUI), `ICSharpCode.Decompiler.PowerShell` 调用
- **调用了**: `DoDecompile(IMethod, ...)` (`CSharpDecompiler.cs:1993`), `RunTransforms`
- **简要说明**: dispatches to the right `DoDecompile*` overload by `EntityHandle` kind

#### `public SyntaxTree DecompileExtension(EntityHandle handle)`

- **位置**: `CSharpDecompiler.cs:1330`
- **可见性**: public
- **简要说明**: extension-method group decompile (when `ExtensionMethods` setting is on)

#### `public string DecompileAsString(params EntityHandle[] definitions)`

- **位置**: `CSharpDecompiler.cs:1397`
- **可见性**: public
- **简要说明**: text variant of `Decompile`

#### `public string DecompileAsString(IEnumerable<EntityHandle> definitions)`

- **位置**: `CSharpDecompiler.cs:1405`
- **可见性**: public
- **简要说明**: text variant of `Decompile`

#### `public void AddPartialTypeDefinition(PartialTypeInfo info)`

- **位置**: `CSharpDecompiler.cs:1412`
- **可见性**: public
- **简要说明**: collect partial-type members across passes (used by round-trip tests)

#### `public Dictionary<ILFunction, List<DebugInfo.SequencePoint>> CreateSequencePoints(SyntaxTree syntaxTree)`

- **签名**: `Dictionary<ILFunction, List<SequencePoint>> CreateSequencePoints(SyntaxTree)`
- **位置**: `CSharpDecompiler.cs:2509`
- **可见性**: public
- **返回值**: map from `ILFunction` to its sequence points
- **调用**: 被 `IlspyCmdProgram.GeneratePdbForAssembly` (`IlspyCmdProgram.cs:330`) 调用
- **简要说明**: extracts the `ILInstruction` -> `SequencePoint` annotations

## `CSharp/OutputVisitor/CSharpOutputVisitor.cs` (3164 LoC)

### `CSharpOutputVisitor` (public class) — `ICSharpCode.Decompiler/CSharp/OutputVisitor/CSharpOutputVisitor.cs`

- **可见性**: public
- **简要说明**: walks the `SyntaxTree` and writes tokens to a `TextWriter`.

#### `public override void WriteTo(TextWriter textWriter)`

- **签名**: `override void WriteTo(TextWriter)`
- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override (from `DepthFirstAstVisitor`)
- **抛出/异常**: `IOException` from the underlying writer
- **副作用**: writes to `TextWriter`
- **调用**: 被 `CSharpDecompiler.SyntaxTreeToString` (`CSharpDecompiler.cs:740`) 调用, `ILSpy/Search/RunningSearch.cs` 调用 (for syntax-highlighted text)
- **简要说明**: top-level entry: walks the entire `SyntaxTree` and emits C# tokens.

#### `public override void VisitTypeDeclaration(TypeDeclaration typeDeclaration)`

- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override
- **简要说明**: emits one class/struct/interface declaration

#### `public override void VisitMethodDeclaration(MethodDeclaration methodDeclaration)`

- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override
- **简要说明**: emits one method (signature + body + braces + attributes)

#### `public override void VisitExpression(Expression expression)`

- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override
- **简要说明**: dispatches to per-expression-kind visitors

#### `public override void VisitInvocationExpression(InvocationExpression invocationExpression)`

- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override
- **简要说明**: emits `target(args)` or `target<typeargs>(args)`

#### `public override void VisitBinaryOperatorExpression(BinaryOperatorExpression binaryOperatorExpression)`

- **位置**: `CSharpOutputVisitor.cs:1`
- **可见性**: public, override
- **简要说明**: emits `a op b` with precedence-aware spacing

### Visitor decorators (wrapping the base visitor)

#### `InsertParenthesesVisitor`

- **位置**: `ICSharpCode.Decompiler/CSharp/OutputVisitor/InsertParenthesesVisitor.cs`
- **可见性**: public
- **简要说明**: walks the tree and adds parentheses when the parser would otherwise mis-bind

#### `InsertMissingTokensDecorator`

- **位置**: `ICSharpCode.Decompiler/CSharp/OutputVisitor/InsertMissingTokensDecorator.cs`
- **可见性**: public
- **简要说明**: synthesizes missing `;` `,` `{` `}` that the AST builder left out

#### `InsertRequiredSpacesDecorator`

- **位置**: `ICSharpCode.Decompiler/CSharp/OutputVisitor/InsertRequiredSpacesDecorator.cs`
- **可见性**: public
- **简要说明**: emits the spaces between adjacent tokens that the lexer would otherwise collapse

#### `GenericGrammarAmbiguityVisitor`

- **位置**: `ICSharpCode.Decompiler/CSharp/OutputVisitor/GenericGrammarAmbiguityVisitor.cs`
- **可见性**: public
- **简要说明**: resolves `a<b>(c)` ambiguity (is it a generic call or a comparison?)

## `CSharp/CallBuilder.cs` (2300 LoC)

### `CallBuilder` (internal class) — `ICSharpCode.Decompiler/CSharp/CallBuilder.cs`

#### `internal Expression Convert(Call call, ...)` (and overloads)

- **位置**: `CallBuilder.cs:1`
- **可见性**: internal
- **抛出/异常**: may throw `DecompilerException` on unresolvable overload
- **调用了**: `CSharpResolver`, `OverloadResolution`
- **简要说明**: turns an ILAst `Call`/`CallVirt` into the right C# form: `InvocationExpression`, `MemberReferenceExpression`, `ArrayAccess`, `PointerArithmetic`, conditional access chain, etc.

## `CSharp/ExpressionBuilder.cs` (5018 LoC — largest file)

### `ExpressionBuilder` (internal class) — `ICSharpCode.Decompiler/CSharp/ExpressionBuilder.cs`

#### `internal TranslatedExpression Convert(ILInstruction inst, ...)` (and many overloads)

- **位置**: `ExpressionBuilder.cs:1`
- **可见性**: internal
- **抛出/异常**: `DecompilerException` on unsupported patterns
- **调用**: 被 `CallBuilder` 调用, `StatementBuilder` 调用
- **调用了**: ~200 per-instruction visitors (`VisitLdLoc`, `VisitStLoc`, `VisitCall`, `VisitBinaryOperator`, ...)
- **简要说明**: top-level ILAst -> `Expression`. Returns `TranslatedExpression` (carries the `ResolveResult` for downstream resolvers).

## `CSharp/StatementBuilder.cs` (1586 LoC)

### `StatementBuilder` (internal class) — `ICSharpCode.Decompiler/CSharp/StatementBuilder.cs`

#### `internal BlockStatement ConvertAsBlock(Block block)`

- **位置**: `StatementBuilder.cs:1`
- **可见性**: internal
- **抛出/异常**: `DecompilerException`
- **调用了**: `Convert(ILInstruction)` for each statement
- **简要说明**: turns the ILAst `Block` into a `BlockStatement`.

#### `internal Statement Convert(ILInstruction inst)` (and overloads)

- **位置**: `StatementBuilder.cs:1`
- **可见性**: internal
- **简要说明**: dispatches by instruction kind to per-statement builders.

## `CSharp/ProjectDecompiler/WholeProjectDecompiler.cs`

### `WholeProjectDecompiler` (public class) — `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/WholeProjectDecompiler.cs`

#### `public ProjectId DecompileProject(MetadataFile module, string targetDir, TextWriter writer)`

- **签名**: `ProjectId DecompileProject(MetadataFile, string targetDir, TextWriter)`
- **位置**: `WholeProjectDecompiler.cs:1`
- **可见性**: public
- **抛出/异常**: `IOException`, `DecompilerException`
- **副作用**: writes files to disk via `ProjectFileWriter`
- **调用**: 被 `IlspyCmdProgram.DecompileAsProject` (`IlspyCmdProgram.cs:275`) 调用, `BamlAwareWholeProjectDecompiler.DecompileProject`
- **调用了**: `ProjectFileWriterSdkStyle.WriteProject`, `CSharpDecompiler.DecompileTypes`, `SolutionCreator.WriteSolutionFile`
- **简要说明**: whole-project decompile entry used by `-p`.

#### `public bool CanUseSdkStyleProjectFormat { get; }`

- **位置**: `WholeProjectDecompiler.cs:1`
- **可见性**: public
- **简要说明**: true when the input assembly is modern enough to be packaged as an SDK-style .csproj.

## `CSharp/Resolver/CSharpResolver.cs` (2986 LoC)

### `CSharpResolver` (public class) — `ICSharpCode.Decompiler/CSharp/Resolver/CSharpResolver.cs`

#### `public ResolveResult ResolveSimpleName(string identifier, ...)` (and overloads)

- **位置**: `CSharpResolver.cs:1`
- **可见性**: public
- **返回值**: `ResolveResult` — what the identifier refers to (or `ErrorResolveResult`)
- **抛出/异常**: `DecompilerException` on internal inconsistency
- **调用**: 被 `CallBuilder`, `ExpressionBuilder`, `CSharpOutputVisitor` 调用
- **调用了**: `CSharpConversions`, `OverloadResolution`, `TypeInference`, `MemberLookup`
- **简要说明**: walks the using-scope and produces a `ResolveResult` for the identifier.

## `IL/ILReader.cs` (2191 LoC)

### `ILReader` (public class) — `ICSharpCode.Decompiler/IL/ILReader.cs:46`

- **可见性**: public
- **简要说明**: turns ECMA-335 CIL bytes into an ILAst (`ILFunction`) with stack-type inference. **NOT thread-safe** — use one instance per parallel member.

#### `public ILReader(MetadataModule module)`

- **签名**: `ILReader(MetadataModule module)`
- **位置**: `ILReader.cs:139`
- **可见性**: public
- **参数**: module to read from
- **简要说明**: bind to a `MetadataModule` (one per .dll/.exe/.winmd)

#### `public bool UseDebugSymbols { get; set; }`

- **位置**: `ILReader.cs:124`
- **可见性**: public
- **简要说明**: when true, local names come from PDB

#### `public bool UseRefLocalsForAccurateOrderOfEvaluation { get; set; }`

- **位置**: `ILReader.cs:125`
- **可见性**: public
- **简要说明**: introduce `ref` locals to model side-effect ordering

#### `public IDebugInfoProvider? DebugInfo { get; set; }`

- **位置**: `ILReader.cs:126`
- **可见性**: public
- **简要说明**: PDB provider

#### `public List<string> Warnings { get; }`

- **位置**: `ILReader.cs:127`
- **可见性**: public, read-only
- **简要说明**: import-time warnings

#### `public List<int> SequencePointCandidates { get; }`

- **位置**: `ILReader.cs:131`
- **可见性**: public, read-only
- **简要说明**: IL offsets that may correspond to source lines

#### `public void WriteTypedIL(MethodDefinitionHandle method, MethodBodyBlock body, GenericContext genericContext = default, CancellationToken cancellationToken = default)`

- **位置**: `ILReader.cs:688`
- **可见性**: public
- **简要说明**: debug helper — emit typed-IL view

#### `public ILFunction ReadIL(MethodDefinitionHandle method, MethodBodyBlock body, GenericContext genericContext = default, ILFunctionKind kind = ILFunctionKind.TopLevelFunction, CancellationToken cancellationToken = default)`

- **签名**: `ILFunction ReadIL(MethodDefinitionHandle, MethodBodyBlock, GenericContext, ILFunctionKind, CancellationToken)`
- **位置**: `ILReader.cs:720`
- **可见性**: public
- **抛出/异常**: `OperationCanceledException`, `BadImageFormatException`
- **调用**: 被 `CSharpDecompiler.DecompileBody` (`CSharpDecompiler.cs:2156`) 调用
- **调用了**: `PeReaderExtensions.DecodeMethod` (SRM), `StackType` inference, `UnionFind<ILVariable>` reference merging
- **简要说明**: **THE** entry point — CIL bytes -> `ILFunction`.

#### `internal static ILInstruction Cast(ILInstruction inst, StackType expectedType, List<string>? warnings, int ilOffset)`

- **位置**: `ILReader.cs:1398`
- **可见性**: internal, static
- **简要说明**: coerce operand to expected stack type (insert cast, box, etc.)

### `ILReader.CollectStackVariablesVisitor` (private nested class) — `ILReader.cs:1289`

- **可见性**: private sealed
- **简要说明**: helper that collects variables discovered on the stack during import.

## `IL/Instructions/ILFunction.cs`

### `ILFunction` (public class) — `ICSharpCode.Decompiler/IL/Instructions/ILFunction.cs`

#### `public BlockContainer Body { get; set; }`

- **位置**: `ILFunction.cs:1`
- **可见性**: public
- **简要说明**: root `BlockContainer` of the ILAst

#### `public IList<ILVariable> Variables { get; }`

- **位置**: `ILFunction.cs:1`
- **可见性**: public, read-only
- **简要说明**: declared locals

#### `public bool IsAsync { get; }`

- **位置**: `ILFunction.cs:1`
- **可见性**: public
- **简要说明**: compiler-generated async state machine?

#### `public bool IsIterator { get; }`

- **位置**: `ILFunction.cs:1`
- **可见性**: public
- **简要说明**: compiler-generated iterator state machine?

#### `public List<string> Warnings { get; }`

- **位置**: `ILFunction.cs:1`
- **可见性**: public, read-only
- **简要说明**: import warnings collected by `ILReader`

## `IL/ControlFlow/ControlFlowGraph.cs`

### `ControlFlowGraph` (public class) — `ICSharpCode.Decompiler/IL/ControlFlow/ControlFlowGraph.cs`

#### `public ControlFlowGraph(BlockContainer container, CancellationToken cancellationToken)`

- **签名**: `ControlFlowGraph(BlockContainer, CancellationToken)`
- **位置**: `ICSharpCode.Decompiler/IL/ControlFlow/ControlFlowGraph.cs:69`
- **可见性**: public
- **抛出/异常**: `OperationCanceledException`
- **调用了**: `CreateEdges`, `Dominance.ComputeDominance`
- **简要说明**: builds the CFG from an ILAst block container.

#### `public IReadOnlyList<ControlFlowNode> Nodes { get; }`

- **位置**: `ControlFlowGraph.cs:1`
- **可见性**: public
- **简要说明**: array of CFG nodes (one per `Block` in the container)

#### `public bool HasReachableExit(ControlFlowNode node)`

- **位置**: `ControlFlowGraph.cs:1`
- **可见性**: public
- **简要说明**: is there a path from `node` to an exit of the container?

## `IL/ControlFlow/AsyncAwaitDecompiler.cs`

### `AsyncAwaitDecompiler` (public class) — `ICSharpCode.Decompiler/IL/ControlFlow/AsyncAwaitDecompiler.cs`

#### `public override void Run(ILFunction function)`

- **位置**: `AsyncAwaitDecompiler.cs:1`
- **可见性**: public, override (`IILTransform`)
- **抛出/异常**: `DecompilerException` on unrecognized state-machine pattern
- **调用**: `GetILTransforms()` (line 100)
- **调用了**: walk numeric state labels, detect `AwaitOnCompletion`/`AwaitUnsafeOnCompletion`
- **简要说明**: rewrites a compiler-generated async state machine into C# `await` in the original method body.

## `IL/ControlFlow/YieldReturnDecompiler.cs`

### `YieldReturnDecompiler` (public class) — `ICSharpCode.Decompiler/IL/ControlFlow/YieldReturnDecompiler.cs`

#### `public override void Run(ILFunction function)`

- **位置**: `YieldReturnDecompiler.cs:1`
- **可见性**: public, override (`IILTransform`)
- **抛出/异常**: `DecompilerException`
- **调用**: `GetILTransforms()` (line 99)
- **简要说明**: rewrites an iterator state machine into C# `yield return`.

## `TypeSystem/DecompilerTypeSystem.cs`

### `DecompilerTypeSystem` (public class) — `ICSharpCode.Decompiler/TypeSystem/DecompilerTypeSystem.cs`

#### `public static Task<DecompilerTypeSystem> CreateAsync(PEFile module, IAssemblyResolver assemblyResolver)`

- **签名**: `static Task<DecompilerTypeSystem> CreateAsync(PEFile, IAssemblyResolver)`
- **位置**: `DecompilerTypeSystem.cs:127`
- **可见性**: public, static
- **返回值**: ready-to-use type system
- **抛出/异常**: `DecompilerException`, `OperationCanceledException`
- **调用**: 被 `CSharpDecompiler.ctor` 调用 (`CSharpDecompiler.cs:243 / 251`)
- **调用了**: `MetadataReader` (SRM), `MetadataExtensions`, `KnownAttributes`
- **简要说明**: builds the decompiler `ICompilation` from a PE file.

#### `public static DecompilerTypeSystem Create(MetadataFile module, IAssemblyResolver assemblyResolver, DecompilerSettings settings)`

- **位置**: `DecompilerTypeSystem.cs:1`
- **可见性**: public, static
- **简要说明**: sync factory (when settings already available)

#### `public static TypeSystemOptions GetOptions(DecompilerSettings settings)`

- **位置**: `DecompilerTypeSystem.cs:1`
- **可见性**: public, static
- **返回值**: `TypeSystemOptions` flags derived from settings
- **简要说明**: enables `ExtensionMethods`, `Tuple`, `Dynamic`, `NullabilityAnnotations` etc. based on settings.

### `[Flags] enum TypeSystemOptions`

- **位置**: `DecompilerTypeSystem.cs:1`
- **简要说明**: `Dynamic=1, Tuple=2, ExtensionMethods=4, OnlyPublicAPI=8, Uncached=0x10, ... ExtensionMembers=0x80000, RuntimeAsync=0x100000, Default=...`

## `Metadata/UniversalAssemblyResolver.cs`

### `UniversalAssemblyResolver` (public class) — `ICSharpCode.Decompiler/Metadata/UniversalAssemblyResolver.cs`

#### `public UniversalAssemblyResolver(string fileName, bool throwOnError, TargetFrameworkIdentifier tfi, TargetFrameworkMoniker tfm, IEnumerable<string>? searchDirs, IEnumerable<string>? resourceSearchDirs = null, MetadataReaderOptions metadataOptions = MetadataReaderOptions.Default, CancellationToken cancellationToken = default)`

- **签名**: ctor with full arg list (see file)
- **位置**: `UniversalAssemblyResolver.cs:1`
- **可见性**: public
- **抛出/异常**: `FileNotFoundException` when `throwOnError`
- **调用**: 被 `CSharpDecompiler.ctor` 调用, `IlspyCmdProgram.GetDecompiler` 调用
- **调用了**: `DotNetCorePathFinder`, file I/O
- **简要说明**: resolves `AssemblyRef` to files on disk / NuGet / shared framework.

#### `public void AddSearchDirectory(string directory)`

- **位置**: `UniversalAssemblyResolver.cs:1`
- **可见性**: public
- **简要说明**: add a path to the search list (`-r` in the CLI).

#### `public Task<PEFile?> ResolveAsync(IAssemblyReference reference)`

- **签名**: `Task<PEFile?> ResolveAsync(IAssemblyReference)`
- **位置**: `UniversalAssemblyResolver.cs:1`
- **可见性**: public
- **返回值**: the resolved `PEFile`, or null
- **抛出/异常**: `OperationCanceledException`
- **简要说明**: async AssemblyRef -> PEFile resolution.

#### `public Task<PEFile?> ResolveModuleAsync(ModuleReference moduleReference)`

- **位置**: `UniversalAssemblyResolver.cs:1`
- **可见性**: public
- **简要说明**: async ModuleRef resolution.

## `Disassembler/ReflectionDisassembler.cs`

### `ReflectionDisassembler` (public class) — `ICSharpCode.Decompiler/Disassembler/ReflectionDisassembler.cs`

#### `public void WriteModuleContents(PEFile module)` (and overloads)

- **位置**: `ReflectionDisassembler.cs:1`
- **可见性**: public
- **抛出/异常**: `IOException` from the writer
- **调用**: 被 `IlspyCmdProgram` `-il` branch (`IlspyCmdProgram.cs:1`) 调用, `ContentTabPageModel.Decompile` for IL view (GUI)
- **调用了**: `MethodBodyDisassembler.WriteMethodBody`, `DisassemblerHelpers.WriteType`...
- **简要说明**: writes the entire module as IL text to a `TextWriter`.

#### `public void WriteMember(...)` (overloads for method/type/property/field/event)

- **位置**: `ReflectionDisassembler.cs:1`
- **可见性**: public
- **简要说明**: write a single member as IL.