# 08 · `Il2CppInspector.Redux.GUI`（C# 后端宿主）

> 文件：
> - `Il2Inspector.Redux.GUI/Program.cs`
> - `Il2Inspector.Redux.GUI/UiProcessService.cs`
> - `Il2Inspector.Redux.GUI/appsettings.json` / `appsettings.Development.json`

---

## `Program.Main`

- **签名**: `static void Main(string[] args)`
- **位置**: `Il2Inspector.Redux.GUI/Program.cs:~10`
- **可见性**: public static
- **调用了**: `MainAsync(args)` (`Program.cs:20`)

## `Program.MainAsync`

- **签名**: `static async Task MainAsync(string[] args)`
- **位置**: `Program.cs:~20`
- **可见性**: public static
- **调用了**:
  - `WebApplication.CreateSlimBuilder(args)`
  - `services.AddFrontendCore()`
  - `services.AddSingleton<UiProcessService>()`
  - `app = builder.Build()`
  - `app.UseCors(...)`
  - `app.MapFrontendCore()` → `app.MapHub<Il2CppHub>("/il2cpp")`
  - `app.StartAsync()`
  - `port = new Uri(app.Urls.First()).Port`
  - **Release**：`app.Services.GetRequiredService<UiProcessService>().LaunchUiProcess(port)`
- **简要说明**: 与 Redux CLI 同骨架，但额外启动 Tauri

---

## `UiProcessService.ctor`

- **签名**: `UiProcessService(ILogger<UiProcessService> logger, IWebHostEnvironment env)`
- **位置**: `Il2Inspector.Redux.GUI/UiProcessService.cs:~15`
- **可见性**: public
- **简要说明**: DI 注入；继承 BackgroundService

## `UiProcessService.ExecuteAsync`

- **签名**: `override Task ExecuteAsync(CancellationToken stoppingToken)`
- **位置**: `UiProcessService.cs:~30`
- **可见性**: public override
- **调用了**: `LaunchUiProcess(portFromArgs)` + `_uiProcess.WaitForExitAsync(stoppingToken)` → `lifetime.StopApplication()`
- **简要说明**: 等待 Tauri 退出，然后关后端

## `UiProcessService.LaunchUiProcess`

- **签名**: `void LaunchUiProcess(int port)`
- **位置**: `UiProcessService.cs:~40`
- **可见性**: public
- **副作用**: 提取嵌入 exe + 启动进程
- **调用了**:
  - `_uiExectuablePath = ExtractUiExecutable()`
  - `_uiProcess = Process.Start(new ProcessStartInfo(_uiExectuablePath, new[] { port.ToString() }))`
- **简要说明**: 启动 Tauri WebView

## `UiProcessService.ExtractUiExecutable`

- **签名**: `string ExtractUiExecutable()`
- **位置**: `UiProcessService.cs:~50`
- **可见性**: private
- **调用了**:
  - `Assembly.GetExecutingAssembly().GetManifestResourceStream("Il2Inspector.Redux.GUI.UI.il2cppinspectorredux.exe")`
  - 写到 `%TEMP%/il2cppinspectorredux-ui/il2cppinspectorredux.exe`
- **简要说明**: 把嵌入资源落盘

## `UiProcessService.StopAsync`

- **签名**: `override Task StopAsync(CancellationToken)`
- **位置**: `UiProcessService.cs:~65`
- **可见性**: public override
- **调用了**:
  - `_uiProcess?.Kill(entireProcessTree: true)`
  - `File.Delete(_uiExectuablePath)`
- **简要说明**: Ctrl+C 时清理