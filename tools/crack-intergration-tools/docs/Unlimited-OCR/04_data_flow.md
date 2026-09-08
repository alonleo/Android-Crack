# 04 数据流

## 全生命周期

```mermaid
stateDiagram-v2
    [*] --> InputArgv: 用户传 --image_dir 或 --pdf
    InputArgv --> ParsedArgs: parse_args()
    ParsedArgs --> ServerCheck: start_server → server_ready
    ServerCheck --> Reuse: 服务已运行
    ServerCheck --> Spawn: 需启动
    Spawn --> SGLangBoot: Popen(sglang.launch_server)
    SGLangBoot --> SGLangReady: GET /health = 200
    Reuse --> BuildJobs: run() 入口
    SGLangReady --> BuildJobs
    BuildJobs --> Jobs: (image_path, output_file) 列表
    Jobs --> SubmitJobs: executor.submit(infer_one, ...)
    SubmitJobs --> HttpRequest: POST /v1/chat/completions
    HttpRequest --> StreamSSE: SSE 流式响应
    StreamSSE --> CollectChunks: collect_stream_silent
    CollectChunks --> WriteMd: open(output_file, w).write(delta)
    WriteMd --> AggregateStats: tokens/decode_time 累加
    AggregateStats --> Done
    StreamSSE --> Retry502: status 502
    Retry502 --> HttpRequest: attempt+1, sleep 3*(attempt+1)
    StreamSSE --> Exception: 其他错误
    Exception --> RetryOrFail: catch
    RetryOrFail --> HttpRequest: attempt+1
    RetryOrFail --> FailureRecord: tokens=0 软失败
    FailureRecord --> Done
    Done --> StopServer: finally
    StopServer --> [*]
```

## 数据结构

脚本没有自定义类，所有数据用 `dict` / `list` / `tuple` 承载。

### `args` 命名空间（`argparse.Namespace`，`parse_args` 返回）

```python
args = Namespace(
    image_dir="",           # str: 图片目录路径
    pdf="",                 # str: PDF 文件路径
    output_dir="./outputs", # str: 输出目录
    concurrency=8,          # int: 线程池大小
    gpu="0",                # str: CUDA_VISIBLE_DEVICES 值
    model_dir="baidu/Unlimited-OCR",  # str: 模型 ID 或本地路径
    image_mode="gundam",    # str: "gundam" | "base"
    server_log="./log/sglang_server.log",  # str: 服务日志路径
)
```

### OpenAI multimodal message（`build_content` 返回）

```python
[
    {"type": "text", "text": "document parsing."},  # PROMPT
    {
        "type": "image_url",
        "image_url": {
            "url": "data:image/png;base64,iVBORw0KGgo..."
        }
    }
]
```

### 推理 payload（`infer_one` 构造）

```python
{
    "model": "Unlimited-OCR",
    "messages": [{"role": "user", "content": [...] }],
    "temperature": 0,
    "skip_special_tokens": False,
    "stream": True,
    "images_config": {"image_mode": "gundam"},
    # 可选：仅当 NO_REPEAT_NGRAM_SIZE > 0 且 NGRAM_WINDOW > 0
    "custom_logit_processor": "DeepseekOCRNoRepeatNGramLogitProcessor.to_str()",
    "custom_params": {
        "ngram_size": 35,
        "window_size": 128,
    },
}
```

### 单任务结果（`collect_stream_silent` / `infer_one` 返回）

```python
{
    "tokens": int,         # token 数（增量计数）
    "decode_time": float,  # 首个 token 到最后一个 token 的耗时（秒）
    "text": str,           # 完整文本拼接
}
```

### Job 列表（`build_jobs` 返回）

```python
[
    ("/abs/path/image1.png", "/output/dir/image1.md"),  # or None
    ("/abs/path/image2.png", "/output/dir/image2.md"),
    ...
]
```

## 文件系统布局变化

```mermaid
flowchart LR
    subgraph In["输入"]
        D0[image_dir/]
        D1[file.pdf]
    end

    subgraph Tmp["./tmp 系统临时目录"]
        T0[pdf_ocr_xxx/page_0001.png]
        T1[pdf_ocr_xxx/page_0002.png]
        Tn[pdf_ocr_xxx/page_NNNN.png]
    end

    subgraph Net["HTTP 传输"]
        N0[base64 data URL<br/>data:image/png;base64,...]
    end

    subgraph Out["./outputs/ 或 --output_dir"]
        O0[image1.md]
        O1[doc_page_0001.md]
        O2[doc_page_0002.md]
        On[doc_page_NNNN.md]
    end

    subgraph Log["./log/"]
        L0[sglang_server.log]
    end

    D0 -->|os.walk + 排序| Net
    D1 -->|fitz 转图| Tmp
    Tmp -->|encode_image| Net
    Net -.POST.-> SGLang[SGLang Server]
    SGLang -.SSE.-> Net
    Net -->|delta 拼接| Out
    D1 -->|派生 prefix| On
    D0 -->|relpath 去前缀| O0
    SGLang -.stdout.-> L0
```

## HTTP 通信协议

```mermaid
sequenceDiagram
    participant C as Client (infer_one)
    participant S as SGLang Server

    C->>S: POST /v1/chat/completions
    Note over C,S: Content-Type: application/json<br/>stream: true<br/>model: Unlimited-OCR
    S-->>C: HTTP/1.1 200 OK
    Note over S: Content-Type: text/event-stream

    loop 每个 token
        S-->>C: data: {"choices":[{"delta":{"content":"..."}}]}
    end

    S-->>C: data: [DONE]

    alt 502 Bad Gateway
        S-->>C: HTTP 502
        C->>C: sleep 3*(attempt+1)
        C->>S: POST /v1/chat/completions (retry)
    end
```

## 关键数据变换

| 阶段 | 输入 | 输出 |
|------|------|------|
| PDF → 图片 | `file.pdf` | `[png_path_1, png_path_2, ...]` (tmpdir 下) |
| 图片 → base64 | `image.png` | `data:image/png;base64,<base64>` |
| base64 → message | base64 URL | OpenAI content array |
| message → payload | content array | request body dict |
| SSE → 文本 | SSE 流 | `{"tokens": N, "decode_time": t, "text": str}` |
| text → .md | text | 写入 `<output_dir>/<stem>.md` |