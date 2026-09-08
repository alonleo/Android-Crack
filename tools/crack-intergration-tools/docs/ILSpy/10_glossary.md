# 10 — Glossary

This glossary defines the technical vocabulary used in the ILSpy codebase. Each term has a short definition and a cross-reference to where it appears.

## .NET / ECMA-335

### CIL — Common Intermediate Language
The bytecode format defined by ECMA-335 that .NET assemblies compile to. The raw bytes of every method body. ILSpy's `ILReader` consumes CIL.

### CLR — Common Language Runtime
The runtime that executes CIL. ILSpy is a static analysis tool — it does not need a CLR, but the `DecompilerTypeSystem` mirrors CLR concepts.

### PE — Portable Executable
The file format that hosts CIL metadata + IL. `PEFile` wraps one PE.

### AssemblyRef / TypeRef / MemberRef
Metadata tokens for cross-assembly references. Resolved by `UniversalAssemblyResolver`.

### Metadata token
A 4-byte handle in PE metadata. The `0x06000001` syntax in ILSpy's search targets metadata tokens.

### Sequence point
A mapping from an IL offset to a source-code line. Produced by the compiler; carried in PDBs.

### Portable PDB
The modern PDB format (replaces Windows-only PDB). ILSpy can emit one via `PortablePdbBuilder`.

### ReadyToRun (R2R)
A pre-compiled native-image section in some .NET assemblies. ILSpy has a viewer plugin (`ILSpy.ReadyToRun`).

### ReadyToRun (format)
A separate MS-internal native-image format; the `ILSpy.ReadyToRun` plugin can inspect it.

## ILAst (IL Abstract Syntax Tree)

### ILAst
The intermediate representation between raw CIL and the C# AST. The class hierarchy is `ILInstruction` -> ... -> `ILFunction` (root). Located in `ICSharpCode.Decompiler/IL/Instructions/`.

### ILFunction
The root ILAst node. Has `Body` (`BlockContainer`), `Variables` (declared locals), `IsAsync`, `IsIterator`, `Warnings`.

### Block / BlockContainer
The basic block types in ILAst. A `BlockContainer` is a sequence of `Block`s (or nested containers for try/catch, loops, ...).

### IILTransform
The interface for ILAst-level transforms. The 30-step pipeline is `CSharpDecompiler.GetILTransforms()`.

### IAstTransform
The interface for AST-level transforms. The 16-step pipeline is `CSharpDecompiler.GetAstTransforms()`.

### ILAst pattern matching
Pattern combinators in `ICSharpCode.Decompiler/IL/Patterns/`. Used by transforms to match ILAst shapes safely (`comp(...)`, `logical(...)`, etc.).

### `function.CheckInvariant(ILPhase.Normal)`
DEBUG-only invariant check after each IILTransform.

## C# AST (NRefactory)

### NRefactory
The historic C# AST library; ILSpy ships a forked/maintained version under `ICSharpCode.Decompiler/CSharp/Syntax/`.

### AstNode
The AST base class — `Parent`, `Children`, `Annotations`, traversal helpers.

### SyntaxTree
The root `AstNode` containing `CompilationUnit`s.

### IAstVisitor
The visitor interface. `CSharpOutputVisitor` is the production visitor; `DepthFirstAstVisitor` is the base.

### CSharpOutputVisitor
The production C# pretty-printer (3164 LoC). Wrapped by `InsertParenthesesVisitor`, `InsertMissingTokensDecorator`, `InsertRequiredSpacesDecorator`.

### InsertParenthesesVisitor
Adds parens when the parser would otherwise mis-bind (e.g. `a + b * c` -> `(a + b) * c`).

### InsertMissingTokensDecorator
Synthesizes missing `;` `,` `{` `}` that the AST builder left out.

### InsertRequiredSpacesDecorator
Adds the spaces between adjacent tokens that the lexer would otherwise collapse.

## Language features

### Async / await de-sugaring
Compiler generates a state-machine class implementing `IAsyncStateMachine.MoveNext()`. `AsyncAwaitDecompiler` rewrites this into `await` in the original method.

### yield return de-sugaring
Compiler generates an iterator state-machine class. `YieldReturnDecompiler` rewrites this into `yield return`.

