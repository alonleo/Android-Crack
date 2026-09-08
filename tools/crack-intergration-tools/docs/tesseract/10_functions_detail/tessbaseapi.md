# `TessBaseAPI` — Method Reference

> `class TESS_API TessBaseAPI` declared in `include/tesseract/baseapi.h:76`,
> implemented in `src/api/baseapi.cpp` (2 354 lines).
>
> Conventions used below:
> - `位置` gives header line and (impl) implementation line.
> - **调用** lists call sites grep-verified; if no caller found, "未找到明确调用方".
> - **调用了** lists callees grep-verified.
> - All file:line references are ripgrep-verified.

---

## `TessBaseAPI` constructor / destructor

### `TessBaseAPI()`
- **签名**: `TessBaseAPI()`
- **位置**: decl `include/tesseract/baseapi.h:78`
- **可见性**: public
- **抛出**: 无
- **副作用**: 构造内部 `Tesseract *` (`tesseract_`)、`ImageThresholder *` (`thresholder_`)、`EquationDetect *` 等成员
- **调用**: 用户代码；CLI `src/tesseract.cpp:714` (`TessBaseAPI api;`)
- **调用了**: `Tesseract` ctor、`ImageThresholder` ctor 等
- **简要说明**: 创建一个未初始化的 `TessBaseAPI`；使用前必须 `Init`

### `virtual ~TessBaseAPI()`
- **签名**: `virtual ~TessBaseAPI()`
- **位置**: decl `include/tesseract/baseapi.h:79`; impl in `src/api/baseapi.cpp`
- **可见性**: public virtual
- **抛出**: 无
- **副作用**: 释放 `tesseract_`、`thresholder_`、`page_res_` 等成员；隐式调用 `End()`
- **调用**: C++ RAII；C-API 中由 `TessBaseAPIDelete` 显式调用
- **调用了**: 多个内部 release
- **简要说明**: 释放所有内部资源

---

## Lifecycle / version

### `static const char *Version()`
- **签名**: `static const char *Version()`
- **位置**: decl `include/tesseract/baseapi.h:87`; impl `src/tesseract.cpp:101`
- **可见性**: public static
- **抛出**: 无
- **副作用**: 无
- **调用**: 任何客户端；CLI `src/tesseract.cpp:104` (banner)
- **调用了**: `TESSERACT_VERSION_STR` (from generated `version.h`)
- **简要说明**: 返回版本字符串 `"5.5.3"`

### `void Clear()`
- **签名**: `void Clear()`
- **位置**: decl `include/tesseract/baseapi.h:658`; impl `src/api/baseapi.cpp:1845`
- **可见性**: public
- **抛出**: 无
- **副作用**: 重置 `thresholder_`、清空 `PAGE_RES`、清空 `block_list_`
- **调用**: `End` 调用方；CLI 不会主动调用
- **调用了**: `thresholder_->Clear()`、`ClearResults()`
- **简要说明**: 清除识别结果但保留已加载的 `.traineddata`；可继续 `SetImage`

### `void End()`
- **签名**: `void End()`
- **位置**: decl `include/tesseract/baseapi.h:666`; impl `src/api/baseapi.cpp:1861`
- **可见性**: public
- **抛出**: 无
- **副作用**: 释放 `page_res_`、`thresholder_`、dict caches
- **调用**: 用户代码；C-API 文档推荐 (`capi.h:203`)
- **调用了**: `ClearResults()`、`delete page_res_`
- **简要说明**: 关闭 Tesseract，释放内部结构；调用后需重新 `Init`

### `static void ClearPersistentCache()`
- **签名**: `static void ClearPersistentCache()`
- **位置**: decl `include/tesseract/baseapi.h:675`
- **可见性**: public static
- **抛出**: 无
- **副作用**: 清空 LSTM 引擎的全局缓存
- **调用**: 用户代码
- **调用了**: 静态成员清理
- **简要说明**: 清空持久缓存；多线程场景下建议在 `Init` 前调用

---

## Initialization

