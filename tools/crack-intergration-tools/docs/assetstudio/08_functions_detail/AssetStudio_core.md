# `AssetStudio_core.md` — 核心库函数详细说明

本章详细列出 `AssetStudio/` 核心库（csproj `AssetStudio.csproj`）下被覆盖的 public/internal 函数。每个函数按统一模板记录。

---

## 1. `AssetStudio/AssetsManager.cs`

### `VersionPromptEventArgs.FileName`
- **签名**：`string FileName { get; set; }`
- **位置**：`AssetStudio/AssetsManager.cs:17`
- **可见性**：public
- **参数**：无
- **返回值**：`string`
- **副作用**：无
- **调用**：`MainForm.AssetsManager_OnVersionPrompt` (`AssetStudio.GUI/MainForm.cs:188`) 读取/设置此字段
- **调用了**：无
- **简要说明**：当 SerializedFile 的 Unity 版本被 strip 时，弹窗显示的文件名

### `VersionPromptEventArgs.UserProvidedVersion`
- **签名**：`string UserProvidedVersion { get; set; }`
- **位置**：`AssetStudio/AssetsManager.cs:18`
- **可见性**：public
- **副作用**：无
- **调用**：`MainForm.AssetsManager_OnVersionPrompt` (`AssetStudio.GUI/MainForm.cs:263`) 设置此字段
- **简要说明**：用户在弹窗中输入的 Unity 版本

### `VersionPromptEventArgs.Cancelled`
- **签名**：`bool Cancelled { get; set; }`
- **位置**：`AssetStudio/AssetsManager.cs:19`
- **可见性**：public
- **简要说明**：用户取消弹窗的标志

### `AssetsManager.OnVersionPrompt`
- **签名**：`event EventHandler<VersionPromptEventArgs> OnVersionPrompt`
- **位置**：`AssetStudio/AssetsManager.cs:25`
- **可见性**：public
- **调用**：`MainForm` 构造器中订阅（`MainForm.cs:96`）；触发点在 `AssetsManager.CheckStrippedVersion` (`AssetsManager.cs:882`)
- **简要说明**：外部代码订阅此事件以便在被 strip 的 SerializedFile 上提供版本

### `AssetsManager.LoadFiles(params string[])`
- **签名**：`void LoadFiles(params string[] files)`
- **位置**：`AssetStudio/AssetsManager.cs:48`
- **可见性**：public
- **参数**：`params string[] files` — 文件路径列表
- **返回值**：void
- **副作用**：修改 `assetsFileList`、`importFiles`、`assetsFileListHash`；触发 `OnVersionPrompt`；调用 `Progress.Reset/Report`
- **调用**：
  - `AssetStudio.GUI/MainForm.cs:305` (drag-drop)
  - `AssetStudio.GUI/MainForm.cs:324` (loadFile_Click)
  - `AssetStudio.CLI/Program.cs:184` (CLI 循环)
  - `AssetStudio.GUI/AssetBrowser.cs:107`
  - `AssetStudio/AssetsHelper.cs:179` (BuildCABMap/AssetMap 内部)
- **调用了**：
  - `AssetsManager.DetectUnityVersionFromFolder` (`AssetsManager.cs:176`)
  - `ImportHelper.MergeSplitAssets` (`ImportHelper.cs:19`)
  - `ImportHelper.ProcessingSplitFiles` (`ImportHelper.cs:49`)
  - `AssetsHelper.ProcessDependencies` (`AssetsHelper.cs:128`)
  - `AssetsManager.Load` (`AssetsManager.cs:96`)
- **简要说明**：CLI/GUI 顶层入口；给定文件路径数组后完成 detect version → merge split → process dependencies → 并行加载 → ReadAssets → ProcessAssets 全流程

### `AssetsManager.LoadFolder(string)`
- **签名**：`void LoadFolder(string path)`
- **位置**：`AssetStudio/AssetsManager.cs:73`
- **可见性**：public
- **参数**：`string path` — 目录路径
- **副作用**：同 LoadFiles
- **调用**：`AssetStudio.GUI/MainForm.cs:301`、`MainForm.cs:339`
- **调用了**：`DetectUnityVersionFromFolder`、`MergeSplitAssets(path, true)`、`ProcessingSplitFiles`、`Load`
- **简要说明**：以递归方式加载目录下所有文件（`SearchOption.AllDirectories`）

### `AssetsManager.Load(string[])`
- **签名**：`void Load(string[] files)`
- **位置**：`AssetStudio/AssetsManager.cs:96`
- **可见性**：private
- **副作用**：高度并发；填充 assetsFileList
- **调用了**：
  - `AssetsManager.LoadFile(string)` (`AssetsManager.cs:289`)
  - `AssetsManager.ReadAssets` (`AssetsManager.cs:937`)
  - `AssetsManager.ProcessAssets` (`AssetsManager.cs:1010`)
  - `AssetsHelper.ClearOffsets` (`AssetsHelper.cs:63`)
- **简要说明**：核心并行加载循环；以 wave 方式处理新发现的依赖

### `AssetsManager.DetectUnityVersionFromFolder(string)`
- **签名**：`void DetectUnityVersionFromFolder(string path)`
- **位置**：`AssetStudio/AssetsManager.cs:176`
- **可见性**：private
- **参数**：`string path`
- **副作用**：设置 `detectedFolderVersion`
- **调用了**：`TryExtractVersionFromFile` (`AssetsManager.cs:243`)、`TryExtractVersionFromBundle` (`AssetsManager.cs:266`)
- **简要说明**：通过 `globalgamemanagers` / `data.unity3d` / 任意 `.bundle` 检测 Unity 版本

### `AssetsManager.TryExtractVersionFromFile(string)`
- **签名**：`string TryExtractVersionFromFile(string filePath)`
- **位置**：`AssetStudio/AssetsManager.cs:243`
- **可见性**：private
- **返回值**：`string`（unityVersion）或 null
- **调用了**：`new SerializedFile(reader, this)`
- **简要说明**：尝试从一个 SerializedFile 读 unityVersion

