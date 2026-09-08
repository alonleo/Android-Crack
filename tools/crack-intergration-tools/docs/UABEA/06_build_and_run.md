# 06 · UABEA 编译 / 运行 / CLI / 插件加载

## 6.1 编译

### 6.1.1 GUI 主项目

```bash
cd UABEA
dotnet build UABEAvalonia/UABEAvalonia.csproj -c Release
```

产物：`UABEAvalonia/bin/Release/net8.0/UABEAvalonia.exe`

### 6.1.2 TexturePlugin（含 C++ TexToolWrap）

构建顺序：

1. 用 MSBuild + MSVC 编译 `TexToolWrap/TexToolWrap.vcxproj`（x64 / Win32），产出 `textoolwrap.dll`。
2. 用 dotnet build 编译 `TexturePlugin/TexturePlugin.csproj`，MSBuild target `BuildNativeAndSetConfig` 拷贝 nativo DLL 到 `runtimes/<rid>/native/`。
3. 用 dotnet build 编译 `UABEAvalonia.csproj`，最终把所有插件 DLL 与 native 合并到 `UABEAvalonia/bin/.../plugins/`。

### 6.1.3 其他插件

```bash
dotnet build AudioClipPlugin/AudioClipPlugin.csproj -c Release
dotnet build FontPlugin/FontPlugin.csproj -c Release
dotnet build TextAssetPlugin/TextAssetPlugin.csproj -c Release
```

或一次性：

```bash
dotnet build UABEAvalonia.sln -c Release
```

### 6.1.4 必要原生依赖

| RID | native DLL 位置 |
|---|---|
| win-x64 | `runtimes/win-x64/native/textoolwrap.dll` + `PVRTexLib.dll` + `ispc_texcomp.dll` + `crnlib.dll` |
| linux-x64 | `runtimes/linux-x64/native/libtextoolwrap.so` 等 |
| win-x86 | `runtimes/win-x86/native/...` |
| osx-x64 | `runtimes/osx-x64/native/...` |

这些 native 由 MSBuild target `CopyLibrariesBuild` / `CopyLibrariesPublish` 自动拷贝。

### 6.1.5 编译开关

`UABEAvalonia.csproj`：
- `TargetFramework: net8.0`
- `PublishAot=true`
- `Nullable: enable`
- `LangVersion: latest`
- 包含 `<EnableDynamicLoading>true</EnableDynamicLoading>` 以支持插件

`TexturePlugin.csproj`：
- 通过 `UABEANativeConfig` 引用 `TexToolWrap.dll`

## 6.2 运行

### 6.2.1 GUI

```bash
cd UABEA/UABEAvalonia/bin/Release/net8.0
./UABEAvalonia.exe               # Windows
# 或
dotnet UABEAvalonia.dll          # 跨平台
```

启动后：
1. Avalonia 加载 XAML
2. MainWindow 构造
3. PluginManager 扫描 `<exe-dir>/plugins/`
4. 显示主窗口

### 6.2.2 CLI

UABEAvalonia.exe 直接接子命令：

```bash
UABEAvalonia.exe batchexportbundle <directory> [-keepnames] [-kd] [-fd] [-md]
UABEAvalonia.exe batchimportbundle <directory> [-keepnames] [-kd] [-fd] [-md]
UABEAvalonia.exe applyemip <emip-file> <directory> [-kd] [-fd] [-md]
```

### 6.2.3 标志说明

| Flag | 含义 |
|---|---|
| `-keepnames` | 写出时使用 bundle 内的 entry 名（不带 `<bundle>_` 前缀）。**注意：这样导出的文件无法被 batchimport 回读** |
| `-kd` | 保留 `.decomp` 临时文件（默认删除） |
| `-fd` | 覆盖已存在的 `.decomp` 文件 |
| `-md` | 解压到内存（不写 `.decomp`）。`-kd` 和 `-fd` 在此模式下失效 |

## 6.3 Crash 处理

- `Program.UABEAExceptionHandler` (`Program.cs:57`) 注册到 `AppDomain.UnhandledException`
- 异常对象 → `uabeacrash.log`
- Windows: `mshta vbscript:Execute(...)` 弹窗显示
- Unix: `Console.WriteLine`

## 6.4 插件加载

### 6.4.1 部署目录结构

