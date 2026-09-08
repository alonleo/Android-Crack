# 03 — Architecture

This document presents two complementary views of the Tesseract architecture:

1. **Module dependency graph** — who calls whom across the 14 `src/` modules.
2. **Class hierarchy** — the inheritance chain from `PageIterator` up through
   `MutableIterator`, and the renderer hierarchy from `TessResultRenderer`.

A third diagram shows the **startup flow** from `main()` to first user-visible
output, satisfying the codebase-deep-documentation requirement of one
flowchart-style top-level entry.

---

## 3.1 Module dependency graph

```mermaid
flowchart TD
    CLI[tesseract CLI<br/>src/tesseract.cpp]
    LIB[libtesseract<br/>CMakeLists.txt:735]
    API[src/api/<br/>TessBaseAPI + renderers]
    CCMAIN[src/ccmain/<br/>Tesseract class]
    LSTM[src/lstm/<br/>LSTM engine]
    WORDREC[src/wordrec/<br/>legacy recognizer]
    TEXTORD[src/textord/<br/>page segmentation]
    CCSTRUCT[src/ccstruct/<br/>data structures]
    CCUTIL[src/ccutil/<br/>utils + TessdataManager]
    DICT[src/dict/<br/>Dawg/Trie/Dict]
    CLASSIFY[src/classify/<br/>legacy features]
    ARCH[src/arch/<br/>SIMD dispatch]
    VIEWER[src/viewer/<br/>ScrollView TCP server]
    TRAINING[src/training/<br/>training executables]
    CUTIL[src/cutil/<br/>tiny helpers]
    LEPT[Leptonica ≥1.74<br/>external dep]

    CLI --> LIB
    LIB --> API
    API --> CCMAIN
    API --> LEPT
    CCMAIN --> LSTM
    CCMAIN --> WORDREC
    CCMAIN --> TEXTORD
    CCMAIN --> CCSTRUCT
    CCMAIN --> CCUTIL
    LSTM --> CCUTIL
    LSTM --> ARCH
    LSTM --> LEPT
    WORDREC --> CLASSIFY
    WORDREC --> CCSTRUCT
    WORDREC --> CCUTIL
    WORDREC --> DICT
    CLASSIFY --> CCSTRUCT
    CLASSIFY --> CCUTIL
    CLASSIFY --> ARCH
    TEXTORD --> CCSTRUCT
    TEXTORD --> CCUTIL
    TEXTORD --> ARCH
    CCSTRUCT --> CCUTIL
    CCSTRUCT --> LEPT
    CCUTIL --> DICT
    CCUTIL --> LEPT
    DICT --> CCUTIL
    TRAINING --> CCUTIL
    TRAINING --> LSTM
    TRAINING --> WORDREC
    TRAINING --> CCSTRUCT
    VIEWER --> CCUTIL
    CUTIL -.->|legacy| CCUTIL

    classDef facade fill:#ffd,stroke:#333
    classDef engine fill:#ddf,stroke:#333
    classDef ext fill:#fdd,stroke:#333
    class API facade
    class CCMAIN,LSTM,WORDREC,TEXTORD,CCSTRUCT engine
    class LEPT ext
```

Key observations:

- **`src/api/`** is the only module that the user-facing C++/C API touches.
  Everything else is hidden behind `TessBaseAPI`.
- **`src/ccmain/`** is the central orchestrator (the `Tesseract` class).
- **`src/lstm/`** is the modern recognizer; **`src/wordrec/`** is legacy,
  dispatched by `OEM_TESSERACT_ONLY` (`src/ccmain/tessedit.cpp:171-172`).
- **Leptonica** is the only external hard dependency — it provides `Pix`,
  the image class Tesseract uses internally.

---

## 3.2 Class hierarchy — iterators

```mermaid
classDiagram
    class PageIterator {
        <<abstract>>
        +Begin() void
        +RestartParagraph() void
        +RestartRow() void
        +Next(level) bool
        +IsAtBeginningOf(level) bool
        +IsAtFinalElement(lvl, el) bool
        +Cmp(other) bool
        +BoundingBox(level, l, t, r, b) void
        +Baseline(...) void
        +RowAttributes(...) void
        +Orientation(...) void
        +ParagraphInfo(...) void
    }
    class LTRResultIterator {
        +GetUTF8Text(level) char*
        +Confidence(level) int
        +WordFontAttributes(...) void
        +WordRecognitionLanguage() const char*
        +WordIsFromDictionary() bool
        +WordIsNumeric() bool
        +WordTruthUTF8Text() const char*
        +WordLattice(...) void
        +SymbolIsSuperscript() bool
        +SymbolIsSubscript() bool
        +SymbolIsDropcap() bool
    }
    class ResultIterator {
        +~ResultIterator() override
    }
    class MutableIterator {
        +PageResIt() const PAGE_RES_IT*
    }
    class ChoiceIterator {
        +Next() bool
        +GetUTF8Text() const char*
        +Confidence() int
    }

    PageIterator <|-- LTRResultIterator
    LTRResultIterator <|-- ResultIterator
    ResultIterator <|-- MutableIterator
    LTRResultIterator ..> ChoiceIterator : nested inner class
```

