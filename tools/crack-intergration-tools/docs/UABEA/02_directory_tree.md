# 02 · UABEA 目录树

## 2.1 顶层

```
UABEA/
├── UABEAvalonia.sln          # 解决方案
├── readme.md                 # 项目说明
├── license                   # MIT-like
├── .gitignore
├── .github/                  # GitHub Actions（CI）
├── Libs/                     # 预编译 AssetsTools.NET DLLs
│   ├── AssetsTools.NET.dll
│   ├── AssetsTools.NET.Cpp2IL.dll
│   ├── AssetsTools.NET.MonoCecil.dll
│   ├── AssetsTools.NET.Texture.dll
│   └── *.deps.json
├── ReleaseFiles/             # 发布时携带的资源
│   ├── classdata.tpk
│   └── icons_license.txt
├── TexToolWrap/              # C++ 封装（生成 textoolwrap.dll）
├── UABEAvalonia/             # 主 GUI + CLI
├── TexturePlugin/            # Texture2D 编解码插件
├── TexturePluginPreview/     # 独立预览器原型
├── AudioClipPlugin/          # FMOD5 音频导出插件
├── FontPlugin/               # .ttf/.otf 导入导出插件
└── TextAssetPlugin/          # TextAsset 导入导出插件
```

## 2.2 UABEAvalonia/ 主项目

```
UABEAvalonia/
├── UABEAvalonia.csproj       # csproj，含 <EnableDynamicLoading>true</EnableDynamicLoading>
├── nuget.config
├── uabeavalonia.ico          # 图标
├── App.axaml                 # Avalonia 应用根样式
├── App.axaml.cs              # Avalonia.Application 初始化 (26 LoC)
├── Program.cs                # 入口 + 异常处理 + Avalonia 配置 (84 LoC)
├── CommandLineHandler.cs     # CLI: batchexportbundle/importbundle/applyemip (373 LoC)
├── ThemeHandler.cs           # 浅/深色 + Fluent/Simple 主题切换
│
├── Assets/                   # Avalonia 资源字典
├── Grammars/                 # TextMate 语法 (UABEDump.tmLanguage.json)
├── Styles/                   # 自定义控件样式
│   ├── ExtendedControlStyles.axaml
│   ├── ImprovedHeaderedContentControlStyles.axaml
│   └── ImprovedTabStyles.axaml
├── TextHighlighting/
│   └── UABEDumpRegistryOptions.cs   # TypeTree .txt 高亮注册
│
├── Config/
│   └── ConfigurationManager.cs (64) # config.json 持久化
│
├── Controls/
│   └── AssetDataTreeView.cs (575)   # TypeTree 树视图（懒加载）
│
├── Forms/                    # 17 个窗口/对话框
│   ├── MainWindow.axaml(.cs)        # 主窗体 (1026 LoC)
│   ├── InfoWindow.axaml(.cs)        # asset 信息/编辑窗
│   ├── DataWindow.axaml(.cs)
│   ├── EditDataWindow.axaml(.cs)
│   ├── About.axaml(.cs)
│   ├── AddAssetWindow.axaml(.cs)
│   ├── AddDependencyWindow.axaml(.cs)
│   ├── ExportBatchChooseTypeDialog.axaml(.cs)
│   ├── FilterAssetTypeDialog.axaml(.cs)
│   ├── GameObjectViewWindow.axaml(.cs)
│   ├── GoToAssetDialog.axaml(.cs)
│   ├── ImportBatch.axaml(.cs)
│   ├── ImportSerializedDialog.axaml(.cs)
│   ├── LoadModPackageDialog.axaml(.cs)
│   ├── ModMakerDialog.axaml(.cs)
│   ├── PluginWindow.axaml(.cs)
│   ├── ProgressWindow.axaml(.cs)
│   ├── RenameWindow.axaml(.cs)
│   ├── SearchDialog.axaml(.cs)
│   ├── SelectDumpWindow.axaml(.cs)
│   ├── VersionWindow.axaml(.cs)
│   ├── AssetTypeIconConverter.cs    # IValueConverter
│   └── AssetsFileInfo/              # 多 Tab 信息窗子视图
│       ├── AssetsFileInfoWindow.axaml
│       ├── AssetsFileInfoWindow.axaml.cs
│       ├── AssetsFileInfoWindow.Deps.axaml.cs
│       ├── AssetsFileInfoWindow.Header.axaml.cs
│       ├── AssetsFileInfoWindow.Script.axaml.cs
│       └── AssetsFileInfoWindow.TypeTree.axaml.cs
│
├── Logic/                    # 业务逻辑层
│   ├── AssetImportExport.cs (719)   # raw/text/json dump 与 import
│   ├── AssetBundleUtil.cs (20)      # IsBundleDataCompressed 检查
│   ├── Emip.cs (230)                # InstallerPackageFile 读写
│   └── FileTypeDetector.cs (68)     # magic sniff
│
├── Plugins/                  # 插件系统
│   ├── PluginManager.cs (80)        # Assembly.LoadFrom + 收集 UABEAPlugin
│   ├── UABEAPlugin.cs               # interface
│   ├── UABEAPluginAction.cs         # enum (Import/Export/Console/Create/All)
│   ├── UABEAPluginOption.cs         # interface
│   ├── UABEAPluginMenuInfo.cs       # 菜单项数据
│   └── PluginInfo.cs                # PluginInfo { name, options }
│
├── Utils/                    # 工具
│   ├── AssetNameUtils.cs
│   ├── FileDialogUtils.cs
│   ├── FileUtils.cs
│   ├── PathUtils.cs
│   ├── SearchUtils.cs
│   └── MessageBox/
│       ├── MessageBox.axaml(.cs)
│       └── MessageBoxUtil.cs
│
└── Workspace/                # 工作区
    ├── AssetWorkspace.cs (436)      # 资产管理（NewAssets/Replacer/Removed）
    ├── BundleWorkspace.cs (203)     # Bundle 项管理（Items/FileLookup）
    ├── UnityContainer.cs (213)      # AssetBundle/ResourceManager 容器查找
    ├── AssetContainer.cs (110)      # 单个 asset 包装（含 BaseValueField）
    └── AssetsFileChangeTypes.cs (14)# enum (None/Dependencies)
```

