# 04 数据结构与数据流（Data Flow）

本章覆盖 AssetStudio 中**最核心**的四个数据结构，以及从磁盘文件到强类型 `Object` 集合的完整数据流。

## 1. 核心数据结构

### 1.1 `AssetsManager`（`AssetStudio/AssetsManager.cs`）

整个项目最顶层的编排器。负责：

- 维护 `assetsFileList`（所有解析过的 `SerializedFile`）
- 维护 `resourceFileReaders`（跨文件的资源二进制流，如 .resS）
- 维护 `importFiles` / `importFilesHash`（待处理文件队列）
- 维护 `noexistFiles`（已经知道不存在的依赖路径，避免重复 IO）
- 维护 `assetsFileListHash`（已加载的 SerializedFile fileName 集合）
- 调度并行加载（`Parallel.For` + wave-based 重试）
- 暴露 `LoadFiles(string[])` / `LoadFolder(string)` / `Clear()` / `CheckStrippedVersion(SerializedFile)`
- 通过 `OnVersionPrompt` 事件对外请求"stripped Unity version"（如果 folder 探测失败且 DefaultVersion 为空）

```csharp
public class AssetsManager
{
    public Game Game;
    public event EventHandler<VersionPromptEventArgs> OnVersionPrompt;
    public bool Silent = false;
    public bool SkipProcess = false;
    public bool ResolveDependencies = false;
    public string SpecifyUnityVersion;
    public string DefaultVersion;
    public CancellationTokenSource tokenSource = new();
    public List<SerializedFile> assetsFileList = new();

    internal ConcurrentDictionary<string, BinaryReader> resourceFileReaders;
    internal List<string> importFiles;
    internal ConcurrentDictionary<string, byte> importFilesHash;
    internal ConcurrentDictionary<string, byte> noexistFiles;
    internal ConcurrentDictionary<string, byte> assetsFileListHash;
}
```

### 1.2 `SerializedFile`（`AssetStudio/SerializedFile.cs`）

Unity 中 **单个** `.assets` / `.unity3d` 文件的逻辑表示。解析后字段：

| 字段 | 类型 | 说明 |
|---|---|---|
| `assetsManager` | `AssetsManager` | 所属的 AssetsManager |
| `reader` | `FileReader` | 当前文件 reader |
| `game` | `Game` | 解析时使用的 Game（影响 m_NextOffset 加密等） |
| `offset` | `long` | 在 bundle 内的偏移（bundle-loaded 时记录） |
| `originalPath` / `fullName` / `fileName` | `string` | 路径信息 |
| `version` | `int[4]` | 解析后的 Unity 版本号（major/minor/patch/build） |
| `buildType` | `BuildType` | 包含 f/p/b 的 BuildType（版本字符串中的字母） |
| `header` | `SerializedFileHeader` | 头：metadataSize/fileSize/version/dataOffset |
| `unityVersion` | `string` | 字符串形式的 Unity 版本 |
| `m_TargetPlatform` | `BuildTarget` | 平台 |
| `m_Types` | `List<SerializedType>` | 类型表 |
| `bigIDEnabled` | `int` | PathID 是否 64-bit |
| `m_Objects` | `List<ObjectInfo>` | 对象表（pathId/byteStart/byteSize/type/classID） |
| `m_Externals` | `List<FileIdentifier>` | 外部依赖 |
| `m_RefTypes` | `List<SerializedType>` | 引用类型（仅 SupportsRefObject 之后） |
| `userInformation` | `string` | userInformation 段 |
| `Objects` | `List<Object>` | 已反序列化的强类型对象 |
| `ObjectsDic` | `Dictionary<long, Object>` | pathId → Object |
| `WasOriginallyStripped` / `IsFromBundle` | `bool` | 标记用 |

关键方法：

- `SerializedFile(FileReader, AssetsManager)`：构造时一次性解析 header + types + objects + externals + refTypes
- `SetVersion(string)`：版本字符串 → `version[4]` + `buildType`
- `AddObject(Object)`：添加到 `Objects` + `ObjectsDic`
- `IsVersionStripped`：当 `unityVersion == "0.0.0"`

### 1.3 `BundleFile`（`AssetStudio/BundleFile.cs`）

UnityFS / UnityWeb / UnityRaw / ENCR 容器的解析器。结构：

