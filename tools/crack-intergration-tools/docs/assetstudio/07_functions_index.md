# 07 函数索引（Functions Index）

本索引列出 AssetStudio 解决方案中所有被文档覆盖的 public / internal 函数 / 属性 / 构造器 / 事件 / record。

> **约定**：
> - 文件路径以 `AssetStudio/` 根目录为基准
> - 行号以最后一次读取的代码为准
> - 详细说明参见 `08_functions_detail/<module>.md`

---

## 1. `AssetStudio/` 核心库

### 1.1 `AssetsManager.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 1 | `VersionPromptEventArgs.FileName` getter/setter | `AssetsManager.cs:17` | `string FileName` | property | 被弹窗显示的文件名 |
| 2 | `VersionPromptEventArgs.UserProvidedVersion` getter/setter | `AssetsManager.cs:18` | `string UserProvidedVersion` | property | 用户输入的版本 |
| 3 | `VersionPromptEventArgs.Cancelled` getter/setter | `AssetsManager.cs:19` | `bool Cancelled` | property | 取消标志 |
| 4 | `AssetsManager.OnVersionPrompt` | `AssetsManager.cs:25` | `event EventHandler<VersionPromptEventArgs>` | event | 请求用户输入 Unity 版本 |
| 5 | `AssetsManager.LoadFiles(params string[] files)` | `AssetsManager.cs:48` | `void LoadFiles(params string[] files)` | public | 顶层入口：加载文件数组 |
| 6 | `AssetsManager.LoadFolder(string path)` | `AssetsManager.cs:73` | `void LoadFolder(string path)` | public | 顶层入口：加载文件夹 |
| 7 | `AssetsManager.Load(string[] files)` | `AssetsManager.cs:96` | `void Load(string[] files)` | private | 实际的并行加载 |
| 8 | `AssetsManager.DetectUnityVersionFromFolder(string path)` | `AssetsManager.cs:176` | `void DetectUnityVersionFromFolder(string path)` | private | 从 `globalgamemanagers` / `data.unity3d` 检测版本 |
| 9 | `AssetsManager.TryExtractVersionFromFile(string filePath)` | `AssetsManager.cs:243` | `string TryExtractVersionFromFile(string filePath)` | private | 尝试从 SerializedFile 读 unityVersion |
| 10 | `AssetsManager.TryExtractVersionFromBundle(string filePath)` | `AssetsManager.cs:266` | `string TryExtractVersionFromBundle(string filePath)` | private | 尝试从 BundleFile 读 unityRevision |
| 11 | `AssetsManager.LoadFile(string fullName)` | `AssetsManager.cs:289` | `void LoadFile(string fullName)` | private | FileReader 包装 |
| 12 | `AssetsManager.LoadFile(FileReader reader)` | `AssetsManager.cs:296` | `void LoadFile(FileReader reader)` | private | FileType 分派 |
| 13 | `AssetsManager.LoadAssetsFile(FileReader reader)` | `AssetsManager.cs:330` | `void LoadAssetsFile(FileReader reader)` | private | 解析单个 SerializedFile |
| 14 | `AssetsManager.LoadAssetsFromMemory(FileReader, string, string, long)` | `AssetsManager.cs:430` | `void LoadAssetsFromMemory(FileReader reader, string originalPath, string unityVersion, long originalOffset)` | private | 从 bundle 内的 stream 加载 |
| 15 | `AssetsManager.LoadBundleFile(FileReader, string?, long, bool)` | `AssetsManager.cs:485` | `void LoadBundleFile(FileReader reader, string originalPath, long originalOffset, bool log)` | private | BundleFile 解析 + 调度 fileList |
| 16 | `AssetsManager.LoadWebFile(FileReader)` | `AssetsManager.cs:542` | `void LoadWebFile(FileReader reader)` | private | WebFile 解析 |
| 17 | `AssetsManager.LoadZipFile(FileReader)` | `AssetsManager.cs:580` | `void LoadZipFile(FileReader reader)` | private | Zip 内多 entry 处理 |
| 18 | `AssetsManager.LoadBlockFile(FileReader)` | `AssetsManager.cs:677` | `void LoadBlockFile(FileReader reader)` | private | BlockFile 多段处理 |
| 19 | `AssetsManager.LoadBlkFile(FileReader)` | `AssetsManager.cs:714` | `void LoadBlkFile(FileReader reader)` | private | Blk 文件处理 |
| 20 | `AssetsManager.LoadMhyFile(FileReader, string?, long, bool)` | `AssetsManager.cs:751` | `void LoadMhyFile(FileReader reader, string originalPath, long originalOffset, bool log)` | private | Mhy 文件处理 |
| 21 | `AssetsManager.LoadBlbFile(FileReader, string?, long, bool)` | `AssetsManager.cs:795` | `void LoadBlbFile(FileReader reader, string originalPath, long originalOffset, bool log)` | private | Blb 文件处理 |
| 22 | `AssetsManager.CheckStrippedVersion(SerializedFile)` | `AssetsManager.cs:838` | `void CheckStrippedVersion(SerializedFile assetsFile)` | public | 处理 version 被 strip 的 SerializedFile |
| 23 | `AssetsManager.Clear()` | `AssetsManager.cs:907` | `void Clear()` | public | 释放所有资源，重置状态 |
| 24 | `AssetsManager.ReadAssets()` | `AssetsManager.cs:937` | `void ReadAssets()` | private | 反序列化所有 Object |
| 25 | `AssetsManager.ProcessAssets()` | `AssetsManager.cs:1010` | `void ProcessAssets()` | private | 关联 GameObject ↔ Transform/Renderer 等 |

### 1.2 `BundleFile.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 26 | `Header.ToString()` | `BundleFile.cs:58` | `override string ToString()` | public | 调试输出 |
| 27 | `StorageBlock.ToString()` | `BundleFile.cs:79` | `override string ToString()` | public | 调试输出 |
| 28 | `Node.ToString()` | `BundleFile.cs:96` | `override string ToString()` | public | 调试输出 |
| 29 | `BundleFile(FileReader, Game)` | `BundleFile.cs:119` | `BundleFile(FileReader reader, Game game)` | public ctor | 解析整个 Bundle |
| 30 | `BundleFile.ReadBundleHeader(FileReader)` | `BundleFile.cs:157` | `Header ReadBundleHeader(FileReader reader)` | private | 读签名/version/unityRevision |
| 31 | `BundleFile.ReadHeaderAndBlocksInfo(FileReader)` | `BundleFile.cs:217` | `void ReadHeaderAndBlocksInfo(FileReader reader)` | private | 旧格式（UnityWeb/UnityRaw） |
| 32 | `BundleFile.CreateBlocksStream(string path)` | `BundleFile.cs:252` | `Stream CreateBlocksStream(string path)` | private | 构造解压输出流 |
| 33 | `BundleFile.ReadBlocksAndDirectory(FileReader, Stream)` | `BundleFile.cs:270` | `void ReadBlocksAndDirectory(FileReader reader, Stream blocksStream)` | private | 旧格式：写 blocks + 读目录 |
| 34 | `BundleFile.ReadFiles(Stream, string)` | `BundleFile.cs:302` | `void ReadFiles(Stream blocksStream, string path)` | public | 把每个 entry 写到 fileList[i].stream |
| 35 | `BundleFile.ReadHeader(FileReader)` | `BundleFile.cs:332` | `void ReadHeader(FileReader reader)` | private | 新格式头（size/flags） |
| 36 | `BundleFile.ReadUnityCN(FileReader)` | `BundleFile.cs:378` | `void ReadUnityCN(FileReader reader)` | private | UnityCN 加密 header |
| 37 | `BundleFile.ReadBlocksInfoAndDirectory(FileReader)` | `BundleFile.cs:408` | `void ReadBlocksInfoAndDirectory(FileReader reader)` | private | 读 blocksInfo + directory |
| 38 | `BundleFile.ReadBlocks(FileReader, Stream)` | `BundleFile.cs:529` | `void ReadBlocks(FileReader reader, Stream blocksStream)` | private | 解压所有 block |
| 39 | `BundleFile.ParseVersion()` | `BundleFile.cs:709` | `int[] ParseVersion()` | public | 把 unityRevision 解析为 int[] |

