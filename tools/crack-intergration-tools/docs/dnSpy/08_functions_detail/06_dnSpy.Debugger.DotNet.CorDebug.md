# 08 — `dnSpy.Debugger.DotNet.CorDebug` (CorDebug Implementation)

This file documents the CorDebug implementation (`Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/`). The main entry is `DbgEngineImpl.cs` (974 LoC) — an `ICorDebug` adapter.

## `TheExtension.cs`

### `TheExtension`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/TheExtension.cs`
- **MEF**: `[ExportExtension] sealed class TheExtension : IExtension`
- **可见性**: public, sealed
- **简要说明**: top-level MEF plugin

## `dnSpy.Debugger.DotNet.CorDebug.csproj`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/dnSpy.Debugger.DotNet.CorDebug.csproj`
- **简要说明**: csproj

## `AntiAntiDebug/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/AntiAntiDebug/`
- **简要说明**: P/Invoke patches to bypass managed anti-debug checks (e.g. `IsDebuggerPresent`, `CheckRemoteDebuggerPresent`, `NtQueryInformationProcess`)

## `Breakpoints/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Breakpoints/`
- **简要说明**: code + module-load breakpoints

## `CallStack/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/CallStack/`
- **简要说明**: call-stack (.NET-specific)

## `Code/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Code/`
- **简要说明**: code locations

