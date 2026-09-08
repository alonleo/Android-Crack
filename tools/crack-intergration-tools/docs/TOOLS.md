# 工具注册表 — tools/crack-intergration-tools

> **Agent 首次进入工作区时必须加载本文件**（见 AGENTS.md §6）。
> 本文件是 `tools/crack-intergration-tools/` 下所有工具的**唯一登记索引**。
> 新增工具时：在下方工具表追加一行 → 在 `docs/<tool>/` 下创建子目录。
>
> 每个工具子目录按 **架构 / API / 操作链 / 工作流嵌入** 四维度建立深度文档。

---

## 工具登记表

| 工具 | 版本 | 类型 | 索引路径 | 核心文档 | 嵌入分析 |
|---|---|---|---|---|---|---|
| **And64InlineHook** | — | ARM64 inline hook（Rprop 单文件） | [`And64InlineHook/`](./And64InlineHook/) | — | — |
| **AssetRipper** | 1.3.14 | Unity 资源提取 + C# 反编译（跨平台 .NET GUI/CLI） | [`AssetRipper/`](./AssetRipper/) | — | — |
| **ffmpeg** | N-125978 | 音视频处理（转码/剪辑/流媒体） | [`ffmpeg/`](./ffmpeg/) | — | — |
| **Android_Inline_Hook_ARM64** | — | ARM64 inline hook（GToad 多文件） | [`Android_Inline_Hook_ARM64/`](./Android_Inline_Hook_ARM64/) | — | — |
| **assetstudio** | — | Unity .assets / .bundle 提取（GUI + CLI） | [`assetstudio/`](./assetstudio/) | — | — |
| **smali / dex2jar** | 3.0.3 / v2.4 | smali：apktool 反汇编产物（smali→dex→jar 流程见 `convert-smali-to-jars.py`）；dex2jar：dex → 真 .class jar（FixStackmaps 补 StackMapTable 后供 javac 编译） | [`dex2jar/`](./dex2jar/) + [`FixStackmaps`](./source-projects/FixStackmaps/) | — | smali 3.0.3 jar：`tools/environments/android-sdk/cmdline-tools/latest/lib/external/com/android/tools/smali/smali-baksmali/3.0.3/`；d2j-smali：`dex2jar/d2j-smali-v2.4.jar`；dx：`dex2jar/dx-30.0.2.jar` |
| **FixStackmaps** | — | 给 dex2jar class 补 StackMapTable（ASM COMPUTE_FRAMES，D8 desugar 必需） | [`source-projects/FixStackmaps/`](../source-projects/FixStackmaps/) | — | — |
| **ASBuilder** ✅ 入口 | 2.11.1 | **APK → Android Studio 工程（fake 子命令）**。`ASBuilder.jar`（FakerAndroid 改名版：随 APK 有无 `lib/*.so` 自动分支——带 .so→hook 注入 native-lib.cpp + com.android.boot.App(loadLibrary)；**无 .so→仍注入 com.android.boot/ Java 骨架（无 native 变体，不 loadLibrary/native 方法）+ build.gradle 无 cmake**；捆绑库升级版；入口统一为 `$FAKER_JAR`，由 `env.sh` 提供）。原 `FakerAndroid-updated.jar` 保留兼容 | — | [rebuild README](../../../scripts/template-files/fakerandroid-rebuild/) | — |
| **LambdaNameNormalizer** + `asbuilder-dex-jarify.py` | — | **ASBuilder 工程补齐游戏 dex**（方案 A：原 APK 每 dex → dex2jar → 剔应用包名 BuildConfig/R$* → FixStackmaps → **ASM 归一化 lambda 类名 '-'→'_'** 放 app/libs/，解决 ASBuilder 用标准 AGP 不编译 smali 致 APK 仅骨架类、运行 NoClassDefFoundError）。`asbuilder-dex-jarify.py <工程根> --apk <原apk>`（skills/common/scripts/） | — | [rebuild README](../../../scripts/template-files/fakerandroid-rebuild/) | — |
| **dnSpy** | — | .NET 反编译 + 调试 + 编辑（WPF） | [`dnSpy/`](./dnSpy/) | — | — |
| **Ghidra** | 12.2 DEV | NSA SRE 框架（反汇编/反编译/脚本） | [`ghidra/`](./ghidra/) | [INDEX](./ghidra/INDEX.md) · [01_overview](./ghidra/01_overview.md) | [07_workflow_integration](./ghidra/07_workflow_integration.md) |
| **Il2CppDumper** | — | il2cpp C# 原版反编译 | [`Il2CppDumper/`](./Il2CppDumper/) | — | — |
| **Il2CppInspectorPro** | 2026.1 | il2cpp 工业级反编译（含插件系统） | [`Il2CppInspectorPro/`](./Il2CppInspectorPro/) | — | — |
| **ILSpy** | 11.0.0.9252 | .NET 反编译（跨平台 Avalonia + ilspycmd CLI） | [`ILSpy/`](./ILSpy/) | [README](./ILSpy/README.md) · [06_build_and_run](./ILSpy/06_build_and_run.md) | [CHECKSUM](../source-projects/ILSpy/CHECKSUM.md) |
| **rodroid-il2cppdumper** | 6.1.0 | il2cpp 反编译（Rust + Tauri 2 跨平台 GUI） | [`rodroid-il2cppdumper/`](./rodroid-il2cppdumper/) | — | — |
| **Tesseract OCR** | 5.5.3 | C++17 OCR 引擎（CPU + LSTM） | [`tesseract/`](./tesseract/) | [INDEX](./tesseract/INDEX.md) · [01_overview](./tesseract/01_overview.md) | [07_workflow_integration](./tesseract/07_workflow_integration.md) |
| **HA4T** | 0.1.6 | 跨平台 UI 自动化框架（OCR/图像/原生控件） | [`ha4t/`](./ha4t/) | [INDEX](./ha4t/INDEX.md) · [01_overview](./ha4t/01_overview.md) | [07_workflow_integration](./ha4t/07_workflow_integration.md) |
| **Swipium** | 1.5.0 | MCP server for mobile QA agents（AI 代理测试） | [`swipium/`](./swipium/) | [INDEX](./swipium/INDEX.md) · [01_overview](./swipium/01_overview.md) | [07_workflow_integration](./swipium/07_workflow_integration.md) |
| **UABEA** | — | Unity 资源包编辑（原版 Avalonia 11） | [`UABEA/`](./UABEA/) | — | — |
| **UABEANext** | — | Unity 资源包编辑（新版 Dock 多面板） | [`UABEANext/`](./UABEANext/) | — | — |
| **Unlimited-OCR** | — | SGLang OCR 长上下文识别 | [`Unlimited-OCR/`](./Unlimited-OCR/) | — | — |
| **xapk-to-apk** | — | XAPK → fat APK（Python，无第三方依赖） | [`xapk-to-apk/`](./xapk-to-apk/) | — | — |
| **txtrtool** | 1.0.2 | Metroid Prime TXTR 纹理解码/编码（C++/CMake，GCC14 打补丁构建） | [`txtrtool/`](./txtrtool/) | [INDEX](./txtrtool/INDEX.md) | [06_build_and_run](./txtrtool/06_build_and_run.md) |
| **UndertaleModTool** | 0.9.1.2 | GameMaker .droid 数据编辑（GMS2 房间/实例/对象/代码；UnderminersTeam 官方仓库） | [`undertale-mod-tool/`](./undertale-mod-tool/) | [INDEX](./undertale-mod-tool/INDEX.md) | [06_build_and_run](./undertale-mod-tool/06_build_and_run.md) |
| **Underanalyzer** | — | GML VM 分析/编译/反编译库（UndertaleModTool 的反编译器内核） | [`underanalyzer/`](./underanalyzer/) | [INDEX](./underanalyzer/INDEX.md) | — |

