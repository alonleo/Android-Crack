# 03 · UABEANext 架构

## 3.1 总体分层

```
+----------------------------------------------------------------+
|  UABEANext4.Desktop.exe                                        |
|  Program.cs → BuildAvaloniaApp → ClassicDesktopLifetime       |
+----------------------------------------------------------------+
|  UABEANext4.App.axaml.cs (DI 注册)                            |
+----------------------------------------------------------------+
|  Dock UI:                                                      |
|    MainDockFactory → IRootDock                                 |
|    ├─ WorkspaceExplorer (Tool)                                 |
|    ├─ Hierarchy (Tool)                                         |
|    ├─ Inspector (Tool)                                         |
|    └─ Previewer (Tool)                                         |
|    + 多个 Document tabs (Asset, Blank, ...)                    |
+----------------------------------------------------------------+
|  ViewModels (CommunityToolkit.Mvvm):                           |
|    MainViewModel → Workspace, MainDockFactory, currentSel      |
|    Dialogs: 12 个独立 VM                                       |
|    Tools: 5 个 tool VM                                         |
|    Documents: 2 个 document VM                                 |
+----------------------------------------------------------------+
|  Workspace (ObservableObject):                                 |
|    AssetsManager, PluginLoader, AssetNamer, RootItems          |
|    UnsavedItems, ModifiedItems                                 |
+----------------------------------------------------------------+
|  PluginLoader + PluginLoadContext:                             |
|    AssemblyLoadContext 隔离 → IUavPluginOption / Previewer     |
+----------------------------------------------------------------+
|  Logic 层:                                                     |
|    AssetImport/AssetExport (.txt/.json 导入导出)               |
|    SearchLogic (并发搜索)                                      |
|    Mesh/MeshObj                                                |
|    AssetInfo/* (元信息)                                        |
|    ConfigurationManager (config.json 持久化)                   |
+----------------------------------------------------------------+
|  AssetsTools.NET (vendored submodule):                         |
|    BundleFile / AssetsFile / AssetTypeValueField / Replacers   |
+----------------------------------------------------------------+
|  插件 DLL:                                                     |
|    TexturePlugin (TextureLoader + Previewer)                   |
|    AudioPlugin (FMOD5 export)                                  |
|    FontPlugin (TTF/OTF)                                        |
|    TextAssetPlugin + Previewer                                 |
|    MeshPlugin (MeshPreviewer)                                  |
|    PluginPreviewer (独立进程)                                  |
+----------------------------------------------------------------+
|  NativeLibs/{win-x64,linux-x64}/:                              |
|    textureencoder / cuttlefish / PVRTexLib                     |
+----------------------------------------------------------------+
```

## 3.2 模块依赖图

