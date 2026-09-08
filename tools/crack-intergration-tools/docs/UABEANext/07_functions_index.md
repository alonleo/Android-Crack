# 07 · UABEANext 函数索引

> 索引列出所有 UABEANext 主项目 + 插件项目的公共 / 内部 / 关键私有 函数。
> 每条记录：签名 · 可见性 · 文件:行号 · 一句话职责。

---

## 7.1 入口

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 1 | `Main(string[] args)` | public static | `UABEANext4.Desktop/Program.cs` | 入口；装崩溃钩；启动 Avalonia |
| 2 | `UABEANExceptionHandler(object, UnhandledExceptionEventArgs)` | public static | `UABEANext4.Desktop/Program.cs` | 全局崩溃 → log |
| 3 | `BuildAvaloniaApp()` | public static | `UABEANext4.Desktop/Program.cs` | 配置 Avalonia 桌面 |
| 4 | `App()` / `Initialize()` / `OnFrameworkInitializationCompleted()` | public override | `UABEANext4/App.axaml.cs:8-67` | DI 注册 |

## 7.2 AssetWorkspace/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 5 | `Workspace()` | public ctor | `Workspace.cs:51` | 加载 classdata.tpk + plugins |
| 6 | `WorkspaceItem? LoadAnyFile(Stream stream, int loadOrder, string path)` | public | `Workspace.cs:67` | 按文件类型分发 |
| 7 | `WorkspaceItem LoadBundle(Stream stream, int loadOrder, string name)` | public | `Workspace.cs:93` | 加载 .bundle |
| 8 | `WorkspaceItem LoadAssets(Stream stream, int loadOrder, string name)` | public | `Workspace.cs:156` | 加载 .assets |
| 9 | `WorkspaceItem LoadAssetsFromBundle(BundleFileInstance bunInst, int index)` | public | `Workspace.cs:204` | bundle 内单个 .assets |
| 10 | `void FixupAssetsFile(AssetsFileInstance fileInst)` | private | `Workspace.cs:217` | 把 AssetFileInfo 替换为 AssetInst + AssetNamer |
| 11 | `void TryLoadClassDatabase(AssetBundleFile file)` | public | `Workspace.cs:237` | 按 Bundle Header version 加载 |
| 12 | `void TryLoadClassDatabase(AssetsFile file)` | public | `Workspace.cs:249` | 按 AssetsMetadata version 加载 |
| 13 | `WorkspaceItem LoadResource(Stream stream, int loadOrder, string name)` | public | `Workspace.cs:262` | 加载 .resS / .resource |
| 14 | `void AddRootItemThreadSafe(WorkspaceItem item, string itemName)` | internal | `Workspace.cs:275` | UI 线程安全插入 |
| 15 | `void AddChildItemThreadSafe(WorkspaceItem item, WorkspaceItem parent, string itemName)` | internal | `Workspace.cs:299` | 同上但 child |
| 16 | `void SetProgressThreadSafe(float value, string text)` | public | `Workspace.cs:310` | UI 线程安全进度更新 |
| 17 | `AssetTypeTemplateField GetTemplateField(AssetInst asset, bool skipMonoBehaviourFields)` | public | `Workspace.cs:324` | 模板查询 |
| 18 | `AssetTypeTemplateField GetTemplateField(AssetsFileInstance, AssetFileInfo, bool)` | public | `Workspace.cs:335` | 同上 |
| 19 | `void CheckAndSetMonoTempGenerators(AssetsFileInstance, AssetFileInfo?)` | public | `Workspace.cs:346` | 首次访问 MonoBehaviour 时 |
| 20 | `bool SetMonoTempGenerators(string fileDir)` | private | `Workspace.cs:360` | 选择 Cpp2IL 或 MonoCecil |
| 21 | `AssetFileInfo? GetAssetFileInfo(AssetsFileInstance, AssetTypeValueField pptrField)` | public | `Workspace.cs:391` | 通过 PPtr 取 info |
| 22 | `AssetFileInfo? GetAssetFileInfo(AssetsFileInstance, int fileId, long pathId)` | public | `Workspace.cs:396` | 通过 fileId+pathId 取 info |
| 23 | `AssetInst? GetAssetInst(AssetsFileInstance, AssetTypeValueField pptrField)` | public | `Workspace.cs:410` | 取 AssetInst（UI 用） |
| 24 | `AssetInst? GetAssetInst(AssetsFileInstance, int fileId, long pathId)` | public | `Workspace.cs:415` | 同上 |
| 25 | `AssetTypeValueField? GetBaseField(AssetInst asset)` | public | `Workspace.cs:438` | 取 base 字段 |
| 26 | `AssetTypeValueField? GetBaseField(AssetsFileInstance, long pathId)` | public | `Workspace.cs:443` | |
| 27 | `AssetTypeValueField? GetBaseField(AssetsFileInstance, AssetTypeValueField pptrField)` | public | `Workspace.cs:448` | |
| 28 | `AssetTypeValueField? GetBaseField(AssetsFileInstance, int fileId, long pathId)` | public | `Workspace.cs:453` | |
| 29 | `void Dirty(WorkspaceItem item)` | public | `Workspace.cs:495` | 标记脏 |
| 30 | `void Close(WorkspaceItem item)` | public | `Workspace.cs:505` | 关闭 |
| 31 | `void CloseAll()` | public | `Workspace.cs:541` | 全部关闭 |
| 32 | `void RenameFile(WorkspaceItem wsItem, string newName)` | public | `Workspace.cs:561` | 重命名 |
| 33 | `WorkspaceItem? FindWorkspaceItemByInstance(AssetsFileInstance)` | public | `Workspace.cs:583` | 通过 instance 查找 |
| 34 | `WorkspaceItem? FindWorkspaceItemByInstance(BundleFileInstance)` | public | `Workspace.cs:598` | |
| 35 | `WorkspaceItem? FindWorkspaceItemBfs(Func<WorkspaceItem,bool>)` | private | `Workspace.cs:611` | BFS 兜底 |
| 36 | `static IStorageFile? ShowSaveAsDialog(IStorageProvider, string)` | private static | `Workspace.Saving.cs:19` | 弹保存对话框 |
| 37 | `static bool TryGetFileStream(WorkspaceItem, out FileStream?)` | private static | `Workspace.Saving.cs:32` | 提取底层 FileStream |
| 38 | `static bool TryOpenForWriting(string, out FileStream?)` | private static | `Workspace.Saving.cs:55` | 打开写入流 |
| 39 | `void WriteAssetsFile(WorkspaceItem, Stream)` | private | `Workspace.Saving.cs:69` | 写单个 .assets |
| 40 | `void WriteBundleFile(WorkspaceItem, Stream)` | private | `Workspace.Saving.cs:76` | 写 .bundle |
| 41 | `void WriteResource(WorkspaceItem, Stream)` | private | `Workspace.Saving.cs:120` | 写 .resS |
| 42 | `Task<(bool saved, bool failed)> Save(WorkspaceItem)` | public | `Workspace.Saving.cs:142` | 保存 |
| 43 | `Task<bool> SaveAs(WorkspaceItem)` | public | `Workspace.Saving.cs:288` | 另存 |
| 44 | `Task SaveAllAs()` | public | `Workspace.Saving.cs:342` | 全部另存 |
| 45 | `ContainerTool.FromAssetBundle(AssetsManager, AssetsFileInstance, AssetTypeValueField)` | public static | `ContainerTool.cs:16` | 解析 AssetBundle.AssetMap |
| 46 | `ContainerTool.FromResourceManager(AssetsManager, AssetsFileInstance, AssetTypeValueField)` | public static | `ContainerTool.cs:45` | 解析 ResourceManager.AssetMap |
| 47 | `string? GetContainerPath(AssetsFileInstance, long)` / `(AssetPPtr)` | public | `ContainerTool.cs:68, 73` | 反查路径 |
| 48 | `ContainerAssetInfo GetContainerInfo(string)` | public | `ContainerTool.cs:84` | 反查 info |
| 49 | `ContainerToolManager(Workspace)` | public ctor | `ContainerToolManager.cs:17` | 缓存容器工具 |
| 50 | `bool TryGetContainerTool(AssetsFileInstance, [NotNullWhen(true)] out ContainerTool?, [NotNullWhen(false)] out AssetsFileInstance?, [NotNullWhen(false)] out AssetTypeValueField?)` | public | `ContainerToolManager.cs:22` | 取或创建 |
| 51 | `AssetFileInfo? FindFirstAssetOfType(AssetsFileInstance, int)` | private | `ContainerToolManager.cs:85` | 工具 |
| 52 | `WorkspaceItem(...)` 3 重载 | public ctor | `WorkspaceItem.cs:23, 34, 66` | 3 种构造 |
| 53 | `static IEnumerable<WorkspaceItem> GetAssetsFileWorkspaceItems(IEnumerable<WorkspaceItem>)` | public static | `WorkspaceItem.cs:77` | 工具 |
| 54 | `void Update(string propertyName)` | public | `WorkspaceItem.cs:98` | 触发 PropertyChanged |
| 55 | `AssetInst(AssetsFileInstance, AssetFileInfo)` | public ctor | `AssetInst.cs:14` | 包装 AssetFileInfo |
| 56 | `string GetNameWithPathId()` | public | `AssetInst.cs` | 显示名 |

