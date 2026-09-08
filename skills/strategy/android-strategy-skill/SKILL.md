---
name: android-strategy-skill
description: 处理普通 Android（Java/Kotlin）APK 的标准逆向策略。无引擎保护、无 native hook，标准 13 阶段即可完成破解。详见 STRATEGY.md §1.2 类型表 "android" 行。
when_to_use: 当 sub-stage-assess 类型嗅探判定 type=android（仅含 classes*.dex，无任何 lib<engine>.so）；或难度评级 ≤ C（普通混淆）时调用。
---

# Android 普通 Java/Kotlin 逆向策略

> 处理**普通 Android（Java/Kotlin）APK** 的专用工作流。游戏不含游戏引擎 native 库，
> 仅由 Java/Kotlin 代码 + Android SDK + 标准第三方 SDK 组成，**标准 13 阶段**即可完成破解。
>
> 本 skill **不需要 native hook、不需要 inline hook、不需要 Frida（除非用动态辅助）**。
> 主路线：apktool 解包 → smali patch → apktool b 重打包。

---

## 0. Skill 目录结构

```
skills/strategy/android-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 策略详述（识别/工具/坑位）
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 流程脚本
│   └── common/           ← 通用脚本
└── assets/               ← 资源（混淆模式样例）
```

## 1. 加载顺序

Agent 选中本 skill 后按下列顺序加载：
1. **[SKILL.md](./SKILL.md)**（本文件）—— 总览 + 何时调用
2. **[strategy.md](./strategy.md)** —— 类型策略详述
3. **[workflow.md](./workflow.md)** —— 阶段流程 + 验证
4. **[tools-index.md](./tools-index.md)** —— 工具与脚本索引
5. **[EXPERIENCES.md](../../EXPERIENCES.md)** —— 经验沉淀
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

### 2.1 触发条件

| 信号 | 检测方式 |
|------|---------|
| `unzip -l <apk>` 仅含 `classes*.dex` | 无 `lib<engine>.so` |
| 难度评级 ≤ C（≤ 20 分） | `difficulty.json` |
| type 路由到 android | `strategy-config.yaml` 中 type=android |

### 2.2 调用方式

```bash
# 通过 crack.py 主驱动（推荐）
./skills/common/scripts/crack.py <apk>           # 自动嗅探 + 路由

# 单阶段
./skills/common/scripts/crack.py <apk> stage-03  # jadx 反编译
./skills/common/scripts/crack.py <apk> stage-09  # SDK 移除
```

## 3. 默认策略（标准 13 阶段）

```
00 → 00a → 01 → 02 → 03 → 04 → 05 → 06 → 09 → 10 → 11 → 12 → 13
```

**关键差异（vs il2cpp）**：
- ❌ 不需要 `02b` FakerAndroid
- ❌ 不需要 `03b` Il2CppDumper
- ❌ 不需要 `04b` / `04c` / `08b` hook 脚手架
- ✅ 主路径：apktool 解包 + smali patch
- ✅ 主要工具：jadx（Java 反编译）+ apktool（解/打包）

详见 [strategy.md](./strategy.md)。

## 4. 验收清单

| 阶段 | 关键产物 | 验证命令 |
|------|---------|---------|
| 02 | apktool 解包 | `ls crackings/<type>/<Name>/raw/01-apktool/AndroidManifest.xml` |
| 03 | jadx 反编译 | `ls crackings/<type>/<Name>/raw/02-jadx/sources/` |
| 09 | SDK 移除 | `grep -ci "firebase\|ironsource\|playgenesis" AndroidManifest.xml` = 0 |
| 10 | 重打包签名 | `apksigner verify --verbose patched.apk` 三签齐全 |
| 11 | 运行时验证 | `adb logcat *:E \| grep FATAL` 空 |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| MultiDex 5+ classes.dex | 大型 APK 必现 | 阶段 02 加 `--multi-dex`；debug 时 Frida 同样 `--multi-dex` |
| ProGuard/R8 强混淆 | 名字变 a/b/c | 用 jadx --deobf 增强；或换 d2j-dex2jar + CFR |
| 加固（360/乐固/梆梆/PGL） | smali 被加密 | 先脱壳（FDex2 / blackdex / DexDump），再走标准流程 |
| AndResGuard 资源混淆 | res 名变 r/a/a.xml | 用 `aapt2 dump xmltree` 直接看 raw 资源 |
| 启动崩溃（移除 SDK 后） | 桥接类引用空指针 | 用策略 A（桩化）保留 stub 类，避免策略 C（物理删除） |

## 6. 关联文档

| 文档 | 角色 |
|------|------|
| [strategy.md](./strategy.md) | 类型策略详述 |
| [workflow.md](./workflow.md) | 阶段流程 |
| [tools-index.md](./tools-index.md) | 工具索引 |
| [EXPERIENCES.md](../../EXPERIENCES.md) | 经验沉淀 |
| [../../STRATEGY.md §1.2](../../STRATEGY.md) | 类型识别速查表（android 行） |
| [../../WORKFLOW.md](../../WORKFLOW.md) | 顶层 7 大阶段主流程 |
| [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) | SDK 移除验收硬指标 |
| [../../AGENTS.md §1.2](../../AGENTS.md) | 环境加载约束 |
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

