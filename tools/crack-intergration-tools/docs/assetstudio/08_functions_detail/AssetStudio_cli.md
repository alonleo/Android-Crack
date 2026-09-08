# `AssetStudio_cli.md` — CLI 函数详细说明

本章详细列出 `AssetStudio.CLI/`（csproj `AssetStudio.CLI.csproj`）下被覆盖的 public/internal 函数。

---

## 1. `AssetStudio.CLI/Program.cs`

### `Program.Main(string[])`
- **签名**：`static void Main(string[] args)`
- **位置**：`AssetStudio.CLI/Program.cs:14`
- **可见性**：public static
- **调用了**：`CommandLine.Init(args)`
- **简要说明**：CLI 入口

### `Program.Run(Options)`
- **签名**：`static void Run(Options o)`
- **位置**：`AssetStudio.CLI/Program.cs:16`
- **可见性**：public static
- **副作用**：写大量状态；异常时捕获并输出到控制台
- **调用了**：
  - `GameManager.GetGame/SupportedGames` (`GameManager.cs:54/68`)
  - `UnityCNManager.TryGetEntry` (`UnityCNManager.cs:50`)
  - `UnityCN.SetKey` (`UnityCN.cs:50`)
  - `AssetsHelper.SetUnityVersion/Minimal/BuildCABMap/LoadCABMapInternal/ParseAssetMap/BuildAssetMap/BuildBoth` (`AssetsHelper.cs:36/21/142/248/504/316/687`)
  - `TypeFlags.SetTypes/SetType` (`TypeFlags.cs:9/14`)
  - `ResourceIndex.FromFile` (`ResourceIndex.cs:13`)
  - `AssemblyLoader.Load` (`AssemblyStudio.Utility/AssemblyLoader.cs`)
  - `ImportHelper.MergeSplitAssets/ProcessingSplitFiles` (`ImportHelper.cs:19/49`)
  - `Studio.BuildAssetData` (`Studio.cs:231`)
  - `Studio.ExportAssets` (`Studio.cs:366`)
  - `assetsManager.LoadFiles/Clear`
- **简要说明**：CLI 主流程；详见 [05_operation_chains.md 链 1](../05_operation_chains.md)

---

## 2. `AssetStudio.CLI/Studio.cs`

### `Studio.ExtractFolder(string, string)`
- **签名**：`static int ExtractFolder(string path, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:35`
- **可见性**：public
- **返回值**：`int`（成功提取的文件数）
- **调用了**：`Studio.ExtractFile(string, string)`
- **简要说明**：遍历目录提取

### `Studio.ExtractFile(string[], string)`
- **签名**：`static int ExtractFile(string[] fileNames, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:49`
- **可见性**：public
- **调用了**：`Studio.ExtractFile(string, string)`
- **简要说明**：批量提取

### `Studio.ExtractFile(string, string)`
- **签名**：`static int ExtractFile(string fileName, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:60`
- **可见性**：public
- **调用了**：`new FileReader`、`FileReader.PreProcessing`、`ExtractBundleFile`、`ExtractWebDataFile`、`ExtractBlkFile`、`ExtractBlockFile`
- **简要说明**：FileType 分派后调用对应 Extract*

### `Studio.ExtractBundleFile(FileReader, string)`
- **签名**：`static int ExtractBundleFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:78`
- **可见性**：private
- **调用了**：`new BundleFile`、`ExtractStreamFile`
- **简要说明**：bundle 解压到 `<name>_unpacked/`

### `Studio.ExtractWebDataFile(FileReader, string)`
- **签名**：`static int ExtractWebDataFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:98`
- **可见性**：private
- **调用了**：`new WebFile`、`ExtractStreamFile`
- **简要说明**：处理 WebFile 提取

### `Studio.ExtractBlkFile(FileReader, string)`
- **签名**：`static int ExtractBlkFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:111`
- **可见性**：private
- **调用了**：`BlkUtils.Decrypt`、`ExtractBundleFile`、`ExtractMhyFile`
- **简要说明**：Blk 提取

### `Studio.ExtractBlockFile(FileReader, string)`
- **签名**：`static int ExtractBlockFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:142`
- **可见性**：private
- **调用了**：`new OffsetStream`、`ExtractBundleFile`
- **简要说明**：BlockFile 提取

### `Studio.ExtractMhyFile(FileReader, string)`
- **签名**：`static int ExtractMhyFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.CLI/Studio.cs:158`
- **可见性**：private
- **调用了**：`new MhyFile`、`ExtractStreamFile`
- **简要说明**：Mhy 提取

