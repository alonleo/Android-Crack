# 03 架构

## 整体架构

脚本分四层：CLI → 服务管理 → 任务编排 → 单任务执行。脚本本身作为**客户端**驱动 SGLang 服务（子进程），并通过 OpenAI 兼容 HTTP API 与之通信。

```mermaid
flowchart TD
    subgraph Layer1["Layer 1 · CLI 入口"]
        A[main 行 319]
        A1[parse_args 行 303]
        A --> A1
    end

    subgraph Layer2["Layer 2 · 服务管理"]
        B1[start_server 行 85]
        B2[server_ready 行 77]
        B3[stop_server 行 139]
        A --> B1
        B1 --> B2
        A --> B3
    end

    subgraph Layer3["Layer 3 · 任务编排"]
        C1[build_jobs 行 240]
        C2[run 行 267]
        A --> C2
        C2 --> C1
        C1 --> D1[pdf_to_images]
        C1 --> D2[collect_dataset_images]
    end

    subgraph Layer4["Layer 4 · 单任务执行"]
        D3[infer_one 行 188]
        D4[build_content 行 73]
        D5[encode_image 行 65]
        D6[collect_stream_silent 行 151]
        D7[get_ngram_processor_str 行 40]
        C2 --> D3
        D3 --> D4
        D4 --> D5
        D3 --> D6
        D3 --> D7
    end

    subgraph Ext["外部进程"]
        E1[SGLang Server<br/>sglang.launch_server]
        E2[Unlimited-OCR 模型<br/>HuggingFace]
        B1 -.启动.-> E1
        E1 -.加载.-> E2
        D3 -.HTTP POST.-> E1
    end
```

## 线程模型

```mermaid
flowchart TD
    Main[主线程<br/>main]
    SP[SGLang 服务进程<br/>subprocess.Popen]
    T1[工作线程 1<br/>infer_one]
    T2[工作线程 2<br/>infer_one]
    Tn[工作线程 N<br/>infer_one]
    Main -.Popen.-> SP
    Main --> TPE[ThreadPoolExecutor<br/>max_workers=concurrency]
    TPE --> T1
    TPE --> T2
    TPE --> Tn
    T1 -.HTTP.-> SP
    T2 -.HTTP.-> SP
    Tn -.HTTP.-> SP
```

- **主线程**：CLI 解析 → 启动服务 → 提交任务 → 收集 Future → 打印统计 → 关闭服务
- **SGLang 子进程**：加载模型 + 监听 `0.0.0.0:10000` + 处理推理请求
- **工作线程池**：N 个线程（默认 8），每个线程顺序执行 `infer_one`

## 启动流程

```mermaid
sequenceDiagram
    participant U as User
    participant Main as main()
    participant SA as start_server
    participant SR as server_ready
    participant SP as subprocess
    participant SG as SGLang Server

    U->>Main: python infer.py --image_dir X
    Main->>Main: parse_args()
    Main->>SA: start_server(args)
    SA->>SR: server_ready(url)?
    SR-->>SA: True/False
    alt 服务已存在
        SA-->>Main: return None
    else 需启动
        SA->>SP: Popen(sglang.launch_server [...])
        SP-->>SA: process
        loop 轮询 health
            SA->>SR: server_ready(url)?
            SR->>SG: GET /health
            SG-->>SR: 200
            SR-->>SA: True
        end
        SA-->>Main: return process
    end
    Main->>Main: run(args)
    Main->>Main: stop_server(process)
    Main->>SP: terminate
```

## 数据生命周期

```mermaid
stateDiagram-v2
    [*] --> Input
    Input --> PdfPages: --pdf
    Input --> ImageDir: --image_dir
    PdfPages --> PdfConverted: pdf_to_images
    ImageDir --> ScannedImages: collect_dataset_images
    PdfConverted --> JobList: build_jobs
    ScannedImages --> JobList
    JobList --> InFlight: executor.submit
    InFlight --> StreamResponse: requests.post stream
    StreamResponse --> CollectChunks: collect_stream_silent
    CollectChunks --> WriteFile: 输出 .md
    WriteFile --> Done
    StreamResponse --> Retry502: 502 error
    Retry502 --> InFlight: attempt+1
    StreamResponse --> Failed: max retries exceeded
    Failed --> Done
    Done --> [*]
```

## 单任务执行链（`infer_one`）

```mermaid
flowchart TD
    Start([infer_one image_path, output_file, args, idx]) --> Payload[构造 payload dict]
    Payload --> NgramCheck{NO_REPEAT_NGRAM_SIZE > 0?}
    NgramCheck -->|Yes| AddProcessor[payload.custom_logit_processor<br/>+ custom_params]
    NgramCheck -->|No| Skip[skip]
    AddProcessor --> LoopStart{for attempt in 0..MAX_RETRIES}
    Skip --> LoopStart
    LoopStart -->|attempt| PostReq[POST /v1/chat/completions stream]
    PostReq --> CheckStatus{status_code?}
    CheckStatus -->|502 + attempt < N| Sleep3[sleep 3*attempt+1] --> LoopStart
    CheckStatus -->|200| CollectStream[collect_stream_silent]
    CheckStatus -->|Other| RaiseError[raise_for_status]
    RaiseError --> CatchException{catch Exception}
    CatchException -->|attempt < N| PrintRetry[print retry] --> LoopStart
    CatchException -->|attempt == N| ReturnFailed[return {tokens:0,...}]
    CollectStream --> PrintResult[print idx tokens decode_time]
    PrintResult --> ReturnOK[return result]
    ReturnOK --> End([end])
    ReturnFailed --> End
```

## 关键设计决策

| 决策 | 原因 |
|------|------|
| SGLang 而非 Transformers 默认 | 高吞吐 + 长上下文 + 自定义 logit processor |
| `subprocess.Popen` 启动服务 | 单一 Python 进程管理生命周期，简化调用 |
| `ThreadPoolExecutor` 而非 `ProcessPoolExecutor` | HTTP I/O 密集而非 CPU 密集；GPU 在服务端 |
| 服务复用检测 | `server_ready` 优先于 Popen，避免端口冲突 |
| 流式 + 静默 | 用户只关心最终 .md，过程 token 不打印（区别于 README 示例） |
| 重试 502 单独处理 | SGLang 偶发 502 是过载特征，标准 backoff |
| `get_ngram_processor_str` 延迟导入 | 不强制依赖 SGLang 在解析阶段就加载 |
| `--gpu` 单值 | 简化部署；多卡留给 vLLM/SGLang 内部调度 |