## 7.3 Logic/ImportExport/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 57 | `AssetExport(Stream writeStream)` | public ctor | `AssetExport.cs:15` | 构造（流） |
| 58 | `void DumpRawAsset(AssetsFileReader, long, uint)` | public | `AssetExport.cs:21` | 原始字节导出 |
| 59 | `void DumpTextAsset(AssetTypeValueField)` | public | `AssetExport.cs:36` | .txt 导出入口 |
| 60 | `void RecurseTextDump(AssetTypeValueField, int)` | private | `AssetExport.cs:42` | 递归 |
| 61 | `void TextDumpManagedReferencesRegistry(AssetTypeValueField, int)` | private | `AssetExport.cs:118` | v1/v2 |
| 62 | `void DumpJsonAsset(AssetTypeValueField)` | public | `AssetExport.cs:185` | .json 导出 |
| 63 | `JToken RecurseJsonDump(AssetTypeValueField, bool)` | private | `AssetExport.cs:192` | 递归 |
| 64 | `JObject JsonDumpManagedReferencesRegistry(AssetTypeValueField, bool)` | private | `AssetExport.cs:263` | |
| 65 | `static string TextDumpEscapeString(string)` | private static | `AssetExport.cs:325` | 转义 |
| 66 | `AssetImport(Stream readStream, RefTypeManager)` | public ctor | `AssetImport.cs:16` | 构造 |
| 67 | `byte[] ImportRawAsset()` | public | `AssetImport.cs:23` | |
| 68 | `byte[]? ImportTextAsset(out string?)` | public | `AssetImport.cs:30` | .txt 导入 |
| 69 | `void ImportTextAssetLoop(AssetsFileWriter)` | private | `AssetImport.cs:51` | 解析循环 |
| 70 | `byte[]? ImportJsonAsset(AssetTypeTemplateField, out string?)` | public | `AssetImport.cs:189` | .json 导入 |
| 71 | `void RecurseJsonImport(AssetsFileWriter, AssetTypeTemplateField, JToken)` | private | `AssetImport.cs:213` | 递归 |
| 72 | `void JsonImportManagedReferencesRegistry(AssetsFileWriter, AssetTypeTemplateField, JToken)` | private | `AssetImport.cs:358` | |
| 73 | `JToken ExpectAndReadField(JToken, string, AssetTypeTemplateField?)` | private | `AssetImport.cs:430` | |
| 74 | `static bool StartsWithSpace(string, string)` | private static | `AssetImport.cs:447` | |
| 75 | `static string UnescapeDumpString(string)` | private static | `AssetImport.cs:452` | |

