# 09 关键调用栈（Call Stacks）

本章汇总 AssetStudio 中 **典型用户操作** 对应的完整调用栈。每条调用栈都标注了关键中间函数所在的 `file:line`。

---

## 调用栈 1：GUI 用户拖入文件夹 → 加载 → 树+列表+预览

```
User 拖拽文件夹到 MainForm
└─ MainForm.MainForm_DragDrop                MainForm.cs:285
   └─ MainForm.LoadPaths                    MainForm.cs:294
      ├─ MainForm.ResetForm                  MainForm.cs:1581
      │  └─ assetsManager.Clear             AssetsManager.cs:907
      ├─ assetsManager.LoadFolder(path)     AssetsManager.cs:73
      │  ├─ AssetsManager.DetectUnityVersionFromFolder(path)
      │  │  ├─ AssetsManager.TryExtractVersionFromFile(filePath)  AssetsManager.cs:243
      │  │  │  └─ new SerializedFile(reader, this)               SerializedFile.cs:50
      │  │  └─ AssetsManager.TryExtractVersionFromBundle(filePath)  AssetsManager.cs:266
      │  │     └─ new BundleFile(reader, Game)                   BundleFile.cs:119
      │  ├─ ImportHelper.MergeSplitAssets(path, true)            ImportHelper.cs:19
      │  ├─ ImportHelper.ProcessingSplitFiles(files)            ImportHelper.cs:49
      │  └─ AssetsManager.Load(files)          AssetsManager.cs:96
      │     ├─ AssetsManager.LoadFile(fullName) [Parallel.For]    AssetsManager.cs:289
      │     │  └─ new FileReader
      │     │  └─ FileReader.PreProcessing(Game)                  FileReader.cs:163
      │     │     └─ [ImportHelper.DecryptXxx 或直接识别]
      │     │  └─ AssetsManager.LoadFile(reader)                  AssetsManager.cs:296
      │     │     ├─ case AssetsFile → LoadAssetsFile(reader)    AssetsManager.cs:330
      │     │     │  ├─ new SerializedFile(reader, this)          SerializedFile.cs:50
      │     │     │  └─ AssetsManager.CheckStrippedVersion(assetsFile)  AssetsManager.cs:838
      │     │     │     └─ SerializedFile.SetVersion(stringVersion)    SerializedFile.cs:259
      │     │     │     └─ [触发 OnVersionPrompt → MainForm.AssetsManager_OnVersionPrompt]
      │     │     ├─ case BundleFile → LoadBundleFile(reader)    AssetsManager.cs:485
      │     │     │  ├─ new BundleFile(reader, Game)             BundleFile.cs:119
      │     │     │  │  ├─ BundleFile.ReadBundleHeader           BundleFile.cs:157
      │     │     │  │  ├─ BundleFile.ReadHeader                 BundleFile.cs:332
      │     │     │  │  ├─ BundleFile.ReadUnityCN                BundleFile.cs:378
      │     │     │  │  ├─ BundleFile.ReadBlocksInfoAndDirectory  BundleFile.cs:408
      │     │     │  │  │  ├─ LZ4.Decompress / Mr0kUtils.Decrypt / ...
      │     │     │  │  └─ BundleFile.ReadBlocks                 BundleFile.cs:529
      │     │     │  │     └─ [switch 6+ 种 compression 解压]
      │     │     │  └─ BundleFile.ReadFiles(blocksStream, path)  BundleFile.cs:302
      │     │     ├─ case WebFile → LoadWebFile                  AssetsManager.cs:542
      │     │     ├─ case BlkFile → LoadBlkFile                  AssetsManager.cs:714
      │     │     │  └─ BlkUtils.Decrypt                         BlkUtils.cs:14
      │     │     ├─ case MhyFile → LoadMhyFile                  AssetsManager.cs:751
      │     │     └─ case BlbFile → LoadBlbFile                  AssetsManager.cs:795
      │     ├─ AssetsManager.ReadAssets                          AssetsManager.cs:937
      │     │  ├─ new ObjectReader(assetsFile.reader, assetsFile, objectInfo, Game)
      │     │  ├─ switch objectReader.type → new Texture2D/AnimationClip/...
      │     │  └─ assetsFile.AddObject(obj)                      SerializedFile.cs:429
      │     └─ AssetsManager.ProcessAssets                       AssetsManager.cs:1010
      │        └─ 关联 GameObject ↔ Transform/Renderer/Animator/Animation/SpriteAtlas↔Sprite
      └─ MainForm.BuildAssetStructures                           MainForm.cs:377
         ├─ Task.Run(Studio.BuildAssetData)                     Studio.cs:234
         │  ├─ new AssetItem(asset) per Object
         │  ├─ 处理 AssetBundle containers / IndexObject mihoyoBinDataNames
         │  ├─ 调用 Studio.UpdateContainers                      Studio.cs:205 (GI)
         │  ├─ 过滤 exportableAssets by type/name/container regex
         │  ├─ 构建 TreeNode 树（originalPath → fileName → GameObject）
         │  └─ return (productName, treeNodeCollection)
         ├─ Task.Run(Studio.BuildClassStructure)                 Studio.cs:489
         ├─ sceneTreeView.Nodes.AddRange(treeNodeCollection)
         ├─ assetListView.VirtualListSize = visibleAssets.Count
         └─ classesListView.Items.Add(...)

User 双击 assetListView 中某行
└─ MainForm.selectAsset                                       MainForm.cs:862
   └─ MainForm.PreviewAsset(assetItem)                          MainForm.cs:923
      ├─ case GameObject → PreviewGameObject                    MainForm.cs:1404
      │  └─ new ModelConverter(gameObject, options, [])
      │  └─ PreviewModel                                       MainForm.cs:1443
      │     ├─ CreateVAO                                       MainForm.cs:2977
      │     └─ glControl.Invalidate
      ├─ case Texture2D → PreviewTexture2D                     MainForm.cs:989
      │  └─ Texture2D.ConvertToImage(true) → Texture2DConverter.DecodeTexture2D
      ├─ case AudioClip → PreviewAudioClip                     MainForm.cs:1047
      │  └─ system.createSound + system.playSound
      ├─ case Shader → PreviewShader                           MainForm.cs:1173
      │  └─ m_Shader.Convert() (→ ShaderConverter.Convert)
      ├─ case TextAsset → PreviewTextAsset                     MainForm.cs:1185
      ├─ case MonoBehaviour → PreviewMonoBehaviour              MainForm.cs:1192
      │  └─ MonoBehaviourToTypeTree + JsonConvert.SerializeObject
      ├─ case Font → PreviewFont                               MainForm.cs:1204
      │  └─ FontHelper.AddFontMemResourceEx
      ├─ case Mesh → PreviewMesh                               MainForm.cs:1254
      │  └─ CreateVAO
      ├─ case Sprite → PreviewSprite                           MainForm.cs:1521
      ├─ case Animator → PreviewAnimator                       MainForm.cs:1419
      ├─ case AnimationClip → PreviewAnimationClip             MainForm.cs:1435
      └─ default → Object.Dump()
```

