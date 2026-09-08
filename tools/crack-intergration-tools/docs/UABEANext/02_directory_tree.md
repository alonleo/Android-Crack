# 02 · UABEANext 目录树

## 2.1 顶层

```
UABEANext/
├── UABEANext4.sln
├── Directory.Build.props       # 全局 SDK 设置
├── .editorconfig
├── .gitignore
├── .gitmodules                 # 引用 AssetsTools.NET 子模块
├── license
├── readme.md
├── ReleaseFiles/               # classdata.tpk + icons_license.txt
├── Libraries/
│   └── AssetsTools.NET/        # Git submodule（可能空）
├── NativeLibs/
│   ├── win-x64/                # textureencoder.dll / cuttlefish.dll / PVRTexLib.dll
│   ├── linux-x64/              # libtextureencoder.so / libcuttlefish.so.2.10 / libPVRTexLib.so
├── UABEANext4/                 # 主 GUI 库
├── UABEANext4.Desktop/         # 桌面启动器
├── AudioPlugin/
├── FontPlugin/
├── MeshPlugin/
├── TextAssetPlugin/
├── TexturePlugin/
├── PluginPreviewer/            # 独立预览器库
└── PluginPreviewer.Desktop/    # 独立预览器桌面启动器
```

## 2.2 UABEANext4/ 主项目

