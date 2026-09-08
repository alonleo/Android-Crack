# 08 — `dnSpy.Decompiler` (decompiler glue)

This file documents the decompiler glue (`dnSpy/dnSpy/dnSpy.Decompiler/`). It is small but central: it bridges dnlib model objects to the embedded ILSpy 5 / NRefactory 5 decompiler, formats C# output, and resolves MSBuild SDKs.

## `DecompilerBase.cs`

### `DecompilerBase` (public abstract class) — `dnSpy.Decompiler/DecompilerBase.cs`

- **位置**: `dnSpy.Decompiler/DecompilerBase.cs:1`
- **可见性**: public, abstract
- **简要说明**: base class for language backends (C#, VB, IL). Implements `IDecompiler` partially.

#### `public override DecompilerSettingsBase Settings { get; }`

- **位置**: `DecompilerBase.cs:1`
- **可见性**: public, override
- **简要说明**: per-decompiler settings

#### `public abstract Guid GenericGuid { get; }`

- **位置**: `DecompilerBase.cs:1`
- **可见性**: public, abstract
- **简要说明**: `IDecompiler.GenericGuid` — stable id for the language family

#### `public abstract Guid UniqueGuid { get; }`

- **位置**: `DecompilerBase.cs:1`
- **可见性**: public, abstract
- **简要说明**: `IDecompiler.UniqueGuid` — stable id for this specific decompiler

## `CSharp/CSharpFormatter.cs` (~900 LoC)

### `CSharpFormatter` (struct) — `dnSpy.Decompiler/CSharp/CSharpFormatter.cs`

- **位置**: `dnSpy.Decompiler/CSharp/CSharpFormatter.cs:1`
- **可见性**: internal, struct
- **简要说明**: struct-based C# text formatter (writes tokens to `ITextColorWriter`). The big idea: pass-by-value struct avoids virtual dispatch for the inner formatter loop.

#### `public void WriteName(...)` / `WriteType(...)`

- **位置**: `CSharpFormatter.cs:1`
- **可见性**: public
- **调用了**: `ITextColorWriter.Write(...)`, `IWriter.*`
- **简要说明**: emit one name / type into the output

#### `public void WriteMethod(MethodDef, ...)`

- **位置**: `CSharpFormatter.cs:1`
- **可见性**: public
- **简要说明**: emit one method declaration

#### `public void WriteProperty(PropertyDef, ...)`

- **位置**: `CSharpFormatter.cs:1`
- **可见性**: public
- **简要说明**: emit one property declaration

#### `public void WriteEvent(EventDef, ...)`

- **位置**: `CSharpFormatter.cs:1`
- **可见性**: public
- **简要说明**: emit one event declaration

#### `public void WriteField(FieldDef, ...)`

- **位置**: `CSharpFormatter.cs:1`
- **可见性**: public
- **简要说明**: emit one field declaration

## `IL/ILLanguageHelper.cs`

### `ILLanguageHelper` (public class) — `dnSpy.Decompiler/IL/ILLanguageHelper.cs`

- **位置**: `ILLanguageHelper.cs:1`
- **可见性**: public
- **简要说明**: shared helpers for the IL decompiler

#### `public string GetOpCodeName(OpCode opCode)`

- **位置**: `ILLanguageHelper.cs:1`
- **可见性**: public
- **简要说明**: name for an opcode (with size suffix)

#### `public string FormatInstruction(...)` (overloads)

- **位置**: `ILLanguageHelper.cs:1`
- **可见性**: public
- **简要说明**: format one IL instruction

## `IL/InstructionBytesReader.cs` / `ModifiedInstructionBytesReader.cs` / `OriginalInstructionBytesReader.cs`

- **位置**: `dnSpy.Decompiler/IL/`
- **简要说明**: IL byte-code reader variants. "Original" reads the unmodified bytes; "Modified" reads after user edits.

## `IL/InstructionUtils.cs`

- **位置**: `dnSpy.Decompiler/IL/InstructionUtils.cs`
- **简要说明**: IL instruction helpers

## `MSBuild/`

- **位置**: `dnSpy.Decompiler/MSBuild/`
- **简要说明**: MSBuild SDK resolver for project export (decompile-to-csproj flow)

### `MSBuildSdkInfo`

- **位置**: `dnSpy.Decompiler/MSBuild/MSBuildSdkInfo.cs`
- **简要说明**: SDK metadata

### `MSBuildSdkResolver`

- **位置**: `dnSpy.Decompiler/MSBuild/MSBuildSdkResolver.cs`
- **简要说明**: discovers MSBuild SDKs on disk

## `Settings/`

- **位置**: `dnSpy.Decompiler/Settings/`
- **简要说明**: decompiler settings page UI

### `DecompilerSettingsPage`

- **位置**: `dnSpy.Decompiler/Settings/DecompilerSettingsPage.cs`
- **简要说明**: settings page class

### `DecompilerAppSettingsPageContainer`

- **位置**: `dnSpy.Decompiler/Settings/`
- **简要说明**: settings-page container

## `TargetFrameworkInfo.cs` / `TargetFrameworkUtils.cs`

- **位置**: `dnSpy.Decompiler/`
- **简要说明**: target-framework info

## `FilenameUtils.cs`

- **位置**: `dnSpy.Decompiler/FilenameUtils.cs`
- **简要说明**: filename helpers

## `FormatterMethodInfo.cs`

- **位置**: `dnSpy.Decompiler/FormatterMethodInfo.cs`
- **简要说明**: per-method formatter state

## `TypeFormatterUtils.cs`

- **位置**: `dnSpy.Decompiler/TypeFormatterUtils.cs`
- **简要说明**: type formatter helpers

## `Utils/`

- **位置**: `dnSpy.Decompiler/Utils/`
- **简要说明**: misc utilities