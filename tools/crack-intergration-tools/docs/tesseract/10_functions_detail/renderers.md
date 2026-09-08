# Renderers — `TessResultRenderer` and subclasses

> Abstract base `class TESS_API TessResultRenderer`
> (`include/tesseract/renderer.h:47`) with 11 concrete subclasses.
> Constructed via C-API factory functions (`include/tesseract/capi.h:161-174`).
> Composition via `void insert(TessResultRenderer *next)` (`renderer.h:54`).
> All file:line references grep-verified.

The class hierarchy is documented in [`03_architecture.md §3.3`](../03_architecture.md).

---

## Abstract base `class TESS_API TessResultRenderer` — `include/tesseract/renderer.h:47`

### `void insert(TessResultRenderer *next)`
- **签名**: `void insert(TessResultRenderer *next)`
- **位置**: decl `include/tesseract/renderer.h:54`
- **可见性**: public
- **副作用**: 把 `next` 链到当前 renderer 之后
- **调用**: `TessResultRendererInsert` (C API wrapper at `capi.h:178`)
- **简要说明**: 链式组合；一个 `ProcessPages` 调用可生成多个输出

### Lifecycle hooks (virtual)

#### `virtual bool BeginDocumentHandler()`
- **位置**: declared in `renderer.h:47+`
- **调用**: `TessResultRendererBeginDocument` (`:182`)
- **简要说明**: 文档开始时调用

#### `virtual bool AddImageHandler(TessBaseAPI *)`
- **位置**: declared in `renderer.h:47+`
- **调用**: `TessResultRendererAddImage` (`:184`)
- **简要说明**: 每页调用

#### `virtual bool EndDocumentHandler()`
- **位置**: declared in `renderer.h:47+`
- **调用**: `TessResultRendererEndDocument` (`:186`)
- **简要说明**: 文档结束时调用

---

## Concrete renderers

### `class TESS_API TessTextRenderer` — `include/tesseract/renderer.h:160`
- **impl**: `src/api/renderer.cpp:139`
- **构造**: `TessTextRendererCreate(outputbase)` (`capi.h:161`)
- **输出**: `.txt`
- **触发**: 默认 / `tessedit_create_txt=1`
- **简要说明**: 纯文本输出；最常用

### `class TESS_API TessHOcrRenderer` — `include/tesseract/renderer.h:171`
- **impl**: `src/api/hocrrenderer.cpp:513`
- **构造**: `TessHOcrRendererCreate(outputbase)` / `Create2(outputbase, font_id)` (`capi.h:162-163`)
- **输出**: `.hocr`（HTML-based OCR）
- **触发**: `tessedit_create_hocr=1`
- **简要说明**: hOCR XML 含 bbox；通用下游工具友好

### `class TESS_API TessAltoRenderer` — `include/tesseract/renderer.h:188`
- **impl**: `src/api/altorenderer.cpp:80`
- **构造**: `TessAltoRendererCreate(outputbase)` (`capi.h:165`)
- **输出**: `.xml`（ALTO XML）
- **触发**: `tessedit_create_alto=1`
- **简要说明**: ALTO schema（archive 标准）

### `class TESS_API TessPAGERenderer` — `include/tesseract/renderer.h:204`
- **impl**: `src/api/pagerenderer.cpp:628`
- **构造**: `TessPAGERendererCreate(outputbase)` (`capi.h:166`)
- **输出**: `.xml`（PAGE XML）
- **触发**: `tessedit_create_page_xml=1`
- **简要说明**: PAGE schema（Transkribus / OCR-D 标准）

### `class TESS_API TessTsvRenderer` — `include/tesseract/renderer.h:221`
- **impl**: `src/api/renderer.cpp:179`
- **构造**: `TessTsvRendererCreate(outputbase)` (`capi.h:167`)
- **输出**: `.tsv`（Tab-separated）
- **触发**: `tessedit_create_tsv=1`
- **简要说明**: 含 bbox 坐标的 TSV；适合脚本二次处理

