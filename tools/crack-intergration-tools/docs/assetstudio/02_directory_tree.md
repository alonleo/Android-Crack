# 02 目录结构（Directory Tree）

本目录树覆盖 `/home/leo/文档/android-crack/tools/source-projects/assetstudio/` 下所有源码与配置文件，每个文件附 1-2 行中文说明。

> 行号信息以最后一次读取的代码为准；如代码有更新，请以实际行号为准。

## 顶层

```
assetstudio/
├── AssetStudio.sln                       解决方案文件，包含 6 个 csproj
├── README.md / RELEASE.md / VERSION / AI_ONBOARDING.md / AI_QUICK_REFERENCE.md / CURRENT_STATE.md / DEBUG_LOGGING*.md / UNITY_6000_FIXES.md
│                                          项目文档与维护说明
├── LICENSE                               MIT 许可证
├── .gitattributes / .gitignore / .github/ Git 元数据与 PR 模板
```

## `AssetStudio/` — 核心库（解析、TypeTree、Crypto、Game 注册）

```
AssetStudio/
├── AssetStudio.csproj                    主库 csproj（net8.0;net10.0），引用 MessagePack/Newtonsoft.Json/ZstdSharp
├── AssetsManager.cs                      顶层编排器：并行加载、依赖解析、对外 LoadFiles/LoadFolder/Clear
├── BundleFile.cs                         UnityFS / UnityWeb / ENCR 容器解析，多种 LZ4/Zstd/LZMA 解压
├── SerializedFile.cs                     SerializedFile 元数据与对象表解析（TypeTree、Version 兼容）
├── ImportHelper.cs                       split 文件合并 + 20+ 种游戏解密 (Mark/EnsembleStar/AnchorPanic/...) + GZip/Brotli 解压
├── AssetsHelper.cs                       CABMap / AssetMap 构建与加载；CABMap 是 (filename→path,offset,deps) 的二进制索引
├── GameManager.cs                        38 种游戏类型注册表 + GameType 扩展方法（IsGI/IsBH3/IsSR/IsMhyGroup/...）
├── FileReader.cs                         FileReader（含 PreProcessing 扩展：检测 type 并调用对应 Decrypt*）
├── FileType.cs / FileIdentifier.cs       FileType 枚举（BundleFile/AssetsFile/WebFile/BlkFile/...）
├── ObjectReader.cs                       反序列化单个 Object 的二进制 reader
├── ResourceReader.cs                     Resources 文件流读取 + 通过 assetsManager.resourceFileReaders 解析跨文件引用
├── EndianBinaryReader.cs                 大小端感知的二进制读取，Unity 各版本字段读取函数集中地
├── MhyFile.cs / BlbFile.cs               米哈游专属 .blk / .blb 容器解析
├── WebFile.cs                            UnityWeb / UnityRaw 旧式 .unity3d 容器解析
├── OffsetStream.cs                       block-file 多段读取
├── XORStream.cs                          XOR 解密流（用于 Blk）
├── UnityCNManager.cs                     UnityCN 加密 key 索引管理（GUI/CLI 入口）
├── UnityCN.cs                            UnityCN AES + 块级解密
├── AIVersionManager.cs                   拉取 gi-asset-indexes GitHub 仓库的 asset_index.json
├── ResourceIndex.cs                      解析 asset_index.json（GI 容器 ID → 真实路径）
├── ResourceMap.cs                        进程级单例，缓存 ResourceIndex
├── AssetIndex.cs / AssetMap.cs           AssetMap 序列化数据模型
├── TypeTree.cs / TypeTreeNode.cs / TypeTreeHelper.cs
│                                          TypeTree 节点结构与解码
├── SerializedType.cs / SerializedFileHeader.cs / SerializedFileFormatVersion.cs
│                                          SerializedFile 子结构
├── IImported.cs                          FBX 中间表示的 ImportedFrame/Mesh/Material/Texture 等
├── ClassIDType.cs                        所有 Unity ClassID 枚举 + Parse/Export 静态控制
├── TypeFlags.cs                          静态注册表，控制哪些 ClassID 参与 Parse 与 Export
├── BuildType.cs / BuildTarget.cs / ExportType.cs / ExportTypeList.cs / ExportListType.cs
│                                          各种枚举
├── FileIdentifier.cs / LocalSerializedObjectIdentifier.cs / ObjectInfo.cs
│                                          SerializedFile 子结构
├── Logger.cs / ILogger.cs / Progress.cs  日志与进度抽象
├── Keys.json                             内置的 MIHOYO/UnityCN 备用 keys
├── CommonString.cs                       TypeTree string buffer 公用字符串池
│
├── Classes/                              40 个 Unity 类的强类型表示
│   ├── Object.cs                         所有 Unity 类的根，含 Dump()/GetRawData()
│   ├── EditorExtension.cs / NamedObject.cs / Behaviour.cs / Component.cs / GameObject.cs / Transform.cs / RectTransform.cs
│   ├── Mesh.cs / MeshFilter.cs / MeshRenderer.cs / SkinnedMeshRenderer.cs / Sprite.cs / SpriteAtlas.cs
│   ├── Texture.cs / Texture2D.cs / Material.cs / Shader.cs
│   ├── AudioClip.cs / VideoClip.cs / MovieTexture.cs / Font.cs / TextAsset.cs
│   ├── MonoBehaviour.cs / MonoScript.cs / Animation.cs / AnimationClip.cs
│   ├── Animator.cs / AnimatorController.cs / AnimatorOverrideController.cs / RuntimeAnimatorController.cs / Avatar.cs
│   ├── AssetBundle.cs / PlayerSettings.cs / BuildSettings.cs / ResourceManager.cs / IndexObject.cs / MiHoYoBinData.cs / PPtr.cs
│
├── Crypto/                               加密工具集
│   ├── AES.cs / MT19937_64.cs / XORShift128.cs   通用原语
│   ├── CryptoHelper.cs                   通用 helper
│   ├── BlkUtils.cs                       Blk 文件解密（XORStream）
│   ├── Mr0kUtils.cs                      Mr0k 加密块解密（SBox + InitVector + 索引表）
│   ├── NetEaseUtils.cs / OPFPUtils.cs / FairGuardUtils.cs / UnityCN.cs
│   │                                      各游戏厂商专用
│
├── 7zip/                                 7zip LZMA 解码器的纯 C# 移植（仅解码）
│   ├── Common/                           CRC / InBuffer / OutBuffer / CommandLineParser
│   ├── Compress/LZ/                      LzBinTree / LzInWindow / LzOutWindow / IMatchFinder
│   ├── Compress/LZMA/                    LzmaBase / LzmaDecoder / LzmaEncoder
│   ├── Compress/RangeCoder/              RangeCoder / RangeCoderBit / RangeCoderBitTree
│   └── ICoder.cs                         7zip 接口
│
├── Brotli/                               Brotli 解码器纯 C# 实现（来自 Org.Brotli.Dec）
│   ├── BitReader.cs / IntReader.cs / Decode.cs / Dictionary.cs / Context.cs / Huffman.cs
│   ├── HuffmanTreeGroup.cs / Prefix.cs / RunningState.cs / State.cs / Transform.cs / Utils.cs
│   ├── WordTransformType.cs              词变换类型枚举
│   ├── BrotliInputStream.cs              Stream 适配
│   └── BrotliRuntimeException.cs
│
├── LZ4/                                  LZ4 系列解码器
│   ├── LZ4.cs                            标准 LZ4
│   ├── LZ4Inv.cs                         Endfield 反向变体
│   └── LZ4Lit.cs                         ExAstris 变体
│
├── Math/                                 数学库
│   ├── Color.cs / Vector2.cs / Vector3.cs / Vector4.cs / Matrix4x4.cs / Quaternion.cs / XForm.cs
│   ├── Half.cs                           IEEE 754 half-precision
│   ├── HalfHelper.cs                     Half ↔ Single 转换
│   └── Float.cs                          Unity 5+ 的 Float 类型（带 m_Numerics/m_Value）
│
├── Extensions/
│   ├── ByteArrayExtensions.cs            Search / SequenceEqual 扩展
│   └── StreamExtensions.cs               流复制、长度读取
│
├── Helpers/
│   └── KVPConverter.cs                   YAML KVP 转换器
│
├── YAML/                                 自实现 YAML emitter（用于 Object.Dump）
│   ├── Base/
│   │   ├── Emitter.cs                    缩进/字符流式发射器
│   │   ├── IYAMLExportable.cs            YAML 可导出接口
│   │   ├── MappingStyle.cs / ScalarStyle.cs / SequenceStyle.cs / ScalarType.cs / MetaType.cs / YAMLNodeType.cs / YAMLTag.cs
│   │   ├── YAMLDocument.cs / YAMLNode.cs / YAMLMappingNode.cs / YAMLScalarNode.cs / YAMLSequenceNode.cs / YAMLWriter.cs
│   └── Utils/Extensions/                 Array / BitConverter / Emitter / IDictionaryExport / IDictionary / IEnumerable / IList / Primitive / StringBuilder / YAMLMappingNode 扩展
```

