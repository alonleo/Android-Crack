# 08 — Functions Detail: Utils (Executor / Dummy / SectionHelper / CustomAttribute / PELoader)

本文件覆盖 `Utils/` 目录的所有函数。

---

## `Il2CppExecutor` (`Utils/Il2CppExecutor.cs`)

### `Il2CppExecutor` 构造器
- **签名**：`public Il2CppExecutor(Metadata metadata, Il2Cpp il2Cpp)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:36`
- **可见性**：public
- **副作用**：保存 metadata + il2Cpp；按版本聚合 `customAttributeGenerators[]`（v>=27 && v<29 时按 imageDef 从 `codeGenModules[i].customAttributeCacheGenerator` 读）
- **调用**：被 `Program.Dump:257` 调用

### `Il2CppExecutor.GetTypeName(Il2CppType, bool addNamespace, bool is_nested)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:61`
- **可见性**：public
- **返回值**：可读 C# 类型名
- **调用**：被 `Il2CppDecompiler:48,59,166,219,227,282,290`、`StructGenerator:437`、`DummyAssemblyGenerator:417` 大量调用
- **说明**：switch 各类（ARRAY/SZARRAY/PTR/VAR/MVAR/CLASS/VALUETYPE/GENERICINST），递归构造

### `Il2CppExecutor.GetTypeDefName(Il2CppTypeDefinition, bool addNamespace, bool genericParameter)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:149`
- **可见性**：public
- **调用**：`StructGenerator:68,69,83,468`、`DummyAssemblyGenerator:0`
- **说明**：与 `GetTypeName` 不同，此函数以 typeDef 为输入；嵌套类型加 `.` 前缀；含 `genericContainerIndex` 时追加 `<T1, T2>`

### `Il2CppExecutor.GetGenericInstParams(Il2CppGenericInst)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:181`
- **可见性**：public
- **调用**：`GetTypeName:134`、`GetMethodSpecName:213,219`

### `Il2CppExecutor.GetGenericContainerParams(Il2CppGenericContainer)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:193`
- **可见性**：public
- **调用**：`GetTypeName:139`、`GetTypeDefName:175`、`Il2CppDecompiler:276`

### `Il2CppExecutor.GetMethodSpecName(Il2CppMethodSpec, bool addNamespace = false)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:205`
- **可见性**：public
- **返回值**：(typeName, methodName)
- **调用**：`Il2CppDecompiler:377`、`StructGenerator:158,509,849,895`

### `Il2CppExecutor.GetMethodSpecGenericContext(Il2CppMethodSpec)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:224`
- **返回值**：`Il2CppGenericContext { class_inst, method_inst }`
- **调用**：`StructGenerator:162`

### `Il2CppExecutor.GetRGCTXDefinition(string imageName, Il2CppTypeDefinition)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:239`
- **返回值**：`Il2CppRGCTXDefinition[]`
- **调用**：`StructGenerator.AddRGCTX:815`

### `Il2CppExecutor.GetRGCTXDefinition(string imageName, Il2CppMethodDefinition)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:257`
- **调用**：`StructGenerator.GenerateRGCTX:861`

### `Il2CppExecutor.GetGenericClassTypeDefinition(Il2CppGenericClass)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:275`
- **说明**：v>=27 用 `Il2CppType` + `klassIndex`；否则用 `genericClass.typeDefinitionIndex`
- **调用**：`GetTypeName:97`、`StructGenerator:62,622,712,942`

### `Il2CppExecutor.GetTypeDefinitionFromIl2CppType(Il2CppType)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:293`
- **调用**：被广泛使用

### `Il2CppExecutor.GetGenericParameteFromIl2CppType(Il2CppType)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:307`
- **注意**：方法名拼写为 "Paramete"（少一个 r），是上游原版

### `Il2CppExecutor.GetSectionHelper()`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:321`
- **调用**：`StructGenerator:268`

### `Il2CppExecutor.TryGetDefaultValue(int typeIndex, int dataIndex, out object value)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:326`
- **调用**：`Il2CppDecompiler:169,320`、`DummyAssemblyGenerator:193,288`

### `Il2CppExecutor.GetConstantValueFromBlob(Il2CppTypeEnum, BinaryReader, out BlobValue)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:343`
- **说明**：switch 各类基础类型，从 BinaryReader 读 const 值；IL2CPP_TYPE_SZARRAY 递归
- **调用**：`CustomAttributeDataReader.ReadAttributeDataValue:145`