```mermaid
classDiagram
    class BundleFile {
        +Header m_Header
        +List~StorageBlock~ m_BlocksInfo
        +List~Node~ m_DirectoryInfo
        +List~StreamFile~ fileList
    }
    class Header {
        +string signature
        +uint version
        +string unityVersion
        +string unityRevision
        +long size
        +uint compressedBlocksInfoSize
        +uint uncompressedBlocksInfoSize
        +ArchiveFlags flags
    }
    class StorageBlock {
        +uint compressedSize
        +uint uncompressedSize
        +StorageBlockFlags flags
    }
    class Node {
        +long offset
        +long size
        +uint flags
        +string path
    }
    class StreamFile {
        +string path
        +string fileName
        +Stream stream
    }
    BundleFile --> Header
    BundleFile --> StorageBlock : m_BlocksInfo
    BundleFile --> Node : m_DirectoryInfo
    BundleFile --> StreamFile : fileList
```

压缩类型 `CompressionType`：`None`、`Lzma`、`Lz4`、`Lz4HC`、`Lzham`、`Lz4Mr0k`、`Lz4Inv`、`Lz4Lit4`、`Lz4Lit5`、`Zstd`。

### 1.4 `GameManager`（`AssetStudio/GameManager.cs`）

静态注册表，把 `GameType`（枚举）映射到对应的 `Game` / `Mr0k` / `Blk` / `Mhy` 实例：

```csharp
static GameManager()
{
    Games.Add(index++, new(GameType.Normal));
    Games.Add(index++, new(GameType.UnityCN));
    Games.Add(index++, new Mhy(GameType.GI, GIMhyShiftRow, GIMhyKey, GIMhyMul, GIExpansionKey, GISBox, GIInitVector, GIInitSeed));
    Games.Add(index++, new Mr0k(GameType.GI_Pack, PackExpansionKey, blockKey: PackBlockKey));
    // ... 共 38 项
}
```

关键方法：

- `GetGame(GameType)` / `GetGame(int)` / `GetGame(string)`：按 enum / 索引 / 名字查询
- `GetGames()` / `GetGameNames()`：枚举所有
- `SupportedGames()`：格式化为字符串

`GameTypes` 静态扩展类提供 `IsGI()` / `IsBH3Group()` / `IsMhyGroup()` / `IsBlockFile()` 等谓词。

## 2. 数据流

### 2.1 总体数据流

```mermaid
flowchart LR
    Disk[(磁盘/文件夹)]
    FileReader[FileReader]
    PreProc{{PreProcessing<br/>解密 + 检测 FileType}}
    AM[AssetsManager.LoadFile]
    BF[BundleFile]
    Mhy[MhyFile]
    Web[WebFile]
    Blk[BlkFile]
    SF[SerializedFile]
    OR[ObjectReader]
    Obj[强类型 Object<br/>Texture2D/Mesh/GameObject/...]
    Export[Exporter<br/>Texture/Mesh/Shader/Fbx]

    Disk --> FileReader --> PreProc
    PreProc -->|BundleFile| AM
    PreProc -->|MhyFile| AM
    PreProc -->|AssetsFile| AM
    AM -->|LoadBundleFile| BF
    AM -->|LoadMhyFile| Mhy
    AM -->|LoadAssetsFile| SF
    AM -->|LoadAssetsFromMemory| SF
    AM -->|LoadWebFile| Web
    AM -->|LoadBlkFile| Blk
    BF -->|fileList| SF
    Mhy -->|fileList| SF
    Web -->|fileList| SF
    Blk -->|offsets| BF
    SF -->|m_Objects| OR -->|Object 强类型实例| Obj
    Obj --> Export
    Export --> DiskOut[(导出目录)]
```

### 2.2 SerializedFile 解析细节

```mermaid
sequenceDiagram
    participant R as FileReader
    participant SF as SerializedFile
    participant TR as TypeTreeReader
    participant O as Object

    R->>SF: ReadUInt32 metadataSize / fileSize / version / dataOffset
    SF->>SF: Read endianness
    alt version ≥ Unknown_7
        SF->>R: ReadStringToNull unityVersion
        SF->>SF: SetVersion
    end
    SF->>R: ReadInt32 typeCount
    loop typeCount
        SF->>TR: ReadSerializedType
        TR->>R: Read classID / scriptTypeIndex / scriptID / oldTypeHash
        alt m_EnableTypeTree
            TR->>R: Read type tree (blob 或 recursive)
        end
    end
    SF->>R: ReadInt32 objectCount
    loop objectCount
        SF->>R: Read pathId / byteStart / byteSize / typeID / classID
        SF->>SF: 关联到 m_Types
    end
    SF->>R: Read externals
    SF-->>AM: 返回 SerializedFile
```

### 2.3 Bundle 解压细节

