# 07 · UABEA 函数索引

> 索引列出所有 UABEA 主项目 + 插件项目中公共 / 内部 / 受保护 / 关键私有 函数。
> 每条记录：`签名` · `可见性` · `文件:行号` · 一句话职责。

---

## 7.1 UABEAvalonia/ 入口与配置

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 1 | `static void Main(string[] args)` | public | `Program.cs:21` | STA 入口：装 console / 装异常钩 / 分流 CLI 或 Avalonia |
| 2 | `static void UABEAExceptionHandler(object, UnhandledExceptionEventArgs)` | public | `Program.cs:57` | 全局崩溃 → `uabeacrash.log` + Windows mshta 弹窗 |
| 3 | `static AppBuilder BuildAvaloniaApp()` | public | `Program.cs:79` | Avalonia 应用配置（platform detect + LogToTrace） |
| 4 | `static void PrintHelp()` | public | `CommandLineHandler.cs:11` | 打印 CLI 帮助 |
| 5 | `static string GetMainFileName(string[] args)` | private | `CommandLineHandler.cs:33` | 解析 CLI 子命令后的主文件路径 |
| 6 | `static HashSet<string> GetFlags(string[] args)` | private | `CommandLineHandler.cs:43` | 解析 `-keepnames` / `-kd` 等标志 |
| 7 | `static AssetBundleFile DecompressBundle(string file, string? decompFile)` | private | `CommandLineHandler.cs:54` | 解压 .bundle 到内存或 .decomp |
| 8 | `static string GetNextBackup(string affectedFilePath)` | private | `CommandLineHandler.cs:86` | 查找下一个可用 `.bakNNNN` 名 |
| 9 | `static void BatchExportBundle(string[] args)` | private | `CommandLineHandler.cs:101` | CLI: 批量导出 bundle 内所有 entry |
| 10 | `static void BatchImportBundle(string[] args)` | private | `CommandLineHandler.cs:156` | CLI: 批量导入目录内匹配文件回 bundle |
| 11 | `static void ApplyEmip(string[] args)` | private | `CommandLineHandler.cs:237` | CLI: 应用 .emip mod 包 |
| 12 | `static void CLHMain(string[] args)` | public | `CommandLineHandler.cs:349` | CLI 入口分发 |
| 13 | `App()` / `Initialize()` / `OnFrameworkInitializationCompleted()` | public override | `App.axaml.cs:10, 16` | Avalonia App 初始化 |
| 14 | `static ConfigurationSettings Settings { get; }` | public static | `ConfigurationManager.cs:10` | 全局只读配置访问器 |
| 15 | `static void SaveConfig()` | public static | `ConfigurationManager.cs:29` | 持久化 `config.json` |

