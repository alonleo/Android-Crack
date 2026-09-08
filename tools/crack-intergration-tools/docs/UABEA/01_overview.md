# 01 · UABEA 项目概览

## 1.1 基本属性

| 属性 | 值 |
|---|---|
| **项目名** | UABEA (Unity Asset Bundle Extractor for Avalonia) |
| **作者** | nesrak1 |
| **仓库** | github.com/nesrak1/UABEAvalonia |
| **版本** | 主分支（`UABEAvalonia.sln`） |
| **语言** | C# 主体 + C++ 包装（TexToolWrap） |
| **GUI 框架** | Avalonia 11.0.1 |
| **运行时** | .NET 8 (`net8.0`) |
| **解析库** | AssetsTools.NET（vendored in `Libs/`，含 Texture/Cpp2IL/MonoCecil 子 DLL） |
| **构建** | `dotnet build` / MSBuild；`PublishAot=true` |
| **入口** | `UABEAvalonia/UABEAvalonia.csproj` → `UABEAvalonia.exe` |
| **子项目** | `TexturePlugin`, `TexturePluginPreview`, `TexToolWrap`, `TextAssetPlugin`, `AudioClipPlugin`, `FontPlugin` |

## 1.2 项目定位

UABEA 是 **Unity 资产包级** 的反向工程 / 修改工具，定位介于"原始字节级编辑"（010 Editor）和"完整场景导出"（AssetStudio）之间：

- 它只关心 `.assets` 和 `.bundle` 文件，不做 FBX / GLTF 之类的格式转换。
- 它把每个 asset 表示为 TypeTree 树（与 Unity Editor 内部的 SerializedObject 同构），通过插件可以批量导出 / 替换。
- 它提供 `.emip` mod 包格式，便于分发"只改一个 Texture2D"的小型补丁。

## 1.3 与经典 UABE / AssetStudio / UABEANext 的区别

| 维度 | UABE (经典 WinForms) | UABEA | AssetStudio (Razmoth) | UABEANext |
|---|---|---|---|---|
| 平台 | Windows only | 跨平台 Avalonia | WinForms | 跨平台 Avalonia + Dock |
| 解析库 | AssetsTools.NET 经典 | AssetsTools.NET (vendored) | 自研 + 38 款游戏特殊解密 | AssetsTools.NET (vendored) |
| 多 bundle 文件 | 部分支持 | `BundleWorkspace` 多文件 | 友好 | `WorkspaceItem` 树 |
| 插件架构 | 无（官方闭源） | `UABEAPlugin` + `Assembly.LoadFrom` | 无 | `IUavPluginOption` + `AssemblyLoadContext` |
| 3D 预览 | 无 | 无 | OpenGL / DirectX 内置 | Silk.NET (MeshPreviewer) |
| CLI 批处理 | 无 | 有 (`batchexportbundle` 等) | `--game`/`--map_op`/`--types` 复杂 | 无 |
| .emip mod | 无 | 第一类支持 | 无 | 无（保留设计但未实现） |
| Crash 处理 | Windows 弹窗 | `uabeacrash.log` + mshta | 简单 | `uabeacrash.log` |
| 类型树写入 | 仅 dump/import .txt | `.txt` + `.json` | n/a | `.txt` + `.json` |
| 跨文件资源 | resS | resS (TextureHelper / AudioClip) | 内置 | resS (TextureLoader) |
| Switch 平台 | 不支持 | `Texture2DSwitchDeswizzler` | n/a | n/a |
| Crunch 压缩 | 不支持 | `PInvoke.EncodeByCrunchUnity` | 不支持 | n/a |

## 1.4 核心抽象

### `AssetsManager`
来自 AssetsTools.NET 库。封装 `BundleFileInstance` + `AssetsFileInstance` 索引；提供 `LoadBundleFile / LoadAssetsFile / GetTemplateBaseField / GetBaseField` 等高层方法。

### `AssetWorkspace`（`UABEAvalonia/Workspace/AssetWorkspace.cs`）
- 每个打开的 `.assets` / `.bundle` 都拥有一个 `AssetWorkspace`。
- 持有 `LoadedFiles`、`LoadedAssets`、`NewAssets`（replacer 列表）、`RemovedAssets`、`OtherAssetChanges`。
- 通过 `AddReplacer(replacer, previewStream)` 注册对单个 asset 的修改。
- 通过 `ItemUpdated` 事件通知 UI。
- 当首个 MonoBehaviour 被访问时，自动 `SetMonoTempGenerators`（Cpp2IL 或 MonoCecil）。