## 7.4 Logic/Mesh/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 76 | `class MeshObj` | public | `MeshObj.cs` | 内存网格 |
| 77 | `void BuildFromBaseField(AssetTypeValueField bf, AssetsFileInstance fileInst)` | public | `MeshObj.cs` | 构造自 BaseField |
| 78 | `class Channel` | public | `Channel.cs` | 顶点属性 |
| 79 | `enum Topology / ChannelFormat` | public | `MeshEnums.cs` | 枚举 |

## 7.5 Logic/Search/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 80 | `List<SearchResultItem> Search(...)` | public | `SearchLogic.cs` | 并发搜索 |

## 7.6 Plugins/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 81 | `PluginLoadContext(string pluginPath)` | public ctor | `PluginLoadContext.cs:11` | 隔离 ALC |
| 82 | `Assembly LoadAssemblyByName(string)` | public | `PluginLoadContext.cs:16` | |
| 83 | `Assembly LoadAssemblyByPath(string)` | public | `PluginLoadContext.cs:21` | |
| 84 | `Assembly? Load(AssemblyName)` | protected override | `PluginLoadContext.cs:26` | |
| 85 | `IntPtr LoadUnmanagedDll(string)` | protected override | `PluginLoadContext.cs:37` | |
| 86 | `bool LoadPlugin(string path)` | public | `PluginLoader.cs:15` | LoadFromAssemblyPath |
| 87 | `void LoadPluginsInDirectory(string dir)` | public | `PluginLoader.cs:79` | 扫描 |
| 88 | `List<PluginOptionModePair> GetOptionsThatSupport(Workspace, List<AssetInst>, UavPluginMode)` | public | `PluginLoader.cs:93` | 菜单项匹配 |
| 89 | `List<PluginPreviewerTypePair> GetPreviewersThatSupport(Workspace, AssetInst)` | public | `PluginLoader.cs:113` | 预览器匹配 |
| 90 | `interface IUavPluginOption` | public | `IUavPluginOption.cs:6` | 菜单项接口 |
| 91 | `interface IUavPluginPreviewer` | public | `IUavPluginPreviewer.cs:7` | 预览器接口 |
| 92 | `interface IUavPluginFunctions` | public | `IUavPluginFunctions.cs:6` | 主机能力 |
| 93 | `interface IUavPluginPreviewerFunctions` | public | `IUavPluginPreviewerFunctions.cs:7` | 预览主机能力 |
| 94 | `UavPluginFunctions()` | public ctor | `UavPluginFunctions.cs:16` | |
| 95 | `Task<string[]> ShowOpenFileDialog(FilePickerOpenOptions)` | public | `UavPluginFunctions.cs:26` | |
| 96 | `Task<string?> ShowSaveFileDialog(FilePickerSaveOptions)` | public | `UavPluginFunctions.cs:32` | |
| 97 | `Task<string?> ShowOpenFolderDialog(FolderPickerOpenOptions)` | public | `UavPluginFunctions.cs:38` | |
| 98 | `Task<T?> ShowDialog<T>(IDialogAware<T>)` | public | `UavPluginFunctions.cs:48` | |
| 99 | `Task ShowMessageDialog(string, string)` | public | `UavPluginFunctions.cs:53` | |
| 100 | `class PluginItemInfo` | public | `PluginItemInfo.cs:8` | 菜单项 VM |
| 101 | `Task Execute(object selectedItems)` | public | `PluginItemInfo.cs:22` | 调插件 |
| 102 | `PluginOptionModePair(IUavPluginOption, UavPluginMode)` | public ctor | `PluginOptionModePair.cs:2` | |
| 103 | `PluginPreviewerTypePair(IUavPluginPreviewer, UavPluginPreviewerType)` | public ctor | `UavPluginPreviewerTypePair.cs:2` | |
| 104 | `enum UavPluginMode` | public | `UavPluginMode.cs:6` | Import/Export/Info |
| 105 | `enum UavPluginPreviewerType` | public | `UavPluginPreviewerType.cs:2` | None/Image/Text/Mesh |

