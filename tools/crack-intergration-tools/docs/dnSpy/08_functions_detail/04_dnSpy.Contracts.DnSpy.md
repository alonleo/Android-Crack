# 08 — `dnSpy.Contracts.DnSpy` (interface-only)

This file documents the public contract surface (`dnSpy/dnSpy/dnSpy.Contracts.DnSpy/`). The assembly contains no implementation; everything is interface, attribute, or DTO. Every extension depends on it.

## `App/`

### `IAppWindow.cs`

#### `IAppWindow` (public interface)

- **位置**: `dnSpy.Contracts.DnSpy/App/IAppWindow.cs`
- **可见性**: public
- **简要说明**: the main window facade

##### `Window MainWindow { get; }`

- **可见性**: public
- **简要说明**: the WPF Window

##### `IAppCommandLineArgs CommandLineArgs { get; }`

- **可见性**: public
- **简要说明**: parsed CLI

##### `IWpfCommands MainWindowCommands { get; }`

- **可见性**: public
- **简要说明**: command registry

##### `bool AppLoaded { get; }`

- **可见性**: public
- **简要说明**: app-fully-loaded signal

##### `event EventHandler<CancelEventArgs> MainWindowClosing`

- **可见性**: public

##### `event EventHandler MainWindowClosed`

- **可见性**: public

### `IAppCommandLineArgs.cs`

- **位置**: `dnSpy.Contracts.DnSpy/App/IAppCommandLineArgs.cs`
- **简要说明**: matches `AppCommandLineArgs` properties + `HasArgument`, `GetArgumentValue`, `GetArguments()`

### `IAppCommandLineArgsHandler.cs`

- **位置**: `dnSpy.Contracts.DnSpy/App/IAppCommandLineArgsHandler.cs`
- **简要说明**: handlers for CLI args, ordered by `Order`

#### `int Order { get; }`

- **可见性**: public
- **简要说明**: ascending order

#### `void OnNewArgs(IAppCommandLineArgs args)`

- **可见性**: public
- **简要说明**: handler entry

### `IMessageBoxService.cs`

- **位置**: `dnSpy.Contracts.DnSpy/App/IMessageBoxService.cs`
- **简要说明**: message-box service contract

### `AppDirectories.cs`

- **位置**: `dnSpy.Contracts.DnSpy/App/AppDirectories.cs`
- **简要说明**: known folder paths (settings, profile, extensions, ...)

## `AsmEditor/`

- **位置**: `dnSpy.Contracts.DnSpy/AsmEditor/`
- **简要说明**: interfaces for assembly editor extensions

### `IAsmEditor`

- **位置**: `dnSpy.Contracts.DnSpy/AsmEditor/IAsmEditor.cs`
- **简要说明**: top-level contract

### `IMemberEditor`

- **位置**: `dnSpy.Contracts.DnSpy/AsmEditor/IMemberEditor.cs`
- **简要说明**: per-member edit interface

## `BackgroundImage/`

- **位置**: `dnSpy.Contracts.DnSpy/BackgroundImage/`
- **简要说明**: background image provider

## `Bookmarks/`

- **位置**: `dnSpy.Contracts.DnSpy/Bookmarks/`

### `IBookmark` / `IBookmarkService` / `IBookmarkListener`

- **位置**: `dnSpy.Contracts.DnSpy/Bookmarks/`
- **可见性**: public
- **简要说明**: bookmark service + per-bookmark contract

## `Command/`

### `IWpfCommandService.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Command/IWpfCommandService.cs`
- **简要说明**: command registration

#### `WpfCommand Create(Guid guid, ...)` / `GetCommand(Guid)` / `Remove(...)`

- **可见性**: public

### `IWpfCommands.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Command/IWpfCommands.cs`
- **简要说明**: command registry (per-menu)

### `WpfCommand.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Command/WpfCommand.cs`
- **简要说明**: command contract

## `Controls/`

- **位置**: `dnSpy.Contracts.DnSpy/Controls/`
- **简要说明**: custom WPF control contracts

## `Decompiler/`

### `IDecompilerService.cs`

#### `IDecompilerService` (public interface)

- **位置**: `dnSpy.Contracts.DnSpy/Decompiler/IDecompilerService.cs`
- **可见性**: public
- **简要说明**: decompiler service contract

##### `IEnumerable<IDecompiler> AllDecompilers { get; }`

- **可见性**: public

##### `IDecompiler Decompiler { get; set; }`

- **可见性**: public

##### `event EventHandler DecompilerChanged`

- **可见性**: public

##### `IDecompiler? Find(Guid)`

- **可见性**: public

##### `IDecompiler FindOrDefault(Guid)`

- **可见性**: public

### `IMethodDebugService.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Decompiler/IMethodDebugService.cs`
- **简要说明**: step-info bridge (which decompiled line corresponds to which IL offset)

## `Disassembly/`