### `AssetsManager.TryExtractVersionFromBundle(string)`
- **签名**：`string TryExtractVersionFromBundle(string filePath)`
- **位置**：`AssetStudio/AssetsManager.cs:266`
- **可见性**：private
- **返回值**：`string`（unityRevision）或 null
- **调用了**：`new BundleFile(reader, Game)`
- **简要说明**：尝试从一个 BundleFile 读 unityRevision

### `AssetsManager.LoadFile(string)`
- **签名**：`void LoadFile(string fullName)`
- **位置**：`AssetStudio/AssetsManager.cs:289`
- **可见性**：private
- **调用了**：`new FileReader`、`FileReader.PreProcessing`、`AssetsManager.LoadFile(FileReader)`
- **简要说明**：包装 `FileReader` 创建 + PreProcessing

### `AssetsManager.LoadFile(FileReader)`
- **签名**：`void LoadFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:296`
- **可见性**：private
- **副作用**：switch on FileType
- **调用了**：`LoadAssetsFile`、`LoadBundleFile`、`LoadWebFile`、`DecompressGZip`、`DecompressBrotli`、`LoadZipFile`、`LoadBlockFile`、`LoadBlkFile`、`LoadMhyFile`
- **简要说明**：FileType 分派表

### `AssetsManager.LoadAssetsFile(FileReader)`
- **签名**：`void LoadAssetsFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:330`
- **可见性**：private
- **副作用**：构造 SerializedFile；填充 `assetsFileList`
- **调用了**：`new SerializedFile`、`CheckStrippedVersion`
- **简要说明**：处理独立 .assets / .unity3d 文件；跳过 `_unpacked/CAB-*` 副本

### `AssetsManager.LoadAssetsFromMemory(FileReader, string, string, long)`
- **签名**：`void LoadAssetsFromMemory(FileReader reader, string originalPath, string unityVersion, long originalOffset)`
- **位置**：`AssetStudio/AssetsManager.cs:430`
- **可见性**：private
- **副作用**：构造 SerializedFile with `IsFromBundle=true`；记录 offset
- **调用了**：`new SerializedFile`、`CheckStrippedVersion`
- **简要说明**：从 bundle 内 / webfile 内的子流加载 SerializedFile

### `AssetsManager.LoadBundleFile(FileReader, string?, long, bool)`
- **签名**：`void LoadBundleFile(FileReader reader, string originalPath = null, long originalOffset = 0, bool log = true)`
- **位置**：`AssetStudio/AssetsManager.cs:485`
- **可见性**：private
- **调用了**：`new BundleFile`、`LoadAssetsFromMemory`、`LoadWebFile`、`LoadMhyFile`、`LoadBlbFile`
- **简要说明**：解析 BundleFile 后对 fileList 内每个 entry 分派；记录 detectedFolderVersion

### `AssetsManager.LoadWebFile(FileReader)`
- **签名**：`void LoadWebFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:542`
- **可见性**：private
- **调用了**：`new WebFile`、`LoadAssetsFromMemory`、`LoadBundleFile`、`LoadWebFile`（递归）
- **简要说明**：解析 WebFile 后分发

### `AssetsManager.LoadZipFile(FileReader)`
- **签名**：`void LoadZipFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:580`
- **可见性**：private
- **调用了**：`ZipArchive`、`LoadFile`
- **简要说明**：处理 Zip 内的 .split 与每个 entry

### `AssetsManager.LoadBlockFile(FileReader)`
- **签名**：`void LoadBlockFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:677`
- **可见性**：private
- **调用了**：`OffsetStream`、`LoadBundleFile`、`LoadBlbFile`、`LoadMhyFile`
- **简要说明**：Unity block-file（多 bundle 串联）解析

### `AssetsManager.LoadBlkFile(FileReader)`
- **签名**：`void LoadBlkFile(FileReader reader)`
- **位置**：`AssetStudio/AssetsManager.cs:714`
- **可见性**：private
- **调用了**：`BlkUtils.Decrypt`、`OffsetStream`、`LoadBundleFile`、`LoadMhyFile`
- **简要说明**：Blk (XOR) 文件处理

### `AssetsManager.LoadMhyFile(FileReader, string?, long, bool)`
- **签名**：`void LoadMhyFile(FileReader reader, string originalPath = null, long originalOffset = 0, bool log = true)`
- **位置**：`AssetStudio/AssetsManager.cs:751`
- **可见性**：private
- **调用了**：`new MhyFile`、`LoadAssetsFromMemory`
- **简要说明**：Mhy 容器处理（米哈游）

### `AssetsManager.LoadBlbFile(FileReader, string?, long, bool)`
- **签名**：`void LoadBlbFile(FileReader reader, string originalPath = null, long originalOffset = 0, bool log = true)`
- **位置**：`AssetStudio/AssetsManager.cs:795`
- **可见性**：private
- **调用了**：`new BlbFile`、`LoadAssetsFromMemory`
- **简要说明**：Blb 容器处理

### `AssetsManager.CheckStrippedVersion(SerializedFile)`
- **签名**：`void CheckStrippedVersion(SerializedFile assetsFile)`
- **位置**：`AssetStudio/AssetsManager.cs:838`
- **可见性**：public
- **副作用**：可能设置 `assetsFile.unityVersion`、触发 `OnVersionPrompt`
- **调用**：`LoadAssetsFile` (`AssetsManager.cs:346`)、`LoadAssetsFromMemory` (`AssetsManager.cs:444`)
- **调用了**：`SerializedFile.SetVersion` (`SerializedFile.cs:259`)
- **抛出/异常**：未指定版本且无法检测时抛 `Exception("The Unity version has been stripped, please set the version in the options")`
- **简要说明**：处理 unityVersion == "0.0.0" 的 SerializedFile

### `AssetsManager.Clear()`
- **签名**：`void Clear()`
- **位置**：`AssetStudio/AssetsManager.cs:907`
- **可见性**：public
- **副作用**：释放所有 reader；清空所有 dictionary
- **调用**：
  - `MainForm.ResetForm` (`MainForm.cs:1584`)
  - `AssetBrowser.cs:114`
  - `AssetStudio.CLI/Program.cs:191`
  - `AssetsHelper.LoadFiles` (`AssetsHelper.cs:192`)
