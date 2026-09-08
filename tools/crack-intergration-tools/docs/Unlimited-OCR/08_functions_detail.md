# 08 函数详细说明

所有函数位于 `infer.py`，按文件行号排列。每个函数标注：签名、位置、可见性、参数、副作用、调用栈关系。

---

## `get_ngram_processor_str()` (行 40)

- **签名**：`def get_ngram_processor_str() -> str`
- **位置**：`infer.py:40`
- **可见性**：module-level
- **参数**：无
- **返回值**：`DeepseekOCRNoRepeatNGramLogitProcessor.to_str()` 的字符串表示
- **抛出**：`ImportError` 当 sglang 未安装
- **副作用**：可能设置全局变量 `NO_REPEAT_NGRAM_PROCESSOR_STR`（行 41-46）
- **调用**：被 `infer_one()` 调用（行 198）
- **调用了**：`from sglang.srt.sampling.custom_logit_processor import DeepseekOCRNoRepeatNGramLogitProcessor`（行 43-45，行 46）
- **简要说明**：延迟导入 DeepSeek OCR 的 logit 处理器字符串

延迟模式（行 41-47）：首次调用时执行 import + 序列化，结果缓存到 module global。避免 SGLang 在脚本启动阶段被强制加载。

---

## `pdf_to_images(pdf_path, dpi=300)` (行 50)

- **签名**：`def pdf_to_images(pdf_path: str, dpi: int = 300) -> list[str]`
- **位置**：`infer.py:50`
- **可见性**：module-level
- **参数**：
  - `pdf_path: str` —— PDF 文件绝对或相对路径
  - `dpi: int = 300` —— 转图片的 DPI（影响 OCR 质量）
- **返回值**：PNG 图片绝对路径列表（按页顺序）
- **抛出**：`fitz.FileNotFoundError`、`fitz.EmptyFileError` 等 PyMuPDF 异常
- **副作用**：在系统 `tempfile` 目录下创建 `pdf_ocr_xxx/` 目录；调用 `fitz.open` + `doc.close`
- **调用**：被 `build_jobs()` 调用（行 242）
- **调用了**：`import fitz`（行 51）、`fitz.open(pdf_path)`（行 53）、`tempfile.mkdtemp(prefix="pdf_ocr_")`（行 54）、`fitz.Matrix(dpi / 72, dpi / 72)`（行 56）、`page.get_pixmap(matrix=mat).save(out_path)`（行 59）、`doc.close()`（行 61）
- **简要说明**：把 PDF 的每页转成 PNG 图片到 tmp 目录

**DPI 转换公式**：`fitz.Matrix(dpi / 72, dpi / 72)` —— PDF 默认 72 DPI，矩阵缩放到目标 DPI。

---

## `encode_image(image_path)` (行 65)

- **签名**：`def encode_image(image_path: str) -> dict`
- **位置**：`infer.py:65`
- **可见性**：module-level
- **参数**：`image_path: str` —— 图片绝对路径
- **返回值**：OpenAI multimodal content item
  ```python
  {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
  ```
- **抛出**：`FileNotFoundError`、`OSError`（读图失败）
- **副作用**：读文件 + base64 编码（CPU 密集）
- **调用**：被 `build_content()` 调用（行 74）
- **调用了**：`os.path.splitext(image_path)`（行 66）、`open(image_path, "rb")`（行 68）、`base64.b64encode(f.read())`（行 69）
- **简要说明**：把图片文件编码成 base64 data URL

**MIME 推断**（行 67）：
| 扩展名 | MIME |
|--------|------|
| `.jpg`, `.jpeg` | `image/jpeg` |
| 其他 | `image/{ext}`（去除前导 `.`） |

---

## `build_content(image_path)` (行 73)

- **签名**：`def build_content(image_path: str) -> list[dict]`
- **位置**：`infer.py:73`
- **可见性**：module-level
- **参数**：`image_path: str` —— 图片绝对路径
- **返回值**：OpenAI multimodal messages content（2 个 item：text + image_url）
- **抛出**：通过 `encode_image` 抛
- **副作用**：无（纯构造）
- **调用**：被 `infer_one()` 调用（行 191）
- **调用了**：`encode_image()`（行 74）
- **简要说明**：构造单个图片的 OpenAI 请求 content

---

## `server_ready(server_url)` (行 77)

