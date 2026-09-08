# 01 — Overview

## What ILSpy is

ILSpy is a cross-platform .NET assembly browser and decompiler. Given a managed `.dll` or `.exe` it produces readable C# (also IL and VB) source code, including de-sugared forms for:

- Async / await state machines
- Iterator / `yield return` state machines
- Pattern matching (`switch` expressions, `is T x`, list patterns)
- Tuples, records, primary constructors
- Nullable reference type annotations (when the original used them)
- Lambda bodies, local functions, display classes
- LINQ query expressions
- COM interop and `dynamic` call sites

The same engine is the foundation of `ilspycmd` (the CLI shipped as a .NET global tool), the ILSpy VS 2022 extension, the ILSpy PowerShell cmdlets, and the `ICSharpCode.Decompiler` NuGet package consumed by third parties (including dnSpy itself).

## Stack

| Layer | Tech |
|---|---|
| GUI shell | Avalonia 12 (cross-platform XAML), `AvaloniaEdit` text editor, Dock (wieslawsoltes) layout |
| Theme | Simple (not Fluent) |
| Composition | `System.Composition` MEF (System.Composition.MEF) |
| DI | `Microsoft.Extensions.DependencyInjection` (small bridge) |
| Core engine | `ICSharpCode.Decompiler` (netstandard2.0, also multi-RID: win/linux/osx) |
| AST model | NRefactory (own, derived from the historic NRefactory 5) |
| IL model | own `IL/Instructions/*.cs` ILAst hierarchy |
| Type system | own `TypeSystem/I*.cs` over `System.Reflection.Metadata` |
| Metadata | `System.Reflection.Metadata` + `UniversalAssemblyResolver` for AssemblyRef resolution |
| Target framework (GUI) | `net10.0` |
| Target framework (libraries) | `netstandard2.0` |
| Language version | C# 14 |

## Top-level architecture (one paragraph)

`ICSharpCode.Decompiler` reads a `MetadataFile` (PE file, NuGet bundle, single-file bundle, or WebCIL) and constructs a `DecompilerTypeSystem`. The user-facing `CSharpDecompiler` is instantiated with that type system plus a `DecompilerSettings` object. Each method body flows through three phases: **(1)** `ILReader` turns the ECMA-335 CIL bytes into an ILAst (`ILFunction`) with stack-type inference, **(2)** a 30-step pipeline of `IILTransform`s de-sugars the ILAst into a near-final statement list (async/await, yield, pattern matching, expression trees, collection initializers, ...), and **(3)** `StatementBuilder` / `ExpressionBuilder` / `CallBuilder` translate the ILAst into an NRefactory `SyntaxTree` of `AstNode`s. The `SyntaxTree` is then pretty-printed by `CSharpOutputVisitor` (a 3164-LoC visitor that walks the AST and emits C# tokens). The GUI host (`ICSharpCode.ILSpyX` + Avalonia) wraps the engine for interactive tree browsing; the CLI host (`ICSharpCode.ILSpyCmd`) calls the same engine and supports batch modes (`-p` for whole-project export, `--generate-diagrammer` for HTML class diagrams, `-genpdb` for portable PDB emission).

## Key entry points

| Entry | Path | LoC |
|---|---|---|
| Avalonia GUI Main | `ILSpy/Program.cs:35` | 52 |
| Avalonia App lifecycle | `ILSpy/App.axaml.cs` | ~170 (file is 5629 bytes) |
| CLI Main | `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:71` | ~700 |
| Engine facade | `ICSharpCode.Decompiler/CSharp/CSharpDecompiler.cs:61` | 2517 |
| IL importer | `ICSharpCode.Decompiler/IL/ILReader.cs:46` | 2191 |
| C# output | `ICSharpCode.Decompiler/CSharp/OutputVisitor/CSharpOutputVisitor.cs` | 3164 |
| UI-host core | `ICSharpCode.ILSpyX/LoadedAssembly.cs:55` | 766 |
| MEF composition | `ILSpy/AppEnv/AppComposition.cs:35` | ~140 |
| Settings model | `ICSharpCode.Decompiler/DecompilerSettings.cs:30` | 2450 |

## Licensing and maintenance

- License: MIT (X11). Copyright holders vary; the original contributors are listed in source headers.
- Project home: github.com/icsharpcode/ILSpy.
- The repository is actively maintained; new C# language features (records, primary constructors, file-scoped namespaces, pattern matching) are added to the decompiler as the runtime catches up.
- Central package management is enabled (`Directory.Packages.props`), so every `PackageReference` needs a matching `PackageVersion` entry. Build scripts wrap this so a bare `dotnet build` does not silently prune `packages.lock.json` (see `restore.ps1`).