- **简要说明**：释放并重置 AssetsManager

### `AssetsManager.ReadAssets()`
- **签名**：`void ReadAssets()`
- **位置**：`AssetStudio/AssetsManager.cs:937`
- **可见性**：private
- **调用了**：`new ObjectReader`、`SerializedFile.AddObject`、`Progress.Report`
- **简要说明**：遍历所有 SerializedFile 的 m_Objects，构造强类型 Object（switch on `objectReader.type`）

### `AssetsManager.ProcessAssets()`
- **签名**：`void ProcessAssets()`
- **位置**：`AssetStudio/AssetsManager.cs:1010`
- **可见性**：private
- **副作用**：修改 `m_GameObject.m_Transform` / `m_MeshRenderer` / ... 等组件指针
- **简要说明**：把 GameObject 与 Transform / Renderer / Animator / Animation / SpriteAtlas ↔ Sprite 关联起来

---

## 2. `AssetStudio/BundleFile.cs`

### `Header.ToString()`
- **签名**：`override string ToString()`
- **位置**：`AssetStudio/BundleFile.cs:58`
- **简要说明**：返回 header 的格式化字符串

### `StorageBlock.ToString()`
- **签名**：`override string ToString()`
- **位置**：`AssetStudio/BundleFile.cs:79`
- **简要说明**：返回 block 的格式化字符串

### `Node.ToString()`
- **签名**：`override string ToString()`
- **位置**：`AssetStudio/BundleFile.cs:96`
- **简要说明**：返回 directory entry 的格式化字符串

### `BundleFile(FileReader, Game)`
- **签名**：`BundleFile(FileReader reader, Game game)`
- **位置**：`AssetStudio/BundleFile.cs:119`
- **可见性**：public ctor
- **调用了**：`ReadBundleHeader`、`ReadHeader`、`ReadUnityCN`、`ReadBlocksInfoAndDirectory`、`ReadBlocks`、`ReadFiles`
- **简要说明**：解析整个 BundleFile；m_Header / fileList 完成后可用

### `BundleFile.ReadBundleHeader(FileReader)`
- **签名**：`Header ReadBundleHeader(FileReader reader)`
- **位置**：`AssetStudio/BundleFile.cs:157`
- **可见性**：private
- **调用了**：`XORShift128.InitSeed`（BH3 / BH3PrePre）
- **简要说明**：读 signature + version + unityRevision

### `BundleFile.ReadHeaderAndBlocksInfo(FileReader)`
- **签名**：`void ReadHeaderAndBlocksInfo(FileReader reader)`
- **位置**：`AssetStudio/BundleFile.cs:217`
- **可见性**：private
- **简要说明**：旧版 UnityWeb/UnityRaw 头解析

### `BundleFile.CreateBlocksStream(string)`
- **签名**：`Stream CreateBlocksStream(string path)`
- **位置**：`AssetStudio/BundleFile.cs:252`
- **可见性**：private
- **简要说明**：根据 block 总大小返回 MemoryStream 或临时 FileStream

### `BundleFile.ReadBlocksAndDirectory(FileReader, Stream)`
- **签名**：`void ReadBlocksAndDirectory(FileReader reader, Stream blocksStream)`
- **位置**：`AssetStudio/BundleFile.cs:270`
- **可见性**：private
- **调用了**：`SevenZipHelper.StreamDecompress`
- **简要说明**：旧版的 block + directory 读

### `BundleFile.ReadFiles(Stream, string)`
- **签名**：`void ReadFiles(Stream blocksStream, string path)`
- **位置**：`AssetStudio/BundleFile.cs:302`
- **可见性**：public
- **调用了**：`new StreamFile`
- **简要说明**：把每个 entry 的 stream 切出来放到 fileList

### `BundleFile.ReadHeader(FileReader)`
- **签名**：`void ReadHeader(FileReader reader)`
- **位置**：`AssetStudio/BundleFile.cs:332`
- **可见性**：private
- **调用了**：`XORShift128.NextDecryptUInt/Int/Long`（BH3 系）
- **简要说明**：读 size/compressedBlocksInfoSize/uncompressedBlocksInfoSize/flags

### `BundleFile.ReadUnityCN(FileReader)`
- **签名**：`void ReadUnityCN(FileReader reader)`
- **位置**：`AssetStudio/BundleFile.cs:378`
- **可见性**：private
- **调用了**：`new UnityCN(reader)`
- **简要说明**：处理 UnityCN 加密 header

### `BundleFile.ReadBlocksInfoAndDirectory(FileReader)`
- **签名**：`void ReadBlocksInfoAndDirectory(FileReader reader)`
- **位置**：`AssetStudio/BundleFile.cs:408`
- **可见性**：private
- **调用了**：`LZ4.Instance.Decompress`、`Mr0kUtils.IsMr0k/Decrypt`、`SevenZipHelper.StreamDecompress`
- **简要说明**：解压 blocksInfo（含 6 种压缩），解析 blocksInfo + directory

### `BundleFile.ReadBlocks(FileReader, Stream)`
- **签名**：`void ReadBlocks(FileReader reader, Stream blocksStream)`
- **位置**：`AssetStudio/BundleFile.cs:529`
- **可见性**：private
- **调用了**：所有 compression 解码（LZMA/LZ4/LZ4-Mr0k/LZ4-Inv/LZ4-Lit/Zstd）、`Mr0kUtils.Decrypt`、`FairGuardUtils.Decrypt`、`OPFPUtils.Decrypt`、`NetEaseUtils.Decrypt*`、`UnityCN.DecryptBlock`
- **简要说明**：解压每个 block 到 blocksStream

### `BundleFile.ParseVersion()`
- **签名**：`int[] ParseVersion()`
- **位置**：`AssetStudio/BundleFile.cs:709`
- **可见性**：public
- **返回值**：`int[]`（major, minor, patch, build）
- **简要说明**：解析 unityRevision 为 int[]

---

## 3. `AssetStudio/SerializedFile.cs`