## 7.7 Util/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 106 | `AssetNamer(Workspace)` | public ctor | `AssetNamer.cs:18` | 命名助手 |
| 107 | `string? GetAssetName(AssetInst, bool usePrefix, int maxLen)` | public | `AssetNamer.cs:23` | 缓存 |
| 108 | `string GetAssetTypeName(AssetInst, bool, int)` | public | `AssetNamer.cs:29` | |
| 109 | `void GetDisplayName(AssetInst, bool, int, out string?, out string)` | public | `AssetNamer.cs:35` | 主入口 |
| 110 | `string GetMonoBehaviourNameFast(AssetInst)` | public | `AssetNamer.cs:229` | MonoBehaviour 名 |
| 111 | `static string GetFallbackName(AssetInst, string?)` | public static | `AssetNamer.cs:270` | 兜底 |
| 112 | `static string GetAssetFileName(Workspace, AssetInst, string, int, bool)` | public static | `AssetNamer.cs:275` | 导出文件名 |
| 113 | `static string GetAssetFileName(AssetInst, string, string, bool)` | public static | `AssetNamer.cs:285` | |
| 114 | `static void GetLockObjAndReader(...)` | private static | `AssetNamer.cs:293` | 锁 + reader |
| 115 | `static NameReadOptimization GetGameObjectNro(AssetTypeTemplateField)` | private static | `AssetNamer.cs:314` | 优化字段访问 |
| 116 | `static NameReadOptimization GetMonoBehaviourNro(AssetTypeTemplateField)` | private static | `AssetNamer.cs:371` | |
| 117 | `static void TrimAssetName(ref string, int)` | private static | `AssetNamer.cs:418` | 截断 |
| 118 | `DetectedFileType DetectFileType(string)` | public static | `FileTypeDetector.cs:9` | |
| 119 | `DetectedFileType DetectFileType(AssetsFileReader, long)` | public static | `FileTypeDetector.cs:18` | |
| 120 | `MessageBoxResult ShowDialog(...)` 多个重载 | public static | `MessageBoxUtil.cs` | 弹窗 |
| 121 | `IStorageProvider? GetStorageProvider()` | public static | `StorageService.cs` | 跨视图单例 |
| 122 | `static class WindowUtils` | public | `WindowUtils.cs` | 工具 |
| 123 | `static class PathUtils` | public | `PathUtils.cs` | 路径 |

