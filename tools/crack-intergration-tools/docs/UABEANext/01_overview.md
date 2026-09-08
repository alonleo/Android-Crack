# 01 · UABEANext 项目概览

## 1.1 基本属性

| 属性 | 值 |
|---|---|
| **项目名** | UABEANext (Unity Asset Bundle Extractor - Next generation) |
| **作者** | nesrak1 |
| **仓库** | github.com/nesrak1/UABEANext |
| **版本** | 主分支（`UABEANext4.sln`） |
| **语言** | C#（主体） + Vendored C++/原生（cuttlefish/PVRTexLib） |
| **GUI 框架** | Avalonia 11.3.8 + Dock.Avalonia 11.3.6.5 |
| **运行时** | .NET 8 |
| **MVVM** | CommunityToolkit.Mvvm 8.4.0 + DynamicData 9.4.1 |
| **DI** | Microsoft.Extensions.DependencyInjection 9.0.10 |
| **解析库** | AssetsTools.NET（vendored 在 `Libraries/AssetsTools.NET/` 子模块） |
| **构建** | `dotnet build`，无 AOT |
| **入口** | `UABEANext4.Desktop/UABEANext4.Desktop.exe` → `Program.cs` |
| **插件项目** | TexturePlugin, AudioPlugin, FontPlugin, MeshPlugin, TextAssetPlugin, PluginPreviewer, PluginPreviewer.Desktop |
| **原生依赖** | `NativeLibs/{win-x64,linux-x64}/` 含 textureencoder/cuttlefish/PVRTexLib |

## 1.2 项目定位

UABEANext 是 **UABEA 的后继版本**，主要改动：

1. **从单一主窗到 Dock 多面板**：Explorer / Hierarchy / Inspector / Previewer 四个 tool window 可拖拽停靠。
2. **从手写命令到 MVVM**：用 `[ObservableProperty]` + `[RelayCommand]` 生成代码。
3. **从 AssetWorkspace 树到 WorkspaceItem 树**：可同时打开多个 bundle / .assets，结构化在 `RootItems` 集合。
4. **从 Assembly.LoadFrom 到 AssemblyLoadContext**：插件相互隔离，可独立引用不同版本的 AssetsTools.NET。
5. **从 Avalonia.Controls.TreeView 到 AssetDataTreeView 强化**：节点懒加载 + 彩色 syntax 高亮。
6. **插件系统大扩展**：除 `IUavPluginOption`（菜单项）外，新增 `IUavPluginPreviewer`（实时预览）。
7. **独立 MeshPlugin + PluginPreviewer 进程**：3D 预览用 Silk.NET.OpenGL，跑在独立窗口。
8. **删除了 CLI 模式**：UABEANext 无 headless 入口，纯 GUI。

## 1.3 与 UABEA / AssetStudio 的关键区别

| 维度 | UABEA | UABEANext | AssetStudio (Razmoth) |
|---|---|---|---|
| UI 框架 | Avalonia 11 单主窗 | Avalonia 11 + Dock 多面板 | WinForms |
| MVVM | 无（直接事件） | CommunityToolkit.Mvvm | 无 |
| 插件加载 | `Assembly.LoadFrom` | `PluginLoadContext` 隔离 | 无 |
| 插件能力 | 仅菜单项 | 菜单项 + 实时预览器 | 无 |
| 多文件管理 | `BundleWorkspace` 单实例 | `WorkspaceItem` 树任意嵌套 | 列表 |
| 类型树编辑 | Avalonia.TreeView | AssetDataTreeView 强化版 | 无 |
| 类型树文本格式 | `.txt` + `.json` | `.txt` + `.json`（同一格式） | 无 |
| 3D 预览 | 无 | Silk.NET.OpenGL | OpenGL/DirectX 内置 |
| 多 bundle 同时打开 | 否（每次只能 1 个） | 是 | 是 |
| 文本资产搜索 | 通配符 | 增强（SearchLogic 多线程） | 按 type + container |
| Mesh 导入导出 | 无 | MeshPlugin 预览 | FBX 导出 |
| CLI 模式 | 有 (`batchexportbundle` 等) | 无 | `--game/--types/--map_op` |
| .emip mod | 第一类支持 | 移除（未实现） | 无 |
| SpriteAtlas 解析 | 无 | SpriteAtlasLookup | 简单 |
| 跨平台 native | 部分 | 全套 (win-x64/x86 + linux-x64/x86) | 仅 Windows |
| Avalonia 版本 | 11.0.1 | 11.3.8 | n/a |
| Dock 库 | 无 | Dock.Avalonia 11.3.6.5 | 无 |
| `PublishAot` | true | false（推测） | n/a |