### `Studio.ExtractStreamFile(string, List<StreamFile>)`
- **签名**：`static int ExtractStreamFile(string extractPath, List<StreamFile> fileList)`
- **位置**：`AssetStudio.CLI/Studio.cs:178`
- **可见性**：private
- **简要说明**：写所有 stream 到磁盘

### `Studio.UpdateContainers()`
- **签名**：`static void UpdateContainers()`
- **位置**：`AssetStudio.CLI/Studio.cs:202`
- **可见性**：public
- **调用了**：`ResourceIndex.GetContainer`
- **简要说明**：把 GI container ID 替换为真实路径

### `Studio.BuildAssetData(ClassIDType[], Regex[], Regex[], ref int)`
- **签名**：`static void BuildAssetData(ClassIDType[] typeFilters, Regex[] nameFilters, Regex[] containerFilters, ref int i)`
- **位置**：`AssetStudio.CLI/Studio.cs:231`
- **可见性**：public
- **调用了**：`Studio.ProcessAssetData`、`Studio.UpdateContainers`
- **简要说明**：CLI 版 AssetData 构建 + 过滤

### `Studio.ProcessAssetData(Object, ...)`
- **签名**：`static void ProcessAssetData(Object asset, Dictionary<Object, AssetItem> objectAssetItemDic, List<(PPtr<Object>, string)> mihoyoBinDataNames, List<(PPtr<Object>, string)> containers, ref int i)`
- **位置**：`AssetStudio.CLI/Studio.cs:283`
- **可见性**：public
- **调用了**：`new AssetItem`、`GameObject.HasModel`
- **简要说明**：单 Object → AssetItem，构造 mihoyoBinDataNames/containers 列表

### `Studio.ExportAssets(string, List<AssetItem>, AssetGroupOption, ExportType, ImageFormat)`
- **签名**：`static void ExportAssets(string savePath, List<AssetItem> toExportAssets, AssetGroupOption assetGroupOption, ExportType exportType, ImageFormat imageFormat = ImageFormat.Png)`
- **位置**：`AssetStudio.CLI/Studio.cs:366`
- **可见性**：public
- **调用了**：`Parallel.ForEach`、`ExportRawFile`、`ExportDumpFile`、`ExportConvertFile`、`ExportJSONFile`
- **简要说明**：并行导出

### `Studio.ExportAssetsMap(string, List<AssetEntry>, string, ExportListType)`
- **签名**：`static void ExportAssetsMap(string savePath, List<AssetEntry> toExportAssets, string exportListName, ExportListType exportListType)`
- **位置**：`AssetStudio.CLI/Studio.cs:454`
- **可见性**：public
- **调用了**：`XmlWriter.Create`、`JsonSerializer`
- **简要说明**：AssetMap XML/JSON 导出

### `Studio.MonoBehaviourToTypeTree(MonoBehaviour)`
- **签名**：`static TypeTree MonoBehaviourToTypeTree(MonoBehaviour m_MonoBehaviour)`
- **位置**：`AssetStudio.CLI/Studio.cs:503`
- **可见性**：public
- **调用了**：`m_MonoBehaviour.ConvertToTypeTree(assemblyLoader)`
- **简要说明**：转 TypeTree（CLI 没有弹窗，假设用户已经通过 `--dummy_dlls` 加载）

---

## 3. `AssetStudio.CLI/Exporter.cs`

### `Exporter.ExportTexture2D(AssetItem, string, ImageFormat)`
- **签名**：`static bool ExportTexture2D(AssetItem item, string exportPath, ImageFormat imageFormat = ImageFormat.Png)`
- **位置**：`AssetStudio.CLI/Exporter.cs:12`
- **可见性**：public
- **调用了**：`Texture2D.ConvertToImage`、`Image.WriteToStream`、`m_Texture2D.image_data.GetData`、`TryExportFile`
- **简要说明**：Texture 导出

### `Exporter.ExportAudioClip(AssetItem, string)`
- **签名**：`static bool ExportAudioClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:41`
- **调用了**：`new AudioClipConverter`、`AudioClipConverter.ConvertToWav`、`TryExportFile`
- **简要说明**：AudioClip 导出

### `Exporter.ExportShader(AssetItem, string)`
- **签名**：`static bool ExportShader(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:66`
- **调用了**：`m_Shader.Convert`、`TryExportFile`
- **简要说明**：Shader 导出

