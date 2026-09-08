# 08 — `dnSpy` (Main WPF Application)

This file documents the public surface of the main WPF application (`dnSpy/dnSpy/dnSpy/`). The startup path is `StartUpClass.Main` -> `App` (MEF init) -> `AppWindow` -> `MainWindowControl`.

## `MainApp/StartUpClass.cs`

### `StartUpClass` (public static class) — `dnSpy/dnSpy/dnSpy/MainApp/StartUpClass.cs:31`

- **可见性**: public, static
- **简要说明**: `[STAThread] Main` entry; multicore-JIT + BG JIT profile.

#### `public static void Main()`

- **签名**: `static void Main()`
- **位置**: `dnSpy/dnSpy/dnSpy/MainApp/StartUpClass.cs:33`
- **可见性**: public, static, `[STAThread]`
- **抛出/异常**: forwards `App` exceptions
- **调用了**: `new App(readSettings, startupStopwatch).Run()`
- **简要说明**: WPF entry point.

## `MainApp/App.xaml.cs`

### `App` (sealed partial class) — `dnSpy/dnSpy/dnSpy/MainApp/App.xaml.cs:97`

- **可见性**: public, sealed, partial, `Application`
- **简要说明**: WPF bootstrap. Starts MEF discovery in the background.

#### `Task<ExportProvider> initializeMEFTask`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: the in-progress MEF composition task

#### `ExportProvider? exportProvider`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: the resolved MEF provider, set after `InitializeMEF`

#### `public App(bool readSettings, Stopwatch startupStopwatch)`

- **签名**: `App(bool readSettings, Stopwatch startupStopwatch)`
- **位置**: `MainApp/App.xaml.cs:97`
- **可见性**: public
- **参数**: `readSettings` — false to skip reading settings (Shift-click bypass), `startupStopwatch` — for `--show-startup-time`
- **副作用**: schedules MEF composition
- **调用了**: `Task.Run(() => InitializeMEF(readSettings, useCache: readSettings))`
- **简要说明**: WPF Application ctor; non-blocking MEF init

#### `public ExportProvider InitializeMEF(bool readSettings, bool useCache)`

- **签名**: `ExportProvider InitializeMEF(bool readSettings, bool useCache)`
- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: public
- **抛出/异常**: `CompositionFailedException`
- **调用了**: `TryCreateExportProviderFactoryCached` (when `useCache`) or `CreateExportProviderFactorySlow`
- **简要说明**: builds the MEF `ExportProvider` once

#### `IExportProviderFactory? TryCreateExportProviderFactoryCached(Resolver, bool useCache, out long resourceManagerTokensOffset)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: try the cached composition path (`CachedMefInfo`)

#### `IExportProviderFactory CreateExportProviderFactorySlow(Resolver)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: full composition

#### `Assembly[] GetAssemblies()`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: list of built-in assemblies for VS-MEF discovery

#### `Assembly[] LoadExtensionAssemblies()`

- **位置**: `MainApp/App.xaml.cs:316-371`
- **可见性**: internal
- **副作用**: `Assembly.LoadFrom(file)` for each `*.x.dll`
- **简要说明**: enumerates extension assemblies

#### `IEnumerable<string> GetExtensionFiles(string dir)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: finds `*.x.dll` in a directory

#### `bool CanLoadExtension(string file)` / `bool CanLoadExtension(Assembly asm)`

- **位置**: `MainApp/App.xaml.cs:362-401`
- **可见性**: internal
- **简要说明**: reads `<file>.xml` `ExtensionConfig` (OS / Framework / App version check) + assembly public-key + min version

#### `override void OnStartup(StartupEventArgs e)`

- **位置**: `MainApp/App.xaml.cs:521`
- **可见性**: public, override
- **抛出/异常**: forwards exceptions to `AppDomain.UnhandledException`
- **调用了**: blocks on `initializeMEFTask.GetAwaiter().GetResult()`, `SwitchToOtherInstance()`, `cultureService.Initialize(args)`, `GetExportedValue<IDpiService>()`, `appWindow.InitializeMainWindow()`, `HandleAppArgs(args)`, `HandleAppArgs2(args)`
- **简要说明**: WPF `Application.OnStartup`; awaits MEF, opens main window

