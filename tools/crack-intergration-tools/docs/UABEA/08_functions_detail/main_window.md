# 08 · MainWindow 与 InfoWindow 详细说明

涉及文件：
- `UABEAvalonia/Forms/MainWindow.axaml.cs` (1026 LoC)
- `UABEAvalonia/Forms/InfoWindow.axaml.cs` (1307 LoC)
- `UABEAvalonia/Forms/AssetTypeIconConverter.cs`
- `UABEAvalonia/Forms/AssetsFileInfo/*` (多 Tab)

---

## 8.1 MainWindow.axaml.cs

### `class MainWindow : Window`

#### 字段 / 属性
- `BundleWorkspace Workspace { get; }` —— 全局 workspace (`MainWindow.axaml.cs:19`)
- `AssetsManager am { get => Workspace.am; }` —— 包装访问
- `BundleFileInstance BundleInst { get => Workspace.BundleInst; }`
- `private bool ignoreCloseEvent`
- `private List<InfoWindow> openInfoWindows`

#### `MainWindow()`
- **签名**：`public MainWindow()`
- **位置**：`MainWindow.axaml.cs:31`
- **可见性**：public
- **副作用**：
  - `Workspace = new BundleWorkspace()`
  - `Workspace.BundleInst = null`
  - `Workspace.am.LoadClassPackage("classdata.tpk")` 若存在
  - 构造 menu items / buttons
  - `DataContext = this`
  - `Initialized += MainWindow_Initialized`

#### `MainWindow_Initialized(object?, EventArgs)`
- **签名**：`private async void MainWindow_Initialized(object? sender, EventArgs e)`
- **位置**：`MainWindow.axaml.cs:71`
- **可见性**：private
- **副作用**：
  - 注册 `DragDrop.DropEvent`
  - 加载 plugins
  - 订阅 `ConfigurationManager.Settings.UseDarkTheme` PropertyChanged（若存在）
- **调用了**：`pluginManager.LoadPluginsInDirectory`

#### 菜单事件

| 事件 | 位置 | 行为 |
|---|---|---|
| `MenuOpen_Click` | `MainWindow.axaml.cs:191` | 打开文件对话框 + 调 `LoadFile` |
| `MenuLoadPackageFile_Click` | `MainWindow.axaml.cs:210` | 加载 .emip 包 |
| `MenuAbout_Click` | `MainWindow.axaml.cs:237` | 弹出 About 窗 |
| `MenuSave_Click` | `MainWindow.axaml.cs:243` | 调 `AskForLocationAndSave(false)` |
| `MenuSaveAs_Click` | `MainWindow.axaml.cs:248` | 调 `AskForLocationAndSave(true)` |
| `MenuCompress_Click` | `MainWindow.axaml.cs:253` | 调 `AskForLocationAndCompress` |
| `MenuClose_Click` | `MainWindow.axaml.cs:258` | 调 `CloseAllFiles` |
| `MenuExit_Click` | `MainWindow.axaml.cs:513` | 关闭应用 |
| `MenuToggleDarkTheme_Click` | `MainWindow.axaml.cs:518` | 翻转 `ConfigurationManager.Settings.UseDarkTheme` |
| `MenuToggleCpp2Il_Click` | `MainWindow.axaml.cs:524` | 翻转 `UseCpp2Il` |
| `MainWindow_Closing` | `MainWindow.axaml.cs:533` | 询问是否保存 |
| `InfoWindow_Closing` | `MainWindow.axaml.cs:550` | 通知 |

#### 按钮事件

| 事件 | 位置 | 行为 |
|---|---|---|
| `BtnExport_Click` | `MainWindow.axaml.cs:264` | 调 bundle 文件列表导出 |
| `BtnImport_Click` | `MainWindow.axaml.cs:290` | 弹 ImportSerializedDialog → 导入 |
| `BtnRemove_Click` | `MainWindow.axaml.cs:324` | 标记 BundleWorkspaceItem 为 IsRemoved |
| `BtnInfo_Click` | `MainWindow.axaml.cs:346` | 选中的 .assets 打开 InfoWindow |
| `BtnExportAll_Click` | `MainWindow.axaml.cs:403` | 全部导出 |
| `BtnImportAll_Click` | `MainWindow.axaml.cs:444` | 全部导入 |
| `BtnRename_Click` | `MainWindow.axaml.cs:482` | 弹 RenameWindow → 调 RenameFile |

#### 关键私有方法

##### `LoadOrAskTypeData(AssetsFileInstance)`
- **签名**：`private async Task<bool> LoadOrAskTypeData(AssetsFileInstance fileInst)`
- **位置**：`MainWindow.axaml.cs:587`
- **可见性**：private
- **算法**：
  1. 若 `am.ClassDatabase != null` → return true
  2. `fileInst.file.Metadata.UnityVersion` → `LoadClassDatabaseFromPackage`
  3. 失败时弹打开文件对话框让用户选 classdata.tpk
  4. `LoadClassPackage`

