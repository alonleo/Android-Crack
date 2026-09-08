# 08 · ImportExport / AssetInfo / Mesh / Search 详细说明

## 1. Logic/ImportExport/

涉及文件：
- `UABEANext4/Logic/ImportExport/AssetExport.cs` (332 LoC)
- `UABEANext4/Logic/ImportExport/AssetImport.cs` (485 LoC)

### AssetExport.cs

#### `class AssetExport`

##### `AssetExport(Stream writeStream)`
- **签名**：`public AssetExport(Stream writeStream)`
- **位置**：`AssetExport.cs:15`
- **可见性**：public
- **副作用**：构造 `StreamWriter`

##### `void DumpRawAsset(AssetsFileReader reader, long position, uint size)`
- **签名**：`public void DumpRawAsset(AssetsFileReader reader, long position, uint size)`
- **位置**：`AssetExport.cs:21`
- **可见性**：public
- **算法**：从 reader 拷 size 字节到 _stream

##### `void DumpTextAsset(AssetTypeValueField baseField)`
- **签名**：`public void DumpTextAsset(AssetTypeValueField baseField)`
- **位置**：`AssetExport.cs:36`
- **可见性**：public
- **算法**：递归 + 写 _streamWriter

##### `void RecurseTextDump(AssetTypeValueField field, int depth)`
- **签名**：`private void RecurseTextDump(AssetTypeValueField field, int depth)`
- **位置**：`AssetExport.cs:42`
- **可见性**：private

##### `void TextDumpManagedReferencesRegistry(AssetTypeValueField field, int depth)`
- **签名**：`private void TextDumpManagedReferencesRegistry(AssetTypeValueField field, int depth)`
- **位置**：`AssetExport.cs:118`
- **可见性**：private

##### `void DumpJsonAsset(AssetTypeValueField baseField)`
- **签名**：`public void DumpJsonAsset(AssetTypeValueField baseField)`
- **位置**：`AssetExport.cs:185`
- **可见性**：public

##### `JToken RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor)`
- **签名**：`private JToken RecurseJsonDump(AssetTypeValueField field, bool uabeFlavor)`
- **位置**：`AssetExport.cs:192`

##### `JObject JsonDumpManagedReferencesRegistry(AssetTypeValueField field, bool uabeFlavor = false)`
- **签名**：`private JObject JsonDumpManagedReferencesRegistry(AssetTypeValueField field, bool uabeFlavor = false)`
- **位置**：`AssetExport.cs:263`

##### `static string TextDumpEscapeString(string str)`
- **位置**：`AssetExport.cs:325`

### AssetImport.cs

#### `class AssetImport`

##### `AssetImport(Stream readStream, RefTypeManager refMan)`
- **签名**：`public AssetImport(Stream readStream, RefTypeManager refMan)`
- **位置**：`AssetImport.cs:16`
- **可见性**：public

##### `byte[] ImportRawAsset()`
- **签名**：`public byte[] ImportRawAsset()`
- **位置**：`AssetImport.cs:23`

##### `byte[]? ImportTextAsset(out string? exceptionMessage)`
- **签名**：`public byte[]? ImportTextAsset(out string? exceptionMessage)`
- **位置**：`AssetImport.cs:30`

##### `void ImportTextAssetLoop(AssetsFileWriter writer)`
- **签名**：`private void ImportTextAssetLoop(AssetsFileWriter writer)`
- **位置**：`AssetImport.cs:51`

##### `byte[]? ImportJsonAsset(AssetTypeTemplateField tempField, out string? exceptionMessage)`
- **签名**：`public byte[]? ImportJsonAsset(AssetTypeTemplateField tempField, out string? exceptionMessage)`
- **位置**：`AssetImport.cs:189`

##### `void RecurseJsonImport(AssetsFileWriter writer, AssetTypeTemplateField tempField, JToken token)`
- **签名**：`private void RecurseJsonImport(AssetsFileWriter writer, AssetTypeTemplateField tempField, JToken token)`
- **位置**：`AssetImport.cs:213`

##### `void JsonImportManagedReferencesRegistry(AssetsFileWriter writer, AssetTypeTemplateField tempField, JToken token)`
- **签名**：`private void JsonImportManagedReferencesRegistry(AssetsFileWriter writer, AssetTypeTemplateField tempField, JToken token)`
- **位置**：`AssetImport.cs:358`

##### `JToken ExpectAndReadField(JToken token, string name, AssetTypeTemplateField? tempField)`
- **签名**：`private JToken ExpectAndReadField(JToken token, string name, AssetTypeTemplateField? tempField)`
- **位置**：`AssetImport.cs:430`

##### `static bool StartsWithSpace(string str, string value)`
- **位置**：`AssetImport.cs:447`

