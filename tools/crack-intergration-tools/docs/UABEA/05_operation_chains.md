# 05 · UABEA 主要操作链

本节列出 ≥ 7 条核心操作链。每条都配有 mermaid 时序图或流程图。

---

## 5.1 启动 → 主窗体 → 打开 .assets / .bundle 文件

```mermaid
sequenceDiagram
    participant U as 用户
    participant OS as OS Shell
    participant P as Program.Main
    participant A as Avalonia Runtime
    participant App as App.axaml.cs
    participant MW as MainWindow
    participant PM as PluginManager
    participant WS as AssetWorkspace
    participant FTD as FileTypeDetector
    participant ATN as AssetsManager

    U->>OS: 双击 UABEAvalonia.exe / dotnet run
    OS->>P: 进入 Main(args)
    P->>P: AppDomain.UnhandledException += handler
    alt args 为空
        P->>A: BuildAvaloniaApp().StartWithClassicDesktopLifetime
        A->>App: App.OnFrameworkInitializationCompleted
        App->>MW: new MainWindow()
        MW->>PM: pluginManager.LoadPluginsInDirectory("plugins/")
        PM->>PM: foreach *.dll → LoadFrom → 创建 UABEAPlugin
        MW->>WS: workspc = new AssetWorkspace(am, fromBundle: false)
        MW->>MW: window.Show()
        U->>MW: 拖拽 / 菜单 / OpenFilePicker
        MW->>FTD: FileTypeDetector.DetectFileType(path)
        FTD-->>MW: DetectedFileType
        alt AssetsFile
            MW->>ATN: am.LoadAssetsFile(path)
            MW->>WS: workspc.LoadAssetsFile(fileInst, true)
            MW->>MW: open InfoWindow
        else BundleFile
            MW->>ATN: am.LoadBundleFile(path)
            MW->>MW: new BundleWorkspace(bundleInst)
            MW->>MW: ShowBundleFiles
        end
    else 有 args
        P->>P: CommandLineHandler.CLHMain
    end
```

---

## 5.2 Bundle 解压（CLI / GUI 通用）

```mermaid
flowchart TD
    A[bundle file path] --> B[AssetBundleFile.Read<br/>new AssetsFileReader]
    B --> C{bun.Header.GetCompressionType == 0?}
    C -->|是| F[直接使用 bun.DataReader]
    C -->|否| D{decompFile 非空?}
    D -->|是| E[File.Open decompFile]
    D -->|否| M[MemoryStream]
    E --> U[bun.Unpack writer]
    M --> U
    U --> R[new AssetBundleFile<br/>bun.Read r]
    R --> F
    F --> END[可读 DirectoryInfos/Blocks]
```

涉及代码：
- `CommandLineHandler.DecompressBundle` (`CommandLineHandler.cs:54`)
- `BundleWorkspace.Reset` 内 `PopulateFilesList` (`BundleWorkspace.cs:45`)
- `TextureHelper.GetResSTexture` (`TextureHelper.cs:32`)

---

## 5.3 Asset 树构建 + 选中 → DumpRaw / DumpText 导出

```mermaid
sequenceDiagram
    participant U as 用户
    participant MW as MainWindow
    participant IW as InfoWindow
    participant WS as AssetWorkspace
    participant ATN as AssetsManager
    participant AIE as AssetImportExport
    participant FS as File System

    U->>MW: 选中 asset，右键 Export raw / Export text
    MW->>IW: ShowExportWindow
    IW->>WS: GetBaseField(cont)
    WS->>ATN: GetTemplateBaseField(fileInst, reader, pos, classId, monoId, flags)
    ATN-->>WS: AssetTypeTemplateField
    WS->>ATN: MakeValue(reader, pos)
    ATN-->>WS: AssetTypeValueField
    WS-->>IW: cont.BaseValueField
    alt DumpRaw
        IW->>AIE: DumpRawAsset(wfs, reader, pos, size)
        AIE->>FS: WriteAllBytes
    else DumpText
        IW->>AIE: DumpTextAsset(sw, baseField)
        AIE->>AIE: RecurseTextDump
        AIE->>FS: WriteAllText
    end
```

涉及代码：
- `AssetWorkspace.GetBaseField` (`AssetWorkspace.cs:337`)
- `AssetImportExport.DumpRawAsset` (`AssetImportExport.cs:20`)
- `AssetImportExport.DumpTextAsset` + `RecurseTextDump` (`AssetImportExport.cs:34, 40`)

---

## 5.4 Raw / Text Import 回写

```mermaid
flowchart LR
    A[用户改好 .txt] --> B[AssetImportExport.ImportTextAsset]
    B --> C[ImportTextAssetLoop<br/>维护 alignStack<br/>逐行解析类型与值]
    C --> D[AssetsFileWriter.WriteXXX]
    D --> E[byte[] savedAsset]
    E --> F[AssetTypeValueField.WriteToByteArray<br/>或 cont.BaseValueField.WriteToByteArray]
    F --> G[AssetsReplacerFromMemory]
    G --> H[AssetWorkspace.AddReplacer]
    H --> I[ItemUpdated 事件]
```