### `int Init(datapath, language, OEM, configs[], configs_size, vars_vec, vars_values, set_only_non_debug)`
- **签名**: `int Init(const char *datapath, const char *language, OcrEngineMode mode, char **configs, int configs_size, const std::vector<std::string> *vars_vec, const std::vector<std::string> *vars_values, bool set_only_non_debug_params)`
- **位置**: decl `include/tesseract/baseapi.h:197`; impl `src/api/baseapi.cpp:300`
- **可见性**: public
- **抛出**: 可能返回非零（错误码）；不抛异常
- **副作用**: 读取 `.traineddata`、构建字典和 LSTM recognizer、初始化参数
- **调用**: CLI `src/tesseract.cpp:718` (`api.Init(datapath, "eng", OEM_LSTM_ONLY, configs, argc-arg_i, ...)`)
- **调用了**: `TessdataManager`、`tesseract_->init_tesseract`、`init_lstm_components` (`src/ccmain/tessedit.cpp:171`)
- **简要说明**: 完整 Init，加载指定 datapath 和语言的 `.traineddata`

### `int Init(datapath, language)` (inline)
- **签名**: `int Init(const char *datapath, const char *language)`
- **位置**: decl `include/tesseract/baseapi.h:205`
- **可见性**: public
- **抛出**: 无
- **副作用**: 同上，但使用 `OEM_DEFAULT`
- **调用**: 通用库调用方
- **调用了**: 7-arg overload
- **简要说明**: 2-arg 便捷版本，OEM 走默认

### `int Init(datapath, language, OEM)` (inline)
- **签名**: `int Init(const char *datapath, const char *language, OcrEngineMode oem)`
- **位置**: decl `include/tesseract/baseapi.h:202`
- **可见性**: public
- **抛出**: 无
- **调用**: 库调用方
- **调用了**: 7-arg overload
- **简要说明**: 3-arg 便捷版本

### `int Init(data, data_size, language, OEM, configs[], configs_size, ..., FileReader reader)`
- **签名**: `int Init(const char *data, int data_size, const char *language, OcrEngineMode mode, char **configs, int configs_size, ..., FileReader reader)`
- **位置**: decl `include/tesseract/baseapi.h:211`; impl `src/api/baseapi.cpp:310`
- **可见性**: public
- **抛出**: 无
- **副作用**: 内存中读 `.traineddata`（无需文件系统）
- **调用**: 嵌入式场景；JNI wrapper 推荐
- **调用了**: 7-arg overload via memory callback
- **简要说明**: 内存中的 Init；适合 APK 内嵌 `.traineddata`

### `void InitForAnalysePage()`
- **签名**: `void InitForAnalysePage()`
- **位置**: decl `include/tesseract/baseapi.h:243`; impl `src/api/baseapi.cpp:411`
- **可见性**: public
- **抛出**: 无
- **副作用**: 初始化 adaptive classifier
- **调用**: `TessBaseAPI::AnalyseLayout` 之前调用
- **调用了**: `tesseract_->InitAdaptiveClassifier(nullptr)`
- **简要说明**: 为 layout-only 分析初始化（无需完整 recognizer）

### `void ReadConfigFile(filename)` / `ReadDebugConfigFile(filename)`
- **签名**: `void ReadConfigFile(const char *filename)` / `void ReadDebugConfigFile(const char *filename)`
- **位置**: decl `include/tesseract/baseapi.h:251, 253`
- **可见性**: public
- **抛出**: 无（失败时内部 warn）
- **调用**: CLI 末尾追加 configfile 时；库调用方
- **简要说明**: 读取 `.config` 文件中的 `VAR VALUE` 行；debug 版还会覆盖 `tessedit_*_debug` 参数

### `const char *GetInitLanguagesAsString() const`
- **签名**: `const char *GetInitLanguagesAsString() const`
- **位置**: decl `include/tesseract/baseapi.h:225`; impl `src/api/baseapi.cpp:376`
- **可见性**: public
- **返回值**: `"eng+chi_sim"` 形式（静态字符串，do not free）
- **调用**: 用户代码、CLI banner
- **简要说明**: 返回初始化时使用的语言列表

### `void GetLoadedLanguagesAsVector(vector<string> *) const`
- **位置**: decl `include/tesseract/baseapi.h:232`
- **调用**: 库调用方
- **简要说明**: 把已加载的语言填充到 vector

### `void GetAvailableLanguagesAsVector(vector<string> *) const`
- **位置**: decl `include/tesseract/baseapi.h:237`
- **调用**: 库调用方
- **简要说明**: 列出 `--tessdata-dir` 中所有可用的语言（需有 `.traineddata`）

