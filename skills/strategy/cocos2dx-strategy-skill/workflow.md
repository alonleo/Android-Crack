# Cocos2d-x Workflow — 阶段流程操作手册

> 本文件是 cocos2dx-strategy-skill 的"流程操作手册"。
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
| 01 | static-analyze | `skills/strategy/cocos2dx-strategy-skill/scripts/workflow/sub-stage-cocos-static-analyze.py` | ✅ **type-specific** | 通用静态分析 |
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

> **type-specific 脚本（> 2000B，真实覆盖）**：
> - `sub-stage-cocos-static-analyze.py`（3394B，96L）：jadx + so 提取 + so 字符串扫描 + Lua 文件提取
> - `sub-stage-cocos-lua-extract.py`（3909B，100L）：Lua 脚本解密/提取 + so/资产字符串扫描

---

## 3. 阶段详细流程（01–15）

### 阶段 01 — static-analyze ⭐ type-specific

**目标**：jadx 反编译 Java 层 + 提取 Cocos 引擎 .so + so 字符串扫描 + 提取 Lua 文件。

**脚本**：`skills/strategy/cocos2dx-strategy-skill/scripts/workflow/sub-stage-cocos-static-analyze.py`

**调用**：
```bash
python3 skills/strategy/cocos2dx-strategy-skill/scripts/workflow/sub-stage-cocos-static-analyze.py <apk-path>
```

**步骤**：

| 步骤 | 操作 | 命令/动作 |
|------|------|----------|
| 1 | jadx 反编译 | `jadx -d raw/02-jadx/sources/ --no-res --threads-count 8 <apk>` |
| 2 | 提取 Cocos .so | 从 APK zip 提取含 `cocos`/`mygame`/`game` 关键字的 `.so` 到 `raw/03-cocos/` |
| 3 | so 字符串扫描 | `strings -n 6 <so_file>`，筛选含 `Lua`/`tolua`/`luaL_load`/`lua_pcall`/`lua_getglobal` 的行 → `<so>_lua_refs.txt` |
| 4 | 提取 Lua 文件 | 从 APK zip 提取所有 `.lua` 文件到 `raw/03-cocos-lua/` |

**关键产物**：
```
crackings/<type>/<Name>/raw/
├── 02-jadx/sources/              # Java 源码
├── 03-cocos/                     # 提取的 Cocos 引擎 .so
│   ├── libMyGame.so
│   └── *_lua_refs.txt            # Lua 相关字符串引用
└── 03-cocos-lua/                 # 提取的 Lua 文件（*.lua）
```

**验证命令**：
```bash
# so 文件数量
ls crackings/<type>/<Name>/raw/03-cocos/*.so 2>/dev/null | wc -l
# 期望：≥ 1

# Lua 文件数量
ls crackings/<type>/<Name>/raw/03-cocos-lua/*.lua 2>/dev/null | wc -l
# 期望：≥ 0（本项目可能无 Lua 文件）

# Lua 引用存在于 so
ls crackings/<type>/<Name>/raw/03-cocos/*_lua_refs.txt 2>/dev/null && \
  head crackings/<type>/<Name>/raw/03-cocos/*_lua_refs.txt
```

**注意项**：
- Cocos2d-x 游戏的 Lua 文件可能加密（`.luac` 或自定义加密），未提取到 `.lua` 不等于无 Lua
- libMyGame.so 是 Cocos 游戏的默认主模块名，实际名称因游戏而异
- `strings` 扫描结果用于判断该 APK 是否使用 Lua（而非 JavaScript/C++）
- so 文件可能被加壳（upx 等），需先脱壳再分析

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
├── app/src/main/smali/
├── app/src/main/java/com/android/boot/{MainActivity.java,JniBridge.java,App.java}
└── my.keystore.jks
```

**验证命令**：
```bash
cd crackings/<type>/<Name>/project/app && ./gradlew assembleRelease
echo $?
# 期望：0
```

**Cocos2d-x 特定注意**：
- Cocos 引擎的 .so（libMyGame.so 等）必须在 `lib/arm64-v8a/` 或 `lib/armeabi-v7a/`，apktool 解包后保留在 `lib/` 目录
- Gradle 构建时**不要 strip** libMyGame.so，需要在 `build.gradle` 中配置 `packagingOptions { doNotStrip '**/libMyGame.so' }`
- `abiFilters` 建议只保留目标 ABI（如 `arm64-v8a`），减少 APK 体积

---

### 阶段 03 — sdk-network-removal

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

**验证命令**：
```bash
# 期望：0
./gradlew assembleRelease; echo $?
# 期望：0
```

**注意项**：成功 → **强制固化**

---

### 阶段 04 — sdk-network-device-verify

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 04b — network-detection（并入 sdk-network-removal）

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 05b — airplane-mode（并入 sdk-network-device-verify）

实现要点见 [去第三方 SDK：cocos2dx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#cocos2dx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 阶段 05 — revenue-forwarding

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk-path>
```

