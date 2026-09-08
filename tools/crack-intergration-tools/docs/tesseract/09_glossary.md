# 09 — Glossary

Alphabetical. Each term links to the file:line where the canonical
definition lives.

---

### `BLOCK`
A top-level region in the page layout (text block, image block, equation
block, etc.). One of the `PageIteratorLevel` values (`publictypes.h:214`).
See `include/tesseract/publictypes.h:51` for `PolyBlockType`.

### C API
The `extern "C"` wrapper surface in `include/tesseract/capi.h` (625 lines,
100+ entries) that lets non-C++ callers use `TessBaseAPI`. Every `TessBaseAPI`
C++ method has a `TessBaseAPI<Verb>` C wrapper; convention `TessBaseAPICreate`
/ `TessBaseAPIDelete` for lifecycle, `TessDeleteText` for memory.

### `componentimages`
Layout-analysis API on `TessBaseAPI` returning a `Boxa *` of all sub-image
regions (`GetComponentImages` at `include/tesseract/baseapi.h:411`).

### `.config` files
One-line `VAR VALUE` files in `tessdata/configs/` (24 of them). They set
`tessedit_create_*` flags and other parameters. Used by the CLI when passed
as a positional arg after the image / outputbase, or loaded via
`TessBaseAPI::ReadConfigFile` (`baseapi.h:251`).

### `cpufeatures.h`
Android NDK header providing `android_getCpuFeatures()`. Required because
Tesseract dispatches NEON at runtime (`src/arch/simddetect.cpp:227`). Pulled
in via `CpuFeaturesNdkCompat` (`CMakeLists.txt:851-858`).

### `Dict`
Dictionary class in `src/dict/dict.cpp`. Provides `is_valid_word`,
`probability_in_context_`. Used by the language-model pass
(`src/wordrec/language_model.cpp:1235`).

### `Dawg`
Directed Acyclic Word Graph — compact representation of a word list.
`src/dict/dawg.cpp`.

### `ETEXT_DESC`
Progress / cancel callback struct. `include/tesseract/ocrclass.h:102`.
Used by `TessBaseAPI::Recognize(ETEXT_DESC *)` (`baseapi.h:453`) and the
TSV / HOCR overloads.

### `findFileFormat`
Internal autodetect helper at `src/api/baseapi.cpp:1142`. Recognizes PNG,
JPEG, TIFF, PDF, PNM, BMP, GIF, WEBP, and remote URLs (via libcurl).

### `HOCR` / `hOCR`
HTML-based OCR output format. `TessHOcrRenderer` at `include/tesseract/renderer.h:171`;
triggered by `tessedit_create_hocr=1`.

### `init_lstm_components`
`Tesseract` method that constructs the LSTM recognizer. Called during `Init`
when OEM is LSTM-capable. `src/ccmain/tessedit.cpp:171-172`.

### `LSTM`
Long Short-Term Memory network. Tesseract 4.x+ recognizer backend.
`src/lstm/` (36 files). The pre-4.x shape-classifier engine is in
`src/classify/` + `src/wordrec/`, gated by `DISABLED_LEGACY_ENGINE`.

### `LTRResultIterator`
Base class for `ResultIterator` and `MutableIterator`. Adds text extraction
methods on top of `PageIterator`. `include/tesseract/ltrresultiterator.h:45`.

### `MutableIterator`
Subclass of `ResultIterator` that exposes the internal `PAGE_RES_IT *`.
`src/ccmain/mutableiterator.h:51`. Useful for advanced callers that need
to walk Tesseract's data structures directly.

### `OEM` — `OcrEngineMode`
Enum selecting the recognizer. `include/tesseract/publictypes.h:263-277`:
`OEM_TESSERACT_ONLY (=0)`, `OEM_LSTM_ONLY (=1)`, `OEM_TESSERACT_LSTM_COMBINED (=2)`,
`OEM_DEFAULT (=3)`. CLI default `OEM_LSTM_ONLY` when legacy is disabled
(`src/tesseract.cpp:670-674`).

### `OSD` — Orientation & Script Detection
Detects page rotation (0° / 90° / 180° / 270°) and script (Latin / Han /
Cyrillic / Arabic / …). Headers in `include/tesseract/osdetect.h`. Trigger
flags: `PSM_OSD_ONLY (=0)`, `PSM_AUTO_OSD (=1)`, `PSM_SPARSE_TEXT_OSD (=12)`.
Renderer: `TessOsdRenderer` (`include/tesseract/renderer.h:322`).

### `PAGE_RES`
Internal data structure holding the recognition result tree (`PAGE_RES` in
`src/ccstruct/pageres.{h,cpp}`). `TessBaseAPI::Recognize` constructs this
(`src/api/baseapi.cpp:786`); iterators point into it.

### `PAGE XML`
Page Analysis XML format used by Transkribus / OCR-D. `TessPAGERenderer`
at `include/tesseract/renderer.h:204`. Triggered by
`tessedit_create_page_xml=1`.

### `Pdf.ttf`
Font bundled in `tessdata/pdf.ttf`, embedded by `TessPDFRenderer`
(`src/api/pdfrenderer.cpp:827`) so searchable PDFs render the invisible text
layer without depending on the viewer's installed fonts.

