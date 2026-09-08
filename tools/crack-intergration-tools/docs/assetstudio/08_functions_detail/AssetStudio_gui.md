# `AssetStudio_gui.md` — GUI 函数详细说明

本章详细列出 `AssetStudio.GUI/`（csproj `AssetStudio.GUI.csproj`）下被覆盖的 public/internal 函数。`MainForm.Designer.cs` 等 Windows Forms 自动生成文件不在此文档范围内。

---

## 1. `AssetStudio.GUI/Studio.cs`

### `Studio.ExtractFolder(string, string)`
- **签名**：`static int ExtractFolder(string path, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:34`
- **可见性**：public
- **返回值**：`int`（成功提取的文件数）
- **副作用**：调用 `Progress.Reset/Report`
- **调用**：`MainForm.extractFolderToolStripMenuItem_Click` (`MainForm.cs:371`)
- **调用了**：`Studio.ExtractFile(string, string)`
- **简要说明**：遍历目录下所有文件并提取

### `Studio.ExtractFile(string[], string)`
- **签名**：`static int ExtractFile(string[] fileNames, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:50`
- **可见性**：public
- **调用**：`MainForm.extractFileToolStripMenuItem_Click` (`MainForm.cs:354`)
- **调用了**：`Studio.ExtractFile(string, string)`
- **简要说明**：批量提取

### `Studio.ExtractFile(string, string)`
- **签名**：`static int ExtractFile(string fileName, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:63`
- **可见性**：public
- **调用了**：`new FileReader`、`FileReader.PreProcessing`、`ExtractBundleFile`、`ExtractWebDataFile`、`ExtractBlkFile`、`ExtractBlockFile`
- **简要说明**：FileType 分派后调用对应 Extract*

### `Studio.ExtractBundleFile(FileReader, string)`
- **签名**：`static int ExtractBundleFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:81`
- **可见性**：private
- **调用了**：`new BundleFile`、`Studio.StatusStripUpdate`、`ExtractStreamFile`
- **简要说明**：把 bundle 解压到 `<name>_unpacked/`

### `Studio.ExtractWebDataFile(FileReader, string)`
- **签名**：`static int ExtractWebDataFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:101`
- **可见性**：private
- **调用了**：`new WebFile`、`Studio.StatusStripUpdate`、`ExtractStreamFile`
- **简要说明**：处理 WebFile 提取

### `Studio.ExtractBlkFile(FileReader, string)`
- **签名**：`static int ExtractBlkFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:114`
- **可见性**：private
- **调用了**：`BlkUtils.Decrypt`、`OffsetStream`、`ExtractBundleFile`、`ExtractMhyFile`
- **简要说明**：Blk 提取

### `Studio.ExtractBlockFile(FileReader, string)`
- **签名**：`static int ExtractBlockFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:145`
- **可见性**：private
- **调用了**：`OffsetStream`、`ExtractBundleFile`
- **简要说明**：BlockFile 提取

### `Studio.ExtractMhyFile(FileReader, string)`
- **签名**：`static int ExtractMhyFile(FileReader reader, string savePath)`
- **位置**：`AssetStudio.GUI/Studio.cs:161`
- **可见性**：private
- **调用了**：`new MhyFile`、`Studio.StatusStripUpdate`、`ExtractStreamFile`
- **简要说明**：Mhy 提取

### `Studio.ExtractStreamFile(string, List<StreamFile>)`
- **签名**：`static int ExtractStreamFile(string extractPath, List<StreamFile> fileList)`
- **位置**：`AssetStudio.GUI/Studio.cs:181`
- **可见性**：private
- **简要说明**：写所有 stream 到磁盘

### `Studio.UpdateContainers()`
- **签名**：`static void UpdateContainers()`
- **位置**：`AssetStudio.GUI/Studio.cs:205`
- **可见性**：public
- **调用**：
  - `Studio.BuildAssetData`（`GUI/Studio.cs:372`）
  - `MainForm.toolStripComboBox1_SelectedIndexChanged` (`MainForm.cs:2162`)
  - `MainForm.UpdateContainers` (`MainForm.cs:2184`)
- **调用了**：`ResourceIndex.GetContainer`
- **简要说明**：把 GI 的 container ID 替换为真实路径

### `Studio.BuildAssetData()`
- **签名**：`static (string productName, List<TreeNode> treeNodeCollection) BuildAssetData()`
- **位置**：`AssetStudio.GUI/Studio.cs:234`
- **可见性**：public
- **调用**：`MainForm.BuildAssetStructures` (`MainForm.cs:385`)
- **调用了**：`new AssetItem`、`PPtr.TryGet`、`ObjectReader`、`TreeNode` / `GameObjectTreeNode`
- **简要说明**：构建 exportableAssets + 场景树（按 `originalPath` → fileName → GameObject 嵌套）