## `AssetStudio.Utility/` — 转换器与辅助工具

```
AssetStudio.Utility/
├── AssetStudio.Utility.csproj            net8.0;net10.0，引用核心库
├── ModelConverter.cs                     ModelConverter : IImported — 把 GameObject/Animator 转为 ImportedFrame/Mesh/Material/Animation
├── ModelExporter.cs                      ModelExporter.ExportFbx（调 FbxExporter 写文件）
├── Texture2DConverter.cs                 Texture2DConverter — 30+ 种 TextureFormat 解码到 BGRA32
├── ShaderConverter.cs                    ShaderConverter.Convert + ShaderProgram/ShaderSubProgram + HLSLDecompiler（P/Invoke）
├── AudioClipConverter.cs                 FMOD 驱动的音频解码 + .wav 写入
├── SpriteHelper.cs                       Sprite → 图像
├── FontHelper.cs                         P/Invoke AddFontMemResourceEx（私有字体）
├── AssemblyLoader.cs                     Mono.Cecil 程序集加载（MonoBehaviour 反序列化辅助）
├── MonoBehaviourConverter.cs             MonoBehaviour → JSON
├── SerializedTypeHelper.cs               SerializedType 辅助（GetTypeTree 等）
├── TypeDefinitionConverter.cs            Mono.Cecil TypeDefinition ↔ SerializedType
├── ImageFormat.cs                        图像格式枚举（Png/Jpeg/Bmp/Webp）
├── ConsoleHelper.cs                      控制台显示/隐藏（GUI 子窗口）
├── ImageExtensions.cs                    Image 转字节 / 字节转 Image
├── Texture2DExtensions.cs                Texture2D → Image / Stream 的扩展
├── ACL/                                  Animation Compression Library 纯 C# 移植
│   ├── ACL.cs
│   └── ACLExtensions.cs
├── CSspv/                                SPIRV 反汇编器（来自 SPIRV-Cross 项目）
│   ├── Disassembler.cs / Reader.cs / Instruction.cs / OperandType.cs / ParsedInstruction.cs / Module.cs
│   ├── Types.cs / SpirV.Core.Grammar.cs / SpirV.Meta.cs / EnumValuesExtensions.cs
├── FMOD Studio API/                      FMOD C# 绑定（fmod.cs / fmod_dsp.cs / fmod_errors.cs）
├── Smolv/                                Smolv SPIRV 解码器
│   ├── SmolvDecoder.cs / OpData.cs / SpvOp.cs
├── SpirVShaderConverter.cs               Smolv → 文本
├── Unity.CecilTools/                      Mono.Cecil 类型扩展
│   ├── CecilUtils.cs / ElementType.cs
│   └── Extensions/MethodDefinitionExtensions.cs / ResolutionExtensions.cs / TypeDefinitionExtensions.cs / TypeReferenceExtensions.cs
├── Unity.SerializationLogic/
│   ├── UnityEngineTypePredicates.cs      Unity 内置类型谓词
│   └── UnitySerializationLogic.cs        Unity 序列化规则
└── YAML/                                 动画 YAML 输出
    ├── AnimationClipConverter.cs         AnimationClip → YAML
    ├── AnimationClipExtensions.cs        AnimationClip 扩展
    ├── CustomCurveResolver.cs            自定义曲线解析
    └── MuscleHelper.cs                   Avatar muscle 数据
```

