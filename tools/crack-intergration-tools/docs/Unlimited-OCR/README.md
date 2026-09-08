# Unlimited-OCR 深度文档

> 源仓库：[`/home/leo/文档/android-crack/tools/source-projects/Unlimited-OCR`](../../Unlimited-OCR/)
> 作者：Baidu Inc. (Youyang Yin 等)
> 论文：arxiv:2606.23050 (2026/06)
> 类型：单文件 Python 3 CLI 脚本
> 体积：329 行 / 1 个主文件 `infer.py`
> 模型：`baidu/Unlimited-OCR`（基于 DeepSeek-OCR 改进）

## 项目定位

`infer.py` 是百度 Unlimited-OCR 模型的 **SGLang 并发推理客户端**。脚本自动启动 SGLang 服务、并发提交图片/PDF 请求、收集流式响应、写入 `.md` 输出。它不包含模型本身（模型从 HuggingFace `baidu/Unlimited-OCR` 下载）。

## 文档导航

| 文件 | 内容 |
|------|------|
| [01_overview.md](01_overview.md) | 项目定位、技术栈、与 DeepSeek-OCR 的关系 |
| [02_module_layout.md](02_module_layout.md) | 脚本结构 + 常量分组 + 函数分组 |
| [03_architecture.md](03_architecture.md) | 整体架构（mermaid：模块依赖 + 控制流 + 线程模型） |
| [04_data_flow.md](04_data_flow.md) | 数据从图片/PDF 到 .md 的全生命周期 |
| [05_operation_chains.md](05_operation_chains.md) | 7 条主要操作链（每条配 mermaid） |
| [06_build_and_run.md](06_build_and_run.md) | 运行方式、依赖、CLI 参数、SGLang 服务配置 |
| [07_functions_index.md](07_functions_index.md) | 14 个函数索引表 |
| [08_functions_detail.md](08_functions_detail.md) | 每个函数详细说明（单文件） |
| [09_callstacks.md](09_callstacks.md) | 关键调用栈汇总 |
| [10_glossary.md](10_glossary.md) | 术语表（SGLang / VLM / OCR / No-Repeat N-Gram / page_size / fa3） |

## 一句话总结

`infer.py` 的工作流：**parse_args → start_server (SGLang 子进程) → build_jobs (PDF 转图 或 扫描目录) → run (ThreadPoolExecutor 并发) → 每个线程 infer_one → collect_stream_silent → 输出 .md → stop_server**。