### `SerializedFile(FileReader, AssetsManager)`
- **签名**：`SerializedFile(FileReader reader, AssetsManager assetsManager)`
- **位置**：`AssetStudio/SerializedFile.cs:50`
- **可见性**：public ctor
- **副作用**：填充 `m_Types / m_Objects / m_Externals / Objects / ObjectsDic`
- **调用**：`AssetsManager.LoadAssetsFile`、`AssetsManager.LoadAssetsFromMemory`、`AssetsManager.TryExtractVersionFromFile`
- **简要说明**：完整解析一个 SerializedFile

### `SerializedFile.SetVersion(string)`
- **签名**：`void SetVersion(string stringVersion)`
- **位置**：`AssetStudio/SerializedFile.cs:259`
- **可见性**：public
- **副作用**：修改 `unityVersion / version[] / buildType`
- **调用**：`AssetsManager.CheckStrippedVersion`、`SerializedFile` 构造器（`SerializedFile.cs:100`）
- **简要说明**：把版本字符串解析为 int[4] + BuildType

### `SerializedFile.ReadSerializedType(bool)`
- **签名**：`SerializedType ReadSerializedType(bool isRefType)`
- **位置**：`AssetStudio/SerializedFile.cs:274`
- **可见性**：private
- **调用了**：`TypeTreeBlobRead`、`ReadTypeTree`
- **简要说明**：读单个 SerializedType（含 classID + scriptTypeIndex + type tree）

### `SerializedFile.ReadTypeTree(TypeTree, int)`
- **签名**：`void ReadTypeTree(TypeTree m_Type, int level = 0)`
- **位置**：`AssetStudio/SerializedFile.cs:342`
- **可见性**：private
- **简要说明**：递归读旧格式 type tree

### `SerializedFile.TypeTreeBlobRead(TypeTree)`
- **签名**：`void TypeTreeBlobRead(TypeTree m_Type)`
- **位置**：`AssetStudio/SerializedFile.cs:375`
- **可见性**：private
- **简要说明**：读 Unity 2019+ 的 blob 格式 type tree

### `SerializedFile.AddObject(Object)`
- **签名**：`void AddObject(Object obj)`
- **位置**：`AssetStudio/SerializedFile.cs:429`
- **可见性**：public
- **调用**：`AssetsManager.ReadAssets`、`AssetsHelper.BuildAssetMap`
- **简要说明**：把强类型对象加入 `Objects + ObjectsDic`

### `SerializedFile.DecodeClassID(int)`
- **签名**：`static int DecodeClassID(int value)`
- **位置**：`AssetStudio/SerializedFile.cs:436`
- **可见性**：private static
- **简要说明**：GI 系列 encoded classID 解码（异或 `0x23746FBE`，减 3）

---

## 4. `AssetStudio/ImportHelper.cs`

### `ImportHelper.MergeSplitAssets(string, bool)`
- **签名**：`static void MergeSplitAssets(string path, bool allDirectories = false)`
- **位置**：`AssetStudio/ImportHelper.cs:19`
- **可见性**：public
- **调用**：
  - `AssetsManager.LoadFiles` (`AssetsManager.cs:60`)
  - `AssetsManager.LoadFolder` (`AssetsManager.cs:84`)
  - `AssetsHelper.LoadFiles` (`AssetsHelper.cs:172`)
  - `AssetStudio.CLI/Program.cs:178`
- **简要说明**：合并 `.split0..N` 文件

### `ImportHelper.ProcessingSplitFiles(List<string>)`
- **签名**：`static string[] ProcessingSplitFiles(List<string> selectFile)`
- **位置**：`AssetStudio/ImportHelper.cs:49`
- **可见性**：public
- **调用**：同 `MergeSplitAssets`
- **简要说明**：从输入路径中移除 `.split`，加入合并后的路径

### `ImportHelper.DecompressGZip(FileReader)`
- **签名**：`static FileReader DecompressGZip(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:67`
- **调用**：`AssetsManager.LoadFile(FileReader)` (`AssetsManager.cs:310`)
- **简要说明**：GZip 解压

### `ImportHelper.DecompressBrotli(FileReader)`
- **签名**：`static FileReader DecompressBrotli(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:82`
- **调用**：`AssetsManager.LoadFile(FileReader)` (`AssetsManager.cs:313`)
- **简要说明**：Brotli 解压

### `ImportHelper.DecryptPack(FileReader, Game)`
- **签名**：`static FileReader DecryptPack(FileReader reader, Game game)`
- **位置**：`AssetStudio/ImportHelper.cs:97`
- **调用**：`FileReader.PreProcessing`
- **调用了**：`Mr0kUtils.Decrypt`
- **简要说明**：GI_Pack 的 mr0k 加密块解密

### `ImportHelper.DecryptMark(FileReader)`
- **签名**：`static FileReader DecryptMark(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:228`
- **调用了**：`MarkKey`（内部常量数组）
- **简要说明**：Mark XOR 解密

### `ImportHelper.DecryptEnsembleStar(FileReader)`
- **签名**：`static FileReader DecryptEnsembleStar(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:277`
- **调用了**：`EnsembleStarKey1/2/3`
- **简要说明**：Ensemble Stars 解密

### `ImportHelper.ParseFakeHeader(FileReader)`
- **签名**：`static FileReader ParseFakeHeader(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:303`
- **调用了**：`OffsetStream`
- **简要说明**：跳过头部 fake bytes 找到真正 UnityFS

### `ImportHelper.DecryptFantasyOfWind(FileReader)`
- **签名**：`static FileReader DecryptFantasyOfWind(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:330`
- **简要说明**：Fantasy of Wind XOR + fake Unity 头

### `ImportHelper.ParseHelixWaltz2(FileReader)`
- **签名**：`static FileReader ParseHelixWaltz2(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:389`
- **简要说明**：Helix Waltz 2 RC4

### `ImportHelper.DecryptAnchorPanic(FileReader)`
- **签名**：`static FileReader DecryptAnchorPanic(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:440`
- **调用了**：内部 RC4 + MD5
- **简要说明**：Anchor Panic 选择性 RC4