### `void SetPageSegMode(PageSegMode mode)`
- **签名**: `void SetPageSegMode(PageSegMode mode)`
- **位置**: decl `include/tesseract/baseapi.h:260`
- **可见性**: public
- **副作用**: 设置 `pageseg_mode_`
- **调用**: 库调用方；CLI `src/tesseract.cpp:752` (`FixPageSegMode`)
- **简要说明**: 设置 PSM；下次 `Recognize` 生效

### `PageSegMode GetPageSegMode() const`
- **位置**: decl `include/tesseract/baseapi.h:263`
- **调用**: 用户代码
- **简要说明**: 返回当前 PSM

---

## Image input

### `void SetImage(imagedata, width, height, bytes_per_pixel, bytes_per_line)`
- **签名**: `void SetImage(const unsigned char *imagedata, int width, int height, int bytes_per_pixel, int bytes_per_line)`
- **位置**: decl `include/tesseract/baseapi.h:307`; impl `src/api/baseapi.cpp:506`
- **可见性**: public
- **副作用**: 拷贝 `imagedata` 到内部 Pix；清空旧 PAGE_RES
- **调用**: 库调用方；`TesseractRect` 内部调用 (`src/api/baseapi.cpp:476`)
- **调用了**: `InternalSetImage`、`thresholder_->SetImage(...)`
- **简要说明**: 原始缓冲区输入；需要 `TesseractRect` 后接 `GetUTF8Text`

### `void SetImage(Pix *pix)`
- **签名**: `void SetImage(Pix *pix)`
- **位置**: decl `include/tesseract/baseapi.h:318`; impl `src/api/baseapi.cpp:529`
- **可见性**: public
- **副作用**: 接管 Pix 所有权（不会复制）；清空旧 PAGE_RES
- **调用**: 库调用方；`ProcessPage` 内部 (`src/api/baseapi.cpp:1200`)
- **调用了**: `InternalSetImage`、`thresholder_->SetImage(pix)`
- **简要说明**: Leptonica Pix 输入；推荐路径（无需 memcpy）

### `void SetInputName(const char *name)`
- **位置**: decl `include/tesseract/baseapi.h:93`
- **调用**: 库调用方
- **简要说明**: 设置输入文件名（PDF 嵌入和 UNLV zone 读取需要）

### `const char *GetInputName()`
- **位置**: decl `include/tesseract/baseapi.h:101`
- **调用**: 库调用方
- **简要说明**: 返回上次的输入文件名

### `void SetInputImage(Pix *pix)` / `Pix *GetInputImage()`
- **位置**: decl `include/tesseract/baseapi.h:103, 104`
- **调用**: 库调用方
- **简要说明**: 输入图像的 getter / setter（不影响识别状态）

### `int GetSourceYResolution()`
- **位置**: decl `include/tesseract/baseapi.h:105`
- **简要说明**: 返回图像源 Y 分辨率（DPI）

### `const char *GetDatapath()`
- **位置**: decl `include/tesseract/baseapi.h:106`
- **简要说明**: 返回当前 tessdata 路径

### `void SetOutputName(const char *name)`
- **位置**: decl `include/tesseract/baseapi.h:109`
- **调用**: 库调用方
- **简要说明**: 设置输出基础名（hOCR 等带 source 链接时需要）

### `void SetSourceResolution(int ppi)`
- **签名**: `void SetSourceResolution(int ppi)`
- **位置**: decl `include/tesseract/baseapi.h:324`
- **可见性**: public
- **调用**: CLI `--dpi`；库调用方
- **简要说明**: 显式告诉 Tesseract 图像源 DPI

### `void SetRectangle(int left, int top, int width, int height)`
- **签名**: `void SetRectangle(int left, int top, int width, int height)`
- **位置**: decl `include/tesseract/baseapi.h:331`
- **可见性**: public
- **副作用**: 设置后续 Recognize 的 ROI
- **调用**: `TesseractRect` 内部
- **简要说明**: 在已 SetImage 的图中限定识别范围