```
UABEAvalonia/
└── bin/Release/net8.0/
    ├── UABEAvalonia.exe
    ├── UABEAvalonia.dll
    ├── AssetsTools.NET*.dll
    ├── ...
    └── plugins/                       # 插件目录
        ├── TexturePlugin.dll          # 启动时自动加载
        ├── AudioClipPlugin.dll
        ├── FontPlugin.dll
        └── TextAssetPlugin.dll
```

### 6.4.2 自定义插件

开发者写一个实现 `UABEAPlugin` 接口的类库：

```csharp
public class MyPlugin : UABEAPlugin
{
    public PluginInfo Init()
    {
        return new PluginInfo
        {
            name = "My Plugin",
            options = new List<UABEAPluginOption>
            {
                new MyOption()
            }
        };
    }
}

public class MyOption : UABEAPluginOption
{
    public bool SelectionValidForPlugin(AssetsManager am, UABEAPluginAction action,
        List<AssetContainer> selection, out string name)
    {
        name = "My action";
        return action == UABEAPluginAction.Export
            && selection.All(c => c.ClassId == (int)AssetClassID.Texture2D);
    }

    public async Task<bool> ExecutePlugin(Window win, AssetWorkspace workspace,
        List<AssetContainer> selection)
    {
        // your work
        return true;
    }
}
```

编译后把 DLL 放进 `<exe-dir>/plugins/`，重启 UABEA 即可。

### 6.4.3 插件隔离性

⚠️ **注意**：UABEA 使用 `Assembly.LoadFrom`（非 `AssemblyLoadContext`），因此所有插件共享主程序的依赖解析。如果两个插件引用不同版本的 AssetsTools.NET，会按"先加载优先"。

UABEANext 才使用 `PluginLoadContext`（见 UABEANext/03_architecture）。

## 6.5 运行时依赖

| 类型 | 包 | 版本 |
|---|---|---|
| 主 | Avalonia | 11.0.1 |
| 主 | Avalonia.AvaloniaEdit | 11.0.1 |
| 主 | Avalonia.Controls.DataGrid | 11.0.1 |
| 主 | Avalonia.Themes.Fluent | 11.0.1 |
| 主 | AvaloniaEdit.TextMate | 11.0.1 |
| 主 | Newtonsoft.Json | 13.0.3-beta1 |
| 主 | Mono.Cecil | 0.11.4 |
| 主 | Samboy063.LibCpp2IL | 2022.0.7.2 |
| 主 | AssetRipper.TextureDecoder | 1.2.0 |
| 插件共 | AssetRipper.TextureDecoder | 1.2.0 |
| 插件共 | Mono.Cecil | 0.11.4 |
| 插件共 | SixLabors.ImageSharp | 3.1.4 |
| AudioPlugin | Fmod5Sharp | （无版本号） |
| TexToolWrap | PVRTexLib / ISPC / Crunch | vendored |

## 6.6 配置

`config.json`（与 UABEAvalonia.exe 同目录）：

```json
{
  "UseDarkTheme": false,
  "UseCpp2Il": true
}
```

| 字段 | 含义 | 默认 |
|---|---|---|
| `UseDarkTheme` | 是否使用深色主题 | `false` |
| `UseCpp2Il` | MonoBehaviour 类型恢复优先使用 Cpp2IL（而非 MonoCecil） | `true` |

被 `ConfigurationManager.Settings` 静态缓存。设置变更时立即写回文件（`ConfigurationSettings.UseDarkTheme.set`）。

## 6.7 classdata.tpk

- 位置：`ReleaseFiles/classdata.tpk` 或 `<exe-dir>/classdata.tpk`
- 作用：Unity Class Database，让 UABEA 知道每个 SerializedType 字段名与类型
- 缺失时：GUI 提示用户选择；CLI 模式直接退出
- 来源：UABE 官方仓库 ([Releases](https://github.com/nesrak1/UABEAvalonia/releases)) 随 release 分发

## 6.8 调试技巧

1. **插件未显示**：检查 `<exe-dir>/plugins/` 是否有 DLL；插件类是否 `public` 且实现 `UABEAPlugin`。
2. **Texture 导出失败**：先看 `errorBuilder` 中的格式名，确认 native DLL 已就位。
3. **MonoBehaviour 字段全无**：确认 `classdata.tpk` 已加载；尝试切 `UseCpp2Il`。
4. **崩溃无信息**：看 `uabeacrash.log`。