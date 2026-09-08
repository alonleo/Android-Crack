# 06 — Build and Run

Tesseract ships with **two build systems** (CMake primary, Autotools legacy),
requires **Leptonica ≥ 1.74** as the only hard external dep, and has **two
primary delivery targets**: Linux desktop (CLI + library) and Android
(cross-compile via NDK, no in-tree JNI). This document collects every
verified command.

---

## 6.1 Linux desktop — CMake (recommended)

### Prerequisites

| Package | Version | Evidence |
|---|---|---|
| CMake | ≥ 3.18 | `CMakeLists.txt:12` |
| C++ compiler | C++17 (C++20 preferred) | `CMakeLists.txt:135-138` |
| Leptonica | ≥ 1.74 with zlib + libpng + libtiff | `CMakeLists.txt:445`, `README.md:122-126` |
| pthread | any | auto-detected |
| (optional) libarchive | any | compressed `.traineddata` |
| (optional) libcurl | any | `tesseract URL ...` remote image |
| (optional) libtiff | any | TIFF read/write |
| (optional) OpenMP | any | parallel Recognize |

Ubuntu install line:

```bash
sudo apt install build-essential cmake libleptonica-dev pkg-config \
                 zlib1g-dev libpng-dev libtiff-dev libarchive-dev \
                 libcurl4-openssl-dev
```

### Build & install

```bash
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

Outputs:

- `build/bin/tesseract` — CLI binary
- `build/libtesseract.so` (or `.a`) — library

Verify:

```bash
tesseract --version
# Should print: tesseract 5.5.3
#                leptonica 1.XX.X
#                libgif 5.2.x ... libjpeg ... libpng ... ...
```

---

## 6.2 Linux desktop — Autotools (alternative)

```bash
./autogen.sh
./configure --enable-training      # adds icu/pango/cairo requirements
make -j$(nproc)
sudo make install
sudo ldconfig
```

Required autotools: autoconf ≥ 2.69 (`configure.ac:8`).

---

## 6.3 Critical step — download `.traineddata` models

The `tessdata/` directory ships **only** config templates and `pdf.ttf`. No
language models. You must download at least:

| Model | Size | URL |
|---|---:|---|
| `eng.traineddata` | ~22 MB | `https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata` |
| `chi_sim.traineddata` | ~26 MB | `https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata` |
| `osd.traineddata` | ~10 MB | `https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata` |

Mirror options:
- `tessdata_fast` — smaller LSTM models (faster, slightly lower accuracy)
- `tessdata_best` — larger models (slower, higher accuracy)

```bash
mkdir -p tessdata
cd tessdata
wget https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/main/chi_sim.traineddata
wget https://github.com/tesseract-ocr/tessdata/raw/main/osd.traineddata
cd ..
export TESSDATA_PREFIX=$(pwd)/tessdata
```

Or pass `--tessdata-dir` to the CLI on every invocation.

### Smoke test

```bash
# English
tesseract path/to/test.png out -l eng && cat out.txt

# Simplified Chinese
tesseract path/to/chinese.png out_cn -l chi_sim && cat out_cn.txt

