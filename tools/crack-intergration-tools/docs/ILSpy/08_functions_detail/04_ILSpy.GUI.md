# 08 — `ILSpy` (Avalonia GUI)

This file documents the public surface of the Avalonia GUI project (`ILSpy/ILSpy.csproj`, net10.0, ~120 .cs + 34 .xaml files). The startup path is `Program.cs` -> `App.axaml.cs` -> `AppComposition.Initialize` (MEF) -> `MainWindow`.

## `Program.cs`

### `Program` (public static class) — `ILSpy/Program.cs`

- **可见性**: public, static

#### `[STAThread] public static void Main(string[] args)`

- **位置**: `ILSpy/Program.cs:35`
- **可见性**: public, static, `[STAThread]`
- **参数**: command-line args
- **调用了**: `BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)`
- **简要说明**: Avalonia entry; triggers `App.axaml.cs` lifecycle

#### `static AppBuilder BuildAvaloniaApp()`

- **位置**: `ILSpy/Program.cs:1`
- **可见性**: internal (called from Main)
- **返回值**: `AppBuilder` configured for Avalonia
- **调用了**: `AppBuilder.Configure<App>().UsePlatformDetect().With(new X11PlatformOptions { OverlayPopups = true }).LogToTrace()`
- **简要说明**: Avalonia builder

## `App.axaml.cs`

### `App` (public sealed class) — `ILSpy/App.axaml.cs`

- **可见性**: public, sealed, partial (XAML loads from `App.axaml`)
- **简要说明**: the Avalonia `Application` subclass.

#### `public static CommandLineArguments? CommandLineArguments`

- **位置**: `App.axaml.cs:1`
- **可见性**: public, static
- **简要说明**: parsed CLI args, set in `OnFrameworkInitializationCompleted`

#### `public static CompositionHost? Composition`

- **位置**: `App.axaml.cs:1`
- **可见性**: public, static
- **简要说明**: the MEF container, set after `AppComposition.Initialize`

#### `public static bool SeedFullFrameworkDefaultList`

- **位置**: `App.axaml.cs:1`
- **可见性**: public, static
- **简要说明**: when true, seed with the BCL reference assemblies

#### `override void Initialize()`

- **位置**: `App.axaml.cs:1`
- **可见性**: public, override
- **调用了**: `AvaloniaXamlLoader.Load(this)`
- **简要说明**: Avalonia XAML loader entry

#### `override void OnFrameworkInitializationCompleted()`

- **位置**: `ILSpy/App.axaml.cs:36`
- **可见性**: public, override
- **抛出/异常**: unhandled exceptions bubble to `GlobalExceptionHandler`
- **副作用**: installs `ILSpyTraceListener`, creates MEF container, opens main window
- **调用了**: `CommandLineArguments.Create`, `ILSpySettings.SettingsFilePathProvider`, `AppComposition.Initialize`, `ThemeManager.Current.Attach`, `Composition.GetExport<MainWindow>()`
- **简要说明**: the GUI lifecycle entry after XAML loads

## `AppEnv/AppComposition.cs` (MEF composition)

### `AppComposition` (public static class) — `ILSpy/AppEnv/AppComposition.cs:35`

- **可见性**: public, static
- **简要说明**: builds the `CompositionHost` from built-in assemblies + plugins.

#### `public static CompositionHost Current { get; }`

- **位置**: `AppComposition.cs:47`
- **可见性**: public, static
- **简要说明**: the live container

#### `public static T? TryGetExport<T>() where T : class`

- **位置**: `AppComposition.cs:57`
- **可见性**: public, static
- **简要说明**: get one export, or null

#### `public static IEnumerable<T> TryGetExports<T>() where T : class`

- **位置**: `AppComposition.cs:64`
- **可见性**: public, static
- **简要说明**: get all exports

#### `public static CompositionHost Initialize()`

- **位置**: `AppComposition.cs:67`
- **可见性**: public, static
- **抛出/异常**: `CompositionFailedException`
- **副作用**: composes the MEF container, assigns to `App.Composition`
- **调用了**: `RegisterPluginResolver`, `CreateContainer`
- **简要说明**: one-time MEF bootstrap

