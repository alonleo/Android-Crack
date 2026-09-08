# Unity il2cpp Hook 点检索模式

> 基于 dump.cs 的自动 hook 点检索经验。每次完成 Unity il2cpp 项目的 hook 点分析后，在此追加新发现的检索模式。
> 加载位置：`skills/strategy/il2cpp-strategy-skill/references/hook-points-search-patterns.md`
>
> 来源项目的命名归一 + 日期见每项首行。

## 检索模式汇总

| 模式 | 检索关键词 | 预期结果 | 来源 |
|------|-----------|---------|------|
| `[hook-points] IAP 购买` | 检索 `Purchase` / `PurchaseSuccessful` / `ProcessPurchase` / `IAP` / `Billing` / `Store` | 59+ 候选点，按方法名和参数类型排序 | GoldenFarm | 2026-07-25 |
| `[hook-points] 广告/激励视频` | 检索 `Reward` / `Advert` / `Interstitial` / `MobileAdvertising` / `CrossPromo` | 179+ 候选点，区分展示、加载、完成、关闭 | GoldenFarm | 2026-07-25 |
| `[hook-points] Premium 解锁` | 检索 `Premium` / `Premuim`(原游戏拼写错误) / `Pass` / `Vip` / `Subscription` | 58+ 候选点，注意游戏代码中的拼写错误 | GoldenFarm | 2026-07-25 |
| `[hook-points] 本地化` | 检索 `Localize` / `Locale` / `Localization` / `GameLocalization` | 115+ 候选点，含语言检测和切换 | GoldenFarm | 2026-07-25 |
| `[hook-points] 文本组件（汉化）` | 检索 `set_text(string)` 匹配类名含 `TMP_Text` / `UI.Text` | 2+ 候选点，含 RVA 和 method slot | GoldenFarm | 2026-07-25 |
| `[hook-points] 反调试` | 检索 `DebugConsole` / `Debug` / `Root` / `Tamper` / `Cheat` / `Modify` | 30+ 候选点，含 isDebug/isRoot/isTamper 检测 | GoldenFarm | 2026-07-25 |
| `[hook-points] 网络检测` | 检索 `Network` / `Internet` / `Connect` / `Ping` / `Online` / `ServerAvailability` | 20+ 候选点，用于单机适配 | GoldenFarm | 2026-07-25 |

## 通用检索指令（供脚本/Agent 复用）

```bash
# 从 dump.cs 检索 IAP 相关函数（前 30 行）
head -n 100 dump.cs | grep -n "Purchase\|IAP\|Billing\|Store\|Offer" | head -30

# 从 dump.cs 检索广告相关函数
grep -n "Reward\|Advert\|Interstitial\|MobileAdvertising" dump.cs | head -30

# 从 dump.cs 检索 Premium 相关（注意拼写变体）
grep -n -i "premium\|premuim\|vip\|pass" dump.cs | head -30

# 从 dump.cs 检索本地化
grep -n -i "localize\|locale" dump.cs | head -30

# 从 dump.cs 检索 Unity 文本组件
grep -n "set_text" dump.cs | grep -E "TMP_Text|UnityEngine.UI.Text"
```

## 优先级排序规则

1. ⭐1: 有明显 `success` / `complete` / `reward` 的方法名 — 优先 hook
2. ⭐2: 泛用类名（如 `AbstractMobileAdvertising`、`UnityIAP`）— 覆盖多实现
3. 3-4: 供应商特定实现（如 `AdmobAdvertising`、`HuaweiPurchase`）— 按需
4. 5+: 工具/辅助函数（如 `Save`/`Load`/`IsPremiumBuyed`）— 桩化即可

## 经验教训

- 【GoldenFarm 2026-07-25】部分游戏类名/方法名有拼写错误（如 `UnlockPremuim` 而非 `Premium`），检索时必须用 `grep -i` 大小写不敏感，且搜索 `premuim`、`buyed` 等常见拼写错误
- 【GoldenFarm 2026-07-25】`stringliteral.json` 文件可能含大量非 UI 字符串，应先用希里尔字符/Unicode 范围过滤再提取 UI 字符串（减少无效条目 97%：从 24417 降到 293）

## 相关文档

- [il2cpp-strategy-skill/strategy.md §3 Hook 转发链路](../strategy.md) — hook 后链路
- [il2cpp-strategy-skill/strategy.md §4 Hook 类别与模板对接](../strategy.md) — hook 类别映射
- [il2cpp-strategy-skill/tools-index.md §3 dump.cs → Frida JS + C++ 桩](../tools-index.md) — 自动化生成
- [il2cpp-strategy-skill/references/il2cpp-metadata-version-limit.md](./il2cpp-metadata-version-limit.md) — metadata 版本限制
- [il2cpp-strategy-skill/references/il2cpp-dump-cs-parse.md](./il2cpp-dump-cs-parse.md) — dump.cs 解析技巧
- [il2cpp-strategy-skill/references/il2cpp-arm32-limitation.md](./il2cpp-arm32-limitation.md) — ARM32 限制