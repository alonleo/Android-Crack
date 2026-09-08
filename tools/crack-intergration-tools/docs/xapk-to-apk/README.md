# xapk-to-apk 深度文档

> 源仓库：[`/home/leo/文档/android-crack/tools/source-projects/xapk-to-apk`](../../xapk-to-apk/)
> 作者：LuigiVampa92
> 类型：单文件 Python 3 脚本（无第三方依赖）
> 体积：623 行 / 1 个主文件 `xapktoapk.py`
> 许可证：见 [`LICENSE.md`](../../xapk-to-apk/LICENSE.md)

## 项目定位

将 **`.xapk`** 文件（App Bundle 的 split 形式）转换为单一的 **fat `.apk`**，方便在不支持 split 包的旧设备或模拟器上安装。零 Python 依赖；运行时依赖系统 `$PATH` 中的三个外部工具：`apktool`、`zipalign`、`apksigner`。

## 文档导航

| 文件 | 内容 |
|------|------|
| [01_overview.md](01_overview.md) | 项目定位、技术栈、与 Android App Bundle 的关系 |
| [02_module_layout.md](02_module_layout.md) | 脚本结构 + 常量分组 + 函数分组 |
| [03_architecture.md](03_architecture.md) | 整体架构（mermaid：模块依赖 + 控制流） |
| [04_data_flow.md](04_data_flow.md) | 数据从 .xapk 到 .apk 的全生命周期 |
| [05_operation_chains.md](05_operation_chains.md) | 8 条主要操作链（每条配 mermaid） |
| [06_build_and_run.md](06_build_and_run.md) | 运行方式、依赖安装、配置文件、退出码 |
| [07_functions_index.md](07_functions_index.md) | 全部 36 个函数的索引表 |
| [08_functions_detail.md](08_functions_detail.md) | 每个函数的详细说明（单文件） |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表（xapk / split / doNotCompress / STAMP_TYPE / lib / res / assetpack） |

## 一句话总结

`xapk-to-apk` 的工作流：**解析 xapk → 拆出所有 .apk → apktool d -s 解包每个 → 把 arch/dpi/locale 分片的 `lib/`、`res/`、`assets/` 合并到主 APK → 修改 `AndroidManifest.xml` 去掉 split 标记 → apktool b 重新打包 → zipalign → apksigner 签名**。