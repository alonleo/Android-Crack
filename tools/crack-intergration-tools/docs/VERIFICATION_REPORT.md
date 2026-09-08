# 索引项目验收报告

> 记录每个工具索引项目的最终产出与验证指标。  
> Phase 2 subagent 在 FINAL 报告中所列数据已与文件系统交叉核对。

## Tesseract OCR 5.5.3

- **任务**：为 `tools/crack-intergration-tools/source-projects/tesseract/` 建立索引 + 工作流嵌入分析
- **源项目路径**：`tools/crack-intergration-tools/source-projects/tesseract/`（READONLY）
- **索引路径**：`tools/crack-intergration-tools/docs/tesseract/`
- **完成日期**：2026-07-28

### Phase 1 — Inventory

| 项目 | 值 |
|---|---|
| 报告路径 | `docs/tesseract/.inventory/tesseract.md` |
| 行数 | 758 |
| 大小 | 50 KB |
| 子模块清单 | 14 个 src/ 子目录 + 12 个 header |
| 操作链 | 7 条（含 CLI、TesseractRect、LSTM、迭代器、多页 TIFF、训练、Java Swing） |
| 依赖 | Leptonica（硬依赖） + libpng/jpeg/tiff/archive/curl（可选） |
| 验证方式 | 全部 `file:line` 经 ripgrep 验证 |

### Phase 2 — 索引文档

| 指标 | 阈值 | 实际 | 状态 |
|---|---:|---:|---|
| `.md` 文件数（不含 `.inventory/`） | ≥ 12 | **15** | ✅ |
| Mermaid 图总数 | ≥ 10 | **14** | ✅ |
| `INDEX.md` 行数 | ≥ 150 | **651** | ✅ |
| `10_functions_detail/*.md` 文件数 | ≥ 4 | **4** | ✅ |
| `04_operation_chains.md` 操作链数 | ≥ 6 | **7** | ✅ |

### Mermaid 图分布

| 文件 | 图数 | 类型 |
|---|---:|---|
| `03_architecture.md` | 6 | flowchart / classDiagram |
| `04_operation_chains.md` | 7 | sequenceDiagram（每链一张） |
| `07_workflow_integration.md` | 1 | flowchart（逆向流程嵌入图） |
| **合计** | **14** | — |

### 嵌入分析核心结论（07_workflow_integration.md）

1. **定位**：Tesseract 是 `stage-06-ocr.sh` 的 **CPU 兜底 backend**，不取代 Unlimited-OCR
2. **硬阻塞**：`tessdata/` 缺少 `.traineddata` 文件 → 必须先下载 eng/chi_sim/osd
3. **Android 端嵌入不推荐**：运行时 OCR 延迟 ≥200ms 破坏 UI 流畅度；且无原生 JNI；已用 stage-05a frida hook 拦截 set_text 解决
4. **推荐方案**：方案 A（stage-06-ocr.sh 加 backend 开关 + 离线 fallback）+ 方案 C（独立的 `stage-06b-offline-image-translate.sh` 给纯图片游戏）

### 已知 gap

- Tesseract 5.5.3 主线已发布 5.5.4/5.5.5，本仓库冻结在 5.5.3
- `tessdata/` 中无任何 `.traineddata` 文件，需运行时下载
- `Tesseract::recognize_page()` 声明但未定义（inventory 已记录）
- `.gitmodules` 中 leptonica 子模块未 checkout（未影响本次索引）