# il2cpp Tools Index — 工具与脚本索引

> **本文件是 il2cpp skill 的"工具索引"**——所有本 skill 用到的工具和脚本的统一索引。
>
> **加载顺序**：strategy.md → workflow.md → **[tools-index.md（本文件）]**
>
> **同步关系**：
> - 本目录的工具/脚本是 **canonical 副本**，与 `skills/common/scripts/`、`tools/crack-intergration-tools/` 同步
> - 修改时必须**双向同步**（除非 skill-only 脚本）

---

## 1. 外部工具（来自 `tools/crack-intergration-tools/`）

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **ASBuilder.jar** | `tools/crack-intergration-tools/execable/ASBuilder.jar` | APK → AS 工程骨架（含内嵌 il2cpp 二进制） | **01** |
| **dex2jar** | `tools/crack-intergration-tools/execable/dex2jar/` | dex → 真 .class jar（smali 转 jar 引用，问题 7） | 输出项目装配 |
| **Il2CppDumper** | `tools/crack-intergration-tools/source-projects/Il2CppDumper/` | libil2cpp.so + global-metadata.dat → dump.cs | **05** |
| **FakerAndroid 内置 A64HookFunction** | `ASBuilder.jar` 内嵌 | inline hook 引擎（fakeCpp / A64HookFunction），il2cpp 默认 hook 方式，无需额外集成 | 07 / 11 / 16 / 18 |
| **Frida** | 系统安装 | 动态 hook 框架 | 11 / 13 |

### 1.2 备选工具

| 工具 | 路径 | 用途 | 何时使用 |
|------|------|------|---------|
| **Il2CppInspectorPro** | `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/` | 工业级 il2cpp 反编译（含插件系统） | Il2CppDumper 段错误/版本太新 |
| **rodroid-il2cppdumper** | `tools/crack-intergration-tools/source-projects/rodroid-il2cppdumper/` | 跨平台 GUI（Tauri + Rust） | 需要 GUI 操作 |
| **Android_Inline_Hook_ARM64** | `tools/crack-intergration-tools/source-projects/Android_Inline_Hook_ARM64/` | ARM64 inline hook 库（GToad 多文件版） | And64InlineHook 失败时备选 |
| **Il2Fusion** | `tools/crack-intergration-tools/source-projects/il2Fusion/` | Android 侧运行时代理（LSPosed + JNI Hook） | 需要在非 root 设备上做 hook |

### 1.3 工具链版本

| 工具 | 推荐版本 | 来源 |
|------|---------|------|
| FakerAndroid | 最新 stable | https://github.com/Efaker/FakerAndroid |
| Il2CppDumper | 最新 stable | https://github.com/Perfare/Il2CppDumper |
| And64InlineHook | Rprop 主分支 | https://github.com/Rprop/And64InlineHook |
| Frida | 16.x+ | https://frida.re |

## 2. 模板文件（来自 `skills/common/scripts/template-files/`）

> **不可修改**；所有 il2cpp 项目共享同一份；扩展时必须同步更新原始文件。

| 模板 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| `MainActivity.template.java` | `skills/common/scripts/template-files/MainActivity.template.java` | 模板 Activity（含 JNI 回调路由 + Handler） | 04 |
| `JniBridge.template.java` | `skills/common/scripts/template-files/JniBridge.template.java` | native→java 桥接器 | 04 |
| `SDKUtils.java` | `skills/common/scripts/template-files/SDKUtils.java` | 激励视频/IAP 三阶段模拟工具类 | 04 |
| `native-lib.template.cpp` | `skills/common/scripts/template-files/il2cpp/native-lib.template.cpp` | **il2cpp 标准 native hook 入口（A64HookFunction + callJava + installNativeHooks + 空 setupHooks 骨架）**。覆盖 FakerAndroid fakeCpp 模式（其硬编码 RVA 在重打包后偏移错误 → SIGSEGV）。[FLOWFIX] | 12 |
| `LXGWWenKai-Regular.ttf` | `skills/common/scripts/template-files/LXGWWenKai-Regular.ttf` | 中文字体（汉化） | 13 |

