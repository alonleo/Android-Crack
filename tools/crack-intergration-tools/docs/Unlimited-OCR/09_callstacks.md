# 09 关键调用栈

## 栈 1 — 启动到参数解析

```
用户执行
└── main()  (行 319)
    └── parse_args()  (行 320 → 303)
        ├── argparse.ArgumentParser  (行 304-307)
        └── parser.add_argument × 8  (行 308-315)
            └── parser.parse_args()  (行 316)
                └── sys.argv 解析
```

## 栈 2 — SGLang 服务生命周期

```
main()  (行 321)
└── start_server(args)  (行 85)
    ├── server_ready(SERVER_URL)  (行 86 → 77)
    │   ├── requests.get(/health, timeout=5)
    │   └── resp.status_code == 200?
    │
    ├── [若就绪] print "Reuse existing" → return None  (行 87-88)
    │
    ├── [若需启动]
    │   ├── os.makedirs(server_log 父目录)  (行 90)
    │   ├── env = os.environ.copy()  (行 91)
    │   ├── env["CUDA_VISIBLE_DEVICES"] = args.gpu  (行 92)
    │   ├── cmd = [sys.executable, "-m", "sglang.launch_server", ...]  (行 94-117)
    │   ├── log_file = open(args.server_log, "w")  (行 120)
    │   ├── process = subprocess.Popen(cmd, env=env, stdout=log_file, stderr=STDOUT)  (行 121)
    │   ├── process._log_file = log_file  (行 122)
    │   │
    │   └── 轮询循环  (行 125-133)
    │       ├── process.poll() → raise RuntimeError 若已退出  (行 127-129)
    │       ├── server_ready(URL)  (行 130 → 77)
    │       │   ├── requests.get(/health)
    │       │   └── return 200
    │       ├── print "Server ready"  (行 131)
    │       ├── time.sleep(3)  (行 133)
    │       └── [超时] stop_server(process) + raise TimeoutError  (行 135-136)

[run 完成后]
main()  (行 325, finally)
└── stop_server(process)  (行 139)
    ├── [None] return  (行 140-141)
    ├── process.terminate()  (行 142)
    ├── process.wait(timeout=30)  (行 144)
    ├── [TimeoutExpired] process.kill() + wait  (行 145-147)
    └── process._log_file.close()  (行 148)
```

## 栈 3 — 任务列表构建

```
run(args)  (行 268)
└── build_jobs(args)  (行 240)
    ├── [if args.pdf]
    │   ├── image_files = pdf_to_images(args.pdf, dpi=PDF_DPI)  (行 242 → 50)
    │   │   ├── import fitz
    │   │   ├── doc = fitz.open(pdf_path)
    │   │   ├── tmp_dir = tempfile.mkdtemp(prefix="pdf_ocr_")
    │   │   ├── mat = fitz.Matrix(dpi/72, dpi/72)
    │   │   ├── [for each page] page.get_pixmap(matrix=mat).save(out_path)
    │   │   ├── doc.close()
    │   │   └── return image_paths
    │   ├── prefix = os.path.splitext(os.path.basename(args.pdf))[0]
    │   ├── [for each image_path]
    │   │   ├── output_file = "{prefix}_page_{i+1:04d}.md"  (行 248)
    │   │   └── jobs.append((image_path, output_file))
    │   └── return jobs
    │
    └── [elif args.image_dir]
        ├── image_files = collect_dataset_images(args.image_dir)  (行 254 → 230)
        │   └── os.walk + 大小倒排
        ├── [for each image_path]
        │   ├── rel = os.path.relpath(image_path, args.image_dir)
        │   ├── stem = os.path.splitext(rel)[0].replace(os.sep, "__")
        │   ├── output_file = "{stem}.md"
        │   └── jobs.append((image_path, output_file))
        └── return jobs
    │
    └── [both empty] raise ValueError  (行 252-253)
```

## 栈 4 — 并发调度（核心）

```
run(args)  (行 267)
├── jobs = build_jobs(args)  (行 268)
├── os.makedirs(args.output_dir, exist_ok=True)  (行 270)
├── print mode/requests/concurrency/image_mode  (行 273)
├── wall_start = time.time()  (行 275)
├── with ThreadPoolExecutor(max_workers=args.concurrency) as executor  (行 277)
│   ├── futures = {
│   │     executor.submit(infer_one, image_path, output_file, args, i+1): image_path
│   │     for i, (image_path, output_file) in enumerate(jobs)
│   │ }  (行 278-281)
│   │
│   └── [for future in as_completed(futures)]  (行 282)
│       └── results.append(future.result())  (行 283)
│
├── wall_time = time.time() - wall_start  (行 285)
├── total_tokens = sum(r["tokens"] for r in results)  (行 286)
├── successful = sum(1 for r in results if r["tokens"] > 0)  (行 287)
└── 打印统计  (行 288-300)
```