### 1.3 `SerializedFile.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 40 | `SerializedFile(FileReader, AssetsManager)` | `SerializedFile.cs:50` | `SerializedFile(FileReader reader, AssetsManager assetsManager)` | public ctor | 解析整个 SerializedFile |
| 41 | `SerializedFile.SetVersion(string)` | `SerializedFile.cs:259` | `void SetVersion(string stringVersion)` | public | 设置 unityVersion + version[] + buildType |
| 42 | `SerializedFile.ReadSerializedType(bool)` | `SerializedFile.cs:274` | `SerializedType ReadSerializedType(bool isRefType)` | private | 读单个 SerializedType |
| 43 | `SerializedFile.ReadTypeTree(TypeTree, int)` | `SerializedFile.cs:342` | `void ReadTypeTree(TypeTree m_Type, int level)` | private | 递归读 type tree |
| 44 | `SerializedFile.TypeTreeBlobRead(TypeTree)` | `SerializedFile.cs:375` | `void TypeTreeBlobRead(TypeTree m_Type)` | private | 读 blob type tree（Unknown_12+） |
| 45 | `SerializedFile.AddObject(Object)` | `SerializedFile.cs:429` | `void AddObject(Object obj)` | public | 添加到 Objects + ObjectsDic |
| 46 | `SerializedFile.DecodeClassID(int)` | `SerializedFile.cs:436` | `static int DecodeClassID(int value)` | private static | GI 类 ID 解码 |

### 1.4 `ImportHelper.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 47 | `ImportHelper.MergeSplitAssets(string, bool)` | `ImportHelper.cs:19` | `static void MergeSplitAssets(string path, bool allDirectories)` | public | 合并 `.split0..N` 文件 |
| 48 | `ImportHelper.ProcessingSplitFiles(List<string>)` | `ImportHelper.cs:49` | `static string[] ProcessingSplitFiles(List<string> selectFile)` | public | 过滤 .split 路径，加入合并后的路径 |
| 49 | `ImportHelper.DecompressGZip(FileReader)` | `ImportHelper.cs:67` | `static FileReader DecompressGZip(FileReader reader)` | public | GZip 解压 |
| 50 | `ImportHelper.DecompressBrotli(FileReader)` | `ImportHelper.cs:82` | `static FileReader DecompressBrotli(FileReader reader)` | public | Brotli 解压 |
| 51 | `ImportHelper.DecryptPack(FileReader, Game)` | `ImportHelper.cs:97` | `static FileReader DecryptPack(FileReader reader, Game game)` | public | GI_Pack mr0k 解密 |
| 52 | `ImportHelper.DecryptMark(FileReader)` | `ImportHelper.cs:228` | `static FileReader DecryptMark(FileReader reader)` | public | 通用 Mark XOR 解密 |
| 53 | `ImportHelper.DecryptEnsembleStar(FileReader)` | `ImportHelper.cs:277` | `static FileReader DecryptEnsembleStar(FileReader reader)` | public | EnsembleStars 解密 |
| 54 | `ImportHelper.ParseFakeHeader(FileReader)` | `ImportHelper.cs:303` | `static FileReader ParseFakeHeader(FileReader reader)` | public | FakeHeader 跳过头 |
| 55 | `ImportHelper.DecryptFantasyOfWind(FileReader)` | `ImportHelper.cs:330` | `static FileReader DecryptFantasyOfWind(FileReader reader)` | public | Fantasy of Wind 解密 |
| 56 | `ImportHelper.ParseHelixWaltz2(FileReader)` | `ImportHelper.cs:389` | `static FileReader ParseHelixWaltz2(FileReader reader)` | public | Helix Waltz 2 解密 |
| 57 | `ImportHelper.DecryptAnchorPanic(FileReader)` | `ImportHelper.cs:440` | `static FileReader DecryptAnchorPanic(FileReader reader)` | public | Anchor Panic RC4 |
| 58 | `ImportHelper.DecryptDreamscapeAlbireo(FileReader)` | `ImportHelper.cs:557` | `static FileReader DecryptDreamscapeAlbireo(FileReader reader)` | public | Dreamscape Albireo 重排头 |
| 59 | `ImportHelper.DecryptImaginaryFest(FileReader)` | `ImportHelper.cs:624` | `static FileReader DecryptImaginaryFest(FileReader reader)` | public | Imaginary Fest XOR |
| 60 | `ImportHelper.DecryptAliceGearAegis(FileReader)` | `ImportHelper.cs:757` | `static FileReader DecryptAliceGearAegis(FileReader reader)` | public | Alice Gear Aegis XOR |
| 61 | `ImportHelper.DecryptProjectSekai(FileReader)` | `ImportHelper.cs:797` | `static FileReader DecryptProjectSekai(FileReader reader)` | public | Project Sekai 大端 XOR |
| 62 | `ImportHelper.DecryptCodenameJump(FileReader)` | `ImportHelper.cs:835` | `static FileReader DecryptCodenameJump(FileReader reader)` | public | Codename Jump XOR |
| 63 | `ImportHelper.DecryptGirlsFrontline(FileReader)` | `ImportHelper.cs:868` | `static FileReader DecryptGirlsFrontline(FileReader reader)` | public | Girls Frontline XOR |
| 64 | `ImportHelper.DecryptReverse1999(FileReader)` | `ImportHelper.cs:897` | `static FileReader DecryptReverse1999(FileReader reader)` | public | Reverse: 1999 单字节 XOR |
| 65 | `ImportHelper.DecryptJJKPhantomParade(FileReader)` | `ImportHelper.cs:949` | `static FileReader DecryptJJKPhantomParade(FileReader reader)` | public | JJK Phantom Parade AES-XOR |
| 66 | `ImportHelper.DecryptMuvLuvDimensions(FileReader)` | `ImportHelper.cs:1014` | `static FileReader DecryptMuvLuvDimensions(FileReader reader)` | public | Muv Luv Dimensions XOR |
| 67 | `ImportHelper.DecryptPartyAnimals(FileReader)` | `ImportHelper.cs:1034` | `static FileReader DecryptPartyAnimals(FileReader reader)` | public | PartyAnimals XOR |
| 68 | `ImportHelper.DecryptLoveAndDeepspace(FileReader)` | `ImportHelper.cs:1061` | `static FileReader DecryptLoveAndDeepspace(FileReader reader)` | public | Love and Deepspace XOR |
| 69 | `ImportHelper.DecryptSchoolGirlStrikers(FileReader)` | `ImportHelper.cs:1100` | `static FileReader DecryptSchoolGirlStrikers(FileReader reader)` | public | School Girl Strikers XOR |