**.so 类型引擎特定**：使用 Android_Inline_Hook_ARM64，注入 `Hooked_*` + `callJava("showRewardVideo")`，注册到"Hook Engine Initialized"前

**验证命令**：
```bash
grep -c 'callJava.*showVideo\|Hooked' \
  crackings/<type>/<Name>/project/app/app/src/main/cpp/native-lib.cpp
# 期望：≥ 1
```

**注意项**：成功 → **强制固化**

---

### 阶段 06 — revenue-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**注意项**：成功 → **强制固化**

---

### 阶段 06b — iap（并入 revenue-forwarding）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-forwarding.py <apk-path>
```

**验证命令**：
```bash
grep -c 'callJava.*processPurchase\|callJava.*premiumUnlock' \
  crackings/<type>/<Name>/project/app/app/src/main/java/com/android/boot/MainActivity.java
# 期望：≥ 2
```

**注意项**：成功 → **强制固化**

---

### 阶段 07b — iap-verify（并入 revenue-device-verify）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-revenue-device-verify.py`

**注意项**：成功 → **强制固化**

---

### 阶段 07 — ui-hide

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide.py`

实现要点见 [去功能点：cocos2dx](../../common/feature-removal-strategy-skill/references/engine-notes.md#cocos2dx)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

### 阶段 08 — ui-hide-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-ui-hide-device-verify.py`