### `ImportHelper.DecryptDreamscapeAlbireo(FileReader)`
- **签名**：`static FileReader DecryptDreamscapeAlbireo(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:557`
- **简要说明**：Dreamscape Albireo 头部 Scramble

### `ImportHelper.DecryptImaginaryFest(FileReader)`
- **签名**：`static FileReader DecryptImaginaryFest(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:624`
- **简要说明**：Imaginary Fest 单字节 XOR + 路径哈希解密

### `ImportHelper.DecryptAliceGearAegis(FileReader)`
- **签名**：`static FileReader DecryptAliceGearAegis(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:757`
- **简要说明**：Alice Gear Aegis XOR

### `ImportHelper.DecryptProjectSekai(FileReader)`
- **签名**：`static FileReader DecryptProjectSekai(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:797`
- **简要说明**：Project Sekai 大端 XOR

### `ImportHelper.DecryptCodenameJump(FileReader)`
- **签名**：`static FileReader DecryptCodenameJump(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:835`
- **简要说明**：Codename Jump 长 XOR

### `ImportHelper.DecryptGirlsFrontline(FileReader)`
- **签名**：`static FileReader DecryptGirlsFrontline(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:868`
- **简要说明**：Girls Frontline XOR

### `ImportHelper.DecryptReverse1999(FileReader)`
- **签名**：`static FileReader DecryptReverse1999(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:897`
- **简要说明**：Reverse: 1999 单字节 XOR（key 由文件名 MD5 推导）

### `ImportHelper.DecryptJJKPhantomParade(FileReader)`
- **签名**：`static FileReader DecryptJJKPhantomParade(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:949`
- **调用了**：`Aes.Create`、`Aes.Encrypt`
- **简要说明**：JJK Phantom Parade AES-ECB

### `ImportHelper.DecryptMuvLuvDimensions(FileReader)`
- **签名**：`static FileReader DecryptMuvLuvDimensions(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:1014`
- **简要说明**：Muv Luv Dimensions XOR

### `ImportHelper.DecryptPartyAnimals(FileReader)`
- **签名**：`static FileReader DecryptPartyAnimals(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:1034`
- **简要说明**：PartyAnimals XOR

### `ImportHelper.DecryptLoveAndDeepspace(FileReader)`
- **签名**：`static FileReader DecryptLoveAndDeepspace(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:1061`
- **简要说明**：Love and Deepspace XOR + seed

### `ImportHelper.DecryptSchoolGirlStrikers(FileReader)`
- **签名**：`static FileReader DecryptSchoolGirlStrikers(FileReader reader)`
- **位置**：`AssetStudio/ImportHelper.cs:1100`
- **简要说明**：School Girl Strikers XOR

---

## 5. `AssetStudio/AssetsHelper.cs`

### `AssetsHelper.SetUnityVersion(string)`
- **签名**：`static void SetUnityVersion(string version)`
- **位置**：`AssetStudio/AssetsHelper.cs:36`
- **调用**：`AssetStudio.CLI/Program.cs:47`、`MainForm.cs:2381, 2444, 2610`
- **简要说明**：设置全局 `assetsManager.SpecifyUnityVersion`

### `AssetsHelper.Clear()`
- **签名**：`static void Clear()`
- **位置**：`AssetStudio/AssetsHelper.cs:50`
- **调用**：`MainForm.resetToolStripMenuItem_Click` (`MainForm.cs:2480`)
- **简要说明**：清空 CABMap + Offsets + 重置 tokenSource

### `AssetsHelper.ClearOffsets()`
- **签名**：`static void ClearOffsets()`
- **位置**：`AssetStudio/AssetsHelper.cs:63`
- **调用**：`AssetsManager.Load` (`AssetsManager.cs:164`)
- **简要说明**：仅清空 Offsets 缓存

### `AssetsHelper.TryGet(string, out long[])`
- **签名**：`static bool TryGet(string path, out long[] offsets)`
- **位置**：`AssetStudio/AssetsHelper.cs:69`
- **调用**：`OffsetStream.cs:74`
- **简要说明**：查 path 对应的 offsets

### `AssetsHelper.AddCABOffsets(string[], List<string>)`
- **签名**：`static void AddCABOffsets(string[] paths, List<string> cabs)`
- **位置**：`AssetStudio/AssetsHelper.cs:81`
- **调用**：`AssetsHelper.ProcessFiles` (`AssetsHelper.cs:121`)
- **简要说明**：把 cab 依赖链上的 offsets 加到 Offsets

### `AssetsHelper.FindCAB(string, out List<string>)`
- **签名**：`static bool FindCAB(string path, out List<string> cabs)`
- **位置**：`AssetStudio/AssetsHelper.cs:105`
- **调用**：`AssetsHelper.ProcessFiles` (`AssetsHelper.cs:119`)
- **简要说明**：在 CABMap 中找包含 path 的 cab

### `AssetsHelper.ProcessFiles(string[])`
- **签名**：`static string[] ProcessFiles(string[] files)`
- **位置**：`AssetStudio/AssetsHelper.cs:113`
- **调用**：`AssetsHelper.ProcessDependencies` (`AssetsHelper.cs:137`)
- **简要说明**：返回最终要加载的 files（含依赖）

### `AssetsHelper.ProcessDependencies(string[])`
- **签名**：`static string[] ProcessDependencies(string[] files)`
- **位置**：`AssetStudio/AssetsHelper.cs:128`
- **调用**：`AssetsManager.LoadFiles` (`AssetsManager.cs:63`)
- **简要说明**：包装 `ProcessFiles`

### `AssetsHelper.BuildCABMap(string[], string, string, Game)`
- **签名**：`static void BuildCABMap(string[] files, string mapName, string baseFolder, Game game)`
- **位置**：`AssetStudio/AssetsHelper.cs:142`
- **调用**：
  - `AssetStudio.CLI/Program.cs:150`
  - `MainForm.buildMapToolStripMenuItem_Click` (`MainForm.cs:2382`)
- **调用了**：`AssetsHelper.LoadFiles (private yield)` (`AssetsHelper.cs:167`)
- **简要说明**：构建 CABMap 并写到 `Maps/<mapName>.bin`

