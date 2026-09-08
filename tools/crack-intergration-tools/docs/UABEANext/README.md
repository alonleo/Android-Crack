# UABEANext 文档

> nesrak1 新版（UABEANext4）—— 基于 Avalonia 11 + Dock.Avalonia + CommunityToolkit.Mvvm 的 Unity Asset 编辑器

## 导航

| 章节 | 主题 |
|---|---|
| [01_overview.md](01_overview.md) | 项目定位、版本、技术栈、与 UABEA / AssetStudio 的区别 |
| [02_directory_tree.md](02_directory_tree.md) | 完整目录树 + 注释 |
| [03_architecture.md](03_architecture.md) | 整体架构 + Dock + MVVM + 插件系统 mermaid |
| [04_data_flow.md](04_data_flow.md) | 核心数据结构 + WorkspaceItem + 数据流 |
| [05_operation_chains.md](05_operation_chains.md) | 主要操作链（≥10 条），含 mermaid |
| [06_build_and_run.md](06_build_and_run.md) | 编译、运行、插件加载 |
| [07_functions_index.md](07_functions_index.md) | 公共/内部函数索引表（≥300 行） |
| [08_functions_detail/](08_functions_detail/) | 各模块函数详细说明 |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表 |

## 章节子目录

```
08_functions_detail/
├── entry_programs.md       UABEANext4.Desktop/Program.cs + UABEANext4/App.axaml.cs
├── workspace.md            Workspace.cs + Workspace.Saving.cs + WorkspaceItem + AssetInst
├── viewmodels.md           MainViewModel + MainDockFactory + 对话框/文档/工具 VM
├── views.md                MainView + MainWindow + 对话框/工具 .axaml
├── plugins.md              PluginLoader + PluginLoadContext + IUavPlugin* + UavPluginFunctions
├── import_export.md        AssetImport + AssetExport
├── asset_info.md           TypeTreeInfo / ScriptInfo / ExternalInfo / GeneralInfo / BuildTarget
├── mesh.md                 Logic/Mesh/* (MeshObj / MeshEnums / Channel)
├── search.md               SearchLogic + SearchResultItem
├── converters.md           6 个 IValueConverter
├── util.md                 AssetNamer + FileTypeDetector + GeneralExtensionUtils + ...
├── services.md             DialogService + IDialogService + DummyDialogService
├── texture_plugin.md       TexturePlugin/* (TextureLoader, EditTexture, SpriteAtlas...)
├── audio_plugin.md         AudioPlugin/ExportAudioOption
├── font_plugin.md          FontPlugin/*
├── text_asset_plugin.md    TextAssetPlugin/*
├── mesh_plugin.md          MeshPlugin/MeshPreviewer
├── plugin_previewer.md     PluginPreviewer + PluginPreviewer.Desktop
└── native_libs.md          NativeLibs/* side-cars
```

## 一句话总结

UABEANext = Avalonia Dock UI + MVVM (CommunityToolkit.Mvvm) + PluginLoader (AssemblyLoadContext 隔离) + Workspace (Observability + 多 bundle 文件管理) + 7 个插件（Texture / Audio / Font / Mesh / TextAsset / Sprite Previewer / Mesh Previewer）+ 自带 Silk.NET 3D Mesh 预览窗口。**与 UABEA 的核心区别**：MVVM、docking、插件加载隔离、无 CLI 批处理。