# Adobe AIR Workflow — 阶段流程操作手册

> 本文件是 air-strategy-skill 的"流程操作手册"。
>
> 加载顺序：strategy.md → **[workflow.md（本文件）]** → tools-index.md

---

## 1. 头部引用

| 文档 | 路径 | 用途 |
|------|------|------|
| strategy.md | `./strategy.md` | 类型策略总览 |
| **workflow.md** | `./workflow.md`（本文件） | 阶段操作手册 |
| tools-index.md | `./tools-index.md` | 工具索引 |
| EXPERIENCES.md | `../../../EXPERIENCES.md` | 通用逆向经验 |
| 通用骨架 | `skills/common/general-strategy-skill/workflow.md` | 通用阶段骨架 |
| 通用脚本 | `skills/common/general-strategy-skill/stages/sub-stage-register.yaml` | 通用 01–15 路由定义 |
| 主流程 | `../../../WORKFLOW.md` | 主阶段与子阶段流程 |

---

## 2. 子阶段路由速查表（01–15）

| 阶段 | 名称 | 脚本来源 | 真实覆盖 | 说明 |
|------|------|----------|----------|------|
| 01 | static-analyze | `skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-static-analyze.py` | ✅ **type-specific** | 通用静态分析 |
| 02 | preprocess-build | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py` | ✅ common | 预处理构建 |
| 03 | sdk-network-removal | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-removal.py` | ✅ common | 去SDK + 去网络检测 |
| 04 | sdk-network-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-device-verify.py` | ✅ common | 真机验收（SDK+网络） |
| 05 | revenue-forwarding | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py` | ✅ common | 激励 + IAP 转发 |
| 06 | revenue-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py` | ✅ common | 真机验收（激励+IAP） |
| 07 | ui-hide | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py` | ✅ common | 去功能点 |
| 08 | ui-hide-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py` | ✅ common | 真机验收（去功能点） |
| 09 | font-replace | `skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-fonts.py` | ✅ **type-specific** | 字体替换 |
| 10 | font-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py` | ✅ common | 真机验收（字体） |
| 11 | text-hanization | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py` | ✅ common | 文本汉化 |
| 12 | text-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-device-verify.py` | ✅ common | 真机验收（文本） |
| 13 | image-hanization | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py` | ✅ common | 图片汉化 |
| 14 | image-device-verify | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py` | ✅ common | 真机验收（图片） |
| 15 | record-project-files | `skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py` | ✅ common | 记录工程文件 |

> **type-specific 脚本（> 2000B，真实覆盖）**：
> - `sub-stage-air-static-analyze.py`（2707B，82L）：jadx + SWF 提取 + AIR application.xml
> - `sub-stage-air-fonts.py`（3224B，84L）：SWF 嵌入字体分析 + 字体子集化

---

## 3. 阶段详细流程（01–15）

### 阶段 01 — static-analyze ⭐ type-specific

**目标**：jadx 反编译 Java 容器层 + 提取 SWF 文件 + 提取 AIR 应用描述符。

**脚本**：`skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-static-analyze.py`

**调用**：
```bash
python3 skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-static-analyze.py <apk-path>
```

**步骤**：

| 步骤 | 操作 | 命令/动作 |
|------|------|----------|
| 1 | jadx 反编译 | `jadx -d raw/02-jadx/sources/ --no-res --threads-count 8 <apk>` |
| 2 | 提取 SWF 文件 | 遍历 APK zip，提取所有 `.swf` 文件到 `raw/03-swf/` |
| 3 | 提取 application.xml | 从 `META-INF/AIR/application.xml` 或 `assets/META-INF/AIR/application.xml` 提取 AIR 应用描述符到 `raw/03-air-application.xml` |

**关键产物**：
```
crackings/<type>/<Name>/raw/
├── 02-jadx/sources/           # Java 源码
├── 03-swf/                    # 提取的 SWF 文件（*.swf）
└── 03-air-application.xml     # AIR 应用描述符
```

**验证命令**：
```bash
# SWF 文件数量
ls crackings/<type>/<Name>/raw/03-swf/*.swf 2>/dev/null | wc -l
# 期望：≥ 1（如 APK 包含 SWF）

# application.xml 存在
[ -f "crackings/<type>/<Name>/raw/03-air-application.xml" ]

# jadx sources 存在
[ -d "crackings/<type>/<Name>/raw/02-jadx/sources/" ]
find "crackings/<type>/<Name>/raw/02-jadx/sources/" -name "*.java" | head -3
```