#### `void HandleAppArgs(IAppCommandLineArgs args)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: applies `--language`, `--new-tab`, `--full-screen`, opens files via `OpenDocumentsHelper`

#### `void HandleAppArgs2(IAppCommandLineArgs args)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: dispatches to all `IAppCommandLineArgsHandler` exports in `Order` ascending

#### `void SwitchToOtherInstance()`

- **位置**: `MainApp/App.xaml.cs:411-470`
- **可见性**: internal
- **副作用**: forwards args via `WM_COPYDATA` (header `0x11C9B152`)
- **简要说明**: single-instance IPC

#### `IDecompiler? GetDecompiler(string language)`

- **位置**: `MainApp/App.xaml.cs:1`
- **可见性**: internal
- **简要说明**: resolve `IDecompiler` by name or GUID

## `MainApp/AppCommandLineArgs.cs` (273 LoC, ~25 flags)

### `AppCommandLineArgs` (sealed class) — `MainApp/AppCommandLineArgs.cs`

- **可见性**: public, sealed
- **简要说明**: parsed CLI args.

#### `public AppCommandLineArgs(string[] args)`

- **签名**: `AppCommandLineArgs(string[])`
- **位置**: `MainApp/AppCommandLineArgs.cs:61`
- **可见性**: public
- **调用了**: parses every flag
- **简要说明**: ctor parses args

#### All 25 properties (`SettingsFilename`, `Filenames`, `SingleInstance`, `Activate`, `Language`, `Culture`, `SelectMember`, `NewTab`, `SearchText`, `SearchFor`, `SearchIn`, `Theme`, `LoadFiles`, `FullScreen`, `ShowToolWindow`, `HideToolWindow`, `ShowStartupTime`, `DebugAttachPid`, `DebugEvent`, `JitDebugInfo`, `DebugAttachProcess`, `ExtraExtensionDirectory`)

- **位置**: `MainApp/AppCommandLineArgs.cs:31-52`
- **可见性**: public, get-only
- **简要说明**: each property maps to one CLI flag (see [06_build_and_run.md](../06_build_and_run.md))

#### `public bool HasArgument(string argName)`

- **签名**: `bool HasArgument(string)`
- **位置**: `MainApp/AppCommandLineArgs.cs:264`
- **可见性**: public
- **简要说明**: user-args lookup (`argName` from `argName:value`)

#### `public string? GetArgumentValue(string argName)`

- **签名**: `string? GetArgumentValue(string)`
- **位置**: `MainApp/AppCommandLineArgs.cs:266`
- **可见性**: public
- **简要说明**: user-args value

#### `public IEnumerable<(string argument, string value)> GetArguments()`

- **位置**: `MainApp/AppCommandLineArgs.cs:271`
- **可见性**: public
- **简要说明**: all user-args

## `MainApp/AppCommandLineArgsHandler.cs`

- **位置**: `dnSpy/dnSpy/dnSpy/MainApp/AppCommandLineArgsHandler.cs`
- **简要说明**: `IAppCommandLineArgsHandler` impl for the main app

## `MainApp/AppWindow.cs` (225 LoC)

### `AppWindow` — `MainApp/AppWindow.cs`

- **位置**: `MainApp/AppWindow.cs:1`
- **MEF**: `[Export, Export(typeof(IAppWindow))] sealed class AppWindow : IAppWindow, IDsLoaderContentProvider`
- **可见性**: public, sealed
- **简要说明**: `IAppWindow` impl; the actual main window

#### `AppWindow` ctor (`[ImportingConstructor]`)

- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public
- **简要说明**: pulls all MEF dependencies

#### `public Window InitializeMainWindow()`

- **签名**: `Window InitializeMainWindow()`
- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public
- **返回值**: the constructed `Window`
- **调用了**: builds `StackedContent`, `MainWindow`, `MainWindowControl`
- **简要说明**: main-window assembly

#### `public void RefreshToolBar()`

- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public

