# Il2CppDumper 深度文档

Perfare/Il2CppDumper 的 C# 实现（`.NET 6/8`）—— Unity IL2CPP 二进制 + `global-metadata.dat` 反编译工具集。

## 文档结构

| 文件 | 内容 |
|------|------|
| [README.md](./README.md) | 本导航页 |
| [01_overview.md](./01_overview.md) | 项目定位、版本、技术栈、运行环境 |
| [02_directory_tree.md](./02_directory_tree.md) | 完整目录树 + 文件注释 |
| [03_architecture.md](./03_architecture.md) | 架构总览 + 模块依赖图（mermaid） |
| [04_data_flow.md](./04_data_flow.md) | 核心数据结构（Il2Cpp / Metadata / Config / Il2CppType ...）+ 数据流 |
| [05_operation_chains.md](./05_operation_chains.md) | 7 条主操作链 + mermaid 流程图 / 时序图 |
| [06_build_and_run.md](./06_build_and_run.md) | 编译、运行、CLI 参数、Config 字段 |
| [07_functions_index.md](./07_functions_index.md) | 全函数索引表（≥150 行） |
| [08_functions_detail/](./08_functions_detail/) | 函数详细说明（按模块） |
| [09_callstacks.md](./09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](./10_glossary.md) | 术语表（il2cpp 版本、PE/ELF/Mach-O、MonoBehaviour、CodeRegistration、MetadataRegistration、RGCTX、generic…） |

## 阅读顺序

1. 先读 `01_overview.md` 了解项目背景。
2. 再读 `03_architecture.md` + `04_data_flow.md` 掌握整体骨架。
3. 根据关注点选择：
   - 想理清"一次 dump 怎么跑起来" → `05_operation_chains.md`
   - 想知道"某个字段是干什么的" → `10_glossary.md`
   - 想知道"某个函数被谁调用" → `07_functions_index.md` → `08_functions_detail/`

## 项目来源

- 仓库：<https://github.com/Perfare/Il2CppDumper>
- 适用：Unity IL2CPP 编译产物（Android APK 内 `libil2cpp.so`、iOS IPA 内二进制、PC Player、`global-metadata.dat`、Switch NSO、WASM、PE）
- 与本仓库的 rodroid-il2cppdumper（Rust + Svelte 重写版）配对阅读效果更佳。