# 05 操作链

脚本的"操作链"是 7 条从 CLI 参数到 .md 输出的数据流。所有链汇聚到 `main()` 终点（`./outputs/*.md`）。

## 链 1 — CLI 解析

```mermaid
flowchart TD
    A([python infer.py --image_dir X]) --> B[main 行 319]
    B --> C[parse_args 行 303]
    C --> D{argparse 解析}
    D --> E[Namespace 实例]
    E --> F[args.image_dir]
    E --> G[args.pdf]
    E --> H[args.output_dir]
    E --> I[args.concurrency]
    E --> J[args.gpu]
    E --> K[args.model_dir]
    E --> L[args.image_mode]
    E --> M[args.server_log]
```

**关键函数**：`main`(319) · `parse_args`(303)

## 链 2 — SGLang 服务生命周期

```mermaid
sequenceDiagram
    participant Main as main()
    participant Start as start_server
    participant Ready as server_ready
    participant Popen as subprocess.Popen
    participant SGLang as SGLang

    Main->>Start: start_server(args) (行 321)
    Start->>Ready: server_ready(SERVER_URL) (行 86)
    Ready->>SGLang: GET /health (timeout 5)
    alt 健康
        SGLang-->>Ready: 200 OK
        Ready-->>Start: True
        Start-->>Main: None (复用)
    else 不可用
        Ready-->>Start: False
        Start->>Start: mkdir server_log 目录 (行 90)
        Start->>Start: 设置 CUDA_VISIBLE_DEVICES (行 92)
        Start->>Popen: Popen(sglang.launch_server [...]) (行 121)
        Popen-->>Start: process (PID)
        Start->>Start: 记录 process._log_file
        loop 每 3 秒轮询，最多 SERVER_TIMEOUT
            Start->>Ready: server_ready(URL) (行 130)
            alt process 已退出
                Start->>Start: raise RuntimeError
            else 服务就绪
                Ready->>SGLang: GET /health
                SGLang-->>Ready: 200 OK
                Ready-->>Start: True
                Start-->>Main: process
            end
            Start->>Start: sleep(3)
        end
        Start->>Start: stop_server + raise TimeoutError
    end
```

**关键函数**：`start_server`(85) · `server_ready`(77) · `stop_server`(139) · `subprocess.Popen` · `time.sleep`

## 链 3 — Job 列表构建

```mermaid
flowchart TD
    A[build_jobs args 行 240] --> B{args.pdf?}
    B -->|非空| C[pdf_to_images args.pdf PDF_DPI]
    C --> D[image_files = PNG 路径列表]
    D --> E[遍历每个 image_path]
    E --> F{args.output_dir?}
    F -->|是| G[output_file = prefix_page_NNNN.md]
    F -->|否| H[output_file = None]
    G --> I[jobs.append]
    H --> I
    B -->|空| J[collect_dataset_images args.image_dir]
    J --> K{args.image_dir?}
    K -->|空| L[raise ValueError]
    K -->|非空| M[os.walk + 大小倒排]
    M --> N[遍历每个 image_path]
    N --> O{args.output_dir?}
    O -->|是| P[output_file = relpath 替换分隔符.md]
    O -->|否| H
    P --> Q[jobs.append]
    I --> R[return jobs]
    Q --> R
```

**关键函数**：`build_jobs`(240) · `pdf_to_images`(50) · `collect_dataset_images`(230) · `os.path.relpath` · `os.walk`

## 链 4 — 并发调度（核心）

```mermaid
sequenceDiagram
    participant Main as main → run
    participant TPE as ThreadPoolExecutor
    participant Worker as infer_one (N 副本)
    participant SGLang as SGLang Server
    participant FS as FileSystem

    Main->>Main: jobs = build_jobs(args) (行 268)
    Main->>Main: os.makedirs(output_dir) (行 270)
    Main->>Main: print mode/requests/concurrency (行 273)
    Main->>Main: wall_start = time.time()
    Main->>TPE: ThreadPoolExecutor(max_workers=concurrency) (行 277)
    loop 每个 job
        Main->>TPE: executor.submit(infer_one, image, output, args, i+1)
    end
    TPE->>Worker: 创建 Future
    loop as_completed futures
        Worker->>Worker: payload 构造 (行 189-196)
        Worker->>Worker: 注入 logit_processor (行 197-202)
        loop attempt 0..MAX_RETRIES
            Worker->>SGLang: POST /v1/chat/completions stream (行 207)
            alt 200
                SGLang-->>Worker: SSE 流
                Worker->>Worker: collect_stream_silent (行 218)
                Worker->>FS: 写 output_file
                Worker->>Worker: print stats
                Worker-->>TPE: return result
            else 502 + retryable
                Worker->>Worker: sleep(3*(attempt+1)) (行 215)
            else 其他异常
                Worker->>Worker: catch Exception
                alt attempt < MAX_RETRIES-1
                    Worker->>Worker: print retry + sleep
                else
                    Worker-->>TPE: return {tokens:0,...}
                end
            end
        end
        TPE-->>Main: future.result() (行 283)
        Main->>Main: results.append
    end
    Main->>Main: wall_time = time.time() - wall_start
    Main->>Main: 统计打印 (行 286-300)
```

**关键函数**：`run`(267) · `infer_one`(188) · `collect_stream_silent`(151) · `ThreadPoolExecutor` · `as_completed`

## 链 5 — 单图片推理（`infer_one` 详细）