涉及代码：
- `AssetImportExport.ImportTextAsset` (`AssetImportExport.cs:328`)
- `AssetImportExport.ImportTextAssetLoop` (`AssetImportExport.cs:349`)
- `AssetImportExport.ImportRawAsset` (`AssetImportExport.cs:319`)
- `AssetWorkspace.AddReplacer` (`AssetWorkspace.cs:68`)

---

## 5.5 EMIP mod 包导入应用

```mermaid
sequenceDiagram
    participant CLI as CommandLineHandler.ApplyEmip
    participant FS as File System
    participant IPF as InstallerPackageFile
    participant ATN as AssetsTools.NET
    participant BUN as AssetBundleFile
    participant ASF as AssetsFile

    CLI->>FS: File.OpenRead(emipFile)
    CLI->>IPF: instPkg.Read(reader, true)
    loop instPkg.affectedFiles
        CLI->>BUN: DecompressBundle → AssetBundleFile
        alt affectedFile.isBundle
            CLI->>BUN: bun.Write(mw, reps, addedTypes)
            CLI->>FS: File.Move modFile → 原文件
            CLI->>FS: File.Move 原文件 → .bakNNNN
        else isAssetsFile
            CLI->>ASF: assets.Read(ar)
            CLI->>ASF: assets.Write(mw, 0, reps, addedTypes)
            CLI->>FS: File.Move modFile → 原文件
            CLI->>FS: File.Move 原文件 → .bakNNNN
        end
    end
```

涉及代码：
- `CommandLineHandler.ApplyEmip` (`CommandLineHandler.cs:237`)
- `CommandLineHandler.GetNextBackup` (`CommandLineHandler.cs:86`)
- `Emip.InstallerPackageFile.Read` (`Emip.cs:20`)
- `Emip.ParseReplacer` (`Emip.cs:116`)

---

## 5.6 插件调用（TexturePlugin 导出 PNG → 编辑 → 导入）

```mermaid
sequenceDiagram
    participant U as 用户
    participant MW as MainWindow
    participant PM as PluginManager
    participant TP as TexturePlugin.ExportTextureOption
    participant WS as AssetWorkspace
    participant TH as TextureHelper
    participant TF as TextureFile (ATN)
    participant TIE as TextureImportExport
    participant TED as TextureEncoderDecoder
    participant PI as PInvoke (textoolwrap.dll)

    U->>MW: 选中 Texture2D → 插件菜单
    MW->>PM: GetPluginsThatSupport
    PM-->>MW: [UABEAPluginMenuInfo]
    MW->>TP: ExecutePlugin
    TP->>WS: GetByteArrayTexture (设置 image data 为 ByteArray)
    WS-->>TP: AssetTypeValueField
    TP->>TF: ReadTextureFile
    TF-->>TP: TextureFile
    TP->>TH: GetResSTexture / GetRawTextureBytes
    TH-->>TP: byte[] pictureData
    TP->>TIE: Export(data, path, w, h, fmt, platform, platformBlob)
    alt Switch 平台 (38)
        TIE->>TIE: ImportSwitch / ExportSwitch<br/>(SwitchSwizzle / Unswizzle)
    end
    TIE->>TED: Decode / Encode
    TED->>PI: DecodeByPVRTexLib / Crunch / ISPC
    TIE->>U: 写 PNG/TGA
    U->>U: 用外部工具修改
    U->>MW: 选 modified.png → 触发 ImportTextureOption
    Note over MW,TIE: 镜像 Export 路径，构造 AssetsReplacerFromMemory
```

涉及代码：
- `TexturePlugin.ExportTextureOption.ExecutePlugin / BatchExport / SingleExport` (`ExportTextureOption.cs:36, 44, 123`)
- `TexturePlugin.ImportTextureOption.ExecutePlugin / ImportTextures` (`ImportTextureOption.cs:109, 39`)
- `TexturePlugin.TextureImportExport.Export / Import / ExportSwitch / ImportSwitch` (`TextureImportExport.cs:79, 12, 112, 47`)
- `TexturePlugin.TextureEncoderDecoder.Decode / Encode / EncodeMip / RGBAToFormatByteSize` (`TextureEncoderDecoder.cs:339, 519, 438, 12`)
- `TexturePlugin.Texture2DSwitchDeswizzler.*` (`Texture2DSwitchDeswizzler.cs:54, 98, 143, 180, 187`)
- `TexturePlugin.PInvoke.*` (`PInvoke.cs:13, 16, 19, 22, 25, 28`)

---

## 5.7 CLI batch 模式（batchexportbundle / batchimportbundle）