### 2.1 SDKUtils.java 提供的接口

| 方法 | 用途 | 调用时机 |
|------|------|---------|
| `SDKUtils.showRewardedVideo(IRewardVideoListener)` | 模拟激励视频三阶段（500/1500/300ms） | hook `ShowRewardAd` 后 |
| `SDKUtils.loadRewardedVideo(IRewardVideoListener)` | 模拟激励视频预加载 | hook `LoadRewardedVideo` 后 |
| `SDKUtils.showInterstitial()` | 模拟插屏广告（跳过） | hook `ShowInterstitial` 后 |
| `SDKUtils.processPurchase(productId, onSuccess, onError)` | 模拟 IAP 购买成功（记录已购买） | hook `OnPurchaseRequested` 后 |
| `SDKUtils.recordPurchase(productId)` | 记录已购买（SharedPreferences 持久化） | 购买成功后 |
| `SDKUtils.isPurchased(productId)` | 查询已购买（native Is* hook 调用） | native JNI 查询 |
| `SDKUtils.unlockPremium(onComplete)` | 模拟 Premium 解锁 | hook `UnlockPremium` 后 |

### 2.2 占位符说明（MainActivity.template.java）

| 占位符 | 示例值 | 说明 |
|--------|--------|------|
| `{PACKAGE_NAME}` | `com.android.boot` | FakerAndroid 的 Java 包名 |
| `{ORIGINAL_ACTIVITY}` | `UnityPlayerActivity` | 游戏原始 Activity 类名 |
| `{ORIGINAL_ACTIVITY_IMPORT}` | `com.unity3d.player.UnityPlayerActivity` | 原始 Activity 的完整 import |
| `{NATIVE_LIB_LOAD}` | `System.loadLibrary("native-lib")` | native 库加载语句 |
| `{VIDEO_COMPLETE_CALLBACK}` | `onVideoReward(isSucess)` | 激励视频完成后的 JNI 回调 |

## 3. Skill 内部脚本（本目录）

### 3.0 目录结构

```
skills/strategy/il2cpp-strategy-skill/scripts/
├── workflow/        ← 26 个阶段专用脚本（stage-04..29-*.py，01-03 来自 general-strategy-skill）
├── common/          ← 跨阶段工具（dump-cs-generator.py + analyze-hook-points.py + extract-fm-mono-dll.py）
└── lib/
    └── stage_common.py   ← 阶段公共工具：ADB / Gradle / 进度记录 / 路径契约
```

> **声明式调度**：`skills/common/scripts/strategy/strategy-config.yaml` 的三层架构
> （sniff_routing → stage_routing → stage_details）中 `stage_details.il2cpp`
> 是单一事实来源（29 项）。`crack.py` 通过 `load_stage_registry` + `resolve_stage_script`
> 加载并按注册路径调度；旧编号通过 `legacy_stage_map` 自动迁移到 01–29。

### 3.1 scripts/workflow/（流程脚本 — 阶段专用，04–29）

> 01–03（sniff / assess / static-analyze）来自 general-strategy-skill，不在本目录。
> 07/09/20-25/28/29 等验收/通用类脚本的 il2cpp 副本已删除（详见 [REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md](../../../../docs/REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md)），路由表指向 general-strategy-skill 的对应脚本。

