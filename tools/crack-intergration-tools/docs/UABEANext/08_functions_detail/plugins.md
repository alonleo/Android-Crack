# 08 · 插件系统详细说明

涉及文件：
- `UABEANext4/Plugins/PluginLoader.cs` (125 LoC)
- `UABEANext4/Plugins/PluginLoadContext.cs` (46 LoC)
- `UABEANext4/Plugins/IUavPluginOption.cs` (14)
- `UABEANext4/Plugins/IUavPluginPreviewer.cs`
- `UABEANext4/Plugins/IUavPluginPreviewerFunctions.cs`
- `UABEANext4/Plugins/IUavPluginFunctions.cs`
- `UABEANext4/Plugins/UavPluginFunctions.cs` (58 LoC)
- `UABEANext4/Plugins/UavPluginMode.cs`
- `UABEANext4/Plugins/UavPluginPreviewerType.cs`
- `UABEANext4/Plugins/PluginItemInfo.cs`
- `UABEANext4/Plugins/PluginOptionModePair.cs`
- `UABEANext4/Plugins/PluginPreviewerTypePair.cs` / `UavPluginPreviewerTypePair.cs`

---

## PluginLoadContext.cs

### `class PluginLoadContext : AssemblyLoadContext`
- **位置**：`PluginLoadContext.cs:8`

#### 字段
- `private readonly AssemblyDependencyResolver _resolver`

#### `PluginLoadContext(string pluginPath)`
- **签名**：`public PluginLoadContext(string pluginPath)`
- **位置**：`PluginLoadContext.cs:11`
- **可见性**：public
- **调用了**：`base(isCollectible: true)` —— 支持 GC 卸载
- **副作用**：`new AssemblyDependencyResolver(pluginPath)`

#### `Assembly LoadAssemblyByName(string name)`
- **签名**：`public Assembly LoadAssemblyByName(string name)`
- **位置**：`PluginLoadContext.cs:16`
- **可见性**：public
- **算法**：通过 resolver 解析 → `LoadFromAssemblyPath` 或 null

#### `Assembly LoadAssemblyByPath(string path)`
- **签名**：`public Assembly LoadAssemblyByPath(string path)`
- **位置**：`PluginLoadContext.cs:21`

#### `Assembly? Load(AssemblyName assemblyName)`
- **签名**：`protected override Assembly? Load(AssemblyName assemblyName)`
- **位置**：`PluginLoadContext.cs:26`
- **可见性**：protected override

#### `IntPtr LoadUnmanagedDll(string unmanagedDllName)`
- **签名**：`protected override IntPtr LoadUnmanagedDll(string unmanagedDllName)`
- **位置**：`PluginLoadContext.cs:37`
- **可见性**：protected override

---

## PluginLoader.cs

### `class PluginLoader`

#### 字段
- `private readonly List<IUavPluginOption> _pluginOptions = []`
- `private readonly List<IUavPluginPreviewer> _pluginPreviewers = []`
- `private readonly HashSet<string> _loadedPaths = new(StringComparer.OrdinalIgnoreCase)`

### `bool LoadPlugin(string path)`
- **签名**：`public bool LoadPlugin(string path)`
- **位置**：`PluginLoader.cs:15`
- **可见性**：public
- **返回值**：是否成功加载
- **算法**：
  1. 检查 `_loadedPaths`
  2. `var alc = new PluginLoadContext(path)`
  3. `var asm = alc.LoadFromAssemblyPath(path)`
  4. 遍历 `asm.GetExportedTypes()`：
     - `typeof(IUavPluginOption).IsAssignableFrom(t)` → `Activator.CreateInstance(t)` → `_pluginOptions.Add`
     - `typeof(IUavPluginPreviewer).IsAssignableFrom(t)` → `Activator.CreateInstance(t)` → `_pluginPreviewers.Add`
  5. `_loadedPaths.Add(path)`
- **被调用**：`LoadPluginsInDirectory` 内

### `void LoadPluginsInDirectory(string directory)`
- **签名**：`public void LoadPluginsInDirectory(string directory)`
- **位置**：`PluginLoader.cs:79`
- **可见性**：public
- **副作用**：`Directory.CreateDirectory` 若不存在
- **调用了**：`LoadPlugin`

### `List<PluginOptionModePair> GetOptionsThatSupport(Workspace, List<AssetInst>, UavPluginMode)`
- **签名**：`public List<PluginOptionModePair> GetOptionsThatSupport(Workspace workspace, List<AssetInst> assets, UavPluginMode mode)`
- **位置**：`PluginLoader.cs:93`
- **可见性**：public
- **返回值**：匹配的 (option, mode) 对
- **算法**：
  - 遍历 `_pluginOptions`
  - `option.Options.HasFlag(mode) && option.SupportsSelection(workspace, mode, selection)` → 加入

