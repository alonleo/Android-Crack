# 08 — Functions Detail: Outputs (Decompiler / StructGenerator / DummyAssemblyExporter)

本文件覆盖 `Outputs/` 目录的所有函数。

---

## `Il2CppDecompiler` (`Outputs/Il2CppDecompiler.cs`)

### `Il2CppDecompiler` 构造器
- **位置**：`Il2CppDumper/Outputs/Il2CppDecompiler.cs:17`
- **可见性**：public
- **副作用**：保存 executor/metadata/il2Cpp；初始化 `methodModifiers` 缓存

### `Il2CppDecompiler.Decompile(Config config, string outputDir)`
- **位置**：`Il2CppDumper/Outputs/Il2CppDecompiler.cs:25`
- **可见性**：public
- **副作用**：写 `<outputDir>/dump.cs`
- **抛出**：try/catch 整段，外层写入 `/* <exception> */`
- **调用**：被 `Program.Dump:259` 调用
- **调用了**：`GetCustomAttribute`、`GetModifiers`
- **说明**：按 imageDef → typeDef 顺序写 namespace / class / field / property / method / GenericInstMethod 注释

### `Il2CppDecompiler.GetCustomAttribute(Il2CppImageDefinition, int customAttributeIndex, uint token, string padding = "")`
- **位置**：`Il2CppDumper/Outputs/Il2CppDecompiler.cs:399`
- **可见性**：public
- **返回值**：attribute 字符串；空表示无
- **调用**：`Decompile:65,126,211,249`
- **说明**：v<21 直接返回空；v<29 走旧 attributeTypeRanges + methodPointer 注释；v>=29 走 `CustomAttributeDataReader.GetStringCustomAttributeData`

### `Il2CppDecompiler.GetModifiers(Il2CppMethodDefinition)`
- **位置**：`Il2CppDumper/Outputs/Il2CppDecompiler.cs:451`
- **可见性**：public
- **返回值**：`public/private/... static abstract virtual override sealed override extern` 等
- **调用**：`Decompile:217,224,270`
- **说明**：缓存到 `methodModifiers` dict

---

## `StructGenerator` (`Outputs/StructGenerator.cs`)

