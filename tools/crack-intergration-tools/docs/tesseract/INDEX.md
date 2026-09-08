# INDEX — Searchable File / Class / Function Index

> **Lookup-only file**: every entry lists a path, symbol, line range and one-line summary.
> Use Ctrl-F / `grep` on this file. All entries grep-verified 2026-07-28 against the inventory.

Format: `path:line` — `Symbol` — one-liner.

---

## 1. Top-level repo files

| Path | Line | Note |
|---|---:|---|
| `VERSION` | 1 | Single line `5.5.3` — the canonical version stamp |
| `LICENSE` | 1 | Apache-2.0 full text |
| `README.md` | 7 | Apache-2.0 license badge |
| `README.md` | 25 | `This package contains an OCR engine` — project description anchor |
| `CMakeLists.txt` | 12 | `cmake_minimum_required(VERSION 3.18)` |
| `CMakeLists.txt` | 70 | `set(MINIMUM_LEPTONICA_VERSION 1.74)` |
| `CMakeLists.txt` | 91 | `option(OPENMP_BUILD ...)` |
| `CMakeLists.txt` | 101 | `option(BUILD_TESTS ...)` |
| `CMakeLists.txt` | 135 | `set(CMAKE_CXX_STANDARD 17)` |
| `CMakeLists.txt` | 338 | `find_package(OpenMP)` |
| `CMakeLists.txt` | 378 | `${LIB_pthread}` linkage |
| `CMakeLists.txt` | 382 | `${LIB_Ws2_32}` linkage (Win) |
| `CMakeLists.txt` | 445 | `find_package(Leptonica ${MINIMUM_LEPTONICA_VERSION} CONFIG)` |
| `CMakeLists.txt` | 470 | `find_package(TIFF)` — optional libtiff |
| `CMakeLists.txt` | 484 | `find_package(LibArchive)` — optional libarchive |
| `CMakeLists.txt` | 498 | `find_package(CURL)` — optional libcurl |
| `CMakeLists.txt` | 540 | `configure_file(... version.h.in ...)` |
| `CMakeLists.txt` | 735 | `add_library(libtesseract ...)` |
| `CMakeLists.txt` | 801 | defines `TESS_EXPORTS` / `TESS_IMPORTS` |
| `CMakeLists.txt` | 851 | `if(ANDROID)` branch — pulls CpuFeaturesNdkCompat |
| `CMakeLists.txt` | 853 | `find_package(CpuFeaturesNdkCompat REQUIRED)` |
| `CMakeLists.txt` | 864 | `add_executable(tesseract src/tesseract.cpp)` |
| `CMakeLists.txt` | 865 | `target_link_libraries(tesseract libtesseract)` |
| `CMakeLists.txt` | 876 | `BUILD_TESTS=ON` block |
| `configure.ac` | 8 | requires autoconf 2.69 |
| `configure.ac` | 9 | `AC_INIT([tesseract], ...)` |
| `configure.ac` | 10 | `m4_esyscmd_s([test -d .git && git describe --abbrev=4 ... || cat VERSION])` |
| `configure.ac` | 136 | SIMD `AX_CHECK_COMPILE_FLAG` for AVX/AVX2/AVX512F/FMA/SSE4.1/NEON/RVV |
| `configure.ac` | 283 | `AC_CHECK_HEADERS([tiffio.h], ...)` |
| `configure.ac` | 317 | macOS Apple Accelerate framework |
| `configure.ac` | 426 | `AC_SEARCH_LIBS([pthread_create], [pthread])` |
| `configure.ac` | 449 | asciidoctor detection (man-pages) |
| `configure.ac` | 473 | libcurl detection |
| `configure.ac` | 487 | `PKG_CHECK_MODULES([LEPTONICA], [lept >= 1.74], ...)` |
| `configure.ac` | 494 | libarchive detection |
| `configure.ac` | 512 | `PKG_CHECK_MODULES([ICU_UC], [icu-uc >= 52.1] ...)` |
| `configure.ac` | 522 | `PKG_CHECK_MODULES([pango], [pango >= 1.38.0] ...)` |
| `configure.ac` | 531 | `PKG_CHECK_MODULES([cairo], [cairo] ...)` |
| `configure.ac` | 538 | pangocairo/pangoft2 (optional) |
| `configure.ac` | 546 | `version.h.in` configure_file |
| `Makefile.am` | 1 | Autotools top-level glue (~60 KB) |
| `tesseract.pc.in` | — | Autotools pkg-config template |
| `tesseract.pc.cmake` | — | CMake pkg-config template |
| `sw.cpp` | 1 | 12 963-byte C++17 "single-header" wrapper |
| `autogen.sh` | 1 | Wrapper to bootstrap autotools |
| `.gitmodules` | — | leptonica submodule reference |
| `INSTALL.GIT.md` | — | Git-submodule hint for leptonica |

---

## 2. `include/tesseract/` — public C++ headers (12 files)

### 2.a `baseapi.h` — `TessBaseAPI` class declaration

