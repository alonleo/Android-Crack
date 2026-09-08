# Android Workflow — 普通 Java/Kotlin 阶段流程

> 本文件是 android-strategy-skill 的"流程操作手册"。
>
> 加载顺序：strategy.md → **[workflow.md（本文件）]** → tools-index.md
>
> **Android type 无 type-specific 子阶段脚本**，全部复用 general-strategy-skill 的通用脚本。

---

## 1. 头部引用

| 文档 | 路径 | 用途 |
|------|------|------|
| strategy.md | `./strategy.md` | 类型策略总览 |
| **workflow.md** | `./workflow.md`（本文件） | 阶段操作手册 |
| tools-index.md | `./tools-index.md` | 工具索引 |
| EXPERIENCES.md | `../../../EXPERIENCES.md` | 通用逆向经验 |
| 通用骨架 | `skills/common/general-strategy-skill/workflow.md` | 通用阶段骨架 |
| 通用脚本 | `skills/common/general-strategy-skill/stages/sub-stage-register.yaml` | 通用默认脚本路径（各 type 的 register 驱动: `skills/strategy/<type>-strategy-skill/stages/sub-stage-register.yaml` + `sub_stage-dispatcher.py`） |
| 主流程 | `../../../WORKFLOW.md` | 主阶段与子阶段流程 |

---

## 2. 子阶段路由速查表（01–15）

| 阶段 | 名称 | 脚本来源 | 真实覆盖 | 说明 |
|------|------|----------|----------|------|
| 01 | static-analyze | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py` | ✅ common | 通用静态分析 |
| 02 | preprocess-build | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py` | ✅ common | 预处理构建 |
| 03 | sdk-network-removal | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-removal.py` | ✅ common | 去SDK + 去网络检测 |
| 04 | sdk-network-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-device-verify.py` | ✅ common | 真机验收（SDK+网络） |
| 05 | revenue-forwarding | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py` | ✅ common | 激励 + IAP 转发 |
| 06 | revenue-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py` | ✅ common | 真机验收（激励+IAP） |
| 07 | ui-hide | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py` | ✅ common | 去功能点 |
| 08 | ui-hide-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py` | ✅ common | 真机验收（去功能点） |
| 09 | font-replace | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py` | ✅ common | 字体替换 |
| 10 | font-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py` | ✅ common | 真机验收（字体） |
| 11 | text-hanization | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py` | ✅ common | 文本汉化 |
| 12 | text-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-device-verify.py` | ✅ common | 真机验收（文本） |
| 13 | image-hanization | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py` | ✅ common | 图片汉化 |
| 14 | image-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py` | ✅ common | 真机验收（图片） |
| 15 | record-project-files | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py` | ✅ common | 记录工程文件 |

> **Android type 全部复用 common，无 type-specific 脚本。** 如需查看某阶段详细步骤，参阅
> `skills/common/general-strategy-skill/workflow.md` 或直接查看对应脚本。

---

## 3. 阶段详细流程（01–15）

### 阶段 01 — static-analyze

**目标**：jadx 反编译 Java 层，扫描第三方 SDK，定位入口点。

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py <apk-path>
```

**步骤**：

| 步骤 | 操作 | 命令/动作 |
|------|------|----------|
| 1 | jadx 反编译 | `jadx -d sources/ --no-res --threads-count 8 <apk>` |
| 2 | smali 导出 | apktool 解包后保留 smali 目录 |
| 3 | SDK 扫描 | 扫描 `sources/` 中第三方 SDK 包名 |
| 4 | 入口定位 | 识别 Application / MainActivity / ContentProvider |

**验证命令**：
```bash
# 验证 sources/ 存在且含 Java 文件
[ -d "crackings/android/<Name>/raw/03-jadx/sources/" ] && \
  find "crackings/android/<Name>/raw/03-jadx/sources/" -name "*.java" | head -5
```

**注意项**：
- jadx 内存消耗大，建议 `JAVA_OPTS="-Xmx8g"`
- 部分 APK 有 multiple dex，需确认主 dex 入口

---

### 阶段 02 — preprocess-build

