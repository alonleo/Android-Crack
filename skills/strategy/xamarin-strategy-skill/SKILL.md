---
name: xamarin-strategy-skill
description: 处理 Xamarin (Mono runtime) 项目的专用工作流。使用 ILSpy / dnSpy 反编译 assemblies/*.dll。详见 STRATEGY.md §1.2 类型表 "xamarin" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=xamarin（libmonodroid.so / libmono-native.so / libxamarin-app.so）；或企业内部 Xamarin 应用调用。
---

# Xamarin (Mono Runtime) 逆向策略

> 处理 **Xamarin (Mono runtime)** 项目的专用策略。
> 游戏较少使用 Xamarin（性能与生态问题），多见于企业内部应用与跨平台 productivity 应用。
>
> 加载顺序：SKILL.md → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/xamarin-strategy-skill/
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
| `libmonodroid.so` | **必须存在** |
| `libmono-native.so` / `libxamarin-app.so` | 备选 |
| `<application android:name="mono.android.app.Application"` | 可选 |
| `assemblies/*.dll` | 多个 .NET DLL 打包为 assemblies |

## 3. 默认策略

```
00 → 00a → 01 → 02 → 03 → mono-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`mono-03`（同 Unity Mono — ILSpy / dnSpy）

## 4. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| mono-03 | assemblies/*.dll 反编译 | ILSpy 可见 C# 代码 |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| DLL 包签名校验 | 重编译触发反作弊 | Frida hook 签名校验函数 |
| 混合调用栈 | C# ↔ Java ↔ Native | 分别 hook |
| Mono runtime 资源占用 | 比 ART 高 | 接受 |

## 6. 关联文档

- [strategy.md](./strategy.md)
- [workflow.md](./workflow.md)
- [tools-index.md](./tools-index.md)
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（xamarin 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：xamarin](../../common/third-party-removal-strategy-skill/references/engine-notes.md#xamarin)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