## 7.2 Workspace/ 工作区层

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 16 | `AssetWorkspace(AssetsManager am, bool fromBundle)` | public ctor | `AssetWorkspace.cs:46` | 构造 |
| 17 | `void AddReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, Stream? previewStream)` | public | `AssetWorkspace.cs:68` | 注册对单个 asset 的修改（最核心入口） |
| 18 | `void RemoveReplacer(AssetsFileInstance forFile, AssetsReplacer replacer, bool closePreviewStream)` | public | `AssetWorkspace.cs:108` | 撤销修改 |
| 19 | `void LoadAssetsFile(AssetsFileInstance fromFile, bool loadDependencies)` | public | `AssetWorkspace.cs:131` | 加载 .assets 并递归 externals |
| 20 | `HashSet<AssetsFileInstance> GetChangedFiles()` | public | `AssetWorkspace.cs:172` | 收集已修改的 .assets 文件 |
| 21 | `void SetOtherAssetChangeFlag(AssetsFileInstance, AssetsFileChangeTypes)` | public | `AssetWorkspace.cs:195` | 标记依赖关系变更 |
| 22 | `void UnsetOtherAssetChangeFlag(AssetsFileInstance, AssetsFileChangeTypes)` | public | `AssetWorkspace.cs:203` | 撤销标记 |
| 23 | `void GenerateAssetsFileLookup()` | public | `AssetWorkspace.cs:224` | 构建 fileName → fileInst 字典 |
| 24 | `AssetTypeTemplateField GetTemplateField(AssetContainer cont, bool forceCldb, bool skipMonoBehaviourFields)` | public | `AssetWorkspace.cs:232` | 取模板字段 |
| 25 | `AssetContainer? GetAssetContainer(AssetsFileInstance fileInst, int fileId, long pathId, bool onlyInfo)` | public | `AssetWorkspace.cs:243` | 取容器（核心访问器） |
| 26 | `AssetContainer GetAssetContainer(AssetsFileInstance, AssetTypeValueField pptrField, bool onlyInfo)` | public | `AssetWorkspace.cs:293` | pptr 重载 |
| 27 | `AssetContainer GetAssetContainer(AssetsFileInstance, AssetPPtr pptr, bool onlyInfo)` | public | `AssetWorkspace.cs:300` | PPtr 重载 |
| 28 | `AssetContainer GetAssetContainer(AssetContainer cont)` | public | `AssetWorkspace.cs:308` | 同上 |
| 29 | `List<AssetContainer> GetAssetsOfType(int classId)` | public | `AssetWorkspace.cs:313` | 按 ClassId 过滤 |
| 30 | `AssetTypeValueField? GetBaseField(AssetContainer cont)` | public | `AssetWorkspace.cs:337` | 取 base 字段（缓存或新建） |
| 31 | `AssetTypeValueField? GetBaseField(AssetsFileInstance fileInst, int fileId, long pathId)` | public | `AssetWorkspace.cs:352` | 重载 |
| 32 | `AssetTypeValueField? GetBaseField(AssetsFileInstance, AssetTypeValueField pptrField)` | public | `AssetWorkspace.cs:361` | pptr 重载 |
| 33 | `AssetTypeValueField GetConcatMonoBaseField(AssetContainer cont, string managedPath)` | public | `AssetWorkspace.cs:373` | 拼接 MonoBehaviour 字段（Managed 模式） |
| 34 | `AssetTypeTemplateField GetConcatMonoTemplateField(AssetContainer cont, string managedPath)` | public | `AssetWorkspace.cs:379` | 同上但返回 template |
| 35 | `bool SetMonoTempGenerators(string fileDir)` | public | `AssetWorkspace.cs:411` | 设置 Mono 模板生成器（Cpp2IL 优先） |
| 36 | `BundleWorkspace()` | public ctor | `BundleWorkspace.cs:23` | 构造 + 新 AssetsManager |
| 37 | `void Reset(BundleFileInstance? bundleInst)` | public | `BundleWorkspace.cs:33` | 重置 + 填充 Files |
| 38 | `void PopulateFilesList()` | private | `BundleWorkspace.cs:45` | 遍历 BlockAndDirInfo |
| 39 | `void AddOrReplaceFile(Stream stream, string name, bool isSerialized, string? prevName)` | public | `BundleWorkspace.cs:60` | 新增或替换 entry |
| 40 | `void RenameFile(string origName, string newName)` | public | `BundleWorkspace.cs:100` | 重命名 |
| 41 | `List<BundleReplacer> GetReplacers()` | public | `BundleWorkspace.cs:111` | 收集所有 BundleReplacer |
| 42 | `void FromAssetBundle(AssetsManager, AssetsFileInstance, AssetTypeValueField assetBundleBf)` | public | `UnityContainer.cs:19` | 解析 AssetBundle.AssetMap |
| 43 | `void FromResourceManager(AssetsManager, AssetsFileInstance, AssetTypeValueField rsrcManBf)` | public | `UnityContainer.cs:44` | 解析 ResourceManager.AssetMap |
| 44 | `string? GetContainerPath(AssetsFileInstance fileInst, long pathId)` | public | `UnityContainer.cs:63` | 取容器路径 |
| 45 | `string? GetContainerPath(AssetPPtr assetPPtr)` | public | `UnityContainer.cs:68` | PPtr 重载 |
| 46 | `UnityContainerAssetInfo GetContainerInfo(string path)` | public | `UnityContainer.cs:79` | 反向查找 |
| 47 | `static bool TryGetBundleContainerBaseField(AssetWorkspace, AssetsFileInstance, out AssetsFileInstance, out AssetTypeValueField)` | public static | `UnityContainer.cs:85` | 取 AssetBundle 容器字段 |
| 48 | `static bool TryGetRsrcManContainerBaseField(AssetWorkspace, AssetsFileInstance, out AssetsFileInstance, out AssetTypeValueField)` | public static | `UnityContainer.cs:111` | 取 ResourceManager 容器字段 |
| 49 | `AssetContainer(...)` 4 个 ctor 重载 | public | `AssetContainer.cs:39, 54, 70, 84` | 4 种构造 |
| 50 | `void SetNewFile(AssetsFileInstance fileInst)` | public | `AssetContainer.cs:98` | 写盘后更新位置 |