##### `AskForLocationAndSave(bool saveAs)`
- **签名**：`private async Task AskForLocationAndSave(bool saveAs)`
- **位置**：`MainWindow.axaml.cs:619`
- **可见性**：private
- **算法**：保存对话框 → 调 `SaveBundle / SaveBundleOver`

##### `AskForSave()`
- **位置**：`MainWindow.axaml.cs:666`

##### `AskForLocationAndCompress()`
- **位置**：`MainWindow.axaml.cs:680`

##### `AskLoadSplitFile(string fileToSplit)`
- **签名**：`private async Task<string?> AskLoadSplitFile(string fileToSplit)`
- **位置**：`MainWindow.axaml.cs:767`
- **用途**：处理 Unity 分包文件（`*.split0`）

##### `AskLoadCompressedBundle(BundleFileInstance bundleInst)`
- **签名**：`private async void AskLoadCompressedBundle(BundleFileInstance bundleInst)`
- **位置**：`MainWindow.axaml.cs:814`
- **可见性**：private
- **副作用**：弹 MessageBox 询问解压方式
- **调用了**：`DecompressToFile / DecompressToMemory`

##### `DecompressToFile(BundleFileInstance, string savePath)`
- **位置**：`MainWindow.axaml.cs:873`

##### `DecompressToMemory(BundleFileInstance)`
- **位置**：`MainWindow.axaml.cs:889`

##### `LoadBundle(BundleFileInstance)`
- **位置**：`MainWindow.axaml.cs:905`
- **副作用**：把 entry 列表显示到 UI

##### `SaveBundle(BundleFileInstance, string path)`
- **位置**：`MainWindow.axaml.cs:917`
- **副作用**：从 BundleWorkspace 收集 replacers + assets workspace.NewAssets 调 bun.Write

##### `SaveBundleOver(BundleFileInstance)`
- **位置**：`MainWindow.axaml.cs:928`
- **算法**：临时文件 → File.Move 覆盖原文件 → 备份

##### `CompressBundle(object?)`
- **位置**：`MainWindow.axaml.cs:960`
- **异步**

##### `CloseAllFiles()`
- **位置**：`MainWindow.axaml.cs:976`

##### `SetBundleControlsEnabled(bool, bool)`
- **位置**：`MainWindow.axaml.cs:998`

##### `GetBundleDataDecompressedSize(AssetBundleFile)`
- **位置**：`MainWindow.axaml.cs:1016`

---

## 8.2 InfoWindow.axaml.cs

### `class InfoWindow : Window`

#### 字段
- `AssetWorkspace Workspace`
- `AssetsManager am { get => Workspace.am; }`
- `string searchText`, `int searchStart`, `bool searchDown`, `bool searchCaseSensitive`, `bool searching`
- `HashSet<AssetClassID> filteredOutTypeIds`
- `List<Tuple<AssetsFileInstance, byte[]>> ChangedAssetsDatas`
- `ObservableCollection<AssetInfoDataGridItem> dataGridItems`
- `PluginManager pluginManager`
- `DataGridCollectionView dgcv`

#### ctor
- 无参 `InfoWindow()` (`InfoWindow.axaml.cs:47`)
- `InfoWindow(AssetsManager, List<AssetsFileInstance>, bool fromBundle)` (`InfoWindow.axaml.cs:92`)

#### 菜单事件

| 事件 | 位置 |
|---|---|
| `MenuAdd_Click` | `InfoWindow.axaml.cs:119` |
| `MenuSave_Click` | `InfoWindow.axaml.cs:125` |
| `MenuSaveAs_Click` | `InfoWindow.axaml.cs:132` |
| `MenuCreatePackageFile_Click` | `InfoWindow.axaml.cs:139` (.emip 制作) |
| `MenuClose_Click` | `InfoWindow.axaml.cs:145` |
| `MenuSearchByName_Click` | `InfoWindow.axaml.cs:150` |
| `MenuContinueSearch_Click` | `InfoWindow.axaml.cs:167` |
| `MenuGoToAsset_Click` | `InfoWindow.axaml.cs:172` |
| `MenuFilter_Click` | `InfoWindow.axaml.cs:185` |
| `MenuHierarchy_Click` | `InfoWindow.axaml.cs:196` |
| `MenuInfo_Click` | `InfoWindow.axaml.cs:202` |
| `MenuTypeTree_Click` | `InfoWindow.axaml.cs:207` |
| `MenuDependencies_Click` | `InfoWindow.axaml.cs:212` |
| `MenuScripts_Click` | `InfoWindow.axaml.cs:217` |

#### 按钮事件