---

## 调用栈 2：CLI 主流程

```
User: AssetStudio.CLI.exe <input> <output> --game GI --types Texture2D:Both,Shader:Both
└─ Program.Main(args)                                         Program.cs:14
   └─ CommandLine.Init(args)                                  CommandLine.cs:14
      └─ CommandLine.RegisterOptions()                        CommandLine.cs:19
         ├─ new OptionsBinder                                 CommandLine.cs:95
         │  ├─ new Option<...>("--game", ...)
         │  │  GameName.FromAmong(GameManager.GetGameNames())  GameManager.cs:67
         │  ├─ LoggerFlags.SetDefaultValue(...) 等
         └─ rootCommand.SetHandler(Program.Run, optionsBinder)
   └─ rootCommand.Invoke(args)
      └─ Program.Run(Options o)                              Program.cs:16
         ├─ game = GameManager.GetGame(o.GameName)            GameManager.cs:54
         ├─ if game.Type.IsUnityCN: UnityCNManager.TryGetEntry + UnityCN.SetKey  UnityCNManager.cs:50 / UnityCN.cs:50
         ├─ Studio.Game = game
         ├─ Logger.Default = new ConsoleLogger
         ├─ AssetsHelper.SetUnityVersion(o.UnityVersion)      AssetsHelper.cs:36
         ├─ TypeFlags.SetTypes(JsonConvert.DeserializeObject<...>(Settings.Default.types))
         ├─ [解析 o.TypeFilter → 设置 TypeFlags + classTypeFilter]
         ├─ assetsManager.Silent = o.Silent
         ├─ assetsManager.Game = game
         ├─ assetsManager.SpecifyUnityVersion = o.UnityVersion
         ├─ o.Output.Create()
         ├─ if o.Key != default: MiHoYoBinData.Encrypted/Key
         ├─ if o.AIFile: ResourceIndex.FromFile               ResourceIndex.cs:13
         ├─ if o.DummyDllFolder: assemblyLoader.Load           AssemblyLoader.cs
         ├─ [map_op 分支]
         │  ├─ if CABMap + Load: AssetsHelper.BuildCABMap     AssetsHelper.cs:142
         │  │                写 Maps/<mapName>.bin
         │  ├─ if CABMap + (Build): AssetsHelper.LoadCABMapInternal  AssetsHelper.cs:248
         │  ├─ if AssetMap + Load: AssetsHelper.ParseAssetMap  AssetsHelper.cs:504
         │  ├─ if AssetMap + Build: AssetsHelper.BuildAssetMap  AssetsHelper.cs:316
         │  └─ if Both: AssetsHelper.BuildBoth                  AssetsHelper.cs:687
         └─ else (None 或 Load):
            ├─ files = Directory.GetFiles 或 [o.Input.FullName]
            ├─ ImportHelper.MergeSplitAssets(path)             ImportHelper.cs:19
            ├─ ImportHelper.ProcessingSplitFiles(files)         ImportHelper.cs:49
            └─ foreach file in fileList:
               ├─ assetsManager.LoadFiles(file)                 AssetsManager.cs:48
               │  (→ 同 GUI 路径 Load → ReadAssets → ProcessAssets)
               ├─ if assetsManager.assetsFileList.Count > 0:
               │  ├─ Studio.BuildAssetData(classTypeFilter, o.NameFilter, o.ContainerFilter, ref i)  Studio.cs:231
               │  │  └─ ProcessAssetData per Object             Studio.cs:283
               │  │     ├─ new AssetItem
               │  │     ├─ switch on type
               │  │     └─ if exportable: exportableAssets.Add
               │  └─ Studio.ExportAssets(savePath, exportableAssets, groupBy, exportType, imageFormat)  Studio.cs:366
               │     └─ Parallel.ForEach
               │        └─ switch exportType:
               │           ├─ Raw → Exporter.ExportRawFile      Exporter.cs:292
               │           ├─ Dump → Exporter.ExportDumpFile    Exporter.cs:454
               │           ├─ Convert → Exporter.ExportConvertFile  Exporter.cs:467
               │           │  └─ switch item.Type:
               │           │     ├─ Texture2D → ExportTexture2D → Texture2DConverter.DecodeTexture2D
               │           │     ├─ GameObject → ExportGameObject → ModelConverter → FbxExporter
               │           │     ├─ Shader → ExportShader → ShaderConverter.Convert → ShaderSubProgram.Export
               │           │     ├─ MonoBehaviour → ExportMonoBehaviour → Studio.MonoBehaviourToTypeTree
               │           │     └─ ...
               │           └─ JSON → Exporter.ExportJSONFile   Exporter.cs:506
               ├─ exportableAssets.Clear
               └─ assetsManager.Clear                         AssetsManager.cs:907
```