| Path:line | Symbol | Note |
|---|---:|---|
| `include/tesseract/baseapi.h:76` | `class TESS_API TessBaseAPI` | public façade class |
| `:78` | `TessBaseAPI()` | ctor |
| `:79` | `virtual ~TessBaseAPI()` | dtor |
| `:87` | `static const char *Version()` | returns `5.5.3` |
| `:93` | `void SetInputName(const char *)` | |
| `:101` | `const char *GetInputName()` | |
| `:103` | `void SetInputImage(Pix *)` | Leptonica Pix overload |
| `:104` | `Pix *GetInputImage()` | |
| `:105` | `int GetSourceYResolution()` | |
| `:106` | `const char *GetDatapath()` | |
| `:109` | `void SetOutputName(const char *)` | |
| `:124` | `bool SetVariable(const char *, const char *)` | |
| `:125` | `bool SetDebugVariable(...)` | |
| `:131` | `bool GetIntVariable(...) const` | |
| `:132` | `bool GetBoolVariable(...) const` | |
| `:133` | `bool GetDoubleVariable(...) const` | |
| `:139` | `const char *GetStringVariable(...) const` | |
| `:146` | `void PrintFontsTable(FILE *) const` | legacy-only |
| `:153` | `void PrintVariables(FILE *) const` | |
| `:158` | `bool GetVariableAsString(...) const` | |
| `:197` | `int Init(datapath, lang, OEM, configs[], size, vars_vec, vars_values, set_only_non_debug)` | full Init |
| `:202` | `int Init(datapath, lang, OEM)` (inline) | 3-arg convenience |
| `:205` | `int Init(datapath, lang)` (inline) | 2-arg convenience, OEM_DEFAULT |
| `:211` | `int Init(data, data_size, lang, OEM, configs, configs_size, ..., FileReader reader)` | in-memory init |
| `:225` | `const char *GetInitLanguagesAsString() const` | |
| `:232` | `void GetLoadedLanguagesAsVector(vector<string> *) const` | |
| `:237` | `void GetAvailableLanguagesAsVector(vector<string> *) const` | |
| `:243` | `void InitForAnalysePage()` | for layout-only mode |
| `:251` | `void ReadConfigFile(const char *)` | |
| `:253` | `void ReadDebugConfigFile(const char *)` | |
| `:260` | `void SetPageSegMode(PageSegMode)` | |
| `:263` | `PageSegMode GetPageSegMode() const` | |
| `:282` | `char *TesseractRect(imagedata, bpp, bpl, left, top, width, height)` | pre-segmented ROI OCR |
| `:290` | `void ClearAdaptiveClassifier()` | |
| `:307` | `void SetImage(imagedata, w, h, bpp, bpl)` | raw buffer overload |
| `:318` | `void SetImage(Pix *)` | Leptonica Pix overload |
| `:324` | `void SetSourceResolution(int ppi)` | |
| `:331` | `void SetRectangle(int left, int top, int w, int h)` | ROI |
| `:338` | `Pix *GetThresholdedImage()` | |
| `:343` | `float GetGradient()` | |
| `:350` | `Boxa *GetRegions(Pixa **)` | |
| `:363` | `Boxa *GetTextlines(raw_image, padding, pixa, blockids, paraids)` | |
| `:368` | `Boxa *GetTextlines(pixa, blockids)` (inline) | |
| `:380` | `Boxa *GetStrips(pixa, blockids)` | |
| `:387` | `Boxa *GetWords(pixa)` | |
| `:397` | `Boxa *GetConnectedComponents(cc)` | |
| `:411` | `Boxa *GetComponentImages(level, text_only, raw_image, padding, pixa, blockids, paraids)` | |
| `:415` | `Boxa *GetComponentImages(level, text_only, pixa, blockids)` (inline) | |
| `:427` | `int GetThresholdedImageScaleFactor() const` | |
| `:444` | `PageIterator *AnalyseLayout()` | default |
| `:445` | `PageIterator *AnalyseLayout(bool merge_similar_words)` | full |
| `:453` | `int Recognize(ETEXT_DESC *)` | main recognizer entry |
| `:482` | `bool ProcessPages(filename, retry_config, timeout_ms, renderer)` | multi-file/auto-detect |
| `:485` | `bool ProcessPagesInternal(filename, retry_config, timeout_ms, renderer)` | |
| `:497` | `bool ProcessPage(Pix *, page_index, filename, retry_config, timeout_ms, renderer)` | single-page |
| `:509` | `ResultIterator *GetIterator()` | |
| `:519` | `MutableIterator *GetMutableIterator()` | exposes internals |
| `:525` | `char *GetUTF8Text()` | simple text output |
| `:536` | `char *GetHOCRText(ETEXT_DESC *, page_number)` | hOCR XML |
| `:544` | `char *GetHOCRText(int page_number)` | |
| `:550` | `char *GetAltoText(ETEXT_DESC *, page_number)` | ALTO XML |
| `:556` | `char *GetAltoText(int page_number)` | |
| `:562` | `char *GetPAGEText(ETEXT_DESC *, page_number)` | PAGE XML |
| `:568` | `char *GetPAGEText(int page_number)` | |
| `:575` | `char *GetTSVText(int page_number)` | TSV |
| `:583` | `char *GetLSTMBoxText(int page_number)` | LSTM box |
| `:592` | `char *GetBoxText(int page_number)` | legacy box |
| `:600` | `char *GetWordStrBoxText(int page_number)` | wordstr box |
| `:607` | `char *GetUNLVText()` | UNLV zone format |
| `:618` | `bool DetectOrientationScript(orient_deg*, orient_conf*, script_name**, script_conf*)` | |
| `:626` | `char *GetOsdText(int page_number)` | OSD-only output |
| `:629` | `int MeanTextConf()` | mean over all words 0-100 |
| `:636` | `int *AllWordConfidences()` | per-word, -1 terminated |
| `:649` | `bool AdaptToWordStr(PSM, wordstr)` (legacy) | |
| `:658` | `void Clear()` | reset results, keep init |
| `:666` | `void End()` | full teardown |
| `:675` | `static void ClearPersistentCache()` | global cache reset |
| `:683` | `int IsValidWord(const char *) const` | |
| `:685` | `bool IsValidCharacter(const char *) const` | |
| `:687` | `bool GetTextDirection(out_offset*, out_slope*)` | |
| `:690` | `void SetDictFunc(DictFunc)` | custom dictionary callback |
| `:695` | `void SetProbabilityInContextFunc(...)` | |
| `:701` | `bool DetectOS(OSResults *)` | low-level OSD |
| `:707` | `void GetBlockTextOrientations(...)` | |
| `:711` | `const char *GetUnichar(int unichar_id) const` | |
| `:714` | `const Dawg *GetDawg(int i) const` | |
| `:717` | `int NumDawgs() const` | |
| `:719` | `Tesseract *tesseract() const` | accessor for engine |
| `:723` | `OcrEngineMode oem() const` | |
| `:727` | `void set_min_orientation_margin(double)` | |
| `:816` | `std::string HOcrEscape(const char *)` | free helper, hOCR escaping |

