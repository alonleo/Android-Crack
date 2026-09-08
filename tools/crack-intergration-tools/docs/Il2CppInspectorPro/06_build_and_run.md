# 06 · 构建、运行、CLI 参数、插件加载

## 6.1 构建准备

```bash
cd /home/leo/文档/android-crack/tools/source-projects/Il2CppInspectorPro

# 1. 子模块（必须；当前为空）
git submodule update --init --recursive

# 2. .NET 10 SDK（preview 必须启用）
dotnet workload install  # 若需要 wasm-tools 等
dotnet --list-sdks       # 应显示 10.0.x

# 3. Tauri 前端额外依赖（仅 Redux GUI 需要）
cd Il2CppInspector.Redux.GUI.UI
pnpm install              # 或 npm install
cd ../..
```

## 6.2 编译命令

```bash
# 全量还原 + 构建
dotnet restore Il2CppInspector.sln
dotnet build    Il2CppInspector.sln -c Release

# 单独发布旧版 CLI（win-x64, 单文件）
dotnet publish Il2CppInspector.CLI/Il2CppInspector.CLI.csproj \
    -c Release -r win-x64 --self-contained true

# Redux GUI 会自动 BeforeBuild → pnpm tauri build --no-bundle → 嵌入 Tauri exe
dotnet publish Il2CppInspector.Redux.GUI/Il2CppInspector.Redux.GUI.csproj -c Release

# Redux CLI
dotnet publish Il2CppInspector.Redux.CLI/Il2CppInspector.Redux.CLI.csproj -c Release

# 测试
dotnet test Il2CppTests/Il2CppTests.csproj -c Release
```

> 注：`Directory.Build.props` 中 `<TargetFramework>net10.0</TargetFramework>`、`<LangVersion>preview</LangVersion>`、`<Version>2026.1</Version>`。

## 6.3 旧版 CLI（`Il2Inspector.CLI`）

`dotnet run --project Il2CppInspector.CLI -- [args]`

| 短 | 长 | 类型 | 默认 | 说明 |
|----|----|------|------|------|
| `-i` | `--bin` | `IEnumerable<string>` | `libil2cpp.so` | IL2CPP binary、APK、AAB、XAPK、IPA、Zip 或 process map 输入 |
| `-m` | `--metadata` | `string` | `global-metadata.dat` | 元数据文件（APK/AAB/XAPK/IPA/Zip 下忽略） |
|   | `--image-base` | `string` (hex) | – | ELF 内存转储的基址 |
|   | `--select-outputs` | `bool` | `false` | 仅生成命令行指定的输出 |
| `-c` | `--cs-out` | `string` | `types.cs` | C# 输出（单文件 / 目录路径） |
| `-p` | `--py-out` | `string` | `il2cpp.py` | Python 脚本输出 |
| `-h` | `--cpp-out` | `string` | `cpp` | C++ scaffolding 工程输出路径 |
| `-o` | `--json-out` | `string` | `metadata.json` | JSON 元数据 |
| `-d` | `--dll-out` | `string` | `dll` | .NET dummy DLL 输出路径 |
|   | `--metadata-out` | `string` | – | 重导出 metadata |
|   | `--binary-out` | `string` | – | 重导出 binary（多文件自动 `-N` 后缀） |
| `-e` | `--exclude-namespaces` | `IEnumerable<string>` | `System,Mono,...,AOT,JetBrains.Annotations` | 排除命名空间（`none` 禁用） |
| `-l` | `--layout` | `string` | `single` | `single`/`namespace`/`assembly`/`class`/`tree` |
| `-s` | `--sort` | `string` | `index` | `index` 或 `name` |
| `-f` | `--flatten` | `bool` | `false` | 扁平化命名空间 |
| `-n` | `--suppress-metadata` | `bool` | `false` | 不输出 method ptr/field offset/type idx |
|   | `--suppress-dll-metadata` | `bool` | `false` | 同上但针对 DLL 输出 |
| `-k` | `--must-compile` | `bool` | `false` | 强行保证可编译（跳过 Locale 等） |
|   | `--separate-attributes` | `bool` | `false` | 程序集级 attribute 写入 `AssemblyInfo.cs` |
| `-j` | `--project` | `bool` | `false` | 创建 VS 解决方案（隐含 `--layout tree --must-compile --separate-attributes`） |
|   | `--cpp-compiler` | `CppCompilerType` | `BinaryFormat` | `MSVC`/`GCC` |
| `-t` | `--script-target` | `string` | `IDA` | `IDA` / `Ghidra`（大小写敏感） |
|   | `--unity-path` | `string` | `C:\Program Files\Unity\Hub\Editor\*` | Unity 编辑器路径（`--project` 时使用） |
|   | `--unity-assemblies` | `string` | `C:\Program Files\Unity\Hub\Editor\*\Editor\Data\Resources\PackageManager\ProjectTemplates\libcache\com.unity.template.3d-*\ScriptAssemblies` | Unity 脚本程序集路径 |
|   | `--unity-version` | `UnityVersion` | – | Unity 版本 |
|   | `--unity-version-from-asset` | `string` | – | 从 asset 文件推断 Unity 版本 |
|   | `--plugins` | `IEnumerable<string>` | – | 每插件一个子参数：`--plugins "pluginone --opt val"` |

退出码：`0` 成功；`1` 参数错误 / 异常（Windows 上会显示 banner 到 stderr）。

## 6.4 GUI 启动

