# 01 — Overview

## What is Tesseract?

**Tesseract OCR** is the canonical open-source OCR engine (currently maintained under
the `tesseract-ocr` GitHub organization, originally a Hewlett-Packard project from
1985–1995, open-sourced in 2005, and adopted by Google). It converts raster images
of text — PNG/JPEG/TIFF/PDF — into UTF-8 strings, hOCR XML, ALTO XML, PAGE XML,
TSV, searchable PDF, UNLV zones, or box files.

The version documented here is **5.5.3** (`VERSION:1`), released under **Apache-2.0**.
The codebase comprises **489 `.cpp`/`.h` files** in `src/` totalling roughly 130 KLOC,
plus a small Java Swing tool in `java/` for visualizing `.box` training files.

## Why this version matters

- **5.x** is the LSTM-lineage series: since 4.x the recognizer backend is a single
  LSTM that reads a whole text-line. The legacy "Tesseract 3.x" shape-classifier
  engine is still in the source tree under `src/classify/` and `src/wordrec/` but
  is gated by `DISABLED_LEGACY_ENGINE` (CMake option, default ON in 5.x).
- **5.5.3** is the latest stable as of inventory (2026-07-28).

## Language stack

| Layer | Language | Note |
|---|---|---|
| Engine | **C++17** (upgraded to C++20 if compiler allows) | `CMakeLists.txt:135-138` |
| CLI | C++ | `src/tesseract.cpp` (864 lines) |
| Public headers | C++ (namespace `tesseract::`) | `include/tesseract/*.h` (12 files) |
| C API | `extern "C"` wrappers | `include/tesseract/capi.h` (625 lines, 100+ entries) |
| Java | **Java Swing** (desktop), not Android | `java/com/google/scrollview/` |
| Python | one build helper only | `src/lstm/generate_lut.py` |

## Build systems (dual)

| System | File | Notes |
|---|---|---|
| **CMake** (primary) | `CMakeLists.txt` (974 lines) | requires ≥ 3.18; CMake option `-DBUILD_TESTS=ON` enables 74+ googletest files |
| **GNU Autotools** (legacy) | `configure.ac` (627 lines) + `Makefile.am` (60 KB) + `autogen.sh` | requires autoconf 2.69; builds from `./autogen.sh && ./configure && make` |

Both systems share `version.h.in` (`include/tesseract/version.h.in`), configured
in CMake at `CMakeLists.txt:540` and in autoconf at `configure.ac:546`.

## Hard and soft dependencies

| Dependency | Required? | Used for |
|---|---|---|
| **Leptonica ≥ 1.74** | **REQUIRED** (fatal if missing) | image load, threshold, box, Pix |
| pthread | required | threading |
| libarchive | optional | compressed `.traineddata` |
| libcurl | optional | `tesseract URL` remote image |
| ICU 52.1 | training only | character normalization |
| pango/cairo | training only | `text2image` rendering |
| libtiff | optional | TIFF load/save |
| OpenMP | optional | parallel Recognize |
| CpuFeaturesNdkCompat | Android only | `android_getCpuFeatures()` |
| SIMD (AVX/AVX2/AVX512/FMA/SSE4.1/NEON/RVV) | detected at configure | dot-product, int-simd-matrix |

See [`08_dependencies.md`](./08_dependencies.md) for full details.

## The `.traineddata` gap (CRITICAL)

The `tessdata/` directory ships **only** config templates, font (`pdf.ttf`),
and example user-dictionaries. It does **NOT** contain any `.traineddata`
language models:

```
$ find tessdata -name '*.traineddata' -o -name '*.traineddata.gz'
(empty)
```

Without models, `tesseract image.png out -l eng` fails with
`Could not initialize tesseract.` You must download at least:
- `eng.traineddata` (~22 MB) — English LSTM
- `chi_sim.traineddata` (~26 MB) — Simplified Chinese LSTM
- `osd.traineddata` (~10 MB) — Orientation & Script Detection

from <https://github.com/tesseract-ocr/tessdata> or the "fast" / "best" siblings.

## Java ≠ Android (READ THIS BEFORE YOU TRY TO EMBED)

The `java/` folder is a **desktop Swing + Piccolo2D viewer** of training `.box`
files. It is NOT an Android JNI bridge:

```java
import javax.swing.JFrame;                   // SVWindow.java:40
import java.awt.BasicStroke;                 // SVWindow.java:29
import org.piccolo2d.nodes.PImage;           // SVWindow.java:24
```

It talks over TCP to the C++ `scrollview` server compiled into `libtesseract`
(`src/viewer/scrollview.cpp`). The server listens on **port 8461**.

To use Tesseract on Android you must:
1. Cross-compile `libtesseract` + `libleptonica` for `arm64-v8a` / `armeabi-v7a`
   via the Android NDK (the `CMakeLists.txt:851-858` `ANDROID` branch pulls in
   `CpuFeaturesNdkCompat`).
2. Write your own JNI wrapper (`Java_com_example_tesseract_Tess_nativeRecognize`
   etc.) bridging `JNIEXPORT` to `tess::TessBaseAPI`.
3. Ship `eng.traineddata` (and friends) in `assets/`.

Established third-party Android wrappers (NOT in this repo):
- `adaptech-cz/Tesseract4Android` — pure-Java/Kotlin API on NDK-built libs
- `rmtheis/tess-two` — legacy Tess4J predecessor

## How Tesseract fits into the cracking pipeline

Tesseract is the **CPU-only, offline OCR backend** the workspace needs for the
game-UI image-translation step (stage 06 in `AGENTS.md`). Today the pipeline
calls **Unlimited-OCR** (Baidu's LLM-driven OCR via SGLang server, GPU-only)
through `tools/scripts/stage-06-ocr.sh`. Tesseract plugs in as a fallback when
no GPU is available, or as a quick-path when the GPU server is busy.

Full analysis: **[07_workflow_integration.md](./07_workflow_integration.md)**.

## Where to next

- Layout & directory tree → [`02_directory_tree.md`](./02_directory_tree.md)
- Architecture / class hierarchy → [`03_architecture.md`](./03_architecture.md)
- Lookup tables & grep index → [`INDEX.md`](./INDEX.md)
- Decision on whether to embed Tesseract → [`07_workflow_integration.md`](./07_workflow_integration.md)