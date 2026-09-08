# il2cpp ARM32 (armeabi-v7a) 限制与解决方案

> 来源: RealmDefenseHeroLegendsTD (Unity il2cpp, armeabi-v7a) | 2026-07-26
> 作者: Agent

## 问题描述

Unity il2cpp 游戏 APK **只包含 armeabi-v7a (32-bit ARM)** 时，标准的 inline hook 库**全部不可用**：
- **And64InlineHook** (Rprop) — 仅 `__aarch64__`，32-bit 编译时整个 `extern "C"` 块被 `#if` 排除
- **Android_Inline_Hook_ARM64** (GToad) — 同样仅 aarch64
- **FakerAndroid fakeCpp** — 通过 `.so` 注入，依赖 `libbase.so`（不公开）

编译时表现为 `undefined reference to A64HookFunction`，链接失败。

## 复现

```bash
# APK 结构
unzip -l app.apk | grep "lib/.*\.so"
  lib/armeabi-v7a/libil2cpp.so      # 仅 32-bit ARM
  lib/armeabi-v7a/libunity.so

# 编译 native-lib.cpp 链接 And64InlineHook
# → ld: error: undefined symbol: A64HookFunction
# 因为 .cpp 顶部: #if defined(__aarch64__)
# armeabi-v7a 编译时 __aarch64__ 未定义
```

## 解决方案

### 方案 A（推荐）：添加 arm64-v8a ABI 支持

让游戏支持 64-bit 后，inline hook 即可生效：

```gradle
// app/build.gradle
defaultConfig {
    ndk {
        abiFilters 'armeabi-v7a', 'arm64-v8a'  // 双 ABI
    }
}
```

**前提**: 原 APK 的 `libil2cpp.so` 必须有 arm64-v8a 版本（但本案例只有 armeabi-v7a）
**操作**: 重新从 Play Store 下载 arm64 APK，或自行编译 Unity 工程生成

### 方案 B：Frida 运行时注入

native 端不编译 hook 代码，运行时用 Frida 挂载：

```javascript
// frida-hook.js
Interceptor.attach(base.add(0xC13B0C), {
    onEnter(args) {
        send("Purchaser.ProcessPurchase called");
        args[0] = ptr(0);  // 返回 Complete
    }
});
```

```bash
# 启动游戏后注入
frida -U -f com.babeltimeus.legendstd -l frida-hook.js --no-pause
```

**优势**: 兼容任何 ABI，无需重新编译
**劣势**: 需 USB 调试或 frida-gadget 嵌入

### 方案 C：纯 Java 层 + Stub 模拟（已实施）

放弃 native hook，让 Java 层接管：
- `App.java` 启动后 `System.loadLibrary("native-lib")` 注入 JNI 桥接
- `native-lib.cpp` 提供 `baseImageAddr` / `fakeCpp` / `onJniLoad` stub（#if aarch64 守卫）
- 玩家主动调用模拟路径：`MainActivity.callJava("processPurchase")` → `SDKUtils.processPurchase()` → Toast 反馈

**适用场景**: 仅需模拟 IAP / 广告，不在意游戏内部状态机
**劣势**: 游戏主动调用 IAP 时（如打开商店）会调用原始 `Purchaser.ProcessPurchase` → 真实 Google Play Billing 缺失 → 崩溃

## 当前项目实施

- **方案 C 已实施**: native-lib.cpp + A64HookFunction 用 `#if defined(__aarch64__)` 守卫
- **残留 libnative-googlesignin.so**: Google Sign-In 已删 smali 但 .so 仍存在（无引用，待清理）
- **Frida 注入可用**: 见上方案 B 脚本模板

## 经验

- **遇到 armeabi-v7a il2cpp 项目时优先检查 ABI**: `unzip -l *.apk | grep "lib/.*libil2cpp"`
- **不要假设有 arm64**: 一些老 Unity 项目（2018-2019）只编译 32-bit
- **Frida 是最稳妥的兜底**: 不依赖 ABI，运行时挂载
- **Stub 函数必须返回合理值**: `fakeCpp` 返回 false 表明 hook 未应用，避免静默失败

