# 08 · Workspace 层详细说明

涉及文件：
- `UABEAvalonia/Workspace/AssetWorkspace.cs` (436 LoC)
- `UABEAvalonia/Workspace/BundleWorkspace.cs` (203 LoC)
- `UABEAvalonia/Workspace/UnityContainer.cs` (213 LoC)
- `UABEAvalonia/Workspace/AssetContainer.cs` (110 LoC)
- `UABEAvalonia/Workspace/AssetsFileChangeTypes.cs` (14 LoC)

---

## 8.1 AssetsFileChangeTypes.cs

```csharp
public enum AssetsFileChangeTypes
{
    None = 0,
    Dependencies = 1
}
```

无方法，无成员函数。仅一个 flags enum。

---

## 8.2 AssetContainer.cs

### `AssetContainer.AssetContainer(AssetFileInfo info, AssetsFileInstance fileInst, AssetTypeValueField? baseField)`
- **签名**：`public AssetContainer(AssetFileInfo info, AssetsFileInstance fileInst, AssetTypeValueField? baseField = null)`
- **位置**：`UABEAvalonia/Workspace/AssetContainer.cs:39`
- **可见性**：public
- **用途**：从已有 `AssetFileInfo` 构造（首次加载时调用）
- **副作用**：从 `fileInst.file.Reader` 取 `AssetsFileReader`

### `AssetContainer.AssetContainer(AssetsFileReader fileReader, long assetPosition, long pathId, int classId, ushort monoId, uint size, AssetsFileInstance fileInst, AssetTypeValueField?)`
- **签名**：`public AssetContainer(AssetsFileReader fileReader, long assetPosition, long pathId, int classId, ushort monoId, uint size, AssetsFileInstance fileInst, AssetTypeValueField? baseField = null)`
- **位置**：`UABEAvalonia/Workspace/AssetContainer.cs:54`
- **可见性**：public
- **用途**：用于"新创建"或"修改后"的 asset（位置由 caller 提供）
- **被调用**：`AssetWorkspace.AddReplacer`（line 92）

### `AssetContainer.AssetContainer(AssetContainer container, AssetsFileReader fileReader, long assetPosition, uint size)`
- **签名**：`public AssetContainer(AssetContainer container, AssetsFileReader fileReader, long assetPosition, uint size)`
- **位置**：`UABEAvalonia/Workspace/AssetContainer.cs:70`
- **可见性**：public
- **用途**：保留其他字段，更新位置/大小/reader

### `AssetContainer.AssetContainer(AssetContainer container, AssetTypeValueField baseField)`
- **签名**：`public AssetContainer(AssetContainer container, AssetTypeValueField baseField)`
- **位置**：`UABEAvalonia/Workspace/AssetContainer.cs:84`
- **可见性**：public
- **用途**：克隆 + 替换 BaseValueField（懒加载结果）
- **被调用**：`AssetWorkspace.GetAssetContainer`（line 280）

### `AssetContainer.SetNewFile(AssetsFileInstance fileInst)`
- **签名**：`public void SetNewFile(AssetsFileInstance fileInst)`
- **位置**：`UABEAvalonia/Workspace/AssetContainer.cs:98`
- **可见性**：public
- **副作用**：抛 `Exception("Missed an asset during save")` 若 pathId 找不到
- **调用了**：`fileInst.file.GetAssetInfo(PathId)`

---

## 8.3 AssetWorkspace.cs

### `AssetWorkspace.AssetWorkspace(AssetsManager am, bool fromBundle)`
- **签名**：`public AssetWorkspace(AssetsManager am, bool fromBundle)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:46`
- **可见性**：public
- **调用了**：集合初始化器

### `AssetWorkspace.AddReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, Stream? previewStream)`
- **签名**：`public void AddReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, Stream? previewStream = null)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:68`
- **可见性**：public
- **副作用**：
  - 若已有同 assetId replacer → 旧 replacer 通过 `RemoveReplacer(..., true)` 移除
  - 把 replacer 加入 `NewAssets`
  - `previewStream == null` 时 `replacer.Write` 到 `MemoryStream`
  - 把 `previewStream` 加到 `NewAssetDatas`
  - 若 replacer 是 `AssetsRemover`，从 `LoadedAssets` 删除；否则新建 `AssetContainer` 加到 `LoadedAssets`
  - 触发 `ItemUpdated` 事件
  - `Modified = true`
- **调用了**：`RemoveReplacer`, `replacer.Write`, `new AssetContainer(...)`
- **被调用**：所有插件的 import 路径（如 `ImportTextureOption.ExecutePlugin` line 150, `ImportFontOption` line 96, `ImportTextAssetOption` line 84, `EditTextureOption` line 48）

