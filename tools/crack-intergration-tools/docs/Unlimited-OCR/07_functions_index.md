# 07 函数索引

所有 14 个函数按行号排序。完整说明见 [`08_functions_detail.md`](08_functions_detail.md)。

| # | 函数名 | 行号 | 分组 | 一句话职责 |
|---|--------|------|------|------------|
| 1 | `get_ngram_processor_str` | 40 | 模型/Logit | 延迟导入 `DeepseekOCRNoRepeatNGramLogitProcessor` 并返回其 `to_str()` |
| 2 | `pdf_to_images` | 50 | 数据准备 | 把 PDF 每页转 PNG，返回路径列表 |
| 3 | `encode_image` | 65 | 数据准备 | 图片 → base64 data URL |
| 4 | `build_content` | 73 | 数据准备 | 构造 OpenAI multimodal message |
| 5 | `server_ready` | 77 | 服务管理 | GET `/health` 检查 SGLang 服务健康 |
| 6 | `start_server` | 85 | 服务管理 | subprocess.Popen 启动 SGLang + 轮询 readiness |
| 7 | `stop_server` | 139 | 服务管理 | terminate / kill SGLang 子进程 |
| 8 | `collect_stream_silent` | 151 | 请求处理 | 解析 SSE 流 → 写文件 + 计时 + 累计 |
| 9 | `infer_one` | 188 | 请求处理 | 单图片 POST → 重试 → 返回 dict |
| 10 | `collect_dataset_images` | 230 | 请求处理 | os.walk 扫描目录 + 按文件大小倒排 |
| 11 | `build_jobs` | 240 | 编排 | PDF 模式 / image_dir 模式 → job 列表 |
| 12 | `run` | 267 | 编排 | ThreadPoolExecutor 并发执行 + 统计 |
| 13 | `parse_args` | 303 | 编排 | argparse CLI |
| 14 | `main` | 319 | 编排 | 顶层编排（启动 → run → 关闭） |

## 按调用频度统计

### 被 `main` 直接调用（4 个）

```python
main() 直接调用:
- parse_args()       行 320
- start_server()     行 321
- run()              行 323
- stop_server()      行 325 (finally)
```

### `start_server` 调用链

```
start_server → server_ready (× 多次)
start_server → subprocess.Popen
start_server → time.sleep / time.time
start_server → os.makedirs, os.path.dirname, os.path.abspath
```

### `run` 调用链

```
run → build_jobs → pdf_to_images / collect_dataset_images
run → os.makedirs
run → ThreadPoolExecutor → infer_one (× N)
run → as_completed → future.result()
run → sum / len 统计
```

### `infer_one` 调用链

```
infer_one → build_content → encode_image
infer_one → get_ngram_processor_str (条件)
infer_one → requests.post
infer_one → collect_stream_silent
infer_one → resp.raise_for_status / json.dumps / time.sleep
```

## 模块统计

| 分组 | 函数数 | 占比 |
|------|--------|------|
| A. 模型/Logit 配置 | 1 | 7% |
| B. 数据准备 | 3 | 21% |
| C. 服务管理 | 3 | 21% |
| D. 请求处理 | 3 | 21% |
| E. 编排 | 4 | 29% |
| **总计** | **14** | **100%** |

## 全局状态

| 名称 | 类型 | 行号 | 说明 |
|------|------|------|------|
| `SERVED_MODEL_NAME` | `str` 常量 | 21 | OpenAI API 模型名 |
| `SERVER_URL` | `str` 常量 | 22 | 默认服务地址 |
| `HOST` | `str` 常量 | 23 | 监听网卡 |
| `PORT` | `int` 常量 | 24 | 监听端口 |
| `SERVER_TIMEOUT` | `int` 常量 | 25 | 启动超时秒数 |
| `PDF_DPI` | `int` 常量 | 26 | PDF 转图片 DPI |
| `ATTENTION_BACKEND` | `str` 常量 | 27 | SGLang attention 后端 |
| `PAGE_SIZE` | `int` 常量 | 28 | SGLang 页大小 |
| `MEM_FRACTION_STATIC` | `float` 常量 | 29 | KV cache 静态占比 |
| `PROMPT` | `str` 常量 | 30 | 默认 prompt |
| `TEMPERATURE` | `int` 常量 | 31 | 采样温度 |
| `CONTEXT_LENGTH` | `int` 常量 | 32 | 最大上下文长度 |
| `NO_REPEAT_NGRAM_SIZE` | `int` 常量 | 33 | 禁用 n-gram 重复大小 |
| `NGRAM_WINDOW` | `int` 常量 | 34 | n-gram 检查窗口 |
| `REQUEST_TIMEOUT` | `int` 常量 | 35 | HTTP 请求超时 |
| `MAX_RETRIES` | `int` 常量 | 36 | 最大重试次数 |
| `NO_REPEAT_NGRAM_PROCESSOR_STR` | `Optional[str]` 全局变量 | 37, 41-47 | logit processor 字符串缓存 |