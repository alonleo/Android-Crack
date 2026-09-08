# 08 · 插件系统详细说明（Plugins/ + 插件项目）

涉及文件：
- `UABEAvalonia/Plugins/PluginManager.cs` (80 LoC)
- `UABEAvalonia/Plugins/UABEAPlugin.cs`
- `UABEAvalonia/Plugins/UABEAPluginAction.cs`
- `UABEAvalonia/Plugins/UABEAPluginOption.cs`
- `UABEAvalonia/Plugins/UABEAPluginMenuInfo.cs`
- `UABEAvalonia/Plugins/PluginInfo.cs`
- 四个插件项目：`TexturePlugin/`, `AudioClipPlugin/`, `FontPlugin/`, `TextAssetPlugin/`

---

## 8.1 PluginManager.cs

### `PluginManager.PluginManager()`
- **签名**：`public PluginManager()`
- **位置**：`UABEAvalonia/Plugins/PluginManager.cs:16`
- **可见性**：public

### `PluginManager.LoadPlugin(string path)`
- **签名**：`public bool LoadPlugin(string path)`
- **位置**：`UABEAvalonia/Plugins/PluginManager.cs:21`
- **可见性**：public
- **参数**：`path` —— DLL 完整路径
- **返回值**：是否成功加载
- **副作用**：
  - `Assembly.LoadFrom(path)`
  - 遍历类型，找第一个 `UABEAPlugin` 子类
  - `Activator.CreateInstance` → `Init()` → 加入 `loadedPlugins`
- **抛出**：try/catch 失败返回 false（不重抛）
- **被调用**：`LoadPluginsInDirectory` 内

### `PluginManager.LoadPluginsInDirectory(string directory)`
- **签名**：`public void LoadPluginsInDirectory(string directory)`
- **位置**：`UABEAvalonia/Plugins/PluginManager.cs:48`
- **可见性**：public
- **副作用**：`Directory.CreateDirectory(directory)`（不存在则创建）
- **调用了**：`LoadPlugin`
- **被调用**：`MainWindow` 构造函数 (`MainWindow.axaml.cs:31+`)

### `PluginManager.GetPluginsThatSupport(AssetsManager am, List<AssetContainer> selectedAssets)`
- **签名**：`public List<UABEAPluginMenuInfo> GetPluginsThatSupport(AssetsManager am, List<AssetContainer> selectedAssets)`
- **位置**：`UABEAvalonia/Plugins/PluginManager.cs:57`
- **可见性**：public
- **算法**：
  - 对每个 loaded plugin 的每个 option，遍历 Import/Export 两个 action
  - 调 `option.SelectionValidForPlugin(am, action, selection, out entryName)`
  - 若支持 → `new UABEAPluginMenuInfo(pluginInf, option, entryName)` 加入列表
- **被调用**：`InfoWindow.BtnPlugin_Click` (`InfoWindow.axaml.cs:402`)

---

## 8.2 接口与枚举

### `interface UABEAPlugin`
- **位置**：`UABEAvalonia/Plugins/UABEAPlugin.cs:9`
- **方法**：`PluginInfo Init()`

### `enum UABEAPluginAction`
- **位置**：`UABEAvalonia/Plugins/UABEAPluginAction.cs:3`
- 值：`Import = 1`, `Export = 2`, `Console = 4`, `Create = 8`, `All = 15`

### `interface UABEAPluginOption`
- **位置**：`UABEAvalonia/Plugins/UABEAPluginOption.cs:8`
- 方法：
  - `bool SelectionValidForPlugin(AssetsManager am, UABEAPluginAction action, List<AssetContainer> selection, out string name)`
  - `Task<bool> ExecutePlugin(Window win, AssetWorkspace workspace, List<AssetContainer> selection)`

### `class UABEAPluginMenuInfo`
- **位置**：`UABEAvalonia/Plugins/UABEAPluginMenuInfo.cs:9`
- 字段：`pluginInf`, `pluginOpt`, `displayName`（只读）
- `override ToString() => displayName`

### `class PluginInfo`
- **位置**：`UABEAvalonia/Plugins/PluginInfo.cs:9`
- 字段：`name`, `options`

---

## 8.3 TexturePlugin 入口

### `class TexturePlugin : UABEAPlugin`
- **位置**：`TexturePlugin/Program.cs:16`
- **`Init()`** 注册三个 Option：
  - `ImportTextureOption`（Import action）
  - `ExportTextureOption`（Export action）
  - `EditTextureOption`（Import action）

