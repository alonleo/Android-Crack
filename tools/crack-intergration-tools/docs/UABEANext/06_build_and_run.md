# 06 · UABEANext 编译 / 运行 / 插件加载

## 6.1 编译

### 6.1.1 主项目

```bash
cd UABEANext
dotnet restore  # 首次需要还原 AssetsTools.NET 子模块
dotnet build UABEANext4/UABEANext4.csproj -c Release
dotnet build UABEANext4.Desktop/UABEANext4.Desktop.csproj -c Release
```

产物：`UABEANext4/bin/Release/net8.0/UABEANext4.Desktop.exe`

### 6.1.2 插件项目

```bash
for proj in TexturePlugin AudioPlugin FontPlugin MeshPlugin TextAssetPlugin; do
  dotnet build $proj/$proj.csproj -c Release
done
```

`EnableDynamicLoading=true` 在每个插件 csproj 中，使插件 DLL 可独立加载。

### 6.1.3 独立预览器

```bash
dotnet build PluginPreviewer/PluginPreviewer.csproj -c Release
dotnet build PluginPreviewer.Desktop/PluginPreviewer.Desktop.csproj -c Release
```

产物：`PluginPreviewer.Desktop.exe`，独立进程用于显示 3D mesh 预览。

### 6.1.4 AssetsTools.NET 子模块

```bash
git submodule update --init --recursive
```

需要拉取 `Libraries/AssetsTools.NET/`（包含 AssetsTools.NET, AssetsTools.NET.Cpp2IL, AssetsTools.NET.MonoCecil, AssetsTools.NET.Texture 子项目）。

### 6.1.5 原生依赖

| RID | native 路径 |
|---|---|
| win-x64 | `NativeLibs/win-x64/{textureencoder.dll,cuttlefish.dll,PVRTexLib.dll}` |
| linux-x64 | `NativeLibs/linux-x64/{libtextureencoder.so,libcuttlefish.so.2.10,libPVRTexLib.so}` |

MSBuild target `BuildNativeAndSetConfig` 在插件 csproj 中触发拷贝到 `runtimes/<rid>/native/`。

## 6.2 运行

### 6.2.1 GUI

```bash
cd UABEANext/UABEANext4.Desktop/bin/Release/net8.0
./UABEANext4.Desktop.exe        # Windows
# 或
dotnet UABEANext4.Desktop.dll
```

### 6.2.2 Crash 处理

`Program.cs` 中：
- 注册 `AppDomain.UnhandledException` 写 `uabeacrash.log`
- 没有 Windows mshta 弹窗（与 UABEA 不同）

## 6.3 插件加载

### 6.3.1 部署目录结构

```
UABEANext4.Desktop/
└── bin/Release/net8.0/
    ├── UABEANext4.Desktop.exe
    ├── UABEANext4.dll               # 主库
    ├── UABEANext4.Desktop.dll
    ├── AssetsTools.NET*.dll
    ├── CommunityToolkit.Mvvm*.dll
    ├── Dock.Avalonia*.dll
    ├── ...
    ├── classdata.tpk
    ├── plugins/                     # 插件目录
    │   ├── TexturePlugin.dll
    │   ├── AudioPlugin.dll
    │   ├── FontPlugin.dll
    │   ├── MeshPlugin.dll
    │   └── TextAssetPlugin.dll
    └── runtimes/                    # 原生依赖
        └── win-x64/native/
            ├── textureencoder.dll
            ├── cuttlefish.dll
            └── PVRTexLib.dll
```

### 6.3.2 自定义插件

```csharp
// MyPlugin.cs
public class MyOption : IUavPluginOption
{
    public string Name => "My Action";
    public string Description => "Does something";
    public UavPluginMode Options => UavPluginMode.Import | UavPluginMode.Export;
    
    public bool SupportsSelection(Workspace workspace, UavPluginMode mode, 
        List<AssetInst> selection)
    {
        return mode == UavPluginMode.Export 
            && selection.All(a => a.Type == (int)AssetClassID.Texture2D);
    }
    
    public async Task<bool> Execute(Workspace workspace, IUavPluginFunctions funcs,
        UavPluginMode mode, List<AssetInst> selection)
    {
        var file = await funcs.ShowSaveFileDialog(new FilePickerSaveOptions
        {
            Title = "Save",
            FileTypeChoices = new[] { new FilePickerFileType("PNG") { Patterns = new[] { "*.png" } } }
        });
        if (file == null) return false;
        // your work
        return true;
    }
}

// 自定义 Previewer
public class MyPreviewer : IUavPluginPreviewer
{
    public string Name => "My Previewer";
    public string Description => "Preview MyType";
    public UavPluginPreviewerType SupportsPreview(Workspace workspace, AssetInst asset)
    {
        if (asset.Type == (int)AssetClassID.MyType)
            return UavPluginPreviewerType.Image;  // or Text or Mesh
        return UavPluginPreviewerType.None;
    }
}
```