```mermaid
flowchart TD
    Start([infer_one image_path output_file args idx]) --> Payload[构造 payload dict 行 189-196]
    Payload --> NgramEnable{NO_REPEAT_NGRAM_SIZE > 0<br/>and NGRAM_WINDOW > 0?}
    NgramEnable -->|Yes| GetStr[get_ngram_processor_str 行 198]
    NgramEnable -->|No| Loop
    GetStr --> Inject[payload.custom_logit_processor<br/>+ custom_params 行 199-202]
    Inject --> Loop
    Loop[for attempt in range MAX_RETRIES 行 205] --> Post[requests.post stream 行 207-213]
    Post --> CheckStatus{resp.status_code?}
    CheckStatus -->|200| Collect[collect_stream_silent 行 218]
    Collect --> PrintOK[print tokens, decode_time 行 219]
    PrintOK --> ReturnOK[return result]
    CheckStatus -->|502 and attempt < N-1| SleepBackoff[sleep 3 * attempt+1 行 215]
    SleepBackoff --> Loop
    CheckStatus -->|其他| Raise[raise_for_status 行 217]
    Raise --> Catch{catch Exception 行 221}
    Catch -->|attempt < N-1| PrintRetry[print retry 行 223]
    PrintRetry --> SleepRetry[sleep 3 * attempt+1 行 224]
    SleepRetry --> Loop
    Catch -->|attempt == N-1| PrintFail[print FAILED 行 226]
    PrintFail --> ReturnFail[return {tokens:0, decode_time:0, text:}]
    ReturnOK --> End
    ReturnFail --> End
```

**关键函数**：`infer_one`(188) · `collect_stream_silent`(151) · `get_ngram_processor_str`(40) · `requests.post` · `time.sleep`

## 链 6 — SSE 流式响应收集

```mermaid
flowchart TD
    Start([collect_stream_silent resp output_file]) --> OpenFile{output_file?}
    OpenFile -->|非空| F1[open w utf-8 行 155]
    OpenFile -->|None| F0[f = None]
    F1 --> Loop
    F0 --> Loop[for raw_line in resp.iter_lines 行 157]
    Loop --> SkipEmpty{raw_line 为空?}
    SkipEmpty -->|Yes| Loop
    SkipEmpty -->|No| Decode[bytes → str 解码 行 160]
    Decode --> HasData{以 data: 开头?}
    HasData -->|No| Loop
    HasData -->|Yes| StripData[data: 后的内容 strip 行 163]
    StripData --> Done{data == [DONE]?}
    Done -->|Yes| BreakOut[break]
    Done -->|No| TryJson[try json.loads 行 167]
    TryJson -->|JSONDecodeError or KeyError| Loop
    TryJson -->|OK| GetDelta[delta = choices[0].delta.content 行 168]
    GetDelta --> HasDelta{delta 非空?}
    HasDelta -->|No| Loop
    HasDelta -->|Yes| TimeFirst{first_token_time 为 None?}
    TimeFirst -->|Yes| MarkTime[first_token_time = time.time 行 174]
    TimeFirst -->|No| Count
    MarkTime --> Count[token_count += 1 行 175]
    Count --> Append[chunks.append delta 行 176]
    Append --> WriteFile{f?}
    WriteFile -->|Yes| WriteDelta[f.write delta 行 178]
    WriteFile -->|No| Loop
    WriteDelta --> Loop
    BreakOut --> Finally[finally: 关闭 f 行 180-181]
    Finally --> CalcTime[end_time = time.time 行 183]
    CalcTime --> DecodeTime[decode_time 计算 行 184]
    DecodeTime --> ReturnDict[return {tokens, decode_time, text}]
```

**关键函数**：`collect_stream_silent`(151) · `requests.get/post` · `resp.iter_lines` · `json.loads`

## 链 7 — PDF 转图片

```mermaid
sequenceDiagram
    participant Main as main → build_jobs
    participant PDF as pdf_to_images
    participant Fitz as PyMuPDF (fitz)
    participant Tmp as 系统 tmp 目录
    participant FS as FileSystem

    Main->>PDF: pdf_to_images(args.pdf, dpi=PDF_DPI) (行 242)
    PDF->>Fitz: import fitz (行 51)
    PDF->>Fitz: fitz.open(pdf_path) (行 53)
    Fitz-->>PDF: doc
    PDF->>Tmp: tempfile.mkdtemp(prefix='pdf_ocr_') (行 54)
    Tmp-->>PDF: tmp_dir
    PDF->>Fitz: fitz.Matrix(dpi/72, dpi/72) (行 56)
    loop 每页 page in doc
        PDF->>PDF: out_path = tmp_dir/page_NNNN.png (行 58)
        PDF->>Fitz: page.get_pixmap(matrix=mat).save(out_path) (行 59)
        PDF->>PDF: image_paths.append (行 60)
    end
    PDF->>Fitz: doc.close() (行 61)
    PDF-->>Main: image_paths (list)
    Note over Main: image_paths 在 tmpdir 下<br/>脚本不清理（依赖 OS tmp 回收）
```

**关键函数**：`pdf_to_images`(50) · `tempfile.mkdtemp` · `fitz.open` · `fitz.Matrix` · `page.get_pixmap`

## 整体调用图（简化）

```mermaid
flowchart LR
    main[main 319] --> parse_args[parse_args 303]
    main --> start_server[start_server 85]
    main --> run[run 267]
    main --> stop_server[stop_server 139]
    start_server --> server_ready[server_ready 77]
    run --> build_jobs[build_jobs 240]
    build_jobs --> pdf_to_images[pdf_to_images 50]
    build_jobs --> collect_dataset_images[collect_dataset_images 230]
    run --> infer_one_pool{{ThreadPoolExecutor<br/>N 个 infer_one}}
    infer_one_pool --> infer_one[infer_one 188]
    infer_one --> build_content[build_content 73]
    infer_one --> get_ngram_processor_str[get_ngram_processor_str 40]
    infer_one --> collect_stream_silent[collect_stream_silent 151]
    build_content --> encode_image[encode_image 65]
```