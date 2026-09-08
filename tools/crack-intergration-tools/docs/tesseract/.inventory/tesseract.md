# Tesseract OCR — Source Inventory

> Inventory of `tools/crack-intergration-tools/source-projects/tesseract/`
> Verified by grep / ls / find on 2026-07-28. All file:line references are real.
> Absolute paths omit the leading `/home/leo/文档/android-crack/`; the project
> root used throughout is `tools/crack-intergration-tools/source-projects/tesseract/`
> (referred to below as `<repo>`).

---

## 1. Project basics

| Field | Value | Evidence |
|---|---|---|
| Name | Tesseract OCR | `README.md:25` (`This package contains an OCR engine`) |
| Version | **5.5.3** | `VERSION:1` (single line: `5.5.3`); echoed by `tesseract::TessBaseAPI::Version()` (`src/tesseract.cpp:101`) |
| Source-of-version | `VERSION` file (1 line) OR `git describe --abbrev=4` | `configure.ac:10` (`m4_esyscmd_s([test -d .git && git describe --abbrev=4 2>/dev/null || cat VERSION])`) |
| Languages | C++17/20 (`CMakeLists.txt:135` `set(CMAKE_CXX_STANDARD 17)`, upgraded to 20 if available, line 136-138); Java (Swing, see §9); Python (build scripts only, `generate_lut.py` in `src/lstm/`) | `CMakeLists.txt:135`, `src/lstm/generate_lut.py` |
| License | **Apache-2.0** | `README.md:7` badge + `LICENSE:1`; headers begin `// SPDX-License-Identifier: Apache-2.0` |
| Build systems | **CMake** (primary, `CMakeLists.txt`, 974 lines) + **GNU Autotools** (autoconf `configure.ac:1`, automake `Makefile.am` 60 KB, `autogen.sh`) | `CMakeLists.txt:1`, `configure.ac:1`, `Makefile.am:1` |
| Build-system tests | googletest under `unittest/third_party/googletest/` (vendored), enabled with `BUILD_TESTS=ON` | `CMakeLists.txt:876-883` |

### Entry points

| Artifact | File | Line | Note |
|---|---|---|---|
| **CLI binary `tesseract`** | `src/tesseract.cpp` | `main()` at line **855**, wraps `main1()` at line **650** | Wrapped in `try/catch` at lines 856-863 |
| **Library `libtesseract`** | All files listed in `cmake/SourceLists.cmake` (TESSERACT_SRC_API, ..._CCMAIN, ..._LSTM, etc.) compiled into single static/shared lib via `add_library(libtesseract ...)` | `CMakeLists.txt:735` | Outputs `libtesseract.a` / `libtesseract.so` (or `tesseract<ver>.dll` on Win) |
| CLI links library | `add_executable(tesseract src/tesseract.cpp)` then `target_link_libraries(tesseract libtesseract)` | `CMakeLists.txt:864-865` |  |

The library's "user-visible" entry is `TessBaseAPI` (class declared `include/tesseract/baseapi.h:76`), implemented in `src/api/baseapi.cpp` (`TessBaseAPI::Init` at line **300**, `TessBaseAPI::Recognize` at line **762**, etc.).

---

## 2. Top-level directory tree

Annotated from `ls <repo>` (without `tools/`, `apks/`, `crackings/`, `crackings/<type>/<Name>/project/`, `gui/`, `usages/`).