```mermaid
flowchart TB
  subgraph Desktop[Desktop Launcher]
    Prog[Program.cs<br/>UABEANext4.Desktop]
    AppD[App.axaml.cs]
    WinD[Window.axaml]
  end

  subgraph App[Application]
    AppA[App.axaml.cs<br/>67 LoC]
    VL[ViewLocator.cs]
    SS[Services/DialogService]
    CFG[Logic/Configuration/ConfigurationManager]
  end

  subgraph Dock[Dock UI]
    MVF[MainDockFactory<br/>153]
    MV[MainView<br/>XAML]
    MW[MainWindow<br/>XAML]
  end

  subgraph VMs[ViewModels]
    MVM[MainViewModel<br/>851]
    DV[Dialogs/* 12 个 VM]
    TV[Tools/* 5 个 VM]
    DV2[Documents/* 2 个 VM]
    VMB[ViewModelBase]
  end

  subgraph Views[ViewModels Views]
    DVv[Views/Dialogs/* 12 个]
    TVv[Views/Tools/* 7 个]
    DVv2[Views/Documents/* 2 个]
  end

  subgraph Workspace[Workspace]
    WS[Workspace.cs<br/>630]
    WSS[Workspace.Saving.cs<br/>416]
    WSI[WorkspaceItem.cs<br/>102]
    WSIT[WorkspaceItemType.cs]
    AIN[AssetInst.cs]
    DCT[ContainerTool.cs<br/>133]
    DCM[ContainerToolManager.cs<br/>97]
  end

  subgraph Logic[Logic 层]
    AIE[ImportExport/AssetExport 332]
    AII[ImportExport/AssetImport 485]
    SL[Search/SearchLogic]
    ATI[AssetInfo/* 8 个]
    HIR[Hierarchy/HierarchyItem]
    MESH[Mesh/* 3 个]
    MSGS[Messages.cs]
  end

  subgraph Plugins[Plugins]
    PL[PluginLoader<br/>125]
    PLC[PluginLoadContext<br/>46]
    IOP[IUavPluginOption]
    IPR[IUavPluginPreviewer]
    IFU[IUavPluginFunctions]
    UPF[UavPluginFunctions<br/>58]
  end

  subgraph PluginDLL[Plugin DLL]
    TP[TexturePlugin]
    AP[AudioPlugin]
    FP[FontPlugin]
    TAP[TextAssetPlugin]
    MP[MeshPlugin]
    PP[PluginPreviewer]
  end

  subgraph Util[Util]
    AN[AssetNamer<br/>407]
    FTD[FileTypeDetector<br/>67]
    PUtils[PathUtils/SearchUtils/FileUtils]
    MSS[MessageBoxUtil]
    SSrv[StorageService]
  end

  subgraph Converters[Converters]
    CV[6 个 IValueConverter]
  end

  subgraph Controls[Controls]
    ADTV[AssetDataTreeView]
    MPC[MeshPreviewer/*]
  end

  subgraph Vendor[Vendored]
    ATN[AssetsTools.NET]
    Cut[cuttlefish<br/>Crunch]
    PVR[PVRTexLib]
    TEXENC[textureencoder]
    Cpp2IL[Samboy063.LibCpp2IL]
    Cecil[Mono.Cecil]
    Silk[Silk.NET.OpenGL]
    Stb[StbImage*]
  end

  Prog --> AppD
  AppD --> MV
  MV --> MW
  MW --> MVM
  MVM --> MVF
  MVM --> WS
  MVM --> DV
  MVM --> TV
  MVM --> DV2
  MVM --> MSGS

  DV --> DVv
  TV --> TVv
  DV2 --> DVv2
  DVv --> CV
  TVv --> CV

  WS --> AIN
  WS --> WSI
  WS --> ATN
  WS --> PL
  WS --> AN
  WS --> FTD
  WS --> Cpp2IL

  WSS --> SSrv
  WSS --> MSS
  WSS --> WS

  PL --> PLC
  PL --> IOP
  PL --> IPR
  PLC --> ATN
  IOP --> IFU
  IPR --> IFU
  IFU --> UPF
  UPF --> SS

  PL --> TP
  PL --> AP
  PL --> FP
  PL --> TAP
  PL --> MP
  PL --> PP

  TP --> ATN
  TP --> Cut
  TP --> PVR
  TP --> TEXENC
  TP --> Stb
  AP --> ATN
  FP --> ATN
  TAP --> ATN
  MP --> Silk
  MP --> ATN
```

## 3.3 启动时序

```mermaid
sequenceDiagram
    participant OS as OS
    participant P as Program
    participant Aval as Avalonia
    participant App as App.axaml.cs
    participant MVF as MainDockFactory
    participant MVM as MainViewModel
    participant WS as Workspace
    participant PL as PluginLoader

    OS->>P: 启动 UABEANext4.Desktop.exe
    P->>Aval: BuildAvaloniaApp().StartWithClassicDesktopLifetime
    Aval->>App: OnFrameworkInitializationCompleted
    App->>App: Configure DI (ServiceCollection)
    App->>MVF: new MainDockFactory()
    App->>MVM: Ioc.Default.GetRequiredService<MainViewModel>()
    MVM->>WS: new Workspace()
    WS->>WS: Manager.LoadClassPackage("classdata.tpk")
    WS->>PL: Plugins.LoadPluginsInDirectory("plugins")
    PL->>PL: foreach *.dll → PluginLoadContext.LoadFromAssemblyPath
    PL->>PL: 扫描 IUavPluginOption / IUavPluginPreviewer
    MVM->>MVF: BuildDock()
    MVF-->>App: RootDock
    Aval->>Aval: window.DataContext = MainViewModel
    Aval->>Aval: MainWindow 显示
```

## 3.4 关键设计模式

### 3.4.1 MVVM (CommunityToolkit.Mvvm)

