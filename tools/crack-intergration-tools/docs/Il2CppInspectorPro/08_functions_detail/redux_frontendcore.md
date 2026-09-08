# 08 · `Il2CppInspector.Redux.FrontendCore`

> 文件：
> - `Il2Inspector.Redux.FrontendCore/UiContext.cs`
> - `Il2Inspector.Redux.FrontendCore/UiClient.cs`
> - `Il2Inspector.Redux.FrontendCore/Il2CppHub.cs`
> - `Il2Inspector.Redux.FrontendCore/LoadingSession.cs`
> - `Il2Inspector.Redux.FrontendCore/Extensions.cs`
> - `Il2Inspector.Redux.FrontendCore/PathHeuristics.cs`
> - `Il2Inspector.Redux.FrontendCore/FrontendCoreJsonSerializerContext.cs`
> - `Il2Inspector.Redux.FrontendCore/InspectorSettings.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/IOutputFormat.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/OutputFormatRegistry.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/CSharpStubOutput.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/VsSolutionOutput.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/DummyDllOutput.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/DisassemblerMetadataOutput.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/CppScaffoldingOutput.cs`
> - `Il2Inspector.Redux.FrontendCore/Outputs/CSharpLayout.cs` / `TypeSortingMode.cs` / `DisassemblerType.cs`

---

## `UiContext.ctor`

- **签名**: `UiContext(...)`
- **位置**: `Il2Inspector.Redux.FrontendCore/UiContext.cs:~50`
- **可见性**: public
- **简要说明**: 每连接上下文；持有 `Metadata` + `IFileFormatStream` + `AppModel[]` + 队列 + Unity 版本候选

## `UiContext.InitializeAsync`

- **签名**: `Task InitializeAsync(UiClient client, CancellationToken = default)`
- **位置**: `UiContext.cs:~80`
- **可见性**: public
- **调用了**: `client.OnUiLaunched()` 等
- **调用**: `Il2CppHub.OnUiLaunched`

## `UiContext.LoadInputFilesAsync`

- **签名**: `Task LoadInputFilesAsync(UiClient, List<string> paths, CancellationToken = default)`
- **位置**: `UiContext.cs:~120`
- **可见性**: public
- **调用了**:
  - `Inspector.GetStreamsFromPackage(...)` 尝试 APK/AAB
  - `PathHeuristics.IsMetadataPath` / `IsBinaryPath` 分流
  - `Inspector.LoadFromStream(...)`
  - 对每个 inspector 建 `TypeModel` + `AppModel(false)`
  - `UnityHeaders.GuessHeadersForBinary`
  - `client.OnImportCompleted()`
- **调用**: `Il2CppHub.SubmitInputFiles`

## `UiContext.QueueExportAsync`

- **签名**: `Task QueueExportAsync(UiClient, string exportFormatId, string outputDirectory, Dictionary<string, string> settings, CancellationToken = default)`
- **位置**: `UiContext.cs:~170`
- **可见性**: public
- **调用**: `Il2CppHub.QueueExport`

## `UiContext.StartExportAsync`

- **签名**: `Task StartExportAsync(UiClient, CancellationToken = default)`
- **位置**: `UiContext.cs:~200`
- **可见性**: public
- **调用了**:
  - `LoadingSession.Start(client)`
  - `OutputFormatRegistry.GetOutputFormat(id).Export(model, client, path, settings)`
- **调用**: `Il2CppHub.StartExport`

## `UiContext.GetPotentialUnityVersionsAsync`

- **签名**: `Task<List<string>> GetPotentialUnityVersionsAsync()`
- **位置**: `UiContext.cs:~225`
- **可见性**: public
- **调用**: `Il2CppHub.GetPotentialUnityVersions`

## `UiContext.ExportIl2CppFilesAsync`

- **签名**: `Task ExportIl2CppFilesAsync(UiClient, string outputDirectory, CancellationToken = default)`
- **位置**: `UiContext.cs:~245`
- **可见性**: public
- **调用**: `Il2CppHub.ExportIl2CppFiles`

