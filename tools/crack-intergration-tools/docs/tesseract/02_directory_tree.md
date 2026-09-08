# 02 — Directory Tree

Annotated tree of `tools/crack-intergration-tools/source-projects/tesseract/`.
File counts are from `find ... -type f \( -name "*.cpp" -o -name "*.h" \)` and
are grep-verified.

```
tesseract/                              # <repo> = project root
├── VERSION                             # 1 line: 5.5.3
├── LICENSE                             # Apache-2.0 full text
├── README.md                           # install/build/run instructions
├── INSTALL                             # autotools install notes
├── INSTALL.GIT.md                      # git-submodule hint (leptonica)
├── ChangeLog                           # release notes
├── AUTHORS                             # contributor list
├── CITATIONS.bib                       # BibTeX
├── CONTRIBUTING.md                     # contribution rules
├── SECURITY.md                         # vuln disclosure
│
├── CMakeLists.txt                      # PRIMARY BUILD (974 lines)
├── configure.ac                        # autotools (627 lines)
├── Makefile.am                         # autotools top-level (60 KB)
├── autogen.sh                          # bootstrap autotools
│
├── tesseract.pc.in                     # pkg-config (autotools)
├── tesseract.pc.cmake                  # pkg-config (cmake)
├── sw.cpp                              # 12 963-byte C++17 single-header wrapper
│
├── include/tesseract/                  # ===== PUBLIC C++ HEADERS (12 files) =====
│   ├── baseapi.h                       # TessBaseAPI class (820 lines)
│   ├── capi.h                          # C API (625 lines, 100+ entries)
│   ├── export.h                        # TESS_API macro (37 lines)
│   ├── pageiterator.h                  # PageIterator class (364 lines)
│   ├── resultiterator.h                # ResultIterator class (250 lines)
│   ├── ltrresultiterator.h             # LTRResultIterator + ChoiceIterator (235 lines)
│   ├── renderer.h                      # TessResultRenderer hierarchy (334 lines)
│   ├── publictypes.h                   # enums (PSM, OEM, RIL, …) (281 lines)
│   ├── ocrclass.h                      # EANYCODE_CHAR, ETEXT_DESC (158 lines)
│   ├── osdetect.h                      # OSBestResult, OrientationDetector (136 lines)
│   ├── unichar.h                       # UNICHAR class (174 lines)
│   └── version.h.in                    # generated → include/tesseract/version.h
│
├── src/                                # ===== ENGINE (489 .cpp/.h files) =====
│   │
│   ├── tesseract.cpp                   # CLI main() at line 855; main1() at 650
│   ├── svpaint.cpp                     # standalone paint tool using ScrollView
│   │
│   ├── api/                            # ── 10 files ── public façade + renderers
│   │   ├── baseapi.cpp                 # TessBaseAPI class (2 354 lines)
│   │   ├── capi.cpp                    # extern "C" wrappers (711 lines)
│   │   ├── renderer.cpp                # base + TXT/TSV/UNLV/Box/Osd renderers (244 lines)
│   │   ├── hocrrenderer.cpp            # hOCR (524 lines)
│   │   ├── altorenderer.cpp            # ALTO XML (274 lines)
│   │   ├── pagerenderer.cpp            # PAGE XML (1 139 lines)
│   │   ├── pdfrenderer.cpp             # searchable PDF (1 000 lines, embeds pdf.ttf)
│   │   ├── pdf_ttf.h                   # embedded font table for PDF
│   │   ├── lstmboxrenderer.cpp         # LSTM .box (106 lines)
│   │   └── wordstrboxrenderer.cpp      # wordstr .box (105 lines)
│   │
│   ├── arch/                           # ── 15 files ── SIMD dispatch
│   │   ├── simddetect.cpp              # runtime SIMD detection (ANDROID branch @ 227)
│   │   ├── dotproduct.{h,cpp}          # int / float dot-product
│   │   ├── intsimdmatrix.{h,cpp}       # int-simd matrix
│   │   ├── dotproductsse.cpp, dotproductsse41.cpp,
│   │   │   dotproductavx.cpp, dotproductavx2.cpp, dotproductavx512.cpp,
│   │   │   dotproductfma.cpp, dotproductneon.cpp, dotproductrvv.cpp
│   │   └── …
│   │
│   ├── ccmain/                         # ── 45 files ── Tesseract main controller
│   │   ├── tesseractclass.{h,cpp}      # Tesseract class (top-level)
│   │   ├── pagesegmain.cpp             # SetupPageSegAndDetectOrientation, AutoPageSeg
│   │   ├── thresholder.{h,cpp}         # ImageThresholder (Otsu/Sauvola)
│   │   ├── osdetect.{h,cpp}            # OrientationDetector, ScriptDetector
│   │   ├── linerec.cpp                 # LSTMRecognizeWord
│   │   ├── tfacepp.cpp                 # recog_word (legacy)
│   │   ├── output.cpp                  # output_pass
│   │   ├── reject.cpp                  # compute_reject_threshold
│   │   ├── control.{h,cpp}             # ETEXT_CTRL signals
│   │   ├── fixspace.{h,cpp}            # space fixup
│   │   ├── docqual.{h,cpp}             # document quality
│   │   ├── equationdetect.{h,cpp}      # equation detection
│   │   ├── applybox.{h,cpp}            # apply box training data
│   │   ├── adaptions.{h,cpp}           # language adaptations
│   │   ├── mutableiterator.h           # MutableIterator class (in ccmain!)
│   │   ├── ltrresultiterator.{h,cpp}   # impl
│   │   ├── pageiterator.{h,cpp}        # impl
│   │   ├── resultiterator.{h,cpp}      # impl
│   │   └── tessedit.cpp                # init_lstm_components
│   │
│   ├── ccstruct/                       # ── 74 files ── core data structures
│   │   ├── image.{h,cpp}               # IMAGE struct
│   │   ├── blob.{h,cpp}, blobs.{h,cpp} # BLOB, BLOBS
│   │   ├── werd.{h,cpp}                # WERD
│   │   ├── row.{h,cpp}                 # ROW
│   │   ├── block.{h,cpp}               # BLOCK
│   │   ├── polyblk.{h,cpp}             # POLY_BLOCK
│   │   ├── pageres.{h,cpp}             # PAGE_RES
│   │   ├── wordres.{h,cpp}             # WERD_RES
│   │   ├── blamer.{h,cpp}              # BlamerBundle
│   │   ├── fontinfo.{h,cpp}            # font info
│   │   ├── imgs.{h,cpp}                # image read/write
│   │   ├── points.{h,cpp}, rect.{h,cpp}, poly.{h,cpp}
│   │   └── …                           # many small geometry helpers
│   │
│   ├── ccutil/                         # ── 43 files ── generic utilities
│   │   ├── params.h                    # Params, ParamsVectors runtime config
│   │   ├── tessdatamanager.{h,cpp}     # .traineddata reader (HAVE_LIBARCHIVE gates)
│   │   ├── unicharset.{h,cpp}          # UNICHARSET
│   │   ├── unichar.cpp                 # impl
│   │   ├── bitvector.{h,cpp}           # BIT_VECTOR
│   │   ├── elst.h, elst2.h, clst.h     # linked-list macros (ELISTIZE)
│   │   ├── ambigs.{h,cpp}              # ambiguity tables
│   │   ├── errcode.{h,cpp}             # tesseract error codes
│   │   ├── ccutil.{h,cpp}              # misc
│   │   ├── scanutils.{h,cpp}           # parsing helpers
│   │   ├── tprintf.{h,cpp}             # logging (tprintf)
│   │   └── …
│   │
│   ├── classify/                       # ── 52 files ── legacy feature extraction
│   │   ├── intfx.cpp                   # feature extraction
│   │   ├── picofeat.cpp                # pico-features
│   │   ├── mfoutline.cpp               # micro-features
│   │   ├── outfeat.cpp                 # outfeat
│   │   ├── intmatcher.cpp              # prototype matcher
│   │   ├── intproto.cpp                # prototypes
│   │   ├── kdtree.cpp                  # KD-tree matcher
│   │   ├── normmatch.cpp               # normalization match
│   │   ├── adaptmatch.cpp              # adaptive match
│   │   ├── shapeclassifier.cpp
│   │   └── …                           # gated by DISABLED_LEGACY_ENGINE
│   │
│   ├── cutil/                          # ── 3 files ── tiny old-list helpers
│   │   ├── oldlist.h
│   │   ├── cutil.h
│   │   └── cutil.cpp
│   │
│   ├── dict/                           # ── 14 files ── dictionary system
│   │   ├── dawg.{h,cpp}                # Dawg
│   │   ├── trie.{h,cpp}                # Trie
│   │   ├── dict.{h,cpp}                # Dict::is_valid_word, Dict::probability_in_context_
│   │   ├── stopper.{h,cpp}             # Stopper
│   │   ├── hyphen.{h,cpp}              # Hyphen
│   │   ├── permdawg.{h,cpp}            # PermDawg
│   │   └── dawg_cache.{h,cpp}          # DawgCache
│   │
│   ├── lstm/                           # ── 36 files ── LSTM engine
│   │   ├── lstmrecognizer.{h,cpp}      # LSTMRecognizer::RecognizeLine (247/320)
│   │   ├── network.{h,cpp}, series.{h,cpp}, plumbing.{h,cpp}
│   │   ├── convolution.{h,cpp}, maxpool.{h,cpp}, fullyconnected.{h,cpp}
│   │   ├── lstm.{h,cpp}, reversed.{h,cpp}, reconfig.{h,cpp}, recodebeam.{h,cpp}
│   │   ├── weightmatrix.{h,cpp}        # Android guard @ 28
│   │   ├── networkio.{h,cpp}, input.{h,cpp}, parallel.{h,cpp}
│   │   ├── staticshape.{h,cpp}, stridedmap.{h,cpp}
│   │   └── generate_lut.py             # Python build helper
│   │
│   ├── textord/                        # ── 79 files ── text-line ordering / page-seg
│   │   ├── textord.{h,cpp}             # Textord::TextordPage
│   │   ├── colfind.{h,cpp}             # ColumnFinder
│   │   ├── colpartition.{h,cpp}, colpartitionset.{h,cpp}, colpartitiongrid.{h,cpp}
│   │   ├── linefind.{h,cpp}, tabfind.{h,cpp}, tablerecog.{h,cpp}
│   │   ├── imagefind.{h,cpp}, makerow.{h,cpp}, pitsync.{h,cpp}, pithsync.{h,cpp}
│   │   ├── tabvector.{h,cpp}, alignedblob.{h,cpp}, baselinedetect.{h,cpp}
│   │   ├── blkocc.{h,cpp}, blobgrid.{h,cpp}, bbgrid.{h,cpp}
│   │   ├── fpchop.{h,cpp}, edgblob.{h,cpp}, wordseg.{h,cpp}
│   │   └── …
│   │
│   ├── training/                       # ── 19 files ── training executables
│   │   ├── unicharset_extractor.cpp    # main @ 103
│   │   ├── shapeclustering.cpp         # main @ 44  (legacy)
│   │   ├── mftraining.cpp              # main @ 193 (legacy)
│   │   ├── cntraining.cpp              # main @ 103 (legacy)
│   │   ├── wordlist2dawg.cpp           # main @ 33
│   │   ├── dawg2wordlist.cpp           # main @ 71
│   │   ├── lstmtraining.cpp            # main @ 76  (LSTM)
│   │   ├── lstmeval.cpp                # main @ 32  (LSTM)
│   │   ├── merge_unicharsets.cpp       # main @ 22
│   │   ├── set_unicharset_properties.cpp # main @ 25
│   │   ├── combine_tessdata.cpp        # main @ 117 — merges into .traineddata
│   │   ├── text2image.cpp              # main @ 713 — renders training text
│   │   ├── combine_lang_model.cpp      # main @ 42
│   │   ├── ambiguous_words.cpp         # main @ 30
│   │   └── classifier_tester.cpp       # main @ 100
│   │
│   ├── viewer/                         # ── 6 files ── ScrollView TCP server
│   │   ├── scrollview.{h,cpp}          # server, port 8461
│   │   ├── svmnode.{h,cpp}             # tree primitives
│   │   └── svutil.{h,cpp}              # helpers
│   │
│   └── wordrec/                        # ── 32 files ── legacy word recognizer
│       ├── chop_word_main → chopper.cpp : 385
│       ├── segsearch.cpp               # Wordrec::SegSearch @ 33
│       ├── initialsegsearch.cpp
│       ├── language_model.cpp          # LM::UpdateBestChoice @ 1235, ANDROID @ 45
│       ├── lm_consistency.cpp, lm_state.cpp, lm_pain_points.cpp
│       ├── outlines.cpp, pieces.cpp, plotedges.cpp, tface.cpp
│       └── wordrec.{h,cpp}             # Wordrec class
│
├── java/                               # ===== Swing ScrollView viewer (NOT Android) =====
│   ├── Manifest.txt
│   ├── Makefile.am
│   ├── com/
│   │   ├── Makefile.am
│   │   ├── google/
│   │   │   ├── Makefile.am
│   │   │   └── scrollview/
│   │   │       ├── Makefile.am
│   │   │       ├── ScrollView.java     # main entry, port 8461
│   │   │       ├── events/
│   │   │       │   ├── Makefile.am
│   │   │       │   ├── SVEvent.java
│   │   │       │   ├── SVEventHandler.java
│   │   │       │   └── SVEventType.java
│   │   │       └── ui/
│   │   │           ├── Makefile.am
│   │   │           ├── SVWindow.java   # imports javax.swing.JFrame @ 40
│   │   │           ├── SVAbstractMenuItem.java
│   │   │           ├── SVCheckboxMenuItem.java
│   │   │           ├── SVEmptyMenuItem.java
│   │   │           ├── SVImageHandler.java
│   │   │           ├── SVMenuBar.java
│   │   │           ├── SVMenuItem.java
│   │   │           ├── SVPopupMenu.java
│   │   │           └── SVSubMenuItem.java
│   │
├── tessdata/                           # ===== NO MODELS — configs only =====
│   ├── Makefile.am                     # install rules
│   ├── eng.user-words                  # example user word list
│   ├── eng.user-patterns               # example regex patterns
│   ├── pdf.ttf                         # font for PDF renderer
│   ├── configs/                        # 24 param files (txt, hocr, alto, page,
│   │   │                               #          tsv, pdf, unlv, lstmbox, box, …)
│   │   └── …
│   └── tessconfigs/                    # 6 legacy config files (batch, matdemo, …)
│       └── …
│
├── test/                               # EMPTY (placeholder for legacy make check)
│
├── unittest/                           # ===== GoogleTest (74+ files, OFF by default) =====
│   ├── third_party/googletest/         # vendored gtest
│   ├── baseapi_test.cc
│   ├── capiexample_test.cc
│   ├── apiexample_test.cc
│   ├── lstm_test.cc
│   ├── lstmtrainer_test.cc
│   ├── validator_test.cc
│   ├── loadlang_test.cc
│   └── …
│
├── doc/                                # ===== AsciiDoc man-pages + Doxyfile =====
│   ├── Doxyfile                        # Doxygen config
│   ├── tesseract.1.asc                 # main man page (AsciiDoc)
│   ├── lstmtraining.1.asc
│   └── tesseract.natvis                # MSVC visualizers (Natvis)
│
├── cmake/                              # ===== CMake helpers =====
│   ├── BuildFunctions.cmake
│   ├── CheckFunctions.cmake
│   ├── Configure.cmake
│   ├── SourceGroups.cmake
│   ├── SourceLists.cmake               # defines TESSERACT_SRC_API … _LSTM
│   ├── BuildOptimizations.cmake
│   └── templates/
│       ├── cmake_uninstall.cmake.in
│       └── TesseractConfig.cmake.in    # find_package(Tesseract) config
│
├── m4/                                 # ===== Autoconf macros =====
│   ├── ax_check_compile_flag.m4
│   └── ax_split_version.m4
│
├── snap/                               # ===== Snapcraft package =====
│   └── snapcraft.yaml
│
├── nsis/                               # ===== Windows NSIS installer =====
│   ├── tesseract.nsi
│   ├── build.sh
│   ├── find_deps.py
│   └── winpath.cpp
│
├── scripts/                            # **NOT PRESENT** — build helpers live in cmake/
│
└── .github/                            # ===== CI + issue templates =====
    ├── dependabot.yml
    ├── ISSUE_TEMPLATE/
    └── workflows/                      # GitHub Actions CI
```