### `Studio.BuildClassStructure()`
- **签名**：`static Dictionary<string, SortedDictionary<int, TypeTreeItem>> BuildClassStructure()`
- **位置**：`AssetStudio.GUI/Studio.cs:489`
- **可见性**：public
- **调用**：`MainForm.BuildAssetStructures` (`MainForm.cs:386`)
- **调用了**：`new TypeTreeItem`
- **简要说明**：构建 unityVersion → ClassID → TypeTreeItem 的索引

### `Studio.ExportAssets(string, List<AssetItem>, ExportType, bool)`
- **签名**：`static Task ExportAssets(string savePath, List<AssetItem> toExportAssets, ExportType exportType, bool openAfterExport)`
- **位置**：`AssetStudio.GUI/Studio.cs:530`
- **可见性**：public
- **调用**：`MainForm.ExportAssets` (`MainForm.cs:2075`)
- **调用了**：`Parallel.ForEach`、`Studio.StatusStripUpdate`、`OpenFolderInExplorer`、`ExportRawFile`、`ExportDumpFile`、`ExportConvertFile`、`ExportJSONFile`
- **简要说明**：并行导出

### `Studio.ExportAssetsList(string, List<AssetItem>, ExportListType)`
- **签名**：`static Task ExportAssetsList(string savePath, List<AssetItem> toExportAssets, ExportListType exportListType)`
- **位置**：`AssetStudio.GUI/Studio.cs:631`
- **可见性**：public
- **调用**：`MainForm.ExportAssetsList` (`MainForm.cs:2109`)
- **简要说明**：导出 asset 列表（XML）

### `Studio.ExportSplitObjects(string, TreeNodeCollection)`
- **签名**：`static Task ExportSplitObjects(string savePath, TreeNodeCollection nodes)`
- **位置**：`AssetStudio.GUI/Studio.cs:681`
- **可见性**：public
- **调用**：`MainForm.exportAllObjectssplitToolStripMenuItem1_Click` (`MainForm.cs:1911`)
- **调用了**：`GetNodes`、`CollectNode`、`ExportGameObject(GameObject, string)`、`OpenFolderInExplorer`
- **简要说明**：按 tree node split 导出

### `Studio.ExportAnimatorWithAnimationClip(AssetItem, List<AssetItem>, string)`
- **签名**：`static Task ExportAnimatorWithAnimationClip(AssetItem animator, List<AssetItem> animationList, string exportPath)`
- **位置**：`AssetStudio.GUI/Studio.cs:775`
- **可见性**：public
- **调用**：`MainForm.exportAnimatorwithAnimationClipMenuItem_Click` (`MainForm.cs:1688`)
- **调用了**：`ExportAnimator(AssetItem, string, List<AssetItem>)`
- **简要说明**：Animator + 选中 AnimationClips 导出 FBX

### `Studio.ExportObjectsWithAnimationClip(string, TreeNodeCollection, List<AssetItem>)`
- **签名**：`static Task ExportObjectsWithAnimationClip(string exportPath, TreeNodeCollection nodes, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Studio.cs:799`
- **可见性**：public
- **调用**：`MainForm.ExportObjects` (`MainForm.cs:1722`)
- **调用了**：`GetSelectedParentNode`、`ExportGameObject(GameObject, string, List<AssetItem>)`、`OpenFolderInExplorer`
- **简要说明**：选中 GameObject 导出

### `Studio.ExportObjectsMergeWithAnimationClip(string, List<GameObject>, List<AssetItem>)`
- **签名**：`static Task ExportObjectsMergeWithAnimationClip(string exportPath, List<GameObject> gameObjects, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Studio.cs:839`
- **可见性**：public
- **调用**：`MainForm.ExportMergeObjects` (`MainForm.cs:1767`)
- **调用了**：`ExportGameObjectMerge`、`OpenFolderInExplorer`
- **简要说明**：合并多个 GameObject 导出

### `Studio.ExportNodesWithAnimationClip(string, List<TreeNode>, List<AssetItem>)`
- **签名**：`static Task ExportNodesWithAnimationClip(string exportPath, List<TreeNode> nodes, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Studio.cs:864`
- **可见性**：public
- **调用**：`MainForm.ExportNodes` (`MainForm.cs:1812`)
- **调用了**：`GetSelectedParentNode`、`ExportGameObjectMerge`、`OpenFolderInExplorer`
- **简要说明**：tree nodes 导出

