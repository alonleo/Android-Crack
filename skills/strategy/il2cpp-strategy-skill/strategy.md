# il2cpp Strategy — FakerAndroid 默认 + Hook 模板架构（01–29）

> **本文件是 il2cpp 策略的"策略声明"**——所有该 type 的 APK 都按此策略执行。
>
> **加载顺序**：在 Agent 选择到 il2cpp skill 后，按下列顺序加载：
> 1. [SKILL.md](./SKILL.md) — 总览、何时调用、能力地图
> 2. **[strategy.md（本文件）】** — 策略声明（默认工具 + Hook 架构 + 模板对接）
> 3. [workflow.md](./workflow.md) — 阶段流程（命令 + 验证 + 故障处理）
> 4. [tools-index.md](./tools-index.md) — 工具索引（外部工具 + skill 内部脚本）
> 5. [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀（按时间倒序追加）
>
> 阶段重排为 01–29 线性连续。
> 旧 15 阶段（01-15）经 `strategy-config.yaml legacy_stage_map` 自动迁移。

---

## 1. 策略宣言（强制）

```
任何 type=il2cpp 的 APK 都按下列默认流程执行：
  1. 入口工具: FakerAndroid-Update.jar (fake 子命令)
     → 产出可编译的 Android Studio 工程 (crackings/<type>/<Name>/project/)
  2. 该 AS 工程默认采用 Hook 模板架构：
     - 所有游戏行为修改点（网络检测 / 激励视频 / 内购）均通过
       native-lib.cpp 的 inline hook 注入 (fakeCpp)
     - 激励视频、内购、Premium 通过 hook 转发 (callJava) → Java 层处理
     - Java 层使用 SDKUtils.java 统一模拟回调生命周期
  3. 模板文件来源固定:
     skills/common/scripts/template-files/
       ├─ MainActivity.template.java   模板 Activity（含 JNI 回调路由）
       ├─ JniBridge.template.java      native→java 桥接器
       └─ SDKUtils.java                激励视频/IAP 三阶段模拟工具类
  4. 处理 il2cpp 项目所产生的脚本（hook 桩 / Frida 脚本 / native-lib.cpp
     片段 / hanization_map.h 等）必须固化到本 skill 的 scripts/workflow/
     或 scripts/common/ 中。
```

> 任何"apktool 手改 smali + 重打包"路线在 il2cpp 项目下都视为**次优解**——除非
> FakerAndroid fake 失败（极少数 packed-armor 类项目）才回退。

## 当前工程集成架构（01–15 模型）

本节是 IL2CPP 工程中 Java 与 native 集成的技术参考；通用阶段顺序、脚本调度和验收门槛以根 [WORKFLOW.md](../../../WORKFLOW.md) 为准。

| 组件 | 职责 |
|---|---|
| `MainActivity` | 承载启动 Activity 与主线程事件分发；由项目模板生成并在 manifest 中声明。 |
| `App` | 在 `onCreate()` 初始化 native 入口，避免将引擎专属逻辑放入根 Android 配置。 |
| `JniBridge` | 只负责 native 与 Java 的事件路由，不承载游戏业务决策。 |
| `native-lib.cpp` | 安装经静态分析确认的 native Hook，并保留原始函数指针与可观测日志。 |
| `SDKUtils` | 在不依赖远程 SDK 的情况下，为本地可验证的奖励或购买状态机提供 Java 侧回调模拟。 |

集成链路为：`native Hook → JNI 事件 → JniBridge → MainActivity 主线程 → SDKUtils → JNI 回调 → 原始游戏回调`。任何具体 Hook 点、返回值和调用顺序必须由该 APK 的静态/动态分析确认，不能作为跨项目常量复制。

验证至少覆盖：模板 Activity 可加载、native 库可加载、目标 Hook 可观测、Java 回调可达，以及对应的核心玩法状态变化。非 IL2CPP type 不适用本架构。

## 1.1 Hook 方式约定（通用规则）

| 类型 | 默认 Hook 方式 | 说明 |
|------|---------------|------|
| **il2cpp** | FakerAndroid + A64HookFunction | FakerAndroid 生成完整 hook 骨架（native-lib.cpp + callJava + fakeCpp） |
| **其他类型** | And64InlineHook | 直接使用 And64InlineHook 库进行 native hook |

**il2cpp 特殊说明**：
- FakerAndroid 自带 A64HookFunction 实现，无需额外集成
- 所有修改通过 `native-lib.cpp` 的 inline hook 注入

**非 il2cpp 说明**：
- hook 点通过静态分析（jadx / IDA / Ghidra）确定
- 可结合 Frida 进行动态调试和 hook 验证

## 2. 策略架构总览（01–29）

```
APK (type=il2cpp)
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 01–02: 嗅探 + 评估（general-strategy-skill）                     │
│   01: unzip -l → type=il2cpp                                │
│   02: 6 维加权 → grade (S/A/B/C/D/F)                        │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 03: 通用静态分析（general-strategy-skill）                        │
│   jadx 反编译 + smali 分析 + SDK 扫描 + 入口定位             │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 04: 预处理构建检测                                            │
│   apktool 解包 + ASBuilder.jar fake → AS 工程骨架            │
│   + 工具链规范化 (AGP 7.4.2 / Gradle 7.5.1 / compileSdk 33) │
│   + 基线编译 + 真机安装 + 启动门禁     
   12: MainActivity + App + JniBridge + native-lib scaffolding│
│   13: 模板集成真机验收 ⚠️成功→强制固化                       │
│   14: SDKUtils.java 三阶段模拟（500ms/1500ms/300ms）  │
│   输出: crackings/<type>/<Name>/project/              │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 05: 需 hook/转发相关函数分析                                  │
│   Il2CppDumper → dump.cs / il2cpp.h / DummyDll              │
│   + 自动匹配 hook 候选点 (IAP/Ad/Premium/Localization)       │
│   输出: hook-plan.yaml                         │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 06–09: SDK 清理 + 网络检测移除                                │
│   06: 去第三方 SDK（manifest + smali + .so ）      │
│   07: SDK 移除真机验收 ⚠️成功→强制固化                       │
│   08: 去除网络检测（isNetworkAvailable 桩化）                 │
│   09: 飞行模式真机验收 ⚠️成功→强制固化                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 10–11: 去功能点                                              │
│   10: UI 隐藏 + 区域裁剪                                     │
│   11: 去功能点真机验收 ⚠️成功→强制固化                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 12–15: 模板集成（il2cpp 专用）                                │
│        │
│   15: SDKUtils 真机验收 ⚠️成功→强制固化                      │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 16–19: 激励/IAP 转发（通用）                              │
│   16: 激励视频转发（showVideo callJava + native hook）        │
│   17: 激励视频真机验收 ⚠️成功→强制固化                       │
│   18: IAP（Premium）转发（processPurchase callJava）          │
│   19: IAP 真机验收 ⚠️成功→强制固化                           │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 20–25: 汉化（字体/文本/图片）                                │
│   20: 字体替换（中文字体注入 res/font/）                      │
│   21: 字体真机验收 ⚠️成功→强制固化                           │
│   22: 文本汉化（hanization_map.h + strings.xml）             │
│   23: 文本汉化真机验收 ⚠️成功→强制固化                       │
│   24: 图片汉化（含文字 PNG 重绘）                            │
│   25: 图片汉化真机验收 ⚠️成功→强制固化                       │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
┌─────────────────────────────────────────────────────────────┐
│ 26–29: 交付                                                  │
│   26: AS 工程化（gradle assembleRelease + apksigner v1+v2+v3）│
│   27: 记录工程文件（dir-index.yaml + manifest.yaml）           │
│   28: 最终验收（6 条硬指标全过）                              │
│   29: 清理临时空间                                            │
└─────────────────────────────────────────────────────────────┘
  │
  ▼
patched.apk (adb install -r)
```

## 3. Hook 转发链路（End-to-End）

**激励视频完整链路**（native hook → Java 模拟 → native 回调）：

```
il2cpp ShowRewardAd / OnRewardRequested 被调用
  │
  ▼ A64HookFunction(target, HookedShowReward, &orig)
HookedShowReward() {
    LOGI("[hook] 拦截激励视频请求");
    callJava("showVideo");                ── JNI 向 Java 发送事件
}
  │
  ▼ JNI bridge (callJava in native-lib.cpp)
JniBridge.onJniCall("showVideo")          ── 桥接器
  │
  ▼
MainActivity.onJniCall("showVideo")
  │ Handler.sendMessage → 主线程
  ▼
MainActivity.callJava("showVideo")
  │
  ▼
SDKUtils.showRewardedVideo(IRewardVideoListener)
  ├─ 阶段1 (500ms): onRewardLoaded()        模拟广告加载
  ├─ 阶段2 (1500ms): listener.onReward()    模拟播放完成，发放奖励
  └─ 阶段3 (300ms): listener.onRewardHidden 模拟关闭
  │
  ▼
videoComplete(true)
  │
  ▼ JNI 回 native
MainActivity.onVideoReward(true) → Java_com_android_boot_MainActivity_onVideoReward
  │
  ▼
native 端调用原始 il2cpp OnRewardComplete → 触发游戏实际奖励发放
```

**IAP 完整链路**：

```
il2cpp OnPurchaseRequested / PurchaseInitiate 被调用
  │
  ▼ A64HookFunction 拦截
HookedOnPurchaseRequested(productId) {
    callJava("processPurchase:" + productId);
}
  │
  ▼ MainActivity.callJava("processPurchase:com.game.gem_pack_100")
SDKUtils.processPurchase(productId, onSuccess, onError)
  │ Handler.postDelayed(800ms) 模拟支付网关
  ▼
MainActivity.onIapSuccess("com.game.gem_pack_100")
  │
  ▼ JNI 回 native
native 端调用原始 PurchaseSuccessful → 道具发放
```

**汉化 / 网络检测**（不转发到 SDKUtils，由 hook 自身完成）：

```
汉化 (Frida + native hook):
  ├─ Frida: Interceptor.attach(set_text_addr, onEnter → 替换 args[1] 为译文)
  └─ Native: A64HookFunction(set_text_addr, HookedSetText)
              → textTranslations[orig] → translated

网络检测 (Frida hook Java 层):
  ├─ NetworkInfo.isConnected  → 强制返回 true
  ├─ NetworkInfo.isAvailable  → 强制返回 true
  └─ ConnectivityManager.getActiveNetworkInfo → 强制返回非空
```

## 4. Hook 类别与模板对接（01–29）

| 类别 | 处理位置 | 模板/工具 | 阶段 |
|------|----------|----------|------|
| **汉化 - 字体** | Typeface.createFromAsset + res/font/ | NotoSansSC / 文泉驿 | 20 + 21 |
| **汉化 - 文本** | native hook (set_text) + hanization_map.h | `sub-stage-text-hanization.py` | 22 + 23 |
| **汉化 - 图片** | PNG 重绘 + 9-patch | `sub-stage-image-hanization.py` | 24 + 25 |
| **去网络检测** | Frida hook Java 层 (NetworkInfo) | `sub-stage-network-detection-removal.py` | 08 |
| **激励视频** | native hook → Java SDKUtils 三阶段模拟 | `SDKUtils.showRewardedVideo` + `MainActivity.template.java callJava("showVideo")` | 16 + 17 |
| **内购 (IAP)** | native hook `PurchaseProduct` → callJava → Java SDKUtils 记录购买 | `templates/native-lib.iap.template.cpp` + `SDKUtils.recordPurchase/isPurchased` | 18 + 19 |
| **Premium 解锁** | native hook → Java SDKUtils.unlockPremium | `SDKUtils.unlockPremium` + `MainActivity.template.java callJava("premiumUnlock")` | 18 + 19 |
| **广告移除** | 物理删广告资产 + Manifest 清理 + native hook 广告管理类 | `templates/native-lib.ad-removal.template.cpp` | 06 |
| **UI 隐藏（NGUI）** | [统一实现说明](../../common/feature-removal-strategy-skill/references/engine-notes.md#il2cpp) | 由 type 注册表路由 | 08 + 09 |
| **反调试绕过** | Frida hook (TracerPid / ptrace 检测) | hook-main.js anti-debug 段 | 06 |
| **加密字符串** | Frida hook (il2cpp_string_new) + 译文表 | hook-main.js stringNew 段 | 06 |
| **Native 协议加密** | Frida hook (recv/send/connect) + dump | hook-main.js 网络段 | 06 |

## 5. 模板文件使用规范（强制）

| 模板 | 路径 | 使用规则 |
|------|------|---------|
| `MainActivity.template.java` | `skills/common/scripts/template-files/MainActivity.template.java` | **不可修改**；通过占位符 `{PACKAGE_NAME}` `{ORIGINAL_ACTIVITY}` 等替换 |
| `JniBridge.template.java` | `skills/common/scripts/template-files/JniBridge.template.java` | **不可修改**；统一处理 native → java 回调路由 |
| `SDKUtils.java` | `skills/common/scripts/template-files/SDKUtils.java` | **不可修改**；扩展 SDKUtils 类时（如新增一种激励视频回调模式）必须同步更新本文件；所有 il2cpp 项目共享同一份 |

**FakerAndroid 自带的 `MainActivity.java` / `App.java`** 在阶段 04 会被自动产出；
阶段 12 用模板覆盖之。

> 任何针对单个项目定制 MainActivity 的行为（如新增 JNI 方法）应通过新增 native
> 函数 + 模板的 `{VIDEO_COMPLETE_CALLBACK}` 占位符扩展，而非修改模板本身。

## 6. 脚本固化规则（agent 必读）

> **固化对象**：处理 il2cpp 项目过程中**新生成**的所有脚本/代码片段，**不**包括
> `crackings/<type>/<Name>/project/` 下任何项目级产物。
>
> **固化位置**：本 skill 的 `scripts/` 目录：
> - `scripts/workflow/` — 流程脚本（每阶段专用，命名 `stage-<NN>-*.py`）
> - `scripts/common/` — 通用脚本（跨阶段工具，命名 `<verb>-<scope>.py`）
>
> **固化时机**：
> 1. 新发现的 **hook 桩模式**（如某类回调的 A64HookFunction 模板）→ 立即固化
> 2. 新发现的 **Frida hook 脚本**（如某类反调试绕过）→ 立即固化
> 3. 项目级 `native-lib.cpp` 中可复用的 hook 段 → 抽离为通用函数后固化
> 4. `hanization_map.h` 等翻译映射 → 抽离通用翻译模式后固化
>
> **固化流程**（遵循 AGENTS.md §1.1 固化优先）：
> ```
> 项目内临时脚本 → 抽出通用版本 → 命名 <verb>-<scope>.py
>   → 移动到本 skill 的 scripts/workflow/ 或 scripts/common/
>   → 在 skills/common/scripts/README.md 中追加条目（如果也在 skills/common/scripts/）
>   → 在 status.yaml 记录固化来源（APK + 日期）
> ```

## 7. 阶段序列固化（01–29）

```
01 → 02 → 03 → 04 → 05 → 06 → 07 → 08 → 09 → 10 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19 → 20 → 21 → 22 → 23 → 24 → 25 → 26 → 27 → 28 → 29
```

**强制阶段（21 个，不可跳过）**：
- `01` sniff — 类型嗅探
- `02` assess — 难度评估
- `03` 通用静态分析 — jadx + smali + 入口定位
- `04` 预处理构建检测 — FakerAndroid + toolchain + 编译测试
- `05` fn 分析 — dump.cs + hook-plan
- `06` 去第三方 SDK — manifest + smali + apktool b
- `07` SDK 真机验收 — verify_app_alive
- `08` 去除网络检测 — isNetworkAvailable 桩化
- `09` 飞行模式真机验收 — airplane-mode enable
- `10` 去功能点 — UI 隐藏
- `11` 去功能点真机验收 — 目标按钮不可见
- `12` 集成模板文件 — MainActivity + App + JniBridge + native-lib
- `14` 集成 SDKUtils — SDKUtils.java 三阶段模拟
- `16` 激励视频转发 — showVideo callJava
- `18` IAP（Premium）转发 — processPurchase callJava
- `20` 字体替换 — 中文字体注入
- `22` 文本汉化 — hanization_map.h
- `24` 图片汉化 — PNG 重绘
- `26` AS 工程化 — gradle assembleRelease + apksigner
- `28` 最终验收 — 6 条硬指标
- `29` 清理临时空间

**声明式调度**：上述序列与强制集合通过 `skills/common/scripts/strategy/strategy-config.yaml` 的三层架构
（sniff_routing → stage_routing → stage_details）中 il2cpp 的 `stage_routing` 与 `mandatory` 字段登记；
`crack.py` 通过 `load_stage_registry` + `resolve_stage_script` 加载并调度。

## 8. 启用条件与回退

| 条件 | 处理 |
|------|------|
| 默认 | 评级 ≥ B 即启用（il2cpp type 自动触发，无需手动指定） |
| 评级 F（最易） | 阶段 04 自动 SKIP；其余阶段仍可手动跑 |
| FakerAndroid fake 失败 | 回退到 apktool + smali patch 路线（极少） |
| libil2cpp.so 加固无法 dump | 用 Frida 在运行时 hook `il2cpp_init` → 内存 dump metadata.dat |
| patched.apk 启动崩溃 | 用 Frida 注释对应 hook 重启，逐步恢复 |

## 9. 关联阅读

- [workflow.md](./workflow.md) — 阶段流程、命令、验证
- [tools-index.md](./tools-index.md) — 工具与脚本索引
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [references/hook-points-search-patterns.md](./references/hook-points-search-patterns.md) — ⭐ Hook 点检索模式（IAP/广告/Premium/本地化/反调试/网络）
- [references/fakerandroid-output-fix.md](./references/fakerandroid-output-fix.md) — FakerAndroid 导出修复
- [references/il2cpp-arm32-limitation.md](./references/il2cpp-arm32-limitation.md) — ARM32 限制
- [references/il2cpp-dump-cs-parse.md](./references/il2cpp-dump-cs-parse.md) — dump.cs 解析技巧
- [references/il2cpp-metadata-version-limit.md](./references/il2cpp-metadata-version-limit.md) — metadata 版本限制
- [references/unity-asset-extraction.md](./references/unity-asset-extraction.md) — Unity 资源提取
- [references/unity6-tricky-tribe-pattern.md](./references/unity6-tricky-tribe-pattern.md) — Unity 6 / Tricky Tribe 项目
- [../../STRATEGY.md §1.2](../../STRATEGY.md#12-类型快速识别表路由核心) — 顶层策略章节
- [../../WORKFLOW.md](../../WORKFLOW.md) — 8 阶段主流程
- [../../OBJECTIVES.md §1.4 / §3](../../OBJECTIVES.md) — 模板架构验收清单

## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：il2cpp](../../common/third-party-removal-strategy-skill/references/engine-notes.md#il2cpp)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。
