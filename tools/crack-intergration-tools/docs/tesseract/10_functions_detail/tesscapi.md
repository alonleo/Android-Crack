# Tess C API — `include/tesseract/capi.h`

> The C-API façade exposes 100+ `extern "C"` wrappers that mirror
> `TessBaseAPI` methods. Declared in `include/tesseract/capi.h` (625 lines),
> implemented in `src/api/capi.cpp` (711 lines).
>
> Memory rule: every `char *` returned must be freed with `TessDeleteText`
> (`capi.h:156`); every `char **` with `TessDeleteTextArray` (`:157`); every
> `int *` with `TessDeleteIntArray` (`:158`).
>
> All file:line references below are grep-verified.

---

## Free functions

### `const char *TessVersion()`
- **签名**: `const char *TessVersion()`
- **位置**: decl `include/tesseract/capi.h:148`
- **可见性**: public
- **抛出**: 无
- **返回值**: `"5.5.3"`
- **调用**: 用户代码
- **简要说明**: 返回版本字符串

### `void TessDeleteText(const char *text)`
- **签名**: `void TessDeleteText(const char *text)`
- **位置**: decl `include/tesseract/capi.h:156`
- **可见性**: public
- **副作用**: `delete[]` 内部分配的文本
- **调用**: 每个返回 `char *` 的 API 后必须调用
- **简要说明**: 释放 `TessBaseAPIGetUTF8Text` 等返回的字符串

### `void TessDeleteTextArray(char **arr)`
- **位置**: decl `include/tesseract/capi.h:157`
- **简要说明**: 释放 `TessBaseAPIGetLoadedLanguagesAsVector` 等返回的字符串数组

### `void TessDeleteIntArray(const int *arr)`
- **位置**: decl `include/tesseract/capi.h:158`
- **简要说明**: 释放 `TessBaseAPIAllWordConfidences` 等返回的 int 数组

---

## Renderer factories

### `TessResultRenderer *TessTextRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:161`
- **调用**: CLI `PreloadRenderers` (`src/tesseract.cpp:510`)
- **简要说明**: 创建纯文本 renderer

### `TessResultRenderer *TessHOcrRendererCreate(outputbase)` / `Create2(outputbase, font_id)`
- **位置**: decl `include/tesseract/capi.h:162, 163`
- **简要说明**: 创建 hOCR renderer；`Create2` 可指定字体 ID

### `TessResultRenderer *TessAltoRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:165`
- **简要说明**: 创建 ALTO XML renderer

### `TessResultRenderer *TessPAGERendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:166`
- **简要说明**: 创建 PAGE XML renderer

### `TessResultRenderer *TessTsvRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:167`
- **简要说明**: 创建 TSV renderer

### `TessResultRenderer *TessPDFRendererCreate(outputbase, datadir, textonly)`
- **位置**: decl `include/tesseract/capi.h:168`
- **简要说明**: 创建 searchable PDF renderer

### `TessResultRenderer *TessUnlvRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:171`
- **简要说明**: 创建 UNLV zone renderer

### `TessResultRenderer *TessBoxTextRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:172`
- **简要说明**: 创建 box text renderer

### `TessResultRenderer *TessLSTMBoxRendererCreate(outputbase)`
- **位置**: decl `include/tesseract/capi.h:173`
- **简要说明**: 创建 LSTM box renderer

### `TessResultRenderer *TessWordStrBoxRendererCreate(outputbase, page)`
- **位置**: decl `include/tesseract/capi.h:174`
- **简要说明**: 创建 wordstr box renderer

### Renderer control

| Symbol | Line | Note |
|---|---:|---|
| `TessDeleteResultRenderer(renderer)` | `:177` | destructor |
| `TessResultRendererInsert(renderer, next)` | `:178` | chain outputs |
| `TessResultRendererNext(renderer)` | `:180` | walk chain |
| `TessResultRendererBeginDocument(renderer, title)` | `:182` | start |
| `TessResultRendererAddImage(renderer, api)` | `:184` | per-image |
| `TessResultRendererEndDocument(renderer)` | `:186` | end |
| `TessResultRendererExtention(renderer)` | `:188` | file ext |
| `TessResultRendererTitle(renderer)` | `:189` | title |
| `TessResultRendererImageNum(renderer)` | `:190` | image count |

---

## TessBaseAPI C-API wrappers

