# 08 — `ICSharpCode.ILSpyCmd` (CLI)

This file documents the CLI sub-project (`ICSharpCode.ILSpyCmd/`, ~15 .cs files, ~1200 LoC). The CLI is published as the `ilspycmd` .NET global tool.

## `IlspyCmdProgram.cs` (~700 LoC)

### `ILSpyCmdProgram` (public class) — `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs`
- **可见性**: public
- **MEF / CLI marker**: `[Command(Name = "ilspycmd", Description = "...")]` from `McMaster.Extensions.CommandLineUtils`
- **简要说明**: the entire CLI surface — option declarations + dispatch logic

#### `public static Task<int> Main(string[] args)`

- **签名**: `static Task<int> Main(string[])`
- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:71`
- **可见性**: public, static, async
- **参数**: command-line args
- **返回值**: process exit code
- **抛出/异常**: forwards exceptions to `ProgramExitCodes`
- **副作用**: file I/O (decompile output); NuGet probe (unless disabled)
- **调用了**: `HostBuilder().RunCommandLineApplicationAsync<ILSpyCmdProgram>(args)`
- **简要说明**: CLI entry point

#### `public async Task<int> OnExecuteAsync(CommandLineApplication app)`

- **签名**: `async Task<int> OnExecuteAsync(CommandLineApplication)`
- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:236`
- **可见性**: public, async
- **参数**: the `CommandLineApplication` from `McMaster.Extensions.CommandLineUtils`
- **返回值**: process exit code
- **副作用**: file I/O (decompile output)
- **调用了**: `PerformPerFileAction` per file, or one of `DecompileAsProject`, `GeneratePdbForAssembly`, ...
- **简要说明**: top-level dispatch — branches on flags (`-p`, `-il`, `--generate-diagrammer`, `-genpdb`, ...)

#### `private void PerformPerFileAction(string file)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:286`
- **可见性**: private
- **参数**: input file path
- **调用了**: dispatches to the right branch based on the active flag set
- **简要说明**: per-file entry

#### `private int Decompile(string fileName, TextWriter output, string? TypeName)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:549`
- **可见性**: private
- **副作用**: writes to `output`
- **调用了**: `GetDecompiler`, `CSharpDecompiler.DecompileWholeModuleAsSingleFile` or `DecompileType`
- **简要说明**: text-output decompile

#### `private void DecompileAsProject(string file, string projectFileName)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:275`
- **可见性**: private
- **抛出/异常**: `IOException`
- **副作用**: writes `.csproj` + per-type `.cs` files to disk
- **调用了**: `WholeProjectDecompiler.DecompileProject` (or `BamlAwareWholeProjectDecompiler`)
- **简要说明**: `-p` branch

#### `private void GeneratePdbForAssembly(string fileName, string pdbFileName, CommandLineApplication app)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:330`
- **可见性**: private
- **副作用**: writes PDB file to disk
- **调用了**: `CSharpDecompiler.CreateSequencePoints`, `PortablePdbBuilder`
- **简要说明**: `-genpdb` branch

#### `private CSharpDecompiler GetDecompiler(string fileName)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:430-510`
- **可见性**: private
- **返回值**: ready-to-use `CSharpDecompiler`
- **抛出/异常**: `FileNotFoundException`, `BadImageFormatException`
- **调用了**: `PEFile` ctor, `UniversalAssemblyResolver` ctor, `DecompilerSettings` ctor (with `-ds` overrides)
- **简要说明**: builds the `CSharpDecompiler` from a file path

#### `private void ApplySettingOverride(DecompilerSettings settings, string name, string value)`

- **位置**: `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs:1`
- **可见性**: private
- **调用了**: reflection on `DecompilerSettings` properties
- **简要说明**: applies `-ds name=value` override

### 28 `[Option]` properties