| 脚本 | 阶段 | 角色 | 强制 |
|------|------|------|------|
| `sub-stage-preprocess-build.py` | **04** | 预处理构建检测（apktool + FakerAndroid + toolchain + 编译测试） | ✓ |
| `sub-stage-hook-plan.py` | (03 helper) | hook-plan.yaml 生成（dump.cs 启发式匹配 IAP/Ad/Premium/Localization） | ✓ |
| `sub-stage-sdk-network-removal.py` | **04** | 去SDK + 去网络检测（manifest + smali + .so + apktool b） | ✓ |
| `sub-stage-sdk-network-device-verify.py` | **05** | 真机验收（普通模式 + 飞行模式 2 段）⚠️成功→强制固化 | ✓ |
| `sub-stage-ui-hide.py` | **10** | 去功能点（UI 隐藏 + 区域裁剪） | ✓ |
| `sub-stage-ui-hide-device-verify.py` | 08 | 去功能点真机验收 ⚠️成功→强制固化 | ✓ |
| `sub-stage-template-integration.py` | **12** | 集成模板文件（MainActivity + App + JniBridge + native-lib scaffolding） | ✓ |
| `sub-stage-template-device-verify.py` | 13 | 模板集成真机验收 ⚠️成功→强制固化 | ✓ |
| `sub-stage-sdk-utils-integration.py` | **14** | 集成 SDKUtils（com.android.common.SDKUtils 三阶段模拟） | ✓ |
| `sub-stage-sdk-utils-device-verify.py` | 15 | SDKUtils 真机验收 ⚠️成功→强制固化 | ✓ |
| `sub-stage-reward-video-forwarding.py` | **16** | 激励视频转发（showVideo callJava + native hook） | ✓ |
| `sub-stage-reward-video-device-verify.py` | 17 | 激励视频真机验收 ⚠️成功→强制固化 | ✓ |
| `sub-stage-iap-premium-forwarding.py` | **18** | IAP（Premium）转发（processPurchase callJava） | ✓ |
| `sub-stage-iap-device-verify.py` | 19 | IAP 真机验收 ⚠️成功→强制固化 | ✓ |
| *(20-25 → common)* | **20-25** | 字体/文本/图片汉化（参考 general-strategy-skill） | ✓ |
| `sub-stage-as-build.py` | **26** | AS 工程化（gradle assembleRelease + apksigner v1+v2+v3） | ✓ |
| `sub-stage-record-project-files.py` | 15 | 记录工程文件（dir-index.yaml + manifest.yaml） | ✓ |
| *(28/29 → common: `sub-stage-final-check.py` / `sub-stage-cleanup.py`)* | **28/29** | 最终验收 / 清理 | ✓ |

> 调用方式：通过 `skills/common/scripts/crack.py <apk> stage-NN` 或独立运行 `python3 stage-NN-*.py`。
> 所有脚本通过 `os.environ` 接收 `NAME`/`APK`/`STRATEGY_TYPE`/`ANDROID_SERIAL`。

### 3.2 scripts/common/（通用工具 — 跨阶段）