### 1.5 `AssetsHelper.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 70 | `AssetsHelper.SetUnityVersion(string)` | `AssetsHelper.cs:36` | `static void SetUnityVersion(string version)` | public | 设置全局 Unity version |
| 71 | `AssetsHelper.Clear()` | `AssetsHelper.cs:50` | `static void Clear()` | public | 清空所有状态 |
| 72 | `AssetsHelper.ClearOffsets()` | `AssetsHelper.cs:63` | `static void ClearOffsets()` | public | 仅清 Offsets 缓存 |
| 73 | `AssetsHelper.TryGet(string, out long[])` | `AssetsHelper.cs:69` | `static bool TryGet(string path, out long[] offsets)` | public | 查询 path 的 offsets |
| 74 | `AssetsHelper.AddCABOffsets(string[], List<string>)` | `AssetsHelper.cs:81` | `static void AddCABOffsets(string[] paths, List<string> cabs)` | public | 把 cab 列表的 offsets 加入 |
| 75 | `AssetsHelper.FindCAB(string, out List<string>)` | `AssetsHelper.cs:105` | `static bool FindCAB(string path, out List<string> cabs)` | public | 找包含 path 的 cab |
| 76 | `AssetsHelper.ProcessFiles(string[])` | `AssetsHelper.cs:113` | `static string[] ProcessFiles(string[] files)` | public | 解析依赖，返回最终加载清单 |
| 77 | `AssetsHelper.ProcessDependencies(string[])` | `AssetsHelper.cs:128` | `static string[] ProcessDependencies(string[] files)` | public | 顶层包装 |
| 78 | `AssetsHelper.BuildCABMap(string[], string, string, Game)` | `AssetsHelper.cs:142` | `static void BuildCABMap(string[] files, string mapName, string baseFolder, Game game)` | public | 构建 CABMap |
| 79 | `AssetsHelper.LoadCABMapInternal(string)` | `AssetsHelper.cs:248` | `static bool LoadCABMapInternal(string mapName)` | public | 加载 Maps/<name>.bin |
| 80 | `AssetsHelper.LoadCABMap(string)` | `AssetsHelper.cs:269` | `static bool LoadCABMap(string path)` | public | 加载任意路径 CABMap |
| 81 | `AssetsHelper.BuildAssetMap(...)` | `AssetsHelper.cs:316` | `static async Task BuildAssetMap(string[] files, string mapName, Game game, string savePath, ExportListType exportListType, ClassIDType[] typeFilters, Regex[] nameFilters, Regex[] containerFilters)` | public | 构建 AssetMap |
| 82 | `AssetsHelper.ParseAssetMap(string, ExportListType, ClassIDType[], Regex[], Regex[])` | `AssetsHelper.cs:504` | `static string[] ParseAssetMap(string mapName, ExportListType mapType, ClassIDType[] typeFilter, Regex[] nameFilter, Regex[] containerFilter)` | public | 读 AssetMap 返回命中文件列表 |
| 83 | `AssetsHelper.BuildBoth(...)` | `AssetsHelper.cs:687` | `static async Task BuildBoth(...)` | public | CABMap + AssetMap 同时构建 |

### 1.6 `GameManager.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 84 | `GameManager.GetGame(GameType)` | `GameManager.cs:54` | `static Game GetGame(GameType gameType)` | public | 按 enum 取 Game |
| 85 | `GameManager.GetGame(int)` | `GameManager.cs:55` | `static Game GetGame(int index)` | public | 按索引取 Game |
| 86 | `GameManager.GetGame(string)` | `GameManager.cs:65` | `static Game GetGame(string name)` | public | 按名字取 Game |
| 87 | `GameManager.GetGames()` | `GameManager.cs:66` | `static Game[] GetGames()` | public | 取所有 Game |
| 88 | `GameManager.GetGameNames()` | `GameManager.cs:67` | `static string[] GetGameNames()` | public | 取所有 Name |
| 89 | `GameManager.SupportedGames()` | `GameManager.cs:68` | `static string SupportedGames()` | public | 格式化为字符串 |
| 90 | `Game(GameType)` | `GameManager.cs:76` | `Game(GameType type)` | public ctor | 基础 Game |
| 91 | `Mr0k(GameType, byte[], byte[], byte[], byte[], byte[])` | `GameManager.cs:93` | `Mr0k(GameType, byte[], byte[], byte[], byte[], byte[])` | public ctor | Mr0k 类构造 |
| 92 | `Blk(GameType, byte[], byte[], byte[], ulong)` | `GameManager.cs:110` | `Blk(GameType, byte[], byte[], byte[], ulong)` | public ctor | Blk 类构造 |
| 93 | `Mhy(GameType, byte[], byte[], byte[], byte[], byte[], byte[], ulong)` | `GameManager.cs:125` | `Mhy(GameType, byte[], byte[], byte[], byte[], byte[], byte[], ulong)` | public ctor | Mhy 类构造 |

---

## 2. `AssetStudio.CLI/`

### 2.1 `Program.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 94 | `Program.Main(string[])` | `Program.cs:14` | `static void Main(string[] args)` | entry | CLI 入口 |
| 95 | `Program.Run(Options)` | `Program.cs:16` | `static void Run(Options o)` | public | 主流程 |

### 2.2 `Studio.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 96 | `Studio.ExtractFolder(string, string)` | `Studio.cs:35` | `static int ExtractFolder(string path, string savePath)` | public | 遍历目录提取 |
| 97 | `Studio.ExtractFile(string[], string)` | `Studio.cs:49` | `static int ExtractFile(string[] fileNames, string savePath)` | public | 批量提取 |
| 98 | `Studio.ExtractFile(string, string)` | `Studio.cs:60` | `static int ExtractFile(string fileName, string savePath)` | public | 单文件提取 |
| 99 | `Studio.UpdateContainers()` | `Studio.cs:202` | `static void UpdateContainers()` | public | GI 系列 container ID 解析 |
| 100 | `Studio.BuildAssetData(ClassIDType[], Regex[], Regex[], ref int)` | `Studio.cs:231` | `static void BuildAssetData(ClassIDType[] typeFilters, Regex[] nameFilters, Regex[] containerFilters, ref int i)` | public | 构建 AssetItem 列表 + 过滤 |
| 101 | `Studio.ProcessAssetData(Object, ...)` | `Studio.cs:283` | `static void ProcessAssetData(Object asset, Dictionary<Object, AssetItem> objectAssetItemDic, List<(PPtr<Object>, string)> mihoyoBinDataNames, List<(PPtr<Object>, string)> containers, ref int i)` | public | 单个 Object 转 AssetItem |
| 102 | `Studio.ExportAssets(string, List<AssetItem>, AssetGroupOption, ExportType, ImageFormat)` | `Studio.cs:366` | `static void ExportAssets(string savePath, List<AssetItem> toExportAssets, AssetGroupOption assetGroupOption, ExportType exportType, ImageFormat imageFormat)` | public | 并行导出 |
| 103 | `Studio.ExportAssetsMap(string, List<AssetEntry>, string, ExportListType)` | `Studio.cs:454` | `static void ExportAssetsMap(string savePath, List<AssetEntry> toExportAssets, string exportListName, ExportListType exportListType)` | public | AssetMap XML/JSON 写文件 |
| 104 | `Studio.MonoBehaviourToTypeTree(MonoBehaviour)` | `Studio.cs:503` | `static TypeTree MonoBehaviourToTypeTree(MonoBehaviour m_MonoBehaviour)` | public | 转 TypeTree |

