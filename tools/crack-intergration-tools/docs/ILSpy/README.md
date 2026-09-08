# ILSpy — Deep Documentation

> Source root: `/home/leo/文档/android-crack/tools/source-projects/ILSpy/`
> Decompiler version: 8.x series (commit-time stamped into `DecompilerVersionInfo.cs`)
> Language: C# 14, .NET 10 GUI / .NET Standard 2.0 libraries
> License: MIT (X11)

This documentation set covers the full ILSpy codebase: the cross-platform .NET assembly browser / decompiler built on Avalonia 12 plus the standalone `ICSharpCode.Decompiler` library, the `ilspycmd` CLI, and the `ICSharpCode.ILSpyX` UI-host-agnostic core.

## File map

| File | Purpose |
|---|---|
| [01_overview.md](./01_overview.md) | What ILSpy is, top-level architecture summary |
| [02_directory_tree.md](./02_directory_tree.md) | Annotated sub-project / directory layout |
| [03_architecture.md](./03_architecture.md) | Module dependencies, class hierarchy, lifecycle (mermaid) |
| [04_data_flow.md](./04_data_flow.md) | PE bytes -> ILAst -> C# AST -> text (mermaid) |
| [05_operation_chains.md](./05_operation_chains.md) | 12 end-to-end operation chains, each with mermaid |
| [06_build_and_run.md](./06_build_and_run.md) | Build scripts, CLI flags, run targets |
| [07_functions_index.md](./07_functions_index.md) | Index table of every catalogued function |
| [08_functions_detail/](./08_functions_detail/) | Per-subproject deep function references |
| [09_callstacks.md](./09_callstacks.md) | Text-based call stacks for the 12 chains |
| [10_glossary.md](./10_glossary.md) | ECMA-335 / ILAst / NRefactory / MEF vocabulary |

## Sub-project deep references

| Sub-project | Reference |
|---|---|
| `ICSharpCode.Decompiler` (core engine) | [08_functions_detail/01_ICSharpCode.Decompiler.md](./08_functions_detail/01_ICSharpCode.Decompiler.md) |
| `ICSharpCode.Decompiler.CSharp` (C# AST, transforms, visitors) | [08_functions_detail/02_ICSharpCode.Decompiler.CSharp.md](./08_functions_detail/02_ICSharpCode.Decompiler.CSharp.md) |
| `ICSharpCode.ILSpyX` (UI-host-agnostic core) | [08_functions_detail/03_ICSharpCode.ILSpyX.md](./08_functions_detail/03_ICSharpCode.ILSpyX.md) |
| `ILSpy` (Avalonia GUI) | [08_functions_detail/04_ILSpy.GUI.md](./08_functions_detail/04_ILSpy.GUI.md) |
| `ICSharpCode.ILSpyCmd` (CLI) | [08_functions_detail/05_ICSharpCode.ILSpyCmd.md](./08_functions_detail/05_ICSharpCode.ILSpyCmd.md) |
| Other sub-projects (Generators, BAML, VS AddIn, PowerShell, Tests) | [08_functions_detail/06_Other.md](./08_functions_detail/06_Other.md) |

## Cross-project comparison

A side-by-side comparison of ILSpy with dnSpy lives at the top of the docs tree:

- [../ILSPY_DNSPY_COMPARISON.md](../ILSPY_DNSPY_COMPARISON.md)

## Quick navigation

- Onboarding read order (per `ILSpy/CLAUDE.md`): `Program.cs` -> `App.axaml.cs` -> `Views/MainWindow.axaml.cs` -> `AssemblyListPane.axaml.cs` -> `DecompilerTextView.axaml.cs`
- MEF composition graph: `ILSpy/AppEnv/AppComposition.cs`
- Whole-module decompiler entry: [`CSharpDecompiler.DecompileWholeModuleAsSingleFile`](./07_functions_index.md)
- ILAst pipeline definition (the 30-step list): `CSharpDecompiler.GetILTransforms()` at `ICSharpCode.Decompiler/CSharp/CSharpDecompiler.cs:88`