### `StructGenerator` 构造器
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:35`
- **可见性**：public
- **副作用**：保存 executor/metadata/il2Cpp；初始化多个缓存 dict

### `StructGenerator.WriteScript(string outputDir)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:42`
- **可见性**：public
- **副作用**：写 `<outputDir>/script.json`、`stringliteral.json`、`il2cpp.h`
- **调用**：被 `Program.Dump:265` 调用
- **调用了**：`AddStruct`、`CreateStructNameDic`、`AddMetadataUsage*`、`FixName`、`ParseType`、`GetMethodTypeSignature`、`AddGenericClassStruct`、`RecursionStructInfo`、`GenerateMethodInfo`、`GenerateRGCTX`、`GetMethodSpecName`、`GetMethodSpecGenericContext`
- **说明**：整个 il2cpp.h 输出阶段的主调度。

### `StructGenerator.AddMetadataUsageTypeInfo(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:434`
- **可见性**：private
- **说明**：把 `kIl2CppMetadataUsageTypeInfo` 写成 `<TypeName>_TypeInfo`，签名 `Il2CppClass*`

### `StructGenerator.AddMetadataUsageIl2CppType(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:453`
- **说明**：`<TypeName>_var`，签名 `Il2CppType*`

### `StructGenerator.AddMetadataUsageMethodDef(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:464`
- **说明**：`Method$<TypeName>.<MethodName>()`

### `StructGenerator.AddMetadataUsageFieldInfo(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:482`
- **说明**：`Field$<TypeName>.<FieldName>`

### `StructGenerator.AddMetadataUsageStringLiteral(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:495`
- **说明**：写入 `ScriptString{Address, Value}`，最后由 `WriteScript` 写出 `stringliteral.json`

### `StructGenerator.AddMetadataUsageMethodRef(ScriptJson, uint, ulong)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:503`
- **说明**：`Method$<SpecTypeName>.<SpecMethodName>()`

### `StructGenerator.FixName(string)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:521`
- **可见性**：private static
- **副作用**：keyword 加下划线前缀；specialKeyword 双下划线；开头数字加下划线；非法字符 → `_`
- **调用**：被大量调用（每写一个 field/type/method 都过 FixName）

### `StructGenerator.ParseType(Il2CppType, Il2CppGenericContext = null)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:542`
- **可见性**：private
- **返回值**：C 类型字符串（`int32_t`、`MyType_o*`、`MyType_o` 等）
- **调用**：`WriteScript:100,124,164,189,195,210`、`AddStruct:753`、`GenerateMethodInfo:0`、`GetIl2CppStructName:610,648`
- **说明**：switch Il2CppTypeEnum → C 字符串；处理 `GenericContext` 来物化 VAR/MVAR

### `StructGenerator.GetMethodTypeSignature(List<Il2CppTypeEnum>)`
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:678`
- **可见性**：public static
- **返回值**：IDA 风格单字符签名（v/i/j/f/d…）
- **调用**：`WriteScript:137,223`

### `StructGenerator.AddStruct(Il2CppTypeDefinition)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:697`
- **副作用**：填充 `structInfoList`

### `StructGenerator.AddGenericClassStruct(ulong pointer)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:709`

### `StructGenerator.AddParents(Il2CppTypeDefinition, StructInfo)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:722`

### `StructGenerator.AddFields(Il2CppTypeDefinition, StructInfo, Il2CppGenericContext)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:737`

### `StructGenerator.AddVTableMethod(StructInfo, Il2CppTypeDefinition)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:775`

### `StructGenerator.AddRGCTX(StructInfo, Il2CppTypeDefinition)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:812`

### `StructGenerator.GenerateRGCTX(string imageName, Il2CppMethodDefinition)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:858`

### `StructGenerator.ParseArrayClassStruct(Il2CppType, Il2CppGenericContext)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:905`
- **副作用**：追加到 `arrayClassHeader`

### `StructGenerator.GetTypeDefinition(Il2CppType)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:916`

### `StructGenerator.CreateStructNameDic(Il2CppTypeDefinition)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:949`
- **副作用**：填 `structNameDic[typeDef] = uniqueName`

### `StructGenerator.GetUniqueName(string)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:957`
- **副作用**：可能加 `_<n>` 后缀确保唯一

### `StructGenerator.RecursionStructInfo(StructInfo)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:968`
- **返回值**：完整 C struct 字符串（含 `_Fields`、`_RGCTXs`、`_VTable`、`_c`、`_o`、`_StaticFields`）
- **调用**：`WriteScript:392`

### `StructGenerator.GetIl2CppStructName(Il2CppType, Il2CppGenericContext = null)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:1128`
- **返回值**：结构体名（不含 `_o` 后缀）

### `StructGenerator.IsValueType(Il2CppType, Il2CppGenericContext)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:1224`

### `StructGenerator.IsCustomType(Il2CppType, Il2CppGenericContext)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:1270`

### `StructGenerator.GenerateMethodInfo(string methodInfoName, string structTypeName, List<StructRGCTXInfo>)` (private)
- **位置**：`Il2CppDumper/Outputs/StructGenerator.cs:1336`
- **副作用**：追加到 `methodInfoHeader`
- **调用**：`WriteScript:156`

### 静态字段
| 字段 | 行 |
|------|----|
| `methodInfoCache` (static HashSet<ulong>) | 28 |
| `keyword` (static HashSet<string>) | 29 |
| `specialKeywords` (static HashSet<string>) | 32 |

---

## `DummyAssemblyExporter` (`Outputs/DummyAssemblyExporter.cs`)

### `DummyAssemblyExporter.Export(Il2CppExecutor, string outputDir, bool addToken)` (static)
- **位置**：`Il2CppDumper/Outputs/DummyAssemblyExporter.cs:7`
- **可见性**：public static
- **副作用**：`Directory.SetCurrentDirectory(outputDir)`；创建 `DummyDll/`；实例化 `DummyAssemblyGenerator`；循环所有 `assemblies[i]` 写盘
- **调用**：被 `Program.Dump:271` 调用

---

## `ScriptJson` 与 JSON 数据类 (`Outputs/ScriptJson.cs`)

### `ScriptJson`
POCO。字段：
- `ScriptMethod: List<ScriptMethod>`
- `ScriptString: List<ScriptString>`
- `ScriptMetadata: List<ScriptMetadata>`
- `ScriptMetadataMethod: List<ScriptMetadataMethod>`
- `Addresses: ulong[]`

### `ScriptMethod`
- `Address: ulong`
- `Name: string` — `TypeFullName$$MethodName`
- `Signature: string`
- `TypeSignature: string`

### `ScriptString`
- `Address: ulong`
- `Value: string`

### `ScriptMetadata`
- `Address: ulong`
- `Name: string`
- `Signature: string`

### `ScriptMetadataMethod`
- `Address: ulong`
- `Name: string`
- `MethodAddress: ulong`

---

## `StructInfo` 与辅助 (`Outputs/StructInfo.cs`)

### `StructInfo`
- `TypeName: string`
- `IsValueType: bool`
- `Parent: string`
- `Fields: List<StructFieldInfo>`
- `StaticFields: List<StructFieldInfo>`
- `VTableMethod: StructVTableMethodInfo[]`
- `RGCTXs: List<StructRGCTXInfo>`

### `StructFieldInfo`
- `FieldTypeName: string`
- `FieldName: string`
- `IsValueType: bool`
- `IsCustomType: bool`

### `StructVTableMethodInfo`
- `MethodName: string`

### `StructRGCTXInfo`
- `Type: Il2CppRGCTXDataType`
- `TypeName / ClassName / MethodName: string`

---

## `Il2CppConstants` (`Outputs/Il2CppConstants.cs`)

POCO — TypeAttributes / FieldAttributes / MethodAttributes / PARAM_ATTRIBUTE 常量集合。

```
FIELD_ATTRIBUTE_*           (8-20)
METHOD_ATTRIBUTE_*          (24-43)
TYPE_ATTRIBUTE_*            (48-64)
PARAM_ATTRIBUTE_*           (69-71)
```

调用：`Il2CppDecompiler.Decompile` 中所有 visibility / static / abstract / sealed / pInvoke 判断都引用此处常量。

---

## `HeaderConstants` (`Outputs/HeaderConstants.cs`)

`HeaderConstants` 是一个静态类，持有大段字符串字面量供 `StructGenerator.WriteScript` 拼接 `il2cpp.h`：

| 字段 | 行 |
|------|----|
| `GenericHeader` | 5 |
| `HeaderV29` | 45 |
| `HeaderV27` | 154 |
| `HeaderV240` (v23/24) | （约 280） |
| `HeaderV241` | （约 350） |
| `HeaderV242` (v24.2~24.5) | （约 420） |
| `HeaderV22` | （约 540） |

每个 header 包含 `Il2CppClass_1 / Il2CppClass_2 / Il2CppClass / Il2CppArrayBounds / MethodInfo` 的版本特定 POD 定义。