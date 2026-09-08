# 08 · Forms 其余窗口 / Controls / Utils / Config

## 8.1 Forms/ 其余窗口

UABEA 共 17 个对话框 / 窗口。每个 .axaml.cs 都是 Avalonia Window 子类 + 几个事件 handler。本节摘要。

### About.axaml.cs
- `AboutWindow()` ctor，仅显示版本 + 链接
- 调用方：MainWindow.MenuAbout_Click

### AddAssetWindow.axaml.cs
- 让用户选择 type + path id，把新建 AssetsReplacerFromMemory 加到 workspace

### AddDependencyWindow.axaml.cs
- 让用户选择一个 .assets / .bundle 加入依赖图

### DataWindow.axaml.cs
- 显示纯字节十六进制视图（用于查看 Texture2D 等无法树化的资源）

### EditDataWindow.axaml.cs
- 与 DataWindow 类似但允许编辑；保存后构造 AssetsReplacerFromMemory

### ExportBatchChooseTypeDialog.axaml.cs
- 让用户在 BatchExport 时选 png/tga/jpg/bmp

### FilterAssetTypeDialog.axaml.cs
- 列表显示所有 AssetClassID + 复选框
- 返回 HashSet<AssetClassID> 用于 InfoWindow 过滤

### GameObjectViewWindow.axaml.cs
- 显示 GameObject 的 Transform 树（仅显示 m_Name / m_Children 列表）

### GoToAssetDialog.axaml.cs
- 跳转对话框（按 PathID）

### ImportBatch.axaml.cs
- 批量导入时让用户选择哪个文件对应哪个 asset
- 字段：`ImportBatchInfo { AssetContainer cont, string importFile, long pathId }`

### ImportSerializedDialog.axaml.cs
- 把外部 .assets 文件导入到当前 bundle（作为新 entry）

### LoadModPackageDialog.axaml.cs
- 加载 .emip 文件并预览信息

### ModMakerDialog.axaml.cs
- 让用户从当前修改创建 .emip 包
- 调 `InstallerPackageFile.Write`

### PluginWindow.axaml.cs
- 显示已加载插件列表 + 启动 plugin 的入口

### ProgressWindow.axaml.cs
- 通用进度条窗口（包装 IProgress）

### RenameWindow.axaml.cs
- 重命名 dialog

### SearchDialog.axaml.cs
- 按名字 / path 搜索资产
- 使用 SearchUtils.WildcardMatches

### SelectDumpWindow.axaml.cs
- 在 MonoBehaviour 字段未恢复时，让用户指定 dump 工具输出文件位置

### VersionWindow.axaml.cs
- 版本信息 + Unity class database 状态

---

## 8.2 Controls/AssetDataTreeView.cs

### `class AssetDataTreeView : TreeView`

#### 字段
- `private AssetWorkspace workspace`
- `private InfoWindow win`
- 4 个 Avalonia `SolidColorBrush` 主题色（prim/type/string/value）

#### 事件
- `DoubleTapped` (`AssetDataTreeView.cs:87`)
- `menuEditAsset/menuVisitAsset/menuExpandSel/menuCollapseSel.Click` (`AssetDataTreeView.cs:88-91`)

#### 构造函数
##### `AssetDataTreeView()`
- **位置**：`AssetDataTreeView.cs:80`
- 创建 4 个 MenuItem 与 ContextMenu

#### 事件处理
##### `MenuEditAsset_Click` (`AssetDataTreeView.cs:103`)
- **算法**：
  1. 取 `SelectedItem` → `TreeViewItem`
  2. `workspace.GetAssetContainer(info.fromFile, 0, info.fromPathId, false)`
  3. `win.ShowEditAssetWindow(cont)` → 弹 EditDataWindow
  4. 若 saved → 弹 MessageBoxUtil

##### `AssetDataTreeView_DoubleTapped` (`AssetDataTreeView.cs:127`)
- **算法**：toggle `IsExpanded`

##### `MenuVisitAsset_Click` (`AssetDataTreeView.cs:136`)
- **算法**：`win.SelectAsset(info.fromFile, info.fromPathId)`

##### `MenuExpandSel_Click` / `MenuCollapseSel_Click` (`AssetDataTreeView.cs:149, 157`)
- 调 `ExpandAllChildren / CollapseAllChildren`

#### 公共方法

##### `Init(InfoWindow win, AssetWorkspace workspace)`
- **签名**：`public void Init(InfoWindow win, AssetWorkspace workspace)`
- **位置**：`AssetDataTreeView.cs:165`

