# 08 · `Il2CppTests` 测试

> 文件：
> - `Il2CppTests/TestRunner.cs`
> - `Il2CppTests/TestRunnerConfig.cs`
> - `Il2CppTests/TestCppTypeDeclarations.cs`
> - `Il2CppTests/TestAppModelQueries.cs`
> - `Il2CppTests/TestGenerics.cs`
> - `Il2CppTests/TestNames.cs`
> - `Il2CppTests/TestUnityVersion.cs`
> - 辅助 PowerShell：`generate-tests.ps1`, `il2cpp.ps1`, `update-expected-results.ps1`
> - 测试夹具（仅 Content，不编译）：`TestSources/*.cs`, `TestExpectedResults/*.{cs,json,h}`

---

## `TestRunner.Run`

- **签名**: `void Run(...)`
- **位置**: `Il2CppTests/TestRunner.cs:~30`
- **可见性**: public
- **调用了**:
  - 对每个 sample 二进制：`Il2Inspector.LoadFromFile` → `TypeModel` → `AppModel.Build`
  - `CSharpCodeStubs.WriteSingleFile` / `JSONMetadata.Write` / `CppScaffolding.WriteTypes`
  - 与 `TestExpectedResults/*` 做 diff
- **简要说明**: 跨样本回归主驱动

## `TestRunner.RunSingle`

- **签名**: `TestRunResult RunSingle(string samplePath, ...)`
- **位置**: `TestRunner.cs:~80`
- **可见性**: public

## `TestRunnerConfig`

- **签名**: `class TestRunnerConfig`
- **位置**: `TestRunnerConfig.cs`
- **可见性**: public
- **简要说明**: 测试配置（路径、要跑的样本集合）

---

## `TestCppTypeDeclarations` (NUnit)

- **位置**: `Il2CppTests/TestCppTypeDeclarations.cs:~30-200`
- **可见性**: public
- **方法**: 多个 `[TestCase]` — 例如：
  - `TestGenerateCppTypeDeclarations_SampleA()` / `TestGenerateCppTypeDeclarations_SampleB()`
- **简要说明**: 跨样本检查 C++ 类型声明

## `TestAppModelQueries` (NUnit)

- **位置**: `Il2CppTests/TestAppModelQueries.cs:~15-130`
- **方法**: `[TestCase]` 验证 `AppModel.GetTypeGroup` / `GetMethodGroup` 等查询结果
- **简要说明**: AppModel 查询稳定性

## `TestGenerics` (NUnit)

- **位置**: `Il2CppTests/TestGenerics.cs:~20-400`
- **方法**: 大量 `[TestCase]` 验证 `MakeGenericType` / `SubstituteGenericArguments` / `ResolveGenericArguments`
- **简要说明**: 泛型处理回归

## `TestNames` (NUnit)

- **位置**: `Il2CppTests/TestNames.cs:~10-100`
- **方法**: `[TestCase]` 验证 `ToCIdentifier` / 命名规则
- **简要说明**: 标识符生成

## `TestUnityVersion` (NUnit)

- **位置**: `Il2CppTests/TestUnityVersion.cs:~10-50`
- **方法**: `[TestCase]` 验证 `UnityVersion.Parse` / `TryParse` / 比较
- **简要说明**: Unity 版本解析

---

## 辅助脚本

### `il2cpp.ps1`

- **位置**: `Il2CppTests/il2cpp.ps1`
- **大小**: 12.2 KB
- **简要说明**: 调用 Il2CppInspectorPro CLI 生成期望产物

### `generate-tests.ps1`

- **位置**: `Il2CppTests/generate-tests.ps1`
- **大小**: 997 B
- **简要说明**: 在所有样本上跑 `il2cpp.ps1`

### `update-expected-results.ps1`

- **位置**: `Il2CppTests/update-expected-results.ps1`
- **大小**: 2.8 KB
- **简要说明**: 用新输出覆盖期望结果（维护基线）