---

## 调用栈 3：GameObject → FBX 导出

```
Exporter.ExportGameObject(item, exportPath, animationList)  Exporter.cs:390
└─ TryExportFolder(exportPath, item, out exportFullPath)     Exporter.cs:323
└─ Exporter.ExportGameObject(gameObject, exportPath+sep, animationList)  Exporter.cs:399
   ├─ var options = new ModelConverter.Options { ... }      ModelConverter.cs:1174
   ├─ convert = animationList != null
   │              ? new ModelConverter(gameObject, options, animationList.Select(x => (AnimationClip)x.Asset).ToArray())  ModelConverter.cs:27
   │              : new ModelConverter(gameObject, options)
   │  ├─ if gameObject.m_Animator != null: InitWithAnimator(gameObject.m_Animator)  ModelConverter.cs:106
   │  │  └─ InitWithGameObject(m_GameObject, m_Animator.m_HasTransformHierarchy)  ModelConverter.cs:115
   │  │     ├─ ConvertTransforms(m_Transform, RootFrame)     ModelConverter.cs:251
   │  │     │  └─ ConvertTransform(trans)                    ModelConverter.cs:226
   │  │     │     └─ SetFrame(frame, trans.m_LocalPosition, trans.m_LocalRotation, trans.m_LocalScale)
   │  │     │  └─ 递归 trans.m_Children
   │  │     ├─ CreateBonePathHash(m_Transform)               ModelConverter.cs:1079
   │  │     │  └─ GetTransformPathByFather(transform)         ModelConverter.cs:636
   │  │     │  └─ new SevenZip.CRC().Update(bytes, ...).GetDigest()
   │  │     └─ ConvertMeshRenderer(m_Transform)               ModelConverter.cs:154
   │  │        └─ ConvertMeshRenderer(m_GameObject.m_MeshRenderer / m_SkinnedMeshRenderer)
   │  │           ├─ GetMesh(meshR)                            ModelConverter.cs:588
   │  │           ├─ ConvertMaterial(mat)                      ModelConverter.cs:647
   │  │           │  ├─ ImportedHelpers.FindMaterial
   │  │           │  ├─ 解析 mat.m_SavedProperties.m_Colors/Floats
   │  │           │  └─ foreach texEnv in m_TexEnvs:
   │  │           │     └─ ConvertTexture2D(m_Texture2D, name)  ModelConverter.cs:770
   │  │           │        └─ m_Texture2D.ConvertToStream(options.imageFormat, true)
   │  │           ├─ 遍历 mesh.m_Vertices/Normals/UV/Tangents/Colors/BoneInfluence/Morph
   │  │           └─ morph channel name 编码 CRC + nameHash 字典
   │  └─ else: InitWithGameObject(m_GameObject)
   │  ├─ CollectAnimationClip(m_GameObject.m_Animator) [若 collectAnimations]   ModelConverter.cs:190
   │  └─ ConvertAnimations                                    ModelConverter.cs:789
   │     ├─ legacy 分支: 处理 m_CompressedRotationCurves/RotationCurves/PositionCurves/ScaleCurves/EulerCurves/FloatCurves
   │     └─ mecanim 分支:
   │        ├─ m_Clip.m_StreamedClip.ReadData
   │        ├─ m_ACLClip.Process(game, out values, out times)
   │        ├─ m_DenseClip 遍历
   │        └─ ReadCurveData per binding                        ModelConverter.cs:983
   ├─ if options.exportMaterials: 遍历 options.materials → ExportJSONFile(matItem, "Materials")
   ├─ exportPath = exportPath + FixFileName(gameObject.m_Name) + ".fbx"
   └─ Exporter.ExportFbx(convert, exportPath)                  Exporter.cs:435
      ├─ var exportOptions = new Fbx.ExportOptions { ... }
      └─ ModelExporter.ExportFbx(exportPath, convert, exportOptions)
         └─ FbxExporter.WriteFile → FbxDll (P/Invoke) → AssetStudio.FBXNative.dll
```