### 2.b `capi.h` — C-API (62 `TESS_API` entries)

| Path:line | Symbol | Note |
|---|---:|---|
| `include/tesseract/capi.h:148` | `const char *TessVersion()` | |
| `:156` | `void TessDeleteText(const char *)` | |
| `:157` | `void TessDeleteTextArray(char **)` | |
| `:158` | `void TessDeleteIntArray(const int *)` | |
| `:161` | `TessResultRenderer *TessTextRendererCreate(outputbase)` | |
| `:162` | `TessResultRenderer *TessHOcrRendererCreate(outputbase)` | |
| `:163` | `TessResultRenderer *TessHOcrRendererCreate2(outputbase, font_id)` | |
| `:165` | `TessResultRenderer *TessAltoRendererCreate(outputbase)` | |
| `:166` | `TessResultRenderer *TessPAGERendererCreate(outputbase)` | |
| `:167` | `TessResultRenderer *TessTsvRendererCreate(outputbase)` | |
| `:168` | `TessResultRenderer *TessPDFRendererCreate(outputbase, datadir, textonly)` | |
| `:171` | `TessResultRenderer *TessUnlvRendererCreate(outputbase)` | |
| `:172` | `TessResultRenderer *TessBoxTextRendererCreate(outputbase)` | |
| `:173` | `TessResultRenderer *TessLSTMBoxRendererCreate(outputbase)` | |
| `:174` | `TessResultRenderer *TessWordStrBoxRendererCreate(outputbase, page)` | |
| `:177` | `void TessDeleteResultRenderer(renderer)` | |
| `:178` | `void TessResultRendererInsert(renderer, next)` | chain outputs |
| `:180` | `TessResultRenderer *TessResultRendererNext(renderer)` | |
| `:182` | `BOOL TessResultRendererBeginDocument(renderer, title)` | |
| `:184` | `BOOL TessResultRendererAddImage(renderer, api)` | |
| `:186` | `BOOL TessResultRendererEndDocument(renderer)` | |
| `:188` | `const char *TessResultRendererExtention(renderer)` | |
| `:189` | `const char *TessResultRendererTitle(renderer)` | |
| `:190` | `int TessResultRendererImageNum(renderer)` | |
| `:210` | `TessBaseAPI *TessBaseAPICreate()` | |
| `:217` | `void TessBaseAPIDelete(handle)` | |
| `:219` | `void TessBaseAPISetInputName(handle, name)` | |
| `:220` | `const char *TessBaseAPIGetInputName(handle)` | |
| `:222` | `void TessBaseAPISetInputImage(handle, Pix *)` | |
| `:223` | `Pix *TessBaseAPIGetInputImage(handle)` | |
| `:225` | `int TessBaseAPIGetSourceYResolution(handle)` | |
| `:226` | `const char *TessBaseAPIGetDatapath(handle)` | |
| `:228` | `void TessBaseAPISetOutputName(handle, name)` | |
| `:230` | `BOOL TessBaseAPISetVariable(handle, name, value)` | |
| `:232` | `BOOL TessBaseAPISetDebugVariable(handle, name, value)` | |
| `:235` | `BOOL TessBaseAPIGetIntVariable(handle, name, value*)` | |
| `:237` | `BOOL TessBaseAPIGetBoolVariable(handle, name, value*)` | |
| `:239` | `BOOL TessBaseAPIGetDoubleVariable(handle, name, value*)` | |
| `:241` | `const char *TessBaseAPIGetStringVariable(handle, name)` | |
| `:244` | `void TessBaseAPIPrintVariables(handle, FILE *)` | |
| `:245` | `BOOL TessBaseAPIPrintVariablesToFile(handle, filename, append)` | |
| `:248` | `int TessBaseAPIInit1(handle, datapath, language, OEM, configs[], configs_size)` | |
| `:251` | `int TessBaseAPIInit2(handle, datapath, language, OEM)` | |
| `:267` | `int TessBaseAPIInit3(handle, datapath, language, OEM, configs[], configs_size, vars_vec, vars_values, set_only_non_debug)` | |
| `:270` | `int TessBaseAPIInit4(handle, datapath, language, OEM)` | |
| `:276` | `int TessBaseAPIInit5(handle, data, data_size, language, OEM, configs[], configs_size, vars_vec, vars_values, set_only_non_debug, FileReader reader)` | |
| `:282` | `const char *TessBaseAPIGetInitLanguagesAsString(handle)` | |
| `:284` | `char **TessBaseAPIGetLoadedLanguagesAsVector(handle)` | |
| `:286` | `char **TessBaseAPIGetAvailableLanguagesAsVector(handle)` | |
| `:289` | `void TessBaseAPIInitForAnalysePage(handle)` | |
| `:291` | `void TessBaseAPIReadConfigFile(handle, filename)` | |
| `:293` | `void TessBaseAPIReadDebugConfigFile(handle, filename)` | |
| `:296` | `void TessBaseAPISetPageSegMode(handle, PSM)` | |
| `:298` | `TessPageSegMode TessBaseAPIGetPageSegMode(handle)` | |
| `:300` | `char *TessBaseAPIRect(handle, imagedata, bpp, bpl, left, top, w, h)` | |
| `:305` | `void TessBaseAPIClearAdaptiveClassifier(handle)` | |
| `:307` | `void TessBaseAPISetImage(handle, imagedata, w, h, bpp, bpl)` | |
| `:323` | `void TessBaseAPISetImage2(handle, Pix *)` | |
| `:325` | `void TessBaseAPISetSourceResolution(handle, ppi)` | |
| `:327` | `void TessBaseAPISetRectangle(handle, left, top, w, h)` | |
| `:330` | `Pix *TessBaseAPIGetThresholdedImage(handle)` | |
| `:331` | `float TessBaseAPIGetGradient(handle)` | |
| `:332` | `Boxa *TessBaseAPIGetRegions(handle, pixa)` | |
| `:334` | `Boxa *TessBaseAPIGetTextlines(handle, raw_image, raw_padding, pixa, blockids, paraids)` | |
| `:337` | `Boxa *TessBaseAPIGetTextlines1(handle, pixa, blockids)` | |
| `:341` | `Boxa *TessBaseAPIGetStrips(handle, pixa, blockids)` | |
| `:343` | `Boxa *TessBaseAPIGetWords(handle, pixa)` | |
| `:345` | `Boxa *TessBaseAPIGetConnectedComponents(handle, cc)` | |
| `:347` | `Boxa *TessBaseAPIGetComponentImages(handle, level, text_only, raw_image, raw_padding, pixa, blockids, paraids)` | |
| `:352` | `Boxa *TessBaseAPIGetComponentImages1(handle, level, text_only, pixa, blockids)` | |
| `:357` | `int TessBaseAPIGetThresholdedImageScaleFactor(handle)` | |
| `:360` | `TessPageIterator *TessBaseAPIAnalyseLayout(handle)` | |
| `:362` | `int TessBaseAPIRecognize(handle, ETEXT_DESC *)` | |
| `:364` | `BOOL TessBaseAPIProcessPages(handle, filename, retry_config, timeout_ms, renderer)` | |
| `:368` | `BOOL TessBaseAPIProcessPage(handle, Pix *, page_index, filename, retry_config, timeout_ms, renderer)` | |
| `:374` | `TessResultIterator *TessBaseAPIGetIterator(handle)` | |
| `:375` | `TessMutableIterator *TessBaseAPIGetMutableIterator(handle)` | |
| `:387` | `char *TessBaseAPIGetUTF8Text(handle)` | |
| `:398` | `char *TessBaseAPIGetHOCRText(handle, page_number)` | |
| `:409` | `char *TessBaseAPIGetAltoText(handle, page_number)` | |
| `:420` | `char *TessBaseAPIGetPAGEText(handle, page_number)` | |
| `:431` | `char *TessBaseAPIGetTsvText(handle, page_number)` | |
| `:442` | `char *TessBaseAPIGetBoxText(handle, page_number)` | |
| `:453` | `char *TessBaseAPIGetLSTMBoxText(handle, page_number)` | |
| `:464` | `char *TessBaseAPIGetWordStrBoxText(handle, page_number)` | |
| `:475` | `char *TessBaseAPIGetUNLVText(handle)` | |
| `:476` | `int TessBaseAPIMeanTextConf(handle)` | |
| `:478` | `int *TessBaseAPIAllWordConfidences(handle)` | |
| `:481` | `BOOL TessBaseAPIAdaptToWordStr(handle, PSM, wordstr)` | |
| `:486` | `void TessBaseAPIClear(handle)` | |
| `:487` | `void TessBaseAPIEnd(handle)` | |
| `:489` | `int TessBaseAPIIsValidWord(handle, word)` | |
| `:490` | `BOOL TessBaseAPIGetTextDirection(handle, out_offset*, out_slope*)` | |
| `:493` | `const char *TessBaseAPIGetUnichar(handle, unichar_id)` | |
| `:495` | `void TessBaseAPIClearPersistentCache(handle)` | |
| `:501` | `BOOL TessBaseAPIDetectOrientationScript(handle, orient_deg*, orient_conf*, script_name**, script_conf*)` | |
| `:508` | `void TessBaseAPISetMinOrientationMargin(handle, margin)` | |
| `:511` | `int TessBaseAPINumDawgs(handle)` | |
| `:513` | `TessOcrEngineMode TessBaseAPIOem(handle)` | |