#### `public static void RegisterPluginResolver()`

- **位置**: `AppComposition.cs:78`
- **可见性**: public, static
- **副作用**: hooks `AssemblyLoadContext.Default.Resolving`, calls `LoadPlugins`
- **简要说明**: sets up plugin discovery

#### `public static CompositionHost CreateContainer()`

- **位置**: `AppComposition.cs:99`
- **可见性**: public, static
- **返回值**: the new `CompositionHost`
- **调用了**: `ContainerConfiguration().WithAssemblies(...).CreateContainer()`
- **简要说明**: builds the MEF container

## `AppEnv/CommandLineArguments.cs`

### `CommandLineArguments` (public class) — `ILSpy/AppEnv/CommandLineArguments.cs`

- **可见性**: public
- **简要说明**: parsed CLI args

#### `public static CommandLineArguments? Create(IEnumerable<string> args)`

- **位置**: `CommandLineArguments.cs:40-103`
- **可见性**: public, static
- **参数**: command-line args
- **返回值**: parsed args or null when no args
- **简要说明**: parses all flags

#### `public bool NewInstance { get; }`

- **简要说明**: `--newinstance`

#### `public string? Navigateto { get; }`

- **简要说明**: `-n|--navigateto`

#### `public string? Search { get; }`

- **简要说明**: `-s|--search`

#### `public string? Language { get; }`

- **简要说明**: `-l|--language`

#### `public string? Config { get; }`

- **简要说明**: `-c|--config`

#### `public bool NoActivate { get; }`

- **简要说明**: `--noactivate`

#### `public IReadOnlyList<string> Assemblies { get; }`

- **简要说明**: positional assembly paths

## `Entry.cs`

### `Entry` (public class) — `ILSpy/Entry.cs`

- **可见性**: public
- **简要说明**: public facade for embedding ILSpy in a host.

#### `public Entry(...)` (ctor)

- **位置**: `Entry.cs:1`
- **可见性**: public
- **参数**: settings file path, app data dir, etc.

#### `public void ShowAssemblies(IEnumerable<string> files)`

- **位置**: `Entry.cs:1`
- **可见性**: public
- **简要说明**: load and display the given assemblies

## `NavigationHistory.cs` (148 LoC)

### `NavigationHistory<T>` (public class) — `ILSpy/NavigationHistory.cs`

- **可见性**: public
- **简要说明**: two-stack browser-style back/forward.

#### `public void Record(T entry)`

- **位置**: `NavigationHistory.cs:1`
- **可见性**: public
- **简要说明**: push current

#### `public T? GoBack()`

- **位置**: `NavigationHistory.cs:1`
- **可见性**: public
- **抛出/异常**: throws if `!CanNavigateBack` (caller should check first)
- **调用了**: pop from back stack, push to forward stack

#### `public T? GoForward()`

- **位置**: `NavigationHistory.cs:1`
- **可见性**: public

#### `public bool CanNavigateBack { get; }`

- **位置**: `NavigationHistory.cs:1`
- **可见性**: public

#### `public bool CanNavigateForward { get; }`

- **位置**: `NavigationHistory.cs:1`
- **可见性**: public

## `Commands/`

### `CommandManager` (public static class) — `ILSpy/Commands/CommandManager.cs`

- **可见性**: public, static
- **简要说明**: Avalonia re-query-suggested analog.

#### `public static void InvalidateRequerySuggested()`

- **位置**: `CommandManager.cs:1`
- **可见性**: public, static
- **简要说明**: weak-event re-query signal — every `ICommand.CanExecute` is re-checked

#### `public static event EventHandler? RequerySuggested`

- **位置**: `CommandManager.cs:1`
- **可见性**: public, static
- **简要说明**: weak `RequerySuggested` analog

### `SimpleCommand` (public class) — `ILSpy/Commands/SimpleCommand.cs`

- **可见性**: public
- **简要说明**: minimal `ICommand` impl

### `FileCommands` — `ILSpy/Commands/FileCommands.cs`

