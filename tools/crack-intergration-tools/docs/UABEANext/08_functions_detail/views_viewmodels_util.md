# 08 · ViewModels / Views / Converters / Util / Services

## 1. ViewModels/

### 1.1 MainViewModel.cs (851 LoC)

`class MainViewModel : ViewModelBase`

#### 字段（自动生成 property）
- `Workspace Workspace`
- `MainDockFactory Factory`
- `IDialogService DialogService`
- `IStorageService StorageService`
- `IReadOnlyList<WorkspaceItem> SelectedItems`

#### 命令
- `RelayCommand OpenFileCommand`
- `RelayCommand CloseFileCommand`
- `RelayCommand SaveCommand`
- `RelayCommand SaveAsCommand`
- `RelayCommand SaveAllCommand`
- `RelayCommand OpenDirectoryCommand`

#### 主要方法
- `void OpenFileAsync()` —— 弹文件对话框 → `workspace.LoadAnyFile`
- `void CloseFileAsync(WorkspaceItem)` —— 调 `workspace.Close`
- `Task SaveAsync(WorkspaceItem)` —— 调 `workspace.Save`
- `Task SaveAsAsync(WorkspaceItem)` —— 调 `workspace.SaveAs`
- `Task SaveAllAsync()` —— 调 `workspace.SaveAllAs`
- `void OnWorkspaceItemChanged(...)` —— 响应 ItemUpdated

#### 消息订阅
- 通过 `WeakReferenceMessenger.Default.Register<T>(this, ...)` 订阅：
  - `SelectedWorkspaceItemChangedMessage`
  - `RequestEditAssetMessage`
  - `RequestCloseFileMessage`
  - `RequestVisitAssetMessage`
  - `FileLoadedMessage`

### 1.2 MainDockFactory.cs (153 LoC)

`class MainDockFactory : IDockFactory`

#### `IRootDock BuildDock()`
- **签名**：`public IRootDock BuildDock()`
- **位置**：`MainDockFactory.cs`
- **可见性**：public
- **算法**：
  1. 创建 RootDock
  2. 创建 4 个 Tool Dockable：WorkspaceExplorer / Hierarchy / Inspector / Previewer
  3. 创建初始 Document
  4. 用 DockLayout 配置布局

### 1.3 ViewModelBase.cs

`class ViewModelBase : ObservableObject`
- 公共基类，可被 VM 继承

### 1.4 Tools/

| VM | 文件 |
|---|---|
| `class WorkspaceExplorerToolViewModel` | `Tools/WorkspaceExplorerToolViewModel.cs` |
| `class HierarchyToolViewModel` | `Tools/HierarchyToolViewModel.cs` |
| `class InspectorToolViewModel` | `Tools/InspectorToolViewModel.cs` |
| `class PreviewerToolViewModel` | `Tools/PreviewerToolViewModel.cs` |
| `class ImagePreviewViewModel` | `Tools/ImagePreviewViewModel.cs` |

每个含：
- `[ObservableProperty]` 字段
- `[RelayCommand]` 命令
- 消息订阅
- 选中状态管理

### 1.5 Documents/

| VM | 文件 |
|---|---|
| `class AssetDocumentViewModel` | `Documents/AssetDocumentViewModel.cs` |
| `class BlankDocumentViewModel` | `Documents/BlankDocumentViewModel.cs` |

AssetDocumentViewModel 主要字段：
- `WorkspaceItem Item`
- `AssetInst? SelectedAsset`
- `AssetTypeValueField? BaseField`
- `IList<AssetInst> Assets`
- 选中变化时通过消息广播

### 1.6 Dialogs/ (12 个 VM)

| VM | 用途 |
|---|---|
| `AddAssetViewModel` | 新增 asset |
| `AddExternalViewModel` | 添加外部依赖 |
| `AssetDataSearchViewModel` | 资产数据搜索 |
| `AssetInfoViewModel` | asset 元信息 |
| `BatchImportViewModel` | 批量导入映射 |
| `EditDataViewModel` | 编辑字节 |
| `MessageBoxViewModel` | 消息对话框 |
| `RenameFileViewModel` | 重命名文件 |
| `SelectDumpViewModel` | 选择 dump 工具输出 |
| `SelectTypeFilterViewModel` | 类型过滤 |
| `SettingsViewModel` | 设置 |
| `VersionSelectViewModel` | Unity version 选择 |

