# Cocos2d-x Strategy — C++ + Lua 逆向策略

> 处理 **Cocos2d-x（C++ + Lua）** 项目的专用策略。`JurassicPixelCraft` 类型。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `lib/<abi>/libMyGame.so` / `libgame.so` | **游戏核心 native 库**（通常 20-50 MB） |
| `lib/<abi>/libcocos2d*.so` | Cocos2d-x 引擎 |
| `lib/<abi>/libluacocos2d*.so` | 若用 Lua（含 Lua 引擎） |
| `assets/Replace/Plist/*.plist` 或 `assets/*.plist` | 本地化 plist |
| `assets/*.lua` / `assets/*.luac` | Lua 脚本（可能加密为 .luac / .mt） |
| smali | `org.cocos2dx.lib.Cocos2dxActivity` / `org.cocos2dx.cpp.AppActivity` |

## 2. 阶段序列

```
00 → 00a → 01 → 02 → cocos-03 → 04 → cocos-05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13
```

类型化分支：
- `cocos-03`：so + Lua 分析
- `cocos-05`：Lua 提取 / 解密

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| so 分析 | **readelf** + **objdump** + **capstone** | 系统 / IDA / Ghidra |
| Lua 提取 | **cocos-lua-extract** / 自写解密脚本 | `source-projects/` |
| 网络分析 | Frida hook `socket_connect` / `connect` | 系统安装 |
| 重打包 | apktool b + native hook 集成 | `execable/apktool.jar` |
| 静态反编译 | jadx | `source-projects/jadx/` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| `libMyGame.so` 中 `luaopen_*` / `tolua_pushuserdata` | Lua 注册函数（C++ ↔ Lua ↔ Java 桥接） |
| 网络协议相关函数（`recv` / `send` / `connect`） | 网络拦截点 |
| `libMyGame.so` 中加密字符串 | 自写解密脚本起点 |
| `assets/*.plist` | 本地化字典（汉化替换点） |
| `assets/*.luac` / `.mt` | 加密 Lua 脚本（需解密） |

## 5. 动态分析重点

```bash
# Frida hook libMyGame.so（基于反汇编地址）
frida -U -l hook-game.js -f <pkg> --no-pause

# Hook Java ↔ Lua 桥接
hook org.cocos2dx.lib.Cocos2dxLuaJavaBridge.callLuaFunction

# Hook 网络
hook socket_connect  # 防止卡服务器验证
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| 多 dex | Cocos 项目经常打包大量 SDK dex（5+ classes.dex） | AGP 必须配置 `multiDexEnabled true` |
| ndk abi filters | APK 体积膨胀 | 仅保留目标 ABI（如 arm64-v8a） |
| `doNotStrip` | 必须保留 `libMyGame.so`（不剥离符号） | 在 AGP `packagingOptions` 中配置 |
| apktool 期望 lib/ 而非 jniLibs/ | 与 AGP 默认行为不同 | 构建脚本特殊处理 |
| apktool.yml 必须存在 | apktool b 启动读取该文件 | 02 阶段产出后验证 |
| AGP 资源 `$` 限制 | apktool 解码后含 `$`-前缀的 drawable | 删除 + 清理 public.xml |
| So + Lua + Java 三层耦合 | 改一处可能需要其他两层配合 | 阶段 04 系统性摸清三层结构 |

## 7. 阶段细节

详见 [workflow.md](./workflow.md)。

## 8. 启用条件与回退

| 条件 | 处理 |
|------|------|
| 默认 | type=cocos2dx 自动触发；嗅探命中 `libMyGame.so` / `libgame.so` / `libcocos2d*.so` |
| Lua 加密 | `sub-stage-cocos-lua-extract.py` 解密（key 在 .so 中） |
| 多 dex | AGP `multiDexEnabled true` |
| PGL 加固 | 先脱壳（FDex2 / blackdex） |

## 9. 已知 APK 示例

- **`JurassicPixelCraft`（com.tappocket.dinovillage）** — libMyGame.so 23MB + PGL 加固 + 5 SDK dex + 数 MB plist
- `CandyLegend`（libMyGame.so + IAP 模拟）
- `Julongzhizhan`（Cocos2d-x + Lua + librslg.so + UC SDK）

## 10. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [references/known-patterns.md](./references/known-patterns.md) — 已知模式
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表（cocos2dx 行）
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