---

## 调用栈 4：Shader 反编译导出

```
Exporter.ExportShader(item, exportPath)                       Exporter.cs:66
└─ TryExportFile(exportPath, item, ".shader", out exportFullPath)  Exporter.cs:300
└─ m_Shader.Convert()                                         ShaderConverter.cs:18
   ├─ if m_SubProgramBlob != null (5.3-5.4):
   │  ├─ LZ4.Instance.Decompress(m_SubProgramBlob, decompressedBytes)
   │  ├─ new ShaderProgram(blobReader, shader)              ShaderConverter.cs:915
   │  │  └─ for i in subProgramsCapacity: new ShaderSubProgramEntry(reader, version)  ShaderConverter.cs:897
   │  ├─ shaderProgram.Read(blobReader, 0)                    ShaderConverter.cs:930
   │  │  └─ new ShaderSubProgram(reader, hasUpdatedGpuProgram)  ShaderConverter.cs:963
   │  │     ├─ m_Version / m_ProgramType / m_Keywords / m_LocalKeywords
   │  │     └─ m_ProgramCode = reader.ReadUInt8Array
   │  └─ return header + shaderProgram.Export(Encoding.UTF8.GetString(shader.m_Script))  ShaderConverter.cs:943
   │     └─ Regex.Replace(shader, "GpuProgramIndex (.+)", evaluator) 替换为 m_SubPrograms[index].Export()
   ├─ else if compressedBlob != null (5.5+):
   │  ├─ ConvertSerializedShader(shader)                       ShaderConverter.cs:44
   │  │  ├─ for platform i in shader.platforms:
   │  │  │  ├─ [解压 compressedBlob 切片 → decompressedBytes]
   │  │  │  │  └─ GI 子组: Buffer.BlockCopy
   │  │  │  │  └─ 其他: LZ4.Instance.Decompress
   │  │  │  └─ new ShaderProgram(blobReader, shader)
   │  │  │  └─ shaderPrograms[i].Read(blobReader, j)
   │  │  └─ ConvertSerializedShader(m_ParsedForm, platforms, programs)  ShaderConverter.cs:82
   │  │     ├─ "Shader \"{name}\" {"
   │  │     ├─ ConvertSerializedProperties(m_PropInfo)        ShaderConverter.cs:674
   │  │     │  └─ foreach m_Prop: ConvertSerializedProperty(m_Prop)  ShaderConverter.cs:686
   │  │     │     └─ [Type/Attribute/Range/Vector/Color/Texture]
   │  │     ├─ foreach m_SubShader: ConvertSerializedSubShader  ShaderConverter.cs:108
   │  │     │  ├─ ConvertSerializedTagMap(m_Tags, 1)
   │  │     │  └─ foreach m_Passe: ConvertSerializedPass       ShaderConverter.cs:127
   │  │     │     ├─ ConvertSerializedShaderState(m_State)   ShaderConverter.cs:243
   │  │     │     │  ├─ ConvertSerializedShaderRTBlendState
   │  │     │     │  ├─ ConvertSerializedStencilOp
   │  │     │     │  └─ [ZTest/ZWrite/Cull/Offset/Fog]
   │  │     │     └─ foreach prog (vp/fp/gp/hp/dp/rtp):
   │  │     │        └─ ConvertSerializedSubPrograms         ShaderConverter.cs:208
   │  │     │           ├─ GroupBy m_BlobIndex + m_GpuProgramType
   │  │     │           └─ ShaderSubProgram.Export           ShaderConverter.cs:1006
   │  │     │              ├─ switch m_ProgramType:
   │  │     │              │  ├─ GLLegacy/GLES*/GLCore*: UTF-8 直接
   │  │     │              │  ├─ DX9*: Vortice.Compiler.Disassemble
   │  │     │              │  ├─ DX11*: HLSLDecompiler.DecompileShader → HLSLDecompiler.dll
   │  │     │              │  ├─ MetalVS/FS: 解析 0xf00dcafe + UTF-8
   │  │     │              │  ├─ SPIRV: SpirVShaderConverter.Convert → Smolv
   │  │     │              │  └─ 其他: 占位
   │  │     ├─ "Fallback \"{fallback}\""
   │  │     └─ "CustomEditor \"{customEditor}\""
   └─ else:
      └─ Encoding.UTF8.GetString(shader.m_Script)
└─ File.WriteAllText(exportFullPath, str)
```

