# 逆向项目脚本索引（SCRIPTS-INDEX）

> **本表只收录逆向项目脚本及必要的配置、运行库。**
> 收录范围：APK 嗅探、分析、修改、汉化、构建、签名、真机验收、项目记录，以及所需工具链和策略支持。
> 不收录文件改名、目录迁移、路径引用替换、文档归并、索引整理等仓库维护脚本，也不列出这些脚本的路径索引。
> 创建脚本前必须声明类别；仓库维护脚本按 AGENTS.md §1.3 独立存放，不加入本表或 skill 子索引。
> Agent 查找/复用逆向项目脚本时，**必须先查本表**（AGENTS.md §1.9）；新增逆向项目脚本后同步登记。
>
> **脚本分布规则**（AGENTS.md §1.3）：
> - 跨 type 通用脚本 → `skills/common/scripts/` 或 `skills/common/*-skill/scripts/`
> - type 专用脚本 → `skills/strategy/<type>-strategy-skill/scripts/{workflow,common}/`
>
> **子阶段脚本命名重整**：
> - 旧名 `stage-XX-name.py` → 新名 `sub-stage-name.py`（**去数字前缀**）
> - 数字归属由各 type skill 的 `stages/sub-stage-register.yaml` 记录（机器可读）
> - 详见 [docs/REFACTOR-2026-08-11-sub-stage-routing.md](../docs/REFACTOR-2026-08-11-sub-stage-routing.md)
> - 旧 `stage-XX-name.py` 已全部重命名（70 个），旧版已删除
>
> **子阶段编号重排为 01–15 线性连续**（旧 00/00a/01-21 → 新 01-15）。
> 每个修改阶段紧跟独立真机验收（04/06/08/10/12/14，成功→强制固化）。
>
> 各 skill 的 `scripts/README.md` 是子集索引（本表的精简版），以本表为 canonical。
> 各 type 的 `stages/sub-stage-register.yaml` 定义子阶段，`action-register.yaml` 选择方案，`step-register.yaml` 定义步骤。

---

## 1. 共享工具 / 策略支持（skills/common/scripts/）

> 当前流程由 Agent 控制四大主阶段，type register → action → step 执行子阶段。下列历史批量入口仍有引用，因此保留；其旧编号和跳阶段参数不属于当前正式流程。