- **位置**: `dnSpy.Contracts.DnSpy/Disassembly/`
- **简要说明**: disassembly view contracts

## `Documents/`

### `IDsDocument` / `IDsDocumentService` / `IDsPEDocument` / ...

- **位置**: `dnSpy.Contracts.DnSpy/Documents/`
- **简要说明**: document model contracts

#### `IDsDocumentService.GetDocuments()`

- **可见性**: public
- **简要说明**: list of loaded documents

#### `IDsDocumentService.DisableAssemblyLoad()`

- **可见性**: public
- **简要说明**: `IDisposable` scope guard

#### `IDsDocumentService.CollectionChanged` (event)

- **可见性**: public

#### `IDsDocumentService.AssemblyResolver`

- **可见性**: public

### `Documents/Tabs/`

- **位置**: `dnSpy.Contracts.DnSpy/Documents/Tabs/`
- **简要说明**: tab model contracts

#### `IDocumentTab` / `IDocumentTabService` / `IReferenceDocumentTabContentProvider`

- **位置**: `dnSpy.Contracts.DnSpy/Documents/Tabs/`
- **简要说明**: tab contracts

### `Documents/TreeView/`

- **位置**: `dnSpy.Contracts.DnSpy/Documents/TreeView/`
- **简要说明**: tree-view contracts

#### `IDocumentTreeView` / `IDocumentTreeNodeProvider` / `DocumentTreeNodeData`

- **位置**: `dnSpy.Contracts.DnSpy/Documents/TreeView/`
- **简要说明**: tree-view contracts

### `Documents/AnnotationsImpl.cs` / `DocumentConstants.cs` / `DotNetReferences.cs` / `ReferenceNavigator.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Documents/`
- **简要说明**: helpers

## `ETW/`

### `DnSpyEventSource.cs`

- **位置**: `dnSpy.Contracts.DnSpy/ETW/DnSpyEventSource.cs`
- **简要说明**: ETW `EventSource`

#### `StartupStart` / `StartupStop` (events)

- **可见性**: public
- **简要说明**: emitted by the main app

## `Extension/`

### `IExtension.cs`

#### `IExtension` (public interface)

- **位置**: `dnSpy.Contracts.DnSpy/Extension/IExtension.cs`
- **可见性**: public
- **简要说明**: per-extension entry

##### `ExtensionInfo ExtensionInfo { get; }`

- **可见性**: public
- **简要说明**: metadata (name, author, version)

##### `IEnumerable<string> MergedResourceDictionaries { get; }`

- **可见性**: public
- **简要说明**: XAML resource dictionaries to merge

##### `void OnEvent(ExtensionEvent, object?)`

- **可见性**: public
- **简要说明**: lifecycle callback

### `[ExportExtension]` (custom MEF attribute)

- **位置**: `dnSpy.Contracts.DnSpy/Extension/IExtension.cs`
- **简要说明**: `[MetadataAttribute, Export(typeof(IExtension))]`

### `IAutoLoaded` / `IAutoLoadedMetadata`

- **位置**: `dnSpy.Contracts.DnSpy/Extension/IAutoLoaded.cs`
- **简要说明**: hooks for `BeforeExtensions`, `AfterExtensions`, `AfterExtensionsLoaded`

### `ExtensionInfo.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Extension/ExtensionInfo.cs`
- **简要说明**: DTO with extension metadata

## `Hex/`

- **位置**: `dnSpy.Contracts.DnSpy/Hex/`
- **简要说明**: hex editor contracts

## `Images/`

### `IImageService` / `IImageSource`

- **位置**: `dnSpy.Contracts.DnSpy/Images/`
- **简要说明**: image service contracts

## `Language/`

### `ILanguageManager` / language GUIDs

- **位置**: `dnSpy.Contracts.DnSpy/Language/`
- **简要说明**: language-manager contract

## `Menus/`

### `IMenuService` / `IMenuItem` / `IMenuItemProvider` / `IContextMenuProvider`

- **位置**: `dnSpy.Contracts.DnSpy/Menus/`
- **简要说明**: menu + context-menu contracts

## `Metadata/`

- **位置**: `dnSpy.Contracts.DnSpy/Metadata/`
- **简要说明**: UI-layer metadata helpers

## `MVVM/`

- **位置**: `dnSpy.Contracts.DnSpy/MVVM/`

### `IInitializeDataTemplate.cs`

- **位置**: `dnSpy.Contracts.DnSpy/MVVM/IInitializeDataTemplate.cs`
- **简要说明**: VM <-> View template initialization

### `RelayCommand.cs`

- **位置**: `dnSpy.Contracts.DnSpy/MVVM/RelayCommand.cs`
- **简要说明**: `ICommand` impl

### `ListVM.cs` / `EnumVM.cs` / `DataFieldVM.cs`

- **位置**: `dnSpy.Contracts.DnSpy/MVVM/`
- **简要说明**: VM bases

## `Output/`