```mermaid
flowchart TD
    A[UABEAvalonia batchexportbundle DIR] --> B[BatchExportBundle]
    B --> C{遍历 DIR 中文件}
    C -->|FileTypeDetector == BundleFile| D[DecompressBundle]
    D --> E{遍历 bun.DirectoryInfos}
    E -->|每个 entry| F[BundleHelper.LoadAssetDataFromBundle]
    F --> G{flags.Contains -keepnames?}
    G -->|是| H[outName = entry.Name]
    G -->|否| I[outName = bunFile_ + entry.Name]
    H --> J[File.WriteAllBytes]
    I --> J
    J --> K[完成]

    L[UABEAvalonia batchimportbundle DIR] --> M[BatchImportBundle]
    M --> N{遍历 DIR 中文件}
    N -->|BundleFile| O[DecompressBundle]
    O --> P{遍历 bun.DirectoryInfos}
    P -->|每个 entry| Q{File.Exists bunFile_ + entry.Name?}
    Q -->|是| R[BundleReplacerFromStream]
    Q -->|否| S[跳过]
    R --> T[bun.Write writer, reps<br/>写入内存]
    T --> U[File.WriteAllBytes file, data]
    U --> V[完成]
```

涉及代码：
- `CommandLineHandler.BatchExportBundle` (`CommandLineHandler.cs:101`)
- `CommandLineHandler.BatchImportBundle` (`CommandLineHandler.cs:156`)
- `CommandLineHandler.GetMainFileName / GetFlags` (`CommandLineHandler.cs:33, 43`)
- `CommandLineHandler.DecompressBundle` (`CommandLineHandler.cs:54`)

---

## 5.8 TypeTree 文本 dump/import 详细流程（操作链 4 展开）

```mermaid
flowchart TB
    subgraph DumpTextAsset
      A1[DumpTextAsset sw, baseField] --> A2[RecurseTextDump field, depth=0]
      A2 --> A3{isArray?}
      A3 -->|是| A4[写 sizeTemplate + size = N]
      A4 --> A5[for each child<br/>RecurseTextDump child depth+2]
      A3 -->|否| A6[判断 ValueType]
      A6 -->|String| A7[value = escape + quote]
      A6 -->|其他 primitive| A8[value = AsString]
      A6 -->|ManagedReferencesRegistry| A9[特殊格式 v1/v2]
      A9 --> A10[for each referencedObject<br/>RecurseTextDump child depth+3]
      A7 --> A11[sw.WriteLine]
      A8 --> A11
      A11 --> A12{field 有 children?}
      A12 -->|是| A13[RecurseTextDump children depth+1]
    end

    subgraph ImportTextAssetLoop
      B1[ImportTextAssetLoop] --> B2[while true: readLine]
      B2 --> B3[计算 thisDepth = leading spaces]
      B3 --> B4{line[thisDepth] == '['?}
      B4 -->|是 - array index| B2
      B4 -->|否| B5{thisDepth < alignStack.Count?}
      B5 -->|是| B6[pop align → aw.Align]
      B6 --> B5
      B5 -->|否| B7[parse align bit + typeName + value]
      B7 --> B8{有 =?}
      B8 -->|是| B9[按类型写 aw.WriteXXX]
      B9 --> B10{align ? aw.Align}
      B10 --> B2
      B8 -->|否| B11[alignStack.Push align]
      B11 --> B2
    end
```

涉及代码：
- `AssetImportExport.RecurseTextDump` (`AssetImportExport.cs:40`)
- `AssetImportExport.ImportTextAssetLoop` (`AssetImportExport.cs:349`)

---

## 5.9 Plugin 加载流程（GUI 启动时）

```mermaid
sequenceDiagram
    participant MW as MainWindow
    participant PM as PluginManager
    participant FS as File System
    participant ASM as Assembly
    participant PLG as UABEAPlugin

    MW->>PM: new PluginManager
    MW->>PM: LoadPluginsInDirectory("plugins/")
    PM->>FS: Directory.CreateDirectory (if missing)
    PM->>FS: EnumerateFiles("*.dll")
    loop 每个 DLL
        PM->>ASM: Assembly.LoadFrom(path)
        ASM-->>PM: Assembly
        loop Assembly.GetTypes
            PM->>PLG: typeof(UABEAPlugin).IsAssignableFrom(t) ?
            alt 是
                PM->>PLG: Activator.CreateInstance(t)
                PLG->>PLG: Init()
                PLG-->>PM: PluginInfo { name, options }
                PM->>PM: loadedPlugins.Add
            end
        end
    end
```

涉及代码：
- `PluginManager.LoadPlugin` (`PluginManager.cs:21`)
- `PluginManager.LoadPluginsInDirectory` (`PluginManager.cs:48`)
- `PluginManager.GetPluginsThatSupport` (`PluginManager.cs:57`)