### `List<PluginPreviewerTypePair> GetPreviewersThatSupport(Workspace, AssetInst)`
- **签名**：`public List<PluginPreviewerTypePair> GetPreviewersThatSupport(Workspace workspace, AssetInst asset)`
- **位置**：`PluginLoader.cs:113`
- **可见性**：public
- **算法**：遍历 `_pluginPreviewers`，调用 `SupportsPreview`；返回非 None 的

---

## 接口

### `interface IUavPluginOption`
- **位置**：`IUavPluginOption.cs:6`
- 成员：
  - `string Name { get; }`
  - `string Description { get; }`
  - `UavPluginMode Options { get; }`
  - `bool SupportsSelection(Workspace workspace, UavPluginMode mode, List<AssetInst> selection)`
  - `Task<bool> Execute(Workspace workspace, IUavPluginFunctions funcs, UavPluginMode mode, List<AssetInst> selection)`

### `interface IUavPluginPreviewer`
- **位置**：`IUavPluginPreviewer.cs:7`
- 成员：
  - `string Name { get; }`
  - `string Description { get; }`
  - `UavPluginPreviewerType SupportsPreview(Workspace workspace, AssetInst asset)`

### `interface IUavPluginFunctions`
- **位置**：`IUavPluginFunctions.cs:6`
- 成员：
  - `Task<string[]> ShowOpenFileDialog(FilePickerOpenOptions options)`
  - `Task<string?> ShowSaveFileDialog(FilePickerSaveOptions options)`
  - `Task<string?> ShowOpenFolderDialog(FolderPickerOpenOptions options)`
  - `Task<T?> ShowDialog<T>(IDialogAware<T> dialogAware)`
  - `Task ShowMessageDialog(string title, string message)`

### `interface IUavPluginPreviewerFunctions`
- **位置**：`IUavPluginPreviewerFunctions.cs:7`
- 成员：
  - `Task SetPreviewText(TextDocument document)`
  - `Task SetPreviewImage(Bitmap image)`
  - `Task SetPreviewMesh(MeshObj mesh)`

---

## UavPluginFunctions.cs (58 LoC)

### `class UavPluginFunctions : IUavPluginFunctions`

#### 字段
- `private readonly IDialogService _dialogService`
- `private readonly IStorageProvider _storageProvider`

### `UavPluginFunctions()`
- **签名**：`public UavPluginFunctions()`
- **位置**：`UavPluginFunctions.cs:16`
- **可见性**：public

### `Task<string[]> ShowOpenFileDialog(FilePickerOpenOptions)`
- **位置**：`UavPluginFunctions.cs:26`
- **算法**：用 `_storageProvider.OpenFilePickerAsync` → 取 LocalPath

### `Task<string?> ShowSaveFileDialog(FilePickerSaveOptions)`
- **位置**：`UavPluginFunctions.cs:32`

### `Task<string?> ShowOpenFolderDialog(FolderPickerOpenOptions)`
- **位置**：`UavPluginFunctions.cs:38`

### `Task<T?> ShowDialog<T>(IDialogAware<T>)`
- **位置**：`UavPluginFunctions.cs:48`

### `Task ShowMessageDialog(string, string)`
- **位置**：`UavPluginFunctions.cs:53`

---

## 枚举

### `enum UavPluginMode`
- **位置**：`UavPluginMode.cs:6`
- 值：`Import = 1`, `Export = 2`, `Info = 4`（flags）

### `enum UavPluginPreviewerType`
- **位置**：`UavPluginPreviewerType.cs:2`
- 值：`None`, `Image`, `Text`, `Mesh`

---

## 元数据类

### `class PluginItemInfo`
- **位置**：`PluginItemInfo.cs:8`
- 字段：`Name`, `_option`, `_docViewModel`
- ctor + `Task Execute(object selectedItems)` + `override ToString`

### `class PluginOptionModePair(IUavPluginOption, UavPluginMode)`
- **位置**：`PluginOptionModePair.cs:2`
- `IUavPluginOption Option { get; }`
- `UavPluginMode Mode { get; }`
- `override ToString`

### `class PluginPreviewerTypePair(IUavPluginPreviewer, UavPluginPreviewerType)`
- **位置**：`UavPluginPreviewerTypePair.cs:2`
- 类似

---

## 关键调用栈

```
[启动]
  → Workspace ctor
    → Plugins.LoadPluginsInDirectory("plugins")
      → foreach *.dll:
        new PluginLoadContext(path)
        asm = LoadFromAssemblyPath
        foreach exported type:
          if IUavPluginOption → 实例化 → _pluginOptions.Add
          if IUavPluginPreviewer → 实例化 → _pluginPreviewers.Add
```

```
[右键菜单]
  → MainViewModel.PopulatePluginMenu
    → Plugins.GetOptionsThatSupport(workspace, assets, mode)
    → for each: 创建 RelayCommand → Execute
      → option.Execute(workspace, funcs, mode, selection)
```

```
[预览]
  → MainViewModel.SelectedAsset changed
    → Plugins.GetPreviewersThatSupport(workspace, asset)
    → 第一个匹配 → 调用 SetPreviewText/Image/Mesh
```