### 1.7 Menu/MenuOptionViewModel.cs
- 菜单项 VM

---

## 2. Views/

### 2.1 MainView / MainWindow

`MainWindow.axaml(.cs)`：
- 主窗口壳
- Content = MainView

`MainView.axaml(.cs)`：
- 主内容区（含 Dock）

### 2.2 Dialogs/ (12 个 view)

每个 Dialog 对应一个 Dialog VM。.axaml 包含 UI 元素 + `DataContext = VM`。

### 2.3 Documents/ (2 个 view)

`AssetDocumentView.axaml(.cs)` —— 单个 asset 的"文档"视图
`BlankDocumentView.axaml(.cs)` —— 占位文档

### 2.4 Tools/ (7 个 view)

| View | 文件 | 用途 |
|---|---|---|
| `HierarchyToolView` | `Tools/HierarchyToolView.axaml(.cs)` | GameObject 层级 |
| `ImagePreviewView` | `Tools/ImagePreviewView.axaml(.cs)` | 图片预览 |
| `InspectorToolView` | `Tools/InspectorToolView.axaml(.cs)` | Inspector（字段树） |
| `MeshPreviewView` | `Tools/MeshPreviewView.axaml(.cs)` | Mesh 预览 |
| `PreviewerToolView` | `Tools/PreviewerToolView.axaml(.cs)` | 预览器容器 |
| `TextPreviewView` | `Tools/TextPreviewView.axaml(.cs)` | 文本预览 |
| `WorkspaceExplorerToolView` | `Tools/WorkspaceExplorerToolView.axaml(.cs)` | Workspace 树 |

---

## 3. Converters/ (6 个 IValueConverter)

| 类 | 位置 | 用途 |
|---|---|---|
| `AssetClassIDConverter` | `AssetClassIDConverter.cs` | AssetClassID → 字符串 |
| `AssetsFileInstanceNameConverter` | `AssetsFileInstanceNameConverter.cs` | AssetsFileInstance → 显示名 |
| `AssetTypeIconConverter` | `AssetTypeIconConverter.cs` | AssetClassID → Bitmap 图标 |
| `BitmapAssetValueConverter` | `BitmapAssetValueConverter.cs` | AssetTypeValueField → Bitmap |
| `RadioButtonValueConverter` | `RadioButtonValueConverter.cs` | 单选按钮值转换 |
| `WsItemColorConverter` | `WsItemColorConverter.cs` | WorkspaceItem → 颜色 |

每个含 `Convert` + `ConvertBack` 两个公共方法。

---

## 4. Util/

### AssetNamer.cs (407 LoC)

`class AssetNamer`

#### 字段
- `private readonly Workspace _workspace`
- `private readonly ConcurrentDictionary<AssetsFileInstance, NameReadOptimization> _gameObjectNro`
- `private readonly ConcurrentDictionary<AssetsFileInstance, NameReadOptimization> _monoBehaviourNro`

#### `AssetNamer(Workspace workspace)`
- **签名**：`public AssetNamer(Workspace workspace)`
- **位置**：`AssetNamer.cs:18`

#### `string? GetAssetName(AssetInst asset, bool usePrefix, int maxLen)`
- **位置**：`AssetNamer.cs:23`
- **返回值**：可空（无 name）

#### `string GetAssetTypeName(AssetInst asset, bool usePrefix, int maxLen)`
- **位置**：`AssetNamer.cs:29`

#### `void GetDisplayName(AssetInst asset, bool usePrefix, int maxLen, out string? assetName, out string typeName)`
- **位置**：`AssetNamer.cs:35`
- **可见性**：public
- **算法**：
  - 若是 GameObject → 取 m_Name
  - 若是 MonoBehaviour → 取 m_Name 或 MonoScript 类名
  - 兜底 → TypeName + PathId