##### `Reset()`
- **签名**：`public void Reset()`
- **位置**：`AssetDataTreeView.cs:172`
- **副作用**：ItemsSource = new AvaloniaList

##### `LoadComponent(AssetContainer container)`
- **签名**：`public void LoadComponent(AssetContainer container)`
- **位置**：`AssetDataTreeView.cs:177`
- **算法**：
  1. `workspace.GetBaseField(container)`
  2. 显示错误或构造 baseItem
  3. 加 MonoBehaviour 名后缀
  4. 子节点占位 "Loading..." → SetTreeItemEvents

##### `ExpandAllChildren / CollapseAllChildren(TreeViewItem)`
- **签名**：`public void ExpandAllChildren(TreeViewItem treeItem)` / `public void CollapseAllChildren(TreeViewItem treeItem)`
- **位置**：`AssetDataTreeView.cs:214, 237`

#### 私有方法

##### `CreateTreeItem(string)` / `CreateColorTreeItem(typeName, fieldName, ...)` 
- 位置：`AssetDataTreeView.cs:260, 265, 270`
- 算法：构造 Avalonia TextBlock + Span/Bold

##### `SetTreeItemEvents(TreeViewItem, AssetsFileInstance, long, AssetTypeValueField)`
- **签名**：`private void SetTreeItemEvents(TreeViewItem item, AssetsFileInstance fromFile, long fromPathId, AssetTypeValueField field)`
- **位置**：`AssetDataTreeView.cs:310`
- **可见性**：private
- **算法**：
  1. `item.Tag = AssetDataTreeViewItem(fromFile, fromPathId)`
  2. 订阅 `IsExpanded` 变化
  3. 第一次展开 → `TreeLoad`

##### `SetPPtrEvents(TreeViewItem, AssetsFileInstance, long, AssetContainer)`
- **位置**：`AssetDataTreeView.cs:326`
- **算法**：与 SetTreeItemEvents 类似，但 on expand 调 `GetBaseField(cont)` 并构造新的 child items

##### `TreeLoad(AssetsFileInstance, AssetTypeValueField, long, TreeViewItem)`
- **签名**：`private void TreeLoad(AssetsFileInstance fromFile, AssetTypeValueField assetField, long fromPathId, TreeViewItem treeItem)`
- **位置**：`AssetDataTreeView.cs:355`
- **可见性**：private
- **算法**：
  1. `assetField.Children`
  2. 数组 → 显示 size 字段 + `[i]` 索引
  3. 叶子 → 显示 typeName + fieldName + value
  4. `ManagedReferencesRegistry` → 渲染 v1/v2 特殊格式
  5. `PPtr<>` 类型 → 添加 `[view asset]` 子项 → `SetPPtrEvents`
- **副作用**：极大填充 ItemsSource

### `class AssetDataTreeViewItem`
- 字段：`loaded`, `fromFile`, `fromPathId`
- ctor (`AssetDataTreeView.cs:568`)

---

## 8.3 Utils/

### AssetNameUtils.cs

#### `static void GetDisplayNameFast(AssetWorkspace workspace, AssetContainer cont, bool usePrefix, out string assetName, out string typeName)`
- **签名**：`public static void GetDisplayNameFast(AssetWorkspace workspace, AssetContainer cont, bool usePrefix, out string assetName, out string typeName)`
- **位置**：`UABEAvalonia/Utils/AssetNameUtils.cs:14`
- **可见性**：public static
- **算法**：
  1. GameObject → 取 m_Name（尝试避免 BaseField IO）
  2. MonoBehaviour → 读 m_Name 字段
  3. 其他 → 退化为 Type/PathID

#### `static string GetMonoBehaviourNameFast(AssetWorkspace workspace, AssetContainer cont)`
- **签名**：`public static string GetMonoBehaviourNameFast(AssetWorkspace workspace, AssetContainer cont)`
- **位置**：`UABEAvalonia/Utils/AssetNameUtils.cs:136`
- **可见性**：public static
- **被调用**：`AssetDataTreeView.LoadComponent`

### FileDialogUtils.cs

#### `static string[] GetOpenFileDialogFiles(IReadOnlyList<IStorageFile> files)`
- **签名**：`public static string[] GetOpenFileDialogFiles(IReadOnlyList<IStorageFile> files)`
- **位置**：`UABEAvalonia/Utils/FileDialogUtils.cs:12`
- **可见性**：public static
- **返回值**：所有 Path.LocalPath

#### `static string[] GetOpenFolderDialogFiles(IReadOnlyList<IStorageFolder>)`
- **位置**：`UABEAvalonia/Utils/FileDialogUtils.cs:17`