## 7.8 Services/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 124 | `interface IDialogService` | public | `IDialogService.cs` | 对话框服务 |
| 125 | `class DialogService : IDialogService` | public | `DialogService.cs` | 实现 |
| 126 | `class DummyDialogService : IDialogService` | public | `DummyDialogService.cs` | 测试桩 |

## 7.9 Converters/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 127 | `class AssetClassIDConverter : IValueConverter` | public | `AssetClassIDConverter.cs` | |
| 128 | `class AssetsFileInstanceNameConverter : IValueConverter` | public | `AssetsFileInstanceNameConverter.cs` | |
| 129 | `class AssetTypeIconConverter : IValueConverter` | public | `AssetTypeIconConverter.cs` | |
| 130 | `class BitmapAssetValueConverter : IValueConverter` | public | `BitmapAssetValueConverter.cs` | |
| 131 | `class RadioButtonValueConverter : IValueConverter` | public | `RadioButtonValueConverter.cs` | |
| 132 | `class WsItemColorConverter : IValueConverter` | public | `WsItemColorConverter.cs` | |

每个含 `Convert` + `ConvertBack` 2 个公共方法。

## 7.10 TexturePlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 133 | `ExportTextureOption : IUavPluginOption` | public | `ExportTextureOption.cs` | Export action |
| 134 | `ImportBatchTextureOption : IUavPluginOption` | public | `ImportBatchTextureOption.cs` | Import |
| 135 | `EditTextureOption : IUavPluginOption` | public | `EditTextureOption.cs` | Edit dialog |
| 136 | `TexturePreviewer : IUavPluginPreviewer` | public | `TexturePreviewer.cs` | 纹理预览 |
| 137 | `SpritePreviewer : IUavPluginPreviewer` | public | `SpritePreviewer.cs` | Sprite 预览 |
| 138 | `class SpriteAtlasLookup` | public | `Helpers/SpriteAtlasLookup.cs` | SpriteAtlas 解析 |
| 139 | `class TextureHelper` | public | `Helpers/TextureHelper.cs` | |
| 140 | `class TextureLoader` | public | `Helpers/TextureLoader.cs` | 加载 + 解码 |
| 141 | `Bitmap LoadTexture(AssetsFileInstance, long pathId)` | public | `TextureLoader.cs` | 主入口 |
| 142 | `byte[] EncodeTexture(Bitmap, TextureFormat, ...)` | public | `TextureLoader.cs` | |
| 143 | `EditTextureViewModel` | public | `ViewModels/EditTextureViewModel.cs` | |
| 144 | `ExportBatchOptionsViewModel` | public | `ViewModels/ExportBatchOptionsViewModel.cs` | |

