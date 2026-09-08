---
name: air-strategy-skill
description: 处理 Adobe AIR 项目的专用工作流。使用 ffdec + swfmill 反编译/编辑 SWF。详见 STRATEGY.md §1.2 类型表 "air" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=air（assets/META-INF/AIR/application.xml + *.swf）；或需要汉化 Adobe AIR SWF 游戏时调用。
---

# Adobe AIR 项目逆向策略

> 处理 **Adobe AIR** 项目（Flash/AIR 移植到 Android）的专用工作流。
> 加载顺序：[SKILL.md](#1-加载顺序) → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/air-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 策略详述（识别/工具/坑位）
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 流程脚本
│   └── common/           ← 通用脚本（含继承自原 air-localization 的 swf-text-import.sh）
├── assets/               ← 资源
└── references/
    └── corona-sdk-patterns.md   # Corona SDK (Solar2D) 逆向模式
```

## 1. 加载顺序

1. [SKILL.md](./SKILL.md) — 总览 + 何时调用
2. [strategy.md](./strategy.md) — 类型策略详述
3. [workflow.md](./workflow.md) — 阶段流程 + 验证
4. [tools-index.md](./tools-index.md) — 工具与脚本索引
5. [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

### 2.1 触发条件

| 信号 | 检测方式 |
|------|---------|
| `assets/META-INF/AIR/application.xml` | `unzip -l <apk>` |
| `assets/*.swf` | SWF ActionScript 字节码（核心游戏代码） |
| `<application android:name="air.my.application.AppEntry"` | AndroidManifest 入口 |
| 汉化目标在 SWF 内嵌文本 | 不在 strings.xml 或 smali |

### 2.2 调用方式

```bash
# 通过 crack.py 主驱动（推荐）
./skills/common/scripts/crack.py <apk>           # 自动嗅探 + 路由

# 单阶段
./skills/common/scripts/crack.py <apk> stage-air-03    # SWF 反编译
./skills/common/scripts/crack.py <apk> stage-air-09    # 字体嵌入
./skills/common/scripts/crack.py <apk> stage-10        # 重打包 + 签名
```

## 3. 默认策略

```
00 → 00a → 01 → 02 → air-03 → 04 → 05 → 06 → 07 → air-09 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `air-03`：SWF 反编译（ffdec）
- `air-09`：AIR 字体嵌入到 SWF

详见 [strategy.md](./strategy.md)。

## 4. SWF 文本类型判断（汉化场景）

| 特征 | 类型 | 可用方案 |
|------|------|---------|
| ffdec export 显示 `DefineEditText` | 动态文本 | A (CLI 直接回灌) |
| ffdec export 显示 `DefineText` | 静态字形 | B1/B2/B3 (注入/GUI/swfmill) |
| 文本不出现在 ffdec export 中 | 图片/位图 | OCR → 图片替换 (stage-06/07) |

## 5. 验收清单

| 阶段 | 关键产物 | 验证 |
|------|---------|------|
| air-03 | SWF 反编译产物 | 至少 1 个 AS 类可见 |
| air-09 | 字体嵌入 SWF | 抓屏 OCR 主菜单能识别中文 |
| 10 | 重打包 + 签名 | 三签齐全 |

## 6. 工具链

| 工具 | 用途 | 安装 |
|------|------|------|
| **JPEXS ffdec** | SWF 反编译/编辑/重编译 | ✅ 已安装 `tools/crack-intergration-tools/` |
| **AS3 注入** (内置) | 运行时 TextField 覆盖静态文本 | ✅ 内置 `inject-as-text.sh` |
| **swfmill** | XML 驱动的 SWF 编辑器 | ❌ 需手动安装 `install-swfmill.sh` |
| **Python 回退** | 二进制字符串替换 | ✅ 内置 `filter-swf-strings.py` |
| **fontTools** | 中文字体子集化 | `pip install fonttools brotli` |
| **baoyu-translate** | 自动翻译 | `~/.agents/skills/baoyu-translate/` |

## 7. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| ffdec 反编译崩溃 | SWF 加密 / 损坏 | 用 ffdec deobfuscator；或换 jpexs-decompiler |
| 字体替换后字体丢失 | SWF 中字体 ID 变化 | ffdec 用相同 fontId；保留原 glyph 索引 |
| patched.apk 启动崩溃 | AIR 签名校验失败 | Frida hook AIR 签名校验函数 |
| SWF 反编译混淆（Alchemy） | ActionScript 编译为字节码 | ffdec deobfuscator + 字符串解密 |
| DefineEditText 不能直接回灌 | 静态字形（DefineText） | 用 B1 AS3 注入 / B2 GUI / B3 swfmill |

## 8. 关联文档

| 文档 | 角色 |
|------|------|
| [strategy.md](./strategy.md) | 类型策略详述 |
| [workflow.md](./workflow.md) | 阶段流程 |
| [tools-index.md](./tools-index.md) | 工具索引 |
| [EXPERIENCES.md](../../EXPERIENCES.md) | 经验沉淀 |
| [references/corona-sdk-patterns.md](./references/corona-sdk-patterns.md) | Corona SDK (Solar2D) 逆向模式 |
| [../../STRATEGY.md §1.2](../../STRATEGY.md#12-类型快速识别表路由核心) | 类型识别速查表（air 行） |
| [../../WORKFLOW.md](../../WORKFLOW.md) | 顶层 7 大阶段主流程 |
| [../../OBJECTIVES.md §1.5](../../OBJECTIVES.md) | 网络检测去除验收 |
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

