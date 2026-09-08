# 06 构建、运行与配置

## 编译

```bash
cd Il2CppDumper
dotnet build Il2CppDumper/Il2CppDumper.csproj -c Release
```

产物：`Il2CppDumper/bin/Release/net6.0/Il2CppDumper.exe`（或 `net8.0/`）。

多目标 `net6.0;net8.0` —— 默认 restore 出哪个 framework 取决于 dotnet SDK 安装情况。

## 运行

### 自动模式（Windows 弹窗）

直接双击 `Il2CppDumper.exe`，根据弹窗选择：
1. il2cpp 二进制文件（任意 `*.*`）
2. `global-metadata.dat`

### CLI 模式

```
Il2CppDumper.exe <il2cpp-binary> <global-metadata.dat> <output-directory>
```

参数识别规则（`Program.Main:35-55`）：

- 若参数是已存在的文件 → 看 magic：magic `0xFAB11BAF` 是 metadata；否则是 il2cpp 二进制。
- 若参数是已存在的目录 → 输出目录。
- 三个参数必须分别落到三个变量（顺序不限，但 1 个文件 + 1 个目录 = 只够 2 个角色，缺一个会回退到 GUI 弹窗）。

### 帮助

`-h` / `--help` / `/?` / `/h` 任意一个：

```
usage: Il2CppDumper.exe <executable-file> <global-metadata> <output-directory>
```

### 退出按键

`Config.RequireAnyKey = true`（默认）→ 退出前等待任意键。CLI 脚本里可改成 `false`。

## config.json

`config.json` 必须在 `Il2CppDumper.exe` 同级目录，结构：

```json
{
  "DumpMethod": true,
  "DumpField": true,
  "DumpProperty": false,
  "DumpAttribute": false,
  "DumpFieldOffset": true,
  "DumpMethodOffset": true,
  "DumpTypeDefIndex": true,
  "GenerateDummyDll": true,
  "GenerateStruct": true,
  "DummyDllAddToken": true,
  "RequireAnyKey": true,
  "ForceIl2CppVersion": false,
  "ForceVersion": 24.3,
  "ForceDump": false,
  "NoRedirectedPointer": false
}
```

| 字段 | 默认 | 作用 |
|------|------|------|
| `DumpMethod` | true | dump.cs 中是否写方法签名 |
| `DumpField` | true | dump.cs 中是否写字段 |
| `DumpProperty` | false | dump.cs 中是否写属性 |
| `DumpAttribute` | false | 还原 `[Foo(...)]` attribute |
| `DumpFieldOffset` | true | 字段后注释 `// 0xN` |
| `DumpMethodOffset` | true | 方法前注释 `// RVA: 0xN Offset: 0xN VA: 0xN` |
| `DumpTypeDefIndex` | true | 类型后注释 `// TypeDefIndex: N` |
| `GenerateDummyDll` | true | 是否写 `DummyDll/` |
| `GenerateStruct` | true | 是否写 `il2cpp.h` + scripts |
| `DummyDllAddToken` | true | 在 stub 上写 `[Token("0xN")]` |
| `RequireAnyKey` | true | 退出前等待按键 |
| `ForceIl2CppVersion` | false | 强制使用 `ForceVersion` 而非 metadata 探测 |
| `ForceVersion` | 24.3 | 强制版本号 |
| `ForceDump` | false | 输入视为内存转储（不重新 relocate） |
| `NoRedirectedPointer` | false | dump 模式下不重新指向 (需配合 `ForceDump=true`) |

## 输出目录结构

```
<output-dir>/
├── dump.cs                 C# 反编译
├── il2cpp.h                C 结构定义（IDA / Ghidra / Binary Ninja 使用）
├── script.json             {Addresses, ScriptMethod[], ScriptMetadata[], ScriptMetadataMethod[], ScriptString[]}
├── stringliteral.json      [{value, address}]
└── DummyDll/
    ├── Assembly-CSharp.dll
    ├── UnityEngine.dll
    └── …（每个 image 一个）
```

## 输出与下游工具的对接

`script.json` 字段：

| 字段 | 类型 | 含义 |
|------|------|------|
| `Addresses` | `ulong[]` | 全部 method 类指针 RVA |
| `ScriptMethod[].Address` | `ulong` | 该方法 RVA |
| `ScriptMethod[].Name` | `string` | `TypeFullName$$MethodName` |
| `ScriptMethod[].Signature` | `string` | 完整 C 签名 `ReturnType Foo(Args);` |
| `ScriptMethod[].TypeSignature` | `string` | 单字符签名（IDA 的 `__usercall` 模式） |
| `ScriptString[].Address` | `ulong` | 字符串字面量地址 |
| `ScriptString[].Value` | `string` | 字符串字面量值 |
| `ScriptMetadata[].Address` | `ulong` | `TypeInfo` / `Il2CppType` / `FieldInfo` 句柄 RVA |
| `ScriptMetadataMethod[].Address` | `ulong` | `Method$...` 句柄 RVA |
| `ScriptMetadataMethod[].MethodAddress` | `ulong` | 对应方法 RVA |

将 `il2cpp.h` 拖入 IDA 的 Local Types 窗口，再执行根目录 `ida_with_struct_py3.py` 即可批量重命名 + 应用 `script.json`。

## 已知陷阱

1. **ForceDump + ELF**：`Program.Main:184` 自动检查；若 `IsDumped=true` 但未手动给 dump address，`SectionHelper` 会找不到 `CodeRegistration`，需要回退到手动输入。
2. **PELoader 仅 Windows**：跨 PE 保护需要 Win32 `LoadLibrary`，非 Windows 系统直接走 `PlusSearch`。
3. **WASM**：要求 wasm 包含 `id==11`（data section）；其他 wasm 格式可能 throw `InvalidOperationException` (`WebAssembly.cs:31,37`)。
4. **Encrypted metadata**：本仓库不包含解密逻辑；解密需先单独处理 `global-metadata.dat`，再喂给 Il2CppDumper。
5. **v29 attribute 还原**：依赖 `header.attributeDataOffset` 和 `header.attributeDataRangeOffset`；早期 Unity 编译产物若 metadata 头部字段错位，可能导致 `IndexOutOfRangeException`。