Hierarchy summary:

| Class | Header:line | Role |
|---|---|---|
| `PageIterator` | `include/tesseract/pageiterator.h:50` | layout-only traversal (block → para → line → word → symbol) |
| `LTRResultIterator` | `include/tesseract/ltrresultiterator.h:45` | adds text extraction; for LTR (Latin) scripts |
| `ResultIterator` | `include/tesseract/resultiterator.h:32` | adds recognition-specific helpers |
| `MutableIterator` | `src/ccmain/mutableiterator.h:51` | exposes internal `PAGE_RES_IT *` |
| `ChoiceIterator` | `include/tesseract/ltrresultiterator.h:180` | nested in LTR; alternative word choices with confidences |

> **Lifespan warning** (every header repeats this): `PageIterator` and its
> subclasses point to data inside `TessBaseAPI`; calling `Init/SetImage/Recognize/Clear/End/DetectOS`
> invalidates them.

---

## 3.3 Class hierarchy — renderers

```mermaid
classDiagram
    class TessResultRenderer {
        <<abstract>>
        +insert(next) void
        +BeginDocumentHandler() bool
        +AddImageHandler(api) bool
        +EndDocumentHandler() bool
    }
    class TessTextRenderer
    class TessHOcrRenderer
    class TessAltoRenderer
    class TessPAGERenderer
    class TessTsvRenderer
    class TessPDFRenderer
    class TessUnlvRenderer
    class TessLSTMBoxRenderer
    class TessBoxTextRenderer
    class TessWordStrBoxRenderer
    class TessOsdRenderer

    TessResultRenderer <|-- TessTextRenderer
    TessResultRenderer <|-- TessHOcrRenderer
    TessResultRenderer <|-- TessAltoRenderer
    TessResultRenderer <|-- TessPAGERenderer
    TessResultRenderer <|-- TessTsvRenderer
    TessResultRenderer <|-- TessPDFRenderer
    TessResultRenderer <|-- TessUnlvRenderer
    TessResultRenderer <|-- TessLSTMBoxRenderer
    TessResultRenderer <|-- TessBoxTextRenderer
    TessResultRenderer <|-- TessWordStrBoxRenderer
    TessResultRenderer <|-- TessOsdRenderer
```

Composition: `TessResultRenderer::insert()` (`include/tesseract/renderer.h:54`)
chains renderers so a single `ProcessPages` call can produce multiple output
formats in parallel (e.g. `.txt` + `.pdf`).

---

## 3.4 Startup flow — from `main()` to first OCR result

```mermaid
flowchart TD
    A([main argc argv]) --> B[try/catch wrapper<br/>src/tesseract.cpp:855]
    B --> C[main1<br/>src/tesseract.cpp:650]
    C --> D[ParseArgs<br/>src/tesseract.cpp:366]
    D --> E[TessBaseAPI api<br/>src/tesseract.cpp:714]
    E --> F[api.Init datapath, lang, OEM<br/>src/api/baseapi.cpp:300]
    F --> G[FixPageSegMode<br/>src/tesseract.cpp:300]
    G --> H[api.SetSourceResolution ppi]
    H --> I[PreloadRenderers<br/>src/tesseract.cpp:503]
    I --> J{Which output?}
    J -->|--tessedit_create_txt| K[TessTextRenderer]
    J -->|hocr| L[TessHOcrRenderer]
    J -->|alto| M[TessAltoRenderer]
    J -->|page_xml| N[TessPAGERenderer]
    J -->|tsv| O[TessTsvRenderer]
    J -->|pdf| P[TessPDFRenderer]
    J -->|unlv| Q[TessUnlvRenderer]
    J -->|lstmbox| R[TessLSTMBoxRenderer]
    J -->|boxfile| S[TessBoxTextRenderer]
    J -->|wordstrbox| T[TessWordStrBoxRenderer]
    K --> U[api.ProcessPages<br/>src/api/baseapi.cpp:999]
    L --> U
    M --> U
    N --> U
    O --> U
    P --> U
    Q --> U
    R --> U
    S --> U
    T --> U
    U --> V[ProcessPagesInternal<br/>src/api/baseapi.cpp:1033]
    V --> W[findFileFormat<br/>:1142]
    W --> X{format?}
    X -->|TIFF| Y[ProcessPagesMultipageTiff<br/>:958]
    X -->|PDF/PNG/JPG| Z[ProcessPage<br/>:1196]
    Y --> Z
    Z --> AA[SetImage + Recognize + AddImage<br/>per page]
    AA --> AB([out.txt / out.hocr / out.pdf / ...])
```