## 方案 D：ELF 二进制直接 patch libil2cpp.so（arm32 强制改函数返回值）

> [ViragoHerstory112 实测] 在不依赖 A64HookFunction（arm32 不可用）也不改 Java 层的前提下，
> **直接修改 libil2cpp.so 的函数字节**实现"强制中文"。这是 arm32 il2cpp 持久化改游戏逻辑的可行路径。

### 关键事实
- il2cpp 游戏 **C# 逻辑全部编译进 libil2cpp.so，smali 里只有 SDK 桥接**（无游戏逻辑类）
- 因此"改 smali 层"（方案2）对 il2cpp 游戏**不适用**——没有游戏逻辑 smali 可改
- 游戏 `LanguageManager` 的 `LoadSavedLanguage` / `SetLanguage` / `LocalizedText.UpdateText`
  **全部在 libil2cpp.so native 层**

### 落地步骤（armv7 ARM 模式，小端）
1. 用 `ndk/.../bin/llvm-objdump -d` 反汇编目标函数，确认是 ARM 模式（非 Thumb）
2. 确认 ELF `il2cpp` section vaddr == file offset（`readelf -S`；第一个 LOAD 从 0 映射）
3. 用 `patch-so-return-null.py --imm N` patch 单函数返回指定值：
   - `get_CurrentLanguage` (0x131b684) → `mov r0,#7; bx lr` 强制返回 Chinese(7)
   - `SetLanguage` (0x131bd60) → `mov r5,#7` 强制 language 参数 = Chinese
   - **核心** `LocalizedText.UpdateText` (0x131c31c) → `mov r6,#7` 强制所有文本用中文词条 ★

### 指令编码（armv7）
```
mov r0, #imm  = 0xE3A00000 | imm      (mov r0,#7 = 0700a0e3)
mov r5, #imm  = 0xE3A05000 | imm      (mov r5,#7 = 0750a0e3)
mov r6, #imm  = 0xE3A06000 | imm      (mov r6,#7 = 0760a0e3)
bx lr         = 0xE12FFF1E            (1eff2fe1)
```
> armv7 BL 跨段（il2cpp段 0x0139xxxx → .text段 0x0404xxxx）偏移约 46MB，
> **在 arm BL ±128MB 范围内**，可直接 `bl`（BL 编码算 (target-(pc+8))>>2）。

### 经验
- **"强制中文" = patch `LocalizedText.UpdateText`**（不是单一 getter/Setter）：所有本地化文本组件
  更新时强制 language 参数 = 中文，主菜单/UI 全中文。★最有效入口
- **单 patch getter/SetLanguage 不够**：il2cpp 文本是"组件级 LocalizedText 各自从翻译表选词条"，
  启动即用默认语言渲染，不经单一 SetLanguage 切换点
- **隐藏语言按钮**：主菜单 LANGUAGE 入口按钮是**场景预制件节点**（不挂 `LanguageSwitcher`，
  LanguageSwitcher 只在语言弹窗选项上；也不在 `GroupLanguageManager.members`），
  patch `LanguageSwitcher.Awake` / `GroupLanguageManager.DeactivateAllExcept` 均**无法隐藏**。
  → 需 Unity 场景 Asset 逆向（AssetStudio/UnityPy 改 GameObject.m_IsActive，Unity 2022+ 格式），
  二进制 patch 无法覆盖。
- **Frida 查询被 anti-frida 拒**：release 签名 + 进程有注入保护，`frida -U` attach 报
  `agent connection closed unexpectedly`（即使 frida-server root + SELinux Permissive）。
  → 仅查询也受阻时，退到纯 ELF patch。
- **patch 已打进 APK 的 .so**：改 `app/src/main/lib/armeabi-v7a/libil2cpp.so` 后重跑
  `./gradlew assembleRelease`（apktool b 会把该目录 .so 打进 APK），不是改 raw 源的 .so。