## 栈 5 — 单图片推理（详细）

```
infer_one(image_path, output_file, args, idx)  (行 188)
├── payload = {
│     "model": SERVED_MODEL_NAME,
│     "messages": [{"role": "user", "content": build_content(image_path)}],  (行 191 → 73)
│     "temperature": TEMPERATURE,
│     "skip_special_tokens": False,
│     "stream": True,
│     "images_config": {"image_mode": args.image_mode},
│   }  (行 189-196)
│
├── [if NO_REPEAT_NGRAM_SIZE > 0 and NGRAM_WINDOW > 0]
│   ├── payload["custom_logit_processor"] = get_ngram_processor_str()  (行 198 → 40)
│   │   ├── from sglang.srt.sampling.custom_logit_processor import DeepseekOCRNoRepeatNGramLogitProcessor
│   │   ├── DeepseekOCRNoRepeatNGramLogitProcessor.to_str()
│   │   └── 缓存到全局 NO_REPEAT_NGRAM_PROCESSOR_STR
│   └── payload["custom_params"] = {"ngram_size": 35, "window_size": 128}  (行 199-202)
│
├── name = os.path.basename(image_path)  (行 204)
│
└── [for attempt in range(MAX_RETRIES)]  (行 205-227)
    ├── resp = requests.post(  (行 207-213)
    │     f"{SERVER_URL}/v1/chat/completions",
    │     headers={"Content-Type": "application/json"},
    │     data=json.dumps(payload),
    │     timeout=REQUEST_TIMEOUT,
    │     stream=True,
    │ )
    │
    ├── [if status_code == 502 and attempt < MAX_RETRIES-1]
    │   └── time.sleep(3 * (attempt + 1))  (行 215)
    │       └── continue
    │
    ├── resp.raise_for_status()  (行 217)
    │
    ├── result = collect_stream_silent(resp, output_file)  (行 218 → 151)
    │   ├── [if output_file] f = open(output_file, "w", encoding="utf-8")
    │   ├── [for raw_line in resp.iter_lines]
    │   │   ├── 解码 bytes → str
    │   │   ├── 跳过非 data: 开头
    │   │   ├── [DONE] 终止
    │   │   ├── json.loads 解析 chunk
    │   │   ├── delta = chunk["choices"][0]["delta"]["content"]
    │   │   ├── token_count += 1
    │   │   └── f.write(delta)  [若 f]
    │   ├── [finally] f.close()
    │   ├── decode_time = end_time - first_token_time  [若 first_token_time and token_count > 1]
    │   └── return {"tokens": N, "decode_time": t, "text": "".join(chunks)}
    │
    ├── print(f"[{idx}] {name}: {tokens} tokens, {decode_time:.1f}s")  (行 219)
    └── return result
│
├── [except Exception as e]  (行 221)
│   ├── [if attempt < MAX_RETRIES-1]
│   │   ├── print(f"[{idx}] {name}: retry {attempt + 1}/{MAX_RETRIES} ({e})")  (行 223)
│   │   ├── time.sleep(3 * (attempt + 1))  (行 224)
│   │   └── continue
│   │
│   └── print(f"[{idx}] {name}: FAILED ({e})")  (行 226)
│       └── return {"tokens": 0, "decode_time": 0, "text": ""}
```

## 栈 6 — PDF 转图片

```
build_jobs(args)  (行 242)
└── pdf_to_images(args.pdf, dpi=PDF_DPI)  (行 50)
    ├── import fitz  (行 51)
    ├── doc = fitz.open(pdf_path)  (行 53)
    ├── tmp_dir = tempfile.mkdtemp(prefix="pdf_ocr_")  (行 54)
    ├── image_paths = []  (行 55)
    ├── mat = fitz.Matrix(dpi / 72, dpi / 72)  (行 56)
    │
    ├── [for i, page in enumerate(doc)]  (行 57)
    │   ├── out_path = os.path.join(tmp_dir, f"page_{i + 1:04d}.png")  (行 58)
    │   ├── page.get_pixmap(matrix=mat).save(out_path)  (行 59)
    │   └── image_paths.append(out_path)
    │
    ├── doc.close()  (行 61)
    └── return image_paths
```

注：tmp_dir **未被脚本清理**（无 `shutil.rmtree` 调用）。依赖 OS tmp 回收。

## 栈 7 — 收尾关闭服务

```
main()  (行 322-325, try/finally)
├── try
│   └── run(args)  (行 323)
│       ├── ... 完整推理流程 ...
│
└── finally
    └── stop_server(server_process)  (行 325 → 139)
        ├── [None] return  (行 140-141)
        ├── process.terminate()  (行 142)
        ├── process.wait(timeout=30)  (行 144)
        ├── [TimeoutExpired] process.kill() + process.wait()  (行 145-147)
        └── process._log_file.close()  (行 148)
```