| 脚本 | 角色 |
|------|------|
| `dump-cs-generator.py` | dump.cs → Frida JS 片段 + C++ 桩函数（按 hook-discovery-rules.json） |
| `analyze-hook-points.py` | dump.cs → IAP/Ad/Premium hook 候选点启发式分析 |
| `extract-fm-mono-dll.py` | FM 框架 .mdl → 解密 DLL 提取（hook LoadAssemblyWithImageBinary + frida send） |
| `inject-smali-dex.py` | smali_classesN → classesN.dex 汇编 + 注入 APK（`--force` 重注入；FakerAndroid 无插件 / 超大 APK / Zip64 时用） |
| `convert-smali-to-jars.py` | smali → dex → jar(.class) 转换（问题 7：输出项目无 smali，jar 进 app/libs/ 引用） |
| `rename-dollar-res.py` | `$` 前缀资源重命名 + XML/public.xml 引用修复（AAPT2 拒绝 `$` 资源名） |
| `patch-so-return-null.py` | 二进制 patch ELF .so 函数返回 null/指定值（Firebase C++ Crashlytics SIGABRT 绕过；aarch64 `mov x0,#0` + **armv7 `mov r0,#imm; bx lr` + `--imm`** — 用于 arm32 il2cpp 强改函数返回值，如 LanguageManager 强制中文） |
| `fix-dex-jar-frames.py` | ASM 重算 StackMapTable（修复 dex2jar 输出被 D8 "Expected stack map table" 拒收） |
| `generate-stable-ids.py` | apktool public.xml → stable_ids.txt（资源 ID 保真，`aaptOptions --stable-ids`） |
| `inject-native-hook-loader.py` | 注入 native-lib 加载 + installNativeHooks 到真实 Application（解决 native hook 从未生效） |
| `generate-ui-hide-hooks.py` | 生成 UIElements 按钮隐藏 hook 代码（Update / 触发方法两种模式 + 调用链切断） |
| `frida-disable-gameobjects.py` | Frida 一次性 hook 每帧方法 → GameObject.Find + SetActive(false) 运行时禁用 GameObject（不修改 data.unity3d；il2cpp-string-new + GameObject.RVAs 来自 il2cpp-functions.h） |
| `hide-menu-pages.py` | 静态隐藏 NGUI UI：MenuPage tab（--hide, showOnPlatform=0）+ GameObject 按钮（--hide-go, m_IsActive）+ 语言按钮（--hide-langs, 裁剪 GuiLanguageSelect.buttonList）；data.unity3d 重打包 |
| `hide-unity-gameobject.py` | 静态隐藏 Unity 场景 GameObject（BundleFile 子文件 + m_Name → m_IsActive=False）；移除游戏 Logo/游戏名标题（level0 加载页 + level1 主菜单）+ 主菜单按钮（LeaderBoard/MoreGames/VR Help/VR Mode）；多场景/多名称批量 + --pid 精确隐藏；--list / --list-objects；data.unity3d 重打包 |
| `remove-logo-texture.py` | 静态替换 Unity Texture2D 为全透明（移除 Logo 纹理；仅当标题经该纹理渲染时生效） |
| `verify-il2cpp-rva.py` | 生成 Frida 脚本验证 libil2cpp RVA 是否函数入口（防 hook 极短内联函数 SIGSEGV） |
| `fix-faker-android-invalid-data.py` | FakerAndroid 内置 apktool 2.4.0 "Invalid data detected" 兜底合并（项目环境 apktool 2.11.1 + smali/res/jniLibs 合并 + manifest 修复） |
| `clean-manifest-3rd-sdk.py` | ElementTree 清理 AndroidManifest 第三方 SDK 组件（BidMachine/Yodo1/AppLovin/Unity Ads + androidx.startup meta-data + 受限权限） |
| `templates/native-lib.ad-removal.template.cpp` | il2cpp 广告移除 hook 模板（find_module_base /proc/self/maps + NoodleAdManager DisplayAd/ShowInterstitial/ShouldShowInterstitial） |
| `templates/native-lib.iap.template.cpp` | il2cpp IAP 内购模拟模板（PurchaseProduct → callJava 转发 MainActivity；Is* → JNI 查 SDKUtils.isPurchased，Java 层控制） |
| `collect-localization-strings.py` | Frida 收集 Unity Localization 字符串（hook GetEntry/GetLocalizedString） |
| `generate-hanization-map.py` | translations.json → hanization_map.h（native hook 汉化表） |
| `hanize-unity-texts-safe.py` | 场景 MB m_Text 安全汉化（m_Text 末尾检测 + 严格等长；变长会崩溃） |
| `assetstudio-haniz/` | AssetStudio 汉化辅助（C#）：DummyDll 解析 MonoBehaviour 脚本类型 + 导出 Text m_Text 布局 |
| `replace-game-font.py` | 静态替换 Unity 内嵌字体（⚠️ 实测崩溃，仅记录失败路径；Unity 6 汉化无需字体注入） |

### 3.4 assets/font-module/（中文字体注入模板，来自 tape-thrower 模板项目）