## 1.4 核心抽象

### `Workspace`（`UABEANext4/AssetWorkspace/Workspace.cs`，630 LoC）
- 继承 `CommunityToolkit.Mvvm.ComponentModel.ObservableObject`
- 持有 `AssetsManager`, `PluginLoader`, `AssetNamer`
- `RootItems: ObservableCollection<WorkspaceItem>` —— 文件树根
- `ItemLookup: Dictionary<string, WorkspaceItem>` —— 名字索引
- `UnsavedItems / ModifiedItems: HashSet<WorkspaceItem>` —— 脏标记
- 关键方法：`LoadAnyFile / LoadBundle / LoadAssets / LoadResource / FixupAssetsFile / TryLoadClassDatabase / GetTemplateField / GetBaseField / Dirty / Close / CloseAll / Save / SaveAs / SaveAllAs`

### `WorkspaceItem`（`UABEANext4/AssetWorkspace/WorkspaceItem.cs`，102 LoC）
- 树节点，承载 1 个 `AssetsFileInstance` / `BundleFileInstance` / `AssetBundleDirectoryInfo`（resource） / Stream
- 字段：`Name`, `OriginalName`, `LoadIndex`, `Object`, `ObjectType`, `Parent`, `Children`

### `WorkspaceItemType` 枚举
- `AssetsFile`, `BundleFile`, `ResourceFile`

### `MainViewModel`（`UABEANext4/ViewModels/MainViewModel.cs`，851 LoC）
- 顶层 VM
- 持有 `Workspace`, `MainDockFactory`, 当前选中 asset 列表
- 订阅 `WeakReferenceMessenger`

### `MainDockFactory`（`UABEANext4/ViewModels/MainDockFactory.cs`，153 LoC）
- 用 `Dock.Avalonia` 构建 `IRootDock`
- 创建 4 个 tool：Explorer / Hierarchy / Inspector / Previewer

### `PluginLoader`（`UABEANext4/Plugins/PluginLoader.cs`，125 LoC）
- 用 `PluginLoadContext` 隔离加载插件
- `LoadPlugin(path) → bool`
- `LoadPluginsInDirectory(dir) → void`
- `GetOptionsThatSupport(workspace, assets, mode) → List<PluginOptionModePair>`
- `GetPreviewersThatSupport(workspace, asset) → List<PluginPreviewerTypePair>`

### `IUavPluginOption`
- 菜单项接口：`SupportsSelection / Execute(workspace, funcs, mode, selection)`
- 返回 `Task<bool>`

### `IUavPluginPreviewer`
- 预览接口：`SupportsPreview(workspace, asset) → UavPluginPreviewerType`
- 实际预览由 `PluginPreviewer` 进程通过进程间通信承担

### `IUavPluginFunctions`
- 主机提供给插件的能力：`ShowOpenFileDialog / ShowSaveFileDialog / ShowOpenFolderDialog / ShowDialog<T> / ShowMessageDialog`

## 1.5 主要模块摘要

