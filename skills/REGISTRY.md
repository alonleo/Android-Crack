# Skills 注册表

> **Agent 首次进入工作区时必须加载本文件**。本表是调用 skill 的唯一索引。
> 新增 skill 后必须在此表追加一行。

---

## 工作区 skill

| Skill | 位置 | 触发场景 | 策略位置 |
|-------|------|---------|---------|
| **general-strategy-skill** | `skills/common/general-strategy-skill/` | 遇到未注册的新 type 时，逐阶段读取根 WORKFLOW.md，创建、注册并验证规范 type skill；同时承载公共阶段实现 | [STRATEGY.md §2.1](../STRATEGY.md#21-冲突与未知类型) → skill |
| **adjusting-sub-stages** | `skills/common/adjusting-sub-stages/` | 全局或单个既有 type 的子阶段新增、删除、重命名、重排、脚本/action 替换 | 根 [WORKFLOW.md](../WORKFLOW.md) + 目标 type register |
| **il2cpp-strategy-skill** | `skills/strategy/il2cpp-strategy-skill/` | Unity il2cpp 加密项目（FakerAndroid + Hook 模板架构） | [STRATEGY.md §1.2 il2cpp 行](../STRATEGY.md) → skill |
| **android-strategy-skill** | `skills/strategy/android-strategy-skill/` | 普通 Java/Kotlin Android（标准 15 阶段） | [STRATEGY.md §1.2 android 行](../STRATEGY.md) → skill |
| **unity-mono-strategy-skill** | `skills/strategy/unity-mono-strategy-skill/` | Unity Mono / .NET DLL（ILSpy/dnSpy） | [STRATEGY.md §1.2 unity-mono 行](../STRATEGY.md) → skill |
| **cocos2dx-strategy-skill** | `skills/strategy/cocos2dx-strategy-skill/` | Cocos2d-x C++ + Lua（readelf + Frida + Lua 解密） | [STRATEGY.md §1.2 cocos2dx 行](../STRATEGY.md) → skill |
| **cocos-creator-strategy-skill** | `skills/strategy/cocos-creator-strategy-skill/` | Cocos Creator JS/TS（cc-reverse + XXTEA） | [STRATEGY.md §1.2 cocos-creator 行](../STRATEGY.md) → skill |
| **unreal-strategy-skill** | `skills/strategy/unreal-strategy-skill/` | Unreal Engine 4/5（UE dumper + IDA） | [STRATEGY.md §1.2 unreal 行](../STRATEGY.md) → skill |
| **flutter-strategy-skill** | `skills/strategy/flutter-strategy-skill/` | Flutter Dart AOT（blutter + Dart SDK） | [STRATEGY.md §1.2 flutter 行](../STRATEGY.md) → skill |
| **xamarin-strategy-skill** | `skills/strategy/xamarin-strategy-skill/` | Xamarin Mono runtime（ILSpy/dnSpy） | [STRATEGY.md §1.2 xamarin 行](../STRATEGY.md) → skill |
| **air-strategy-skill** | `skills/strategy/air-strategy-skill/` | Adobe AIR（ffdec + SWF 反编译） | [STRATEGY.md §1.2 air 行](../STRATEGY.md) → skill |
| **defold-strategy-skill** | `skills/strategy/defold-strategy-skill/` | Defold 引擎（libdmengine.so + game.dmanifest/arcd；lang pack 汉化） | [STRATEGY.md §1.2 defold 行](../STRATEGY.md) → skill |
| **gamemaker-strategy-skill** | `skills/strategy/gamemaker-strategy-skill/` | GameMaker Studio 引擎（libyoyo.so + game.droid FORM..GEN8；YYObjectBase/RValue/JNI glue；GML 编译进 CODE chunk） | [STRATEGY.md §1.2 gamemaker 行](../STRATEGY.md) → skill |
| **libgdx-strategy-skill** | `skills/strategy/libgdx-strategy-skill/` | libGDX 引擎（libgdx.so + com.badlogic.gdx；TTF 替换汉化） | [STRATEGY.md §1.2 libgdx 行](../STRATEGY.md) → skill |
| **third-party-removal-strategy-skill** | `skills/common/third-party-removal-strategy-skill/` | 去第三方 SDK 统一资料：分类、依赖、12 个 type 实现要点和 03/04 共用要求；执行由 type 注册表路由 | [STRATEGY.md §3](../STRATEGY.md) → skill |
| **feature-removal-strategy-skill** | `skills/common/feature-removal-strategy-skill/` | 去功能点统一资料：分类、依赖边界、12 个 type 实现要点与 07/08 共用接口；执行由 type 注册表路由 | [WORKFLOW.md §2.1 阶段 07/08](../WORKFLOW.md) → skill |
| **hanization-strategy-skill** | `skills/common/hanization-strategy-skill/` | 字体、文本与图片汉化的分类、质量边界与经验参考；实际执行以已路由 type skill workflow 为准 | [WORKFLOW.md §2.1 阶段 09–14](../WORKFLOW.md) → skill |

## 全局 skill

| Skill | 位置 | 触发场景 |
|-------|------|---------|
| **systematic-debugging** | `~/.agents/skills/systematic-debugging/` | 反编译产物含反调试 / 异常行为 |
| **diagnosing-bugs** | `~/.agents/skills/diagnosing-bugs/` | 工具调用失败 / 异常栈 |
| **dispatching-parallel-agents** | `~/.agents/skills/dispatching-parallel-agents/` | 大量文档/源码需要并行审阅 |
| **codebase-deep-documentation** | `~/.agents/skills/codebase-deep-documentation/` | 工具源码需深度理解 |
| **baoyu-image-gen** | `~/.agents/skills/baoyu-image-gen/` | 反编译产物需 UI 截图说明 / 汉化图片生成 |
| **baoyu-translate** | `~/.agents/skills/baoyu-translate/` | 字符串翻译 / 汉化 |
| **claude-handoff** | `~/.agents/skills/claude-handoff/` | 整套工作流跨多 session 交接 |
| **finishing-a-development-branch** | `~/.agents/skills/finishing-a-development-branch/` | 收尾 / 是否进入下一个 APK |

## Skill 标准结构

> 每个 `<type>-strategy-skill` 必须遵循下述文档与目录结构。`skills/common/` 下的横切 skill 不受此结构硬性约束，按实际职责组织。

```
skills/strategy/<type>-strategy-skill/
├── SKILL.md              ← 总览 + 加载顺序 + 何时调用
├── strategy.md           ← 类型策略详述（识别/工具/坑位）
├── workflow.md           ← 阶段流程（命令 + 验证 + 故障处理）
├── tools-index.md        ← 工具与脚本索引
├── experiences.md        ← type 私有逆向问题经验库
├── scripts/
│   ├── workflow/         ← 阶段专用脚本
│   └── common/           ← 通用脚本（命名 <verb>-<scope>.py）
└── assets/               ← 资源（heuristic 规则 / 已知项目列表）
```

**加载顺序**（agent 选中 skill 后）：
1. `SKILL.md` — 总览 + 何时调用
2. `strategy.md` — 类型策略
3. `workflow.md` — 阶段流程
4. `tools-index.md` — 工具索引
5. `experiences.md` — 当前 type 私有问题经验（按需加载）
6. [EXPERIENCES.md](../../EXPERIENCES.md) — 跨 type 通用问题经验（按需加载）
