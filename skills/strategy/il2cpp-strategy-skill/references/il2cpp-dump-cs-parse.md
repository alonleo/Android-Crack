# dump.cs Hook 点分析正则模式

> 来源: RealmDefenseHeroLegendsTD (Unity 2022 il2cpp) | 2026-07-26

## dump.cs 实际格式

Il2CppDumper 输出的 `dump.cs` 不是单行格式，而是**两行**：

```
	// RVA: 0xC13B0C Offset: 0xC13B0C VA: 0xC13B0C Slot: 6
	public PurchaseProcessingResult ProcessPurchase(PurchaseEventArgs args) { }
```

**关键**:
- RVA 信息在注释行（`// RVA: 0x...`）
- 函数签名在下一行
- 中间可能隔一个空行或 `// ...` 块

## 错误正则（stage-04b 原版）

```python
# 原版 — 期望单行格式
rva_match = re.match(r'\s*(0x[0-9a-fA-F]+)\s+(.*)', line_stripped)
```

**问题**: 注释行的 `// RVA: 0x...` 不以 `0x` 开头，所以匹配失败
**结果**: hook 点为 0 个

## 正确正则

### 方案 A：单文件多行匹配

```python
full_func_re = re.compile(
    r'//\s*RVA:\s*(0x[0-9a-fA-F]+)[^\n]*\n\s*'
    r'((?:public|private|protected|internal|static|virtual|override|sealed|new|abstract|\s)+[^\n]+)'
)
content = open('dump.cs').read()
for m in full_func_re.finditer(content):
    rva = m.group(1)
    sig = re.sub(r'\s+', ' ', m.group(2)).strip()
    sig = re.sub(r'\s*\{?\s*\}\s*$', '', sig)
    # 处理 sig
```

### 方案 B：逐行扫描 + 状态机

```python
RVA_LINE = re.compile(r'//\s*RVA:\s*(0x[0-9a-fA-F]+)\s+(?:Offset:\s*0x[0-9a-fA-F]+\s+)?VA:\s*0x[0-9a-fA-F]+')
prev_rva = None
for line in f:
    rva_m = RVA_LINE.search(line)
    if rva_m:
        prev_rva = rva_m.group(1)
        continue
    if prev_rva and re.match(r'\s*(public|private|protected|internal|static)\s+', line):
        # 处理函数签名
        prev_rva = None
```

## 改进建议

- **优先用方案 A**（单文件 finditer）— 性能更好
- **处理大文件 (20 MB)** — 用 `errors="replace"` 防止编码错误
- **去重** — 同一函数可能匹配多个模式，按 RVA 去重
- **结果数限制** — 报告中每类前 30-50 个高优先级即可

## 应用范围

- 任何用 Il2CppDumper 生成的 dump.cs
- Il2CppInspectorPro 输出的格式相同
- rodroid-il2cppdumper 输出格式略有不同（包含元数据行）

## 相关 hook 模式

- **IAP**: `ProcessPurchase`, `OnInitialized`, `OnPurchaseFailed`, `InitiatePurchase`, `ConfirmPurchase`
- **广告**: `RewardedVideoOnAdRewardedEvent`, `ShowRewardedVideo`, `LoadRewardedVideo`, `OnAdLoaded`
- **Premium**: `UnlockPremium`, `BuyPremiumPass`, `CallPurchaseSubscription`
- **汉化**: `TMP_Text.set_text`, `UI.Text.set_text`, `Localize`, `SetText`
- **SDK**: `FacebookInit`, `FacebookLogPurchase`, `AppsFlyer`, `Analytics*`
