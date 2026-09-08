---
name: defold-strategy-skill
description: 处理 Defold 引擎 APK 的专用逆向策略。Defold 游戏以 lib<game>.so（含 libdmengine.so）+ assets/game.{dmanifest,projectc,arcd,arci} 归档为特征，Java 层仅 DefoldActivity + SDK JNI glue。详见 STRATEGY.md §1.2 类型表 "defold" 行 + §4.4 新建流程。
when_to_use: 当 stage-00 嗅探判定 lib/<abi>/<game>.so 内含 libdmengine.so，且 assets/ 含 game.dmanifest/game.projectc/game.arcd/game.arci 时调用。
---

# Defold 引擎逆向策略

> 处理 **Defold 引擎** 游戏的专用工作流。游戏逻辑以 Lua 脚本编译进 `game.arcd` 归档，
> Java 层为 `com.dynamo.android.DefoldActivity` + 各 SDK 的 JNI glue（`com.defold.*`）。
>
> **本 skill 遵循「引擎类型 ↔ 策略 skill 一对一」硬规则（AGENTS.md §1.12）**：
> Defold 不应降级到 `android` 兜底，一律路由到本 skill。

---

## 0. Skill 目录结构

```
skills/strategy/defold-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 识别特征 / 工具链 / 坑位
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具与脚本索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 阶段专用脚本
│   └── common/           ← 通用脚本
└── assets/               ← 资源（已知项目列表）
```

## 1. 加载顺序

1. **[SKILL.md](./SKILL.md)**（本文件）—— 总览 + 何时调用
2. **[strategy.md](./strategy.md)** —— 类型策略详述
3. **[workflow.md](./workflow.md)** —— 阶段流程 + 验证
4. **[tools-index.md](./tools-index.md)** —— 工具与脚本索引
5. **[EXPERIENCES.md](../../EXPERIENCES.md)** —— 经验沉淀
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `lib/<abi>/lib<game>.so` 内字符串含 `libdmengine.so` | `strings <so> \| grep dmengine` |
| `assets/game.dmanifest` + `game.projectc` + `game.arcd` + `game.arci` | `unzip -l <apk>` |
| Java 层含 `com.dynamo.android.DefoldActivity` + `com.defold.*JNI` | jadx / smali |

## 3. 默认策略（阶段序列）

```
00 → 00a → 01 → 02 → 03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

**与 android 兜底的关键差异**：
- 汉化走 **lang pack 替换**（`res/raw/bk_lang_pack.zip` 哨兵 → zh-Hans 真实包），详见 strategy.md §汉化。

详见 [strategy.md](./strategy.md)。

## 4. 验收清单

| 阶段 | 关键产物 | 验证命令 |
|------|---------|---------|
| 09 | manifest 清理 | `grep -ci "applovin\|firebase\|mbridge" AndroidManifest.xml` = 0 |
| 10 | 重打包签名 | `apksigner verify patched.apk` 通过 |
| 11 | 运行时验证 | `adb logcat *:E \| grep FATAL` 空 |
| 汉化 | lang pack 生效 | `adb logcat \| grep "ENTSCHIEDEN: Sprache zh-hans (Pack aktiv, Sentinel PASS)"` |

## 5. 已知项目

- **BananaKong**（com.fdgentertainment.bananakong）2026-08-04 —— 首个 Defold 项目，定义本 skill 基线。见 EXPERIENCES.md。

## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：defold](../../common/third-party-removal-strategy-skill/references/engine-notes.md#defold)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

