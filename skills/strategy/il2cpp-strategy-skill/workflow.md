# il2cpp Workflow — 阶段流程操作手册

> **加载顺序**：strategy.md → **workflow.md（本文件）** → tools-index.md
>
> **核心事实来源**：
> - 策略路由 + 引擎特征 → [`strategy.md`](./strategy.md)
> - 工具索引 → [`tools-index.md`](./tools-index.md)
> - 经验沉淀 → [`EXPERIENCES.md`](../../../EXPERIENCES.md)
> - 主流程 + 01–15 槽位语义 → [`WORKFLOW.md`](../../../WORKFLOW.md)
> - 跨 type 汉化分类与质量边界 → [汉化策略参考](../../common/hanization-strategy-skill/SKILL.md)
> - **子阶段调度** → [`il2cpp-strategy-skill/stages/sub-stage-register.yaml`](./stages/sub-stage-register.yaml)（`sub_stages:` 书写顺序 = 执行顺序）
> - 路由速查表（下表）每行 [id · name · 逻辑归属(common/il2cpp覆盖)]：实际执行由 `stages/sub_stage-dispatcher.py` 按 register 逐个子阶段委托 `stages/<name>/action-driver.py`
>
> common 汉化 skill 只提供参考；实际入口、action/step、产物与验收以本 workflow 和当前 register 为执行权威。

---

## 子阶段路由

## 01 — static-analyze · 通用静态分析

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py`（11302B）

### 步骤

| 步骤 | 内容 | 产物 |
|------|------|------|
| — | jadx 反编译 Java 层，提取 `sources/` | `crackings/<type>/<Name>/raw/03-jadx/sources/` |
| — | 扫描第三方 SDK（manifest + .so + smali） | `crackings/<type>/<Name>/04-findings/sdks_found.txt` |
| — | 定位原启动入口（Activity / Application） | `crackings/<type>/<Name>/raw/03-static-analyze/original-entry-analysis.md` |
| — | **il2cpp 额外**：提取 `lib/arm64-v8a/libil2cpp.so` + `assets/bin/Data/Managed/Metadata/global-metadata.dat` | 供子阶段 03 使用 |

### 验证

```bash
[ -d crackings/<type>/<Name>/raw/03-jadx/sources ] && find ... -name '*.java' | head -1
grep -c "libil2cpp.so" crackings/<type>/<Name>/raw/unzip-list.txt   # ≥ 1
```

### 注意
- 原入口 Activity 存档供后续模板注入对照，实际交付入口统一为 `com.android.boot.MainActivity`

---

## 02 — preprocess-build · 预处理构建

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py`（24412B）

### 步骤（10步）

| 步骤 | 内容 | 产物 |
|------|------|------|
| 步骤1 | 环境初始化：加载 env.sh → 解析 APK 路径/名称 → 创建 crackings/output-projects 目录 | 目录创建 |
| 步骤2 | 计算 MD5：`md5sum source.apk → source.apk.md5` | `crackings/<type>/<Name>/source.apk.md5` |
| 步骤3 | 解包：**FakerAndroid 优先**，失败则 apktool 兜底 | `crackings/<type>/<Name>/raw/01-apktool/` |
| 步骤4 | 清理 res/values/：只保留 `strings.xml`，删除 `strings-*.xml` | — |
| 步骤5 | Android 资源修复：$文件名 / v31 / 损坏 vector/selector / 空 intent | — |
| 步骤6 | AndroidManifest 修复：package 属性 / splits / Android 13+ 属性 / 空 intent | — |
| 步骤7 | build.gradle namespace 注入：动态提取包名 → 写入 namespace | `crackings/<type>/<Name>/project/app/build.gradle` |
| 步骤8 | 模板集成：MainActivity / JniBridge / App / SDKUtils / native-lib / And64InlineHook / CMakeLists | `app/src/main/java/com/android/boot/` 等 |
| 步骤9 | smali → jar：smali 目录编译为 `classes.all.dex.jar` | `crackings/<type>/<Name>/project/app/javaScaffoding/classes.all.dex.jar` |
| 步骤10 | 编译测试：`./gradlew assembleRelease` | `crackings/<type>/<Name>/project/app/build/outputs/apk/release/app-release.apk` |

### 验证