### `char *TesseractRect(imagedata, bytes_per_pixel, bytes_per_line, left, top, width, height)`
- **签名**: `char *TesseractRect(const unsigned char *imagedata, int bytes_per_pixel, int bytes_per_line, int left, int top, int width, int height)`
- **位置**: decl `include/tesseract/baseapi.h:282`; impl `src/api/baseapi.cpp:467-481`
- **可见性**: public
- **抛出**: 无；返回 NULL 表示失败
- **副作用**: SetImage + SetRectangle + Recognize + GetUTF8Text
- **调用**: 库调用方；JNI wrapper 推荐路径
- **调用了**: `SetImage`、`Recognize`、`GetUTF8Text`
- **简要说明**: ROI 识别一行；返回的 `char *` 必须 `delete[]`

### `void ClearAdaptiveClassifier()`
- **位置**: decl `include/tesseract/baseapi.h:290`; impl `src/api/baseapi.cpp:488`
- **调用**: 用户代码
- **简要说明**: 清空自适应分类器状态

---

## Layout analysis (pre-Recognize)

### `int GetThresholdedImageScaleFactor() const`
- **位置**: decl `include/tesseract/baseapi.h:427`
- **简要说明**: 返回 thresholder 缩放因子

### `Pix *GetThresholdedImage()`
- **位置**: decl `include/tesseract/baseapi.h:338`
- **简要说明**: 返回二值化后的图像（用于 debug）

### `float GetGradient()`
- **位置**: decl `include/tesseract/baseapi.h:343`
- **简要说明**: 返回全局文本方向梯度（弧度）

### `Boxa *GetRegions(Pixa **pixa)`
- **位置**: decl `include/tesseract/baseapi.h:350`
- **简要说明**: 找出所有 text regions

### `Boxa *GetTextlines(...)`, `GetStrips(...)`, `GetWords(...)`, `GetConnectedComponents(...)`, `GetComponentImages(...)`
- **位置**: decl `include/tesseract/baseapi.h:363, 380, 387, 397, 411`
- **简要说明**: layout 分析 helper；返回 Leptonica Boxa 列表

### `PageIterator *AnalyseLayout(bool merge_similar_words)`
- **位置**: decl `include/tesseract/baseapi.h:444, 445`
- **调用**: 库调用方
- **简要说明**: 仅做 layout 分析（不 OCR），返回 `PageIterator` 供遍历

---

## Recognition

### `int Recognize(ETEXT_DESC *monitor)`
- **签名**: `int Recognize(ETEXT_DESC *monitor)`
- **位置**: decl `include/tesseract/baseapi.h:453`; impl `src/api/baseapi.cpp:762`
- **可见性**: public
- **抛出**: 无；返回 `< 0` 表示错误
- **副作用**: 构造 `PAGE_RES`；可能耗时数十秒
- **调用**: `ProcessPage` 内部 (`src/api/baseapi.cpp:1218`)、CLI/库调用方
- **调用了**: `FindLines()` (`:2070`)、`tesseract_->recog_all_words(...)`、`LSTMRecognizeWord` (`src/ccmain/linerec.cpp:229`) 或 `recog_word` (`src/ccmain/tfacepp.cpp:37`)
- **简要说明**: 主识别入口；调用后用 `GetUTF8Text` / `GetIterator` 取结果

---

## Multi-page processing

### `bool ProcessPages(filename, retry_config, timeout_millisec, renderer)`
- **签名**: `bool ProcessPages(const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer)`
- **位置**: decl `include/tesseract/baseapi.h:482`; impl `src/api/baseapi.cpp:999`
- **可见性**: public
- **抛出**: 无；返回 false 表示失败
- **副作用**: 调用 `ProcessPagesInternal`；写入 renderer
- **调用**: CLI `src/tesseract.cpp:845`
- **调用了**: `ProcessPagesInternal` (`:1033`)
- **简要说明**: 单文件名 → 自动检测格式 → 多页处理

### `bool ProcessPagesInternal(filename, retry_config, timeout_millisec, renderer)`
- **位置**: decl `include/tesseract/baseapi.h:485`; impl `src/api/baseapi.cpp:1033`
- **调用**: `ProcessPages` 调用
- **调用了**: `findFileFormat` (`:1142`)
- **简要说明**: 实现层

### `bool ProcessPage(Pix *pix, int page_index, filename, retry_config, timeout_millisec, renderer)`
- **位置**: decl `include/tesseract/baseapi.h:497`; impl `src/api/baseapi.cpp:1196`
- **调用**: `ProcessPages` 内部
- **调用了**: `SetImage` (`:1200`)、`Recognize` (`:1218`)、`renderer->AddImage`
- **简要说明**: 处理单页

