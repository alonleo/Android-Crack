# 03 架构总览（Architecture）

## 1. 分层架构

AssetStudio 采用清晰的 **分层 + 静态状态** 架构。底层为 IO 与解析，中间层为核心数据结构，顶层为 GUI/CLI 双前端。**两个项目都把 `AssetsManager`、`Studio`、`AssemblyLoader` 设为 static global**，因此不需要 DI 容器。

### 1.1 模块依赖图

```mermaid
flowchart TD
    subgraph FRONTEND["前端 (Entry Points)"]
        GUI["AssetStudio.GUI<br/>WinForms + OpenTK + FMOD"]
        CLI["AssetStudio.CLI<br/>System.CommandLine"]
    end

    subgraph ORCHESTRATION["编排层"]
        StaticStudioGUI["Studio (GUI static)"]
        StaticStudioCLI["Studio (CLI static)"]
        AM["AssetsManager"]
        AH["AssetsHelper (CABMap / AssetMap)"]
        IH["ImportHelper (split/decrypt)"]
        GM["GameManager (game-type registry)"]
    end

    subgraph CORE_TYPES["核心类型"]
        SF["SerializedFile"]
        BF["BundleFile"]
        Mhy["MhyFile"]
        Web["WebFile"]
        Blk["BlkFile"]
        ObjClasses["Classes/* (Unity Object hierarchy)"]
    end

    subgraph UTIL["AssetStudio.Utility"]
        MC["ModelConverter"]
        TC["Texture2DConverter"]
        SC["ShaderConverter"]
        AC["AudioClipConverter"]
        SH["SpriteHelper"]
        MBC["MonoBehaviourConverter"]
        AL["AssemblyLoader (Mono.Cecil)"]
        ME["ModelExporter"]
    end

    subgraph FBX["FBX 写入"]
        FBXExporter["FbxExporter"]
        FBXWrapper["FbxDll / Fbx.PInvoke"]
        FBXNative["AssetStudio.FBXNative (C++ DLL)"]
    end

    CRYPTO["Crypto/*<br/>(AES, Mr0k, Blk, NetEase, OPFP,<br/>FairGuard, UnityCN, XORShift128)"]
    COMPRESS["7zip / Brotli / LZ4 / ZstdSharp<br/>(LZX/LZMA/Zstd 解码)"]
    MATH["Math/* (Vector / Quaternion / Color)"]
    YAML["YAML/* (emitter)"]

    GUI --> StaticStudioGUI
    CLI --> StaticStudioCLI
    StaticStudioGUI --> AM
    StaticStudioCLI --> AM
    GUI --> AH
    CLI --> AH
    AM --> IH
    AM --> GM
    AM --> SF
    AM --> BF
    AM --> Mhy
    AM --> Web
    AM --> Blk
    IH --> CRYPTO
    BF --> COMPRESS
    SF --> MATH
    SF --> YAML
    SF --> ObjClasses
    GUI --> MC
    GUI --> TC
    GUI --> SC
    GUI --> AC
    CLI --> MC
    CLI --> TC
    CLI --> SC
    CLI --> AC
    StaticStudioGUI --> ME
    StaticStudioCLI --> ME
    ME --> FBXExporter
    FBXExporter --> FBXWrapper --> FBXNative
    GUI --> MBC
    CLI --> MBC
    MBC --> AL
    TC --> COMPRESS
    SC --> COMPRESS
    SC --> FBXWrapper
```

### 1.2 关键设计决策