#### `public void AddTitleInfo(...)` / `RemoveTitleInfo(...)`

- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public
- **简要说明**: status-bar info chips (e.g. "Debugging")

#### `public event EventHandler<CancelEventArgs>? MainWindowClosing`

- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public

#### `public event EventHandler? MainWindowClosed`

- **位置**: `MainApp/AppWindow.cs:1`
- **可见性**: public

## `MainApp/MainWindowControl.cs` (638 LoC)

### `MainWindowControl`

- **位置**: `MainApp/MainWindowControl.cs:1`
- **可见性**: internal (WPF element)
- **简要说明**: dock layout — left/right/top/bottom tool windows + horizontal/vertical stacked content

### `MainWindowControlState`

- **位置**: `MainApp/MainWindowControl.cs:9`
- **可见性**: internal
- **简要说明**: serialized state (tool window placement, splitter distances)

## `MainApp/DsLoaderService.cs`

### `DsLoaderService` (sealed) — `MainApp/DsLoaderService.cs`

- **MEF**: `[Export(typeof(IDsLoaderService))] sealed class DsLoaderService : IDsLoaderService`
- **可见性**: public, sealed
- **简要说明**: splash-screen loader driver; chains `IDsLoader`s from MEF

#### `DsLoaderService` ctor

- **位置**: `MainApp/DsLoaderService.cs:1`
- **MEF**: `[ImportMany] IEnumerable<Lazy<IDsLoader, IDsLoaderMetadata>> mefLoaders`
- **简要说明**: discovers all `IDsLoader`s

#### `public void Initialize(IDsLoaderContentProvider, Window, IAppCommandLineArgs)`

- **位置**: `MainApp/DsLoaderService.cs:1`
- **可见性**: public
- **副作用**: starts splash screen, runs loaders
- **简要说明**: drives the splash

#### `public event EventHandler? OnAppLoaded`

- **位置**: `MainApp/DsLoaderService.cs:1`
- **可见性**: public
- **简要说明**: raised when all loaders finish

## `MainApp/CachedMefInfo.cs` (173 LoC)

- **位置**: `dnSpy/dnSpy/dnSpy/MainApp/CachedMefInfo.cs`
- **简要说明**: cached MEF composition binary blob (`dnSpy-mef-info.bin` in profile dir)

## `MainApp/BGJitUtils.cs`

- **位置**: `MainApp/BGJitUtils.cs`
- **简要说明**: BG-JIT profile folder helpers

## `MainApp/Constants.cs`

- **位置**: `MainApp/Constants.cs`
- **简要说明**: constant strings

## `MainApp/DotNetAssemblyLoader.cs`

- **位置**: `MainApp/DotNetAssemblyLoader.cs`
- **简要说明**: `Assembly.LoadFrom` wrapper that handles .NET Framework vs .NET 5+

## `MainApp/ResourceManagerTokenCacheImpl.cs`

- **位置**: `MainApp/ResourceManagerTokenCacheImpl.cs`
- **简要说明**: caches `ResourceManager` tokens

## `MainApp/SavedWindowState.cs`

- **位置**: `MainApp/SavedWindowState.cs`
- **简要说明**: window position persistence

## `MainApp/DevBuildWarning.cs`

- **位置**: `MainApp/DevBuildWarning.cs`
- **简要说明**: shows a nag screen on dev builds

## `MainApp/ToolBarCommands.cs` / `ViewCommands.cs`

- **位置**: `MainApp/ToolBarCommands.cs` / `ViewCommands.cs`
- **简要说明**: command registrations

## `MainApp/DocumentTreeViewWindowContent.cs`

- **位置**: `MainApp/DocumentTreeViewWindowContent.cs`
- **简要说明**: tool-window content for the document tree

## `MainApp/AboutCommands.cs` / `MainApp/AboutScreen.cs`

- **位置**: `MainApp/`
- **简要说明**: About commands + About dialog

## `MainApp/AskDlg.xaml*` / `AskVM.cs`

- **位置**: `MainApp/AskDlg.*` / `AskVM.cs`
- **简要说明**: Yes/No/Cancel dialog

