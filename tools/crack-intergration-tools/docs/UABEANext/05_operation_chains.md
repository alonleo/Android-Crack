# 05 · UABEANext 主要操作链

---

## 5.1 启动 → Dock UI → 加载 plugins

```mermaid
sequenceDiagram
    participant OS as OS
    participant P as Program (UABEANext4.Desktop)
    participant A as App.axaml.cs
    participant DI as DI Container
    participant MVM as MainViewModel
    participant WS as Workspace
    participant PL as PluginLoader
    participant MVF as MainDockFactory

    OS->>P: dotnet UABEANext4.Desktop.exe
    P->>A: BuildAvaloniaApp().StartWithClassicDesktopLifetime
    A->>DI: ServiceCollection.AddSingleton(...)
    A->>MVM: Ioc.Default.GetRequiredService<MainViewModel>()
    MVM->>WS: Workspace()
    WS->>WS: Manager.LoadClassPackage("classdata.tpk")
    WS->>PL: Plugins.LoadPluginsInDirectory("plugins")
    loop each dll
        PL->>PL: new PluginLoadContext + LoadFromAssemblyPath
        PL->>PL: collect IUavPluginOption / IUavPluginPreviewer
    end
    MVM->>MVF: BuildDock()
    MVF-->>MVM: IRootDock
    MVM->>A: DataContext = MainViewModel
    A-->>OS: 显示主窗
```

## 5.2 拖拽 / 菜单打开 .bundle 文件

```mermaid
sequenceDiagram
    participant U as User
    participant MVM as MainViewModel
    participant SP as IStorageProvider
    participant WS as Workspace
    participant FTD as FileTypeDetector
    participant AM as AssetsManager
    participant PL as PluginLoader

    U->>MVM: 拖拽文件 / 菜单 Open
    MVM->>SP: OpenFilePickerAsync
    SP-->>MVM: IReadOnlyList<IStorageFile>
    MVM->>WS: LoadAnyFile(stream, loadOrder)
    WS->>FTD: DetectFileType(reader, 0)
    FTD-->>WS: DetectedFileType
    alt BundleFile
        WS->>WS: LoadBundle
        WS->>AM: LoadBundleFile
        WS->>WS: lock(_workingKeys) duplicate check
        WS->>WS: TryLoadClassDatabase
        WS->>WS: new WorkspaceItem
        WS->>WS: AddRootItemThreadSafe
    else AssetsFile
        WS->>WS: LoadAssets → FixupAssetsFile → WorkspaceItem
    end
    WS-->>MVM: WorkspaceItem
    MVM->>MVM: WeakReferenceMessenger.Send(FileLoadedMessage)
```

## 5.3 选中文件 → 显示文件内 asset 列表

```mermaid
flowchart TD
  S[用户选中 WorkspaceItem] --> MV[MainViewModel.SelectedItems.Add]
  MV --> WSE[WorkspaceExplorerToolViewModel.SelectedItem]
  WSE --> MSG[Send SelectedWorkspaceItemChangedMessage]
  MSG --> ASPV[AssetDocumentViewModel 接收到]
  ASPV --> ASPV2[加载 AssetList from file.file.AssetInfos]
  ASPV2 --> UI[Document Tab 显示 DataGrid]
```

## 5.4 选中 asset → Inspector 显示字段 → 修改 → 保存

```mermaid
sequenceDiagram
    participant U as User
    participant Asp as AssetDocumentViewModel
    participant Insp as InspectorToolViewModel
    participant WS as Workspace
    participant Atn as AssetsManager

    U->>Asp: Click asset in DataGrid
    Asp->>Asp: SelectedAsset = asset
    Asp->>WS: GetBaseField(asset)
    WS->>Atn: GetBaseField(fileInst, info)
    Atn-->>WS: AssetTypeValueField
    WS-->>Asp: BaseField
    Asp->>Asp: 通知 Inspector 更新
    Insp->>Insp: BuildTree(BaseField)
    Insp-->>U: 显示 TreeView
    U->>Insp: 修改字段值
    Insp->>Asp: BaseField updated
    Asp->>Asp: BaseField.WriteToByteArray()
    Asp->>WS: Dirty(this)
    WS->>WS: UnsavedItems.Add(item)
    U->>MVM: Click Save
    MVM->>WS: Save(item)
    WS->>WS: WriteAssetsFile / WriteBundleFile
    WS-->>MVM: saved=true
```