## 7.3 Logic/ 业务层

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 51 | `void DumpRawAsset(FileStream wfs, AssetsFileReader reader, long position, uint size)` | public | `AssetImportExport.cs:20` | 4KB 缓冲拷贝原始字节 |
| 52 | `void DumpTextAsset(StreamWriter sw, AssetTypeValueField baseField)` | public | `AssetImportExport.cs:34` | 文本 dump 入口 |
| 53 | `void RecurseTextDump(AssetTypeValueField field, int depth)` | private | `AssetImportExport.cs:40` | 递归生成 TypeTree 文本 |
| 54 | `void DumpJsonAsset(StreamWriter sw, AssetTypeValueField baseField)` | public | `AssetImportExport.cs:179` | JSON 格式 dump |
| 55 | `JToken RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor)` | private | `AssetImportExport.cs:186` | JSON 递归 |
| 56 | `byte[] ImportRawAsset(FileStream fs)` | public | `AssetImportExport.cs:319` | 读取原始字节 |
| 57 | `byte[]? ImportTextAsset(StreamReader sr, out string? exceptionMessage)` | public | `AssetImportExport.cs:328` | 文本回写入口 |
| 58 | `void ImportTextAssetLoop()` | private | `AssetImportExport.cs:349` | 文本解析循环（核心） |
| 59 | `byte[]? ImportJsonAsset(AssetTypeTemplateField, StreamReader, out string?)` | public | `AssetImportExport.cs:487` | JSON 回写 |
| 60 | `void RecurseJsonImport(AssetTypeTemplateField, JToken)` | private | `AssetImportExport.cs:512` | JSON 递归导入 |
| 61 | `static AssetsReplacer CreateAssetReplacer(AssetContainer, byte[])` | public static | `AssetImportExport.cs:699` | 工具：构造 AssetsReplacerFromMemory |
| 62 | `static BundleReplacer CreateBundleReplacer(string, bool, byte[])` | public static | `AssetImportExport.cs:704` | 工具：构造 BundleReplacerFromMemory |
| 63 | `static BundleReplacer CreateBundleReplacer(string, bool, Stream, long, long)` | public static | `AssetImportExport.cs:709` | 工具：构造 BundleReplacerFromStream |
| 64 | `static BundleReplacer CreateBundleRemover(string, bool, int)` | public static | `AssetImportExport.cs:714` | 工具：构造 BundleRemover |
| 65 | `bool Read(AssetsFileReader reader, bool prefReplacersInMemory)` | public | `Emip.cs:20` | InstallerPackageFile.Read |
| 66 | `void Write(AssetsFileWriter writer)` | public | `Emip.cs:75` | 写入 .emip |
| 67 | `static object ParseReplacer(AssetsFileReader, bool)` | private static | `Emip.cs:116` | 解析单个 replacer |
| 68 | `static DetectedFileType DetectFileType(string filePath)` | public static | `FileTypeDetector.cs:9` | magic sniff 文件路径重载 |
| 69 | `static DetectedFileType DetectFileType(AssetsFileReader r, long startAddress)` | public static | `FileTypeDetector.cs:18` | magic sniff stream 重载 |
| 70 | `static bool IsBundleDataCompressed(AssetBundleFile bundle)` | public static | `AssetBundleUtil.cs:15` | 检查任何 block 是否压缩 |