#### `static string? GetSaveFileDialogFile(IStorageFile? file)`
- **位置**：`UABEAvalonia/Utils/FileDialogUtils.cs:22`

### FileUtils.cs

#### `static string GetFormattedByteSize(long size)`
- **签名**：`public static string GetFormattedByteSize(long size)`
- **位置**：`UABEAvalonia/Utils/FileUtils.cs:13`
- **可见性**：public static
- **算法**：除 1024 找合适 suffix (B/KB/MB/GB/TB/PB/EB)

#### `static List<string> GetFilesInDirectory(string path, List<string> extensions)`
- **位置**：`UABEAvalonia/Utils/FileUtils.cs:21`
- **算法**：Directory.EnumerateFiles + 后缀过滤

### PathUtils.cs

#### `static string ReplaceInvalidPathChars(string filename)`
- **签名**：`public static string ReplaceInvalidPathChars(string filename)`
- **位置**：`UABEAvalonia/Utils/PathUtils.cs:14`
- **可见性**：public static

#### `static string GetFilePathWithoutExtension(string path)`
- **位置**：`UABEAvalonia/Utils/PathUtils.cs:19`

#### `static string GetAssetsFileDirectory(AssetsFileInstance fileInst)`
- **位置**：`UABEAvalonia/Utils/PathUtils.cs:30`
- **算法**：
  - 若 `parentBundle != null`，返回 bundle 路径目录
  - 否则返回 `Path.GetDirectoryName(fileInst.path)`

### SearchUtils.cs

#### `static bool WildcardMatches(string test, string pattern, bool caseSensitive)`
- **签名**：`public static bool WildcardMatches(string test, string pattern, bool caseSensitive = true)`
- **位置**：`UABEAvalonia/Utils/SearchUtils.cs:19`
- **可见性**：public static
- **算法**：支持 `*` 通配符

### MessageBox/

#### `enum MessageBoxType`
- **位置**：`UABEAvalonia/Utils/MessageBox/MessageBox.axaml.cs:148`
- 值：Information, Warning, Error, YesNo, YesNoCancel

#### `enum MessageBoxResult`
- **位置**：`UABEAvalonia/Utils/MessageBox/MessageBox.axaml.cs:157`
- 值：Button1, Button2, Button3

#### `class MessageBox : Window`
- 3 个 ctor (`MessageBox.axaml.cs:12, 24, 52`)
- `Btn1_Click / Btn2_Click / Btn3_Click` (`MessageBox.axaml.cs:88, 113, 134`)

#### `static class MessageBoxUtil`
- **`ShowDialog(Window, string, string)`** 等 5 个重载 (`MessageBoxUtil.cs:8+`)
- 返回 `Task<MessageBoxResult>`

---

## 8.4 Config/ConfigurationManager.cs

### `static class ConfigurationManager`

#### 字段
- `public const string CONFIG_FILENAME = "config.json"`
- `public static ConfigurationSettings Settings { get; }`

#### 静态构造
- 读取 `<exe-dir>/config.json`，不存在则创建默认 `ConfigurationSettings { UseDarkTheme=false, UseCpp2Il=true }`

#### `static void SaveConfig()`
- **签名**：`public static void SaveConfig()`
- **位置**：`UABEAvalonia/Config/ConfigurationManager.cs:29`
- **可见性**：public static
- **副作用**：JSON 序列化 Settings 到磁盘
- **被调用**：ConfigurationSettings 属性 setter

### `class ConfigurationSettings`

#### 属性（带自动 SaveConfig）
- `bool UseDarkTheme { get; set; }` (`ConfigurationManager.cs:43`)
- `bool UseCpp2Il { get; set; }` (`ConfigurationManager.cs:54`)

---

## 8.5 关键调用栈

```
[打开 .bundle]
  → MainWindow.MenuOpen_Click
    → FileTypeDetector.DetectFileType
    → if BundleFile:
      → am.LoadBundleFile
      → LoadBundle(bundleInst) → Workspace.Files 填 UI
      → AskLoadCompressedBundle (if compressed)
```

```
[编辑 asset]
  → AssetDataTreeView.MenuEditAsset_Click
    → workspace.GetAssetContainer
    → win.ShowEditAssetWindow
      → EditDataWindow (Avalonia Edit)
      → AssetImportExport.ImportTextAsset
      → workspace.AddReplacer
        → ItemUpdated
      → InfoWindow.Workspace_ItemUpdated → 刷新 DataGrid
```