### `Exporter.ExportTextAsset(AssetItem, string)`
- **签名**：`static bool ExportTextAsset(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:76`
- **调用了**：`TryExportFile`
- **简要说明**：TextAsset 导出

### `Exporter.ExportMonoBehaviour(AssetItem, string)`
- **签名**：`static bool ExportMonoBehaviour(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:93`
- **调用了**：`Studio.MonoBehaviourToTypeTree`、`JsonConvert.SerializeObject`、`TryExportFile`
- **简要说明**：MonoBehaviour JSON 导出

### `Exporter.ExportMiHoYoBinData(AssetItem, string)`
- **签名**：`static bool ExportMiHoYoBinData(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:109`
- **调用了**：`m_MiHoYoBinData.Dump`、`TryExportFile`
- **简要说明**：MiHoYoBinData 导出

### `Exporter.ExportFont(AssetItem, string)`
- **签名**：`static bool ExportFont(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:150`
- **调用了**：`TryExportFile`
- **简要说明**：Font 导出

### `Exporter.ExportMesh(AssetItem, string)`
- **签名**：`static bool ExportMesh(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:168`
- **调用了**：`TryExportFile`
- **简要说明**：Mesh → OBJ

### `Exporter.ExportVideoClip(AssetItem, string)`
- **签名**：`static bool ExportVideoClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:250`
- **调用了**：`m_VideoClip.m_VideoData.WriteData`、`TryExportFile`
- **简要说明**：VideoClip 导出

### `Exporter.ExportMovieTexture(AssetItem, string)`
- **签名**：`static bool ExportMovieTexture(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:263`
- **调用了**：`TryExportFile`
- **简要说明**：MovieTexture 导出

### `Exporter.ExportSprite(AssetItem, string, ImageFormat)`
- **签名**：`static bool ExportSprite(AssetItem item, string exportPath, ImageFormat imageFormat = ImageFormat.Png)`
- **位置**：`AssetStudio.CLI/Exporter.cs:272`
- **调用了**：`Sprite.GetImage`、`Image.WriteToStream`、`TryExportFile`
- **简要说明**：Sprite 导出

### `Exporter.ExportRawFile(AssetItem, string)`
- **签名**：`static bool ExportRawFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:292`
- **调用了**：`item.Asset.GetRawData`、`TryExportFile`
- **简要说明**：原始字节导出

### `Exporter.ExportAnimationClip(AssetItem, string)`
- **签名**：`static bool ExportAnimationClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:345`
- **调用了**：`m_AnimationClip.Convert`、`TryExportFile`
- **简要说明**：AnimationClip → .anim

### `Exporter.ExportAnimator(AssetItem, string, List<AssetItem>)`
- **签名**：`static bool ExportAnimator(AssetItem item, string exportPath, List<AssetItem> animationList = null)`
- **位置**：`AssetStudio.CLI/Exporter.cs:357`
- **调用了**：`new ModelConverter(m_Animator, ...)`、`ExportFbx`、`ExportJSONFile`、`TryExportFolder`
- **简要说明**：Animator → FBX

### `Exporter.ExportGameObject(AssetItem, string, List<AssetItem>)`
- **签名**：`static bool ExportGameObject(AssetItem item, string exportPath, List<AssetItem> animationList = null)`
- **位置**：`AssetStudio.CLI/Exporter.cs:390`
- **调用了**：`ExportGameObject(GameObject, string, List<AssetItem>)`、`TryExportFolder`
- **简要说明**：GameObject → FBX 重载

### `Exporter.ExportGameObject(GameObject, string, List<AssetItem>)`
- **签名**：`static bool ExportGameObject(GameObject gameObject, string exportPath, List<AssetItem> animationList = null)`
- **位置**：`AssetStudio.CLI/Exporter.cs:399`
- **调用了**：`new ModelConverter`、`ExportFbx`、`ExportJSONFile`
- **简要说明**：GameObject → FBX

### `Exporter.ExportDumpFile(AssetItem, string)`
- **签名**：`static bool ExportDumpFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:454`
- **调用了**：`item.Asset.Dump`、`TryExportFile`
- **简要说明**：Object.Dump()

### `Exporter.ExportConvertFile(AssetItem, string, ImageFormat)`
- **签名**：`static bool ExportConvertFile(AssetItem item, string exportPath, ImageFormat imageFormat = ImageFormat.Png)`
- **位置**：`AssetStudio.CLI/Exporter.cs:467`
- **调用了**：所有 `ExportXxx`
- **简要说明**：按 item.Type 分派

