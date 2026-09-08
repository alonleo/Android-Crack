# 08 · Workspace 层详细说明

涉及文件：
- `UABEANext4/AssetWorkspace/Workspace.cs` (630 LoC)
- `UABEANext4/AssetWorkspace/Workspace.Saving.cs` (416 LoC)
- `UABEANext4/AssetWorkspace/WorkspaceItem.cs` (102 LoC)
- `UABEANext4/AssetWorkspace/WorkspaceItemType.cs`
- `UABEANext4/AssetWorkspace/AssetInst.cs`
- `UABEANext4/AssetWorkspace/ContainerTool.cs` (133 LoC)
- `UABEANext4/AssetWorkspace/ContainerToolManager.cs` (97 LoC)
- `UABEANext4/AssetWorkspace/DuplicateWorkspaceFileException.cs`

---

## Workspace.cs

### 字段
```csharp
public AssetsManager Manager { get; } = new AssetsManager();
public PluginLoader Plugins { get; } = new PluginLoader();
public AssetNamer Namer { get; }
public Mutex ModifyMutex { get; } = new Mutex();

[ObservableProperty] public float _progressValue = 0f;
[ObservableProperty] public string _progressText = "";

public ObservableCollection<WorkspaceItem> RootItems { get; } = [];
public Dictionary<string, WorkspaceItem> ItemLookup { get; } = [];
private SynchronizationContext? FileSyncContext { get; } = SynchronizationContext.Current;

public HashSet<WorkspaceItem> UnsavedItems { get; } = [];
public HashSet<WorkspaceItem> ModifiedItems { get; } = [];

public int NextLoadIndex => RootItems.Count != 0 ? RootItems.Max(i => i.LoadIndex) + 1 : 0;

public delegate void MonoTemplateFailureEvent(string path);
public event MonoTemplateFailureEvent? MonoTemplateLoadFailed;

private HashSet<string> _workingKeys = [];
private bool _setMonoTempGeneratorsYet;
```

### `Workspace()`
- **签名**：`public Workspace()`
- **位置**：`Workspace.cs:51`
- **可见性**：public
- **算法**：
  1. `<baseDir>/classdata.tpk` 存在 → `Manager.LoadClassPackage`
  2. `<baseDir>/plugins` 目录 → `Plugins.LoadPluginsInDirectory`
  3. `Manager.UseRefTypeManagerCache = true; UseTemplateFieldCache = true; UseQuickLookup = true`
  4. `Namer = new AssetNamer(this)`

### `WorkspaceItem? LoadAnyFile(Stream stream, int loadOrder, string path)`
- **签名**：`public WorkspaceItem? LoadAnyFile(Stream stream, int loadOrder = -1, string path = "")`
- **位置**：`Workspace.cs:67`
- **可见性**：public
- **算法**：
  - `FileTypeDetector.DetectFileType(reader, 0)`
  - BundleFile → `LoadBundle`
  - AssetsFile → `LoadAssets`
  - `.resS` / `.resource` → `LoadResource`
- **被调用**：`MainViewModel.OpenFileAsync` 等

### `WorkspaceItem LoadBundle(Stream stream, int loadOrder, string name)`
- **签名**：`public WorkspaceItem LoadBundle(Stream stream, int loadOrder = -1, string name = "")`
- **位置**：`Workspace.cs:93`
- **可见性**：public
- **算法**：
  1. `Manager.LoadBundleFile(stream, name)`
  2. `lock (_workingKeys)`：
     - 对每个 `dirInf`，检查是否已在 `Manager.FileLookup` 或 `_workingKeys`
     - 若重复 → 抛 `DuplicateWorkspaceFileException`
     - 否则加入 `ourWorkingKeys`
  3. `TryLoadClassDatabase(bunInst.file)`
  4. `new WorkspaceItem(this, bunInst, loadOrder)`
  5. `AddRootItemThreadSafe(item, bunInst.name)`
  6. finally: `_workingKeys.Remove` 全部
- **副作用**：可能触发 `MonoTemplateLoadFailed`（后续访问 MonoBehaviour 时）
- **抛出**：`DuplicateWorkspaceFileException`

### `WorkspaceItem LoadAssets(Stream stream, int loadOrder, string name)`
- **签名**：`public WorkspaceItem LoadAssets(Stream stream, int loadOrder = -1, string name = "")`
- **位置**：`Workspace.cs:156`
- **可见性**：public
- **算法**：
  1. 取 `fileKey = AssetsManager.GetFileLookupKey(fileVirtualPath)`
  2. `lock (_workingKeys)` 重复检查
  3. `Manager.LoadAssetsFile`
  4. `TryLoadClassDatabase`
  5. `FixupAssetsFile`
  6. `new WorkspaceItem`
  7. `AddRootItemThreadSafe`
  8. finally: 清理
