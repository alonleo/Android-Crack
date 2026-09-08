# 08 — `dnSpy.Debugger` (Generic Debugger UI + Framework)

This file documents the generic debugger extension (`Extensions/dnSpy.Debugger/dnSpy.Debugger/`). It contains the abstract `DbgManager` + `DbgEngine` implementations, the tool windows, and the attach-to-process UI. The actual engine adapters (CorDebug, Mono) live in sibling projects documented in [06_dnSpy.Debugger.DotNet.CorDebug.md](./06_dnSpy.Debugger.DotNet.CorDebug.md).

## `TheExtension.cs`

### `TheExtension`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/TheExtension.cs`
- **MEF**: `[ExportExtension] sealed class TheExtension : IExtension`
- **可见性**: public, sealed
- **简要说明**: top-level MEF plugin

## `dnSpy.Debugger.csproj`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/dnSpy.Debugger.csproj`
- **简要说明**: csproj

## `AntiAntiDebug/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/AntiAntiDebug/`
- **简要说明**: P/Invoke patches to bypass managed anti-debug checks. The CorDebug-side version lives under `dnSpy.Debugger.DotNet.CorDebug/AntiAntiDebug/`.

## `Attach/`

### `AttachableProcessesServiceImpl` (sealed) — `Extensions/dnSpy.Debugger/dnSpy.Debugger/Attach/AttachableProcessesServiceImpl.cs`

- **MEF**: `[Export]`
- **可见性**: public, sealed
- **简要说明**: enumerates Win32 processes (PID, name, architecture, title)

#### `public void RefreshProcesses()`

- **位置**: `Attach/AttachableProcessesServiceImpl.cs:1`
- **可见性**: public
- **副作用**: starts an async refresh
- **简要说明**: re-snapshot

#### `public IReadOnlyList<AttachableProcess> Processes { get; }`

- **位置**: `Attach/AttachableProcessesServiceImpl.cs:1`
- **可见性**: public

#### `public event EventHandler ProcessesUpdated`

- **位置**: `Attach/AttachableProcessesServiceImpl.cs:1`
- **可见性**: public

### `AttachableProcessImpl` — `Attach/AttachableProcessImpl.cs`

- **可见性**: public
- **简要说明**: one process

#### `public DotNetAttachToProgramOptions? CreateAttachOptions()`

- **位置**: `Attach/AttachableProcessImpl.cs:1`
- **可见性**: public
- **简要说明**: build attach options from this process

### `Win32CommandLineProvider` — `Attach/Win32CommandLineProvider.cs`

- **可见性**: public
- **简要说明**: builds command-line debug options

### `AppCommandLineArgsHandler` — `Attach/AppCommandLineArgsHandler.cs`

- **可见性**: public
- **简要说明**: CLI flag handler for debugger

## `Breakpoints/`

### `Breakpoints/Code/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Breakpoints/Code/`
- **简要说明**: code-breakpoint UI

### `Breakpoints/Modules/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Breakpoints/Modules/`
- **简要说明**: module-load breakpoints

## `CallStack/`

### `DbgCallStackServiceImpl` — `CallStack/DbgCallStackServiceImpl.cs`

- **MEF**: `[Export]`
- **可见性**: public, sealed
- **简要说明**: the call-stack tool window

### `DbgStackFrameImpl` — `CallStack/DbgStackFrameImpl.cs`

- **可见性**: public
- **简要说明**: one stack frame

### `DbgStackWalkerImpl` — `CallStack/DbgStackWalkerImpl.cs`

- **可见性**: public
- **简要说明**: walks the call stack

### `SpecialDbgEngineStackFrame` — `CallStack/SpecialDbgEngineStackFrame.cs`

- **可见性**: public
- **简要说明**: a synthetic frame (e.g. debugger-internal)

## `Code/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Code/`
- **简要说明**: code-location contracts

## `DbgUI/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/DbgUI/`
- **简要说明**: debugger UI service

## `Dialogs/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Dialogs/`
- **简要说明**: Attach to Process, Breakpoint settings

## `Disassembly/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Disassembly/`
- **简要说明**: native disassembly view

## `Evaluation/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Evaluation/`
- **简要说明**: expression evaluation

## `Exceptions/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Exceptions/`
- **简要说明**: exception settings UI

## `Impl/` (27 files)