## `MainApp/MsgBoxDlg.xaml*` / `MsgBoxVM.cs` / `MainApp/MessageBoxService.cs`

- **位置**: `MainApp/`
- **简要说明**: message-box service

## `MainApp/DsLoaderControl.xaml*` / `MainApp/DsLoaderService.cs`

- **位置**: `MainApp/`
- **简要说明**: splash-screen UI

## `MainApp/MainWindow.xaml*`

- **位置**: `MainApp/MainWindow.xaml` + `MainWindow.xaml.cs`
- **简要说明**: WPF window (XAML + code-behind)

## `MainApp/Extension/ExtensionService.cs`

### `ExtensionService` (sealed) — `MainApp/Extension/ExtensionService.cs`

- **MEF**: `[Export, Export(typeof(IExtensionService))]`
- **可见性**: public, sealed
- **简要说明**: loads `IExtension`s; merges resource dictionaries

#### `public void LoadExtensions(Collection<ResourceDictionary> resourceDictionaries)`

- **位置**: `MainApp/Extension/ExtensionService.cs:1`
- **可见性**: public
- **副作用**: merges `IExtension.MergedResourceDictionaries`
- **简要说明**: UI theme merging

#### `public void NotifyExtensions(ExtensionEvent, object?)`

- **位置**: `MainApp/Extension/ExtensionService.cs:1`
- **可见性**: public
- **简要说明**: broadcast to all `IExtension.OnEvent`

## `MainApp/Extension/ExtensionConfig.cs` / `ExtensionConfigReader.cs` / `LoadedExtension.cs`

- **位置**: `MainApp/Extension/`
- **简要说明**: parses the `<file>.xml` extension config

## `MainApp/DsToolWindowServiceCommands.cs`

- **位置**: `MainApp/DsToolWindowServiceCommands.cs`
- **简要说明**: tool-window commands

## `Documents/DsDocumentService.cs`

### `DsDocumentService` (sealed) — `Documents/DsDocumentService.cs`

- **MEF**: `[Export(typeof(IDsDocumentService))] sealed class DsDocumentService : IDsDocumentService`
- **可见性**: public, sealed
- **简要说明**: the model — list of loaded assemblies

#### `public IDsDocument[] GetDocuments()`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **简要说明**: snapshot of loaded documents

#### `public void Add(IDsDocument)`

- **位置**: `Documents/DsDocumentService.cs:103+`
- **可见性**: public
- **副作用**: guarded by `ReaderWriterLockSlim`; fires `CollectionChanged`
- **简要说明**: add a document

#### `public IDisposable DisableAssemblyLoad()`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **简要说明**: temporary guard against auto-load during sensitive operations

#### `public event EventHandler<NotifyDocumentCollectionChangedEventArgs>? CollectionChanged`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public

#### `public IAssemblyResolver AssemblyResolver { get; }`

- **位置**: `Documents/DsDocumentService.cs:1`
- **可见性**: public
- **简要说明**: shared assembly resolver

## `Documents/Tabs/DocumentTabService.cs`

### `DocumentTabService` (sealed) — `Documents/Tabs/DocumentTabService.cs`

- **MEF**: `[Export, Export(typeof(IDocumentTabService))]`
- **可见性**: public, sealed
- **简要说明**: the tab manager

#### `public DocumentTreeView DocumentTreeView { get; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public

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
- **简要说明**: visible tabs first

#### `public IDocumentTab? ActiveTab { get; set; }`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public

#### `public IDocumentTab GetOrCreateActiveTab()`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **简要说明**: lazy-create an active tab

#### `void DocumentTreeView_NodeActivated(...)`

- **位置**: `Documents/Tabs/DocumentTabService.cs:1`
- **可见性**: public
- **副作用**: opens / switches tabs
- **简要说明**: main entry for tree-node activation

## `Documents/Tabs/DocumentTabServiceSettings.cs` / `DocumentTabServiceLoader.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: settings + loader

## `Documents/Tabs/DocumentTabContentFactoryService.cs` / `DocumentTabContentFactoryContext.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: factories for tab content (decompile / Roslyn edit / etc.)