- **抛出**：`DuplicateWorkspaceFileException`

### `WorkspaceItem LoadAssetsFromBundle(BundleFileInstance bunInst, int index)`
- **签名**：`public WorkspaceItem LoadAssetsFromBundle(BundleFileInstance bunInst, int index)`
- **位置**：`Workspace.cs:204`
- **可见性**：public
- **副作用**：构造子 WorkspaceItem（Parent 为 null）
- **被调用**：SaveBundle 重载加载 children

### `void FixupAssetsFile(AssetsFileInstance fileInst)`
- **签名**：`private void FixupAssetsFile(AssetsFileInstance fileInst)`
- **位置**：`Workspace.cs:217`
- **可见性**：private
- **算法**：
  1. 若 `AssetInfos is not RangeObservableCollection<AssetFileInfo>`：
     - 构造 `RangeObservableCollection<AssetFileInfo>`
     - 对每个 AssetInfo 包成 `AssetInst`，调 `Namer.GetAssetName` 设置 `AssetName`
     - 替换 `fileInst.file.Metadata.AssetInfos`
  2. `GenerateQuickLookup`

### `void TryLoadClassDatabase(AssetBundleFile file)`
- **签名**：`public void TryLoadClassDatabase(AssetBundleFile file)`
- **位置**：`Workspace.cs:237`
- **可见性**：public
- **算法**：若 `Manager.ClassDatabase == null` 且 `file.Header.EngineVersion != "0.0.0"` → `LoadClassDatabaseFromPackage`

### `void TryLoadClassDatabase(AssetsFile file)`
- **签名**：`public void TryLoadClassDatabase(AssetsFile file)`
- **位置**：`Workspace.cs:249`
- **可见性**：public

### `WorkspaceItem LoadResource(Stream stream, int loadOrder, string name)`
- **签名**：`public WorkspaceItem LoadResource(Stream stream, int loadOrder = -1, string name = "")`
- **位置**：`Workspace.cs:262`
- **可见性**：public
- **算法**：包成 `WorkspaceItem { type = ResourceFile }`

### `void AddRootItemThreadSafe(WorkspaceItem item, string itemName)`
- **签名**：`internal void AddRootItemThreadSafe(WorkspaceItem item, string itemName)`
- **位置**：`Workspace.cs:275`
- **可见性**：internal
- **算法**：
  - 若 `FileSyncContext != null`：`Post` 到 UI 线程
  - 按 `LoadIndex` 二分插入 `RootItems`
  - `ItemLookup[itemName] = item`
- **被调用**：`LoadBundle / LoadAssets / LoadResource`

### `void AddChildItemThreadSafe(WorkspaceItem item, WorkspaceItem parent, string itemName)`
- **签名**：`internal void AddChildItemThreadSafe(WorkspaceItem item, WorkspaceItem parent, string itemName)`
- **位置**：`Workspace.cs:299`
- **可见性**：internal
- **算法**：`parent.Children.Add(item); item.Parent = parent`

### `void SetProgressThreadSafe(float, string)`
- **签名**：`public void SetProgressThreadSafe(float value, string text)`
- **位置**：`Workspace.cs:310`
- **可见性**：public
- **算法**：四舍五入到 0.05 精度，更新 `ProgressValue` / `ProgressText` 到 UI 线程

### `AssetTypeTemplateField GetTemplateField(AssetInst asset, bool skipMonoBehaviourFields)`
- **签名**：`public AssetTypeTemplateField GetTemplateField(AssetInst asset, bool skipMonoBehaviourFields = false)`
- **位置**：`Workspace.cs:324`
- **可见性**：public

### `AssetTypeTemplateField GetTemplateField(AssetsFileInstance, AssetFileInfo, bool)`
- **签名**：`public AssetTypeTemplateField GetTemplateField(AssetsFileInstance fileInst, AssetFileInfo info, bool skipMonoBehaviourFields = false)`
- **位置**：`Workspace.cs:335`
- **可见性**：public

### `void CheckAndSetMonoTempGenerators(AssetsFileInstance, AssetFileInfo?)`
- **签名**：`public void CheckAndSetMonoTempGenerators(AssetsFileInstance fileInst, AssetFileInfo? info)`
- **位置**：`Workspace.cs:346`
- **可见性**：public
- **算法**：首次访问 MonoBehaviour 时调 `SetMonoTempGenerators(fileDir)`