---

## 命名与目录约定

```
tools/crack-intergration-tools/
├── source-projects/           ← 原始源码（READONLY，禁止修改）
│   ├── tesseract/             ← Tesseract 5.5.3 源码
│   └── ...
├── execable/                  ← 已编译可执行 (ASBuilder.jar 等)
└── docs/                      ← 工具注册表 + 知识库（TOOLS.md 为入口）
    ├── TOOLS.md               ← ★ 工具注册表（本文件，MUST-LOAD）
    ├── <Tool>/                ← 每工具一个子目录
    │   ├── README.md          ← 导航
        ├── 02_directory_tree.md
        ├── 03_architecture.md ← 模块依赖图 + 类继承图
        ├── 04_operation_chains.md
        ├── 05_api_surface.md
        ├── 06_build_and_run.md
        ├── 07_workflow_integration.md  ← 嵌入到逆向流程的方案分析
        ├── 08_dependencies.md
        ├── 09_glossary.md
        ├── 10_functions_detail/       ← 关键类/函数详解
        └── .inventory/<Name>.md       ← Phase 1 原始 inventory
```

---

## 索引规范

- 每工具 12+ 个 `.md` 文件，10+ 张 mermaid 图，INDEX.md ≥ 150 行
- 所有 `file:line` 引用须 `ripgrep` 验证，禁止猜测
- 嵌入分析文档（`07_workflow_integration.md`）使用中文，与 AGENTS.md 一致
- 新增工具时复制 `tesseract/` 的目录结构作为模板
