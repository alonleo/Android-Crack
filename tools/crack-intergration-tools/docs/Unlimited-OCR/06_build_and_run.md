# 06 编译与运行

## 运行方式

### 1. 图片目录批量 OCR

```bash
python infer.py \
    --image_dir ./examples/images \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode gundam
```

### 2. PDF 多页并发 OCR

```bash
python infer.py \
    --pdf ./examples/document.pdf \
    --output_dir ./outputs \
    --concurrency 8 \
    --image_mode gundam
```

## CLI 参数表

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `--image_dir` | `""` | 图片目录路径（与 `--pdf` 二选一） |
| `--pdf` | `""` | PDF 文件路径 |
| `--output_dir` | `"./outputs"` | 输出 `.md` 目录 |
| `--concurrency` | `8` | 并发线程数 |
| `--gpu` | `"0"` | `CUDA_VISIBLE_DEVICES` 值 |
| `--model_dir` | `"baidu/Unlimited-OCR"` | 模型 ID 或本地路径 |
| `--image_mode` | `"gundam"` | `gundam`（base=1024/img=640/crop）或 `base`（base=1024/img=1024/no crop） |
| `--server_log` | `"./log/sglang_server.log"` | SGLang 服务日志路径 |

## 环境准备

### Python 依赖（依据 README:48-58 + infer.py:43）

```text
torch==2.10.0
torchvision==0.25.0
transformers==4.57.1
Pillow==12.1.1
matplotlib==3.10.8
einops==0.8.2
addict==2.4.0
easydict==1.13
pymupdf==1.27.2.2
psutil==7.2.2
requests>=2.28
```

### SGLang（必需）

仓库 `wheel/` 已附 SGLang wheel：

```bash
# 创建虚拟环境
uv venv --python 3.12
source .venv/bin/activate

# 安装内置 wheel
uv pip install wheel/sglang-0.0.0.dev11416+g92e8bb79e-py3-none-any.whl

# 固定依赖（与 wheel 兼容）
uv pip install kernels==0.9.0
uv pip install pymupdf==1.27.2.2
```

### GPU 要求

| 模型 | VRAM | CUDA |
|------|------|------|
| Unlimited-OCR (gundam mode) | ≥ 24 GB | 12.9 / 13.0 |
| Unlimited-OCR (base mode) | ≥ 16 GB | 12.9 / 13.0 |

## SGLang 服务启动参数（脚本自动）

`infer.py` 启动服务时使用以下参数（`start_server` 行 94-117）：

```
python -m sglang.launch_server \
    --model <args.model_dir> \
    --served-model-name Unlimited-OCR \
    --attention-backend fa3 \
    --page-size 1 \
    --mem-fraction-static 0.8 \
    --context-length 32768 \
    --enable-custom-logit-processor \
    --disable-overlap-schedule \
    --skip-server-warmup \
    --host 0.0.0.0 \
    --port 10000
```

## 关键常量（推断 `infer.py` 顶部，21-37 行）

| 常量 | 值 | 说明 |
|------|-----|------|
| `SERVED_MODEL_NAME` | `"Unlimited-OCR"` | OpenAI API 模型名 |
| `SERVER_URL` | `http://127.0.0.1:10000` | 默认服务地址 |
| `HOST` | `0.0.0.0` | 监听所有网卡 |
| `PORT` | `10000` | 监听端口 |
| `SERVER_TIMEOUT` | `300`（秒） | 服务启动超时 |
| `PDF_DPI` | `300` | PDF 转图片 DPI |
| `ATTENTION_BACKEND` | `"fa3"` | FlashAttention-3 |
| `PAGE_SIZE` | `1` | SGLang 页大小 |
| `MEM_FRACTION_STATIC` | `0.8` | KV cache 静态占比 |
| `PROMPT` | `"document parsing."` | 默认 prompt |
| `TEMPERATURE` | `0` | 确定性输出 |
| `CONTEXT_LENGTH` | `32768` | 最大上下文长度 |
| `NO_REPEAT_NGRAM_SIZE` | `35` | 禁用 n-gram 重复 |
| `NGRAM_WINDOW` | `128` | n-gram 检查窗口 |
| `REQUEST_TIMEOUT` | `1200`（秒） | HTTP 请求超时 |
| `MAX_RETRIES` | `5` | 最大重试次数 |

## 输出示例

`--image_dir ./examples/images --output_dir ./outputs` 后：

```
./outputs/
├── img_001.md
├── img_002.md
└── ...

./log/
└── sglang_server.log
```

`--pdf doc.pdf --output_dir ./outputs` 后：

```
./outputs/
├── doc_page_0001.md
├── doc_page_0002.md
└── doc_page_NNNN.md
```

## 退出码

| 退出方式 | 触发条件 |
|----------|----------|
| 正常退出 | `main` 函数返回（`finally` 执行 `stop_server`） |
| `RuntimeError` | SGLang 服务启动后立即退出（`process.poll() is not None`，行 128） |
| `TimeoutError` | `SERVER_TIMEOUT`（300 秒）内服务未 ready（行 136） |
| `ValueError` | 同时缺 `--image_dir` 和 `--pdf`（`build_jobs` 行 253） |
| HTTP 异常 | `requests.post` 抛 `RequestException`，被 `infer_one` catch |

## 常见问题

| 症状 | 原因 | 解决 |
|------|------|------|
| `RuntimeError: SGLang server exited early` | 模型加载失败或 GPU OOM | 查看 `--server_log` 详细错误 |
| `TimeoutError: Timed out waiting for SGLang server` | 服务启动超过 5 分钟 | 增大 `SERVER_TIMEOUT` 或检查 GPU 状态 |
| 大量 502 错误 | 并发过高超过 GPU 吞吐 | 降低 `--concurrency` |
| `ModuleNotFoundError: No module named 'sglang'` | SGLang 未安装 | 按 README 安装 wheel |
| `ImportError: DeepseekOCRNoRepeatNGramLogitProcessor` | SGLang 版本不匹配 | 使用仓库自带的 wheel 版本 |