# Unity il2cpp 启动时 GDPR/Privacy Consent 弹窗移除（native hook）

> 适用：Unity il2cpp 项目启动时弹出隐私同意弹窗（文案 "We use device identifiers
> and informations related to your use of this digital product..." 带 Privacy Policy
> 链接 + Accept 绿色按钮）。
> 关联：EXPERIENCES.md「GDPR 弹窗 hook」条目；脚本 `skills/common/scripts/extract-gdpr-hooks.py`。

## 1. 弹窗判定

**文案特征**（Unity Ads 内置 GDPR/consent UI）：
```
We use device identifiers and informations related to your use of this digital
product to personalize content and ads, to provide social media features and to
analyze the use of our products. For details, see our Privacy Policy
```
下方含 **Privacy Policy** 链接 + **Accept** 绿色按钮 + 右上角 ✕。

## 2. 根因

这是 **Unity Ads 内置 ConsentPopup / GDPRController**（C# 层）在启动时检查是否
已同意 GDPR，未同意则弹窗。逻辑核心：
- `GDPRController.CheckForGDPR()` — 弹窗显示入口（Start() 里调用）
- `ConsentPopup.GDPRConsentWasSet()` / 静态版 — 是否已同意
- `ConsentPopup.ShowBuiltInConsentPopup()` — 内置弹窗显示
- `ConsentPopup.CanShowAds()` — 是否可显示广告

判定"是否弹"的关键是 `GDPRConsentWasSet()` 返回 true 则不弹。

## 3. 解决方案（native hook，默认已同意）

在 `native-lib.cpp` 用 A64HookFunction 注入以下 hook，让"是否已同意"恒返 true、
弹窗入口 no-op、广告关闭：

### 3.1 函数定义（放 setupHooks() 之前）
```cpp
// GDPRConsentWasSet() → 恒返 true（已同意，弹窗不显示）
static bool (*orig_GDPRConsentWasSet)();
extern "C" bool Hooked_GDPRConsentWasSet() {
    LOGI("[hook] GDPRConsentWasSet → return true");
    return true;
}

// CheckForGDPR() → no-op（跳过弹窗入口）
static void (*orig_CheckForGDPR)(void*);
extern "C" void Hooked_CheckForGDPR(void* thiz) {
    LOGI("[hook] CheckForGDPR → no-op (skip popup)");
}

// CanShowAds() → 恒返 false（关闭广告）
static bool (*orig_CanShowAds)();
extern "C" bool Hooked_CanShowAds() {
    LOGI("[hook] CanShowAds → return false");
    return false;
}
```

### 3.2 注册（放入 setupHooks() 内 "Hook Engine Initialized" 之前）
```cpp
{
    void* target = (void*)(baseAddr + 0x1425438);  // GDPRConsentWasSet()
    A64HookFunction(target, (void*)Hooked_GDPRConsentWasSet, (void**)&orig_GDPRConsentWasSet);
    LOGI("[hook] Hooked_GDPRConsentWasSet installed @ 0x%x", (unsigned)(uintptr_t)target);
}
{
    void* target = (void*)(baseAddr + 0x13F426C);  // CheckForGDPR()
    A64HookFunction(target, (void*)Hooked_CheckForGDPR, (void**)&orig_CheckForGDPR);
    LOGI("[hook] Hooked_CheckForGDPR installed @ 0x%x", (unsigned)(uintptr_t)target);
}
{
    void* target = (void*)(baseAddr + 0x14259E8);  // CanShowAds()
    A64HookFunction(target, (void*)Hooked_CanShowAds, (void**)&orig_CanShowAds);
    LOGI("[hook] Hooked_CanShowAds installed @ 0x%x", (unsigned)(uintptr_t)target);
}
```

## 4. RVA 获取（extract-gdpr-hooks.py）

不同项目的 RVA 不同，但函数模式相同。**每个项目单独提取**：
```bash
python3 skills/common/scripts/extract-gdpr-hooks.py \
    --dump crackings/<type>/<name>/stages/03-fn-analyze/step1-signatures/dump/dump.cs
```
脚本从 dump.cs 自动提取 GDPRConsentWasSet / CheckForGDPR / CanShowAds /
SetGDPRConsent / CCPAConsentWasSet / ShowBuiltInConsentPopup / HasBuiltInConsentWindow
的 RVA 并生成完整 hook 片段。

## 5. 验证

```bash
# logcat 应见 hook 命中且无弹窗
adb logcat -d | grep -iE "GDPR|CheckForGDPR|CanShowAds"
# 应为:
# [hook] Hooked_GDPRConsentWasSet installed @ 0x...
# [hook] Hooked_CheckForGDPR installed @ 0x...
# [hook] Hooked_CanShowAds installed @ 0x...
# [hook] CheckForGDPR → no-op (skip popup)
# 截图确认无隐私弹窗，主菜单正常
```

## 6. 易错点

- **RVA 须是函数入口**（标准 prologue stp x29,x30）；极短函数（mov w0,#N; ret）不可 hook。
- 若 hook `GDPRConsentWasSet()` 后仍弹窗，说明游戏用的是**instance 版**（`ConsentPopup.GDPRConsentWasSet`，
  需要 this），此时应 hook `CheckForGDPR()`（no-op）而非注册 instance 版（避免 this=null）。
- **排除法诊断**：先只 hook `CheckForGDPR()`（no-op）——若弹窗消失，说明弹窗确由它触发；
  若仍存在，弹窗可能来自 Google UMP（com.google.android.ump）而非 Unity Ads，
  需剔除 `com/google/android/ump` 或走 AppLovin CMP 路径。
- **不要用 SharedPreferences 预置 consent 键**——AppLovin/Unity Ads 的 consent 状态键
  复杂多变，预置不生效（实测弹窗仍在）。native hook 是唯一可靠路径。
