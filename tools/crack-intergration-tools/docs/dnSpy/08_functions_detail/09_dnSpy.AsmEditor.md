# 08 — `dnSpy.AsmEditor` (Assembly Editor — largest extension)

This file documents the assembly editor extension (`Extensions/dnSpy.AsmEditor/`, ~400 .cs files, ~72K LoC — the largest extension). It enables in-place editing of .NET assemblies: change method bodies, add/remove members, edit metadata, then save back via dnlib.

## `TheExtension.cs`

### `TheExtension`

- **位置**: `Extensions/dnSpy.AsmEditor/TheExtension.cs`
- **MEF**: `[ExportExtension] sealed class TheExtension : IExtension`
- **可见性**: public, sealed
- **简要说明**: top-level MEF plugin

## `dnSpy.AsmEditor.csproj`

- **位置**: `Extensions/dnSpy.AsmEditor/dnSpy.AsmEditor.csproj`
- **简要说明**: csproj

## Sub-directories (23 — one per kind of edit)

### `Assembly/`

- **位置**: `Extensions/dnSpy.AsmEditor/Assembly/`
- **简要说明**: assembly-level edits (version, public key, ...)

### `Commands/`

- **位置**: `Extensions/dnSpy.AsmEditor/Commands/`
- **简要说明**: command registry for AsmEditor

### `Compiler/`

- **位置**: `Extensions/dnSpy.AsmEditor/Compiler/`
- **简要说明**: Roslyn compilation glue (compiles user edits to PE)

### `Converters/`

- **位置**: `Extensions/dnSpy.AsmEditor/Converters/`
- **简要说明**: WPF value converters (e.g. hex <-> bytes)

### `DnlibDialogs/`

- **位置**: `Extensions/dnSpy.AsmEditor/DnlibDialogs/`
- **简要说明**: dialog helpers for dnlib-based edits

### `Event/`

- **位置**: `Extensions/dnSpy.AsmEditor/Event/`
- **简要说明**: event-member edits

### `Field/`

- **位置**: `Extensions/dnSpy.AsmEditor/Field/`
- **简要说明**: field-member edits

### `Hex/`

- **位置**: `Extensions/dnSpy.AsmEditor/Hex/`
- **简要说明**: hex-aware edits

### `Method/` (largest sub-directory)

- **位置**: `Extensions/dnSpy.AsmEditor/Method/`
- **简要说明**: method-body edits
- Key types:
  - `MethodDefNode` — wraps a `dnlib.DotNet.MethodDef`
  - `MethodDefVM` — VM
  - `MethodOptions` — edit options
  - `EditMethodCommand` — `Apply` command

### `MethodBody/`

- **位置**: `Extensions/dnSpy.AsmEditor/MethodBody/`
- **简要说明**: IL-body editor

### `Module/`

- **位置**: `Extensions/dnSpy.AsmEditor/Module/`
- **简要说明**: module-level metadata edits

### `Namespace/`

- **位置**: `Extensions/dnSpy.AsmEditor/Namespace/`
- **简要说明**: namespace edits

### `Property/`

- **位置**: `Extensions/dnSpy.AsmEditor/Property/`
- **简要说明**: property-member edits

### `Resources/`

- **位置**: `Extensions/dnSpy.AsmEditor/Resources/`
- **简要说明**: string + resource edits

### `SaveModule/`

- **位置**: `Extensions/dnSpy.AsmEditor/SaveModule/`
- **简要说明**: save changes back via dnlib

### `Themes/`

- **位置**: `Extensions/dnSpy.AsmEditor/Themes/`
- **简要说明**: AsmEditor XAML themes

### `Types/`

- **位置**: `Extensions/dnSpy.AsmEditor/Types/`
- **简要说明**: type-declaration edits

### `UndoRedo/`

- **位置**: `Extensions/dnSpy.AsmEditor/UndoRedo/`
- **简要说明**: undo/redo stack

### `Utilities/`

- **位置**: `Extensions/dnSpy.AsmEditor/Utilities/`
- **简要说明**: helpers

### `ViewHelpers/`

- **位置**: `Extensions/dnSpy.AsmEditor/ViewHelpers/`
- **简要说明**: VM helpers

### `ExtensionMethods.cs`

- **位置**: `Extensions/dnSpy.AsmEditor/ExtensionMethods.cs`
- **简要说明**: extension methods

## AsmEditor call stack (edit + apply)