### `class TESS_API TessPDFRenderer` — `include/tesseract/renderer.h:238`
- **impl**: `src/api/pdfrenderer.cpp:827`
- **构造**: `TessPDFRendererCreate(outputbase, datadir, textonly)` (`capi.h:168`)
- **输出**: `.pdf`（searchable PDF）
- **触发**: `tessedit_create_pdf=1`
- **简要说明**: 输出带不可见文本层的 PDF；嵌入 `tessdata/pdf.ttf` 字体

### `class TESS_API TessUnlvRenderer` — `include/tesseract/renderer.h:276`
- **impl**: `src/api/renderer.cpp:196`
- **构造**: `TessUnlvRendererCreate(outputbase)` (`capi.h:171`)
- **输出**: `.unlv`
- **触发**: `tessedit_write_unlv=1`
- **简要说明**: UNLV zone 格式（90 年代 OCR 标准）

### `class TESS_API TessLSTMBoxRenderer` — `include/tesseract/renderer.h:287`
- **impl**: `src/api/lstmboxrenderer.cpp:95`
- **构造**: `TessLSTMBoxRendererCreate(outputbase)` (`capi.h:173`)
- **输出**: `.box`（LSTM 训练用）
- **触发**: `tessedit_create_lstmbox=1`
- **简要说明**: LSTM box 格式（与 unicharset 配对）

### `class TESS_API TessBoxTextRenderer` — `include/tesseract/renderer.h:298`
- **impl**: `src/api/renderer.cpp:213`
- **构造**: `TessBoxTextRendererCreate(outputbase)` (`capi.h:172`)
- **输出**: `.box`（legacy box）
- **触发**: `tessedit_create_boxfile=1`
- **简要说明**: 传统 box 格式（legacy training）

### `class TESS_API TessWordStrBoxRenderer` — `include/tesseract/renderer.h:309`
- **impl**: `src/api/wordstrboxrenderer.cpp:94`
- **构造**: `TessWordStrBoxRendererCreate(outputbase, page)` (`capi.h:174`)
- **输出**: `.box`（wordstr 格式）
- **触发**: `tessedit_create_wordstrbox=1`
- **简要说明**: 单词级 box + ground truth string

### `class TESS_API TessOsdRenderer` — `include/tesseract/renderer.h:322` (legacy)
- **impl**: `src/api/renderer.cpp:231`
- **构造**: 不在 C API；CLI 通过 `PSM_OSD_ONLY` 触发
- **输出**: `.osd`
- **简要说明**: 仅输出 OSD 结果（orientation + script）；与 `TessBaseAPI::GetOsdText` 重复

---

## Renderer construction pattern

```cpp
// C++ API (for library users)
#include <tesseract/renderer.h>
auto text  = std::make_unique<TessTextRenderer>("out");
auto hocr  = std::make_unique<TessHOcrRenderer>("out");
text->insert(hocr.get());           // chain hocr after text

api.ProcessPages("image.png", nullptr, 0, text.get());
// out.txt + out.hocr both produced
```

```c
// C API
TessResultRenderer *text = TessTextRendererCreate("out");
TessResultRenderer *hocr = TessHOcrRendererCreate("out");
TessResultRendererInsert(text, hocr);     // chain hocr after text

TessBaseAPIProcessPages(api, "image.png", NULL, 0, text);
// out.txt + out.hocr both produced

TessDeleteResultRenderer(text);
TessDeleteResultRenderer(hocr);
```

---

## Quick selection guide

| Need | Renderer |
|---|---|
| Quick sanity check | `TessTextRenderer` |
| Downstream scripts (Python etc.) | `TessTsvRenderer` (bbox) |
| Transkribus / OCR-D | `TessPAGERenderer` or `TessAltoRenderer` |
| Searchable PDF | `TessPDFRenderer` |
| Re-train LSTM | `TessLSTMBoxRenderer` |
| Page rotation detection only | `TessOsdRenderer` (or `GetOsdText`) |