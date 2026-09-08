# 10 术语表（Glossary）

本章列出 AssetStudio 项目（及 Unity / Bundle 解析生态）中出现的关键术语，按字母顺序排列。

## 字母 A

### ACL（Animation Compression Library）
用于压缩 Unity 骨骼动画的关键帧数据。AssetStudio 通过 `AssetStudio.Utility/ACL/ACL.cs` 端口实现解码，处理 `m_ACLClip`。

### `AssetBundle`
Unity 中一种资源类型（ClassID 142），包含若干 `m_Container` → `preloadIndex / preloadSize` 引用，关联到一组 `m_PreloadTable` 中的对象。AssetStudio 用它来反推每个资源的"容器路径"。

### `AssetsManager`
核心编排器，位于 `AssetStudio/AssetsManager.cs`，负责加载 SerializedFile、处理跨文件依赖、维护 `assetsFileList / resourceFileReaders` 等核心状态。

### `AssetsHelper`
`AssetStudio/AssetsHelper.cs` 中的静态类，专门处理 CABMap / AssetMap 的构建、加载、解析。

### AssetMap
AssetStudio 专有概念：通过遍历所有 `assetsFile.m_Objects`，把每个 `AssetEntry { Name, Container, Type, PathID, Source }` 写入到 `Maps/<name>.{xml,json,map}` 的清单文件，用于：
- 通过 `--map_op AssetMap` 加速下次加载（按需过滤 source）
- 通过 `--map_op Both` 同时构建 CABMap + AssetMap

### AIVersionManager
`AssetStudio/AIVersionManager.cs`：从 `radioegor146/gi-asset-indexes` GitHub 仓库拉取 `asset_index.json`，把 GI 的 numeric container ID 解析为真实路径。

## 字母 B

### `Blk`（类）
游戏专属加密流类型（XOR），用于 BH3 / GI_CB2 / GI_CB3。`GameManager.cs:103` 定义 `Blk : Game`。

### `BlockFile`
Unity 的"块文件"格式：多个 Bundle 简单串联，中间靠 `OffsetStream.GetOffsets` 找到每个 bundle 的起始位置。`AssetsManager.LoadBlockFile` (`AssetsManager.cs:677`) 处理。

### `BlbFile`
米哈游早期格式，类似 Bundle 但布局不同。`AssetStudio/BlbFile.cs` 解析。

### `BundleFile`
Unity 5+ 的标准打包容器（UnityFS / UnityWeb / UnityRaw / ENCR）。`AssetStudio/BundleFile.cs` 解析。

## 字母 C

### CABMap
AssetStudio 专有概念：(filename → {Path, Offset, Dependencies}) 的二进制索引，存于 `Maps/<name>.bin`。用于：
- 通过 `AssetsHelper.LoadCABMap` 加载后，`AssetsHelper.ProcessDependencies` 能精确只读取 bundle 内的特定 CAB 段（不必解压整个 bundle）

### `ClassID`
Unity 引擎中每个类对应的枚举值（如 `GameObject = 1`, `Texture2D = 28`, `Mesh = 43`, `MonoBehaviour = 114`）。`AssetStudio/ClassIDType.cs` 定义。

### `CompressionType`
BundleFile 的压缩算法枚举：`None / Lzma / Lz4 / Lz4HC / Lzham / Lz4Mr0k / Lz4Inv / Zstd / Lz4Lit4 / Lz4Lit5`。

### `Container`
AssetBundle 中预加载资源的容器路径；AssetStudio 用此字段组织输出结构。

### CRC32
7zip 风格的 CRC 实现，位于 `AssetStudio/7zip/Common/CRC.cs`，被 ModelConverter 用于把 bone path 编码为 hash。

## 字母 D

### `DecryptXxx`
`AssetStudio/ImportHelper.cs` 中 20+ 种游戏的解密函数，每个对应一种 `GameType`。

### `DecodeClassID`
`SerializedFile.cs:436`：GI 系列将 classID 反转 + XOR `0x23746FBE` - 3。