## 5.5 Bundle 解压 / 加载

```mermaid
flowchart TD
  B[bundle file path] --> LF[Workspace.LoadBundle stream]
  LF --> MLB[Manager.LoadBundleFile stream]
  MLB --> AFI[BundleFileInstance]
  AFI --> LF2[lock _workingKeys]
  LF2 --> CHK{每 entry 已存在?}
  CHK -->|是| DWF[抛 DuplicateWorkspaceFileException]
  CHK -->|否| ADD[加入 _workingKeys]
  ADD --> TLCD[TryLoadClassDatabase bun.file]
  TLCD --> TPK[Manager.LoadClassDatabaseFromPackage version]
  TLCD --> NEW[new WorkspaceItem bunInst, loadOrder]
  NEW --> ARI[AddRootItemThreadSafe]
  ARI --> FSC[FileSyncContext?.Post]
  FSC --> RI[RootItems.Insert BinarySearch by LoadIndex]
  ARI --> IL[ItemLookup name → item]
  ARI --> FIN[finally: _workingKeys.Remove]
```

## 5.6 插件调用（Texture 导出）

```mermaid
sequenceDiagram
    participant U as User
    participant Insp as InspectorToolViewModel
    participant MVM as MainViewModel
    participant PL as PluginLoader
    participant TP as TexturePlugin.ExportTextureOption
    participant WS as Workspace
    participant Fun as UavPluginFunctions
    participant TL as TextureLoader
    participant TE as TextureEncoderDecoder

    U->>Insp: Right-click asset → Plugins → Export
    Insp->>MVM: ContextMenu
    MVM->>PL: GetOptionsThatSupport(ws, assets, Export)
    PL-->>MVM: List<PluginOptionModePair>
    MVM->>TP: Execute(ws, funcs, Export, selection)
    TP->>Fun: ShowSaveFileDialog(options)
    Fun-->>U: 文件选择对话框
    U-->>Fun: 选定文件
    TP->>WS: GetBaseField(asset)
    WS-->>TP: AssetTypeValueField
    TP->>TL: LoadTexture(...)
    TL->>TL: AssetRipper.TextureDecoder.Decode
    TL-->>TP: Bitmap
    TP->>TP: SaveImageAtPath
```

## 5.7 3D Mesh 预览

```mermaid
sequenceDiagram
    participant U as User
    participant Insp as Inspector
    participant Doc as AssetDocumentViewModel
    participant WS as Workspace
    participant MPM as MeshPreviewer (plugin)
    participant PP as PluginPreviewer 进程
    participant Silk as Silk.NET.OpenGL

    U->>Insp: Select GameObject
    Insp->>Doc: GetBaseField
    Doc->>WS: GetBaseField(gameObject)
    Doc->>Doc: 遍历 m_Components Array 找 MeshFilter
    Doc->>WS: GetBaseField(meshFilter)
    Doc->>Doc: 解析 Mesh.m_Mesh (Mesh asset)
    Doc->>Doc: new MeshObj { Vertices, Indices, Channels }
    Doc->>MPM: SetPreviewMesh(meshObj)
    MPM->>PP: IPC (named pipe / stdin?)
    PP->>Silk: OpenGL 渲染
    Silk-->>U: 显示 3D
```

## 5.8 搜索资产