### `Studio.GetSelectedParentNode(TreeNodeCollection, List<GameObject>)`
- **签名**：`static void GetSelectedParentNode(TreeNodeCollection nodes, List<GameObject> gameObjects)`
- **位置**：`AssetStudio.GUI/Studio.cs:903`
- **可见性**：public
- **调用**：`Studio.ExportObjectsWithAnimationClip`、`Studio.ExportNodesWithAnimationClip`、`MainForm.ExportMergeObjects` (`MainForm.cs:1746`)
- **简要说明**：从树中收集 checked GameObject

### `Studio.MonoBehaviourToTypeTree(MonoBehaviour)`
- **签名**：`static TypeTree MonoBehaviourToTypeTree(MonoBehaviour m_MonoBehaviour)`
- **位置**：`AssetStudio.GUI/Studio.cs:918`
- **可见性**：public
- **调用**：`GUI.Exporter.ExportMonoBehaviour` (`GUI/Exporter.cs:101`)、`GUI.Exporter.ExportDumpFile` (`GUI/Exporter.cs:489`)、`MainForm.PreviewMonoBehaviour` (`MainForm.cs:1197`)
- **调用了**：`OpenFolderDialog`、`assemblyLoader.Load`、`m_MonoBehaviour.ConvertToTypeTree(assemblyLoader)`
- **简要说明**：弹窗选 DLL 目录并转换 MonoBehaviour 为 TypeTree

### `Studio.DumpAsset(Object)`
- **签名**：`static string DumpAsset(Object obj)`
- **位置**：`AssetStudio.GUI/Studio.cs:936`
- **可见性**：public
- **调用**：`MainForm.selectAsset` (`MainForm.cs:882`)、`MainForm.tabControl2_SelectedIndexChanged` (`MainForm.cs:2232`)
- **调用了**：`Object.Dump`、`Studio.MonoBehaviourToTypeTree`、`JsonConvert.SerializeObject`
- **简要说明**：Object → 文本（dump 或 JSON）

### `Studio.OpenFolderInExplorer(string)`
- **签名**：`static void OpenFolderInExplorer(string path)`
- **位置**：`AssetStudio.GUI/Studio.cs:953`
- **可见性**：public
- **调用**：被多个 Export 方法调用
- **简要说明**：用 explorer 打开文件夹

---

## 2. `AssetStudio.GUI/Exporter.cs`

### `GUI.Exporter.ExportTexture2D(AssetItem, string)`
- **签名**：`static bool ExportTexture2D(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:12`
- **可见性**：public
- **调用了**：`Texture2D.ConvertToImage`、`Image.WriteToStream`、`m_Texture2D.image_data.GetData`、`TryExportFile`
- **简要说明**：Texture 导出（GUI 版）

### `GUI.Exporter.ExportAudioClip(AssetItem, string)`
- **签名**：`static bool ExportAudioClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:41`
- **调用了**：`new AudioClipConverter`、`AudioClipConverter.ConvertToWav`、`TryExportFile`
- **简要说明**：AudioClip 导出

### `GUI.Exporter.ExportShader(AssetItem, string)`
- **签名**：`static bool ExportShader(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:66`
- **调用了**：`m_Shader.Convert`、`TryExportFile`
- **简要说明**：Shader 导出

### `GUI.Exporter.ExportTextAsset(AssetItem, string)`
- **签名**：`static bool ExportTextAsset(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:76`
- **简要说明**：TextAsset 导出

### `GUI.Exporter.ExportMonoBehaviour(AssetItem, string)`
- **签名**：`static bool ExportMonoBehaviour(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:93`
- **调用了**：`Studio.MonoBehaviourToTypeTree`、`JsonConvert.SerializeObject`、`TryExportFile`
- **简要说明**：MonoBehaviour JSON 导出

### `GUI.Exporter.ExportMiHoYoBinData(AssetItem, string)`
- **签名**：`static bool ExportMiHoYoBinData(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:109`
- **调用了**：`m_MiHoYoBinData.Dump`、`TryExportFile`
- **简要说明**：MiHoYoBinData 导出

### `GUI.Exporter.ExportFont(AssetItem, string)`
- **签名**：`static bool ExportFont(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:150`
- **调用了**：`TryExportFile`
- **简要说明**：Font 导出（.ttf/.otf）

### `GUI.Exporter.ExportMesh(AssetItem, string)`
- **签名**：`static bool ExportMesh(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:168`
- **调用了**：`TryExportFile`
- **简要说明**：Mesh → OBJ

### `GUI.Exporter.ExportVideoClip(AssetItem, string)`
- **签名**：`static bool ExportVideoClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:250`
- **调用了**：`m_VideoClip.m_VideoData.WriteData`、`TryExportFile`
- **简要说明**：VideoClip 导出

### `GUI.Exporter.ExportMovieTexture(AssetItem, string)`
- **签名**：`static bool ExportMovieTexture(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:263`
- **调用了**：`TryExportFile`
- **简要说明**：MovieTexture 导出

