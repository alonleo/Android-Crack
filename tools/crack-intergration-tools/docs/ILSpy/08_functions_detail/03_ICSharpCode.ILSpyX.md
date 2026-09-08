# 08 — `ICSharpCode.ILSpyX` (UI-host-agnostic core)

This file documents the public surface of `ICSharpCode.ILSpyX/`. The library is a `netstandard2.0` library shared between the Avalonia GUI and the `ilspycmd` CLI. It owns the `LoadedAssembly` lazy-load model, the assembly list manager, the file loaders, the search strategies, and the settings service.

## `LoadedAssembly.cs` (766 LoC)

### `LoadedAssembly` (public sealed class) — `ICSharpCode.ILSpyX/LoadedAssembly.cs:55`

- **可见性**: public, sealed, `IDisposable`
- **简要说明**: a wrapper around a `MetadataFile` with lazy async loading via `FileLoaderRegistry`.

#### `public event Action? Loaded`

- **位置**: `LoadedAssembly.cs:79`
- **可见性**: public
- **简要说明**: raised when the load task completes

#### `public LoadedAssembly? ParentBundle { get; }`

- **位置**: `LoadedAssembly.cs:90`
- **可见性**: public
- **简要说明**: when the assembly is inside a NuGet / single-file bundle, the parent

#### `public LoadedAssembly(AssemblyList assemblyList, string fileName, ...)` (and overloads)

- **签名**: ctor with overloads at lines `92` and `127`
- **位置**: `LoadedAssembly.cs:92 / 127`
- **可见性**: public
- **副作用**: schedules the load task; does not start until first `.Value`
- **调用了**: `FileLoaderRegistry.Load`
- **简要说明**: construct a new `LoadedAssembly`; lazy load begins on first async access.

#### `public async Task<string> GetTargetFrameworkIdAsync()`

- **位置**: `LoadedAssembly.cs:143`
- **可见性**: public, async
- **返回值**: TFM string (e.g. `net8.0`, `net472`)
- **简要说明**: reads `TargetFrameworkAttribute` from the metadata

#### `public async Task<string> GetDetectedTargetFrameworkIdAsync()`

- **位置**: `LoadedAssembly.cs:160`
- **可见性**: public, async
- **简要说明**: detects TFM from references when no explicit attribute

#### `public async Task<string> GetRuntimePackAsync()`

- **位置**: `LoadedAssembly.cs:175`
- **可见性**: public, async
- **简要说明**: name of the runtime pack the assembly needs

#### `public ReferenceLoadInfo LoadedAssemblyReferencesInfo { get; }`

- **位置**: `LoadedAssembly.cs:188`
- **可见性**: public
- **简要说明**: tracks which references were resolved

#### `public Task<LoadResult> GetLoadResultAsync()`