### 6.4.1 旧版 WPF（仅 Windows）

```bash
dotnet run --project Il2CppInspector.GUI                  # 开发模式
# 或发布后直接运行
./Il2CppInspector.GUI/bin/Release/net10.0-windows/win-x64/publish/Il2CppInspector.exe
```

WPF 窗口打开后流程：菜单 → Load binary + metadata → 自动构建 TypeModel/AppModel → 用户点 Analyze / Generate。

### 6.4.2 Redux GUI（Tauri + Svelte）

```bash
# 开发
dotnet run --project Il2CppInspector.Redux.GUI

# 发布
dotnet publish Il2CppInspector.Redux.GUI/Il2Inspector.Redux.GUI.csproj -c Release
# 产物: ./bin/Release/net10.0/win-x64/publish/Il2CppInspector.Redux.GUI.exe
# 内部会:
#   1. 启动 ASP.NET Core WebApplication（SignalR hub）
#   2. UiProcessService 提取 embedded Tauri exe 到 %TEMP%/il2cppinspectorredux-ui/
#   3. Process.Start tauri-exe.exe argv[0]=port
#   4. _uiProcess.WaitForExitAsync → lifetime.StopApplication
```

Tauri 端通过 `http://localhost:{port}/il2cpp` 反向 RPC 到后端。

## 6.5 Redux CLI（`dotnet run --project Il2Inspector.Redux.CLI`）

启动后：
1. ASP.NET 监听随机端口
2. Spectre `CommandApp<InteractiveCommand>` 启动
3. 用户键入 `process` 进入交互向导（`InteractiveCommand`）
4. 或键入 `process --bin X --meta Y --cs-out Z ...` 走 `ProcessCommand`

`ProcessCommand` 关键选项：

| 选项 | 用途 |
|------|------|
| `--bin <path>` / `--metadata <path>` | 输入 |
| `--output <dir>` | 输出目录 |
| `--export <id>` | 输出 ID（`cs`/`cppscaffolding`/`dummydlls`/`disassemblermetadata`/`vssolution`） |
| `--cs-layout` / `--cs-sort` / `--cs-must-compile` / `--cs-suppress-metadata` | C# 布局 |
| `--cpp-compiler` (`MSVC`/`GCC`/`BinaryFormat`) | C++ 编译器 |
| `--disassembler` (`IDA`/`Ghidra`/`BinaryNinja`) | 目标 |
| `--name-translation <file>` | 名称混淆复原表 |
| `--unity-version` / `--unity-version-from-asset` | Unity 版本 |
| `--image-base` | ELF 内存转储基址 |

## 6.6 插件加载

### 6.6.1 安装

```bash
# Windows
.\get-plugins.ps1
# Linux/macOS
./get-plugins.sh
```

脚本从 `https://github.com/djkaty/Il2CppInspectorPlugins/releases/latest/download/plugins.zip` 下载并解压到 `./plugins/`。

### 6.6.2 加载机制

```csharp
// Il2Inspector.Common/Plugins/Internal/PluginManager.cs
public static void Reload(string pluginPath = null, bool reset = true, bool coreOnly = false) {
    pluginPath ??= Path.GetFullPath(Process.GetCurrentProcess().MainModule.FileName + "/plugins");
    if (!Directory.Exists(pluginPath)) throw new DirectoryNotFoundException(pluginPath);

    foreach (var dll in Directory.GetFiles(pluginPath, "*.dll", SearchOption.AllDirectories)) {
        var loader = PluginLoader.CreateFromAssemblyFile(dll, sharedTypes: new[] { typeof(V100.IPlugin) });
        var asm = loader.LoadDefaultAssembly();
        foreach (var type in asm.GetTypes()) {
            if (typeof(V100.IPlugin).IsAssignableFrom(type) && !type.IsAbstract) {
                var plugin = (V100.IPlugin)Activator.CreateInstance(type);
                ManagedPlugins.Add(new ManagedPlugin {
                    Plugin = plugin,
                    Available = true,
                    Enabled = plugin is ICorePlugin   // 核心插件自动启用
                });
            }
        }
    }
}
```

### 6.6.3 CLI 暴露插件选项

`Il2Inspector.CLI/PluginOptions.cs` 用 `System.Reflection.Emit` 在运行时为每个插件动态生成 `[Verb]`/`[Option]` 类，然后让 `CommandLineParser` 解析 `--plugins "pluginid --opt value"`。

### 6.6.4 Hook 转发

```csharp
// Il2Inspector.Common/Plugins/Internal/PluginHooks.cs
public static PluginPreProcessMetadataEventInfo PreProcessMetadata(BinaryObjectStream s) {
    return PluginManager.Try<IPlugin, PluginPreProcessMetadataEventInfo>(
        action: (plugin, info) => info.Merge(plugin.PreProcessMetadata(s, info)),
        hookName: nameof(PreProcessMetadata)
    );
}
```

`PluginManager.Try<I, E>` 用栈追踪检查是否递归（`[ReentrantAttribute]` 可豁免）。

## 6.7 平台备注

| 平台 | 旧版 CLI | 旧版 WPF GUI | Redux CLI | Redux GUI |
|------|---------|-------------|-----------|-----------|
| Windows | ✓ | ✓ | ✓ | ✓ |
| Linux | ✓ (运行时) | ✗ | ✓ | ✗ (Tauri exe 仅 win) |
| macOS | ✓ | ✗ | ✓ | ✗ |