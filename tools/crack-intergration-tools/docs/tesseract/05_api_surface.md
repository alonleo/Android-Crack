# 05 — API Surface

This document enumerates the public API: every method on `TessBaseAPI`, the
companion C API (`include/tesseract/capi.h`), and the supporting enumerations
in `include/tesseract/publictypes.h`. All file:line references are
grep-verified.

---

## 5.1 `OcrEngineMode` (OEM) — `include/tesseract/publictypes.h:263-277`

```cpp
enum OcrEngineMode {
  OEM_TESSERACT_ONLY,            // = 0  legacy only; deprecated since 5.x
  OEM_LSTM_ONLY,                 // = 1  default in 5.x for `tesseract --oem 1`
  OEM_TESSERACT_LSTM_COMBINED,   // = 2  LSTM with legacy fallback; deprecated
  OEM_DEFAULT,                   // = 3  select from language/config defaults
  OEM_COUNT
};
```

Dispatch: `tesseract_->AnyLSTMLang()` → LSTM recognizer constructed in
`Tesseract::init_lstm_components` (`src/ccmain/tessedit.cpp:171-172`).
CLI default is `OEM_LSTM_ONLY` when `DISABLED_LEGACY_ENGINE` is set
(`src/tesseract.cpp:670-674`).

---

## 5.2 `PageSegMode` (PSM) — `include/tesseract/publictypes.h:157-178`

```cpp
enum PageSegMode {
  PSM_OSD_ONLY               = 0,   // OSD only
  PSM_AUTO_OSD               = 1,   // auto + orientation/script detect
  PSM_AUTO_ONLY              = 2,   // segmentation, no OSD/OCR
  PSM_AUTO                   = 3,   // default for CLI (no OSD)
  PSM_SINGLE_COLUMN          = 4,
  PSM_SINGLE_BLOCK_VERT_TEXT = 5,
  PSM_SINGLE_BLOCK           = 6,   // default for the library
  PSM_SINGLE_LINE            = 7,
  PSM_SINGLE_WORD            = 8,
  PSM_CIRCLE_WORD            = 9,
  PSM_SINGLE_CHAR            = 10,
  PSM_SPARSE_TEXT            = 11,
  PSM_SPARSE_TEXT_OSD        = 12,
  PSM_RAW_LINE               = 13,
  PSM_COUNT
};
```

Six inline predicate helpers (`publictypes.h:186-207`):
- `PSM_OSD_ENABLED(m)`
- `PSM_ORIENTATION_ENABLED(m)`
- `PSM_COL_FIND_ENABLED(m)`
- `PSM_SPARSE(m)`
- `PSM_BLOCK_FIND_ENABLED(m)`
- `PSM_LINE_FIND_ENABLED(m)`
- `PSM_WORD_FIND_ENABLED(m)`

Used throughout `src/ccmain/pagesegmain.cpp` to gate which analysis stages run.

---

## 5.3 `PageIteratorLevel` (RIL) — `include/tesseract/publictypes.h:214`

```cpp
enum PageIteratorLevel {
  RIL_BLOCK,    // block
  RIL_PARA,     // paragraph
  RIL_TEXTLINE, // textline
  RIL_WORD,     // word
  RIL_SYMBOL    // symbol
};
```

---

## 5.4 Other enums (`include/tesseract/publictypes.h`)

| Enum | Purpose |
|---|---|
| `enum PolyBlockType` (`:51`) | `PT_UNKNOWN`, `PT_FLOWING_TEXT`, `PT_HEADING_TEXT`, `PT_PULLOUT_TEXT`, `PT_EQUATION`, `PT_INLINE_EQUATION`, `PT_TABLE`, `PT_VERTICAL_TEXT`, `PT_CAPTION_TEXT`, `PT_FLOWING_IMAGE`, `PT_HEADING_IMAGE`, `PT_PULLOUT_IMAGE`, `PT_HORZ_LINE`, `PT_VERT_LINE`, `PT_NOISE`, `PT_COUNT` |
| `enum Orientation` | `ORIENTATION_PAGE_UP`, `ORIENTATION_PAGE_RIGHT`, `ORIENTATION_PAGE_DOWN`, `ORIENTATION_PAGE_LEFT` |
| `enum WritingDirection` | `WRITING_DIRECTION_LEFT_TO_RIGHT`, `WRITING_DIRECTION_RIGHT_TO_LEFT`, `WRITING_DIRECTION_TOP_TO_BOTTOM` |
| `enum TextlineOrder` | `TEXTLINE_ORDER_LEFT_TO_RIGHT`, `TEXTLINE_ORDER_RIGHT_TO_LEFT`, `TEXTLINE_ORDER_TOP_TO_BOTTOM` |
| `enum ParagraphJustification` | `JUSTIFICATION_UNKNOWN`, `JUSTIFICATION_LEFT`, `JUSTIFICATION_CENTER`, `JUSTIFICATION_RIGHT` |