```
UABEANext4/
├── UABEANext4.csproj
├── App.axaml                   # Avalonia 应用 XAML
├── App.axaml.cs                # Application 子类 + DI (67 LoC)
├── ViewLocator.cs              # VM→View 自动定位
├── Assets/                     # Avalonia 资源字典
│
├── AssetWorkspace/             # 工作区抽象
│   ├── AssetInst.cs            # AssetContainer 的升级版（继承 AssetFileInfo）
│   ├── ContainerTool.cs        # 容器工具类 (133 LoC)
│   ├── ContainerToolManager.cs # 容器工具管理 (97 LoC)
│   ├── DuplicateWorkspaceFileException.cs
│   ├── Workspace.cs            # 顶层 Workspace (630 LoC)
│   ├── Workspace.Saving.cs     # 保存逻辑 (416 LoC)
│   ├── WorkspaceItem.cs        # 树节点 (102 LoC)
│   └── WorkspaceItemType.cs    # enum
│
├── Controls/
│   ├── AssetDataTreeView.cs    # 类型树视图（UABEA 同款增强版）
│   └── MeshPreviewer/
│       ├── MeshPreviewerControl.cs
│       └── MeshPreviewerShaders.cs
│
├── Converters/                 # 6 个 IValueConverter
│   ├── AssetClassIDConverter.cs
│   ├── AssetsFileInstanceNameConverter.cs
│   ├── AssetTypeIconConverter.cs
│   ├── BitmapAssetValueConverter.cs
│   ├── RadioButtonValueConverter.cs
│   └── WsItemColorConverter.cs
│
├── Interfaces/
│   └── IDialogAware.cs         # 通用对话框接口
│
├── Logic/                      # 业务逻辑
│   ├── AssetInfo/              # 元信息
│   │   ├── BuildTarget.cs      # Unity BuildTarget 包装
│   │   ├── ExternalInfo.cs     # 外部依赖信息
│   │   ├── GeneralInfo.cs      # 文件通用信息
│   │   ├── ScriptInfo.cs       # MonoBehaviour 类型引用信息
│   │   ├── TypeTreeInfo.cs     # TypeTree 摘要
│   │   ├── TypeTreeNodeConverter.cs
│   │   ├── TypeTreeTypeInfo.cs
│   │   └── TypeTreeUINode.cs   # 类型树 UI 节点包装
│   ├── Configuration/          # 配置
│   │   ├── ConfigurationItem.cs
│   │   ├── ConfigurationManager.cs
│   │   ├── ConfigurationThemeType.cs
│   │   └── ConfigurationValues.cs
│   ├── DevTools/
│   │   └── DevToolsAdblock.cs
│   ├── Documents/
│   │   └── DocumentManager.cs  # Document dock 管理
│   ├── Hierarchy/
│   │   └── HierarchyItem.cs    # GameObject 层级
│   ├── ImportExport/
│   │   ├── AssetExport.cs      # .txt/.json 导出 (332)
│   │   └── AssetImport.cs      # .txt/.json 导入 (485)
│   ├── Mesh/                   # 网格结构
│   │   ├── Channel.cs          # 顶点属性 channel
│   │   ├── MeshEnums.cs        # Topology / Format 枚举
│   │   └── MeshObj.cs          # 内存网格表示
│   ├── Search/
│   │   ├── SearchLogic.cs      # 并发搜索
│   │   └── SearchResultItem.cs
│   └── Messages.cs             # WeakReferenceMessenger 消息类型
│
├── Plugins/                    # 插件系统
│   ├── IUavPluginFunctions.cs       # 主机能力 (13)
│   ├── IUavPluginOption.cs          # 菜单项 (14)
│   ├── IUavPluginPreviewer.cs       # 预览器 (12)
│   ├── IUavPluginPreviewerFunctions.cs
│   ├── PluginItemInfo.cs
│   ├── PluginLoadContext.cs         # AssemblyLoadContext 子类 (46)
│   ├── PluginLoader.cs              # 加载器 (125)
│   ├── PluginOptionModePair.cs
│   ├── PluginPreviewerTypePair.cs
│   ├── UavPluginFunctions.cs        # 默认实现 (58)
│   ├── UavPluginMode.cs             # 枚举
│   └── UavPluginPreviewerType.cs    # 枚举
│
├── Services/                   # 服务
│   ├── DialogService.cs
│   ├── DummyDialogService.cs
│   └── IDialogService.cs
│
├── Themes/                     # XAML 主题
│   ├── Accents/
│   │   ├── SimpleDark.axaml
│   │   ├── SimpleLight.axaml
│   │   └── SimpleShared.axaml
│   ├── ButtonStyle.axaml
│   ├── ComboBoxStyle.axaml
│   ├── DataGridStyle.axaml
│   ├── DataValidationStyle.axaml
│   ├── DockSimpleThemeEdit.axaml
│   ├── DockSimpleThemeEdit.cs
│   ├── HeaderedContentControlStyle.axaml
│   ├── ListBoxItemStyle.axaml
│   ├── NumericUpDownStyle.axaml
│   ├── RadioButtonListBoxStyle.axaml
│   ├── ScrollBarStyle.axaml
│   ├── SliderStyle.axaml
│   ├── TabStyle.axaml
│   ├── TextBoxStyle.axaml
│   └── TreeViewItemStyle.axaml
│
├── Util/                       # 工具
│   ├── ApplicationExtensions.cs
│   ├── AssetNamer.cs           # 命名助手 (407)
│   ├── DebounceUtils.cs
│   ├── FileDialogUtils.cs
│   ├── FileTypeDetector.cs     # magic sniff (67)
│   ├── FileUtils.cs
│   ├── GeneralExtensionUtils.cs
│   ├── MessageBoxUtil.cs
│   ├── ObservableCollectionExtensions.cs
│   ├── PathUtils.cs
│   ├── RangeObservableCollection.cs
│   ├── SearchUtils.cs
│   ├── SimpleObserver.cs
│   ├── StorageService.cs       # IStorageProvider 单例
│   └── WindowUtils.cs
│
├── ViewModels/                 # 所有 VM
│   ├── Dialogs/
│   │   ├── AddAssetViewModel.cs
│   │   ├── AddExternalViewModel.cs
│   │   ├── AssetDataSearchViewModel.cs
│   │   ├── AssetInfoViewModel.cs
│   │   ├── BatchImportViewModel.cs
│   │   ├── EditDataViewModel.cs
│   │   ├── MessageBoxViewModel.cs
│   │   ├── RenameFileViewModel.cs
│   │   ├── SelectDumpViewModel.cs
│   │   ├── SelectTypeFilterViewModel.cs
│   │   ├── SettingsViewModel.cs
│   │   └── VersionSelectViewModel.cs
│   ├── Documents/
│   │   ├── AssetDocumentViewModel.cs
│   │   └── BlankDocumentViewModel.cs
│   ├── Menu/
│   │   └── MenuOptionViewModel.cs
│   ├── Tools/
│   │   ├── HierarchyToolViewModel.cs
│   │   ├── ImagePreviewViewModel.cs
│   │   ├── InspectorToolViewModel.cs
│   │   ├── PreviewerToolViewModel.cs
│   │   └── WorkspaceExplorerToolViewModel.cs
│   ├── MainDockFactory.cs      # Dock 布局 (153)
│   ├── MainViewModel.cs        # 顶层 VM (851)
│   └── ViewModelBase.cs        # ObservableObject 子类
│
└── Views/                      # 所有视图（XAML + code-behind）
    ├── Dialogs/
    │   ├── AddAssetView.axaml(.cs)
    │   ├── AddExternalView.axaml(.cs)
    │   ├── AssetDataSearchView.axaml(.cs)
    │   ├── AssetInfoView.axaml(.cs)
    │   ├── BatchImportView.axaml(.cs)
    │   ├── EditDataView.axaml(.cs)
    │   ├── MessageBoxView.axaml(.cs)
    │   ├── RenameFileView.axaml(.cs)
    │   ├── SelectDumpView.axaml(.cs)
    │   ├── SelectTypeFilterView.axaml(.cs)
    │   ├── SettingsView.axaml(.cs)
    │   └── VersionSelectView.axaml(.cs)
    ├── Documents/
    │   ├── AssetDocumentView.axaml(.cs)
    │   └── BlankDocumentView.axaml(.cs)
    ├── Tools/
    │   ├── HierarchyToolView.axaml(.cs)
    │   ├── ImagePreviewView.axaml(.cs)
    │   ├── InspectorToolView.axaml(.cs)
    │   ├── MeshPreviewView.axaml(.cs)
    │   ├── PreviewerToolView.axaml(.cs)
    │   ├── TextPreviewView.axaml(.cs)
    │   └── WorkspaceExplorerToolView.axaml(.cs)
    ├── MainView.axaml(.cs)     # 主内容区（不含 Window）
    └── MainWindow.axaml(.cs)   # 主窗口壳
```

