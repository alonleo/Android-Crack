---
name: unity-mono-strategy-skill
description: 处理 Unity Mono / .NET DLL 项目（GameAssembly.dll + *.dll）的专用工作流。使用 ILSpy/dnSpy 反编译 .NET DLL。详见 STRATEGY.md §1.2 类型表 "unity-mono" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=unity-mono（GameAssembly.dll + *.dll）；或老版本 Unity 项目（2017 年前后默认 Mono）调用。
---

# Unity Mono / .NET DLL 逆向策略

> 处理 **Unity Mono / .NET DLL** 项目的专用策略。
> 适用于老版本 Unity 项目（2017 年前后 Unity 默认 Mono 编译模式，已少见）。
>
> 加载顺序：SKILL.md → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/unity-mono-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 策略详述
├── workflow.md           ← 阶段流程
├── tools-index.md        ← 工具索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 阶段专用脚本
│   └── common/           ← 通用脚本
└── assets/               ← 资源
```

## 1. 加载顺序

1. [SKILL.md](./SKILL.md) — 总览
2. [strategy.md](./strategy.md) — 策略
3. [workflow.md](./workflow.md) — 流程
4. [tools-index.md](./tools-index.md) — 工具
5. [EXPERIENCES.md](../../EXPERIENCES.md) — 经验
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `GameAssembly.dll` + `*.dll` | `unzip -l <apk>` |
| 老 Unity 版本 | type=unity-mono |

## 3. 默认策略

```
00 → 00a → 01 → 02 → 03 → mono-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`mono-03`（.NET DLL 反编译）

详见 [strategy.md](./strategy.md)。

## 4. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| mono-03 | ILSpy / dnSpy 反编译 | 看到完整 C# 代码 |
| 09 | SDK 移除 | manifest 干净 |
| 10 | 重打包 + 签名 | 三签齐全 |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| DLL 包签名校验 | 重编译后触发反作弊 | Frida hook 签名校验函数 |
| 混合调用栈 | C# ↔ Java ↔ Native 三层交错 | 分别 hook |
| dnSpy 崩溃 | .NET runtime 兼容 | 换 ILSpy |

## 6. 关联文档

- [strategy.md](./strategy.md)
- [workflow.md](./workflow.md)
- [tools-index.md](./tools-index.md)
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（unity-mono 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：unity-mono](../../common/third-party-removal-strategy-skill/references/engine-notes.md#unity-mono)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