## `Documents/Tabs/DocumentTreeNodeDecompiler.cs`

- **位置**: `Documents/Tabs/DocumentTreeNodeDecompiler.cs`
- **简要说明**: bridges `IDocumentTreeNodeData` to `IDecompiler.Decompile`

## `Documents/Tabs/DocumentTabSerializer.cs` / `DsDocumentInfoSerializer.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: tab-content serialization (session save)

## `Documents/Tabs/DocumentTabUIContextLocator.cs` / `DocumentTabUIContextLocatorProvider.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: UI-context routing

## `Documents/Tabs/DocumentList.cs` / `DocumentListLoader.cs` / `DocumentListService.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: the user's document list (persisted)

## `Documents/Tabs/AppCommandLineArgsHandler.cs` / `EntryPointCommands.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: `--select`, `--new-tab` handling

## `Documents/Tabs/Commands.cs` / `GoToTokenCommand.cs` / `CopyTokenCommand.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: commands

## `Documents/Tabs/DocTabReferenceNavigator.cs` / `DefaultDecompileNode.cs` / `DecompilationCache.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: reference navigation + decompile cache

## `Documents/Tabs/AsyncShowResult.cs` / `DefaultDocumentList.cs` / `DefaultDocumentTabContentProvider.cs`

- **位置**: `Documents/Tabs/`
- **简要说明**: defaults

## `Documents/Tabs/Dialogs/` / `DocViewer/` / `Hex/`

- **位置**: `Documents/Tabs/`
- **简要说明**: per-tab dialogs + viewers

## `Documents/TreeView/`

### `DocumentTreeView`

- **位置**: `Documents/TreeView/DocumentTreeView.cs`
- **可见性**: public
- **简要说明**: WPF tree-view of loaded documents (uses vendored `ICSharpCode.TreeView`)

#### `public event EventHandler<DocumentTreeNodeActivatedEventArgs> NodeActivated`

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public

#### `public IDsDocumentService DocumentService { get; }`

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public

#### `public void SelectItems(...)`

- **位置**: `Documents/TreeView/DocumentTreeView.cs:1`
- **可见性**: public
- **简要说明**: navigate to a specific node

### `DocumentTreeViewSettings`

- **位置**: `Documents/TreeView/DocumentTreeViewSettings.cs`
- **简要说明**: persisted settings

### `(resource folders / nodes / providers / filters)`

- **位置**: `Documents/TreeView/`
- **简要说明**: many small files — one class per node kind

## `Tabs/TabService.cs` / `TabServiceProvider.cs` / `TabGroup.cs` / `TabGroupService.cs` / `TabItemImpl.cs` / `TabElementZoomer.cs` / `TabUtils.cs`

- **位置**: `dnSpy/dnSpy/dnSpy/Tabs/`
- **简要说明**: generic WPF tab control layer

## `Decompiler/DecompilerService.cs` / `DecompilerServiceSettings.cs` / `DecompilerAppSettingsPageContainer.cs` / `MethodDebugService.cs` / `DummyDecompiler.cs`

- **位置**: `dnSpy/dnSpy/dnSpy/Decompiler/`
- **简要说明**: decompiler service implementation

## `Search/` — full search subsystem

### `Search/SearchService.cs`

- **MEF**: `[Export]`
- **简要说明**: facade

### `Search/DocumentSearcher.cs`

#### `public void Start(IEnumerable<DsDocumentNode> nodes)`

- **签名**: `void Start(IEnumerable<DsDocumentNode>)`
- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public
- **副作用**: spawns async search
- **调用了**: `FilterSearcher.FilterAsync`

#### `public void Start(IEnumerable<SearchTypeInfo> typeInfos)`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public
- **简要说明**: alternate entry

#### `public void Cancel()`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public
- **简要说明**: abort

#### `public bool TooManyResults { get; }`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public
- **简要说明**: cancellation signal

#### `public bool SyntaxHighlight { get; set; }`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public
- **简要说明**: highlight matched text

#### `public IDecompiler Decompiler { get; }`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public

#### `public ISearchResult? SearchingResult { get; }`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public

#### `public event EventHandler? OnSearchCompleted`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public

