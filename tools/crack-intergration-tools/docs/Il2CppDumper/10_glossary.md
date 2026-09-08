# 10 — 术语表

## IL2CPP 与 Unity

| 术语 | 含义 |
|------|------|
| **IL2CPP** | Unity 的 AOT 编译器，把 IL（中间语言）翻译成 C++，再用平台编译器（clang/gcc/msvc）编译成 native。 |
| **global-metadata.dat** | IL2CPP 输出的元数据库，magic = `0xFAB11BAF`。包含所有 imageDef/typeDef/methodDef/fieldDef/stringLiteral 等。 |
| **il2cpp binary** | 即 libil2cpp.so / 游戏 .exe / iOS app binary。包含两份运行时全局注册表：`Il2CppCodeRegistration` 与 `Il2CppMetadataRegistration`。 |
| **MonoBehaviour** | Unity 的 Mono 脚本组件；序列化数据（`m_Script`、字段值）保存在 Scene/Asset 文件里；其字段定义在 dummy DLL 中通过 `MonoScript` 引用。 |
| **MonoScript** | `ScriptingTypeIdentifier` 的运行时包装，dummy DLL 中的 `MonoScript` 让 dnSpy 能反序列化 MonoBehaviour 字段。 |
| **RGCTX (Runtime Generic Context)** | IL2CPP 在 v24+ 为泛型类/方法生成的运行时上下文；用于在虚方法 dispatch 中快速查找泛型实例。 |
| **TypeDefIndex** | 元数据中的全局 TypeDef 编号；dump.cs 每个类型后注释 `// TypeDefIndex: N`。 |
| **token** | CLI metadata token (4 字节)，如 `0x02000002` 表示 TypeDef row 2。 |
| **dummy DLL** | Mono.Cecil 生成的方法体为空的 DLL；让 dnSpy/ILSpy 能浏览 MonoBehaviour 字段定义，但无法还原 IL 代码。 |
| **VA / RVA / FileOffset** | `VA = RVA + ImageBase`；`RVA = VA - ImageBase`；`FileOffset = MapVATR(VA)`。 |
| **metadataUsage** | IL2CPP 运行时的"metadata 间接引用"表（TypeInfo/Il2CppType/MethodDef/FieldInfo/StringLiteral/MethodRef）。 |

## 版本

| 版本 | il2cpp 二进制版本号（double）| 关键变化 |
|------|------|------|
| v16 | 16.0 | baseline |
| v17~v19 | 17~19 | 加入 genericContainers + metadataUsage |
| v21 | 21 | 加入 fieldOffset 指针 vs uint 区分；customAttributeIndex |
| v22 | 22 | 加入 reversePInvokeWrappers / unresolvedVirtualCallPointers |
| v23 | 23 | 加入 windowsRuntimeTypeNames |
| v24 | 24.0/24.1/24.2/24.3/24.4/24.5 | 加入 codeGenModules、interopData、FieldRVA |
| v27 | 27/27.1/27.2 | 加入 genericAdjustorThunks、methodSpec → typeDef 用 typeHandle |
| v29 | 29/29.1 | 加入 attributeDataRanges / attributeDataOffset；CodeRegistration 结构变化 |
| v31 | 31 | 引入新 CodeRegistration 字段 |
| v104/v106 | 104/106 | CODM 内部混淆版 metadata（rodroid `MetadataVariant::Codm`） |

## 可执行格式

| 术语 | 含义 |
|------|------|
| **PE** | Portable Executable（Windows .exe / .dll）。`Magic = MZ` (0x5A4D)。 |
| **ELF** | Executable and Linkable Format（Android .so, Linux）。`Magic = 0x464C457F`。 |
| **Mach-O** | Mach Object（iOS app、macOS app）。32-bit magic `0xFEEDFACE`，64-bit magic `0xFEEDFACF`，Fat magic `0xCAFEBABE` 或 `0xBEBAFECA`。 |
| **NSO** | Nintendo Switch Object。`Magic = 0x304F534E` (NSO0)。三个段 .text/.rodata/.data 可独立 LZ4 压缩。 |
| **WASM** | WebAssembly。`Magic = 0x6D736100`（`\0asm`）。需要包含 data section（id=11）。 |

## 全局注册表

### `Il2CppCodeRegistration`

```c
struct Il2CppCodeRegistration {
    uint32_t codeGenModulesCount;
    Il2CppCodeGenModule** codeGenModules;
    uint8_t reversePInvokeWrapperCount;
    void** reversePInvokeWrappers;
    uint32_t genericMethodPointersCount;
    void** genericMethodPointers;
    uint32_t invokerPointersCount;
    void** invokerPointers;
    // ... customAttributeGenerators, interopData, windowsRuntimeFactory 等
};
```

字段集合随 il2cpp 版本变化。Il2CppDumper 通过 `[VersionAttribute(Min, Max)]` 反射选择当前版本需要的字段。

### `Il2CppMetadataRegistration`

```c
struct Il2CppMetadataRegistration {
    Il2CppMethodDefinition const** methodDefinitions;  // 仅旧版本
    Il2CppGenericClass** genericClasses;
    Il2CppGenericInst** genericInsts;
    Il2CppMethodSpec** methodSpecs;
    Il2CppType** types;
    uint32_t fieldOffsetsCount;
    int32_t* fieldOffsets;
    // ...
};
```

## 核心数据类

### `Il2CppType` (8 字节 data + 4 字节 bits)

`bits` 拆分：
- bit 0~15: `attrs`
- bit 16~23: `type` (Il2CppTypeEnum)
- bit 24+: mods（v>=27.2: 5-bit num_mods + byref + pinned + valuetype；v<27.2: 6-bit num_mods + byref + pinned）