### Pattern matching
C# 8/9/10/11 pattern syntax (`is T x`, list patterns, recursive patterns, switch expressions). Detected by `PatternMatchingTransform` + `PatternStatementTransform`.

### Records
C# 9 `record class` / C# 10 `record struct` — primary constructors, value equality, `with` expression. Emitted by `RecordDecompiler` + settings.

### Primary constructors
C# 12 syntax — parameters in the type header. `UsePrimaryConstructorSyntax` setting.

### Nullable reference types
C# 8 feature — `[Nullable(1)]` attribute + `?` on reference types. Handled by `DecompilerSettings.NullabilityAnnotations` and `KnownAttributes`.

### File-scoped namespaces
C# 10 `namespace Foo;` syntax. `FileScopedNamespaces` setting.

### Required members
C# 11 `required` modifier. `RequiredMembers` setting.

## Type system

### ICompilation / IDecompilerTypeSystem
The decompiler's `ICompilation`. Built by `DecompilerTypeSystem.CreateAsync` from a `PEFile`.

### IType / ITypeDefinition / ITypeParameter / ITypeReference
The four core type interfaces.

### IMethod / IField / IProperty / IEvent
Member interfaces.

### MetadataTypeDefinition / MetadataMethod / ...
Concrete `IMethod` etc. implementations over `System.Reflection.Metadata`.

### UniversalAssemblyResolver
Resolves `AssemblyRef`s to PE files on disk / NuGet / shared framework.

## Plugins and extension

### MEF — Managed Extensibility Framework
The composition framework. ILSpy uses `System.Composition` (`System.Composition.MEF`).

### `[Export]` / `[Import]` / `[ImportingConstructor]` / `[Shared]`
MEF attributes. ViewModels and services are `[Export]`; ctors are `[ImportingConstructor]`; long-lived objects are `[Shared]`.

### AppComposition
The static class that owns the MEF container.

### *.Plugin.dll
The naming convention for plugin assemblies. Discovered by `AppComposition.RegisterPluginResolver`.

## GUI

### Avalonia 12
The cross-platform XAML UI framework used by ILSpy.

### AvaloniaEdit
The text-editor control (decompiled code view).

### Dock (wieslawsoltes)
The panel-layout framework (not to be confused with `Avalonia.Controls.Dock`).

### Simple theme
ILSpy's chosen theme (NOT Fluent). Defined in `App.axaml` and `ILSpy/Themes/`.

### SharpTreeNode
The virtual tree-node base in `ICSharpCode.ILSpyX/TreeView/`. Used by both Avalonia GUI and the decompiler.

### NavigationHistory
Two-stack browser-style history. `ILSpy/NavigationHistory.cs`.

### CommandManager
Weak-event re-query-suggested analog (Avalonia doesn't have one built-in).

## Build

### Central Package Management (CPM)
`Directory.Packages.props` declares all `PackageVersion`s. Every csproj `PackageReference` references it by name.

### packages.lock.json
Per-project lock file. CI NuGet caching keys off these. Bare `dotnet restore` will prune them — use `restore.ps1`.

### SourceLink
Embeds GitHub URL in PDBs so debuggers can fetch source.

## Embedding

### NuGet `ICSharpCode.Decompiler` package
The standalone engine. Consumers instantiate `CSharpDecompiler` directly.

### Entry
The public facade for embedding the GUI. `ILSpy/Entry.cs`.

### `IDebugInfoProvider` / `IDocumentationProvider`
Pluggable providers for PDB and XML doc comments.

### Settings (the public NuGet package `DecompilerSettings`)
~200 properties. Serializable. Observable.

## CLI

### ilspycmd
The CLI global tool. `ICSharpCode.ILSpyCmd/`.

### `--generate-diagrammer`
Generates an HTML Mermaid class diagram. `ICSharpCode.ILSpyX/MermaidDiagrammer/`.

### `-genpdb`
Generates a portable PDB. Uses `PortablePdbBuilder`.

### `-p`
Project export (whole .csproj + per-type .cs).

### `--decompile-baml`
With `-p`, also translates `.g.resources` BAML into XAML pages.