---

## 5.5 `TessBaseAPI` method table

`class TESS_API TessBaseAPI` (`include/tesseract/baseapi.h:76`); impl
`src/api/baseapi.cpp` (2 354 lines). Lines below are header declaration lines
unless noted (`(impl)`).

### Construction / lifecycle

| Header:line | Method |
|---:|---|
| `:78` | `TessBaseAPI();` |
| `:79` | `virtual ~TessBaseAPI();` |
| `:658` | `void Clear();` (impl `:1845`) |
| `:666` | `void End();` (impl `:1861`) |
| `:675` | `static void ClearPersistentCache();` |

### Version

| Header:line | Method |
|---:|---|
| `:87` | `static const char *Version();` (returns `"5.5.3"`) |

### Image input

| Header:line | Method |
|---:|---|
| `:93` | `void SetInputName(const char *name);` |
| `:101` | `const char *GetInputName();` |
| `:103` | `void SetInputImage(Pix *pix);` |
| `:104` | `Pix *GetInputImage();` |
| `:105` | `int GetSourceYResolution();` |
| `:106` | `const char *GetDatapath();` |
| `:109` | `void SetOutputName(const char *name);` |
| `:307` | `void SetImage(const unsigned char *imagedata, int width, int height, int bytes_per_pixel, int bytes_per_line);` (impl `:506`) |
| `:318` | `void SetImage(Pix *pix);` (impl `:529`) |
| `:324` | `void SetSourceResolution(int ppi);` |
| `:331` | `void SetRectangle(int left, int top, int width, int height);` |
| `:282` | `char *TesseractRect(const unsigned char *imagedata, int bytes_per_pixel, int bytes_per_line, int left, int top, int width, int height);` (impl `:467`) |
| `:290` | `void ClearAdaptiveClassifier();` (impl `:488`) |

### Layout analysis (pre-recognize)

| Header:line | Method |
|---:|---|
| `:338` | `Pix *GetThresholdedImage();` |
| `:343` | `float GetGradient();` |
| `:350` | `Boxa *GetRegions(Pixa **pixa);` |
| `:363` | `Boxa *GetTextlines(bool raw_image, int raw_padding, Pixa **pixa, int **blockids, int **paraids);` |
| `:368` | `Boxa *GetTextlines(Pixa **pixa, int **blockids);` (inline) |
| `:380` | `Boxa *GetStrips(Pixa **pixa, int **blockids);` |
| `:387` | `Boxa *GetWords(Pixa **pixa);` |
| `:397` | `Boxa *GetConnectedComponents(Pixa **cc);` |
| `:411` | `Boxa *GetComponentImages(PageIteratorLevel level, bool text_only, bool raw_image, int raw_padding, Pixa **pixa, int **blockids, int **paraids);` |
| `:415` | `Boxa *GetComponentImages(const PageIteratorLevel level, const bool text_only, Pixa **pixa, int **blockids);` (inline) |
| `:427` | `int GetThresholdedImageScaleFactor() const;` |
| `:444` | `PageIterator *AnalyseLayout();` |
| `:445` | `PageIterator *AnalyseLayout(bool merge_similar_words);` |

### Initialization

