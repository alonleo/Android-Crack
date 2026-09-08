# 04 · UABEANext 数据结构与数据流

## 4.1 核心数据结构

### 4.1.1 Workspace 文件树

```mermaid
classDiagram
  class Workspace {
    +AssetsManager Manager
    +PluginLoader Plugins
    +AssetNamer Namer
    +ObservableCollection~WorkspaceItem~ RootItems
    +Dictionary~string,WorkspaceItem~ ItemLookup
    +SynchronizationContext? FileSyncContext
    +HashSet~WorkspaceItem~ UnsavedItems
    +HashSet~WorkspaceItem~ ModifiedItems
    +Mutex ModifyMutex
    +event MonoTemplateLoadFailed
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
  class ContainerTool {
    +AssetsFileInstance? File
    +ContainerToolManager Manager
    +Dictionary~long,string~ PathIdToContainerPath
    +Initialize(file)
    +TryGetContainer(pathId, out path)
  }
  class ContainerToolManager {
    +ConcurrentDictionary~AssetsFileInstance,ContainerTool~ Tools
    +GetOrCreateTool(file)
    +FreeTool(file)
  }

  Workspace "1" *-- "*" WorkspaceItem : RootItems
  Workspace "1" *-- "1" ContainerToolManager
  ContainerToolManager "1" *-- "*" ContainerTool
  WorkspaceItem "1" *-- "*" WorkspaceItem : Children
  WorkspaceItem --> WorkspaceItemType
  Workspace "1" *-- "*" AssetInst : via FileInst
  AssetsFileInstance "1" *-- "*" AssetInst
```

### 4.1.2 ViewModel 层

```mermaid
classDiagram
  class MainViewModel {
    +Workspace Workspace
    +MainDockFactory Factory
    +IDialogService DialogService
    +IStorageService StorageService
    +IReadOnlyList~WorkspaceItem~ SelectedItems
    +RelayCommand OpenFileCommand
    +RelayCommand CloseFileCommand
    +RelayCommand SaveCommand
    +RelayCommand SaveAsCommand
    +RelayCommand ExportModPackageCommand
  }
  class WorkspaceExplorerToolViewModel {
    +ObservableCollection~WorkspaceItem~ Items
    +RelayCommand OpenCommand
    +RelayCommand CloseCommand
  }
  class HierarchyToolViewModel {
    +WorkspaceItem CurrentFile
    +AssetInst SelectedGameObject
    +ObservableCollection~HierarchyItem~ Hierarchy
  }
  class InspectorToolViewModel {
    +IList~object~ SelectedObjects
    +AssetTypeValueField? BaseField
  }
  class PreviewerToolViewModel {
    +AssetInst SelectedAsset
    +UavPluginPreviewerType PreviewType
  }
  class AssetDocumentViewModel {
    +WorkspaceItem Item
    +AssetInst SelectedAsset
    +AssetTypeValueField? BaseField
    +IList~ImportableItem~ AssetList
  }
  class AddAssetViewModel {
    +int TypeId
    +long PathId
    +byte[] Data
  }
  class EditDataViewModel {
    +byte[] Data
    +EditMode Mode
  }
  class SettingsViewModel {
    +string Theme
    +int ListingNameLength
    +bool UseManagedOverIl2cpp
  }

  MainViewModel "1" *-- "1" WorkspaceExplorerToolViewModel
  MainViewModel "1" *-- "1" HierarchyToolViewModel
  MainViewModel "1" *-- "1" InspectorToolViewModel
  MainViewModel "1" *-- "1" PreviewerToolViewModel
  MainViewModel "1" *-- "*" AssetDocumentViewModel
```

### 4.1.3 插件宿主