## 7.4 Plugins/ 插件系统

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 71 | `bool LoadPlugin(string path)` | public | `PluginManager.cs:21` | LoadFrom + 创建 UABEAPlugin |
| 72 | `void LoadPluginsInDirectory(string directory)` | public | `PluginManager.cs:48` | 遍历 plugins/*.dll |
| 73 | `List<UABEAPluginMenuInfo> GetPluginsThatSupport(AssetsManager, List<AssetContainer>)` | public | `PluginManager.cs:57` | 收集支持当前选择的菜单项 |
| 74 | `PluginInfo Init()` | interface | `UABEAPlugin.cs:11` | 插件初始化 |
| 75 | `bool SelectionValidForPlugin(...)` / `Task<bool> ExecutePlugin(...)` | interface | `UABEAPluginOption.cs:10, 11` | 插件能力声明 + 执行 |
| 76 | `UABEAPluginMenuInfo(PluginInfo, UABEAPluginOption, string)` | public ctor | `UABEAPluginMenuInfo.cs:15` | 构造菜单项 |

## 7.5 Forms/ UI（关键窗口）

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 77 | `MainWindow()` | public ctor | `MainWindow.axaml.cs:31` | 构造 |
| 78 | `MainWindow_Initialized` 等 30+ 事件 | private | `MainWindow.axaml.cs:71-1016` | 见 08_functions_detail/main_window.md |
| 79 | `LoadOrAskTypeData(AssetsFileInstance)` | private | `MainWindow.axaml.cs:587` | 缺失 classdata.tpk 时询问 |
| 80 | `AskLoadCompressedBundle(BundleFileInstance)` | private | `MainWindow.axaml.cs:814` | 询问解压 .bundle |
| 81 | `DecompressToFile / DecompressToMemory` | private | `MainWindow.axaml.cs:873, 889` | 解压实现 |
| 82 | `LoadBundle / SaveBundle / SaveBundleOver` | private | `MainWindow.axaml.cs:905, 917, 928` | 加载/保存 |
| 83 | `CompressBundle(object?)` | private | `MainWindow.axaml.cs:960` | 压缩（异步） |
| 84 | `InfoWindow()` 2 重载 | public ctor | `InfoWindow.axaml.cs:47, 92` | 构造 |
| 85 | `MenuAdd/Save/SaveAs/CreatePackageFile/Close/Search/GoTo/Filter/...` | private | `InfoWindow.axaml.cs:119-217` | 工具栏与菜单事件 |
| 86 | `BtnViewData/SceneView/ExportRaw/ExportDump/ImportRaw/ImportDump/EditData/Remove/Plugin_Click` | private | `InfoWindow.axaml.cs:222-402` | 按钮事件 |
| 87 | `ShowEditAssetWindow(AssetContainer)` | public | `InfoWindow.axaml.cs:980` | 弹出 EditDataWindow |
| 88 | `SelectAsset(AssetsFileInstance, long)` | public | `InfoWindow.axaml.cs:1060` | 选中指定 pathId |
| 89 | `SetupContainers()` / `MakeDataGridItems()` | private | `InfoWindow.axaml.cs:1080, 1113` | 构建 Unity container 字典 |
| 90 | `BatchExportRaw / SingleExportRaw / BatchExportDump / SingleExportDump` 等 8 个 | private | `InfoWindow.axaml.cs:649-998` | 导入导出 4 模式 × 2 |
| 91 | `Workspace_ItemUpdated` / `Workspace_MonoTemplateLoadFailed` | private | `InfoWindow.axaml.cs:1229, 1267` | 工作区事件回调 |

## 7.6 Controls/AssetDataTreeView

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 92 | `AssetDataTreeView()` | public ctor | `AssetDataTreeView.cs:80` | 构造 + 4 个 context menu 项 |
| 93 | `void Init(InfoWindow win, AssetWorkspace workspace)` | public | `AssetDataTreeView.cs:165` | 初始化引用 |
| 94 | `void Reset()` | public | `AssetDataTreeView.cs:172` | 清空 |
| 95 | `void LoadComponent(AssetContainer container)` | public | `AssetDataTreeView.cs:177` | 把 asset 装到树 |
| 96 | `void ExpandAllChildren / CollapseAllChildren(TreeViewItem)` | public | `AssetDataTreeView.cs:214, 237` | 折叠/展开 |
| 97 | `void TreeLoad(AssetsFileInstance, AssetTypeValueField, long, TreeViewItem)` | private | `AssetDataTreeView.cs:355` | 懒加载子节点 |

## 7.7 Utils/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 98 | `static void GetDisplayNameFast(AssetWorkspace, AssetContainer, bool, out string, out string)` | public static | `AssetNameUtils.cs:14` | 取显示名（无 IO） |
| 99 | `static string GetMonoBehaviourNameFast(AssetWorkspace, AssetContainer)` | public static | `AssetNameUtils.cs:136` | MonoBehaviour 名解析 |
| 100 | `static string[] GetOpenFileDialogFiles(IReadOnlyList<IStorageFile>)` | public static | `FileDialogUtils.cs:12` | 取全部选中路径 |
| 101 | `static string[] GetOpenFolderDialogFiles(IReadOnlyList<IStorageFolder>)` | public static | `FileDialogUtils.cs:17` | 取文件夹路径 |
| 102 | `static string? GetSaveFileDialogFile(IStorageFile?)` | public static | `FileDialogUtils.cs:22` | 取保存路径 |
| 103 | `static string GetFormattedByteSize(long size)` | public static | `FileUtils.cs:13` | 字节数人类可读 |
| 104 | `static List<string> GetFilesInDirectory(string, List<string>)` | public static | `FileUtils.cs:21` | 扩展名过滤 |
| 105 | `static string ReplaceInvalidPathChars(string)` | public static | `PathUtils.cs:14` | 清理非法路径字符 |
| 106 | `static string GetFilePathWithoutExtension(string)` | public static | `PathUtils.cs:19` | 去扩展 |
| 107 | `static string GetAssetsFileDirectory(AssetsFileInstance)` | public static | `PathUtils.cs:30` | bundle 内 .assets 的目录 |
| 108 | `static bool WildcardMatches(string, string, bool)` | public static | `SearchUtils.cs:19` | 通配符匹配 |
| 109 | `static Task<MessageBoxResult> ShowDialog(Window, string, string)` 等 5 个重载 | public static | `MessageBoxUtil.cs:8+` | 异步弹窗 |

## 7.8 TexturePlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 110 | `PluginInfo Init()` | public | `TexturePlugin/Program.cs:18` | 注册 3 个 Option |
| 111 | `bool SelectionValidForPlugin(...)` / `Task<bool> ExecutePlugin(...)` | public | `ExportTextureOption.cs:18, 36` | Export action |
| 112 | `Task<bool> BatchExport(Window, AssetWorkspace, List<AssetContainer>)` | public | `ExportTextureOption.cs:44` | 批量导出 |
| 113 | `Task<bool> SingleExport(Window, AssetWorkspace, List<AssetContainer>)` | public | `ExportTextureOption.cs:123` | 单个导出 |
| 114 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `ImportTextureOption.cs:21, 109` | Import action |
| 115 | `Task<bool> ImportTextures(Window, List<ImportBatchInfo>)` | private | `ImportTextureOption.cs:39` | 批量导入主循环 |
| 116 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `EditTextureOption.cs:15, 33` | Edit action |
| 117 | `static AssetTypeValueField GetByteArrayTexture(AssetWorkspace, AssetContainer)` | public static | `TextureHelper.cs:13` | 模板 image data 标记 ByteArray |
| 118 | `static bool GetResSTexture(TextureFile, AssetsFileInstance)` | public static | `TextureHelper.cs:32` | 从 bundle resS 读 |
| 119 | `static byte[] GetRawTextureBytes(TextureFile, AssetsFileInstance)` | public static | `TextureHelper.cs:69` | 从外部文件读 |
| 120 | `static byte[] GetPlatformBlob(AssetTypeValueField)` | public static | `TextureHelper.cs:98` | 取 m_PlatformBlob 字节 |
| 121 | `static bool IsPo2(int)` | public static | `TextureHelper.cs:109` | 2 的幂判断 |
| 122 | `static int GetMaxMipCount(int, int)` | public static | `TextureHelper.cs:115` | 计算最大 mip 层数 |
| 123 | `static byte[] Import(...)` 2 重载 | public static | `TextureImportExport.cs:12, 21` | 主导入入口 |
| 124 | `static byte[] ImportSwitch(...)` | private static | `TextureImportExport.cs:47` | Switch 平台导入 |
| 125 | `static bool Export(...)` / `static Image<Rgba32> Export(...)` | public static | `TextureImportExport.cs:79, 91` | 主导出入口 |
| 126 | `static Image<Rgba32> ExportSwitch(...)` | private static | `TextureImportExport.cs:112` | Switch 平台导出 |
| 127 | `static void SaveImageAtPath(Image<Rgba32>, string)` | public static | `TextureImportExport.cs:143` | 写 PNG/TGA |
| 128 | `static TextureFormat GetCorrectedSwitchTextureFormat(TextureFormat)` | private static | `TextureImportExport.cs:158` | RGB24 → RGBA32 修正 |
| 129 | `static int RGBAToFormatByteSize(TextureFormat, int, int)` | public static | `TextureEncoderDecoder.cs:12` | 计算纹理格式字节数 |
| 130 | `static byte[] Decode(byte[], int, int, TextureFormat)` | public static | `TextureEncoderDecoder.cs:339` | 主解码入口 |
| 131 | `static byte[] EncodeMip(byte[], int, int, TextureFormat, int, int)` | public static | `TextureEncoderDecoder.cs:438` | 单 mip 编码 |
| 132 | `static byte[] Encode(Image<Rgba32>, int, int, TextureFormat, int, int)` | public static | `TextureEncoderDecoder.cs:519` | 主编码入口 |
| 133 | `static byte[] DecodeAssetRipperTex / DecodePVRTexLib / DecodeCrunch` | private static | `TextureEncoderDecoder.cs:153, 166, 194` | 三个具体解码器 |
| 134 | `static byte[] EncodeISPC / EncodePVRTexLib / EncodeCrunch` | private static | `TextureEncoderDecoder.cs:214, 252, 290` | 三个具体编码器 |
| 135 | `internal static Image<Rgba32> SwitchUnswizzle(Image<Rgba32>, Size, int)` | internal static | `Texture2DSwitchDeswizzler.cs:54` | Switch 去 swizzle |
| 136 | `internal static Image<Rgba32> SwitchSwizzle(Image<Rgba32>, Size, int)` | internal static | `Texture2DSwitchDeswizzler.cs:98` | Switch 加 swizzle |
| 137 | `internal static Size TextureFormatToBlockSize(TextureFormat)` | internal static | `Texture2DSwitchDeswizzler.cs:143` | 格式→块大小映射 |
| 138 | `internal static Size GetPaddedTextureSize(int, int, int, int, int)` | internal static | `Texture2DSwitchDeswizzler.cs:180` | 计算填充后尺寸 |
| 139 | `internal static int GetSwitchGobsPerBlock(byte[])` | internal static | `Texture2DSwitchDeswizzler.cs:187` | 从 platformBlob 提取 GOB 数 |
| 140 | `[DllImport("textoolwrap")] static extern uint DecodeByCrunchUnity(...)` 等 6 个 | public | `PInvoke.cs:13-28` | C++ 封装入口 |

## 7.9 AudioClipPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 141 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `Program.cs:32, 47` | Export action |
| 142 | `Task<bool> BatchExport / SingleExport` | public | `Program.cs:55, 107` | 导出 2 模式 |
| 143 | `static void FixWAV(ref byte[])` | private static | `Program.cs:161` | 修复 FMOD5 输出的 WAV 头 |
| 144 | `static string GetExtension(CompressionFormat)` | private static | `Program.cs:193` | 压缩格式→扩展名 |
| 145 | `bool GetAudioBytes(AssetContainer, string, ulong, ulong, out byte[])` | private | `Program.cs:211` | 从 bundle/disk 取音频字节 |
| 146 | `PluginInfo Init()` | public | `Program.cs:282` | 注册 ExportAudioClipOption |

## 7.10 FontPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 147 | `static AssetTypeValueField GetByteArrayFont(AssetWorkspace, AssetContainer)` | public static | `Program.cs:16` | 模板 m_FontData 标记 ByteArray |
| 148 | `static bool IsDataOtf(byte[])` | public static | `Program.cs:30` | 检测 OTF magic |
| 149 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `ImportFontOption.cs:41, 56` | Import action |
| 150 | `Task<bool> BatchImport / SingleImport` | public | `ImportFontOption.cs:64, 101` | 导入 2 模式 |
| 151 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `ExportFontOption.cs:138, 153` | Export action |
| 152 | `Task<bool> BatchExport / SingleExport` | public | `ExportFontOption.cs:161, 196` | 导出 2 模式 |
| 153 | `PluginInfo Init()` | public | `Program.cs:241` | 注册 2 个 Option |

## 7.11 TextAssetPlugin/

| # | 签名 | 可见性 | 位置 | 说明 |
|---|---|---|---|---|
| 154 | `static string GetUContainerExtension(AssetContainer)` | public static | `Program.cs:15` | 取 Unity container 扩展名 |
| 155 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `ImportTextAssetOption.cs:29, 44` | Import action |
| 156 | `Task<bool> BatchImport / SingleImport` | public | `ImportTextAssetOption.cs:52, 88` | 导入 2 模式 |
| 157 | `bool SelectionValidForPlugin / ExecutePlugin` | public | `ExportTextAssetOption.cs:136, 151` | Export action |
| 158 | `Task<bool> BatchExport / SingleExport` | public | `ExportTextAssetOption.cs:159, 194` | 导出 2 模式 |
| 159 | `PluginInfo Init()` | public | `Program.cs:242` | 注册 2 个 Option |

---

**索引统计**：共 **159** 个公共/内部/关键私有函数。

- UABEAvalonia/（主项目）：约 90
- TexturePlugin/：约 31
- AudioClipPlugin/：6
- FontPlugin/：7
- TextAssetPlugin/：6
- Utils/：12
- Forms（含 MainWindow + InfoWindow）：约 30 个关键事件方法

详细说明（每个函数的 caller/callee）见 `08_functions_detail/`。