```mermaid
sequenceDiagram
    participant U as User
    participant DSL as AssetDataSearchViewModel
    participant SL as SearchLogic
    participant WS as Workspace
    participant FILE as AssetsFileInstance
    participant IT as InspectorToolViewModel

    U->>DSL: 输入查询字符串 + 选项
    DSL->>SL: Search(ws, query, options, cts)
    SL->>WS: GetAllFileInstances
    WS-->>SL: List<AssetsFileInstance>
    SL->>SL: Parallel.ForEach (max = ProcessorCount)
    par 每个文件
        SL->>FILE: BuildAssetNameIndex
        FILE-->>SL: List<SearchResultItem>
    end
    SL-->>DSL: List<SearchResultItem>
    DSL-->>U: 显示结果列表
    U->>IT: Select result
    IT->>WS: SelectAsset(file, pathId)
```

## 5.9 类型树导入导出（与 UABEA 同）

```mermaid
flowchart LR
  A[User click Export .txt] --> B[new AssetExport stream]
  B --> C[DumpTextAsset baseField]
  C --> D[RecurseTextDump 0]
  D --> E[写入 sw]

  F[User click Import .txt] --> G[new AssetImport stream, refMan]
  G --> H[ImportTextAsset]
  H --> I[ImportTextAssetLoop writer]
  I --> J[写入 AssetsFileWriter]
  J --> K[Workspace.Dirty item]
```

涉及：`UABEANext4/Logic/ImportExport/AssetExport.cs` (`AssetExport.cs:36, 42`)、`AssetImport.cs` (`AssetImport.cs:30, 51`)

## 5.10 配置持久化

```mermaid
flowchart TD
  S[User 修改 Theme / ListingNameLength] --> VM[SettingsViewModel.SetProperty]
  VM --> CFG[ConfigurationManager.Settings.Set]
  CFG --> SET[ConfigurationItem setter]
  SET --> SV[SaveConfig → JSON]
  SV --> FS[File.WriteAllText config.json]

  R[启动] --> LD[LoadConfig]
  LD --> JP[JsonConvert.DeserializeObject]
  JP --> DM[ConfigurationManager.Settings]
```

## 5.11 关闭文件

```mermaid
sequenceDiagram
    participant U as User
    participant MVM as MainViewModel
    participant WS as Workspace
    participant AM as AssetsManager
    participant File as AssetsFileInstance

    U->>MVM: Close File
    MVM->>WS: Close(item)
    WS->>WS: item.Loaded && RootItems.Contains
    alt ObjectType == ResourceFile
        WS->>WS: stream.Close()
    else ObjectType == BundleFile
        WS->>AM: UnloadBundleFile(bunInst)
    else ObjectType == AssetsFile && Parent == null
        WS->>AM: UnloadAssetsFile(fileInst)
    end
    WS->>WS: RootItems.Remove
    WS->>WS: ItemLookup.Remove
    WS->>WS: UnsavedItems/ModifiedItems.Remove
```

## 5.12 主题切换（Avalonia 11 + Dock）

```mermaid
sequenceDiagram
    participant U as User
    participant SVM as SettingsViewModel
    participant App as App.axaml
    participant DockFactory as MainDockFactory
    participant Theme as Themes/Accents

    U->>SVM: Select theme (Dark / Light)
    SVM->>App: RequestedThemeVariant = theme
    App->>Theme: 切换 Accents 资源
    SVM->>ConfigurationManager: Settings.Theme = new
    ConfigurationManager->>ConfigurationManager: SaveConfig
    SVM->>DockFactory: Rebuild dock (optional)
```

## 5.13 跨平台原生互操作

```mermaid
flowchart LR
  Build[dotnet build -r linux-x64] --> RID[RuntimeIdentifier win-x64/x86/linux-x64]
  RID --> Cop[MSBuild copy native libs]
  Cop --> NL[NativeLibs/rid/*]
  NL --> RT[runtimes/rid/native/*]
  RT --> Plug[Plugin DLL LoadUnmanagedDll]
  Plug --> PLC[PluginLoadContext.LoadUnmanagedDll]
  PLC --> Find[AssemblyDependencyResolver finds]
  Find --> Sym[LoadLib by symlink path]
  Sym --> Enc[textureencoder/cuttlefish/PVRTexLib]
```