### 2.c `publictypes.h` — enums & helpers

| Path:line | Symbol | Note |
|---|---:|---|
| `include/tesseract/publictypes.h:51` | `enum PolyBlockType` | PT_UNKNOWN … PT_COUNT |
| `:157-178` | `enum PageSegMode` | 14 values (0–13) |
| `:186` | `inline bool PSM_OSD_ENABLED(m)` | predicate helper |
| `:193` | `inline bool PSM_ORIENTATION_ENABLED(m)` | |
| `:199` | `inline bool PSM_COL_FIND_ENABLED(m)` | |
| `:201` | `inline bool PSM_SPARSE(m)` | |
| `:203` | `inline bool PSM_BLOCK_FIND_ENABLED(m)` | |
| `:205` | `inline bool PSM_LINE_FIND_ENABLED(m)` | |
| `:207` | `inline bool PSM_WORD_FIND_ENABLED(m)` | |
| `:214` | `enum PageIteratorLevel` | RIL_BLOCK…RIL_SYMBOL |
| `:263-277` | `enum OcrEngineMode` | OEM_TESSERACT_ONLY, OEM_LSTM_ONLY, OEM_TESSERACT_LSTM_COMBINED, OEM_DEFAULT |
| `:39+` | `enum Orientation`, `WritingDirection`, `TextlineOrder`, `ParagraphJustification` | |