- **可见性**: public
- **简要说明**: open, save, recent files, exit
- **MEF**: `[Export]`

### `ViewCommands` — `ILSpy/Commands/ViewCommands.cs`

- **可见性**: public
- **简要说明**: toggle tool panes, font size

### `WindowCommands` — `ILSpy/Commands/WindowCommands.cs`

- **可见性**: public
- **简要说明**: new window, close

### `HelpCommands` — `ILSpy/Commands/HelpCommands.cs`

- **可见性**: public
- **简要说明**: about, docs

### `MainMenuCommandRegistry` — `ILSpy/Commands/MainMenuCommandRegistry.cs`

- **可见性**: public
- **简要说明**: assembles the main menu

### `ToolbarCommandRegistry` — `ILSpy/Commands/ToolbarCommandRegistry.cs`

- **可见性**: public
- **简要说明**: assembles the toolbar

### `ToolPaneRegistry` — `ILSpy/Commands/ToolPaneRegistry.cs`

- **可见性**: public
- **简要说明**: tool-pane provider registry

### `AboutCommand` — `ILSpy/Commands/AboutCommand.cs`

- **简要说明**: About dialog

### `DecompileAllCommand` — `ILSpy/Commands/DecompileAllCommand.cs`

- **简要说明**: decompile all loaded assemblies

### `BrowseBackCommand` / `BrowseForwardCommand`

- **位置**: `ILSpy/Commands/BrowseBackCommand.cs`, `BrowseForwardCommand.cs`
- **简要说明**: history navigation

### `ProjectExport` / `ProjectExporter` / `ProjectExportOptions`

- **位置**: `ILSpy/Commands/ProjectExport*.cs`
- **简要说明**: `-p` GUI equivalent

### `FilePickers`

- **位置**: `ILSpy/Commands/FilePickers.cs`
- **简要说明**: file / folder picker helpers

### `PdbGenerator`

- **位置**: `ILSpy/Commands/PdbGenerator.cs`
- **简要说明**: `-genpdb` GUI equivalent

### `ResourceLinkGenerator`

- **位置**: `ILSpy/Commands/ResourceLinkGenerator.cs`
- **简要说明**: resource-link resolution for tree nodes

### `MainMenuCommandRegistry`

- **位置**: `ILSpy/Commands/MainMenuCommandRegistry.cs`
- **简要说明**: registry that builds the menu at startup

### `ExportCommandAttribute` / `ExportToolPaneAttribute`

- **位置**: `ILSpy/Commands/ExportCommandAttribute.cs`, `ExportToolPaneAttribute.cs`
- **简要说明**: MEF export markers for commands / tool panes

## `AppEnv/ConfigurationFiles.cs`

- **位置**: `ILSpy/AppEnv/ConfigurationFiles.cs`
- **简要说明**: tracks per-user config paths

## `AppEnv/GlobalExceptionHandler.cs`

- **位置**: `ILSpy/AppEnv/GlobalExceptionHandler.cs`
- **简要说明**: unhandled-exception dialog

## `AppEnv/ILSpyTraceListener.cs`

- **位置**: `ILSpy/AppEnv/ILSpyTraceListener.cs`
- **简要说明**: bridges `System.Diagnostics.Trace` to the Output tool window

## `AppEnv/StartupErrorWindow.cs` / `StartupExceptions.cs` / `CompositionErrors.cs`

- **位置**: `ILSpy/AppEnv/`
- **简要说明**: startup error UI

## `AppEnv/ResourceHelper.cs` / `UiContext.cs` / `AppLog.cs` / `AssertionFailedDialog.cs` / `InputDiagnostics.cs`

- **位置**: `ILSpy/AppEnv/`
- **简要说明**: assorted helpers

## `AssemblyTree/AssemblyTreeModel.cs` (1013 LoC)

### `AssemblyTreeModel` (public class) — `ILSpy/AssemblyTree/AssemblyTreeModel.cs`

- **可见性**: public
- **简要说明**: the TreeView hierarchy (assemblies -> namespaces -> types -> members)

#### `public SharpTreeNode Root { get; }`