This flowchart covers both CLI and library entry points — `TessBaseAPI::ProcessPages`
is the same call regardless of which renderer chain was constructed.

---

## 3.5 Recognition pipeline — 7 stages

When `TessBaseAPI::Recognize(ETEXT_DESC *)` runs (`src/api/baseapi.cpp:762-844`),
the work flows through 7 stages. Each stage can be considered its own
subsystem; see [`INDEX.md`](./INDEX.md) § 4 for the file:line references.

```mermaid
flowchart LR
    IMG[Input image<br/>Pix or raw buffer] --> S1
    S1[1. Image loading & thresholding<br/>src/api/baseapi.cpp:2070 FindLines<br/>src/ccmain/thresholder.cpp:284 ThresholdToPix] --> S2
    S2[2. Component finding<br/>Textord::find_components<br/>src/ccmain/pagesegmain.cpp:309] --> S3
    S3[3. Layout / page segmentation<br/>src/ccmain/pagesegmain.cpp:272 SetupPageSegAndDetectOrientation<br/>src/textord/colfind.cpp FindBlocks] --> S4
    S4[4. Orientation & Script detection<br/>src/ccmain/pagesegmain.cpp:366<br/>os_detect_blobs include/tesseract/osdetect.h:122] --> S5
    S5{5. OEM dispatch<br/>init_lstm_components<br/>src/ccmain/tessedit.cpp:171-172}
    S5 -->|OEM_LSTM_ONLY| S5L[LSTM Recognizer<br/>src/lstm/lstmrecognizer.cpp:247 RecognizeLine<br/>src/ccmain/linerec.cpp:229 LSTMRecognizeWord]
    S5 -->|OEM_TESSERACT_ONLY| S5W[Legacy Recognizer<br/>src/wordrec/chopper.cpp:385 chop_word_main<br/>src/wordrec/segsearch.cpp:33 SegSearch]
    S5L --> S6
    S5W --> S6
    S6[6. Language model / dictionary<br/>src/wordrec/language_model.cpp:1235 UpdateBestChoice<br/>src/dict/dict.cpp probability_in_context_] --> S7
    S7[7. Output / rendering<br/>src/ccmain/output.cpp:39 output_pass<br/>src/api/renderer.cpp:88 AddImage] --> OUT[out.txt / hocr / pdf / …]
```

Legacy vs LSTM is selected at `Init` time. The dispatch happens once and is
cached in `Tesseract::AnyLSTMLang()` / `Tesseract::AnyTessLang()`.

---

## 3.6 Public-API encapsulation

`src/api/` is intentionally isolated (`cmake/SourceLists.cmake:5-15`):

```mermaid
flowchart LR
    subgraph Public[Public Surface]
        H1[include/tesseract/baseapi.h]
        H2[include/tesseract/capi.h]
        H3[include/tesseract/renderer.h]
        H4[include/tesseract/pageiterator.h]
        H5[include/tesseract/resultiterator.h]
        H6[include/tesseract/ltrresultiterator.h]
        H7[include/tesseract/publictypes.h]
        H8[include/tesseract/osdetect.h]
        H9[include/tesseract/ocrclass.h]
        H10[include/tesseract/unichar.h]
        H11[include/tesseract/export.h]
        H12[include/tesseract/version.h.in]
    end
    subgraph Impl[src/api/ Implementation]
        I1[baseapi.cpp 2 354 lines]
        I2[capi.cpp 711 lines]
        I3[renderer.cpp 244 lines]
        I4[hocrrenderer.cpp 524 lines]
        I5[altorenderer.cpp 274 lines]
        I6[pagerenderer.cpp 1 139 lines]
        I7[pdfrenderer.cpp 1 000 lines]
        I8[lstmboxrenderer.cpp 106 lines]
        I9[wordstrboxrenderer.cpp 105 lines]
    end
    subgraph Engine[Engine: src/ccmain + lstm + wordrec + textord + ccstruct + ccutil + dict + classify]
        E[120 KLOC]
    end
    H1 --> I1
    H2 --> I2
    H3 --> I3
    H3 --> I4
    H3 --> I5
    H3 --> I6
    H3 --> I7
    H3 --> I8
    H3 --> I9
    I1 --> E
    I2 --> I1
    I4 --> E
    I5 --> E
    I6 --> E
    I7 --> E
    I3 --> E
    I8 --> E
    I9 --> E
```

`include/tesseract/*.h` is the *only* surface visible to library consumers;
no headers from `src/ccmain/` etc. are exposed.

See [`04_operation_chains.md`](./04_operation_chains.md) for end-to-end call
chains, and [`05_api_surface.md`](./05_api_surface.md) for the full
`TessBaseAPI` method table.