### `GUI.Exporter.ExportSprite(AssetItem, string)`
- **签名**：`static bool ExportSprite(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:272`
- **调用了**：`Sprite.GetImage`、`Image.WriteToStream`、`TryExportFile`
- **简要说明**：Sprite 导出

### `GUI.Exporter.ExportRawFile(AssetItem, string)`
- **签名**：`static bool ExportRawFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:292`
- **调用了**：`item.Asset.GetRawData`、`TryExportFile`
- **简要说明**：原始字节导出

### `GUI.Exporter.ExportAnimationClip(AssetItem, string)`
- **签名**：`static bool ExportAnimationClip(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:343`
- **调用了**：`m_AnimationClip.Convert`、`TryExportFile`
- **简要说明**：AnimationClip → .anim

### `GUI.Exporter.ExportAnimator(AssetItem, string, List<AssetItem>)`
- **签名**：`static bool ExportAnimator(AssetItem item, string exportPath, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Exporter.cs:355`
- **调用了**：`new ModelConverter(m_Animator, ...)`、`ExportFbx`、`ExportJSONFile`、`TryExportFolder`
- **简要说明**：Animator → FBX

### `GUI.Exporter.ExportGameObject(AssetItem, string, List<AssetItem>)`
- **签名**：`static bool ExportGameObject(AssetItem item, string exportPath, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Exporter.cs:389`
- **调用了**：`ExportGameObject(GameObject, string, List<AssetItem>)`、`TryExportFolder`
- **简要说明**：GameObject → FBX 重载

### `GUI.Exporter.ExportGameObject(GameObject, string, List<AssetItem>)`
- **签名**：`static bool ExportGameObject(GameObject gameObject, string exportPath, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Exporter.cs:398`
- **调用了**：`new ModelConverter`、`ExportFbx`、`ExportJSONFile`
- **简要说明**：GameObject → FBX（接受 GameObject 而非 AssetItem）

### `GUI.Exporter.ExportGameObjectMerge(List<GameObject>, string, List<AssetItem>)`
- **签名**：`static void ExportGameObjectMerge(List<GameObject> gameObject, string exportPath, List<AssetItem> animationList)`
- **位置**：`AssetStudio.GUI/Exporter.cs:434`
- **调用了**：`new ModelConverter(rootName, ...)`、`ExportFbx`、`ExportJSONFile`
- **简要说明**：合并 GameObject → FBX

### `GUI.Exporter.ExportDumpFile(AssetItem, string)`
- **签名**：`static bool ExportDumpFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:482`
- **调用了**：`Studio.MonoBehaviourToTypeTree`、`TryExportFile`
- **简要说明**：Object.Dump() 或 TypeTree 反序列化

### `GUI.Exporter.ExportConvertFile(AssetItem, string)`
- **签名**：`static bool ExportConvertFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:500`
- **调用了**：`ExportGameObject`、`ExportTexture2D`、`ExportAudioClip`、`ExportShader`、`ExportTextAsset`、`ExportMonoBehaviour`、`ExportFont`、`ExportMesh`、`ExportVideoClip`、`ExportMovieTexture`、`ExportSprite`、`ExportAnimator`、`ExportAnimationClip`、`ExportMiHoYoBinData`、`ExportJSONFile`、`ExportRawFile`
- **简要说明**：按 item.Type 分派

### `GUI.Exporter.ExportJSONFile(AssetItem, string)`
- **签名**：`static bool ExportJSONFile(AssetItem item, string exportPath)`
- **位置**：`AssetStudio.GUI/Exporter.cs:539`
- **调用了**：`JsonConvert.SerializeObject`、`TryExportFile`
- **简要说明**：JSON 导出

### `GUI.Exporter.FixFileName(string)`
- **签名**：`static string FixFileName(string str)`
- **位置**：`AssetStudio.GUI/Exporter.cs:551`
- **简要说明**：清洗文件名

---

## 3. `AssetStudio.GUI/MainForm.cs`（仅核心事件处理，Designer 自动生成的不计）

### `MainForm` 构造器
- **签名**：`MainForm()`
- **位置**：`AssetStudio.GUI/MainForm.cs:84`
- **可见性**：public ctor
- **副作用**：初始化 WinForms；订阅 `OnVersionPrompt`；初始化 FMOD
- **调用了**：`InitializeComponent`、`InitializeExportOptions`、`InitializeProgressBar`、`InitializeLogger`、`InitalizeOptions`、`FMODinit`
- **简要说明**：WinForms 主窗体构造

### `MainForm.InitializeExportOptions`
- **签名**：`void InitializeExportOptions()`
- **位置**：`AssetStudio.GUI/MainForm.cs:99`
- **可见性**：private
- **简要说明**：从 `Properties.Settings.Default` 初始化导出选项 checkbox