Each CLI flag is a `[Option]` property on `ILSpyCmdProgram`. The properties (with short aliases) are listed in [06_build_and_run.md](../06_build_and_run.md#ilspycmd-cli-flags-28-total). They cover:

- File selection (`<assembly>` positional, `-t`)
- Output (`-o`)
- Modes (`-p`, `-il`, `--il-sequence-points`, `-genpdb`, `-usepdb`)
- Listing (`-l`, `--list-resources`)
- Resource extraction (`--resource`, `--decompile-baml`)
- Language (`-lv`)
- Settings (`--ilspy-settingsfile`, `-ds`)
- Reference paths (`-r`)
- Toggles (`--no-dead-code`, `--no-dead-stores`, `--nested-directories`, `--disable-updatecheck`)
- Diagrammer (`--generate-diagrammer`, `--generate-diagrammer-include`, `--generate-diagrammer-exclude`, `--generate-diagrammer-report-excluded`, `--generate-diagrammer-docs`, `--generate-diagrammer-strip-namespaces`, `--generate-diagrammer-json-only`)
- Misc (`-v|--version`, `-d|--dump-package`)

## `BamlAwareWholeProjectDecompiler.cs`

### `BamlAwareWholeProjectDecompiler` (public class) — `ICSharpCode.ILSpyCmd/BamlAwareWholeProjectDecompiler.cs`

- **可见性**: public
- **简要说明**: extends `WholeProjectDecompiler` to translate `.g.resources` BAML.

#### `public override ProjectId DecompileProject(MetadataFile module, string targetDir, TextWriter writer)`

- **位置**: `BamlAwareWholeProjectDecompiler.cs:1`
- **可见性**: public, override
- **调用了**: base `DecompileProject`, then post-processes `.g.resources` -> `.xaml`
- **简要说明**: `-p --decompile-baml` branch

## `ProgramExitCodes.cs`

### `ProgramExitCodes` (public static class) — `ICSharpCode.ILSpyCmd/ProgramExitCodes.cs`

- **可见性**: public, static
- **简要说明**: exit-code constants — `EX_SOFTWARE` (70), `EX_DATAERR` (65), `EX_USAGE` (64), `EX_OK` (0), etc. (BSD sysexits.h names)

## `TypesParser.cs`

### `TypesParser` (public static class) — `ICSharpCode.ILSpyCmd/TypesParser.cs`

- **可见性**: public, static
- **简要说明**: parses `-l c,i,s,d,e` -> `TypeKind` set.

#### `public static HashSet<TypeKind> Parse(string spec)`

- **位置**: `TypesParser.cs:1`
- **可见性**: public, static
- **参数**: `-l` argument (e.g. `"c,i"`)
- **返回值**: set of `TypeKind`s
- **简要说明**: `c`=class, `i`=interface, `s`=struct, `d`=delegate, `e`=enum

## `DotNetToolUpdateChecker.cs`

### `DotNetToolUpdateChecker` (public class) — `ICSharpCode.ILSpyCmd/DotNetToolUpdateChecker.cs`

- **可见性**: public
- **简要说明**: probes NuGet for a newer version of `ilspycmd`.

#### `public async Task<bool> CheckForUpdateAsync()`

- **位置**: `DotNetToolUpdateChecker.cs:1`
- **可见性**: public, async
- **返回值**: true if newer version is available
- **简要说明**: skipped when `--disable-updatecheck`

## `ResourceExtensions.cs`

### `ResourceExtensions` (public static class) — `ICSharpCode.ILSpyCmd/ResourceExtensions.cs`

- **可见性**: public, static
- **简要说明**: resource enumeration + extraction helpers.

#### `public static IEnumerable<string> EnumerateResourcePaths(MetadataFile module)`

- **位置**: `ResourceExtensions.cs:1`
- **简要说明**: list all resources

#### `public static Stream? TryGetResource(MetadataFile module, string name)`

- **位置**: `ResourceExtensions.cs:1`
- **简要说明**: open one resource

#### `public static string DecompileBaml(Stream bamlStream)`

- **位置**: `ResourceExtensions.cs:1`
- **简要说明**: BAML -> XAML (uses `ICSharpCode.BamlDecompiler`)

## `ValidationAttributes.cs`

- **位置**: `ICSharpCode.ILSpyCmd/ValidationAttributes.cs`
- **简要说明**: validation attrs for `McMaster.Extensions.CommandLineUtils`

## `AsContainer/`

- **位置**: `ICSharpCode.ILSpyCmd/AsContainer/`
- **简要说明**: NuGet `.nupkg` handling

## `README.md`

- **位置**: `ICSharpCode.ILSpyCmd/README.md`
- **简要说明**: package README