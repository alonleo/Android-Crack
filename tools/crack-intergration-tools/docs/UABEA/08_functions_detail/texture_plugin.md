# 08 · TexturePlugin 详细说明

涉及文件：
- `TexturePlugin/Program.cs` (33)
- `TexturePlugin/EditTextureOption.cs` (54)
- `TexturePlugin/ExportTextureOption.cs` (186)
- `TexturePlugin/ImportTextureOption.cs` (160)
- `TexturePlugin/TextureEncoderDecoder.cs` (558)
- `TexturePlugin/Texture2DSwitchDeswizzler.cs` (195)
- `TexturePlugin/TextureHelper.cs` (124)
- `TexturePlugin/TextureImportExport.cs` (172)
- `TexturePlugin/PInvoke.cs` (30)
- `TexturePlugin/EditDialog.axaml(.cs)` (258)

---

## 8.1 Program.cs

### `class TexturePlugin : UABEAPlugin`
- **`Init()`** (`TexturePlugin/Program.cs:18`)：构造 `PluginInfo { name = "Texture Import/Export", options = [ImportTextureOption, ExportTextureOption, EditTextureOption] }`

---

## 8.2 TextureHelper.cs

### `static AssetTypeValueField GetByteArrayTexture(AssetWorkspace, AssetContainer)`
- **签名**：`public static AssetTypeValueField GetByteArrayTexture(AssetWorkspace workspace, AssetContainer tex)`
- **位置**：`TexturePlugin/TextureHelper.cs:13`
- **可见性**：public static
- **算法**：
  1. `workspace.GetTemplateField(tex)` → 模板
  2. `image data` 字段标记 `AssetValueType.ByteArray`
  3. `m_PlatformBlob` 子数组标记 ByteArray
  4. `MakeValue(reader, position)`
- **调用了**：`AssetWorkspace.GetTemplateField`, `tempField.MakeValue`
- **被调用**：`ExportTextureOption.SingleExport / BatchExport`, `ImportTextureOption.ExecutePlugin`, `EditTextureOption.ExecutePlugin`

### `static bool GetResSTexture(TextureFile texFile, AssetsFileInstance fileInst)`
- **签名**：`public static bool GetResSTexture(TextureFile texFile, AssetsFileInstance fileInst)`
- **位置**：`TexturePlugin/TextureHelper.cs:32`
- **可见性**：public static
- **算法**：
  - 若 `streamInfo.path` 非空且 `fileInst.parentBundle != null`：
    - 去掉 `archive:/` 前缀，取文件名
    - 在 bundle 的 `DirectoryInfos` 中匹配
    - 从 `reader.Position = info.Offset + streamInfo.offset` 读 `streamInfo.size` 字节
    - 清空 `m_StreamData`
  - 否则直接 return true
- **返回值**：resS 字节是否成功读到 `texFile.pictureData`
- **被调用**：`ExportTextureOption` 两条路径

### `static byte[] GetRawTextureBytes(TextureFile texFile, AssetsFileInstance inst)`
- **签名**：`public static byte[] GetRawTextureBytes(TextureFile texFile, AssetsFileInstance inst)`
- **位置**：`TexturePlugin/TextureHelper.cs:69`
- **可见性**：public static
- **算法**：
  - 若 `streamInfo.size != 0`：
    - 取根目录（去掉 archive:/ 前缀）
    - 拼接完整路径
    - 若文件存在 → 打开读取 streamInfo.size 字节
    - 否则返回 null
  - 否则返回 `texFile.pictureData`
- **被调用**：`ExportTextureOption`

### `static byte[] GetPlatformBlob(AssetTypeValueField texBaseField)`
- **签名**：`public static byte[] GetPlatformBlob(AssetTypeValueField texBaseField)`
- **位置**：`TexturePlugin/TextureHelper.cs:98`
- **可见性**：public static
- **返回值**：m_PlatformBlob.Array 字节，若 IsDummy 则 null

### `static bool IsPo2(int n)`
- **签名**：`public static bool IsPo2(int n)`
- **位置**：`TexturePlugin/TextureHelper.cs:109`
- **可见性**：public static
- **算法**：`n > 0 && (n & (n-1)) == 0`

