# 08 — `ICSharpCode.Decompiler.CSharp` (AST, builders, transforms)

This file documents the C# AST layer. The biggest categories are the visitors (`CSharpOutputVisitor`), the transforms (IL-level 30-step pipeline + AST-level 16-step pipeline), and the resolver.

## `CSharp/ProjectDecompiler/WholeProjectDecompiler.cs`

See [01_ICSharpCode.Decompiler.md#wholeprojectdecompiler](./01_ICSharpCode.Decompiler.md) for the primary entries.

### `ProjectFileWriterSdkStyle`

- **位置**: `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/ProjectFileWriterSdkStyle.cs`
- **可见性**: public
- **简要说明**: writes an SDK-style .csproj (netstandard2.0+ projects).

### `ProjectFileWriterDefault`

- **位置**: `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/ProjectFileWriterDefault.cs`
- **可见性**: public
- **简要说明**: writes a legacy (non-SDK-style) .csproj.

### `IProjectFileWriter`

- **位置**: `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/IProjectFileWriter.cs`
- **可见性**: public
- **简要说明**: contract for the two writers above.

### `TargetFramework` / `TargetServices`

- **位置**: `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/TargetFramework.cs`
- **可见性**: public
- **简要说明**: info classes about the target framework the decompiled code should compile against.

### `IProjectInfoProvider`

- **位置**: `ICSharpCode.Decompiler/CSharp/ProjectDecompiler/IProjectInfoProvider.cs`
- **可见性**: public
- **简要说明**: supplies the info needed by the project file writer.

## `CSharp/Syntax/` (NRefactory AST nodes)

The `Syntax` directory contains ~100 files implementing the NRefactory AST hierarchy. The base class is `AstNode`.

### `AstNode` (public abstract class) — `ICSharpCode.Decompiler/CSharp/Syntax/AstNode.cs`

- **位置**: `AstNode.cs:1` (1075 LoC)
- **可见性**: public, abstract
- **简要说明**: AST base — parent pointer, annotations, traversal, child roles.

#### `public AstNode Parent`

- **可见性**: public
- **简要说明**: back-pointer to the parent

#### `public T? GetParent<T>()` (and many helpers)

- **位置**: `AstNode.cs:1`
- **可见性**: public
- **简要说明**: traverse up to the nearest ancestor of type T

#### `public IEnumerable<AstNode> Descendants` / `DescendantNodes`

- **可见性**: public
- **简要说明**: depth-first traversal

#### `public abstract void AcceptVisitor(IAstVisitor visitor)`

- **位置**: `AstNode.cs:1`
- **可见性**: public, abstract
- **调用**: every visitor enters through this
- **简要说明**: dispatch to `visitor.Visit*(this)`

#### `public void AddAnnotation(object annotation)`

- **位置**: `AstNode.cs:1`
- **可见性**: public
- **简要说明**: attach arbitrary data to a node

#### `public T? GetAnnotation<T>()`

- **位置**: `AstNode.cs:1`
- **可见性**: public
- **简要说明**: retrieve attached annotation by type

### Concrete AstNode types (file per type, listed by category)

#### Type expressions (in `Syntax/`)

- `PrimitiveType` (`Syntax/PrimitiveType.cs`)
- `ComposedType` (`Syntax/ComposedType.cs`) — `int[]`, `List<int>[]`, ...
- `MemberType` (`Syntax/MemberType.cs`) — `Namespace.Type`
- `SimpleType` (`Syntax/SimpleType.cs`)
- `TupleAstType` (`Syntax/TupleAstType.cs`)
- `FunctionPointerAstType` (`Syntax/FunctionPointerAstType.cs`)
- `InvocationAstType` (`Syntax/InvocationAstType.cs`)
- `ArrayType` (in `TypeSystem/`)
- `PointerType` (in `TypeSystem/`)
- `ByReferenceType` (in `TypeSystem/`)

#### Statements (in `Syntax/Statements/`, 21 classes)

- `BlockStatement`, `IfElseStatement`, `ForStatement`, `ForEachStatement`, `WhileStatement`, `DoWhileStatement`, `SwitchStatement`, `TryCatchStatement`, `UsingStatement`, `LockStatement`, `ReturnStatement`, `BreakStatement`, `ContinueStatement`, `ThrowStatement`, `GotoStatement`, `LabelStatement`, `ExpressionStatement`, `FixedStatement`, `CheckedStatement`, `UncheckedStatement`, `YieldStatement`, `EmptyStatement`

#### Expressions (in `Syntax/Expressions/`, 50+ classes)

- `AssignmentExpression`, `BinaryOperatorExpression`, `UnaryOperatorExpression`, `ConditionalExpression`, `InvocationExpression`, `MemberReferenceExpression`, `IdentifierExpression`, `PrimitiveExpression`, `NullReferenceExpression`, `ThisReferenceExpression`, `BaseReferenceExpression`, `ArrayCreateExpression`, `ArrayInitializerExpression`, `ObjectCreateExpression`, `CollectionInitializerExpression`, `CastExpression`, `AsExpression`, `IsExpression`, `TypeOfExpression`, `DefaultValueExpression`, `SizeOfExpression`, `CheckedExpression`, `LambdaExpression`, `AnonymousMethodExpression`, `AnonymousTypeCreateExpression`, `TupleExpression`, `NamedExpression`, `NamedArgumentExpression`, `DirectionExpression`, `IndexerExpression`, `ParenthesizedExpression`, `QueryExpression`, `QueryContinuationExpression`, `QueryFromClause`, `QuerySelectClause`, `QueryWhereClause`, `QueryOrderClause`, `QueryGroupClause`, `QueryJoinClause`, `QueryLetClause`, `InterpolatedStringExpression`, `PatternExpression`, `RecursivePattern`, `ListPattern`, `SwitchExpression`, `SwitchSection`, `StackAllocExpression`, `AwaitExpression`, ...

#### Pattern matching (in `Syntax/PatternMatching/`)

- `PatternAst` (base), `ListPattern`, `RecursivePattern`, `ConstantPattern`, `TypePattern`, `VarPattern`, `DeclarationPattern`, `BinaryPattern`, `UnaryPattern`, ...

#### Type members (in `Syntax/TypeMembers/`)

- `TypeDeclaration`, `MethodDeclaration`, `PropertyDeclaration`, `FieldDeclaration`, `EventDeclaration`, `IndexerDeclaration`, `ConstructorDeclaration`, `DestructorDeclaration`, `OperatorDeclaration`, `EnumMemberDeclaration`, `DelegateDeclaration`, `Accessor`, ...

#### Other

- `DocumentationReference` (`Syntax/DocumentationReference.cs`)
- `Identifier` (`Syntax/Identifier.cs`)
- `IAnnotatable` (`Syntax/IAnnotatable.cs`)
- `Modifiers` (`Syntax/Modifiers.cs`)
- `Tokens` (`Syntax/Tokens.cs`) — token kinds for trivia reconstruction
- `SyntaxTree` (`Syntax/SyntaxTree.cs`) — root `AstNode` subclass

## `CSharp/Transforms/` (21 AST transforms)

The AST-layer pipeline (`GetAstTransforms()` at `CSharpDecompiler.cs:185`) runs after the ILAst pipeline. Each transform below is a single `IAstTransform` subclass.

### `PatternStatementTransform`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/PatternStatementTransform.cs`
- **可见性**: public
- **调用**: `GetAstTransforms()`
- **简要说明**: rewrites `if (x is T y) y.Foo()` into `switch` patterns.

### `ReplaceMethodCallsWithOperators`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/ReplaceMethodCallsWithOperators.cs`
- **可见性**: public
- **简要说明**: turns `a.op_Addition(b)` into `a + b`.

### `DeclareVariables`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/DeclareVariables.cs`
- **可见性**: public
- **简要说明**: hoists `var x = ...` declarations to first use.

### `TransformFieldAndConstructorInitializers`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/TransformFieldAndConstructorInitializers.cs`
- **可见性**: public
- **简要说明**: flattens field initializers into constructors when appropriate.

### `IntroduceExtensionMethods`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/IntroduceExtensionMethods.cs`
- **可见性**: public
- **简要说明**: turns static-method calls into extension-method syntax.

### `IntroduceUsingDeclarations`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/IntroduceUsingDeclarations.cs`
- **可见性**: public
- **简要说明**: collects `using` namespaces per file.

### `IntroduceQueryExpressions`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/IntroduceQueryExpressions.cs`
- **可见性**: public
- **简要说明**: detects LINQ chains and rewrites them as `from ... in ... select` syntax.

### `CombineQueryExpressions`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/CombineQueryExpressions.cs`
- **可见性**: public
- **简要说明**: merges adjacent `from` clauses into one.

### `IntroduceUnsafeModifier`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/IntroduceUnsafeModifier.cs`
- **可见性**: public
- **简要说明**: adds `unsafe` modifier to types/methods that contain pointer code.

### `AddCheckedBlocks`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/AddCheckedBlocks.cs`
- **可见性**: public
- **简要说明**: wraps arithmetic in `checked { ... }` per `DecompilerSettings.FoldChecked` setting.

### `NormalizeBlockStatements`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/NormalizeBlockStatements.cs`
- **可见性**: public
- **简要说明**: collapses single-statement blocks.

### `FlattenSwitchBlocks`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/FlattenSwitchBlocks.cs`
- **可见性**: public
- **简要说明**: merges adjacent cases.

### `FixNameCollisions`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/FixNameCollisions.cs`
- **可见性**: public
- **简要说明**: renames locals when they collide with type names.

### `PrettifyAssignments`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/PrettifyAssignments.cs`
- **可见性**: public
- **简要说明**: combines `x = x + 1` into `x += 1`; etc.

### `AddXmlDocumentationTransform`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/AddXmlDocumentationTransform.cs`
- **可见性**: public
- **简要说明**: attaches XML doc comments to declarations.

### `EscapeInvalidIdentifiers`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/EscapeInvalidIdentifiers.cs`
- **可见性**: public
- **简要说明**: escapes identifiers that would not compile (e.g. `@class`).

### `RemoveCLSCompliantAttribute`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/RemoveCLSCompliantAttribute.cs`
- **可见性**: public
- **简要说明**: removes CLS-compliant attributes when redundant.

### `IAstTransform` (interface) — `ICSharpCode.Decompiler/CSharp/Transforms/IAstTransform.cs`

#### `void Run(SyntaxTree syntaxTree)` / `void Run(AstNode compilationUnit)`

- **可见性**: public
- **抛出/异常**: may throw `DecompilerException`
- **简要说明**: the contract each transform implements

### `TransformContext` — `ICSharpCode.Decompiler/CSharp/Transforms/TransformContext.cs`

- **可见性**: public
- **简要说明**: per-decompilation shared state passed to AST transforms (settings, type-system, cancellation).

### `ContextTrackingVisitor`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/ContextTrackingVisitor.cs`
- **可见性**: public
- **简要说明**: base visitor that tracks `TransformContext` while walking.

### `CustomPatterns`

- **位置**: `ICSharpCode.Decompiler/CSharp/Transforms/CustomPatterns.cs`
- **可见性**: public
- **简要说明**: pattern combinators used by the AST transforms.

## `CSharp/Resolver/` (C# language services)

### `CSharpResolver` — `ICSharpCode.Decompiler/CSharp/Resolver/CSharpResolver.cs`

Documented in [01_ICSharpCode.Decompiler.md](./01_ICSharpCode.Decompiler.md). 2986 LoC; public surface covers name resolution, member lookup, overload resolution, conversion checking.

### `CSharpConversions` — `ICSharpCode.Decompiler/CSharp/Resolver/CSharpConversions.cs`

- **可见性**: public
- **简要说明**: implicit / explicit conversion rules per the C# spec.

### `CSharpOperators` — `ICSharpCode.Decompiler/CSharp/Resolver/CSharpOperators.cs`

- **可见性**: public
- **简要说明**: operator overload resolution.

### `OverloadResolution` — `ICSharpCode.Decompiler/CSharp/Resolver/OverloadResolution.cs`

- **可见性**: public
- **简要说明**: the standard 4-phase overload-resolution algorithm.

### `TypeInference` — `ICSharpCode.Decompiler/CSharp/Resolver/TypeInference.cs`

- **可见性**: public
- **简要说明**: generic-method type-argument inference.

### `MemberLookup` — `ICSharpCode.Decompiler/CSharp/Resolver/MemberLookup.cs`

- **可见性**: public
- **简要说明**: name -> member lookup per the C# spec.

### `MethodGroupResolveResult` — `ICSharpCode.Decompiler/CSharp/Resolver/MethodGroupResolveResult.cs`

- **可见性**: public
- **简要说明**: a set of candidate methods from a name lookup.

### `LambdaResolveResult` — `ICSharpCode.Decompiler/CSharp/Resolver/LambdaResolveResult.cs`

- **可见性**: public
- **简要说明**: a lambda's type, parameters, body, return type.

### `OverloadResolutionErrors` — `ICSharpCode.Decompiler/CSharp/Resolver/OverloadResolutionErrors.cs`

- **可见性**: public
- **简要说明**: structured overload-resolution failure info.

### `Log` — `ICSharpCode.Decompiler/CSharp/Resolver/Log.cs`

- **可见性**: public
- **简要说明**: warning sink for resolution issues.

## `IL/Transforms/` (49 IL transforms)

These run BEFORE the AST pipeline and form the bulk of the ILAst -> de-sugared-ILAst work. The order matters; see [05_operation_chains.md Chain 4](../05_operation_chains.md).

### Critical ordering transforms (must run before loop detection)

| Transform | File |
|---|---|
| `ControlFlowSimplification` | `IL/Transforms/ControlFlowSimplification.cs` |
| `SplitVariables` | `IL/Transforms/SplitVariables.cs` |
| `ILInlining` | `IL/Transforms/ILInlining.cs` |
| `InlineReturnTransform` | `IL/Transforms/InlineReturnTransform.cs` |
| `RemoveInfeasiblePathTransform` | `IL/Transforms/RemoveInfeasiblePathTransform.cs` |
| `DetectPinnedRegions` | `IL/Transforms/DetectPinnedRegions.cs` |
| `YieldReturnDecompiler` | `IL/Transforms/YieldReturnDecompiler.cs` (alias for `IL/ControlFlow/YieldReturnDecompiler.cs`) |
| `AsyncAwaitDecompiler` | `IL/Transforms/AsyncAwaitDecompiler.cs` (alias for `IL/ControlFlow/AsyncAwaitDecompiler.cs`) |
| `DetectCatchWhenConditionBlocks` | `IL/Transforms/DetectCatchWhenConditionBlocks.cs` |
| `DetectExitPoints` | `IL/Transforms/DetectExitPoints.cs` |
| `LdLocaDupInitObjTransform` | `IL/Transforms/LdLocaDupInitObjTransform.cs` |
| `EarlyExpressionTransforms` | `IL/Transforms/EarlyExpressionTransforms.cs` |
| `RemoveDeadVariableInit` | `IL/Transforms/RemoveDeadVariableInit.cs` |
| `DynamicCallSiteTransform` | `IL/Transforms/DynamicCallSiteTransform.cs` |
| `SwitchDetection` | `IL/Transforms/SwitchDetection.cs` |
| `SwitchOnStringTransform` | `IL/Transforms/SwitchOnStringTransform.cs` |
| `SwitchOnNullableTransform` | `IL/Transforms/SwitchOnNullableTransform.cs` |
| `IntroduceRefReadOnlyModifierOnLocals` | `IL/Transforms/IntroduceRefReadOnlyModifierOnLocals.cs` |
| `LoopDetection` | `IL/Transforms/LoopDetection.cs` |
| `PatternMatchingTransform` | `IL/Transforms/PatternMatchingTransform.cs` |
| `ConditionDetection` | `IL/Transforms/ConditionDetection.cs` |
| `LockTransform` | `IL/Transforms/LockTransform.cs` |
| `UsingTransform` | `IL/Transforms/UsingTransform.cs` |
| `CachedDelegateInitialization` | `IL/Transforms/CachedDelegateInitialization.cs` |

### Per-block interleaved transforms

| Transform | File |
|---|---|
| `StatementTransform` | `IL/Transforms/StatementTransform.cs` (driver) |
| `ILInlining(AllowInliningOfLdloca)` | `IL/Transforms/ILInlining.cs` |
| `ExpressionTransforms` | `IL/Transforms/ExpressionTransforms.cs` |
| `DynamicIsEventAssignmentTransform` | `IL/Transforms/DynamicIsEventAssignmentTransform.cs` |
| `TransformAssignment` | `IL/Transforms/TransformAssignment.cs` |
| `NullCoalescingTransform` | `IL/Transforms/NullCoalescingTransform.cs` |
| `NullableLiftingStatementTransform` | `IL/Transforms/NullableLiftingStatementTransform.cs` |
| `NullPropagationStatementTransform` | `IL/Transforms/NullPropagationStatementTransform.cs` |
| `TransformArrayInitializers` | `IL/Transforms/TransformArrayInitializers.cs` |
| `TransformCollectionAndObjectInitializers` | `IL/Transforms/TransformCollectionAndObjectInitializers.cs` |
| `TransformExpressionTrees` | `IL/Transforms/TransformExpressionTrees.cs` |
| `IndexRangeTransform` | `IL/Transforms/IndexRangeTransform.cs` |
| `DeconstructionTransform` | `IL/Transforms/DeconstructionTransform.cs` |
| `NamedArgumentTransform` | `IL/Transforms/NamedArgumentTransform.cs` |
| `RemoveUnconstrainedGenericReferenceTypeCheck` | `IL/Transforms/RemoveUnconstrainedGenericReferenceTypeCheck.cs` |
| `UserDefinedLogicTransform` | `IL/Transforms/UserDefinedLogicTransform.cs` |
| `InterpolatedStringTransform` | `IL/Transforms/InterpolatedStringTransform.cs` |

### Final cleanup transforms

| Transform | File |
|---|---|
| `ProxyCallReplacer` | `IL/Transforms/ProxyCallReplacer.cs` |
| `FixRemainingIncrements` | `IL/Transforms/FixRemainingIncrements.cs` |
| `CopyPropagation` | `IL/Transforms/CopyPropagation.cs` |
| `DelegateConstruction` | `IL/Transforms/DelegateConstruction.cs` |
| `LocalFunctionDecompiler` | `IL/Transforms/LocalFunctionDecompiler.cs` |
| `TransformDisplayClassUsage` | `IL/Transforms/TransformDisplayClassUsage.cs` |
| `HighLevelLoopTransform` | `IL/Transforms/HighLevelLoopTransform.cs` |
| `ReduceNestingTransform` | `IL/Transforms/ReduceNestingTransform.cs` |
| `RemoveRedundantReturn` | `IL/Transforms/RemoveRedundantReturn.cs` |
| `IntroduceDynamicTypeOnLocals` | `IL/Transforms/IntroduceDynamicTypeOnLocals.cs` |
| `IntroduceNativeIntTypeOnLocals` | `IL/Transforms/IntroduceNativeIntTypeOnLocals.cs` |
| `AssignVariableNames` | `IL/Transforms/AssignVariableNames.cs` |

### Other transforms

| Transform | File |
|---|---|
| `ILInlining` (base, no options) | `IL/Transforms/ILInlining.cs` |
| `InlineArrayTransform` | `IL/Transforms/InlineArrayTransform.cs` |
| `InterpolatedStringTransform` | `IL/Transforms/InterpolatedStringTransform.cs` |
| `DetectPinnedRegions` | `IL/Transforms/DetectPinnedRegions.cs` |
| `AwaitInCatchTransform` | `IL/ControlFlow/AwaitInCatchTransform.cs` |
| `AwaitInFinallyTransform` | `IL/ControlFlow/AwaitInFinallyTransform.cs` |
| `RuntimeAsyncExceptionRewriteTransform` | `IL/ControlFlow/RuntimeAsyncExceptionRewriteTransform.cs` |
| `RuntimeAsyncManualAwaitTransform` | `IL/ControlFlow/RuntimeAsyncManualAwaitTransform.cs` |
| `SwitchAnalysis` | `IL/ControlFlow/SwitchAnalysis.cs` |
| `StateRangeAnalysis` | `IL/ControlFlow/StateRangeAnalysis.cs` |
| `ExitPoints` | `IL/ControlFlow/ExitPoints.cs` |
| `SymbolicExecution` | `IL/ControlFlow/SymbolicExecution.cs` |
| `RemoveRedundantReturn` | `IL/ControlFlow/RemoveRedundantReturn.cs` |
| `RemoveDeadReturn` (sub) | `IL/ControlFlow/RemoveRedundantReturn.cs` |
| `ILExtraction` | `IL/Transforms/ILExtraction.cs` |
| `TupleTransform` | `IL/Transforms/TupleTransform.cs` |
| `DynamicCallSiteTransform` | `IL/Transforms/DynamicCallSiteTransform.cs` |

## `IL/Patterns/` (IL pattern combinators)

- `Pattern` (base) — `ICSharpCode.Decompiler/IL/Patterns/Pattern.cs`
- `comp(...)` — `IL/Patterns/CombinedPattern.cs`
- `logical(...)` — `IL/Patterns/LogicalPattern.cs`
- `any(...)`, `optional(...)`, `repeat(...)` — combinators in `IL/Patterns/*.cs`

## `IL/Instructions/`

The ILAst instruction classes — one file per instruction kind:

- `Block`, `BlockContainer`, `ILFunction`
- `IfInstruction`, `SwitchInstruction`, `Leave`
- `Call`, `CallVirt`, `NewObj`, `LdVirtFtn`, `LdFtn`
- `Branch`, `ConditionalBranch`, `Leave`
- `LdLoc`, `StLoc`, `LdLoca`, `StObj`, `LdObj`
- `BinaryNumericInstruction` (binary operator base)
- `Ldc`, `LdStr`, `LdToken`, `LdTypeToken`, `LdMemberToken`
- `Box`, `Unbox`, `UnboxAny`
- `Castclass`, `IsInst`, `NewArr`
- `Comp`, `Conv`, `Neg`, `Not`
- `LdFld`, `StFld`, `LdsFld`, `StsFld`, `Ldflda`, `Ldsflda`
- `LdElem`, `StElem`, `LdElema`
- `Sizeof`, `InitObj`, `CpObj`, `CpBlk`
- `LocAlloc` — stack allocation
- `Try`, `Catch`, `Filter`, `Finally`, `Fault` — exception-handling blocks
- `Nop`, `Break`, `Invalid` — debug/marker ops
- `ILInstruction` (base) — abstract instruction with annotations

## `TypeSystem/`

Documented at the category level (60+ files):

### Interfaces (one file per interface)

- `IType`, `ITypeDefinition`, `ITypeParameter`, `ITypeReference`, `ITypeDefinitionOrUnknown`
- `IMethod`, `IField`, `IProperty`, `IEvent`, `IMember`, `IEntity`, `ISymbol`
- `IAttribute`, `IAssembly`, `ICompilation`, `IDecompilerTypeSystem`, `ICodeContext`
- `IParameterizedMember`, `IParameter`, `IVariable`, `IInterningProvider`, `IFreezable`

### Concrete implementations (in `TypeSystem/Implementation/`)

- `MetadataTypeDefinition`, `MetadataMethod`, `MetadataField`, `MetadataProperty`, `MetadataEvent`, `MetadataParameter`, `MetadataTypeParameter`, `MetadataNamespace`
- `AbstractFreezable`, `AbstractType`, `AbstractTypeParameter`, `SimpleCompilation`
- `DecoratedType`, `SpecializedMethod`, `SpecializedField`, `SpecializedProperty`, `SpecializedEvent`
- `MergedNamespace`, `NullabilityAnnotatedType`, `PinnedType`, `TypeWithElementType`
- `GetMembersHelper`, `KnownTypeCache`, `KnownAttributes`, `MinimalCorlib`
- `LocalFunctionMethod`, `FakeMember`, `TypeParameterReference`, `NestedTypeReference`
- `BaseTypeCollector`, `CustomAttribute`, `AttributeListBuilder`, `DecimalConstantHelper`
- `DefaultAssemblyReference`, `DefaultAttribute`, `DefaultParameter`, `DefaultTypeParameter`
- `DefaultVariable`, `DummyTypeParameter`, `MetadataEvent`, `SyntheticRangeIndexer`
- `ThreeState`

### Type helpers

- `KnownTypeReference`, `SpecialType`, `Accessibility`, `TypeKind`, `FullTypeName`
- `ArrayType`, `ByReferenceType`, `ParameterizedType`, `PointerType`, `IntersectionType`
- `ModifiedType`, `NullableType`, `TupleType`, `FunctionPointerType`, `TaskType`
- `TypeParameterSubstitution`, `TypeVisitor`, `NormalizeTypeVisitor`
- `ApplyAttributeTypeVisitor`, `TypeProvider`, `TypeSystemExtensions`, `TypeUtils`
- `ReflectionHelper`, `ReflectionNameParseException`
- `InheritanceHelper`, `ParameterListComparer`
- `TopLevelTypeName`, `AssemblyQualifiedTypeName`, `GenericContext`, `SimpleTypeResolveContext`
- `Nullability`, `ReferenceResolvingException`, `VarArgInstanceMethod`, `ComHelper`
- `ExtensionInfo` (C# 14 extension member grouping)