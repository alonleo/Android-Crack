---
name: cocos2dx-strategy-skill
description: 处理 Cocos2d-x (C++ + Lua) 项目的专用工作流。使用 readelf + objdump + Frida 分析 libMyGame.so + Lua 脚本。详见 STRATEGY.md §1.2 类型表 "cocos2dx" 行。
when_to_use: 当 sub-stage-assess 嗅探判定 type=cocos2dx（libMyGame.so / libgame.so / libcocos2d*.so + assets/*.lua）；或包含 Cocos2dxActivity Java 类时调用。
---

# Cocos2d-x C++ + Lua 逆向策略

> 处理 **Cocos2d-x（C++ + Lua）** 项目的专用工作流。
> `JurassicPixelCraft` 类型（libMyGame.so 20-50 MB + PGL 加固 + 5+ dex）。
>
> 加载顺序：[SKILL.md](#1-加载顺序) → **[SKILL.md 之后所有文档]**。

## 0. Skill 目录结构

```
skills/strategy/cocos2dx-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 策略详述（识别/工具/坑位）
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 流程脚本
│   └── common/           ← 通用脚本
├── assets/               ← 资源
└── references/           ← 已知模式（继承自原 cocos2dx-crack-experience）
    └── known-patterns.md
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
| `lib/armeabi-v7a/librslg.so` 或 `libMyGame.so` 等 | `unzip -l <apk>` |
| `org/cocos2dx/lib/Cocos2dxActivity` | Java 类 |
| 资源目录 `assets/` 含 `.mt` 加密文件 / `config.lua` / `resList.lua` | 资源嗅探 |
| `libcocos2d*.so` | Cocos2d-x 引擎库 |
| `assets/*.lua` / `assets/*.luac` | Lua 脚本（可能加密） |

### 2.2 调用方式

```bash
./skills/common/scripts/crack.py <apk>                   # 自动嗅探 + 路由
./skills/common/scripts/crack.py <apk> stage-cocos-03    # so + Lua 分析
./skills/common/scripts/crack.py <apk> stage-cocos-05    # Lua 提取 / 解密
```

## 3. 默认策略

```
00 → 00a → 01 → 02 → cocos-03 → 04 → cocos-05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `cocos-03`：so + Lua 分析
- `cocos-05`：Lua 提取 / 解密

详见 [strategy.md](./strategy.md)。

## 4. 关键模式

### 4.1 Java 层 SDK 剔除（Cocos2d-x 插件模式）

Cocos2d-x 游戏通常通过 PluginWrapper 接入渠道 SDK：
- UC/九游 → patch `SocialUC.smali` / `IABUC.smali`
- 华为 → patch `SocialHW.smali` / `IABHW.smali`
- 小米 → patch `SocialXiaomi.smali`
- 通用模式：`login()` + `payForProduct()` 直接回调成功

### 4.2 Native 层网络阻断

使用 Frida hook `libMyGame.so` 中的 `socket_connect`：
```bash
# Frida hook Java ↔ Lua 桥接
hook org.cocos2dx.lib.Cocos2dxLuaJavaBridge.callLuaFunction

# Hook 网络
hook socket_connect  # 防止卡服务器验证
```

### 4.3 资源解密（.mt 文件）

```
Header: "Antm" + version(1) + type(1) + ???(2) + original_size(4) + reserved(4)
```

加密库：`libilongyuan_encryption.so`（Bangcle AES）
Key 位置：Java 类 `com.ilongyuan.encryption.EncryptionTool.KEY`（大整数 hex）

### 4.4 协议分析

- 网络库：LuaSocket（`luaopen_socket_core`）
- 抓包：PCAPdroid（no-root）或 tcpdump（需要 root）
- mock server：`skills/common/scripts/network-analyze/mock-server.py`

## 5. 验收清单

- [ ] apktool 解包成功
- [ ] jadx 反编译 + JDWP 分析
- [ ] SDK 登录/支付 stub
- [ ] socket_connect hook 阻断网络
- [ ] Lua 脚本提取 / 解密
- [ ] 重打包 + zipalign + apksigner 签名
- [ ] adb install 成功
- [ ] 游戏启动不崩溃

## 6. 已知 APK 示例

- **`JurassicPixelCraft`（com.tappocket.dinovillage）** — libMyGame.so 23MB + PGL 加固 + 5 SDK dex + 数 MB plist
- `CandyLegend`（libMyGame.so + IAP 模拟）
- `Julongzhizhan`（Cocos2d-x + Lua + librslg.so + UC SDK）

## 7. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| Lua 解密失败 | 密钥错误 | Frida hook `luaL_loadbuffer` 提取运行时密钥 |
| so 反汇编信息少 | 剥离符号 | `doNotStrip` 已配；用 `radare2 -A` 自动分析 |
| 启动闪退 | 资源 `$` 前缀未清理 | 阶段 09 用 grep + sed 清理 |
| AGP 资源编译失败 | 缺 `apktool.yml` | 阶段 02 验证 apktool.yml 存在 |
| patched.apk 体积过大 | 多 ABI | abiFilters 仅保留 arm64-v8a |

## 8. 关联文档

| 文档 | 角色 |
|------|------|
| [strategy.md](./strategy.md) | 类型策略详述 |
| [workflow.md](./workflow.md) | 阶段流程 |
| [tools-index.md](./tools-index.md) | 工具索引 |
| [EXPERIENCES.md](../../EXPERIENCES.md) | 经验沉淀 |
| [references/known-patterns.md](./references/known-patterns.md) | 已知模式 |
| [../../STRATEGY.md §1.2](../../STRATEGY.md#12-类型快速识别表路由核心) | 类型识别速查表（cocos2dx 行） |
| [../../WORKFLOW.md](../../WORKFLOW.md) | 顶层 7 大阶段主流程 |
| [../../OBJECTIVES.md §1.5](../../OBJECTIVES.md) | 网络检测去除验收 |
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