### `DetectedFolderVersion`
`AssetsManager.detectedFolderVersion`：从 `globalgamemanagers` / `data.unity3d` / 任意 `.bundle` 检测到的 Unity 版本。

### `DLC`/`dummy DLL`
游戏发行包外的 MonoBehaviour 真实类型定义（用户用 `Mono.Cecil` 生成空方法的 stub DLL）。AssetStudio 通过 `--dummy_dlls` 加载它们来辅助反序列化 MonoBehaviour。

## 字母 E

### `EndianBinaryReader`
`AssetStudio/EndianBinaryReader.cs`：支持大小端切换的二进制 reader，提供 `ReadAlignedString / ReadStringToNull / ReadQuaternion / ReadVector2/3/4 / ReadColor4 / ReadMatrix` 等类型化读取。

### `ENCR`
Unity bundle header 的一种 signature，米哈游版本。

## 字母 F

### `FakeHeader`
部分游戏会在真正 UnityFS header 前添加一段假字节，`ImportHelper.ParseFakeHeader` 跳过这段。

### `FileReader`
`AssetStudio/FileReader.cs`：扩展 `EndianBinaryReader`，带 `PreProcessing(Game)` 扩展方法做 file type 检测 + 解密。

### `FileType`
枚举：`AssetsFile / BundleFile / WebFile / GZipFile / BrotliFile / ZipFile / BlockFile / BlkFile / MhyFile / BlbFile / ResourceFile`。

### `FbxExporter`
`AssetStudio.FBXWrapper/FbxExporter.cs`：高阶 FBX 写入逻辑，调用 `FbxDll` (P/Invoke) → `AssetStudio.FBXNative.dll`（C++）。

### `FbxNative`
C++ 原生 FBX 写入器。`AssetStudio.FBXNative/`。

### FMOD
音频引擎。GUI 端用 FMOD 实时播放 / 暂停 / 停止音频。原生库 `fmod.dll` 随 GUI 分发。

### `FbxDll`
`AssetStudio.FBXWrapper/FbxDll.cs`：对原生 FBX 写入器的低级 C# 包装（P/Invoke）。

## 字母 G

### `Game` / `GameType` / `GameManager`
`AssetStudio/GameManager.cs`：38 种游戏类型的注册表 + 多态派生 `Mr0k / Blk / Mhy`。通过 `GameManager.GetGame(name)` 获取实例。

### `GI`（Genshin Impact）
原神，米哈游。`GameType.GI` 是 `Mhy` 类，带 `GIMhyShiftRow/GIMhyKey/GIMhyMul/GIExpansionKey/GISBox/GIInitVector/GIInitSeed` 一组 keys。

### `globalgamemanagers`
Unity PC 构建的常见文件名（无后缀），位于 `*_Data` 目录下，包含引擎元数据 + 一些游戏内对象。AssetStudio 从中提取 Unity 版本。

## 字母 H

### HLSLDecompiler
原生 DLL (`HLSLDecompiler.dll`)，把 DX11 shader 字节码反编译为 HLSL 文本。`ShaderSubProgram.Export` 中通过 `AssetStudio.Utility/ShaderConverter.cs:1177` 调用。

### `HashSet<long> Offsets`
`AssetsHelper.Offsets`：path → 多个 long 偏移。`ProcessFiles` 时填充。

## 字母 I

### `IImported`
`AssetStudio/IImported.cs` 接口，作为 ModelConverter 输出与 FbxExporter 输入的契约。

### `ImportHelper`
`AssetStudio/ImportHelper.cs`：split 文件合并 + GZip/Brotli 解压 + 20+ 种游戏解密。

### `ImportedFrame` / `ImportedMesh` / `ImportedMaterial` / `ImportedTexture` / `ImportedKeyframedAnimation` / `ImportedMorph`
FBX 中间表示（`IImported` 的数据模型）。

### `IsFromBundle`
`SerializedFile.cs:48`：标记此 SerializedFile 是从 bundle 内 stream 加载的（用于优先使用 bundle 版本，避免 strip CAB 数据）。

## 字母 L