### `AssetWorkspace.RemoveReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, bool closePreviewStream)`
- **签名**：`public void RemoveReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, bool closePreviewStream = true)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:108`
- **可见性**：public
- **副作用**：
  - 从 `NewAssets`/`NewAssetDatas`/`RemovedAssets` 移除
  - 触发 `ItemUpdated`
  - 若 NewAssets 为空且 `AnyOtherAssetChanges()==false` → `Modified = false`
- **被调用**：`AddReplacer` 内部

### `AssetWorkspace.LoadAssetsFile(AssetsFileInstance fromFile, bool loadDependencies)`
- **签名**：`public void LoadAssetsFile(AssetsFileInstance fromFile, bool loadDependencies)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:131`
- **可见性**：public
- **副作用**：
  - 若 `LoadedFileNames` 已包含（lowercase）→ return
  - `fromFile.file.GenerateQuickLookup()`
  - 把所有 AssetInfo 包成 `AssetContainer` 加入 `LoadedAssets`
  - 若 `loadDependencies`，对每个 external 递归调用
- **调用了**：`GenerateQuickLookup`, `new AssetContainer`, `fromFile.GetDependency`
- **被调用**：`MainWindow.LoadBundle`, `InfoWindow.LoadAllAssetsWithDeps`

### `AssetWorkspace.GetChangedFiles()`
- **签名**：`public HashSet<AssetsFileInstance> GetChangedFiles()`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:172`
- **可见性**：public
- **返回值**：包含所有 NewAssets 所在文件 + OtherAssetChanges != None 的文件
- **被调用**：保存时（`MainWindow.SaveBundleOver` 等）

### `AssetWorkspace.SetOtherAssetChangeFlag(AssetsFileInstance, AssetsFileChangeTypes)`
- **签名**：`public void SetOtherAssetChangeFlag(AssetsFileInstance fileInst, AssetsFileChangeTypes changeTypes)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:195`
- **可见性**：public
- **副作用**：OR-merge `changeTypes` 到 `OtherAssetChanges[fileInst]`

### `AssetWorkspace.UnsetOtherAssetChangeFlag(AssetsFileInstance, AssetsFileChangeTypes)`
- **签名**：`public void UnsetOtherAssetChangeFlag(AssetsFileInstance fileInst, AssetsFileChangeTypes changeTypes)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:203`
- **可见性**：public
- **副作用**：AND-NOT `changeTypes`；若结果为 None 则从字典删除

### `AssetWorkspace.GenerateAssetsFileLookup()`
- **签名**：`public void GenerateAssetsFileLookup()`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:224`
- **可见性**：public
- **副作用**：填充 `LoadedFileLookup[path.ToLower()]`

### `AssetWorkspace.GetTemplateField(AssetContainer cont, bool forceCldb, bool skipMonoBehaviourFields)`
- **签名**：`public AssetTypeTemplateField GetTemplateField(AssetContainer cont, bool forceCldb = false, bool skipMonoBehaviourFields = false)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:232`
- **可见性**：public
- **返回值**：`AssetTypeTemplateField`
- **调用了**：`am.GetTemplateBaseField`
- **被调用**：`TextureHelper.GetByteArrayTexture`, `FontHelper.GetByteArrayFont`, `AssetDataTreeView.LoadComponent` 间接

### `AssetWorkspace.GetAssetContainer(AssetsFileInstance fileInst, int fileId, long pathId, bool onlyInfo)`
- **签名**：`public AssetContainer? GetAssetContainer(AssetsFileInstance fileInst, int fileId, long pathId, bool onlyInfo = true)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:243`
- **可见性**：public
- **算法**：
  1. `fileId != 0` 时 resolve 依赖
  2. 在 `LoadedAssets` 查找
  3. `!onlyInfo && !HasValueField` 时：
     - MonoBehaviour → `SetMonoTempGenerators`（若未设置）
     - `MakeValue(reader, pos, refMan)`
     - 用新 `AssetContainer(cont, baseField)` 替换
- **副作用**：可能触发 `MonoTemplateLoadFailed` 事件
- **调用了**：`fileInst.GetDependency`, `GetTemplateField`, `am.GetRefTypeManager`, `tempField.MakeValue`
- **被调用**：UI、InfoWindow、AssetDataTreeView、UnityContainer

### `AssetWorkspace.GetAssetContainer` 其他 3 重载
- `(AssetsFileInstance, AssetTypeValueField pptrField, bool onlyInfo)` (`AssetWorkspace.cs:293`)
- `(AssetsFileInstance, AssetPPtr pptr, bool onlyInfo)` (`AssetWorkspace.cs:300`)
- `(AssetContainer cont)` (`AssetWorkspace.cs:308`)