- **位置**: `AssemblyTreeModel.cs:1`
- **可见性**: public
- **简要说明**: the tree root

#### `event Action? Loaded`

- **位置**: `AssemblyTreeModel.cs:1`
- **简要说明**: raised after a load completes

#### `event Action? Refreshed`

- **位置**: `AssemblyTreeModel.cs:1`
- **简要说明**: raised after refresh

### `AssemblyListNode` / `AssemblyReferenceNode` / `AssemblyReferenceReferencedTypesTreeNode`

- **位置**: `ILSpy/AssemblyTree/`
- **简要说明**: SharpTreeNode subclasses (one per tree-node kind)

### `Compare/*`

- **位置**: `ILSpy/AssemblyTree/Compare/`
- **简要说明**: comparison tree nodes (`ComparisonTreeNode`, `CompareNode`, ...)

## `Search/SearchPane.axaml.cs` + `SearchPaneModel.cs` + `RunningSearch.cs`

### `SearchPane` (Avalonia UserControl) — `ILSpy/Search/SearchPane.axaml.cs`

- **简要说明**: GUI search pane

### `SearchPaneModel` (public class) — `ILSpy/Search/SearchPaneModel.cs`

- **可见性**: public
- **简要说明**: VM for the search pane

#### `public void StartSearch()`

- **位置**: `SearchPaneModel.cs:1`
- **可见性**: public
- **调用了**: `RunningSearch.Start`

#### `public void Cancel()`

- **位置**: `SearchPaneModel.cs:1`
- **可见性**: public

### `RunningSearch` (public class) — `ILSpy/Search/RunningSearch.cs`

- **可见性**: public
- **简要说明**: async driver for active search

#### `public void Start(ISearchStrategy strategy)` (and overloads)

- **位置**: `RunningSearch.cs:1`
- **可见性**: public
- **副作用**: schedules async work

### `AvaloniaSearchResultFactory` — `ILSpy/Search/AvaloniaSearchResultFactory.cs`

- **简要说明**: maps `SearchResult` to `SharpTreeNode`

### `ScopeSearchToAssemblyContextMenuEntry` / `ScopeSearchToNamespaceContextMenuEntry`

- **位置**: `ILSpy/Search/`
- **简要说明**: context-menu entries to scope the search

## `ViewModels/`

### `MainWindowViewModel` (public partial class) — `ILSpy/ViewModels/MainWindowViewModel.cs`

- **可见性**: public, partial
- **MEF**: `[Export][Shared]`
- **简要说明**: top-level VM; pulled by `[ImportingConstructor]`

### `ViewModelBase` — `ILSpy/ViewModels/ViewModelBase.cs`

- **简要说明**: Avalonia `INotifyPropertyChanged` base

### `ToolPaneModel` / `ToolPaneMenuItem` — `ILSpy/ViewModels/`

- **简要说明**: tool-pane VMs

### `ContentTabPage` / `ContentPageModel` / `CompareTabPageModel` / `TabPageModel` / `TabPageMenuItem`

- **位置**: `ILSpy/ViewModels/`
- **简要说明**: tab-page VMs

### `DebugStepsPaneModel` — `ILSpy/ViewModels/DebugStepsPaneModel.cs`

- **简要说明**: Debug Steps pane VM

### `MetadataTablePageModel` — `ILSpy/ViewModels/MetadataTablePageModel.cs`

- **简要说明**: metadata-table page VM

### `NuGetPackageViewModel` / `OpenFromNuGetFeedDialogViewModel` — `ILSpy/ViewModels/`

- **简要说明**: NuGet feed browse VM

### `UpdatePanelViewModel` — `ILSpy/ViewModels/UpdatePanelViewModel.cs`

- **简要说明**: auto-update banner VM

## `Views/`

### `MainWindow` (public partial class) — `ILSpy/Views/MainWindow.axaml.cs`

- **可见性**: public, partial
- **简要说明**: the dock-root window
- **MEF**: `[Export]`

### `MainWindowControl` / dock layout

- **位置**: `ILSpy/Views/`
- **简要说明**: `StackedContent` (toolbar / center / status)

