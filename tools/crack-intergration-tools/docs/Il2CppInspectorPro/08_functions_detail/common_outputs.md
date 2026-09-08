# 08 · `Il2CppInspector.Common` 输出发射器

> 文件范围：
> - `Outputs/CSharpCodeStubs.cs`
> - `Outputs/CppScaffolding.cs`
> - `Outputs/AssemblyShims.cs`
> - `Outputs/JSONMetadata.cs`
> - `Outputs/PythonScript.cs`
> - `Outputs/OutputFormatStream.cs`

---

## `CSharpCodeStubs.ctor`

- **签名**: `public CSharpCodeStubs(TypeModel model)`
- **位置**: `Il2CppInspector.Common/Outputs/CSharpCodeStubs.cs:~50`
- **可见性**: public
- **副作用**: 缓存命名空间列表
- **简要说明**: 持有 TypeModel 与发射选项（ExcludeNamespaces, MustCompile, SuppressMetadata）

## `CSharpCodeStubs.GetAndClearLastException`

- **签名**: `public Exception GetAndClearLastException()`
- **位置**: `CSharpCodeStubs.cs:49`
- **可见性**: public
- **简要说明**: 取 + 清最近一次发射异常，便于 GUI 提示

## `CSharpCodeStubs.WriteSingleFile`

- **签名**:
  - `void WriteSingleFile(string outFile)`
  - `void WriteSingleFile<TKey>(string outFile, Func<TypeInfo, TKey> orderBy)`
- **位置**: `CSharpCodeStubs.cs:55 / :57`
- **可见性**: public
- **副作用**: 写文件
- **调用了**:
  - `Parallel.ForEach<TypeInfo>(types, generateType)`
  - `File.WriteAllText(outFile, ...)`
- **调用**: CLI `-c types.cs`、GUI `GenerateCSharp_Click`、`CSharpStubOutput.Export`、`FrontendCore.UiContext`
- **简要说明**: 单文件类型桩

## `CSharpCodeStubs.WriteFilesByNamespace<TKey>`

- **签名**: `void WriteFilesByNamespace<TKey>(string outPath, Func<TypeInfo, TKey> orderBy, bool flattenHierarchy)`
- **位置**: `CSharpCodeStubs.cs:62`
- **可见性**: public
- **调用了**: `Directory.CreateDirectory`、`groupBy(ns).ForEach(writeFile)`
- **简要说明**: 按命名空间拆分文件

## `CSharpCodeStubs.WriteFilesByAssembly<TKey>`

- **签名**: `void WriteFilesByAssembly<TKey>(string outPath, Func<TypeInfo, TKey> orderBy, bool separateAttributes)`
- **位置**: `CSharpCodeStubs.cs:71`
- **可见性**: public
- **简要说明**: 按 Assembly 拆分

## `CSharpCodeStubs.WriteFilesByClass`

- **签名**: `void WriteFilesByClass(string outPath, bool flattenHierarchy)`
- **位置**: `CSharpCodeStubs.cs:82`
- **可见性**: public
- **简要说明**: 一类型一文件

## `CSharpCodeStubs.WriteFilesByClassTree`

- **签名**: `HashSet<Assembly> WriteFilesByClassTree(string outPath, bool separateAttributes)`
- **位置**: `CSharpCodeStubs.cs:90`
- **可见性**: public
- **调用了**: 内部递归遍历类型树
- **简要说明**: 保留命名空间目录层级

## `CSharpCodeStubs.WriteSolution`

- **签名**: `void WriteSolution(string outPath, string unityPath, string unityAssembliesPath)`
- **位置**: `CSharpCodeStubs.cs:116`
- **可见性**: public
- **副作用**: 写 `.sln` + 每个 assembly 的 `.csproj` + 类树
- **调用了**:
  - `WriteFilesByClassTree(outPath, true)`
  - `Resources.SlnProjectDefinition`、`Resources.SlnProjectConfiguration`、`Resources.CsProjTemplate`、`Resources.CsSlnTemplate`（来自 `Properties/Resources.Designer.cs`）
- **调用**: CLI `-j`、`VsSolutionOutput.Export`
- **简要说明**: 输出可直接 `dotnet build` 的完整 VS 解决方案

---

## `CppScaffolding.ctor`

- **签名**: `public CppScaffolding(AppModel model, bool useBetterArraySize = false, bool includeUnresolvedCppTypes = false)`
- **位置**: `Il2CppInspector.Common/Outputs/CppScaffolding.cs:~50`
- **可见性**: public
- **简要说明**: 持有 AppModel + 选项

## `CppScaffolding.Write`