### `BundleWorkspace`（`UABEAvalonia/Workspace/BundleWorkspace.cs`）
- 与 `AssetWorkspace` 并列，但承载"bundle 自身"的修改（新增/删除/重命名子文件）。
- `Files: ObservableCollection<BundleWorkspaceItem>` 驱动 UI 列表。
- `GetReplacers()` 在保存时把所有修改物化为 `BundleReplacer`。

### `UABEAPlugin`
- 极简接口：`Init() → PluginInfo { name, options }`。
- 每个 `UABEAPluginOption` 实现 `SelectionValidForPlugin(...)` 和 `ExecutePlugin(Window, workspace, selection) → Task<bool>`。
- 通过 `Assembly.LoadFrom` 加载 `<exe-dir>/plugins/*.dll`。

## 1.5 技术栈

- **GUI**: Avalonia 11.0.1 + Avalonia.AvaloniaEdit + Avalonia.Controls.DataGrid + AvaloniaEdit.TextMate
- **图像**: SixLabors.ImageSharp 3.1.4
- **音频**: Fmod5Sharp（无版本标注）
- **字体**: 仅 .NET 自带 System.IO + AssetTypeValueField
- **C++ 封装**: `TexToolWrap.dll`（C++）封装 PVRTexLib / ISPC TextureCompressor / Crunch
- **持久化**: `config.json` (Newtonsoft.Json 13.0.3-beta1)
- **文本编辑**: Mono.Cecil 0.11.4（用于 MonoBehaviour 类型恢复）
- **IL2CPP 互操作**: Samboy063.LibCpp2IL 2022.0.7.2
- **依赖**: AssetRipper.TextureDecoder 1.2.0

## 1.6 主要模块摘要

| 模块 | 文件 | 责任 |
|---|---|---|
| Entry | `Program.cs` (84) | STA Main + 异常处理 + Avalonia 构建 |
| CLI | `CommandLineHandler.cs` (373) | batchexportbundle / batchimportbundle / applyemip |
| Theme | `ThemeHandler.cs` | 切换 Simple/Fluent 主题 |
| Config | `Config/ConfigurationManager.cs` (64) | `config.json` 持久化 |
| Workspace | `Workspace/*.cs` (936 LoC) | AssetWorkspace / BundleWorkspace / UnityContainer |
| Logic | `Logic/*.cs` (1017 LoC) | Import/Export/EMIP/FileType/Compression |
| Plugins | `Plugins/*.cs` (145 LoC) | 插件宿主 |
| Forms | `Forms/*.axaml.cs` (~17 窗口) | 所有对话框与主窗 |
| Controls | `Controls/AssetDataTreeView.cs` (575) | 类型树懒加载视图 |
| Utils | `Utils/*.cs` | 文件、消息框、路径等辅助 |
| TexturePlugin | `TexturePlugin/*.cs` (1554 LoC) | 编解码、Switch deswizzle、Crunch |
| AudioClipPlugin | `AudioClipPlugin/Program.cs` (292) | FMOD5 → WAV/OGG/MP3 |
| FontPlugin | `FontPlugin/Program.cs` (252) | .ttf/.otf 导入导出 |
| TextAssetPlugin | `TextAssetPlugin/Program.cs` (252) | TextAsset 字节导入导出 |
| TexToolWrap | `TexToolWrap/*.cpp` | C++ 包装（PVRTex + ISPC + Crunch） |
| TexturePluginPreview | `TexturePluginPreview/*.cs` (22 LoC) | 独立预览器（早期原型） |

## 1.7 适用场景

- 翻译替换：批量替换 TextAsset / Texture2D 中的字符串
- 模型替换：通过插件或自定义插件重写 MonoBehaviour 引用
- 离线解包：从压缩 UnityFS bundle 中解出原始 .assets
- Mod 制作：通过 .emip 包分发"只动一两个文件"的修改
- 字段级编辑：在 TypeTree 树视图中查看并修改任意字段

## 1.8 不适用场景

- 大批量"导出 → 编辑 → 重新打包"（请用 AssetStudio CLI）
- FBX / GLTF 等 3D 模型导出（UABEA 只导出原始 .obj/.fbx 字节，TexturePlugin 不包含 ModelPlugin）
- Shader 反编译（无对应插件）
- 加载主数据 + 自动下载依赖（必须手动提供 classdata.tpk）