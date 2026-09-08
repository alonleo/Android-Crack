# 08 · Logic 层详细说明

涉及文件：
- `UABEAvalonia/Logic/AssetImportExport.cs` (719 LoC)
- `UABEAvalonia/Logic/Emip.cs` (230 LoC)
- `UABEAvalonia/Logic/FileTypeDetector.cs` (68 LoC)
- `UABEAvalonia/Logic/AssetBundleUtil.cs` (20 LoC)

---

## 8.1 AssetImportExport.cs

### `AssetImportExport.DumpRawAsset(FileStream wfs, AssetsFileReader reader, long position, uint size)`
- **签名**：`public void DumpRawAsset(FileStream wfs, AssetsFileReader reader, long position, uint size)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:20`
- **可见性**：public
- **算法**：4KB buffer 循环读取 `reader.BaseStream`
- **被调用**：`InfoWindow.BatchExportRaw / SingleExportRaw` (`InfoWindow.axaml.cs:649, 678`)

### `AssetImportExport.DumpTextAsset(StreamWriter sw, AssetTypeValueField baseField)`
- **签名**：`public void DumpTextAsset(StreamWriter sw, AssetTypeValueField baseField)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:34`
- **可见性**：public
- **副作用**：写入 sw 字段缓存
- **调用了**：`RecurseTextDump`
- **被调用**：`InfoWindow.BatchExportDump / SingleExportDump` (`InfoWindow.axaml.cs:709, 754`)

### `AssetImportExport.RecurseTextDump(AssetTypeValueField field, int depth)`
- **签名**：`private void RecurseTextDump(AssetTypeValueField field, int depth)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:40`
- **可见性**：private
- **算法**：
  - 模板 → `IsAligned` 取 0/1，写入首字符
  - `IsArray`：先写 size 子字段，然后 `[i]` + 子字段
  - `ByteArray` 类型：每个字节独立一行
  - 叶子：写 `typeName fieldName = value`
  - `ManagedReferencesRegistry`：特殊格式 v1/v2
- **副作用**：输出 sw.WriteLine
- **调用了**：`TextDumpEscapeString`

### `AssetImportExport.DumpJsonAsset(StreamWriter sw, AssetTypeValueField baseField)`
- **签名**：`public void DumpJsonAsset(StreamWriter sw, AssetTypeValueField baseField)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:179`
- **可见性**：public
- **调用了**：`RecurseJsonDump`

### `AssetImportExport.RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor)`
- **签名**：`private JToken RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:186`
- **可见性**：private
- **返回值**：`JToken`（JArray/JObject）

### `AssetImportExport.ImportRawAsset(FileStream fs)`
- **签名**：`public byte[] ImportRawAsset(FileStream fs)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:319`
- **可见性**：public
- **返回值**：完整原始字节
- **被调用**：`InfoWindow.BatchImportRaw / SingleImportRaw` (`InfoWindow.axaml.cs:798, 835`)

### `AssetImportExport.ImportTextAsset(StreamReader sr, out string? exceptionMessage)`
- **签名**：`public byte[]? ImportTextAsset(StreamReader sr, out string? exceptionMessage)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:328`
- **可见性**：public
- **算法**：创建 MemoryStream + AssetsFileWriter，调 `ImportTextAssetLoop`
- **抛出**：捕获并写入 exceptionMessage（不重抛）
- **被调用**：`InfoWindow.BatchImportDump / SingleImportDump` (`InfoWindow.axaml.cs:865, 931`)