### Lifecycle

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPICreate()` | `:210` | ctor |
| `TessBaseAPIDelete(handle)` | `:217` | dtor |
| `TessBaseAPIClear(handle)` | `:486` | `Clear()` |
| `TessBaseAPIEnd(handle)` | `:487` | `End()` |
| `TessBaseAPIClearPersistentCache(handle)` | `:495` | `static ClearPersistentCache()` |

### Input name / image

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPISetInputName(handle, name)` | `:219` | `SetInputName` |
| `TessBaseAPIGetInputName(handle)` | `:220` | `GetInputName` |
| `TessBaseAPISetInputImage(handle, Pix *)` | `:222` | `SetInputImage` |
| `TessBaseAPIGetInputImage(handle)` | `:223` | `GetInputImage` |
| `TessBaseAPIGetSourceYResolution(handle)` | `:225` | `GetSourceYResolution` |
| `TessBaseAPIGetDatapath(handle)` | `:226` | `GetDatapath` |
| `TessBaseAPISetOutputName(handle, name)` | `:228` | `SetOutputName` |

### Init (5 variants)

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIInit1(handle, datapath, lang, OEM, configs[], n)` | `:248` | 4-arg Init (no debug) |
| `TessBaseAPIInit2(handle, datapath, lang, OEM)` | `:251` | 3-arg Init |
| `TessBaseAPIInit3(handle, datapath, lang, OEM, configs[], n, vars, vals, flag)` | `:267` | full 7-arg Init |
| `TessBaseAPIInit4(handle, datapath, lang, OEM)` | `:270` | debug 3-arg |
| `TessBaseAPIInit5(handle, data, data_size, lang, OEM, ..., FileReader)` | `:276` | memory Init |

### Language / config

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIGetInitLanguagesAsString(handle)` | `:282` | `GetInitLanguagesAsString` |
| `TessBaseAPIGetLoadedLanguagesAsVector(handle)` | `:284` | `GetLoadedLanguagesAsVector` |
| `TessBaseAPIGetAvailableLanguagesAsVector(handle)` | `:286` | `GetAvailableLanguagesAsVector` |
| `TessBaseAPIInitForAnalysePage(handle)` | `:289` | `InitForAnalysePage` |
| `TessBaseAPIReadConfigFile(handle, filename)` | `:291` | `ReadConfigFile` |
| `TessBaseAPIReadDebugConfigFile(handle, filename)` | `:293` | `ReadDebugConfigFile` |
| `TessBaseAPISetPageSegMode(handle, PSM)` | `:296` | `SetPageSegMode` |
| `TessBaseAPIGetPageSegMode(handle)` | `:298` | `GetPageSegMode` |

### Variable access

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPISetVariable(handle, name, value)` | `:230` | `SetVariable` |
| `TessBaseAPISetDebugVariable(handle, name, value)` | `:232` | `SetDebugVariable` |
| `TessBaseAPIGetIntVariable(handle, name, value*)` | `:235` | `GetIntVariable` |
| `TessBaseAPIGetBoolVariable(handle, name, value*)` | `:237` | `GetBoolVariable` |
| `TessBaseAPIGetDoubleVariable(handle, name, value*)` | `:239` | `GetDoubleVariable` |
| `TessBaseAPIGetStringVariable(handle, name)` | `:241` | `GetStringVariable` |
| `TessBaseAPIPrintVariables(handle, FILE *)` | `:244` | `PrintVariables` |
| `TessBaseAPIPrintVariablesToFile(handle, filename, append)` | `:245` | file print |

### Image input

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIRect(handle, imagedata, bpp, bpl, left, top, w, h)` | `:300` | `TesseractRect` |
| `TessBaseAPIClearAdaptiveClassifier(handle)` | `:305` | `ClearAdaptiveClassifier` |
| `TessBaseAPISetImage(handle, imagedata, w, h, bpp, bpl)` | `:307` | raw buffer |
| `TessBaseAPISetImage2(handle, Pix *)` | `:323` | Pix overload |
| `TessBaseAPISetSourceResolution(handle, ppi)` | `:325` | `SetSourceResolution` |
| `TessBaseAPISetRectangle(handle, left, top, w, h)` | `:327` | `SetRectangle` |

