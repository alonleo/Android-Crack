# Ghidra — 文件/模块快速索引

> Ghidra 12.2 DEV（NSA SRE 框架）
> 路径: `tools/crack-intergration-tools/source-projects/ghidra/`

---

## 顶层目录

| 路径 | 说明 |
|------|------|
| `Ghidra/` | 主源码树（12 个子模块） |
| `Ghidra/Framework/` | 12 个框架模块（DB/Docking/Emulation/FileSystem/Graph/Gui/Help/Project/Pty/SoftwareModeling/Utility） |
| `Ghidra/Features/` | 36 个功能模块（Base/BSim/BytePatterns/Decompiler/FileFormats/PyGhidra 等） |
| `Ghidra/Processors/` | 39 个指令集模块（AARCH64/ARM/Dalvik/JVM/x86 等） |
| `Ghidra/Configurations/` | 发布配置（Public_Release） |
| `GhidraBuild/` | 构建工具（Eclipse 插件/IDA 集成/LaunchSupport/Skeleton） |
| `GhidraDocs/` | 文档 + 培训材料 |
| `GPL/` | GPL 子项目 |

## Android 逆向核心模块

### 处理器

| 模块 | 路径 | 用途 |
|------|------|------|
| **AARCH64** | `Processors/AARCH64/` | arm64-v8a 原生库反汇编（SVE/Neon/PAC） |
| **ARM** | `Processors/ARM/` | armeabi-v7a 原生库反汇编（含 Thumb/Thumb-2） |
| **Dalvik** | `Processors/Dalvik/` | DEX 字节码反汇编（KitKat → Android 12） |
| **Hexagon** | `Processors/Hexagon/` | Qualcomm DSP 固件分析 |
| **JVM** | `Processors/JVM/` | Java 字节码（非 Android 专用） |

### Android 文件格式（Features/FileFormats）

| 组件 | 路径 | 用途 |
|------|------|------|
| **APK Loader** | `.../opinion/ApkLoader.java` | APK 加载（多 dex） |
| **DEX Loader** | `.../opinion/DexLoader.java` | DEX 加载 |
| **CDex 加载器** | `.../opinion/CDexLoader.java` | Compact DEX |
| **DEX 格式解析** | `.../android/dex/format/` | 50 个类，完整 DEX 结构 |
| **ART 格式** | `.../android/art/` | ART image（14 版头，8 种 section） |
| **OAT 格式** | `.../android/oat/` | OAT AOT 编译格式 |
| **VDEX** | `.../android/vdex/` | Verified DEX |
| **WDEX** | `.../android/wdex/` | WDEX 格式 |
| **APK 文件系统** | `.../android/apk/` | APK 虚拟文件系统 |
| **Android XML** | `.../android/xml/` | AXML 二进制 XML 解析 |
| **Boot Image** | `.../android/bootimg/` | Android boot image |
| **Dex→Jar** | `.../DexToJarFileSystem.java` | DEX → JAR 解编译 |
| **Dex→Smali** | `.../DexToSmaliFileSystem.java` | DEX → Smali 导出 |
| **APK→Eclipse** | `.../AndroidProjectCreator.java` | APK → Eclipse 项目 |

## ARM64 核心文件（Processors/AARCH64）

| 文件 | 说明 |
|------|------|
| `AARCH64.slaspec` | AArch64 SLEIGH 规范（LE） |
| `AARCH64BE.slaspec` | AArch64 Big-Endian |
| `AARCH64base.sinc` | 基础指令集 |
| `AARCH64instructions.sinc` | 通用指令 |
| `AARCH64ldst.sinc` | Load/Store 指令 |
| `AARCH64neon.sinc` | NEON SIMD |
| `AARCH64sve.sinc` | SVE（Scalable Vector Extension） |
| `AARCH64.cspec` | 编译器规范（Linux） |
| `AARCH64_apple.cspec` | Apple Silicon 调用约定 |
| `AARCH64_win.cspec` | Windows ARM64 调用约定 |
| `AARCH64_golang.cspec` | Go 调用约定 |

## 功能模块索引

| 模块 | 路径 | 关键类 |
|------|------|--------|
| **反编译器** | `Features/Decompiler/` | `DecompInterface.java`, `PcodeEmit.java` |
| **Base（核心）** | `Features/Base/` | `CodeBrowserPlugin`, `ListingPanel`, `DecompilerPanel` |
| **PyGhidra** | `Features/PyGhidra/` | Python 3 脚本框架 |
| **FileFormats** | `Features/FileFormats/` | 所有文件格式加载器 |
| **BSim** | `Features/BSim/` | 函数相似度匹配 |
| **SystemEmulation** | `Features/SystemEmulation/` | Unicorn-based 模拟 |
| **PDB** | `Features/PDB/` | PDB 符号加载 |
| **函数 ID** | `Features/FunctionID/` | FID 函数识别 |
