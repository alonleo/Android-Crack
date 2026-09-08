# 01 项目概览

## 项目定位

Il2CppDumper 是 Unity IL2CPP 编译产物的离线反编译工具：

1. 解析 Unity 生成的 `libil2cpp.so`（或 iOS Mach-O、Switch NSO、WebAssembly 等）二进制，定位两张全局注册表：
   - `Il2CppCodeRegistration` — 包含 methodPointers / genericMethodPointers / invokerPointers / customAttributeGenerators …
   - `Il2CppMetadataRegistration` — 包含 genericInsts / methodSpecs / fieldOffsets / types …
2. 解析 `global-metadata.dat`（通常加密的元数据库，magic = `0xFAB11BAF`），获得 imageDefs / typeDefs / methodDefs / fieldDefs / stringLiterals …
3. 输出：
   - `dump.cs`：可读的 C# 伪源码（命名空间、字段、属性、方法签名、默认值、RVA/Offset/VA 注释）
   - `il2cpp.h` + `script.json` + `stringliteral.json`：用于 IDA / Ghidra / Binary Ninja 的结构定义与重命名脚本
   - `DummyDll/*.dll`：用 Mono.Cecil 生成的方法体为空但元数据完整的 DLL 集合，便于 dnSpy / ILSpy 浏览 MonoBehaviour 字段

## 版本信息

| 项 | 值 |
|---|---|
| Assembly 版本 | `1.0.0.0` |
| 当前 README | 6.6.x |
| 支持 il2cpp 版本 | `v16 ~ v31`（含 `v24.x` 与 `v27.x`/`v29.x` 子版本） |
| Unity 版本覆盖 | 2018 ~ 2022+（隐含——取决于 metadata 版本） |

## 技术栈

| 维度 | 选择 |
|------|------|
| 语言 | C# 10 |
| TFM | `net6.0;net8.0`（多目标） |
| 构建系统 | dotnet SDK + MSBuild |
| 主要 NuGet | `Mono.Cecil` 0.11.4（用于 DummyDll 生成） |
| 平台 | Windows / macOS / Linux 均可运行；GUI 弹窗（OpenFileDialog）仅 Windows 上原生 |
| 辅助脚本 | Python 3（IDA / Ghidra / Hopper / Binary Ninja） |

## 入口与可执行文件

- 解决方案：`Il2CppDumper.sln`
- 单一项目：`Il2CppDumper/Il2CppDumper.csproj`
- 单一可执行文件：`Il2CppDumper.exe`（`Program.Main`，`STAThread`）

## 运行模式

1. **自动模式**（默认）：通过 magic 检测二进制格式 → 解析 metadata → 启发式搜索 `CodeRegistration` / `MetadataRegistration` → dump.cs + il2cpp.h + DummyDll。
2. **手动模式**：自动搜索失败时，从控制台读取用户输入的两个 RVA。
3. **ForceDump / NoRedirectedPointer**：用于内存转储（dumped-from-memory）场景。

## 局限

- 不处理 .NET `PEVerify` 级别校验；dummy DLL 的方法体只是 stub。
- 不解析 IL 字节码本身——这是 Il2CppDumper 与 Il2CppInspector 的核心差异。
- WASM 模式只覆盖包含 data section 的 wasm 格式。