| 文件 | 角色 |
|------|------|
| `font-module.h` / `font-module.cpp` | 运行时动态创建中文字体（FontEngine_LoadFontFace → TMP_FontAsset 动态创建 → hook 注入） |
| `build.java` | Java 侧 assets 复制 + 中文字符集加载 → JNI nativeInitFont |

> 集成指南见 [references/font-injection.md](./references/font-injection.md)。

### 3.3 scripts/lib/stage_common.py（阶段公共工具）

阶段脚本共享的库：
- `repo_root()` / `as_dir(name)` / `crack_dir(name)` / `stage_out(stage_id, label)` — 路径工具
- `adb_devices()` / `adb_install()` / `adb_launch_activity()` / `adb_logcat_errors()` — ADB 包装
- `gradle_assemble_release(project, build_dir)` — Gradle 调用
- `package_from_manifest(apk)` / `launchable_activity(apk)` — APK 元数据
- `append_status()` / `append_tool_call()` — 进度与工具调用记录
- `log_info/log_warn/log_error/log_step/log_success/fatal` — 统一日志

## 4. Skill assets/ 资源

### 4.1 assets/ 目录结构

```
assets/
├── README.md                          # 资源索引（本表对应）
├── frida-hook-template.js             # Frida 主脚本模板（hook-main.js 基础）
├── and64-inline-hook-template.cpp     # And64InlineHook C++ 模板（il2cpp_hook_main.cpp 基础）
├── hook-discovery-rules.json          # 从 dump.cs 自动匹配 hook 目标的正则规则
├── dump.cs-parsing.awk                # awk 解析 dump.cs 的辅助脚本
├── known-il2cpp-games.tsv             # 已知 il2cpp 加密游戏列表（启发式参考）
└── GoldenFarm/                        # 已知项目的工作样例（参考用）
    └── hook-main.js                   # 实际 Frida 脚本样例
```

### 4.2 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `frida-hook-template.js` | 阶段 10/22 生成 `hook-main.js` 时作为基础 | 不可修改，仅作模板 |
| `and64-inline-hook-template.cpp` | 阶段 10/12 生成 `il2cpp_hook_main.cpp` 时作为基础 | 不可修改，仅作模板 |
| `hook-discovery-rules.json` | `dump-cs-generator.py` 输入；阶段 05 启发式 | 可扩展（追加新规则） |
| `known-il2cpp-games.tsv` | 启发式预判（嗅探新 APK 时对照） | 只追加不删改 |
| `GoldenFarm/hook-main.js` | 实际 Frida 脚本样例参考 | 已知项目的工作样例 |

### 4.3 扩展规则

- 新增资源前必须评估：是项目级（→ `crackings/<type>/<Name>/raw/`）还是 skill 级（→ `assets/`）
- skill 级资源须被 2 个以上项目复用
- 命名 `<scope>-<format>`（如 `hook-discovery-rules.json`、`frida-hook-template.js`）

## 5. 工具调用示例

### 5.1 阶段 04：预处理构建检测（强制）

```bash
# 通过 crack.py 主驱动（推荐）
./skills/common/scripts/crack.py <apk> stage-04

# 直接调用
python3 skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py

# 手动执行（FakerAndroid 本身）
java -jar tools/crack-intergration-tools/execable/ASBuilder.jar fake \
     -o crackings/<type>/<Name>/project/
     apks/<file>.apk
```

### 5.2 阶段 05：fn 分析（强制）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-05

# 手动执行（Il2CppDumper）
unzip -p apks/<file>.apk lib/arm64-v8a/libil2cpp.so > crackings/<type>/<Name>/stages/05-hook-fn-analyze/libil2cpp.so
unzip -p apks/<file>.apk assets/bin/Data/Managed/Metadata/global-metadata.dat > crackings/<type>/<Name>/stages/05-hook-fn-analyze/global-metadata.dat
Il2CppDumper crackings/<type>/<Name>/stages/05-hook-fn-analyze/libil2cpp.so \
               crackings/<type>/<Name>/stages/05-hook-fn-analyze/global-metadata.dat \
               crackings/<type>/<Name>/stages/05-hook-fn-analyze/dump/
