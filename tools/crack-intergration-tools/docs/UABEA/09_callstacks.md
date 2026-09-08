# 09 · UABEA 关键调用栈汇总

## 9.1 启动与插件加载

```
[OS]
  → Program.Main (Program.cs:21)
    → AttachConsole (-1) [Win32]
    → AppDomain.UnhandledException += UABEAExceptionHandler
    → if args.Length > 0:
        CommandLineHandler.CLHMain(args) (CommandLineHandler.cs:349)
      else:
        BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)
          → App.OnFrameworkInitializationCompleted
            → new MainWindow() (MainWindow.axaml.cs:31)
              → new BundleWorkspace() (BundleWorkspace.cs:23)
              → am.LoadClassPackage("classdata.tpk")
              → MainWindow_Initialized (MainWindow.axaml.cs:71)
                → AddHandler(DragDrop.DropEvent, Drop)
                → pluginManager.LoadPluginsInDirectory("plugins/")
                  → foreach *.dll:
                    Assembly.LoadFrom(path) (PluginManager.cs:25)
                    → foreach type in asm:
                      typeof(UABEAPlugin).IsAssignableFrom(t) ?
                      → Activator.CreateInstance(t)
                      → Init() → PluginInfo
```

## 9.2 打开 .assets 文件

```
[拖拽 / 菜单打开]
  → MainWindow.OpenFile → FileTypeDetector.DetectFileType (FileTypeDetector.cs:9)
    → DetectFileType(AssetsFileReader, 0)
  → if AssetsFile:
    → am.LoadAssetsFile(path) → AssetsFileInstance
    → LoadOrAskTypeData (MainWindow.axaml.cs:587)
      → am.LoadClassDatabaseFromPackage(fileInst.file.Metadata.UnityVersion)
      → 或弹文件对话框让用户选 classdata.tpk
    → AssetWorkspace.LoadAssetsFile (AssetWorkspace.cs:131)
      → GenerateQuickLookup
      → foreach AssetInfo → AssetContainer
      → 递归 externals
    → open InfoWindow
      → SetupContainers (InfoWindow.axaml.cs:1080)
      → MakeDataGridItems (InfoWindow.axaml.cs:1113)
      → AddDataGridItem (InfoWindow.axaml.cs:1126)
```

## 9.3 打开 .bundle 文件

```
[MainWindow]
  → am.LoadBundleFile(path) → BundleFileInstance
  → AskLoadCompressedBundle (MainWindow.axaml.cs:814)
    → if AssetBundleUtil.IsBundleDataCompressed (AssetBundleUtil.cs:15):
      弹 MessageBox 询问
        → DecompressToFile → File.OpenWrite(bundle.decomp) + bun.Unpack
        → DecompressToMemory → MemoryStream + bun.Unpack
      → new AssetBundleFile from decompressed
  → BundleWorkspace.Reset (BundleWorkspace.cs:33)
    → PopulateFilesList (BundleWorkspace.cs:45)
      → foreach dirInf:
        → new SegmentStream + BundleWorkspaceItem
        → Files.Add / FileLookup[name]
  → LoadBundle 显示 UI
  → 用户点击 BtnInfo
    → 对每个 .assets entry:
      am.LoadAssetsFileFromBundle
      AssetWorkspace.LoadAssetsFile
      open InfoWindow
```

## 9.4 编辑 Texture2D（导出 + 重新导入）

```
[选中 Texture2D, 菜单 → Plugins → Export]
  → pluginManager.GetPluginsThatSupport (PluginManager.cs:57)
  → ExportTextureOption.ExecutePlugin (ExportTextureOption.cs:36)
    → SingleExport (ExportTextureOption.cs:123)
      → TextureHelper.GetByteArrayTexture (TextureHelper.cs:13)
        → workspace.GetTemplateField
        → image data → ByteArray
        → MakeValue
      → TextureFile.ReadTextureFile
      → TextureHelper.GetResSTexture (TextureHelper.cs:32) [if parentBundle]
      → TextureHelper.GetRawTextureBytes (TextureHelper.cs:69)
      → TextureHelper.GetPlatformBlob (TextureHelper.cs:98)
      → TextureImportExport.Export (TextureImportExport.cs:79)
        → if platform == 38 (Switch):
          ExportSwitch (TextureImportExport.cs:112)
            → Texture2DSwitchDeswizzler.GetSwitchGobsPerBlock
            → Texture2DSwitchDeswizzler.TextureFormatToBlockSize
            → Texture2DSwitchDeswizzler.GetPaddedTextureSize
            → TextureEncoderDecoder.Decode (TextureEncoderDecoder.cs:339)
            → Texture2DSwitchDeswizzler.SwitchUnswizzle
            → crop + flip
          else:
            → Decode
              case Crunch → DecodeCrunch → PInvoke.DecodeByCrunchUnity
              case PVR → DecodePVRTexLib → PInvoke.DecodeByPVRTexLib
              case DXT/BC7 → DecodeAssetRipperTex
        → SaveImageAtPath (TextureImportExport.cs:143)
          → Image.SaveAsPng / SaveAsTga

[用户修改 PNG 后]
  → ImportTextureOption.ExecutePlugin (ImportTextureOption.cs:109)
    → TextureHelper.GetByteArrayTexture
    → ImportTextures (ImportTextureOption.cs:39)
      → Image.Load
      → TextureImportExport.Import (TextureImportExport.cs:12)
        → if platform == 38:
          ImportSwitch (TextureImportExport.cs:47)
            → SwitchSwizzle + Encode
          else:
            → flip + TextureEncoderDecoder.Encode (TextureEncoderDecoder.cs:519)
      → baseField 修改
      → AssetsReplacerFromMemory
      → workspace.AddReplacer
        → ItemUpdated
```

