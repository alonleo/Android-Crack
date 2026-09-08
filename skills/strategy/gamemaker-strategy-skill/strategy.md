# GameMaker Studio 引擎策略详述

> 识别特征 / 工具链 / 坑位。来源: FindTheDifferences (com.fdg.findthedifferences) | 2026-08-08

## 1. 识别特征

| 特征 | 值 |
|------|-----|
| 引擎库 | `lib/<abi>/libyoyo.so`（YoYo Games 官方 runner） |
| 引擎内字符串 | `YYObjectBase` / `RValue` / `Java_com_yoyogames_runner_RunnerJNILib_*` / `_ZN8Rollback*` |
| assets 签名 | `assets/game.droid`（FORM..GEN8 magic，~15MB）— GameMaker Studio 2 归档 |
| Java 层 | `com.yoyogames.runner.RunnerActivity`（launchable）+ `RunnerJNILib`（JNI glue） |
| 语言支持 | GMS2 `.droid` LANG chunk + game strings；不依赖 Android strings.xml |
| 版本信息 | AndroidManifest.xml + GameMaker project settings 编译进 OPTN chunk |

### 1.1 .droid 格式 chunk 列表（GEN8）

```
FORM .... GEN8 ....    ← archive magic（FORM = IFF / GEN8 = GameMaker 8 格式）
├── OPTN    选项
├── LANG    语言字符串
├── EXTN    扩展
├── SOND    声音
├── SPRT    精灵
├── BGND    背景
├── PATH    路径
├── SCPT    脚本
├── GLOB    全局变量
├── SHDR    着色器
├── FONT    字体
├── TMLN    时间线
├── OBJ     对象
├── FEDS    ???（GameMaker 内部）
├── ACRV    动画曲线
├── SEQN    序列
├── TAGS    标签
├── ROOM    房间
├── DAFL    数据文件
├── EMB I   嵌入资源
├── PSEM    粒子系统发射器
├── PSYS    粒子系统
├── TPAG    纹理页面
├── TGIN    纹理组信息
└── CODE    GML 编译字节码
```

### 1.2 关键 JNI 入口（Java glue）

| 符号 | 用途 |
|------|------|
| `Java_com_yoyogames_runner_RunnerJNILib_Startup` | 启动入口 |
| `Java_com_yoyogames_runner_RunnerJNILib_Process` | 主循环 |
| `Java_com_yoyogames_runner_RunnerJNILib_RenderSplash` | 启动画面 |
| `Java_com_yoyogames_runner_RunnerJNILib_TouchEvent` | 触摸输入 |
| `Java_com_yoyogames_runner_RunnerJNILib_HttpResult` | HTTP 异步回调 |
| `Java_com_yoyogames_runner_RunnerJNILib_HttpProgress` | HTTP 进度回调 |
| `Java_com_yoyogames_runner_RunnerJNILib_HttpResultString` | HTTP 字符串回调 |
| `Java_com_yoyogames_runner_RunnerJNILib_CloudResultData` | 云存档 |
| `Java_com_yoyogames_runner_RunnerJNILib_CloudResultString` | 云存档字符串 |
| `Java_com_yoyogames_runner_RunnerJNILib_LoginResult` | 社交登录 |
| `Java_com_yoyogames_runner_RunnerJNILib_InputResult` | IAP 入口 |
| `Java_com_yoyogames_runner_RunnerJNILib_BackKeyLongPressEvent` | 返回键 |
| `Java_com_yoyogames_runner_RunnerJNILib_dsMapCreate` | dsMap 创建 |
| `Java_com_yoyogames_runner_RunnerJNILib_dsListCreate` | dsList 创建 |
| `Java_com_yoyogames_runner_RunnerJNILib_jCreateDsMap` | Java 侧创建 dsMap |

## 2. 工具链

| 用途 | 工具 |
|------|------|
| 解包/重打包 | apktool 2.11.1（`apktool d` / `apktool b`） |
| Java 静态分析 | jadx |
| 引擎/归档分析 | `strings` / `readelf`（.so）；`.droid` 内 GML 逻辑在 CODE chunk（加密二进制，需 UndertaleModTool / 自定义提取） |
| 汉化 | `.droid` LANG chunk 字符串提取替换（待写脚本） |
| 动态验证 | adb + logcat（GameMaker 输出 `yoyo` / `runner` / `GameMaker` tag） |

## 3. 坑位

### 3.1 native JNI 依赖 → 禁止物理删 SDK smali

实现要点见 [去第三方 SDK：gamemaker](../../common/third-party-removal-strategy-skill/references/engine-notes.md#gamemaker)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 3.2 GML 逻辑不可静态 patch

- 与 il2cpp（dump IL2CPP metadata + patch binary）或 Android（smali patch）不同，
  GML 编译进 `game.droid` 的 CODE chunk 是加密的 bytecode，无法像 smali 那样直接 patch。
- **汉化**: 必须提取 LANG chunk 中的字符串，patch 后重打包 .droid（需自定义脚本或 UndertaleModTool）。
- **去功能点（按钮移除）**：ROOM 三处实例列表、动态对象创建与代码替换统一见 [GameMaker 去功能点说明](../../common/feature-removal-strategy-skill/references/engine-notes.md#gamemaker)。

### 3.3 仅 arm64-v8a 单 ABI

- GameMaker 项目一般只编译单 ABI → APK 体积优化；不需要 `ndk.abiFilters` 过滤。

### 3.4 XAPK split 合并后 resources.arsc 不完整

- 同 Defold，XAPK config split 各自带 resources.arsc；简单合并仅保留 base 的 arsc。
- **manifest 会残留 `requiredSplitTypes="base__abi,base__density"`** → 必须删除，否则 `INSTALL_FAILED_MISSING_SPLIT`。

## 4. 静态分析重点

1. 先确认引擎类型（`strings libyoyo.so | grep YYObjectBase`）→ 强信号。
2. 反编译 `RunnerJNILib.java` → 看 JNI glue 调用哪些 SDK 类。
3. 检查 manifest 的 provider/activity/service/receiver → 决定 SDK 移除清单。
4. 检查 `assets/game.droid` 的 chunk 列表 → 决定可汉化内容（LANG chunk）。
5. `hexdump game.droid | head -1` → 确认 FORM..GEN8 magic。

## 5. 动态分析重点

- `adb logcat | grep -E "yoyo|runner|GameMaker|YYRunner"`（GameMaker 自有日志）。
- 启动后确认进入主场景（具体 tag 待首个项目验证）。
- 飞行模式测试：移除网络检测后应能启动+加载+游玩。

## 6. 已知 APK 示例

- **FindTheDifferences**（com.fdg.findthedifferences）1.2.0，2026-08-08 —— 首个 GameMaker 项目。
  - libyoyo.so（13MB，arm64-v8a）
  - assets/game.droid（15MB）FORM..GEN8，含 img300_1/a*.jpg 关卡图
  - 关卡玩法：找两幅图片差异（spot-the-difference）

## 7. SDK 移除策略：JNI 桩化（规则）

实现要点见 [去第三方 SDK：gamemaker](../../common/third-party-removal-strategy-skill/references/engine-notes.md#gamemaker)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

## 8. 对照策略

实现要点见 [去第三方 SDK：gamemaker](../../common/third-party-removal-strategy-skill/references/engine-notes.md#gamemaker)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