### `Pix`
Leptonica image class. Tesseract uses `Pix *` throughout (`SetImage(Pix *)`
at `include/tesseract/baseapi.h:318`). Comes from Leptonica ≥ 1.74.

### `PolyBlockType`
Block type enum (`include/tesseract/publictypes.h:51`). Values
`PT_UNKNOWN`, `PT_FLOWING_TEXT`, `PT_HEADING_TEXT`, `PT_PULLOUT_TEXT`,
`PT_EQUATION`, `PT_INLINE_EQUATION`, `PT_TABLE`, `PT_VERTICAL_TEXT`,
`PT_CAPTION_TEXT`, `PT_FLOWING_IMAGE`, `PT_HEADING_IMAGE`,
`PT_PULLOUT_IMAGE`, `PT_HORZ_LINE`, `PT_VERT_LINE`, `PT_NOISE`.

### `PSM` — `PageSegMode`
Enum selecting the page-segmentation strategy. `include/tesseract/publictypes.h:157-178`.
14 values, 0–13. CLI default `PSM_AUTO` (`:300`); library default `PSM_SINGLE_BLOCK`.

### `ResultIterator`
Subclass of `LTRResultIterator` adding recognition-specific helpers
(`include/tesseract/resultiterator.h:32`). Returned by `TessBaseAPI::GetIterator()`.

### `ScrollView`
TCP-based interactive viewer. C++ server: `src/viewer/scrollview.cpp` (port 8461).
Java Swing client: `java/com/google/scrollview/` (imports `javax.swing.JFrame`).
Used for visualizing `.box` training files.

### `Stopper`
Dictionary stop-word list (`src/dict/stopper.{h,cpp}`). Words that are
common enough that the recognizer shouldn't insist on them.

### `TESS_API`
DLL export visibility macro. `include/tesseract/export.h:19-35`.
Windows: `__declspec(dllexport/dllimport)`; GCC/Clang: `__attribute__((visibility("default")))`
when `TESS_EXPORTS` or `TESS_IMPORTS` is defined (`CMakeLists.txt:801-807`).

### `tessdata`
The directory holding language model `.traineddata` files. **Not shipped**
in this repo — must be downloaded from
<https://github.com/tesseract-ocr/tessdata>. The repo's `tessdata/`
contains only configs and `pdf.ttf`.

### `tessedit_*`
The `tessedit_*` parameter namespace (e.g. `tessedit_pageseg_mode`,
`tessedit_create_pdf`, `tessedit_create_hocr`). All defined in
`src/ccmain/tessvars.cpp` (auto-generated by `Params` macros).

### `.traineddata`
A binary file produced by `combine_tessdata` (`src/training/combine_tessdata.cpp:117`)
that bundles the LSTM weights, dictionary DAWGs, unicharset, and config for a
language. Internally a directory of components (`lstm`, `lstm_p`, `feat`,
`normproto`, `pffmtable`, `unicharset`, `ambigs`, `dawg`, `params`,
`config`, `curlang`, `lm`, `wordbigram`, `indic`, `userpatterns`,
`userwords`) read by `TessdataManager` (`src/ccutil/tessdatamanager.cpp`).

### `TSV`
Tab-separated-value output format. `TessTsvRenderer`
(`include/tesseract/renderer.h:221`). Triggered by `tessedit_create_tsv=1`.
Most useful for layout-aware downstream tools because it includes
bounding-box coords.

### `UNICHARSET`
Class in `src/ccutil/unicharset.{h,cpp}`. Maps between `UNICHAR_ID` (int)
and the UTF-8 string for each character the model knows.

### `WERD_RES`
Internal data structure holding a recognized word's results
(`src/ccstruct/wordres.{h,cpp}`). Iterator methods like
`ResultIterator::Confidence` ultimately read from this.

---

## Appendix — PSM and OEM quick tables

| PSM | Name | Use case |
|---:|---|---|
| 0 | `PSM_OSD_ONLY` | OSD only, no OCR |
| 1 | `PSM_AUTO_OSD` | auto + OSD |
| 2 | `PSM_AUTO_ONLY` | segmentation only |
| 3 | `PSM_AUTO` | CLI default (no OSD) |
| 4 | `PSM_SINGLE_COLUMN` | one column |
| 5 | `PSM_SINGLE_BLOCK_VERT_TEXT` | vertical text block |
| 6 | `PSM_SINGLE_BLOCK` | library default |
| 7 | `PSM_SINGLE_LINE` | one line |
| 8 | `PSM_SINGLE_WORD` | one word |
| 9 | `PSM_CIRCLE_WORD` | circular word |
| 10 | `PSM_SINGLE_CHAR` | one char |
| 11 | `PSM_SPARSE_TEXT` | sparse text (no block layout) |
| 12 | `PSM_SPARSE_TEXT_OSD` | sparse + OSD |
| 13 | `PSM_RAW_LINE` | raw line (no word segmentation) |

| OEM | Name | Notes |
|---:|---|---|
| 0 | `OEM_TESSERACT_ONLY` | legacy only; deprecated since 5.x |
| 1 | `OEM_LSTM_ONLY` | 5.x default for `--oem 1` |
| 2 | `OEM_TESSERACT_LSTM_COMBINED` | LSTM with legacy fallback; deprecated |
| 3 | `OEM_DEFAULT` | select from language/config defaults |