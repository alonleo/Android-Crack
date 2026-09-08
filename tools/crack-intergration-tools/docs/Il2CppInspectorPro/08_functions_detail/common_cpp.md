# 08 · `Il2CppInspector.Common` C++ 发射

> 文件范围：
> - `Cpp/CppDeclarationGenerator.cs`
> - `Cpp/CppTypeCollection.cs`
> - `Cpp/CppType.cs`
> - `Cpp/CppField.cs` / `CppEnumField.cs`
> - `Cpp/CppNamespace.cs`
> - `Cpp/CppTypeDependencyGraph.cs`
> - `Cpp/CppCompilerType.cs`
> - `Cpp/MangledNameBuilder.cs`
> - `Cpp/UnityHeaders/UnityHeaders.cs`
> - `Cpp/UnityHeaders/UnityVersion.cs`
> - 嵌入式 `Cpp/UnityHeaders/*.h` 与 `Cpp/Il2CppAPIHeaders/*.h`（EmbeddedResource）

---

## `CppDeclarationGenerator.ctor`

- **签名**: `public CppDeclarationGenerator(AppModel appModel)`
- **位置**: `Il2CppInspector.Common/Cpp/CppDeclarationGenerator.cs:~80`
- **可见性**: public
- **简要说明**: 缓存 UnityVersion + InheritanceStyle（由 `CppCompiler.GuessFromImage` 决定）

## `CppDeclarationGenerator.AsCType`

- **签名**: `CppType AsCType(TypeInfo ti)`
- **位置**: `CppDeclarationGenerator.cs:~150`
- **可见性**: public
- **调用了**: `CppTypeCollection.GetType/GetComplexType/MakeArrayType/MakePointerType`
- **调用**: `IncludeType` / `IncludeMethod` 内部使用
- **简要说明**: TypeInfo → CppType 转换器

## `CppDeclarationGenerator.Reset`

- **签名**: `void Reset()`
- **位置**: `CppDeclarationGenerator.cs:~220`
- **可见性**: public
- **简要说明**: 清空已收集的 method/type 缓存

## `CppDeclarationGenerator.IncludeMethod`

- **签名**: `void IncludeMethod(MethodBase method)`
- **位置**: `CppDeclarationGenerator.cs:~250`
- **可见性**: public
- **调用了**: `GenerateMethodDeclaration` + `IncludeType` 对方法签名里的所有类型
- **简要说明**: 把方法及其依赖类型拉入待生成集合

## `CppDeclarationGenerator.IncludeType`

- **签名**: `void IncludeType(TypeInfo type)`
- **位置**: `CppDeclarationGenerator.cs:~330`
- **可见性**: public
- **调用了**: `AsCType` + `CppTypeCollection.GetComplexType(...).AddField(...)`
- **简要说明**: 递归 Include 所有依赖

## `CppDeclarationGenerator.GenerateRemainingTypeDeclarations`

- **签名**: `List<(TypeInfo, CppComplexType valueType, CppComplexType referenceType, CppComplexType fieldsType, CppComplexType vtableType, CppComplexType staticsType)> GenerateRemainingTypeDeclarations()`
- **位置**: `CppDeclarationGenerator.cs:~430`
- **可见性**: public
- **调用了**: 内部按 MSVC / GCC 继承风格分支
- **简要说明**: 生成所有类型的 value/reference/fields/vtable/statics 子结构

## `CppDeclarationGenerator.GenerateMethodDeclaration`

- **签名**: `CppFnPtrType GenerateMethodDeclaration(MethodBase method)`
- **位置**: `CppDeclarationGenerator.cs:~520`
- **可见性**: public
- **调用了**: `MangledNameBuilder.Method`
- **简要说明**: 方法签名 → C++ 函数指针类型

## `CppDeclarationGenerator.GenerateRequiredForwardDefinitions`

- **签名**: `List<CppType> GenerateRequiredForwardDefinitions()`
- **位置**: `CppDeclarationGenerator.cs:~620`
- **可见性**: public
- **简要说明**: 计算必需的前置声明

---

## `CppTypeCollection.ctor`

- **签名**: `public CppTypeCollection(int wordSize)`
- **位置**: `Il2CppInspector.Common/Cpp/CppTypeCollection.cs:~80`
- **可见性**: public

## `CppTypeCollection.AddFromDeclarationText`

- **签名**: `void AddFromDeclarationText(string text)`
- **位置**: `CppTypeCollection.cs:~150`
- **可见性**: public
- **调用了**: 大量正则解析头文件
- **调用**: `FromUnityHeaders` 内部
- **简要说明**: 把 `.h` 文本转成 `CppType` 树

## `CppTypeCollection.GetType`

- **签名**: `CppType GetType(string typeName, bool returnUnaliased = false)`
- **位置**: `CppTypeCollection.cs:~260`
- **可见性**: public

## `CppTypeCollection.GetComplexType`

- **签名**: `CppComplexType GetComplexType(string typeName)`
- **位置**: `CppTypeCollection.cs:~300`
- **可见性**: public

## `CppTypeCollection.AddField`

- **签名**: `int AddField(CppComplexType declaringType, string fieldName, string typeName, bool isConst = false)`
- **位置**: `CppTypeCollection.cs:~400`
- **可见性**: public

