# 08 — Other Sub-Projects

This file documents the remaining sub-projects that contribute to ILSpy but are not part of the core three (engine / GUI / CLI).

## `ICSharpCode.Decompiler.Generators`

### `DecompilerVersionInfoGenerator` (public class) — `ICSharpCode.Decompiler.Generators/DecompilerVersionInfoGenerator.cs`

- **可见性**: public
- **简要说明**: Roslyn `ISourceGenerator` that emits `Properties/DecompilerVersionInfo.cs` (full version string, commit hash).

#### `public void Initialize(GeneratorInitializationContext context)`

- **位置**: `DecompilerVersionInfoGenerator.cs:1`
- **可见性**: public
- **调用了**: registers syntax provider
- **简要说明**: Roslyn generator entry

#### `public void Execute(GeneratorExecutionContext context)`

- **位置**: `DecompilerVersionInfoGenerator.cs:1`
- **可见性**: public
- **副作用**: adds `DecompilerVersionInfo.cs` to compilation
- **简要说明**: emits the source

### Build target

- **`ILSpyUpdateAssemblyInfo`** — target inside `ICSharpCode.Decompiler.csproj` runs `pwsh BuildTools/update-assemblyinfo.ps1` before build to inject the actual commit hash from git (overrides the generator's placeholder).

## `ICSharpCode.BamlDecompiler`

### `BamlDecompiler` (public class) — `ICSharpCode.BamlDecompiler/BamlDecompiler.cs`

- **可见性**: public
- **简要说明**: parses BAML records into a structured form.

#### `public BamlDocument Decompile(Stream bamlStream)` (and overloads)

- **位置**: `BamlDecompiler.cs:1`
- **可见性**: public
- **抛出/异常**: `BamlReaderException`
- **调用了**: `BamlReader.Read`, `XamlDecompiler.Emit`
- **简要说明**: BAML bytes -> `BamlDocument`

### `BamlReader` / `BamlRecord` / `BamlNode`

- **位置**: `ICSharpCode.BamlDecompiler/`
- **简要说明**: low-level BAML parser

## `ICSharpCode.Decompiler.PowerShell`

### Cmdlets (one file each)

- `DecompileCSharpCmdlet` — `ICSharpCode.Decompiler.PowerShell/...:1` — `Get-DecompiledCSharp`
- `DecompileProjectCmdlet` — `ICSharpCode.Decompiler.PowerShell/...:1` — `Export-DecompiledProject`
- `ListEntitiesCmdlet` — `ICSharpCode.Decompiler.PowerShell/...:1` — `Get-DecompiledEntities`
- (additional cmdlets)

Each cmdlet wraps a `CSharpDecompiler` call.

## `ICSharpCode.Decompiler.Tests` (NUnit)

- **位置**: `ICSharpCode.Decompiler.Tests/`
- **简要说明**: heavy test suite. Test kinds (per the project `CLAUDE.md`):
  - **`DecompilerTestBase`** — base for compiler-matrix tests; runs a snippet through C# / VB / F#, decompiles the result, and asserts round-trip equality.
  - **`RoundtripAssembly`** — decompile large real-world assemblies from the `ILSpy-tests/` submodule; assert decompiler is idempotent.
  - **`ILPrettyTestRunner`** — IL-pretty-print cases (e.g. `FSharp.Core.dll`).
  - **`DebuggerTests`** — uses `IDebugInfoProvider` to test PDB-driven variable names.
- Tests skip cleanly when `ILSpy-tests/` is not checked out (via `Assert.Ignore`).
- README: `ICSharpCode.Decompiler.Tests/CLAUDE.md` (project-specific guide).

## `ICSharpCode.Decompiler.TestRunner`

### `TestRunner` — `ICSharpCode.Decompiler.TestRunner/Program.cs`

- **可见性**: public
- **简要说明**: out-of-process test runner; runs tests in a child process to keep state isolated.

#### `static int Main(string[])`

- **位置**: `TestRunner/Program.cs:1`
- **可见性**: public, static
- **简要说明**: entry point — spawns a test host, reports results

## `TestFixtures.Resources`

- **位置**: `TestFixtures.Resources/`
- **简要说明**: generates resource fixtures (e.g. `.resources`, `.baml` blobs) consumed by the decompiler tests.

## `TestPlugin`

- **位置**: `TestPlugin/`
- **简要说明**: sample `*.Plugin.dll` that exercises the plugin-loading system. Targets `net10.0` so it loads inside a `net11.0` test host.

### `TestPlugin.ThePlugin`

- **位置**: `TestPlugin/ThePlugin.cs:1`
- **MEF**: `[Export(typeof(IPlugin))]`
- **简要说明**: adds a sample view

## `BuildTools/`

- **`update-assemblyinfo.ps1`** — sets the git commit hash in `Properties/DecompilerVersionInfo.cs`
- **`format.ps1`** — runs `dotnet format` (mirrors the pre-commit hook)

## `ILSpy.ReadyToRun`

- **位置**: `ILSpy.ReadyToRun/`
- **简要说明**: ReadyToRun-image viewer plugin. Lets the GUI show the ReadyToRun section of an assembly.
- **MEF**: `[Export]`

## `ILSpy.Tests` (headless Avalonia tests)

- **位置**: `ILSpy.Tests/`
- **简要说明**: NUnit tests using `Avalonia.Headless.NUnit`

## `ILSpy.Tests.Windows` (Windows-only)

- **位置**: `ILSpy.Tests.Windows/`
- **简要说明**: OS-gated UI tests (`net11.0-windows`)

## `ILSpy.BamlDecompiler.Tests`

- **位置**: `ILSpy.BamlDecompiler.Tests/`
- **简要说明**: BAML-decompiler tests (still WPF/Windows-bound)

## `ILSpy.AddIn.VS2022`

- **位置**: `ILSpy.AddIn.VS2022/`
- **简要说明**: Visual Studio extension (`net472`)
- **MEF**: VS package model
- Key entry: `ILSpyAddInPackage`

## `ILSpy.Installer`

- **位置**: `ILSpy.Installer/`
- **简要说明**: WiX 3 installer (`net472`)
- Targets: `win-x64`, `win-x86`

## `ILSpy-tests/` (git submodule)

- **位置**: `ILSpy-tests/`
- **简要说明**: pre-built real-world assemblies + test fixtures. NOT checked out by default. Ships its own `Directory.Build.props` (sets `TreatWarningsAsErrors=false`).
- Tests that need it call `Assert.Ignore` when absent.
- Reference: https://github.com/icsharpcode/ILSpy-tests

## Vendored libraries

- **`Humanizer/`** (in `ICSharpCode.Decompiler/Humanizer/`) — vendored Humanizer (MIT)
- **`TunnelVisionLabs.ReferenceAssemblyAnnotator`** — netstandard reference-assembly annotation tool
- **`LightJson/`** (in `ICSharpCode.Decompiler/Metadata/LightJson/`) — tiny JSON helper for NuGet v2/v3

## Notable internals

- **`ILSpaced/Image/ILSpy.png`** — application icon
- **`.editorconfig`** — enforced C# formatting (handled by `BuildTools/format.ps1`)
- **`Directory.Packages.props`** — central package management
- **`global.json`** — pins `Microsoft.Testing.Platform`
- **`.gitattributes`** — LF line endings + driver hints