#### `public event EventHandler<SearchResultEventArgs>? OnNewSearchResults`

- **位置**: `Search/DocumentSearcher.cs:1`
- **可见性**: public

### `Search/DocumentSearcherProvider.cs`

- **MEF**: `[Export(typeof(IDocumentSearcherProvider))]`
- **简要说明**: factory

### `Search/FilterSearcher.cs` / `FilterSearcherOptions.cs`

- **位置**: `Search/`
- **简要说明**: walks the document trees and applies the comparer

### `Search/SearchControl.xaml*` / `SearchControlVM.cs`

- **位置**: `Search/`
- **简要说明**: search tool-window UI + VM

### `Search/SearchResultContext.cs` / `SearchResult.cs` / `SearchSettings.cs` / `SearchType.cs` / `SearchTypeVM.cs` / `SearchToolWindowContent.cs`

- **位置**: `Search/`
- **简要说明**: search types + results + tool-window

### `Search/FrameworkFileUtils.cs` / `AppCommandLineArgsHandler.cs`

- **位置**: `Search/`
- **简要说明**: utilities

### `Search/BooleanToThicknessConverter.cs` / `Commands.cs` / `ContentTypeDefinitions.cs`

- **位置**: `Search/`
- **简要说明**: XAML + commands

## `ToolWindows/ToolWindowService.cs` / `ToolWindowServiceProvider.cs` / `ToolWindowGroup.cs` / `ToolWindowGroupService.cs` / `TabContentImpl.cs`

- **位置**: `dnSpy/dnSpy/dnSpy/ToolWindows/`
- **简要说明**: tool-window framework

## `Menus/` / `Commands/` / `TreeView/` / `Metadata/` / `Scripting/`

- **位置**: `dnSpy/dnSpy/dnSpy/`
- **简要说明**: standard MEF service implementations

## `Settings/` / `Output/` / `Bookmarks/` / `ToolBars/` / `TextView/` / `Controls/` / `UI/`

- **位置**: `dnSpy/dnSpy/dnSpy/`
- **简要说明**: standard WPF MVVM support

## `Hex/` (large)

- **位置**: `dnSpy/dnSpy/dnSpy/Hex/`
- **简要说明**: hex editor engine — many WPF controls

## `Text/` (large)

- **位置**: `dnSpy/dnSpy/dnSpy/Text/`
- **简要说明**: `Microsoft.VisualStudio.Text.*` MEF reimplementation

## `Themes/`

- **位置**: `dnSpy/dnSpy/dnSpy/Themes/`
- **简要说明**: blue / dark / light / dark-high-contrast `.dntheme` binary XAML

## `Language/`

- **位置**: `dnSpy/dnSpy/dnSpy/Language/`
- **简要说明**: language preferences (decompiler language, not UI culture)

## `Culture/`

- **位置**: `dnSpy/dnSpy/dnSpy/Culture/`
- **简要说明**: UI culture service (per-language resources)

## `FileLists/`

- **位置**: `dnSpy/dnSpy/dnSpy/FileLists/`
- **简要说明**: DLL enumeration + copy-to-output

## `LicenseInfo/`

- **位置**: `dnSpy/dnSpy/dnSpy/LicenseInfo/`
- **简要说明**: CREDITS.txt embedded

## `Images/`

- **位置**: `dnSpy/dnSpy/dnSpy/Images/`
- **简要说明**: image catalog

## `MVVM/`

- **位置**: `dnSpy/dnSpy/dnSpy/MVVM/`
- **简要说明**: `InitializeDataTemplateContextMenu.cs` + VM helpers

## `BackgroundImage/`

- **位置**: `dnSpy/dnSpy/dnSpy/BackgroundImage/`
- **简要说明**: startup background image provider

## `Events/`

- **位置**: `dnSpy/dnSpy/dnSpy/Events/`
- **简要说明**: `WeakEventList`, `WeakEventSource`

## `Properties/`

- **位置**: `dnSpy/dnSpy/dnSpy/Properties/`
- **简要说明**: `Resources.resx` + `Resources.Designer.cs` (auto-generated)