### `AssetImportExport.ImportTextAssetLoop()`
- **签名**：`private void ImportTextAssetLoop()`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:349`
- **可见性**：private
- **算法**：
  - `alignStack` 追踪当前嵌套深度对齐状态
  - 每行：缩进 → `thisDepth`，`[` 开头跳过（数组索引）
  - `thisDepth < alignStack.Count` 时 pop 触发 `aw.Align()`
  - 否则解析 align 标记 + 类型名 + `= value` 写值；否则 push 对齐
  - 18 种类型分支（int, float, bool, SInt64, string, UInt8, ...）
- **调用了**：`aw.Write`, `aw.Align`, `StartsWithSpace`, `UnescapeDumpString`

### `AssetImportExport.ImportJsonAsset(AssetTypeTemplateField tempField, StreamReader sr, out string? exceptionMessage)`
- **签名**：`public byte[]? ImportJsonAsset(AssetTypeTemplateField tempField, StreamReader sr, out string? exceptionMessage)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:487`
- **可见性**：public
- **调用了**：`RecurseJsonImport`

### `AssetImportExport.RecurseJsonImport(AssetTypeTemplateField tempField, JToken token)`
- **签名**：`private void RecurseJsonImport(AssetTypeTemplateField tempField, JToken token)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:512`
- **可见性**：private
- **副作用**：写 AssetsFileWriter；ManagedReferencesRegistry 抛 `NotImplementedException`

### `AssetImportExport.StartsWithSpace(string str, string value)`
- **签名**：`private bool StartsWithSpace(string str, string value)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:650`
- **可见性**：private

### `AssetImportExport.UnescapeDumpString(string str)` / `TextDumpEscapeString(string str)`
- **签名**：`private string UnescapeDumpString(string str)` / `private string TextDumpEscapeString(string str)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:655, 691`
- **可见性**：private
- **算法**：转义 `\\` `\r` `\n`

### `AssetImportExport.CreateAssetReplacer(AssetContainer, byte[])`
- **签名**：`public static AssetsReplacer CreateAssetReplacer(AssetContainer cont, byte[] data)`
- **位置**：`UABEAvalonia/Logic/AssetImportExport.cs:699`
- **可见性**：public static
- **被调用**：InfoWindow.SaveFile 等保存路径

### `AssetImportExport.CreateBundleReplacer` 3 重载
- `(string, bool, byte[])` (`AssetImportExport.cs:704`)
- `(string, bool, Stream, long, long)` (`AssetImportExport.cs:709`)
- `(string, bool, int)` → BundleRemover (`AssetImportExport.cs:714`)

---

## 8.2 Emip.cs

### `InstallerPackageFile.Read(AssetsFileReader reader, bool prefReplacersInMemory)`
- **签名**：`public bool Read(AssetsFileReader reader, bool prefReplacersInMemory = false)`
- **位置**：`UABEAvalonia/Logic/Emip.cs:20`
- **可见性**：public
- **算法**：
  - 4 byte magic "EMIP"
  - `includesCldb` byte
  - `modName/modCreators/modDescription` CountStringInt16
  - 若 includesCldb → ClassDatabaseFile.Read
  - affectedFilesCount + 循环：每个 isBundle, path, replacerCount + 循环 `ParseReplacer`
- **返回值**：`bool`（magic 是否匹配）
- **被调用**：`CommandLineHandler.ApplyEmip` (`CommandLineHandler.cs:252`)

### `InstallerPackageFile.Write(AssetsFileWriter writer)`
- **签名**：`public void Write(AssetsFileWriter writer)`
- **位置**：`UABEAvalonia/Logic/Emip.cs:75`
- **可见性**：public
- **算法**：逆 Read 流程
- **副作用**：每个 replacer 调 `repObj.WriteReplacer(writer)`

### `InstallerPackageFile.ParseReplacer(AssetsFileReader, bool prefReplacersInMemory)`
- **签名**：`private static object ParseReplacer(AssetsFileReader reader, bool prefReplacersInMemory)`
- **位置**：`UABEAvalonia/Logic/Emip.cs:116`
- **可见性**：private static
- **算法**：
  - `replacerType` (int16) + `fileType` (byte)
  - `fileType == 0` (BundleReplacer)：oldName/newName/hasSerializedData/replacerCount + 递归读 AssetsReplacer
    - `replacerType == 4` → `BundleReplacerFromAssets`
  - `fileType == 1` (AssetsReplacer)：unknown01/fileId/pathId/classId/monoScriptIndex/preloadDeps
    - `replacerType == 0` → `AssetsRemover`
    - `replacerType == 2` → `AssetsReplacerFromMemory` 或 `AssetsReplacerFromStream`
- **抛出**：`NotSupportedException("flag1 set")` 或 `NotSupportedException("unknown replacer")`
- **被调用**：Read 内部

### `InstallerPackageAssetsDesc` 类
- 字段：`isBundle`, `path`, `List<object> replacers`
- 无方法

---

## 8.3 FileTypeDetector.cs

### `FileTypeDetector.DetectFileType(string filePath)`
- **签名**：`public static DetectedFileType DetectFileType(string filePath)`
- **位置**：`UABEAvalonia/Logic/FileTypeDetector.cs:9`
- **可见性**：public static
- **副作用**：开 FileStream 并立即关闭
- **被调用**：`CommandLineHandler.BatchExportBundle / BatchImportBundle`, `MainWindow.OpenFiles`

### `FileTypeDetector.DetectFileType(AssetsFileReader r, long startAddress)`
- **签名**：`public static DetectedFileType DetectFileType(AssetsFileReader r, long startAddress)`
- **位置**：`UABEAvalonia/Logic/FileTypeDetector.cs:18`
- **可见性**：public static
- **算法**：
  - BigEndian = true
  - 长度 < 0x20 → Unknown
  - 读 7 字节 header
  - 在 startAddress + 0x08 读 int32 possibleFormat
  - 在 startAddress + (possibleFormat >= 0x16 ? 0x30 : 0x14) 读版本字符串
  - 用 regex 过滤非版本字符
  - "UnityFS" → BundleFile
  - possibleFormat < 0xFF 且 emptyVersion 空且 fullVersion >= 5 → AssetsFile
- **返回值**：`DetectedFileType`

### `DetectedFileType` enum
- `Unknown = 0`, `AssetsFile`, `BundleFile`

---

## 8.4 AssetBundleUtil.cs

### `AssetBundleUtil.IsBundleDataCompressed(AssetBundleFile bundle)`
- **签名**：`public static bool IsBundleDataCompressed(AssetBundleFile bundle)`
- **位置**：`UABEAvalonia/Logic/AssetBundleUtil.cs:15`
- **可见性**：public static
- **算法**：`bundle.BlockAndDirInfo.BlockInfos.Any(inf => inf.GetCompressionType() != 0)`
- **被调用**：`MainWindow.AskLoadCompressedBundle` (`MainWindow.axaml.cs:814`)

---

## 8.5 关键调用栈

```
[UI ImportDump]
  → InfoWindow.BatchImportDump
    → AssetImportExport.ImportTextAsset
      → ImportTextAssetLoop
    → AssetContainer(cont, baseField) 克隆
    → workspace.AddReplacer
      → ItemUpdated
```

```
[CLI ApplyEmip]
  → InstallerPackageFile.Read
    → ParseReplacer (recursive)
  → DecompressBundle
  → bun.Write (with BundleReplacer list)
  → File.Move (temp → original, original → .bakNNNN)
```

```
[打开文件]
  → FileTypeDetector.DetectFileType (string 或 stream)
  → switch DetectedFileType
    case AssetsFile → am.LoadAssetsFile → AssetWorkspace.LoadAssetsFile
    case BundleFile → am.LoadBundleFile → BundleWorkspace.Reset
```