---

## Iterators

### `ResultIterator *GetIterator()`
- **签名**: `ResultIterator *GetIterator()`
- **位置**: decl `include/tesseract/baseapi.h:509`; impl `src/api/baseapi.cpp:1280`
- **可见性**: public
- **返回值**: 新构造的 `ResultIterator`（caller owns; `delete it`）
- **抛出**: 无
- **副作用**: 构造内部 iterator 指针
- **调用**: 库调用方；`GetUTF8Text` 内部 (`src/api/baseapi.cpp:1312`)
- **调用了**: `new ResultIterator(...)`
- **简要说明**: 获取结果 iterator

### `MutableIterator *GetMutableIterator()`
- **签名**: `MutableIterator *GetMutableIterator()`
- **位置**: decl `include/tesseract/baseapi.h:519`; impl `src/api/baseapi.cpp:1297`
- **可见性**: public
- **调用**: `GetTSVText` 内部 (`src/api/baseapi.cpp:2299`)
- **简要说明**: 获取可变 iterator（暴露 PAGE_RES_IT 内部）

---

## Output formats

### `char *GetUTF8Text()`
- **签名**: `char *GetUTF8Text()`
- **位置**: decl `include/tesseract/baseapi.h:525`; impl `src/api/baseapi.cpp:1307`
- **可见性**: public
- **抛出**: 无
- **副作用**: 构造 `ResultIterator` 后丢弃
- **调用**: `TesseractRect` 内部 (`src/api/baseapi.cpp:480`)
- **调用了**: `GetIterator()` (`:1312`)
- **简要说明**: 最简单的输出格式；纯文本，caller `delete[]`

### `char *GetHOCRText(ETEXT_DESC *monitor, int page_number)` / `GetHOCRText(int)`
- **位置**: decl `include/tesseract/baseapi.h:536, 544`
- **简要说明**: 输出 hOCR XML

### `char *GetAltoText(ETEXT_DESC *monitor, int page_number)` / `GetAltoText(int)`
- **位置**: decl `include/tesseract/baseapi.h:550, 556`
- **简要说明**: 输出 ALTO XML

### `char *GetPAGEText(ETEXT_DESC *monitor, int page_number)` / `GetPAGEText(int)`
- **位置**: decl `include/tesseract/baseapi.h:562, 568`
- **简要说明**: 输出 PAGE XML

### `char *GetTSVText(int page_number)`
- **位置**: decl `include/tesseract/baseapi.h:575`; impl `src/api/baseapi.cpp:1353`
- **调用**: CLI `-c tessedit_create_tsv=1`
- **调用了**: `GetMutableIterator` (`:2299`)
- **简要说明**: 输出 TSV（含 bbox）

### `char *GetLSTMBoxText(int)` / `GetBoxText(int)` / `GetWordStrBoxText(int)`
- **位置**: decl `include/tesseract/baseapi.h:583, 592, 600`; `GetBoxText` impl `:1497`
- **简要说明**: 输出 box 文件格式（LSTM-training / Tesseract 训练 / 单词级）

### `char *GetUNLVText()`
- **位置**: decl `include/tesseract/baseapi.h:607`
- **简要说明**: 输出 UNLV zone 格式

---

## OSD / confidence

### `bool DetectOrientationScript(int *orient_deg, float *orient_conf, const char **script_name, float *script_conf)`
- **位置**: decl `include/tesseract/baseapi.h:618`; impl `src/api/baseapi.cpp:1653`
- **调用**: `GetOsdText` 内部 (`:1695`)
- **调用了**: `DetectOS`
- **简要说明**: 同时检测旋转角度和脚本（Latin / Han / …）

### `char *GetOsdText(int page_number)`
- **位置**: decl `include/tesseract/baseapi.h:626`; impl `src/api/baseapi.cpp:1689`
- **调用**: `PSM_OSD_ONLY` 模式
- **简要说明**: 输出 OSD 文本

### `int MeanTextConf()`
- **签名**: `int MeanTextConf()`
- **位置**: decl `include/tesseract/baseapi.h:629`; impl `src/api/baseapi.cpp:1719`
- **调用**: `AllWordConfidences`
- **简要说明**: 返回所有词的平均置信度（0-100）