## `AssetStudio.FBXNative/` — 原生 C++ FBX 写入器

```
AssetStudio.FBXNative/
├── AssetStudio.FBXNative.vcxproj         C++ DLL 工程
├── api.cpp / api.h                       C ABI 入口（被 FbxDll.cs P/Invoke）
├── asfbx_context.cpp/h                   FBX 上下文
├── asfbx_anim_context.cpp/h              动画上下文
├── asfbx_morph_context.cpp/h             morph（blendshape）上下文
├── asfbx_skin_context.cpp/h              骨骼蒙皮上下文
├── utils.cpp/h / bool32_t.h / dllexport.h / resource.h   工具与跨平台宏
```

## `AssetStudio.FBXWrapper/` — C# 包装

```
AssetStudio.FBXWrapper/
├── AssetStudio.FBXWrapper.csproj         引用 PInvoke
├── Fbx.cs                                Fbx static class + ExportOptions + EulerToQuaternion
├── FbxDll.cs                             对原生 API 的低级包装（每个 extern "C" 函数对应一个方法）
├── FbxExporter.cs                        高层 FbxExporter（写一个完整 FBX 文件）
├── FbxExporterContext.cs                 FbxExporter 上下文封装
├── FbxExporterContext.PInvoke.cs         上下文相关 P/Invoke
└── Fbx.PInvoke.cs                        Fbx 全局 P/Invoke 函数
```