1. **静态 `Studio` 类持有全局状态**：`assetsManager`、`assemblyLoader`、`exportableAssets` 都是 `static`。GUI/CLI 各自一份，互不干扰。
2. **并行 IO**：所有"批处理"任务（Load/Read/Export）都用 `Parallel.For` / `Parallel.ForEach`，度数为 `Environment.ProcessorCount`。
3. **`FileReader.PreProcessing(Game)` 扩展方法**：把"游戏类型感知"的解密逻辑封装成 FileReader 上的链式扩展，再由 `AssetsManager.LoadFile(FileReader)` 调度。
4. **TypeTree 驱动反序列化**：`ObjectReader` 通过 `m_SerializedType.m_Type.m_Nodes` 逐字段读取。
5. **`ResourceIndex` / `AIVersionManager`**：独立缓存系统，专门处理 GI 系列的 container ID → 真实路径映射（从 `gi-asset-indexes` GitHub 仓库动态拉取）。
6. **原生 P/Invoke 边界**：`FbxExporter` 与 `HLSLDecompiler` 是仅有的两处原生调用边界；其余均为纯 C#。

## 2. 核心类继承与组合

### 2.1 Game 类型继承（`AssetStudio/GameManager.cs`）

```mermaid
classDiagram
    class GameType {
        <<enum>>
        Normal
        UnityCN
        GI
        GI_Pack
        GI_CB1
        GI_CB2
        GI_CB3
        GI_CB3Pre
        BH3
        BH3Pre
        BH3PrePre
        SR_CB2
        SR
        ZZZ_CB1
        TOT
        Naraka
        EnsembleStars
        OPFP
        FakeHeader
        FantasyOfWind
        ShiningNikki
        HelixWaltz2
        NetEase
        AnchorPanic
        DreamscapeAlbireo
        ImaginaryFest
        AliceGearAegis
        ProjectSekai
        CodenameJump
        GirlsFrontline
        Reverse1999
        ArknightsEndfield
        JJKPhantomParade
        MuvLuvDimensions
        PartyAnimals
        LoveAndDeepspace
        SchoolGirlStrikers
        ExAstris
        PerpetualNovelty
    }

    class Game {
        +string Name
        +GameType Type
        +Game(GameType)
        +ToString() string
    }

    class Mr0k {
        +byte[] ExpansionKey
        +byte[] SBox
        +byte[] InitVector
        +byte[] BlockKey
        +byte[] PostKey
    }

    class Blk {
        +byte[] ExpansionKey
        +byte[] SBox
        +byte[] InitVector
        +ulong InitSeed
    }

    class Mhy {
        +byte[] MhyShiftRow
        +byte[] MhyKey
        +byte[] MhyMul
    }

    class GameTypes {
        <<static extension>>
        +IsNormal()
        +IsGI() / IsGIGroup() / IsGISubGroup()
        +IsBH3() / IsBH3Group()
        +IsSR() / IsSRGroup()
        +IsMhyGroup()
        +IsBlockFile()
        +IsUnityCN()
        +...
    }

    GameManager ..> Game : holds Dictionary
    Game <|-- Mr0k
    Game <|-- Blk
    Blk <|-- Mhy
    Game --> GameType
```

### 2.2 Object 类继承（`AssetStudio/Classes/*.cs`）

```mermaid
classDiagram
    class Object {
        +assetsFile
        +reader
        +byteSize
        +m_PathID
        +version
        +type
        +Dump()
        +GetRawData()
        +ExportYAML()
    }
    class EditorExtension
    class NamedObject {
        +string m_Name
    }
    class PPtr~T~ {
        +m_PathID
        +m_FileID
        +TryGet(T) bool
        +IsNull
    }

    Object <|-- EditorExtension
    EditorExtension <|-- NamedObject
    NamedObject <|-- Behaviour
    NamedObject <|-- AssetBundle
    NamedObject <|-- Texture
    NamedObject <|-- TextAsset
    NamedObject <|-- Font
    NamedObject <|-- MonoScript
    NamedObject <|-- PlayerSettings
    NamedObject <|-- BuildSettings
    NamedObject <|-- Shader
    NamedObject <|-- MonoBehaviour
    NamedObject <|-- ResourceManager
    NamedObject <|-- MiHoYoBinData
    NamedObject <|-- Avatar
    NamedObject <|-- IndexObject

    Texture <|-- Texture2D

    Behaviour <|-- Component
    Component <|-- Transform
    Component <|-- MeshFilter
    Component <|-- MeshRenderer
    Component <|-- SkinnedMeshRenderer
    Component <|-- Animation
    Component <|-- Animator

    Object --> PPtr : references
```