**目标**：apktool 解包 → 整理 AS 项目 → 注入模板文件 → 工具链规范 → ProGuard → 签名 → 编译测试。

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py <apk-path>
```

**步骤**：

| 步骤 | 操作 | 命令/动作 |
|------|------|----------|
| 1 | 环境初始化 | 加载 env.sh → 解析 APK 路径/名称 → 创建 crackings/output-projects 目录 |
| 2 | 计算 MD5 | `md5sum source.apk → source.apk.md5` |
| 3 | apktool 解包 | `apktool d <apk> -o raw/01-apktool/`，自动修复 split 配置 |
| 4 | 清理 res/values/ | 只保留 strings.xml，删除 strings-*.xml |
| 5 | Android 资源修复 | 修复 `$` 文件名 / v31 / 损坏 vector/selector / 空 intent |
| 6 | AndroidManifest 修复 | 修复 package 属性 / splits / Android 13+ 属性 / 空 intent |
| 7 | build.gradle namespace 注入 | 动态提取包名 → 写入 namespace |
| 6 | 模板集成 | MainActivity/JniBridge/App/SDKUtils/native-lib/And64InlineHook/CMakeLists |
| 7 | smali → jar | smali 目录编译为 `classes.all.dex.jar` |
| 6 | 编译测试 | `./gradlew assembleRelease` → 安装 → 启动 → 5s 无 FATAL |

**关键产物**：
```
crackings/<type>/<Name>/
├── source.apk.md5
├── raw/01-apktool/{AndroidManifest.xml,apktool.yml,smali/}
crackings/<type>/<Name>/project/
├── {settings.gradle,app/build.gradle,gradle/wrapper/}
├── app/src/main/smali/（保留原 smali，不转 dex）
├── app/src/main/java/com/android/boot/{MainActivity.java,JniBridge.java,App.java}
└── app/src/main/AndroidManifest.xml（入口已替换）
```

**验证命令**：
```bash
# 基础产物验证
[ -f "crackings/android/<Name>/source.apk.md5" ] && \
[ -f "crackings/android/<Name>/raw/01-apktool/AndroidManifest.xml" ] && \
[ -d "crackings/android/<Name>/raw/01-apktool/smali/" ] && \
echo "BASIC CHECK PASS"

# 编译验证
cd crackings/android/<Name>/project/app && ./gradlew assembleRelease
# 期望：BUILD SUCCESSFUL，退出码 0
```

**注意项**：
- split APK 必须先合并（调用 sub-stage-xapk-merge.py）
- ProGuard 必须 keep androidx.* / com.android.boot.* / 原 Application 类 / 原入口 Activity
- 签名信息生成 my.keystore.jks（alias jy, dname CN=jky）

---

### 阶段 03 — sdk-network-removal

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# Manifest SDK 关键字 = 0
grep -c "admob\|facebook\|unity.*ads\|mobius\|chartboost" \
  crackings/android/<Name>/raw/01-apktool/AndroidManifest.xml
# 期望：0

# gradlew 构建成功
cd crackings/android/<Name>/project/app && ./gradlew assembleRelease
echo $?
# 期望：0
```

**注意项**：
- 成功 → **强制固化**（按 AGENTS.md §1.6 任务后固化）
- .so 清理时必须保留引擎 .so（libunity.so / libapp.so 等）

---

### 阶段 04 — sdk-network-device-verify

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# 查找验证报告
ls crackings/android/<Name>/stages/04-sdk-network-device-verify/
# 期望：verify-report.md + screenshot.png
```

**注意项**：成功 → **强制固化**

---

### 阶段 04b — network-detection（并入 sdk-network-removal）

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# network-detection.yaml 存在且桩化方法数 ≥ 1
[ -f "crackings/android/<Name>/stages/03-sdk-network-removal/network-detection.yaml" ]
grep -c "stub\|hook" "crackings/android/<Name>/stages/03-sdk-network-removal/network-detection.yaml"
# 期望：≥ 1
```

**注意项**：成功 → **强制固化**

---

### 阶段 05b — airplane-mode（并入 sdk-network-device-verify）

