---
name: unreal-strategy-skill
description: 处理 Unreal Engine 4/5 项目的专用工作流。使用 UE dumper / FModel + IDA / Ghidra 分析 libUE4.so 与 .pak 资源包。详见 STRATEGY.md §1.2 类型表 "unreal" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=unreal（libUE4.so / libUnreal.so / libUnrealEngine.so）；或大型 UE4/UE5 手游调用。
---

# Unreal Engine 4/5 逆向策略

> 处理 **Unreal Engine 4/5** 项目的专用策略。
> 通常 libUE4.so 体积大（100-500 MB），需要高性能机器 + IDA/Ghidra。
>
> 加载顺序：SKILL.md → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/unreal-strategy-skill/
├── SKILL.md
├── strategy.md
├── workflow.md
├── tools-index.md
├── scripts/{workflow,common}/
└── assets/
```

## 1. 加载顺序

1. [SKILL.md](./SKILL.md)
2. [strategy.md](./strategy.md)
3. [workflow.md](./workflow.md)
4. [tools-index.md](./tools-index.md)
5. [EXPERIENCES.md](../../EXPERIENCES.md)
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `libUE4.so` | UE4 |
| `libUnreal.so` | 旧 UE |
| `libUnrealEngine.so` | UE5 |
| `assets/<ProjectName>/Content/Paks/*.pak` | 资源包 |
| `<activity android:name="com.epicgames.unreal.GameActivity"` | UE4 标准入口 |

## 3. 默认策略

```
00 → 00a → 01 → 02 → unreal-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`unreal-03`（资源包提取）

## 4. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| unreal-03 | .pak 解包产物 | 看到 .uasset / .umap / .ubulk |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| libUE4.so 体积过大 | 100-500 MB | 高性能机器 + 充足内存 |
| .pak 加密 | 资源包加密 | UE dumper + 偏移解包 |
| C++ 反射类名混淆 | bUseUnityBuild + 重命名 | IDA 符号恢复脚本 |

## 6. 关联文档

- [strategy.md](./strategy.md)
- [workflow.md](./workflow.md)
- [tools-index.md](./tools-index.md)
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（unreal 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：unreal](../../common/third-party-removal-strategy-skill/references/engine-notes.md#unreal)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