| Header:line | Method |
|---:|---|
| `:197` | `int Init(const char *datapath, const char *language, OcrEngineMode mode, char **configs, int configs_size, const std::vector<std::string> *vars_vec, const std::vector<std::string> *vars_values, bool set_only_non_debug_params);` (impl `:300`) |
| `:202` | `int Init(const char *datapath, const char *language, OcrEngineMode oem);` (inline) |
| `:205` | `int Init(const char *datapath, const char *language);` (inline, OEM_DEFAULT) |
| `:211` | `int Init(const char *data, int data_size, const char *language, OcrEngineMode mode, char **configs, int configs_size, const std::vector<std::string> *vars_vec, const std::vector<std::string> *vars_values, bool set_only_non_debug_params, FileReader reader);` (impl `:310`) |
| `:225` | `const char *GetInitLanguagesAsString() const;` (impl `:376`) |
| `:232` | `void GetLoadedLanguagesAsVector(std::vector<std::string> *langs) const;` |
| `:237` | `void GetAvailableLanguagesAsVector(std::vector<std::string> *langs) const;` |
| `:243` | `void InitForAnalysePage();` (impl `:411`) |
| `:251` | `void ReadConfigFile(const char *filename);` |
| `:253` | `void ReadDebugConfigFile(const char *filename);` |
| `:260` | `void SetPageSegMode(PageSegMode mode);` |
| `:263` | `PageSegMode GetPageSegMode() const;` |

### Recognition

| Header:line | Method |
|---:|---|
| `:453` | `int Recognize(ETEXT_DESC *monitor);` (impl `:762`) |

### Multi-page processing

| Header:line | Method |
|---:|---|
| `:482` | `bool ProcessPages(const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` (impl `:999`) |
| `:485` | `bool ProcessPagesInternal(const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` (impl `:1033`) |
| `:497` | `bool ProcessPage(Pix *pix, int page_index, const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` (impl `:1196`) |

### Iterators

| Header:line | Method |
|---:|---|
| `:509` | `ResultIterator *GetIterator();` (impl `:1280`) |
| `:519` | `MutableIterator *GetMutableIterator();` (impl `:1297`) |

### Output formats

| Header:line | Method |
|---:|---|
| `:525` | `char *GetUTF8Text();` (impl `:1307`) |
| `:536` | `char *GetHOCRText(ETEXT_DESC *monitor, int page_number);` |
| `:544` | `char *GetHOCRText(int page_number);` |
| `:550` | `char *GetAltoText(ETEXT_DESC *monitor, int page_number);` |
| `:556` | `char *GetAltoText(int page_number);` |
| `:562` | `char *GetPAGEText(ETEXT_DESC *monitor, int page_number);` |
| `:568` | `char *GetPAGEText(int page_number);` |
| `:575` | `char *GetTSVText(int page_number);` (impl `:1353`) |
| `:583` | `char *GetLSTMBoxText(int page_number);` |
| `:592` | `char *GetBoxText(int page_number);` (impl `:1497`) |
| `:600` | `char *GetWordStrBoxText(int page_number);` |
| `:607` | `char *GetUNLVText();` |
| `:626` | `char *GetOsdText(int page_number);` (impl `:1689`) |

### Confidence & orientation

| Header:line | Method |
|---:|---|
| `:618` | `bool DetectOrientationScript(int *orient_deg, float *orient_conf, const char **script_name, float *script_conf);` (impl `:1653`) |
| `:629` | `int MeanTextConf();` (impl `:1719`) |
| `:636` | `int *AllWordConfidences();` (impl `:1737`) |
| `:701` | `bool DetectOS(OSResults *);` |
| `:707` | `void GetBlockTextOrientations(int **block_orientation, bool **vertical_writing);` |
| `:687` | `bool GetTextDirection(int *out_offset, float *out_slope);` |
| `:727` | `void set_min_orientation_margin(double margin);` |

### Variable access

| Header:line | Method |
|---:|---|
| `:124` | `bool SetVariable(const char *name, const char *value);` |
| `:125` | `bool SetDebugVariable(const char *name, const char *value);` |
| `:131` | `bool GetIntVariable(const char *name, int *value) const;` |
| `:132` | `bool GetBoolVariable(const char *name, bool *value) const;` |
| `:133` | `bool GetDoubleVariable(const char *name, double *value) const;` |
| `:139` | `const char *GetStringVariable(const char *name) const;` |
| `:146` | `void PrintFontsTable(FILE *fp) const;` (legacy) |
| `:153` | `void PrintVariables(FILE *fp) const;` |
| `:158` | `bool GetVariableAsString(const char *name, std::string *val) const;` |