### `CompareView` / `ContentTabPageView` / `DebugStepsView` / `MetadataTablePageView` / `UpdatePanelView`

- **位置**: `ILSpy/Views/`
- **简要说明**: one view per pane

### `CreateListDialog` / `ExportProjectDialog` / `ManageAssemblyListsDialog`

- **位置**: `ILSpy/Views/`
- **简要说明**: dialog windows

### `OpenFromGacDialog` / `OpenFromNuGetFeedDialog` / `SetTargetFrameworkDialog`

- **位置**: `ILSpy/Views/`
- **简要说明**: more dialogs

### `GacEntry` / `DebugStepFilterConverter` / `TargetFrameworkConverter`

- **位置**: `ILSpy/Views/`
- **简要说明**: helpers

## `Languages/`

### `CSharpLanguage` — `ILSpy/Languages/CSharpLanguage.cs`

- **MEF**: `[Export(typeof(ILanguage))]`
- **简要说明**: wires `CSharpDecompiler` to the GUI

### `ILSpyILLanguage` — `ILSpy/Languages/ILSpyILLanguage.cs`

- **MEF**: `[Export(typeof(ILanguage))]`
- **简要说明**: IL output language (uses `ReflectionDisassembler`)

### `VBLanguage` — `ILSpy/Languages/VBLanguage.cs`

- **MEF**: `[Export(typeof(ILanguage))]`
- **简要说明**: VB output language (NRefactory-based legacy)

## `Options/`

- **位置**: `ILSpy/Options/`
- **简要说明**: Avalonia settings-dialog pages (decompiler, display, BAML, ...)

## `Docking/`

### `DockFactory` / `DockWorkspace`

- **位置**: `ILSpy/Docking/`
- **简要说明**: wieslawsoltes/Dock adapter

## `Controls/`

- **位置**: `ILSpy/Controls/`
- **简要说明**: Avalonia custom controls (AvaloniaEdit text view wrapper, search box, ...)

## `Themes/`

- **位置**: `ILSpy/Themes/`
- **简要说明**: Simple theme; `Colors.xaml`

## `TreeNodes/`

- **位置**: `ILSpy/TreeNodes/`
- **简要说明**: ~40 SharpTreeNode subclasses (TypeTreeNode, MethodTreeNode, FieldTreeNode, ResourceTreeNode, ...)

## `Updates/`

- **位置**: `ILSpy/Updates/`
- **简要说明**: NuGet-feed update check

## `NuGetFeeds/`

- **位置**: `ILSpy/NuGetFeeds/`
- **简要说明**: NuGet v3 search + browse

## `Metadata/`

- **位置**: `ILSpy/Metadata/`
- **简要说明**: `MetadataTablePage` + `DecompilerInfoProvider`, `AssemblyListSettings`

## `Bookmarks/`

- **位置**: `ILSpy/Bookmarks/`
- **简要说明**: `BookmarkManager` + bookmark persistence

## `Analyzers/`

- **位置**: `ILSpy/Analyzers/`
- **简要说明**: Avalonia `AnalyzerPane` UI

## `Assets/`

- **位置**: `ILSpy/Assets/`
- **简要说明**: icons + fonts

## `Properties/Resources`

- **位置**: `ILSpy/Properties/`
- **简要说明**: resources (auto-generated)

## `Util/`

- **位置**: `ILSpy/Util/`
- **简要说明**: `WeakEventSource`, ETW helpers, ...

## `TextView/`

- **位置**: `ILSpy/TextView/`
- **简要说明**: decompiled text view (AvaloniaEdit wrapper)

## Other top-level files

- `CompareEngine.cs` — diff two assemblies
- `DecompilationOptions.cs` — per-tab settings + formatting
- `EntityReference.cs` — navigable token wrapper
- `ExtensionMethods.cs` / `FireAndForgetExtensions.cs`
- `Images.cs` — central image registry
- `LanguageSettings.cs` / `SessionSettings.cs` / `SettingsService.cs`
- `SmartTextOutputExtensions.cs` / `SolutionWriter.cs`
- `TaskbarProgressService.cs` / `ViewLocator.cs`