## 7.11 AudioPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 145 | `enum CompressionFormat` | public | `CompressionFormat.cs` | |
| 146 | `ExportAudioOption : IUavPluginOption` | public | `ExportAudioOption.cs` | Export |
| 147 | `BatchExport(Workspace, IUavPluginFunctions, List<AssetInst>)` | public | `ExportAudioOption.cs` | |

## 7.12 FontPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 148 | `ExportFontOption : IUavPluginOption` | public | `ExportFontOption.cs` | |
| 149 | `ImportFontOption : IUavPluginOption` | public | `ImportFontOption.cs` | |
| 150 | `class FontHelper` | public | `FontHelper.cs` | |

## 7.13 TextAssetPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 151 | `ExportTextAssetPlugin : IUavPluginOption` | public | `ExportTextAssetPlugin.cs` | |
| 152 | `ImportTextAssetPlugin : IUavPluginOption` | public | `ImportTextAssetPlugin.cs` | |
| 153 | `TextAssetPreviewer : IUavPluginPreviewer` | public | `TextAssetPreviewer.cs` | |

## 7.14 MeshPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 154 | `MeshPreviewer : IUavPluginPreviewer` | public | `MeshPreviewer.cs` | |
| 155 | `bool Initialize(Workspace workspace, IUavPluginPreviewerFunctions funcs)` | public | `MeshPreviewer.cs` | |
| 156 | `Task OnPreview(AssetInst asset, UavPluginPreviewerFunctions funcs)` | public | `MeshPreviewer.cs` | |

## 7.15 PluginPreviewer & Desktop

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 157 | `MainViewModel` | public | `PluginPreviewer/ViewModels/MainViewModel.cs` | 预览器主 VM |
| 158 | `Main()` | public static | `PluginPreviewer.Desktop/Program.cs` | 入口 |

