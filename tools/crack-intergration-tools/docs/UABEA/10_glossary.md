# 10 · UABEA 术语表

| 术语 | 含义 |
|---|---|
| **UABEA / UABE** | Unity Asset Bundle Extractor。UABEA 指 nesrak1 的 Avalonia 重写版（UABEAvalonia）。 |
| **AssetStudio** | Razmoth/Perfare 的另一个 Unity 反向工程工具；侧重全场景导出与多游戏解密。 |
| **AssetsTools.NET** | nesrak1 开发的 .NET 库，用于解析 Unity 的 SerializedFile / BundleFile / TypeTree。是 UABEA 的核心依赖（vendored in `Libs/`）。 |
| **Bundle / .bundle** | Unity 的 UnityFS 容器，封装若干压缩的 .assets + .resS + .resource 文件。 |
| **AssetsFile / .assets** | 包含若干 serialized object 的核心 Unity 文件。每个 bundle 内可有多个 .assets。 |
| **SerializedFile** | AssetsTools.NET 中 `AssetsFile` 类的逻辑名；包含 metadata + object table + type tree。 |
| **TypeTree** | Unity 用于在字节流中序列化对象时携带类型信息的结构。UABEA 用它来 dump/edit 单个字段。 |
| **TypeTree .txt** | UABEA 文本 dump 格式：`0/1 typeName fieldName (= value)`，前导空格表缩进。 |
| **Replacer** | AssetsTools.NET 的修改机制。所有修改不直接改源文件，而是构造一个 Replacer，在 Write 时应用。 |
| **AssetsReplacer** | 单 .assets 内一个 asset 的修改（FromMemory/FromStream/Remover）。 |
| **BundleReplacer** | bundle 内一个 entry 的修改（FromMemory/FromStream/FromAssets/Remover/Renamer）。 |
| **AssetsRemover** | 标记删除某 PathID 的 asset。 |
| **AssetsReplacerFromMemory** | Replacer 直接携带新字节数据（最常用）。 |
| **AssetsReplacerFromStream** | Replacer 持有 stream + offset + size，按需读取。 |
| **BundleReplacerFromMemory** | Bundle 级别的完整字节替换。 |
| **BundleReplacerFromAssets** | Bundle 内 .assets 资产的子修改（写入 bundle 时会调 `Init` 二次初始化）。 |
| **BundleRemover** | Bundle 内删除一个 entry。 |
| **BundleRenamer** | Bundle 内重命名一个 entry。 |
| **.emip** | EMIP（Extensible Mod Installer Package）格式 —— UABE 自家的 mod 包格式。包含 modName/Creators/Description + affected files + replacers + 可选 classdb。 |
| **InstallerPackageFile** | .emip 解析后内存表示。 |
| **InstallerPackageAssetsDesc** | .emip 内单个 affected file 描述。 |
| **classdata.tpk** | Unity Class Database 的压缩二进制格式。UABEA 用它来把 TypeTree 字段对应到类成员。无 tpk 时只能 dump 通用字段。 |
| **ClassDatabaseFile** | classdata.tpk 的内存表示（AssetsTools.NET 提供）。 |
| **MonoTempGenerator** | AssetsTools.NET 接口，用于在没有完整 type tree 时通过 Cpp2IL/MonoCecil 推断 MonoBehaviour 字段。 |
| **Cpp2IlTempGenerator** | 用 libil2cpp.so + global-metadata.dat 推断（IL2CPP 二进制游戏）。 |
| **MonoCecilTempGenerator** | 用 Managed/*.dll 推断（标准 Mono 游戏）。 |
| **MonoBehaviour** | Unity 的脚本绑定对象。自定义字段依赖 type tree；缺失 tpk 时无法解析。 |
| **m_PlatformBlob** | Unity Texture2D 的可选 Switch 平台块数据（包含 gob count）。 |
| **m_StreamData** | Unity Texture2D 的可选 resS 引用（path + offset + size）。 |
| **resS / .resS** | 共享资源文件，bundle 内独立于 .assets，存放大型纹理 / 音频。 |
| **.resource** | Unity 5.x 时代的另一种资源文件（被 .resS 取代）。 |
| **Switch 平台** | Nintendo Switch；Unity 在该平台使用 GOB swizzle 编码 BC/DXT 纹理。 |
| **GOB swizzle** | Switch 纹理格式：4×8 block 块重排。UABEA 用 `Texture2DSwitchDeswizzler` 处理。 |
| **Crunch** | Unity 自家的 DXT/ETC2 压缩库（开源）。纹理格式名以 `Crunched` 结尾。 |
| **TextureFormat** | Unity 内部纹理格式枚举（DXT1, DXT5, BC1..7, ETC2, ASTC, RGBA32, ...）。 |
| **ASTC** | Adaptive Scalable Texture Compression（移动平台）。 |
| **Block size** | 压缩纹理的最小块大小（BC1=8 bytes/16 px，BC3=16 bytes/16 px，ASTC 4x4=16 bytes/16 px）。 |
| **PVRTC** | PowerVR Texture Compression（旧 iOS）。 |
| **FMOD / FSB** | FMOD 音频库；Unity 默认使用 FMOD 打包音频为 FSB（FSB5 格式）。Fmod5Sharp 解析。 |
| **FmodSoundBank / FmodSample** | Fmod5Sharp 解出的内存结构。 |
| **RebuildAsStandardFileFormat** | Fmod5Sharp 把 FSB 样本转回 WAV/OGG/MP3 等。 |
| **CompressionFormat** | Unity 内部的音频压缩格式枚举。 |
| **.ttf / .otf** | TrueType / OpenType 字体。UABEA 通过 `m_FontData` 字段识别。 |
| **TextAsset** | Unity 的字符串/字节资源，`m_Script` 字段。 |
| **Managed/** | Unity 标准 Mono 编译产物（Assembly-CSharp.dll 等）所在的目录。 |
| **global-metadata.dat** | Unity IL2CPP 元数据文件，Cpp2IlTempGenerator 需要。 |
| **libil2cpp.so** | Unity IL2CPP 运行时的 ELF 库。 |
| **FindCpp2IlFiles** | AssetsTools.NET.Cpp2IL 提供的辅助类，在游戏目录中查找 il2cpp 文件。 |
| **Workspace** | 工作区抽象。UABEA 有 AssetWorkspace（asset 级）与 BundleWorkspace（entry 级）。 |
| **PluginManager** | 加载 `<exe-dir>/plugins/*.dll` 并按 UABEAPlugin 接口收集。 |
| **UABEAPlugin** | 插件接口（`Init() → PluginInfo`）。 |
| **UABEAPluginOption** | 插件菜单项（`SelectionValidForPlugin` + `ExecutePlugin`）。 |
| **UABEAPluginAction** | 动作类型（Import/Export/Console/Create）。 |
| **UABEAPluginMenuInfo** | 菜单项的运行时表示。 |
| **AssemblyLoadContext** | .NET Core/5+ 提供的程序集隔离机制。UABEA 用 Assembly.LoadFrom 共享主程序上下文（区别于 UABEANext）。 |
| **Avalonia** | 跨平台 .NET UI 框架（XAML + 渲染后端 Skia）。 |
| **TextMate grammar** | VSCode 兼容的语法高亮格式。UABEA 用它高亮 TypeTree .txt。 |
| **Drag/Drop** | Avalonia 的 `AddHandler(DragDrop.DropEvent, Drop)` 模式。 |
| **MainWindow / InfoWindow** | 主窗 + asset 列表窗（前者管 bundle，后者管单文件）。 |
| **AssetDataTreeView** | TypeTree 树视图（懒加载）。 |
| **AssetTypeValueField** | AssetsTools.NET 的中间表示：具体值 + 模板 + 字段名。 |
| **AssetTypeTemplateField** | 类型描述（仅模板，不含值）。 |
| **AssetTypeReference** | SerializeReference 字段的类型引用。 |
| **ManagedReferencesRegistry** | SerializeReference 注册表（v1/v2）。 |
| **ExternalInfo** | 跨文件依赖信息（其他 .assets / .bundle）。 |
| **FileID / PathID** | Unity 对象引用：`FileID` = 0 指向同文件；非 0 指向第 N 个 external。 |
| **PPtr** | Unity 的对象指针结构：`{ fileId, pathId }`。 |
| **bigIDEnabled** | Unity 2017+ 引入的 64 位 PathID 标志。 |
| **TypeTreeEnabled** | Unity 2019.3+ 可选字段：是否带完整 type tree；为 false 时只能靠 cldb 推断。 |
| **TargetPlatform** | `BuildTarget` 枚举，决定字节序、对齐规则、纹理格式选择。 |
| **UnityVersion** | `x.y.z` 字符串，影响 ClassPackage 匹配。 |
| **Align** | 字节对齐到 4 字节边界（某些 PPtr / Array）。 |
| **ReadCountStringInt32 / ReadCountStringInt16** | AssetsTools.NET 的"长度前缀字符串"读取方式。 |
| **SevenZip.Compression.LZMA** | .NET 的 LZMA 库（来自 SevenZipSharp），AssetsTools.NET 用它解压 LZMA bundle。 |
| **LZ4 / LZ4HC** | UnityFS 使用的两种 LZ4 压缩变种。 |
| **PPtr.FromField / SetFilePathFromFile** | AssetsTools.NET 的 PPtr 字段转换工具。 |
| **BundleHelper.LoadAssetDataFromBundle / GetDirInfo** | AssetsTools.NET 的 bundle 操作辅助。 |
| **InfoWindow** | 单 .assets 的 UI。 |
| **AvaloniaList** | Avalonia 提供的 ObservableCollection 替代。 |
| **AnonymousObserver** | Avalonia ReactiveUI 的简单观察者。 |
| **ThemeHandler** | UABEA 内部的浅/深色 + Fluent/Simple 主题切换。 |
| **ConfigurationManager** | `config.json` 持久化。 |
| **uabeacrash.log** | 崩溃日志。 |