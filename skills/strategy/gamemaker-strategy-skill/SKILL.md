---
name: gamemaker-strategy-skill
description: 处理 GameMaker Studio 引擎 APK 的专用逆向策略。GameMaker 游戏以 libyoyo.so（含 YYObjectBase / RValue / Java_com_yoyogames_runner_RunnerJNILib_*） + assets/game.droid（FORM..GEN8 magic）为特征，Java 层为 com.yoyogames.runner.RunnerActivity + GameMaker Runtime JNI glue。详见 STRATEGY.md §1.2 类型表 "gamemaker" 行 + §4.4 新建流程。
when_to_use: 当 stage-00 嗅探判定 lib/<abi>/libyoyo.so 内含 YYObjectBase/RValue，且 assets/ 含 game.droid（FORM..GEN8 magic）时调用。
---

# GameMaker Studio 引擎逆向策略

> 处理 **GameMaker Studio** 游戏的专用工作流。游戏逻辑以 GML（GameMaker Language）
> 编译进 `game.droid` 归档的 CODE chunk，Java 层为 `com.yoyogames.runner.RunnerActivity`
> + GameMaker Runner JNI glue（`Java_com_yoyogames_runner_RunnerJNILib_*`）。
>
> **本 skill 遵循「引擎类型 ↔ 策略 skill 一对一」硬规则（AGENTS.md §1.12）**：
> GameMaker 不应降级到 `android` 兜底，一律路由到本 skill。

---

## 0. Skill 目录结构

```
skills/strategy/gamemaker-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 识别特征 / 工具链 / 坑位
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具与脚本索引
├── scripts/
│   ├── workflow/         ← 阶段专用脚本
│   └── common/           ← 通用脚本
└── assets/               ← 资源（已知项目列表）
```

## 1. 加载顺序

1. **[SKILL.md](./SKILL.md)**（本文件）—— 总览 + 何时调用
2. **[strategy.md](./strategy.md)** —— 类型策略详述
3. **[workflow.md](./workflow.md)** —— 阶段流程 + 验证
4. **[tools-index.md](./tools-index.md)** —— 工具索引
5. **[EXPERIENCES.md](../../EXPERIENCES.md)** —— 经验沉淀

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `lib/<abi>/libyoyo.so`（或 lib<gamename>.so） | `unzip -l <apk> \| grep lib/` |
| `.so` 内字符串含 `YYObjectBase`/`RValue`/`Java_com_yoyogames_runner_RunnerJNILib_*` | `strings <so> \| grep -E "YYObjectBase\|RValue\|yoyogames"` |
| `assets/game.droid`（FORM..GEN8 magic，~15MB） | `unzip -l <apk>` + `hexdump game.droid \| head -1` |
| Java 层含 `com.yoyogames.runner.RunnerActivity` + `RunnerJNILib` | jadx / smali |

## 3. 默认策略（阶段序列）

> **遵循通用 01–21 骨架**（WORKFLOW.md §1.3）。


**与其他 engine-skill 的关键差异**：

- **去功能点**：实现与限制见 [GameMaker 去功能点说明](../../common/feature-removal-strategy-skill/references/engine-notes.md#gamemaker)，07/08 阶段必须执行并验证。
- **图片汉化走 .droid LANG chunk**（stage-15）：跳过 07/08，不依赖 res/drawable。
- **字体汉化走 .droid FONT chunk**：跳过 09/10，GameMaker 内部 SpriteFont 不走 Android Typeface。

详见 [strategy.md](./strategy.md)。

## 4. 验收清单

| 阶段 | 关键产物 | 验证命令 |
|------|---------|---------|
| 00 | 类型判定 GameMaker | `strings libyoyo.so \| grep YYObjectBase` 命中 |
| 00a | 6 维度评估 | `crackings/<type>/<Name>/difficulty.json` |
| 02 | apktool 解包 | `apktool b` 零错误 |
| 03 | Java glue 清单 | jadx 输出 `RunnerJNILib` |
| 09 | manifest 清理 | `grep -ci "applovin\|firebase\|play.services" AndroidManifest.xml` = 0 |
| 10 | 重打包签名 | `apksigner verify patched.apk` 通过 |
| 11 | 运行时验证 | `adb logcat *:E \| grep FATAL` 空 |
| 13 | 最终验收 | 6 条硬指标（OBJECTIVES.md §1） |

## 5. 已知项目

- **FindTheDifferences**（com.fdg.findthedifferences）1.2.0，2026-08-08 —— 首个 GameMaker 项目，定义本 skill 基线。
  - libyoyo.so（13MB）含 GameMaker Studio 2 runtime
  - assets/game.droid（15MB）FORM..GEN8 含 img300_1/a*.jpg 关卡图
  - 见 [EXPERIENCES.md](../../EXPERIENCES.md)。

## 6. 关联阅读

- [strategy.md](./strategy.md) — 类型策略详述
- [workflow.md](./workflow.md) — 阶段流程 + 验证
- [STRATEGY.md §1.2](../../STRATEGY.md) — 类型快速识别表 gamemaker 行
- [AGENTS.md §1.12](../../AGENTS.md) — 引擎类型 ↔ skill 一对一硬规则

## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：gamemaker](../../common/third-party-removal-strategy-skill/references/engine-notes.md#gamemaker)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