## 7.16 ViewModels/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 159 | `class MainViewModel : ViewModelBase` | public | `MainViewModel.cs` | 顶层 VM |
| 160 | `class MainDockFactory : IDockFactory` | public | `MainDockFactory.cs` | Dock 布局 |
| 161 | `IRootDock BuildDock()` | public | `MainDockFactory.cs` | 入口 |
| 162 | `class ViewModelBase : ObservableObject` | public | `ViewModelBase.cs` | 公共基类 |
| 163 | `class WorkspaceExplorerToolViewModel` | public | `Tools/WorkspaceExplorerToolViewModel.cs` | |
| 164 | `class HierarchyToolViewModel` | public | `Tools/HierarchyToolViewModel.cs` | |
| 165 | `class InspectorToolViewModel` | public | `Tools/InspectorToolViewModel.cs` | |
| 166 | `class PreviewerToolViewModel` | public | `Tools/PreviewerToolViewModel.cs` | |
| 167 | `class ImagePreviewViewModel` | public | `Tools/ImagePreviewViewModel.cs` | |
| 168 | `class AssetDocumentViewModel` | public | `Documents/AssetDocumentViewModel.cs` | |
| 169 | `class BlankDocumentViewModel` | public | `Documents/BlankDocumentViewModel.cs` | |
| 170 | `class AddAssetViewModel` | public | `Dialogs/AddAssetViewModel.cs` | |
| 171 | `class AddExternalViewModel` | public | `Dialogs/AddExternalViewModel.cs` | |
| 172 | `class AssetDataSearchViewModel` | public | `Dialogs/AssetDataSearchViewModel.cs` | |
| 173 | `class AssetInfoViewModel` | public | `Dialogs/AssetInfoViewModel.cs` | |
| 174 | `class BatchImportViewModel` | public | `Dialogs/BatchImportViewModel.cs` | |
| 175 | `class EditDataViewModel` | public | `Dialogs/EditDataViewModel.cs` | |
| 176 | `class MessageBoxViewModel` | public | `Dialogs/MessageBoxViewModel.cs` | |
| 177 | `class RenameFileViewModel` | public | `Dialogs/RenameFileViewModel.cs` | |
| 178 | `class SelectDumpViewModel` | public | `Dialogs/SelectDumpViewModel.cs` | |
| 179 | `class SelectTypeFilterViewModel` | public | `Dialogs/SelectTypeFilterViewModel.cs` | |
| 180 | `class SettingsViewModel` | public | `Dialogs/SettingsViewModel.cs` | |
| 181 | `class VersionSelectViewModel` | public | `Dialogs/VersionSelectViewModel.cs` | |
| 182 | `class MenuOptionViewModel` | public | `Menu/MenuOptionViewModel.cs` | |

每个 VM 至少有 1 个 `ICommand`/`RelayCommand` 属性 + `[] ObservableProperty` 字段。

---

## 7.17 Logic/AssetInfo/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 183 | `class BuildTarget` | public | `BuildTarget.cs` | Unity BuildTarget 枚举包装 |
| 184 | `string ToString()` | public override | `BuildTarget.cs` | |
| 185 | `class ExternalInfo` | public | `ExternalInfo.cs` | 外部依赖信息 |
| 186 | `void Build(AssetsFile file)` | public | `ExternalInfo.cs` | 解析 Externals |
| 187 | `class GeneralInfo` | public | `GeneralInfo.cs` | 文件通用信息 |
| 188 | `void Build(AssetsFile file)` | public | `GeneralInfo.cs` | 解析 Header |
| 189 | `class ScriptInfo` | public | `ScriptInfo.cs` | MonoBehaviour 类型引用 |
| 190 | `void Build(AssetsFile file)` | public | `ScriptInfo.cs` | 解析 Scripts |
| 191 | `class TypeTreeInfo` | public | `TypeTreeInfo.cs` | TypeTree 摘要 |
| 192 | `void Build(AssetsFile file)` | public | `TypeTreeInfo.cs` | 解析 TypeTree |
| 193 | `class TypeTreeUINode` | public | `TypeTreeUINode.cs` | 树 UI 节点 |
| 194 | `string DisplayName` | public | `TypeTreeUINode.cs` | |
| 195 | `class TypeTreeTypeInfo` | public | `TypeTreeTypeInfo.cs` | 类型信息 |
| 196 | `class TypeTreeNodeConverter` | public | `TypeTreeNodeConverter.cs` | 节点转换 |

## 7.18 Logic/Configuration/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 197 | `class ConfigurationManager` | public static | `ConfigurationManager.cs` | 配置中心 |
| 198 | `static ConfigurationValues Settings { get; }` | public static | `ConfigurationManager.cs` | 全局访问 |
| 199 | `static void SaveConfig()` | public static | `ConfigurationManager.cs` | 持久化 |
| 200 | `class ConfigurationValues` | public | `ConfigurationValues.cs` | 配置项 |
| 201 | `string Theme { get; set; }` | public | `ConfigurationValues.cs` | 主题 |
| 202 | `int ListingNameLength { get; set; }` | public | `ConfigurationValues.cs` | 名称截断长度 |
| 203 | `bool UseManagedOverIl2cpp { get; set; }` | public | `ConfigurationValues.cs` | Mono 恢复优先级 |
| 204 | `bool ExportImportJustNames { get; set; }` | public | `ConfigurationValues.cs` | |
| 205 | `class ConfigurationItem` | public | `ConfigurationItem.cs` | 单配置项 |
| 206 | `event PropertyChanged` | public | `ConfigurationItem.cs` | |
| 207 | `enum ConfigurationThemeType` | public | `ConfigurationThemeType.cs` | 主题枚举 |

