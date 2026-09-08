# 06 — Build and Run

## Build scripts (use these — bare `dotnet build` will prune `packages.lock.json`)

| Script | Purpose | Notes |
|---|---|---|
| `restore.ps1` | Restore NuGet packages | Passes `-p:RestoreEnablePackagePruning=false` to keep lock files whole |
| `build.ps1` | Build the solution | Forwards args; targets `ILSpy.sln` |
| `publish.ps1` | Publish self-contained | Use for distribution |
| `updatedeps.ps1` | Regenerate `packages.lock.json` | Run after adding/bumping a `PackageReference` |
| `clean.ps1` | Clean `obj/` and `bin/` | |
| `BuildTools/format.ps1` | Run `dotnet format` | Mirrors the pre-commit hook |

## Solution filters

| Filter | Contents | Use case |
|---|---|---|
| `ILSpy.sln` | Everything | Full build (CI) |
| `ILSpy.Desktop.slnf` | Avalonia UI + tests + dependencies | GUI dev |
| `ILSpy.XPlat.slnf` | Decompiler libs + ilspycmd + tests (no UI) | Linux CI |
| `ILSpy.Installer.sln` | WiX packaging | Release |
| `ILSpy.VSExtensions.slnx` | VS 2022 extension | Extension dev |

## Central package management

`Directory.Packages.props` is the central manifest. Every `PackageReference` in any csproj must have a matching `PackageVersion` entry here. After adding a package, run `updatedeps.ps1` to refresh `packages.lock.json` files.

`Directory.Build.props` sets `RestorePackagesWithLockFile=true`; the core libraries also set `RestoreLockedMode=true`. This means a plain `restore` will FAIL until lock files are refreshed.

## Build sequence (typical)

```bash
pwsh restore.ps1                          # restore with correct flags
pwsh build.ps1 --no-restore               # build (Debug|Release via -Configuration)
pwsh updatedeps.ps1                       # only if you bumped dependencies
pwsh BuildTools/format.ps1                # mirror the pre-commit hook
```

## Run the GUI

```bash
dotnet run --project ILSpy/ILSpy.csproj -- --newinstance sample.dll
```

or after a build:

```bash
dotnet ILSpy/bin/Debug/net10.0/ILSpy.dll sample.dll
```

### GUI CLI flags

Parsed in `ILSpy/AppEnv/CommandLineArguments.cs:40-103`:

| Flag | Meaning |
|---|---|
| `--newinstance` | Start a new ILSpy even when single-instance is set |
| `-n\|--navigateto <TYPENAME>` | Navigate to a member by ID |
| `-s\|--search <SEARCHTERM>` | Search syntax `t:TypeName` / `m:Member` / `c:Constant` |
| `-l\|--language <LANGUAGEIDENTIFIER>` | Set the output language |
| `-c\|--config <CONFIGFILENAME>` | Override `ILSpy.xml` settings path |
| `--noactivate` | Don't activate existing single-instance window |
| (positional) | Assemblies to load |

## Run the CLI

```bash
dotnet run --project ICSharpCode.ILSpyCmd -- sample.dll -o out
```

Install as a .NET global tool:

```bash
dotnet tool install -g ilspycmd
ilspycmd sample.dll -o out.cs
```

### ilspycmd CLI flags (28 total)

Parsed in `ICSharpCode.ILSpyCmd/IlspyCmdProgram.cs`:

| Flag | Meaning |
|---|---|
| `<assembly>...` (positional, required) | Input assemblies |
| `-o\|--outputdir <dir>` | Output directory; required with `-p`; defaults to stdout |
| `-p\|--project` | Emit a compilable .csproj + per-type .cs files |
| `-t\|--type <fully-qualified>` | Only decompile the given type |
| `-il\|--ilcode` | Show IL instead of C# |
| `--il-sequence-points` | Show IL with sequence points (implies `-il`) |
| `-genpdb\|--generate-pdb` | Generate a portable PDB |
| `-usepdb\|--use-varnames-from-pdb <path?>` | Use PDB variable names |
| `-l\|--list <c,i,s,d,e>` | List entities of given kinds |
| `--list-resources` | List embedded resources |
| `--resource <name>` | Extract one resource (BAML -> XAML if `.baml`) |
| `--decompile-baml` | With `-p`, decompile BAML to XAML Page items |
| `-lv\|--languageversion <ver>` | CSharp1..CSharp13, Preview, Latest |
| `--ilspy-settingsfile <path>` | Custom ILSpy settings XML |
| `-ds\|--decompiler-setting name=value` | Per-decompiler-setting override (repeatable) |
| `-r\|--referencepath <path>` | Additional assembly resolution path (repeatable) |
| `--no-dead-code` / `--no-dead-stores` | Toggle transforms |
| `-d\|--dump-package` | Dump .nupkg assemblies to disk |
| `--nested-directories` | One folder per namespace |
| `--disable-updatecheck` | Skip NuGet version probe |
| `--generate-diagrammer` | HTML diagrammer output |
| `--generate-diagrammer-include <regex>` | Whitelist types |
| `--generate-diagrammer-exclude <regex>` | Blacklist types |
| `--generate-diagrammer-report-excluded` | Dump excluded types report |
| `--generate-diagrammer-docs <uri-or-path>` | XML doc comments |
| `--generate-diagrammer-strip-namespaces <space-separated>` | Strip namespaces from docs |
| `--generate-diagrammer-json-only` | Emit `model.json` only (dev mode) |
| `-v\|--version` | Print ilspycmd + Decompiler version |