### `MainForm.InitializeLogger`
- **签名**：`void InitializeLogger()`
- **位置**：`AssetStudio.GUI/MainForm.cs:118`
- **可见性**：private
- **调用了**：`new GUILogger`、`ConsoleHelper.*`、`Logger.Default`
- **简要说明**：分配/显示 console 子窗口

### `MainForm.InitializeProgressBar`
- **签名**：`void InitializeProgressBar()`
- **位置**：`AssetStudio.GUI/MainForm.cs:145`
- **可见性**：private
- **简要说明**：绑定 `Progress.Default = new Progress<int>(SetProgressBarValue)`

### `MainForm.InitalizeOptions`
- **签名**：`void InitalizeOptions()`
- **位置**：`AssetStudio.GUI/MainForm.cs:151`
- **可见性**：private
- **调用了**：`GameManager.GetGames`、`GameManager.GetGame`、`TypeFlags.SetTypes`、`AssetsHelper.LoadCABMapInternal`、`UnityCNManager.SetKey`
- **简要说明**：初始化 AssetMap 下拉、Game 下拉、TypeFlags

### `MainForm.AssetsManager_OnVersionPrompt`
- **签名**：`void AssetsManager_OnVersionPrompt(object sender, VersionPromptEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:188`
- **可见性**：private
- **副作用**：可能设置 `SpecifyUnityVersion`、`specifyUnityVersion.Text`
- **简要说明**：Unity 版本询问弹窗

### `MainForm.MainForm_DragEnter`
- **签名**：`void MainForm_DragEnter(object sender, DragEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:277`
- **可见性**：private
- **简要说明**：拖拽高亮

### `MainForm.MainForm_DragDrop`
- **签名**：`void MainForm_DragDrop(object sender, DragEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:285`
- **可见性**：private
- **调用了**：`LoadPaths`
- **简要说明**：拖拽落点

### `MainForm.LoadPaths`
- **签名**：`async void LoadPaths(params string[] paths)`
- **位置**：`AssetStudio.GUI/MainForm.cs:294`
- **可见性**：public
- **调用了**：`ResetForm`、`assetsManager.LoadFolder/LoadFiles`、`BuildAssetStructures`
- **简要说明**：加载入口

### `MainForm.loadFile_Click`
- **签名**：`async void loadFile_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:310`
- **可见性**：private
- **调用了**：`openFileDialog1`、`assetsManager.LoadFiles`、`BuildAssetStructures`
- **简要说明**：Load File 菜单

### `MainForm.loadFolder_Click`
- **签名**：`async void loadFolder_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:329`
- **可见性**：private
- **调用了**：`OpenFolderDialog`、`assetsManager.LoadFolder`、`BuildAssetStructures`
- **简要说明**：Load Folder 菜单

### `MainForm.extractFileToolStripMenuItem_Click`
- **签名**：`async void extractFileToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:344`
- **可见性**：private
- **调用了**：`Studio.ExtractFile(string[], string)`、`StatusStripUpdate`
- **简要说明**：Extract File 菜单

### `MainForm.extractFolderToolStripMenuItem_Click`
- **签名**：`async void extractFolderToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:360`
- **可见性**：private
- **调用了**：`Studio.ExtractFolder`、`StatusStripUpdate`
- **简要说明**：Extract Folder 菜单

### `MainForm.BuildAssetStructures`
- **签名**：`async void BuildAssetStructures()`
- **位置**：`AssetStudio.GUI/MainForm.cs:377`
- **可见性**：private
- **调用了**：`Studio.BuildAssetData`、`Studio.BuildClassStructure`、`sceneTreeView.BeginUpdate/EndUpdate`
- **简要说明**：树 + 列表 + 类型树构建

### `MainForm.PreviewAsset`
- **签名**：`void PreviewAsset(AssetItem assetItem)`
- **位置**：`AssetStudio.GUI/MainForm.cs:923`
- **可见性**：private
- **调用了**：所有 `PreviewXxx`、`Object.Dump`
- **简要说明**：按 Type 分派预览

### `MainForm.PreviewTexture2D`
- **签名**：`void PreviewTexture2D(AssetItem assetItem, Texture2D m_Texture2D)`
- **位置**：`AssetStudio.GUI/MainForm.cs:989`
- **可见性**：private
- **调用了**：`Texture2D.ConvertToImage`、`DirectBitmap`、`PreviewTexture`
- **简要说明**：纹理预览（支持 B/G/R/A 通道开关）

### `MainForm.PreviewAudioClip`
- **签名**：`void PreviewAudioClip(AssetItem assetItem, AudioClip m_AudioClip)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1047`
- **可见性**：private
- **调用了**：FMOD API
- **简要说明**：音频预览