## 7.19 Logic/DevTools/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 208 | `static class DevToolsAdblock` | public | `DevToolsAdblock.cs` | 关闭 DevTools 广告 |

## 7.20 Logic/Documents/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 209 | `class DocumentManager` | public | `DocumentManager.cs` | Document dock 管理 |
| 210 | `void CloseDocument(IDocument)` | public | `DocumentManager.cs` | |

## 7.21 Logic/Hierarchy/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 211 | `class HierarchyItem` | public | `HierarchyItem.cs` | GameObject 树节点 |
| 212 | `IEnumerable<HierarchyItem> Build(GameObject go, Workspace ws)` | public static | `HierarchyItem.cs` | 构建 |

## 7.22 Logic/Messages.cs

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 213 | `record SelectedWorkspaceItemChangedMessage(...)` | public | `Messages.cs` | VM 通信 |
| 214 | `record RequestEditAssetMessage(...)` | public | `Messages.cs` | |
| 215 | `record RequestCloseFileMessage(...)` | public | `Messages.cs` | |
| 216 | `record RequestVisitAssetMessage(...)` | public | `Messages.cs` | |
| 217 | `record FileLoadedMessage(...)` | public | `Messages.cs` | |

## 7.23 Controls/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 218 | `class AssetDataTreeView : TreeView` | public | `AssetDataTreeView.cs` | 类型树视图 |
| 219 | `void Init(MainViewModel, WorkspaceItem, AssetInst)` | public | `AssetDataTreeView.cs` | |
| 220 | `void Reset()` | public | `AssetDataTreeView.cs` | |
| 221 | `void LoadComponent(AssetTypeValueField)` | public | `AssetDataTreeView.cs` | |
| 222 | `void ExpandAllChildren(TreeViewItem)` | public | `AssetDataTreeView.cs` | |
| 223 | `class MeshPreviewerControl : UserControl` | public | `MeshPreviewer/MeshPreviewerControl.cs` | GL 渲染 |
| 224 | `void SetMesh(MeshObj)` | public | `MeshPreviewerControl.cs` | |
| 225 | `static class MeshPreviewerShaders` | public static | `MeshPreviewer/MeshPreviewerShaders.cs` | GLSL 字符串 |

## 7.24 NativeLibs/

| # | 资源 | 位置 | 说明 |
|---|---|---|---|
| 226 | `textureencoder.dll` | `NativeLibs/win-x64/` | Crunch + 编码（推测） |
| 227 | `cuttlefish.dll` | `NativeLibs/win-x64/` | Crunch 库 |
| 228 | `PVRTexLib.dll` | `NativeLibs/win-x64/` | PVRTex |
| 229 | `libtextureencoder.so` | `NativeLibs/linux-x64/` | Linux 镜像 |
| 230 | `libcuttlefish.so.2.10` | `NativeLibs/linux-x64/` | Linux 镜像 |
| 231 | `libPVRTexLib.so` | `NativeLibs/linux-x64/` | Linux 镜像 |

---

**索引统计**：共 **231** 个公共/内部/关键私有 函数/资源条目。

- 入口：4
- AssetWorkspace：52
- Logic (ImportExport + Mesh + Search + AssetInfo)：约 30
- Plugins：25
- Util：18
- Services/Converters：9
- TexturePlugin：12
- AudioPlugin/Font/TextAsset/Mesh：约 10
- PluginPreviewer：2
- ViewModels：24
- Views：~30（每个含初始化 + 关闭回调）

详细说明见 `08_functions_detail/`。