### `Il2CppExecutor.ReadEncodedTypeEnum(BinaryReader, out Il2CppType enumType)`
- **位置**：`Il2CppDumper/Utils/Il2CppExecutor.cs:464`
- **调用**：`CustomAttributeDataReader.ReadAttributeDataValue:144`、`CustomAttributeDataReader.VisitCustomAttributeData:111`

---

## `DummyAssemblyGenerator` (`Utils/DummyAssemblyGenerator.cs`)

### `DummyAssemblyGenerator` 构造器
- **签名**：`public DummyAssemblyGenerator(Il2CppExecutor il2CppExecutor, bool addToken)`
- **位置**：`Il2CppDumper/Utils/DummyAssemblyGenerator.cs:27`
- **可见性**：public
- **副作用**：四遍 pass 构造所有 type/method/field/property/event；填充 `typeDefinitionDic`、`methodDefinitionDic` 等
- **抛出**：attribute 错误时打印但不 throw
- **调用**：被 `DummyAssemblyExporter.Export:14` 调用

### 私有函数

| 函数 | 行 | 说明 |
|------|----|------|
| `GetTypeReferenceWithByRef` | 451 | 包 `ByReferenceType` |
| `GetTypeReference` | 464 | 主类型引用映射（switch Il2CppTypeEnum → Cecil TypeReference） |
| `CreateCustomAttribute` | 562 | pass 4 调用：v<29 写 AttributeAttribute stub；v>=29 解析 blob |
| `TryRestoreCustomAttribute` | 639 | 快速匹配零参 ctor |
| `CreateGenericParameter` | 654 | |
| `CreateCustomAttributeArgument` | 673 | 把 BlobValue 转 CustomAttributeArgument（含数组、Type、Object） |
| `GetBlobValueTypeReference` | 709 | enum vs primitive |

---

## `SectionHelper` (`Utils/SectionHelper.cs`)

### `SectionHelper` 构造器
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:23`
- **可见性**：public
- **副作用**：保存 il2Cpp、methodCount、typeDefinitionsCount、metadataUsagesCount、imageCount

### 公开属性

| 属性 | 行 | 说明 |
|------|----|------|
| `Exec` | 19 | exec section 列表 |
| `Data` | 20 | data section 列表 |
| `Bss` | 21 | bss section 列表 |

### `SetSection` 重载

| 重载 | 行 |
|------|----|
| `SetSection(SearchSectionType, Elf32_Phdr[])` | 32 |
| `SetSection(SearchSectionType, Elf64_Phdr[])` | 51 |
| `SetSection(SearchSectionType, MachoSection[])` | 70 |
| `SetSection(SearchSectionType, MachoSection64Bit[])` | 89 |
| `SetSection(SearchSectionType, ulong imageBase, SectionHeader[])` | 108 |
| `SetSection(SearchSectionType, params NSOSegmentHeader[])` | 127 |
| `SetSection(SearchSectionType, params SearchSection[])` | 146 |
| `SetSection(SearchSectionType, List<SearchSection>)` (private) | 151 |

### `SectionHelper.FindCodeRegistration()`
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:167`
- **可见性**：public
- **返回值**：CR VA；0 表示未找到
- **副作用**：可能修改 `pointerInExec`
- **调用**：被各格式的 `PlusSearch` 调用

### `SectionHelper.FindMetadataRegistration()`
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:198`
- **可见性**：public
- **返回值**：MR VA；0 表示未找到
- **调用**：被各格式的 `PlusSearch` 调用

### `SectionHelper.FindCodeRegistrationOld()` (private)
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:211`
- **说明**：v<24.2 路径，data section 扫 `intptr == methodCount` → deref → 检查指针是否在 exec range