## 2.3 TexturePlugin/

```
TexturePlugin/
├── TexturePlugin.csproj
├── Program.cs (33)                       # UABEAPlugin.Init() 注册三个 Option
├── EditTextureOption.cs (54)             # Import action：编辑对话框
├── ExportTextureOption.cs (186)          # Export action：单 + 批量导出 PNG/TGA
├── ImportTextureOption.cs (160)          # Import action：批量导入 PNG/TGA
├── EditDialog.axaml(.cs) (258)           # EditDialog UI
├── TextureEncoderDecoder.cs (558)        # Encode/Decode 主入口
├── Texture2DSwitchDeswizzler.cs (195)    # Switch GOB swizzle/unswizzle
├── TextureHelper.cs (124)                # 公共工具：byte array、resS、Po2
├── TextureImportExport.cs (172)          # Import()/Export() 主入口
└── PInvoke.cs (30)                       # 6 个 [DllImport("textoolwrap")]
```

## 2.4 TexToolWrap/ (C++ 包装)

```
TexToolWrap/
├── TexToolWrap.vcxproj
├── textoolwrap.cpp                        # 5 个 C 导出函数
├── crunch/                                # Crunch 源码
├── ispc/                                  # ISPC TextureCompressor
└── PVRTexLib/                             # PVRTexLib 头与库
```

## 2.5 TexturePluginPreview/

```
TexturePluginPreview/
├── TexturePluginPreview.csproj
├── Program.cs (22)                        # 独立 Avalonia 启动
├── App.axaml(.cs)
└── MainWindow.axaml(.cs)                  # 独立预览窗口（早期原型）
```

## 2.6 AudioClipPlugin/

```
AudioClipPlugin/
├── AudioClipPlugin.csproj
└── Program.cs (292)                       # 一个文件，含 enum + ExportAudioClipOption + Plugin
```

## 2.7 FontPlugin/

```
FontPlugin/
├── FontPlugin.csproj
└── Program.cs (252)                       # FontHelper + ImportFontOption + ExportFontOption + Plugin
```

## 2.8 TextAssetPlugin/

```
TextAssetPlugin/
├── TextAssetPlugin.csproj
└── Program.cs (252)                       # TextAssetHelper + Import/Export TextAssetOption + Plugin
```

## 2.9 关键非源文件

| 路径 | 用途 |
|---|---|
| `Libs/AssetsTools.NET*.dll` | vendored nesrak1/AssetsTools.NET 编译产物 |
| `ReleaseFiles/classdata.tpk` | 默认 Class Database（运行时由 `Manager.LoadClassPackage` 加载） |
| `TexToolWrap/textoolwrap.dll` | C++ 端构建产物，被 TexturePlugin 加载 |
| `UABEAvalonia/Assets/` | Avalonia XAML 资源 |
| `UABEAvalonia/Grammars/` | TextMate .tmLanguage 语法 JSON（TypeTree 高亮） |
| `UABEAvalonia/uabeavalonia.ico` | Windows 图标 |