### `MainForm.PreviewShader`
- **签名**：`void PreviewShader(Shader m_Shader)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1173`
- **可见性**：private
- **调用了**：`m_Shader.Convert`、`PreviewText`
- **简要说明**：Shader 文本预览

### `MainForm.PreviewTextAsset`
- **签名**：`void PreviewTextAsset(TextAsset m_TextAsset)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1185`
- **可见性**：private
- **调用了**：`Encoding.UTF8.GetString`、`PreviewText`
- **简要说明**：TextAsset 预览

### `MainForm.PreviewMonoBehaviour`
- **签名**：`void PreviewMonoBehaviour(MonoBehaviour m_MonoBehaviour)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1192`
- **可见性**：private
- **调用了**：`m_MonoBehaviour.ToType`、`Studio.MonoBehaviourToTypeTree`、`JsonConvert.SerializeObject`
- **简要说明**：MonoBehaviour JSON 预览

### `MainForm.PreviewFont`
- **签名**：`void PreviewFont(Font m_Font)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1204`
- **可见性**：private
- **调用了**：`FontHelper.AddFontMemResourceEx`、`PrivateFontCollection`
- **简要说明**：Font 预览

### `MainForm.PreviewMesh`
- **签名**：`void PreviewMesh(Mesh m_Mesh)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1254`
- **可见性**：private
- **调用了**：OpenGL 初始化数据
- **简要说明**：Mesh OpenGL 预览

### `MainForm.PreviewGameObject`
- **签名**：`void PreviewGameObject(GameObject m_GameObject)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1404`
- **可见性**：private
- **调用了**：`new ModelConverter`、`PreviewModel`
- **简要说明**：GameObject OpenGL 预览

### `MainForm.PreviewAnimator`
- **签名**：`void PreviewAnimator(Animator m_Animator)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1419`
- **可见性**：private
- **调用了**：`new ModelConverter(m_Animator, ...)`、`PreviewModel`
- **简要说明**：Animator OpenGL 预览

### `MainForm.PreviewAnimationClip`
- **签名**：`void PreviewAnimationClip(AnimationClip clip)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1435`
- **可见性**：private
- **调用了**：`clip.Convert`、`PreviewText`
- **简要说明**：AnimationClip 文本预览

### `MainForm.PreviewModel`
- **签名**：`void PreviewModel(ModelConverter model)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1443`
- **可见性**：private
- **调用了**：`CreateVAO`、`ChangeGLSize`
- **简要说明**：通用 Model 预览

### `MainForm.PreviewSprite`
- **签名**：`void PreviewSprite(AssetItem assetItem, Sprite m_Sprite)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1521`
- **可见性**：private
- **调用了**：`Sprite.GetImage`、`DirectBitmap`、`PreviewTexture`
- **简要说明**：Sprite 预览

### `MainForm.PreviewTexture`
- **签名**：`void PreviewTexture(DirectBitmap bitmap)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1537`
- **可见性**：private
- **简要说明**：设置预览背景图

### `MainForm.PreviewText`
- **签名**：`void PreviewText(string text)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1548`
- **可见性**：private
- **简要说明**：设置 textPreviewBox

### `MainForm.SetProgressBarValue`
- **签名**：`void SetProgressBarValue(int value)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1554`
- **可见性**：private
- **简要说明**：UI 线程更新 progressBar1

### `MainForm.StatusStripUpdate`
- **签名**：`void StatusStripUpdate(string statusText)`
- **位置**：`AssetStudio.GUI/MainForm.cs:1568`
- **可见性**：private
- **简要说明**：UI 线程更新状态栏

### `MainForm.ResetForm`
- **签名**：`void ResetForm()`
- **位置**：`AssetStudio.GUI/MainForm.cs:1581`
- **可见性**：public
- **调用了**：`assetsManager.Clear`、`assemblyLoader.Clear`、`FMODreset`
- **简要说明**：清空所有 UI 状态

### `MainForm.FilterAssetList`
- **签名**：`void FilterAssetList()`
- **位置**：`AssetStudio.GUI/MainForm.cs:1931`
- **可见性**：private
- **简要说明**：按类型/正则过滤

### `MainForm.UpdateAssetCountStatus`
- **签名**：`void UpdateAssetCountStatus()`
- **位置**：`AssetStudio.GUI/MainForm.cs:1991`
- **可见性**：private
- **简要说明**：更新 selected/total 计数

### `MainForm.ExportAssets(ExportFilter, ExportType)`
- **签名**：`async void ExportAssets(ExportFilter type, ExportType exportType)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2052`
- **可见性**：private
- **调用了**：`OpenFolderDialog`、`Studio.ExportAssets`
- **简要说明**：菜单导出触发