### 2.d `pageiterator.h`, `resultiterator.h`, `ltrresultiterator.h`, `renderer.h`

| Path:line | Symbol | Note |
|---|---:|---|
| `include/tesseract/pageiterator.h:50` | `class TESS_API PageIterator` | |
| `:66` | `PageIterator(...)` | ctor |
| `:77` | `PageIterator(const PageIterator &)` | copy ctor |
| `:89` | `virtual void Begin()` | |
| `:96` | `virtual void RestartParagraph()` | |
| `:109` | `virtual void RestartRow()` | |
| `:122` | `virtual bool Next(PageIteratorLevel)` | |
| `:137` | `virtual bool IsAtBeginningOf(level) const` | |
| `:155` | `bool IsAtFinalElement(lvl, el) const` | |
| `:164` | `bool Cmp(other) const` | |
| `:188` | `void SetBoundingBoxComponents(...)` | |
| `:203` | `void BoundingBox(level, &l, &t, &r, &b)` | |
| `:261` | `void Baseline(...)` | |
| `:265` | `void RowAttributes(...)` | |
| `:276` | `void Orientation(...)` | |
| `:309` | `void ParagraphInfo(...)` | |
| `include/tesseract/resultiterator.h:32` | `class TESS_API ResultIterator : public LTRResultIterator` | |
| `include/tesseract/ltrresultiterator.h:45` | `class TESS_API LTRResultIterator : public PageIterator` | |
| `:82` | `char *GetUTF8Text(level)` | |
| `:92` | `int Confidence(level)` | |
| `:104` | `void WordFontAttributes(...)` | |
| `:111` | `const char *WordRecognitionLanguage()` | |
| `:117` | `bool WordIsFromDictionary()` | |
| `:123` | `bool WordIsNumeric()` | |
| `:149` | `const char *WordTruthUTF8Text()` | |
| `:157` | `void WordLattice(...)` | |
| `:164-172` | `SymbolIsSuperscript/Subscript/Dropcap` | |
| `:180` | `class TESS_API ChoiceIterator` | nested |
| `:190` | `Next()` | |
| `:198` | `GetUTF8Text()` | |
| `:206` | `Confidence()` | |
| `src/ccmain/mutableiterator.h:51` | `class TESS_API MutableIterator : public ResultIterator` | exposes internals |
| `include/tesseract/renderer.h:47` | `class TESS_API TessResultRenderer` | abstract base |
| `:54` | `void insert(TessResultRenderer *next)` | chain |
| `:160` | `class TessTextRenderer` | |
| `:171` | `class TessHOcrRenderer` | |
| `:188` | `class TessAltoRenderer` | |
| `:204` | `class TessPAGERenderer` | |
| `:221` | `class TessTsvRenderer` | |
| `:238` | `class TessPDFRenderer` | |
| `:276` | `class TessUnlvRenderer` | |
| `:287` | `class TessLSTMBoxRenderer` | |
| `:298` | `class TessBoxTextRenderer` | |
| `:309` | `class TessWordStrBoxRenderer` | |
| `:322` | `class TessOsdRenderer` (legacy) | |

### 2.e Other public headers

| Path:line | Symbol | Note |
|---|---:|---|
| `include/tesseract/ocrclass.h:59` | `struct EANYCODE_CHAR` | |
| `:98-100` | `CANCEL_FUNC`, `PROGRESS_FUNC`, `PROGRESS_FUNC2` (type aliases) | |
| `:102` | `class ETEXT_DESC` | progress/cancel callback struct |
| `:128` | `void set_deadline_msecs(int)` | |
| `:136` | `bool deadline_exceeded() const` | |
| `include/tesseract/osdetect.h:38` | `struct OSBestResult` | |
| `:47` | `struct OSResults` | |
| `:83` | `class OrientationDetector` | |
| `:95` | `class ScriptDetector` | |
| `:116` | `int orientation_and_script_detection(...)` | |
| `:119` | `int os_detect(...)` | |
| `:122` | `int os_detect_blobs(...)` | |
| `:126` | `bool os_detect_blob(...)` | |
| `include/tesseract/unichar.h:55` | `class TESS_API UNICHAR` | |
| `include/tesseract/version.h.in:30` | `TESSERACT_VERSION_STR` template | generated at CMake `:540` |
| `include/tesseract/export.h:19-35` | `TESS_API` macro | dllexport / `__attribute__((visibility("default")))` |

---