### `AssetWorkspace.GetAssetsOfType(int classId)` / `(AssetClassID classId)`
- **签名**：`public List<AssetContainer> GetAssetsOfType(int classId)` / `public List<AssetContainer> GetAssetsOfType(AssetClassID classId)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:313, 332`
- **可见性**：public
- **被调用**：`UnityContainer.TryGetBundleContainerBaseField` 等

### `AssetWorkspace.GetBaseField` 3 重载
- `(AssetContainer cont)` (`AssetWorkspace.cs:337`)
- `(AssetsFileInstance fileInst, int fileId, long pathId)` (`AssetWorkspace.cs:352`)
- `(AssetsFileInstance, AssetTypeValueField pptrField)` (`AssetWorkspace.cs:361`)
- **实现**：先 `GetAssetContainer(..., onlyInfo: false)`，再 `cont.BaseValueField`

### `AssetWorkspace.GetConcatMonoBaseField(AssetContainer cont, string managedPath)`
- **签名**：`public AssetTypeValueField GetConcatMonoBaseField(AssetContainer cont, string managedPath)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:373`
- **可见性**：public
- **用途**：通过 Managed DLL 中的 MonoScript 信息扩展 MonoBehaviour 的 TypeTree

### `AssetWorkspace.GetConcatMonoTemplateField(AssetContainer cont, string managedPath)`
- **签名**：`public AssetTypeTemplateField GetConcatMonoTemplateField(AssetContainer cont, string managedPath)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:379`
- **可见性**：public
- **调用了**：`MonoCecilTempGenerator.GetTemplateField`

### `AssetWorkspace.SetMonoTempGenerators(string fileDir)`
- **签名**：`public bool SetMonoTempGenerators(string fileDir)`
- **位置**：`UABEAvalonia/Workspace/AssetWorkspace.cs:411`
- **可见性**：public
- **返回值**：是否成功设置
- **算法**：
  - 一次性标志 `setMonoTempGeneratorsYet`
  - `FindCpp2IlFiles.Find(fileDir)` → 成功且 `ConfigurationManager.Settings.UseCpp2Il` → `Cpp2IlTempGenerator`
  - 否则查找 `Managed/` 目录 → `MonoCecilTempGenerator`
- **调用了**：`FindCpp2IlFiles.Find`

---

## 8.4 BundleWorkspace.cs

### `BundleWorkspace.BundleWorkspace()`
- **签名**：`public BundleWorkspace()`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:23`
- **可见性**：public
- **副作用**：`new AssetsManager()`

### `BundleWorkspace.Reset(BundleFileInstance? bundleInst)`
- **签名**：`public void Reset(BundleFileInstance? bundleInst)`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:33`
- **可见性**：public
- **副作用**：清空 Files/FileLookup/RemovedFiles + PopulateFilesList

### `BundleWorkspace.PopulateFilesList()`
- **签名**：`private void PopulateFilesList()`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:45`
- **可见性**：private
- **副作用**：把 `BlockAndDirInfo.DirectoryInfos` 转成 `BundleWorkspaceItem`，加入 `Files`/`FileLookup`
- **调用了**：`new SegmentStream`, `new BundleWorkspaceItem`

### `BundleWorkspace.AddOrReplaceFile(Stream stream, string name, bool isSerialized, string? prevName)`
- **签名**：`public void AddOrReplaceFile(Stream stream, string name, bool isSerialized, string? prevName = null)`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:60`
- **可见性**：public
- **副作用**：替换 Files 中条目；管理 FileLookup；关闭旧 stream（如果 IsNew）