### `Exporter.ExportJSONFile(AssetItem, string)`
- **签名**：`static bool ExportJSONFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.CLI/Exporter.cs:506`
- **调用了**：`JsonConvert.SerializeObject`、`TryExportFile`
- **简要说明**：JSON 导出

### `Exporter.FixFileName(string)`
- **签名**：`static string FixFileName(string str)`
- **位置**：`AssetStudio.CLI/Exporter.cs:518`
- **简要说明**：清洗文件名

---

## 4. `AssetStudio.CLI/Components/CommandLine.cs`

### `CommandLine.Init(string[])`
- **签名**：`static void Init(string[] args)`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:14`
- **可见性**：public
- **调用了**：`CommandLine.RegisterOptions`、`rootCommand.Invoke(args)`
- **简要说明**：CLI 参数解析入口

### `CommandLine.RegisterOptions()`
- **签名**：`static RootCommand RegisterOptions()`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:19`
- **可见性**：public
- **调用了**：`new OptionsBinder`、`new RootCommand`、`rootCommand.SetHandler(Program.Run, optionsBinder)`
- **简要说明**：创建 RootCommand + 18 个 Option + 绑定 handler

### `OptionsBinder` 构造器
- **签名**：`OptionsBinder()`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:95`
- **可见性**：public ctor
- **调用了**：`GameManager.GetGameNames`
- **简要说明**：18 个 Option 字段初始化

### `OptionsBinder.ParseKey(string)`
- **签名**：`byte ParseKey(string value)`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:211`
- **可见性**：public
- **抛出/异常**：非 hex / 非 byte 抛 `FormatException`
- **简要说明**：解析 `0xNN` 或 `NN`

### `OptionsBinder.FilterValidator(OptionResult)`
- **签名**：`void FilterValidator(OptionResult result)`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:224`
- **可见性**：public
- **抛出/异常**：无效 regex 设 `result.ErrorMessage`
- **简要说明**：校验 regex 合法性

### `OptionsBinder.GetBoundValue(BindingContext)`
- **签名**：`override Options GetBoundValue(BindingContext bindingContext)`
- **位置**：`AssetStudio.CLI/Components/CommandLine.cs:247`
- **可见性**：protected override
- **调用了**：`bindingContext.ParseResult.GetValueForOption/GetValueForArgument`
- **简要说明**：把 args 绑定到 Options 对象

---

## 5. `AssetStudio.CLI/Components/AssetItem.cs`

### `AssetItem(Object)` 构造器
- **签名**：`AssetItem(Object asset)`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **调用**：`Studio.ProcessAssetData` (`Studio.cs:285`)
- **简要说明**：包装 Object 并初始化 Text/Container/TypeString/SourceFile

### `AssetItem.UniqueID` 属性
- **签名**：`string UniqueID { get; set; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **简要说明**：CLI 端用 `#N` 编号

### `AssetItem.Container` 属性
- **签名**：`string Container { get; set; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **简要说明**：AssetBundle 容器路径

### `AssetItem.Text` 属性
- **签名**：`string Text { get; set; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **简要说明**：显示文本（asset name）

### `AssetItem.Type` 属性 / `TypeString`
- **签名**：`ClassIDType Type { get; }` / `string TypeString { get; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **简要说明**：ClassID + 字符串表示

### `AssetItem.FullSize` 属性
- **签名**：`long FullSize { get; set; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **调用**：`Studio.ProcessAssetData` (`Studio.cs:296, 301, 306`)
- **简要说明**：完整大小（含外部资源）

### `AssetItem.Asset` 属性
- **签名**：`Object Asset { get; }`
- **位置**：`AssetStudio.CLI/Components/AssetItem.cs`
- **简要说明**：原始 Object

---

## 6. `AssetStudio.CLI/Settings.cs`

### `Settings.Default` 属性
- **位置**：`AssetStudio.CLI/Settings.cs`
- **调用**：`Program.Run`（多处）、`Exporter.ExportXxx`
- **简要说明**：从 App.config 加载的强类型设置（enableFileLogging / minimalAssetMap / types / convertTexture / convertAudio / convertType / collectAnimations / exportMaterials / uvs / texs / restoreExtensionName / allowDuplicates / convertType 等）

---

## 7. `AssetStudio.CLI/App.config`

- **位置**：`AssetStudio.CLI/App.config`
- **简要说明**：CLI 的运行时配置；`Settings.Default` 读取这里的值