- **位置**: `LoadedAssembly.cs:195`
- **可见性**: public
- **返回值**: `LoadResult` (the file loader's result)
- **简要说明**: awaits the `Lazy<Task<LoadResult>>`; idempotent

#### `public async Task<MetadataFile> GetMetadataFileAsync()`

- **位置**: `LoadedAssembly.cs:203`
- **可见性**: public, async
- **返回值**: `MetadataFile` (PEFile, SingleFileBundle, ...)
- **抛出/异常**: `DecompilerException`
- **调用了**: `GetLoadResultAsync`
- **简要说明**: unwraps to the underlying metadata file

#### `public MetadataFile? GetMetadataFileOrNull()`

- **位置**: `LoadedAssembly.cs:216`
- **可见性**: public
- **简要说明**: sync, returns null if not yet loaded

#### `public async Task<MetadataFile?> GetMetadataFileOrNullAsync()`

- **位置**: `LoadedAssembly.cs:234`
- **可见性**: public, async

#### `public ICompilation? GetTypeSystemOrNull()`

- **位置**: `LoadedAssembly.cs:257`
- **可见性**: public
- **简要说明**: cached `ICompilation` (built on first request)

#### `public ICompilation? GetTypeSystemOrNull(TypeSystemOptions options)`

- **位置**: `LoadedAssembly.cs:278`
- **可见性**: public
- **参数**: options flags
- **简要说明**: build with explicit `TypeSystemOptions`

#### `public AssemblyList AssemblyList { get; }`

- **位置**: `LoadedAssembly.cs:294`
- **可见性**: public
- **简要说明**: the parent list

#### `public string FileName { get; }`

- **位置**: `LoadedAssembly.cs:296`
- **可见性**: public

#### `public string ShortName { get; }`

- **位置**: `LoadedAssembly.cs:298`
- **可见性**: public
- **简要说明**: short file name for display

#### `public string Text { get; }`

- **位置**: `LoadedAssembly.cs:307`
- **可见性**: public
- **简要说明**: display text (typically `ShortName`)

#### `public bool IsLoaded { get; }`

- **位置**: `LoadedAssembly.cs:363`
- **可见性**: public
- **简要说明**: has the lazy task completed?

#### `public void Dispose()`

- **位置**: `LoadedAssembly.cs:1`
- **可见性**: public
- **简要说明**: releases the underlying `MetadataFile`

#### `public static ConditionalWeakTable<MetadataFile, LoadedAssembly> loadedAssemblies`

- **位置**: `LoadedAssembly.cs:1`
- **可见性**: public, static
- **简要说明**: cache from `MetadataFile` -> `LoadedAssembly` so the same file maps to the same wrapper across lists.

## `AssemblyList.cs` (468 LoC)

### `AssemblyList` (public class) — `ICSharpCode.ILSpyX/AssemblyList.cs`

- **可见性**: public
- **简要说明**: a list of `LoadedAssembly` with persistence support

#### `public ObservableCollection<LoadedAssembly> LoadedAssemblies { get; }`

- **位置**: `AssemblyList.cs:1`
- **可见性**: public
- **简要说明**: the live collection

#### `public LoadedAssembly? OpenAssembly(...)` (overloads)

- **位置**: `AssemblyList.cs:1`
- **可见性**: public
- **抛出/异常**: `FileNotFoundException`
- **调用了**: `LoadedAssembly` ctor
- **简要说明**: add a new assembly to the list; returns the wrapper

#### `public void Clear()`

- **位置**: `AssemblyList.cs:1`
- **可见性**: public
- **简要说明**: remove all

#### `public void RefreshAssemblies()`

- **位置**: `AssemblyList.cs:1`
- **可见性**: public
- **简要说明**: force re-load all (used after settings change)

#### `public void Save(...)` / `public static AssemblyList Load(...)`

- **位置**: `AssemblyList.cs:1`
- **可见性**: public
- **副作用**: file I/O
- **简要说明**: persist to / restore from the user's settings XML

## `AssemblyListManager.cs` (316 LoC)

### `AssemblyListManager` (public class) — `ICSharpCode.ILSpyX/AssemblyListManager.cs`

- **可见性**: public
- **简要说明**: CRUD over `AssemblyList`s with Undo support

#### `public AssemblyList CreateList(string name)`

- **位置**: `AssemblyListManager.cs:1`
- **可见性**: public
- **简要说明**: create a new list; emits undo unit

#### `public void DeleteList(...)`

- **位置**: `AssemblyListManager.cs:1`
- **可见性**: public
- **简要说明**: remove list; undoable

#### `public void RenameList(...)`

- **位置**: `AssemblyListManager.cs:1`
- **可见性**: public
- **简要说明**: rename list; undoable

#### `public void SetCurrentList(...)`

- **位置**: `AssemblyListManager.cs:1`
- **可见性**: public
- **简要说明**: switch active list; undoable

#### `public void Undo()` / `public void Redo()`

- **位置**: `AssemblyListManager.cs:1`
- **可见性**: public
- **调用了**: `IUndoUnit.Undo` / `.Redo`
- **简要说明**: standard undo / redo

## `AssemblyListSnapshot.cs` (201 LoC)

### `AssemblyListSnapshot` (public class) — `ICSharpCode.ILSpyX/AssemblyListSnapshot.cs`

- **可见性**: public
- **简要说明**: an immutable view of an `AssemblyList` at a point in time

## `Abstractions/`

### `ILanguage` — `ICSharpCode.ILSpyX/Abstractions/ILanguage.cs`

- **可见性**: public
- **简要说明**: interface for a language backend (C#, VB, IL).

#### `string Name { get; }`

- **简要说明**: display name

#### `string ContentType { get; }`

- **简要说明**: MIME-like content type (e.g. `text/x-csharp`)

#### `void Decompile(...)`

- **简要说明**: decompile a member to text

#### `string TypeToString(ITypeDefinition)`

- **简要说明**: display string for a type

### `IResourceFileHandler`

- **位置**: `ICSharpCode.ILSpyX/Abstractions/IResourceFileHandler.cs`
- **可见性**: public
- **简要说明**: handles a custom resource format (BAML, .resources, ...).

### `IResourceNodeFactory`

- **位置**: `ICSharpCode.ILSpyX/Abstractions/IResourceNodeFactory.cs`
- **可见性**: public
- **简要说明**: produces tree nodes for a resource.

### `ITreeNode`

- **位置**: `ICSharpCode.ILSpyX/Abstractions/ITreeNode.cs`
- **可见性**: public
- **简要说明**: tree-node interface — `Text`, `Children`, `LoadChildrenAsync`, ...

## `Analyzers/`

### `IAnalyzer` — `ICSharpCode.ILSpyX/Analyzers/IAnalyzer.cs`

- **可见性**: public
- **简要说明**: interface for built-in analyzer extensions.

#### `void Analyze(ISymbol symbol, AnalyzerContext context)`

- **简要说明**: runs the analyzer on a symbol

### `AnalyzerContext` / `AnalyzerScope` / `Helpers`

- **位置**: `ICSharpCode.ILSpyX/Analyzers/`
- **简要说明**: shared types for analyzer implementations

### `Builtin/*` analyzers

- several built-in analyzers (e.g. "used by", "inherits from")

## `Extensions/CollectionExtensions.cs`

- **位置**: `ICSharpCode.ILSpyX/Extensions/CollectionExtensions.cs`
- **简要说明**: extension methods for collections (used by Avalonia VMs)

## `FileLoaders/`

### `FileLoaderRegistry` (public class) — `ICSharpCode.ILSpyX/FileLoaders/FileLoaderRegistry.cs`

#### `public LoadResult Load(string fileName)`

- **签名**: `LoadResult Load(string fileName)`
- **位置**: `FileLoaderRegistry.cs:1`
- **可见性**: public
- **抛出/异常**: `FileNotFoundException`, `NotSupportedException`
- **调用了**: try each registered loader until one succeeds
- **简要说明**: dispatch to the right loader for the file

### `PEFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/PEFileLoader.cs`
- **简要说明**: default loader for `.dll` / `.exe` / `.winmd`

### `ArchiveFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/ArchiveFileLoader.cs`
- **简要说明**: looks inside ZIP archives for `.dll` / `.exe`

### `BundleFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/BundleFileLoader.cs`
- **简要说明**: reads .NET 5+ single-file bundles (`.bundle`)

### `XamarinCompressedFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/XamarinCompressedFileLoader.cs`
- **简要说明**: reads Xamarin-compressed assemblies

### `WebCilFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/WebCilFileLoader.cs`
- **简要说明**: reads WebCIL (portable .NET in browser, `wc` magic)

### `MetadataFileLoader`

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/MetadataFileLoader.cs`
- **简要说明**: fallback wrapper for pre-loaded `MetadataFile`

### `LoadResult` (public class)

- **位置**: `ICSharpCode.ILSpyX/FileLoaders/LoadResult.cs`
- **简要说明**: the result of a `FileLoaderRegistry.Load` call

## `MermaidDiagrammer/`

### `GenerateHtmlDiagrammer` (public class) — `ICSharpCode.ILSpyX/MermaidDiagrammer/GenerateHtmlDiagrammer.cs`

#### `public string Assembly { get; set; }`

- **简要说明**: the input assembly path

#### `public string OutputFolder { get; set; }`

- **简要说明**: where to write `index.html`

#### `public string? Include { get; set; }`

- **简要说明**: regex whitelist for type names

#### `public string? Exclude { get; set; }`

- **简要说明**: regex blacklist

#### `public void Run()`

- **位置**: `GenerateHtmlDiagrammer.cs:1`
- **可见性**: public
- **抛出/异常**: `IOException`
- **副作用**: writes HTML + JSON to disk
- **调用**: 被 `IlspyCmdProgram` `--generate-diagrammer` 调用
- **调用了**: `Factory.BuildTypes`, `ClassDiagrammer.Render`
- **简要说明**: top-level driver

### `Factory`

- **位置**: `ICSharpCode.ILSpyX/MermaidDiagrammer/Factory.cs`
- **简要说明**: produces types + relationships from the input assembly

### `ClassDiagrammer`

- **位置**: `ICSharpCode.ILSpyX/MermaidDiagrammer/ClassDiagrammer.cs`
- **简要说明**: emits Mermaid `classDiagram` syntax

## `PdbProvider/`

### `PortableDebugInfoProvider`

- **位置**: `ICSharpCode.ILSpyX/PdbProvider/PortableDebugInfoProvider.cs`
- **可见性**: public
- **简要说明**: reads portable PDBs

### `MonoCecilDebugInfoProvider`

- **位置**: `ICSharpCode.ILSpyX/PdbProvider/MonoCecilDebugInfoProvider.cs`
- **可见性**: public
- **简要说明**: legacy Mono.Cecil-based PDB reader

### `DebugInfoUtils`

- **位置**: `ICSharpCode.ILSpyX/PdbProvider/DebugInfoUtils.cs`
- **简要说明**: PDB helpers

## `Search/`

### `AbstractEntitySearchStrategy<T>` (public abstract) — `ICSharpCode.ILSpyX/Search/AbstractEntitySearchStrategy.cs`

- **位置**: `AbstractEntitySearchStrategy.cs:1`
- **可见性**: public, abstract
- **简要说明**: base class for search strategies

#### `public abstract IEnumerable<SearchResult> Search(...args)`

- **简要说明**: the search contract

### `AssemblySearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/AssemblySearchStrategy.cs`
- **简要说明**: `t:Name` matches assemblies by name

### `MemberSearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/MemberSearchStrategy.cs`
- **简要说明**: `m:Name` matches type members

### `NamespaceSearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/NamespaceSearchStrategy.cs`
- **简要说明**: matches namespaces

### `LiteralSearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/LiteralSearchStrategy.cs`
- **简要说明**: plain substring across everything

### `MetadataTokenSearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/MetadataTokenSearchStrategy.cs`
- **简要说明**: `0x06000001`

### `ResourceSearchStrategy`

- **位置**: `ICSharpCode.ILSpyX/Search/ResourceSearchStrategy.cs`
- **简要说明**: matches resource names

### `CSharpLexer`

- **位置**: `ICSharpCode.ILSpyX/Search/CSharpLexer.cs`
- **简要说明**: tiny lexer used by search

### `SearchResult` (public class)

- **位置**: `ICSharpCode.ILSpyX/Search/SearchResult.cs`
- **简要说明**: a single search hit — type / member + location

## `Settings/`

### `DecompilerSettings` (public class, in ILSpyX) — `ICSharpCode.ILSpyX/Settings/DecompilerSettings.cs`

#### `public static DecompilerSettings Load()`

- **位置**: `Settings/DecompilerSettings.cs:1`
- **可见性**: public, static
- **简要说明**: load from `ILSpy.xml`

#### `public void Save()`

- **位置**: `Settings/DecompilerSettings.cs:1`
- **可见性**: public
- **简要说明**: persist to `ILSpy.xml`

### `ILSpySettings` (public static class) — `ICSharpCode.ILSpyX/Settings/ILSpySettings.cs`

#### `public static ILSpySettings Load()`

- **位置**: `Settings/ILSpySettings.cs:1`
- **可见性**: public, static
- **简要说明**: load global settings

#### `public static SettingsFilePathProvider SettingsFilePathProvider`

- **位置**: `Settings/ILSpySettings.cs:1`
- **可见性**: public, static
- **简要说明**: factory for the settings path (next to exe or `%AppData%`)

### `ISettingsProvider` (public interface) — `ICSharpCode.ILSpyX/Settings/ISettingsProvider.cs`

- **简要说明**: MEF export contract for settings services

### `SettingsServiceBase` (public class) — `ICSharpCode.ILSpyX/Settings/SettingsServiceBase.cs`

- **简要说明**: observable settings service base class

### `MutexProtector` (public class) — `ICSharpCode.ILSpyX/Settings/MutexProtector.cs`

- **简要说明**: per-process mutex for settings access

## `TreeView/`

### `SharpTreeNode` (public abstract class) — `ICSharpCode.ILSpyX/TreeView/SharpTreeNode.cs`

- **可见性**: public, abstract
- **简要说明**: virtual tree node base — used by both Avalonia GUI and the decompiler.

#### `public virtual string Text { get; }`

- **简要说明**: display text

#### `public abstract IEnumerable<SharpTreeNode> Children { get; }`

- **简要说明**: child nodes

#### `public virtual Task LoadChildrenAsync()`

- **简要说明**: async load hook

#### `public void RaiseChanged()`

- **简要说明**: raise property changed

### `SharpTreeNodeCollection`

- **位置**: `ICSharpCode.ILSpyX/TreeView/SharpTreeNodeCollection.cs`
- **简要说明**: observable collection of `SharpTreeNode`

### `TreeFlattener`

- **位置**: `ICSharpCode.ILSpyX/TreeView/TreeFlattener.cs`
- **简要说明**: flattens a `SharpTreeNode` tree into a linear list (for TreeView virtualization)

### `FlatListTreeNode`

- **位置**: `ICSharpCode.ILSpyX/TreeView/FlatListTreeNode.cs`
- **简要说明**: a flat-list tree-node used by the TreeDataGrid

### `TreeTraversal`

- **位置**: `ICSharpCode.ILSpyX/TreeView/TreeTraversal.cs`
- **简要说明**: pre-order / post-order traversal helpers

### `PlatformAbstractions/*`

- **位置**: `ICSharpCode.ILSpyX/TreeView/PlatformAbstractions/`
- **简要说明**: per-platform helpers (Avalonia-specific)

## `Util/`

### `GuessFileType`

- **位置**: `ICSharpCode.ILSpyX/Util/GuessFileType.cs`
- **简要说明**: looks at a file's magic bytes to decide its kind (PE / ZIP / bundle / WebCIL / native)