### `BundleWorkspace.RenameFile(string origName, string newName)`
- **签名**：`public void RenameFile(string origName, string newName)`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:100`
- **可见性**：public
- **被调用**：`MainWindow.BtnRename_Click` (`MainWindow.axaml.cs:482`)

### `BundleWorkspace.GetReplacers()`
- **签名**：`public List<BundleReplacer> GetReplacers()`
- **位置**：`UABEAvalonia/Workspace/BundleWorkspace.cs:111`
- **可见性**：public
- **返回值**：包含 RemovedFiles → BundleRemover；ItemModified → BundleReplacerFromStream；Name changed → BundleRenamer
- **被调用**：保存路径（`MainWindow.SaveBundle` line 924）

### `BundleWorkspaceItem` 类
- 字段：`Name`, `OriginalName`, `IsNew`, `IsSerialized`, `IsRemoved`, `IsModified`, `Stream`
- 计算属性 `Color` 根据 IsSerialized/.resS/.resource 决定 Avalonia `IBrush` 颜色
- `override ToString() => Name + (IsModified ? "*" : "")`

---

## 8.5 UnityContainer.cs

### `UnityContainer.FromAssetBundle(AssetsManager am, AssetsFileInstance fromFile, AssetTypeValueField assetBundleBf)`
- **签名**：`public void FromAssetBundle(AssetsManager am, AssetsFileInstance fromFile, AssetTypeValueField assetBundleBf)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:19`
- **可见性**：public
- **算法**：解析 `m_PreloadTable.Array` 与 `m_Container.Array`，填入 `PreloadTable` / `AssetMap`

### `UnityContainer.FromResourceManager(AssetsManager am, AssetsFileInstance fromFile, AssetTypeValueField rsrcManBf)`
- **签名**：`public void FromResourceManager(AssetsManager am, AssetsFileInstance fromFile, AssetTypeValueField rsrcManBf)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:44`
- **可见性**：public
- **算法**：解析 `m_Container.Array`，不读 preloadIndex（设为 -1）

### `UnityContainer.GetContainerPath(AssetsFileInstance fileInst, long pathId)` / `(AssetPPtr assetPPtr)`
- **签名**：`public string? GetContainerPath(AssetsFileInstance fileInst, long pathId)` / `public string? GetContainerPath(AssetPPtr assetPPtr)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:63, 68`
- **可见性**：public
- **调用了**：`AssetMap.TryGetValue`

### `UnityContainer.GetContainerInfo(string path)`
- **签名**：`public UnityContainerAssetInfo GetContainerInfo(string path)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:79`
- **可见性**：public
- **实现**：LINQ FirstOrDefault

### `UnityContainer.TryGetBundleContainerBaseField(AssetWorkspace, AssetsFileInstance, out AssetsFileInstance, out AssetTypeValueField)`
- **签名**：`public static bool TryGetBundleContainerBaseField(AssetWorkspace workspace, AssetsFileInstance file, [MaybeNullWhen(false)] out AssetsFileInstance actualFile, [MaybeNullWhen(false)] out AssetTypeValueField baseField)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:85`
- **可见性**：public static
- **返回值**：是否找到 AssetBundle asset
- **调用了**：`workspace.GetAssetContainer`

### `UnityContainer.TryGetRsrcManContainerBaseField(...)`
- **签名**：`public static bool TryGetRsrcManContainerBaseField(AssetWorkspace workspace, AssetsFileInstance file, [MaybeNullWhen(false)] out AssetsFileInstance actualFile, [MaybeNullWhen(false)] out AssetTypeValueField baseField)`
- **位置**：`UABEAvalonia/Workspace/UnityContainer.cs:111`
- **可见性**：public static
- **算法**：
  1. `PathUtils.GetAssetsFileDirectory(file)`
  2. 加载 `globalgamemanagers` 文件
  3. 找 ResourceManager asset
  4. 取 BaseValueField

### `UnityContainerAssetInfo` 类
- 字段：`preloadIndex`, `preloadSize`, `AssetPPtr asset`, `object name`
- ctor 2 重载（`UnityContainer.cs:175, 182`）
- 静态 `FromField(AssetTypeValueField)` (`UnityContainer.cs:189`)
- `Equals/GetHashCode` 基于 `asset`

---

## 8.6 关键调用栈

```
[UI 按钮] Save
  → MainWindow.AskForLocationAndSave (MainWindow.axaml.cs:619)
    → BundleWorkspace.GetReplacers
    → AssetWorkspace.GetChangedFiles
    → bun.Write (AssetsTools.NET)
    → File.Move (temp → original, original → .bak)
```

```
[Texture] ExportTextureOption.ExecutePlugin
  → TextureHelper.GetByteArrayTexture
    → AssetWorkspace.GetTemplateField
  → TextureFile.ReadTextureFile
  → TextureHelper.GetResSTexture / GetRawTextureBytes
  → TextureImportExport.Export
    → TextureEncoderDecoder.Decode
      → PInvoke.DecodeByCrunchUnity / DecodeByPVRTexLib / DecodeAssetRipperTex
  → TextureImportExport.SaveImageAtPath
```

```
[MonoBehaviour 首次访问]
  → AssetWorkspace.GetAssetContainer (with onlyInfo: false)
    → SetMonoTempGenerators
      → FindCpp2IlFiles.Find
      → am.MonoTempGenerator = new Cpp2IlTempGenerator(...)
    → tempField.MakeValue
      → am.GetRefTypeManager
```