### `static int GetMaxMipCount(int width, int height)`
- **签名**：`public static int GetMaxMipCount(int width, int height)`
- **位置**：`TexturePlugin/TextureHelper.cs:115`
- **可见性**：public static
- **算法**：`Math.Max(log2(width)+1, log2(height)+1)`

---

## 8.3 TextureImportExport.cs

### `static byte[] Import(string imagePath, TextureFormat format, out int width, out int height, ref int mips, uint platform, byte[] platformBlob)`
- **签名**：`public static byte[] Import(string imagePath, TextureFormat format, out int width, out int height, ref int mips, uint platform = 0, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:12`
- **可见性**：public static
- **算法**：加载图片，调另一个重载

### `static byte[] Import(Image<Rgba32> image, TextureFormat format, out int, out int, ref int, uint, byte[])`
- **签名**：`public static byte[] Import(Image<Rgba32> image, TextureFormat format, out int width, out int height, ref int mips, uint platform = 0, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:21`
- **可见性**：public static
- **算法**：
  - Switch 平台 (38) 且 platformBlob 非空 → `ImportSwitch`
  - 否则：
    - 不能 mipmap（非方形或非 Po2）→ `mips = 1`
    - 垂直翻转
    - `TextureEncoderDecoder.Encode(image, w, h, fmt, 5, mips)`
- **被调用**：插件 `ImportTextureOption.ImportTextures` (`ImportTextureOption.cs:70`)

### `static byte[] ImportSwitch(Image<Rgba32> image, TextureFormat, out int, out int, byte[])`
- **签名**：`private static byte[] ImportSwitch(Image<Rgba32> image, TextureFormat format, out int width, out int height, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:47`
- **可见性**：private static
- **算法**：
  1. 修正 RGB24→RGBA32、BGR24→BGRA32
  2. `Texture2DSwitchDeswizzler.GetSwitchGobsPerBlock` + `TextureFormatToBlockSize` + `GetPaddedTextureSize`
  3. `Resize(BoxPad, BottomLeft, Fuchsia)` → swizzle → encode
- **调用了**：`Texture2DSwitchDeswizzler.*`

### `static bool Export(byte[] encData, string imagePath, int w, int h, TextureFormat format, uint platform, byte[] platformBlob)`
- **签名**：`public static bool Export(byte[] encData, string imagePath, int width, int height, TextureFormat format, uint platform = 0, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:79`
- **可见性**：public static
- **返回值**：是否成功写出

### `static Image<Rgba32> Export(byte[] encData, int w, int h, TextureFormat format, uint platform, byte[] platformBlob)`
- **签名**：`public static Image<Rgba32> Export(byte[] encData, int width, int height, TextureFormat format, uint platform = 0, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:91`
- **可见性**：public static
- **算法**：Switch → `ExportSwitch`；否则 → `Decode` + 垂直翻转

### `static Image<Rgba32> ExportSwitch(byte[] encData, int w, int h, TextureFormat, byte[])`
- **签名**：`private static Image<Rgba32> ExportSwitch(byte[] encData, int width, int height, TextureFormat format, byte[] platformBlob = null)`
- **位置**：`TexturePlugin/TextureImportExport.cs:112`
- **可见性**：private static
- **算法**：与 ImportSwitch 对称

### `static void SaveImageAtPath(Image<Rgba32> image, string path)`
- **签名**：`public static void SaveImageAtPath(Image<Rgba32> image, string path)`
- **位置**：`TexturePlugin/TextureImportExport.cs:143`
- **可见性**：public static
- **算法**：扩展名 .png / .tga 分支

### `static TextureFormat GetCorrectedSwitchTextureFormat(TextureFormat)`
- **签名**：`private static TextureFormat GetCorrectedSwitchTextureFormat(TextureFormat format)`
- **位置**：`TexturePlugin/TextureImportExport.cs:158`
- **可见性**：private static

---

## 8.4 Texture2DSwitchDeswizzler.cs

Nintendo Switch 平台使用 GOB swizzle 模式，4×8 block layout，调用之前需 deswizzle。