## 9.5 保存修改

```
[用户菜单 Save]
  → MainWindow.MenuSave_Click (MainWindow.axaml.cs:243)
    → AskForLocationAndSave(false)
      → SaveBundle (MainWindow.axaml.cs:917)
        → BundleWorkspace.GetReplacers (BundleWorkspace.cs:111)
          → RemovedFiles → BundleRemover
          → Modified items → BundleReplacerFromStream
          → Renamed items → BundleRenamer
        → AssetWorkspace.GetChangedFiles (AssetWorkspace.cs:172)
          → foreach NewAssets → file
          → OtherAssetChanges != None → file
        → for each changed file:
          → file.file.Write(tempWriter, 0, replacers, null)
        → bun.Write(writer, bundleReplacers)
        → 写临时 ~file.bundle
        → File.Move 覆盖原文件
        → 原文件 → .bak0001 (递增)
```

## 9.6 .emip 应用（CLI）

```
[UABEAvalonia.exe applyemip foo.emip <game_dir>]
  → CommandLineHandler.ApplyEmip (CommandLineHandler.cs:237)
    → GetFlags(args)
    → InstallerPackageFile.Read (Emip.cs:20)
      → ParseReplacer (Emip.cs:116) 递归
    → for each affectedFile:
      if isBundle:
        GetNextBackup (CommandLineHandler.cs:86)
        DecompressBundle (CommandLineHandler.cs:54)
        for each replacer:
          if BundleReplacerFromAssets:
            GetDirInfo (BundleHelper)
            Init(reader, pos, size)
        bun.Write(mw, reps, addedTypes)
        File.Move modFile → affectedFile
        File.Move affectedFile → .bakNNNN
        delete .decomp (unless -kd or -md)
      else:
        assets.Read
        foreach replacer (AssetsReplacer):
          add to list
        assets.Write(mw, 0, reps, addedTypes)
        File.Move modFile → affectedFile
        File.Move affectedFile → .bakNNNN
```

## 9.7 TypeTree 文本导出

```
[InfoWindow BtnExportDump]
  → BatchExportDump (InfoWindow.axaml.cs:709)
    → for each selected:
      → cont = workspace.GetAssetContainer(onlyInfo: false)
      → file dialog (save as .txt)
      → AssetImportExport.DumpTextAsset (AssetImportExport.cs:34)
        → RecurseTextDump (AssetImportExport.cs:40)
          → 数组 → 写 size + 元素
          → 叶子 → type name + = value
          → ManagedReferencesRegistry v1/v2 特殊处理
```

## 9.8 TypeTree 文本导入

```
[InfoWindow BtnImportDump]
  → BatchImportDump (InfoWindow.axaml.cs:865)
    → for each selected:
      → file dialog (open .txt)
      → AssetImportExport.ImportTextAsset (AssetImportExport.cs:328)
        → AssetsFileWriter
        → ImportTextAssetLoop (AssetImportExport.cs:349)
          → alignStack
          → each line:
            → depth 检测
            → pop stack if depth decreases
            → parse align + typeName + value
            → aw.WriteXxx + maybe Align
      → AssetContainer(cont, baseField) 替换
      → workspace.AddReplacer
        → ItemUpdated
```

## 9.9 MonoBehaviour 字段恢复

```
[AssetDataTreeView 第一次展开 MonoBehaviour 节点]
  → workspace.GetAssetContainer(onlyInfo: false) (AssetWorkspace.cs:243)
    → isMonoBehaviour → SetMonoTempGenerators (AssetWorkspace.cs:411)
      → FindCpp2IlFiles.Find (AssetsTools.NET.Cpp2IL)
      → if success && ConfigurationManager.Settings.UseCpp2Il:
        am.MonoTempGenerator = new Cpp2IlTempGenerator(metaPath, asmPath)
      → else if Directory.Exists(<gameDir>/Managed):
        am.MonoTempGenerator = new MonoCecilTempGenerator(managedDir)
      → if 全部失败 → MonoTemplateLoadFailed event
    → am.GetRefTypeManager
    → tempField.MakeValue
```

## 9.10 崩溃处理

```
[任意未捕获异常]
  → AppDomain.UnhandledException
    → Program.UABEAExceptionHandler (Program.cs:57)
      → File.WriteAllText("uabeacrash.log", ex.ToString())
      → if Win32:
        Process.Start("mshta", "vbscript:Execute(...)") → 弹窗
      → else:
        Console.WriteLine
```