实现要点见 [去第三方 SDK：android](../../common/third-party-removal-strategy-skill/references/engine-notes.md#android)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# 期望：verify-report.md + screenshot.png
```

**注意项**：成功 → **强制固化**

---

### 阶段 05 — revenue-forwarding

**目标**：showVideo callJava + native hook。

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk-path>
```

**步骤**：

| 步骤 | 操作 | 命令/动作 |
|------|------|----------|
| 1 | 信息收集 | 从 smali/step1-signatures 收集激励视频方法 → `reward-video-detection.yaml` |
| 2 | 策略选择 | smali 类型 → smali patch（方法体替换为 callJava）|
| 3 | hook 注册 | Android Inline Hook（lib 目录）|
| 4 | 调用链检查 | MainActivity → SDKUtils.showRewardVideo() |
| 5 | 报告生成 | `reward-video-report.yaml` |
| 6 | smali→jar | → `app/javaScaffoding/classes.all.dex.jar` |
| 7 | gradlew 构建 | `./gradlew assembleRelease` |

**验证命令**：
```bash
# callJava(showVideo) ≥ 1
grep -c 'callJava.*showVideo\|showRewardVideo' \
  crackings/android/<Name>/project/app/app/src/main/java/com/android/boot/MainActivity.java
# 期望：≥ 1
```

**注意项**：成功 → **强制固化**

---

### 阶段 06 — revenue-device-verify

**目标**：验证激励视频转发正常工作。

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py
```

**验收标准**：`adb logcat [xNative] showVideo` 命中 + 进程存活 30s + 无 native crash

**注意项**：成功 → **强制固化**

---

### 阶段 06b — iap（并入 revenue-forwarding）

**目标**：processPurchase callJava + premiumUnlock callJava + native hook。

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk-path>
```

**验证命令**：
```bash
grep -c 'callJava.*processPurchase\|callJava.*premiumUnlock' \
  crackings/android/<Name>/project/app/app/src/main/java/com/android/boot/MainActivity.java
# 期望：≥ 2
```

**注意项**：成功 → **强制固化**

---

### 阶段 07b — iap-verify（并入 revenue-device-verify）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**验收标准**：logcat `processPurchase` 命中 + Premium 解锁 Toast 命中 + 30s 存活 + 无 native crash

**注意项**：成功 → **强制固化**

---

### 阶段 07 — ui-hide

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py`

实现要点见 [去功能点：android](../../common/feature-removal-strategy-skill/references/engine-notes.md#android)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

### 阶段 08 — ui-hide-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py`

实现要点见 [去功能点：android](../../common/feature-removal-strategy-skill/references/engine-notes.md#android)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

## 汉化阶段（10–15）

通用的汉化对象分类、质量边界与风险判断见[通用汉化策略](../../common/hanization-strategy-skill/SKILL.md)。实际执行、脚本选择和验收以本 workflow 及 `stages/sub-stage-register.yaml` 为准。

### 阶段 09 — font-replace

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py <apk-path>
```

**register 产物契约**：`crackings/<type>/<Name>/project/app/app/src/main/res/font/notosanssc.ttf`。

**Android 差异**：字体须作为 Android `res/font/` 资源参与应用构建，并由当前 Android 资源引用链加载。

---

### 阶段 10 — font-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py`

**register 产物契约**：`crackings/<type>/<Name>/stages/13-font-device-verify/verify-screenshot.png`。

**Android 额外验收**：确认 Android 资源打包后的字体可由实际资源引用加载；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 11 — text-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py <apk-path>
```

**模式**：interactive。

**register 产物契约**：`crackings/<type>/<Name>/stages/14-text-hanization/{strings-collected.json,translations.json}`。

**Android 差异**：优先处理 Android 资源字符串及其构建时资源引用；任何 native 映射仅在当前项目实际使用该路径时处理。

---

### 阶段 12 — text-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-device-verify.py`

**register 产物契约**：`crackings/<type>/<Name>/stages/15-text-device-verify/verify-screenshot.png`。

**Android 额外验收**：确认 release 包中的 Android 资源引用仍解析到已汉化条目；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 13 — image-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py <apk-path>
```

**模式**：interactive。

**register 产物契约**：`crackings/<type>/<Name>/stages/16-image-hanization/{replacements/,images-manifest.yaml}`。

**Android 差异**：替换项须保持 Android drawable 资源可被 aapt/Gradle 打包并由既有资源 ID 解析。

---

### 阶段 14 — image-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py`

**register 产物契约**：`crackings/<type>/<Name>/stages/17-image-device-verify/verify-screenshot.png`。

**Android 额外验收**：确认 release 包实际加载替换后的 drawable 资源；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 15 — record-project-files

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py
```

**验证命令**：
```bash
[ -f "crackings/android/<Name>/dir-index.yaml" ]
[ -f "crackings/android/<Name>/output-project-manifest.yaml" ]
```

---

## 4. 强制固化规则

以下阶段成功后**必须**执行任务后固化（AGENTS.md §1.6）：

| 阶段 | 触发条件 | 固化内容 |
|------|----------|----------|
| 04 sdk-network-device-verify | 验收通过 | SDK 移除经验（3rd-party-libs 保留策略）+ 网络检测去除经验 |
| 06 revenue-device-verify | 验收通过 | 激励视频转发经验 + IAP 转发经验 |
| 08 ui-hide-device-verify | 验收通过 | 去功能点经验 |
| 10 font-device-verify | 验收通过 | 字体替换经验 |
| 12 text-device-verify | 验收通过 | 文本汉化经验 |
| 14 image-device-verify | 验收通过 | 图片汉化经验 |

固化方式：在 `EXPERIENCES.md` 中新增条目，记录当时的 hook-plan.yaml / hide-plan.yaml 关键参数。

---

## 5. 常见失败模式

| 失败 | 原因 | 回退 |
|------|------|------|
| apktool 解包失败 | APK 损坏 / 加固 | 用 `unzip -l <apk>` 验证；加固则先脱壳 |
| jadx 反编译崩溃 | 内存不足 | `JAVA_OPTS="-Xmx8g"`；拆开多次反编译 |
| `apktool b` 资源编译错误 | AndResGuard / 删除资源未同步清理 public.xml | 恢复 public.xml；用 `aapt2 dump resources` 校对 |
| `apksigner verify` v2 失败 | 未 zipalign | 强制顺序：apktool b → zipalign → apksigner |
| 启动 ClassNotFoundException | 删除 SDK 过深 | 回退到策略 A（桩化），保留 stub 类 |
| 图片汉化后崩溃 | 图片格式/尺寸不匹配 | 使用相同格式和尺寸的图片 |
| 字体替换后崩溃 | 字体文件损坏/格式不兼容 | 使用标准 TTF 字体 |
| SDK移除后卡加载 | 网络检测未桩化 | 桩化网络检测方法 |
| gradlew assembleRelease 失败 | smali 语法错误 / 缺失类 | 检查 smali 目录完整性，对照原始 dex |
| hook-plan.yaml 候选不足 | 函数名混淆 | 扩大扫描范围或手动分析 .so 字符串 |

---

## 6. 主阶段（sniff / assess / final-check / cleanup）

### M1 — 类型嗅探（sniff）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk-path>
```

**产物**：`crackings/android/<Name>/findings.md`

**验证命令**：
```bash
grep "TYPE\|SUBTYPE" crackings/android/<Name>/findings.md
# 期望：TYPE=Android SUBTYPE=java-kotlin
```

---

### M2 — 难度评估（assess）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py <apk-path>
```

**产物**：`crackings/android/<Name>/difficulty.json`

**验证命令**：
```bash
cat crackings/android/<Name>/difficulty.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('grade','MISSING'))"
# 期望：S / A / B / C / D / F（非空）
```

---

### M3 — 最终验收（final-check）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py
```

**产物**：`crackings/android/<Name>/stages/23-final-check/final-report.md`

**验收标准**（OBJECTIVES.md §1 六条硬指标）：
1. §1.1 可运行：编译通过 + 安装成功 + 启动无 FATAL
2. §1.2 汉化：OCR 命中中文 + 字体加载正常
3. §1.3 移除第三方插件：Manifest 无 SDK 关键字
4. §1.4 自定义重签名：v1 + v2 + v3 三签通过
5. 网络检测去除：飞行模式可启动
6. 激励视频/IAP 转发：按需（可选）

---

### M4 — 清理临时空间（cleanup）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py
```

**保留产物**：
```
crackings/<type>/<Name>/project/
├── app/
├── patched.apk
├── my.keystore.jks → symlink
├── gradle/
├── *.gradle*
└── settings.gradle*
```

**删除内容**：crackings/ 下中间产物（jadx/smali/apktool 临时目录等）

---

## 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../../EXPERIENCES.md) — 通用逆向经验
- [`skills/common/general-strategy-skill/workflow.md`](../../common/general-strategy-skill/workflow.md) — 通用阶段骨架
- [`skills/common/general-strategy-skill/stages/sub-stage-register.yaml`](../../common/general-strategy-skill/stages/sub-stage-register.yaml) — 通用 01–15 路由定义
- [experiences.md](./experiences.md) — 本 type 私有逆向经验
- [WORKFLOW.md](../../../WORKFLOW.md) — 主阶段与子阶段流程
- [../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单