### LZ4 / LZ4HC / LZ4Mr0k / LZ4Inv / LZ4Lit
Unity bundle 5 种 LZ4 变体。`AssetStudio/LZ4/` 包含纯 C# 实现。

### `LoadFiles` / `LoadFolder`
`AssetsManager` 的两个公开入口（`AssetsManager.cs:48/73`）。

## 字母 M

### `Mhy`（类）
游戏专属加密流类型（米哈游 AES），`GameManager.cs:119` 定义 `Mhy : Blk`。

### `MhyFile`
米哈游 `.blk` 文件的另一种形式，`AssetStudio/MhyFile.cs` 解析。

### `MessagePack`
高效二进制序列化。CLI/GUI 用 `MessagePack` 库把 `AssetMap` 写入 `.map` 文件。

### `Mesh.GetUV(int)`
Mesh 类辅助函数，返回指定 channel (0-7) 的 UV 数组。ModelConverter 通过它处理 8 套 UV。

### `MiHoYoBinData`
米哈游自定义二进制数据（可能是 JSON 也可能是 Bytes），带 XOR 加密。`MiHoYoBinData.Encrypted/Key` 通过 `--key` 设置。

### `ModelConverter`
`AssetStudio.Utility/ModelConverter.cs`：把 Unity GameObject / Animator / 合并 GameObject 转换为 FBX 友好的 `IImported` 中间结构。

### MonoBehaviour
Unity 自定义脚本。`AssetStudio/Classes/MonoBehaviour.cs` 解析。导出时通过 `--dummy_dlls` + `AssemblyLoader.Load` 提供 Cecil 元数据后转 JSON。

### `MonoBehaviourToTypeTree`
`Studio.MonoBehaviourToTypeTree(MonoBehaviour)`：CLI `Studio.cs:503`、GUI `Studio.cs:918`。

### Mr0k
米哈游加密流（哈希 + SBox），`GameManager.cs:85` 定义 `Mr0k : Game`。`Crypto/Mr0kUtils.cs` 解密。

## 字母 N

### `Node`
`BundleFile.cs:89` 内嵌类，表示 bundle 内目录的一个 entry（offset/size/flags/path）。

## 字母 O

### `OffsetStream`
`AssetStudio/OffsetStream.cs`：支持多段偏移的 Stream，BlockFile/Blk 处理用。

### OPFP
`GameType.OPFP`，`ImportHelper` 中对应解密函数（实际解密逻辑在 `Crypto/OPFPUtils.cs`）。

## 字母 P

### `ParseVersion`
`BundleFile.cs:709`：把 unityRevision 解析为 int[]。

### `Parallel.For` / `Parallel.ForEach`
AssetsManager/Studio 使用 `Environment.ProcessorCount` 度数的并行 IO 循环。

### `PreProcessing`
`FileReader.cs:163` 的扩展方法，按 game type 解密 + 检测 FileType。

### `ProcessAssets`
`AssetsManager.cs:1010`：把 GameObject 与 Transform/Renderer/Animator/Animation 等组件关联。

### `Progress`
`AssetStudio/Progress.cs`：单实例进度抽象（`Reset / Report`）。

## 字母 R

### `ResourceIndex`
`AssetStudio/ResourceIndex.cs`：从 `gi-asset-indexes` 仓库下载的 `asset_index.json` 解析得到的 container ID → 路径映射。`GetContainer(id, last)` 查询。

### `resourceFileReaders`
`AssetsManager.resourceFileReaders`：跨文件的二进制资源流（如 .resS）。`ResourceReader.cs` 通过它解析 Texture2D.streamData / AudioClip 等外部资源。

### `ReadAssets`
`AssetsManager.cs:937`：把所有 SerializedFile 的 m_Objects 反序列化为强类型 Object。

## 字母 S

### `SerializedFile`
Unity 中单个 .assets / .unity3d 文件的逻辑表示。`AssetStudio/SerializedFile.cs` 解析。

