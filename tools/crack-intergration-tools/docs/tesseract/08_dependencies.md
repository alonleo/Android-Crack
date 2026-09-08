# 08 — Dependencies

This document inventories every external library Tesseract touches, separated
into hard / soft / training-only / Android-only categories. All file:line
references grep-verified.

---

## 8.1 Hard dependencies (REQUIRED, fatal if missing)

| Library | Min version | Where declared | Used for |
|---|---|---|---|
| **Leptonica** | **≥ 1.74** | `configure.ac:487` (`PKG_CHECK_MODULES([LEPTONICA], [lept >= 1.74], ...)`); `CMakeLists.txt:445-455` (`find_package(Leptonica ${MINIMUM_LEPTONICA_VERSION} CONFIG)`) | Pix image class, thresholding, box ops |
| **pthread** | any | `configure.ac:426` (`AC_SEARCH_LIBS([pthread_create], [pthread])`); `CMakeLists.txt:378-380` (`${LIB_pthread}`) | thread pool |
| **C++ compiler** | C++17 (C++20 preferred) | `CMakeLists.txt:135-138` | language |

Leptonica is the only **non-compiler** hard dep. Building Leptonica with
zlib + libpng + libtiff is recommended by `README.md:122-126` so that
Tesseract can read PNG / JPEG / TIFF inputs.

---

## 8.2 Optional runtime dependencies

| Library | Default | Where declared | Used for |
|---|---|---|---|
| **libarchive** | auto-detect | `configure.ac:494-507`; `CMakeLists.txt:484-493` (`-DDISABLE_ARCHIVE=ON` to force off) | compressed `.traineddata` |
| **libcurl** | auto-detect | `configure.ac:473-485`; `CMakeLists.txt:498-507` (`-DDISABLE_CURL=ON`) | `tesseract URL ...` remote-image path (`src/api/baseapi.cpp:1056-1128`) |
| **libtiff** | auto-detect | `configure.ac:283` (`AC_CHECK_HEADERS([tiffio.h], ...)`); `CMakeLists.txt:470-479` (`-DDISABLE_TIFF=ON`) | TIFF read/write; gated also by `check_leptonica_tiff_support()` (`CMakeLists.txt:457-463`) |
| **OpenMP** | `OFF` | `CMakeLists.txt:91,338` (`-DOPENMP_BUILD=ON`) | parallel Recognize |
| **Ws2_32** | auto on Windows | `CMakeLists.txt:382` | Winsock |
| **Apple Accelerate** | macOS only | `configure.ac:317-321` (`MY_CHECK_FRAMEWORK([Accelerate])`) | BLAS on macOS |

---

## 8.3 Training-only dependencies

These are only needed when `-DBUILD_TRAINING_TOOLS=ON` (default). Missing
them disables training but does NOT break the OCR engine.

| Library | Min version | Where declared | Used by |
|---|---|---|---|
| **ICU** | 52.1 (`icu-uc` + `icu-i18n`) | `configure.ac:512-519` (`PKG_CHECK_MODULES([ICU_UC], [icu-uc >= 52.1] ...)`) | `combine_lang_model`, `set_unicharset_properties` |
| **pango** | 1.38.0 | `configure.ac:522-528` | `text2image` rendering |
| **cairo** | any | `configure.ac:531-536` | `text2image` rendering |
| **pangocairo** | any | `configure.ac:538` | (optional) |
| **pangoft2** | any | `configure.ac:539` | (optional) |

If any of these are missing at configure time, autoconf emits a warning and
flips `AM_CONDITIONAL([ENABLE_TRAINING], false)` (no equivalent grep
collocation was found for CMake, but the CMake option `-DBUILD_TRAINING_TOOLS=OFF`
achieves the same effect).

---

## 8.4 Android-only dependencies

| Library | Where | Used for |
|---|---|---|
| **CpuFeaturesNdkCompat** | `CMakeLists.txt:851-858` (`if(ANDROID)` block, `find_package(CpuFeaturesNdkCompat REQUIRED)`) | `android_getCpuFeatures()` runtime SIMD detection in `src/arch/simddetect.cpp:227` |
| **Android NDK STL** (`c++_shared`) | via `-DCMAKE_ANDROID_STL_TYPE=c++_shared` | C++ runtime |

