# 08 — Document / Tab Management

This file documents the assembly-document model and tab management in `dnSpy/dnSpy/dnSpy/Documents/`. Together with `Documents/Tabs/`, this is the heart of dnSpy's interactive decompile-and-edit experience.

## `Documents/DsDocumentService.cs`

### `DsDocumentService` (sealed) — `Documents/DsDocumentService.cs`

- **MEF**: `[Export(typeof(IDsDocumentService))]`
- **可见性**: public, sealed
- **简要说明**: the model — list of loaded assemblies with safe concurrent access.

#### `public IDsDocument[] GetDocuments()`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **返回值**: snapshot of loaded documents
- **简要说明**: snapshot read; thread-safe via `ReaderWriterLockSlim`

#### `public void Add(IDsDocument document)`

- **位置**: `Documents/DsDocumentService.cs:103+`
- **可见性**: public
- **抛出/异常**: `ArgumentNullException`
- **副作用**: writes lock; fires `CollectionChanged`
- **调用了**: `ReaderWriterLockSlim.EnterWriteLock`, `OnCollectionChanged`
- **简要说明**: add a document to the model

#### `public IDisposable DisableAssemblyLoad()`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **返回值**: `IDisposable` guard
- **副作用**: temporarily blocks auto-load
- **简要说明**: scope guard (used during decompile-many to avoid async add)

#### `public event EventHandler<NotifyDocumentCollectionChangedEventArgs>? CollectionChanged`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **简要说明**: raised when documents are added / removed

#### `public IAssemblyResolver AssemblyResolver { get; }`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **简要说明**: shared resolver for cross-document references

## `Documents/DsDocumentServiceProvider.cs` / `DsDocumentServiceSettings.cs`

- **位置**: `Documents/`
- **简要说明**: provider + settings for the document service

## `Documents/DsDocumentServiceAppSettingsModifiedListener.cs`

- **位置**: `Documents/`
- **简要说明**: re-loads documents when settings change

## `Documents/DefaultDsDocumentLoader.cs` / `DsDocumentLoader.cs` / `DefaultDsDocumentProvider.cs`

- **位置**: `Documents/`
- **简要说明**: `IDsDocumentLoader` + provider

## `Documents/IDsDocumentLoader.cs` / `IDsDocumentProvider.cs`

- **位置**: `Documents/`
- **简要说明**: contracts re-exported from `dnSpy.Contracts.DnSpy`

## `Documents/AssemblyResolver.cs` / `DotNetPathProvider.cs` / `FileUtils.cs` / `FrameworkPath.cs`

- **位置**: `Documents/`
- **简要说明**: assembly resolution + path providers

## `Documents/TargetFrameworkAttributeInfo.cs` / `MethodAnnotations.cs` / `ReferenceNavigatorServiceImpl.cs`

- **位置**: `Documents/`
- **简要说明**: TFM helpers + reference navigation

## `Documents/Tabs/DocumentTabService.cs`

### `DocumentTabService` (sealed) — `Documents/Tabs/DocumentTabService.cs`

- **MEF**: `[Export, Export(typeof(IDocumentTabService))]`
- **可见性**: public, sealed
- **简要说明**: the tab manager

#### `public DocumentTreeView DocumentTreeView { get; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **简要说明**: the tree-view driving tab creation

#### `public ITabGroupService TabGroupService { get; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public

#### `public IEnumerable<IDocumentTab> SortedTabs { get; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **简要说明**: tabs sorted by activation time

#### `public IEnumerable<IDocumentTab> VisibleFirstTabs { get; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **简要说明**: visible tabs first, then hidden

#### `public IDocumentTab? ActiveTab { get; set; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public

#### `public IDocumentTab GetOrCreateActiveTab()`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **简要说明**: lazy-create the active tab if none

#### `public void DocumentTreeView_NodeActivated(object? sender, DocumentTreeNodeActivatedEventArgs e)`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **抛出/异常**: forwards
- **副作用**: creates / switches tabs
- **调用了**: switches on `e.Node.Data.GetType()`:
  - `AssemblyReferenceNode` -> resolves the reference, navigates tree
  - `DerivedTypeNode` / `BaseTypeNode` -> selects the target type
  - `TypeReferenceNode` / `MethodReferenceNode` / `PropertyReferenceNode` / `EventReferenceNode` / `FieldReferenceNode` -> resolves and selects the target
  - otherwise: `ActiveTabContentImpl` -> `TabContentImpl.Show(impl, nodes)`
- **简要说明**: main entry for tree-node activation