### `SerializedFileFormatVersion`
枚举：`Unknown_2 / Unknown_3 / Unknown_5 / Unknown_6 / Unknown_7 / Unknown_8 / Unknown_9 / Unknown_10 / Unknown_12 / Unknown_14 / LargeFilesSupport / HasTypeTreeHashes / RefactoredClassId / RefactorTypeData / StoresTypeDependencies / SupportsStrippedObject / HasScriptTypeIndex / SupportsRefObject / TypeTreeNodeWithTypeFlags`。

### `SetVersion(string)`
`SerializedFile.cs:259`：解析版本字符串到 `version[]` + `buildType`。

### Smolv
SPIRV 解码器，AssetStudio 通过 `AssetStudio.Utility/Smolv/SmolvDecoder.cs` + `SpirVShaderConverter.cs` 把 Vulkan SPIRV shader 字节反汇编。

### SPIRV
`ShaderCompilerPlatform.Vulkan` 对应的 SubProgram 字节码格式。

### `StorageBlock`
`BundleFile.cs:73` 内嵌类，存储一个 block 的 compressedSize / uncompressedSize / flags。

### `StreamFile`
`AssetStudio/StreamFile.cs`：bundle 解压后，每个 entry 一个 StreamFile（含 path / fileName / stream）。

## 字母 T

### `Texture2DConverter`
`AssetStudio.Utility/Texture2DConverter.cs`：30+ 种 TextureFormat → BGRA32 解码器。

### `TypeTree` / `TypeTreeNode`
Unity 中描述类结构的反射信息（Type ID / Field name / Field type / Size 等）。`AssetStudio/TypeTree.cs`、`TypeTreeNode.cs`。

### `TypeFlags`
`AssetStudio/TypeFlags.cs`：静态字典控制哪些 `ClassIDType` 参与 Parse / Export。

## 字母 U

### `UnityCN`
Unity 中国版加密方案（Block-level AES + 派生密钥）。`Crypto/UnityCN.cs` 解密。

### `UnityCNManager`
`AssetStudio/UnityCNManager.cs`：UnityCN key 的多 entry 管理（GUI `UnityCNForm` 编辑）。

### `UnityFS`
Unity 5+ 标准 Bundle 的 signature（也是 file format 名）。

### `UnityWeb` / `UnityRaw`
旧版 Unity Bundle 的 signature。

### `unityRevision`
`BundleFile.Header.unityRevision`：从 bundle 头解析出来的精确 Unity 版本字符串（如 `2022.3.10f1`）。

### `unityVersion`
`SerializedFile.unityVersion`：从 SerializedFile 头解析出来的 Unity 版本字符串；如果文件被 strip 则为 `"0.0.0"`。

## 字母 V

### Vortice.D3DCompiler
托管 D3D 编译器，用于 DX9 SM20/30/PS20/30 的反汇编。`ShaderSubProgram.Export` (`ShaderConverter.cs:1052, 1104`) 调用。

## 字母 W

### `WasOriginallyStripped`
`SerializedFile.cs:42`：记录文件**初次加载**时是否被 strip；一旦设置不再改变。

### `WebFile`
旧版 Unity Web 资源包（`UnityWeb` v<6）。`AssetStudio/WebFile.cs` 解析。

## 字母 X

### `XORStream`
`AssetStudio/XORStream.cs`：XOR 解密流，`BlkUtils.Decrypt` 返回值。

### `XForm`
`AssetStudio/Math/XForm.cs`：Unity 自定义 4x4 变换矩阵（含 t/q/s）。

## 字母 Z

### ZstdSharp
Zstd 解码库（AssetStudio 通过 `using ZstdSharp;` 在 `BundleFile.ReadBlocks` 中使用）。

### 其它

### `cabal_file`/`cab file` 概念
AssetStudio 中 `CAB` 指 bundle 内的子文件（不是 Unity 官方的 .cab 格式）。CABMap 通过 (filename, path, offset, dependencies) 把 CAB 关联到原 bundle 内位置。

### 节点 ID
bundle 内每个 entry 的 PathID 是由 Unity AssetBundle 写入时分配的 64 位整数。

### SPIRV-Cross
`AssetStudio.Utility/CSspv/` 是 SPIRV-Cross 项目反汇编器的 C# 移植。