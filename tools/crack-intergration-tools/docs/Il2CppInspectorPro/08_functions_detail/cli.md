# 08 · `Il2CppInspector.CLI`（旧版命令行）

> 文件：
> - `Il2CppInspector.CLI/Program.cs`
> - `Il2CppInspector.CLI/PluginOptions.cs`
> - `Il2CppInspector.CLI/PathUtils.cs`
> - `Il2CppInspector.CLI/Properties/launchSettings.json`

---

## `App.Main`

- **签名**: `static int Main(string[] args)`
- **位置**: `Il2Inspector.CLI/Program.cs:~30`
- **可见性**: public static
- **调用了**:
  - `CommandLineParser.ParseArguments<Options>(args)`
  - `App.Run(options)`（成功路径）
- **抛出/异常**: 任何未捕获异常 → exit code 1
- **简要说明**: 程序入口

## `App.Run`

- **签名**: `static int Run(Options options)`
- **位置**: `Il2Inspector.CLI/Program.cs:~80`
- **可见性**: public static
- **副作用**: 输出文件
- **调用了**:
  - `PluginManager.EnsureInit()`
  - `Il2Inspector.LoadFromPackage(...)` 或 `LoadFromFile(...)`
  - `new TypeModel(il2cpp)`（每个 inspector）
  - `new AppModel(model, false)`
  - `AppModel.Build(unityVersion, cppCompiler)`
  - 5 个 emitter 之一/全部（取决于 options）
- **简要说明**: 主调度

## `App.RunPlugin` (private)

- **签名**: `static void RunPlugin(...)` (private)
- **位置**: `Program.cs:~250`
- **可见性**: private static
- **调用了**: `PluginOptions.ParsePluginOptions`
- **简要说明**: 处理 `--plugins` 子命令

## `App.getOutputPath`

- **签名**: `static string getOutputPath(string basePath, string defaultExt, int idx)`
- **位置**: `Program.cs:~440`
- **可见性**: private static
- **简要说明**: 多 binary 自动追加 `-N` 后缀

## `Options` (CommandLineParser)

- **签名**: `class Options`（含所有 `[Option]`/`[Verb]` 字段）
- **位置**: `Program.cs:~50-300`
- **可见性**: public
- **简要说明**: 完整 CLI 选项集合（详见 [06_build_and_run.md §6.3](../06_build_and_run.md)）

---

## `PluginOptions.CreateOptionsFromPlugin`

- **签名**: `static Type[] CreateOptionsFromPlugin(IPlugin plugin)`
- **位置**: `Il2Inspector.CLI/PluginOptions.cs:~40`
- **可见性**: public static
- **副作用**: `System.Reflection.Emit` 动态创建类型
- **调用了**: `AssemblyBuilder.DefineType`、`TypeBuilder.DefineProperty`、`SetCustomAttribute(new OptionAttribute(...))`
- **简要说明**: 把 `IPluginOption` 列表转成 CommandLineParser 可消费的 Type

## `PluginOptions.GetPluginOptionTypes`

- **签名**: `static IEnumerable<Type> GetPluginOptionTypes()`
- **位置**: `PluginOptions.cs:~80`
- **可见性**: public static
- **调用**: CLI `App.Run` 启动时调用
- **简要说明**: 聚合所有已启用插件的 option type

## `PluginOptions.ParsePluginOptions`

- **签名**: `static void ParsePluginOptions(...)`
- **位置**: `PluginOptions.cs:~170`
- **可见性**: public static
- **调用了**: 反射写回插件属性
- **简要说明**: 把解析出的值回写到插件

---

## `PathUtils.FindPath`

- **签名**: `static IEnumerable<string> FindPath(string searchPattern)`
- **位置**: `Il2Inspector.CLI/PathUtils.cs:~20`
- **可见性**: public static
- **简要说明**: 通配符展开（`bin/**/*.so` 等）