---

## 调用栈 5：MonoBehaviour 导出（含 Dummy DLL）

```
Exporter.ExportMonoBehaviour(item, exportPath)                 Exporter.cs:93
└─ TryExportFile(exportPath, item, ".json", out exportFullPath)  Exporter.cs:300
└─ m_MonoBehaviour.ToType()                                   MonoBehaviour.cs (ToType)
   ├─ 若直接解析成功 → return type
   └─ 否则:
      └─ Studio.MonoBehaviourToTypeTree(m_MonoBehaviour)        Studio.cs:918 (GUI) / Studio.cs:503 (CLI)
         ├─ 若 !assemblyLoader.Loaded: GUI 弹 OpenFolderDialog, 用户选目录 → assemblyLoader.Load(folder)
         ├─ else (CLI): 直接用 Program.Run 已加载的 assemblyLoader
         └─ m_MonoBehaviour.ConvertToTypeTree(assemblyLoader)   MonoBehaviour.cs
            └─ TypeDefinitionConverter.ConvertToTypeTree       TypeDefinitionConverter.cs
└─ m_MonoBehaviour.ToType(type)
└─ JsonConvert.SerializeObject(type, Formatting.Indented)
└─ File.WriteAllText(exportFullPath, str)
```

---

## 调用栈 6：Build CABMap