### 2.3 `Exporter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 105 | `Exporter.ExportTexture2D(AssetItem, string, ImageFormat)` | `Exporter.cs:12` | `static bool ExportTexture2D(AssetItem item, string exportPath, ImageFormat imageFormat)` | public | Texture 导出 |
| 106 | `Exporter.ExportAudioClip(AssetItem, string)` | `Exporter.cs:41` | `static bool ExportAudioClip(AssetItem item, string exportPath)` | public | AudioClip 导出 |
| 107 | `Exporter.ExportShader(AssetItem, string)` | `Exporter.cs:66` | `static bool ExportShader(AssetItem item, string exportPath)` | public | Shader 导出 |
| 108 | `Exporter.ExportTextAsset(AssetItem, string)` | `Exporter.cs:76` | `static bool ExportTextAsset(AssetItem item, string exportPath)` | public | TextAsset 导出 |
| 109 | `Exporter.ExportMonoBehaviour(AssetItem, string)` | `Exporter.cs:93` | `static bool ExportMonoBehaviour(AssetItem item, string exportPath)` | public | MonoBehaviour 导出 |
| 110 | `Exporter.ExportMiHoYoBinData(AssetItem, string)` | `Exporter.cs:109` | `static bool ExportMiHoYoBinData(AssetItem item, string exportPath)` | public | MiHoYoBinData 导出 |
| 111 | `Exporter.ExportFont(AssetItem, string)` | `Exporter.cs:150` | `static bool ExportFont(AssetItem item, string exportPath)` | public | Font 导出 |
| 112 | `Exporter.ExportMesh(AssetItem, string)` | `Exporter.cs:168` | `static bool ExportMesh(AssetItem item, string exportPath)` | public | Mesh → OBJ |
| 113 | `Exporter.ExportVideoClip(AssetItem, string)` | `Exporter.cs:250` | `static bool ExportVideoClip(AssetItem item, string exportPath)` | public | VideoClip 导出 |
| 114 | `Exporter.ExportMovieTexture(AssetItem, string)` | `Exporter.cs:263` | `static bool ExportMovieTexture(AssetItem item, string exportPath)` | public | MovieTexture 导出 |
| 115 | `Exporter.ExportSprite(AssetItem, string, ImageFormat)` | `Exporter.cs:272` | `static bool ExportSprite(AssetItem item, string exportPath, ImageFormat imageFormat)` | public | Sprite 导出 |
| 116 | `Exporter.ExportRawFile(AssetItem, string)` | `Exporter.cs:292` | `static bool ExportRawFile(AssetItem item, string exportPath)` | public | 原始字节 |
| 117 | `Exporter.ExportAnimationClip(AssetItem, string)` | `Exporter.cs:345` | `static bool ExportAnimationClip(AssetItem item, string exportPath)` | public | AnimationClip → .anim |
| 118 | `Exporter.ExportAnimator(AssetItem, string, List<AssetItem>)` | `Exporter.cs:357` | `static bool ExportAnimator(AssetItem item, string exportPath, List<AssetItem> animationList)` | public | Animator → FBX |
| 119 | `Exporter.ExportGameObject(AssetItem, string, List<AssetItem>)` | `Exporter.cs:390` | `static bool ExportGameObject(AssetItem item, string exportPath, List<AssetItem> animationList)` | public | GameObject → FBX（重载） |
| 120 | `Exporter.ExportGameObject(GameObject, string, List<AssetItem>)` | `Exporter.cs:399` | `static bool ExportGameObject(GameObject gameObject, string exportPath, List<AssetItem> animationList)` | public | GameObject → FBX |
| 121 | `Exporter.ExportDumpFile(AssetItem, string)` | `Exporter.cs:454` | `static bool ExportDumpFile(AssetItem item, string exportPath)` | public | Object.Dump() |
| 122 | `Exporter.ExportConvertFile(AssetItem, string, ImageFormat)` | `Exporter.cs:467` | `static bool ExportConvertFile(AssetItem item, string exportPath, ImageFormat imageFormat)` | public | 按 item.Type 分派 |
| 123 | `Exporter.ExportJSONFile(AssetItem, string)` | `Exporter.cs:506` | `static bool ExportJSONFile(AssetItem item, string exportPath)` | public | JSON 序列化 |
| 124 | `Exporter.FixFileName(string)` | `Exporter.cs:518` | `static string FixFileName(string str)` | public | 文件名清洗 |

### 2.4 `Components/CommandLine.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 125 | `CommandLine.Init(string[])` | `CommandLine.cs:14` | `static void Init(string[] args)` | public | CLI 入口 |
| 126 | `CommandLine.RegisterOptions()` | `CommandLine.cs:19` | `static RootCommand RegisterOptions()` | public | 创建 RootCommand |
| 127 | `OptionsBinder` 构造器 | `CommandLine.cs:95` | `OptionsBinder()` | public ctor | 18 个 Option 字段初始化 |
| 128 | `OptionsBinder.ParseKey(string)` | `CommandLine.cs:211` | `byte ParseKey(string value)` | public | 解析 0xNN 或 NN |
| 129 | `OptionsBinder.FilterValidator(OptionResult)` | `CommandLine.cs:224` | `void FilterValidator(OptionResult result)` | public | 校验 regex 合法性 |
| 130 | `OptionsBinder.GetBoundValue(BindingContext)` | `CommandLine.cs:247` | `override Options GetBoundValue(BindingContext bindingContext)` | protected override | 绑定到 Options 对象 |

---

## 3. `AssetStudio.GUI/`

### 3.1 `Studio.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 131 | `Studio.ExtractFolder(string, string)` | `Studio.cs:34` | `static int ExtractFolder(string path, string savePath)` | public | 遍历目录提取 |
| 132 | `Studio.ExtractFile(string[], string)` | `Studio.cs:50` | `static int ExtractFile(string[] fileNames, string savePath)` | public | 批量提取 |
| 133 | `Studio.ExtractFile(string, string)` | `Studio.cs:63` | `static int ExtractFile(string fileName, string savePath)` | public | 单文件提取 |
| 134 | `Studio.UpdateContainers()` | `Studio.cs:205` | `static void UpdateContainers()` | public | GI container 解析 |
| 135 | `Studio.BuildAssetData()` | `Studio.cs:234` | `static (string, List<TreeNode>) BuildAssetData()` | public | GUI 端 AssetData + 树构建 |
| 136 | `Studio.BuildClassStructure()` | `Studio.cs:489` | `static Dictionary<string, SortedDictionary<int, TypeTreeItem>> BuildClassStructure()` | public | ClassID → TypeTree |
| 137 | `Studio.ExportAssets(string, List<AssetItem>, ExportType, bool)` | `Studio.cs:530` | `static Task ExportAssets(string savePath, List<AssetItem> toExportAssets, ExportType exportType, bool openAfterExport)` | public | 异步导出 |
| 138 | `Studio.ExportAssetsList(string, List<AssetItem>, ExportListType)` | `Studio.cs:631` | `static Task ExportAssetsList(string savePath, List<AssetItem> toExportAssets, ExportListType exportListType)` | public | 导出 asset 列表 |
| 139 | `Studio.ExportSplitObjects(string, TreeNodeCollection)` | `Studio.cs:681` | `static Task ExportSplitObjects(string savePath, TreeNodeCollection nodes)` | public | 按 tree node split 导出 |
| 140 | `Studio.ExportAnimatorWithAnimationClip(AssetItem, List<AssetItem>, string)` | `Studio.cs:775` | `static Task ExportAnimatorWithAnimationClip(AssetItem animator, List<AssetItem> animationList, string exportPath)` | public | Animator + anim 导出 |
| 141 | `Studio.ExportObjectsWithAnimationClip(string, TreeNodeCollection, List<AssetItem>)` | `Studio.cs:799` | `static Task ExportObjectsWithAnimationClip(string exportPath, TreeNodeCollection nodes, List<AssetItem> animationList)` | public | GameObject 导出 |
| 142 | `Studio.ExportObjectsMergeWithAnimationClip(string, List<GameObject>, List<AssetItem>)` | `Studio.cs:839` | `static Task ExportObjectsMergeWithAnimationClip(string exportPath, List<GameObject> gameObjects, List<AssetItem> animationList)` | public | 合并导出 |
| 143 | `Studio.ExportNodesWithAnimationClip(string, List<TreeNode>, List<AssetItem>)` | `Studio.cs:864` | `static Task ExportNodesWithAnimationClip(string exportPath, List<TreeNode> nodes, List<AssetItem> animationList)` | public | TreeNode 集合导出 |
| 144 | `Studio.GetSelectedParentNode(TreeNodeCollection, List<GameObject>)` | `Studio.cs:903` | `static void GetSelectedParentNode(TreeNodeCollection nodes, List<GameObject> gameObjects)` | public | 取选中的 GameObject |
| 145 | `Studio.MonoBehaviourToTypeTree(MonoBehaviour)` | `Studio.cs:918` | `static TypeTree MonoBehaviourToTypeTree(MonoBehaviour m_MonoBehaviour)` | public | 转 TypeTree |
| 146 | `Studio.DumpAsset(Object)` | `Studio.cs:936` | `static string DumpAsset(Object obj)` | public | Object → 文本（dump/json） |
| 147 | `Studio.OpenFolderInExplorer(string)` | `Studio.cs:953` | `static void OpenFolderInExplorer(string path)` | public | 打开文件夹 |