### 常量
- `GOB_X_BLOCK_COUNT = 4`
- `GOB_Y_BLOCK_COUNT = 8`
- `BLOCKS_IN_GOB = 32`

### `static void CopyBlock(Image<Rgba32> src, Image<Rgba32> dst, int sbx, int sby, int dbx, int dby, int bsW, int bsH)`
- **签名**：`private static void CopyBlock(Image<Rgba32> srcImage, Image<Rgba32> dstImage, int sbx, int sby, int dbx, int dby, int blockSizeW, int blockSizeH)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:38`
- **可见性**：private static
- **算法**：逐像素拷贝

### `static int CeilDivide(int a, int b)`
- **签名**：`private static int CeilDivide(int a, int b)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:49`
- **可见性**：private static

### `internal static Image<Rgba32> SwitchUnswizzle(Image<Rgba32> srcImage, Size blockSize, int gobsPerBlock)`
- **签名**：`internal static Image<Rgba32> SwitchUnswizzle(Image<Rgba32> srcImage, Size blockSize, int gobsPerBlock)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:54`
- **可见性**：internal static
- **算法**：四重循环（gobRow, gobCol, gobIndexInSet, blockIndexInGob）按 `gobX = ((l>>3)&0b10) | ((l>>1)&0b1)`, `gobY = ((l>>1)&0b110) | (l&0b1)` 计算目标

### `internal static Image<Rgba32> SwitchSwizzle(Image<Rgba32> srcImage, Size blockSize, int gobsPerBlock)`
- **签名**：`internal static Image<Rgba32> SwitchSwizzle(Image<Rgba32> srcImage, Size blockSize, int gobsPerBlock)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:98`
- **可见性**：internal static
- **算法**：Unswizzle 的逆过程

### `internal static Size TextureFormatToBlockSize(TextureFormat m_TextureFormat)`
- **签名**：`internal static Size TextureFormatToBlockSize(TextureFormat m_TextureFormat)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:143`
- **可见性**：internal static
- **算法**：switch 27 种 TextureFormat → `Size`（包括 Alpha8, ARGB4444, RGBA32, DXT1/5, BC4/5/6H/7, ASTC 4x4..12x12）

### `internal static Size GetPaddedTextureSize(int width, int height, int blockWidth, int blockHeight, int gobsPerBlock)`
- **签名**：`internal static Size GetPaddedTextureSize(int width, int height, int blockWidth, int blockHeight, int gobsPerBlock)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:180`
- **可见性**：internal static
- **算法**：向上取整到 `blockWidth * GOB_X_BLOCK_COUNT` 倍数 + `blockHeight * GOB_Y_BLOCK_COUNT * gobsPerBlock` 倍数

### `internal static int GetSwitchGobsPerBlock(byte[] platformBlob)`
- **签名**：`internal static int GetSwitchGobsPerBlock(byte[] platformBlob)`
- **位置**：`TexturePlugin/Texture2DSwitchDeswizzler.cs:187`
- **可见性**：internal static
- **算法**：`1 << BitConverter.ToInt32(platformBlob, 8)`

---

## 8.5 TextureEncoderDecoder.cs

### `static int RGBAToFormatByteSize(TextureFormat format, int width, int height)`
- **签名**：`public static int RGBAToFormatByteSize(TextureFormat format, int width, int height)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:12`
- **可见性**：public static
- **算法**：switch format → 算字节数（rgba32 → w*h*4，BC1/4 → blockCount*8，BC5/6/7 → blockCount*16，ASTC 4x4 → blockCount*16，PVRTC 2bpp → blockCount*8）

### `static byte[] DecodeAssetRipperTex(byte[] data, int w, int h, TextureFormat format)`
- **签名**：`private static byte[] DecodeAssetRipperTex(byte[] data, int width, int height, TextureFormat format)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:153`
- **可见性**：private static
- **算法**：`TextureFile.DecodeManaged`，再 BGRA → RGBA 交换

### `static byte[] DecodePVRTexLib(byte[] data, int w, int h, TextureFormat format)`
- **签名**：`private static byte[] DecodePVRTexLib(byte[] data, int width, int height, TextureFormat format)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:166`
- **可见性**：private static
- **算法**：P/Invoke `DecodeByPVRTexLib`

