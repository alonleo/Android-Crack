# 08 · Program.cs 与 CommandLineHandler.cs 详细说明

## 8.1 Program.cs (`UABEAvalonia/Program.cs`)

### `Program.Main(string[] args)`
- **签名**：`public static void Main(string[] args)`
- **位置**：`UABEAvalonia/Program.cs:21`
- **可见性**：public static
- **参数**：`args` —— 命令行参数
- **返回值**：void
- **副作用**：
  - Windows 下 `AttachConsole(-1)` 接管父终端
  - 注册 `AppDomain.UnhandledException`
  - 若 `args.Length > 0` 则调用 `CommandLineHandler.CLHMain(args)`，否则调用 `BuildAvaloniaApp().StartWithClassicDesktopLifetime(args)`
- **被调用**：CLR 启动入口
- **调用了**：`AttachConsole` (P/Invoke), `UABEAExceptionHandler`, `CommandLineHandler.CLHMain`, `CommandLineHandler.PrintHelp`, `BuildAvaloniaApp`

### `Program.UABEAExceptionHandler(object sender, UnhandledExceptionEventArgs args)`
- **签名**：`public static void UABEAExceptionHandler(object sender, UnhandledExceptionEventArgs args)`
- **位置**：`UABEAvalonia/Program.cs:57`
- **可见性**：public static
- **副作用**：
  - 写 `uabeacrash.log` 到当前目录
  - Windows：`mshta vbscript:Execute(...)` 弹窗
  - Unix：`Console.WriteLine(ex)`
- **调用了**：`File.WriteAllText`, `Process.Start`, `Console.WriteLine`

### `Program.BuildAvaloniaApp()`
- **签名**：`public static AppBuilder BuildAvaloniaApp()`
- **位置**：`UABEAvalonia/Program.cs:79`
- **可见性**：public static
- **返回值**：`AppBuilder`
- **调用了**：`AppBuilder.Configure<App>().UsePlatformDetect().LogToTrace()`

---

## 8.2 CommandLineHandler.cs (`UABEAvalonia/CommandLineHandler.cs`)