| 脚本 | 角色 |
|------|------|
| `run-pipeline.py` | 历史七段批量兼容入口；非当前四大主阶段的默认入口 |
| `run-major-sniff.py` | M1 类型嗅探辅助 |
| `run-major-assess.py` | M2 难度评估辅助 |
| `run-major-strategy.py` | 历史策略路由辅助；不独立构成当前主阶段 |
| `run-major-verify.py` | 产出核对辅助（AS 工程 + patched.apk md5） |
| `run-major-accept.py` | M3 交付验收辅助 |
| `run-major-cleanup.py` | M4 临时空间清理辅助 |
| `crack.py` | 历史兼容入口，仍有批量调用；新任务按当前 type workflow 执行 |
| `find-project.py` | 检索用户指定项目：apks/ 新跑 or crackings/ 断点续跑，读 status.yaml 给续跑入口 |
| `init-project-index.py` | 为已有项目生成/刷新 dir-index.yaml（项目目录索引表） |
| `strategy/strategy-config.py` | 策略引擎：APK → type → skill 路由 |
| `strategy/strategy-config.yaml` | 策略配置（type/stages/mandatory/scripts 注册） |
| `car-tool.py` | Corona SDK resource.car repacker |
| `extract-corona-car.py` | Corona SDK resource.car extractor |
| `integrate-activity-files.py` | 活动文件集成 |
| `patch-librslg-connect.py` | librslg connect patch |
| `setup-local-tools.py` | 本地工具链安装 |
| `setup-local-tools.ps1` | 本地工具链安装（PowerShell） |
| `install-tools.sh` / `install-tools.bat` / `tools-source-registry.txt` | **下载所有工具项目源码**（读取 registry 逐个 git clone 到 source-projects/；Linux 用 .sh、Windows 用 .bat；支持 --list/--force/--full/--only/镜像前缀 GIT_PROXY_URL；dex2jar/FixStackmaps 为已内置非 git 项目） |
| `init-project-git.py` | **给单个处理项目初始化嵌套独立 git 仓库**（crackings/<type>/<Name>/ 内 git init + 生成项目级 .gitignore 忽略 raw/project.build 等体积产物 + 剥离内嵌 .git + 首次基线提交；父仓库整棵忽略 crackings/ 故每项目独立版本控制） |
| `commit-project-stage.py` | **项目独立 git 仓库：阶段提交**（每完成一个子阶段 add+commit 形成回滚节点；--stage 并入提交信息；--dry-run 预览；回滚方式为人工 git reset --hard） |
| `push-project-remote.py` | **仅推送 project/ 子目录到远程 git**（sparse-checkout 临时切到 project/* → set remote → push --force-with-lease → disable 恢复完整视图；--remote 必填脚本不内置；--dry-run 预览；--restore-only 异常复位） |
| `verify-commit-push-major-stage.py` | **主阶段提交/推送校验**（读 sub-stage-register.yaml 的 stage id 列表 + 校验每个 id 都有 commit + remote origin 已设 + origin/branch 至少 1 commit；失败时给出每个缺失 stage 的修复命令） |
| `dex-dex2jar-classpath.py` | **原始 APK dex→class jar 编译类路径**（[FLOWFIX 2026-08-30] 替代缺失的 convert-smali-to-jars.py；dex2jar 转 jar + 剔除 com/<pkg>/ + SDK 前缀，放 app/libs/ 应对 UnityPlayerActivity 编译期缺失） |
| `asbuilder-dex-jarify.py` | **ASBuilder 工程补齐游戏 dex（方案 A 落地）**（原 APK 每 dex → dex2jar → 剔应用包名 BuildConfig/R$* → FixStackmaps 补 StackMapTable → **LambdaNameNormalizer ASM 归一化 lambda 类名 '-'→'_'** → 放 app/libs/ by implementation fileTree；解决 ASBuilder 用标准 AGP 不编译 smali 致 APK 仅骨架类；配套 execable/LambdaNameNormalizer.jar） |
| `fix-fakerandroid-cmakelists.py` | **修复 FakerAndroid CMakeLists**（[FLOWFIX] 移除 find_package(base)，改 file(GLOB)+And64InlineHook+dl/log/z） |
| `apply-sdk-removal-from-registry.py` | **按 SDK 移除清单删除文件**（[FLOWFIX] 替代缺失的 sub-stage-sdk-network-removal.py SDK 段；smali/so/assets 按清单删，engine_so_keep 白名单校验） |
| `strip-manifest-sdks.py` | **按清单清理 AndroidManifest 组件/权限/queries**（[FLOWFIX] 替代手工 patch；manifest_drop_exact/keyword + 广告权限 + queries） |
| `extract-gdpr-hooks.py` | **提取 GDPR/consent 弹窗 hook RVA**（[FLOWFIX] 从 dump.cs 提取 GDPRConsentWasSet/CheckForGDPR/CanShowAds 等 RVA 并生成 native-lib.cpp hook 片段；移除启动时隐私弹窗） |
| `lib/common.py` | 公共函数库（路径/日志/进度/工具函数） |
| `lib/filter-dex-jar.py` | dex/jar 类过滤 |
| `lib/stub-sdk-smali.py` | SDK smali 桩化 |
| `network-analyze/capture-and-analyze.py` | 抓包分析 |
| `network-analyze/mock-server.py` | 网络 mock server |
| `network-analyze/setup-reverse-tether.py` | 反向网络设置 |
| `device-swipe.py` | 真机模拟滑动/点击手势（`<x1> <y1> <x2> <y2> [ms]` 或 `tap <x> <y>`；§1.13 替代手敲 adb swipe/input tap） |
| `tests/test_il2cpp_workflow.py` | il2cpp 工作流契约测试 |
| `update-status.py` | 项目状态更新脚本（更新 status.yaml） |
| `run-sub-stage.py` | 历史 worker 路由入口；当前子阶段使用 type 的 register/action/step 调度链 |
| `rebuild-fakerandroid-jar.py` | **ASBuilder.jar 一键重建**（捆绑库升级 apktool 2.11.1/smali 2.5.2/dex2jar 2.4/guava 兼容补丁；`--test <apk>` 带冒烟；产物 `tmp/faker-rebuild/FakerAndroid-updated.jar`，已落位 `execable/`；实测 Invalid data 11.6万→0、jniLibs 补全） |
| `verify-stage.py` | 阶段验收脚本（验证阶段产物是否符合要求） |
| `fix-split-manifest.py` | 修复 AndroidManifest.xml 中的 split 配置（移除 requiredSplitTypes 等） |
| `asset-identify.py` | 资源识别脚本（扫描APK中的所有资源，生成资源清单） |
| `asset-analyze.py` | 资源分析脚本（分析文本/图片/字体，生成汉化映射表） |
| `asset-replace.py` | 资源替换脚本（替换图片/文本/字体用于汉化） |
| `assetripper-extract.py` | AssetRipper 封装脚本（提取Unity资源） |
| `unstore-arsc.py` | **resources.arsc → ZIP_STORED + 4字节对齐**（Android 11+ SDK 30 要求 uncompressed，apktool b 压缩导致安装 -124；signSmaliApk 注入，跨 type 通用） |
| `generate-hanization-translations.py` | **用「通用游戏关键字→中文」字典生成汉化译文表**（[FLOWFIX-汉化] 读 hanization-common-keywords.yaml + stringliteral.json → 参数匹配(exact/contains 带剩余护栏) → 写 stages/<text-hanization>/translations.json，供方案A metadata-patcher 回写；文本汉化子阶段 step-load-translations 缺失译文表时自动加载该字典生成） |
| `hanization-common-keywords.yaml` | **常见游戏内容关键字→中文 汉化字典（跨 type 共享）**（objects 通用段 + type_extra 类型专用段；match=exact|contains；由 generate-hanization-translations.py 在文本汉化子阶段加载） |

## 2. 跨 type 公共阶段与依赖（skills/common/general-strategy-skill/scripts/）

以下路径相对 `skills/common/general-strategy-skill/scripts/`，仅列实际存在的脚本；文件存在不等于通过项目验收。

| 文件 | 职责 |
|---|---|
| `create-type-skill.py` | 创建新 type skill 草稿；默认预览，--apply 生成，--verify 静态校验 |
| `workflow/sub-stage-sniff.py` | M1：读取集中策略配置并识别 APK/XAPK 引擎 |
| `workflow/sub-stage-assess.py` | M2：评估项目难度并输出评估记录 |
| `workflow/sub-stage-final-check.py` | M3：检查交付产物 |
| `workflow/sub-stage-cleanup.py` | M4：按项目规则清理产物 |
| `workflow/sub-stage-static-analyze.py` | 01：公共静态分析 |
| `workflow/sub-stage-preprocess-build.py` | 02：预处理与工程构建 |
| `workflow/sub-stage-sdk-network-device-verify.py` | 04：SDK/网络修改后的设备验证（既有实现） |
| `workflow/sub-stage-xapk-merge.py` | M1 helper：合并 XAPK |
| `lib/device_verify_common.py` | 设备验证依赖库：ADB 调用、安装、启动及结果采集 |
| `lib/stage_runtime.py` | 公共运行库：项目路径、环境、release 构建/签名、证据和失败记录 |
| `lib/modification_plans.py` | 显式源码/Manifest 修改方案：哈希校验、预检与幂等写入 |
| `lib/localization.py` | 文本、字体和图片预检及替换（可编辑工程资源） |
| `lib/stage_device_verify.py` | 显式页面断言与参考图设备验证，绑定 release APK |
| `workflow/sub-stage-sdk-network-removal.py` | 03：执行 SDK/网络源码与 Manifest 修改方案并构建 |
| `workflow/sub-stage-revenue-forwarding.py` | 05：执行收益路径源码修改方案并构建 |
| `workflow/sub-stage-revenue-device-verify.py` | 06：验证收益目标页面/本地状态断言 |
| `workflow/sub-stage-ui-hide.py` | 07：执行功能入口源码/布局修改方案并构建 |
| `workflow/sub-stage-ui-hide-device-verify.py` | 08：验证目标入口消失及保留页面 |
| `workflow/sub-stage-font-replace.py` | 09：校验字体格式/目标字形，替换字体并构建 |
| `workflow/sub-stage-font-device-verify.py` | 10：按参考图验证字体渲染 |
| `workflow/sub-stage-text-hanization.py` | 11：校验占位符/标签并替换文本、构建 |
| `workflow/sub-stage-text-device-verify.py` | 12：验证目标文本或页面参考图 |
| `workflow/sub-stage-image-hanization.py` | 13：校验图片尺寸/格式/色彩，替换图片并构建 |
| `workflow/sub-stage-image-device-verify.py` | 14：按参考图验证目标图片页面 |
| `workflow/sub-stage-record-project-files.py` | 15：校验 release 一致性与签名，生成工程文件哈希清单和目录索引 |

公共路由表：`skills/common/general-strategy-skill/stages/sub-stage-register.yaml`。四个主阶段、当前 15 个子阶段及 XAPK helper 均保留声明。当前注册的公共阶段均有脚本入口；这不代表所有 type 的打包资源均可使用公共方案。 各 type 的实现仍优先；公共方案、输入边界与产物见该 skill 的 `scripts/stage-plans.md`。

包标识 `__init__.py` 与缓存不作为运行入口；`scripts/common/` 暂留旧引用兼容占位。旧 handler 基类、loader、PLAN_REGISTRY 及其方案文件当前不存在，不属于可用公共能力。详细缺口见本 skill 的 `scripts/README.md`。

## 3. 通用 skills（skills/common/）

### feature-removal-strategy-skill（去功能点）

| 脚本 | 角色 |
|---|---|
| `scripts/verify-feature-checklist.py` | YAML 清单 CRUD、文档同步与阶段数据消费回归验证 |
| `scripts/manage-feature-checklist.py` | YAML 清单增删改查与同步 Agent Markdown |
| `scripts/step-load-feature-checklist.py` | 统一 YAML 清单加载步骤（type 过滤、版本摘要、候选项） |
| `scripts/sync-feature-checklist-stages.py` | 接入各 type ui-hide 首步；同步注册表、委托适配器和子索引 |

各 type 的 `stages/ui-hide/default-action/step-load-feature-checklist.py` 是对应本地适配器：android、il2cpp、unity-mono、cocos2dx、cocos-creator、unreal、flutter、xamarin、air、defold、gamemaker、libgdx；全部委托上述共同步骤，不维护独立清单。

### general-strategy-skill（新 type 构建规范与公共阶段）

规范入口：`skills/common/general-strategy-skill/SKILL.md`；创建流程见同目录 `workflow.md`。实际脚本统一列于本表 §2，文件级说明和公共实现缺口见该 skill 的 `scripts/README.md`。

### third-party-removal-strategy-skill（第三方 SDK 移除）

| 清单管理脚本（scripts/） | 角色 |
|---|---|
| manage-sdk-registry.py | references 下 YAML 清单 CRUD，自动生成同名 MD；validate/sync-doc/--dry-run |
| verify-sdk-registry.py | 临时 YAML/MD 副本上的 CRUD、同步、兼容与无副作用验证 |

实际目录：skills/common/third-party-removal-strategy-skill/scripts/。

| 补充文件 | 角色 |
|---|---|
| load_sdk_removal_registry.py | 共享清单加载器 |
| workflow/lib/common.py | 旧 worker 的随附公共库，迁移保留；新工具使用统一 common |

| 脚本 | 角色 |
|------|------|
| `workflow/sub-stage-remove-sdks.py` | 第三方 SDK 移除（通用） |
| `workflow/sub-stage-remove-sdks-extra.py` | SDK 专项清理（RealmDefense 案例） |
| `workflow/sub-stage-stub-sdks.py` | SDK smali 桩化（策略 A） |
| `workflow/sub-stage-defold-manifest-clean.py` | Defold 引擎 manifest SDK 清理（保留 smali，防 JNI NoClassDefFoundError；BananaKong 案例） |
| `common/clean-android-manifest.py` | ElementTree 清理 Manifest 第三方组件（保留 Firebase 注册项） |
| `common/add-sdk-to-registry.py` | Agent 判定需移除的 SDK → 写入第三方SDK清单（third-party-sdk-removal-registry.yaml） |
| `common/stub-applovin-consent.py` | 移除 AppLovin MAX 隐私/同意弹窗（桩化 consent + CMP 方法） |
| `common/stub-sdk-methods.py` | 通用 SDK 入口方法桩化（C# 引用类时保留类，停副作用） |
| `common/remove-sdk-classes.py` | 物理删除 SDK 类 + 残留引用排查（直接类引用需桩化，字符串/反射引用仍需确认） |

## 4. 类型专用 skills（skills/strategy/）

### il2cpp-strategy-skill（阶段 01–15，）

> 路由表：`skills/strategy/il2cpp-strategy-skill/stages/sub-stage-register.yaml`（driver 唯一事实来源）
> `sub_stage > action > step`:
>   - 总调度器：`skills/strategy/il2cpp-strategy-skill/sub_stage-dispatcher.py`（`--stage N` / 全跑）
>   - 步骤基类：`skills/strategy/il2cpp-strategy-skill/scripts/step_base.py`
>   - 子阶段目录：`stages/<NN-name>/`，其内仅放执行方案目录 `<action>/`
>   - 各 action 目录：`dispatcher.py`(执行方案调度器) + `actions.yaml`(方案路由表) + `step_register.yaml`(步骤注册表) + `step_dispatcher.py`(步骤调度器) + `step-NN-*.py`(步骤脚本)
> il2cpp 在以下子阶段使用 type-specific 脚本（覆盖 common 默认）：02, 03, 04, 06, 07, 08, 09, 16
> 其余子阶段（01, 05, 10-15）复用 general-strategy-skill 的脚本
> **[FLOWFIX]** 原 11 个 il2cpp-skill 死代码副本已删除（详见 [REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md](../docs/REFACTOR-2026-08-11-il2cpp-deadcode-cleanup.md)）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-preprocess-build.py` | 02 | 预处理构建检测（apktool + FakerAndroid + toolchain + 编译测试） |
| `workflow/sub-stage-sdk-network-removal.py` | 03 | 去SDK + 去网络检测（15 步合并：原 10 步 SDK 移除 + 5 步网络检测桩化）⚠️成功→强制固化 |
| `workflow/sub-stage-ui-hide.py` | 07 | 去功能点（il2cpp UI 隐藏 + 区域裁剪） |
| `workflow/sub-stage-ui-hide-device-verify.py` | 08 | 去功能点真机验收 |
| `workflow/sub-stage-reward-video-forwarding.py` | 06 | 激励视频转发（showVideo callJava + native hook） |
| `workflow/sub-stage-reward-video-device-verify.py` | 07 | 激励视频真机验收 |
| `workflow/sub-stage-record-project-files.py` | 15 | 记录工程文件（crackings/<type>/<Name>/project/ 工程清单 + dir-index.yaml） |
| `workflow/sub-stage-hook-plan.py` | (03 helper) | hook-plan.yaml 生成（dump.cs 启发式匹配 IAP/Ad/Premium/Localization） | |
| `common/dump-cs-generator.py` | — | dump.cs → Frida JS + C++ 桩 |
| `common/analyze-hook-points.py` | — | il2cpp hook 点启发式分析 |
| `common/extract-fm-mono-dll.py` | — | FM 框架 .mdl → 解密 DLL 提取（frida） |
| `common/inject-smali-dex.py` | — | smali_classesN → classesN.dex 注入 APK（`--force` 重注入） |
| `skills/common/scripts/convert-dex-to-jar.py` | DEX/APK → JAR 转换（Java -cp 调用 dex2jar；修复了 dex-tools BASEDIR bug） | DEX/APK → JAR（供 Gradle 编译） |
| `common/rename-dollar-res.py` | — | `$` 前缀资源重命名 + 引用修复（AAPT2 编译门槛） |
| `common/patch-so-return-null.py` | — | 二进制 patch ELF .so 函数返回 null（Firebase Crashlytics SIGABRT 绕过） |
| `common/fix-dex-jar-frames.py` | — | ASM 重算 StackMapTable，修复 dex2jar 输出被 D8 拒收 |
| `common/patch-pairip-license.py` | — | ASM 置空 LicenseClient.checkLicense + 移除 Application.attachBaseContext（PairIP/Play Licensing 重签名绕过；覆盖 LicenseContentProvider 所有入口） |
| `common/sub-stage-pairip-verify.py` | — | PairIP 绕过后真机验收（PairIP=resigned 专用，label=PairIP绕过/启动验收） |
| `common/patch-pairip-smali-raw.py` | — | smali 层置空 checkLicense + attachBaseContext（patch 原始 raw smali 目录；APKTool 打包前用） |
| `common/check-pairip-in-apk.py` | — | 检查 APK 所有 DEX 是否已移除 PairIP 类/方法（PairIP patch 验证） |
| `common/fix-dex-new-instance.py` | — | ASM 修复 dex2jar `new Object` 误类型（无显式构造器类）→ 防真机 VerifyError |
| `common/generate-stable-ids.py` | — | apktool public.xml → stable_ids.txt（资源 ID 保真） |
| `common/inject-native-hook-loader.py` | — | 注入 native-lib 加载到真实 Application（解决 native hook 从未生效） |
| `common/fix-faker-android-invalid-data.py` | — | FakerAndroid 内置 apktool 2.4.0 "Invalid data detected" 兜底合并 |
| `common/detect-and-fix-invalid-data.py` | — | 检测 FakerAndroid "Invalid data detected" 问题并自动触发修复 |
| `common/fix-toolchain-standard.py` | — | 工具链标准化（AGP 7.4.2 / Gradle 7.5.1 / compileSdk 33 / buildTools 30.0.3） |
| `init-status-yaml.py` | — | 初始化项目 status.yaml（扫描 stages/ + APK 生成状态文件） |
| `common/clean-manifest-3rd-sdk.py` | — | ElementTree 清理 AndroidManifest 第三方 SDK 组件 |
| `common/generate-ui-hide-hooks.py` | — | 生成 UIElements 按钮隐藏 hook 代码（Update/触发方法两种模式） |
| `common/generate-ui-hide-region-hooks.py` | — | 生成 UIElements 区域容器隐藏 hook（树遍历+保留标记区域） |
| `common/frida-dump-uielements-tree.py` | — | Frida 从 rootElement 递归 dump UXML 树 |
| `common/frida-disable-gameobjects.py` | — | Frida 一次性 hook MenuManager.Update → GameObject.Find/SetActive(false) |
| `common/hide-menu-pages.py` | — | 静态隐藏 Unity NGUI UI：MenuPage tab + GameObject 按钮 |
| `common/hide-unity-gameobject.py` | — | 静态隐藏 Unity 场景 GameObject |
| `common/remove-logo-texture.py` | — | 静态替换 Unity Texture2D 为全透明 |
| `common/verify-il2cpp-rva.py` | — | 生成 Frida 脚本验证 libil2cpp RVA 是否函数入口 |
| `templates/native-lib.ad-removal.template.cpp` | — | il2cpp 广告移除 hook 模板 |
| `templates/native-lib.iap.template.cpp` | — | il2cpp IAP 内购模拟模板 |
| `skills/common/scripts/template-files/il2cpp/native-lib.template.cpp` | — | **il2cpp 标准 native hook 入口模板**（A64HookFunction + callJava + installNativeHooks + 空 setupHooks 骨架）。[FLOWFIX] 覆盖 FakerAndroid fakeCpp 模式（RVA 偏移错误 → SIGSEGV） |
| `common/collect-localization-strings.py` | — | Frida 收集 Unity Localization 字符串 |
| `common/generate-hanization-map.py` | — | translations.json → hanization_map.h（native hook 汉化表） |
| `common/replace-game-font.py` | — | 静态替换 Unity 内嵌字体（⚠️ 实测崩溃，仅记录失败路径） |
| `common/hanize-unity-texts.py` | — | 场景 MonoBehaviour m_Text 汉化（⚠️ 实测崩溃） |
| `common/hanize-unity-texts-safe.py` | — | 场景 MB m_Text 安全汉化（字节级替换） |
| `common/assetstudio-haniz/` | — | AssetStudio 汉化辅助（C# 工具） |
| `common/assets-tools-haniz/` | — | **完整汉化部署工具**（C#，AssetsTools.NET） |
| `common/extract-mb-strings.py` | — | 提取 data.unity3d MonoBehaviour 字符串 → translations.json 种子 |
| `common/metadata-patcher.py` | — | **方案A核心**：global-metadata.dat 字符串字面量提取/回写（il2cpp-stringliteral-patcher 算法自实现，MIT） |
| `lib/stage_common.py` | — | 阶段公共工具（ADB/Gradle/路径/进度/日志/`append_experience_sync_task` 强制固化待办） |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考（必须去除按钮 + NGUI 三方案 + 语言规则 + 真机验收项） |

### air-strategy-skill（Adobe AIR）

> 路由表：`skills/strategy/air-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：01（sub-stage-air-static-analyze）、10（sub-stage-air-fonts）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-air-static-analyze.py` | 01 | AIR 静态分析（SWF 反编译 + ffdec） |
| `workflow/sub-stage-air-fonts.py` | 10 | AIR 字体处理（SWF 内嵌 + assets/fonts/） |
| `common/extract-swf-text.py` | — | SWF 文本提取 |
| `common/filter-swf-strings.py` | — | SWF 字符串过滤 → 翻译 TSV |
| `common/inject-as-text.py` | — | AS 文本注入 |
| `common/patch-swf-translations.py` | — | SWF 翻译 patch |
| `common/verify-swf-text.py` | — | SWF 文本验证 |
| `common/swf-gui-edit.py` / `common/swf-xml-edit.py` | — | SWF GUI / XML 编辑 |
| `common/install-ffdec.py` / `common/install-swfmill.py` | — | 工具安装（ffdec / swfmill） |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

### cocos2dx-strategy-skill

> 路由表：`skills/strategy/cocos2dx-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：01（sub-stage-cocos-static-analyze）、03（sub-stage-cocos-lua-extract）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-cocos-static-analyze.py` | 01 | Cocos2d-x 静态分析 |
| `workflow/sub-stage-cocos-lua-extract.py` | 03 | Cocos2d-x Lua 脚本提取 |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |
| `lsposed-config.py` | — | LSPosed 模块作用域配置 |
| `frida-cocos-text-capture.py` | — | Cocos2d-x 运行时文本捕获 |
| `lsposed-hook-scaffold/` | — | LSPosed hook 模块脚手架 |

### cocos-creator-strategy-skill

> 路由表：`skills/strategy/cocos-creator-strategy-skill/stages/sub-stage-register.yaml`

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `scripts/common/decrypt-jsc-assets.py` | — | 批量解密 Cocos Creator JSC 资产（APK → 明文 JS） |
| `scripts/common/repack-jsc-assets.py` | — | 重打包 JSC 资产进 APK（JS → 加密 JSC + 签名） |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

### flutter-strategy-skill

> 路由表：`skills/strategy/flutter-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：01（sub-stage-flutter-static-analyze）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-flutter-static-analyze.py` | 01 | Flutter 静态分析 |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

### unity-mono-strategy-skill

> 路由表：`skills/strategy/unity-mono-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：01（sub-stage-mono-static-analyze）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-mono-static-analyze.py` | 01 | Unity Mono 静态分析（ILSpy / dnSpy） |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

### unreal-strategy-skill

> 路由表：`skills/strategy/unreal-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：01（sub-stage-unreal-static-analyze）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-unreal-static-analyze.py` | 01 | Unreal 静态分析 |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

### xamarin-strategy-skill

> 路由表：`skills/strategy/xamarin-strategy-skill/stages/sub-stage-register.yaml`
> 复用 unity-mono 的 01 静态分析（mono 运行时）

| 脚本 | 角色 |
|------|------|
| `../feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考 |

### android-strategy-skill（纯 Java/Kotlin 兜底）

> 路由表：`skills/strategy/android-strategy-skill/stages/sub-stage-register.yaml`
> 全部子阶段复用 general-strategy-skill 通用骨架（无 type-specific 覆盖；无 JNI 桥接）

| 脚本 | 角色 |
|------|------|
| `../feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考 |

### defold-strategy-skill（Defold 引擎）

> 路由表：`skills/strategy/defold-strategy-skill/stages/sub-stage-register.yaml`
> 06 复用 third-party-removal-skill/sub-stage-defold-manifest-clean.py

| 脚本 | 角色 |
|------|------|
| `common/build-defold-hook-native-lib.py` | 编译 Defold SDK hook native-lib.so |
| `common/inject-defold-hook.py` | 注入 hook（拷贝 .so + DefoldActivity.onCreate 注入 loadLibrary） |
| `assets/native-lib.sdk-hook.template.cpp` | Defold SDK hook 模板 |
| `../feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考 |
| （复用跨 type 阶段脚本；Defold 专用 manifest 清理见 third-party-removal-strategy-skill `sub-stage-defold-manifest-clean.py`） | — |

### gamemaker-strategy-skill（GameMaker Studio 引擎）

> 路由表：`skills/strategy/gamemaker-strategy-skill/stages/sub-stage-register.yaml`
> 跳过 13-25（GML 编译加密，无法静态 patch UI）

| 脚本 | 角色 |
|------|------|
| `common/setup-output-project.py` | 搭 AS 工程化骨架 |
| `workflow/remove-gamemaker-buttons.py` | 移除 GameMaker 按钮/对象实例 |
| `workflow/inspect-gamemaker-rooms.py` | 检查 GameMaker .droid 结构 |
| `SKILL.md / strategy.md / workflow.md / tools-index.md` | 识别特征/工具链/坑位 |
| （复用跨 type 阶段脚本；GameMaker 专用 manifest 清理见 third-party-removal-strategy-skill `sub-stage-defold-manifest-clean.py`） | — |

### libgdx-strategy-skill（libGDX 引擎）

> 路由表：`skills/strategy/libgdx-strategy-skill/stages/sub-stage-register.yaml`
> type-specific 覆盖：06（sub-stage-libgdx-cleanup）

| 脚本 | 子阶段 | 角色 |
|------|--------|------|
| `workflow/sub-stage-libgdx-cleanup.py` | 06 | libGDX SDK 清理（manifest + .so + FB/Firebase/ThinkingData 桩化链；首个项目 JungleMarbleBlast 2026-08-06） |
| `assets/frida-hook-assets.js` | — | Frida hook AssetManager.open 探测游戏运行时资源加载 |
| `assets/frida-hook-font.js` | — | Frida hook Typeface.createFromAsset 探测字体文件名 |
| `../feature-removal-strategy-skill/SKILL.md` | — | 去功能点统一参考 |

## 5. HA4T 自动化验收脚本（计划中）

> 以下脚本基于 [HA4T](https://github.com/exuils/HA4T) UI 自动化框架，用于真机验收阶段的自动化验证。
> 文档详见 `tools/crack-intergration-tools/docs/ha4t/07_workflow_integration.md`。

| 脚本 | 角色 | 状态 |
|------|------|------|
| `ha4t-verify.py` | 真机验收自动化（启动/等待/截图/OCR） | ✅ 已创建 |
| `ha4t-hanization-verify.py` | 汉化效果验证（OCR 中文识别 + 截图存档） | 📋 计划中 |
| `ha4t-network-verify.py` | 网络检测移除验证（飞行模式下启动测试） | 📋 计划中 |

## 6. Swipium QA 测试脚本（计划中）

> 以下脚本基于 [Swipium](https://github.com/GeroPalombo/swipium) MCP server，用于 AI 代理驱动的 QA 测试。
> 文档详见 `tools/crack-intergration-tools/docs/swipium/07_workflow_integration.md`。

| 脚本 | 角色 | 状态 |
|------|------|------|
| `swipium-verify.py` | Swipium QA 测试（冒烟/探索/报告） | ✅ 已创建 |
| `swipium-smoke.py` | 冒烟测试自动化 | 📋 计划中 |
| `swipium-explore.py` | 探索性测试 + 应用图谱 | 📋 计划中 |

## 6.5 Android 12+ Oplus / Realme 设备闪退修复

> 这些脚本解决 Unity 6 + il2cpp 游戏在 Realme Android 14 上启动 6-8 秒必闪退的问题。
> 由 [FLOWFIX 2026-08-18] 在 CrowdCity 项目上验证：清掉 Crashlytics/Firebase 早期 init + 加 BuildConfig stub + 装哑 UncaughtExceptionHandler + 加底部随机提示 banner。

| 脚本 | 角色 | 状态 |
|------|------|------|
| `add-random-tip-banner.py` | 给已构建的项目加底部随机提示 banner（覆盖系统手势条白条） | ✅ 已创建 |
| `patch-firebase-realme-fix.py` | Realme Android 14 闪退一键止血包（删早期 .so + 生成 BuildConfig stub + 装哑 handler） | ✅ 已创建 |
| `load_sdk_removal_registry.py` | 集中加载第三方 SDK 移除清单 YAML（4 个下游脚本共用；落点 `skills/common/third-party-removal-strategy-skill/scripts/`，所有 type-strategy-skill 公共） | ✅ 已创建 |
| `frida-recon-gameobjects.py` | frida 侦察游戏对象名（只读不改） | ✅ 已创建 |

调用方式（用户说"应用"时执行）:

```bash
source tools/environments/env.sh
python3 skills/strategy/il2cpp-strategy-skill/scripts/common/add-random-tip-banner.py <Name> --type <type>
```

## 7. 自动化汉化收集脚本

> 以下脚本使用无障碍服务 + OCR 自动收集游戏中的非中文内容。
> 原理：无障碍服务获取原生 UI 文本，OCR 获取游戏渲染的文本。

| 脚本 | 角色 | 状态 |
|------|------|------|
| `collect-non-chinese.py` | 收集非中文内容（无障碍 + OCR） | ✅ 已创建 |
| `auto-hanization-test.py` | 自动化汉化测试完整流程 | ✅ 已创建 |

---

## 维护规则

- **创建前分类**：声明用途和归属；仓库维护脚本不放入逆向运行目录，不登记本表、skill 子索引或逆向工具表。
- **新增逆向项目脚本**：在对应目录落位后登记脚本名与角色，并同步 skill 的 `scripts/README.md`；阶段、方案或步骤变化时同步实际使用的注册表。
- **逆向脚本移动/重命名/删除**：同步本表、对应子索引和调用路径。
- **索引清理**：移除仓库维护条目；不得因为名称含 `verify`、`init` 或 `setup` 就移除逆向验收、项目记录或工具链脚本。
- **查找范围**：逆向项目脚本先查本表（AGENTS.md §1.9）；维护脚本按 §1.3 查找，不受本表登记约束。

## 相关文档

- [AGENTS.md §1.9 脚本索引查询](../../../AGENTS.md)
- [skills/common/scripts/README.md](./README.md) — 主驱动器 + 策略引擎说明
- `docs/REFACTOR-2026-08-11-sub-stage-routing.md` — 子阶段路由表重构说明
- `skills/strategy/il2cpp-strategy-skill/stages/sub-stage-register.yaml` — il2cpp 子阶段注册表
- `skills/common/general-strategy-skill/stages/sub-stage-register.yaml` — 通用骨架子阶段路由表
- `skills/strategy/il2cpp-strategy-skill/scripts/README.md` — il2cpp 脚本子索引
