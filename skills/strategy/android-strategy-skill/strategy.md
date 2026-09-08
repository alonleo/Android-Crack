# Android Strategy — 普通 Java/Kotlin 逆向策略详述

> 本文件是 android-strategy-skill 的"策略详述"——包含识别特征、阶段序列、工具、坑位。
>
> 加载顺序：SKILL.md → **[strategy.md（本文件）]** → workflow.md → tools-index.md

---

## 1. 识别特征

| 项 | 期望 |
|----|------|
| `classes*.dex` | 仅含 dex（可能多个，MultiDex） |
| `lib/<abi>/*.so` | **不存在**任何引擎 lib（libil2cpp / libUE4 / libMyGame 等） |
| AndroidManifest | `<application android:name>` 指向 Java/Kotlin Application 子类 |
| smali 路径 | `L<top-level-domain>/<company>/<app>/...;`（遵循 `<tld>/<company>/<app>/...`） |

**反例**（命中即走其他 skill）：
- 含 `libil2cpp.so` → il2cpp-strategy-skill
- 含 `libUE4.so` → unreal-strategy-skill
- 含 `libMyGame.so` / `libcocos2d*.so` → cocos2dx-strategy-skill
- 含 `libflutter.so` + `libapp.so` → flutter-strategy-skill
- 含 `libmonodroid.so` / `libmono-native.so` → xamarin-strategy-skill
- 含 `GameAssembly.dll` + `*.dll` → unity-mono-strategy-skill

## 2. 阶段序列（通用子阶段骨架 01–21，仿 il2cpp 模型）

```
00 → 00a → 01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12
→ 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20 → 21
```

- **01–06 分析**：完整性记录 / apktool 解包 / jadx 静态分析 / 入口定位 / 字符串提取 / 图片识别
- **07–16 修改+真机验收对**（每个修改阶段紧跟 device-verify，成功→强制固化）：
  - 07/08 图片汉化 · 09/10 字体替换 · 11/12 SDK 移除 · 13/14 去功能点 · 15/16 汉化
- **17–21 交付**：重打包签名 / 运行时验证 / AS 工程化 / 最终验收 / 清理

强制阶段（strategy-config `mandatory`）：`01 02 03 05 07 09 11 13 15 17 18 20`。
真机验收 08/10/12/14/16 防「卡加载误判」：多窗口采样 + 渲染帧推进（common-stage `lib/device_verify_common.py`）。
旧编号（10→17、11→18、12→19、13→20、15→21）由 `legacy_stage_map` 迁移。

## 3. 主要工具

| 用途 | 工具 | 路径 |
|------|------|------|
| 静态反编译 | **jadx** | `tools/crack-intergration-tools/source-projects/jadx/` |
| 解包 / 打包 | **apktool** | `tools/crack-intergration-tools/execable/apktool.jar` |
| 重签名 | **apksigner** | `tools/environments/android-sdk/build-tools/34.0.0/apksigner` |
| 对齐 | **zipalign** | `tools/environments/android-sdk/build-tools/34.0.0/zipalign` |
| 动态辅助 | Frida（仅当需 hook Java 层） | 系统安装 |
| 资源解码 | aapt2 | `tools/environments/android-sdk/build-tools/34.0.0/aapt2` |

## 4. 静态分析重点

| 切入点 | 找什么 |
|--------|-------|
| `Application.onCreate()` | 第三方 SDK 初始化点 |
| Activity `launchMode` / `intent-filter` | 主入口 Activity 路径 |
| `ContentProvider.onCreate()` | 自启动点（早于 Application） |
| `BroadcastReceiver` | 隐式触发点 |
| `Service.onCreate()` | 后台服务 |
| `WebView.loadUrl()` | H5 容器（部分游戏用 WebView 加载逻辑） |

## 5. 动态分析重点（可选）

```bash
# Frida attach（仅当需要）
frida -U -l script.js -f <pkg> --no-pause

# Hook 关键点
hook Activity.startActivity       # 看跳转链路
hook Toast.show / Log.d           # 看运行状态
hook System.currentTimeMillis     # 时间反作弊绕过
hook Signature.toString           # 签名校验绕过
```

## 6. 常见坑位

| 坑位 | 现象 | 处理 |
|------|------|------|
| MultiDex（5+ classes.dex） | jadx / Frida 默认只看主 dex | 加 `--multi-dex`；frida `-C` 全局参数；jadx 用最新版本自动处理 |
| ProGuard / R8 强混淆 | 方法名变 a/b/c | jadx 加 `--no-res`；CFR 反编译兜底；重要方法用 `trace` + `(a)` 改名 |
| 加固（360 / 乐固 / 梆梆 / PGL） | dex 被加密 | 先脱壳：FDex2 / blackdex / DexDump；再用本 skill |
| AndResGuard 资源混淆 | res 名变 `r/a/a.xml` | 用 `aapt2 dump xmltree <apk> --file r/a/a.xml` 直接看 |
| Multi-Locale 资源 | `values-zh-rTW` / `values-ja` 等多语言 | 阶段 11 清理仅保留 `values/` + `values-zh-rCN/` |
| Application 多 dex 加载 | `Application.attachBaseContext` 钩子链 | 看 `MultiDex.install` 调用位置；勿动 base 库 |

## 7. 阶段细节（执行命令）

详见 [workflow.md](./workflow.md)。

## 8. 启用条件与回退

| 条件 | 处理 |
|------|------|
| 默认 | type=android 自动触发；无需手动指定 |
| 加固 | **先脱壳**（FDex2/blackdex），再走标准流程 |
| 资源混淆 | 走通用阶段 09 + 资源清理 |

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程、命令、验证
- [tools-index.md](./tools-index.md) — 工具与脚本索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../STRATEGY.md §1.2](../../STRATEGY.md) — 类型识别速查表
- [../../WORKFLOW.md](../../WORKFLOW.md) — 顶层 7 大阶段主流程
- [../../OBJECTIVES.md §1.3](../../OBJECTIVES.md) — SDK 移除验收硬指标
## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