### `AssetsHelper.LoadCABMapInternal(string)`
- **签名**：`static bool LoadCABMapInternal(string mapName)`
- **位置**：`AssetStudio/AssetsHelper.cs:248`
- **调用**：
  - `AssetStudio.CLI/Program.cs:154`
  - `MainForm.InitalizeOptions` (`MainForm.cs:176`)
  - `MainForm.specifyNameComboBox_SelectedIndexChanged` (`MainForm.cs:2319`)
- **简要说明**：从 `Maps/<mapName>.bin` 加载 CABMap

### `AssetsHelper.LoadCABMap(string)`
- **签名**：`static bool LoadCABMap(string path)`
- **位置**：`AssetStudio/AssetsHelper.cs:269`
- **调用**：`MainForm.loadCABMapToolStripMenuItem_Click` (`MainForm.cs:2565`)
- **简要说明**：从任意路径加载 CABMap

### `AssetsHelper.BuildAssetMap(...)`
- **签名**：`static async Task BuildAssetMap(string[] files, string mapName, Game game, string savePath, ExportListType exportListType, ClassIDType[] typeFilters, Regex[] nameFilters, Regex[] containerFilters)`
- **位置**：`AssetStudio/AssetsHelper.cs:316`
- **调用**：
  - `AssetStudio.CLI/Program.cs:166`
  - `MainForm.buildAssetMapToolStripMenuItem_Click` (`MainForm.cs:2611`)
- **简要说明**：构建 AssetMap

### `AssetsHelper.ParseAssetMap(string, ExportListType, ClassIDType[], Regex[], Regex[])`
- **签名**：`static string[] ParseAssetMap(string mapName, ExportListType mapType, ClassIDType[] typeFilter, Regex[] nameFilter, Regex[] containerFilter)`
- **位置**：`AssetStudio/AssetsHelper.cs:504`
- **调用**：`AssetStudio.CLI/Program.cs:162`
- **简要说明**：从已有 AssetMap 解析出命中的 source 文件

### `AssetsHelper.BuildBoth(...)`
- **签名**：`static async Task BuildBoth(string[] files, string mapName, string baseFolder, Game game, string savePath, ExportListType exportListType, ClassIDType[] typeFilters, Regex[] nameFilters, Regex[] containerFilters)`
- **位置**：`AssetStudio/AssetsHelper.cs:687`
- **调用**：
  - `AssetStudio.CLI/Program.cs:171`
  - `MainForm.buildBothToolStripMenuItem_Click` (`MainForm.cs:2445`)
- **简要说明**：同时构建 CABMap + AssetMap

---

## 6. `AssetStudio/GameManager.cs`

### `GameManager.GetGame(GameType)`
- **签名**：`static Game GetGame(GameType gameType)`
- **位置**：`AssetStudio/GameManager.cs:54`
- **调用**：`AssetStudio.CLI/Program.cs:20` 隐式
- **简要说明**：按 enum 取 Game 实例

### `GameManager.GetGame(int)`
- **签名**：`static Game GetGame(int index)`
- **位置**：`AssetStudio/GameManager.cs:55`
- **调用**：`MainForm.InitalizeOptions` (`MainForm.cs:164`)、`MainForm.specifyGame_SelectedIndexChanged` (`MainForm.cs:2297`)
- **抛出/异常**：未知 index 抛 `ArgumentException("Invalid format !!")`
- **简要说明**：按索引取 Game 实例

### `GameManager.GetGame(string)`
- **签名**：`static Game GetGame(string name)`
- **位置**：`AssetStudio/GameManager.cs:65`
- **调用**：`AssetStudio.CLI/Program.cs:20`
- **简要说明**：按 Name 取 Game 实例

### `GameManager.GetGames()`
- **签名**：`static Game[] GetGames()`
- **位置**：`AssetStudio/GameManager.cs:66`
- **调用**：`MainForm.InitalizeOptions` (`MainForm.cs:161`)
- **简要说明**：所有 Game 数组

### `GameManager.GetGameNames()`
- **签名**：`static string[] GetGameNames()`
- **位置**：`AssetStudio/GameManager.cs:67`
- **调用**：`CommandLine.OptionsBinder` (`CommandLine.cs:200`)
- **简要说明**：所有 Name 数组

### `GameManager.SupportedGames()`
- **签名**：`static string SupportedGames()`
- **位置**：`AssetStudio/GameManager.cs:68`
- **调用**：`AssetStudio.CLI/Program.cs:25`
- **简要说明**：所有 game 的格式化字符串

### `Game(GameType)`
- **签名**：`Game(GameType type)`
- **位置**：`AssetStudio/GameManager.cs:76`
- **简要说明**：基础 Game 构造器

### `Mr0k(GameType, byte[], byte[], byte[], byte[], byte[])`
- **签名**：`Mr0k(GameType type, byte[] expansionKey, byte[] sBox, byte[] initVector, byte[] blockKey, byte[] postKey)`
- **位置**：`AssetStudio/GameManager.cs:93`
- **调用**：在 `GameManager()` 静态构造器中使用
- **简要说明**：Mr0k 子类构造器

### `Blk(GameType, byte[], byte[], byte[], ulong)`
- **签名**：`Blk(GameType type, byte[] expansionKey, byte[] sBox, byte[] initVector, ulong initSeed)`
- **位置**：`AssetStudio/GameManager.cs:110`
- **调用**：在 `GameManager()` 静态构造器中使用
- **简要说明**：Blk 子类构造器

### `Mhy(GameType, byte[], byte[], byte[], byte[], byte[], byte[], ulong)`
- **签名**：`Mhy(GameType type, byte[] mhyShiftRow, byte[] mhyKey, byte[] mhyMul, byte[] expansionKey, byte[] sBox, byte[] initVector, ulong initSeed)`
- **位置**：`AssetStudio/GameManager.cs:125`
- **调用**：在 `GameManager()` 静态构造器中使用
- **简要说明**：Mhy 子类构造器

---

## 7. `AssetStudio/Crypto/UnityCN.cs`