- **签名**：`def server_ready(server_url: str) -> bool`
- **位置**：`infer.py:77`
- **可见性**：module-level
- **参数**：`server_url: str` —— 服务 URL（一般 `SERVER_URL` 常量）
- **返回值**：`True` 当 GET `/health` 返回 200
- **抛出**：无（异常时返回 False）
- **副作用**：HTTP GET 请求
- **调用**：被 `start_server()` 调用（行 86, 130）
- **调用了**：`requests.get(f"{server_url}/health", timeout=5)`（行 79）、`resp.status_code`（行 80）、`except requests.RequestException`（行 81）
- **简要说明**：检查 SGLang 服务是否就绪

**容错**：捕获所有 `RequestException` 返回 False，避免脚本因临时网络错误中断。

---

## `start_server(args)` (行 85)

- **签名**：`def start_server(args: argparse.Namespace) -> Optional[subprocess.Popen]`
- **位置**：`infer.py:85`
- **可见性**：module-level
- **参数**：`args: argparse.Namespace` —— CLI 解析后的参数
- **返回值**：`subprocess.Popen` 进程对象（新建）或 `None`（复用现有）
- **抛出**：`RuntimeError` 当服务启动后立即退出；`TimeoutError` 当超时
- **副作用**：创建日志目录 + 启动 SGLang 子进程 + 轮询健康检查
- **调用**：被 `main()` 调用（行 321）
- **调用了**：`server_ready(SERVER_URL)`（行 86, 130）、`os.makedirs/os.path.dirname/os.path.abspath`（行 90）、`os.environ.copy()`（行 91）、`subprocess.Popen(...)`（行 121）、`time.time()`（行 125, 131）、`time.sleep(3)`（行 133）、`process.poll()`（行 127）、`stop_server(process)`（行 135）
- **简要说明**：启动 SGLang 子进程或复用现有进程

**复用逻辑**（行 86-88）：如果 `server_ready(SERVER_URL)` 返回 True，直接返回 None，让现有服务继续服务（避免端口冲突）。

**轮询策略**（行 125-133）：每 3 秒检查一次；总超时 `SERVER_TIMEOUT`（300 秒）；进程退出立即抛错。

**进程句柄属性**（行 122）：`process._log_file` —— 保存日志文件句柄供 `stop_server` 关闭。

---

## `stop_server(process)` (行 139)

- **签名**：`def stop_server(process: Optional[subprocess.Popen]) -> None`
- **位置**：`infer.py:139`
- **可见性**：module-level
- **参数**：`process: Optional[subprocess.Popen]` —— `start_server` 返回的进程或 None
- **返回值**：None
- **抛出**：`subprocess.TimeoutExpired` 不会传播（行 145-147 处理）
- **副作用**：终止进程 + 关闭日志文件句柄
- **调用**：被 `main()` 调用（行 325），被 `start_server()` 调用（行 135）
- **调用了**：`process.terminate()`（行 142）、`process.wait(timeout=30)`（行 144）、`process.kill()`（行 146）、`process._log_file.close()`（行 148）
- **简要说明**：优雅终止 SGLang 子进程

**优雅关闭链**（行 142-147）：
1. `terminate()` 发送 SIGTERM
2. 等 30 秒
3. 超时则 `kill()` 发送 SIGKILL
4. 同步等待

---

## `collect_stream_silent(resp, output_file)` (行 151)

- **签名**：`def collect_stream_silent(resp, output_file: str | None) -> dict`
- **位置**：`infer.py:151`
- **可见性**：module-level
- **参数**：
  - `resp: requests.Response` —— 已打开的流式响应
  - `output_file: str | None` —— 输出文件路径或 None（不写）
- **返回值**：`{"tokens": int, "decode_time": float, "text": str}`
- **抛出**：无（`JSONDecodeError` / `KeyError` 被 catch，行 169-170）
- **副作用**：打开并写入 output_file
- **调用**：被 `infer_one()` 调用（行 218）
- **调用了**：`open(output_file, "w", encoding="utf-8")`（行 155）、`resp.iter_lines()`（行 157）、`raw_line.decode("utf-8")`（行 160）、`json.loads(data)`（行 167）、`time.time()`（行 174, 183）
- **简要说明**：解析 OpenAI SSE 流，累加 token，写文件