```
[user edits C# method, clicks Apply]
└── EditMethodCommand.Apply                    (Method/EditMethodCommand.cs)
    └── RoslynLanguageCompiler.Compile         (Compiler/RoslynLanguageCompiler.cs)
        └── SyntaxTree from buffer
        └── CSharpCompilation.Create
        └── Emit PE blob
    └── SaveModuleCommand.Save                 (SaveModule/SaveModuleCommand.cs)
        └── dnlib writes PE blob back to original DsDocument
            ├── preserve metadata tokens where possible
            └── renumber on structural change
        └── DocumentService.CollectionChanged
            └── tree nodes refresh
```

## Other Extensions

### `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy/`

- **位置**: `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy/`
- **简要说明**: MEF plugin wrapper around the embedded ILSpy 5 / NRefactory 5 decompiler
- `TheExtension.cs` — `[ExportExtension]`
- `CSharp/` / `IL/` / `VisualBasic/` / `ILAst/` — adapter per language

### `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core/`

- **位置**: `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core/`
- **简要说明**: actual decompiler engine
- `CSharp/CSharpDecompiler.cs` — 525 LoC
- `VisualBasic/VBDecompiler.cs`
- `IL/ILDecompiler.cs` / `ILDecompilerUtils.cs`
- `Settings/DecompilerSettingsService.cs`
- `BuilderCache` / `BuilderState` / `ThreadSafeObjectPool`

### `Extensions/ILSpy.Decompiler/ICSharpCode.Decompiler/`

- **位置**: `Extensions/ILSpy.Decompiler/ICSharpCode.Decompiler/`
- **简要说明**: vendored legacy ILSpy decompiler (pre-8)

### `Extensions/ILSpy.Decompiler/NRefactory/`

- **位置**: `Extensions/ILSpy.Decompiler/NRefactory/`
- **简要说明**: vendored NRefactory 5

### `Extensions/Examples/Example1.Extension/` / `Example2.Extension/`

- **位置**: `Extensions/Examples/`
- **简要说明**: sample MEF plugins
  - `Example1` — minimal extension
  - `Example2` — tool-window sample

### `Extensions/dnSpy.BamlDecompiler/`

- **位置**: `Extensions/dnSpy.BamlDecompiler/`
- **简要说明**: BAML -> XAML for WPF assemblies
- `TheExtension.cs` — `[ExportExtension]`
- `BamlDecompiler.cs` / `BamlDisassembler.cs` / `BamlElement.cs`
- `BamlResourceElementNode.cs` / `BamlResourceNodeProvider.cs`
- `BamlSettings.cs` / `BamlSettings.xaml`
- `BamlToolTipProvider.cs`
- `Handlers/IRewritePass.cs` + `Handlers/*` — rewrite passes
- `MenuCommands.cs` / `RecursionCounter.cs`
- `Rewrite/*` — rewrite steps
- `Xaml/XamlContext.cs` / `XamlDecompiler.cs` / `XamlOutputCreator.cs`
- `XamlOutputOptionsProvider.cs` / `XmlnsDictionary.cs` / `Annotations.cs`

### `Extensions/dnSpy.Debugger.DotNet.Mono/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.Mono/`
- **简要说明**: Mono soft-debugger adapter
- `TheExtension.cs`
- `AntiAntiDebug/`, `CallStack/`, `Dialogs/`, `Impl/`, `Metadata/`, `Properties/`, `Steppers/`, `Themes/`

### `Extensions/dnSpy.Debugger.DotNet.Interpreter/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.Interpreter/`
- **简要说明**: pure-IL interpreter (no live process required)
- `TheExtension.cs`
- `DebuggerRuntime.cs` — `Impl/DebuggerRuntime.cs`
- `ILValue.cs` — IL value abstraction
- `ILVM.cs` — virtual machine
- `ILVMFactory.cs` — factory
- `InterpreterException.cs` / `InterpreterMessageException.cs` / `InterpreterThrownExceptionException.cs`
- `Impl/`, `NRT.cs`

### `Extensions/dnSpy.Debugger.DotNet.Metadata/`

- **位置**: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.Metadata/`
- **简要说明**: DMD (dnSpy Metadata Debug) runtime abstraction
- `DmdRuntime.cs` / `DmdModule.cs` / `DmdTypeDef.cs` / ...

### `Extensions/AppHostInfoGenerator/`

- **位置**: `Extensions/dnSpy.Debugger/AppHostInfoGenerator/`
- **简要说明**: rewrites apphost.exe for attach
- `AppHostInfoGenerator.csproj`

### `Extensions/Mono.Debugger.Soft/`

- **位置**: `Extensions/dnSpy.Debugger/Mono.Debugger.Soft/`
- **简要说明**: vendored Mono soft-debugger protocol client (empty in this checkout)

### `Extensions/netcorefiles/`

- **位置**: `Extensions/dnSpy.Debugger/netcorefiles/`
- **简要说明**: x86/x64 .NET debug files (copied at build time)