### 3.2 `Exporter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 148 | `GUI.Exporter.ExportTexture2D(AssetItem, string)` | `GUI/Exporter.cs:12` | `static bool ExportTexture2D(AssetItem item, string exportPath)` | public | Texture 导出 |
| 149 | `GUI.Exporter.ExportAudioClip(AssetItem, string)` | `GUI/Exporter.cs:41` | `static bool ExportAudioClip(AssetItem item, string exportPath)` | public | AudioClip 导出 |
| 150 | `GUI.Exporter.ExportShader(AssetItem, string)` | `GUI/Exporter.cs:66` | `static bool ExportShader(AssetItem item, string exportPath)` | public | Shader 导出 |
| 151 | `GUI.Exporter.ExportTextAsset(AssetItem, string)` | `GUI/Exporter.cs:76` | `static bool ExportTextAsset(AssetItem item, string exportPath)` | public | TextAsset 导出 |
| 152 | `GUI.Exporter.ExportMonoBehaviour(AssetItem, string)` | `GUI/Exporter.cs:93` | `static bool ExportMonoBehaviour(AssetItem item, string exportPath)` | public | MonoBehaviour 导出 |
| 153 | `GUI.Exporter.ExportMiHoYoBinData(AssetItem, string)` | `GUI/Exporter.cs:109` | `static bool ExportMiHoYoBinData(AssetItem item, string exportPath)` | public | MiHoYoBinData 导出 |
| 154 | `GUI.Exporter.ExportFont(AssetItem, string)` | `GUI/Exporter.cs:150` | `static bool ExportFont(AssetItem item, string exportPath)` | public | Font 导出 |
| 155 | `GUI.Exporter.ExportMesh(AssetItem, string)` | `GUI/Exporter.cs:168` | `static bool ExportMesh(AssetItem item, string exportPath)` | public | Mesh → OBJ |
| 156 | `GUI.Exporter.ExportVideoClip(AssetItem, string)` | `GUI/Exporter.cs:250` | `static bool ExportVideoClip(AssetItem item, string exportPath)` | public | VideoClip 导出 |
| 157 | `GUI.Exporter.ExportMovieTexture(AssetItem, string)` | `GUI/Exporter.cs:263` | `static bool ExportMovieTexture(AssetItem item, string exportPath)` | public | MovieTexture 导出 |
| 158 | `GUI.Exporter.ExportSprite(AssetItem, string)` | `GUI/Exporter.cs:272` | `static bool ExportSprite(AssetItem item, string exportPath)` | public | Sprite 导出 |
| 159 | `GUI.Exporter.ExportRawFile(AssetItem, string)` | `GUI/Exporter.cs:292` | `static bool ExportRawFile(AssetItem item, string exportPath)` | public | 原始字节 |
| 160 | `GUI.Exporter.ExportAnimationClip(AssetItem, string)` | `GUI/Exporter.cs:343` | `static bool ExportAnimationClip(AssetItem item, string exportPath)` | public | AnimationClip → .anim |
| 161 | `GUI.Exporter.ExportAnimator(AssetItem, string, List<AssetItem>)` | `GUI/Exporter.cs:355` | `static bool ExportAnimator(AssetItem item, string exportPath, List<AssetItem> animationList)` | public | Animator → FBX |
| 162 | `GUI.Exporter.ExportGameObject(AssetItem, string, List<AssetItem>)` | `GUI/Exporter.cs:389` | `static bool ExportGameObject(AssetItem item, string exportPath, List<AssetItem> animationList)` | public | GameObject → FBX（重载） |
| 163 | `GUI.Exporter.ExportGameObject(GameObject, string, List<AssetItem>)` | `GUI/Exporter.cs:398` | `static bool ExportGameObject(GameObject gameObject, string exportPath, List<AssetItem> animationList)` | public | GameObject → FBX |
| 164 | `GUI.Exporter.ExportGameObjectMerge(List<GameObject>, string, List<AssetItem>)` | `GUI/Exporter.cs:434` | `static void ExportGameObjectMerge(List<GameObject> gameObject, string exportPath, List<AssetItem> animationList)` | public | 合并 GameObject → FBX |
| 165 | `GUI.Exporter.ExportDumpFile(AssetItem, string)` | `GUI/Exporter.cs:482` | `static bool ExportDumpFile(AssetItem item, string exportPath)` | public | Object.Dump() |
| 166 | `GUI.Exporter.ExportConvertFile(AssetItem, string)` | `GUI/Exporter.cs:500` | `static bool ExportConvertFile(AssetItem item, string exportPath)` | public | 按 item.Type 分派 |
| 167 | `GUI.Exporter.ExportJSONFile(AssetItem, string)` | `GUI/Exporter.cs:539` | `static bool ExportJSONFile(AssetItem item, string exportPath)` | public | JSON 序列化 |
| 168 | `GUI.Exporter.FixFileName(string)` | `GUI/Exporter.cs:551` | `static string FixFileName(string str)` | public | 文件名清洗 |