```
MainForm.buildMapToolStripMenuItem_Click                       MainForm.cs:2332
└─ AssetsHelper.SetUnityVersion(version)                       AssetsHelper.cs:36
└─ Task.Run(AssetsHelper.BuildCABMap(files, name, openFolderDialog.Folder, Studio.Game))  AssetsHelper.cs:142
   ├─ CABMap.Clear
   ├─ Progress.Reset
   ├─ BaseFolder = openFolderDialog.Folder
   ├─ assetsManager.Game = Studio.Game
   └─ foreach file in LoadFiles(files):                        AssetsHelper.cs:167 [yield]
      ├─ ImportHelper.MergeSplitAssets(path)                   ImportHelper.cs:19
      ├─ ImportHelper.ProcessingSplitFiles(files)              ImportHelper.cs:49
      ├─ assetsManager.LoadFiles(file)                          AssetsManager.cs:48
      ├─ yield file (返回 file 给调用方)
      ├─ if assetsManager.assetsFileList.Count > 0: BuildCABMap(file, ref collision)  AssetsHelper.cs:196
      │  ├─ foreach assetsFile in assetsManager.assetsFileList:
      │  │  ├─ var entry = new Entry { Path = relativePath, Offset = assetsFile.offset, Dependencies = assetsFile.m_Externals.Select(x => x.fileName).ToList() }
      │  │  └─ CABMap.Add(assetsFile.fileName, entry)
      │  └─ 累加 collision
      └─ assetsManager.Clear
   └─ DumpCABMap(mapName)                                      AssetsHelper.cs:222
      ├─ CABMap.OrderBy(...)
      └─ File.OpenWrite(Maps/<mapName>.bin) + BinaryWriter
```

---

## 调用栈 7：Build AssetMap（CLI + GUI）

```
MainForm.buildAssetMapToolStripMenuItem_Click                  MainForm.cs:2575
└─ AssetsHelper.SetUnityVersion(version)                       AssetsHelper.cs:36
└─ Task.Run(AssetsHelper.BuildAssetMap(files, name, Studio.Game, saveFolderDialog.Folder, exportListType))  AssetsHelper.cs:316
   ├─ assetsManager.Game = Studio.Game
   └─ foreach file in LoadFiles(files):
      └─ BuildAssetMap(file, assets, ...)                       AssetsHelper.cs:340
         └─ foreach assetsFile in assetsManager.assetsFileList:
            └─ foreach objInfo in assetsFile.m_Objects:
               ├─ new ObjectReader(...) + switch type → new AssetEntry { ... }
               │  ├─ case AssetBundle: 收集 preloadTable → containers
               │  ├─ case IndexObject: 收集 mihoyoBinDataNames
               │  ├─ case Texture2D/Font/Material/...: 读 name
               └─ assetsFile.AddObject(obj)

   └─ UpdateContainers(assets, game) [若 IsGISubGroup]         AssetsHelper.cs:594
      └─ ResourceIndex.GetContainer(id, last)

   └─ ExportAssetsMap(assets, game, name, savePath, exportListType)  AssetsHelper.cs:623
      ├─ if XML: XmlWriter.Create + foreach asset: writer.WriteStartElement("Asset") ...
      ├─ if JSON: JsonSerializer.Serialize(file, toExportAssets)
      └─ if MessagePack: MessagePackSerializer.Serialize(file, assetMap, ...)
```

---

## 调用栈 8：Texture 导出

```
Exporter.ExportTexture2D(item, exportPath, imageFormat)      Exporter.cs:12 (CLI) / GUI/Exporter.cs:12
├─ if convertTexture:
│  ├─ TryExportFile(exportPath, item, ".png", out path)      Exporter.cs:300
│  ├─ image = m_Texture2D.ConvertToImage(true)               Texture2DExtensions.cs
│  │  └─ var converter = new Texture2DConverter(m_Texture2D)  Texture2DConverter.cs:18
│  │  └─ var bytes = new byte[m_Width * m_Height * 4]
│  │  └─ converter.DecodeTexture2D(bytes)                     Texture2DConverter.cs:29
│  │     └─ switch m_TextureFormat:
│  │        ├─ DXT1 → TextureDecoder.DecodeDXT1 (via SwapBytesForXbox)
│  │        ├─ DXT5 → TextureDecoder.DecodeDXT5
│  │        ├─ ETC2_* → TextureDecoder.DecodeETC2/A1/A8
│  │        ├─ ASTC_* → TextureDecoder.DecodeASTC
│  │        ├─ PVRTC_* → TextureDecoder.DecodePVRTC
│  │        ├─ RGBA32 → DecodeRGBA32 (直接)
│  │        └─ ...
│  ├─ image.WriteToStream(file, ImageFormat)                 ImageExtensions.cs
│  └─ return true
└─ else:
   ├─ TryExportFile(..., ".tex", out path)
   └─ File.WriteAllBytes(path, m_Texture2D.image_data.GetData())
```

---

## 调用栈 9：Extract Bundle