### `DbgManagerImpl.cs` (1234 LoC — central debugger manager)

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs:34`
- **MEF**: `[Export(typeof(DbgManager))] sealed partial class DbgManagerImpl : DbgManager, IIsRunningProvider`
- **可见性**: public, sealed, partial
- **简要说明**: the central debugger manager; all event fan-out

#### All event overrides (lines 37-57)

- `Message` (line 37)
- `MessageProcessCreated` / `MessageProcessExited` (lines 38-39)
- `MessageRuntimeCreated` / `MessageRuntimeExited` (lines 40-41)
- `MessageAppDomainLoaded` / `MessageAppDomainUnloaded` (lines 42-43)
- `MessageModuleLoaded` / `MessageModuleUnloaded` (lines 44-45)
- `MessageThreadCreated` / `MessageThreadExited` (lines 46-47)
- `MessageExceptionThrown` (line 48)
- `MessageEntryPointBreak` (line 49)
- `MessageProgramMessage` (line 50)
- `MessageBoundBreakpoint` (line 51)
- `MessageProgramBreak` (line 52)
- `MessageStepComplete` (line 53)
- `MessageSetIPComplete` (line 54)
- `MessageUserMessage` (line 55)
- `MessageBreak` (line 56)
- `MessageAsyncProgramMessage` (line 57)

#### `public override DbgDispatcher Dispatcher => dbgDispatcherProvider.Dispatcher` (line 157)

#### `public override event EventHandler<DbgCollectionChangedEventArgs<DbgProcess>>? ProcessesChanged` (line 160)

#### `public override DbgProcess[] Processes { get; }` (line 161)

#### `public override event EventHandler? IsDebuggingChanged` (line 169)

#### `public override bool IsDebugging { get; }` (line 170)

#### `public override event EventHandler? DelayedIsRunningChanged` (line 190)

#### `public override event EventHandler? IsRunningChanged` (line 191)

#### `public override bool? IsRunning { get; }` (line 192)

#### `public override event EventHandler<DbgCollectionChangedEventArgs<string>>? DebugTagsChanged` (line 214)

#### `public override string[] DebugTags { get; }` (line 215)

### Helper partials

- `DbgManagerImpl.BoundBreakpointsManager.cs`
- `DbgManagerImpl.BreakAllHelper.cs`
- `DbgManagerImpl.CurrentObjects.cs`
- `DbgManagerImpl.ProcessKey.cs`
- `DbgManagerImpl.Steppers.cs`
- `DbgManagerImpl.StopDebuggingHelper.cs`
- `DbgManagerImpl.TagsCollection.cs`
- `DbgManagerImpl.EngineState.cs`

### Other Impl files

- `DbgEngineImpl.cs` (abstract partial, base for engines)
- `DbgEngineImpl.Breakpoints.cs` / `DbgEngineImpl.Evaluation.cs` / etc.
- `DbgProcessImpl.cs` / `DbgThreadImpl.cs` / `DbgModuleImpl.cs` / `DbgAppDomainImpl.cs`
- `DbgRuntimeImpl.cs`
- `DbgBoundCodeBreakpointImpl.cs`
- `DbgBreakInfoCollectionBuilder.cs`
- `DbgDispatcherImpl.cs` / `DbgDispatcherProvider.cs`
- `DebuggerThread.cs`
- `DelayedIsRunningHelper.cs`
- `SwitchToDebuggedProcess.cs`
- `TagsCollection.cs`
- `CurrentObject.cs`
- `ProcessKey.cs`
- `StopDebuggingHelper.cs`
- `BreakAllHelper.cs`
- `BoundBreakpointsManager.cs`
- `Steppers.cs`
- `ObjectFactoryImpl.cs`

## `Modules/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Modules/`
- **简要说明**: Modules tool window

## `Native/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Native/`
- **简要说明**: native process / threads

## `Settings/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Settings/`
- **简要说明**: debugger settings UI

## `Shared/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Shared/`
- **简要说明**: `Dispatcher`, `FileUtilities` — shared by other projects

## `Steppers/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Steppers/`
- **简要说明**: step engine

## `Text/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Text/`
- **简要说明**: debugger text adornments (current-line highlight)

## `Themes/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Themes/`
- **简要说明**: debugger XAML themes

## `ToolWindows/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/`
- **简要说明**: Autos, CallStack, CodeBreakpoints, Exceptions, Locals, Logger, Memory, ModuleBreakpoints, Modules, Processes, Threads, Watch, ...

### `ToolWindows/ToolWindowsOperations.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/ToolWindowsOperations.cs`
- **简要说明**: helper operations

### `ToolWindows/FormatterUtils.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/FormatterUtils.cs`
- **简要说明**: value formatter

### `ToolWindows/LazyToolWindowVMHelper.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/LazyToolWindowVMHelper.cs`
- **简要说明**: lazy VM helper

### `ToolWindows/SimpleProcessVM.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/SimpleProcessVM.cs`
- **简要说明**: process VM

### `ToolWindows/AntiFlickerConstants.cs`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/ToolWindows/AntiFlickerConstants.cs`
- **简要说明**: anti-flicker constants

## `UI/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/UI/`
- **简要说明**: debugger UI helpers

## `Utilities/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger/Utilities/`
- **简要说明**: debugger-side utilities