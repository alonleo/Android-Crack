# Unity 6 / Tricky Tribe 项目逆向模式

> 来源: TinkerIslandSurvivalStory | 2026-07-30
> 作者: Agent

## 项目特征

| 项 | 值 |
|---|---|
| 包名 | `com.kongregate.mobile.tinkerisland.google` |
| 开发商 | Tricky Tribe (`markovidmar@TrickyTribe`) |
| 发行商 | Kongregate |
| 引擎 | Unity 6 (libil2cpp 62.7 MB, metadata v39) |
| ABI | arm64-v8a only |
| Firebase | `tinker-island-55643367` |
| AppLovin SDK Key | `g98xkb76aSDbm93QerPvTIneTAIzKnN_xWwe62mhU-IF7MfnB3geMRIrbaowMAwHxqxothUMfobo8FTJJEzffG` |

## 内部模块结构（从 metadata.dat 反推）

```
TinkerIsland.Game                ← 游戏根
  ├─ Garden                       ← 花园小游戏（标准 + Winter 事件）
  ├─ GardenWinter                 ← 圣诞/冬季花园
DriftwoodIsland                  ← 实际岛屿模块（内部命名）
  ├─ Logic / Data / Tutorial / Animation / LocalizedImage
IdleDuck                         ← 第三方 SDK 整合商（analytics/ads/consent）
  ├─ Analytics, ByteBrew, Config, Facebook, Firebase, MaxSDK, Usercentrics
```

**注意**: 包名是 `tinkerisland`，但内部主模块叫 `DriftwoodIsland`——历史遗留命名。

## i18n 翻译系统（关键发现）

游戏使用**数字 i18n key** 而非字符串 key：

```xml
<!-- assets/game_garden.xml -->
<popup id="welcome">
  <title i18n="584">Winter Garden</title>
  <text i18n="439">Stack tiles to grow flowers.</text>
  <button i18n="443">Play</button>
</popup>
```

- **ID 范围**: 203-584（101 个唯一 ID）
- **翻译内容**: 运行时从 Kongregate/PlayFab 服务器加载
- **本地 APK 不含翻译表**——分析 UI 文本需通过 dump.cs 或 strings 反推

## 命名空间/C# 类反推技巧

从 `global-metadata.dat` 提取字符串，可发现完整 C# 项目结构：

```bash
strings -n 6 global-metadata.dat | grep -E '\\TinkerIsland|\\DriftwoodIsland'
# 包含：
#   \Assets\Runtime\Scripts\Core\Game.cs
#   \Assets\Runtime\Scripts\View\Popups\PopupView.cs
#   \Assets\Runtime\Scripts\Billing\BillingManager.cs
#   \Assets\Runtime\Scripts\Tutorial\TutorialView.cs
#   \Assets\Runtime\Garden\Common\Scripts\GameBase.cs
```

**原开发者 Unity 项目路径**:
```
/Users/markovidmar/Dev/TrickyTribe/Packages/ti1/
  com.unity.ugui/Runtime/TMP/    ← TMP 扩展
  com.unity.ugui/Runtime/UGUI/   ← UGUI 扩展
\Assets/Runtime/Scripts/         ← 游戏代码
  Core/, Helpers/, Localization/, Billing/, View/, Tutorial/
```

## TMP 字体图集（多语言支持证据）

游戏内置多语言 TMP 字体图集：

| 字体 | 尺寸 | 用途 |
|------|------|------|
| `chinese_font Atlas` | 4096×4096 | 中文 |
| `korean_font Atlas` | 1024×2048 | 韩文（×2，可能含 SDF 子图） |
| `LiberationSans SDF Atlas` | 1024×1024 | 主字体（TMP 默认） |
| `logbook2 SDF Atlas` | 2048×2048 | 玩家日志字体 |
| `complex_font` / `font` / `complexFont` | 256-512 | 备用字体 |

**意义**: 即使不联网加载翻译表，UI 也能渲染任何 CJK 字符（已在 atlas 内）。

## Unity Services 配置

`assets/UnityServicesProjectConfiguration.json`:

```json
{
  "environment-name": "production",
  "cloud-environment": "production",
  "core.version": "1.16.0",
  "analytics.version": "6.2.0",
  "purchasing.version": "5.0.2"
}
```