```

### 5.3 阶段 10：激励视频转发（强制）

> [FLOWFIX 2026-08-16] 激励/IAP 阶段前移至网络检测移除（08）之后；飞行模式验收紧跟 08
> （新 09），激励/IAP 顺延为新 09/10（激励）与 11/12（IAP）。

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-10

# il2cpp 默认使用 FakerAndroid 内置 A64HookFunction（无需额外配置）

# 手动：Frida attach（调试用）
adb shell am start -n <pkg>/<activity>
frida -U -f <pkg> -l crackings/<type>/<Name>/project/app/src/main/cpp/hooks/frida-scripts/hook-main.js --no-pause
```

### 5.4 dump.cs → Frida JS + C++ 桩

```bash
python3 skills/strategy/il2cpp-strategy-skill/scripts/common/dump-cs-generator.py \
    crackings/<type>/<Name>/stages/05-hook-fn-analyze/dump/dump.cs \
    skills/strategy/il2cpp-strategy-skill/assets/hook-discovery-rules.json \
    crackings/<type>/<Name>/project/hooks
```

## 6. 工具下载与更新

> 下载新工具后必须按 AGENTS.md §6 在主仓库工具路径速查表中追加一行。
> 本目录 `assets/` 和 `scripts/` 是 skill 内部维护，不在 AGENTS.md 中索引。

### 6.1 下载来源

| 工具 | 仓库 | 备注 |
|------|------|------|
| FakerAndroid | https://github.com/Efaker/FakerAndroid | release jar |
| Il2CppDumper | https://github.com/Perfare/Il2CppDumper | 自编译 |
| And64InlineHook | https://github.com/Rprop/And64InlineHook | header + cpp 单文件 |
| Frida | https://frida.re | pip / npm 安装 |

### 6.2 SHA-256 校验

下载后必须校验 SHA-256 并记录在 `tools/crack-intergration-tools/source-projects/<tool>/CHECKSUM`。

## 7. 关联阅读

- [strategy.md](./strategy.md) — 默认策略
- [workflow.md](./workflow.md) — 阶段流程
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [assets/README.md](./assets/README.md) — 资源详细说明
- [scripts/workflow/README.md](./scripts/workflow/README.md) — 流程脚本索引
- [scripts/common/README.md](./scripts/common/README.md) — 通用脚本索引
- [../../AGENTS.md §6](../../AGENTS.md) — 主仓库工具路径速查表
- [../../OBJECTIVES.md §2](../../OBJECTIVES.md) — 工具版本约束

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |


## sub_stage > action > step 三层架构脚本（register 驱动）

| 脚本 | 角色 |
|------|------|
| `stages/sub_stage-dispatcher.py` | 子阶段总调度器（读 `stages/sub-stage-register.yaml`，按 `sub_stages:` 书写顺序逐个委托各子阶段 action-driver） |
| `stages/sub-stage-register.yaml` | 子阶段注册表（id + name + actions；sub_stages 书写顺序 = 执行顺序） |
| `stages/<name>/action-driver.py` | 执行方案驱动器（读 action-register.yaml 选当前 action → 委托 default-action/step-driver） |
| `stages/<name>/action-register.yaml` | 动作配置表（动态 action 声明：default + all-actions） |
| `stages/<name>/default-action/step-driver.py` | 步骤调度器（读 step-register.yaml 按 number 顺序 → 动态 import step-*.py） |
| `stages/<name>/default-action/step-register.yaml` | 步骤注册表（number + name + script） |
| `stages/<name>/default-action/step-*.py` | 步骤脚本（Step 子类，execute(steps_results)，无数字前缀） |
| `scripts/step_base.py` | Step 基类 + `_find_repo()` 自适应探测 REPO + `stage_path()` 从 register 动态拼产物目录 |