---

## 8.4 AudioClipPlugin 入口

### `enum CompressionFormat`
- **位置**：`AudioClipPlugin/Program.cs:16`
- 值：`PCM`, `Vorbis`, `ADPCM`, `MP3`, `VAG`, `HEVAG`, `XMA`, `AAC`, `GCADPCM`, `ATRAC9`

### `class ExportAudioClipOption : UABEAPluginOption`
- **`SelectionValidForPlugin`**：`cont.ClassId == AudioClip` 且 `action == Export`
- **`ExecutePlugin`** → 调 `BatchExport` 或 `SingleExport`
- **`BatchExport / SingleExport`**：
  - 取 `m_Name`, `m_CompressionFormat`, `m_Resource.m_Source/Offset/Size`
  - `GetAudioBytes` → 从 bundle 或磁盘取字节
  - `FsbLoader.TryLoadFsbFromByteArray`
  - `samples[0].RebuildAsStandardFileFormat(out sampleData, out sampleExtension)`
  - 若 WAV → `FixWAV`
  - `File.WriteAllBytes`
- **`FixWAV(ref byte[])`**：
  - 移除 ExtraParamSize
  - 写 ChunkSize（RIFF, fmt, data）
- **`GetExtension(CompressionFormat)`**：
  - PCM/ADPCM/GCADPCM → wav
  - Vorbis → ogg
  - MP3 → mp3
  - AAC → aac
  - 其余 → dat
- **`GetAudioBytes`**：
  - 优先从 `parentBundle.file` 内的 resS 读
  - 否则从磁盘 `<assetsDir>/<source>` 读
  - 否则 `<assetsDir>/<source basename>`

### `class TextAssetPlugin : UABEAPlugin`
- **位置**：`AudioClipPlugin/Program.cs:280`
- `Init()` 注册 ExportAudioClipOption

---

## 8.5 FontPlugin 入口

### `static class FontHelper`
- **`GetByteArrayFont(AssetWorkspace, AssetContainer)`** (`Program.cs:16`)：
  - 取 template，`m_FontData.Children[0].ValueType = ByteArray`
  - `MakeValue`
- **`IsDataOtf(byte[])`** (`Program.cs:30`)：magic `OTTO`

### `class ImportFontOption : UABEAPluginOption`
- **`SelectionValidForPlugin`**：`ClassId == Font` 且 action == Import
- **`BatchImport`**：打开文件夹 → `ImportBatch` 对话框 → 替换 `m_FontData.Array`
- **`SingleImport`**：单文件对话框

### `class ExportFontOption : UABEAPluginOption`
- **`BatchExport`**：导出每个 Font 的 `m_FontData.Array`
- **`SingleExport`**：根据 `IsDataOtf` 决定 .otf 或 .ttf

### `class FontPlugin : UABEAPlugin`
- **`Init()`** (`Program.cs:241`) 注册 ImportFontOption + ExportFontOption

---

## 8.6 TextAssetPlugin 入口

### `static class TextAssetHelper`
- **`GetUContainerExtension(AssetContainer)`** (`Program.cs:15`)：返回 Container 路径的扩展名

### `class ImportTextAssetOption : UABEAPluginOption`
- **`BatchImport / SingleImport`**：替换 `m_Script` ByteArray

### `class ExportTextAssetOption : UABEAPluginOption`
- **`BatchExport / SingleExport`**：取 `m_Script` 字节并写出
- 默认扩展名 .txt，若 `GetUContainerExtension` 返回非空，则用其扩展

### `class TextAssetPlugin : UABEAPlugin`
- **`Init()`** (`Program.cs:242`) 注册 ImportTextAssetOption + ExportTextAssetOption

---

## 8.7 关键调用栈

```
[MainWindow 启动]
  → new PluginManager()
  → pluginManager.LoadPluginsInDirectory("plugins/")
    → foreach *.dll
      → Assembly.LoadFrom
      → foreach type in asm
        → typeof(UABEAPlugin).IsAssignableFrom(t) ?
        → new UABEAPlugin()
        → .Init() → PluginInfo { name, options }
```

```
[UI 插件按钮]
  → BtnPlugin_Click
    → pluginManager.GetPluginsThatSupport(am, selectedAssets)
    → foreach menuInfo: ExecutePlugin(win, workspace, selection)
```