### `static byte[] DecodeCrunch(byte[] data, int w, int h, TextureFormat format)`
- **签名**：`private static byte[] DecodeCrunch(byte[] data, int width, int height, TextureFormat format)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:194`
- **可见性**：private static
- **算法**：P/Invoke `DecodeByCrunchUnity`

### `static byte[] EncodeISPC(...)` / `EncodePVRTexLib(...)` / `EncodeCrunch(...)`
- 位置：`TexturePlugin/TextureEncoderDecoder.cs:214, 252, 290`
- 全部 private static
- Crunch 编码使用 ver=1（兼容旧版 Unity）

### `static byte[] Decode(byte[] data, int w, int h, TextureFormat format)`
- **签名**：`public static byte[] Decode(byte[] data, int width, int height, TextureFormat format)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:339`
- **可见性**：public static
- **算法**：switch format → Crunch 先解压再选 PVRTexLib 或 AssetRipper → 一般 PVR → AssetRipper

### `static byte[] EncodeMip(byte[] data, int w, int h, TextureFormat format, int quality, int mips)`
- **签名**：`public static byte[] EncodeMip(byte[] data, int width, int height, TextureFormat format, int quality, int mips = 1)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:438`
- **可见性**：public static
- **算法**：Crunch formats → `EncodeCrunch`；PVR formats → `EncodePVRTexLib`；DXT/BC7 → `EncodeISPC`；其余 → null

### `static byte[] Encode(Image<Rgba32> image, int w, int h, TextureFormat format, int quality, int mips)`
- **签名**：`public static byte[] Encode(SixLabors.ImageSharp.Image<Rgba32> image, int width, int height, TextureFormat format, int quality = 5, int mips = 1)`
- **位置**：`TexturePlugin/TextureEncoderDecoder.cs:519`
- **可见性**：public static
- **算法**：Crunch 直接 `EncodeMip`；否则循环 mip 链 resize 半 + 编码

---

## 8.6 PInvoke.cs

6 个 C 入口：

| # | 签名 | 位置 |
|---|---|---|
| 1 | `[DllImport("textoolwrap")] static extern uint DecodeByCrunchUnity(IntPtr data, IntPtr buf, int mode, uint width, uint height, uint byteSize)` | `PInvoke.cs:13` |
| 2 | `[DllImport("textoolwrap")] static extern uint DecodeByPVRTexLib(IntPtr data, IntPtr buf, int mode, uint width, uint height)` | `PInvoke.cs:16` |
| 3 | `[DllImport("textoolwrap")] static extern uint EncodeByCrunchUnity(IntPtr data, ref int checkoutId, int mode, int level, uint width, uint height, uint ver, int mips)` | `PInvoke.cs:19` |
| 4 | `[DllImport("textoolwrap")] static extern bool PickUpAndFree(IntPtr outBuf, uint size, int id)` | `PInvoke.cs:22` |
| 5 | `[DllImport("textoolwrap")] static extern uint EncodeByPVRTexLib(IntPtr data, IntPtr buf, int mode, int level, uint width, uint height)` | `PInvoke.cs:25` |
| 6 | `[DllImport("textoolwrap")] static extern uint EncodeByISPC(IntPtr data, IntPtr buf, int mode, int level, uint width, uint height)` | `PInvoke.cs:28` |

所有可见性为 public static extern。

---

## 8.7 ExportTextureOption.cs

### `bool SelectionValidForPlugin(AssetsManager, UABEAPluginAction, List<AssetContainer>, out string)`
- **签名**：`public bool SelectionValidForPlugin(AssetsManager am, UABEAPluginAction action, List<AssetContainer> selection, out string name)`
- **位置**：`TexturePlugin/ExportTextureOption.cs:18`
- **可见性**：public
- **算法**：`action == Export` 且全部 `ClassId == Texture2D`

### `Task<bool> ExecutePlugin(Window, AssetWorkspace, List<AssetContainer>)`
- **签名**：`public async Task<bool> ExecutePlugin(Window win, AssetWorkspace workspace, List<AssetContainer> selection)`
- **位置**：`TexturePlugin/ExportTextureOption.cs:36`
- **可见性**：public