## Module-size summary

| Module | .cpp+.h files | Lines (approx) | Purpose |
|---|---:|---:|---|
| `src/api/` | **10** | ~5 900 | public façade + 8 renderers |
| `src/arch/` | 15 | ~2 500 | SIMD dispatch |
| `src/ccmain/` | **45** | ~12 000 | Tesseract class + page-seg + OSD |
| `src/ccstruct/` | **74** | ~15 000 | data structures (IMAGE, BLOB, ROW, …) |
| `src/ccutil/` | 43 | ~8 000 | utils (Params, TessdataManager, UNICHARSET) |
| `src/classify/` | 52 | ~10 000 | legacy feature extraction (gated) |
| `src/cutil/` | 3 | <500 | tiny helpers |
| `src/dict/` | 14 | ~4 000 | dictionary |
| `src/lstm/` | **36** | ~10 000 | LSTM engine |
| `src/textord/` | **79** | ~18 000 | text-line ordering / page-seg |
| `src/training/` | 19 | ~4 000 | training executables |
| `src/viewer/` | 6 | ~2 000 | ScrollView TCP server |
| `src/wordrec/` | 32 | ~10 000 | legacy word recognizer |
| `src/api/tesseract.cpp` + `svpaint.cpp` | 2 | ~1 100 | CLI + paint tool |
| **Total** | **489** | **~120 000** | — |

## Module roles at a glance

```
                   ┌────────────────┐
                   │  src/api/      │  ← public façade
                   │  TessBaseAPI   │
                   └────────┬───────┘
                            │ uses
                   ┌────────▼────────┐
                   │  src/ccmain/    │  ← top-level controller
                   │  Tesseract      │
                   └──┬──────────┬───┘
                      │          │
       ┌──────────────▼─┐      ┌─▼─────────────┐
       │  src/lstm/     │      │  src/wordrec/ │ ← recognizer
       │  (LSTM only)   │      │  (legacy)     │   selection by
       └───────┬────────┘      └──────┬───────┘   OEM (init_lstm_components)
               │                      │
       ┌───────▼──────────────────────▼───────┐
       │          src/textord/ + ccstruct/   │ ← page segmentation
       └───────────────┬─────────────────────┘
                       │
              ┌────────▼────────┐
              │  src/ccutil/    │ ← utils, Params, TessdataManager
              └────────┬────────┘
                       │ uses
              ┌────────▼────────┐
              │  src/dict/      │ ← Dawg, Trie, Stopper
              └─────────────────┘
```

See [`03_architecture.md`](./03_architecture.md) for the full mermaid diagrams.