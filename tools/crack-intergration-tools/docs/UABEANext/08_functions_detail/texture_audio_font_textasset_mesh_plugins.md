# 08 · 4 个媒体插件详细说明

涉及文件：
- `UABEANext/TexturePlugin/`
- `UABEANext/AudioPlugin/`
- `UABEANext/FontPlugin/`
- `UABEANext/TextAssetPlugin/`
- `UABEANext/MeshPlugin/`

---

## 1. TexturePlugin/

### 核心类

#### `class ExportTextureOption : IUavPluginOption`
- **`SupportsSelection`**：检查 mode == Export + 所有 asset 是 Texture2D
- **`Execute(Workspace, IUavPluginFunctions, UavPluginMode, List<AssetInst>)`**：
  - 弹 `ExportBatchOptionsView` 让用户选 PNG / JPG / BMP / TGA
  - 弹保存对话框（`funcs.ShowSaveFileDialog`）
  - 遍历每个 asset：`TextureLoader.LoadTexture(fileInst, pathId)` → 保存为图片

#### `class ImportBatchTextureOption : IUavPluginOption`
- **`Execute`**：
  - 弹选择目录对话框
  - 弹 `BatchImportView` 让用户映射文件到 asset
  - 对每个匹配：`TextureLoader.EncodeTexture` → 替换 baseField bytes

#### `class EditTextureOption : IUavPluginOption`
- **`Execute`**：
  - 弹 `EditTextureView`
  - 用户编辑后回写

#### `class TexturePreviewer : IUavPluginPreviewer`
- **`SupportsPreview`**：对 Texture2D 返回 Image
- 在 `PluginPreviewer.Desktop` 进程中通过 `IUavPluginPreviewerFunctions.SetPreviewImage` 显示

#### `class SpritePreviewer : IUavPluginPreviewer`
- 类似但针对 Sprite 类型

### Helpers

#### `class TextureLoader`
- **`Bitmap LoadTexture(AssetsFileInstance fileInst, long pathId)`**
  - 调 `AssetRipper.TextureDecoder.Decode` + 颜色空间转换 + 垂直翻转
- **`byte[] EncodeTexture(Bitmap bitmap, TextureFormat fmt, ...)`**
  - 使用 textureencoder / cuttlefish / PVRTexLib native

#### `class SpriteAtlasLookup`
- 解析 SpriteAtlas → Sprite 列表

#### `class TextureHelper`
- 公共工具

### Logic/EditTexture/
- `enum ColorSpace { Linear, sRGB }`
- `enum FilterMode { Point, Bilinear, Trilinear }`
- `enum WrapMode { Repeat, Clamp, Mirror, MirrorOnce }`

### ViewModels/
- `class EditTextureViewModel` —— Edit 弹窗 VM
- `class ExportBatchOptionsViewModel` —— 批量导出选项 VM

### Views/
- `EditTextureView.axaml(.cs)`
- `ExportBatchOptionsView.axaml(.cs)`

---

## 2. AudioPlugin/

### `enum CompressionFormat`
- 值：`PCM`, `Vorbis`, `ADPCM`, `MP3`, `VAG`, `HEVAG`, `XMA`, `AAC`, `GCADPCM`, `ATRAC9`

### `class ExportAudioOption : IUavPluginOption`
- **`SupportsSelection`**：`mode == Export && all AudioClip`
- **`Execute`**：
  - 取 `m_Name`/`m_CompressionFormat`/`m_Resource.m_Source/Offset/Size`
  - 从 bundle/disk 取字节
  - `FsbLoader.TryLoadFsbFromByteArray`
  - `RebuildAsStandardFileFormat(out bytes, out ext)`
  - `File.WriteAllBytes`
- **`BatchExport(Workspace, IUavPluginFunctions, List<AssetInst>)`**：
  - 弹保存对话框
  - 遍历每个 asset

依赖：Fmod5Sharp 3.0.1

---

## 3. FontPlugin/

### `class FontHelper`
- `static AssetTypeValueField GetByteArrayFont(Workspace ws, AssetContainer font)` (推测叫法)
- `static bool IsDataOtf(byte[] byteData)` —— OTF magic

### `class ExportFontOption : IUavPluginOption`
- **`Execute`**：
  - 弹保存对话框
  - 遍历 Font asset：取 `m_FontData.Array`
  - 判断 OTF/TTF → 写出

### `class ImportFontOption : IUavPluginOption`
- **`Execute`**：
  - 弹打开对话框
  - 替换 `m_FontData.Array`
  - 构造 Replacer → Workspace.AddReplacer

---

## 4. TextAssetPlugin/

### `class ExportTextAssetPlugin : IUavPluginOption`
- **`Execute`**：
  - 弹保存对话框（filter 按 Unity container 扩展名）
  - 写出 `m_Script` 字节

### `class ImportTextAssetPlugin : IUavPluginOption`
- 类似

### `class TextAssetPreviewer : IUavPluginPreviewer`
- 对 TextAsset 返回 Text
- 通过 `SetPreviewText` 在 PluginPreviewer 显示

---

## 5. MeshPlugin/

### `class MeshPreviewer : IUavPluginPreviewer`
- **`SupportsPreview(Workspace, AssetInst)`**：
  - 若是 GameObject → 检查 m_Components 找 MeshFilter
  - 若是 Mesh asset → 返回 Mesh
- **`OnPreview(AssetInst asset, IUavPluginPreviewerFunctions funcs)`**：
  - 构造 `MeshObj`（从 Mesh asset 的 m_Vertices / m_Indices / m_Channels）
  - `funcs.SetPreviewMesh(meshObj)`
- **`Initialize(Workspace, IUavPluginPreviewerFunctions)`**：初始化

依赖：Silk.NET.OpenGL 2.22.0（在 PluginPreviewer.Desktop 中渲染）

---

## 关键调用栈

```
[Texture Export 单个]
  → ExportTextureOption.Execute
    → funcs.ShowSaveFileDialog
    → TextureLoader.LoadTexture
      → AssetRipper.TextureDecoder.Decode
      → 颜色转换 + flip
    → SaveAsPng/SaveAsTga
```

```
[Audio Export]
  → ExportAudioOption.Execute
    → funcs.ShowSaveFileDialog
    → FsbLoader.TryLoadFsbFromByteArray
    → samples[0].RebuildAsStandardFileFormat
    → File.WriteAllBytes
```

```
[Mesh Preview]
  → MeshPreviewer.SupportsPreview
  → MeshPreviewer.OnPreview
    → new MeshObj.BuildFromBaseField
    → funcs.SetPreviewMesh
      → PluginPreviewer 进程（IPC）
      → Silk.NET.OpenGL 渲染
```

```
[字体导入]
  → ImportFontOption.Execute
    → funcs.ShowOpenFileDialog
    → File.ReadAllBytes
    → baseField["m_FontData.Array"].AsByteArray = bytes
    → WriteToByteArray → AssetsReplacer → workspace.AddReplacer
```