## `DAC/` (Data Access Component)

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/DAC/`
- **简要说明**: ClrMD-based crash-dump inspection

## `dndbg/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/dndbg/`
- **简要说明**: raw CorDebug COM interop

## `Dialogs/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Dialogs/`
- **简要说明**: Attach to Process, Breakpoint settings

## `Impl/` (36 files)

### `DbgEngineImpl.cs` (974 LoC — CorDebug engine)

#### `DbgEngineImpl` (abstract partial) — `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Impl/DbgEngineImpl.cs:53`

- **可见性**: `abstract partial class DbgEngineImpl : DbgEngine, IClrDacDebugger`
- **简要说明**: CorDebug engine base — `ICorDebug` adapter

##### `public override DbgStartKind StartKind { get; }` (line 54)

##### `public override string[] DebugTags => new[] { PredefinedDebugTags.DotNetDebugger }` (line 55)

##### `public override event EventHandler<DbgEngineMessage>? Message` (line 56)

##### `public event EventHandler? ClrDacRunning` (line 57)

##### `public event EventHandler? ClrDacPaused` (line 58)

##### `public event EventHandler? ClrDacTerminated` (line 59)

##### `internal DebuggerThread DebuggerThread => debuggerThread` (line 61)

##### `internal DbgObjectFactory ObjectFactory => objectFactory` (line 62)

##### `internal ClrDac clrDac` (line 71)

##### `internal readonly StackFrameData stackFrameData` (line 82)

##### `internal DmdDispatcherImpl DmdDispatcher { get; }` (line 86)

##### `internal DbgRawMetadataService RawMetadataService { get; }` (line 87)

##### `internal DbgCorDebugInternalRuntime? internalRuntime` (line 99)

##### `internal event EventHandler<ClassLoadedEventArgs>? ClassLoaded` (line 127)

##### `internal bool CheckCorDebugThread() => debuggerThread.CheckAccess()` (line 129)

##### `internal void VerifyCorDebugThread() => debuggerThread.VerifyAccess()` (line 130)

##### `internal T InvokeCorDebugThread<T>(Func<T> callback) => debuggerThread.Invoke(callback)` (line 131)

##### `internal void CorDebugThread(Action callback) => debuggerThread.BeginInvoke(callback)` (line 132)

##### `internal string DebuggeeVersion => dnDebugger.DebuggeeVersion` (line 133)

##### `internal bool IsPaused => dnDebugger.ProcessState == DebuggerProcessState.Paused` (line 134)

##### `internal DbgEngineMessageFlags GetMessageFlags(bool pause = false)` (line 136)

##### `internal void RaiseModulesRefreshed(DbgModule module) => dbgModuleMemoryRefreshedNotifier.RaiseModulesRefreshed(...)` (line 252)

##### `internal DmdDynamicModuleHelperImpl GetDynamicModuleHelper(DnModule dnModule)` (line 254)

##### `internal DbgThread? TryGetThread(CorThread? thread)` (line 281)

##### `internal DbgModule? TryGetModule(CorModule? corModule)` (line 309)

##### `sealed class DbgModuleData` (line 480)

- `DbgEngineImpl Engine { get; }`
- `DnModule DnModule { get; }`
- `ModuleId ModuleId { get; private set; }`
- `bool HasUpdatedModuleId { get; private set; }`
- `int LoadClassVersion`
- `DbgModuleData(DbgEngineImpl, DnModule, ModuleId)`
- `OnLoadClass()`
- `UpdateModuleId(ModuleId)`

##### `internal ModuleId GetModuleId(DbgModule module)` (line 501)

##### `internal bool TryGetDnModuleAndVersion(DbgModule module, [NotNullWhen(true)] out DnModule? dnModule, out int loadClassVersion)` (line 514)

##### `internal bool TryGetDnModule(DbgModule module, [NotNullWhen(true)] out DnModule? dnModule)` (line 525)

##### `internal (CorModuleDef? metadata, ModuleId moduleId) GetDynamicMetadata_EngineThread(DbgModule module)` (line 627)

##### `internal static ModuleId? TryGetModuleId(DbgModule module)` (line 636)

### `DbgEngineImpl.Breakpoints.cs` / `DbgEngineImpl.Evaluation.cs` / `DbgEngineImpl.ModuleDef.cs` / `DbgEngineImpl.Threads.cs` / `DbgEngineImplDependencies.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Impl/`
- **可见性**: internal
- **简要说明**: partial-class files for the engine

### `DbgEngineProviderImpl` — `Impl/DbgEngineProviderImpl.cs`

#### `DbgEngine Create(...)` (overloads)

- **位置**: `Impl/DbgEngineProviderImpl.cs:1`
- **可见性**: public
- **抛出/异常**: `ArgumentException` on unknown start kind
- **简要说明**: instantiates `CorDebugEngineImpl`

### `DbgCorDebugInternalRuntimeImpl` — `Impl/Evaluation/DbgCorDebugInternalRuntimeImpl.cs`

- **可见性**: internal
- **简要说明**: wraps `ICorDebug` runtime

### `DbgDotNetValueImpl` / `DbgCorValueHolder` — `Impl/Evaluation/`

- **可见性**: internal
- **简要说明**: expression-evaluation value holders

### `DmdEvaluatorImpl` — `Impl/Evaluation/DmdEvaluatorImpl.cs`

- **可见性**: internal
- **简要说明**: DMD-based Roslyn expression evaluator

### `DotNetDbgEngineImpl` / `DotNetFrameworkDbgEngineImpl` / `DotNetDbgProcessStarter`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: .NET / .NET Framework engine + process starter

### `CorDebugAttachToProgramOptions` / `DotNetAttachToProgramOptions` / `DotNetFrameworkAttachToProgramOptions`

- **位置**: `Impl/Attach/`
- **可见性**: public
- **简要说明**: attach options per runtime

### `DbgCorDebugInternalRuntimeImpl` / `DbgCorDebugInternalModuleImpl` / `DbgCorDebugInternalAppDomainImpl`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: CorDebug-side runtime abstractions

### `DmdRuntime` / `DmdDispatcherImpl` / `DmdDynamicModuleHelperImpl`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: DMD (dnSpy Metadata Debug) runtime abstraction

### `DnDebuggerObjectHolder`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: holds a debugger object across yields

### `CorDebugTypeCreator`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: builds CorDebug types

### `AppHostInfo*`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: apphost.exe patching for attach

### `DotNetAttach*`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: attach-to-process glue

### `DotNetFrameworkAttachToProgramOptions`

- **位置**: `Impl/Attach/`
- **简要说明**: .NET Framework attach options

### `EvalArgumentConverter`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: argument -> expression conversion

### `ExceptionUtils`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: exception helpers

### `DebugOptionsProviderImpl`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: debug-options provider

### `DebugMessageDispatcher`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: dispatches `ICorDebugManagedCallback` events

### `DebuggerThread` (project-local)

- **位置**: `Impl/DebuggerThread.cs`
- **简要说明**: STA thread for CorDebug calls

### `DnThreadUtils`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: thread helpers

### `DbgModuleMemoryRefreshedNotifierImpl`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: memory-refresh notifier

### `DotNetDbgEngineImpl` / `DotNetFrameworkDbgEngineImpl`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: .NET + .NET Framework engine variants

### `DotNetDbgProcessStarter`

- **位置**: `Impl/`
- **简要说明**: process starter

### `StackFrameData`

- **位置**: `Impl/`
- **可见性**: internal
- **简要说明**: stack-frame data

## `Metadata/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Metadata/`
- **简要说明**: metadata helpers

## `Native/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Native/`
- **简要说明**: native helpers

## `Properties/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Properties/`
- **简要说明**: resources

## `Steppers/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Steppers/`
- **简要说明**: step engine (.NET-specific)

## `Themes/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Themes/`
- **简要说明**: debugger XAML themes

## `UI/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/UI/`
- **简要说明**: .NET-specific UI helpers

## `Utilities/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Utilities/`
- **简要说明**: .NET-specific utilities