# 04 · UABEA 数据结构与数据流

## 4.1 核心数据结构

### 4.1.1 内存模型

```mermaid
classDiagram
  class AssetsManager {
    +BundleFiles Dictionary
    +AssetsFiles Dictionary
    +ClassDatabase
    +MonoTempGenerator
    +LoadBundleFile(path) BundleFileInstance
    +LoadAssetsFile(path) AssetsFileInstance
    +GetTemplateBaseField() AssetTypeTemplateField
  }

  class BundleFileInstance {
    +AssetBundleFile file
    +string path
    +string name
    +AssetsFileReader reader
  }

  class AssetsFileInstance {
    +AssetsFile file
    +string path
    +string name
    +BundleFileInstance parentBundle
    +AssetsFileReader reader
    +GetDependency(am, idx) AssetsFileInstance
  }

  class AssetsFile {
    +AssetsFileMetadata Metadata
    +List~AssetFileInfo~ AssetInfos
    +GenerateQuickLookup()
    +GetAssetsOfType(classId) List~AssetFileInfo~
  }

  class AssetsFileMetadata {
    +string UnityVersion
    +BuildTarget TargetPlatform
    +bool TypeTreeEnabled
    +Externals List
    +RefTypes
  }

  class AssetFileInfo {
    +long PathId
    +ushort TypeId
    +ushort ScriptIndex
    +long AbsoluteByteStart
    +uint ByteSize
  }

  class AssetTypeTemplateField {
    +string Type
    +string Name
    +bool IsAligned
    +bool IsArray
    +AssetValueType ValueType
    +List~AssetTypeTemplateField~ Children
    +MakeValue() AssetTypeValueField
  }

  class AssetTypeValueField {
    +AssetTypeTemplateField TemplateField
    +AssetValueType ValueType
    +AsBool / AsInt / AsString / ...
    +List~AssetTypeValueField~ Children
    +WriteToByteArray() byte[]
  }

  AssetsManager "1" *-- "*" BundleFileInstance
  AssetsManager "1" *-- "*" AssetsFileInstance
  BundleFileInstance "1" o-- "*" AssetsFileInstance : via reader.BaseStream
  AssetsFileInstance "1" *-- "1" AssetsFile
  AssetsFile "1" *-- "1" AssetsFileMetadata
  AssetsFile "1" *-- "*" AssetFileInfo
  AssetFileInfo "1" *-- "1" AssetTypeTemplateField
  AssetTypeTemplateField "1" *-- "*" AssetTypeValueField
  AssetTypeValueField ..> AssetTypeTemplateField
```

### 4.1.2 UABEA 自定义数据结构

```mermaid
classDiagram
  class AssetWorkspace {
    +AssetsManager am
    +bool fromBundle
    +List~AssetsFileInstance~ LoadedFiles
    +Dictionary~AssetID,AssetContainer~ LoadedAssets
    +Dictionary~AssetID,AssetsReplacer~ NewAssets
    +Dictionary~AssetID,Stream~ NewAssetDatas
    +HashSet~AssetID~ RemovedAssets
    +Dictionary~AssetsFileInstance,AssetsFileChangeTypes~ OtherAssetChanges
    +event ItemUpdated
    +event MonoTemplateLoadFailed
    +AddReplacer(file, replacer, stream)
    +RemoveReplacer(file, replacer)
    +LoadAssetsFile(file, loadDependencies)
    +GetAssetContainer(file, fileId, pathId, onlyInfo) AssetContainer?
    +GetBaseField(cont) AssetTypeValueField?
    +SetMonoTempGenerators(fileDir)
  }

  class AssetContainer {
    +long PathId
    +int ClassId
    +ushort MonoId
    +uint Size
    +string Container
    +AssetsFileInstance FileInstance
    +AssetTypeValueField? BaseValueField
    +long FilePosition
    +AssetsFileReader FileReader
  }

  class BundleWorkspace {
    +BundleFileInstance? BundleInst
    +AssetsManager am
    +ObservableCollection~BundleWorkspaceItem~ Files
    +Dictionary~string,BundleWorkspaceItem~ FileLookup
    +HashSet~string~ RemovedFiles
    +Reset(bundleInst)
    +AddOrReplaceFile(stream, name, isSerialized, prevName?)
    +RenameFile(origName, newName)
    +GetReplacers() List~BundleReplacer~
  }

  class BundleWorkspaceItem {
    +string Name
    +string OriginalName
    +bool IsNew
    +bool IsSerialized
    +bool IsModified
    +bool IsRemoved
    +Stream Stream
    +IBrush Color
  }

  class UnityContainer {
    +List~AssetPPtr~ PreloadTable
    +Dictionary~UnityContainerAssetInfo,string~ AssetMap
    +FromAssetBundle(am, file, bf)
    +FromResourceManager(am, file, bf)
    +GetContainerPath(file, pathId)
    +TryGetBundleContainerBaseField()
    +TryGetRsrcManContainerBaseField()
  }

  class InstallerPackageFile {
    +string magic
    +bool includesCldb
    +string modName
    +string modCreators
    +string modDescription
    +ClassDatabaseFile addedTypes
    +List~InstallerPackageAssetsDesc~ affectedFiles
    +Read(reader) bool
    +Write(writer)
  }

  class InstallerPackageAssetsDesc {
    +bool isBundle
    +string path
    +List~object~ replacers
  }

  AssetWorkspace "1" *-- "*" AssetContainer
  BundleWorkspace "1" *-- "*" BundleWorkspaceItem
```