### Layout analysis (pre-Recognize)

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIGetThresholdedImage(handle)` | `:330` | `GetThresholdedImage` |
| `TessBaseAPIGetGradient(handle)` | `:331` | `GetGradient` |
| `TessBaseAPIGetRegions(handle, pixa)` | `:332` | `GetRegions` |
| `TessBaseAPIGetTextlines(handle, raw_image, raw_padding, pixa, blockids, paraids)` | `:334` | full |
| `TessBaseAPIGetTextlines1(handle, pixa, blockids)` | `:337` | simple |
| `TessBaseAPIGetStrips(handle, pixa, blockids)` | `:341` | `GetStrips` |
| `TessBaseAPIGetWords(handle, pixa)` | `:343` | `GetWords` |
| `TessBaseAPIGetConnectedComponents(handle, cc)` | `:345` | `GetConnectedComponents` |
| `TessBaseAPIGetComponentImages(handle, level, text_only, raw_image, raw_padding, pixa, blockids, paraids)` | `:347` | full |
| `TessBaseAPIGetComponentImages1(handle, level, text_only, pixa, blockids)` | `:352` | simple |
| `TessBaseAPIGetThresholdedImageScaleFactor(handle)` | `:357` | `GetThresholdedImageScaleFactor` |
| `TessBaseAPIAnalyseLayout(handle)` | `:360` | `AnalyseLayout` |

### Recognition + outputs

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIRecognize(handle, ETEXT_DESC *)` | `:362` | `Recognize` |
| `TessBaseAPIProcessPages(handle, filename, retry_config, timeout_ms, renderer)` | `:364` | `ProcessPages` |
| `TessBaseAPIProcessPage(handle, Pix *, page_idx, filename, retry_config, timeout_ms, renderer)` | `:368` | `ProcessPage` |
| `TessBaseAPIGetIterator(handle)` | `:374` | `GetIterator` |
| `TessBaseAPIGetMutableIterator(handle)` | `:375` | `GetMutableIterator` |
| `TessBaseAPIGetUTF8Text(handle)` | `:387` | `GetUTF8Text` |
| `TessBaseAPIGetHOCRText(handle, page_number)` | `:398` | `GetHOCRText` |
| `TessBaseAPIGetAltoText(handle, page_number)` | `:409` | `GetAltoText` |
| `TessBaseAPIGetPAGEText(handle, page_number)` | `:420` | `GetPAGEText` |
| `TessBaseAPIGetTsvText(handle, page_number)` | `:431` | `GetTSVText` |
| `TessBaseAPIGetBoxText(handle, page_number)` | `:442` | `GetBoxText` |
| `TessBaseAPIGetLSTMBoxText(handle, page_number)` | `:453` | `GetLSTMBoxText` |
| `TessBaseAPIGetWordStrBoxText(handle, page_number)` | `:464` | `GetWordStrBoxText` |
| `TessBaseAPIGetUNLVText(handle)` | `:475` | `GetUNLVText` |

### Confidence / OSD

| Symbol | Line | Wraps |
|---|---:|---|
| `TessBaseAPIMeanTextConf(handle)` | `:476` | `MeanTextConf` |
| `TessBaseAPIAllWordConfidences(handle)` | `:478` | `AllWordConfidences` |
| `TessBaseAPIAdaptToWordStr(handle, PSM, wordstr)` | `:481` | `AdaptToWordStr` (legacy) |
| `TessBaseAPIIsValidWord(handle, word)` | `:489` | `IsValidWord` |
| `TessBaseAPIGetTextDirection(handle, out_offset*, out_slope*)` | `:490` | `GetTextDirection` |
| `TessBaseAPIGetUnichar(handle, unichar_id)` | `:493` | `GetUnichar` |
| `TessBaseAPIDetectOrientationScript(handle, orient_deg*, orient_conf*, script_name**, script_conf*)` | `:501` | `DetectOrientationScript` |
| `TessBaseAPISetMinOrientationMargin(handle, margin)` | `:508` | `set_min_orientation_margin` |
| `TessBaseAPINumDawgs(handle)` | `:511` | `NumDawgs` |
| `TessBaseAPIOem(handle)` | `:513` | `oem` |

---

## Canonical 4-line usage (from `capi.h:198-206`)

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

This is the exact pattern a JNI wrapper must follow. Memory discipline:

| Allocator | Deallocator | Source |
|---|---|---|
| `TessBaseAPIGetUTF8Text` / `GetHOCRText` / `GetAltoText` / `GetPAGEText` / `GetTsvText` / `GetBoxText` / `GetLSTMBoxText` / `GetWordStrBoxText` / `GetUNLVText` / `GetOsdText` / `TessBaseAPIRect` | `TessDeleteText` | `capi.h:156` |
| `TessBaseAPIGetLoadedLanguagesAsVector` / `GetAvailableLanguagesAsVector` | `TessDeleteTextArray` | `capi.h:157` |
| `TessBaseAPIAllWordConfidences` / `GetIntVariable` (indirect) | `TessDeleteIntArray` | `capi.h:158` |
| `TessBaseAPICreate` | `TessBaseAPIDelete` | `capi.h:210, 217` |
| `TessTextRendererCreate` / `TessHOcrRendererCreate` / etc. | `TessDeleteResultRenderer` | `capi.h:161-174, 177` |
| `TessBaseAPIGetIterator` / `GetMutableIterator` | `delete` (C++ side) | `capi.h:374, 375` |