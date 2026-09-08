# Underanalyzer — 工具文档索引

> GameMaker VM 分析/编译/反编译库（UndertaleModTool 的反编译器内核）

## 基本信息

- **来源**: https://github.com/UnderminersTeam/Underanalyzer（克隆于 2026-08-09）
- **源码**: `tools/crack-intergration-tools/source-projects/Underanalyzer/`（READONLY）
- **构建**: `dotnet build Underanalyzer/Underanalyzer.csproj -c Release`
- **语言**: C#
- **许可证**: MPL-2.0
- **用途**: 精确的 GML 反编译器 + 编译器，供大型 modding 工具（如 UndertaleModTool）集成

## 功能

- **Decompiler**: 高度精确的 GML 反编译器，针对 GML VM 编译器 quirks 设计
  - 支持 GM:S 1.4 → 现代 GameMaker（不含 GMRT）
  - 迭代控制流分析 → 准确反编译
  - 支持 AST 直接输出（程序化处理反编译结果）
  - 反编译后 cleanup pass → 输出更可读
- **Compiler**: 较准确的 GML 编译器，支持 GMLv2 特性（GM 2.3+）

## 与 UndertaleModTool 的关系

Underanalyzer 是 UndertaleModTool 的 `Underanalyzer/` 子模块（decompiler 内核）。
- 本工具库同时登记了 **UndertaleModTool**（可执行工具）和 **Underanalyzer**（库）
- 用途：反编译 `.droid` 的 CODE chunk（GML bytecode）→ 可读 GML 源码
  - 配合 `UndertaleModCli.dll project <datafile> -s <scripts.csx> -o <outdir>` 反编译工程

## 集成接口

要在更大项目中使用，实现 `Underanalyzer/VMData.cs` 和 `Underanalyzer/IGameContext.cs` 的接口：
- `IGMCode`: 游戏数据中的代码条目
- `IGMInstruction`: 代码条目中的单条指令
- `IGMVariable`: 游戏数据中的变量

## 构建产物

```
Underanalyzer/bin/Release/netstandard2.1/Underanalyzer.dll   ← 跨平台（netstandard2.1）
Underanalyzer/bin/Release/net10.0/Underanalyzer.dll           ← 本机（.NET 10）
```

## 坑位

1. **纯库无 CLI**：Underanalyzer 是库，无独立可执行；通过 UndertaleModCli 或自定义 C# 工程调用
2. **不做混淆处理**：README 明确「不会处理任何形式的混淆」
3. **GMRT 不支持**：GameMaker Runtime 不在支持范围