### 3.3 `MainForm.cs`（核心事件处理函数，Designer 自动生成的不计）

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 169 | `MainForm` 构造器 | `MainForm.cs:84` | `MainForm()` | public ctor | 初始化 WinForms |
| 170 | `MainForm.InitializeExportOptions` | `MainForm.cs:99` | `void InitializeExportOptions()` | private | 设置导出选项 |
| 171 | `MainForm.InitializeLogger` | `MainForm.cs:118` | `void InitializeLogger()` | private | 初始化日志 |
| 172 | `MainForm.InitializeProgressBar` | `MainForm.cs:145` | `void InitializeProgressBar()` | private | 初始化进度条 |
| 173 | `MainForm.InitalizeOptions` | `MainForm.cs:151` | `void InitalizeOptions()` | private | 初始化 AssetMap/Game/TypeFlags |
| 174 | `MainForm.AssetsManager_OnVersionPrompt` | `MainForm.cs:188` | `void AssetsManager_OnVersionPrompt(object sender, VersionPromptEventArgs e)` | private | Unity 版本询问弹窗 |
| 175 | `MainForm.MainForm_DragEnter` | `MainForm.cs:277` | `void MainForm_DragEnter(object sender, DragEventArgs e)` | private | 拖拽高亮 |
| 176 | `MainForm.MainForm_DragDrop` | `MainForm.cs:285` | `void MainForm_DragDrop(object sender, DragEventArgs e)` | private | 拖拽落点 |
| 177 | `MainForm.LoadPaths` | `MainForm.cs:294` | `async void LoadPaths(params string[] paths)` | public | 加载入口 |
| 178 | `MainForm.loadFile_Click` | `MainForm.cs:310` | `async void loadFile_Click(object sender, EventArgs e)` | private | Load File 菜单 |
| 179 | `MainForm.loadFolder_Click` | `MainForm.cs:329` | `async void loadFolder_Click(object sender, EventArgs e)` | private | Load Folder 菜单 |
| 180 | `MainForm.extractFileToolStripMenuItem_Click` | `MainForm.cs:344` | `async void extractFileToolStripMenuItem_Click(object sender, EventArgs e)` | private | Extract File 菜单 |
| 181 | `MainForm.extractFolderToolStripMenuItem_Click` | `MainForm.cs:360` | `async void extractFolderToolStripMenuItem_Click(object sender, EventArgs e)` | private | Extract Folder 菜单 |
| 182 | `MainForm.BuildAssetStructures` | `MainForm.cs:377` | `async void BuildAssetStructures()` | private | 树 + 列表 + 类型树构建 |
| 183 | `MainForm.PreviewAsset` | `MainForm.cs:923` | `void PreviewAsset(AssetItem assetItem)` | private | 按 Type 分派预览 |
| 184 | `MainForm.PreviewTexture2D` | `MainForm.cs:989` | `void PreviewTexture2D(AssetItem assetItem, Texture2D m_Texture2D)` | private | 纹理预览 |
| 185 | `MainForm.PreviewAudioClip` | `MainForm.cs:1047` | `void PreviewAudioClip(AssetItem assetItem, AudioClip m_AudioClip)` | private | 音频预览（FMOD） |
| 186 | `MainForm.PreviewShader` | `MainForm.cs:1173` | `void PreviewShader(Shader m_Shader)` | private | Shader 文本预览 |
| 187 | `MainForm.PreviewTextAsset` | `MainForm.cs:1185` | `void PreviewTextAsset(TextAsset m_TextAsset)` | private | TextAsset 预览 |
| 188 | `MainForm.PreviewMonoBehaviour` | `MainForm.cs:1192` | `void PreviewMonoBehaviour(MonoBehaviour m_MonoBehaviour)` | private | MonoBehaviour JSON 预览 |
| 189 | `MainForm.PreviewFont` | `MainForm.cs:1204` | `void PreviewFont(Font m_Font)` | private | Font 预览（PrivateFontCollection） |
| 190 | `MainForm.PreviewMesh` | `MainForm.cs:1254` | `void PreviewMesh(Mesh m_Mesh)` | private | Mesh OpenGL 预览 |
| 191 | `MainForm.PreviewGameObject` | `MainForm.cs:1404` | `void PreviewGameObject(GameObject m_GameObject)` | private | GameObject OpenGL 预览 |
| 192 | `MainForm.PreviewAnimator` | `MainForm.cs:1419` | `void PreviewAnimator(Animator m_Animator)` | private | Animator OpenGL 预览 |
| 193 | `MainForm.PreviewAnimationClip` | `MainForm.cs:1435` | `void PreviewAnimationClip(AnimationClip clip)` | private | AnimationClip 文本预览 |
| 194 | `MainForm.PreviewModel(ModelConverter)` | `MainForm.cs:1443` | `void PreviewModel(ModelConverter model)` | private | 通用 Model 预览 |
| 195 | `MainForm.PreviewSprite` | `MainForm.cs:1521` | `void PreviewSprite(AssetItem assetItem, Sprite m_Sprite)` | private | Sprite 预览 |
| 196 | `MainForm.PreviewTexture` | `MainForm.cs:1537` | `void PreviewTexture(DirectBitmap bitmap)` | private | 设置预览背景图 |
| 197 | `MainForm.PreviewText` | `MainForm.cs:1548` | `void PreviewText(string text)` | private | 设置 textPreviewBox |
| 198 | `MainForm.SetProgressBarValue` | `MainForm.cs:1554` | `void SetProgressBarValue(int value)` | private | UI 线程更新进度 |
| 199 | `MainForm.StatusStripUpdate` | `MainForm.cs:1568` | `void StatusStripUpdate(string statusText)` | private | UI 线程更新状态栏 |
| 200 | `MainForm.ResetForm` | `MainForm.cs:1581` | `void ResetForm()` | public | 清空 UI 状态 |
| 201 | `MainForm.FilterAssetList` | `MainForm.cs:1931` | `void FilterAssetList()` | private | 按类型/正则过滤 |
| 202 | `MainForm.UpdateAssetCountStatus` | `MainForm.cs:1991` | `void UpdateAssetCountStatus()` | private | 更新 selected/total 计数 |
| 203 | `MainForm.ExportAssets(ExportFilter, ExportType)` | `MainForm.cs:2052` | `async void ExportAssets(ExportFilter type, ExportType exportType)` | private | 菜单导出触发 |
| 204 | `MainForm.ExportAssetsList(ExportFilter)` | `MainForm.cs:2084` | `void ExportAssetsList(ExportFilter type)` | private | 导出 asset 列表 |
| 205 | `MainForm.specifyGame_SelectedIndexChanged` | `MainForm.cs:2289` | `void specifyGame_SelectedIndexChanged(object sender, EventArgs e)` | private | 切换 Game |
| 206 | `MainForm.specifyNameComboBox_SelectedIndexChanged` | `MainForm.cs:2309` | `async void specifyNameComboBox_SelectedIndexChanged(object sender, EventArgs e)` | private | 切换 CABMap |
| 207 | `MainForm.buildMapToolStripMenuItem_Click` | `MainForm.cs:2332` | `async void buildMapToolStripMenuItem_Click(object sender, EventArgs e)` | private | 构建 CABMap |
| 208 | `MainForm.buildBothToolStripMenuItem_Click` | `MainForm.cs:2387` | `async void buildBothToolStripMenuItem_Click(object sender, EventArgs e)` | private | 构建 CABMap + AssetMap |
| 209 | `MainForm.clearMapToolStripMenuItem_Click` | `MainForm.cs:2451` | `void clearMapToolStripMenuItem_Click(object sender, EventArgs e)` | private | 删除 CABMap |
| 210 | `MainForm.resetToolStripMenuItem_Click` | `MainForm.cs:2477` | `void resetToolStripMenuItem_Click(object sender, EventArgs e)` | private | 重置 |
| 211 | `MainForm.loadAIToolStripMenuItem_Click` | `MainForm.cs:2535` | `async void loadAIToolStripMenuItem_Click(object sender, EventArgs e)` | private | 加载 AI asset_index |
| 212 | `MainForm.loadCABMapToolStripMenuItem_Click` | `MainForm.cs:2556` | `async void loadCABMapToolStripMenuItem_Click(object sender, EventArgs e)` | private | 加载 CABMap |
| 213 | `MainForm.buildAssetMapToolStripMenuItem_Click` | `MainForm.cs:2575` | `async void buildAssetMapToolStripMenuItem_Click(object sender, EventArgs e)` | private | 构建 AssetMap |
| 214 | `MainForm.loadAssetMapToolStripMenuItem_Click` | `MainForm.cs:2617` | `void loadAssetMapToolStripMenuItem_Click(object sender, EventArgs e)` | private | 打开 AssetBrowser |
| 215 | `MainForm.specifyUnityCNKey_Click` | `MainForm.cs:2623` | `void specifyUnityCNKey_Click(object sender, EventArgs e)` | private | 打开 UnityCNForm |
| 216 | `MainForm.FMODinit` | `MainForm.cs:2630` | `void FMODinit()` | private | FMOD 系统初始化 |
| 217 | `MainForm.FMODreset` | `MainForm.cs:2655` | `void FMODreset()` | private | FMOD 状态重置 |
| 218 | `MainForm.FMODplayButton_Click` | `MainForm.cs:2671` | `void FMODplayButton_Click(object sender, EventArgs e)` | private | FMOD 播放 |
| 219 | `MainForm.FMODpauseButton_Click` | `MainForm.cs:2713` | `void FMODpauseButton_Click(object sender, EventArgs e)` | private | FMOD 暂停 |
| 220 | `MainForm.FMODstopButton_Click` | `MainForm.cs:2746` | `void FMODstopButton_Click(object sender, EventArgs e)` | private | FMOD 停止 |
| 221 | `MainForm.FMODloopButton_CheckedChanged` | `MainForm.cs:2771` | `void FMODloopButton_CheckedChanged(object sender, EventArgs e)` | private | FMOD 循环模式 |
| 222 | `MainForm.FMODvolumeBar_ValueChanged` | `MainForm.cs:2805` | `void FMODvolumeBar_ValueChanged(object sender, EventArgs e)` | private | FMOD 音量 |
| 223 | `MainForm.FMODprogressBar_Scroll` | `MainForm.cs:2813` | `void FMODprogressBar_Scroll(object sender, EventArgs e)` | private | FMOD 进度条拖动 |
| 224 | `MainForm.FMODprogressBar_MouseDown` | `MainForm.cs:2822` | `void FMODprogressBar_MouseDown(object sender, MouseEventArgs e)` | private | FMOD 鼠标按下 |
| 225 | `MainForm.FMODprogressBar_MouseUp` | `MainForm.cs:2827` | `void FMODprogressBar_MouseUp(object sender, MouseEventArgs e)` | private | FMOD 鼠标松开 |
| 226 | `MainForm.timer_Tick` | `MainForm.cs:2850` | `void timer_Tick(object sender, EventArgs e)` | private | FMOD 计时器 |
| 227 | `MainForm.ERRCHECK(FMOD.RESULT)` | `MainForm.cs:2887` | `bool ERRCHECK(FMOD.RESULT result)` | private | FMOD 错误检查 |
| 228 | `MainForm.InitOpenTK` | `MainForm.cs:2900` | `void InitOpenTK()` | private | OpenGL 初始化 |
| 229 | `MainForm.LoadShader(string, ShaderType, int, out int)` | `MainForm.cs:2927` | `static void LoadShader(string filename, ShaderType type, int program, out int address)` | private static | 编译 GL shader |
| 230 | `MainForm.CreateVBO(out int, Vector3[], int)` | `MainForm.cs:2937` | `static void CreateVBO(out int vboAddress, Vector3[] data, int address)` | private static | 创建 VBO |
| 231 | `MainForm.CreateVBO(out int, Vector4[], int)` | `MainForm.cs:2949` | `static void CreateVBO(out int vboAddress, Vector4[] data, int address)` | private static | 创建 VBO |
| 232 | `MainForm.CreateVBO(out int, Matrix4, int)` | `MainForm.cs:2961` | `static void CreateVBO(out int vboAddress, Matrix4 data, int address)` | private static | 创建 VBO |
| 233 | `MainForm.CreateEBO(out int, int[])` | `MainForm.cs:2967` | `static void CreateEBO(out int address, int[] data)` | private static | 创建 EBO |
| 234 | `MainForm.CreateVAO` | `MainForm.cs:2977` | `void CreateVAO()` | private | 创建 VAO |
| 235 | `MainForm.ChangeGLSize(Size)` | `MainForm.cs:3001` | `void ChangeGLSize(Size size)` | private | 调整 viewport |
| 236 | `MainForm.glControl_Load` | `MainForm.cs:3017` | `void glControl_Load(object sender, EventArgs e)` | private | GL 控件加载 |
| 237 | `MainForm.glControl_Paint` | `MainForm.cs:3023` | `void glControl_Paint(object sender, PaintEventArgs e)` | private | GL 绘制 |
| 238 | `MainForm.glControl_MouseWheel` | `MainForm.cs:3057` | `void glControl_MouseWheel(object sender, MouseEventArgs e)` | private | 滚轮缩放 |
| 239 | `MainForm.glControl_MouseDown` | `MainForm.cs:3066` | `void glControl_MouseDown(object sender, MouseEventArgs e)` | private | 鼠标按下 |
| 240 | `MainForm.glControl_MouseMove` | `MainForm.cs:3080` | `void glControl_MouseMove(object sender, MouseEventArgs e)` | private | 鼠标移动 |
| 241 | `MainForm.glControl_MouseUp` | `MainForm.cs:3105` | `void glControl_MouseUp(object sender, MouseEventArgs e)` | private | 鼠标松开 |

