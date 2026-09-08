# 10 术语表

| 术语 | 解释 |
|------|------|
| **OCR** | Optical Character Recognition，光学字符识别。从图像中提取文字。 |
| **VLM** | Vision-Language Model，视觉语言模型。同时处理图像和文本的大模型。 |
| **DeepSeek-OCR** | DeepSeek 在 2025 年发布的开源 OCR VLM。Unlimited-OCR 在其基础上改进长上下文能力。 |
| **Unlimited-OCR** | 百度 2026/06 发布的 OCR VLM。论文：arXiv:2606.23050。模型 ID：`baidu/Unlimited-OCR`。 |
| **one-shot long-horizon parsing** | 一次性长上下文解析。Unlimited-OCR 的核心能力：单次前向传播处理超长文档。 |
| **SGLang** | 高性能 LLM/VLM 服务框架。提供 OpenAI 兼容 API。仓库：`sgl-project/sglang`。 |
| **vLLM** | 另一主流 LLM 服务框架。Unlimited-OCR 也支持（见 README）。 |
| **HuggingFace Transformers** | HF 的模型推理库。最简单但性能不如 SGLang/vLLM。 |
| **gundam mode** | Unlimited-OCR 单图模式之一：`base_size=1024, image_size=640, crop_mode=True`。适合高分辨率文档。 |
| **base mode** | Unlimited-OCR 单图模式之一：`base_size=1024, image_size=1024, crop_mode=False`。多页/PDF 只能用此模式。 |
| **No-Repeat N-Gram** | 文本生成约束。禁止模型重复输出已出现的 n-gram。在 OCR 中用于避免重复识别同一区块。 |
| **DeepseekOCRNoRepeatNGramLogitProcessor** | DeepSeek-OCR 的 SGLang logit 处理器实现。脚本通过 `get_ngram_processor_str` 注入。 |
| **Custom Logit Processor** | SGLang 的扩展机制。在采样阶段自定义 logits 修改。本脚本用此机制注入 no-repeat n-gram。 |
| **SSE** | Server-Sent Events。基于 HTTP 的流式协议。OpenAI API 流式响应使用此格式。 |
| **OpenAI Multimodal Message** | OpenAI Chat API 格式：`messages[].content: [{type:text,text:...}, {type:image_url,...}]`。 |
| **page_size** | SGLang 参数。KV cache 的页大小（连续分配单元）。脚本设为 1，减少长上下文碎片。 |
| **fa3** | FlashAttention-3。脚本指定 SGLang 用此 attention 后端提升性能。 |
| **attention_backend** | SGLang 参数。选择 attention 实现。脚本硬编码 `fa3`。 |
| **mem_fraction_static** | SGLang 参数。KV cache 静态占用显存比例。脚本设为 0.8（80%）。 |
| **context_length** | SGLang 参数。最大序列长度。脚本设为 32768（与 Unlimited-OCR 设计一致）。 |
| **skip-server-warmup** | SGLang 参数。跳过启动时的预热推理。脚本启用以加速启动。 |
| **disable-overlap-schedule** | SGLang 参数。禁用请求调度与计算的重叠。脚本启用以稳定 Custom Logit Processor。 |
| **enable-custom-logit-processor** | SGLang 参数。允许请求中带 `custom_logit_processor` 字段。脚本必须启用。 |
| **Base64 Data URL** | `data:image/png;base64,<编码>` 格式。OpenAI API 直接接受此格式的图片。 |
| **PyMuPDF (fitz)** | Python PDF 处理库。脚本用于 PDF 转图片。 |
| **DPI** | Dots Per Inch。图片分辨率。脚本 PDF 转图用 300 DPI（高质量）。 |
| **max_retries** | HTTP 重试次数。脚本设为 5。502 错误特殊处理（指数退避）。 |
| **502 Bad Gateway** | HTTP 状态码。SGLang 过载时常见。脚本对此单独重试。 |
| **Concurrency vs Parallelism** | 本脚本是并发（线程 + HTTP I/O），非并行（无多进程）。GPU 在服务端，客户端只做 I/O。 |
| **tmp_dir** | 临时目录。脚本用 `tempfile.mkdtemp(prefix='pdf_ocr_')` 创建在系统 tmp 下，**未清理**。 |
| **stream=True** | requests 参数。开启流式响应，避免长响应超时。 |
| **iter_lines** | requests Response 方法。按行迭代流式响应，自动处理 chunked encoding。 |
| **Popen** | subprocess 方法。启动子进程。脚本用此启动 SGLang。 |
| **terminate()** | subprocess 方法。发送 SIGTERM。脚本优雅关闭的第一步。 |
| **kill()** | subprocess 方法。发送 SIGKILL。terminate 超时后强制使用。 |
| **CUDA_VISIBLE_DEVICES** | 环境变量。控制可见 GPU。脚本通过 `--gpu` 注入。 |
| **exit code** | 进程退出码。脚本无显式 `sys.exit`，依赖 Python 默认异常处理。 |

## 缩写速查

| 缩写 | 全称 |
|------|------|
| OCR | Optical Character Recognition |
| VLM | Vision-Language Model |
| LLM | Large Language Model |
| SSE | Server-Sent Events |
| DPI | Dots Per Inch |
| KV | Key-Value（cache） |
| CPU | Central Processing Unit |
| GPU | Graphics Processing Unit |
| HTTP | HyperText Transfer Protocol |
| API | Application Programming Interface |
| CLI | Command Line Interface |
| N-Gram | N 个连续 token 的序列 |
| TPS | Tokens Per Second |
| Popen | Process Open |
| PID | Process ID |
| SIGTERM | Signal Terminate |
| SIGKILL | Signal Kill |
| OOM | Out Of Memory |
| tmp | Temporary |