### Adaptive / dictionary hooks

| Header:line | Method |
|---:|---|
| `:649` | `bool AdaptToWordStr(PageSegMode mode, const char *wordstr);` (legacy; impl `:1777`) |
| `:683` | `int IsValidWord(const char *word) const;` |
| `:685` | `bool IsValidCharacter(const char *utf8_character) const;` |
| `:690` | `void SetDictFunc(DictFunc f);` |
| `:695` | `void SetProbabilityInContextFunc(ProbabilityInContextFunc f);` |

### Accessors

| Header:line | Method |
|---:|---|
| `:711` | `const char *GetUnichar(int unichar_id) const;` |
| `:714` | `const Dawg *GetDawg(int i) const;` |
| `:717` | `int NumDawgs() const;` |
| `:719` | `Tesseract *tesseract() const;` |
| `:723` | `OcrEngineMode oem() const;` |

### Free helper

| Header:line | Symbol |
|---:|---|
| `:816` | `std::string HOcrEscape(const char *text);` |

---

## 5.6 Renderer factory functions

All renderers are concrete subclasses of `TessResultRenderer`
(`include/tesseract/renderer.h:47`). Constructors are `Tess<Type>RendererCreate`
factory functions exposed in the C API (`include/tesseract/capi.h:161-174`).

| Format | Renderer class | Constructor | Output ext | Trigger |
|---|---|---|---|---|
| Plain text | `TessTextRenderer` (`renderer.h:160`) | `TessTextRendererCreate` (`capi.h:161`) | `.txt` | default or `tessedit_create_txt=1` |
| hOCR | `TessHOcrRenderer` (`renderer.h:171`) | `TessHOcrRendererCreate[2]` (`capi.h:162-163`) | `.hocr` | `tessedit_create_hocr=1` |
| ALTO XML | `TessAltoRenderer` (`renderer.h:188`) | `TessAltoRendererCreate` (`capi.h:165`) | `.xml` | `tessedit_create_alto=1` |
| PAGE XML | `TessPAGERenderer` (`renderer.h:204`) | `TessPAGERendererCreate` (`capi.h:166`) | `.xml` | `tessedit_create_page_xml=1` |
| TSV | `TessTsvRenderer` (`renderer.h:221`) | `TessTsvRendererCreate` (`capi.h:167`) | `.tsv` | `tessedit_create_tsv=1` |
| Searchable PDF | `TessPDFRenderer` (`renderer.h:238`) | `TessPDFRendererCreate` (`capi.h:168`) | `.pdf` | `tessedit_create_pdf=1` |
| UNLV | `TessUnlvRenderer` (`renderer.h:276`) | `TessUnlvRendererCreate` (`capi.h:171`) | `.unlv` | `tessedit_write_unlv=1` |
| LSTM Box | `TessLSTMBoxRenderer` (`renderer.h:287`) | `TessLSTMBoxRendererCreate` (`capi.h:173`) | `.box` | `tessedit_create_lstmbox=1` |
| Box | `TessBoxTextRenderer` (`renderer.h:298`) | `TessBoxTextRendererCreate` (`capi.h:172`) | `.box` | `tessedit_create_boxfile=1` |
| WordStr Box | `TessWordStrBoxRenderer` (`renderer.h:309`) | `TessWordStrBoxRendererCreate` (`capi.h:174`) | `.box` | `tessedit_create_wordstrbox=1` |
| OSD (legacy) | `TessOsdRenderer` (`renderer.h:322`) | (CLI-only flag, not in C API) | `.osd` | `PSM_OSD_ONLY` |

Composition: `TessResultRenderer::insert(next)` (`renderer.h:54`) chains
multiple renderers so one `ProcessPages` call produces multiple outputs.

