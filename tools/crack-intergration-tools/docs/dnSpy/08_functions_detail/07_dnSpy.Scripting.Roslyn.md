# 08 — `dnSpy.Scripting.Roslyn` (Roslyn REPL)

This file documents the Roslyn-based scripting REPL (`Extensions/dnSpy.Scripting.Roslyn/`). The REPL lets the user run C# / VB scripts against the loaded assemblies, with `ScriptGlobals` exposing dnSpy internals.

## `TheExtension.cs`

### `TheExtension`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/TheExtension.cs`
- **MEF**: `[ExportExtension] sealed class TheExtension : IExtension`
- **可见性**: public, sealed
- **简要说明**: top-level MEF plugin

## `ContentTypeDefinitions.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/ContentTypeDefinitions.cs`
- **简要说明**: content-type registration

## `CSharpInteractive.rsp` / `VisualBasicInteractive.rsp`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/`
- **简要说明**: default REPL response files

## `Commands/`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/Commands/`
- **简要说明**: REPL commands shown in the script window

## `Common/`

### `ScriptControl.xaml*` + `ScriptControlVM.cs` (~300+ LoC)

#### `ScriptControlVM` (abstract) — `Common/ScriptControlVM.cs:59`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/Common/ScriptControlVM.cs:59`
- **可见性**: internal, abstract
- **简要说明**: REPL VM base — `IReplCommandHandler, IScriptGlobalsHelper`

##### `public string ResetToolTip` (line 69)

##### `public string ClearScreenToolTip` (line 70)

##### `public string HistoryPreviousToolTip` (line 71)

##### `public string HistoryNextToolTip` (line 72)

##### `public string SaveToolTip` (line 73)

##### `public string WordWrapToolTip` (line 74)

##### `public ICommand ResetCommand` (line 76)

##### `public ICommand ClearCommand` (line 77)

##### `public ICommand SaveCommand` (line 78)

##### `public ICommand HistoryPreviousCommand` (line 79)

##### `public ICommand HistoryNextCommand` (line 80)

##### `public bool CanReset` (line 81)

##### `public bool CanSaveText` (line 83)

##### `public void SaveText()` (line 84)

##### `public bool CanSaveCode` (line 85)

##### `public void SaveCode()` (line 86)

##### `public void Reset(bool loadConfig = true)` (line 88)

##### `public bool WordWrap { get; set; }` (line 110)

##### `public IReplEditor ReplEditor { get; }` (line 144)

##### `public IEnumerable<IScriptCommand> ScriptCommands` (line 146)

##### `public void OnVisible()` (line 195)

##### `public bool IsCommand(string text)` (line 214)

### `UserScriptOptions` (sealed) — `Common/ScriptControlVM.cs:52`

- **位置**: `Common/ScriptControlVM.cs:52`
- **可见性**: sealed
- **简要说明**: user's script options
- Fields: `References`, `Imports`, `LibPaths`, `LoadPaths`

### `ExecState` (sealed) — `Common/ScriptControlVM.cs:222`

- **位置**: `Common/ScriptControlVM.cs:222`
- **可见性**: sealed
- **简要说明**: per-execution state
- Fields: `ScriptOptions? ScriptOptions`, ...

### `ScriptControl.xaml*`

- **位置**: `Common/`
- **简要说明**: XAML control

### `ScriptToolWindowContent` / `ScriptContent`

- **位置**: `Common/`
- **简要说明**: tool-window + content classes

### `ScriptGlobals` / `IScriptCommand` / `IScriptGlobalsHelper`

- **位置**: `Common/`
- **简要说明**: shared types

### `RoslynReplCommandInfoProvider` / `RoslynReplCommandTargetFilter[Provider]` / `RoslynReplEditorUtils`

- **位置**: `Common/`
- **简要说明**: command routing inside the editor

### `ReplSettings`

- **位置**: `Common/ReplSettings.cs`
- **简要说明**: persisted REPL state

### `ResetCommand` / `ClearCommand` / `HelpCommand` / `Commands.cs`

- **位置**: `Common/`
- **简要说明**: REPL commands (`#reset`, `#cls`, `#help`, ...)

### `PrintOptionsImpl`

- **位置**: `Common/PrintOptionsImpl.cs`
- **简要说明**: print options

### `RespFileUtils` / `ResponseFileReader`

- **位置**: `Common/`
- **简要说明**: parse `*.Interactive.rsp`

### `CachedWriter`

- **位置**: `Common/CachedWriter.cs`
- **简要说明**: output capture

### `ScriptControl`

- **位置**: `Common/ScriptControl.xaml.cs`
- **简要说明**: the actual control

### `ScriptControlVM` (CSharp / VB subclasses)

- **位置**: `CSharp/CSharpControlVM.cs` / `VisualBasic/VisualBasicControlVM.cs`
- **简要说明**: language-specific VMs

## `CSharp/`

### `CSharpContent` — `CSharp/CSharpContent.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/CSharp/CSharpContent.cs`
- **可见性**: public
- **简要说明**: C# REPL content (extends base)

### `CSharpControlVM` — `CSharp/CSharpControlVM.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/CSharp/CSharpControlVM.cs`
- **可见性**: public
- **简要说明**: C# REPL VM

### `CSharpToolWindowContent` — `CSharp/CSharpToolWindowContent.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/CSharp/CSharpToolWindowContent.cs`
- **可见性**: public
- **简要说明**: C# REPL tool window

### `CSharpReplSettingsImpl` — `CSharp/CSharpReplSettingsImpl.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/CSharp/CSharpReplSettingsImpl.cs`
- **可见性**: public
- **简要说明**: C# REPL settings

### `ReplOptionsDefinitions` — `CSharp/ReplOptionsDefinitions.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/CSharp/ReplOptionsDefinitions.cs`
- **简要说明**: option definitions

## `VisualBasic/`

### `VisualBasicContent` — `VisualBasic/VisualBasicContent.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/VisualBasic/VisualBasicContent.cs`
- **可见性**: public
- **简要说明**: VB REPL content

### `VisualBasicControlVM` — `VisualBasic/VisualBasicControlVM.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/VisualBasic/VisualBasicControlVM.cs`
- **可见性**: public
- **简要说明**: VB REPL VM

### `VisualBasicToolWindowContent` — `VisualBasic/VisualBasicToolWindowContent.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/VisualBasic/VisualBasicToolWindowContent.cs`
- **可见性**: public
- **简要说明**: VB REPL tool window

### `VisualBasicReplSettingsImpl` — `VisualBasic/VisualBasicReplSettingsImpl.cs`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/VisualBasic/VisualBasicReplSettingsImpl.cs`
- **可见性**: public
- **简要说明**: VB REPL settings

## `Properties/`

- **位置**: `Extensions/dnSpy.Scripting.Roslyn/Properties/`
- **简要说明**: resources

## REPL semantics (call stack)

```
[user types in editor]
└── ScriptControl (WPF)
    └── ScriptControlVM.Submit(text)            (Common/ScriptControlVM.cs:1)
        └── CSharpScript.RunAsync(text, ScriptOptions.Default
                                          .WithReferences(...).WithImports(...))
                                          (Microsoft.CodeAnalysis.Scripting)
        └── returns ScriptState
        └── ScriptGlobals exposed to user code (current assembly list, debugger)
        └── output captured by CachedWriter
        └── ScriptControl.WriteOutput(...)
        └── ReplSettings persists state (globals, refs, imports, lib paths)
```