```mermaid
classDiagram
  class PluginLoader {
    -List~IUavPluginOption~ _pluginOptions
    -List~IUavPluginPreviewer~ _pluginPreviewers
    -HashSet~string~ _loadedPaths
    +bool LoadPlugin(string path)
    +void LoadPluginsInDirectory(string directory)
    +List~PluginOptionModePair~ GetOptionsThatSupport(workspace, assets, mode)
    +List~PluginPreviewerTypePair~ GetPreviewersThatSupport(workspace, asset)
  }
  class PluginLoadContext {
    -AssemblyDependencyResolver _resolver
    +Assembly LoadAssemblyByName(string name)
    +Assembly LoadAssemblyByPath(string path)
    +Assembly? Load(AssemblyName)
    +IntPtr LoadUnmanagedDll(string)
  }
  class IUavPluginOption {
    <<interface>>
    +string Name
    +string Description
    +UavPluginMode Options
    +bool SupportsSelection(workspace, mode, selection)
    +Task~bool~ Execute(workspace, funcs, mode, selection)
  }
  class IUavPluginPreviewer {
    <<interface>>
    +string Name
    +string Description
    +UavPluginPreviewerType SupportsPreview(workspace, asset)
  }
  class UavPluginFunctions {
    -IDialogService _dialogService
    -IStorageProvider _storageProvider
    +ShowOpenFileDialog
    +ShowSaveFileDialog
    +ShowOpenFolderDialog
    +ShowDialog~T~
    +ShowMessageDialog
  }

  PluginLoader "1" *-- "*" IUavPluginOption
  PluginLoader "1" *-- "*" IUavPluginPreviewer
  PluginLoader ..> PluginLoadContext : uses
  IUavPluginOption ..> UavPluginFunctions : receives
  UavPluginFunctions ..> IDialogService
```

### 4.1.4 Mesh 数据结构

```mermaid
classDiagram
  class MeshObj {
    +string Name
    +Topology Topology
    +List~Channel~ Channels
    +List~int~ Indices
    +AABB Bounds
    +byte[] RawVertexData
  }
  class Channel {
    +string Name
    +ChannelFormat Format
    +int Dimension
    +int Offset
    +int Stride
    +byte[] Data
  }
  class MeshEnums {
    +enum Topology
    +enum ChannelFormat
  }
  MeshObj "1" *-- "*" Channel
  Channel --> MeshEnums
```

### 4.1.5 搜索

```mermaid
classDiagram
  class SearchLogic {
    +List~SearchResultItem~ Search(workspace, query, options, cts)
    +Task ParallelSearch(fileInsts, query, ...)
  }
  class SearchResultItem {
    +AssetsFileInstance File
    +long PathId
    +AssetClassID Type
    +string Name
    +string Container
    +int MatchScore
  }
  SearchLogic ..> SearchResultItem : produces
```

## 4.2 数据流

### 4.2.1 打开 .bundle 文件

```mermaid
flowchart LR
  U[MainViewModel.OpenFile] --> SP[StorageProvider.OpenFilePickerAsync]
  SP --> FS[FileStream]
  FS --> LA[Workspace.LoadAnyFile stream]
  LA --> FTD[FileTypeDetector.DetectFileType]
  FTD -->|BundleFile| LB[LoadBundle]
  FTD -->|AssetsFile| LA2[LoadAssets]
  FTD -->|.resS| LR[LoadResource]
  LB --> LOCK[lock _workingKeys<br/>检查重复]
  LOCK -->|throw| DWF[DuplicateWorkspaceFileException]
  LOCK -->|ok| AM[Manager.LoadBundleFile]
  AM --> CDB[TryLoadClassDatabase]
  CDB --> TPK[Manager.LoadClassDatabaseFromPackage]
  CDB --> NEW[new WorkspaceItem]
  NEW --> AR[AddRootItemThreadSafe<br/>FileSyncContext.Post]
  AR --> VM[MainViewModel receives ItemUpdated]
```

### 4.2.2 编辑 asset 字段