## `UiContext.GetInspectorVersionAsync`

- **签名**: `static Task<string> GetInspectorVersionAsync()`
- **位置**: `UiContext.cs:~265`
- **可见性**: public static
- **调用**: `Il2CppHub.GetInspectorVersion`

## `UiContext.SetSettingsAsync`

- **签名**: `Task SetSettingsAsync(UiClient, InspectorSettings settings)`
- **位置**: `UiContext.cs:~270`
- **可见性**: public
- **调用了**: `TypeModel.ApplyNameTranslationFromFile`
- **调用**: `Il2CppHub.SetSettings`

---

## `UiClient.ctor`

- **签名**: `UiClient(ISingleClientProxy proxy)`
- **位置**: `Il2Inspector.Redux.FrontendCore/UiClient.cs:~20`
- **可见性**: public

## `UiClient.ShowLogMessage` / `BeginLoading` / `FinishLoading` / `ShowInfoToast` / `ShowSuccessToast` / `ShowErrorToast` / `OnImportCompleted`

- **签名**: 7 个对应 `Task` 方法
- **位置**: `UiClient.cs:~25-40`
- **可见性**: public
- **调用**: `UiContext` 各 RPC 处理函数密集使用
- **简要说明**: 通过 `ISingleClientProxy.InvokeAsync` 推消息给前端

---

## `Il2CppHub` (SignalR Hub)

- **位置**: `Il2Inspector.Redux.FrontendCore/Il2CppHub.cs:~10-60`
- **可见性**: public
- **方法**:
  - `OnUiLaunched()` → `State.InitializeAsync`
  - `SubmitInputFiles(paths)` → `State.LoadInputFilesAsync`
  - `QueueExport(id, path, settings)` → `State.QueueExportAsync`
  - `StartExport()` → `State.StartExportAsync`
  - `GetPotentialUnityVersions()` → `State.GetPotentialUnityVersionsAsync`
  - `ExportIl2CppFiles(path)` → `State.ExportIl2CppFilesAsync`
  - `GetInspectorVersion()` → `State.GetInspectorVersionAsync`
  - `SetSettings(settings)` → `State.SetSettingsAsync`
- **State**: `private UiContext State => (UiContext)Context.Items[nameof(UiContext)]`
- **简要说明**: SignalR Hub；每连接一个 UiContext

---

## `LoadingSession.Start`

- **签名**: `static Task<LoadingSession> Start(UiClient client)`
- **位置**: `Il2Inspector.Redux.FrontendCore/LoadingSession.cs:~10`
- **可见性**: public static
- **调用了**: `client.BeginLoading()`
- **简要说明**: IAsyncDisposable，结束自动 `FinishLoading`

---

## `Extensions.AddFrontendCore`

- **签名**: `static IServiceCollection AddFrontendCore(this IServiceCollection services)`
- **位置**: `Il2Inspector.Redux.FrontendCore/Extensions.cs:~15`
- **可见性**: public static
- **调用**: Redux CLI/GUI 启动
- **简要说明**: 注册 SignalR + CORS

## `Extensions.MapFrontendCore`

- **签名**: `static WebApplication MapFrontendCore(this WebApplication app)`
- **位置**: `Extensions.cs:~25`
- **可见性**: public static
- **调用了**: `app.MapHub<Il2CppHub>("/il2cpp")`

## `Extensions.GetAsBooleanOrDefault` / `GetAsEnumOrDefault<T>`

- **签名**: `static bool GetAsBooleanOrDefault(this Dictionary<string, string>, string, bool = false)` / `static T GetAsEnumOrDefault<T>(this Dictionary<string, string>, string, T defaultValue)`
- **位置**: `Extensions.cs:~35-50`
- **可见性**: public static

---

## `PathHeuristics.IsMetadataPath` / `IsBinaryPath`

