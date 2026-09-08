# 10 · UABEANext 术语表

| 术语 | 含义 |
|---|---|
| **UABEANext** | nesrak1 的新版 Unity Asset 编辑器；基于 Dock.Avalonia + MVVM。 |
| **Dock.Avalonia** | Dock 库（类似 Visual Studio 的可停靠窗布局）。 |
| **MVVM** | Model-View-ViewModel；通过 [ObservableProperty]/[RelayCommand] 源生成。 |
| **CommunityToolkit.Mvvm** | .NET MVVM 工具集；提供 [ObservableProperty]/[RelayCommand] 属性源生成器。 |
| **WorkspaceItem** | 文件树节点；可以是 AssetsFile / BundleFile / ResourceFile。 |
| **WorkspaceItemType** | enum：AssetsFile / BundleFile / ResourceFile。 |
| **Workspace** | 顶层 workspace；持有 AssetsManager + PluginLoader + AssetNamer + RootItems。 |
| **RootItems** | ObservableCollection<WorkspaceItem>；文件树根。 |
| **ItemLookup** | Dictionary<string, WorkspaceItem>；按名字查找。 |
| **UnsavedItems** | HashSet<WorkspaceItem>；待保存。 |
| **ModifiedItems** | HashSet<WorkspaceItem>；已修改。 |
| **ModifyMutex** | Mutex；防止并发修改。 |
| **LoadIndex** | WorkspaceItem 的加载序号；用于排序。 |
| **FileSyncContext** | SynchronizationContext；在 LoadBundle 等异步路径中安全更新 RootItems。 |
| **DuplicateWorkspaceFileException** | 加载重复文件时抛。 |
| **ContainerTool** | 解析 AssetBundle/ResourceManager 的 m_Container。 |
| **ContainerToolManager** | 缓存 ContainerTool 跨 WorkspaceItem。 |
| **AssetInst** | AssetFileInfo 子类；增加 AssetName 等 UI 字段。 |
| **RangeObservableCollection** | 自定义 ObservableCollection，支持 AddRange。 |
| **FixupAssetsFile** | 把 AssetFileInfo 替换为 AssetInst + 设置 AssetName。 |
| **TryLoadClassDatabase** | 按 Unity version 自动加载 classdata.tpk。 |
| **AssetNamer** | 取 human-friendly asset 名（带缓存 + NameReadOptimization）。 |
| **NameReadOptimization** | 优化字段访问（避免 IO 多次）。 |
| **ConfigurationManager** | 全局静态；持有 Settings + SaveConfig/LoadConfig。 |
| **ConfigurationValues** | 配置项 POCO。 |
| **ConfigurationItem** | 单配置项（带 PropertyChanged）。 |
| **ConfigurationThemeType** | enum：SimpleDark / SimpleLight。 |
| **DockFactory / IDockFactory** | Dock 库接口；构建布局。 |
| **IRootDock / IDock / IDockWindow / IDocument / ITool** | Dock 抽象。 |
| **Tool / Document** | Dock 中两类窗口：工具栏 vs 文档。 |
| **ViewLocator** | VM → View 自动映射（基于命名约定）。 |
| **WeakReferenceMessenger** | CommunityToolkit.Mvvm 提供的消息总线；VM 之间解耦通信。 |
| **Message (record)** | 消息体；如 SelectedWorkspaceItemChangedMessage。 |
| **IStorageProvider** | Avalonia 11 抽象的文件系统接口；跨平台。 |
| **IStorageFile / IStorageFolder** | 存储对象。 |
| **FilePickerOpenOptions / SaveOptions / FolderPickerOpenOptions** | Avalonia 对话框选项。 |
| **DialogService** | 主对话框服务（实现 IDialogService）。 |
| **DummyDialogService** | 测试桩。 |
| **IDialogAware<T>** | 通用对话框接口；返回 T?。 |
| **PluginLoadContext** | AssemblyLoadContext 子类；隔离加载插件。 |
| **AssemblyLoadContext** | .NET Core/5+ 提供的程序集隔离机制。 |
| **AssemblyDependencyResolver** | 解析 DLL 依赖到物理路径。 |
| **IUavPluginOption** | 菜单项接口（UABEA 的 UABEAPluginOption 的升级）。 |
| **IUavPluginPreviewer** | 预览器接口（UABEANext 新增）。 |
| **IUavPluginFunctions** | 主机能力；提供给 Option 插件使用。 |
| **IUavPluginPreviewerFunctions** | 预览主机能力；提供给 Previewer 插件使用。 |
| **UavPluginFunctions** | IUavPluginFunctions 默认实现。 |
| **UavPluginMode** | enum：Import / Export / Info。 |
| **UavPluginPreviewerType** | enum：None / Image / Text / Mesh。 |
| **PluginItemInfo** | 菜单项 VM；可触发 Execute。 |
| **PluginOptionModePair / PluginPreviewerTypePair** | 元组。 |
| **AssetImport / AssetExport** | 类型树 .txt/.json 导入导出。 |
| **AssetInfo/* (8 文件)** | 元信息类（GeneralInfo / ExternalInfo / TypeTreeInfo / ScriptInfo / BuildTarget / TypeTreeUINode / TypeTreeTypeInfo / TypeTreeNodeConverter）。 |
| **MeshObj / Channel / MeshEnums** | 内存网格表示。 |
| **Topology** | 网格拓扑：Triangles / Lines / ... |
| **ChannelFormat** | 顶点属性格式：Float / Vector2/3/4 / Color / ... |
| **SearchLogic / SearchResultItem** | 并发搜索。 |
| **HierarchyItem** | GameObject 层级遍历。 |
| **DocumentManager** | Document dock 管理。 |
| **DevToolsAdblock** | 关闭 Avalonia DevTools 广告。 |
| **AssetsTools.NET (vendored)** | 解析库（submodule）。 |
| **cuttlefish** | Crunch 压缩库（开源）。 |
| **textureencoder** | BC/ETC/ASTC 编码器（推测基于 ISPC）。 |
| **PVRTexLib** | PowerVR 纹理编解码（iOS PVRTC）。 |
| **StbImage*Sharp** | stb_image 的 .NET 包装。 |
| **Silk.NET.OpenGL** | .NET OpenGL 绑定（用于 Mesh 渲染）。 |
| **Samboy063.LibCpp2IL** | IL2CPP 元数据解析库。 |
| **Mono.Cecil** | Mono.Cecil.dll 解析。 |
| **AssetRipper.TextureDecoder** | BC/ETC2 格式解码。 |
| **DynamicData** | 响应式集合库（基于 Rx.NET）。 |
| **Microsoft.Extensions.DependencyInjection** | 标准 DI 容器。 |
| **AvaloniaEdit.TextMate** | VSCode 兼容语法高亮。 |
| **classdata.tpk** | Unity Class Database（与 UABEA 共享）。 |
| **ConfigurationThemeType** | 主题枚举。 |
| **Avalonia.Themes.Fluent / Simple** | 主题集。 |
| **Avalonia.Skia** | Skia 渲染后端。 |
| **Plugins.LoadPluginsInDirectory** | 从 plugins/ 加载（UABEA 是 Assembly.LoadFrom；UABEANext 是 ALC）。 |
| **Replacer** | 修改物化机制（来自 AssetsTools.NET）。 |
| **AssetsReplacerFromMemory / FromStream / Remover** | 单 .assets 修改。 |
| **BundleReplacerFromMemory / FromStream / FromAssets / Remover / Renamer** | bundle 修改。 |
| **MonoBehaviour** | Unity 脚本绑定对象。 |
| **Texture2D / Sprite / Mesh / AudioClip / TextAsset / Font** | Unity asset 类型。 |
| **m_PlatformBlob / m_StreamData / m_ImageData** | Texture2D 字段。 |
| **m_Vertices / m_Indices / m_Channels / m_Topology / m_LocalAABB** | Mesh 字段。 |
| **m_Script / m_Name** | TextAsset / GameObject / Mesh 通用字段。 |
| **PPtr / FileID / PathID** | Unity 对象引用。 |
| **TypeTree** | Unity 类型描述。 |
| **TypeTreeEnabled** | 文件是否带完整 type tree。 |
| **bigIDEnabled** | 64 位 PathID。 |
| **TargetPlatform / BuildTarget** | 字节序、对齐、纹理格式选择。 |
| **UnityVersion** | "x.y.z" 字符串。 |
| **SpriteAtlas** | 多 sprite 容器（UABEANext 新增 SpriteAtlasLookup）。 |
| **.emip** | 仅 UABEA 支持；UABEANext 移除。 |
| **PluginPreviewer.Desktop.exe** | 独立进程；承载 MeshPreviewerControl + OpenGL。 |
| **IPC** | 进程间通信（推测用 stdin/stdout 或命名管道）。 |
| **uabeacrash.log** | UABEANext 的崩溃日志（继承自 UABEA）。 |
| **Avalonia 11 / .NET 8** | 运行时。 |
| **PluginLoadContext isCollectible: true** | ALC 可 GC。 |
| **MessageBroker** | WeakReferenceMessenger.Default。 |
| **SelectionValidForPlugin / SupportsSelection** | 插件兼容性检测（UABEA / UABEANext 同名但参数不同）。 |
| **ImportRawAsset / DumpRawAsset** | 字节级导入导出。 |
| **ImportTextAsset / DumpTextAsset** | 类型树文本导入导出。 |
| **ImportJsonAsset / DumpJsonAsset** | JSON 导入导出。 |
| **RecurseTextDump / ImportTextAssetLoop** | 文本递归核心。 |
| **RecurseJsonDump / RecurseJsonImport** | JSON 递归核心。 |
| **TextDumpManagedReferencesRegistry** | SerializeReference v1/v2 dump。 |
| **JsonImportManagedReferencesRegistry** | SerializeReference v1/v2 import。 |