### `UnityCN.SetKey(Entry)`
- **签名**：`static bool SetKey(Entry entry)`
- **位置**：`AssetStudio/Crypto/UnityCN.cs:50`
- **调用**：`AssetStudio.CLI/Program.cs:38`
- **简要说明**：设置全局 UnityCN 解密 key

### `UnityCN.DecryptBlock(Span<byte>, int, int)`
- **签名**：`void DecryptBlock(Span<byte> bytes, int size, int index)`
- **位置**：`AssetStudio/Crypto/UnityCN.cs:70`
- **调用**：`BundleFile.ReadBlocks` (`BundleFile.cs:583`)
- **简要说明**：块级解密

### `UnityCN.Entry.Validate()`
- **签名**：`bool Validate()`
- **位置**：`AssetStudio/Crypto/UnityCN.cs:147`
- **简要说明**：检查 entry 合法性

---

## 8. `AssetStudio/Crypto/BlkUtils.cs` / `Mr0kUtils.cs` / `AES.cs` / `FairGuardUtils.cs` / `OPFPUtils.cs` / `NetEaseUtils.cs`

### `BlkUtils.Decrypt(FileReader, Blk)`
- **签名**：`static XORStream Decrypt(FileReader reader, Blk blk)`
- **位置**：`AssetStudio/Crypto/BlkUtils.cs:14`
- **调用**：`AssetsManager.LoadBlkFile` (`AssetsManager.cs:719`)、`Studio.ExtractBlkFile`（CLI: `Studio.cs:117`、GUI: `Studio.cs:120`）
- **简要说明**：Blk 解密，返回 XORStream

### `Mr0kUtils.Decrypt(Span<byte>, Mr0k)`
- **签名**：`static Span<byte> Decrypt(Span<byte> data, Mr0k mr0k)`
- **位置**：`AssetStudio/Crypto/Mr0kUtils.cs:12`
- **调用**：`BundleFile.ReadBlocksInfoAndDirectory` (`BundleFile.cs:480`)、`BundleFile.ReadBlocks` (`BundleFile.cs:578`)、`ImportHelper.DecryptPack` (`ImportHelper.cs:148`)
- **简要说明**：Mr0k 解密

### `Mr0kUtils.IsMr0k(ReadOnlySpan<byte>)`
- **签名**：`static bool IsMr0k(ReadOnlySpan<byte> data)`
- **位置**：`AssetStudio/Crypto/Mr0kUtils.cs:73`
- **调用**：同上
- **简要说明**：检测 Mr0k magic

### `AES.Decrypt(byte[], byte[])`
- **签名**：`static void Decrypt(byte[] m, byte[] keys)`
- **位置**：`AssetStudio/Crypto/AES.cs:51`
- **简要说明**：AES 解密

### `FairGuardUtils.Decrypt(Span<byte>)`
- **签名**：`static void Decrypt(Span<byte> bytes)`
- **位置**：`AssetStudio/Crypto/FairGuardUtils.cs:9`
- **调用**：`BundleFile.ReadBlocks` (`BundleFile.cs:591, 627`)
- **简要说明**：FairGuard 解密（Arknights Endfield）

### `OPFPUtils.Decrypt(Span<byte>, string)`
- **签名**：`static void Decrypt(Span<byte> data, string path)`
- **位置**：`AssetStudio/Crypto/OPFPUtils.cs:13`
- **调用**：`BundleFile.ReadBlocks` (`BundleFile.cs:595`)
- **简要说明**：OPFP 解密

### `NetEaseUtils.DecryptWithoutHeader(Span<byte>)`
- **签名**：`static void DecryptWithoutHeader(Span<byte> span)`
- **位置**：`AssetStudio/Crypto/NetEaseUtils.cs`
- **调用**：`BundleFile.ReadBlocks` (`BundleFile.cs:552`)
- **简要说明**：NetEase 无头解密

### `NetEaseUtils.DecryptWithHeader(Span<byte>)`
- **签名**：`static void DecryptWithHeader(Span<byte> span)`
- **位置**：`AssetStudio/Crypto/NetEaseUtils.cs`
- **调用**：`BundleFile.ReadBlocks` (`BundleFile.cs:587`)
- **简要说明**：NetEase 带头解密

---

## 9. `AssetStudio/FileReader.cs`

### `FileReader.PreProcessing(FileReader, Game)`
- **签名**：`static FileReader PreProcessing(this FileReader reader, Game game)`
- **位置**：`AssetStudio/FileReader.cs:163`
- **调用**：`AssetsManager.LoadFile` (`AssetsManager.cs:292`)、`Studio.ExtractFile`（CLI: `Studio.cs:64`、GUI: `Studio.cs:67`）
- **调用了**：`ImportHelper.Decrypt*` 系列
- **简要说明**：检测 FileType 并调用对应解密/解压，返回新 FileReader

---

## 10. `AssetStudio/EndianBinaryReader.cs`

### `EndianBinaryReader.AlignStream()`
- **签名**：`void AlignStream()`
- **位置**：`AssetStudio/EndianBinaryReader.cs:136`
- **简要说明**：4 字节对齐

### `EndianBinaryReader.AlignStream(int)`
- **签名**：`void AlignStream(int alignment)`
- **位置**：`AssetStudio/EndianBinaryReader.cs:141`
- **简要说明**：N 字节对齐

### `EndianBinaryReader.ReadAlignedString()`
- **签名**：`string ReadAlignedString()`
- **位置**：`AssetStudio/EndianBinaryReader.cs:151`
- **简要说明**：读 aligned string

### `EndianBinaryReader.ReadStringToNull(int)`
- **签名**：`string ReadStringToNull(int maxLength = 32767)`
- **位置**：`AssetStudio/EndianBinaryReader.cs:164`
- **简要说明**：读 C 字符串

### `EndianBinaryReader.ReadQuaternion`
- **签名**：`Quaternion ReadQuaternion()`
- **位置**：`AssetStudio/EndianBinaryReader.cs:181`
- **简要说明**：读 Quaternion