The NDK's standard sysroot may not include some headers (e.g. `cpufeatures.h`);
the `ANDROID_TOOLCHAIN` branch at `CMakeLists.txt:629-632` exposes
`$ANDROID_TOOLCHAIN/sysroot/usr/include` for that case.

---

## 8.5 SIMD support (compile-time + runtime)

Tesseract auto-detects SIMD capability at configure time (`configure.ac:136-200`,
`AX_CHECK_COMPILE_FLAG` + `host_cpu` dispatch) and runtime-dispatches
in `src/arch/simddetect.cpp`. SIMD is mandatory for performance but not for
correctness — without SIMD the engine still runs, just slower.

| ISA | Dispatch |
|---|---|
| AVX | `src/arch/dotproductavx.cpp` |
| AVX2 | `src/arch/dotproductavx2.cpp` |
| AVX-512F | `src/arch/dotproductavx512.cpp` |
| FMA | `src/arch/dotproductfma.cpp` |
| SSE 4.1 | `src/arch/dotproductsse41.cpp` |
| Generic SSE | `src/arch/dotproductsse.cpp` |
| NEON (ARM) | `src/arch/dotproductneon.cpp` (Android: runtime via `android_getCpuFeatures()`, `src/arch/simddetect.cpp:227`) |
| RVV (RISC-V) | `src/arch/dotproductrvv.cpp` |

---

## 8.6 Build-system options map

| Flag | Default | Effect |
|---|:---:|---|
| `-DCMAKE_BUILD_TYPE=Release` | (unset) | `-O3 -DNDEBUG` |
| `-DBUILD_TRAINING_TOOLS=ON` | ON | build 15 training executables |
| `-DBUILD_TESTS=OFF` | OFF | enable 74+ googletest files (needs `-DBUILD_TESTS=ON`) |
| `-DGRAPHICS_DISABLED=ON` | OFF | disable ScrollView server (recommended for Android) |
| `-DINSTALL_CONFIGS=ON` | ON | install `tessdata/configs/*.config` files |
| `-DOPENMP_BUILD=ON` | OFF | parallel Recognize |
| `-DENABLE_NATIVE` | (unset) | `-march=native` |
| `-DDISABLED_LEGACY_ENGINE` | auto | disables legacy `src/classify/` + `src/wordrec/` (default ON in 5.x) |
| `-DFAST_FLOAT=ON` | ON | fast float math |
| `-DENABLE_LTO` | (unset) | link-time optimization |
| `-DUSE_SYSTEM_ICU` | (unset) | use system ICU |
| `-DDISABLE_TIFF=ON` | (unset) | force-disable TIFF |
| `-DDISABLE_ARCHIVE=ON` | (unset) | force-disable libarchive |
| `-DDISABLE_CURL=ON` | (unset) | force-disable libcurl |

---

## 8.7 Feature → dependency map

| Feature | Required dep |
|---|---|
| Read PNG | Leptonica (built with libpng) |
| Read JPEG | Leptonica (built with libjpeg) |
| Read TIFF | Leptonica (built with libtiff) AND/OR libtiff |
| Read PDF | built-in `pdfrenderer.cpp` (no external dep) |
| Compressed `.traineddata` (`.gz`) | libarchive |
| Remote URL `tesseract URL ...` | libcurl |
| Parallel Recognize | OpenMP |
| Searchable PDF output | none (uses bundled `tessdata/pdf.ttf`) |
| hOCR / ALTO / PAGE / TSV / UNLV / Box output | none |
| Training new models | ICU + pango + cairo |
| Android build | NDK + CpuFeaturesNdkCompat + Leptonica (NDK build) |
| SIMD | compiler auto-detect |

---

## 8.8 Known failure modes

| Symptom | Likely cause |
|---|---|
| `configure: error: Leptonica not found` or CMake fatal at `:445` | install `libleptonica-dev` ≥ 1.74 |
| `Could not initialize tesseract.` | missing `.traineddata` (NOT a dep issue) |
| `tesseract URL https://...` silently fails | libcurl not built in (`-DDISABLE_CURL=ON` was passed or libcurl not detected) |
| `.traineddata.gz` won't open | libarchive not built in |
| Crash on Android startup | `CpuFeaturesNdkCompat` not linked (CMakeLists.txt:851-858) |
| SIMD path wrong ABI | rebuild with appropriate `-mavx2` / `-march=armv8-a+simd` flags |

See [`09_glossary.md`](./09_glossary.md) for terminology definitions.