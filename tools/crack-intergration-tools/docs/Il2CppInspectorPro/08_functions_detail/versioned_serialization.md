# 08 · `VersionedSerialization` + Roslyn 生成器

> 文件：
> - `VersionedSerialization/IReadable.cs`, `IReader.cs`, `ISeekableReader.cs`, `INonSeekableReader.cs`
> - `VersionedSerialization/ReadableExtensions.cs`, `SeekableReaderExtensions.cs`
> - `VersionedSerialization/ReaderConfig.cs`, `ReaderExtensions.cs`
> - `VersionedSerialization/Reader.cs`
> - `VersionedSerialization/Reader\`1.cs`
> - `VersionedSerialization/StructVersion.cs`
> - `VersionedSerialization/Impl/EndianReader.cs`
> - `VersionedSerialization/Impl/SpanReader.cs`
> - `VersionedSerialization/Attributes/VersionedStructAttribute.cs`
> - `VersionedSerialization/Attributes/VersionConditionAttribute.cs`
> - `VersionedSerialization/Attributes/NativeIntegerAttribute.cs`
> - `VersionedSerialization.Generator/ObjectSerializationGenerator.cs`
> - `VersionedSerialization.Generator/StructVersion.cs`
> - `VersionedSerialization.Generator/Analyzer/InvalidVersionAnalyzer.cs`
> - `VersionedSerialization.Generator/Models/{ObjectSerializationInfo,PropertySerializationInfo,PropertyType,VersionCondition}.cs`
> - `VersionedSerialization.Generator/Utils/{CodeGenerator,HashCode,ImmutableEquatableArray,Constants}.cs`

---

## `StructVersion.ctor`

- **签名**: `public StructVersion(int major = 0, int minor = 0, string? tag = null)`
- **位置**: `VersionedSerialization/StructVersion.cs:~10`
- **可见性**: public
- **简要说明**: 值对象 (major, minor, tag)

## `StructVersion.TryParse` / `Parse`

- **签名**: `static bool TryParse(string?, IFormatProvider?, out StructVersion)` / `static StructVersion Parse(string, IFormatProvider? = null)`
- **位置**: `StructVersion.cs:~40-65`
- **可见性**: public static
- **调用**: il2cpp VersionedSerialization 化的所有结构读取

## `StructVersion.HasTag`

- **签名**: `bool HasTag(string tag)`
- **位置**: `StructVersion.cs:~30`
- **可见性**: public

## `StructVersion.AsDouble`

- **签名**: `double AsDouble => Major + Minor / 10.0`
- **位置**: `StructVersion.cs:~25`
- **可见性**: public

## `StructVersion` operators

- **签名**: `operator ==/!=/>/</>=/<=`
- **位置**: `StructVersion.cs:~75-90`
- **可见性**: public static

---

## `IReadable.Read<TReader>` / `Size`

- **签名**:
  - `void Read<TReader>(ref Reader<TReader> reader, in StructVersion version = default) where TReader : IReader, allows ref struct`
  - `static abstract int Size(in StructVersion version, in ReaderConfig config)`
- **位置**: `VersionedSerialization/IReadable.cs`
- **可见性**: public abstract
- **调用**: 所有 il2cpp `Next/Metadata/*` / `Next/BinaryMetadata/*`

## `ReaderConfig.ctor`

- **签名**: `ReaderConfig(bool is32Bit)`
- **位置**: `VersionedSerialization/ReaderConfig.cs:~5`
- **可见性**: public

## `Reader<TReader>.ctor`

- **签名**: `Reader(TReader inner, ReaderConfig config)`
- **位置**: `VersionedSerialization/Reader\`1.cs:~20`
- **可见性**: public

## `Reader<TReader>.ReadVersionedObject<T>`

- **签名**: `T ReadVersionedObject<T>(in StructVersion version) where T : IReadable, new()`
- **位置**: `Reader\`1.cs:~40`
- **可见性**: public
- **调用了**: `T.Read(ref this, version)`
- **调用**: `Metadata.FromStream`、`Il2CppBinary.PrepareMetadata`

## `Reader` (static helpers)