```mermaid
classDiagram
  class ObservableObject {
    <<CommunityToolkit>>
    +event PropertyChanged
    +SetProperty(ref T field, T value, string? name)
  }
  class ViewModelBase {
    ObservableObject
  }
  class MainViewModel {
    +Workspace Workspace
    +MainDockFactory Factory
    +IReadOnlyList~WorkspaceItem~ SelectedItems
    +RelayCommand OpenFileCommand
    +[ObservableProperty] _isBusy
  }
  class AssetDocumentViewModel {
    +WorkspaceItem Item
    +AssetInst SelectedAsset
    +AssetTypeValueField? BaseField
  }
  class WorkspaceExplorerToolViewModel {
    +ObservableCollection~WorkspaceItem~ Items
    +RelayCommand OpenFileCommand
  }
  class InspectorToolViewModel {
    +IList~object~ SelectedObjects
  }
  class PreviewerToolViewModel {
    +UavPluginPreviewerType PreviewType
  }

  ObservableObject <|-- ViewModelBase
  ViewModelBase <|-- MainViewModel
  ViewModelBase <|-- AssetDocumentViewModel
  ViewModelBase <|-- WorkspaceExplorerToolViewModel
  ViewModelBase <|-- InspectorToolViewModel
  ViewModelBase <|-- PreviewerToolViewModel
```

### 3.4.2 Dock 布局

```mermaid
classDiagram
  class IRootDock
  class IDock
  class IDockWindow
  class IDocument
  class ITool
  class Factory {
    +CreateLayout() IRootDock
  }
  class MainDockFactory {
    +BuildDock() IRootDock
  }
  IRootDock "1" *-- "*" IDockWindow
  IDockWindow "1" *-- "*" IDock
  IDock "1" *-- "*" IDocument
  IDock "1" *-- "*" ITool
  Factory <|.. MainDockFactory
```

默认布局：
- **WorkspaceExplorer** (Tool, 左侧) — 显示 `RootItems` 树
- **Hierarchy** (Tool, 左下) — 显示选中 GameObject 的层级
- **Inspector** (Tool, 右侧) — 显示选中 asset 的字段
- **Previewer** (Tool, 右下) — 显示预览
- 中间区域可放 **Document** tabs（AssetDocumentView for selected asset）

### 3.4.3 Workspace 文件树

```mermaid
classDiagram
  class Workspace {
    +AssetsManager Manager
    +PluginLoader Plugins
    +AssetNamer Namer
    +ObservableCollection~WorkspaceItem~ RootItems
    +Dictionary~string,WorkspaceItem~ ItemLookup
    +HashSet~WorkspaceItem~ UnsavedItems
    +HashSet~WorkspaceItem~ ModifiedItems
    +Mutex ModifyMutex
    +event MonoTemplateLoadFailed
    +LoadAnyFile(stream, loadOrder, path)
    +LoadBundle(stream, loadOrder, name)
    +LoadAssets(stream, loadOrder, name)
    +LoadAssetsFromBundle(bunInst, index)
    +LoadResource(stream, loadOrder, name)
    +FixupAssetsFile(fileInst)
    +TryLoadClassDatabase(file)
    +GetTemplateField(asset)
    +GetBaseField(fileInst, pathId)
    +Dirty(item)
    +Close(item)
    +CloseAll()
    +RenameFile(item, newName)
    +Save(item)
    +SaveAs(item)
    +SaveAllAs()
  }
  class WorkspaceItem {
    +string Name
    +string OriginalName
    +int LoadIndex
    +object Object
    +WorkspaceItemType ObjectType
    +WorkspaceItem? Parent
    +ObservableCollection~WorkspaceItem~ Children
  }
  class WorkspaceItemType {
    <<enum>>
    AssetsFile
    BundleFile
    ResourceFile
  }
  class AssetInst {
    +string AssetName
    +AssetsFileInstance FileInstance
    +int Type
    +long PathId
  }
  class DuplicateWorkspaceFileException
  Workspace "1" *-- "*" WorkspaceItem : RootItems
  WorkspaceItem "1" *-- "*" WorkspaceItem : Children
  Workspace "1" *-- "*" AssetInst : 间接
  WorkspaceItem --> WorkspaceItemType
```

### 3.4.4 插件系统（双接口）

