# UABEA (UABE Avalonia) 文档

> nesrak1 原版 `UABE Avalonia` —— 基于 Avalonia 11 + .NET 8 的 Unity Asset Bundle Extractor 跨平台 GUI / CLI 重写版

## 导航

| 章节 | 主题 |
|---|---|
| [01_overview.md](01_overview.md) | 项目定位、版本、技术栈、与 UABE 经典版 / AssetStudio 的区别 |
| [02_directory_tree.md](02_directory_tree.md) | 完整目录树 + 注释 |
| [03_architecture.md](03_architecture.md) | 整体架构 + 模块依赖 mermaid 图 |
| [04_data_flow.md](04_data_flow.md) | 核心数据结构 + 数据流 mermaid |
| [05_operation_chains.md](05_operation_chains.md) | 主要操作链（≥7 条），含时序图 / 流程图 |
| [06_build_and_run.md](06_build_and_run.md) | 编译、运行、CLI 参数、插件加载 |
| [07_functions_index.md](07_functions_index.md) | 公共/内部函数索引表 |
| [08_functions_detail/](08_functions_detail/) | 各模块函数详细说明 |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表 |

## 章节子目录

```
08_functions_detail/
├── main_window.md           MainWindow.axaml.cs (1026 LoC) 主窗体代码后置
├── program_and_cli.md       Program.cs + CommandLineHandler.cs
├── workspace.md             Workspace/*  (Asset/Bundle/Unity/Container)
├── logic.md                 Logic/*  (AssetImportExport/Emip/FileTypeDetector/AssetBundleUtil)
├── plugins.md               Plugins/*  插件系统
├── config.md                Config/*  ConfigurationManager
├── utils.md                 Utils/*  工具类
├── forms.md                 Forms/*  17 个 .axaml 窗口
├── controls.md              Controls/* 自定义控件
├── texture_plugin.md        TexturePlugin/*  编解码 / Switch deswizzle / Crunch
├── audio_plugin.md          AudioClipPlugin/*  FMOD5 音频导出
├── font_plugin.md           FontPlugin/*  .ttf/.otf 导入导出
└── text_asset_plugin.md     TextAssetPlugin/*  TextAsset 导入导出
```

## 一句话总结

UABEA = Avalonia GUI（MainWindow）+ CLI（CommandLineHandler）+ Plugin System（UABEAPlugin），基于 nesrak1 自家的 AssetsTools.NET 库读写 Unity Asset 文件；附四个官方插件（Texture / AudioClip / Font / TextAsset）；支持 .emip mod 包导入应用；提供 batchexportbundle / batchimportbundle / applyemip 三个无头 CLI 模式。