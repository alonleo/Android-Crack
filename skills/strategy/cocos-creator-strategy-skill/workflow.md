# Cocos-creator Strategy — Workflow

> 本文件是 cocos-creator-strategy-skill 的**流程操作手册**。
>
> 加载顺序：strategy.md → **[workflow.md（本文件）]** → tools-index.md
>
> 字体、文本与图片汉化的跨 type 分类和质量边界见 [汉化策略参考](../../common/hanization-strategy-skill/SKILL.md)；实际执行入口、action/step、产物与验收以本 workflow 和 [`stages/sub-stage-register.yaml`](./stages/sub-stage-register.yaml) 为权威。

---

## 1. 头部引用

| 引用文件 | 作用 |
|----------|------|
| `strategy.md` | 类型策略总览：路由规则、评分体系、强制子阶段 |
| `**[workflow.md（本文件）]**` | 流程操作手册：01–15 子阶段 + 主阶段详细步骤 |
| `tools-index.md` | 工具索引：jadx / apktool / il2cppinspector / blutter 等工具用法 |
| `EXPERIENCES.md` | 经验沉淀：本 type 已知坑、最佳实践 |
| [common 汉化 skill](../../common/hanization-strategy-skill/SKILL.md) | 跨 type 汉化对象分类、质量边界与经验；不替代本 type 的执行路由 |

---

## 2. 子阶段路由速查表

| 编号 | 子阶段名 | 类型 | 脚本 |
|------|----------|------|------|
| 01 | static-analyze | common | `sub-stage-static-analyze.py` |
| 02 | preprocess-build | common | `sub-stage-preprocess-build.py` |
| 03 | sdk-network-removal | common | `sub-stage-sdk-network-removal.py` |
| 04 | sdk-network-device-verify | common | `sub-stage-sdk-network-device-verify.py` |
| 05 | revenue-forwarding | common | `sub-stage-revenue-forwarding.py` |
| 06 | revenue-device-verify | common | `sub-stage-revenue-device-verify.py` |
| 07 | ui-hide | common | `sub-stage-ui-hide.py` |
| 08 | ui-hide-device-verify | common | `sub-stage-ui-hide-device-verify.py` |
| 09 | font-replace | common | `sub-stage-font-replace.py` |
| 10 | font-device-verify | common | `sub-stage-font-device-verify.py` |
| 11 | text-hanization | common | `sub-stage-text-hanization.py` |
| 12 | text-device-verify | common | `sub-stage-text-device-verify.py` |
| 13 | image-hanization | common | `sub-stage-image-hanization.py` |
| 14 | image-device-verify | common | `sub-stage-image-device-verify.py` |
| 15 | record-project-files | common | `sub-stage-record-project-files.py` |

> **路由说明**:
> - `type-specific`: 该 type 专用脚本（见 `scripts/workflow/` 目录）
> - `common`: 所有 type 共用脚本（`skills/common/general-strategy-skill/scripts/workflow/`）

---

## 3. 子阶段详细流程（01–15）

### 01 — 通用静态分析（jadx + smali + SDK 扫描 + 入口定位）

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py`

#### 步骤（通用）

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行子阶段脚本 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依子阶段不同检查对应产物文件 | 见各子阶段 outputs |
| 3 | 如需真机验收 | `adb install -r patched.apk && adb shell am start` | 安装/启动成功 |

#### 验证命令

```bash
# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/01-static-analyze/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-static-analyze.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 02 — 预处理构建检测

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py`

#### 步骤（通用）

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行子阶段脚本 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依子阶段不同检查对应产物文件 | 见各子阶段 outputs |
| 3 | 如需真机验收 | `adb install -r patched.apk && adb shell am start` | 安装/启动成功 |

#### 验证命令

```bash
# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/02-preprocess-build/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-preprocess-build.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 03 — 去SDK + 去网络检测

实现要点见 [去第三方 SDK：cocos-creator](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos-creator)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-removal.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/03-sdk-network-removal/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-removal.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 04 — 真机验收（SDK + 网络检测）

实现要点见 [去第三方 SDK：cocos-creator](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos-creator)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-device-verify.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/04-sdk-network-device-verify/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sdk-network-device-verify.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 05 — 激励 + IAP 转发

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

#### 步骤（通用）

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行子阶段脚本 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依子阶段不同检查对应产物文件 | 见各子阶段 outputs |
| 3 | 如需真机验收 | `adb install -r patched.apk && adb shell am start` | 安装/启动成功 |

