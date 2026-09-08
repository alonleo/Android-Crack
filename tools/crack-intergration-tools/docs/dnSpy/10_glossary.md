# 10 — Glossary

This glossary defines the technical vocabulary used in the dnSpy codebase. Each term has a short definition and a cross-reference to where it appears.

## .NET / ECMA-335

### CIL — Common Intermediate Language
The bytecode format defined by ECMA-335 that .NET assemblies compile to.

### CLR — Common Language Runtime
The runtime that executes CIL. dnSpy is a static + dynamic analysis tool; it interacts with the CLR via CorDebug.

### PE — Portable Executable
The file format that hosts CIL metadata + IL. dnlib reads/writes PEs.

### AssemblyRef / TypeRef / MemberRef
Metadata tokens for cross-assembly references. Resolved by dnSpy's `AssemblyResolver`.

### Metadata token
A 4-byte handle in PE metadata. The `--search-for` and Go-To-Token commands target metadata tokens.

### Sequence point
A mapping from an IL offset to a source-code line. The Roslyn-driven edit round-trip preserves these.

### Portable PDB
The modern PDB format (replaces Windows-only PDB). The CorDebug engine reads portable PDBs.

## CorDebug / Mono soft-debugger

### CorDebug
The Windows COM interface for CLR debugging (`ICorDebug`, `ICorDebugManagedCallback`). The `.NET Framework + .NET 5+` engine adapter.

### Mono soft-debugger
The Unity-specific debugger protocol. The Mono engine adapter (`Extensions/dnSpy.Debugger.DotNet.Mono/`).

### `ICorDebugManagedCallback`
The callback interface that the host implements to receive events (module load, thread create, breakpoint hit, ...).

### DAC — Data Access Component
ClrMD-based crash-dump inspection.

### DbgManager / DbgEngine
The engine-agnostic debugger manager + engine contract (from `dnSpy.Contracts.Debugger`).

### DbgRuntime / DbgProcess / DbgThread / DbgModule
Live debugger state with `DbgObject.GetOrCreateData<T>()` extension hook.

### ICorRuntime / ICorDebugAppDomain / ICorDebugThread / ICorDebugModule
The CorDebug-side runtime model.

## dnlib

### dnlib
A managed .NET metadata reader/writer (`dnlib 3.3.2`). Used by dnSpy to read assemblies, edit them, and write them back. Obfuscation-tolerant.

### ModuleDef / TypeDef / MethodDef / FieldDef / PropertyDef / EventDef
The dnlib model classes (all derive from `IHasCustomAttribute`, `IMemberDef`, ...).

### `dnlib.DotNet.Emit`
The IL emission helpers.

### `dnlib.PE`
PE-file-level helpers.

## MEF (composition)

### MEF — Managed Extensibility Framework
The composition framework. dnSpy uses TWO MEF implementations:
- **VS-MEF** (`Microsoft.VisualStudio.Composition`) for the core app + contracts (faster, cached)
- **Classic MEF** (`System.ComponentModel.Composition`) for extension discovery

### `[Export]` / `[Import]` / `[ImportingConstructor]` / `[Shared]`
Classic MEF attributes.

### `[MetadataAttribute]`
VS-MEF attribute on an attribute class that adds metadata to an export.

### `IExtension` / `[ExportExtension]`
The dnSpy extension contract. `[ExportExtension]` is `[MetadataAttribute, Export(typeof(IExtension))]`.

### CachedMefInfo
Cached MEF composition blob (`dnSpy-mef-info.bin` in profile dir). Speeds up repeat startups.

## Roslyn / Microsoft.CodeAnalysis

### Roslyn 2.10.0
The vendored Roslyn compiler. dnSpy uses Roslyn for the edit-and-recompile round-trip and for the REPL.

### `Microsoft.CodeAnalysis.Scripting.CSharpScript`
The REPL driver.

### `SyntaxTree` / `CSharpSyntaxTree` / `Compilation` / `CSharpCompilation`
The Roslyn compilation model.

### `Emit`
Produces a PE blob from a compilation.

## decompiler

### `IDecompiler`
The dnSpy decompiler contract (`dnSpy.Contracts.Logic/Decompiler/IDecompiler.cs`). One implementation per language.

### `IDecompilerOutput`
The color-aware output sink (per language).

### `DecompilationContext`
The settings + cancellation + scoped data passed to a decompile call.

### `Embedded ILSpy 5` / `NRefactory 5`
The vendored decompiler inside `Extensions/ILSpy.Decompiler/`. Pre-dates the modern `ICSharpCode.Decompiler` package.