## `AssetStudio.PInvoke/`

```
AssetStudio.PInvoke/
├── AssetStudio.PInvoke.csproj
└── DllLoader.cs                          跨平台原生 DLL 加载
```

## `AssetStudio.GUI/` — WinForms GUI

```
AssetStudio.GUI/
├── AssetStudio.GUI.csproj                net8.0-windows;net10.0-windows，引用全部下游项目
├── App.config                            配置
├── Program.cs                            入口（仅 Application.Run(new MainForm())）
├── MainForm.cs (3118)                    主窗口：菜单/树/列表/OpenGL/FMOD/状态栏/事件
├── MainForm.Designer.cs (1571)           Windows Forms Designer 自动生成（不在本档覆盖范围）
├── Studio.cs (960)                       GUI 静态 Studio（mirrors CLI. Studio）
├── Exporter.cs (557)                     GUI 资产导出（与 CLI 几乎一致）
├── ExportOptions.cs / ExportOptions.Designer.cs
│                                          导出选项对话框（图像格式、骨骼参数、UV 配置）
├── AssetBrowser.cs                       独立的资产浏览器窗口（基于 AssetMap）
├── AssetBrowser.Designer.cs
├── Components/
│   ├── AssetItem.cs                      资产条目包装（含 TreeNode / UniqueID / FullSize / Container 等）
│   ├── GameObjectTreeNode.cs             场景树节点
│   ├── GOHierarchy.cs                    场景层级辅助
│   ├── OpenFolderDialog.cs               自定义文件夹选择对话框
│   └── TypeTreeItem.cs                   ClassID → TypeTree 列表条目
├── DirectBitmap.cs                       直接位图（用于快速预览）
├── GUILogger.cs                          GUILogger 实现 ILogger
├── UnityCNForm.cs / UnityCNForm.Designer.cs  UnityCN key 选择窗口
├── Properties/Resources.Designer.cs / Properties/Settings.Designer.cs
│                                          资源 & 设置（VS 自动生成）
└── Libraries/x86/ / Libraries/x64/      bundled 原生 DLL（不在仓库内，由构建脚本复制）
```

## `AssetStudio.CLI/` — 命令行

```
AssetStudio.CLI/
├── AssetStudio.CLI.csproj                net8.0-windows;net10.0-windows，引用核心 + Utility
├── App.config                            Settings.Default 持久化
├── Program.cs (201)                      Main → CommandLine.Init → CommandLine.RegisterOptions → Program.Run
├── Studio.cs (508)                       CLI 静态 Studio
├── Exporter.cs (524)                     CLI 资产导出
├── Settings.cs / Settings.Designer.cs / Settings.settings  App.config 自动生成
├── Components/
│   ├── AssetItem.cs                      CLI 端 AssetItem（与 GUI 略不同）
│   └── CommandLine.cs (271)              System.CommandLine 选项注册 + Options/OptionsBinder
└── Resources/                            嵌入资源（如有）
```