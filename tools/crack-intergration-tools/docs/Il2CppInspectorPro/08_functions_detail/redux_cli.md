# 08 · `Il2CppInspector.Redux.CLI`

> 文件：
> - `Il2Inspector.Redux.CLI/Program.cs`
> - `Il2Inspector.Redux.CLI/CliClient.cs`
> - `Il2Inspector.Redux.CLI/PortProvider.cs`
> - `Il2Inspector.Redux.CLI/ServiceTypeRegistrar.cs` + `ServiceTypeResolver.cs`
> - `Il2Inspector.Redux.CLI/Commands/BaseCommand.cs`
> - `Il2Inspector.Redux.CLI/Commands/InteractiveCommand.cs`
> - `Il2Inspector.Redux.CLI/Commands/ManualCommand.cs` + `ManualCommandSettings.cs`
> - `Il2Inspector.Redux.CLI/Commands/ProcessCommand.cs`

---

## `Program.Main`

- **签名**: `static void Main(string[] args)`
- **位置**: `Il2Inspector.Redux.CLI/Program.cs:~10`
- **可见性**: public static
- **调用了**: `MainAsync` (`Program.cs:20`)
- **简要说明**: 入口

## `Program.MainAsync`

- **签名**: `static async Task MainAsync(string[] args)`
- **位置**: `Il2Inspector.Redux.CLI/Program.cs:~20`
- **可见性**: public static
- **调用了**:
  - `WebApplication.CreateSlimBuilder(args)`
  - `services.AddFrontendCore()`
  - `app.MapHub<Il2CppHub>("/il2cpp")`
  - `app.StartAsync()`
  - `CommandApp<InteractiveCommand>.RunAsync(args)`
- **简要说明**: 启 SignalR + Spectre 命令循环

---

## `CliClient.ctor`

- **签名**: `CliClient(string url)`
- **位置**: `Il2Inspector.Redux.CLI/CliClient.cs:~20`
- **可见性**: public
- **调用了**: `HubConnectionBuilder().WithUrl(...).Build()`
- **简要说明**: SignalR 客户端包装

## `CliClient.ConnectAsync` / `Dispose`

- **签名**: `Task ConnectAsync(CancellationToken = default)` / `void Dispose()`
- **位置**: `CliClient.cs:~40-50`
- **可见性**: public
- **调用**: `BaseCommand.ExecuteAsync`

## `CliClient.OnUiLaunched`

- **签名**: `ValueTask OnUiLaunched(...)`
- **位置**: `CliClient.cs:~55`
- **可见性**: public
- **调用**: `BaseCommand.ExecuteAsync` 入口

## `CliClient.SubmitInputFiles`

- **签名**: `ValueTask SubmitInputFiles(...)`
- **位置**: `CliClient.cs:~65`
- **可见性**: public
- **调用**: `ProcessCommand.ExecuteAsync`

## `CliClient.QueueExport` / `StartExport`

- **签名**: `ValueTask QueueExport(...)` / `ValueTask StartExport(...)`
- **位置**: `CliClient.cs:~75-85`
- **可见性**: public

## `CliClient.GetPotentialUnityVersions`

- **签名**: `ValueTask<List<string>> GetPotentialUnityVersions(...)`
- **位置**: `CliClient.cs:~95`
- **可见性**: public

## `CliClient.ExportIl2CppFiles` / `GetInspectorVersion` / `SetSettings`

- **签名**: 三个对应 `ValueTask` 方法
- **位置**: `CliClient.cs:~105-130`
- **可见性**: public

## `CliClient.WaitForLoadingToFinishAsync`

- **签名**: `ValueTask WaitForLoadingToFinishAsync(...)`
- **位置**: `CliClient.cs:~135`
- **可见性**: public

---

## `PortProvider.ctor`

- **签名**: `PortProvider(int port)`
- **位置**: `Il2Inspector.Redux.CLI/PortProvider.cs:3`
- **可见性**: public
- **简要说明**: DI 单例，存 SignalR 监听端口

---

## `ServiceTypeRegistrar.ctor`