## 4.2 数据流

### 4.2.1 打开 .bundle

```mermaid
flowchart LR
  F[文件路径] --> FTD[FileTypeDetector.DetectFileType]
  FTD -->|BundleFile| LB[BundleWorkspace.Reset]
  LB --> PI[PopulateFilesList<br/>遍历 DirectoryInfos]
  PI --> AW[AssetWorkspace.LoadAssetsFileFromBundle]
  AW --> SR[am.LoadAssetsFile]
  SR --> DB[Manager.ClassDatabase<br/>classdata.tpk]
  SR --> CGI[LoadClassDatabaseFromPackage<br/>若 tpk 未加载]
  AW --> LUA[GenerateQuickLookup]
  AW --> IW[open InfoWindow 显示 tree]
```

### 4.2.2 编辑 asset（树视图中双击）

```mermaid
flowchart TD
  UI[AssetDataTreeView 双击] --> IDX[InfoWindow.ShowEditAssetWindow]
  IDX --> DLG[EditDataWindow]
  DLG --> BF[AssetImportExport.DumpTextAsset<br/>→ 写出 .txt]
  DLG --> ED[用户保存修改后的 .txt]
  ED --> IMP[AssetImportExport.ImportTextAsset<br/>→ AssetTypeValueField]
  IMP --> BWA[AssetTypeValueField.WriteToByteArray]
  BWA --> REPL[AssetsReplacerFromMemory]
  REPL --> ADD[AssetWorkspace.AddReplacer]
  ADD --> UPD[ItemUpdated 事件]
  UPD --> UI[UI 重新渲染]
```

### 4.2.3 保存 .bundle

```mermaid
flowchart TD
  ACT[MainWindow.Save 按钮] --> BW[BundleWorkspace.GetReplacers]
  BW --> REP_B[List BundleReplacer]
  ACT --> AW[AssetWorkspace.GetChangedFiles]
  AW --> REP_A[每个 .assets 的 AssetsReplacer]
  ACT --> W[BundleFile.Write]
  W -->|写入临时 ~.bundle| TMP[tempFile]
  TMP --> MV[File.Move 覆盖原文件]
  MV --> BAK[原文件 → .bak0001]
```

### 4.2.4 Texture 导出数据流

```mermaid
sequenceDiagram
    participant UI as MainWindow (PluginWindow)
    participant TP as TexturePlugin.ExportTextureOption
    participant TH as TextureHelper
    participant W as Workspace
    participant TF as TextureFile (ATN)
    participant TIE as TextureImportExport
    participant TED as TextureEncoderDecoder
    participant PI as PInvoke (textoolwrap)

    UI->>TP: ExecutePlugin
    TP->>W: GetByteArrayTexture(workspace, cont)
    W-->>TP: AssetTypeValueField (含 m_ImageData)
    TP->>TF: TextureFile.ReadTextureFile(bf)
    TF-->>TP: TextureFile (m_Width, m_Height, m_TextureFormat, m_StreamData)
    alt m_StreamData.path 非空 (bundle 内 resS)
        TP->>TH: GetResSTexture
        TH->>TF: 把 pictureData 拷出来
    else m_StreamData.size != 0 (外部文件)
        TP->>TH: GetRawTextureBytes
        TH->>TH: File.OpenRead(fixedStreamPath)
    end
    TP->>TIE: Export(data, path, w, h, fmt, platform, platformBlob)
    alt platform == 38 (Switch) && platformBlob != null
        TIE->>TED: EncodeSwitch
        TED->>PI: EncodeByCrunchUnity / EncodeByPVRTexLib
    else 通用
        TIE->>TED: Decode
        TED->>PI: DecodeByPVRTexLib / DecodeByCrunchUnity / DecodeByAssetRipperTex
    end
    TIE->>TIE: SaveImageAtPath (PNG/TGA)
```

### 4.2.5 EMIP 应用数据流

```mermaid
flowchart LR
  EMIP[.emip 文件] --> IPF[InstallerPackageFile.Read]
  IPF --> AF[affectedFiles]
  AF --> DEC{isBundle?}
  DEC -->|是| DBU[DecompressBundle<br/>→ 内存或 .decomp]
  DBU --> REPL1[遍历 BundleReplacer]
  REPL1 --> RFA[若是 BundleReplacerFromAssets:<br/>Init(reader, pos, size)]
  RFA --> W1[bun.Write → .mod]
  DEC -->|否| AFS[assets.Read]
  AFS --> REPL2[遍历 AssetsReplacer]
  REPL2 --> W2[assets.Write → .mod]
  W1 --> M1[File.Move → 原文件<br/>原文件 → .bakNNNN]
  W2 --> M2[File.Move → 原文件<br/>原文件 → .bakNNNN]
```