> `RuntimeAnimatorController` 是 `AnimatorController` / `AnimatorOverrideController` 的共同父。

### 2.3 `IImported` 中间表示（FBX 输出中间结构）

```mermaid
classDiagram
    class IImported {
        <<interface>>
    }
    class ImportedFrame {
        +Name
        +LocalPosition
        +LocalRotation
        +LocalScale
        +Path
        +AddChild()
        +FindFrameByPath()
        +FindRelativeFrameWithPath()
    }
    class ImportedMesh {
        +Path
        +SubmeshList
        +VertexList
        +hasNormal/hasUV/hasColor/hasTangent
        +BoneList
    }
    class ImportedSubmesh {
        +Material
        +BaseVertex
        +FaceList
    }
    class ImportedFace {
        +VertexIndices[3]
    }
    class ImportedVertex {
        +Vertex / Normal / UV[][] / Color
        +Tangent
        +BoneIndices / Weights
    }
    class ImportedMaterial {
        +Name / Diffuse / Ambient / Emissive / Specular / Reflection / Shininess / Transparency
        +Textures
    }
    class ImportedTexture {
        +Stream
        +Name
    }
    class ImportedKeyframedAnimation {
        +Name / SampleRate / TrackList
    }
    class ImportedAnimationKeyframedTrack {
        +Path / Attribute
        +Translations / Rotations / Scalings
        +BlendShape
    }
    class ImportedMorph {
        +Path / Channels
    }
    class ModelConverter {
        +RootFrame
        +MeshList
        +MaterialList
        +TextureList
        +AnimationList
        +MorphList
    }

    IImported <|.. ModelConverter
    ModelConverter --> ImportedFrame : RootFrame
    ModelConverter --> ImportedMesh : MeshList
    ModelConverter --> ImportedMaterial : MaterialList
    ModelConverter --> ImportedTexture : TextureList
    ModelConverter --> ImportedKeyframedAnimation : AnimationList
    ImportedMesh --> ImportedSubmesh : SubmeshList
    ImportedSubmesh --> ImportedFace : FaceList
    ImportedFace --> ImportedVertex
    ImportedMaterial --> ImportedTexture
    ImportedKeyframedAnimation --> ImportedAnimationKeyframedTrack : TrackList
```

## 3. 调用方向

- **下行（依赖方向）**：GUI/CLI → Studio（静态） → AssetsManager → SerializedFile / BundleFile / MhyFile / ...
- **上行（数据流方向）**：FileReader → SerializedFile → Object（强类型） → Studio.exportableAssets → Exporter → 输出文件
- **横向**：Utility 项目独立于前端项目，被两端通过 `using static` 引入；不会反过来引用 Studio/AssetsManager
- **原生边界**：`AssetStudio.Utility` 通过 `AssetStudio.FBXWrapper` 调用 `AssetStudio.FBXNative`；`ShaderConverter` 通过 `AssetStudio.PInvoke.DllLoader` 加载 `HLSLDecompiler.dll`

## 4. 线程模型

- **GUI**：UI 线程持有 `MainForm`；`AssetsManager.LoadFiles/ReadAssets/ProcessAssets` 跑在 `Task.Run` 里；导出跑在 `Task.Run` 里，通过 `BeginInvoke` 回到 UI 线程刷新进度条 / 状态栏
- **CLI**：单线程主流程，但 `assetsManager.LoadFiles`、`AssetsHelper.LoadFiles` 内部用 `Parallel.For` 进行并行 IO；`ExportAssets` 用 `Parallel.ForEach` 并行导出
- **取消**：`AssetsManager.tokenSource`、`AssetsHelper.tokenSource` 是 `CancellationTokenSource`；GUI 的 "Abort" 菜单调用 `tokenSource.Cancel()`