### `dnSpy.Decompiler.ILSpy.Core.CSharp.CSharpDecompiler`
The C# decompiler (525 LoC) — wraps the embedded ILSpy 5.

### `dnSpy.Decompiler.ILSpy.Core.IL.ILDecompiler`
The IL decompiler — flat or structured modes.

## WPF / MVVM

### WPF — Windows Presentation Foundation
The GUI framework. `MetroWindow` is the chrome custom control.

### AvalonEdit / Microsoft.VisualStudio.Text.*
The text-editor control + its MEF platform. dnSpy ships a reimplementation under `dnSpy/dnSpy/Text/`.

### MVVM — Model-View-ViewModel
The standard WPF pattern. `RelayCommand`, `ListVM`, `EnumVM`, `DataFieldVM` are the shared VMs.

### ICSharpCode.TreeView (vendored)
The virtual tree-view control. Lives in `Libraries/ICSharpCode.TreeView/`.

## Tool windows

### Tool window
A dockable panel. Examples: CallStack, Locals, Watch, Breakpoints, Modules, Threads, Processes, Output, Search, Scripting, Analyzer, ...

### `IToolWindowService` / `AppToolWindow*`
The tool-window framework (`dnSpy.Contracts.DnSpy/ToolWindows/`).

### `MainWindowControl`
The dock layout (left/right/top/bottom + horizontal/vertical stacked content).

### `MainWindowControlState`
The serialized state (tool window placement, splitter distances).

## REPL

### REPL — Read-Eval-Print Loop
The interactive scripting window. C# and VB variants.

### `ScriptControl` / `ScriptControlVM`
The REPL control + VM.

### `ScriptGlobals`
dnSpy internals exposed to user code (current assembly list, debugger, ...).

### `CachedWriter`
Output capture.

### `ReplSettings`
Persisted REPL state (globals, refs, imports, lib paths).

### `RespFileUtils` / `ResponseFileReader`
Parses `*.Interactive.rsp`.

## AsmEditor

### AsmEditor
The dnSpy.AsmEditor extension — in-place assembly editing.

### `MethodDefNode` / `MethodDefVM` / `EditMethodCommand`
The per-method edit stack.

### `RoslynLanguageCompiler`
Compiles the user's edited buffer into a PE blob.

### `SaveModuleCommand`
Writes the PE blob back via dnlib.

### `UndoRedo`
Undo/redo stack.

## Analyzer

### Analyzer
The dnSpy.Analyzer extension — static analysis (Used By, Base Type, ...).

### `IAnalyzer`
The analyzer contract.

### `AnalyzerTreeNodeData`
A node in the analyzer tree.

### `MethodUsedByNode` / `BaseTypesTreeNode` / `DerivedTypesTreeNode` / ...
Per-finding tree node kinds (~40 total).

### `AsyncFetchChildrenHelper`
Async fetch of children (for cross-assembly resolution).

## BAML

### BAML — Binary XAML
The compiled form of WPF XAML. Decompiled to XAML by `dnSpy.BamlDecompiler`.

### `BamlDecompiler` / `BamlDisassembler` / `BamlElement`
BAML parsing.

### `XamlDecompiler` / `XamlOutputCreator` / `XmlnsDictionary`
BAML -> XAML emission.

### `IRewritePass` / `RecursionCounter`
Rewrite passes for field references, type lookups, ...

## IL Interpreter

### `ILVM` / `ILVMFactory` / `ILValue`
The pure-IL interpreter VM. Executes IL byte-by-byte without a live process.

### `DebuggerRuntime` (in Interpreter project)
The interpreter's runtime.

## Debugger UI

### `StackFrameData` / `DbgStackFrameImpl` / `DbgStackWalkerImpl`
Call-stack implementation.

### `DbgBoundCodeBreakpointImpl`
A bound code breakpoint (the kind that can fire).

### `BreakAllHelper`
Pauses all threads.

### `BoundBreakpointsManager`
Tracks all bound breakpoints.

### `Steppers`
The step engine.

## Theming

### `.dntheme`
Binary XAML theme files (blue / dark / light / dark-high-contrast).

### Theme manager
`dnSpy.Contracts.DnSpy/Themes/`.

## Localization

### Satellite assemblies
Per-language resource assemblies. Crowdin-translated into 14 languages: `cs;de;es;es-ES;fa;fr;hu;it;pt-BR;pt-PT;ru;tr;uk;zh-CN`.

### CultureService
Sets `Thread.CurrentThread.CurrentUICulture` per `--culture`.