实现要点见 [去功能点：cocos2dx](../../common/feature-removal-strategy-skill/references/engine-notes.md#cocos2dx)；步骤、产物与验收见 [统一阶段接口](../../common/feature-removal-strategy-skill/references/stage-contract.md)。

本阶段仍通过当前 type 注册表路由执行，检查产物并记录状态后继续；09 真机验收不可跳过。

## 汉化阶段（10–15）

通用的汉化对象分类、质量边界与风险判断见[通用汉化策略](../../common/hanization-strategy-skill/SKILL.md)。实际执行、脚本选择和验收以本 workflow 及 `stages/sub-stage-register.yaml` 为准。

### 阶段 09 — font-replace

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-replace.py`

**register 产物契约**：`crackings/<type>/<Name>/project/app/app/src/main/res/font/notosanssc.ttf`。

**Cocos2d-x 差异**：除 register 的 Android 资源输出外，Cocos 可能由 native 层经 `Typeface::createFromAsset` 或 TTF/OTF 直接加载 `assets/fonts/`；实际路径须与引擎加载点一致。

---

### 阶段 10 — font-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-font-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/13-font-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/13-font-device-verify/screenshot.png`

**Cocos2d-x 额外验收**：确认引擎的 native/asset 字体加载路径实际读取替换资源；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 11 — text-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-hanization.py`

**register 产物契约**：
- `crackings/<type>/<Name>/project/app/app/src/main/cpp/hanization_map.h`
- `crackings/<type>/<Name>/project/app/app/src/main/res/values-zh-rCN/strings.xml`

**Cocos2d-x 差异**：文本来源可为 `.lua`/`.luac`、`libMyGame.so` 的 native 硬编码字符串及 `assets/`。无 Lua 时使用阶段 03 的 `all_strings_raw.txt`；加密 Lua 仍须按当前 type 流程先完成提取或解密。

---

### 阶段 12 — text-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-text-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/15-text-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/15-text-device-verify/ocr-screenshots/`

**Cocos2d-x 额外验收**：确认所走的 Lua、native 或 asset 文本路径在 Cocos 场景中生效；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

---

### 阶段 13 — image-hanization

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-hanization.py`

**register 产物契约**：
- `crackings/<type>/<Name>/project/app/app/src/main/res/drawable*/<translated>.png`
- `crackings/<type>/<Name>/stages/16-image-hanization/images-manifest.yaml`

**Cocos2d-x 差异**：同时检查 `assets/` 中的 `.png`、`.jpg`、`.pvr`、`.ccz` 纹理及其引擎加载方式；替换须保留当前纹理格式和图集/资源引用关系。

---

### 阶段 14 — image-device-verify

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-image-device-verify.py`

**register 产物契约**：
- `crackings/<type>/<Name>/stages/17-image-device-verify/verify-report.md`
- `crackings/<type>/<Name>/stages/17-image-device-verify/screenshot.png`

**Cocos2d-x 额外验收**：确认 Cocos 场景能解码并加载替换后的 assets/纹理；以真机证据与 register 契约共同判定，不以脚本退出码单独判定通过。

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
| 04 sdk-network-device-verify | 验收通过 | SDK 移除经验（引擎 .so 保留策略）+ 网络检测去除经验（C++ 层桩化方法） |
| 06 revenue-device-verify | 验收通过 | 激励视频转发经验 + IAP 转发经验 |
| 08 ui-hide-device-verify | 验收通过 | 去功能点经验（Lua 脚本修改策略） |
| 10 font-device-verify | 验收通过 | 字体替换经验 |
| 12 text-device-verify | 验收通过 | 文本汉化经验 |
| 14 image-device-verify | 验收通过 | 图片汉化经验 |

---

## 5. 常见失败模式

| 失败 | 原因 | 回退 |
|------|------|------|
| Lua 解密失败 | 密钥错误 / 未知加密算法 | 从 Frida hook `luaL_loadbuffer` 提取运行时密钥 |
| so 反汇编信息少 | 符号被剥离 | `doNotStrip` 已配；用 `radare2 -A` 自动分析 |
| 启动闪退 | 资源 `$` 前缀未清理 | 阶段：用 `grep + sed` 清理 |
| AGP 资源编译失败 | 缺 `apktool.yml` | 阶段：验证 apktool.yml 存在 |
| patched.apk 体积过大 | 多 ABI | `abiFilters` 仅保留 `arm64-v8a` |
| Cocos so 符号缺失 | libMyGame.so 被 strip | `packagingOptions { doNotStrip }` 已配置；重新提取未 strip 的 .so |
| gradlew assembleRelease 失败 | smali 语法错误 / 缺失类 | 检查 smali 目录完整性 |
| 字体替换后游戏崩溃 | 字体文件过大 | 使用子集化字体（fontTools subsetter）|
| 飞行模式仍检测到网络 | C++ 层网络检测未桩化 | 在 libMyGame.so 中 inline hook `isNetworkAvailable` 函数 |

---

## 6. 主阶段（sniff / assess / final-check / cleanup）

### M1 — 类型嗅探（sniff）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-sniff.py <apk-path>
```

**Cocos2d-x 识别特征**：
- `lib/libMyGame.so` 或 `lib/libcocos2d*.so` 存在
- APK 内含 `.lua` / `.luac` 文件（assets/ 目录下）
- Java 层包含 Cocos 引擎类（如 `org.cocos2dx.lib.Cocos2dxActivity`）

**验证命令**：
```bash
grep "TYPE" crackings/<type>/<Name>/findings.md
# 期望：TYPE=Android SUBTYPE=cocos2dx
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

**Cocos2d-x 额外检查项**：
- libMyGame.so 存在于 `lib/arm64-v8a/` 且未被 strip
- 编译后 APK 包含正确的 Cocos 引擎 .so
- `doNotStrip` 配置生效，无 "stripped" 警告

---

### M4 — 清理临时空间（cleanup）

**脚本**：`skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py`

**调用**：
```bash
python3 skills/common/general-strategy-skill/scripts/workflow/sub-stage-cleanup.py
```

**Cocos2d-x 特定保留**：确保 `lib/arm64-v8a/libMyGame.so` 和其他 Cocos 引擎 .so 不会被误删

---

## 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [tools-index.md](./tools-index.md) — 工具索引
- [EXPERIENCES.md](../../../EXPERIENCES.md) — 通用逆向经验
- [`skills/common/general-strategy-skill/workflow.md`](../../common/general-strategy-skill/workflow.md) — 通用阶段骨架
- [`skills/common/general-strategy-skill/stages/sub-stage-register.yaml`](../../common/general-strategy-skill/stages/sub-stage-register.yaml) — 通用 01–15 路由定义
- [experiences.md](./experiences.md) — 本 type 私有逆向经验
- [WORKFLOW.md](../../../WORKFLOW.md) — 主阶段与子阶段流程