**注意项**：
- 并非所有 AIR APK 都包含 `.swf`（部分纯 AOT 编译），未找到 SWF 不等于失败
- ffdec 反编译 SWF 需要单独步骤（按静态分析阶段的资产分析需求执行）
- AIR application.xml 包含重要元数据：`id`、`version`、`initialWindow`、嵌入的 ANE 扩展列表

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
| 1 | 环境初始化 | 加载 env.sh → 解析 APK 路径/名称 → 创建 crackings/<type>/<Name>/project 目录 |
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
├── app/src/main/smali/
├── app/src/main/java/com/android/boot/{MainActivity.java,JniBridge.java,App.java}
└── my.keystore.jks
```

**验证命令**：
```bash
# 编译验证
cd crackings/<type>/<Name>/project/app && ./gradlew assembleRelease
echo $?
# 期望：0
```

**注意项**：
- AIR APK 的 assets/ 下有 main.swf，重打包时不要遗漏
- AIR runtime 依赖 `libAdobeAIR.so`（在 apktool 解包后的 lib/ 目录），删除会导致闪退

---

### 阶段 03 — sdk-network-removal

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# 期望：0
./gradlew assembleRelease; echo $?
# 期望：0
```

**注意项**：AIR 游戏的 SDK 通常嵌入在 ANE（Adobe Native Extension）中，移除 ANE 时需同步修改 `application.xml` 中的 `extensions` 列表。成功 → **强制固化**

---

### 阶段 04 — sdk-network-device-verify

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 04b — network-detection（并入 sdk-network-removal）

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 05b — airplane-mode（并入 sdk-network-device-verify）