## 3. `src/api/` — public-API façade (10 files, 2354+274+711+524+106+1139+1000+244+105+274 lines)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/api/baseapi.cpp:172` | `// InternalSetImage` comment | |
| `src/api/baseapi.cpp:300` | `int TessBaseAPI::Init(...)` | full Init |
| `src/api/baseapi.cpp:303` | 3-arg Init delegates to 7-arg | |
| `src/api/baseapi.cpp:310` | 9-arg Init (in-memory data) | |
| `src/api/baseapi.cpp:376` | `TessBaseAPI::GetInitLanguagesAsString() const` | |
| `src/api/baseapi.cpp:411` | `TessBaseAPI::InitForAnalysePage()` | |
| `src/api/baseapi.cpp:467` | `TessBaseAPI::TesseractRect(...)` | ROI OCR shortcut |
| `src/api/baseapi.cpp:480` | inside TesseractRect, returns `GetUTF8Text()` | |
| `src/api/baseapi.cpp:488` | `TessBaseAPI::ClearAdaptiveClassifier()` | |
| `src/api/baseapi.cpp:506` | `TessBaseAPI::SetImage(imagedata,...)` | raw buffer overload |
| `src/api/baseapi.cpp:529` | `TessBaseAPI::SetImage(Pix *)` | Leptonica overload |
| `src/api/baseapi.cpp:762` | `int TessBaseAPI::Recognize(ETEXT_DESC *)` | main recognizer |
| `src/api/baseapi.cpp:878` | `TessBaseAPI::ProcessPagesFileList(...)` | |
| `src/api/baseapi.cpp:958` | `TessBaseAPI::ProcessPagesMultipageTiff(...)` | |
| `src/api/baseapi.cpp:999` | `TessBaseAPI::ProcessPages(...)` | public entry |
| `src/api/baseapi.cpp:1033` | `TessBaseAPI::ProcessPagesInternal(...)` | |
| `src/api/baseapi.cpp:1056-1128` | libcurl remote-image path | |
| `src/api/baseapi.cpp:1142` | `findFileFormat` autodetect (PNG/JPEG/TIFF/PDF/PNM) | |
| `src/api/baseapi.cpp:1196` | `TessBaseAPI::ProcessPage(Pix *, ...)` | per-page loop |
| `src/api/baseapi.cpp:1280` | `TessBaseAPI::GetIterator()` | returns `ResultIterator *` |
| `src/api/baseapi.cpp:1297` | `TessBaseAPI::GetMutableIterator()` | returns `MutableIterator *` |
| `src/api/baseapi.cpp:1307` | `TessBaseAPI::GetUTF8Text()` | |
| `src/api/baseapi.cpp:1353` | `TessBaseAPI::GetTSVText(int)` | |
| `src/api/baseapi.cpp:1497` | `TessBaseAPI::GetBoxText(int)` | |
| `src/api/baseapi.cpp:1653` | `TessBaseAPI::DetectOrientationScript(...)` | |
| `src/api/baseapi.cpp:1689` | `TessBaseAPI::GetOsdText(int)` | |
| `src/api/baseapi.cpp:1719` | `TessBaseAPI::MeanTextConf()` | |
| `src/api/baseapi.cpp:1737` | `TessBaseAPI::AllWordConfidences()` | |
| `src/api/baseapi.cpp:1777` | `TessBaseAPI::AdaptToWordStr(...)` | legacy |
| `src/api/baseapi.cpp:1845` | `TessBaseAPI::Clear()` | |
| `src/api/baseapi.cpp:1861` | `TessBaseAPI::End()` | |
| `src/api/baseapi.cpp:1995` | `TessBaseAPI::Threshold(Pix **)` | |
| `src/api/baseapi.cpp:2070` | `TessBaseAPI::FindLines()` | |
| `src/api/baseapi.cpp:2299` | `MutableIterator *result_it = GetMutableIterator();` | inside TSV path |
| `src/api/capi.cpp:415` | `TessMutableIterator *TessBaseAPIGetMutableIterator(...)` | C-API wrapper |
| `src/api/renderer.cpp:88` | `TessResultRenderer::AddImage(...)` | invokes `AddImageHandler` |
| `src/api/renderer.cpp:139` | `TessTextRenderer::AddImageHandler` | writes `*.txt` |
| `src/api/renderer.cpp:179` | `TessTsvRenderer::AddImageHandler` | |
| `src/api/renderer.cpp:196` | `TessUnlvRenderer::AddImageHandler` | |
| `src/api/renderer.cpp:213` | `TessBoxTextRenderer::AddImageHandler` | |
| `src/api/renderer.cpp:231` | `TessOsdRenderer::AddImageHandler` | |
| `src/api/hocrrenderer.cpp:513` | `TessHOcrRenderer::AddImageHandler` | |
| `src/api/altorenderer.cpp:80` | `TessAltoRenderer::AddImageHandler` | |
| `src/api/pagerenderer.cpp:628` | `TessPAGERenderer::AddImageHandler` | |
| `src/api/pdfrenderer.cpp:827` | `TessPDFRenderer::AddImageHandler` | embeds `tessdata/pdf.ttf` |
| `src/api/lstmboxrenderer.cpp:95` | `TessLSTMBoxRenderer::AddImageHandler` | |
| `src/api/wordstrboxrenderer.cpp:94` | `TessWordStrBoxRenderer::AddImageHandler` | |

---

## 4. `src/ccmain/` — controller layer (45 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/ccmain/pagesegmain.cpp:101` | `Tesseract::SegmentPage(...)` | |
| `:201` | `Tesseract::AutoPageSeg(...)` | |
| `:272` | `Tesseract::SetupPageSegAndDetectOrientation(...)` | |
| `:309` | calls `Textord::find_components` | |
| `:366` | calls `os_detect_blobs` | |
| `src/ccmain/thresholder.cpp:182` | `ImageThresholder::Threshold(...)` | |
| `:284` | `ImageThresholder::ThresholdToPix(...)` | Otsu/Sauvola |
| `src/ccmain/linerec.cpp:229` | `Tesseract::LSTMRecognizeWord(...)` | |
| `src/ccmain/tesseractclass.cpp:2064` | `Tesseract::dictionary_correction_pass(...)` | |
| `src/ccmain/output.cpp:39` | `Tesseract::output_pass(...)` | |
| `src/ccmain/tessedit.cpp:171-172` | `init_lstm_components(...)` | constructs `LSTMRecognizer` |
| `src/ccmain/tfacepp.cpp:37` | `Tesseract::recog_word(WERD_RES *)` | legacy entry |
| `src/ccmain/tesseractclass.h:524` | `Tesseract::recognize_page(std::string &)` | declared-only (no def) |
| `src/ccmain/reject.cpp:227-251` | `compute_reject_threshold()` | |
| `src/ccmain/mutableiterator.h:51` | `class TESS_API MutableIterator` | (also under `include/`) |

---

