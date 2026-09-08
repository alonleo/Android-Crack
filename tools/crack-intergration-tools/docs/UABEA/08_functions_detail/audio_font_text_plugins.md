# 08 · 音频 / 字体 / TextAsset 插件详细说明

## 8.1 AudioClipPlugin（FMOD5 音频导出）

文件：`AudioClipPlugin/Program.cs` (292 LoC)，单文件包含全部。

### `enum CompressionFormat`
- **位置**：`AudioClipPlugin/Program.cs:16`
- **值**：`PCM, Vorbis, ADPCM, MP3, VAG, HEVAG, XMA, AAC, GCADPCM, ATRAC9`

### `class ExportAudioClipOption : UABEAPluginOption`

#### `SelectionValidForPlugin(...)`
- **签名**：`public bool SelectionValidForPlugin(AssetsManager am, UABEAPluginAction action, List<AssetContainer> selection, out string name)`
- **位置**：`AudioClipPlugin/Program.cs:32`
- **算法**：`action == Export` 且所有 `ClassId == AudioClip`

#### `ExecutePlugin(...)`
- **位置**：`AudioClipPlugin/Program.cs:47`
- 调 `BatchExport` / `SingleExport`

#### `BatchExport(...)`
- **位置**：`AudioClipPlugin/Program.cs:55`
- **算法**：选目录 → 对每个 cont 取 base field → 取 m_Name/CompressionFormat/Resource → `GetAudioBytes` → `FsbLoader.TryLoadFsbFromByteArray` → `RebuildAsStandardFileFormat` → `FixWAV`(若 WAV) → `File.WriteAllBytes`

#### `SingleExport(...)`
- **位置**：`AudioClipPlugin/Program.cs:107`
- **算法**：弹保存对话框（扩展名按 CompressionFormat 决定）→ 同样音频提取流程

#### `static void FixWAV(ref byte[] wavData)`
- **签名**：`private static void FixWAV(ref byte[] wavData)`
- **位置**：`AudioClipPlugin/Program.cs:161`
- **可见性**：private static
- **副作用**：原地修改 wavData
- **算法**：
  1. 移除 fmt chunk 的 ExtraParamSize（2 bytes）
  2. 重新写 RIFF chunk size (`wavData.Length - 8`)
  3. 重新写 fmt chunk size = 16
  4. 重新写 data chunk size (`wavData.Length - 44`)

#### `static string GetExtension(CompressionFormat format)`
- **位置**：`AudioClipPlugin/Program.cs:193`
- **返回值**：扩展名字符串
- 映射表：
  - PCM / ADPCM / GCADPCM → wav
  - Vorbis → ogg
  - MP3 → mp3
  - AAC → aac
  - VAG / HEVAG / XMA / ATRAC9 → dat

#### `bool GetAudioBytes(AssetContainer cont, string filepath, ulong offset, ulong size, out byte[] audioData)`
- **签名**：`private bool GetAudioBytes(AssetContainer cont, string filepath, ulong offset, ulong size, out byte[] audioData)`
- **位置**：`AudioClipPlugin/Program.cs:211`
- **可见性**：private
- **算法**（按优先级）：
  1. `parentBundle != null` 时在 bundle `DirectoryInfos` 中按文件名匹配 → 读 bundle stream
  2. 失败时从磁盘 `<assetsDir>/<filepath>` 读
  3. 还失败时从 `<assetsDir>/<basename>` 读
- **返回值**：是否成功读到 `audioData`

### `class TextAssetPlugin : UABEAPlugin`（类名其实是 TextAssetPlugin 但在 AudioClipPlugin.csproj 中；命名空间 AudioPlugin）

- **`Init()`** (`AudioClipPlugin/Program.cs:282`)
  - name = "AudioClip Export"
  - options = `[ExportAudioClipOption]`

### 依赖
- Fmod5Sharp（FSB 解析）
- Avalonia（文件对话框）
- AssetsTools.NET

---

## 8.2 FontPlugin（TTF/OTF 导入导出）

文件：`FontPlugin/Program.cs` (252 LoC)。

### `static class FontHelper`

#### `static AssetTypeValueField GetByteArrayFont(AssetWorkspace, AssetContainer)`
- **签名**：`public static AssetTypeValueField GetByteArrayFont(AssetWorkspace workspace, AssetContainer font)`
- **位置**：`FontPlugin/Program.cs:16`
- **可见性**：public static
- **算法**：取 template，`m_FontData.Children[0].ValueType = ByteArray`；`MakeValue` 返回
- **被调用**：`ImportFontOption`, `ExportFontOption`

