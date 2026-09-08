# 01 — Overview

## What dnSpy is

dnSpy is a debugger and .NET assembly editor for Windows. It is the de-facto tool for reverse-engineering .NET binaries that the original author did not publish source for. Given a managed `.dll` / `.exe`, dnSpy can:

- Browse types, members, references (like ILSpy)
- Decompile to C# / Visual Basic / IL (via embedded ILSpy 5 + NRefactory 5)
- **Edit** the assembly in-place — methods, classes, fields, properties — using `dnSpy.AsmEditor` + dnlib + Roslyn compilation
- **Attach** to a running .NET process (CorDebug for .NET Framework + .NET 5+; Mono soft-debugger for Unity)
- **Run** C# / VB scripts against the loaded assemblies (Roslyn REPL, via `dnSpy.Scripting.Roslyn`)
- Analyze references ("used by", "inherits from", "is overridden by", ...) via `dnSpy.Analyzer`
- BAML -> XAML for WPF assemblies (via `dnSpy.BamlDecompiler`)
- Run pure-IL in-process debugging (`dnSpy.Debugger.DotNet.Interpreter`) when no live process is available

## Stack

| Layer | Tech |
|---|---|
| GUI shell | WPF + WinForms interop, AvalonEdit (via vendored `Microsoft.VisualStudio.Text.*`) |
| Composition | VS-MEF (`Microsoft.VisualStudio.Composition`) + classic MEF (`System.ComponentModel.Composition`) |
| Decompiler | Embedded ILSpy 5 + NRefactory 5 (`Extensions/ILSpy.Decompiler/`) |
| Compiler / language services | Roslyn 2.10.0 (`dnSpy.Roslyn.*` projects) |
| Metadata | dnlib 3.3.2 (read + write + obfuscation-tolerant) |
| Debugger engine | CorDebug (Windows .NET) + Mono soft-debugger (Unity) + pure-IL interpreter |
| Expression evaluation | ClrMD (`Microsoft.Diagnostics.Runtime`) for crash-dump inspection |
| Disassembly | Iced 1.9.0 (x86 / x64) |
| Target framework | `net48` + `net5.0-windows` (multi-target) |
| Runtime IDs | `win-x86;win-x64` |

## Top-level architecture (one paragraph)

The `App` WPF bootstrap (`dnSpy/dnSpy/dnSpy/MainApp/App.xaml.cs:97`) does MEF discovery using VS-MEF (`AttributedPartDiscoveryV1` + `ComposableCatalog.Create`), enumerates `*.x.dll` extensions, and composes an `ExportProvider`. The provider exposes contracts from `dnSpy.Contracts.DnSpy` (870 files, ~80K LoC) — the interface-only assembly that every extension consumes. `AppWindow` + `MainWindowControl` build the dock layout; tool windows (CallStack, Locals, Watch, Breakpoints, Modules, Output, Search, Scripting, Analyzer, ...) plug in via `IToolWindowService`. The decompiler is the embedded ILSpy 5 (`Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core`) wrapped by `dnSpy.Decompiler.ILSpy.TheExtension` to expose `IDecompiler` for the GUI. The debugger back end is `dnSpy.Debugger.DotNet.CorDebug.DbgEngineImpl` (974 LoC) — an `ICorDebug` adapter that drives `ICorDebugManagedCallback` events. AsmEditor uses Roslyn to recompile the user's edits and dnlib to write the metadata back. The Roslyn REPL (`dnSpy.Scripting.Roslyn`) wraps `CSharpScript.RunAsync` against the loaded assemblies.

## Key entry points

| Entry | Path | LoC |
|---|---|---|
| WPF Main | `dnSpy/dnSpy/dnSpy/MainApp/StartUpClass.cs:33` | 73 |
| WPF App lifecycle | `dnSpy/dnSpy/dnSpy/MainApp/App.xaml.cs:97` | 625 |
| Main window layout | `dnSpy/dnSpy/dnSpy/MainApp/MainWindowControl.cs` | 638 |
| App window service | `dnSpy/dnSpy/dnSpy/MainApp/AppWindow.cs` | 225 |
| CLI parser | `dnSpy/dnSpy/dnSpy/MainApp/AppCommandLineArgs.cs` | 273 |
| Document service | `dnSpy/dnSpy/dnSpy/Documents/DsDocumentService.cs` | ~500 |
| Tab manager | `dnSpy/dnSpy/dnSpy/Documents/Tabs/DocumentTabService.cs` | ~600 |
| Debugger manager | `Extensions/dnSpy.Debugger/dnSpy.Debugger/Impl/DbgManagerImpl.cs` | 1234 |
| CorDebug engine | `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Impl/DbgEngineImpl.cs` | 974 |
| C# decompiler | `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core/CSharp/CSharpDecompiler.cs` | 525 |
| C# text formatter | `dnSpy/dnSpy/dnSpy.Decompiler/CSharp/CSharpFormatter.cs` | ~900 |

## Licensing and maintenance

- License: GPL v3.
- Project home: github.com/dnSpy/dnSpy (originally by 0xd4d, now community-maintained).
- Active in 2020-2024; updates were paused during .NET 6/7 transitions because the embedded VS-MEF + Roslyn 2.10.0 stack needs work to retarget newer .NET versions.
- Multi-target `net48` + `net5.0-windows`; `net48` uses COM references (`<HasCOMReference>true</HasCOMReference>` -> `IWshRuntimeLibrary`, etc.); `net5.0-windows` strips the COM refs.
- The vendored Roslyn 2.10.0 + VS-MEF are the main reasons modernizing is hard; the project includes a `CachedMefInfo` cache to speed startup.