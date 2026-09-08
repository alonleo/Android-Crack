# 09 · UABEANext 关键调用栈汇总

## 9.1 启动与 DI

```
[OS]
  → UABEANext4.Desktop.exe
    → Program.Main
      → AppDomain.UnhandledException += UABEANExceptionHandler
      → BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)
        → App.axaml.cs.OnFrameworkInitializationCompleted
          → Ioc.Default.GetService<MainViewModel>()
            → new Workspace()
              → Manager.LoadClassPackage("classdata.tpk")  // 若存在
              → Plugins.LoadPluginsInDirectory("plugins")
                → foreach *.dll:
                  new PluginLoadContext(path)
                  asm = LoadFromAssemblyPath
                  collect IUavPluginOption / IUavPluginPreviewer
              → Namer = new AssetNamer(this)
          → MainWindow.DataContext = MainViewModel
        → MainWindow.Show()
```

## 9.2 拖拽 / 打开文件

```
[User drops file]
  → MainViewModel.OpenFileAsync
    → IStorageProvider.OpenFilePickerAsync
    → for each IStorageFile:
      stream = await OpenReadAsync
      WorkspaceItem item = Workspace.LoadAnyFile(stream, loadOrder)
        → FileTypeDetector.DetectFileType(reader, 0)
        → switch:
          case BundleFile → LoadBundle
          case AssetsFile → LoadAssets
          case .resS/.resource → LoadResource
    → WeakReferenceMessenger.Send(FileLoadedMessage)
```

## 9.3 LoadBundle 详情

```
Workspace.LoadBundle(stream, loadOrder, name)
  → Manager.LoadBundleFile(stream, name)
  → lock(_workingKeys)
    → foreach dirInf:
      检查 Manager.FileLookup / _workingKeys
      重复 → throw DuplicateWorkspaceFileException
      加入 ourWorkingKeys
  → TryLoadClassDatabase(bun.file)
    → if ClassDatabase == null && EngineVersion != "0.0.0":
      Manager.LoadClassDatabaseFromPackage(EngineVersion)
  → new WorkspaceItem(this, bunInst, loadOrder)
  → AddRootItemThreadSafe(item, bun.name)
    → FileSyncContext?.Post:
      RootItems.BinarySearch(item, by LoadIndex) → Insert
      ItemLookup[name] = item
  → finally: lock(_workingKeys) Remove all keys
```

## 9.4 选中 asset → Inspector 显示

```
[User selects asset in DataGrid]
  → AssetDocumentViewModel.SelectedAsset = asset
  → Workspace.GetBaseField(asset)
    → Manager.GetBaseField(fileInst, info)
  → [ObservableProperty] BaseField updated
  → WeakReferenceMessenger.Send(AssetDocumentSelectedMessage)
  → InspectorToolViewModel 接收到
    → BuildTreeView(BaseField)
  → AssetDataTreeView (in Inspector) 显示
```

## 9.5 编辑 asset 字段 → 标记脏

```
[User edits field in Inspector]
  → InspectorToolViewModel.FieldChanged
  → AssetDocumentViewModel.BaseField modified
  → BaseField.WriteToByteArray()
  → AssetContainer(AssetInst, baseField) 替换
  → Workspace.Dirty(item)
    → UnsavedItems.Add(item)
    → ModifiedItems.Add(item)
    → if parent: Dirty(parent)
```

## 9.6 保存

```
[User clicks Save]
  → MainViewModel.SaveCommand
  → Workspace.Save(item)
    → if !UnsavedItems.Contains → return (false, false)
    → origBundlePath = TryGetFileStream → stream.Name
    → tempPath = ~file in same dir
    → WriteAssetsFile/WriteBundleFile/WriteResource(item, tempStream)
      case AssetsFile:
        fileInst.file.Write(AssetsFileWriter(tempStream))
      case BundleFile:
        同步 DirectoryInfos
        bun.file.Write(AssetsFileWriter(tempStream))
    → File.Move(tempPath → origBundlePath, overwrite: true)
    → 重新 OpenRead + AssetsFile.Read
    → FixupAssetsFile
    → UnsavedItems.Remove(item)
```

## 9.7 插件菜单

