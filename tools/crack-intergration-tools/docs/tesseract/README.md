# Tesseract OCR — Documentation Index

> **Project**: Tesseract OCR 5.5.3 (Apache-2.0)
> **Source root**: `tools/crack-intergration-tools/source-projects/tesseract/`
> **Inventory**: `.inventory/tesseract.md` (758 lines, 2026-07-28)
> **Audience**: Android reverse-engineering agents integrating OCR into the `crackings/<Name>/` pipeline
> **Primary language**: English (technical), Chinese (workflow integration analysis in §07)

Tesseract is the canonical open-source OCR engine used here as a CPU-only, offline fallback / supplement to the LLM-driven `Unlimited-OCR` (SGLang server). It powers stage 06 OCR when GPU/SGLang is unavailable, and is the offline workhorse for translating UI text embedded in `apktool`-extracted images.

---

## Document map

| File | Purpose | Read when… |
|---|---|---|
| **[INDEX.md](./INDEX.md)** | Searchable index of every file/class/function — primary lookup tool | you need to grep the project |
| **[01_overview.md](./01_overview.md)** | Positioning, version 5.5.3, Apache-2.0, C++ + Java Swing summary | first time reading the docs |
| **[02_directory_tree.md](./02_directory_tree.md)** | Annotated tree of all 14 `src/` modules | navigating source layout |
| **[03_architecture.md](./03_architecture.md)** | Module dependency graph + class inheritance (≥ 2 mermaid) | understanding architecture |
| **[04_operation_chains.md](./04_operation_chains.md)** | 7 representative flows (CLI, library, OSD, training, …) — ≥ 7 mermaid | tracing any single operation |
| **[05_api_surface.md](./05_api_surface.md)** | `TessBaseAPI` method table + C API + OEM/PSM enums | writing integration code |
| **[06_build_and_run.md](./06_build_and_run.md)** | Linux desktop + Android NDK + tessdata download | compiling or installing |
| **[07_workflow_integration.md](./07_workflow_integration.md)** | **★ Analysis** of Tesseract inside `crackings/` pipeline (Chinese) | deciding whether to embed Tesseract |
| **[08_dependencies.md](./08_dependencies.md)** | Leptonica hard dep + optional libs | resolving build issues |
| **[09_glossary.md](./09_glossary.md)** | OEM, PSM, LSTM, OSD, tessdata, traineddata, … | looking up terminology |
| **[10_functions_detail/tessbaseapi.md](./10_functions_detail/tessbaseapi.md)** | Every public `TessBaseAPI` method with `file:line` | writing library code |
| **[10_functions_detail/tesscapi.md](./10_functions_detail/tesscapi.md)** | C API entry points | writing C wrappers (JNI, etc.) |
| **[10_functions_detail/iterators.md](./10_functions_detail/iterators.md)** | Page/Result/LTR/Mutable/Choice iterators | traversing OCR output |
| **[10_functions_detail/renderers.md](./10_functions_detail/renderers.md)** | Renderer hierarchy & output formats | choosing output format |

---

## TL;DR

- **Library** = `libtesseract.so` (or `.a`); **CLI** = `tesseract` binary at `src/tesseract.cpp:855`.
- **Public façade** = `TessBaseAPI` class at `include/tesseract/baseapi.h:76` (impl `src/api/baseapi.cpp`, 2354 lines).
- **Hard dep** = Leptonica ≥ 1.74 (`configure.ac:487`, `CMakeLists.txt:445`); everything else optional.
- **Models NOT shipped**: `tessdata/` ships only configs — you must download `eng.traineddata` (~22 MB) and `chi_sim.traineddata` (~26 MB) from `github.com/tesseract-ocr/tessdata` before any OCR can run.
- **NOT Android-ready**: the `java/` folder is desktop Swing (`SVWindow.java:40 imports javax.swing.JFrame`). For Android you must NDK-cross-compile `libtesseract` + `libleptonica` and write your own JNI wrapper (use `adaptech-cz/Tesseract4Android`).
- **Recommended integration** (see `07_workflow_integration.md`): add Tesseract as a CPU fallback backend to `tools/scripts/stage-06-ocr.sh`, keeping `Unlimited-OCR` as the GPU/SGLang primary.

---

## Verification status (2026-07-28)

| Metric | Required | Actual |
|---|---:|---:|
| `.md` files (excluding `.inventory/`) | ≥ 12 | 15 |
| Total `mermaid` diagrams | ≥ 10 | 12+ |
| `INDEX.md` rows | ≥ 150 | see `INDEX.md` |
| `10_functions_detail/` files | ≥ 4 | 4 |
| Operation chains in `04` | ≥ 6 | 7 |
| All `file:line` refs | grep-verified | ✓ |

See [`10_functions_detail/`](./10_functions_detail/) for the function-level deep-dive,
[`04_operation_chains.md`](./04_operation_chains.md) for end-to-end flows,
and **[`07_workflow_integration.md`](./07_workflow_integration.md)** for the Android reverse-engineering integration analysis.