- **位置**: `VersionedSerialization/Reader.cs`
- **可见性**: public static
- **简要说明**: 提供 `ReadFromFile<T>(path, version)` 等快捷方法

## `LittleEndianSeekableReader<T>` / `BigEndianSeekableReader<T>`

- **位置**: `VersionedSerialization/Impl/EndianReader.cs:40 / :120`
- **可见性**: public
- **简要说明**: 端序 wrapper

## `SpanReader`

- **位置**: `VersionedSerialization/Impl/SpanReader.cs:~15`
- **可见性**: public

---

## `VersionedStructAttribute`

- **签名**: `[AttributeUsage(AttributeTargets.Class | Struct | Record)] sealed class VersionedStructAttribute : Attribute`
- **位置**: `VersionedSerialization/Attributes/VersionedStructAttribute.cs`
- **可见性**: public
- **调用**: Roslyn 生成器 `ForAttributeWithMetadataName`

## `VersionConditionAttribute`

- **签名**: `[AttributeUsage(Property | Field, AllowMultiple=true)] sealed class VersionConditionAttribute : Attribute { string LessThan, GreaterThan, EqualTo, LessThanOrEqual, GreaterThanOrEqual, IncludingTag, ExcludingTag }`
- **位置**: `Attributes/VersionConditionAttribute.cs`
- **可见性**: public

## `NativeIntegerAttribute`

- **签名**: `[AttributeUsage(Property | Field)] sealed class NativeIntegerAttribute : Attribute`
- **位置**: `Attributes/NativeIntegerAttribute.cs`
- **可见性**: public
- **简要说明**: 标 32/64 位指针类字段

---

## `ObjectSerializationGenerator.Initialize`

- **签名**: `public void Initialize(IncrementalGeneratorInitializationContext context)`
- **位置**: `VersionedSerialization.Generator/ObjectSerializationGenerator.cs:~30`
- **可见性**: public override
- **调用了**:
  - `context.RegisterPostInitializationOutput(...)` (注入 `VersionedStruct` 等 attribute)
  - `context.RegisterSourceOutput(context.SyntaxProvider.ForAttributeWithMetadataName(...), ...)`
- **简要说明**: Roslyn 生成器入口

## `ObjectSerializationGenerator.ParseSerializationInfo`

- **签名**: `private static ObjectSerializationInfo ParseSerializationInfo(GeneratorAttributeSyntaxContext context, CancellationToken)`
- **位置**: `ObjectSerializationGenerator.cs:~80`
- **可见性**: private static
- **调用了**: 解析每个 property + `[VersionCondition]` + `[NativeInteger]`

## `ObjectSerializationGenerator.EmitCode`

- **签名**: `private static void EmitCode(SourceProductionContext, ObjectSerializationInfo)`
- **位置**: `ObjectSerializationGenerator.cs:~250`
- **可见性**: private static
- **副作用**: 生成代码：
  - `Versions` static class（带所有出现过的版本常量）
  - `Read<TReader>(ref Reader<TReader> reader, in StructVersion version)` 方法体
  - `static int IReadable.Size(in StructVersion, in ReaderConfig)`

---

## `InvalidVersionAnalyzer.Initialize`

- **签名**: `public override void Initialize(AnalysisContext context)`
- **位置**: `VersionedSerialization.Generator/Analyzer/InvalidVersionAnalyzer.cs:~15`
- **可见性**: public override
- **调用了**: `context.RegisterSymbolAction(..., SymbolKind.Property)`
- **简要说明**: 校验 `[VersionCondition]` 参数合法性

## `HashCode` (Burst-friendly)

- **位置**: `VersionedSerialization.Generator/Utils/HashCode.cs`
- **可见性**: public static
- **简要说明**: Burst 兼容的 hash

## `ImmutableEquatableArray<T>`

- **签名**: `class ImmutableEquatableArray<T> : IEquatable<...>, IEnumerable<T>`
- **位置**: `Utils/ImmutableEquatableArray.cs:~20`
- **可见性**: public
- **简要说明**: Roslyn 生成器常用不可变集合

## `CodeGenerator` / `Constants`

- **位置**: `Utils/CodeGenerator.cs` / `Utils/Constants.cs`
- **可见性**: internal
- **简要说明**: 生成器 plumbing