## `CppTypeCollection.NewDefaultEnum`

- **签名**: `CppEnumType NewDefaultEnum(string name = "")`
- **位置**: `CppTypeCollection.cs:~430`
- **可见性**: public

## `CppTypeCollection.FromUnityVersion`

- **签名**: `static CppTypeCollection FromUnityVersion(UnityVersion, CppDeclarationGenerator = null)`
- **位置**: `CppTypeCollection.cs:~470`
- **可见性**: public static

## `CppTypeCollection.FromUnityHeaders`

- **签名**: `static CppTypeCollection FromUnityHeaders(UnityHeaders, CppDeclarationGenerator)`
- **位置**: `CppTypeCollection.cs:~500`
- **可见性**: public static
- **调用**: `AppModel.Build` 内部

---

## `CppType.AsPointer` / `AsArray` / `AsAlias`

- **签名**:
  - `CppPointerType AsPointer(int)` / `CppArrayType AsArray(int)` / `CppAlias AsAlias(string)`
- **位置**: `Il2CppInspector.Common/Cpp/CppType.cs:~80-110`
- **可见性**: public
- **简要说明**: 装饰当前类型返回新实例

## `CppFnPtrType.FromSignature`

- **签名**: `static CppFnPtrType FromSignature(CppTypeCollection, string signature)`
- **位置**: `CppType.cs:~290`
- **可见性**: public static
- **简要说明**: 解析 C++ 函数指针声明字符串

## `CppComplexType.AddField` / `this[string]`

- **签名**:
  - `void AddField(CppField)`
  - `CppField this[string fieldName]`
- **位置**: `CppType.cs:~360-380`
- **可见性**: public

## `CppEnumType.AddField`

- **签名**: `void AddField(string name, object value)`
- **位置**: `CppType.cs:~440`
- **可见性**: public

## `CppTypeDependencyGraph.DeriveDependencyOrderedTypes`

- **签名**: `List<TypeInfo> DeriveDependencyOrderedTypes(TypeInfo root)`
- **位置**: `Il2CppInspector.Common/Cpp/CppTypeDependencyGraph.cs:~40`
- **可见性**: public
- **简要说明**: 拓扑排序

## `CppTypeDependencyGraph.Reset`

- **签名**: `void Reset()`
- **位置**: `CppTypeDependencyGraph.cs:~140`
- **可见性**: public

## `CppCompilerType` (enum)

- **位置**: `Il2CppInspector.Common/Cpp/CppCompilerType.cs:~10`
- **值**: `MSVC, GCC, BinaryFormat`

## `CppCompiler.GuessFromImage`

- **签名**: `static CppCompilerType GuessFromImage(IFileFormatStream image)`
- **位置**: `CppCompilerType.cs:~30`
- **可见性**: public static
- **简要说明**: PE → MSVC，其他 → GCC

---

## `MangledNameBuilder.Method`

- **签名**: `static string Method(MethodBase method)`
- **位置**: `Il2CppInspector.Common/Cpp/MangledNameBuilder.cs:~50`
- **可见性**: public static
- **简要说明**: Itanium ABI mangler

## `MangledNameBuilder.MethodInfo`

- **签名**: `static string MethodInfo(MethodBase method)`
- **位置**: `MangledNameBuilder.cs:~120`
- **可见性**: public static

## `MangledNameBuilder.TypeInfo`

- **签名**: `static string TypeInfo(TypeInfo type)`
- **位置**: `MangledNameBuilder.cs:~180`
- **可见性**: public static

## `MangledNameBuilder.TypeRef`

- **签名**: `static string TypeRef(TypeInfo type)`
- **位置**: `MangledNameBuilder.cs:~240`
- **可见性**: public static

---

## `UnityHeaders.GuessHeadersForBinary`

- **签名**: `static UnityHeaders GuessHeadersForBinary(Il2CppBinary binary)`
- **位置**: `Il2CppInspector.Common/Cpp/UnityHeaders/UnityHeaders.cs:112`
- **可见性**: public static
- **调用了**: 二分匹配嵌入 `.h` 中的导出符号
- **调用**: CLI `Run` 推断 unity version、Redux CLI 同
- **简要说明**: 决定使用哪一组 Unity 头

## `UnityHeaders.GetHeadersForVersion`

- **签名**: `static UnityHeaders GetHeadersForVersion(UnityVersion)`
- **位置**: `UnityHeaders.cs:~140`
- **可见性**: public static

## `UnityHeaders.GetTypeHeaderText` / `GetApiHeaderText` / `GetTypedefText`

- **签名**:
  - `string GetTypeHeaderText(int wordSizeBits)`
  - `string GetApiHeaderText(int wordSizeBits)`
  - `string GetTypedefText(int wordSizeBits)`
- **位置**: `UnityHeaders.cs:~170-200`
- **可见性**: public
- **调用**: `CppScaffolding.WriteTypes` + `CppTypeCollection.AddFromDeclarationText`

## `UnityVersion.Parse` / `TryParse`

- **签名**: `static bool TryParse(string?, IFormatProvider?, out UnityVersion)` / `static UnityVersion Parse(string)`
- **位置**: `Il2CppInspector.Common/Cpp/UnityHeaders/UnityVersion.cs:~80`
- **可见性**: public static