`data` 是 8 字节 union：
- `klassIndex` (signed i64) — 用于 CLASS/VALUETYPE 在 metadata 中的 typeDef 编号
- `typeHandle` (unsigned u64) — v>=27 + IsDumped 时为 runtime handle
- `array` — ARRAY 类型的 Il2CppArrayType 指针
- `generic_class` — GENERICINST 的 Il2CppGenericClass 指针
- `type` — SZARRAY / PTR 的 element type 指针
- `genericParameterIndex` / `genericParameterHandle` — VAR / MVAR

### `Il2CppGenericInst`

```c
struct Il2CppGenericInst {
    uint32_t type_argc;
    Il2CppType* type_argv[type_argc];
};
```

### `Il2CppGenericContext`

```c
struct Il2CppGenericContext {
    Il2CppGenericInst* class_inst;
    Il2CppGenericInst* method_inst;
};
```

### `Il2CppRGCTXDefinition`

```c
struct Il2CppRGCTXDefinition {
    Il2CppRGCTXDataType type;
    union {
        struct { int32_t rgctxDataDummy; };   // v<=27.1
        Il2CppRGCTXDefinitionData data;        // v<=27.1
        uint64_t _data;                        // v>=27.2
    };
};
```

`type` 取值：
- `IL2CPP_RGCTX_DATA_TYPE` — 一个 Il2CppType
- `IL2CPP_RGCTX_DATA_CLASS` — 一个 Il2CppClass
- `IL2CPP_RGCTX_DATA_METHOD` — 一个 methodSpec
- `IL2CPP_RGCTX_DATA_ARRAY`
- `IL2CPP_RGCTX_DATA_CONSTRAINED`

### `Il2CppCodeGenModule` (v24.2+)

每个 image 一份，包含：
- `moduleName` — string 指针（image 名，如 `Assembly-CSharp.dll`）
- `methodPointerCount` + `methodPointers` — 当前 image 的所有 method 实现
- `rgctxRanges` + `rgctxs` — 当前 image 的 RGCTX 表
- `customAttributeCacheGenerator` (v27+) — 自定义 attribute 缓存

## 搜索策略

| 阶段 | 适用版本 | 入口 |
|------|---------|------|
| PlusSearch | v24.2+ | `mscorlib.dll` 字符串交叉引用 → `CodeRegistration` |
| Search | v<24.2（Macho/Elf32） | ARM/x86 字节模式（LDR/ADD/MOV） |
| SymbolSearch | 始终（仅 ELF） | `.dynsym` 中的 `g_CodeRegistration` / `g_MetadataRegistration` |
| Manual | 兜底 | 提示用户输入 RVA |

## 输出

### `dump.cs`

可读 C# 伪源码：
```csharp
// Namespace: UnityEngine
public class Transform : Component, IEnumerable // TypeDefIndex: 28
{
    // Fields
    public Vector3 m_LocalPosition; // 0x10
    private Quaternion m_LocalRotation; // 0x1C

    // Methods
    // RVA: 0x1234 Offset: 0x1234 VA: 0x12345678 Slot: 5
    public void Translate(Vector3 translation) { }
    /* GenericInstMethod :
    |
    |-RVA: 0x2345 Offset: 0x2345 VA: 0x23456789
    |-List<int>.Add(int)
    */
}
```

### `il2cpp.h`

C 结构定义，配合 IDA/Ghidra/Binary Ninja 使用：
```c
struct Transform_o {
    Transform_c *klass;
    void *monitor;
    Transform_Fields fields;
};
struct Transform_Fields {
    Component_Fields _;
    Vector3 m_LocalPosition;
    Quaternion m_LocalRotation;
};
struct Transform_c {
    Il2CppClass_1 _1;
    void* static_fields;
    Il2CppRGCTXData* rgctx_data;
    Il2CppClass_2 _2;
    VirtualInvokeData vtable[255];
};
```

### `script.json`

JSON 数据，被 `ida_with_struct.py` / `ghidra.py` 读取，用于：
- `ScriptMethod[]` → 函数重命名 + 应用 C 签名
- `ScriptMetadata[]` → `Method$<...>` / `Field$<...>` 变量重命名
- `ScriptString[]` → 字符串字面量重命名
- `Addresses[]` → 全局 method-pointer 标记

### `stringliteral.json`

```json
[
  {"value": "Player", "address": "0xABCD"},
  ...
]
```

### `DummyDll/`

每个 image 一个 stub DLL：
```
DummyDll/
├── Assembly-CSharp.dll
├── UnityEngine.dll
├── mscorlib.dll
├── ...
```

## Misc

| 术语 | 含义 |
|------|------|
| **PHDR** | ELF Program Header |
| **SHDR** | ELF Section Header |
| **PT_LOAD** | ELF PHDR 类型：可加载段 |
| **PT_DYNAMIC** | ELF PHDR 类型：动态段 |
| **DT_SYMTAB / DT_STRTAB / DT_HASH / DT_GNU_HASH** | ELF 动态节类型 |
| **R_ARM_ABS32 / R_AARCH64_ABS64 / R_AARCH64_RELATIVE** | ELF/AArch64 relocation 类型 |
| **__mod_init_func** | Mach-O section：模块初始化函数指针数组 |
| **__bss / __const / __data / __text** | Mach-O section 名 |
| **MOVW/MOVT** | ARM32 立即数加载指令（16+16 位组合） |
| **ADRP/ADD** | ARM64 PC-相对寻址 + 立即数 |
| **LC_SEGMENT / LC_SEGMENT_64** | Mach-O load command |
| **LC_ENCRYPTION_INFO** | Mach-O 加密信息（iOS App Store） |