```mermaid
sequenceDiagram
    participant AM as AssetsManager.LoadBundleFile
    participant BF as BundleFile
    participant SR as SevenZip / LZ4 / Zstd
    participant Stream as blocksStream (MemoryStream/FileStream)
    participant SFr as SerializedFile

    AM->>BF: new BundleFile(reader, Game)
    BF->>BF: ReadBundleHeader (签名/version/unityRevision)
    alt signature == UnityFS / ENCR
        BF->>BF: ReadHeader (size/compressedBlocksInfoSize/...)
        opt game.Type.IsUnityCN()
            BF->>BF: ReadUnityCN (decrypt header)
        end
        BF->>BF: ReadBlocksInfoAndDirectory
        Note over BF: 解压 BlocksInfo → 得到 m_BlocksInfo + m_DirectoryInfo
    else signature == UnityWeb / UnityRaw v6
        BF->>BF: ReadHeaderAndBlocksInfo (legacy)
    end
    BF->>Stream: CreateBlocksStream
    loop m_BlocksInfo
        BF->>BF: ReadBlocks
        Note over BF: 按 CompressionType 选择解码器<br/>(LZMA/LZ4/LZ4-Mr0k/LZ4-Inv/LZ4-Lit/Zstd)
    end
    BF->>BF: ReadFiles (写每个 file.stream)
    BF-->>AM: fileList (List<StreamFile>)
    loop fileList
        AM->>SFr: LoadAssetsFromMemory (subReader, originalPath, ...)
        SFr-->>AM: SerializedFile (with offset, IsFromBundle=true)
    end
```

### 2.4 GameObject 关联建立（`AssetsManager.ProcessAssets`）

```mermaid
sequenceDiagram
    participant AM as AssetsManager.ProcessAssets
    participant SF as SerializedFile
    participant GO as GameObject
    participant Trans as Transform
    participant MR as MeshRenderer
    participant MF as MeshFilter
    participant SMR as SkinnedMeshRenderer
    participant Anim as Animator
    participant Anim2 as Animation

    loop 每个 SerializedFile
        loop 每个 Object
            alt obj is GameObject
                AM->>GO: 读取 m_Components (List<PPtr<Component>>)
                loop 每个 pptr
                    AM->>AM: pptr.TryGet(out var m_Component)
                    alt Transform
                        AM->>GO: m_GameObject.m_Transform = m_Transform
                    else MeshRenderer
                        AM->>GO: m_GameObject.m_MeshRenderer = ...
                    else MeshFilter
                        AM->>GO: m_GameObject.m_MeshFilter = ...
                    else SkinnedMeshRenderer
                        AM->>GO: m_GameObject.m_SkinnedMeshRenderer = ...
                    else Animator
                        AM->>GO: m_GameObject.m_Animator = ...
                    else Animation
                        AM->>GO: m_GameObject.m_Animation = ...
                    end
                end
            else obj is SpriteAtlas
                AM->>AM: 关联 PackedSprites 到 atlas
            end
        end
    end
```

### 2.5 资源跨文件引用（`ResourceReader`）

```mermaid
sequenceDiagram
    participant OR as ObjectReader
    participant RR as ResourceReader
    participant AM as AssetsManager
    participant Disk as 磁盘上的 .resS

    OR->>RR: Read(value, type)
    alt type is PPtr
        OR->>AM: assetsFileList.Find(pathId, fileId) → 找到 PPtr 目标
    else type is需要外部资源 (resources/unity_builtin_extra)
        RR->>AM: resourceFileReaders.TryGetValue(fileName)
        alt 命中
            RR->>RR: 从缓存读
        else 未命中
            RR->>Disk: File.OpenRead + search <container>
            RR->>AM: TryAdd(fileName, reader)
            RR->>RR: 读
        end
    end
```

## 3. 状态机：`FileReader.PreProcessing`

```mermaid
stateDiagram-v2
    [*] --> RawFile: 打开文件
    RawFile --> Bundled: signature == "UnityFS"/"UnityWeb"/"ENCR"
    RawFile --> Webified: signature == "UnityWeb" v<6
    RawFile --> GZip: \x1f\x8b GZip magic
    RawFile --> Zip: PK\x03\x04 ZIP magic
    RawFile --> Brotli: Brotli magic
    RawFile --> CABLike: 需要解密 (Mark / EnsembleStar / ...)

    Bundled --> BundleFileType: Dispatch
    Webified --> WebFileType: Dispatch
    GZip --> AssetsFile: DecompressGZip → 重新检测
    Brotli --> AssetsFile: DecompressBrotli → 重新检测
    Zip --> AssetsFile: ZipArchive 解压 → 重新检测
    CABLike --> AssetsFile: DecryptMark 等 → 重新检测

    state choice <<choice>>
    BundleFileType --> [*]: FileType=BundleFile
    WebFileType --> [*]: FileType=WebFile
    AssetsFile --> [*]: FileType=AssetsFile
```