# rodroid-il2cppdumper 深度文档

Rodroid-Il2CppDumper：Perfare/Il2CppDumper 的 Rust + Svelte 5 + Tauri 2 重写版。

## 文档结构

| 文件 | 内容 |
|------|------|
| [README.md](./README.md) | 导航 |
| [01_overview.md](./01_overview.md) | 定位、版本、技术栈 |
| [02_directory_tree.md](./02_directory_tree.md) | 完整目录树 + 注释 |
| [03_architecture.md](./03_architecture.md) | 架构图 + 模块依赖 |
| [04_data_flow.md](./04_data_flow.md) | 核心数据结构 + 数据流 |
| [05_operation_chains.md](./05_operation_chains.md) | 8 条操作链 + mermaid |
| [06_build_and_run.md](./06_build_and_run.md) | 构建、运行、Tauri 命令、配置项 |
| [07_functions_index.md](./07_functions_index.md) | 全函数索引表 |
| [08_functions_detail/](./08_functions_detail/) | 函数详细说明 |
| [09_callstacks.md](./09_callstacks.md) | 关键调用栈 |
| [10_glossary.md](./10_glossary.md) | 术语表 |

## 阅读顺序

1. `01_overview.md`
2. `03_architecture.md` + `04_data_flow.md`
3. `05_operation_chains.md`
4. 按需要查阅 `07_functions_index.md` 与 `08_functions_detail/`

## 项目来源

- 仓库：<https://github.com/rodroid/rodroid-il2cppdumper>（推断）
- 关联项目：<https://github.com/nicehash/il2cpp_dumper>（原始 CLI 重写）
- 与本仓库的 Perfare/Il2CppDumper 配对阅读以理解"重写 vs 原版"的差异。