##### `static string UnescapeDumpString(string str)`
- **位置**：`AssetImport.cs:452`

---

## 2. Logic/AssetInfo/

### BuildTarget.cs
- `class BuildTarget`
- `override ToString()`

### ExternalInfo.cs
- `class ExternalInfo`
- `void Build(AssetsFile file)` —— 解析 Externals
- 暴露 path / fileName / 类型等属性

### GeneralInfo.cs
- `class GeneralInfo`
- `void Build(AssetsFile file)`
- 暴露：UnityVersion、Platform、TypeTreeEnabled、bigIDEnabled 等

### ScriptInfo.cs
- `class ScriptInfo`
- `void Build(AssetsFile file)`
- 解析 MonoBehaviour 的 m_Script 引用

### TypeTreeInfo.cs
- `class TypeTreeInfo`
- `void Build(AssetsFile file)`
- 暴露类型树节点列表

### TypeTreeTypeInfo.cs
- `class TypeTreeTypeInfo`
- 包装单个 typeId + 节点列表

### TypeTreeNodeConverter.cs
- `class TypeTreeNodeConverter`
- AssetTypeTemplateField ↔ TypeTreeUINode 转换

### TypeTreeUINode.cs
- `class TypeTreeUINode`
- `string DisplayName`
- `IList<TypeTreeUINode> Children`

---

## 3. Logic/Mesh/

### MeshObj.cs
- `class MeshObj`
- 字段：
  - `string Name`
  - `Topology Topology`
  - `List<Channel> Channels`
  - `List<int> Indices`
  - `AABB Bounds`
  - `byte[] RawVertexData`
- 方法：
  - `void BuildFromBaseField(AssetTypeValueField bf, AssetsFileInstance fileInst)`

### Channel.cs
- `class Channel`
- 字段：`Name`, `Format`, `Dimension`, `Offset`, `Stride`, `byte[] Data`

### MeshEnums.cs
- `enum Topology { Triangles, Lines, ...}`
- `enum ChannelFormat { Float, Vector2, Vector3, Vector4, Color, ...}`

---

## 4. Logic/Search/

### SearchLogic.cs
- `class SearchLogic`
- `List<SearchResultItem> Search(Workspace ws, string query, SearchOptions options, CancellationToken ct)`
  - 算法：`Parallel.ForEach` over `ws.GetAssetsFileInstances()`，每个文件匹配
- `Task ParallelSearch(List<AssetsFileInstance> files, string query, ConcurrentBag<SearchResultItem> results, CancellationToken ct)`

### SearchResultItem.cs
- `class SearchResultItem`
- 字段：`File`, `PathId`, `Type`, `Name`, `Container`, `MatchScore`

---

## 5. Logic/Hierarchy/

### HierarchyItem.cs
- `class HierarchyItem`
- 字段：`AssetInst GameObject`, `IList<HierarchyItem> Children`, `int Depth`
- `static IEnumerable<HierarchyItem> Build(GameObject root, Workspace ws)`
  - 递归遍历 m_Transform → m_GameObject → m_Father

---

## 6. Logic/Documents/

### DocumentManager.cs
- `class DocumentManager`
- `void CloseDocument(IDocument doc)`
- `void OpenDocument(IDocument doc)`

---

## 7. Logic/DevTools/

### DevToolsAdblock.cs
- `static class DevToolsAdblock`
- 静态方法禁用 Avalonia DevTools 中的某些行为

---

## 8. Logic/Messages.cs

```csharp
public record SelectedWorkspaceItemChangedMessage(IReadOnlyList<WorkspaceItem> SelectedItems);
public record RequestEditAssetMessage(AssetInst Asset);
public record RequestCloseFileMessage(WorkspaceItem Item);
public record RequestVisitAssetMessage(AssetsFileInstance File, long PathId);
public record FileLoadedMessage(WorkspaceItem Item);
public record AssetDocumentSelectedMessage(WorkspaceItem FileItem, AssetInst Asset);
```

每个 `record` 含一个消息标识符 + payload。

通过 `WeakReferenceMessenger.Default.Send(msg)` 发送，VM 通过 `WeakReferenceMessenger.Default.Register<T>(this, handler)` 订阅。

---

## 9. Logic/Configuration/

### ConfigurationManager.cs
- `static class ConfigurationManager`
- `static ConfigurationValues Settings { get; }`
- `static void SaveConfig()`
- `static void LoadConfig()`

### ConfigurationValues.cs
- `class ConfigurationValues`
- 属性：`Theme`, `ListingNameLength`, `UseManagedOverIl2cpp`, `ExportImportJustNames`

### ConfigurationItem.cs
- `class ConfigurationItem`
- `event PropertyChanged`

### ConfigurationThemeType.cs
- `enum ConfigurationThemeType { SimpleDark, SimpleLight }`