编译后放 `<exe-dir>/plugins/MyPlugin.dll`，重启 UABEANext。

### 6.3.3 插件隔离性（与 UABEA 的关键区别）

UABEANext 使用 `AssemblyLoadContext`：

```csharp
// PluginLoadContext.cs
public class PluginLoadContext : AssemblyLoadContext
{
    private readonly AssemblyDependencyResolver _resolver;
    
    public PluginLoadContext(string pluginPath) : base(isCollectible: true)
    {
        _resolver = new AssemblyDependencyResolver(pluginPath);
    }
    
    protected override Assembly? Load(AssemblyName assemblyName)
    {
        var path = _resolver.ResolveAssemblyToPath(assemblyName);
        return path != null ? LoadFromAssemblyPath(path) : null;
    }
    
    protected override IntPtr LoadUnmanagedDll(string unmanagedDllName)
    {
        var path = _resolver.ResolveUnmanagedDllToPath(unmanagedDllName);
        return path != null ? LoadUnmanagedDllFromPath(path) : IntPtr.Zero;
    }
}
```

优势：
- 不同插件可加载不同版本的 AssetsTools.NET（隔离依赖解析）
- 卸载时整个 ALC 可以 GC（`isCollectible: true`）
- 原生 DLL 也隔离（每个插件独立 native 解析路径）

## 6.4 运行时依赖

| 包 | 版本 |
|---|---|
| AssetRipper.TextureDecoder | 2.1.1 |
| Avalonia | 11.3.8 |
| Avalonia.AvaloniaEdit | 11.3.8 |
| Avalonia.Controls.DataGrid | 11.3.8 |
| Avalonia.Skia | 11.3.8 |
| Avalonia.Themes.Fluent | 11.3.8 |
| Avalonia.Fonts.Inter | 11.3.8 |
| Avalonia.Themes.Simple | 11.3.8 |
| AvaloniaEdit.TextMate | 11.3.8 |
| Dock.Avalonia | 11.3.6.5 |
| Dock.Avalonia.Themes.Simple | 11.3.6.5 |
| Dock.Model | 11.3.6.5 |
| Dock.Model.Mvvm | 11.3.6.5 |
| CommunityToolkit.Mvvm | 8.4.0 |
| DynamicData | 9.4.1 |
| Microsoft.Extensions.DependencyInjection | 9.0.10 |
| Mono.Cecil | 0.11.3 |
| Newtonsoft.Json | 13.0.3 |
| Samboy063.LibCpp2IL | 2022.1.0-pre-release.21 |
| Silk.NET.OpenGL | 2.22.0 |
| StbImageSharp | 2.30.15 |
| StbImageWriteSharp | 1.16.7 |

AudioPlugin:
- Fmod5Sharp 3.0.1

Vendored:
- AssetsTools.NET（submodule）

## 6.5 配置文件

`<exe-dir>/config.json`：

```json
{
  "Theme": "SimpleDark",
  "ListingNameLength": 80,
  "UseManagedOverIl2cpp": false,
  "ExportImportJustNames": false
}
```

| 字段 | 含义 | 默认 |
|---|---|---|
| `Theme` | SimpleDark / SimpleLight | "SimpleDark" |
| `ListingNameLength` | asset 名截断长度 | 80 |
| `UseManagedOverIl2cpp` | MonoBehaviour 恢复优先用 Managed | false |
| `ExportImportJustNames` | 批量导出是否只用文件名 | false |

## 6.6 classdata.tpk

- 与 UABEA 相同
- 通过 `Manager.LoadClassDatabaseFromPackage(version)` 自动按 Unity version 下载/加载
- 也可放 `<exe-dir>/classdata.tpk` 由 `Workspace()` 构造函数加载

## 6.7 调试技巧

1. **Dock 布局丢失**：检查 `DockSimpleThemeEdit.cs` 是否包含所有工具
2. **插件未显示**：检查 `plugins/` 子目录，确认 DLL 有 `[EnableDynamicLoading]`
3. **Mesh 不显示**：检查 `PluginPreviewer.Desktop.exe` 是否独立启动
4. **类型树缺失字段**：检查 `classdata.tpk` 版本与文件 Unity version 匹配

## 6.8 PluginPreviewer 进程

`PluginPreviewer.Desktop` 是**独立 Avalonia 应用**，用于渲染插件提供的预览（如 MeshPreviewer）：

```mermaid
flowchart LR
  Main[UABEANext4.Desktop<br/>主进程] -->|IPC| PP[PluginPreviewer.Desktop<br/>独立进程]
  PP -->|open file| Main
  PP --> Silk[Silk.NET.OpenGL<br/>窗口内渲染]
```

通信方式（推测）：
- 命名管道（Named Pipe）
- 或 stdin/stdout JSON
- 或共享文件

实际协议需要查 `PluginPreviewer.Views.MainView.axaml.cs` 内部实现。