#### `static bool IsDataOtf(byte[] byteData)`
- **签名**：`public static bool IsDataOtf(byte[] byteData)`
- **位置**：`FontPlugin/Program.cs:30`
- **可见性**：public static
- **算法**：检查 magic `OTTO`

### `class ImportFontOption : UABEAPluginOption`

#### `SelectionValidForPlugin / ExecutePlugin`
- 位置：`FontPlugin/Program.cs:41, 56`
- **算法**：`ClassId == Font` 且 `action == Import`

#### `BatchImport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`FontPlugin/Program.cs:64`
- **算法**：选目录 → `ImportBatch` 对话框 → 对每个 batchInfo 读字节 → `baseField["m_FontData.Array"].AsByteArray = byteData` → `WriteToByteArray` → `AssetsReplacerFromMemory` → `workspace.AddReplacer`

#### `SingleImport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`FontPlugin/Program.cs:101`
- **算法**：弹单文件对话框 → 同样处理

### `class ExportFontOption : UABEAPluginOption`

#### `SelectionValidForPlugin / ExecutePlugin`
- 位置：`FontPlugin/Program.cs:138, 153`

#### `BatchExport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`FontPlugin/Program.cs:161`
- **算法**：选目录 → 每个 Font 取 `m_FontData.Array` 字节 → 跳过空 → 根据 `IsDataOtf` 选 .otf 或 .ttf → `File.WriteAllBytes`

#### `SingleExport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`FontPlugin/Program.cs:196`
- **算法**：弹保存对话框（默认扩展名按 IsDataOtf）→ 同上

### `class FontPlugin : UABEAPlugin`
- **`Init()`** (`FontPlugin/Program.cs:241`)
  - name = "Font Import/Export"
  - options = `[ImportFontOption, ExportFontOption]`

---

## 8.3 TextAssetPlugin

文件：`TextAssetPlugin/Program.cs` (252 LoC)。

### `static class TextAssetHelper`

#### `static string GetUContainerExtension(AssetContainer item)`
- **签名**：`public static string GetUContainerExtension(AssetContainer item)`
- **位置**：`TextAssetPlugin/Program.cs:15`
- **可见性**：public static
- **算法**：取 `item.Container` 的扩展名（若文件名包含扩展名）

### `class ImportTextAssetOption : UABEAPluginOption`

#### `SelectionValidForPlugin / ExecutePlugin`
- 位置：`TextAssetPlugin/Program.cs:29, 44`

#### `BatchImport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`TextAssetPlugin/Program.cs:52`
- **算法**：选目录 → `ImportBatch` 对话框（扩展名 `*`）→ 替换 `m_Script` 字节 → `AssetsReplacerFromMemory`

#### `SingleImport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`TextAssetPlugin/Program.cs:88`
- **算法**：根据 container 扩展名定制 file filter → 替换 `m_Script`

### `class ExportTextAssetOption : UABEAPluginOption`

#### `SelectionValidForPlugin / ExecutePlugin`
- 位置：`TextAssetPlugin/Program.cs:136, 151`

#### `BatchExport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`TextAssetPlugin/Program.cs:159`
- **算法**：选目录 → 每个 TextAsset 取 `m_Script` → 默认 .txt，或用 `GetUContainerExtension` 返回的扩展

#### `SingleExport(Window, AssetWorkspace, List<AssetContainer>)`
- **位置**：`TextAssetPlugin/Program.cs:194`
- **算法**：弹保存对话框（filter 按 container 扩展名）→ `File.WriteAllBytes`

### `class TextAssetPlugin : UABEAPlugin`
- **`Init()`** (`TextAssetPlugin/Program.cs:242`)
  - name = "TextAsset Import/Export"
  - options = `[ImportTextAssetOption, ExportTextAssetOption]`

---

## 8.4 关键调用栈

```
[Export Audio]
  → ExportAudioClipOption.ExecutePlugin
    → BatchExport / SingleExport
      → workspace.GetBaseField(cont)
      → GetAudioBytes (bundle resS → 磁盘)
      → FsbLoader.TryLoadFsbFromByteArray
      → samples[0].RebuildAsStandardFileFormat
      → FixWAV (if WAV)
      → File.WriteAllBytes
```

```
[Import Font batch]
  → ImportFontOption.BatchImport
    → FontHelper.GetByteArrayFont
    → baseField["m_FontData.Array"].AsByteArray = bytes
    → baseField.WriteToByteArray()
    → AssetsReplacerFromMemory
    → workspace.AddReplacer
```

```
[Export TextAsset]
  → ExportTextAssetOption.BatchExport
    → workspace.GetBaseField
    → baseField["m_Script"].AsByteArray
    → File.WriteAllBytes
```