**SSE 解析规则**：
- 跳过空行（行 158）
- 解码 bytes → str（行 160）
- 必须以 `data:` 开头（行 161）
- 数据 `[DONE]` 终止（行 164）
- 解析失败容错（行 169-170）
- 仅在 `first_token_time` 未设置时记录（行 173）

**decode_time 定义**（行 184）：从首个 token 接收时间到最后一次循环时间，**仅当 `token_count > 1` 时**为非零。

---

## `infer_one(image_path, output_file, args, idx)` (行 188)

- **签名**：`def infer_one(image_path: str, output_file: str | None, args: argparse.Namespace, idx: int) -> dict`
- **位置**：`infer.py:188`
- **可见性**：module-level
- **参数**：
  - `image_path: str` —— 图片路径
  - `output_file: str | None` —— 输出 .md 路径（None 则只收集不写）
  - `args: argparse.Namespace` —— CLI 参数
  - `idx: int` —— 任务序号（用于日志）
- **返回值**：`{"tokens": int, "decode_time": float, "text": str}` 或失败时 `{"tokens": 0, "decode_time": 0, "text": ""}`
- **抛出**：无（所有异常 catch，行 221）
- **副作用**：HTTP POST + 写 output_file
- **调用**：被 `run()` 调用（行 279）
- **调用了**：`build_content(image_path)`（行 191）、`get_ngram_processor_str()`（行 198）、`os.path.basename(image_path)`（行 204）、`requests.post(...)`（行 207）、`time.sleep(3 * (attempt + 1))`（行 215, 224）、`resp.raise_for_status()`（行 217）、`collect_stream_silent(resp, output_file)`（行 218）、`resp.status_code`（行 214）
- **简要说明**：单图片 POST → 最多重试 5 次 → 返回结果

**重试策略**（行 205-227）：
- 502 + 非最终 attempt：`sleep(3 * (attempt + 1))` 退避
- 其他异常 + 非最终 attempt：同样退避
- 最终 attempt：返回失败 dict，不抛

**logit processor 注入**（行 197-202）：仅当 `NO_REPEAT_NGRAM_SIZE > 0 and NGRAM_WINDOW > 0` 时添加。Hard-coded 常量而非来自 args。

---

## `collect_dataset_images(image_dir)` (行 230)

- **签名**：`def collect_dataset_images(image_dir: str) -> list[str]`
- **位置**：`infer.py:230`
- **可见性**：module-level
- **参数**：`image_dir: str` —— 根目录
- **返回值**：图片绝对路径列表（**按文件大小倒排**）
- **抛出**：无（不存在的目录返回空列表）
- **副作用**：文件系统遍历
- **调用**：被 `build_jobs()` 调用（行 254）
- **调用了**：`os.walk(image_dir)`（行 233）、`name.lower().endswith(exts)`（行 235）、`os.path.join(root, name)`（行 236）、`sorted(..., key=os.path.getsize, reverse=True)`（行 237）
- **简要说明**：递归扫描目录，按文件大小降序排列图片

**支持扩展名**（行 231）：`.png, .jpg, .jpeg, .webp, .bmp`（小写匹配）

**排序策略**：文件大小倒排 —— 假设大文件是更重要的图片（先处理）。这是启发式，可能不是最优。

---

## `build_jobs(args)` (行 240)

- **签名**：`def build_jobs(args: argparse.Namespace) -> list[tuple[str, str | None]]`
- **位置**：`infer.py:240`
- **可见性**：module-level
- **参数**：`args: argparse.Namespace`
- **返回值**：`(image_path, output_file)` 列表，output_file 可为 None
- **抛出**：`ValueError` 当 `--image_dir` 和 `--pdf` 都为空（行 253）
- **副作用**：调用 `pdf_to_images` 时创建 tmp 目录
- **调用**：被 `run()` 调用（行 268）
- **调用了**：`pdf_to_images(args.pdf, dpi=PDF_DPI)`（行 242）、`os.path.splitext/os.path.basename`（行 243）、`os.path.join`（行 248）、`collect_dataset_images(args.image_dir)`（行 254）、`os.path.relpath`（行 260）
- **简要说明**：根据 CLI 参数构造任务列表

**两种模式**：
1. PDF 模式（`--pdf` 非空）：转图 + 输出名 `<pdf前缀>_page_NNNN.md`
2. 图片目录模式（`--image_dir` 非空）：扫描目录 + 输出名 `<relpath去分隔符>.md`