### `int *AllWordConfidences()`
- **位置**: decl `include/tesseract/baseapi.h:636`; impl `src/api/baseapi.cpp:1737`
- **返回值**: 每词一个置信度，-1 终止
- **简要说明**: 返回每词置信度（caller `TessDeleteIntArray`）

### `bool DetectOS(OSResults *)`
- **位置**: decl `include/tesseract/baseapi.h:701`
- **调用**: `DetectOrientationScript` 内部
- **简要说明**: 低层 OSD

### `void GetBlockTextOrientations(int **block_orientation, bool **vertical_writing)`
- **位置**: decl `include/tesseract/baseapi.h:707`
- **简要说明**: 返回每块的方向

### `bool GetTextDirection(int *out_offset, float *out_slope)`
- **位置**: decl `include/tesseract/baseapi.h:687`
- **简要说明**: 全局文本方向

### `void set_min_orientation_margin(double margin)`
- **位置**: decl `include/tesseract/baseapi.h:727`
- **简要说明**: 设置 OSD 的最小 margin

---

## Variable access (Params)

### `bool SetVariable(name, value)` / `SetDebugVariable(name, value)`
- **位置**: decl `include/tesseract/baseapi.h:124, 125`
- **调用**: CLI `-c VAR=VALUE`；库调用方
- **简要说明**: 设置运行时参数；debug 版允许覆盖 `tessedit_*_debug`

### `bool GetIntVariable/BoolVariable/DoubleVariable(StringVariable)(name, *value) const`
- **位置**: decl `include/tesseract/baseapi.h:131-139`
- **简要说明**: 读取参数

### `void PrintVariables(FILE *)` / `PrintFontsTable(FILE *)`
- **位置**: decl `include/tesseract/baseapi.h:146, 153`
- **调用**: CLI `--print-parameters`
- **简要说明**: 调试输出

### `bool GetVariableAsString(name, string *)`
- **位置**: decl `include/tesseract/baseapi.h:158`
- **简要说明**: 同上，字符串形式

---

## Adaptive / dictionary hooks

### `bool AdaptToWordStr(PageSegMode mode, const char *wordstr)` (legacy)
- **位置**: decl `include/tesseract/baseapi.h:649`; impl `src/api/baseapi.cpp:1777`
- **调用**: 用户代码；legacy only
- **简要说明**: 用单个 wordstr 自适应训练（gated by `DISABLED_LEGACY_ENGINE`）

### `int IsValidWord(const char *) const`
- **位置**: decl `include/tesseract/baseapi.h:683`
- **简要说明**: 检查 word 是否在字典中

### `bool IsValidCharacter(const char *utf8_character) const`
- **位置**: decl `include/tesseract/baseapi.h:685`
- **简要说明**: 检查 utf8 字符是否在 unicharset 中

### `void SetDictFunc(DictFunc f)`
- **位置**: decl `include/tesseract/baseapi.h:690`
- **简要说明**: 设置自定义字典函数回调

### `void SetProbabilityInContextFunc(ProbabilityInContextFunc f)`
- **位置**: decl `include/tesseract/baseapi.h:695`
- **简要说明**: 设置 LM 概率上下文回调

---

## Accessors

### `const char *GetUnichar(int unichar_id) const`
- **位置**: decl `include/tesseract/baseapi.h:711`
- **简要说明**: unichar_id → UTF-8 字符串

### `const Dawg *GetDawg(int i) const`
- **位置**: decl `include/tesseract/baseapi.h:714`
- **简要说明**: 取第 i 个 DAWG

### `int NumDawgs() const`
- **位置**: decl `include/tesseract/baseapi.h:717`
- **简要说明**: 已加载 DAWG 数

### `Tesseract *tesseract() const`
- **位置**: decl `include/tesseract/baseapi.h:719`
- **简要说明**: 返回内部 `Tesseract *`（供 advanced 调用方使用）

### `OcrEngineMode oem() const`
- **位置**: decl `include/tesseract/baseapi.h:723`
- **简要说明**: 返回当前 OEM

---

## Free helper

### `std::string HOcrEscape(const char *text)`
- **位置**: decl `include/tesseract/baseapi.h:816`
- **简要说明**: hOCR 文本转义（< → &lt; 等）