```mermaid
classDiagram
  class PluginLoader {
    -List~IUavPluginOption~ _pluginOptions
    -List~IUavPluginPreviewer~ _pluginPreviewers
    -HashSet~string~ _loadedPaths
    +LoadPlugin(path) bool
    +LoadPluginsInDirectory(dir) void
    +GetOptionsThatSupport(workspace, assets, mode) List~PluginOptionModePair~
    +GetPreviewersThatSupport(workspace, asset) List~PluginPreviewerTypePair~
  }
  class PluginLoadContext {
    -AssemblyDependencyResolver _resolver
    +LoadAssemblyByName(name)
    +LoadAssemblyByPath(path)
    +Load(assemblyName)
    +LoadUnmanagedDll(name)
  }
  class IUavPluginOption {
    <<interface>>
    +string Name
    +string Description
    +UavPluginMode Options
    +SupportsSelection(workspace, mode, selection) bool
    +Execute(workspace, funcs, mode, selection) Task~bool~
  }
  class IUavPluginPreviewer {
    <<interface>>
    +string Name
    +string Description
    +SupportsPreview(workspace, asset) UavPluginPreviewerType
  }
  class IUavPluginPreviewerFunctions {
    <<interface>>
    +SetPreviewText(document)
    +SetPreviewImage(image)
    +SetPreviewMesh(mesh)
  }
  class IUavPluginFunctions {
    <<interface>>
    +ShowOpenFileDialog(options) Task~string[]~
    +ShowSaveFileDialog(options) Task~string?~
    +ShowOpenFolderDialog(options) Task~string?~
    +ShowDialog~T~(dialogAware) Task~T?~
    +ShowMessageDialog(title, message)
  }
  class UavPluginMode {
    <<enum>>
    Import = 1
    Export = 2
    Info = 4
  }
  class UavPluginPreviewerType {
    <<enum>>
    None
    Image
    Text
    Mesh
  }
  PluginLoader --> PluginLoadContext : creates
  PluginLoader --> IUavPluginOption
  PluginLoader --> IUavPluginPreviewer
  IUavPluginOption ..> IUavPluginFunctions : receives
  IUavPluginPreviewer ..> IUavPluginPreviewerFunctions : receives
```

### 3.4.5 WeakReferenceMessenger

`UABEANext4/Logic/Messages.cs` 定义若干 `record` 类（如 `SelectedWorkspaceItemChangedMessage`, `RequestEditAssetMessage`, `RequestCloseFileMessage`, `RequestVisitAssetMessage`），ViewModel 之间通过 `WeakReferenceMessenger.Default.Send(msg)` 解耦通信。

### 3.4.6 WorkspaceItem Replacer 与 Save 流程

```mermaid
sequenceDiagram
    participant VM as MainViewModel
    participant Doc as AssetDocumentViewModel
    participant WS as Workspace
    participant Bun as BundleFileInstance
    participant File as AssetsFileInstance

    VM->>Doc: User edits asset field
    Doc->>WS: GetBaseField(asset)
    WS-->>Doc: AssetTypeValueField
    Doc->>Doc: User edits field
    Doc->>Doc: baseField.WriteToByteArray()
    Doc->>WS: Mark item dirty (unsaved)
    WS->>WS: UnsavedItems.Add(item)
    VM->>WS: Save(item)
    WS->>WS: WriteAssetsFile / WriteBundleFile / WriteResource
    alt AssetsFile
        WS->>File: file.Write(tempWriter)
        File->>File: 写 ~tmp.bundle/.assets
        WS->>WS: File.Move(tmp → original)
        WS->>File: 重新 Read 新文件
        WS->>WS: UnsavedItems.Remove(item)
    else BundleFile
        WS->>Bun: 同步 DirectoryInfos
        WS->>Bun: bun.Write(writer)
        WS->>Bun: 对每个 child asset 重新 load
    end
```

## 3.5 错误处理与崩溃恢复

- `Program.cs` 的 `UABEANext4.Desktop` 含 `UABEANExceptionHandler`（推测继承 UABEA 模式）
- `AppDomain.UnhandledException` → `uabeacrash.log`
- 没有弹窗（与 UABEA 不同，UABEANext 假设崩溃发生在初始化后期时 Avalonia 仍可用）

## 3.6 跨平台考量

- **Windows**: full support（验证主要平台）
- **Linux**: 通过 Avalonia + Linux native libs（textureencoder/cuttlefish/PVR）
- **macOS**: 推测支持（仓库有 macOS 路径）
- **Mobile (Android/iOS)**: 推测不支持（UABEANext 是桌面工具）

## 3.7 与 UABEA 的设计哲学差异

| 维度 | UABEA | UABEANext |
|---|---|---|
| 代码风格 | 命令式事件回调 | 声明式 MVVM |
| 状态管理 | 散落在 Form code-behind | 集中在 ViewModel |
| 窗体 | 17 个独立 .axaml | 1 主窗 + 12 dialog + 7 tool 嵌入 Dock |
| 依赖注入 | 无 | Microsoft.Extensions.DependencyInjection |
| ObservableCollection | 散用 | 全局（RootItems / Children / AssetList） |
| 消息总线 | 无 | WeakReferenceMessenger |
| 线程模型 | UI 线程 + 后台 worker | UI 线程 + SynchronizationContext + 后台 worker |
| 测试性 | 低 | 高（VM 可独立测试） |