#### 验证命令

```bash
# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/05-revenue-forwarding/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 06 — 真机验收（激励 + IAP）

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

#### 步骤（通用）

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行子阶段脚本 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依子阶段不同检查对应产物文件 | 见各子阶段 outputs |
| 3 | 如需真机验收 | `adb install -r patched.apk && adb shell am start` | 安装/启动成功 |

#### 验证命令

```bash
# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/06-revenue-device-verify/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试

### 07 — 去功能点（UI 隐藏）

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py`

实现要点见 [去功能点：cocos-creator](../../common/feature-removal-strategy-skill/references/engine-notes.md#cocos-creator)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

### 08 — 真机验收（去功能点）

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py`

实现要点见 [去功能点：cocos-creator](../../common/feature-removal-strategy-skill/references/engine-notes.md#cocos-creator)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

### 09 — 字体替换

**入口**：当前 register 路由到 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py`；注册 action 为 `default-action`，step 顺序以 `stages/font-replace/default-action/step-register.yaml` 为准：`smali-to-jar → gradle-build → gen-report → scan-fonts → replace-font`。

**Cocos Creator 差异**：除 register 声明的 `project/app/app/src/main/res/font/notosanssc.ttf` 外，还要识别 bundle 中由 `cc.TTFFont` 元数据引用的 `assets/assets/resources/native/.../Archive.ttf`。直接替换该字体曾因 DSIG 保护导致崩溃；沿用现有方向时须处理 DSIG，且保持 `import/<uuid>...json` 与 `native/<uuid>/` 的关联，不得把此探索路径写成已通过的注册 action。

### 10 — 真机验收（字体）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。必须在真实设备覆盖使用 bundle 字体的界面并确认未出现字体加载崩溃；产物以 register 为准：`stages/13-font-device-verify/verify-report.md` 与 `screenshot.png`。无法完成真机验收时暂停在 11，不得以构建成功替代。

### 11 — 文本汉化操作

**注册入口**：当前 register 路由到 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py`，`run-action: default-action`。真实注册 step 顺序为 `smali-to-jar → gradle-build → gen-report → collect-strings → build-map`；注册产物仍是 `project/app/app/src/main/cpp/hanization_map.h` 与 `project/app/app/src/main/res/values-zh-rCN/strings.xml`。

**Cocos Creator 专属资源路径**：UI 文本还可能位于加密 JSC 和 3.x 多 bundle 脚本中，尤其是 `assets/assets/main/index.<hash>.js` 及各 bundle。命中 `assets/**/*.jsc` 时，沿用已固化 helper：

1. `scripts/common/decrypt-jsc-assets.py` 用从 `libcocos2djs.so` 提取的现有 XXTEA 密钥批量解密，按 bundle 收集可翻译文本。
2. 修改明文后由 `scripts/common/repack-jsc-assets.py` 使用同一密钥重新加密并写回原 `.jsc` 路径，再走现有重打包与签名链路；文件名、hash、bundle 配置和目录关系保持不变。
3. 若回写后的 JSC 卡在加载页，保留现有 `libcocos2djs.so` 加载/完整性校验调查路径；该调试路径不是已注册 action，也不能绕过 13 的真机验收。

**动态文本**：静态 bundle/映射未覆盖的运行时生成文本，继续沿用 native 调试路径定位 JSC 加载或赋值点，再把持久化修改落回工程；Frida 仅用于定位，不能作为交付汉化。进入 Frida/native 附加调试分支前，设备上的 frida-server 必须已具备附加目标游戏进程的 ptrace 权限；若附加失败，先核实此权限条件，不应将权限不足误判为 JSC 资源或加密错误。helper 解密/回写与动态调试是 Cocos 专属处理，不改变 register 中 `default-action` 的名称和 step 顺序。

### 12 — 真机验收（文本）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。真实设备必须覆盖主流程、至少一个 JSC/bundle 页面及可触发的动态文本，确认重新加密资源可加载且应用持续存活；产物为 `stages/15-text-device-verify/verify-report.md` 与 `ocr-screenshots/`。无法完成时暂停在 13。

### 13 — 图片汉化操作

当前 register 路由 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py`，注册 action 为 `default-action`，真实 step 为 `smali-to-jar → gradle-build → gen-report → detect-images → ocr-images`。Cocos Creator 图片若位于 `assets/assets/<bundle>/` 而非 Android drawable，处理时保留原 bundle 路径、hash/UUID 与配置引用；register 声明的交付输出仍为 `project/app/app/src/main/res/drawable*/<translated>.png` 和 `stages/16-image-hanization/images-manifest.yaml`。

### 14 — 真机验收（图片）

注册 action 为 `default-action`（`check-env → run-verify → gen-report`）。真实设备必须进入实际加载目标 bundle 的页面，按当前 register role 与 common 汉化参考检查显示质量；产物为 `stages/17-image-device-verify/verify-report.md` 与 `screenshot.png`。无法完成时暂停在 15。

### 15 — 记录工程文件

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py`

#### 步骤（通用）

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行子阶段脚本 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依子阶段不同检查对应产物文件 | 见各子阶段 outputs |
| 3 | 如需真机验收 | `adb install -r patched.apk && adb shell am start` | 安装/启动成功 |

#### 验证命令

```bash
# 通用验证（子阶段退出码）
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py <apk> [name] && echo "OK"

# 产物存在性
ls crackings/<type>/<Name>/stages/15-record-project-files/ 2>/dev/null && echo "产物存在"
```

#### 注意项

- 所有子阶段共享 `skills/common/general-strategy-skill/scripts/workflow/sub-stage-record-project-files.py`
- 部分子阶段为 interactive 模式，需人工介入（ui-hide / text-hanization / image-hanization）
- 真机验收子阶段（*-device-verify）需连接设备并开启 USB 调试
## 4. 主阶段（sniff / assess / final-check / cleanup）

#### sniff — 类型嗅探

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py`

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行主阶段 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依主阶段不同检查对应产物 | 见上方各主阶段 outputs |

**验证命令**:

```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk> [name] && echo "OK"
```

#### assess — 难度评估

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py`

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行主阶段 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依主阶段不同检查对应产物 | 见上方各主阶段 outputs |

**验证命令**:

```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py <apk> [name] && echo "OK"
```

#### final-check — 最终验收

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py`

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行主阶段 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依主阶段不同检查对应产物 | 见上方各主阶段 outputs |

**验证命令**:

```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py <apk> [name] && echo "OK"
```

#### cleanup — 清理临时空间

**脚本**: `skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py`

| 步骤 | 操作 | 命令/动作 | 验证 |
|------|------|-----------|------|
| 1 | 执行主阶段 | `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py <apk> [name]` | 退出码 0 |
| 2 | 检查产物 | 依主阶段不同检查对应产物 | 见上方各主阶段 outputs |

**验证命令**:

```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py <apk> [name] && echo "OK"
```


---

## 5. 强制固化规则

以下子阶段完成后**必须固化**（将修改提交至 `crackings/<type>/<Name>/project/` 并更新 `findings.md`）：

| 子阶段 | 固化时机 | 固化内容 |
|--------|----------|----------|
| 02 preprocess-build | 每次成功构建后 | AS 项目模板文件 + 签名配置 |
| 03 sdk-network-removal | 每次 manifest 清理后 | `3rd-party-sdk.yaml` + AndroidManifest.xml |
| 04 sdk-network-device-verify | SDK 与网络检测真机验收通过后 | `verify-report.md` + 截图 |
| 06 revenue-device-verify | 激励转发真机验收通过后 | `verify-report.md` + 截图 |
| 08 ui-hide-device-verify | 去功能点通过后 | `verify-report.md` + 截图 |
| 10 font-device-verify | 字体通过后 | `verify-report.md` + 截图 |
| 12 text-device-verify | 文本汉化通过后 | `verify-report.md` + OCR 截图 |
| 14 image-device-verify | 图片汉化通过后 | `verify-report.md` + 截图 |

---

## 6. 常见失败模式

| 子阶段 | 失败表现 | 常见原因 | 回退方案 |
|--------|----------|----------|----------|
| 01 static-analyze | jadx 崩溃 / 无输出 | APK 加固 / split APK | 手动 `apktool d -s -r` 后用 GUI jadx |
| 02 preprocess-build | gradlew 编译失败 | AGP/JDK/Gradle 版本不匹配 | 检查 `build-report.md`；对照工具链版本 |
| 03 sdk-network-removal | 启动崩溃 | SDK 初始化桩化不完整 | 补充桩化 SDK 生命周期方法 |
| 04 sdk-network-device-verify | 安装失败 | manifest merge 冲突 | 检查 `AndroidManifest.xml` merge 错误 |
| 03 sdk-network-removal | 仍有更新弹窗 | 网络检测在 native 层 | 结合 Frida hook native 层 |
| 05 revenue-forwarding | 激励视频不触发 | JNI 签名/参数不匹配 | 用 Frida 验证 `showVideo` call 签名 |
| 05 revenue-forwarding | IAP 弹窗 | billing SKU 配置错误 | 检查 `processPurchase` 参数 |
| 07 ui-hide | 布局变形 | 隐藏坐标影响布局 | 改用 `alpha=0` 而非移动坐标 |
| 09 font-replace | 替换 bundle 字体后崩溃 | `cc.TTFFont` 资源的 DSIG 或 UUID 引用被破坏 | 保留 import/native 关联并沿用 DSIG 处理方向 |
| 11 text-hanization | 回写 JSC 后卡加载页 | 密钥、加密格式或 native 完整性校验不匹配 | 核对同密钥回写；必要时沿用 `libcocos2djs.so` 调试路径 |
| 13 image-hanization | bundle 图片未生效 | hash/UUID/配置引用或资源路径未保持 | 按原 bundle 关系回写并重跑 15 真机验收 |
| 15 record-project-files | 清单不完整 | 新生成文件未追踪 | 手动 `find crackings/<type>/<Name>/project -type f` 核对 |

---

## 7. 主阶段详细说明

### 7.1 sniff（类型嗅探）

**入口**: `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk> [name]`

**职责**: 用 `unzip -l` 分析 APK 内容，识别 type/subtype，写入 `findings.md §1`。

**Type 识别逻辑**:

```python
if "META-INF/AIR/application.xml" in names: TYPE = "AIR"
elif "libil2cpp.so" in names: TYPE = "il2cpp"
elif "GameAssembly.dll" in names: TYPE = "UnityMono"
elif "libflutter.so" in names: TYPE = "Flutter"
elif "libUE4.so" in names: TYPE = "Unreal"
elif "classes*.dex" in names: TYPE = "Android"
```

**产物**: `crackings/<type>/<Name>/findings.md`（含 TYPE/SUBTYPE/LIB_COUNT/DEX_COUNT）

---

### 7.2 assess（难度评估）

**入口**: `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-assess.py [name]`

**职责**: 6 维度加权评分 → `difficulty.json` + `raw/assessment.md`。

| 维度 | 最高分 | 评分依据 |
|------|--------|----------|
| 代码复杂度 | 6 | type（il2cpp=16, unreal=18…） |
| 代码体积 | 7 | APK 大小（>200MB=15） |
| 加密/加固 | 25 | il2cpp metadata 缺失=+18 |
| 反调试 | 7 | ptrace/TracerPid 字符串命中 |
| 第三方 SDK | 6 | SDK 包名命中数 |
| 运行时约束 | 7 | INTERNET 权限/设备 ID 收集等 |

**产物**: `crackings/<type>/<Name>/difficulty.json`（含 grade S/A/B/C/D/F）

---

### 7.3 final-check（最终验收）

**入口**: `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-final-check.py [name]`

**6 条硬指标**:

1. `patched.apk` 存在
2. aapt2 解析成功
3. `values-zh-rCN/strings.xml` 含中文（标准 Android）或 lang pack 非哨兵（引擎特定）
4. AndroidManifest.xml 第三方 SDK 组件已清理
5. apksigner verify 通过（含 v1+v2+v3）
6. `source.apk.md5` 与 `apks/` 原始文件 MD5 一致

**产物**: `crackings/<type>/<Name>/stages/23-final-check/final-report.md`

---

### 7.4 cleanup（清理临时空间）

**入口**: `python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py [name]`

**保留**: `status.yaml` / `findings.md` / `tool-calls.md` / `difficulty.json` / `patched.apk` / `keystore/` / `05-strings/` 等最终产物

**删除**: `01-apktool/` / `02-jadx/` / `03-*` / `04-findings/` / 中间 APK 产物

**产物**: 无（原地清理）

---

## 8. 工具链版本（强制）

| 工具 | 版本 |
|------|------|
| JDK | 7 |
| AGP | 7.4.2 |
| Gradle | 7.5.1 |
| compileSdk | 33 |
| apktool | 2.9.x |
| jadx | 1.4.x |
| apksigner | 0.9.x |

> **警告**: 版本不匹配会导致 gradlew 编译失败，请严格对照上表。