### `Task<bool> BatchExport(Window, AssetWorkspace, List<AssetContainer>)`
- **签名**：`public async Task<bool> BatchExport(Window win, AssetWorkspace workspace, List<AssetContainer> selection)`
- **位置**：`TexturePlugin/ExportTextureOption.cs:44`
- **可见性**：public
- **算法**：
  1. 全部 cont 替换为带 ByteArray 的 `AssetContainer`
  2. `ExportBatchChooseTypeDialog` 让用户选 png/tga/jpg/bmp
  3. 打开文件夹
  4. 对每个 cont：`TextureFile.ReadTextureFile` → 取 `m_Name` → `GetResSTexture` → `GetRawTextureBytes` → `GetPlatformBlob` → `TextureImportExport.Export`
  5. 错误累积，弹 MessageBoxUtil.ShowDialog

### `Task<bool> SingleExport(Window, AssetWorkspace, List<AssetContainer>)`
- **签名**：`public async Task<bool> SingleExport(Window win, AssetWorkspace workspace, List<AssetContainer> selection)`
- **位置**：`TexturePlugin/ExportTextureOption.cs:123`
- **可见性**：public

---

## 8.8 ImportTextureOption.cs

### `bool SelectionValidForPlugin` / `Task<bool> ExecutePlugin`
- 位置：`TexturePlugin/ImportTextureOption.cs:21, 109`
- **ExecutePlugin 算法**：
  1. 替换 cont 为 ByteArray 版
  2. 打开文件夹
  3. `ImportBatch` 对话框收集映射
  4. 调 `ImportTextures`

### `Task<bool> ImportTextures(Window, List<ImportBatchInfo>)`
- **签名**：`private async Task<bool> ImportTextures(Window win, List<ImportBatchInfo> batchInfos)`
- **位置**：`TexturePlugin/ImportTextureOption.cs:39`
- **可见性**：private
- **算法**：
  1. 对每个 batchInfo：load image → 检查尺寸是否匹配原 m_Width/m_Height
  2. 计算 mips
  3. `TextureImportExport.Import` 编码
  4. 修改 baseField：清空 m_StreamData；m_MipCount/m_Width/m_Height/m_CompleteImageSize；image_data.AsByteArray = encBytes
  5. 构造 `AssetsReplacerFromMemory` → `workspace.AddReplacer`

---

## 8.9 EditTextureOption.cs

### `Task<bool> ExecutePlugin`
- **位置**：`TexturePlugin/EditTextureOption.cs:33`
- **算法**：
  1. `TextureHelper.GetByteArrayTexture`
  2. `TextureFile.ReadTextureFile`
  3. `new EditDialog(name, texFile, baseField, fileInst)`
  4. 若 saved → `baseField.WriteToByteArray()` → `AssetsReplacerFromMemory` → `workspace.AddReplacer`

---

## 8.10 EditDialog.axaml(.cs) (258 LoC)

Avalonia 窗口 UI，包含：
- 缩放比例 ComboBox
- mipmap 复选框
- 重新编码按钮
- 保存 / 取消按钮
- AvaloniaEdit 控件 + 字节 Hex 编辑器
- Preview Image 显示当前 texture

详细字段与回调见 .axaml。

---

## 8.11 关键调用栈

```
[导出] SingleExport
  → TextureHelper.GetByteArrayTexture
  → TextureFile.ReadTextureFile
  → GetResSTexture / GetRawTextureBytes
  → GetPlatformBlob
  → TextureImportExport.Export
    → 平台 == 38 (Switch) → ExportSwitch → Texture2DSwitchDeswizzler.SwitchUnswizzle
    → Decode (Crunch → DXT/ETC2 → PVR)
    → 垂直翻转
  → SaveImageAtPath
```

```
[导入] ImportTextures
  → Image.Load
  → TextureImportExport.Import
    → 平台 == 38 → ImportSwitch → SwitchSwizzle → Encode
    → EncodeMip (Crunch / PVR / ISPC)
  → 修改 baseField
  → AssetsReplacerFromMemory
  → workspace.AddReplacer
```