## 2.3 UABEANext4.Desktop/

```
UABEANext4.Desktop/
├── UABEANext4.Desktop.csproj
├── Program.cs                  # Main + Avalonia 启动
├── App.axaml(.cs)              # Application 派生
├── Window.axaml(.cs)           # 主 Window
└── app.manifest                # Windows manifest
```

## 2.4 TexturePlugin/

```
TexturePlugin/
├── TexturePlugin.csproj
├── EditTextureOption.cs        # Import action
├── ExportTextureOption.cs      # Export action (274)
├── ImportBatchTextureOption.cs # 批量导入 (117)
├── TexturePreviewer.cs         # 预览器 (55)
├── SpritePreviewer.cs          # Sprite 预览 (50)
├── Helpers/
│   ├── SpriteAtlasLookup.cs    # SpriteAtlas 解析
│   ├── TextureHelper.cs        # 通用工具
│   └── TextureLoader.cs        # Texture2D → Bitmap (413)
├── Logic/EditTexture/
│   ├── ColorSpace.cs           # enum
│   ├── FilterMode.cs           # enum
│   └── WrapMode.cs             # enum
├── ViewModels/
│   ├── EditTextureViewModel.cs
│   └── ExportBatchOptionsViewModel.cs
└── Views/
    ├── EditTextureView.axaml(.cs)
    └── ExportBatchOptionsView.axaml(.cs)
```

## 2.5 AudioPlugin/

```
AudioPlugin/
├── AudioPlugin.csproj
├── CompressionFormat.cs        # enum
└── ExportAudioOption.cs        # Export action (296)
```

## 2.6 FontPlugin/

```
FontPlugin/
├── FontPlugin.csproj
├── ExportFontOption.cs         # Export (123)
├── ImportFontOption.cs         # Import (154)
└── FontHelper.cs               # 工具
```

## 2.7 TextAssetPlugin/

```
TextAssetPlugin/
├── TextAssetPlugin.csproj
├── ExportTextAssetPlugin.cs    # Export (119)
├── ImportTextAssetPlugin.cs    # Import (139)
└── TextAssetPreviewer.cs       # Previewer (64)
```

## 2.8 MeshPlugin/

```
MeshPlugin/
├── MeshPlugin.csproj
└── MeshPreviewer.cs            # Live 3D 预览 (121)
```

## 2.9 PluginPreviewer/

```
PluginPreviewer/
├── PluginPreviewer.csproj
├── App.axaml(.cs)
├── ViewModels/
│   ├── MainViewModel.cs
│   └── ViewModelBase.cs
└── Views/
    ├── MainView.axaml(.cs)
    └── MainWindow.axaml(.cs)
```

## 2.10 PluginPreviewer.Desktop/

```
PluginPreviewer.Desktop/
├── PluginPreviewer.Desktop.csproj
├── Program.cs
├── App.axaml(.cs)
├── Window.axaml(.cs)
└── app.manifest
```

## 2.11 NativeLibs/

```
NativeLibs/
├── win-x64/
│   ├── textureencoder.dll       # Crunch + 纹理编码（推测）
│   ├── cuttlefish.dll           # Crunch 库
│   └── PVRTexLib.dll            # PVRTex
└── linux-x64/
    ├── libtextureencoder.so
    ├── libcuttlefish.so.2.10
    └── libPVRTexLib.so
```

## 2.12 关键文件统计

| 子目录 | 文件数 | 估算 LoC |
|---|---|---|
| UABEANext4/ | ~85 | ~5000 |
| UABEANext4.Desktop/ | 5 | ~200 |
| TexturePlugin/ | ~15 | ~1200 |
| AudioPlugin/ | 2 | ~320 |
| FontPlugin/ | 3 | ~290 |
| TextAssetPlugin/ | 3 | ~330 |
| MeshPlugin/ | 1 | ~130 |
| PluginPreviewer/ | 6 | ~400 |
| PluginPreviewer.Desktop/ | 5 | ~100 |
| **合计** | **~125** | **~8000** |