- **签名**: `void Write(string projectPath, string projectName = null)`
- **位置**: `CppScaffolding.cs:~120`
- **可见性**: public
- **副作用**: 创建 `appdata/`、`framework/`、`user/`、`definitions/`、`.vcxproj`、`.filters`、`.sln`
- **调用了**:
  - `WriteTypes(...)`
  - 写 `il2cpp-api-functions.h` / `-ptr.h` / `il2cpp-types-ptr.h` / `il2cpp-functions.h` / `il2cpp-metadata-version.h`
  - 写 `framework/dllmain.cpp helpers.cpp/h il2cpp-appdata.h il2cpp-init.cpp/h pch-il2cpp.cpp/h version.cpp/h`
  - 写 `user/main.cpp/h settings.cpp/h`（仅当不存在）
  - 写 `definitions/version.def`
  - 写 `.vcxproj` / `.vcxproj.filters` / `.sln` via Resources
  - 若 `./libraries/` 存在，解压 `imgui.zip` / `detours.zip` / `handlers.zip`
- **调用**: CLI `-h`、`CppScaffoldingOutput.Export`
- **简要说明**: 完整 C++ DLL 注入工程生成

## `CppScaffolding.WriteTypes`

- **签名**: `void WriteTypes(string typeHeaderFile)`
- **位置**: `CppScaffolding.cs:~250`
- **可见性**: public
- **调用了**: `_model.UnityHeaders.GetTypeHeaderText(WordSizeBits)` + 内部 `writeForwardDefinitions` / `writeTypesForGroup`
- **简要说明**: 仅写类型头 `il2cpp-types.h`

---

## `AssemblyShims.ctor`

- **签名**: `public AssemblyShims(TypeModel model)`
- **位置**: `Il2CppInspector.Common/Outputs/AssemblyShims.cs:~60`
- **可见性**: public
- **简要说明**: dnlib `ModuleDefUser` 容器

## `AssemblyShims.Write`

- **签名**: `void Write(string outPath, EventHandler<string> statusCallback = null)`
- **位置**: `AssemblyShims.cs:~120`
- **可见性**: public
- **副作用**: 创建 dummy DLL
- **调用了**:
  - `new TypeDefUser(...)` / `new MethodDefUser(...)`
  - `dnlibExtensions.AddDefaultConstructor`
  - `dnlibExtensions.AddAttribute`
  - `ModuleDef.Write(...)`
- **调用**: CLI `-d dll/`、`DummyDllOutput.Export`
- **简要说明**: 每个 Assembly 一个 dummy DLL，可被 dnSpy/ILSpy 反编译

## `dnlibExtensions.AddDefaultConstructor`

- **签名**: `static MethodDef AddDefaultConstructor(this TypeDef typeDef, IMethod @base)`
- **位置**: `AssemblyShims.cs:~700`
- **可见性**: public static
- **简要说明**: 给 TypeDef 加默认 ctor

## `dnlibExtensions.AddAttribute`

- **签名**: `static CustomAttribute AddAttribute(this IHasCustomAttribute owner, ModuleDef module, TypeDef attrType, params (string Name, object Value)[] args)`
- **位置**: `AssemblyShims.cs:~720`
- **可见性**: public static
- **简要说明**: 把 attribute 加到 type/method/property 上

---

## `JSONMetadata.ctor`

- **签名**: `public JSONMetadata(AppModel model)`
- **位置**: `Il2CppInspector.Common/Outputs/JSONMetadata.cs:~40`
- **可见性**: public
- **简要说明**: 持有 AppModel

## `JSONMetadata.Write`

- **签名**: `void Write(string filePath)`
- **位置**: `JSONMetadata.cs:~100`
- **可见性**: public
- **副作用**: 写 metadata.json
- **调用了**: `System.Text.Json.JsonSerializer.Serialize`
- **调用**: CLI `-o`、Disassembler 输出阶段
- **简要说明**: 类型/方法/字段/字符串全量 JSON dump

---

## `PythonScript.ctor`

- **签名**: `public PythonScript(AppModel model)`
- **位置**: `Il2CppInspector.Common/Outputs/PythonScript.cs:~30`
- **可见性**: public
- **简要说明**: 持有 AppModel

## `PythonScript.WriteScriptToFile`

- **签名**: `void WriteScriptToFile(string outFile, string target, string cppHeaderFile, string jsonMetadataFile)`
- **位置**: `PythonScript.cs:~50`
- **可见性**: public
- **副作用**: 写 Python 脚本
- **调用了**:
  - 读 `Outputs/ScriptResources/shared_base.py`
  - 读 `Outputs/ScriptResources/Targets/{target}.py`（IDA/Ghidra/BinaryNinja）
  - 模板替换占位符
- **调用**: CLI `-p`、`DisassemblerMetadataOutput.Export`
- **简要说明**: 生成反汇编器脚本

## `PythonScript.GetAvailableTargets`

- **签名**: `static IEnumerable<string> GetAvailableTargets()`
- **位置**: `PythonScript.cs:~75`
- **可见性**: public static
- **简要说明**: 返回 `[ "IDA", "Ghidra", "BinaryNinja" ]`

---

## `OutputFormatStream` (OutputFormatStream.cs)

- **位置**: `Il2CppInspector.Common/Outputs/OutputFormatStream.cs`
- **可见性**: public
- **简要说明**: 文本模板替换器，Python 脚本用它做占位符替换