## 5. `src/ccutil/` — generic utilities (43 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/ccutil/params.h` | `class Params`, `class ParamsVectors` | runtime config |
| `src/ccutil/tessdatamanager.cpp` | `.traineddata` reader; `HAVE_LIBARCHIVE` gates | |
| `src/ccutil/unicharset.*` | `UNICHARSET`, `UNICHAR` impls | |
| `src/ccutil/bitvector.*` | `BIT_VECTOR` | |
| `src/ccutil/ambigs.*` | ambiguity tables | |
| `src/ccutil/elst.h` | linked-list macros `ELISTIZE` | |
| `src/ccutil/errcode.cpp` | tesseract error codes | |

---

## 6. `src/lstm/` — LSTM engine (36 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/lstm/lstmrecognizer.cpp:247` | `LSTMRecognizer::RecognizeLine` (single) | |
| `src/lstm/lstmrecognizer.cpp:320` | full version | |
| `src/lstm/weightmatrix.cpp:28` | `#if defined(ANDROID)` guard | |
| `src/lstm/generate_lut.py` | Python pre-build script | |

---

## 7. `src/wordrec/` — legacy word recognizer (32 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/wordrec/chopper.cpp:385` | `Wordrec::chop_word_main(WERD_RES *)` | |
| `src/wordrec/segsearch.cpp:33` | `Wordrec::SegSearch(...)` | |
| `src/wordrec/language_model.cpp:45` | `#if defined(ANDROID)` guard | |
| `src/wordrec/language_model.cpp:1235` | `LanguageModel::UpdateBestChoice(...)` | |
| `src/wordrec/wordrec.h:193` | `tessedit_certainty_threshold` | |

---

## 8. `src/textord/` — text-line ordering / page segmentation (79 files)

| Path | Symbol | Note |
|---|---|---|
| `src/textord/colfind.cpp` | `ColumnFinder::FindBlocks` | page segmentation |
| `src/textord/colfind.h` | `ColumnFinder::SetupAndFilterNoise` | |
| `src/textord/textord.h` | `Textord::TextordPage` | top-level driver |
| `src/textord/{makerow,pitsync,tabfind,table,blks}.cpp` | page-block internal stages | |

---

## 9. `src/dict/` — dictionary (14 files)

| Path | Symbol | Note |
|---|---|---|
| `src/dict/dawg.cpp` | `Dawg` | |
| `src/dict/trie.cpp` | `Trie` | |
| `src/dict/dict.cpp` | `Dict::is_valid_word`, `Dict::probability_in_context_` | |
| `src/dict/stopper.cpp` | `Stopper` | |
| `src/dict/{hyphen,permdawg,dawg_cache}.cpp` | | |

---

## 10. `src/arch/` — SIMD dispatch (15 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/arch/simddetect.cpp:57` | `#if defined(ANDROID)` | |
| `src/arch/simddetect.cpp:227` | `android_getCpuFeatures()` runtime | |
| `src/arch/simddetect.{h,cpp}` | `SIMDDetect::IsNEONAvailable`, AVX/AVX2/AVX512F/FMA/SSE4.1 | |

---

## 11. `src/training/` — training executables (19 files)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/training/unicharset_extractor.cpp:103` | `main` | |
| `src/training/shapeclustering.cpp:44` | `main` | legacy |
| `src/training/mftraining.cpp:193` | `main` | legacy |
| `src/training/cntraining.cpp:103` | `main` | legacy |
| `src/training/wordlist2dawg.cpp:33` | `main` | |
| `src/training/dawg2wordlist.cpp:71` | `main` | |
| `src/training/lstmtraining.cpp:76` | `main` | LSTM |
| `src/training/lstmeval.cpp:32` | `main` | LSTM |
| `src/training/merge_unicharsets.cpp:22` | `main` | |
| `src/training/set_unicharset_properties.cpp:25` | `main` | |
| `src/training/combine_tessdata.cpp:117` | `main` | merges to `.traineddata` |
| `src/training/text2image.cpp:713` | `main` | renders training text |
| `src/training/combine_lang_model.cpp:42` | `main` | optional |
| `src/training/ambiguous_words.cpp:30` | `main` | optional |
| `src/training/classifier_tester.cpp:100` | `main` | optional |

---

## 12. `src/viewer/` — ScrollView TCP server (6 files)

| Path | Symbol | Note |
|---|---|---|
| `src/viewer/scrollview.cpp` | `ScrollView::Server` | TCP server on port 8461 |
| `src/viewer/scrollview.h` | IPC struct definitions (mirrored by `java/.../events/SVEvent.java`) | |
| `src/viewer/svmnode.cpp` | `SVMenuNode` tree primitives | |
| `src/viewer/svutil.cpp` | helpers | |

---

## 13. `src/classify/` — legacy feature extraction (52 files, gated by `DISABLED_LEGACY_ENGINE`)

| Path | Symbol |
|---|---|
| `src/classify/intfx.cpp` | feature extraction |
| `src/classify/picofeat.cpp` | pico-features |
| `src/classify/mfoutline.cpp` | micro-features |
| `src/classify/outfeat.cpp` | |
| `src/classify/intmatcher.cpp` | |
| `src/classify/intproto.cpp` | |
| `src/classify/kdtree.cpp` | KD-tree prototype matcher |
| `src/classify/normmatch.cpp` | normalization match |
| `src/classify/adaptmatch.cpp` | adaptive match |
| `src/classify/shapeclassifier.cpp` | |

---

## 14. `src/tesseract.cpp` — CLI entry (864 lines)