## `Documents/Tabs/DocumentTabServiceSettings.cs` / `DocumentTabServiceLoader.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: settings + loader

## `Documents/Tabs/DocumentTabContentFactoryService.cs` / `DocumentTabContentFactoryContext.cs`

### `DocumentTabContentFactoryService`

- **位置**: `Documents/Tabs/DocumentTabContentFactoryService.cs`
- **简要说明**: enumerates `IDocumentTabContentFactory`s (Roslyn-based + default) in `Order` ascending

### `DocumentTabContentFactoryContext`

- **位置**: `Documents/Tabs/DocumentTabContentFactoryContext.cs`
- **简要说明**: per-factory-call context

## `Documents/Tabs/DocumentTreeNodeDecompiler.cs`

### `DocumentTreeNodeDecompiler`

- **位置**: `Documents/Tabs/DocumentTreeNodeDecompiler.cs`
- **简要说明**: bridges `IDocumentTreeNodeData` to `IDecompiler.Decompile`

#### `public Task DecompileAsync(...)` (overloads)

- **位置**: `Documents/Tabs/DocumentTreeNodeDecompiler.cs:1`
- **可见性**: public, async
- **副作用**: writes to `IDecompilerOutput`
- **调用了**: `IDecompiler.Decompile(MethodDef/TypeDef, IDecompilerOutput, ctx)`
- **简要说明**: the actual decompile call

## `Documents/Tabs/DocumentTabSerializer.cs` / `DsDocumentInfoSerializer.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: tab-content serialization for session save

## `Documents/Tabs/DocumentTabUIContextLocator.cs` / `DocumentTabUIContextLocatorProvider.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: UI-context routing (which content type belongs where)

## `Documents/Tabs/DocumentList.cs` / `DocumentListLoader.cs` / `DocumentListService.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: the user's document list (persisted across runs)

## `Documents/Tabs/AppCommandLineArgsHandler.cs`

- **位置**: `Documents/Tabs/AppCommandLineArgsHandler.cs`
- **简要说明**: `--select`, `--new-tab` handling

## `Documents/Tabs/EntryPointCommands.cs`

- **位置**: `Documents/Tabs/EntryPointCommands.cs`
- **简要说明**: command bindings for the document tree

## `Documents/Tabs/Commands.cs` / `GoToTokenCommand.cs` / `CopyTokenCommand.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: command registry + token navigation

## `Documents/Tabs/DocTabReferenceNavigator.cs`

### `DocTabReferenceNavigator`

- **位置**: `Documents/Tabs/DocTabReferenceNavigator.cs`
- **简要说明**: navigates references inside a tab

#### `public void GoToReference(...)`

- **位置**: `Documents/Tabs/DocTabReferenceNavigator.cs:1`
- **可见性**: public
- **简要说明**: jump to a reference

## `Documents/Tabs/DefaultDecompileNode.cs`

- **位置**: `Documents/Tabs/DefaultDecompileNode.cs`
- **简要说明**: default node decompile entry

## `Documents/Tabs/DecompilationCache.cs`

### `DecompilationCache`

- **位置**: `Documents/Tabs/DecompilationCache.cs`
- **简要说明**: per-tab decompile cache

#### `public Task<TResult> GetOrCreateAsync<TKey, TResult>(TKey key, Func<TKey, Task<TResult>> factory)`

- **位置**: `Documents/Tabs/DecompilationCache.cs:1`
- **可见性**: public, async
- **简要说明**: memoize decompile results

## `Documents/Tabs/AsyncShowResult.cs` / `DefaultDocumentList.cs` / `DefaultDocumentTabContentProvider.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: defaults

## `Documents/Tabs/Dialogs/` / `DocViewer/` / `Hex/` / `Tabs.snk`

- **位置**: `Documents/Tabs/`
- **简要说明**: per-tab dialogs + viewers + signing key

## `Documents/TreeView/`

### `DocumentTreeView`

- **位置**: `Documents/TreeView/DocumentTreeView.cs`
- **可见性**: public
- **简要说明**: WPF tree-view of loaded documents (uses vendored `ICSharpCode.TreeView`)

#### `public event EventHandler<DocumentTreeNodeActivatedEventArgs>? NodeActivated`

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public

#### `public IDsDocumentService DocumentService { get; }`

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public

#### `public void SelectItems(...)` (overloads)

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public
- **简要说明**: navigate to a specific node

### `DocumentTreeViewSettings`

- **位置**: `Documents/TreeView/DocumentTreeViewSettings.cs`
- **简要说明**: persisted settings

### Tree node kinds

- Many small files; one class per `DocumentTreeNodeData` kind.