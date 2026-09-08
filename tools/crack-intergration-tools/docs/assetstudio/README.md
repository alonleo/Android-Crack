# AssetStudio 文档导航

本目录包含 `assetstudio` 项目（Razmoth fork of Perfare/AssetStudio）的完整深度技术文档，覆盖项目架构、源码目录、核心数据流、主要操作链、CLI 参数以及所有 public/internal 函数级索引与详细说明。

## 项目一句话定位

**AssetStudio** 是一个用 C# 写的 Unity 资源浏览器与导出器，能够直接解析 Unity 的 `UnityFS` / `UnityWeb` / `ENCR` / `BlockFile` / `Blk` / `Blb` / `Mhy` 等容器格式，从中重建 `SerializedFile` 元数据与对象表，再依据 `TypeTree` 把对象反序列化成强类型（`Texture2D`、`Mesh`、`GameObject`、`Shader`、`MonoBehaviour` 等），最终把 Texture 导出为 PNG/JPG/WebP、把 Mesh/Animator/GameObject 导出为 OBJ/FBX、把 Shader 反编译为 HLSL/GLSL/SPIRV、把 MonoBehaviour 反序列化为 JSON。

它有两种运行形态：

- **GUI**（WinForms，`AssetStudio.GUI`）+ **OpenTK** 3D 预览 + **FMOD** 音频预览
- **CLI**（`System.CommandLine`，`AssetStudio.CLI`）：headless 批量导出

## 文档结构

| 编号 | 文件 | 内容 |
|---|---|---|
| — | [README.md](README.md) | 当前页：项目导航 |
| 01 | [01_overview.md](01_overview.md) | 项目定位、版本、技术栈、运行模式（GUI/CLI） |
| 02 | [02_directory_tree.md](02_directory_tree.md) | 完整目录树，每个文件附 1-2 行说明 |
| 03 | [03_architecture.md](03_architecture.md) | 架构总览 + 模块依赖 / 类继承 mermaid |
| 04 | [04_data_flow.md](04_data_flow.md) | 核心数据结构（AssetsManager、BundleFile、SerializedFile、GameManager）+ 数据流 mermaid |
| 05 | [05_operation_chains.md](05_operation_chains.md) | 8 条主要操作链，每条含文字描述 + mermaid 调用栈时序图 + 关键函数清单 |
| 06 | [06_build_and_run.md](06_build_and_run.md) | 编译命令、运行命令、CLI 参数表 |
| 07 | [07_functions_index.md](07_functions_index.md) | 所有 public/internal 函数的索引表 |
| 08 | [08_functions_detail/](08_functions_detail/) | 按模块分文件的函数详细说明 |
| 09 | [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| 10 | [10_glossary.md](10_glossary.md) | 术语表 |

## 关键名词速查

- **UnityFS**：Unity 5+ 的标准打包容器（Header + BlocksInfo + Blocks + Directory）
- **SerializedFile**：Unity 中单个 .assets / .unity3d 的元数据 + 对象表容器
- **TypeTree**：SerializedFile 中描述每个类结构的反射信息
- **Mr0k / Blk / Mhy**：米哈游及其合作方的私有加密流（参见 `GameManager.cs`）
- **FbxExporter**：通过原生 `AssetStudio.FBXNative.dll`（C++）把 `ModelConverter` 中间表示写入 .fbx
- **CABMap / AssetMap**：帮助定位 CAB 偏移的缓存索引（`AssetsHelper`）

## 推荐阅读顺序

1. 想了解项目能做什么 → `01_overview.md`
2. 想了解项目由哪些文件组成 → `02_directory_tree.md`
3. 想理解模块之间的关系 → `03_architecture.md`
4. 想理解一个 Bundle 从磁盘到反序列化的全过程 → `04_data_flow.md` → `05_operation_chains.md`
5. 想编译/运行/查 CLI 参数 → `06_build_and_run.md`
6. 想按文件查函数签名 → `07_functions_index.md` → `08_functions_detail/`
7. 想追踪特定用户操作的完整调用栈 → `09_callstacks.md`
8. 术语不认识 → `10_glossary.md`