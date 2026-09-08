# Ghidra — 项目定位与版本

## 基本信息

| 字段 | 值 |
|------|-----|
| **项目** | Ghidra |
| **版本** | 12.2 DEV (unreleased) |
| **开发商** | NSA（National Security Agency）Research Directorate |
| **许可证** | Apache 2.0 |
| **类型** | 软件逆向工程（SRE）框架 |
| **语言** | Java（主体）+ C++（反编译器核心）+ Python（脚本） |
| **源码路径** | `tools/crack-intergration-tools/source-projects/ghidra/` |
| **发布页** | https://github.com/NationalSecurityAgency/ghidra |

## 核心能力

| 能力 | 说明 |
|------|------|
| **反汇编** | 39 种处理器架构（含 ARM64/ARM/Dalvik） |
| **反编译** | 内置 C++ 反编译器（P-code 中间表示） |
| **脚本** | Python（PyGhidra）+ Java + 批处理（headless） |
| **图形** | 控制流图/调用图/数据流图 |
| **搜索** | 立即数/字符串/指令模式/YARA |
| **匹配** | BSim（函数相似度匹配） |
| **模拟** | Unicorn-based 系统模拟 |
| **调试器** | GDB/Lldb/Windbg 远程调试 |

## Android 逆向能力

| 子项 | 支持范围 |
|------|---------|
| **DEX** | KitKat → Android 12 全部版本 |
| **CDEX / VDEX / WDEX** | 完整 |
| **APK** | 多 dex + AndroidManifest.xml |
| **ART / OAT** | ART image + AOT 编译产物 |
| **APK → Eclipse 项目** | 内建 |
| **ARM32 / ARM64 原生库** | 完整（含 NEON/SVE/Thumb） |
| **Dalvik 字节码** | 含 DEX → JAR 解编译 |
| **Unity / il2cpp** | ❌ 不支持（需手动分析） |

## 构建要求

| 依赖 | 版本 |
|------|------|
| JDK | ≥ 25 |
| Gradle | ≥ 9.1 |
| Python | 3.9-3.14 |
| 额外 (Linux) | GCC/Clang + make |
| 额外 (Windows) | MSVC 2017+ |