| Path:line | Symbol | Note |
|---|---:|---|
| `src/tesseract.cpp:98` | `static void PrintVersionInfo()` | banner |
| `src/tesseract.cpp:155` | `static void PrintHelpForPSM()` | |
| `src/tesseract.cpp:183` | `static void PrintHelpForOEM()` | |
| `src/tesseract.cpp:194` | `static void PrintHelpExtra(...)` | full help |
| `src/tesseract.cpp:255` | `static void PrintHelpMessage(...)` | short help |
| `src/tesseract.cpp:275` | `static void PrintLangsList(...)` | `--list-langs` |
| `src/tesseract.cpp:300` | `static void FixPageSegMode(...)` | coerces lib default to CLI's `PSM_AUTO` |
| `src/tesseract.cpp:366` | `static bool ParseArgs(...)` | argv scanner |
| `src/tesseract.cpp:503` | `static void PreloadRenderers(...)` | constructs renderer chain |
| `src/tesseract.cpp:510-634` | renderer chain (TXT/HOCR/ALTO/PAGE/TSV/PDF/UNLV/LSTMBox/BoxText/WordStrBox) | |
| `src/tesseract.cpp:650` | `static int main1(...)` | real work |
| `src/tesseract.cpp:670-674` | default `OEM_LSTM_ONLY` | |
| `src/tesseract.cpp:714` | `TessBaseAPI api;` | construct |
| `src/tesseract.cpp:718` | `api.Init(...)` | |
| `src/tesseract.cpp:752` | `FixPageSegMode(api, pagesegmode)` | |
| `src/tesseract.cpp:836` | `PreloadRenderers(api, renderers, ...)` | |
| `src/tesseract.cpp:845` | `api.ProcessPages(image, nullptr, 0, renderers[0].get())` | |
| `src/tesseract.cpp:855` | `int main(int argc, char **argv)` | try/catch wrapper |

---

## 15. `java/` — Swing ScrollView (desktop only)

| Path | Symbol | Note |
|---|---|---|
| `java/com/google/scrollview/ScrollView.java:32` | `public class ScrollView` | TCP client |
| `:35` | `SERVER_PORT = 8461` | |
| `java/com/google/scrollview/ui/SVWindow.java:40` | `import javax.swing.JFrame;` | Swing |
| `:24-36` | `java.awt.*` imports | AWT |
| `:24` | `org.piccolo2d.nodes.PImage` | Piccolo2D scenegraph |
| `java/com/google/scrollview/events/SVEvent.java:1-20` | IPC structs (matches C `scrollview.h`) | |
| `java/com/google/scrollview/ui/{SVAbstractMenuItem,SVCheckboxMenuItem,SVEmptyMenuItem,SVImageHandler,SVMenuBar,SVMenuItem,SVPopupMenu,SVSubMenuItem}.java` | menu primitives | |

---

## 16. `tessdata/` — config only, no models

| Path | Note |
|---|---|
| `tessdata/Makefile.am` | install rules |
| `tessdata/configs/` | 24 param files (txt, hocr, alto, page, tsv, pdf, unlv, lstmbox, box, wordstrbox, …) |
| `tessdata/tessconfigs/` | 6 legacy config files |
| `tessdata/eng.user-words` | example user word list |
| `tessdata/eng.user-patterns` | example regex patterns |
| `tessdata/pdf.ttf` | font bundled for `TessPDFRenderer` |
| **`.traineddata`** | **NOT SHIPPED** — must download from `github.com/tesseract-ocr/tessdata` |

---

## 17. `cmake/` — build helpers

| Path | Note |
|---|---|
| `cmake/BuildFunctions.cmake` | helper fns |
| `cmake/CheckFunctions.cmake` | function checks |
| `cmake/Configure.cmake` | project-wide configure |
| `cmake/SourceGroups.cmake` | IDE source grouping |
| `cmake/SourceLists.cmake` | defines `TESSERACT_SRC_API`, …, `_LSTM` etc. |
| `cmake/BuildOptimizations.cmake` | SIMD/LTO |
| `cmake/templates/cmake_uninstall.cmake.in` | uninstall target template |
| `cmake/templates/TesseractConfig.cmake.in` | `find_package(Tesseract)` config |

---

## 18. `unittest/` — GoogleTest tests (74+ files, off by default)

Top examples (enabled with `-DBUILD_TESTS=ON`):
- `unittest/baseapi_test.cc`
- `unittest/capiexample_test.cc`
- `unittest/apiexample_test.cc`
- `unittest/lstm_test.cc`
- `unittest/lstmtrainer_test.cc`
- `unittest/validator_test.cc`
- `unittest/loadlang_test.cc`

---

## 19. Quick lookup by symbol

| You want… | Look at… |
|---|---|
| version string | `VERSION:1` |
| main CLI | `src/tesseract.cpp:855` |
| public façade class | `include/tesseract/baseapi.h:76` |
| full Init | `include/tesseract/baseapi.h:197` (impl `src/api/baseapi.cpp:300`) |
| pre-segmented ROI OCR | `include/tesseract/baseapi.h:282` (impl `src/api/baseapi.cpp:467`) |
| 11 output formats | `src/tesseract.cpp:510-634` (`PreloadRenderers`) |
| 14 PSM enum values | `include/tesseract/publictypes.h:157-178` |
| 4 OEM enum values | `include/tesseract/publictypes.h:263-277` |
| LSTM recognizer | `src/lstm/lstmrecognizer.cpp:247` |
| legacy recognizer | `src/wordrec/chopper.cpp:385` |
| OSD entry | `include/tesseract/osdetect.h:116-126` |
| Leptonica version | `configure.ac:487`, `CMakeLists.txt:445` |
| Android NDK branch | `CMakeLists.txt:851-858` |
| `.traineddata` reader | `src/ccutil/tessdatamanager.cpp` |
| combined-traineddata build | `src/training/combine_tessdata.cpp:117` |
| renderer chain | `include/tesseract/renderer.h:54` (`insert`) |