```
Studio.ExtractFolder(path, savePath)                          Studio.cs:35 (CLI) / GUI/Studio.cs:34
└─ foreach file in Directory.GetFiles(path, "*.*", SearchOption.AllDirectories):
   └─ Studio.ExtractFile(file, savePath)                      Studio.cs:60 (CLI) / GUI/Studio.cs:63
      ├─ new FileReader(fileName)
      ├─ reader = reader.PreProcessing(Game)                  FileReader.cs:163
      └─ switch reader.FileType:
         ├─ BundleFile → Studio.ExtractBundleFile             Studio.cs:78 / 81
         │  ├─ new BundleFile(reader, Game) → 解压完成，fileList 已有 stream
         │  └─ Studio.ExtractStreamFile(extractPath, bundleFile.fileList)  Studio.cs:178 / 181
         │     └─ foreach file in fileList:
         │        ├─ if !File.Exists(filePath):
         │        │  └─ file.stream.CopyTo(FileStream)
         │        └─ file.stream.Dispose
         ├─ WebFile → Studio.ExtractWebDataFile               Studio.cs:98 / 101
         ├─ BlkFile → Studio.ExtractBlkFile                   Studio.cs:111 / 114
         │  ├─ BlkUtils.Decrypt(reader, (Blk)Game) → XORStream   BlkUtils.cs:14
         │  └─ foreach offset: new FileReader(dummyPath, stream) → 回到 switch (BundleFile/MhyFile)
         └─ BlockFile → Studio.ExtractBlockFile               Studio.cs:142 / 145
            └─ new OffsetStream + foreach offset
```

---

## 调用栈 10：MonoBehaviour 反序列化为 JSON（GUI 预览）

```
MainForm.selectAsset                                            MainForm.cs:862
└─ if enablePreview.Checked: PreviewAsset(assetItem)          MainForm.cs:923
   └─ case MonoBehaviour: MainForm.PreviewMonoBehaviour       MainForm.cs:1192
      ├─ obj = m_MonoBehaviour.ToType()                       MonoBehaviour.cs
      │  └─ 若 obj != null: 跳到 PreviewText
      │  └─ else:
      │     └─ type = MonoBehaviourToTypeTree(m_MonoBehaviour)  GUI/Studio.cs:918
      │        ├─ if !assemblyLoader.Loaded:
      │        │  ├─ OpenFolderDialog.ShowDialog()
      │        │  └─ assemblyLoader.Load(folder)
      │        └─ m_MonoBehaviour.ConvertToTypeTree(assemblyLoader)  MonoBehaviour.cs
      │           └─ TypeDefinitionConverter.ConvertToTypeTree
      ├─ obj = m_MonoBehaviour.ToType(type)
      ├─ str = JsonConvert.SerializeObject(obj, Formatting.Indented)
      └─ PreviewText(str)
         └─ textPreviewBox.Text = str
         └─ textPreviewBox.Visible = true
```

---

## 调用栈 11：FMOD 音频预览

```
MainForm.PreviewAudioClip(assetItem, m_AudioClip)              MainForm.cs:1047
├─ assetItem.InfoText = "Compression format: ..."
│  └─ switch m_AudioClip.m_CompressionFormat (or m_Type for v<5)
├─ m_AudioData = m_AudioClip.m_AudioData.GetData()
├─ exinfo = new FMOD.CREATESOUNDEXINFO()
├─ result = system.createSound(m_AudioData, FMOD.MODE.OPENMEMORY | loopMode, ref exinfo, out sound)
├─ sound.getNumSubSounds(out numsubsounds)
├─ sound.getLength(out FMODlenms, FMOD.TIMEUNIT.MS)
├─ result = system.playSound(sound, null, true, out channel)
└─ FMODpanel.Visible = true

[随后 timer_Tick 持续调用]
MainForm.timer_Tick                                            MainForm.cs:2850
├─ channel.getPosition(out ms, FMOD.TIMEUNIT.MS)
├─ channel.isPlaying(out playing)
├─ channel.getPaused(out paused)
├─ 更新 FMODtimerLabel.Text / FMODprogressBar.Value / FMODstatusLabel.Text
└─ system.update()
```

---

## 调用栈 12：OpenGL Mesh 预览

