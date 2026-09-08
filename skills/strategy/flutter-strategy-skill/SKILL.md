---
name: flutter-strategy-skill
description: 处理 Flutter (Dart AOT) 项目的专用工作流。使用 blutter / reFlutter + Dart SDK 分析 libapp.so。详见 STRATEGY.md §1.2 类型表 "flutter" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=flutter（libflutter.so + libapp.so）；或 Flutter 写的小型独立游戏调用。
---

# Flutter (Dart AOT) 逆向策略

> 处理 **Flutter (Dart AOT 编译)** 项目的专用策略。
> libapp.so 是 Dart AOT 编译产物（10-50 MB），反编译难度高。
>
> 加载顺序：SKILL.md → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/flutter-strategy-skill/
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
| `libflutter.so` | Flutter 引擎 |
| `libapp.so` | Dart AOT 编译产物 |
| `<activity android:name="io.flutter.embedding.android.FlutterActivity"` | 入口 Activity |
| `assets/flutter_assets/kernel_blob.bin` | 入口 Dart 类（旧版） |

## 3. 默认策略

```
00 → 00a → 01 → 02 → flutter-03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`flutter-03`（Dart AOT dump）

## 4. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| flutter-03 | blutter 输出 | 看到函数签名 + 类层次 |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| blutter 输出质量差 | Dart AOT 反编译不成熟 | reFlutter + IDA 辅助 |
| Hook 点变化 | Flutter 引擎版本升级 | 用最新 Flutter 引擎文档 |
| Dart 函数签名混淆 | debug vs release 差异 | blutter --release-mode |

## 6. 关联文档

- [strategy.md](./strategy.md)
- [workflow.md](./workflow.md)
- [tools-index.md](./tools-index.md)
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（flutter 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：flutter](../../common/third-party-removal-strategy-skill/references/engine-notes.md#flutter)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