### `IOutputService.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Output/IOutputService.cs`
- **简要说明**: Output tool-window service contract

## `Scripting/`

### `IScriptService.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Scripting/IScriptService.cs`
- **简要说明**: scripting contract

## `Search/`

- **位置**: `dnSpy.Contracts.DnSpy/Search/`
- **简要说明**: search contracts

### `IDocumentSearcher` / `ISearchComparer` / `ISearchResult` / Filters

- **位置**: `dnSpy.Contracts.DnSpy/Search/`
- **简要说明**: search contracts

### `SearchComparers.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Search/SearchComparers.cs`
- **简要说明**: `RegExSearchComparer` / `AndSearchComparer` / `OrSearchComparer`

## `Settings/`

### `ISettingsService.cs` / `ISettingsSection.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Settings/`
- **简要说明**: settings contracts

### `XmlSettingsReader.cs` / `XmlSettingsWriter.cs`

- **位置**: `dnSpy.Contracts.DnSpy/Settings/`
- **简要说明**: XML serialization

## `Tabs/`

### `ITabService` / `ITabGroupService` / `ITabGroup` / `ITabContent`

- **位置**: `dnSpy.Contracts.DnSpy/Tabs/`
- **简要说明**: tab model contracts

## `Text/`

- **位置**: `dnSpy.Contracts.DnSpy/Text/`
- **简要说明**: text editor contracts (classification, projection, ...)

## `Themes/`

- **位置**: `dnSpy.Contracts.DnSpy/Themes/`
- **简要说明**: theme manager contract

## `ToolBars/`

- **位置**: `dnSpy.Contracts.DnSpy/ToolBars/`
- **简要说明**: toolbar service contracts

## `ToolWindows/`

- **位置**: `dnSpy.Contracts.DnSpy/ToolWindows/`

### `IToolWindowService` / `AppToolWindow*`

- **位置**: `dnSpy.Contracts.DnSpy/ToolWindows/`
- **简要说明**: tool-window framework

## `TreeView/`

- **位置**: `dnSpy.Contracts.DnSpy/TreeView/`
- **简要说明**: sharp tree-view contracts

## `Utilities/`

- **位置**: `dnSpy.Contracts.DnSpy/Utilities/`
- **简要说明**: misc helpers

## `Decompiler/IDecompiler.cs` (in `dnSpy.Contracts.Logic`)

### `IDecompiler` (public interface) — `dnSpy.Contracts.Logic/Decompiler/IDecompiler.cs`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/IDecompiler.cs:1`
- **可见性**: public
- **简要说明**: per-language decompiler contract

#### `DecompilerSettingsBase Settings { get; }`

- **可见性**: public

#### `string ContentTypeString { get; }`

- **可见性**: public

#### `string GenericNameUI { get; }` / `string UniqueNameUI { get; }`

- **可见性**: public

#### `double OrderUI { get; }`

- **可见性**: public

#### `Guid GenericGuid { get; }` / `Guid UniqueGuid { get; }`

- **可见性**: public

#### `string FileExtension { get; }` / `string? ProjectFileExtension { get; }`

- **可见性**: public

#### `void WriteName(...)` / `void WriteType(...)`

- **可见性**: public
- **简要说明**: helper emissions

#### `void Decompile(MethodDef methodDef, IDecompilerOutput output, DecompilationContext context)`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/IDecompiler.cs:1`
- **可见性**: public
- **调用了**: emits tokens to `output`
- **简要说明**: per-method decompile

#### `void Decompile(PropertyDef, ...)` / `void Decompile(FieldDef, ...)` / `void Decompile(EventDef, ...)` / `void Decompile(TypeDef, ...)`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/IDecompiler.cs:1`
- **可见性**: public
- **简要说明**: per-member-kind decompile

## `Decompiler/IDecompilerOutput.cs` (in `dnSpy.Contracts.Logic`)

### `IDecompilerOutput` (public interface) — `dnSpy.Contracts.Logic/Decompiler/IDecompilerOutput.cs`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/IDecompilerOutput.cs:1`
- **可见性**: public
- **简要说明**: color-aware output sink

#### `void Write(...)` (overloads)

- **可见性**: public
- **简要说明**: write one token with optional color

#### `void IncreaseIndent()` / `DecreaseIndent()`

- **可见性**: public

#### `void WriteLine()`

- **可见性**: public

#### `void WriteCustom(...)`

- **可见性**: public

## `Decompiler/DecompilationContext.cs` (in `dnSpy.Contracts.Logic`)

### `DecompilationContext`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/DecompilationContext.cs`
- **简要说明**: settings + cancellation + scoped data

## `Decompiler/ITextColorWriter.cs` (in `dnSpy.Contracts.Logic`)

### `ITextColorWriter`

- **位置**: `dnSpy.Contracts.Logic/Decompiler/ITextColorWriter.cs`
- **简要说明**: writes a span with a color