```
MainForm.PreviewMesh(m_Mesh)                                   MainForm.cs:1254
├─ vertexData = new Vector3[m_Mesh.m_VertexCount]
├─ 遍历 m_Mesh.m_Vertices 计算 bounding box
├─ modelMatrixData = Matrix4.CreateTranslation(-offset) * Matrix4.CreateScale(2f / d)
├─ indiceData = new int[m_Mesh.m_Indices.Count]
├─ 计算 normalData（来自 mesh.m_Normals 或重新计算）
├─ 计算 colorData（来自 mesh.m_Colors）
├─ glControl.Visible = true
└─ CreateVAO()                                                 MainForm.cs:2977
   ├─ GL.GenVertexArrays(1, out vao)
   ├─ CreateVBO(out vboPositions, vertexData, attributeVertexPosition)  MainForm.cs:2937
   ├─ CreateVBO(out vboNormals, normalData/normal2Data, attributeNormalDirection)
   ├─ CreateVBO(out vboColors, colorData, attributeVertexColor)
   ├─ CreateVBO(out vboModelMatrix, modelMatrixData, uniformModelMatrix)
   ├─ CreateVBO(out vboViewMatrix, viewMatrixData, uniformViewMatrix)
   ├─ CreateVBO(out vboProjMatrix, projMatrixData, uniformProjMatrix)
   └─ CreateEBO(out eboElements, indiceData)

[随后 GL 重绘]
MainForm.glControl_Paint                                       MainForm.cs:3023
├─ GL.Clear(...)
├─ GL.UseProgram(shadeMode == 0 ? pgmID : pgmColorID)
├─ GL.UniformMatrix4(uniformModelMatrix, ...)
├─ GL.PolygonMode(MaterialFace.FrontAndBack, PolygonMode.Fill)
└─ GL.DrawElements(PrimitiveType.Triangles, indiceData.Length, ...)
```

---

## 调用栈 13：加载 AssetMap (CLI 模式)

```
AssetStudio.CLI.Program.Run(Options o)                          Program.cs:16
└─ if o.MapOp == Load:
   └─ if o.MapOp == AssetMap:
      └─ files = AssetsHelper.ParseAssetMap(o.MapName, o.MapType, classTypeFilter, o.NameFilter, o.ContainerFilter)  AssetsHelper.cs:504
         ├─ switch o.MapType:
         │  ├─ MessagePack: MessagePackSerializer.Deserialize<AssetMap>(stream)
         │  ├─ XML: XmlReader.Create + foreach "Asset" element
         │  └─ JSON: JsonSerializer.Deserialize<List<AssetEntry>>(reader)
         └─ return matched sources[]
```

---

## 调用栈 14：Unity 版本检测（Folder 路径）

```
AssetsManager.LoadFiles(files)                                 AssetsManager.cs:48
└─ DetectUnityVersionFromFolder(path)                          AssetsManager.cs:176
   ├─ var globalGameManagersFiles = Directory.GetFiles(path, "globalgamemanagers", SearchOption.AllDirectories)
   ├─ if found:
   │  └─ detectedFolderVersion = TryExtractVersionFromFile(globalGameManagersFiles[0])   AssetsManager.cs:243
   │     └─ new FileReader → new SerializedFile(reader, this)
   │        └─ if !tempFile.IsVersionStripped: return tempFile.unityVersion
   ├─ var dataUnity3dFiles = Directory.GetFiles(path, "data.unity3d", SearchOption.AllDirectories)
   ├─ if found:
   │  └─ detectedFolderVersion = TryExtractVersionFromBundle(dataUnity3dFiles[0])     AssetsManager.cs:266
   │     └─ new FileReader → new BundleFile(reader, Game)
   │        └─ if !string.IsNullOrEmpty(bundleFile.m_Header.unityRevision): return ...
   ├─ foreach bundleFile in *.unity3d (TopDirectoryOnly, Take 3):
   │  └─ TryExtractVersionFromBundle(bundleFile)
   └─ foreach bundleFile in *.bundle (AllDirectories, Take 5):
      └─ TryExtractVersionFromBundle(bundleFile)

[后续被 CheckStrippedVersion 使用]
AssetsManager.CheckStrippedVersion(assetsFile)                   AssetsManager.cs:838
├─ if assetsFile.IsVersionStripped && string.IsNullOrEmpty(SpecifyUnityVersion):
│  └─ lock versionDetectionLock: version = detectedFolderVersion
│  └─ if !string.IsNullOrEmpty(version): assetsFile.SetVersion(version); return
│  └─ else if !string.IsNullOrEmpty(DefaultVersion): assetsFile.SetVersion(DefaultVersion); return
│  └─ else if OnVersionPrompt != null: 弹窗 (GUI) / CLI 直接抛异常
└─ else: if !string.IsNullOrEmpty(SpecifyUnityVersion): assetsFile.SetVersion(SpecifyUnityVersion)
```