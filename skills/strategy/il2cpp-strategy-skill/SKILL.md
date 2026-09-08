---
name: il2cpp-strategy-skill
description: 处理 Unity il2cpp 加密项目的专用工作流。**默认策略**：ASBuilder.jar → AS 工程 → Hook 模板架构（汉化/去网络检测/激励视频/IAP → SDKUtils 转发）。详见 [STRATEGY.md §1.2 il2cpp 行](../../STRATEGY.md#12-类型快速识别表路由核心)。
when_to_use: 当 strategy-config detect 识别到 TYPE=il2cpp，或 APK 含 libil2cpp.so 时；或难度评级 ≥ A（≥ 60 分）时主动调用。
---

# il2cpp Unity 加密项目逆向工作流（01–29 线性）

> 处理 il2cpp 加密 Unity 项目的**专用**工作流。本工作流在通用 29 阶段骨架基础上
> 使用 **01–29 全部 29 个阶段**（12–15 为 il2cpp 专用 slot：模板集成/SDKUtils；16–19 为通用 slot：激励/IAP 转发），
> 三件核心工具：
>
> | 工具 | 角色 | 阶段 |
> |------|------|------|
> | **ASBuilder.jar** | APK → AS 工程骨架（含 smali + cpp + jniLibs + gradle wrapper） | - |
> | **Il2CppDumper / Il2CppInspectorPro / rodroid-il2cppdumper** | libil2cpp.so + global-metadata.dat → dump.cs / il2cpp.h / DummyDll | - |
> | **FakerAndroid 内置 A64HookFunction** | inline hook 注入（解密 / 鉴权 / 协议） | - |
>
> **适用评级**：S（≥80）/ A（≥60）/ B（≥40）。B 评级以下默认不启用此工作流
> （标准 15 阶段已够），但 type=il2cpp 自动触发。
>
> **声明式阶段调度**：`skills/common/scripts/strategy/strategy-config.yaml` 的三层架构
> （sniff_routing → stage_routing → stage_details）中 il2cpp 的
> `stage_details` 是单一事实来源（16 项）；`crack.py` 通过 `load_stage_registry`
> + `resolve_stage_script` 调度，旧编号通过 `legacy_stage_map` 自动迁移到 01–15。

---

## 0. Skill 目录结构（标准化）

```
skills/strategy/il2cpp-strategy-skill/
├── SKILL.md              ← 本文件（总览 + 加载顺序 + 触发条件）
├── strategy.md           ← 独立策略文档（默认工具 + Hook 架构 + 模板对接）
├── workflow.md           ← 独立流程文档（阶段命令 + 验证 + 故障处理）
├── tools-index.md        ← 工具索引（外部工具 + 模板 + skill 内部脚本）
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（统一由去功能点 skill 维护）
├── references/           ← il2cpp 特定经验库
│   ├── hook-points-search-patterns.md   # ⭐ Hook 点检索模式（IAP/广告/Premium/本地化/反调试/网络）
│   ├── fakerandroid-output-fix.md
│   ├── il2cpp-arm32-limitation.md
│   ├── il2cpp-dump-cs-parse.md
│   ├── il2cpp-metadata-version-limit.md
│   ├── unity-asset-extraction.md        # Unity 资源提取（UnityPy vs AssetStudio vs UABEANext）
│   └── unity6-tricky-tribe-pattern.md   # Unity 6 / Tricky Tribe 项目
├── scripts/
│   ├── workflow/         ← 流程脚本（每阶段专用）
│   └── common/           ← 通用脚本（跨阶段工具）
└── assets/               ← 资源（Frida 模板 / hook 规则 / 已知游戏）
```

## 1. 加载顺序（agent 必读）

> Agent 选中本 skill 后**必须**按下列顺序加载文档：

1. **[SKILL.md](./SKILL.md)**（本文件）—— 总览 + 何时调用 + 目录结构
2. **[strategy.md](./strategy.md)** —— 策略声明（默认工具 + Hook 架构 + 模板对接 + 固化规则）
3. **[workflow.md](./workflow.md)** —— 阶段流程（命令 + 验证 + 故障处理）
4. **[tools-index.md](./tools-index.md)** —— 工具与脚本索引
5. **[EXPERIENCES.md](../../EXPERIENCES.md)** —— 经验沉淀
6. **[references/](./references/)** —— il2cpp 特定经验库（按需加载）（按时间倒序追加）

> **不加载顺序**：每个文档**只**回答自己的问题，互不重复。

## 2. 何时调用

### 2.1 触发条件（满足任一）

| 信号 | 检测方式 |
|------|----------|
| `sub-stage-assess.py` 评级为 S 或 A | `crackings/<type>/<Name>/difficulty.json` |
| APK 含 `libil2cpp.so` | `unzip -l <apk>` |
| 难度评估的 **encryption 维度 ≥ 18** | `difficulty.json → encryption.score` |
| 难度评估的 **runtime 维度 ≥ 8**（含 native 协议加密） | `difficulty.json → runtime.score` |
| type 路由到 il2cpp | `skills/common/scripts/strategy/strategy-config.yaml` 的 `sniff_routing` |

### 2.2 调用方式

```bash
# 自动：crack.py 主驱动检测到 type=il2cpp 时按 strategy-config.yaml 的 stage_details 自动调度 01–20
crack.py <apk>                       # 完整流水线（含自动判断）

# 手动：单独跑 il2cpp 专用阶段（新编号 01-20 + 主阶段独立）
crack.py <apk> stage-01             # 通用静态分析
crack.py <apk> stage-02             # 预处理构建检测（apktool + FakerAndroid + toolchain + 编译测试，含模板集成）
crack.py <apk> stage-03             # 需 hook/转发相关函数分析（dump + hook plan）
crack.py <apk> stage-04             # 去第三方 SDK
crack.py <apk> stage-06             # 去除网络检测
crack.py <apk> stage-07             # 飞行模式验收（紧跟网络检测移除）
crack.py <apk> stage-08             # 激励视频转发
crack.py <apk> stage-10             # IAP（Premium）转发
# 主阶段（独立于子阶段排序，run-major-*.py 驱动）
run-major-sniff.py / run-major-assess.py / run-major-accept.py / run-major-cleanup.py
# 总驱动器（type + 子阶段名 → 执行）
python3 skills/common/scripts/run-sub-stage.py --type il2cpp --name static-analyze
```

> 全部 il2cpp 专用脚本的 canonical 副本位于
> [`skills/strategy/il2cpp-strategy-skill/scripts/workflow/`](./scripts/workflow/)。
> 处理 il2cpp 项目过程中产生的**新脚本**必须固化到该目录。

## 3. 默认策略（FakerAndroid + Hook 模板架构）

> **完整策略声明**见 [strategy.md](./strategy.md)。要点：

```
1. 入口工具固定为 ASBuilder.jar fake —— 产出 AS 工程骨架
2. 生成的 AS 工程采用 Hook 模板架构：
   所有修改点（汉化 / 去网络检测 / 激励视频 / IAP）通过 native-lib.cpp 的 inline hook 注入
3. 激励视频、IAP、Premium 通过 hook 转发（callJava）→ Java 层 → SDKUtils
4. 模板文件位置固定：
   skills/common/scripts/template-files/{MainActivity.template.java, JniBridge.template.java, SDKUtils.java}
5. 处理 il2cpp 项目产生的脚本 → 必须固化到本 skill 的 scripts/{workflow,common}/
```

## 4. 验收清单（关键节点）

> 阶段体系已收敛为 **15 子阶段（01–15）+ 4 主阶段（M1–M4）**，
> 子阶段由 `stages/sub_stage-dispatcher.py` 按 register 调度（`default-action/step-driver` 按
> `step-register.yaml` 的 number 升序执行）。下表对齐
> [`workflow.md`](./workflow.md) 的关键产物与验证；`✅` 标记者须真机验收（成功→强制固化）。
> **完整流程**见 [workflow.md](./workflow.md)。

| 阶段 | name | 关键产物 | 验证 |
|------|------|---------|------|
| **M1** | sniff（嗅探） | `findings.md` 含类型段 | `grep -c "libil2cpp.so" raw/unzip-list.txt` ≥1 |
| **M2** | assess（评估） | `difficulty.json` grade 非空 | grade ≥ A（或 ≥60 分）时启用本工作流 |
| `01` | `static-analyze` | `raw/03-jadx/sources/` + `sdks_found.txt` | sources 含 .java + `libil2cpp.so` ≥1（il2cpp 额外提取 .so + global-metadata.dat） |
| `02` | `preprocess-build` | `app-release.apk` + `classes.all.dex.jar` | gradlew assembleRelease 0 + 安装 0 + 启动 5s 无 FATAL |
| `03` | `sdk-network-removal` | `3rd-party-sdk.yaml` + `network-detection.yaml` + `sdk-network-report.yaml` | Manifest SDK 关键字=0 + `libil2cpp.so` 保留 + gradlew 0 |
| `05` ✅ | `sdk-network-device-verify` | `verify-report.md` + `screenshot-normal.png` + `screenshot-airplane.png` | 普通+飞行两段 verify_app_alive PASS + 无 FATAL |
| `05` | `revenue-forwarding` | `revenue-detection.yaml` + `native-lib.cpp`（Hooked_* + callJava） | Hooked_* ≥1 + showRewardVideo ≥1 + processPurchase ≥1 + gradlew 0 |
| `07` ✅ | `revenue-device-verify` | `verify-report.md` | logcat [xNative] showVideo + processPurchase 命中 + 30s 存活 + 无 native crash |
| `07` | `ui-hide` | `hide-plan.yaml` + `native-lib.cpp`（HookedBehaviour_set_isActiveAndEnabled） | hide-plan.yaml 非空 + gradlew 0 |
| `09` ✅ | `ui-hide-device-verify` | `verify-report.md` + `screenshot.png` | 目标按钮不可见 + 布局未变形 + 核心玩法可进 |
| `09` | `font-replace` | `font-detection.yaml` + `res/font/notosanssc.ttf` | 字体文件存在 + gradlew 0 |
| `11` ✅ | `font-device-verify` | `verify-report.md` | OCR 可见中文字符 + 字体加载无 RuntimeException |
| `11` | `text-hanization` | `hanization_map.h` + `values-zh-rCN/strings.xml` | HANIZATION_MAP ≥200 + gradlew 0 |
| `13` ✅ | `text-device-verify` | `verify-report.md` | OCR 命中中文字符串 + %s/%d 占位符保留 |
| `13` | `image-hanization` | `images-detection.yaml` + `replacements/` + `image-hanization-report.yaml` | images-manifest 闭环 + gradlew 0 |
| `15` ✅ | `image-device-verify` | `verify-report.md` + `screenshot.png` | OCR 图片含中文 + 无变形/拉伸/黑边 |
| `15` | `record-project-files` | `dir-index.yaml` + `output-project-manifest.yaml` | 两文件非空且反映全部产物 |
| **M3** | final-check（最终验收） | `stages/23-final-check/final-report.md` | OBJECTIVES.md §1 六条硬指标全过 |
| **M4** | cleanup（清理） | 清理后的 `crackings/<type>/<Name>/project/` | 仅保留 `app/` `patched.apk` `my.keystore.jks` `gradle/` |

## 5. 常见失败模式与回退

| 失败 | 原因 | 回退 |
|------|------|------|
| `global-metadata.dat` 缺失 | il2cpp 加密（从运行内存 dump） | Frida `Memory.dump()` / Frida hook `il2cpp_init` |
| `libil2cpp.so` 文本字符串稀少 | libil2cpp.so 被压缩/剥符号 | UPX/strip 检查；`radare2 -A` / Ghidra 自动分析 |
| Il2CppDumper 段错误 | metadata 版本太新 | 升级 Il2CppDumper / 换 Il2CppInspectorPro |
| Frida 找不到 libil2cpp.so | 时机问题 | `Java.perform(() => { waitForModule('libil2cpp.so') })` |
| A64HookFunction 段错误 | trampoline 长度不够 | 检查目标函数前 12 字节可被覆盖 |
| patched.apk 启动崩溃 | hook 写错导致 native crash | Frida 注释对应 hook 重启，逐步恢复 |

> **更详细的回退案例**见 [EXPERIENCES.md §0.2](../../EXPERIENCES.md#02-失败案例与回退)。

## 6. 关联文档

| 文档 | 角色 |
|------|------|
| [strategy.md](./strategy.md) | 策略声明（强制） |
| [workflow.md](./workflow.md) | 阶段流程（命令 + 验证） |
| [tools-index.md](./tools-index.md) | 工具索引（外部 + 内部） |
| [EXPERIENCES.md](../../EXPERIENCES.md) | 经验沉淀 |
| [../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) | 通用去功能点清单 |
| [references/hook-points-search-patterns.md](./references/hook-points-search-patterns.md) | ⭐ Hook 点检索模式 |
| [references/il2cpp-dump-cs-parse.md](./references/il2cpp-dump-cs-parse.md) | dump.cs 解析技巧 |
| [references/il2cpp-metadata-version-limit.md](./references/il2cpp-metadata-version-limit.md) | metadata 版本限制 |
| [references/il2cpp-arm32-limitation.md](./references/il2cpp-arm32-limitation.md) | ARM32 限制 |
| [references/fakerandroid-output-fix.md](./references/fakerandroid-output-fix.md) | FakerAndroid 修复 |
| [references/unity-asset-extraction.md](./references/unity-asset-extraction.md) | Unity 资源提取 |
| [references/unity6-tricky-tribe-pattern.md](./references/unity6-tricky-tribe-pattern.md) | Unity 6 / Tricky Tribe |
| [references/blank-screen-loading-fix.md](./references/blank-screen-loading-fix.md) | **黑屏/卡加载修复**（MainActivity extends UnityPlayerActivity + smali 过滤白名单 + JNI 桥接类保留 + raw 像素对比）[FLOWFIX] |
| [references/gdpr-delegate-webview-crash.md](./references/gdpr-delegate-webview-crash.md) | **卡加载页全链路 + Frida 探针方法论**（Il2CppDelegate 布局 method_ptr=+0x10/target=+0x20 / Unity WaitUntil true=停止等待 / Gadsme WebView 崩溃 / StandaloneInputModule 正确地址 / adb swipe phase 坑 / 直接调用游戏方法）[FLOWFIX] |
| [references/gdpr-consent-popup-hook.md](./references/gdpr-consent-popup-hook.md) | **启动时 GDPR/Privacy Consent 弹窗移除**（Unity Ads ConsentPopup/GDPRController；hook GDPRConsentWasSet→true / CheckForGDPR→no-op / CanShowAds→false；RVA 提取脚本 extract-gdpr-hooks.py）[FLOWFIX] |
| [assets/README.md](./assets/README.md) | 资源详细说明 |
| [scripts/README.md](./scripts/README.md) | 脚本库索引（workflow/ + common/） |
| [../../STRATEGY.md §1.2](../../STRATEGY.md#12-类型快速识别表路由核心) | 顶层路由表（il2cpp 行） |
| [../../WORKFLOW.md](../../WORKFLOW.md) | 5 大阶段主流程 |
| [../../OBJECTIVES.md §1.6](../../OBJECTIVES.md) | 模板架构验收清单 |
| [../../AGENTS.md §1.1](../../AGENTS.md) | 固化优先原则 |

## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：il2cpp](../../common/third-party-removal-strategy-skill/references/engine-notes.md#il2cpp)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。