---

## `run(args)` (行 267)

- **签名**：`def run(args: argparse.Namespace) -> None`
- **位置**：`infer.py:267`
- **可见性**：module-level
- **参数**：`args: argparse.Namespace`
- **返回值**：None
- **抛出**：无（所有异常在 `infer_one` 内 catch）
- **副作用**：创建 output_dir；并发 HTTP 请求；打印统计
- **调用**：被 `main()` 调用（行 323）
- **调用了**：`build_jobs(args)`（行 268）、`os.makedirs(args.output_dir, exist_ok=True)`（行 270）、`time.time()`（行 275, 285）、`ThreadPoolExecutor(max_workers=args.concurrency)`（行 277）、`executor.submit(infer_one, ...)`（行 279）、`as_completed(futures)`（行 282）、`future.result()`（行 283）
- **简要说明**：ThreadPoolExecutor 并发调度 + 统计打印

**统计输出**（行 286-300）：
- `Requests: 成功数/总数`
- `Total tokens`
- `Wall time`（秒）
- `System TPS = total_tokens / wall_time`
- `Avg tokens/request`
- `Avg decode_time/request`

---

## `parse_args()` (行 303)

- **签名**：`def parse_args() -> argparse.Namespace`
- **位置**：`infer.py:303`
- **可见性**：module-level
- **参数**：无
- **返回值**：argparse 命名空间实例
- **抛出**：标准 argparse 错误（参数缺失、类型错误）
- **副作用**：从 `sys.argv` 解析
- **调用**：被 `main()` 调用（行 320）
- **调用了**：`argparse.ArgumentParser(...)`（行 304-307）、`parser.add_argument(...)`（行 308-315）、`parser.parse_args()`（行 316）
- **简要说明**：argparse CLI 解析

**所有参数**（行 308-315）：

| 参数 | 默认 | 类型 |
|------|------|------|
| `--image_dir` | `""` | str |
| `--pdf` | `""` | str |
| `--output_dir` | `"./outputs"` | str |
| `--concurrency` | `8` | int |
| `--gpu` | `"0"` | str |
| `--model_dir` | `"baidu/Unlimited-OCR"` | str |
| `--image_mode` | `"gundam"` | choices=(gundam, base) |
| `--server_log` | `"./log/sglang_server.log"` | str |

---

## `main()` (行 319)

- **签名**：`def main() -> None`
- **位置**：`infer.py:319`
- **可见性**：module-level（脚本入口）
- **参数**：无
- **返回值**：None
- **抛出**：`RuntimeError` / `TimeoutError` / `ValueError` 等（来自子函数）
- **副作用**：完整生命周期：启动 → run → finally 关闭
- **调用**：由 `if __name__ == "__main__"` 调用（行 328-329）
- **调用了**：`parse_args()`（行 320）、`start_server(args)`（行 321）、`run(args)`（行 323）、`stop_server(server_process)`（行 325）
- **简要说明**：顶层编排（4 行）

**try/finally 模式**（行 322-325）：保证 `stop_server` 在 `run` 异常时也会执行。

---

## 函数调用关系图

```mermaid
flowchart LR
    main[main 319]
    main --> A1[parse_args 303]
    main --> A2[start_server 85]
    main --> A3[run 267]
    main --> A4[stop_server 139]

    A2 --> B1[server_ready 77]
    A2 --> B2[subprocess.Popen]
    A2 --> B3[time.time/sleep]

    A3 --> C1[build_jobs 240]
    C1 --> C2[pdf_to_images 50]
    C1 --> C3[collect_dataset_images 230]
    A3 --> C4[ThreadPoolExecutor]
    A3 --> C5[as_completed]

    C4 --> D1[infer_one 188]
    D1 --> D2[build_content 73]
    D1 --> D3[get_ngram_processor_str 40]
    D1 --> D4[collect_stream_silent 151]
    D1 --> D5[requests.post]
    D1 --> B3

    D2 --> D6[encode_image 65]
    D4 --> D7[resp.iter_lines]
    D4 --> D8[json.loads]
    D4 --> B3

    C2 --> D9[fitz.open]
    C2 --> D10[page.get_pixmap]
    C3 --> D11[os.walk]
```