实现要点见 [去第三方 SDK：air](../../common/third-party-removal-strategy-skill/references/engine-notes.md#air)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 05 — revenue-forwarding

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**AIR 特定说明**：.so 类型引擎，使用 Android_Inline_Hook_ARM64，注入 `Hooked_*` + `callJava("showRewardVideo")`

**验证命令**：
```bash
grep -c 'callJava.*showVideo\|Hooked' \
  crackings/<type>/<Name>/project/app/app/src/main/cpp/native-lib.cpp
# 期望：≥ 1
```

---

### 阶段 06 — revenue-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**注意项**：成功 → **强制固化**

---

### 阶段 06b — iap（并入 revenue-forwarding）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**AIR 特定说明**：AIR IAP 通常通过 ANE 调用（`ExtensionContext`），需同时修改 ANE 配置和 native hook

---

### 阶段 07b — iap-verify（并入 revenue-device-verify）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**注意项**：成功 → **强制固化**

---

### 阶段 07 — ui-hide

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py`

实现要点见 [去功能点：air](../../common/feature-removal-strategy-skill/references/engine-notes.md#air)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

### 阶段 08 — ui-hide-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py`

实现要点见 [去功能点：air](../../common/feature-removal-strategy-skill/references/engine-notes.md#air)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

## 汉化阶段（10–15）

通用的汉化对象分类、质量边界与风险判断见[通用汉化策略](../../common/hanization-strategy-skill/SKILL.md)。实际执行、脚本选择和验收以本 workflow 及 `stages/sub-stage-register.yaml` 为准。

### 阶段 09 — font-replace ⭐ type-specific

**脚本**：`skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-fonts.py`

**调用**：
```bash
python3 skills/strategy/air-strategy-skill/scripts/workflow/sub-stage-air-fonts.py <apk-path>
```

**register 产物契约**：`crackings/<type>/<Name>/project/app/app/src/main/res/font/notosanssc.ttf`。

**AIR type-private 分析产物**：
- `crackings/<type>/<Name>/raw/08-fonts/swf_embedded_fonts.txt`
- `crackings/<type>/<Name>/raw/08-fonts/asset_fonts.txt`
- `crackings/<type>/<Name>/raw/08-fonts/ffdec_fonts/`
- `crackings/<type>/<Name>/raw/08-fonts/NotoSansSC-subset.ttf`

**AIR 差异与约束**：SWF 可同时承载嵌入字体、ActionScript 文本与图片 symbol。`ffdec` 用于导出 SWF 内嵌字体；缺失时脚本记录警告并跳过该导出。仅当目标字体由 SWF 的嵌入字体/symbol 加载时，才以 ffdec 替换该 symbol、重打包同一 SWF 并置回 APK `assets/`；仅使用 `assets/fonts/` 的 AIR 包则按其 asset 加载链替换，无需重打包 SWF。字体子集化依赖 `fontTools` 与存在的 `NOTO_SRC`（默认 `NotoSansCJK-Regular.ttc`）；任一条件不满足时脚本记录警告并跳过子集生成。

---

### 阶段 10 — font-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/13-font-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/13-font-device-verify/screenshot.png`

**AIR 额外验收**：若实际字体来源是 SWF 嵌入字体/symbol，确认重打包后的 SWF 及其字体 symbol 被 AIR 运行时加载；若来源为 `assets/fonts/` 或其他 asset，则确认对应实际加载链读取替换资源。以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 11 — text-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py`

**register 产物契约**：
- `crackings/<type>/<Name>/project/app/app/src/main/cpp/hanization_map.h`
- `crackings/<type>/<Name>/project/app/app/src/main/res/values-zh-rCN/strings.xml`

**AIR 差异**：文本来源须同时检查 `assets/*.swf` 的 ActionScript/硬编码字符串与 Android `res/strings.xml`；SWF 内条目修改后必须重打包同一 SWF。

---

### 阶段 12 — text-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/15-text-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/15-text-device-verify/ocr-screenshots/`

**AIR 额外验收**：若实际文本来源是 SWF 的 ActionScript/硬编码字符串，确认 AIR 运行时读取已重打包 SWF 内的条目；若来源为 Android `strings.xml` 或其他 asset，则确认对应实际加载链读取已汉化条目。以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 13 — image-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py`

**register 产物契约**：
- `crackings/<type>/<Name>/project/app/app/src/main/res/drawable*/<translated>.png`
- `crackings/<type>/<Name>/stages/16-image-hanization/images-manifest.yaml`

**AIR 差异**：含文字图像可能是 SWF symbol；须以 ffdec 替换 symbol、重打包 SWF，再将结果置回 APK `assets/`，不能只替换 Android drawable。

---

### 阶段 14 — image-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/17-image-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/17-image-device-verify/screenshot.png`

**AIR 额外验收**：若实际图片来源是 SWF symbol，确认 AIR 运行时加载重打包 SWF 中的替换 symbol；若来源为 Android drawable 或其他 asset，则确认对应实际加载链读取替换图片。以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 15 — record-project-files

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py`

**验证命令**：
```bash
[ -f "crackings/<type>/<Name>/dir-index.yaml" ]
[ -f "crackings/<type>/<Name>/output-project-manifest.yaml" ]
```

---

## 4. 强制固化规则

以下阶段成功后**必须**执行任务后固化（AGENTS.md §1.6）：

| 阶段 | 触发条件 | 固化内容 |
|------|----------|----------|
| 04 sdk-network-device-verify | 验收通过 | SDK/ANE 移除经验 + 网络检测去除经验 |
| 06 revenue-device-verify | 验收通过 | 激励视频转发经验 + IAP 转发经验 |
| 08 ui-hide-device-verify | 验收通过 | 去功能点经验（SWF ActionScript 修改策略） |
| 10 font-device-verify | 验收通过 | 字体替换经验（ffdec font swap 操作步骤） |
| 12 text-device-verify | 验收通过 | 文本汉化经验 |
| 14 image-device-verify | 验收通过 | 图片汉化经验（SWF symbol 替换流程） |

---

## 5. 常见失败模式

| 失败 | 原因 | 回退 |
|------|------|------|
| ffdec 反编译崩溃 | SWF 加密 / 损坏 / Alchemy 字节码 | ffdec deobfuscator；或换 jpexs-decompiler |
| 字体替换后字体丢失 | SWF 中字体 ID 变化 | ffdec 用相同 fontId；保留原 glyph 索引 |
| AIR 签名校验失败 | AIR runtime 签名校验未通过 | Frida hook AIR 签名校验函数 |
| SWF 反编译混淆（Alchemy） | ActionScript 编译为字节码 | ffdec deobfuscator + 字符串解密 |
| ANE 移除后崩溃 | application.xml extensions 列表未同步清理 | 同步修改 `<extensions>` 节点 |
| 重打包后 AIR runtime 失效 | libAdobeAIR.so 被误删 | 确保 lib/ 下的 AdobeAIR 相关 .so 全部保留 |
| 编译失败（preprocess-build）| smali 目录缺失 / package 属性解析错误 | 对照 apktool.yml 检查 package name |
| gradlew assembleRelease 失败 | 资源文件名含 `$` / 缺少 public.xml | 用 `aapt2 dump resources` 校对 |

---

## 6. 主阶段（sniff / assess / final-check / cleanup）

### M1 — 类型嗅探（sniff）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk-path>
```

**AIR 识别特征**：
- `assets/META-INF/AIR/application.xml` 存在
- `lib/libAdobeAIR.so` 存在
- APK 内含 `.swf` 文件

**验证命令**：
```bash
grep "TYPE" crackings/<type>/<Name>/findings.md
# 期望：TYPE=Android SUBTYPE=air
```

---

### M2 — 难度评估（assess）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py <apk-path>
```

**验证命令**：
```bash
cat crackings/<type>/<Name>/difficulty.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('grade','MISSING'))"
```

---

### M3 — 最终验收（final-check）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py
```

**AIR 额外检查项**：
- main.swf 存在于 `assets/` 且大小合理（> 10KB）
- libAdobeAIR.so 存在
- application.xml 的 `extensions` 列表已清理

---

### M4 — 清理临时空间（cleanup）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py
```

**保留产物**：crackings/<type>/<Name>/project/ 下的 AS 工程 + patched.apk + my.keystore.jks

---

## 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../../EXPERIENCES.md) — 通用逆向经验
- [`skills/common/general-strategy-skill/workflow.md`](../../common/general-strategy-skill/workflow.md) — 通用阶段骨架
- [`skills/common/general-strategy-skill/stages/sub-stage-register.yaml`](../../common/general-strategy-skill/stages/sub-stage-register.yaml) — 通用 01–15 路由定义
- [experiences.md](./experiences.md) — 本 type 私有逆向经验
- [WORKFLOW.md](../../../WORKFLOW.md) — 主阶段与子阶段流程