| 模块 | 文件 | 责任 |
|---|---|---|
| Entry | `UABEANext4.Desktop/Program.cs` | Avalonia 桌面启动 |
| App | `UABEANext4/App.axaml.cs` (67) | MVVM DI 注册 |
| AssetWorkspace | `UABEANext4/AssetWorkspace/*` (~1200 LoC) | 文件加载、保存、查询 |
| ViewModels | `UABEANext4/ViewModels/*` (~1500 LoC) | 所有 VM |
| Views | `UABEANext4/Views/*` (~700 LoC XAML) | 所有视图 |
| Logic/AssetInfo | `UABEANext4/Logic/AssetInfo/*` | GeneralInfo / TypeTreeInfo / ExternalInfo / ScriptInfo / BuildTarget |
| Logic/Configuration | `UABEANext4/Logic/Configuration/*` | ConfigurationManager + Theme + Values |
| Logic/ImportExport | `UABEANext4/Logic/ImportExport/*` (~820 LoC) | 类型树 .txt / .json |
| Logic/Mesh | `UABEANext4/Logic/Mesh/*` | MeshObj / Channel / Enums |
| Logic/Search | `UABEANext4/Logic/Search/*` | SearchLogic (并发) |
| Logic/Hierarchy | `UABEANext4/Logic/Hierarchy/*` | GameObject 层级遍历 |
| Plugins | `UABEANext4/Plugins/*` (~300 LoC) | 插件宿主 |
| Util | `UABEANext4/Util/*` (~700 LoC) | 工具：AssetNamer 等 |
| Services | `UABEANext4/Services/*` | DialogService |
| Controls | `UABEANext4/Controls/*` | AssetDataTreeView + MeshPreviewer |
| Converters | `UABEANext4/Converters/*` | 6 个 IValueConverter |
| Themes | `UABEANext4/Themes/*` | 主题 XAML |
| TexturePlugin | `TexturePlugin/*` | Texture 编解码 + Edit/Sprite |
| AudioPlugin | `AudioPlugin/*` | Fmod5Sharp 导出 |
| FontPlugin | `FontPlugin/*` | .ttf/.otf 导入导出 |
| TextAssetPlugin | `TextAssetPlugin/*` | TextAsset 导入导出 + Previewer |
| MeshPlugin | `MeshPlugin/*` | Mesh 预览器 |
| PluginPreviewer | `PluginPreviewer/*` + `.Desktop` | 独立预览窗口 |
| NativeLibs | `NativeLibs/{win-x64,linux-x64}/*` | 跨平台 native |

## 1.6 技术栈

- **GUI**: Avalonia 11.3.8 + Dock.Avalonia 11.3.6.5 + Dock.Model.Mvvm + Dock.Model
- **MVVM**: CommunityToolkit.Mvvm 8.4.0 + DynamicData 9.4.1
- **DI**: Microsoft.Extensions.DependencyInjection 9.0.10
- **图像**: SixLabors.ImageSharp（推测）+ StbImageSharp 2.30.15 + StbImageWriteSharp 1.16.7
- **3D**: Silk.NET.OpenGL 2.22.0
- **音频**: Fmod5Sharp 3.0.1
- **Cpp2IL**: Samboy063.LibCpp2IL 2022.1.0-pre-release.21
- **Cecil**: Mono.Cecil 0.11.3
- **JSON**: Newtonsoft.Json 13.0.3
- **解码**: AssetRipper.TextureDecoder 2.1.1
- **Vendored AssetsTools.NET**: `Libraries/AssetsTools.NET/`（子模块）

## 1.7 适用场景

- 与 UABEA 相同（asset 级反向工程），但 UI 更现代、插件隔离更强、可同时打开多个文件
- 需要 3D 预览（MeshPlugin + Silk.NET）
- 需要更精细的 SpriteAtlas 解析
- 想要 MVVM 架构的工作流自动化

## 1.8 不适用场景

- CLI 批处理（UABEANext 没有命令行）
- 跨 .emip mod 分发（仅 UABEA 支持）
- 极简 UI（UABEA 更轻量）