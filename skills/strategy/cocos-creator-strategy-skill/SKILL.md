---
name: cocos-creator-strategy-skill
description: 处理 Cocos Creator (JS/TS) 项目的专用工作流。使用 cc-reverse + reverse + cocos2d-dec 工具链还原 JS 项目结构。详见 STRATEGY.md §1.2 类型表 "cocos-creator" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=cocos-creator（libcocos2djs.so + src/settings.js + main/config.json）；或现代 Cocos 游戏（2.x/3.x）调用。
---

# Cocos Creator (JS/TS) 逆向策略

> 处理 **Cocos Creator（触控科技第二代 Cocos 引擎，使用 TypeScript/JavaScript 开发）** 项目的专用策略。
> 现代 Cocos 游戏的首选框架；逆向思路与 Unity il2cpp 还原代码类似——**目标是还原 JS 项目结构和资源**。
>
> 加载顺序：SKILL.md → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/cocos-creator-strategy-skill/
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

1. [SKILL.md](./SKILL.md)
2. [strategy.md](./strategy.md)
3. [workflow.md](./workflow.md)
4. [tools-index.md](./tools-index.md)
5. [EXPERIENCES.md](../../EXPERIENCES.md)
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `libcocos2djs.so` | `unzip -l <apk>` |
| `assets/src/settings.js` / `settings.json` | 项目元信息 |
| `assets/main/config.json` / `assets/internal/config.json` | bundle 配置文件 |
| `assets/src/chunks/*.js` | 3.x SystemJS 模块分块 |
| `assets/cc.common.js` / `assets/cc.common.min.js` | 引擎 bundle |

## 3. 默认策略

```
00 → 00a → 01 → 02 → cocos-03 → 04 → cocos-05 → 06 → 09 → 10 → 11 → 12 → 13
```

类型化分支：`cocos-03`（so + JS 资源分析）/ `cocos-05`（JS 提取与解密）

## 4. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| cocos-03 | `cc-reverse` 自动检测 + 解密 | 输出 TS/JS 源 |
| cocos-05 | `.jsc` 全部解密 | 已还原项目结构 |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| `.jsc` 解密失败 | XXTEA 密钥未知 | `reverse libcocos2djs.so` 提取密钥 |
| cc-reverse 自动检测失败 | 版本太新 | `--version-hint 3.x` 强制指定 |
| Stage3D 不可见 | GPU 渲染 | 仅 Java / AS 层 hook |

## 6. 关联文档

- [strategy.md](./strategy.md)
- [workflow.md](./workflow.md)
- [tools-index.md](./tools-index.md)
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（cocos-creator 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：cocos-creator](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos-creator)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

