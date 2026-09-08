# 01 项目概览

## 基本信息

| 字段 | 值 |
|------|----|
| 仓库 | `baidu/Unlimited-OCR` |
| 模型 | `baidu/Unlimited-OCR`（基于 DeepSeek-OCR 改进的长上下文 OCR） |
| 项目类型 | 推理客户端 CLI（不含模型权重） |
| 主文件 | `infer.py`（单文件，329 行） |
| 语言 | Python 3.12 |
| 第三方依赖 | `requests`、`PyMuPDF (fitz)`、本地 SGLang wheel（仓库 `wheel/` 已附） |
| 运行时外部依赖 | NVIDIA GPU + CUDA 12.9/13.0、SGLang 服务 |
| 平台 | Linux（CUDA），macOS/Windows 仅理论可行 |
| 入口 | `python infer.py --image_dir <dir> --output_dir <dir>` 或 `--pdf <file>` |

## 文件清单

```
Unlimited-OCR/
├── .gitignore                              # Python / 模型权重忽略
├── CONTRIBUTING.md                         # 贡献指南（29 行）
├── LICENSE                                 # 许可证（20 行）
├── README.md                               # 中文/英文使用文档（310 行）
├── Unlimited-OCR.pdf                      # 项目论文（2178 行，arXiv 2606.23050）
├── infer.py                                # 主脚本（329 行）
├── assets/
│   ├── baidu.png                           # 百度 logo
│   ├── long-horizon-ocr.gif                # 演示动画
│   └── Unlimited-OCR.png                   # 项目概览图
└── wheel/
    └── sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl  # 内置 SGLang wheel
```

## 与 DeepSeek-OCR 的关系

- **DeepSeek-OCR**：DeepSeek 在 2025 年推出的 OCR VLM
- **Unlimited-OCR**：百度 2026/06 发布，"push Deepseek-OCR one step further"
- 改进方向：**长上下文解析**（one-shot long-horizon parsing）
- 复用机制：Unlimited-OCR 直接使用 DeepSeek 的 `DeepseekOCRNoRepeatNGramLogitProcessor`（见 README:185）

## 主要使用场景

| 场景 | 价值 |
|------|------|
| 长文档解析（论文/书籍） | 一键转 Markdown |
| PDF 表格/公式识别 | 单页/多页均可 |
| 数据集批量 OCR | 目录 → 并发 → 多 .md |
| vLLM / SGLang 部署 | 提供官方 recipe + Docker 镜像 |
| 本地 GPU 部署 | 启动服务即可对外提供 OpenAI 兼容 API |

## 与 HuggingFace Transformers 路径的关系

README 给出三种推理路径：

| 路径 | 何时用 | 入口 |
|------|--------|------|
| **Transformers** | 单卡测试 / 简单脚本 | `model.infer(...)` / `model.infer_multi(...)` |
| **vLLM** | 高吞吐服务化部署 | vLLM recipe + Docker 镜像 |
| **SGLang** | 长上下文 + 自定义 logit 处理器 | `infer.py` + 本仓库内置 wheel |

**`infer.py` 仅覆盖 SGLang 路径**。Transformers / vLLM 路径的示例代码在 README 中，但不在仓库代码里。

## 约束 / 已知局限

| 约束 | 来源 |
|------|------|
| 单 GPU（`--gpu` 仅一个值） | `parse_args` 行 312 |
| 不支持 image dir + pdf 同时传入 | `build_jobs` 行 240-264 互斥分支 |
| 必须有 CUDA（PyMuPDF 之外的 SGLang 部分） | 隐含 |
| 流式响应解析只支持 OpenAI SSE 格式 | `collect_stream_silent` 行 157-181 |
| 服务进程必须能被启动（`sglang.launch_server`） | `start_server` 行 94-117 |
| 单进程管理 SGLang 服务（不支持远程已存在的服务复用） | `server_ready` 行 77-82 只能检测本地 |