```bash
./gradlew assembleRelease   # exit 0
adb install -r crackings/<type>/<Name>/project/app/build/outputs/apk/release/app-release.apk   # exit 0
"$ADB_BIN" shell am start -W -n <package>/<activity>   # 5s 无 FATAL
```

### 注意
- il2cpp 模板集成时需注入 `A64HookFunction` + `callJava` 框架
- build.gradle ndk.abiFilters：存在 arm64-v8a 时只保留 arm64-v8a，否则回退 armeabi-v7a

---

## 03 — sdk-network-removal · 去第三方SDK + 去网络检测（合并）

实现要点见 [去第三方 SDK：il2cpp](../../common/third-party-removal-strategy-skill/references/engine-notes.md#il2cpp)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

# Manifest 中 SDK 关键字 = 0
grep -ci "firebase\|ironsource\|applovin\|crashlytics" \
  crackings/<type>/<Name>/project/app/src/main/AndroidManifest.xml   # = 0

# libil2cpp.so 保留
[ -f crackings/<type>/<Name>/project/app/jniLibs/arm64-v8a/libil2cpp.so ]

# gradlew 编译通过
./gradlew assembleRelease   # exit 0
```

### 注意
- 原 04 + 原 06 合并为新 04（统一一次构建，省一半时间）
- **清单驱动**（[FLOWFIX 2026-08-18]）：所有 SDK 判断以 `third-party-sdk-removal-registry.yaml` 为准
- 清单缺失时 raise SystemExit，强制修复清单，不静默回退
- 成功 → 强制固化

---

## 04 — sdk-network-device-verify · 真机验收（SDK + 网络检测合并）

实现要点见 [去第三方 SDK：il2cpp](../../common/third-party-removal-strategy-skill/references/engine-notes.md#il2cpp)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

# 两段都通过（普通模式 PASS + 飞行模式 PASS）
grep -A2 "总结" crackings/<type>/<Name>/stages/04-sdk-network-device-verify/verify-report.md | grep "✅ PASS"
```

#### 注意

- 成功 → 强制固化

---

## 05 — revenue-forwarding · 激励 + IAP 转发（合并）

**脚本**：`skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-reward-video-forwarding.py`

### 步骤（7步）

| 步骤 | 内容 | 产物 |
|------|------|------|
| 步骤1 | 从 step1-signatures/（dump.cs / il2cpp.h / script.json）收集激励视频 + IAP 方法 → 生成 `revenue-detection.yaml` | `revenue-detection.yaml` |
| 步骤2 | **策略选择**：il2cpp → native hook（`Hooked_*` + `callJava("showRewardVideo")` + `callJava("processPurchase")`） | — |
| 步骤3 | **hook 注册**：A64HookFunction（注册到 "Hook Engine Initialized" 前） | `native-lib.cpp` 注入 |
| 步骤4 | 调用链检查：MainActivity → SDKUtils.showRewardVideo() / SDKUtils.processPurchase() → recordPurchase() | — |
| 步骤5 | 生成 yaml 报告 | `revenue-report.yaml` |
| 步骤6 | smali → jar | `app/javaScaffoding/classes.all.dex.jar` |
| 步骤7 | gradlew assembleRelease | `app-release.apk` |

### 调用链

```
# 激励视频
il2cpp ShowRewardedVideo()
  → A64Hook（RVA 来自 hook-plan.yaml category=Ad）
    → callJava("showRewardVideo")  [JNI]
      → JniBridge → MainActivity
        → Handler → SDKUtils.showRewardVideo()
          → forwardRewardEvents()  [Java 层]
            → onRewardVideoComplete()  [JNI 回 native]

# IAP 内购
il2cpp PurchaseProduct(id) 被调用
  → A64Hook（RVA 来自 hook-plan.yaml category=IAP）
    → callJava("processPurchase:<id>")  [JNI]
      → JniBridge → MainActivity
        → Handler 解析 payload=id
          → SDKUtils.processPurchase(id, onSuccess→onIapSuccess(id))
            → recordPurchase(id)  [Java SharedPreferences 持久化]
              → onIapSuccess(id)  [JNI 回 native]
  Is* 判断 → JNI 查 SDKUtils.isPurchased(id) → Java 层控制结果
```

### 验证

```bash
# Hooked_* + callJava 注入（激励 + IAP）
grep -c "Hooked_" crackings/<type>/<Name>/project/app/src/main/cpp/native-lib.cpp   # ≥ 1
grep -c "showRewardVideo" crackings/<type>/<Name>/project/app/src/main/cpp/native-lib.cpp   # ≥ 1
grep -c "processPurchase" crackings/<type>/<Name>/project/app/src/main/cpp/native-lib.cpp   # ≥ 1

# gradlew 通过
./gradlew assembleRelease   # exit 0
```

### 注意
- RVA 来源：hook-plan.yaml（category=Ad / category=IAP），无则从 dump.cs `// RVA: 0x..` 注释行下方的真实方法行提取
- Frida 验证 RVA 有效后再注入（标准 prologue 可 hook，极短函数不可）
- 商品 ID 从 `stringliteral.json` 提取（`grep '"value": "com.<pkg>.'`）
- 带 string 参数的方法用 `il2cppStr()` 解析 x1（UTF-16LE → UTF-8）
- 成功 → 强制固化

### ASBuilder 工程注入方式（il2cpp 实测，替代旧模板 A64HookFunction）
- 本工程原生 hook 基础设施是 `libs/prefab/modules/tool/libs/libtool.a` 的 `baseImageAddr` + `fakeCpp`（Dobby）。**先删 `cpp/faker-stubs.cpp`（桩盖真实实现）+ CMakeLists `add_library(faker STATIC IMPORTED)` 链接 libtool.a**，否则 hook 装不上（base 恒 0）。
- hook 注册时机：native `fakeApp()` 在 `Application.onCreate`（引擎加载前）执行 → **起后台 std::thread 轮询 `baseImageAddr("libil2cpp.so")>0` 再 installHooks**。
- **每次 `fakeCpp` 前 `mprotect` 目标函数页为 `PROT_READ|WRITE|EXEC`**（libil2cpp.so .text 是 execute-only，Dobby 不自带页写权限 → SIGSEGV）。
- `callJava` 需兼容非 Java 线程：`GetEnv` 返回 `JNI_EDETACHED` 时 `AttachCurrentThread`，用后 Detach。
- **调用链语义**（用户约定）：
  - 激励视频 / IAP = **转发**：hook 内 `callJava("showRewardVideo"/"processPurchase")` → Java(onJniCall) → `SDKUtils.showRewardedVideo(listener)` / `SDKUtils.processPurchase(id,onSuccess,onError)`（记录已购集合 + 持久化 + onSuccess）。IAP `ProcessPurchase` 返回 `PurchaseProcessingResult.Complete(=0)`。
  - 插屏 / 横幅 / 非激励广告 = **桩化**：`ShowInterstitial` / `RequestBanner` / `ShowBannerAds` / `ShowBannerView` 纯 no-op（不调用原函数、不转发、不显示）。
- 同一方法名多类多副本×不同 RVA（如 ShowRewardAdsButton 3 处）：需全部 hook 或选 UI 主入口。

---

## 06 — revenue-device-verify · 真机验收（激励 + IAP）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

### 步骤（8步）

| 步骤 | 内容 |
|------|------|
| 步骤1 | 安装 patched.apk |
| 步骤2 | 清 logcat：`adb logcat -c` |
| 步骤3 | 重启应用 |
| 步骤4 | 触发激励视频 + IAP 回调（Frida 或手动） |
| 步骤5 | `adb logcat | grep "\[xNative\]"` 命中 showVideo + processPurchase |
| 步骤6 | Premium 解锁 Toast 命中 + 进程存活 30s + 无 native crash |
| 步骤7 | 截图存档 |
| 步骤8 | 写入 verify-report.md |

### 验证

```bash
[ -s crackings/<type>/<Name>/stages/06-revenue-device-verify/verify-report.md ]
```

### 注意
- 成功 → 强制固化（激励 + IAP 转发经验）

---

## 07 — ui-hide · 去功能点（UI 隐藏）

**脚本**：由当前注册表路由至 `skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-ui-hide.py`。

实现要点见 [去功能点：il2cpp](../../common/feature-removal-strategy-skill/references/engine-notes.md#il2cpp)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

## 08 — ui-hide-device-verify · 真机验收（去功能点）

**脚本**：由当前注册表路由至 `skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py`。

实现要点见 [去功能点：il2cpp](../../common/feature-removal-strategy-skill/references/engine-notes.md#il2cpp)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

## 09 — font-replace · 字体替换

**入口与真实步骤**：register 路由到 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py`，`default-action` 的 step 顺序为 `smali-to-jar → gradle-build → gen-report → scan-fonts → replace-font`；声明产物是 `project/app/app/src/main/res/font/notosanssc.ttf`。

**IL2CPP 差异**：先区分 Unity TextCore/TMP 的系统 CJK fallback、bundle 内嵌字体与确需运行时注入的目标。老 Unity 的静态 `m_FontData` 替换可能触发 `libunity.so` 断言；需要跨设备稳定字体时，沿用现有 `font-module` 路径，在 TMP 初始化后动态创建字体并通过 `TMP_Text_set_font` / `Text_set_font` 注入。若字体位于 `data.unity3d`、`.assets` 或 AssetBundle，必须保持对象与 bundle 结构，不得用 Android `res/font` 产物冒充 Unity 字体已生效。

---

## 10 — font-device-verify · 真机验收（字体）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。在真实设备覆盖实际使用 Text/TMP 或 bundle 字体的页面，并检查 `libunity.so` / `libil2cpp.so` 无字体相关崩溃；register 产物为 `stages/13-font-device-verify/verify-report.md` 与 `screenshot.png`。未完成真机验收时暂停在 11。

---

## 11 — text-hanization · 文本汉化

**执行权威**：register 当前 `run-action: metadata-hanize`；入口为 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py`。不得把备选 hook 方案描述成默认流程。

### 默认 action：metadata-hanize

真实 step 顺序为：

`prepare-metadata → load-translations → patch-metadata → smali-to-jar → gradle-build → gen-report`

- `prepare-metadata` 定位工程中的 `assets/bin/Data/Managed/Metadata/global-metadata.dat`，复用或提取 `stringliteral.json`，并保留 `metadata.original.dat`。
- `load-translations` 加载当前文本阶段目录中的 `translations.json`；仅在该文件不存在时，由现有 step 自动调用 [`generate-hanization-translations.py`](../../common/scripts/generate-hanization-translations.py)，读取 `stringliteral.json` 与 [`hanization-common-keywords.yaml`](../../common/scripts/hanization-common-keywords.yaml) 的 `objects` 和 `type_extra.<type>`，按词条的 `match: exact|contains` 生成译文表。这两个入口已登记于 [SCRIPTS-INDEX](../../common/scripts/SCRIPTS-INDEX.md)；生成失败或仍缺文件时，step 返回 `needs_translation=True`，须补齐译文后重跑。译文质量边界继续引用 [common 汉化 skill](../../common/hanization-strategy-skill/SKILL.md)。
- `patch-metadata` 必须通过现有 `skills/common/scripts/metadata-patcher.py` 基于原始 metadata 重建；字符串 index 保持稳定，现有引擎/.NET 排除与格式保护继续生效，输出写回 register 指定的工程 metadata。
- action 产物包括 `translations.json`、`patch-all.json`、`patched-metadata.yaml`；register 还要求 `stages/11-text-hanization/{strings-collected.yaml, patched-metadata.yaml, text-hanization-report.yaml}` 和构建出的 `app-release.apk`。

### Bundle 与运行时文本路径

`global-metadata.dat` 只覆盖 IL2CPP 字符串字面量。场景 `m_Text`、Text/TMP 对象、`data.unity3d`、`.assets`、AssetBundle 或 Addressables 中的文本继续走现有资产解析/写回路径；保持对象标识、引用关系和 Bundle 结构完整，允许现有工具通过 `set_raw_data` 正确重建变长数据，不得施加等长限制。不能把 metadata 命中数当作这些文本已完成。

metadata 加密、版本不受支持或需要按游戏逻辑处理动态文本时，使用注册的备选 `default-action`：`smali-to-jar → gradle-build → gen-report → collect-strings → build-map`，产出 `hanization_map.h` 与 `values-zh-rCN/strings.xml`，再由 `A64HookFunction` 挂到有效 IL2CPP 函数体完成运行时替换。Frida/运行时 dump 只用于取回解密 metadata 或定位 hook 点；持久化结果必须进入工程与重打包产物。

---

## 12 — text-device-verify · 真机验收（文本）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。真实设备需同时覆盖 metadata 命中的主流程文本，以及实际存在的 Bundle/Text/TMP 或动态文本路径；除 register role 外，还要确认 metadata 写回后索引解析正常且无 `libil2cpp.so` / `libunity.so` 崩溃。产物为 `stages/15-text-device-verify/verify-report.md` 与 `ocr-screenshots/`；无法执行时暂停在 13。

---

## 13 — image-hanization · 图片汉化

register 路由 common 脚本，注册 `default-action` 的真实 step 为 `smali-to-jar → gradle-build → gen-report → detect-images → ocr-images`。IL2CPP 图片可能位于 Android drawable，也可能嵌在 `data.unity3d`、`.assets`、AssetBundle 或 Addressables；后者沿用现有 Unity 资产写回方式并保持对象和 bundle 结构。执行结果必须满足 register 声明的 `project/app/app/src/main/res/drawable*/<translated>.png` 与 `stages/16-image-hanization/images-manifest.yaml`，实际 bundle 产物同时记录进 manifest，不能只检查 drawable。

---

## 14 — image-device-verify · 真机验收（图片）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。真实设备必须进入会实际加载目标 Unity bundle/Addressable 的主流程页面，并完成 register role 的图片验收及应用存活检查；产物为 `stages/17-image-device-verify/verify-report.md` 与 `screenshot.png`。无法执行时暂停在 15。

## 15 — record-project-files · 记录工程文件

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py`（6335B）

### 步骤（4步）

| 步骤 | 内容 | 产物 |
|------|------|------|
| 步骤1 | 扫描 `crackings/<type>/<Name>/project/` 全部生成文件/目录 | — |
| 步骤2 | 生成 `dir-index.yaml`（路径 + 类型 + 说明 + 登记时间） | `crackings/<type>/<Name>/dir-index.yaml` |
| 步骤3 | 生成 `output-project-manifest.yaml`（manifest 字段完整） | `crackings/<type>/<Name>/output-project-manifest.yaml` |

### 验证

```bash
[ -s crackings/<type>/<Name>/dir-index.yaml ]
[ -s crackings/<type>/<Name>/output-project-manifest.yaml ]
```

---

## 强制固化规则

每个 `verify=true` 子阶段（04/06/08/10/12/14）真机验收成功后**必须**强制固化。

**固化流程**（AGENTS.md §1.6）：
1. 盘点本阶段新增/修复的脚本
2. 按分布规则落位：跨 type → `skills/common/scripts/`；il2cpp 专用 → `il2cpp-skill scripts/`
3. 命名 `<verb>-<scope>.py`（禁 `tmp_*` / `test_*`）
4. 登记 `SCRIPTS-INDEX.md` + skill `scripts/README.md`
5. 追加经验到 `EXPERIENCES.md` / `references/`
6. `status.yaml` 记录（标记 `[FLOWFIX]` 若有流程 bug）

---

## 常见失败模式

| 现象 | 原因 | 处理 |
|------|------|------|
| Il2CppDumper 退出码 -6 | Console.ReadKey 不支持，非失败 | 按产物存在判断 |
| A64Hook SIGSEGV | hook 目标非函数入口 / dlopen 基址非页对齐 | Frida 验证 RVA 后再注入 |
| gradlew exit 1 | ProGuard keep 缺失 / namespace 不匹配 | 检查 build.gradle keep 规则 |
| device-verify FATAL | 引擎 .so 被误删 / Manifest 权限缺失 | 确认 engine_so_keep 清单 |

---

## 主阶段（sniff / assess / final-check / cleanup）

| 主阶段 | 脚本 | 产物 |
|--------|------|------|
| sniff（嗅探） | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py` | `crackings/<type>/<Name>/findings.md` |
| assess（评估） | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py` | `crackings/<type>/<Name>/difficulty.json` |
| final-check（最终验收） | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py` | `crackings/<type>/<Name>/stages/23-final-check/final-report.md` |
| cleanup（清理） | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py` | — |

主阶段由 Agent 按 WORKFLOW.md 规则人工判断、记录和验收，不依赖本文件子阶段章节。
