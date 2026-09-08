# 06 — Build and Run

## Build scripts

| Script | Purpose |
|---|---|
| `dnSpy/build.ps1` | Wraps MSBuild (`-NoMsbuild` to skip MSBuild) |
| `dnSpy/clean-all.cmd` | Cleans obj/bin |
| `dotnet build dnSpy/dnSpy/dnSpy/dnSpy.csproj` | Direct build (works) |

## Solution

`dnSpy/dnSpy/dnSpy.sln` (58 KB) includes every project. Use it for full builds.

## Multi-target

`dnSpyCommon.props` sets `<TargetFrameworks>net48;net5.0-windows</TargetFrameworks>` for most projects. `net48` uses `<HasCOMReference>true</HasCOMReference>` to enable COM references (e.g. `IWshRuntimeLibrary`); `net5.0-windows` strips those.

## Runtime IDs

`<RuntimeIdentifiers>win-x86;win-x64</RuntimeIdentifiers>` — dnSpy is Windows-only.

## Common package versions (`DnSpyCommon.props`)

- `dnlib 3.3.2` — metadata reader/writer (obfuscation-tolerant)
- `Iced 1.9.0` — x86/x64 disassembler
- `MSBuild 16.7.0`
- `MSDiagRuntime (Microsoft.Diagnostics.Runtime / ClrMD) 1.1.142101` — crash dumps
- `MSVSComposition 16.4.11` — VS-MEF
- `MSVSIntellisense 15.5.27130`
- `MSVSText 15.5.27130` — editor platform (re-implemented in `dnSpy/dnSpy/Text/`)
- `Newtonsoft.Json 12.0.3`
- `Ookii.Dialogs.Wpf 3.0.1` — open-file dialogs
- `Roslyn 2.10.0` — `Microsoft.CodeAnalysis` (vendored)
- `SCComposition 4.6.0`
- `DiaSymReader 1.7.0`
- `<SatelliteResourceLanguages>cs;de;es;es-ES;fa;fr;hu;it;pt-BR;pt-PT;ru;tr;uk;zh-CN</SatelliteResourceLanguages>` — Crowdin translations

## Signing

`<SignAssembly>true</SignAssembly>` + `dnSpy.snk` (the snk is checked in).

## Build sequence (typical)

```bash
# Full build
dotnet build dnSpy/dnSpy/dnSpy/dnSpy.sln -c Release

# Just the main app
dotnet build dnSpy/dnSpy/dnSpy/dnSpy.csproj -c Release

# Run after build
dotnet run --project dnSpy/dnSpy/dnSpy/dnSpy.csproj -- --multiple sample.dll
```

## Run the GUI

```bash
dotnet run --project dnSpy/dnSpy/dnSpy/dnSpy.csproj
```

or after a build:

```bash
dnSpy/bin/Release/net5.0-windows/dnSpy.exe sample.dll
```

### GUI CLI flags (~25 flags)

Parsed in `dnSpy/dnSpy/dnSpy/MainApp/AppCommandLineArgs.cs`:

| Flag | Meaning |
|---|---|
| `--settings-file <path>` | Override settings XML path |
| `--multiple` | Allow multiple instances |
| `--dont-activate` / `--no-activate` | Don't activate existing instance |
| `-l` / `--language <id-or-guid>` | Switch decompiler language (matches `UniqueNameUI`, `GenericNameUI`, `GenericGuid`, `UniqueGuid`) |
| `--culture <name>` | Force UI culture (`en-US`, `de`, `zh-CN`) |
| `--select <member-id>` | Select a member |
| `--new-tab` | Open an empty tab |
| `--search <text>` | Pre-fill the search box |
| `--search-for <type>` | Search filter (types / methods / fields / properties / events / namespaces / strings / assembly refs) |
| `--search-in <scope>` | Search scope (all loaded / current assembly / ...) |
| `--theme <name>` | Blue / Dark / Light / Dark high contrast |
| `--dont-load-files` / `--no-load-files` | Skip auto-loading CLI-provided files |
| `--full-screen` / `--not-full-screen` | Toggle full-screen |
| `--show-tool-window <guid>` | Show tool window by GUID |
| `--hide-tool-window <guid>` | Hide tool window by GUID |
| `--show-startup-time` | Print startup time at splash end |
| `-p` / `--pid <pid>` | Attach to process (decimal or `0x`/`&H` hex) |
| `-e <debugEvent>` | Set debug event |
| `--jdinfo <jit-debug-info>` | JIT-debug-info token for attach |
| `-pn` / `--process-name <name>` | Attach to process by name |
| `--extension-directory <dir>` | Additional extension directory |
| (positional) | Filenames to open |
| `-h` / `--help` | Print help |
| `<arg>:<value>` | Free-form user argument stored in `userArgs` dict |

IPC: `WM_COPYDATA` (msg 0x4A) with magic header `0x11C9B152` for `--multiple`-less single-instance forwarding. See `App.xaml.cs:411-470`.

## Debug build (debug-only features)

| Feature | Source | What you see |
|---|---|---|
| Cached MEF composition | `MainApp/CachedMefInfo.cs` | Speeds up repeat startups (saved to `<profileDir>/dnSpy-mef-info.bin`) |
| Multicore-JIT | `MainApp/StartUpClass.cs:24-32` | `ProfileOptimization.StartProfile("startup.profile")` |
| VS-MEF cached composition | `MainApp/CachedMefInfo.cs` | Skips re-discovery on subsequent runs |
| Anti-anti-debug | `dnSpy.Debugger.DotNet.CorDebug/AntiAntiDebug/` | P/Invoke patches |
| DAC support | `dnSpy.Debugger.DotNet.CorDebug/DAC/` | Crash dump inspection |

## Build for distribution

```bash
dotnet publish dnSpy/dnSpy/dnSpy/dnSpy.csproj -c Release -r win-x64 --self-contained
```

The publish output includes the `Extensions/` directory plus all `*.x.dll`s.

## Embedding (advanced)

dnSpy is primarily a Windows desktop tool, but its decoupled contract layer (`dnSpy.Contracts.DnSpy`) is reusable. The two main embeddable surfaces are:

1. **Decompiler engine** — `dnSpy.Decompiler.ILSpy.Core.CSharp.CSharpDecompiler` (525 LoC) is an embedded ILSpy 5 + NRefactory 5 decompiler, usable independently of dnSpy.
2. **dnlib-based assembly editing** — `dnSpy.AsmEditor` + dnlib 3.3.2 give you the same edit-and-save capability as the GUI, but only the model layer (no UI).

For new projects, the recommendation is usually to use the newer ILSpy (`ICSharpCode.Decompiler` NuGet) + Roslyn + dnlib directly rather than embedding dnSpy components — the vendored Roslyn 2.10.0 stack is a maintenance burden.