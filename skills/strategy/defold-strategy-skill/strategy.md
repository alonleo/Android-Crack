# Defold 引擎策略详述

> 识别特征 / 工具链 / 坑位。来源: BananaKong (com.fdgentertainment.bananakong) | 2026-08-04

## 1. 识别特征

| 特征 | 值 |
|------|-----|
| 引擎库 | `lib/<abi>/lib<game>.so`（重命名自 `libdmengine.so`） |
| 引擎内字符串 | `strings lib<game>.so \| grep -E "libdmengine|Java_com_defold_|Java_com_dynamo"` |
| assets 签名 | `game.dmanifest`（manifest）+ `game.projectc`（project 编译产物）+ `game.arcd`（归档数据，Lua 编译体）+ `game.arci`（归档索引） |
| Java 层 | `com.dynamo.android.DefoldActivity`（launchable）+ `com.defold.{admob,firebase,gpgs,iap,push}.*JNI`（SDK glue） |
| 语言支持 | `res/raw/bk_lang_pack.zip`（引擎语言包）；XAPK config split 内 `res/raw-b+<lang>/bk_lang_pack.zip` |
| 版本信息 | `manifest.json`（XAPK）含 minSdk/targetSdk/ABI |

## 2. 工具链

| 用途 | 工具 |
|------|------|
| 解包/重打包 | apktool 2.11.1（`apktool d` / `apktool b`） |
| Java 静态分析 | jadx |
| 引擎/归档分析 | `strings` / `readelf`（.so）；Lua 逻辑在 game.arcd 内（编译，非明文） |
| 汉化 | lang pack zip 替换（见 §汉化） |
| 动态验证 | adb + logcat（引擎输出 `bklang` tag） |

## 3. 坑位

### 3.1 native JNI 依赖 → 禁止物理删 SDK smali

实现要点见 [去第三方 SDK：defold](../../common/third-party-removal-strategy-skill/references/engine-notes.md#defold)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 3.2 XAPK split 合并后 resources.arsc 不完整
- XAPK 的 config split（语言/ABI）各自带 resources.arsc；简单合并仅保留 base 的 arsc → 引擎无法按 locale 限定符解析 `raw-b+zh+Hans/bk_lang_pack.zip`。
- **manifest 会残留 `requiredSplitTypes="base__abi,base__density"`** → 必须删除，否则 `INSTALL_FAILED_MISSING_SPLIT`。

### 3.3 汉化走 lang pack，不是 strings.xml
- base `res/raw/bk_lang_pack.zip` 是**哨兵占位**（仅 sentinel.txt，~170B，SHA-256 校验失败 → 引擎强制 EN）。
- 汉化步骤：
  1. 从 XAPK config split 提取 `res/raw-b+zh+Hans/bk_lang_pack.zip`（含字体/标签/图集，20+ 条目）
  2. **整体替换** base `res/raw/bk_lang_pack.zip`
  3. `res/values/strings.xml` 的 `bk_locale_marker` 改 `zh-Hans`
  4. 验证 logcat `ENTSCHIEDEN: Sprache zh-hans (Pack aktiv, Sentinel PASS)`
- 补充：`res/values-zh-rCN/strings.xml` 的 `app_name`（如 香蕉金刚）+ manifest label → `@string/app_name`。

### 3.4 广告 SDK 移除后的容错

实现要点见 [去第三方 SDK：defold](../../common/third-party-removal-strategy-skill/references/engine-notes.md#defold)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

## 4. 静态分析重点
- 先确认引擎类型（strings .so）→ 再列 SDK JNI glue（`com/defold/*`）→ 反查 glue 引用哪些 SDK 实现包（`ads_mobile_sdk` / `com/google/firebase` / `gms` 等）。
- 检查 manifest 的 provider/activity/service/receiver → 决定 SDK 移除清单。
- 检查 `res/raw/bk_lang_pack.zip` 是否为哨兵 → 决定汉化路径。

## 5. 动态分析重点
- `adb logcat | grep bklang`（引擎自有日志，含 `[lang_pack]` / `[mobile-ads]` / `[mobile-iap]` / `[mobile_preboot]`）。
- 启动后确认 `Spielwelt geladen + enabled` = 进入游戏。
- 飞行模式测试：移除网络检测后应能启动+加载+游玩。

## 6. 已知 APK 示例
- **BananaKong**（com.fdgentertainment.bananakong）1.9.18.00，2026-08-04 —— 首个 Defold 项目。

## 7. SDK 移除进阶：And64InlineHook native hook（策略规则）

实现要点见 [去第三方 SDK：defold](../../common/third-party-removal-strategy-skill/references/engine-notes.md#defold)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