### `MainForm.ExportAssetsList(ExportFilter)`
- **签名**：`void ExportAssetsList(ExportFilter type)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2084`
- **可见性**：private
- **调用了**：`Studio.ExportAssetsList`
- **简要说明**：导出 asset 列表

### `MainForm.specifyGame_SelectedIndexChanged`
- **签名**：`void specifyGame_SelectedIndexChanged(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2289`
- **可见性**：private
- **调用了**：`GameManager.GetGame`、`ResetForm`、`UnityCNManager.SetKey`
- **简要说明**：切换 Game

### `MainForm.specifyNameComboBox_SelectedIndexChanged`
- **签名**：`async void specifyNameComboBox_SelectedIndexChanged(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2309`
- **可见性**：private
- **调用了**：`AssetsHelper.LoadCABMapInternal`
- **简要说明**：切换 CABMap

### `MainForm.buildMapToolStripMenuItem_Click`
- **签名**：`async void buildMapToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2332`
- **可见性**：private
- **调用了**：`AssetsHelper.SetUnityVersion`、`AssetsHelper.BuildCABMap`
- **简要说明**：构建 CABMap

### `MainForm.buildBothToolStripMenuItem_Click`
- **签名**：`async void buildBothToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2387`
- **可见性**：private
- **调用了**：`AssetsHelper.BuildBoth`
- **简要说明**：构建 CABMap + AssetMap

### `MainForm.clearMapToolStripMenuItem_Click`
- **签名**：`void clearMapToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2451`
- **可见性**：private
- **简要说明**：删除 CABMap 文件

### `MainForm.resetToolStripMenuItem_Click`
- **签名**：`void resetToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2477`
- **可见性**：private
- **调用了**：`ResetForm`、`AssetsHelper.Clear`
- **简要说明**：reset

### `MainForm.loadAIToolStripMenuItem_Click`
- **签名**：`async void loadAIToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2535`
- **可见性**：private
- **调用了**：`ResourceIndex.FromFile`、`MainForm.UpdateContainers`
- **简要说明**：加载 asset_index.json

### `MainForm.loadCABMapToolStripMenuItem_Click`
- **签名**：`async void loadCABMapToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2556`
- **可见性**：private
- **调用了**：`AssetsHelper.LoadCABMap`
- **简要说明**：加载 CABMap

### `MainForm.buildAssetMapToolStripMenuItem_Click`
- **签名**：`async void buildAssetMapToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2575`
- **可见性**：private
- **调用了**：`AssetsHelper.SetUnityVersion`、`AssetsHelper.BuildAssetMap`
- **简要说明**：构建 AssetMap

### `MainForm.loadAssetMapToolStripMenuItem_Click`
- **签名**：`void loadAssetMapToolStripMenuItem_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2617`
- **可见性**：private
- **调用了**：`new AssetBrowser(this)`、`assetBrowser.Show`
- **简要说明**：打开 AssetBrowser

### `MainForm.specifyUnityCNKey_Click`
- **签名**：`void specifyUnityCNKey_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2623`
- **可见性**：private
- **调用了**：`new UnityCNForm`、`unitycn.Show`
- **简要说明**：打开 UnityCNForm

### `MainForm.FMODinit`
- **签名**：`void FMODinit()`
- **位置**：`AssetStudio.GUI/MainForm.cs:2630`
- **可见性**：private
- **调用了**：`FMOD.Factory.System_Create`、`system.init`、`system.getMasterSoundGroup`、`masterSoundGroup.setVolume`
- **简要说明**：FMOD 系统初始化

### `MainForm.FMODreset`
- **签名**：`void FMODreset()`
- **位置**：`AssetStudio.GUI/MainForm.cs:2655`
- **可见性**：private
- **调用了**：`sound.release`
- **简要说明**：FMOD 状态重置

### `MainForm.FMODplayButton_Click`
- **签名**：`void FMODplayButton_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2671`
- **可见性**：private
- **简要说明**：FMOD 播放

### `MainForm.FMODpauseButton_Click`
- **签名**：`void FMODpauseButton_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2713`
- **可见性**：private
- **简要说明**：FMOD 暂停

### `MainForm.FMODstopButton_Click`
- **签名**：`void FMODstopButton_Click(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2746`
- **可见性**：private
- **简要说明**：FMOD 停止

### `MainForm.FMODloopButton_CheckedChanged`
- **签名**：`void FMODloopButton_CheckedChanged(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2771`
- **可见性**：private
- **简要说明**：FMOD 循环模式切换