---

## 4. `AssetStudio.Utility/`

### 4.1 `ModelConverter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 242 | `ModelConverter(GameObject, Options, AnimationClip[])` | `ModelConverter.cs:27` | `ModelConverter(GameObject m_GameObject, Options options, AnimationClip[] animationList)` | public ctor | GameObject → Imported |
| 243 | `ModelConverter(string, List<GameObject>, Options, AnimationClip[])` | `ModelConverter.cs:53` | `ModelConverter(string rootName, List<GameObject> m_GameObjects, Options options, AnimationClip[] animationList)` | public ctor | 合并 GO |
| 244 | `ModelConverter(Animator, Options, AnimationClip[])` | `ModelConverter.cs:84` | `ModelConverter(Animator m_Animator, Options options, AnimationClip[] animationList)` | public ctor | Animator → Imported |

### 4.2 `Texture2DConverter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 245 | `Texture2DConverter(Texture2D)` | `Texture2DConverter.cs:18` | `Texture2DConverter(Texture2D m_Texture2D)` | public ctor | 构造 |
| 246 | `Texture2DConverter.DecodeTexture2D(byte[])` | `Texture2DConverter.cs:29` | `bool DecodeTexture2D(byte[] bytes)` | public | 主解码入口 |
| 247 | `Texture2DConverter.DownScaleFrom16BitTo8Bit(ushort)` | `Texture2DConverter.cs:653` | `static byte DownScaleFrom16BitTo8Bit(ushort component)` | public static | 16→8 位转换 |

### 4.3 `ShaderConverter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 248 | `ShaderConverter.Convert(this Shader)` | `ShaderConverter.cs:18` | `static string Convert(this Shader shader)` | public static extension | Shader → 文本 |
| 249 | `ShaderConverter.GetPlatformString(ShaderCompilerPlatform)` | `ShaderConverter.cs:825` | `static string GetPlatformString(ShaderCompilerPlatform platform)` | public static | platform enum → 字符串 |
| 250 | `ShaderSubProgramEntry(EndianBinaryReader, int[])` | `ShaderConverter.cs:897` | `ShaderSubProgramEntry(EndianBinaryReader reader, int[] version)` | public ctor | 解析 SubProgram 索引 |
| 251 | `ShaderProgram(EndianBinaryReader, Shader)` | `ShaderConverter.cs:915` | `ShaderProgram(EndianBinaryReader reader, Shader shader)` | public ctor | 解析 ShaderProgram |
| 252 | `ShaderProgram.Read(EndianBinaryReader, int)` | `ShaderConverter.cs:930` | `void Read(EndianBinaryReader reader, int segment)` | public | 读 segment |
| 253 | `ShaderProgram.Export(string)` | `ShaderConverter.cs:943` | `string Export(string shader)` | public | 替换 GpuProgramIndex |
| 254 | `ShaderSubProgram(EndianBinaryReader, bool)` | `ShaderConverter.cs:963` | `ShaderSubProgram(EndianBinaryReader reader, bool hasUpdatedGpuProgram)` | public ctor | 解析 SubProgram |
| 255 | `ShaderSubProgram.Export()` | `ShaderConverter.cs:1006` | `string Export()` | public | 输出 |
| 256 | `ShaderSubProgram.ComputeHash64(Span<byte>)` | `ShaderConverter.cs:1158` | `ulong ComputeHash64(Span<byte> data)` | public | FNV-1a 64 位哈希 |
| 257 | `HLSLDecompiler.DecompileShader(byte[], int, out string)` | `ShaderConverter.cs:1177` | `static void DecompileShader(byte[] shaderByteCode, int shaderByteCodeSize, out string hlslText)` | public static | 调用 HLSLDecompiler 原生 DLL |

### 4.4 `AssemblyLoader.cs` (常用入口)

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 258 | `AssemblyLoader.Load(string folder)` | `AssetStudio.Utility/AssemblyLoader.cs` | `void Load(string folder)` | public | 加载文件夹下所有 dll |
| 259 | `AssemblyLoader.Clear` | `AssetStudio.Utility/AssemblyLoader.cs` | `void Clear()` | public | 清空缓存 |

### 4.5 `MonoBehaviourConverter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 260 | `MonoBehaviourConverter.Convert(MonoBehaviour, ...)` | `AssetStudio.Utility/MonoBehaviourConverter.cs` | `Type Convert(MonoBehaviour m_MonoBehaviour, ...)` | public | MonoBehaviour → Type |

### 4.6 `TypeDefinitionConverter.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 261 | `TypeDefinitionConverter.ConvertToTypeTree(...)` | `AssetStudio.Utility/TypeDefinitionConverter.cs` | `TypeTree ConvertToTypeTree(...)` | public | Cecil TypeDefinition → TypeTree |