| 事件 | 位置 |
|---|---|
| `BtnViewData_Click` | `InfoWindow.axaml.cs:222` |
| `BtnSceneView_Click` | `InfoWindow.axaml.cs:239` |
| `BtnExportRaw_Click` | `InfoWindow.axaml.cs:308` |
| `BtnExportDump_Click` | `InfoWindow.axaml.cs:321` |
| `BtnImportRaw_Click` | `InfoWindow.axaml.cs:334` |
| `BtnImportDump_Click` | `InfoWindow.axaml.cs:347` |
| `BtnEditData_Click` | `InfoWindow.axaml.cs:360` |
| `BtnRemove_Click` | `InfoWindow.axaml.cs:384` |
| `BtnPlugin_Click` | `InfoWindow.axaml.cs:402` |
| `DataGrid_SelectionChanged` | `InfoWindow.axaml.cs:412` |
| `InfoWindow_Closing` | `InfoWindow.axaml.cs:431` |

#### 关键公共方法

##### `ShowEditAssetWindow(AssetContainer cont)`
- **签名**：`public async Task<bool> ShowEditAssetWindow(AssetContainer cont)`
- **位置**：`InfoWindow.axaml.cs:980`
- **可见性**：public
- **被调用**：`AssetDataTreeView.MenuEditAsset_Click` (`AssetDataTreeView.cs:103`)

##### `SelectAsset(AssetsFileInstance targetFile, long targetPathId)`
- **签名**：`public bool SelectAsset(AssetsFileInstance targetFile, long targetPathId)`
- **位置**：`InfoWindow.axaml.cs:1060`
- **被调用**：`AssetDataTreeView.MenuVisitAsset_Click` (`AssetDataTreeView.cs:136`)

#### 关键私有方法

##### `SetupContainers()`
- **位置**：`InfoWindow.axaml.cs:1080`
- **副作用**：把 `UnityContainer.AssetMap` 复制到本地 `Dict<pathId, containerPath>` 供 UI 显示

##### `MakeDataGridItems()`
- **位置**：`InfoWindow.axaml.cs:1113`
- **副作用**：构造 `ObservableCollection<AssetInfoDataGridItem>`

##### `AddDataGridItem(AssetContainer, bool)`
- **位置**：`InfoWindow.axaml.cs:1126`

##### `LoadAllAssetsWithDeps(List<AssetsFileInstance>)`
- **位置**：`InfoWindow.axaml.cs:1172`
- **调用了**：`AssetWorkspace.LoadAssetsFile`

##### `BatchExportRaw / SingleExportRaw / BatchExportDump / SingleExportDump / BatchImportRaw / SingleImportRaw / BatchImportDump / SingleImportDump`
- 8 个批量/单个 + raw/text 组合
- 位置：`InfoWindow.axaml.cs:649-998`
- 调 `AssetImportExport.DumpRawAsset / DumpTextAsset / ImportRawAsset / ImportTextAsset` + 文件对话框

##### `SaveFile(bool saveAs)`
- **位置**：`InfoWindow.axaml.cs:472`
- **算法**：
  1. 收集所有 `AssetsFileInstance` 的 replacers
  2. `assets.Write(writer, 0, replacers, addedTypes)` 写到临时 → File.Move 覆盖
- **副作用**：备份原文件为 .bakNNNN

##### `Workspace_ItemUpdated(AssetsFileInstance, AssetID)`
- **位置**：`InfoWindow.axaml.cs:1229`
- **副作用**：刷新 DataGrid

##### `Workspace_MonoTemplateLoadFailed(string)`
- **位置**：`InfoWindow.axaml.cs:1267`
- **副作用**：弹 MessageBox 让用户选 libil2cpp.so + global-metadata.dat

### `class AssetInfoDataGridItem : INotifyPropertyChanged`
- **位置**：`InfoWindow.axaml.cs:1307`
- 字段：`TypeClass`, `Name`, `Container`, `Type`, `TypeID`, `FileID`, `PathID`, `Size`, `Modified`, `AssetContainer assetContainer`
- `Update(string propertyName)` 触发 PropertyChanged

---

## 8.3 AssetTypeIconConverter.cs

### `class AssetTypeIconConverter : IValueConverter`

#### `Convert(object?, Type, object?, CultureInfo)`
- **签名**：`public object? Convert(object? value, Type targetType, object? parameter, CultureInfo culture)`
- **位置**：`UABEAvalonia/Forms/AssetTypeIconConverter.cs:19`
- **可见性**：public
- **算法**：根据 `AssetClassID` 返回对应 Bitmap

#### `ConvertBack(...)`
- **位置**：`UABEAvalonia/Forms/AssetTypeIconConverter.cs:108`
- 抛 `NotImplementedException`

---

## 8.4 AssetsFileInfo/ 子视图

| 文件 | 作用 |
|---|---|
| `AssetsFileInfoWindow.axaml` | 主 XAML（4 Tab） |
| `AssetsFileInfoWindow.axaml.cs` | 主 code-behind |
| `AssetsFileInfoWindow.Header.axaml.cs` | Header Tab |
| `AssetsFileInfoWindow.Deps.axaml.cs` | Dependencies Tab |
| `AssetsFileInfoWindow.Script.axaml.cs` | Scripts Tab |
| `AssetsFileInfoWindow.TypeTree.axaml.cs` | TypeTree Tab |

每个 Tab 都是 `UserControl`，含 `Init(AssetsFileInstance)` 方法填充 UI。