### `MainForm.FMODvolumeBar_ValueChanged`
- **签名**：`void FMODvolumeBar_ValueChanged(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2805`
- **可见性**：private
- **简要说明**：FMOD 音量调节

### `MainForm.FMODprogressBar_Scroll`
- **签名**：`void FMODprogressBar_Scroll(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2813`
- **可见性**：private
- **简要说明**：FMOD 进度条拖动

### `MainForm.FMODprogressBar_MouseDown`
- **签名**：`void FMODprogressBar_MouseDown(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2822`
- **可见性**：private
- **简要说明**：FMOD 鼠标按下

### `MainForm.FMODprogressBar_MouseUp`
- **签名**：`void FMODprogressBar_MouseUp(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2827`
- **可见性**：private
- **简要说明**：FMOD 鼠标松开

### `MainForm.timer_Tick`
- **签名**：`void timer_Tick(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2850`
- **可见性**：private
- **简要说明**：FMOD 播放计时器

### `MainForm.ERRCHECK(FMOD.RESULT)`
- **签名**：`bool ERRCHECK(FMOD.RESULT result)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2887`
- **可见性**：private
- **简要说明**：FMOD 错误检查

### `MainForm.InitOpenTK`
- **签名**：`void InitOpenTK()`
- **位置**：`AssetStudio.GUI/MainForm.cs:2900`
- **可见性**：private
- **调用了**：`GL.CreateProgram`、`GL.CreateShader`、`GL.LinkProgram`、`LoadShader`
- **简要说明**：OpenGL 初始化

### `MainForm.LoadShader(string, ShaderType, int, out int)`
- **签名**：`static void LoadShader(string filename, ShaderType type, int program, out int address)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2927`
- **可见性**：private static
- **调用了**：`GL.CreateShader`、`GL.ShaderSource`、`GL.CompileShader`、`GL.AttachShader`、`GL.DeleteShader`
- **简要说明**：编译 GL shader（资源来自 `Properties.Resources.<name>`）

### `MainForm.CreateVBO(out int, Vector3[], int)`
- **签名**：`static void CreateVBO(out int vboAddress, Vector3[] data, int address)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2937`
- **可见性**：private static
- **调用了**：`GL.GenBuffers`、`GL.BufferData`、`GL.VertexAttribPointer`
- **简要说明**：创建 VBO

### `MainForm.CreateVBO(out int, Vector4[], int)`
- **签名**：`static void CreateVBO(out int vboAddress, Vector4[] data, int address)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2949`
- **可见性**：private static
- **简要说明**：Vector4 VBO

### `MainForm.CreateVBO(out int, Matrix4, int)`
- **签名**：`static void CreateVBO(out int vboAddress, Matrix4 data, int address)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2961`
- **可见性**：private static
- **调用了**：`GL.UniformMatrix4`
- **简要说明**：Matrix4 uniform

### `MainForm.CreateEBO(out int, int[])`
- **签名**：`static void CreateEBO(out int address, int[] data)`
- **位置**：`AssetStudio.GUI/MainForm.cs:2967`
- **可见性**：private static
- **简要说明**：创建 EBO

### `MainForm.CreateVAO`
- **签名**：`void CreateVAO()`
- **位置**：`AssetStudio.GUI/MainForm.cs:2977`
- **可见性**：private
- **调用了**：所有 `CreateVBO/CreateEBO`
- **简要说明**：创建 VAO

### `MainForm.ChangeGLSize(Size)`
- **签名**：`void ChangeGLSize(Size size)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3001`
- **可见性**：private
- **调用了**：`GL.Viewport`
- **简要说明**：调整 viewport

### `MainForm.glControl_Load`
- **签名**：`void glControl_Load(object sender, EventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3017`
- **可见性**：private
- **调用了**：`InitOpenTK`
- **简要说明**：GL 控件初始化

### `MainForm.glControl_Paint`
- **签名**：`void glControl_Paint(object sender, PaintEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3023`
- **可见性**：private
- **调用了**：OpenGL draw calls
- **简要说明**：GL 绘制

### `MainForm.glControl_MouseWheel`
- **签名**：`void glControl_MouseWheel(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3057`
- **可见性**：private
- **简要说明**：滚轮缩放

### `MainForm.glControl_MouseDown`
- **签名**：`void glControl_MouseDown(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3066`
- **可见性**：private
- **简要说明**：鼠标按下

### `MainForm.glControl_MouseMove`
- **签名**：`void glControl_MouseMove(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3080`
- **可见性**：private
- **简要说明**：鼠标移动（旋转/平移）

### `MainForm.glControl_MouseUp`
- **签名**：`void glControl_MouseUp(object sender, MouseEventArgs e)`
- **位置**：`AssetStudio.GUI/MainForm.cs:3105`
- **可见性**：private
- **简要说明**：鼠标松开