- **签名**: `static bool IsMetadataPath(string path)` / `static bool IsBinaryPath(string path)`
- **位置**: `Il2Inspector.Redux.FrontendCore/PathHeuristics.cs:~10-50`
- **可见性**: public static
- **调用**: `UiContext.LoadInputFilesAsync`
- **简要说明**: 扩展名 + 文件名匹配（GameAssembly / il2cpp / UnityFramework）

---

## `InspectorSettings`

- **签名**: `record InspectorSettings(ulong ImageBase, string NameTranslationMapPath)`
- **位置**: `Il2Inspector.Redux.FrontendCore/InspectorSettings.cs`
- **可见性**: public

---

## `IOutputFormat.Export`

- **签名**: `Task Export(AppModel model, UiClient client, string outputPath, Dictionary<string, string> settingsDict)`
- **位置**: `Il2Inspector.Redux.FrontendCore/Outputs/IOutputFormat.cs:~5`
- **可见性**: public interface
- **调用**: `UiContext.StartExportAsync` 内部循环

## `IOutputFormatProvider.Id`

- **签名**: `static abstract string Id { get; }`
- **位置**: `IOutputFormat.cs:~10`
- **可见性**: public interface

## `OutputFormatRegistry.AvailableOutputFormats` / `GetOutputFormat`

- **签名**: `static IEnumerable<string> AvailableOutputFormats` / `static IOutputFormat GetOutputFormat(string id)`
- **位置**: `Outputs/OutputFormatRegistry.cs:~10-30`
- **可见性**: public static
- **调用**: `UiContext.StartExportAsync`

---

## `CSharpStubOutput.Export`

- **签名**: `override Task Export(AppModel model, UiClient client, string outputPath, Dictionary<string, string> settingsDict)`
- **位置**: `Il2Inspector.Redux.FrontendCore/Outputs/CSharpStubOutput.cs:~15`
- **可见性**: public
- **Id**: `"cs"`
- **调用了**: 按 `(CSharpLayout, TypeSortingMode)` 分派 → `CSharpCodeStubs.Write*`

## `VsSolutionOutput.Export`

- **签名**: `override Task Export(...)`
- **位置**: `Outputs/VsSolutionOutput.cs:~10`
- **可见性**: public
- **Id**: `"vssolution"`
- **调用了**: `CSharpCodeStubs.WriteSolution`

## `DummyDllOutput.Export`

- **签名**: `override Task Export(...)`
- **位置**: `Outputs/DummyDllOutput.cs:~10`
- **可见性**: public
- **Id**: `"dummydlls"`
- **调用了**: `AssemblyShims.Write`

## `DisassemblerMetadataOutput.Export`

- **签名**: `override Task Export(...)`
- **位置**: `Outputs/DisassemblerMetadataOutput.cs:~15`
- **可见性**: public
- **Id**: `"disassemblermetadata"`
- **调用了**:
  - `AppModel.Build(...)`
  - `CppScaffolding(model, useBetterArraySize: true).WriteTypes(...)`
  - `JSONMetadata(model).Write(...)`
  - `PythonScript(model).WriteScriptToFile(...)`

## `CppScaffoldingOutput.Export`

- **签名**: `override Task Export(...)`
- **位置**: `Outputs/CppScaffoldingOutput.cs:~10`
- **可见性**: public
- **Id**: `"cppscaffolding"`
- **调用了**: `CppScaffolding.Write(...)`

---

## `CSharpLayout` (enum)

- **位置**: `Outputs/CSharpLayout.cs`
- **值**: `SingleFile, Namespace, Assembly, Class, Tree`

## `TypeSortingMode` (enum)

- **位置**: `Outputs/TypeSortingMode.cs`
- **值**: `TypeDefinitionIndex, Alphabetical`

## `DisassemblerType` (enum)

- **位置**: `Outputs/DisassemblerType.cs`
- **值**: `IDA, Ghidra, BinaryNinja, None`