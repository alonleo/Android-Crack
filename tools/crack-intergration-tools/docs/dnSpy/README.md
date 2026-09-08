# dnSpy — Deep Documentation

> Source root: `/home/leo/文档/android-crack/tools/source-projects/dnSpy/`
> Decompiler version: 6.1.8 (per `DnSpyCommon.props`)
> Language: C# (latest) + a few VB for editor features
> License: GPL v3
> Target frameworks: `net48` + `net5.0-windows` (multi-target); RIDs `win-x86;win-x64`

This documentation set covers the full dnSpy codebase: the WPF .NET debugger / decompiler / editor built around embedded ILSpy 5 + NRefactory 5, Roslyn 2.10.0, dnlib 3.3.2, and a CorDebug / Mono soft-debugger back end.

## File map

| File | Purpose |
|---|---|
| [01_overview.md](./01_overview.md) | What dnSpy is, top-level architecture summary |
| [02_directory_tree.md](./02_directory_tree.md) | Annotated sub-project / directory layout |
| [03_architecture.md](./03_architecture.md) | Module dependencies, class hierarchy, lifecycle (mermaid) |
| [04_data_flow.md](./04_data_flow.md) | Load assembly -> decompile -> edit (mermaid) |
| [05_operation_chains.md](./05_operation_chains.md) | 12 end-to-end operation chains, each with mermaid |
| [06_build_and_run.md](./06_build_and_run.md) | Build scripts, CLI flags, run targets |
| [07_functions_index.md](./07_functions_index.md) | Index table of every catalogued function |
| [08_functions_detail/](./08_functions_detail/) | Per-subproject deep function references |
| [09_callstacks.md](./09_callstacks.md) | Text-based call stacks for the 12 chains |
| [10_glossary.md](./10_glossary.md) | dnlib / MEF / WPF / CorDebug vocabulary |

## Sub-project deep references

| Sub-project | Reference |
|---|---|
| Main WPF app (`dnSpy/`) | [08_functions_detail/01_dnSpy.MainApp.md](./08_functions_detail/01_dnSpy.MainApp.md) |
| Document / tab management | [08_functions_detail/02_dnSpy.Documents.md](./08_functions_detail/02_dnSpy.Documents.md) |
| Decompiler glue (`dnSpy.Decompiler`) | [08_functions_detail/03_dnSpy.Decompiler.md](./08_functions_detail/03_dnSpy.Decompiler.md) |
| Contracts (`dnSpy.Contracts.DnSpy`) | [08_functions_detail/04_dnSpy.Contracts.DnSpy.md](./08_functions_detail/04_dnSpy.Contracts.DnSpy.md) |
| Generic debugger UI (`dnSpy.Debugger`) | [08_functions_detail/05_dnSpy.Debugger.md](./08_functions_detail/05_dnSpy.Debugger.md) |
| CorDebug implementation | [08_functions_detail/06_dnSpy.Debugger.DotNet.CorDebug.md](./08_functions_detail/06_dnSpy.Debugger.DotNet.CorDebug.md) |
| Roslyn REPL | [08_functions_detail/07_dnSpy.Scripting.Roslyn.md](./08_functions_detail/07_dnSpy.Scripting.Roslyn.md) |
| Static analyzer | [08_functions_detail/08_dnSpy.Analyzer.md](./08_functions_detail/08_dnSpy.Analyzer.md) |
| AsmEditor (assembly editor) | [08_functions_detail/09_dnSpy.AsmEditor.md](./08_functions_detail/09_dnSpy.AsmEditor.md) |

## Cross-project comparison

A side-by-side comparison of dnSpy with ILSpy lives at the top of the docs tree:

- [../ILSPY_DNSPY_COMPARISON.md](../ILSPY_DNSPY_COMPARISON.md)

## Quick navigation

- Startup read order: `MainApp/StartUpClass.cs` -> `MainApp/App.xaml.cs` -> `MainApp/AppWindow.cs` -> `MainApp/MainWindowControl.cs`
- Document / tab model: `Documents/DsDocumentService.cs` + `Documents/Tabs/DocumentTabService.cs`
- CorDebug entry: `Extensions/dnSpy.Debugger/dnSpy.Debugger.DotNet.CorDebug/Impl/DbgEngineImpl.cs`
- Decompiler providers: `Extensions/ILSpy.Decompiler/dnSpy.Decompiler.ILSpy.Core/CSharp/CSharpDecompiler.cs`