### `bool SetMonoTempGenerators(string fileDir)`
- **签名**：`private bool SetMonoTempGenerators(string fileDir)`
- **位置**：`Workspace.cs:360`
- **可见性**：private
- **算法**：
  - Managed 优先（若 `ConfigurationManager.Settings.UseManagedOverIl2cpp`）
  - `FindCpp2IlFiles.Find(fileDir)`
  - `MonoCecilTempGenerator(managedDir)` 或 `Cpp2IlTempGenerator`

### `AssetFileInfo? GetAssetFileInfo(AssetsFileInstance, AssetTypeValueField pptrField)`
- **位置**：`Workspace.cs:391`

### `AssetFileInfo? GetAssetFileInfo(AssetsFileInstance, int fileId, long pathId)`
- **位置**：`Workspace.cs:396`

### `AssetInst? GetAssetInst(AssetsFileInstance, AssetTypeValueField pptrField)`
- **位置**：`Workspace.cs:410`

### `AssetInst? GetAssetInst(AssetsFileInstance, int fileId, long pathId)`
- **位置**：`Workspace.cs:415`

### `AssetTypeValueField? GetBaseField` 4 重载
- `(AssetInst)` (`Workspace.cs:438`)
- `(AssetsFileInstance, long)` (`Workspace.cs:443`)
- `(AssetsFileInstance, AssetTypeValueField pptrField)` (`Workspace.cs:448`)
- `(AssetsFileInstance, int fileId, long pathId)` (`Workspace.cs:453`)

### `void Dirty(WorkspaceItem)`
- **位置**：`Workspace.cs:495`
- **副作用**：`UnsavedItems.Add(item); ModifiedItems.Add(item); 递归 Dirty(item.Parent)`

### `void Close(WorkspaceItem)`
- **位置**：`Workspace.cs:505`
- **副作用**：根据 ObjectType 释放资源；从集合移除

### `void CloseAll()`
- **位置**：`Workspace.cs:541`
- **副作用**：`Manager.UnloadAll(); UnloadClassDatabase; Reset all collections`

### `void RenameFile(WorkspaceItem, string)`
- **位置**：`Workspace.cs:561`
- **副作用**：修改 Object.name + WorkspaceItem.Name + 触发 PropertyChanged + Dirty

### `WorkspaceItem? FindWorkspaceItemByInstance(AssetsFileInstance)`
- **位置**：`Workspace.cs:583`

### `WorkspaceItem? FindWorkspaceItemByInstance(BundleFileInstance)`
- **位置**：`Workspace.cs:598`

### `WorkspaceItem? FindWorkspaceItemBfs(Func<WorkspaceItem,bool>)`
- **位置**：`Workspace.cs:611`

---

## Workspace.Saving.cs

### `static IStorageFile? ShowSaveAsDialog(IStorageProvider, string)`
- **位置**：`Workspace.Saving.cs:19`

### `static bool TryGetFileStream(WorkspaceItem, out FileStream?)`
- **位置**：`Workspace.Saving.cs:32`

### `static bool TryOpenForWriting(string, out FileStream?)`
- **位置**：`Workspace.Saving.cs:55`

### `void WriteAssetsFile(WorkspaceItem, Stream)`
- **位置**：`Workspace.Saving.cs:69`
- **算法**：`fileInst.file.Write(new AssetsFileWriter(stream))`

### `void WriteBundleFile(WorkspaceItem, Stream)`
- **位置**：`Workspace.Saving.cs:76`
- **算法**：
  1. `childrenFiles = item.Children.Intersect(UnsavedItems)`
  2. 同步 `DirectoryInfos`（重命名 + setNewData）
  3. `bunInst.file.Write(new AssetsFileWriter(stream))`

### `void WriteResource(WorkspaceItem, Stream)`
- **位置**：`Workspace.Saving.cs:120`

### `Task<(bool saved, bool failed)> Save(WorkspaceItem)`
- **签名**：`public async Task<(bool saved, bool failed)> Save(WorkspaceItem item)`
- **位置**：`Workspace.Saving.cs:142`
- **可见性**：public
- **算法**：
  1. 检查 `UnsavedItems.Contains`
  2. 取底层 FileStream
  3. 写临时 `~file`
  4. `File.Move(temp → original)`
  5. 重新 Read 新文件 + FixupAssetsFile + UnsavedItems.Remove
  6. 弹错误对话框（如失败）

### `Task<bool> SaveAs(WorkspaceItem)`
- **位置**：`Workspace.Saving.cs:288`