`RuntimeInitializeOnLoads.json` 显示启动顺序：
1. `IdleDuck.Analytics.IdleDuckAnalytics.Init`
2. `IdleDuck.Config.IdleDuckConsent.Initialize`
3. `Unity.AI.Navigation` 清空追踪列表
4. `Unity.Purchasing.*` 注册
5. `Unity.Services.Analytics` 注册
6. `Unity.Services.Core` 初始化

## 已知字符串常量（用于识别）

`assets/GameSettings.prop` 内容：
```
*** DO NOT DELETE OR MODIFY THIS FILE !! ***
zZn-WR_5mrXnyUYa4ipsfA
*** DO NOT DELETE OR MODIFY THIS FILE !! ***
```
中间是 **session token**（不是配置），可能是 PlayFab 玩家会话 ID。

`assets/unity_app_guid`: `6c75e5c1-a3a0-45d7-b78f-605b95fc3be1`
`assets/bin/Data/boot.config`:
```
build-guid=ee09754edd584a55a4708edf6569fc52
```

## 23+ 个 Unity 程序集（从 ScriptingAssemblies.json）

**游戏代码**:
- `Assembly-CSharp.dll` — 主游戏代码
- `DriftwoodIsland.dll` — 主岛屿模块
- `TrickyTribe.ComplexColor.dll` — 工作室色彩系统

**第三方 SDK 套件**:
- IdleDuck 全家桶（7 个 dll）
- PlayFab.dll + 多个 PlayFab.*
- Firebase.*.dll（Analytics, Crashlytics, RemoteConfig, AppCheck）
- Facebook.Unity.*.dll
- Unity.Services.*（9 个 dll）
- Unity.Purchasing.*（5 个 dll）
- Unity.Usercentrics.dll, Unity.Notifications.*.dll
- DOTween.dll, protobuf-net.dll, Newtonsoft.Json.dll
- MaxSdk.Scripts.dll, ByteBrewSDK.dll

## 完整 UI 文本示例（来自 game_garden.xml）

187 条 UI 文案，全部英文。代表样本：

**玩法说明**:
- "Stack tiles to grow flowers."
- "Flowers earn flower points."
- "Earn enough to beat the level and get a reward."
- "Water on earth makes swamps. Most plants don't grow in them."
- "Add sun to swamp to make it fertile again."

**奖励提示**（12 种 × 3 稀有度 = 36 条）:
- "You got Common Pigeon!" / "Rare Pigeon!" / "Epic Pigeon!"
- "You got Common Woodpecker!" / ...
- "You got Common Rooster!" / ...
- "You got Common Kiwi!" / ...
- "You got Common Essence!" / ...
- "Birds are survivors you can use only once."

**解锁提示**（25 种）:
- "You have unlocked the double tile piece!"
- "You have unlocked bird cage!"
- "You have unlocked Square Garden!"
- "You have unlocked Rain Power."
- "You have unlocked Sunflower."
- "You have unlocked Lotus Flower."
- "You have unlocked Cactus."
- "You have unlocked Rose."
- "You have unlocked Sun Power."
- "You have unlocked Rainbow Power."
- "You have unlocked the Bug Bomb."

## 同类型项目识别 checklist

下一个 APK 如果同时满足以下条件，可参考本模式：

- [ ] 包名含 `kongregate` 或 `tinkerisland`
- [ ] 内含 `lib/arm64-v8a/libil2cpp.so` > 30 MB
- [ ] `assets/bin/Data/data.unity3d` > 30 MB
- [ ] 字符串含 `TinkerIsland` 或 `DriftwoodIsland`
- [ ] `app-id` 含 `tinker-island-` 前缀
- [ ] `assets/GameSettings.prop` 是 token 格式（不是配置）

## 已知问题（备忘）

1. **Il2CppDumper v39 失败**: 必须用 strings + UnityPy 替代路径（见 metadata-version-limit.md）
2. **sharedassets*.resource 是 FSB5 音频**: 不是纹理（见 unity-asset-extraction.md）
3. **i18n 翻译表不在 APK 内**: 需从服务器或 PlayFab 拉取
4. **OCR 准确率低**: TMP 抗锯齿字体，Tesseract 标准模式识别差

## 相关文档

- [il2cpp-metadata-version-limit.md](./il2cpp-metadata-version-limit.md)
- [unity-asset-extraction.md](./unity-asset-extraction.md)
- [text-extraction-strategies.md](./text-extraction-strategies.md)