### `EndianBinaryReader.ReadVector2/3/4/Color4/Matrix/Float`
- **签名**：见 `EndianBinaryReader.cs:186..209`
- **简要说明**：类型化读取

### `EndianBinaryReader.ReadMhyInt/ReadMhyUInt/ReadMhyString`
- **签名**：见 `EndianBinaryReader.cs:211..223`
- **简要说明**：Mhy 专用读取

---

## 11. `AssetStudio/Progress.cs` / `Logger.cs`

### `Progress.Reset()`
- **签名**：`static void Reset()`
- **位置**：`AssetStudio/Progress.cs:11`
- **简要说明**：重置进度

### `Progress.Report(int, int)`
- **签名**：`static void Report(int current, int total)`
- **位置**：`AssetStudio/Progress.cs:23`
- **调用**：被 `AssetsManager.LoadFile`、`AssetsManager.ReadAssets`、`AssetsHelper.BuildCABMap`、`AssetsHelper.BuildAssetMap`、`AssetsHelper.BuildBoth`、`Studio.ExportAssets` 调用
- **简要说明**：触发 Progress.Default 回调（GUI 进度条或 CLI 计数）

### `Logger.Verbose/Debug/Info/Warning/Error(...)`
- **签名**：`static void Verbose(object message)` 等
- **位置**：`AssetStudio/Logger.cs`
- **简要说明**：输出日志，受 `Logger.Flags` 控制

---

## 12. `AssetStudio/TypeFlags.cs`

### `TypeFlags.SetTypes(Dictionary<ClassIDType, (bool, bool)>)`
- **签名**：`static void SetTypes(Dictionary<ClassIDType, (bool, bool)> types)`
- **位置**：`AssetStudio/TypeFlags.cs:9`
- **调用**：`AssetStudio.CLI/Program.cs:49`、`MainForm.InitalizeOptions` (`MainForm.cs:165`)
- **简要说明**：批量设置 parse/export 标志

### `TypeFlags.SetType(ClassIDType, bool, bool)`
- **签名**：`static void SetType(ClassIDType type, bool parse, bool export)`
- **位置**：`AssetStudio/TypeFlags.cs:14`
- **调用**：`AssetStudio.CLI/Program.cs:85, 100, 103, 107, 111, 118`
- **简要说明**：单个类型设置

### `TypeFlags.CanParse(this ClassIDType)`
- **签名**：`static bool CanParse(this ClassIDType type)`
- **位置**：`AssetStudio/TypeFlags.cs:20`
- **调用**：`AssetsManager.ReadAssets` (`AssetsManager.cs:959..989`)
- **简要说明**：是否参与 Parse

### `TypeFlags.CanExport(this ClassIDType)`
- **签名**：`static bool CanExport(this ClassIDType type)`
- **位置**：`AssetStudio/TypeFlags.cs:34`
- **调用**：`AssetsHelper.BuildAssetMap` (`AssetsHelper.cs:386, 392, ...`)
- **简要说明**：是否参与 Export

---

## 13. `AssetStudio/ResourceIndex.cs` / `UnityCNManager.cs` / `AIVersionManager.cs`

### `ResourceIndex.FromFile(string)`
- **签名**：`static void FromFile(string path)`
- **位置**：`AssetStudio/ResourceIndex.cs:13`
- **调用**：`AssetStudio.CLI/Program.cs:134`、`MainForm.loadAIToolStripMenuItem_Click` (`MainForm.cs:2550`)
- **简要说明**：从 asset_index.json 加载

### `ResourceIndex.Clear()`
- **签名**：`static void Clear()`
- **位置**：`AssetStudio/ResourceIndex.cs:64`
- **简要说明**：清空

### `ResourceIndex.GetContainer(uint, uint)`
- **签名**：`static string GetContainer(uint id, uint last)`
- **位置**：`AssetStudio/ResourceIndex.cs:75`
- **调用**：`AssetsHelper.UpdateContainers` (`AssetsHelper.cs:607`)、`Studio.UpdateContainers`（CLI: `Studio.cs:215`、GUI: `Studio.cs:218`）
- **简要说明**：GI container ID → 路径

### `UnityCNManager.SaveEntries(List<UnityCN.Entry>)`
- **签名**：`static void SaveEntries(List<UnityCN.Entry> entries)`
- **位置**：`AssetStudio/UnityCNManager.cs:21`
- **简要说明**：持久化 keys

### `UnityCNManager.SetKey(int)`
- **签名**：`static void SetKey(int index)`
- **位置**：`AssetStudio/UnityCNManager.cs:30`
- **调用**：`MainForm.InitalizeOptions` (`MainForm.cs:170`)、`MainForm.specifyGame_SelectedIndexChanged` (`MainForm.cs:2302`)
- **简要说明**：全局设置 UnityCN key

### `UnityCNManager.TryGetEntry(int, out UnityCN.Entry)`
- **签名**：`static bool TryGetEntry(int index, out UnityCN.Entry key)`
- **位置**：`AssetStudio/UnityCNManager.cs:50`
- **调用**：`AssetStudio.CLI/Program.cs:31`、`MainForm.InitalizeOptions` (`MainForm.cs:394`)
- **简要说明**：取 key entry

### `AIVersionManager.GetVersions()`
- **签名**：`static List<(string, bool)> GetVersions()`
- **位置**：`AssetStudio/AIVersionManager.cs:34`
- **调用**：`MainForm.UpdateVersionList` (`MainForm.cs:2173`)
- **简要说明**：版本列表

### `AIVersionManager.FetchVersions()`
- **签名**：`static Task<bool> FetchVersions()`
- **位置**：`AssetStudio/AIVersionManager.cs`
- **调用**：`MainForm.toolStripMenuItem19_DropDownOpening` (`MainForm.cs:2124`)
- **简要说明**：从 GitHub 拉取版本列表

### `AIVersionManager.FetchAI(string)`
- **签名**：`static Task<string> FetchAI(string version)`
- **位置**：`AssetStudio/AIVersionManager.cs`
- **调用**：`MainForm.toolStripComboBox1_SelectedIndexChanged` (`MainForm.cs:2160`)
- **简要说明**：下载指定版本的 asset_index.json