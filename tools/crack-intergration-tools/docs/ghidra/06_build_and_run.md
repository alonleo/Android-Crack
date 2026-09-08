# Ghidra 构建与运行

## 构建要求

| 依赖 | 版本 | 检查 |
|------|------|------|
| JDK | ≥ 25 | `java -version` |
| Gradle | ≥ 9.1 | `gradle --version` |
| Python | 3.9-3.14 | `python3 --version` |

## 构建命令

```bash
cd tools/crack-intergration-tools/source-projects/ghidra
gradle buildGhidra      # 完整构建（产出 build/dist/ghidra-*.zip）
gradle buildNative      # 仅构建原生组件（反编译器/Pe）
```

## 运行

```bash
# GUI 模式
./ghidraRun

# Headless 模式
analyzeHeadless <项目路径> <项目名> -import <文件> [选项]
```

## Headless 常用命令

```bash
# 分析 APK
analyzeHeadless /tmp/ghidra_proj APKAnalysis \
  -import app.apk \
  -processor Dalvik:LE:64:default \
  -readOnly

# 分析 ARM64 原生库
analyzeHeadless /tmp/ghidra_proj LibAnalysis \
  -import libil2cpp.so \
  -processor AARCH64:LE:64:v8A \
  -postScript SearchStrings.java \
  -readOnly
```