#### `string GetMonoBehaviourNameFast(AssetInst asset)`
- **位置**：`AssetNamer.cs:229`

#### `static string GetFallbackName(AssetInst asset, string? name)`
- **位置**：`AssetNamer.cs:270`

#### `static string GetAssetFileName(Workspace, AssetInst, string, int, bool)`
- **位置**：`AssetNamer.cs:275`

#### `static string GetAssetFileName(AssetInst, string, string, bool)`
- **位置**：`AssetNamer.cs:285`

#### `static void GetLockObjAndReader(...)`
- **位置**：`AssetNamer.cs:293`
- **可见性**：private static

#### `static NameReadOptimization GetGameObjectNro(AssetTypeTemplateField)`
- **位置**：`AssetNamer.cs:314`

#### `static NameReadOptimization GetMonoBehaviourNro(AssetTypeTemplateField)`
- **位置**：`AssetNamer.cs:371`

#### `static void TrimAssetName(ref string name, int maxLen)`
- **位置**：`AssetNamer.cs:418`

### FileTypeDetector.cs (67 LoC)

`static class FileTypeDetector`

#### `DetectedFileType DetectFileType(string filePath)`
- **位置**：`FileTypeDetector.cs:9`

#### `DetectedFileType DetectFileType(AssetsFileReader r, long startAddress)`
- **位置**：`FileTypeDetector.cs:18`

### 其他工具

| 类 | 文件 | 用途 |
|---|---|---|
| `static class PathUtils` | `PathUtils.cs` | 路径处理 |
| `static class FileUtils` | `FileUtils.cs` | 文件 IO |
| `static class SearchUtils` | `SearchUtils.cs` | 搜索工具 |
| `static class FileDialogUtils` | `FileDialogUtils.cs` | 文件对话框 |
| `static class MessageBoxUtil` | `MessageBoxUtil.cs` | 弹窗 |
| `static class WindowUtils` | `WindowUtils.cs` | 窗口工具 |
| `static class StorageService` | `StorageService.cs` | 单例 IStorageProvider |
| `static class SimpleObserver` | `SimpleObserver.cs` | Reactive 工具 |
| `static class ObservableCollectionExtensions` | `ObservableCollectionExtensions.cs` | 集合扩展 |
| `static class RangeObservableCollection<T>` | `RangeObservableCollection.cs` | 自定义 Observable |
| `static class DebounceUtils` | `DebounceUtils.cs` | 防抖 |
| `static class ApplicationExtensions` | `ApplicationExtensions.cs` | 应用扩展 |
| `static class GeneralExtensionUtils` | `GeneralExtensionUtils.cs` | 通用扩展 |

---

## 5. Services/

### IDialogService.cs

`interface IDialogService`
- `Task ShowMessageAsync(string title, string message)`
- `Task<bool> ShowConfirmAsync(string title, string message)`
- `Task<T?> ShowDialogAsync<T>(IDialogAware<T> dialog)`
- `Task<string?> ShowOpenFileAsync(...)`
- `Task<string?> ShowSaveFileAsync(...)`

### DialogService.cs

`class DialogService : IDialogService`

### DummyDialogService.cs

`class DummyDialogService : IDialogService`
- 测试桩，返回默认值

---

## 6. Themes/ (Avalonia XAML 主题)

### Accents/
- `SimpleDark.axaml`
- `SimpleLight.axaml`
- `SimpleShared.axaml`

### 各控件样式
- `ButtonStyle.axaml`
- `ComboBoxStyle.axaml`
- `DataGridStyle.axaml`
- `DataValidationStyle.axaml`
- `DockSimpleThemeEdit.axaml(.cs)`
- `HeaderedContentControlStyle.axaml`
- `ListBoxItemStyle.axaml`
- `NumericUpDownStyle.axaml`
- `RadioButtonListBoxStyle.axaml`
- `ScrollBarStyle.axaml`
- `SliderStyle.axaml`
- `TabStyle.axaml`
- `TextBoxStyle.axaml`
- `TreeViewItemStyle.axaml`

通过 `App.axaml.cs` 中的 `<Application.Styles>` 引入。