Renderer control callbacks (C API, `capi.h:177-190`):
- `TessDeleteResultRenderer(renderer)` (`:177`)
- `TessResultRendererInsert(renderer, next)` (`:178`)
- `TessResultRendererNext(renderer)` (`:180`)
- `TessResultRendererBeginDocument(renderer, title)` (`:182`)
- `TessResultRendererAddImage(renderer, api)` (`:184`)
- `TessResultRendererEndDocument(renderer)` (`:186`)
- `TessResultRendererExtention(renderer)` (`:188`)
- `TessResultRendererTitle(renderer)` (`:189`)
- `TessResultRendererImageNum(renderer)` (`:190`)

---

## 5.7 C API — `TessBaseAPI*` wrappers

Every `TessBaseAPI` C++ method has a C wrapper in `include/tesseract/capi.h`
(625 lines, 100+ entries). The complete list lives in [`INDEX.md`](./INDEX.md)
§ 2.b; here is the lifecycle-only subset:

```c
/* Creation / lifecycle */
TessBaseAPI *TessBaseAPICreate();              // line 210
void         TessBaseAPIDelete(handle);         // line 217

/* Init (5 variants) */
int TessBaseAPIInit1(handle, datapath, lang, OEM, configs[], n);                  // 248
int TessBaseAPIInit2(handle, datapath, lang, OEM);                                 // 251
int TessBaseAPIInit3(handle, datapath, lang, OEM, configs[], n, vars, vals, flag);  // 267
int TessBaseAPIInit4(handle, datapath, lang, OEM);                                 // 270
int TessBaseAPIInit5(handle, data, data_size, lang, OEM, ..., FileReader);         // 276

/* Image input */
void TessBaseAPISetImage(handle, imagedata, w, h, bpp, bpl);                       // 307
void TessBaseAPISetImage2(handle, Pix *);                                          // 323
void TessBaseAPISetRectangle(handle, left, top, w, h);                             // 327

/* Recognition + outputs */
int   TessBaseAPIRecognize(handle, ETEXT_DESC *);                                  // 362
BOOL  TessBaseAPIProcessPages(handle, filename, retry_config, timeout_ms, ren);    // 364
BOOL  TessBaseAPIProcessPage(handle, Pix *, page_idx, filename, retry, timeout, ren); // 368
TessPageIterator     *TessBaseAPIAnalyseLayout(handle);                            // 360
TessResultIterator   *TessBaseAPIGetIterator(handle);                              // 374
TessMutableIterator  *TessBaseAPIGetMutableIterator(handle);                       // 375

char *TessBaseAPIGetUTF8Text(handle);                                              // 387
char *TessBaseAPIGetHOCRText(handle, page_number);                                 // 398
char *TessBaseAPIGetAltoText(handle, page_number);                                 // 409
char *TessBaseAPIGetPAGEText(handle, page_number);                                  // 420
char *TessBaseAPIGetTsvText(handle, page_number);                                   // 431
char *TessBaseAPIGetBoxText(handle, page_number);                                   // 442
char *TessBaseAPIGetLSTMBoxText(handle, page_number);                               // 453
char *TessBaseAPIGetWordStrBoxText(handle, page_number);                            // 464
char *TessBaseAPIGetUNLVText(handle);                                              // 475

/* Teardown */
void TessBaseAPIClear(handle);       // 486
void TessBaseAPIEnd(handle);         // 487
void TessBaseAPIClearPersistentCache(handle); // 495
```

Memory rule: every `char *` returned must be freed with `TessDeleteText`
(`capi.h:156`); every `char **` with `TessDeleteTextArray` (`:157`); every
`int *` with `TessDeleteIntArray` (`:158`).

---

## 5.8 Lifecycle cheatsheet (the canonical 4-line usage)

From the C API header doc-comment (`include/tesseract/capi.h:198-206`):

```c
TessBaseAPI *api = TessBaseAPICreate();
TessBaseAPIInit3(api, NULL, "eng", OEM_DEFAULT, NULL, 0, NULL, NULL, FALSE);
TessBaseAPISetImage2(api, pix);
char *text = TessBaseAPIGetUTF8Text(api);
// ... use text ...
TessDeleteText(text);
TessBaseAPIEnd(api);          // optional
TessBaseAPIDelete(api);
```

This is the exact pattern a JNI wrapper must follow. See
[`10_functions_detail/tesscapi.md`](./10_functions_detail/tesscapi.md) for
per-method detail.