# Multi-lang (e.g. eng + chi_sim)
tesseract path/to/mixed.png out_mix -l eng+chi_sim && cat out_mix.txt
```

Expected output: a UTF-8 `.txt` file with recognized text.

---

## 6.4 CLI argument surface (verified from `src/tesseract.cpp:194-253`)

| Flag | Effect |
|---|---|
| `--tessdata-dir PATH` | Override tessdata root |
| `--user-words PATH` | Custom dictionary (one word per line) |
| `--user-patterns PATH` | Custom regex patterns |
| `--dpi VALUE` | Source resolution hint |
| `--loglevel LEVEL` | ALL/TRACE/DEBUG/INFO/WARN/ERROR/FATAL/OFF |
| `-l LANG[+LANG]` | Languages (e.g. `eng`, `eng+deu`) |
| `-c VAR=VALUE` | Inline config (repeatable) |
| `--psm PSM\|NUM` | One of the 14 PSM values |
| `--oem OEM\|NUM` | One of the 4 OEM values (legacy only) |
| `--list-langs` | Enumerate installed languages |
| `--print-parameters` / `--print-fonts-table` | Dump config |
| `--help`, `--help-extra`, `--help-psm`, `--help-oem`, `--version` | Self-doc |
| `[configfile...]` | Trailing config files (read after `-c`) |

---

## 6.5 CLI output formats (driven by `tessedit_create_*` flags)

| Format | Class | Trigger | Extension |
|---|---|---|---|
| Plain text | `TessTextRenderer` | default or `tessedit_create_txt=1` | `.txt` |
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

Chaining: pass multiple `-c tessedit_create_xxx=1` flags; `PreloadRenderers`
(`src/tesseract.cpp:503`) builds a chain of renderers, and one `ProcessPages`
call drives them all.

---

## 6.6 Android NDK cross-compile (no in-tree toolchain)

The repo **does not** ship an Android CMake toolchain file. You supply
NDK's via `-DCMAKE_TOOLCHAIN_FILE=...`. The `ANDROID` branch in
`CMakeLists.txt:851-858` is triggered automatically:

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

Per-ABI outputs:

- `build-android/libtesseract.so` (and `libleptonica.so`, which you must also build)
- `build-android/bin/tesseract` (CLI, mostly useful for on-device testing)

### Inside an Android app

For native code in your own Android app, the canonical wrapper is
`externalNativeBuild { cmake { ... } }` in `app/build.gradle`, pointing at this
checkout and pulling `CpuFeaturesNdkCompat` from Maven:

```gradle
android {
  externalNativeBuild {
    cmake {
      arguments "-DANDROID_STL=c++_shared"
      cppFlags "-std=c++17"
    }
  }
}
```

### JNI bridge

**This repo does NOT ship a JNI bridge** (no `JNIEXPORT`, no `Java_*`
symbols, no `Application.mk`, no `gradle` files). You must write your own
JNI wrapper, or use a third-party project:

- **adaptech-cz/Tesseract4Android** — pure-Java/Kotlin API on top of NDK-built
  `libtesseract.so` + `libleptonica.so`. Recommended.
- **rmtheis/tess-two** — legacy Tess4J predecessor; bundles a fork with Java
  APIs and per-ABI `libtess.so`.

For a JNI implementation pattern see
[`10_functions_detail/tesscapi.md`](./10_functions_detail/tesscapi.md) and the
canonical 4-line usage at [`05_api_surface.md`](./05_api_surface.md#58-lifecycle-cheatsheet-the-canonical-4-line-usage).

---

## 6.7 Build option summary

| CMake option | Default | Effect |
|---|:---:|---|
| `CMAKE_BUILD_TYPE` | unset | `Release` recommended |
| `BUILD_TRAINING_TOOLS` | `ON` | builds the 15 `lstmtraining` / `mftraining` / `combine_tessdata` etc. |
| `BUILD_TESTS` | `OFF` | enables 74+ googletest files |
| `GRAPHICS_DISABLED` | `OFF` | disable ScrollView server (set ON for Android) |
| `INSTALL_CONFIGS` | `ON` | install `tessdata/configs/*.config` files |
| `OPENMP_BUILD` | `OFF` | parallel Recognize |
| `ENABLE_NATIVE` | unset | `-march=native` optimizations |
| `DISABLED_LEGACY_ENGINE` | (auto) | disables legacy `src/classify/` + `src/wordrec/` |
| `FAST_FLOAT` | `ON` | fast float math |
| `ENABLE_LTO` | unset | link-time optimization |
| `USE_SYSTEM_ICU` | unset | use system ICU instead of bundled |
| `DISABLE_TIFF` | unset | force-disable TIFF |
| `DISABLE_ARCHIVE` | unset | force-disable libarchive |
| `DISABLE_CURL` | unset | force-disable libcurl |

---

## 6.8 CMake variables used in `find_package`

| Var | Where | Purpose |
|---|---|---|
| `MINIMUM_LEPTONICA_VERSION` | `CMakeLists.txt:70` | `1.74` |
| `LIB_pthread` | `CMakeLists.txt:378` | pthread linkage |
| `LIB_Ws2_32` | `CMakeLists.txt:382` | Windows sockets |
| `TESS_EXPORTS` / `TESS_IMPORTS` | `CMakeLists.txt:801-807` | visibility dispatch |

---

## 6.9 Installing your build into the workspace

Once built, you can integrate Tesseract into the workspace's
`tools/crack-intergration-tools/` as follows:

```bash
# System install (standard)
sudo make install            # → /usr/local/bin/tesseract + /usr/local/lib/libtesseract*

# Or workspace-local install (preferred for AGENTS.md compliance):
PREFIX=$HOME/文档/android-crack/tools/crack-intergration-tools/execable/tesseract
cmake -DCMAKE_INSTALL_PREFIX="$PREFIX" ..
make install
```

The workspace `AGENTS.md` requires all tool binaries to be tracked in
[`/home/leo/文档/android-crack/tools/crack-intergration-tools/docs/tesseract/`](../README.md).
The preferred layout is:

```
tools/crack-intergration-tools/
├── source-projects/tesseract/        # this checkout (READONLY source)
├── execable/tesseract/                # installed binary + .so + .traineddata
│   ├── bin/tesseract
│   ├── lib/libtesseract.so, libleptonica.so
│   ├── tessdata/eng.traineddata
│   └── tessdata/chi_sim.traineddata
└── docs/tesseract/                    # THIS documentation
```

See [`07_workflow_integration.md`](./07_workflow_integration.md) for the
runtime integration plan and recommended action items.