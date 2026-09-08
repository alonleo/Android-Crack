# 08 · UABEANext 详细说明

> 由于 UABEANext 文件众多（~200），本目录按模块分组。每个 .md 涵盖一个或多个相关模块的所有公共 / 内部函数。

---

## 文件清单

| 文件 | 涵盖模块 |
|---|---|
| [entry_programs.md](entry_programs.md) | UABEANext4.Desktop/Program.cs + UABEANext4/App.axaml.cs |
| [workspace.md](workspace.md) | Workspace + Workspace.Saving + WorkspaceItem + AssetInst + ContainerTool + ContainerToolManager |
| [plugins.md](plugins.md) | PluginLoader + PluginLoadContext + IUavPlugin* + UavPluginFunctions |
| [import_export.md](import_export.md) | AssetImport + AssetExport |
| [asset_info.md](asset_info.md) | TypeTreeInfo / ScriptInfo / ExternalInfo / GeneralInfo / BuildTarget / Messages |
| [mesh.md](mesh.md) | MeshObj / Channel / MeshEnums |
| [search.md](search.md) | SearchLogic + SearchResultItem |
| [converters.md](converters.md) | 6 个 IValueConverter |
| [util.md](util.md) | AssetNamer + FileTypeDetector + PathUtils + MessageBoxUtil + StorageService + WindowUtils |
| [services.md](services.md) | DialogService + IDialogService + DummyDialogService |
| [viewmodels.md](viewmodels.md) | MainViewModel + MainDockFactory + 12 Dialog VM + 5 Tool VM + 2 Document VM + ViewModelBase |
| [views.md](views.md) | MainView + MainWindow + 12 Dialog View + 7 Tool View + 2 Document View |
| [texture_plugin.md](texture_plugin.md) | TexturePlugin 全套（ExportTextureOption + ImportBatch + EditTexture + Previewer + SpritePreviewer + TextureLoader + SpriteAtlasLookup + TextureHelper + Logic/EditTexture/* + ViewModels + Views） |
| [audio_plugin.md](audio_plugin.md) | AudioPlugin（CompressionFormat + ExportAudioOption） |
| [font_plugin.md](font_plugin.md) | FontPlugin（ExportFontOption + ImportFontOption + FontHelper） |
| [text_asset_plugin.md](text_asset_plugin.md) | TextAssetPlugin（Export/Import + Previewer） |
| [mesh_plugin.md](mesh_plugin.md) | MeshPlugin（MeshPreviewer） |
| [plugin_previewer.md](plugin_previewer.md) | PluginPreviewer + PluginPreviewer.Desktop |
| [native_libs.md](native_libs.md) | NativeLibs 各 RID 的 native DLL/SO |

---

## 通用说明

UABEANext 大量使用 `[ObservableProperty]` 和 `[RelayCommand]` 源生成器。例如：

```csharp
[ObservableProperty]
private string _name = "";

[RelayCommand]
private void OpenFile() { ... }
```

会生成：
- `public string Name { get; set; }` + `OnNameChanged(...)` partial method
- `public IRelayCommand OpenFileCommand { get; }` 属性

因此函数索引中**间接存在大量自动生成的 property**，本目录不逐一列出，但调用方按"裸名"引用。