```mermaid
sequenceDiagram
    participant UI as Inspector Tool
    participant Doc as AssetDocumentViewModel
    participant WS as Workspace
    participant ATN as AssetsManager
    participant File as AssetsFileInstance

    UI->>Doc: User edits field
    Doc->>WS: GetBaseField(SelectedAsset)
    WS->>ATN: GetBaseField(fileInst, info, readFlags)
    ATN-->>WS: AssetTypeValueField
    WS-->>Doc: BaseField
    Doc->>Doc: User modifies field
    Doc->>Doc: BaseField.WriteToByteArray()
    Doc->>WS: Dirty(workspaceItem)
    WS->>WS: UnsavedItems.Add(item)
    Doc->>Doc: CreateAssetsReplacer
    Note over Doc: replacer stored in <br/>file info, applied on Save
```

### 4.2.3 保存 .bundle

```mermaid
flowchart TD
  ACT[User clicks Save] --> SAV[Workspace.Save item]
  SAV --> TS{is AssetsFile?}
  TS -->|是| WAF[WriteAssetsFile]
  TS -->|否 - BundleFile| WBF[WriteBundleFile]
  TS -->|否 - ResourceFile| WR[WriteResource]
  WAF --> WT[write to temp ~file]
  WBF --> SYNC[sync DirectoryInfos]
  SYNC --> WT
  WR --> WT
  WT --> MV[File.Move temp → original]
  MV --> REL[重新 Read 新文件]
  REL --> UNS[UnsavedItems.Remove item]
  REL --> FX[FixupAssetsFile]
  FX --> DONE[完成]
```

### 4.2.4 插件加载流程

```mermaid
sequenceDiagram
    participant WS as Workspace
    participant PL as PluginLoader
    participant DIR as plugins/ 目录
    participant PLC as PluginLoadContext
    participant ASM as Assembly
    participant T as Type

    WS->>PL: LoadPluginsInDirectory("plugins")
    PL->>DIR: EnumerateFiles *.dll
    loop each DLL
        PL->>PLC: new PluginLoadContext(path)
        PL->>PLC: LoadFromAssemblyPath(path)
        PLC->>ASM: 独立加载
        ASM-->>PLC: Assembly
        loop GetTypes
            PLC->>T: type
            alt typeof IUavPluginOption
                PL->>T: Activator.CreateInstance
                PL->>PL: _pluginOptions.Add
            else typeof IUavPluginPreviewer
                PL->>T: Activator.CreateInstance
                PL->>PL: _pluginPreviewers.Add
            end
        end
    end
```

### 4.2.5 类型树文本 dump

```mermaid
sequenceDiagram
    participant UI as Inspector
    participant Doc as AssetDocumentViewModel
    participant AE as AssetExport
    participant WS as Workspace
    participant FS as File

    UI->>Doc: User clicks "Export .txt"
    Doc->>WS: GetBaseField(SelectedAsset)
    Doc->>AE: new AssetExport(fileStream)
    Doc->>AE: DumpTextAsset(baseField)
    AE->>AE: RecurseTextDump
    AE->>FS: Write text
```

### 4.2.6 Mesh 预览数据流

```mermaid
flowchart LR
  A[Selected GameObject] --> B[Workspace.GetBaseField<br/>读取 m_Components]
  B --> C[遍历 components<br/>找 MeshFilter]
  C --> D[workspace.GetBaseField<br/>读取 Mesh asset]
  D --> E[解析 m_Vertices / m_Indices / m_Channels]
  E --> F[new MeshObj]
  F --> G[PluginPreviewer 进程<br/>IPC SetPreviewMesh]
  G --> H[Silk.NET.OpenGL 渲染]
```

### 4.2.7 搜索流程

```mermaid
flowchart TD
  SR[User types query in SearchDialog] --> SQ[SearchLogic.Search]
  SQ --> PAR[Parallel.ForEach over RootItems]
  PAR --> FI[for each AssetsFileInstance]
  FI --> FI1[Build NameToPathId map]
  FI1 --> FI2[ConcurrentBag<SearchResultItem>]
  FI2 --> DONE[返回 List<SearchResultItem>]
  DONE --> UI[Inspector Tool 填充结果]
```