Exit codes (`ProgramExitCodes.cs`): `EX_SOFTWARE` (70), `EX_DATAERR` (65), etc.

## Tests

```bash
dotnet test ILSpy.sln --report-trx
```

`ICSharpCode.Decompiler.Tests` ships with a heavy round-trip suite that requires the `ILSpy-tests/` git submodule (large, NOT checked out by default). Tests that need it call `Assert.Ignore` when the directory is absent — a green local run does NOT mean round-trip tests ran. To run them:

```bash
git submodule update --init ILSpy-tests
```

`ILSpy.Tests.Windows` is OS-gated to Windows (`net11.0-windows`); it will be skipped on Linux/macOS.

## Embedding ILSpy in a host

`ILSpy/Entry.cs` exposes a public facade. The recommended pattern:

```csharp
var entry = new ICSharpCode.ILSpy.Entry(...);
await entry.ShowAssemblies(new[] { "sample.dll" });
```

The engine itself can be embedded as a NuGet package:

```xml
<PackageReference Include="ICSharpCode.Decompiler" Version="..." />
```

Then construct a `CSharpDecompiler` directly:

```csharp
var decompiler = new CSharpDecompiler("sample.dll", new DecompilerSettings(LanguageVersion.Latest));
var tree = decompiler.DecompileWholeModuleAsSingleFile();
foreach (var type in tree.Types) {
    Console.WriteLine(type.ToString());
}
```

## Debug build (debug-only features)

| Feature | Source | What you see |
|---|---|---|
| `Stepper` | `CSharpDecompiler.Stepper` (`CSharpDecompiler.cs:180`) | Pause / step through ILAst + AST transforms |
| `DebugSteps` pane | `ILSpy/ViewModels/DebugStepsPaneModel.cs` | Side-by-side view of the ILAst after each transform |
| `StepLimitReachedException` | `DecompilerSettings.DecompilationMaxStepCount` | Thrown when a transform exceeds the limit |
| `CheckInvariant()` | DEBUG-only on `AstNode` and `ILFunction` | Asserts shape after each transform |
| ETW | `Instrumentation/DecompilerEventSource.cs` | Telemetry events (`DoDecompileMethod`, ...) |

## Targeting a different runtime

The GUI is `net10.0` only; cross-platform is implicit. To build for a different RID, pass `-r`:

```bash
dotnet publish ILSpy/ILSpy.csproj -c Release -r linux-x64 --self-contained
```

`ICSharpCode.Decompiler.csproj` declares all four RIDs (`win-x64;win-arm64;linux-x64;osx-arm64`) so the NuGet package ships native binaries for each.
## 工作区构建记录（中国大陆网络 · 2026-08-02）

> 详见 `../source-projects/ILSpy/CHECKSUM.md`。本工作区已将 **ilspycmd 11.0.0.9252** 构建到
> `tools/crack-intergration-tools/execable/ilspycmd/`（net10.0, linux-x64, 自包含 false，依赖 dotnet 10 runtime）。

### 使用
```bash
source tools/environments/env.sh
./tools/crack-intergration-tools/execable/ilspycmd/ilspycmd --version          # 11.0.0.9252
./tools/crack-intergration-tools/execable/ilspycmd/ilspycmd -l c <file>.dll     # 列出类
./tools/crack-intergration-tools/execable/ilspycmd/ilspycmd -t <Class> <file>.dll  # 反编译单类
```

### 中国大陆网络构建要点（踩坑）
1. **SDK 版本**：`global.json` 要求 .NET 11，本机只有 10 → 临时 `mv global.json global.json.bak`（在 worktree 副本操作，不碰 READONLY 源码）。
2. **NuGet 源**：上游 `NuGet.config` 的 `packageSourceMapping` 冲突 + nuget.org 下载被墙 → 改用华为云镜像 `https://mirrors.huaweicloud.com/repository/nuget/v3/index.json`。
3. **Roslyn 版本**：`Generators.csproj` 硬编码 `Microsoft.CodeAnalysis.CSharp 5.0.0`（预发布 5.8 需 Azure dotnet-tools 源，被墙）→ 改为本机缓存 `4.14.0`，同步改 `Directory.Packages.props` 的 `RoslynVersion`。
4. **pwsh 缺失**：`ILSpyUpdateAssemblyInfo` target 调 `pwsh` → 预写 `obj/update-assemblyinfo-last-commit-hash.txt`（内容=HEAD commit）使 Exec 跳过，并手动生成 `Properties/DecompilerVersionInfo.cs`。
5. **发布**：`dotnet publish ICSharpCode.ILSpyCmd/ICSharpCode.ILSpyCmd.csproj -c Release -r linux-x64 --self-contained false -p:RestoreLockedMode=false -o <repo>/tools/crack-intergration-tools/execable/ilspycmd`。
6. **清理**：`git worktree remove /tmp/ilspy-build --force`（worktree 副本，READMEONLY 源码零修改）。