| Dir / file | Purpose |
|---|---|
| `CMakeLists.txt` | Primary build definition (974 lines); requires CMake >= 3.18 (`CMakeLists.txt:12`); defines `libtesseract` (line 735) and `tesseract` executable (line 864). |
| `Makefile.am` | Autotools build glue (60 KB) |
| `configure.ac` | Autoconf input (627 lines); requires autoconf 2.69 (line 8); runs `AC_INIT([tesseract], ...)` (line 9). |
| `autogen.sh` | Wrapper to bootstrap autotools |
| `VERSION` | Single line `5.5.3` |
| `README.md` | Project description, install/build/run instructions |
| `LICENSE` | Apache-2.0 full text |
| `INSTALL` | Generic GNU autotools install instructions |
| `INSTALL.GIT.md` | Git-submodule hint for leptonica |
| `ChangeLog` | Release notes |
| `AUTHORS` | Contributor list |
| `CITATIONS.bib` | BibTeX entries for citing Tesseract |
| `CONTRIBUTING.md` | Contribution rules |
| `SECURITY.md` | Vulnerability disclosure policy |
| `sw.cpp` | 12963-byte C++17 "single-header" wrapper |
| `tesseract.pc.in` / `tesseract.pc.cmake` | pkg-config template (autotools vs CMake) |
| **`src/`** | All C++ implementation (489 .cpp/.h files; see 2.b) |
| **`include/tesseract/`** | Public C++ headers (see 3) |
| **`java/`** | Java ScrollView Swing tool (see 9) |
| **`tessdata/`** | Configuration files + missing traineddata (see 8) |
| **`test/`** | **Empty directory** — reserved for legacy `make check` tests |
| **`unittest/`** | GoogleTest C++ unit tests (74+ files, see 6.f) |
| **`doc/`** | AsciiDoc man-pages (`tesseract.1.asc`, `lstmtraining.1.asc`, ...) + `Doxyfile` + `tesseract.natvis` (MSVC visualizers) |
| **`cmake/`** | CMake helper modules (`BuildFunctions.cmake`, `CheckFunctions.cmake`, `Configure.cmake`, `SourceGroups.cmake`, `SourceLists.cmake`, `BuildOptimizations.cmake`) + `templates/` (CMake package config) |
| **`m4/`** | Autoconf macros: `ax_check_compile_flag.m4`, `ax_split_version.m4` |
| **`snap/`** | Snapcraft package definition (`snapcraft.yaml`) |
| **`nsis/`** | Windows NSIS installer sources (`tesseract.nsi`, `build.sh`, `find_deps.py`, `winpath.cpp`) |
| **`.github/`** | GitHub metadata: `dependabot.yml`, `ISSUE_TEMPLATE/`, `workflows/` (CI), `copilot-instructions.md` |
| `.gitattributes`, `.gitignore`, `.gitmodules`, `.clang-format`, `.mailmap` | Repo metadata |
| **`scripts/`** | **NOT PRESENT at top level** (the prompt's tree listed this, but `ls` shows no such directory in this snapshot — build helpers live in `cmake/` instead) |

### 2.b `src/` sub-tree

Counts are files (`.cpp` + `.h`) in the module's top-level dir (from `find src/<m> -maxdepth 1 -type f \( -name "*.cpp" -o -name "*.h" \) | wc -l`).

| Module | Files | Purpose (1 line) |
|---|---|---|
| `src/api/` | **10** | Public-API façade (`baseapi.cpp`, `capi.cpp`) + renderer plugins (text, hOCR, PDF, ALTO, PAGE, TSV, BOX, LSTM-BOX, WORDSTR-BOX) |
| `src/arch/` | **15** | SIMD dispatch (AVX/AVX2/AVX512/FMA/SSE4.1/NEON/RVV dot-product and int-simd-matrix; `simddetect.cpp` for runtime detection) |
| `src/ccmain/` | **45** | Tesseract main controller (`Tesseract` class in `tesseractclass.{h,cpp}`), page segmentation (`pagesegmain.cpp`), orientation/script detection (`osdetect.{h,cpp}`), thresholder, output, paragraphs, equation-detect, ltr/mutable/result iterators |
| `src/ccstruct/` | **74** | Core data structures: `IMAGE`, `BLOB`, `WERD`, `ROW`, `BLOCK`, `POLY_BLOCK`, `PAGE_RES`, `WERD_RES`, blamer, font info, image read/write |
| `src/ccutil/` | **43** | Generic utilities: `Params`/`ParamsVectors` runtime config, `TessdataManager` (.traineddata reader), `UNICHARSET`, `UNICHAR`, `BIT_VECTOR`, `elst`/`ELISTIZE` macros, `tprintf`, `scanutils`, `ambigs`, error codes |
| `src/classify/` | **52** | Legacy feature extraction (`intfx.cpp`, `picofeat.cpp`, `mfoutline.cpp`, `outfeat.cpp`), prototype matching (`intmatcher.cpp`, `intproto.cpp`, `kdtree.cpp`, `normmatch.cpp`, `adaptmatch.cpp`, `shapeclassifier.cpp`) — gated by `DISABLED_LEGACY_ENGINE` |
| `src/cutil/` | **3** | Tiny old-list helpers (`oldlist.h`, `cutil.h`, `cutil.cpp`) |
| `src/dict/` | **14** | Dictionary system: `Dawg`, `Trie`, `Dict`, `Stopper`, `Hyphen`, `permdawg`, `dawg_cache` |
| `src/lstm/` | **36** | LSTM network engine: `Network`/`Series`/`Plumbing`/`Convolution`/`MaxPool`/`FullyConnected`/`LSTM`/`Reversed`/`Reconfig`/`ReCodeBeam`/`WeightMatrix`/`NetworkIO`/`Input`/`Parallel`/`StaticShape`/`StridedMap` + `LSTMRecognizer` (line recognizer) + `generate_lut.py` |
| `src/textord/` | **79** | Text-line ordering / page segmentation internals: `Textord::TextordPage`, `ColFinder`, `ColPartition{,Set,Grid}`, `LineFinder`, `TabFind`, `TableRecog`, `ImageFind`, `Makerow`, `Pitsync`, `Pithsync`, `TabVector`, `AlignedBlob`, `Baselinedetect`, `Blkocc`, `BlobGrid`, `Bbgrid`, `Fpchop`, `Edgblob`, `WordSeg` |
| `src/training/` | **19** | Standalone training executables (see 6.f) |
| `src/viewer/` | **6** | ScrollView viewer (`scrollview.cpp/.h`, `svmnode.cpp/.h`, `svutil.cpp/.h`) — linked into `libtesseract` for debugging GUI |
| `src/wordrec/` | **32** | Word recognizer (legacy): `Wordrec` class (`chop_word_main`, `SegSearch`, `InitialSegSearch`, `language_model`, `lm_consistency`, `lm_state`, `lm_pain_points`, `outlines`, `pieces`, `plotedges`, `tface`) |
| `src/svpaint.cpp` | — | Standalone paint tool using ScrollView |
| `src/tesseract.cpp` | — | CLI `main()` (see 4) |

---

## 3. Public API surface (`include/tesseract/`)

12 public headers; all `#include "export.h"` to pick up `TESS_API` macro.

### 3.a Header inventory

| Header | Main public symbols | Source |
|---|---|---|
| `baseapi.h` | `class TESS_API TessBaseAPI` (line **76**) | `include/tesseract/baseapi.h` |
| `capi.h` | C-API: `TessBaseAPICreate` (line 210), `TessBaseAPIRecognize` (line 362), `TessBaseAPIGetUTF8Text` (line 387), `TessBaseAPIProcessPages` (line 364), `TessBaseAPIGetIterator` (line 374), `TessBaseAPIInit1`–`Init5` (lines 248–276), `TessTextRendererCreate` (161), etc. | `include/tesseract/capi.h` |
| `publictypes.h` | `enum OcrEngineMode { OEM_TESSERACT_ONLY, OEM_LSTM_ONLY, OEM_TESSERACT_LSTM_COMBINED, OEM_DEFAULT, OEM_COUNT }` (line 263); `enum PageSegMode { PSM_OSD_ONLY=0, PSM_AUTO_OSD=1, PSM_AUTO_ONLY=2, PSM_AUTO=3, PSM_SINGLE_COLUMN=4, PSM_SINGLE_BLOCK_VERT_TEXT=5, PSM_SINGLE_BLOCK=6, PSM_SINGLE_LINE=7, PSM_SINGLE_WORD=8, PSM_CIRCLE_WORD=9, PSM_SINGLE_CHAR=10, PSM_SPARSE_TEXT=11, PSM_SPARSE_TEXT_OSD=12, PSM_RAW_LINE=13, PSM_COUNT }` (line 157); `enum PageIteratorLevel { RIL_BLOCK, RIL_PARA, RIL_TEXTLINE, RIL_WORD, RIL_SYMBOL }` (line 214); `enum PolyBlockType` (line 51); `enum Orientation`, `enum WritingDirection`, `enum TextlineOrder`, `enum ParagraphJustification` | `include/tesseract/publictypes.h` |
| `pageiterator.h` | `class TESS_API PageIterator` (line 50): constructors at 66/77, `Begin()` (89), `RestartParagraph()` (96), `RestartRow()` (109), `Next(level)` (122), `IsAtBeginningOf(level)` (137), `IsAtFinalElement(lvl,el)` (155), `Cmp(other)` (164), `SetBoundingBoxComponents(...)` (188), `BoundingBox(level, l,t,r,b)` (203), `Baseline(...)` (261), `RowAttributes(...)` (265), `Orientation(...)` (276), `ParagraphInfo(...)` (309) | `include/tesseract/pageiterator.h` |
| `resultiterator.h` | `class TESS_API ResultIterator : public LTRResultIterator` (line 32): adds `GetUTF8Text(level)` etc. | `include/tesseract/resultiterator.h` |
| `ltrresultiterator.h` | `class TESS_API LTRResultIterator : public PageIterator` (line 45); `GetUTF8Text(level)` (82), `Confidence(level)` (92), `WordFontAttributes(...)` (104), `WordRecognitionLanguage()` (111), `WordIsFromDictionary()` (117), `WordIsNumeric()` (123), `WordTruthUTF8Text()` (149), `WordLattice(...)` (157), `SymbolIsSuperscript/Subscript/Dropcap` (164/168/172); inner `class TESS_API ChoiceIterator` (line 180): `Next()` (190), `GetUTF8Text()` (198), `Confidence()` (206) | `include/tesseract/ltrresultiterator.h` |
| `renderer.h` | Abstract `class TESS_API TessResultRenderer` (line 47) + 10 concrete subclasses — see 11 | `include/tesseract/renderer.h` |
| `ocrclass.h` | `struct EANYCODE_CHAR` (line 59), `using CANCEL_FUNC`, `PROGRESS_FUNC`, `PROGRESS_FUNC2` (lines 98-100), `class ETEXT_DESC` (line 102) with `set_deadline_msecs()` (128) and `deadline_exceeded()` (136) | `include/tesseract/ocrclass.h` |
| `osdetect.h` | `struct OSBestResult` (line 38), `struct OSResults` (line 47), `class OrientationDetector` (line 83), `class ScriptDetector` (line 95), `int orientation_and_script_detection(...)` (line 116), `int os_detect(...)` (line 119), `int os_detect_blobs(...)` (line 122), `bool os_detect_blob(...)` (line 126) | `include/tesseract/osdetect.h` |
| `unichar.h` | `class TESS_API UNICHAR` (line 55): `first_uni()`, `utf8_len()`, `utf8()`, `utf8_str()`, `static int utf8_step(const char *)` | `include/tesseract/unichar.h` |
| `version.h.in` | Generated `TESSERACT_MAJOR_VERSION`/`MINOR`/`MICRO` macros + `TESSERACT_VERSION_STR` template (`@PACKAGE_VERSION@` placeholder; line 30). Generated to `${CMAKE_CURRENT_BINARY_DIR}/include/tesseract/version.h` per `CMakeLists.txt:540-541`. | `include/tesseract/version.h.in` |
| `export.h` | `TESS_API` visibility macro: dllexport/dllimport on Win, `__attribute__((visibility("default")))` else when `TESS_EXPORTS`/`TESS_IMPORTS` defined | `include/tesseract/export.h` |

### 3.b `TessBaseAPI` public methods (verbatim from `include/tesseract/baseapi.h`)

All methods listed in declaration order; line numbers refer to the header.

| L# | Signature |
|---:|-----------|
| 78  | `TessBaseAPI();` |
| 79  | `virtual ~TessBaseAPI();` |
| 87  | `static const char *Version();` |
| 93  | `void SetInputName(const char *name);` |
| 101 | `const char *GetInputName();` |
| 103 | `void SetInputImage(Pix *pix);` |
| 104 | `Pix *GetInputImage();` |
| 105 | `int GetSourceYResolution();` |
| 106 | `const char *GetDatapath();` |
| 109 | `void SetOutputName(const char *name);` |
| 124 | `bool SetVariable(const char *name, const char *value);` |
| 125 | `bool SetDebugVariable(const char *name, const char *value);` |
| 131 | `bool GetIntVariable(const char *name, int *value) const;` |
| 132 | `bool GetBoolVariable(const char *name, bool *value) const;` |
| 133 | `bool GetDoubleVariable(const char *name, double *value) const;` |
| 139 | `const char *GetStringVariable(const char *name) const;` |
| 146 | `void PrintFontsTable(FILE *fp) const;` (legacy-only) |
| 153 | `void PrintVariables(FILE *fp) const;` |
| 158 | `bool GetVariableAsString(const char *name, std::string *val) const;` |
| 197 | `int Init(const char *datapath, const char *language, OcrEngineMode mode, char **configs, int configs_size, const std::vector<std::string> *vars_vec, const std::vector<std::string> *vars_values, bool set_only_non_debug_params);` |
| 202 | `int Init(const char *datapath, const char *language, OcrEngineMode oem);` (inline convenience) |
| 205 | `int Init(const char *datapath, const char *language);` (inline, `OEM_DEFAULT`) |
| 211 | `int Init(const char *data, int data_size, const char *language, OcrEngineMode mode, char **configs, int configs_size, const std::vector<std::string> *vars_vec, const std::vector<std::string> *vars_values, bool set_only_non_debug_params, FileReader reader);` |
| 225 | `const char *GetInitLanguagesAsString() const;` |
| 232 | `void GetLoadedLanguagesAsVector(std::vector<std::string> *langs) const;` |
| 237 | `void GetAvailableLanguagesAsVector(std::vector<std::string> *langs) const;` |
| 243 | `void InitForAnalysePage();` |
| 251 | `void ReadConfigFile(const char *filename);` |
| 253 | `void ReadDebugConfigFile(const char *filename);` |
| 260 | `void SetPageSegMode(PageSegMode mode);` |
| 263 | `PageSegMode GetPageSegMode() const;` |
| 282 | `char *TesseractRect(const unsigned char *imagedata, int bytes_per_pixel, int bytes_per_line, int left, int top, int width, int height);` |
| 290 | `void ClearAdaptiveClassifier();` |
| 307 | `void SetImage(const unsigned char *imagedata, int width, int height, int bytes_per_pixel, int bytes_per_line);` |
| 318 | `void SetImage(Pix *pix);` |
| 324 | `void SetSourceResolution(int ppi);` |
| 331 | `void SetRectangle(int left, int top, int width, int height);` |
| 338 | `Pix *GetThresholdedImage();` |
| 343 | `float GetGradient();` |
| 350 | `Boxa *GetRegions(Pixa **pixa);` |
| 363 | `Boxa *GetTextlines(bool raw_image, int raw_padding, Pixa **pixa, int **blockids, int **paraids);` |
| 368 | `Boxa *GetTextlines(Pixa **pixa, int **blockids);` (inline) |
| 380 | `Boxa *GetStrips(Pixa **pixa, int **blockids);` |
| 387 | `Boxa *GetWords(Pixa **pixa);` |
| 397 | `Boxa *GetConnectedComponents(Pixa **cc);` |
| 411 | `Boxa *GetComponentImages(PageIteratorLevel level, bool text_only, bool raw_image, int raw_padding, Pixa **pixa, int **blockids, int **paraids);` |
| 415 | `Boxa *GetComponentImages(const PageIteratorLevel level, const bool text_only, Pixa **pixa, int **blockids);` (inline) |
| 427 | `int GetThresholdedImageScaleFactor() const;` |
| 444 | `PageIterator *AnalyseLayout();` |
| 445 | `PageIterator *AnalyseLayout(bool merge_similar_words);` |
| 453 | `int Recognize(ETEXT_DESC *monitor);` |
| 482 | `bool ProcessPages(const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` |
| 485 | `bool ProcessPagesInternal(const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` |
| 497 | `bool ProcessPage(Pix *pix, int page_index, const char *filename, const char *retry_config, int timeout_millisec, TessResultRenderer *renderer);` |
| 509 | `ResultIterator *GetIterator();` |
| 519 | `MutableIterator *GetMutableIterator();` |
| 525 | `char *GetUTF8Text();` |
| 536 | `char *GetHOCRText(ETEXT_DESC *monitor, int page_number);` |
| 544 | `char *GetHOCRText(int page_number);` |
| 550 | `char *GetAltoText(ETEXT_DESC *monitor, int page_number);` |
| 556 | `char *GetAltoText(int page_number);` |
| 562 | `char *GetPAGEText(ETEXT_DESC *monitor, int page_number);` |
| 568 | `char *GetPAGEText(int page_number);` |
| 575 | `char *GetTSVText(int page_number);` |
| 583 | `char *GetLSTMBoxText(int page_number);` |
| 592 | `char *GetBoxText(int page_number);` |
| 600 | `char *GetWordStrBoxText(int page_number);` |
| 607 | `char *GetUNLVText();` |
| 618 | `bool DetectOrientationScript(int *orient_deg, float *orient_conf, const char **script_name, float *script_conf);` |
| 626 | `char *GetOsdText(int page_number);` |
| 629 | `int MeanTextConf();` |
| 636 | `int *AllWordConfidences();` |
| 649 | `bool AdaptToWordStr(PageSegMode mode, const char *wordstr);` (legacy) |
| 658 | `void Clear();` |
| 666 | `void End();` |
| 675 | `static void ClearPersistentCache();` |
| 683 | `int IsValidWord(const char *word) const;` |
| 685 | `bool IsValidCharacter(const char *utf8_character) const;` |
| 687 | `bool GetTextDirection(int *out_offset, float *out_slope);` |
| 690 | `void SetDictFunc(DictFunc f);` |
| 695 | `void SetProbabilityInContextFunc(ProbabilityInContextFunc f);` |
| 701 | `bool DetectOS(OSResults *);` |
| 707 | `void GetBlockTextOrientations(int **block_orientation, bool **vertical_writing);` |
| 711 | `const char *GetUnichar(int unichar_id) const;` |
| 714 | `const Dawg *GetDawg(int i) const;` |
| 717 | `int NumDawgs() const;` |
| 719 | `Tesseract *tesseract() const;` |
| 723 | `OcrEngineMode oem() const;` |
| 727 | `void set_min_orientation_margin(double margin);` |

Free helper: `std::string HOcrEscape(const char *text);` at line **816**.

---

## 4. CLI tool

**Single source file**: `src/tesseract.cpp` (864 lines).

| Symbol | L# | Role |
|---|---:|---|
| `static void PrintVersionInfo()` | 98 | Banner: prints `TessBaseAPI::Version()`, leptonica version, SIMD capabilities, OpenMP, libarchive, libcurl |
| `static void PrintHelpForPSM()` | 155 | PSM help table (matches `enum PageSegMode`) |
| `static void PrintHelpForOEM()` | 183 | OEM help table (matches `enum OcrEngineMode`) |
| `static void PrintHelpExtra(...)` | 194 | Full usage + all options |
| `static void PrintHelpMessage(...)` | 255 | Short usage |
| `static void PrintLangsList(...)` | 275 | `--list-langs` output |
| `static void FixPageSegMode(...)` | 300 | Coerces `PSM_SINGLE_BLOCK` (default in lib) to `PSM_AUTO` for the CLI |
| `static bool ParseArgs(...)` | 366 | argv scanner — populates lang/image/outputbase/datapath/dpi/vars/pagesegmode/enginemode |
| `static void PreloadRenderers(...)` | 503 | Constructs the renderer chain (HOCR / ALTO / PAGE / TSV / PDF / UNLV / LSTMBox / BoxText / WordStrBox / Text) based on `tessedit_create_*` variables |
| `static int main1(...)` | 650 | Real work: parse args → construct `TessBaseAPI api;` → `api.Init(...)` → fix PSM → set DPI → resolve mode → `PreloadRenderers(...)` → `api.ProcessPages(image, nullptr, 0, renderers[0].get())` (line 845) |
| `int main(int argc, char **argv)` | 855 | try/catch wrapper around `main1()` |

### Argument surface (verified from `PrintHelpExtra`, lines 194-253)

| Flag | Effect |
|---|---|
| `--tessdata-dir PATH` | Sets tessdata root |
| `--user-words PATH`, `--user-patterns PATH` | Custom dictionaries |
| `--dpi VALUE` | Source resolution hint |
| `--loglevel LEVEL` | ALL/TRACE/DEBUG/INFO/WARN/ERROR/FATAL/OFF |
| `-l LANG[+LANG]` | Languages (e.g. `eng`, `eng+deu`) |
| `-c VAR=VALUE` | Inline config (repeatable) |
| `--psm PSM\|NUM` | One of the 14 `PageSegMode` values |
| `--oem OEM\|NUM` | One of the 4 `OcrEngineMode` values (legacy only) |
| `--list-langs` | Enumerate installed languages |
| `--print-parameters` / `--print-fonts-table` | Dump config |
| `--help`, `--help-extra`, `--help-psm`, `--help-oem`, `--version` | Self-doc |
| `[configfile...]` | Trailing config files (read after `-c`) |

### Output formats (driven by `tessedit_create_*` flags, see `PreloadRenderers` lines 510-634)

| Format | Renderer class | Trigger | File extension |
|---|---|---|---|
| Plain text | `TessTextRenderer` | default (or `tessedit_create_txt=1`) | `.txt` |
| hOCR | `TessHOcrRenderer` | `tessedit_create_hocr=1` | `.hocr` |
| ALTO XML | `TessAltoRenderer` | `tessedit_create_alto=1` | `.xml` |
| PAGE XML | `TessPAGERenderer` | `tessedit_create_page_xml=1` | `.xml` |
| TSV | `TessTsvRenderer` | `tessedit_create_tsv=1` | `.tsv` |
| Searchable PDF | `TessPDFRenderer` | `tessedit_create_pdf=1` | `.pdf` |
| UNLV | `TessUnlvRenderer` | `tessedit_write_unlv=1` | `.unlv` |
| LSTM Box | `TessLSTMBoxRenderer` | `tessedit_create_lstmbox=1` | `.box` |
| Box | `TessBoxTextRenderer` | `tessedit_create_boxfile=1` | `.box` |
| WordStr Box | `TessWordStrBoxRenderer` | `tessedit_create_wordstrbox=1` | `.box` |
| OSD | `TessOsdRenderer` | `PSM_OSD_ONLY` only | `.osd` |

### Why `src/api/` is the program-vs-frontend split

`src/api/` (10 files, defined at `cmake/SourceLists.cmake:5-15`) is intentionally
isolated from the rest of `src/`. It exposes **only** the user-visible façade:

- `baseapi.cpp` — `TessBaseAPI` class implementation (the entire public C++ API)
- `capi.cpp` — `extern "C"` wrappers for every `TessBaseAPI` method (`TessBaseAPICreate`, ...)
- `renderer.cpp` + 8 `*renderer.cpp` files — plug-in output formatters

`CMakeLists.txt:864-865` shows the **program** (`tesseract` exe = `src/tesseract.cpp`)
calling into the **library** (`libtesseract` = all of `src/`). The control callback
separation is explicit in `baseapi.cpp` via the `ETEXT_DESC` progress/cancel hooks
(`include/tesseract/ocrclass.h:102-156`).

---

## 5. Recognition pipeline

When `TessBaseAPI::Recognize(ETEXT_DESC *)` runs (`src/api/baseapi.cpp:762-844`),
the actual work happens in 7 stages backed by these classes/functions:

| Stage | Module / class | Key entry points | File:line |
|---|---|---|---|
| **1. Image loading & thresholding** | `cutil`/`ccstruct` (Leptonica Pix -> binary) | `TessBaseAPI::FindLines()` -> `TessBaseAPI::Threshold(Pix **)` -> `ImageThresholder::ThresholdToPix` (Otsu/Sauvola) | `src/api/baseapi.cpp:2070` (`FindLines`), `1995` (`Threshold`), `src/ccmain/thresholder.cpp:284` (`ThresholdToPix`), `182` (`Threshold`) |
| **2. Component finding** | `textord` | `Textord::find_components(pix, blocks, to_blocks)` | called at `src/ccmain/pagesegmain.cpp:309` |
| **3. Layout / page segmentation** | `textord` + `ccmain` | `Tesseract::SetupPageSegAndDetectOrientation(...)` -> `ColumnFinder::SetupAndFilterNoise` -> `ColumnFinder::FindBlocks` -> `Tesseract::AutoPageSeg(...)` -> `Tesseract::SegmentPage(...)` | `src/ccmain/pagesegmain.cpp:272` (SetupPageSegAndDetectOrientation), `201` (AutoPageSeg), `101` (SegmentPage); `src/textord/colfind.cpp:FindBlocks` (declared `colfind.h`) |
| **4. Orientation & script detection (OSD)** | `ccmain` | `os_detect_blobs(allowed_scripts, &osd_blobs, osr, osd_tess)` (`osdetect.h:122`) | `src/ccmain/pagesegmain.cpp:366` |
| **5. Word recognition** (legacy + LSTM dispatch) | `ccmain` + `wordrec` + `lstm` | `Tesseract::classify_word_and_language` (pass1/pass2 selection via `Tesseract::classify_word_pass1` / `classify_word_pass2`); legacy: `Wordrec::chop_word_main` (`src/wordrec/chopper.cpp:385`) -> `Wordrec::SegSearch` (`segsearch.cpp:33`); LSTM: `Tesseract::LSTMRecognizeWord` (`src/ccmain/linerec.cpp:229`) -> `LSTMRecognizer::RecognizeLine` (`src/lstm/lstmrecognizer.cpp:247` / full version `:320`) | see column |
| **6. Language model / dictionary** | `dict` + `wordrec` | `Tesseract::dictionary_correction_pass` (`src/ccmain/tesseractclass.cpp:2064`); `Dict::probability_in_context_` / `LanguageModel::UpdateBestChoice` (`src/wordrec/language_model.cpp:1235`); `Dict::is_valid_word`; `Dawg`/`Trie`/`Stopper`/`permdawg` in `src/dict/` | |
| **7. Output / rendering** | `ccmain` + `api` (renderers) | `Tesseract::output_pass` (`src/ccmain/output.cpp:39`); each `TessBaseAPI::Get*Text` triggers `renderer->AddImage(this)` which writes the doc via `TessResultRenderer::AddImage` -> `AddImageHandler` | `src/api/renderer.cpp:88`; renderers in `src/api/{hocr,pdf,alto,page,tsv}renderer.cpp` |

The legacy vs LSTM split is decided by `OEM` (selected at `Init` time, stored in
`tesseract_->AnyLSTMLang()` and `tesseract_->AnyTessLang()`). `TessBaseAPI::Recognize`
constructs the `PAGE_RES` (line 786) which embeds either or both engines.

---

## 6. Operation chains (>=6 representative flows)

### (a) CLI: `tesseract image.png out --oem 1 -l eng`

| # | Call | File:line |
|---:|---|---|
| 1 | `main(int argc, char **argv)` | `src/tesseract.cpp:855` |
| 2 | -> `main1(argc, argv)` | `src/tesseract.cpp:650` |
| 3 | `ParseArgs(...)` parses `-l eng`, `--oem 1`, positional `image.png`, `out` | `src/tesseract.cpp:366` |
| 4 | `TessBaseAPI api;` | `src/tesseract.cpp:714` |
| 5 | `api.Init(datapath, "eng", OEM_LSTM_ONLY, configs, argc-arg_i, ...)` | `src/tesseract.cpp:718`; impl `src/api/baseapi.cpp:300` |
| 6 | `FixPageSegMode(api, pagesegmode)` (defaults to `PSM_AUTO`) | `src/tesseract.cpp:752` (`FixPageSegMode` at line 300) |
| 7 | `PreloadRenderers(api, renderers, pagesegmode, "out")` -> constructs `TessTextRenderer("out")` | `src/tesseract.cpp:836` (`PreloadRenderers` at line 503) |
| 8 | `api.ProcessPages("image.png", nullptr, 0, renderers[0].get())` | `src/tesseract.cpp:845`; impl `src/api/baseapi.cpp:999` -> `ProcessPagesInternal` (line 1033) -> autodetect PNG via `findFileFormat` (line 1142) -> `ProcessPage(pix, 0, "image.png", ..., renderer)` (line 1184) |
| 9 | `ProcessPage` -> `SetImage(pix)` -> `Recognize(nullptr)` | `src/api/baseapi.cpp:1196` (ProcessPage), `:528` (SetImage), `:762` (Recognize) |
| 10 | `Recognize` -> `FindLines()` -> `tesseract_->recog_all_words(...)` -> LSTM line recognizer path | `src/api/baseapi.cpp:762` (Recognize), `:2070` (FindLines) |
| 11 | `renderer->AddImage(this)` -> `TessTextRenderer::AddImageHandler` -> writes `out.txt` | `src/api/renderer.cpp:139` |

### (b) Library: `TessBaseAPI::TesseractRect(...)` for pre-segmented ROI

| # | Call | File:line |
|---:|---|---|
| 1 | `TessBaseAPI api;` | (caller code) |
| 2 | `api.Init(datapath, "eng")` | `src/api/baseapi.cpp:300` |
| 3 | `api.SetVariable("tessedit_pageseg_mode", "8")` (or other PSM_SINGLE_WORD) | `src/api/baseapi.cpp:211` |
| 4 | `char *text = api.TesseractRect(imagedata, bpp, bpl, left, top, width, height);` | declared `include/tesseract/baseapi.h:282`; impl in `src/api/baseapi.cpp` (internally calls `SetImage` + `SetRectangle` + `Recognize` + `GetUTF8Text`) |
| 5 | `delete[] text;` | header doc at `include/tesseract/baseapi.h:524` |

### (c) LSTM-only vs legacy word recognition

| Step | LSTM path | Legacy path |
|---|---|---|
| Build | OEM `1` (`OEM_LSTM_ONLY`) -> `LSTMRecognizer` constructed in `TessBaseAPI::Init` -> `tesseract_->init_lstm_components` -> `lstm_recognizer_ = new LSTMRecognizer(...)` | OEM `0` (`OEM_TESSERACT_ONLY`) or OEM `2` (combined) |
| Per word | `Tesseract::LSTMRecognizeWord(BLOCK, ROW, WERD_RES, ...)` -> `lstm_recognizer_->RecognizeLine(*im_data, threshold, ...)` | `Tesseract::recog_word(WERD_RES *)` -> `Wordrec::chop_word_main(WERD_RES *)` -> `Wordrec::SegSearch(...)` / `InitialSegSearch` |
| Output labels | `LSTMRecognizer::DecodeLabels` / `DecodeSingleLabel` | `BestChoiceBundle` / `WERD_CHOICE` ratings |
| Source | `src/lstm/lstmrecognizer.cpp:247`/`320` (RecognizeLine); `src/ccmain/linerec.cpp:229` (Tesseract::LSTMRecognizeWord) | `src/ccmain/tfacepp.cpp:37` (recog_word); `src/wordrec/chopper.cpp:385` (chop_word_main); `src/wordrec/segsearch.cpp:33` (SegSearch) |

### (d) Page iteration: `TessBaseAPI::GetIterator() -> PageIterator`

| # | Call | File:line |
|---:|---|---|
| 1 | `ResultIterator *it = api.GetIterator();` | `src/api/baseapi.cpp:1280` |
| 2 | Loop: `while (it->Next(RIL_WORD)) { ... }` | `include/tesseract/pageiterator.h:122` |
| 3 | `it->BoundingBox(RIL_WORD, &l, &t, &r, &b);` | `include/tesseract/pageiterator.h:203` |
| 4 | `char *txt = it->GetUTF8Text(RIL_WORD);` | `include/tesseract/ltrresultiterator.h:82` |
| 5 | `float conf = it->Confidence(RIL_WORD);` | `include/tesseract/ltrresultiterator.h:92` |
| 6 | `delete it;` | (caller) |
| 7 | `api.End();` (frees LSTM dict caches via `ClearPersistentCache` if needed) | `src/api/baseapi.cpp:1861` |

### (e) Multi-page TIFF

| # | Call | File:line |
|---:|---|---|
| 1 | `api.ProcessPages("scan.tif", nullptr, 0, renderer)` | `src/api/baseapi.cpp:999` |
| 2 | `ProcessPagesInternal` autodetects TIFF via `findFileFormat` | `src/api/baseapi.cpp:1142` |
| 3 | `ProcessPagesMultipageTiff(data, size, filename, ...)` | `src/api/baseapi.cpp:958` |
| 4 | Loops pages; for each `SetImage` + `Recognize` + `renderer->AddImage(this)` | `src/api/baseapi.cpp:1196` (`ProcessPage`) |

### (f) Training a new language

| # | Step | Tool | Entry file:line |
|---:|---|---|---|
| 1 | Extract character set from `.box` files | `unicharset_extractor` | `src/training/unicharset_extractor.cpp:103` |
| 2 | (Legacy) shape clustering | `shapeclustering` | `src/training/shapeclustering.cpp:44` |
| 3 | (Legacy) train character proto/features | `mftraining` | `src/training/mftraining.cpp:193` |
| 4 | (Legacy) train character normalization | `cntraining` | `src/training/cntraining.cpp:103` |
| 5 | Wordlist -> DAWG | `wordlist2dawg` | `src/training/wordlist2dawg.cpp:33` |
| 6 | DAWG -> reverse wordlist (for stopper) | `dawg2wordlist` | `src/training/dawg2wordlist.cpp:71` |
| 7 | (LSTM) train LSTM network | `lstmtraining` | `src/training/lstmtraining.cpp:76` |
| 8 | (LSTM) evaluate LSTM | `lstmeval` | `src/training/lstmeval.cpp:32` |
| 9 | Merge unicharsets | `merge_unicharsets` | `src/training/merge_unicharsets.cpp:22` |
| 10 | Set unicharset properties (RTL/BiDi) | `set_unicharset_properties` | `src/training/set_unicharset_properties.cpp:25` |
| 11 | **Combine all into one `eng.traineddata`** | `combine_tessdata` | `src/training/combine_tessdata.cpp:117` |
| 12 | Render training text to image | `text2image` | `src/training/text2image.cpp:713` |
| 13 | (Optional) combine lang model | `combine_lang_model` | `src/training/combine_lang_model.cpp:42` |
| 14 | (Optional) emit ambiguity tables | `ambiguous_words` | `src/training/ambiguous_words.cpp:30` |
| 15 | (Optional) batch classifier test | `classifier_tester` | `src/training/classifier_tester.cpp:100` |

**Unit-test surface** (used to drive the libraries, not a separate tool): 74 test
files under `unittest/` including `baseapi_test.cc`, `capiexample_test.cc`,
`apiexample_test.cc`, `lstm_test.cc`, `lstmtrainer_test.cc`,
`validator_test.cc`, `loadlang_test.cc`. Built only when
`-DBUILD_TESTS=ON` (`CMakeLists.txt:101`, `:876-883`).

### (g) Java Swing ScrollView (offline viewer of `.box` files)

| # | Class | File |
|---:|---|---|
| 1 | `com.google.scrollview.ScrollView` — TCP server on port 8461 (`SERVER_PORT = 8461`, line 35) | `java/com/google/scrollview/ScrollView.java:32` |
| 2 | `com.google.scrollview.ui.SVWindow` — main window; imports `javax.swing.JFrame` (line 40), `java.awt.*` (lines 29-36), `org.piccolo2d.*` | `java/com/google/scrollview/ui/SVWindow.java:1-30` |
| 3 | `com.google.scrollview.events.{SVEvent,SVEventHandler,SVEventType}` — IPC structs (one per C `scrollview.h` message type) | `java/com/google/scrollview/events/SVEvent.java:1-20` |
| 4 | Renderer of `.box` files via `com.google.scrollview.ui.SVMenuBar`, `SVPopupMenu`, `SVCheckboxMenuItem`, `SVEmptyMenuItem`, `SVMenuItem`, `SVSubMenuItem`, `SVImageHandler` | `java/com/google/scrollview/ui/*.java` |

This is the **only** Java in the project. It is **not** a JNI bridge; it talks
to the C++ `scrollview` server over TCP (the corresponding server is
`src/viewer/scrollview.cpp`, included in `libtesseract`).

---

## 7. Dependencies

### 7.a Autoconf (`configure.ac`)

| Dep | Required? | Configuration | Evidence |
|---|---|---|---|
| **Leptonica >= 1.74** | **REQUIRED** (fatal if missing) | `PKG_CHECK_MODULES([LEPTONICA], [lept >= 1.74], ...)` | `configure.ac:487-492` |
| pthread | required | `AC_SEARCH_LIBS([pthread_create], [pthread])` | `configure.ac:426` |
| libarchive | optional (default=check) | `PKG_CHECK_MODULES([libarchive], [libarchive], ...)` | `configure.ac:494-507` |
| libcurl | optional (default=check) | `PKG_CHECK_MODULES([libcurl], [libcurl], ...)` | `configure.ac:473-485` |
| **ICU 52.1** (`icu-uc`, `icu-i18n`) | **required for training tools only** (warns + disables training if missing) | `PKG_CHECK_MODULES([ICU_UC], [icu-uc >= 52.1]...)` + `ICU_I18N` | `configure.ac:512-519` |
| pango >= 1.38.0 | required for training | `PKG_CHECK_MODULES([pango], [pango >= 1.38.0]...)` | `configure.ac:522-528` |
| cairo | required for training | `PKG_CHECK_MODULES([cairo], [cairo]...)` | `configure.ac:531-536` |
| pangocairo, pangoft2 | optional | `PKG_CHECK_MODULES(...)` | `configure.ac:538-539` |
| libtiff (header `tiffio.h`) | optional (auto-detected) | `AC_CHECK_HEADERS([tiffio.h], ...)` | `configure.ac:283` |
| Apple Accelerate framework | macOS only | `MY_CHECK_FRAMEWORK([Accelerate])` | `configure.ac:317-321` |
| asciidoctor | optional (for man pages) | `AC_CHECK_PROG([have_asciidoctor], ...)` | `configure.ac:449` |
| SIMD: AVX/AVX2/AVX512F/FMA/SSE4.1/NEON/RVV | detected at configure | `AX_CHECK_COMPILE_FLAG` + `host_cpu` dispatch | `configure.ac:136-200` |

### 7.b CMake (`CMakeLists.txt`)

| Dep | Required? | CMake call | Evidence |
|---|---|---|---|
| **Leptonica >= 1.74** | **REQUIRED (fatal)** | `find_package(Leptonica ${MINIMUM_LEPTONICA_VERSION} CONFIG)` with fallback to `pkg_check_modules(Leptonica lept>=${MINIMUM_LEPTONICA_VERSION})` | `CMakeLists.txt:445-455`; `set(MINIMUM_LEPTONICA_VERSION 1.74)` line 70 |
| Leptonica TIFF support | detection | `check_leptonica_tiff_support()`; auto-disables `TIFF` if leptonica lacks it | `CMakeLists.txt:457-463` |
| **libtiff** | optional (`-DDISABLE_TIFF=ON` to force off) | `find_package(TIFF)` + `pkg_check_modules(TIFF libtiff-4)` | `CMakeLists.txt:470-479` |
| **libarchive** | optional (`-DDISABLE_ARCHIVE=ON`) | `find_package(LibArchive)` | `CMakeLists.txt:484-493` |
| **libcurl** | optional (`-DDISABLE_CURL=ON`) | `find_package(CURL)` | `CMakeLists.txt:498-507` |
| **CpuFeaturesNdkCompat** | required only on Android | `find_package(CpuFeaturesNdkCompat REQUIRED)` | `CMakeLists.txt:853-857` |
| **OpenMP** | optional (`-DOPENMP_BUILD=ON`) | `find_package(OpenMP)` | `CMakeLists.txt:91`, `:338` |
| pthread | auto on UNIX | `${LIB_pthread}` | `CMakeLists.txt:378-380` |
| Ws2_32 | auto on Windows | `${LIB_Ws2_32}` | `CMakeLists.txt:382` |
| SIMD via build options | — | `ENABLE_NATIVE`, `DISABLED_LEGACY_ENGINE`, `FAST_FLOAT` (default ON), `ENABLE_LTO`, `BUILD_TRAINING_TOOLS` (default ON), `BUILD_TESTS` (default OFF), `USE_SYSTEM_ICU`, `GRAPHICS_DISABLED`, `INSTALL_CONFIGS` (default ON) | `CMakeLists.txt:91-112` |

### 7.c Notes

- **Leptonica is the only hard dep.** PNG/JPEG/TIFF/ZLIB support rides on
  whatever Leptonica was built with (the README explicitly recommends
  building Leptonica with zlib+png+tiff support — `README.md:122-126`).
- **ICU/pango/cairo** are needed only for training-tool builds (`configure.ac:512-536`
  flips `AM_CONDITIONAL([ENABLE_TRAINING], false)` if missing).
- **libarchive** is needed only for the compressed-traineddata support
  (`HAVE_LIBARCHIVE` gates `.traineddata` decompression in
  `src/ccutil/tessdatamanager.cpp`).
- **libcurl** is needed only for the `tesseract URL` remote-image path
  (`src/api/baseapi.cpp:1056-1128`).

---

## 8. Tessdata status

Contents of `<repo>/tessdata/` (verbatim `find`):

| Path | Type | Notes |
|---|---|---|
| `Makefile.am` | Autotools | install rules for the subtree |
| `configs/` | dir | 24 param files: `alto`, `ambigs.train`, `api_config`, `bazaar`, `bigram`, `box.train`, `box.train.stderr`, `digits`, `get.images`, `hocr`, `inter`, `kannada`, `linebox`, `logfile`, `lstmbox`, `lstmdebug`, `lstm.train`, `makebox`, `page`, `pdf`, `quiet`, `rebox`, `strokewidth`, `tsv`, `txt`, `unlv`, `wordstrbox` (each is a 1-2 line `VAR VALUE` file used by `tessedit_*` parameters) |
| `tessconfigs/` | dir | 6 legacy config files: `batch`, `batch.nochop`, `matdemo`, `msdemo`, `nobatch`, `segdemo` + `Makefile.am` |
| `eng.user-words` | text | Example user word list (English) — NOT a model |
| `eng.user-patterns` | text | Example user regex patterns (English) — NOT a model |
| `pdf.ttf` | font | Subset TTF bundled for `TessPDFRenderer` (`tessdata/pdf.ttf`; consumed by `src/api/pdfrenderer.cpp` because the PDF renderer embeds a custom font for invisible-text PDF) |

### **CRITICAL GAP**: no `.traineddata` files

```
$ find tessdata -name '*.traineddata' -o -name '*.traineddata.gz'
(no output)
```

The `tessdata/` directory ships **only** configuration templates. Running
`tesseract image.png out -l eng` against this checkout will fail with:

```
Error, could not create TXT output file: ...
Could not initialize tesseract.
```

because `TessBaseAPI::Init` cannot find `eng.traineddata` in the
`--tessdata-dir`. Models are hosted in a **separate repo**:
<https://github.com/tesseract-ocr/tessdata> (`eng.traineddata` ~ 22 MB,
`chi_sim.traineddata` ~ 26 MB, `osd.traineddata` ~ 10 MB; "fast" variants
in <https://github.com/tesseract-ocr/tessdata_fast>).

Workarounds:
- `wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata`
- or build from `tessdata_fast` / `tessdata_best` repos
- or use the `TESSDATA_PREFIX` environment variable

---

## 9. Java folder analysis

### Contents

| Path | Type |
|---|---|
| `java/com/google/scrollview/` | Swing tool |
| `java/com/google/scrollview/ScrollView.java` | Main entry (`public class ScrollView`, server on port 8461, line 35) |
| `java/com/google/scrollview/ui/SVWindow.java` | Top-level window; imports `javax.swing.*`, `java.awt.*`, `org.piccolo2d.*` (lines 20-40) |
| `java/com/google/scrollview/ui/{SVAbstractMenuItem,SVCheckboxMenuItem,SVEmptyMenuItem,SVImageHandler,SVMenuBar,SVMenuItem,SVPopupMenu,SVSubMenuItem}.java` | Menu primitives |
| `java/com/google/scrollview/events/{SVEvent,SVEventHandler,SVEventType}.java` | IPC message structs (matches the C structs in `src/viewer/scrollview.h`) |
| `java/Makefile.am`, `java/com/Makefile.am`, `java/com/google/Makefile.am`, `java/com/google/scrollview/{Makefile.am,events/Makefile.am,ui/Makefile.am}`, `java/Manifest.txt` | Autotools build glue |

### Verdict: NOT an Android wrapper

Confirmed by reading the source:

> `import javax.swing.JFrame;` (line 40)
> `import java.awt.BasicStroke;` (line 29) ... `import java.awt.TextArea;` (line 35)
> `import org.piccolo2d.nodes.PImage;` (line 24)
> (`java/com/google/scrollview/ui/SVWindow.java`)

The tool is a **desktop Swing + Piccolo2D viewer** of `.box` files (training
ground truth). It talks over TCP to the C++ `scrollview` server compiled
into `libtesseract` (`src/viewer/scrollview.cpp`). There is **no Android
JNI bridge** in this repo; **no `JNIEXPORT`, `JNIEnv`, `Java_*` symbols,
no `Application.mk`, no `Android.mk`, no `gradle` files, no
`com/google/tesseract/android/`** anywhere.

### Implication for Android embedding

To use Tesseract on Android you must:

1. Cross-compile `libtesseract` + `libleptonica` for `arm64-v8a` / `armeabi-v7a`
   via the Android NDK. The Tesseract `CMakeLists.txt` has an `if(ANDROID)`
   branch (`CMakeLists.txt:851-858`) that pulls in `CpuFeaturesNdkCompat`,
   plus `#if defined(ANDROID)` guards in `src/lstm/weightmatrix.cpp:28`,
   `src/arch/simddetect.cpp:57/227`, and `src/wordrec/language_model.cpp:45`.
   You supply the NDK toolchain via `-DCMAKE_TOOLCHAIN_FILE=$NDK/build/cmake/android.toolchain.cmake`.
2. Write your own JNI wrapper (`Java_com_example_tesseract_Tess_nativeRecognize`
   etc.) bridging `JNIEXPORT` to `tess::TessBaseAPI`.
3. Ship `eng.traineddata` (and friends) in `assets/`.

Established third-party Android wrappers (NOT in this repo):

- `adaptech-cz/Tesseract4Android` — pure-Java/Kotlin API on top of NDK-built
  `libtesseract.so` + `libleptonica.so`.
- `rmtheis/tess-two` — the legacy Tess4J predecessor; bundles a fork with
  Java APIs and a `libtess.so` built per-ABI.
- `czschool/tesseract-android-tools` — old Build-of-Tesseract-for-Android.

---

## 10. Build commands

### 10.a Linux desktop (CMake — recommended)

```bash
# Prereqs: CMake >= 3.18, C++17 compiler, leptonica-dev >= 1.74 with zlib/png/tiff
# (Ubuntu: apt install build-essential cmake libleptonica-dev pkg-config)
mkdir build && cd build
cmake .. \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TRAINING_TOOLS=ON \
  -DBUILD_TESTS=OFF \
  -DGRAPHICS_DISABLED=OFF
make -j$(nproc)
sudo make install
sudo ldconfig
```

Output: `build/bin/tesseract` + `build/libtesseract.so` (or .a).

### 10.b Linux desktop (Autotools — alternative)

```bash
./autogen.sh
./configure --enable-training   # adds icu/pango/cairo requirements
make -j$(nproc)
sudo make install
sudo ldconfig
```

### 10.c Android NDK cross-compile (no in-tree toolchain — bring your own)

The repo **does not ship** a CMake toolchain file. You pass NDK's via the
standard `-DCMAKE_TOOLCHAIN_FILE=...` switch. Tesseract's `CMakeLists.txt`
will detect `ANDROID=1` and link `CpuFeaturesNdkCompat`:

```bash
export ANDROID_NDK=$ANDROID_HOME/ndk/26.3.11579264

cmake -S . -B build-android \
  -DCMAKE_SYSTEM_NAME=Android \
  -DCMAKE_SYSTEM_VERSION=24 \
  -DCMAKE_ANDROID_ARCH_ABI=arm64-v8a \
  -DCMAKE_ANDROID_NDK=$ANDROID_NDK \
  -DCMAKE_ANDROID_STL_TYPE=c++_shared \
  -DCMAKE_BUILD_TYPE=Release \
  -DBUILD_TRAINING_TOOLS=OFF \
  -DGRAPHICS_DISABLED=ON \
  -DDISABLE_ARCHIVE=OFF \
  -DDISABLE_TIFF=OFF
cmake --build build-android -j
```

The `ANDROID_TOOLCHAIN` branch (`CMakeLists.txt:629-632`) additionally
exposes `$ANDROID_TOOLCHAIN/sysroot/usr/include` for headers that don't ship
in the NDK default sysroot (e.g. `cpufeatures.h`). For native code in your
own Android app, the canonical wrapper is `externalNativeBuild { cmake { ... } }`
in `app/build.gradle`, pointing at this checkout and pulling
`CpuFeaturesNdkCompat` from Maven (`com.google.android.gms:play-services-cpufeatures` or the standalone AAR).

---

## 11. Notable patterns

### 11.a Plugin renderers (`renderer.h` + `renderer.cpp`)

Abstract base `TESS_API TessResultRenderer` (`include/tesseract/renderer.h:47`)
with virtual `BeginDocumentHandler/AddImageHandler/EndDocumentHandler`. Concrete
subclasses (all in `src/api/`, all `TESS_API`):

| Renderer | Header line | Source file |
|---|---|---|
| `TessTextRenderer` | `include/tesseract/renderer.h:160` | `src/api/renderer.cpp:139` |
| `TessHOcrRenderer` | `:171` | `src/api/hocrrenderer.cpp:513` |
| `TessAltoRenderer` | `:188` | `src/api/altorenderer.cpp:80` |
| `TessPAGERenderer` | `:204` | `src/api/pagerenderer.cpp:628` |
| `TessTsvRenderer` | `:221` | `src/api/renderer.cpp:179` |
| `TessPDFRenderer` | `:238` | `src/api/pdfrenderer.cpp:827` |
| `TessUnlvRenderer` | `:276` | `src/api/renderer.cpp:196` |
| `TessLSTMBoxRenderer` | `:287` | `src/api/lstmboxrenderer.cpp:95` |
| `TessBoxTextRenderer` | `:298` | `src/api/renderer.cpp:213` |
| `TessWordStrBoxRenderer` | `:309` | `src/api/wordstrboxrenderer.cpp:94` |
| `TessOsdRenderer` (legacy) | `:322` | `src/api/renderer.cpp:231` |

Composition via `void insert(TessResultRenderer *next)` (`renderer.h:54`)
lets one `TessBaseAPI::ProcessPages` call drive multiple outputs in parallel.

### 11.b `OcrEngineMode` (OEM) dispatch

`include/tesseract/publictypes.h:263`:

```cpp
enum OcrEngineMode {
  OEM_TESSERACT_ONLY,            // = 0, legacy only; deprecated since 5.x
  OEM_LSTM_ONLY,                 // = 1, default in 5.x for `tesseract --oem 1`
  OEM_TESSERACT_LSTM_COMBINED,   // = 2, LSTM with legacy fallback; deprecated
  OEM_DEFAULT,                   // = 3, select from language/config defaults
  OEM_COUNT
};
```

Dispatch: `tesseract_->AnyLSTMLang()` -> LSTM recognizer constructed in
`Tesseract::init_lstm_components` (`src/ccmain/tessedit.cpp:171-172`).
`Tesseract::AnyTessLang()` gates legacy-only paths (`recog_word`,
`classify_word_pass1`, `fixxht`, `bigram_correction_pass`, ...).
The CLI default is `OEM_LSTM_ONLY` when `DISABLED_LEGACY_ENGINE` is set
(`src/tesseract.cpp:670-674`).

### 11.c `PageSegMode` (PSM)

`include/tesseract/publictypes.h:157-178`:

```cpp
enum PageSegMode {
  PSM_OSD_ONLY               = 0,   // OSD only
  PSM_AUTO_OSD               = 1,   // auto + orientation/script detect
  PSM_AUTO_ONLY              = 2,   // segmentation, no OSD/OCR
  PSM_AUTO                   = 3,   // default for the CLI (no OSD)
  PSM_SINGLE_COLUMN          = 4,
  PSM_SINGLE_BLOCK_VERT_TEXT = 5,
  PSM_SINGLE_BLOCK           = 6,   // default for the LIBRARY
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

Six inline predicate helpers (`publictypes.h:186-207`): `PSM_OSD_ENABLED`,
`PSM_ORIENTATION_ENABLED`, `PSM_COL_FIND_ENABLED`, `PSM_SPARSE`,
`PSM_BLOCK_FIND_ENABLED`, `PSM_LINE_FIND_ENABLED`, `PSM_WORD_FIND_ENABLED`.
These are used throughout `src/ccmain/pagesegmain.cpp` to gate which
analysis stages run.

### 11.d Recognition confidence

| Source | Location | Notes |
|---|---|---|
| `TessBaseAPI::MeanTextConf()` | `include/tesseract/baseapi.h:629`, impl `src/api/baseapi.cpp:1719` | Average over all words (0-100) |
| `TessBaseAPI::AllWordConfidences()` | `:636` | Per-word array, -1 terminated |
| `LTRResultIterator::Confidence(level)` | `include/tesseract/ltrresultiterator.h:92` | 0-100 per word/symbol |
| `ChoiceIterator::Confidence()` | `:206` | 0-100 per choice |
| Reject threshold | `tessedit_certainty_threshold` (Wordrec BOOL/double, `src/wordrec/wordrec.h:193`); `tessedit_reject_doc_outlier_factor`, `tessedit_reject_block_outlier_factor`, `tessedit_reject_row_outlier_factor`, `tessedit_reject_ratio`, `tessedit_reject_threshold1/2/3/4/5`, `quality_min_initial_alphas`, `uncertainty_to_reject`, `ok_repeated_ch_non_alphanum_wds` | declared in `src/ccmain/tessvars.cpp` (auto-generated by `Params` macros) |

`src/ccmain/reject.cpp:227-251` shows `compute_reject_threshold()` choosing
the gap midpoint between the best and runner-up choices.

### 11.e Other notable idioms

- **TESS_API** visibility (`include/tesseract/export.h:19-35`): Windows uses
  `__declspec(dllexport/dllimport)`, GCC/Clang uses
  `__attribute__((visibility("default")))` when `TESS_EXPORTS` or `TESS_IMPORTS`
  is set.
- **Dynamic library macro dispatch**: `CMakeLists.txt:801-807` defines
  `TESS_EXPORTS` (private) and `TESS_IMPORTS` (interface) per
  `BUILD_SHARED_LIBS`.
- **SIMD-aware dispatch**: `SIMDDetect::IsNEONAvailable` etc. in
  `src/arch/simddetect.cpp`; runtime detection via `android_getCpuFeatures()`
  in the Android branch (line 227) and `getauxval/elf_aux_info` on Linux.
- **Optional `*.traineddata` components**: `src/ccutil/tessdatamanager.{h,cpp}`
  holds the directory of components inside a `.traineddata` (`lstm`, `lstm_p`,
  `feat`, `normproto`, `pffmtable`, `unicharset`, `ambigs`, `dawg`, `params`,
  `config`, `curlang`, `lm`, `wordbigram`, `indic`, `userpatterns`,
  `userwords`). This is what `combine_tessdata` (6.f step 11) merges.
- **Header-only generated** `version.h.in` (`include/tesseract/version.h.in:21-30`)
  is `configure_file()`-substituted by both CMake (`CMakeLists.txt:540-541`)
  and autoconf (`configure.ac:546`).

---

## Summary verification table

| Claim | Evidence | OK? |
|---|---|:---:|
| Version 5.5.3 | `VERSION:1` | ✓ |
| Apache-2.0 license | `LICENSE:1` + `README.md:7` | ✓ |
| `tesseract` CLI main | `src/tesseract.cpp:855` (`main`) | ✓ |
| `libtesseract` target | `CMakeLists.txt:735` | ✓ |
| Leptonica required, >=1.74 | `configure.ac:487`, `CMakeLists.txt:445` | ✓ |
| No `.traineddata` in repo | `find tessdata -name '*.traineddata'` -> empty | ✓ |
| 14 PSMs (0–13) | `publictypes.h:157-178` | ✓ |
| 4 OEMs (0–3) | `publictypes.h:263-277` | ✓ |
| Java is Swing, not Android | `import javax.swing.JFrame` `SVWindow.java:40` | ✓ |
| 11 output formats | `PreloadRenderers` lines 510-634 | ✓ |
| Android branch in CMake | `CMakeLists.txt:851-858` | ✓ |
| 489 source files under `src/` | `find src -name '*.cpp' -o -name '*.h' | wc -l` | ✓ |

---

## Gaps / things I could not pin down

1. **`scripts/` directory**: the prompt listed a top-level `scripts/` folder,
   but `ls <repo>` shows it does **not exist**. Tesseract puts build helpers in
   `cmake/` (`BuildFunctions.cmake`, `CheckFunctions.cmake`, `Configure.cmake`,
   `SourceGroups.cmake`, `SourceLists.cmake`, `BuildOptimizations.cmake`,
   `templates/{cmake_uninstall.cmake.in,TesseractConfig.cmake.in}`).
2. **`test/` directory is empty** in this snapshot — it exists on disk but
   contains no files (likely a placeholder for legacy `make check` scripts).
3. **No Android JNI bridge** exists in this repo (explicitly verified —
   no `JNIEXPORT`, no `Application.mk`, no `gradle` files). Any Android
   usage must come from a downstream fork (Tess4Android, tess-two).
4. **`Tesseract::recognize_page(std::string &)` declared in
   `src/ccmain/tesseractclass.h:524`** has no definition in the source —
   appears to be a leftover/declaration-only entry. Not called from anywhere
   in `src/` (verified by `grep -rn "recognize_page"`).
5. **`.gitmodules`** is at the root but its contents were not inspected;
   leptonica may be the main submodule (per `INSTALL.GIT.md`). Submodules
   are not checked out in this working copy.