### `CommandLineHandler.PrintHelp()`
- **签名**：`public static void PrintHelp()`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:11`
- **可见性**：public static
- **副作用**：`Console.WriteLine` 输出 help
- **被调用**：`Program.Main`（当无 args 时且 usesConsole 为真）
- **调用了**：`Console.WriteLine`

### `CommandLineHandler.GetMainFileName(string[] args)`
- **签名**：`private static string GetMainFileName(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:33`
- **可见性**：private static
- **参数**：`args` —— CLI 参数
- **返回值**：第一个不以 `-` 开头的参数，否则空字符串
- **被调用**：`BatchExportBundle`, `BatchImportBundle`

### `CommandLineHandler.GetFlags(string[] args)`
- **签名**：`private static HashSet<string> GetFlags(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:43`
- **可见性**：private static
- **返回值**：`HashSet<string>` 含所有 `-xxx` 标志
- **被调用**：`BatchExportBundle`, `BatchImportBundle`, `ApplyEmip`

### `CommandLineHandler.DecompressBundle(string file, string? decompFile)`
- **签名**：`private static AssetBundleFile DecompressBundle(string file, string? decompFile)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:54`
- **可见性**：private static
- **参数**：
  - `file` —— bundle 文件路径
  - `decompFile` —— null=解压到内存；否则解压到该路径
- **返回值**：解压后的 `AssetBundleFile`
- **副作用**：可能创建 .decomp 文件
- **调用了**：`AssetBundleFile.Read`, `bun.Unpack`, `bun.Read`
- **被调用**：`BatchExportBundle`, `BatchImportBundle`, `ApplyEmip`

### `CommandLineHandler.GetNextBackup(string affectedFilePath)`
- **签名**：`private static string GetNextBackup(string affectedFilePath)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:86`
- **可见性**：private static
- **参数**：`affectedFilePath` —— 原文件路径
- **返回值**：下一个可用的 `.bakNNNN` 路径，超过 10000 时返回 null
- **副作用**：输出 "Too many backups..." 并返回 null
- **调用了**：`File.Exists`
- **被调用**：`ApplyEmip`（bundle 与 raw assets 两条路径各一次）

### `CommandLineHandler.BatchExportBundle(string[] args)`
- **签名**：`private static void BatchExportBundle(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:101`
- **可见性**：private static
- **副作用**：在目录中创建解压后的 entry 文件
- **算法**：
  1. 取目录路径
  2. 遍历目录下所有文件
  3. 仅处理 `DetectedFileType.BundleFile`
  4. `DecompressBundle(file, decompFile)`
  5. 遍历 `bun.BlockAndDirInfo.DirectoryInfos`，每个 entry → `BundleHelper.LoadAssetDataFromBundle(bun, i)` → `File.WriteAllBytes`
  6. 根据 `-keepnames` 决定文件名
  7. 删除 `.decomp`（除非 `-kd` 或 `-md`）
- **调用了**：`GetMainFileName`, `GetFlags`, `FileTypeDetector.DetectFileType`, `DecompressBundle`, `BundleHelper.LoadAssetDataFromBundle`, `File.WriteAllBytes`, `File.Delete`

### `CommandLineHandler.BatchImportBundle(string[] args)`
- **签名**：`private static void BatchImportBundle(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:156`
- **可见性**：private static
- **副作用**：覆盖原 .bundle 文件
- **算法**：
  1. 取目录路径
  2. 遍历目录下所有文件
  3. 仅处理 `DetectedFileType.BundleFile`
  4. `DecompressBundle(file, decompFile)`
  5. 遍历 `bun.BlockAndDirInfo.DirectoryInfos`，查找 `<bundle>_<name>` 匹配文件 → `BundleReplacerFromStream`
  6. `bun.Write` 到内存 → `File.WriteAllBytes(file, data)`（直接覆盖，无压缩）
  7. 删除 `.decomp`（除非 `-kd` 或 `-md`）
- **调用了**：`GetMainFileName`, `GetFlags`, `FileTypeDetector.DetectFileType`, `DecompressBundle`, `bun.Write`, `File.WriteAllBytes`

### `CommandLineHandler.ApplyEmip(string[] args)`
- **签名**：`private static void ApplyEmip(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:237`
- **可见性**：private static
- **副作用**：原文件被移动为 .bakNNNN，新 .mod 文件被改名为原文件
- **算法**：
  1. 解析 `InstallerPackageFile`（mod 元数据 + affected files + replacers）
  2. 对每个 `affectedFile`：
     - `isBundle`：`DecompressBundle`，收集 `BundleReplacer`（含 `BundleReplacerFromAssets.Init`），`bun.Write(mw, reps, addedTypes)` 到 `.mod`，移动覆盖原文件
     - 否则：`assets.Read`，`assets.Write(mw, 0, reps, addedTypes)` 到 `.mod`，移动覆盖
- **抛出**：`new NotSupportedException("flag1 set")`（极少见）
- **调用了**：`GetFlags`, `File.OpenRead`, `InstallerPackageFile.Read`, `GetNextBackup`, `DecompressBundle`, `BundleHelper.GetDirInfo`, `BundleReplacerFromAssets.Init`, `bun.Write`, `File.Move`

### `CommandLineHandler.CLHMain(string[] args)`
- **签名**：`public static void CLHMain(string[] args)`
- **位置**：`UABEAvalonia/CommandLineHandler.cs:349`
- **可见性**：public static
- **算法**：
  - `args.Length < 2` → `PrintHelp`
  - `args[0] == "batchexportbundle"` → `BatchExportBundle`
  - `args[0] == "batchimportbundle"` → `BatchImportBundle`
  - `args[0] == "applyemip"` → `ApplyEmip`
- **被调用**：`Program.Main`
- **调用了**：`PrintHelp`, `BatchExportBundle`, `BatchImportBundle`, `ApplyEmip`