---

## 5. `AssetStudio/` — 关键 helpers（参考用）

### 5.1 `TypeFlags.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 262 | `TypeFlags.SetTypes(Dictionary<ClassIDType, (bool, bool)>)` | `TypeFlags.cs:9` | `static void SetTypes(Dictionary<ClassIDType, (bool, bool)> types)` | public | 批量设置 |
| 263 | `TypeFlags.SetType(ClassIDType, bool, bool)` | `TypeFlags.cs:14` | `static void SetType(ClassIDType type, bool parse, bool export)` | public | 单个设置 |
| 264 | `TypeFlags.CanParse(this ClassIDType)` | `TypeFlags.cs:20` | `static bool CanParse(this ClassIDType type)` | public extension | 是否参与 Parse |
| 265 | `TypeFlags.CanExport(this ClassIDType)` | `TypeFlags.cs:34` | `static bool CanExport(this ClassIDType type)` | public extension | 是否参与 Export |

### 5.2 `ResourceIndex.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 266 | `ResourceIndex.FromFile(string)` | `ResourceIndex.cs:13` | `static void FromFile(string path)` | public | 从文件加载 |
| 267 | `ResourceIndex.Clear` | `ResourceIndex.cs:64` | `static void Clear()` | public | 清空 |
| 268 | `ResourceIndex.GetContainer(uint, uint)` | `ResourceIndex.cs:75` | `static string GetContainer(uint id, uint last)` | public | 查 container 路径 |

### 5.3 `UnityCNManager.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 269 | `UnityCNManager.SaveEntries(List<UnityCN.Entry>)` | `UnityCNManager.cs:21` | `static void SaveEntries(List<UnityCN.Entry> entries)` | public | 持久化 keys |
| 270 | `UnityCNManager.SetKey(int)` | `UnityCNManager.cs:30` | `static void SetKey(int index)` | public | 全局 key |
| 271 | `UnityCNManager.TryGetEntry(int, out UnityCN.Entry)` | `UnityCNManager.cs:50` | `static bool TryGetEntry(int index, out UnityCN.Entry key)` | public | 查 entry |

### 5.4 `Crypto/UnityCN.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 272 | `UnityCN.SetKey(Entry)` | `UnityCN.cs:50` | `static bool SetKey(Entry entry)` | public static | 设置解密 key |
| 273 | `UnityCN.DecryptBlock(Span<byte>, int, int)` | `UnityCN.cs:70` | `void DecryptBlock(Span<byte> bytes, int size, int index)` | public | 块级解密 |
| 274 | `UnityCN.Entry.Validate()` | `UnityCN.cs:147` | `bool Validate()` | public | key 验证 |

### 5.5 `Crypto/BlkUtils.cs`、`Crypto/Mr0kUtils.cs`、`Crypto/AES.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 275 | `BlkUtils.Decrypt(FileReader, Blk)` | `BlkUtils.cs:14` | `static XORStream Decrypt(FileReader reader, Blk blk)` | public | Blk 解密 |
| 276 | `Mr0kUtils.Decrypt(Span<byte>, Mr0k)` | `Mr0kUtils.cs:12` | `static Span<byte> Decrypt(Span<byte> data, Mr0k mr0k)` | public | Mr0k 解密 |
| 277 | `Mr0kUtils.IsMr0k(ReadOnlySpan<byte>)` | `Mr0kUtils.cs:73` | `static bool IsMr0k(ReadOnlySpan<byte> data)` | public | 是否 Mr0k 头 |
| 278 | `AES.Decrypt(byte[], byte[])` | `AES.cs:51` | `static void Decrypt(byte[] m, byte[] keys)` | public | AES 解密 |
| 279 | `FairGuardUtils.Decrypt(Span<byte>)` | `FairGuardUtils.cs:9` | `static void Decrypt(Span<byte> bytes)` | public | FairGuard 解密 |
| 280 | `NetEaseUtils.DecryptWithoutHeader(Span<byte>)` | `NetEaseUtils.cs` | `static void DecryptWithoutHeader(Span<byte>)` | public | NetEase 无头 |
| 281 | `NetEaseUtils.DecryptWithHeader(Span<byte>)` | `NetEaseUtils.cs` | `static void DecryptWithHeader(Span<byte>)` | public | NetEase 带头 |
| 282 | `OPFPUtils.Decrypt(Span<byte>, string)` | `OPFPUtils.cs:13` | `static void Decrypt(Span<byte> data, string path)` | public | OPFP |

### 5.6 `EndianBinaryReader.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 283 | `EndianBinaryReader.AlignStream()` | `EndianBinaryReader.cs:136` | `void AlignStream()` | public | 对齐 |
| 284 | `EndianBinaryReader.AlignStream(int)` | `EndianBinaryReader.cs:141` | `void AlignStream(int alignment)` | public | 对齐 N |
| 285 | `EndianBinaryReader.ReadAlignedString()` | `EndianBinaryReader.cs:151` | `string ReadAlignedString()` | public | 读 aligned string |
| 286 | `EndianBinaryReader.ReadStringToNull(int)` | `EndianBinaryReader.cs:164` | `string ReadStringToNull(int maxLength = 32767)` | public | 读 C 字符串 |
| 287 | `EndianBinaryReader.ReadQuaternion` | `EndianBinaryReader.cs:181` | `Quaternion ReadQuaternion()` | public | 读 Quaternion |
| 288 | `EndianBinaryReader.ReadVector2/3/4/Color4/Matrix/Float/Mhy*` | `EndianBinaryReader.cs:186..223` | 多种 | public | 类型化读取 |

### 5.7 `FileReader.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 289 | `FileReader.PreProcessing(this FileReader, Game)` | `FileReader.cs:163` | `static FileReader PreProcessing(this FileReader reader, Game game)` | public extension | 检测并解密 |

### 5.8 `Progress.cs` / `Logger.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 290 | `Progress.Reset()` | `Progress.cs:11` | `static void Reset()` | public | 重置进度 |
| 291 | `Progress.Report(int, int)` | `Progress.cs:23` | `static void Report(int current, int total)` | public | 报告进度 |
| 292 | `Logger.Verbose/Debug/Info/Warning/Error(...)` | `Logger.cs` | `static void Verbose(...)` 等 | public | 日志输出 |

### 5.9 `AIVersionManager.cs`

| # | 函数 | 位置 | 签名 | 类别 | 简要 |
|---|---|---|---|---|---|
| 293 | `AIVersionManager.GetVersions()` | `AIVersionManager.cs:34` | `static List<(string, bool)> GetVersions()` | public | 取版本列表 |
| 294 | `AIVersionManager.FetchVersions()` | `AIVersionManager.cs` | `static Task<bool> FetchVersions()` | public | 拉取 |
| 295 | `AIVersionManager.FetchAI(string)` | `AIVersionManager.cs` | `static Task<string> FetchAI(string)` | public | 拉取指定版本 |

---

## 总结

| 模块 | 函数数 |
|---|---|
| `AssetStudio` 核心库 | 95+（含 helpers） |
| `AssetStudio.CLI` | 38 |
| `AssetStudio.GUI` | 75+（含 WinForms 事件 + FMOD + GL） |
| `AssetStudio.Utility` | 18+ |
| **总计** | **≥ 295** |

所有核心 `AssetsManager.cs` / `BundleFile.cs` / `SerializedFile.cs` / `ImportHelper.cs` / `AssetsHelper.cs` / `GameManager.cs` / CLI `Program.cs` / CLI `Studio.cs` / CLI `Exporter.cs` / CLI `CommandLine.cs` / GUI `Studio.cs` / GUI `Exporter.cs` / GUI `MainForm.cs`（核心事件）/ `ModelConverter.cs` / `Texture2DConverter.cs` / `ShaderConverter.cs` 中的 public/internal 函数 **均已覆盖**。

详细说明参见 [08_functions_detail/](08_functions_detail/) 下的对应文件。