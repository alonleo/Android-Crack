# 08 · `Bin2Object`（子模块 — 未初始化）

> **状态**：子模块未初始化，目录为空（`/home/leo/文档/android-crack/tools/source-projects/Il2CppInspectorPro/Bin2Object/` 无任何文件）。

## 已知信息（基于 inventory + 项目惯例）

- **来源**: `https://github.com/LukeFZ/Bin2Object`
- **声明位置**: `Il2CppInspectorPro/.gitmodules`
- **被引用位置**:
  - `Il2CppInspector.Common/Il2CppInspector.csproj`: `<ProjectReference Include="..\Bin2Object\Bin2Object\Bin2Object.csproj" PrivateAssets="all" />`
  - `Il2Inspector.GUI/Il2Inspector.GUI.csproj`: `ProjectReference → Bin2Object`
  - `Il2Inspector.Redux.FrontendCore/Il2Inspector.Redux.FrontendCore.csproj`: `ProjectReference → Bin2Object`
- **预期类型**:
  - `BinaryObjectStream`：seeka­ble、endian-aware 二进制流
  - `BinaryObjectStreamReader`：扩展类（含 `StructVersion` 的子类在 `Common/Next/BinaryObjectStreamReader.cs`）
  - `FormatLayouts/*` 用 Bin2Object 属性标注 PE/ELF/MachO/NSO/UB 结构
- **预期用法**:
  - `FileFormatStream.Load(stream)` 拷贝 stream 到 `BinaryObjectStream`
  - `Metadata.FromStream(MemoryStream)` 包装为 `BinaryObjectStream` 后再 `Read`
  - `Il2CppBinary.PrepareMetadata` 用 `Image.ReadMappedVersionedObject<T>`，底层走 Bin2Object 的字段读取

## 初始化方式

```bash
cd /home/leo/文档/android-crack/tools/source-projects/Il2CppInspectorPro
git submodule update --init --recursive
```

初始化后，本目录才会有：
- `Bin2Object/Bin2Object/Bin2Object.csproj`
- `Bin2Object/Bin2Object/src/*.cs`
- `Bin2Object/Bin2Object/src/Enums/*`
- 等等

## 跳过理由

- 文档遵守规范：`*.cs` 文件须用 `Glob`/`Read` 重新核实函数签名
- 该子模块为空，无法核实任何函数签名
- 仓库顶部 `inventory.md` 已注明「子模块未初始化」

> 标记：**已跳过**。重新初始化后可补一份 `bin2object.md`。