```
[User right-click asset → Plugins → Export texture]
  → MainViewModel.GetContextMenu
  → Plugins.GetOptionsThatSupport(workspace, assets, Export)
    → for each option:
      if option.Options.HasFlag(Export) && option.SupportsSelection(...):
        添加到结果
  → for each option:
    await option.Execute(workspace, funcs, mode, assets)
      → funcs.ShowSaveFileDialog(...)  // 由 UavPluginFunctions 提供
      → TextureLoader.LoadTexture + Save
      → return true
```

## 9.8 预览器

```
[User selects Mesh asset]
  → InspectorToolViewModel.SelectedAsset changed
  → Plugins.GetPreviewersThatSupport(workspace, asset)
    → for each previewer:
      type = previewer.SupportsPreview(workspace, asset)
      if type != None: add
  → previewer.Initialize(workspace, funcs)
  → previewer.OnPreview(asset, funcs)
    → MeshPreviewer:
      workspace.GetBaseField(asset)
      new MeshObj().BuildFromBaseField(bf, fileInst)
      funcs.SetPreviewMesh(meshObj)
        → IPC to PluginPreviewer.Desktop
        → MeshPreviewerControl.SetMesh(mesh)
        → Silk.NET.OpenGL 重新编译 VBO
```

## 9.9 搜索

```
[User types in SearchDialog]
  → AssetDataSearchViewModel.Search
  → SearchLogic.Search(workspace, query, options, cts)
    → files = workspace.GetAllAssetsFileInstances()
    → Parallel.ForEach(files, new ParallelOptions { MaxDegreeOfParallelism = ProcessorCount })
      → BuildNameIndex
      → Match query
      → results.Add
    → return results
  → AssetDataSearchViewModel.Results = results
  → 显示列表
```

## 9.10 MonoBehaviour 字段恢复

```
[First access to MonoBehaviour asset]
  → Workspace.GetBaseField(asset)
    → CheckAndSetMonoTempGenerators(fileInst, info)
      → if isValidMono && !_setMonoTempGeneratorsYet && !TypeTreeEnabled:
        SetMonoTempGenerators(fileDir)
          → if managedExists && (!il2cppExists || UseManagedOverIl2cpp):
            Manager.MonoTempGenerator = new MonoCecilTempGenerator(managedDir)
          → else if il2cppExists:
            Manager.MonoTempGenerator = new Cpp2IlTempGenerator(metaPath, asmPath)
    → Manager.GetBaseField(fileInst, info)
```

## 9.11 主题切换

```
[User select new theme in SettingsViewModel]
  → SettingsViewModel.Theme = newTheme
  → ConfigurationValues.Theme setter → ConfigurationManager.SaveConfig
  → WeakReferenceMessenger.Send(RequestedThemeVariantChangedMessage)
  → App.OnFrameworkInitializationCompleted 处理
    → Application.Current.RequestedThemeVariant = newTheme
    → Avalonia 重新加载 Accents 资源
```

## 9.12 关闭文件

```
[User right-click → Close]
  → MainViewModel.CloseFileCommand
  → Workspace.Close(item)
    → if !item.Loaded || !RootItems.Contains → return
    → switch item.ObjectType:
      ResourceFile → stream.Close()
      BundleFile → Manager.UnloadBundleFile
      AssetsFile → Manager.UnloadAssetsFile
    → RootItems.Remove(item)
    → ItemLookup.Remove(item.Name)
    → UnsavedItems.Remove(item)
    → ModifiedItems.Remove(item)
    → foreach childItem:
      ItemLookup.Remove / UnsavedItems.Remove / ModifiedItems.Remove
```

## 9.13 EMIP 加载（CLI 不支持，UABEANext 无）

> UABEANext 移除了 .emip 支持。

## 9.14 加载 classdata.tpk

```
[First AssetsFile loaded]
  → Workspace.LoadAssets
    → TryLoadClassDatabase(fileInst.file)
      → if Manager.ClassDatabase == null:
        if metadata.UnityVersion != "0.0.0":
          Manager.LoadClassDatabaseFromPackage(UnityVersion)
            → [AssetsTools.NET] download from cache or repo
```

## 9.15 配置文件加载

```
[App startup]
  → App.OnFrameworkInitializationCompleted
    → var configService = Ioc.Default.GetService<IConfigurationService>()
    → ConfigurationManager.LoadConfig()  // 静态构造
      → 读 <exe-dir>/config.json
      → JsonConvert.DeserializeObject<ConfigurationValues>
    → Apply to services
```