- **签名**: `ServiceTypeRegistrar(IServiceCollection services)`
- **位置**: `Il2Inspector.Redux.CLI/ServiceTypeRegistrar.cs:~5`
- **可见性**: public
- **实现**: `ITypeRegistrar`

## `ServiceTypeRegistrar.Build` / `Register` / `RegisterInstance`

- **签名**: `ITypeResolver Build()` / `void Register(Type, Type)` / `void RegisterInstance(Type, object)`
- **位置**: `ServiceTypeRegistrar.cs:~15-29`
- **可见性**: public
- **简要说明**: Spectre ↔ MS.Extensions.DI 适配

## `ServiceTypeResolver.ctor` / `Resolve`

- **签名**: `ServiceTypeResolver(IServiceProvider provider)` / `object Resolve(Type?)`
- **位置**: `Il2Inspector.Redux.CLI/ServiceTypeResolver.cs:~3-12`
- **可见性**: public

---

## `BaseCommand<T>.ctor`

- **签名**: `BaseCommand(PortProvider portProvider)`
- **位置**: `Il2Inspector.Redux.CLI/Commands/BaseCommand.cs:~15`
- **可见性**: internal
- **简要说明**: 抽象基类，注入 PortProvider

## `BaseCommand<T>.ExecuteAsync`

- **签名**: `override async Task<int> ExecuteAsync(CommandContext context, T settings)`
- **位置**: `BaseCommand.cs:~20`
- **可见性**: internal
- **调用了**:
  - `new CliClient($"http://localhost:{port}/il2cpp")`
  - `client.OnUiLaunched()`
  - 派生类的具体逻辑
  - `client.Dispose()`
- **简要说明**: 公共执行循环

---

## `InteractiveCommand.ExecuteAsync`

- **签名**: `override Task<int> ExecuteAsync(CommandContext context, Settings settings)`
- **位置**: `Il2Inspector.Redux.CLI/Commands/InteractiveCommand.cs:~10`
- **可见性**: internal sealed override
- **简要说明**: Spectre 默认（无参数）的交互向导入口

---

## `ManualCommand<T>.ctor`

- **签名**: `ManualCommand(PortProvider portProvider) : base(portProvider)`
- **位置**: `Il2Inspector.Redux.CLI/Commands/ManualCommand.cs:~10`
- **可见性**: internal

## `ManualCommand.ExecuteAsync`

- **签名**: `override Task<int> ExecuteAsync(...)` (sealed concrete class)
- **位置**: `ManualCommand.cs:~30`
- **可见性**: internal

## `ManualCommandSettings`

- **签名**: `class ManualCommandSettings : CommandSettings { ... }`
- **位置**: `ManualCommandSettings.cs:~5-14`
- **可见性**: internal
- **字段**: `InputPaths` / `OutputPath`

---

## `ProcessCommand.ExecuteAsync`

- **签名**: `override async Task<int> ExecuteAsync(CommandContext context, Settings settings)`
- **位置**: `Il2Inspector.Redux.CLI/Commands/ProcessCommand.cs:~40-197`
- **可见性**: internal sealed override
- **副作用**: 通过 CliClient 调用 SignalR 方法
- **调用了**:
  - `client.SubmitInputFiles(...)`
  - `client.GetPotentialUnityVersions(...)`
  - `client.SetSettings(...)`
  - `client.QueueExport(...)` / `StartExport(...)`
  - `client.WaitForLoadingToFinishAsync()`
- **调用**: Spectre 主循环
- **简要说明**: 所有 Redux CLI flag 在此定义（详见 [06_build_and_run.md §6.5](../06_build_and_run.md)）

## `ProcessCommand.Settings`

- **签名**: `class Settings : ManualCommandSettings`（含所有 `[CommandOption]`）
- **位置**: `ProcessCommand.cs:~30-190`
- **可见性**: internal sealed
- **字段**: `--bin` / `--metadata` / `--output` / `--export` / `--cs-layout` / `--cpp-compiler` / `--disassembler` / `--name-translation` / `--unity-version` / `--image-base` 等