### `SectionHelper.FindMetadataRegistrationOld()` (private)
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:245`
- **说明**：v19~26 路径

### `SectionHelper.FindMetadataRegistrationV21()` (private)
- **位置**：`Il2CppDumper/Utils/SectionHelper.cs:281`
- **说明**：v>=27 路径（连续两个 `intptr == typeDefCount`）

### 检查函数

| 函数 | 行 | 说明 |
|------|----|------|
| `CheckPointerRangeDataRa` | 329 | 指针是否在 data 段的 offset 范围 |
| `CheckPointerRangeExecVa` | 334 | 所有指针是否在 exec 段 VA 范围 |
| `CheckPointerRangeDataVa` | 339 | 同上但 data 段 |
| `CheckPointerRangeBssVa` | 344 | 同上但 bss 段 |

### v24.2+ 搜索

| 函数 | 行 |
|------|----|
| `FindCodeRegistrationData` | 351 |
| `FindCodeRegistrationExec` | 356 |
| `FindCodeRegistration2019` | 361（核心：mscorlib.dll 字符串交叉引用 + imageCount 倒数回退） |
| `FindReference` | 409 |

常量 `featureBytes = "mscorlib.dll\0"` (`SectionHelper.cs:349`)

---

## `CustomAttributeDataReader` (`Utils/CustomAttributeDataReader.cs`)

### `CustomAttributeDataReader` 构造器
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:15`
- **可见性**：public
- **副作用**：从 buffer 读 `Count`、缓存 ctorBuffer / dataBuffer

### `Count` (属性)
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:13`

### `CustomAttributeDataReader.GetStringCustomAttributeData()`
- **签名**：`public string GetStringCustomAttributeData()`
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:24`
- **返回值**：`[Foo(arg1, fieldName=value, propName=value)]` 字符串
- **调用**：被 `Il2CppDecompiler.GetCustomAttribute:439` 调用

### `CustomAttributeDataReader.AttributeDataToString(BlobValue)` (private)
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:71`
- **说明**：STRING 加引号；SZARRAY 转 `new[] { ... }`；IL2CPP_TYPE_INDEX 转 `typeof(...)`

### `CustomAttributeDataReader.VisitCustomAttributeData()`
- **签名**：`public CustomAttributeReaderVisitor VisitCustomAttributeData()`
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:98`
- **返回值**：解析后的 visitor（含 `CtorIndex / Arguments / Fields / Properties`）
- **调用**：被 `DummyAssemblyGenerator.CreateCustomAttribute:604` 调用

### `CustomAttributeDataReader.ReadAttributeDataValue()` (private)
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:142`
- **说明**：读 type + value（委托给 `executor.GetConstantValueFromBlob`）

### `CustomAttributeDataReader.ReadCustomAttributeNamedArgumentClassAndIndex(Il2CppTypeDefinition)` (private)
- **位置**：`Il2CppDumper/Utils/CustomAttributeDataReader.cs:153`
- **说明**：memberIndex >= 0 → 当前类；否则是跨类引用，要读 typeIndex

---

## 数据类

### `CustomAttributeReaderVisitor` (`CustomAttributeReaderVisitor.cs:3`)
POCO：`CtorIndex`、`Arguments`、`Fields`、`Properties`

### `AttributeArgument` (`AttributeArgument.cs:3`)
POCO：`Value: BlobValue`、`Index: int`

### `BlobValue` (`BlobValue.cs:3`)
POCO：`Value: object`、`il2CppTypeEnum`、`EnumType: Il2CppType`

---

## `PELoader` (`Utils/PELoader.cs`)

### `PELoader.Load(string fileName)` (static)
- **位置**：`Il2CppDumper/Utils/PELoader.cs:14`
- **可见性**：public static
- **副作用**：用 `LoadLibrary` 把 PE 加载进进程；按 section 用 `Marshal.Copy` 复制到 managed 字节数组；合并 PE header 与 section 内容返回 `PE` 实例
- **抛出**：PE magic 错、32/64 进程不匹配、`Win32Exception`
- **调用**：被 `Program.Main:216` 调用

### P/Invoke
- `LoadLibrary` (`PELoader.cs:11-12`)

---

## `SearchSection` (`Utils/SearchSection.cs`)
- `SearchSectionType` enum (`SearchSection.cs:3`)：`Exec`、`Data`、`Bss`
- `SearchSection` POCO (`SearchSection.cs:10`)：`offset / offsetEnd / address / addressEnd`

---

## 其他 Utils 文件（partial）

### `OpenFileDialog.cs`
Win32 IFileOpenDialog 包装。仅 Windows。

### `FileDialogNative.cs`
COM interop 定义（IFileOpenDialog、IFileDialog 等）。

### `MyAssemblyResolver.cs`
Cecil 的 `IAssemblyResolver` 实现，用于 DummyDll 生成时解析 `Il2CppDummyDll` 引用。