### `Task SaveAllAs()`
- **位置**：`Workspace.Saving.cs:342`
- **算法**：对所有 unsaved assets / bundles / resources 弹 SaveAs 对话框

---

## WorkspaceItem.cs

### `class WorkspaceItem : INotifyPropertyChanged`

#### 字段
- `string OriginalName { get; set; }`
- `string Name { get; set; }`
- `WorkspaceItem? Parent { get; set; }`
- `List<WorkspaceItem> Children { get; set; }`
- `object? Object { get; set; }` —— 真实 AssetsFileInstance / BundleFileInstance / Stream / AssetBundleDirectoryInfo
- `WorkspaceItemType ObjectType { get; }`
- `int LoadIndex { get; }`
- `bool Loaded => Object != null`

#### ctor 3 重载
- `(AssetsFileInstance fileInst, int loadOrder)` (`WorkspaceItem.cs:23`)
- `(Workspace workspace, BundleFileInstance bunInst, int loadOrder)` (`WorkspaceItem.cs:34`)
- `(string name, object? obj, int loadOrder, WorkspaceItemType type = WorkspaceItemType.OtherFile)` (`WorkspaceItem.cs:66`)

### `static IEnumerable<WorkspaceItem> GetAssetsFileWorkspaceItems(IEnumerable<WorkspaceItem>)`
- **位置**：`WorkspaceItem.cs:77`
- **算法**：DFS 提取所有 type == AssetsFile 的 item

### `void Update(string propertyName)`
- **位置**：`WorkspaceItem.cs:98`
- **副作用**：触发 `PropertyChanged`

---

## AssetInst.cs

### `class AssetInst : AssetFileInfo, INotifyPropertyChanged`

- **字段**：`AssetName`, `DisplayContainer`, `FileInstance`
- **属性**：
  - `AssetClassID Type => (AssetClassID)TypeId`
  - `AssetsFileReader FileReader => IsReplacerPreviewable ? previewStream : FileInstance.file.Reader`
  - `string FileName => FileInstance.name`
  - `long AbsoluteByteStart => IsReplacerPreviewable ? 0 : GetAbsoluteByteOffset(FileInstance.file)`
  - `string ModifiedString => Replacer != null ? "*" : ""`
  - `uint ByteSizeModified => Replacer.HasPreview() ? previewStream.Length : ByteSize`

---

## ContainerTool.cs (133 LoC)

### `class ContainerTool`

#### `List<AssetPPtr> PreloadTable { get; }`
#### `Dictionary<ContainerAssetInfo, string> AssetMap { get; }`

### `static ContainerTool FromAssetBundle(AssetsManager, AssetsFileInstance, AssetTypeValueField)`
- **签名**：`public static ContainerTool FromAssetBundle(AssetsManager am, AssetsFileInstance fromFile, AssetTypeValueField assetBundleBf)`
- **位置**：`ContainerTool.cs:16`

### `static ContainerTool FromResourceManager(AssetsManager, AssetsFileInstance, AssetTypeValueField)`
- **位置**：`ContainerTool.cs:45`

### `string? GetContainerPath(AssetsFileInstance, long)` / `(AssetPPtr)`
- 位置：`ContainerTool.cs:68, 73`

### `ContainerAssetInfo GetContainerInfo(string)`
- 位置：`ContainerTool.cs:84`

### `class ContainerAssetInfo`
- **位置**：`ContainerTool.cs:90`
- 字段：`PreloadIndex`, `PreloadSize`, `Ptr`, `Name`
- ctor 2 重载 + `static FromField` + `Equals/GetHashCode` 基于 `Ptr`

---

## ContainerToolManager.cs (97 LoC)

### `class ContainerToolManager`

#### 字段
- `Workspace _workspace`
- `Dictionary<(string, string), ContainerTool> _bundleContCache` —— 缓存
- `Dictionary<string, ContainerTool> _rsrcManContCache`

### `ContainerToolManager(Workspace)`
- **位置**：`ContainerToolManager.cs:17`

### `bool TryGetContainerTool(AssetsFileInstance, [NotNullWhen(true)] out ContainerTool?, [NotNullWhen(false)] out AssetsFileInstance?, [NotNullWhen(false)] out AssetTypeValueField?)`
- **位置**：`ContainerToolManager.cs:22`
- **算法**：缓存命中 → 直接返回；否则解析 AssetBundle / ResourceManager 缓存

### `AssetFileInfo? FindFirstAssetOfType(AssetsFileInstance, int)`
- **位置**：`ContainerToolManager.cs:85`
- **可见性**：private

---

## DuplicateWorkspaceFileException

简单异常类，含重复文件名 + 来源路径信息。