# AGENTS.md — Android Reverse Engineering Workspace

> **本文件是 Agent 进入此工作区的首读入口**，定义 **agent 行为约束**：
> - 怎么读环境、怎么跑脚本、怎么记录、怎么协同、怎么维护工具与经验库。
>
> **不包含**：
> - 类型策略详情（识别/工具/坑位）→ 见 `skills/strategy/<type>-strategy-skill/`
> - 阶段命令细节 → 见对应 skill 的 `workflow.md`
> - 产出约束（交付物长什么样、签名方案、验收清单）→ 见 [OBJECTIVES.md](./OBJECTIVES.md)
> - 类型嗅探与策略路由 → 见 [STRATEGY.md](./STRATEGY.md)
> - 通用逆向问题的处理经验 → 见 [EXPERIENCES.md](./EXPERIENCES.md)；type 私有问题见对应 strategy skill 的 `experiences.md`
>
> 所有路径相对 `<repo>` = `./`。
> **FORBIDDEN** 的操作不得擅自执行；**REQUIRED** 的步骤不得跳过。
>
> **配套文档**：[OBJECTIVES.md](./OBJECTIVES.md)（产出约束 + 验收硬指标）· [STRATEGY.md](./STRATEGY.md)（类型路由）· [WORKFLOW.md](./WORKFLOW.md)（主流程）· [EXPERIENCES.md](./EXPERIENCES.md)（跨 type 通用逆向问题经验库）

---

## 0. 项目范围

- **目标类型**：单机游戏（含联网单机游戏）
  - 可为纯离线单机，亦可为含联网功能的单机游戏（排行榜、云存档、内购验证等）
  - 联网功能不可影响核心玩法可玩性——移除网络检测后仍需能正常进入和游玩
- **限制**：不处理纯网游/MMO/强联机竞技类游戏
- **当前 APK 池**（`apks/`）：每次 Agent 启动时须用 `unzip -l` 嗅探类型，匹配 [STRATEGY.md §1.2 类型识别表](./STRATEGY.md#12-类型快速识别表路由核心)

---

## 1. 通用原则

### 1.1 固化优先

> **适用范围**：本文件关于脚本必须落位 skill/common、登记逆向脚本索引、加载 Android 环境以及项目阶段固化的要求，适用于逆向项目脚本。仓库维护脚本按 §1.3 的分类规则处理；不得把文档整理、目录迁移等维护操作登记为 APK 阶段或逆向经验。

> **🔴 强制约束**：Agent 在任何阶段都必须**优先调用脚本**完成操作。
> 禁止在 bash / Write 工具里手工拼接 shell 命令片段、自己生成临时代码（`.sh` / `.py` /
> Frida JS / awk / sed / grep 管道组合等）直接绕过现有脚本执行。
> 缺脚本 → **先补脚本再执行**，而非「先跑了再说」。

- AI 生成的逆向项目脚本操作，修改成通用版本 → **必须**提取为 `skills/common/scripts/` 或 `skills/{strategy,common}/<name>/scripts/` 下的脚本；仓库维护脚本按 §1.3 独立存放。
- 每次发现可跨项目复用的 SDK、反调试、汉化、构建或真机验证问题模式 → **必须**按固定格式追加到 [EXPERIENCES.md](./EXPERIENCES.md)，并且在对应的子阶段创建一个 Action、在注册表中注册。`EXPERIENCES.md` 仅记录通用逆向问题经验；来源 APK、项目过程、日期和项目产物必须记录在对应 `crackings/<type>/<Name>/` 下。
- 经验库条目只追加不删改；原结论错误时追加更正 `[supersedes: <原条目>]`。
- 调试探针跑通后**必须**提取为正式脚本并删除本体。
- 脚本命名 `<verb>-<scope>.py`（如 `sub-stage-sniff.py`），禁止 `tmp_*` / `test_*` / `try_*`。

**禁止行为**：
- ❌ Agent 用 `bash` 工具手敲 `adb shell ...`、`apktool d ...`、`apksigner sign ...`、`zipalign ...`、`grep | sed | awk` 等命令链完成阶段操作 → 必须调对应 `sub-stage-*.py` | `run-major-*.py`
- ❌ Agent 用 `Write` 工具在 `temp/` 或项目目录写临时 `.py` 跑一次性脚本 → 必须先把脚本落到 `skills/common/scripts/` 或 skill `scripts/` 后再调
- ❌ Agent 用 `python3 -c "..."` 内联代码片段完成阶段操作 → 必须封装为正式脚本
- ❌ Agent 在 `status.yaml` 中贴大段命令 / Frida JS 而不提取成脚本 → 必须提取后再跑
- ❌ 遇到脚本 bug 时 Agent 选择「绕过去手敲」 → 必须先修复脚本本体

**例外**（允许 Agent 直接执行少量命令）：
- `source tools/environments/env.sh`（环境加载，硬约束前置条件）
- `./skills/common/scripts/<driver>.py ...`（驱动脚本自身调用）
- 只读探查：`ls`、`cat <index.md>`、`grep <SCRIPTS-INDEX.md>`、`read` 工具读文档

详见 §1.11 完整「FORBIDDEN 手工拼接」清单。

### 1.1.1 四大主阶段默认入口（REQUIRED）

> **⛔ 全部阶段强制跑通（零跳过硬约束）**：
> **四大主阶段（M1/M2/M3/M4）+ 子阶段 01–15，都必须强制执行完毕并通过验证。**
> - 禁止跳过任何主阶段：M1 sniff → M2 assess -> M4 final-check → M5 cleanup
> - 禁止跳过任何子阶段（对应 type 的 `stages/sub-stage-register.yaml` 中全部条目）
> - 禁止跳过任何真机验收环节（不得以「编译通过即可」为由跳过真机验证）
> - **真机验收无法执行时的处理（用户声明）**：若 `verify=true` 子阶段（04/06/08/10/12/14）无法执行
>   （无设备 / 设备离线 / 验收条件不满足），**禁止跳过或降级**——必须**暂停处理流程**，在 `status.yaml` 的
>   `current_stage` / `failed_stages` 中**记录该子阶段名**并注明原因，待条件恢复后**从该子阶段续跑**。
> - 禁止用 `--skip` 规避失败阶段而不修复
> - M4 cleanup 同样是**必选**，`--no-cleanup` 仅限开发调试
> - 详见 [WORKFLOW.md §🔴](./WORKFLOW.md#-全部阶段强制跑通零跳过硬约束)

> **调整后的执行模型（用户确认）**：四大主阶段是 Agent 的流程控制层，不要求调用主阶段 driver 脚本；Agent 按
> `STRATEGY.md`、`WORKFLOW.md`、对应 strategy skill 和产物契约自行完成每个主阶段的检查、决策、记录与验收。
> 主阶段脚本仅作为可选的历史兼容工具，不再是 REQUIRED 入口。

> **子阶段为 01–15 线性连续**。

| 主阶段 | 驱动脚本 | 调用的子脚本 |
|--------|---------|--------------|
| **M1** sniff（嗅探） | `run-major-sniff.py` | `sub-stage-sniff.py` |
| **M2** assess（评估） | `run-major-assess.py` | `sub-stage-assess.py` |
|   ↳ stages（子阶段 01–15） | 各 type skill 的 `stages/sub_stage-dispatcher.py` | 读 `sub-stage-register.yaml` 按书写顺序跑（全部 type 已迁移 register 驱动） |
| **M3** final-check（验收） | `run-major-accept.py` | `sub-stage-final-check.py`（6 条硬指标全过） |
| **M4** cleanup（清理） | `run-major-cleanup.py` | `sub-stage-cleanup.py` |

**可选的批量辅助调用**（不替代 Agent 对主阶段的人工处理）：
```bash
python3 skills/strategy/<type>-strategy-skill/stages/sub_stage-dispatcher.py [--stage NN]   # 跑该 type 子阶段(register 驱动)
```

### 1.1.2 主阶段与子阶段执行边界（REQUIRED · 用户调整）

> **⛔ 硬约束**：主阶段由 Agent 自行按规则处理；子阶段必须使用对应的子阶段脚本，并由 Agent 理解脚本输出、检查产物、判断是否通过。
> 主阶段 driver 不再是主阶段的必经入口，子阶段脚本也不得被当作无需理解的黑盒。

#### 术语表（type / major_stage / stage / action / step / register）

| 概念 | 含义 | 载体 | 说明 |
|------|------|------|------|
| **type** | APK 引擎类型（il2cpp / android / cocos2dx / …） | `skills/strategy/<type>-strategy-skill/` | sniff 判定；每 type 一个 skill |
| **major_stage（主阶段）** | M1 sniff / M2 assess / M3 final-check / M4 cleanup | `sub-stage-register.yaml` 的 `major_stages:` 段 | 流程控制层，由 Agent 人工判断、记录、验收 |
| **stage / sub_stage（子阶段）** | 一个逻辑处理单元，编号 01–15 | `stages/sub-stage-register.yaml` 的 `sub_stages:` 条目 + `stages/<name>/` 目录 | 执行单元，register 书写顺序 = 执行顺序 |
| **action（执行方案）** | 单个子阶段下的一种执行方案 | 子阶段目录的 `action-register.yaml` 的 `all-actions:` 列表 | 同一子阶段可有多种方案（如 text-hanization 的 default-action vs metadata-hanize） |
| **default-action（默认方案）** | 子阶段默认采用的 action | `action-register.yaml` 的 `default:` 字段 | 可被 `--action` 运行时覆盖 |
| **step（步骤）** | action 内按序执行的最小动作 | `<action>/step-register.yaml` 的 `steps:` + `step-*.py` | 由 step-driver 按 `number` 升序调度 |
| **register（注册表）** | 子阶段总注册表 | `stages/sub-stage-register.yaml` | `sub_stages:` 书写顺序 = 执行顺序；主阶段在 `major_stages:` |
| **step-register** | action 的步骤注册表 | `<action>/step-register.yaml` | 每 step 含 `number/name/script` |
| **handlers（已废弃）** | 旧 B 模式三级 fallback | — | 已被 sub_stage > action > step 取代 |

**主阶段脚本（一级 driver）**：
- `skills/common/scripts/run-major-sniff.py`（M1）/ `run-major-assess.py`（M2）/ `run-major-accept.py`（M3）/ `run-major-cleanup.py`（M4）


**子阶段脚本（二级 worker）**：
- `skills/strategy/<type>-strategy-skill/scripts/workflow/sub-stage-*.py`
- M2 内部的子阶段通过各 type skill 的 `stages/sub_stage-dispatcher.py` 调度：读 `stages/sub-stage-register.yaml`（`sub_stages:` 书写顺序 = 执行顺序），逐个委托 `stages/<name>/action-driver.py` → `default-action/step-driver.py`。
- 由 driver 通过 `skills/common/scripts/lib/routing.py` 按 name 动态查脚本路径（**禁止** Agent 在 driver 之外硬编码子阶段脚本路径直接调用）

**执行方案脚本（三级 action）**：
- 通过 各 子阶段 的 `stages/<name>/action-driver.py` 调度：读 `stages/action-register.yaml`（`run-action:` 当前子阶段使用的执行方案，`path：` 当前执行方案的步骤调度器路径 ）

**方案步骤脚本（四级 step）**：
- 通过 设置的执行方案 的 `<name>/step-driver.py` 调度：读 `<name>/step-register.yaml`（`steps:` 当前执行方案的步骤顺序，`number：` 序号 = 逐步执行顺序，`name:` 当前步骤的名称，`script：` 当前步骤该调用的脚本 ）

**禁止行为（FORBIDDEN）**：
- ❌ 用主阶段 driver 代替 Agent 对主阶段规则、产物和验收结果的理解
- ❌ 直接跳过子阶段脚本，改用 Agent 手工拼接该子阶段的 apktool/adb/apksigner 等操作
- ❌ 运行子阶段脚本后不检查其输出、产物和状态记录就宣称阶段通过
- ❌ 为了绕过失败而跳过策略中定义的主阶段或子阶段

**正确做法（REQUIRED）**：
- ✅ Agent 先读取规则与路由，人工完成主阶段 M1/M2/M3/M4 的决策、检查、记录和验收
- ✅ M2 assess 内嵌入子阶段 01–15 流程，每个子阶段均调用其路由到的 `sub-stage-*.py`，再由 Agent 解释结果并决定是否通过
- ✅ 子阶段失败时先理解失败原因、修复脚本或输入，再重跑对应子阶段
- ✅ M3 final-check + M4 cleanup 由 Agent 根据验收清单、产物契约和清理规则自行执行；相关 driver 仅作可选复核工具
- ✅ 子阶段脚本可单独调试和重跑，但每次都必须由 Agent 检查输出、产物和状态记录

**约束目的**：
1. 主阶段由 Agent 负责流程判断、证据收集、状态同步和验收结论。
2. 子阶段脚本负责可重复的具体操作；Agent 负责选择脚本、理解输出、检查产物并处理失败。
3. 防止把“脚本退出码为 0”误认为完整阶段通过。

### 1.2 项目环境（REQUIRED）
- 处理任何项目时，**必须先加载本项目环境**：`source tools/environments/env.sh`。
- 所有工具调用必须使用 `env.sh` 提供的变量（`$ADB_BIN`、`$APKTOOL`、`$JADX`、`$AAPT2`、`$APKSIGNER`、`$ZIPALIGN`、`$KEYTOOL`），禁止直接依赖系统同名命令。
- Agent 手工执行命令时同样必须在同一 shell 中先加载环境，例如：`source tools/environments/env.sh && "$ADB_BIN" devices`。
- 判断工具缺失前，必须先加载项目环境并检查变量指向的可执行文件；不得因系统 `PATH` 中找不到工具而直接判定缺失。
- Gradle、ADB、Android SDK、JDK、apktool、jadx 等均优先使用 `tools/environments/` 下的项目内版本。
- 工具链版本严格遵循 [OBJECTIVES.md §2.1](./OBJECTIVES.md#21-工具版本约束)（JDK 11 / AGP 7.4.2 / Gradle 7.5.1 / compileSdk 33）。

### 1.3 脚本硬规范

**创建脚本前必须声明用途和归属（REQUIRED）**：
- **逆向项目脚本**：直接用于 APK 嗅探、分析、修改、构建、签名、设备验收、项目记录，或提供这些流程必需的工具链、策略与运行库。按下述 skill 分布规则落位，并登记 `SCRIPTS-INDEX.md` 和对应子索引。
- **仓库维护脚本**：仅用于文件/目录改名、路径引用迁移、文档与索引整理、仓库结构校验等。统一放在 `tools/maintenance/scripts/`，**不放入 `skills/common/scripts/` 或策略 skill 的运行脚本目录，不登记 `SCRIPTS-INDEX.md`、skill 脚本子索引或逆向工具表**。使用说明写在脚本自身的 docstring / `--help` 中。
- 新脚本应在创建说明及文件头标明所属类别、用途和依赖；维护脚本仍须为正式可复用 Python 脚本，保留预览/验证能力，不以临时代码替代。
- 纯文件维护不依赖 Android 工具链，不要求加载 `env.sh`、执行 APK 阶段或写项目 `status.yaml`；需要调用 Android 工具时应重新按逆向项目脚本分类。
- 此分类优先于本文件 §1.1、§1.6、§1.9、§1.11、§1.12 中未区分类别的通用措辞。维护脚本可直接在维护目录查找和调用，无须先查逆向索引；不要求另建维护脚本索引。

- **Python only**: 所有新脚本必须使用 Python 3，禁止新增 `.sh` 脚本。
- **脚本分布规则**：
  - 跨 type 共享的通用脚本 → `skills/common/scripts/`（如 `run-major-*.py` 等主阶段驱动器）
  - 子阶段脚本 → 对应 skill 的 `scripts/workflow/`（如 `sub-stage-sniff.py` → `skills/common/general-strategy-skill/scripts/workflow/`；il2cpp 专用 `sub-stage-preprocess-build.py` → `skills/strategy/il2cpp-strategy-skill/scripts/workflow/`）
  - `skills/common/scripts/lib/routing.py` 提供统一的子阶段路由查询（按 name 查脚本路径）
- **子阶段命名规范**：
  - 格式：`sub-stage-<descriptive-name>.py`（**不带数字前缀**；数字归属由对应 type 的 `stages/sub-stage-register.yaml` 记录）
  - type-specific 变体：`sub-stage-<type>-<name>.py`（如 `sub-stage-cocos-static-analyze.py`）
- **子阶段路由表**：
  - 每个 type 策略 skill 只使用 `stages/sub-stage-register.yaml`；不得再创建根级 `sub-stages.yaml`，`sub_stages:` 书写顺序 = 执行顺序
  - 是 driver 动态读取的**机器可读**事实来源
  - 主键：英文 `name`（如 `'static-analyze'` / `'preprocess-build'`）；ID 字段标识编号
- 逆向项目脚本必须：`chmod +x` → 语法自检（`python3 -m py_compile`）→ 可重入（不污染环境）→ 调用 `log_*` 日志函数（`lib/common.py`）→ 通过 `lib/common.py | env.sh` 获取环境变量。
- 环境加载：Python 脚本在 `if __name__ == "__main__"` 中调用 `common.ensure_env()`。
- 工具路径：通过 `common.apktool()`、`common.adb()` 等函数获取，禁止硬编码路径。
- **索引登记**：逆向项目脚本落位后必须按 §1.9 在 `skills/common/scripts/SCRIPTS-INDEX.md` 登记（含对应 skill `scripts/README.md`）；仓库维护脚本不登记。
- **禁止手工拼接命令（与 §1.1 §1.11 一致）**：
  - ❌ Agent 用 `bash` 工具手敲 `adb shell ...` / `apktool d ...` / `apksigner sign ...` / `zipalign ...` 等命令链完成阶段操作
  - ❌ Agent 用 `python3 -c "..."` 内联代码片段完成阶段操作
  - ❌ Agent 用 `Write` 工具在 `temp/` 或项目目录写临时代码（Frida JS / awk / sed / grep 管道组合）
  - ❌ Agent 在 driver 脚本里硬编码 `skills/.../sub-stage-*.py` 路径（必须 `from routing import get_script_path`）
  - ✅ 任何阶段操作必须通过 `skills/common/scripts/run-pipeline.py` / `run-major-*.py` / `sub-stage-*.py` 入口调用
  - 例外：环境加载（`source tools/environments/env.sh`）、驱动脚本自身调用、只读探查（`ls`/`cat`/`grep`/`read`）

### 1.4 阶段记录（REQUIRED）
- **每阶段完成后立即记录**「完成即记录、不得延后」，Agent 人工写入 `status.yaml`。
- 手工/降级/跳过的操作同样记录（标注 `[MANUAL]` / `[SKIPPED]`）。
- 中断恢复：读 `status.yaml` 的 `current_stage`，从下一阶段继续；失败则重跑失败阶段。
- 不可跳阶段记录。

### 1.5 每阶段编译安装验证（REQUIRED）
- **每个阶段完成后必须编译验证**，不得将问题堆积到最后的验证阶段。
- **流程：必须通过脚本入口**（与 §1.1 §1.11 一致）：
  ```bash
  source tools/environments/env.sh
  python3 skills/strategy/<type>-strategy-skill/stages/sub_stage-dispatcher.py     # [register 驱动]重跑该 type 全部子阶段
  ./skills/common/scripts/run-major-verify.py <Name>                                # 核对 AS 工程 + patched.apk md5
  $ADB_BIN install -r crackings/<type>/<Name>/project/patched.apk                # 安装（环境变量来自 env.sh）
  ```
- 直接手敲 `./gradlew assembleRelease` / `adb install -r patched.apk` 仅作命令**示例**，实际必须通过脚本入口调用。
- 验证通过后才能进入下一阶段。
- 发现问题立即修复，修复后重新走「编译 → 安装 → 验证」闭环（重跑 `run-major-verify.py` + `run-major-accept.py`）。
- 验证结果由 Agent 人工写入 `status.yaml` 对应条目。

### 1.6 任务后固化（REQUIRED）
- **每个项目跑完**（无论成功 / 归档 / 放弃）**必须**执行以下「脚本同步」步骤，不得遗漏：
- **每次真机测试成功后强制固化（REQUIRED，通用规则）**：**任何** type、**任何**阶段的真机测试
  成功，都必须**立即**提炼本阶段的经验与脚本（不等项目跑完），**不限于**某个策略 skill 或
  固定阶段编号（如 il2cpp 的 07/09/11/13 只是具体应用示例）。
  - 机制：各 type 的 device-verify 脚本成功路径调用
    `append_experience_sync_task(name, stage, focus)`（il2cpp `stage_common.py` 提供），
    输出提示由 Agent 人工完成经验固化，不自动写文件。
  - 无脚本化的真机验证（手工 adb 测试）同样适用：成功后 Agent 人工处理固化。
  - 提炼重点随阶段而异（汉化阶段→汉化经验；SDK 清理→SDK 移除经验；UI 隐藏→UI 隐藏经验…）。

  1. **盘点本次会话生成的脚本**：所有在项目目录（`crackings/<type>/<Name>/`、`crackings/<type>/<Name>/project/`、`temp/`）新创建的 `.py` / `.js` / 可复用命令片段。
     **注意**：按 §1.1 §1.11，Agent 不应在项目目录或 `temp/` 写临时代码；本条仅覆盖「不得不写的临时探针」场景——这种临时体必须在收尾时**强制提取**为正式脚本（不允许保留 `tmp_*` / `test_*` / `try_*` 命名）。
  2. **同步到对应 skill**：按 §1.3 脚本分布规则落位——
     - 跨 type 通用脚本 → `skills/common/scripts/`
     - **type 专用脚本 → 对应 `skills/strategy/<type>-strategy-skill/scripts/common/`**（如 FM 提取脚本 → il2cpp skill `scripts/common/`）
  3. **命名规范**：统一为 `<verb>-<scope>.py`（禁止保留 `tmp_*` / `test_*` / `try_*` / 项目内临时名）。
  4. **登记索引**：在对应 skill 的 `tools-index.md`（或 `skills/common/tools-register.md`）追加脚本条目。
  5. **清理临时体**：删除项目目录 / `temp/` 中的临时脚本副本，正式脚本以 skill / `skills/common/scripts/` 内为准。

- 完成任务后回顾会话，找出可复用的命令/模式 → 提取脚本 → 按经验归属追加记录：跨 type 结论写根 [EXPERIENCES.md](./EXPERIENCES.md)，type 私有结论写对应 `<type>-strategy-skill/experiences.md`，项目事实仅写入 `crackings/<type>/<Name>/`。
- 发现 stage 脚本 bug → 修复脚本本身而非绕过去。
- 判定项目「放弃 / 超范围」时，**同样先执行上述同步**再收尾——脚本经验是项目最大资产，不得随项目丢弃。

### 1.7 工具补充
- 先查本地（`skills/common/scripts/`、`skills/common/crack-intergration-tools/`、`skills/`）→ 再查网络。
- 下载记录来源、版本、SHA-256；源码落 `source-projects/`，可执行落 `execable/`。
- 后续 Agent **必须**通过脚本调用工具，不得重复手工拼接命令（与 §1.1 §1.11 一致）。
- 缺工具脚本 → **先补脚本再调用**，禁止 Agent 在 bash 里直接跑二进制命令凑合。

### 1.8 镜像源优先（中国大陆网络）
- `pip install -i https://pypi.tuna.tsinghua.edu.cn/simple`
- `npm install --registry=https://registry.npmmirror.com`
- Gradle `distributionUrl` → `mirrors.cloud.tencent.com/gradle/distributions`（已写入 [OBJECTIVES.md §2.1 模板](./OBJECTIVES.md#21-工具版本约束)）
- 降级顺序：清华 > 阿里云 > 中科大 > 华为 → 官方源

### 1.9 脚本索引查询（REQUIRED）

> **查找脚本必须查索引表，禁止自行 `ls` 脚本目录。**

- **唯一逆向索引**：`skills/common/scripts/SCRIPTS-INDEX.md` 只收录逆向项目脚本及其必要配置、运行库，按目录分组列出脚本与角色；仓库维护脚本不属于本表范围，按 §1.3 处理。
- **查询流程**：需要查找/复用脚本时，先读 `skills/common/scripts/SCRIPTS-INDEX.md` 定位脚本路径与角色，再按路径读取；**不得** `ls` 或 `find` 枚举脚本目录来"找脚本"。
- **维护规则**（新增/移动/重命名/删除脚本时）：
  1. 按 §1.3 分布规则落位到对应 skill 目录
  2. **必须**在 `skills/common/scripts/SCRIPTS-INDEX.md` 相应分组追加/更新一行（脚本名 + 角色）
  3. 同步更新对应 skill 的 `scripts/README.md`（子索引）
  4. 命名规范 `<verb>-<scope>.py`（§1.1）
- **例外**：仅当索引表缺失该脚本且无法确认时，才允许 `ls` 对应目录做核对（并随后补登索引）。


### 1.10 引擎类型 ↔ 策略 skill 一对一（REQUIRED）

- 新 type 的规范创建入口为 [general-strategy-skill](./skills/common/general-strategy-skill/SKILL.md)：先读取根 `WORKFLOW.md` 各阶段内容，再按该 skill 的 `workflow.md` 建立、注册和验证对应 type skill。

> **每识别出一个新的引擎 / 框架类型，必须新建一条对应的规范 `<type>-strategy-skill`，禁止降级兜底。**

- **触发条件**：sniff 判定类型不在 `strategy-config.yaml` 例如某 Defold 引擎 APK（`libdmengine.so` + `game.dmanifest/game.projectc`），曾因无对应 skill 而错误降级到 android 兜底——**正是本规则要杜绝的情形**。
- **硬约束**：
  - ❌ 禁止把新引擎 APK 直接按 `android` 兜底处理。
  - ✅ sniff 命中新引擎特征（`lib<engine>.so` / 专属 assets 签名 / 专属 manifest 标志）→ 按 STRATEGY.md §4.4 新建 `<engine>-strategy-skill`。
- **新 skill 必须符合标准结构**（模板见 `skills/strategy/<type>-strategy-skill/`）：

  ```
  skills/strategy/<engine>-strategy-skill/
  ├── SKILL.md              ← 总览 + 加载顺序 + 何时调用
  ├── strategy.md           ← 引擎识别特征 / 工具链 / 坑位
  ├── workflow.md           ← 阶段流程（命令 + 验证）
  ├── tools-index.md        ← 工具索引
  ├── experiences.md        ← type 私有逆向问题经验库（仅记录该引擎独有的问题、根因、处理与验证）
  ├── scripts/{workflow,common}/
  └── assets/
  ```
- **经验库边界**：每个 `<type>-strategy-skill/experiences.md` 只记录归属于该 type 的私有逆向问题经验，
  不得写入来源 APK、项目过程、日期或可跨 type 复用的结论。跨 type 的问题经验统一写入仓库根
  [EXPERIENCES.md](./EXPERIENCES.md)；具体 APK 的事实、过程和阶段状态仍保留在
  `crackings/<type>/<Name>/` 下。
- **适用范围**：本标准结构只约束 `skills/strategy/<type>-strategy-skill/`。`skills/common/` 下的横切 skill
  （例如第三方 SDK 移除）可按其实际职责组织文档与资源，不受本目录结构的硬性要求。
- **登记要求**：
  1. `strategy-config.yaml` 新增 type 条目（sniff_patterns + stages + tools + skill）→ 登记 SCRIPTS-INDEX 阶段脚本
  2. `STRATEGY.md §1.2` 类型快速识别表加新行
  3. `skills/REGISTRY.md` Skills 注册表加新行
  4. 首次实现新引擎 APK 后把经验/脚本固化到新 skill
- **验收**：同一引擎的后续 APK 必须能被 sniff 正确路由到新 skill，不再走 android 兜底。

### 1.11 FORBIDDEN 手工拼接命令清单（REQUIRED）

> **本节是 §1.1「固化优先」的硬清单——Agent 在任何阶段都不得违反。**
> 触发本清单时，Agent 必须**先补脚本再执行**，而非「先跑了再说」。

| # | FORBIDDEN 行为 | 正确做法 |
|---|---------------|---------|
| 1 | Agent 在 `bash` 工具里手敲 `adb shell ...` / `adb install ...` / `adb logcat ...` 命令链 | 调 `sub-stage-image-device-verify.py` / `sub-stage-runtime-verify.py` 等 device-verify 脚本 |
| 2 | Agent 在 `bash` 里手敲 `apktool d ...` / `apktool b ...` / `apksigner sign ...` / `zipalign ...` | 调 `sub-stage-preprocess.py` / `sub-stage-repack-sign.py` / `sub-stage-sdk-removal.py` |
| 3 | Agent 在 `bash` 里手敲 `python3 -c "..."` 内联代码做阶段操作 | 封装为正式脚本落到 `skills/common/scripts/` 或 skill `scripts/` |
| 4 | Agent 用 `Write` 工具在 `temp/` 或 `crackings/<type>/<Name>/` 写临时 `.py` 跑一次性脚本 | 脚本必须落 `skills/common/scripts/` 或 `skills/<...>/scripts/{workflow,common}/` 后再调 |
| 5 | Agent 用 `Write` 工具写 Frida JS（`.js`）到项目目录或 `temp/` 跑一次性 hook | Frida JS 必须落 `skills/strategy/<type>-strategy-skill/scripts/common/` 或 `assets/` 后调 |
| 6 | Agent 在 `bash` 里手敲 `grep ... | sed ... | awk ... | cut ...` 管道组合做阶段分析 | 封装为 `extract-<scope>.py` / `filter-<scope>.py` 等正式脚本 |
| 7 | Agent 在 `bash` 里手敲 `unzip -l <apk> | grep ...` 做类型嗅探 | 调 `sub-stage-sniff.py`（已支持 .xapk 自动合并） |
| 8 | Agent 在 `bash` 里手敲 `keytool -genkey ...` / `apksigner verify ...` 做签名校验 | 调 `sub-stage-repack-sign.py` / `sub-stage-final-check.py` |
| 9 | Agent 在 `bash` 里手敲 `curl ...` / `wget ...` 下载工具 | 调 `skills/common/scripts/setup-local-tools.py` 或先补脚本再下载 |
| 10 | Agent 在 `bash` 里手敲 `pip install ...` / `npm install ...` 临时安装 | 写入工具脚本并登记到 `tools/crack-intergration-tools/docs/TOOLS.md` |
| 11 | Agent 手写 Frida 启动命令 `frida -U -f <pkg> ...` | 调 `skills/strategy/<type>-strategy-skill/scripts/common/frida-*.py` 模板脚本 |
| 12 | Agent 手写 `monkey -p <pkg> ...` 或 adb shell input tap 序列做真机验收 | 调通用真机验收脚本（`lib/device_verify_common.py` 已提供 `verify_app_alive`） |
| 13 | Agent 在 `bash` 里手写 Gradle 命令 `./gradlew ...` / `./gradlew assembleRelease` | 调用负责该子阶段的 `sub-stage-as-build.py`，再由 Agent 检查构建结果 |
| 14 | Agent 在 `status.yaml` 中贴大段 shell / Frida JS 命令片段而不提取成脚本 | 提取为正式脚本后只贴脚本路径 + 关键参数 |
| 15 | Agent 在 driver 脚本里硬编码 `skills/.../sub-stage-*.py` 路径 | 调 `from routing import get_script_path("sniff")`（按 name 查，driver 单一事实来源）|
| 16 | 把主阶段 driver 的退出码当作完整验收结论，或用批量 driver 隐藏子阶段脚本的真实输出 | 主阶段由 Agent 按规则人工判断；每个子阶段必须调用对应 `sub-stage-*.py`，并检查输出、产物和状态 |

**例外（允许 Agent 直接执行）**：

- `source tools/environments/env.sh`（环境加载，硬约束前置条件）
- `./skills/common/scripts/<driver>.py ...`（驱动脚本自身调用）
- 只读探查：`ls`、`cat <index.md>`、`grep <SCRIPTS-INDEX.md>`、`read` 工具读文档
- 一次性 `pip install <pkg>` 安装缺失依赖（必须在 `status.yaml` 标注，且事后补脚本固化）
- `adb devices` / `$ADB_BIN devices` 查看设备连接状态

### 1.11.1 脚本 bug 处理硬约束（REQUIRED）

> **⛔ 一句话约束**：调用脚本时遇到 bug（脚本报错 / 输出与契约不符 / 退出码非 0 / 产物缺失 / 行为异常），
> Agent **必须先修脚本本体，再验证执行，不得跳过不修复**。
> 禁止「绕过 bug 跑下一阶段」「手敲等价命令凑数」「改用相邻脚本替代」。

**触发条件**（满足其一即触发本约束）：

1. 脚本退出码非 0 且 stderr 有错误信息
2. 脚本退出码 0 但产物与契约不符（缺文件 / md5 不一致 / 状态未写入）
3. 脚本输出与 register / sub-stage-register.yaml 声明的 role 不匹配
4. 同一脚本连续 2 次失败 / 第二次出现新错误（不要陷入"先跑了再说"的循环）
5. Agent 准备「绕过去手敲」的那一刻（这是 bug 处理的绝对红线）

**正确处理顺序（REQUIRED）**：

1. **定位根因**：先 `read_file` 脚本 + 重现命令，理解脚本为何失败（不要盲目打 patch）
3. **应用最小修复**：`patch` 工具精确修改，避免顺手改其他逻辑（避免 scope creep）
4. **重跑同一脚本验证**：确认修复后退出码 0 + 产物齐全 + 状态写入
5. **继续原流程**：修好后再回到主流程跑下一阶段

**禁止行为（FORBIDDEN）**：

- ❌ 脚本报错后 Agent 直接「绕过去手敲」——必须先修脚本本体（§1.1 已声明；本节再次强化）
- ❌ 脚本失败 → 改用相邻脚本 / 改用 type 兜底策略 → 把失败标记为 `skipped` → 继续下一阶段
- ❌ 用 `--skip` / `--no-verify` / `--force` 绕过失败阶段而不修复
- ❌ 把脚本 bug 标记为 `[MANUAL]` 后不修复、直接在 status.yaml 写入「已完成」
- ❌ 修改一处脚本 bug 时顺手"重构 / 重写 / 改 API 风格"（scope creep；只修 bug）
- ❌ Agent 自己写临时脚本跑通后，忘记把脚本落到 `skills/common/scripts/` 长期化

**反例（典型坑）**：

- 脚本 A 失败 → Agent 改用脚本 B（语义不同） → 状态标记 `[skip-A]` → 下一阶段基于错误状态运行 → 后续阶段连锁失败
- 脚本 import 路径 bug（`parents[2]` 错指 skills/）→ Agent 直接 `cd ... && python3 -c` 绕过 → 临时跑通 → 项目状态标记 OK → 下一个 Agent 接手又卡在同一 bug
- 脚本 stdout/stderr 分离 bug → Agent 看不到 error → 误判成功 → 实际产物缺失 → 后续阶段基于"假成功"运行

**Bug 修复后固化（REQUIRED）**：

- 修复后必须**重跑同一脚本**验证（不跳过重跑）；
- 若修复过程发现新模式 / 新坑位 → 按 §1.6 的经验归属规则写入根 [EXPERIENCES.md](./EXPERIENCES.md) 或对应 type 私有 `experiences.md`；
- 若脚本结构 / API 需重构 → 提取改进点，单独 patch（不要在 bug 修复 commit 里混合）。

---

### 1.12 工具脚本调用前置条件（REQUIRED）

> Agent 调用任何脚本前必须**先校验三项**，避免因环境缺失导致连锁误判：

1. **环境已加载**：`source tools/environments/env.sh` 已执行（`$ADB_BIN` / `$APKTOOL` / `$JADX` 等变量非空）
2. **脚本存在**：`read` 或 `ls` 脚本路径确认；引用 `skills/REGISTRY.md` / `skills/common/scripts/SCRIPTS-INDEX.md` 索引（禁止直接 `find` 枚举）
3. **依赖满足**：Python import / 二进制依赖 / 镜像源已就绪（否则按 §1.7 补工具，不要裸跑失败）

**误判防御**：脚本调用失败时，**不要立即归因为"业务 bug"**；先排除：
- 环境变量未加载（`env.sh` 没 source）
- PYTHONPATH 不含 `skills/common/scripts/lib`（如 run-major-*.py 的 ROOT 误指）
- 工具版本不兼容（JDK / AGP / Gradle / Python 版本）
- 中文字符路径导致 AAPT2 mojibake / git 路径解析失败

**修脚本 vs 修环境**：脚本本身有 bug → 修脚本；环境配置错 → 修 env.sh / 项目配置；用户约定冲突 → 暂停确认。

---

## 2. 目录契约（硬约束）

主阶段由 Agent 按 `WORKFLOW.md` 判断、记录与验收；子阶段按当前 type 的 register → action → step 执行。目录结构不再把历史批量 driver 作为默认流程，也不固定 type 数量。

```
<repo>/
├── apks/                                  ← 原始输入，只读
├── temp/                                  ← 可清理的工作文件，按需创建
├── reference-project/<type>/<Name>/        ← 只读参考
├── crackings/<type>/<Name>/                ← 单项目工作区
│   ├── status.yaml                        ← 当前状态，由 Agent 维护
│   ├── findings.md / dir-index.yaml        ← 发现与产物索引
│   ├── stages/                            ← 各阶段报告与验收证据
│   ├── raw/                               ← 解包、分析输入与中间产物
│   └── project/                           ← 可修改工程与最终交付物
├── skills/
│   ├── REGISTRY.md                        ← skill 注册表
│   ├── strategy/<type>-strategy-skill/
│   │   ├── SKILL.md / strategy.md / workflow.md
│   │   ├── tools-index.md / experiences.md
│   │   ├── stages/
│   │   │   ├── sub-stage-register.yaml
│   │   │   ├── sub_stage-dispatcher.py
│   │   │   └── <stage-name>/
│   │   │       ├── action-register.yaml / action-driver.py
│   │   │       └── <action-name>/
│   │   │           ├── step-register.yaml / step-driver.py
│   │   │           └── step-*.py
│   │   ├── scripts/{workflow,common}/      ← type 专用 worker 与工具
│   │   └── assets/                        ← type 专用资源
│   └── common/
│       ├── scripts/                       ← 逆向共享工具、运行库和兼容入口
│       │   ├── SCRIPTS-INDEX.md / README.md
│       │   ├── lib/                       ← 公共函数与路由查询
│       │   ├── strategy/                  ← 类型配置及兼容路由数据
│       │   └── template-files/            ← 构建与注入所需模板
│       └── <name>-strategy-skill/         ← 公共阶段能力或横切参考
└── tools/
    ├── environments/                      ← Android 运行环境（处理 APK 时必需）
    ├── android-reverse/                   ← 只读知识库
    ├── crack-intergration-tools/           ← 工具源码、可执行与说明
    └── maintenance/                       ← 仓库维护，与 APK 阶段分离
        ├── scripts/                       ← 改名、迁移、文档整理等工具
        └── records/                       ← 必要的迁移记录与恢复材料
```

> 树中省略的签名文件、工程内部结构和最终保留清单以 `OBJECTIVES.md` 为准。`workflow.md` 等补充文件以具体 type skill 为准，不要求横切参考 skill 复制完整阶段树。

### 2.1 关键约束（FORBIDDEN）

- **`apks/`**：FORBIDDEN 创建/修改/解包到此目录。解包输出必须到 `crackings/<type>/<Name>/raw/`。
- **`temp/`**：仅放可清理的工作文件，按需创建；需保留的分析输入放项目 `raw/`，验收证据放项目 `stages/`。M4 按产物契约清理，不依赖“自动清理”假设。
- **`reference-project/<type>/<Name>/`**：参考项目目录，只读不修改；操作流程出现问题时对比参考其 `status.yaml`、`findings.md`、阶段产物与脚本。
- **`crackings/<type>/<Name>/`**：命名 `<NameCamelCase>` 无日期前缀，type 由 sniff 判定。状态、工程和索引可按当前阶段更新；过程证据应保留，清理仅删除契约允许的中间产物，不得整目录覆盖或无记录删除项目。
- **`tools/`**：FORBIDDEN 修改 `android-reverse/` 和 `source-projects/` 下任何文件（除非用户显式授权）。
- **`raw/`**：允许原 APK 解包出的 smali、JS、native 等内容；禁止把 Agent 新写的一次性探针当作项目产物保留。可复用实现按 §1.3 落位。
- **`skills/common/scripts/`**：不放仓库维护脚本、旧阶段迁移生成器、写死项目/机器/RVA 的一次性探针。既有兼容入口与路由数据只有确认无当前调用者后才能删除；不得用旧工具重新生成已退役阶段结构。
- **`skills/{strategy,common}/`**：仅修改当前任务所需的 skill 与共享依赖，不顺手改无关 skill；跨 type 能力与 type 私有能力按职责落位。
- **`tools/maintenance/`**：维护脚本和清理记录不进入逆向脚本索引、项目状态或逆向经验库。删除前核对引用与绝对路径，必要时保留可校验的恢复材料。

### 2.2 项目状态文件（REQUIRED）

> 每个项目**必须**维护一个 YAML 格式的状态文件，用于快速查询项目当前状态。

#### 2.2.1 单项目状态文件（`crackings/<type>/<Name>/status.yaml`）

- **生成时机**：项目初始化时建立 YAML 状态文件。已有项目保留原字段结构，不为目录整理重置状态。
- **更新时机**：Agent 每阶段完成或失败后立即记录，通过与否须有产物和验证证据。
- **恢复信息**：必须能查到 `current_stage`、`completed_stages`、`failed_stages` 及失败原因；字段层级与当前项目的消费脚本保持一致。
- **内容格式**：

```yaml
# 示例：现有项目保留其字段层级与兼容字段
project:
  name: "<Name>"
  source_apk: "apks/<原文件名>.apk"
  md5: "<md5值>"
  type: "<type>"  # android / il2cpp / unity-mono / cocos2dx / cocos-creator / unreal / flutter / xamarin / air / defold
  created: "<创建日期>"
  last_updated: "<最后更新日期>"
status:
  phase: "<当前主阶段>"  # sniff / assess / final-check / cleanup
  current_stage: "<当前阶段名>"  # 如 sdk-network-device-verify，使用当前 type register 的 name
  grade: "<难度评级>"   # S / A / B / C / D / F
  is_delivered: false
  is_archived: false
  completed_stages:
    - "M1"
    - "M2"
    - "01"
    - "02"
    - "03"
  failed_stages: []
artifacts:
  patched_apk: false
  as_project: false
  findings_md: true
  dir_index_yaml: true
```

#### 2.2.2 维护规则

- **记录责任**：由 Agent 理解结果后维护状态；旧初始化/更新辅助脚本不能代替验收判断，不得自动写入未验证的完成状态。
- **幂等更新**：重复更新同一项目状态不会产生重复条目。
- **手动维护**：手工操作时同样**必须**更新状态文件（标注 `[MANUAL]`）。

---

## 3. APK 命名归一

> **执行规则**（在创建 `crackings/<type>/<Name>/` 之前执行，结果在 `status.yaml` 声明）：
> - 只保留字母数字，驼峰拼接。去除版本/来源后缀。
> - 示例：`Can+You+Escape+2_3.9_APKPure.apk` → `CanYouEscape2`

| **<type> 父目录规则**：项目目录**必须**放入 sniff 判定 type 的同名父目录下
| （如 `il2cpp` / `android` / `air` / `defold` / `cocos2dx` / `unity-mono` / `libgdx` / `gamemaker` / `corona` 等），
| 即 `crackings/<type>/<Name>/`（含 `project/` 子目录），**禁止**直接放在 `crackings/<Name>/`。
| type 值以主阶段 1（sniff）输出为准（STRATEGY.md §1.2）。

> **本规则同时是产出约束**——`crackings/<type>/<Name>/project/` 目录名与 `crackings/` 目录名（含 <type> 父目录）必须一致；详见 [OBJECTIVES.md §0 总目标](./OBJECTIVES.md#0-总目标)。

---

## 4. 文档分层导航（REQUIRED）

> 工作区采用分层文档结构。Agent 必读顺序：

| 顺序 | 文档 | 角色 |
|------|------|------|
| 1 | [AGENTS.md](./AGENTS.md)（本文件） | agent 行为约束 + 索引 |
| 2 | [STRATEGY.md](./STRATEGY.md) | 类型 sniff + 难度评级 + skill 路由 |
| 3 | [WORKFLOW.md](./WORKFLOW.md) | 4 大主阶段 + 15 子阶段主流程 |
| 4 | [EXPERIENCES.md](./EXPERIENCES.md) | **APK 逆向问题经验库（跨 type 共享）**——只记录可跨 type 复用的问题、根因、处理和验证；解包、分析、改造、构建、安装、启动或验证异常时按需检索 |
| 5 | **`skills/strategy/<type>-strategy-skill/`** | 当前 type 的完整工作流，以及该 type 的 `experiences.md` 私有问题经验库 |
| 6 | [OBJECTIVES.md](./OBJECTIVES.md) | 验收硬指标 + 工具链版本 + 风险回退 |

> **核心原则**：根文档**只放规则/约束/索引**，类型细节全部下沉到 skill。
>
> **🔴 逆向问题参考**：[EXPERIENCES.md](./EXPERIENCES.md) 是所有 type 共享的逆向问题经验库。
> 在解包、类型识别、静态/动态分析、SDK 清理、资源汉化、构建、签名、安装、启动或真机验证异常时，先检索对应分类再排查。
> 新增可复用经验必须使用该文件规定的固定条目格式追加；具体 APK 事实、项目过程和阶段状态仍记录在 `status.yaml`、`findings.md` 与阶段产物中。
>
> **经验分流**：根 `EXPERIENCES.md` 记录跨 type 的通用结论；`skills/strategy/<type>-strategy-skill/experiences.md` 记录只适用于该引擎的私有结论；`crackings/<type>/<Name>/` 只记录具体 APK 的事实、过程、日期和产物。前两类经验文档均不得包含来源 APK 或项目叙事。

---

## 5. Status.yaml 协议（多 Agent 协同核心）

`status.yaml` 是 `crackings/<type>/<Name>/` 下唯一的协调文件。任何 Agent 接手前**必须先读** `status.yaml`，知道当前做到哪儿了。

### 5.1 最小骨架
- **项目元信息**：name / type / source_apk / md5 / phase / stage / grade
- **已完成阶段**：`completed_stages` 列表
- **当前阶段**：`current_stage`
- **上下文快照**：已识别的关键类/函数/偏移/hook 位置/反调试点（记录在 `findings.md`）
- **风险与注意事项**

### 5.2 协同规则
- Agent 人工维护：`status.yaml` 由 Agent 读写，不通过脚本自动写入
- 每阶段完成后更新 `current_stage` 和 `completed_stages`
- 修正结论时：追加新条目，保留历史记录
- **文件分工**：
  - `status.yaml` = 机器可读状态（阶段/评级/产物路径）
  - `findings.md` = 结构化知识（类型/协议/反调试/加密点）

---

## 6. 工具路径索引（MUST-LOAD）

> 工具路径与文档索引是统一入口，**Agent 首次进入工作区时必须加载**。
> 所有工具的路径、功能、用途请查阅：

| 文件 | 角色 | 加载要求 |
|------|------|---------|
| `tools/crack-intergration-tools/docs/TOOLS.md` | **工具注册表**：每工具一子目录（INDEX.md + 架构/API/工作流嵌入） | **MUST-LOAD**（新增工具只在此追加） |
| `tools/crack-intergration-tools/source-projects/` | 上游源码（READONLY） | 索引指向，不直接编辑 |
| `tools/crack-intergration-tools/execable/` | 已编译可执行文件 | 索引指向，不直接枚举 |

> **维护规则**：新增工具时，在 `tools/crack-intergration-tools/docs/TOOLS.md` 工具表中追加一行，并在 `docs/<tool>/` 下创建文档子目录。
> Agent 不得在 AGENTS.md / STRATEGY.md / WORKFLOW.md 中硬编码工具路径表——以 `TOOLS.md` 为准。

---

## 7. Skills 集成表（MUST-LOAD）

> Skills 注册表已迁出到独立文件。**Agent 首次进入工作区时必须加载**。
> 新增/修改 skill 后必须更新注册表，核心文件不维护 inline 表。

| 文件 | 角色 | 加载要求 |
|------|------|---------|
| `skills/REGISTRY.md` | **Skills 注册表**：工作区 skill + 全局 skill 完整索引 | **MUST-LOAD** |
| `skills/strategy/` | type 策略 skills（每种 APK 类型一个） | 按需加载 |
| `skills/common/` | skills 通用资源（跨 type 横切） | 按需加载 |
| `~/.agents/skills/` | 全局 skills（工作区外） | 按需加载 |

**维护规则**：新增 skill 时在 `skills/REGISTRY.md` 追加一行。Agent 不得在 AGENTS.md 中硬编码 skill 表。

---

## 8. 横切参考 skill — Agent 记录责任

- 静态分析后，Agent 必须逐项判断第三方 SDK 是否会影响单机核心玩法，并将项目级依据与决定写入 `findings.md`。
- SDK 分类、依赖风险和特征库格式参考 [third-party-removal-strategy-skill](./skills/common/third-party-removal-strategy-skill/SKILL.md)。
- 实际清理阶段、脚本选择、构建和设备验收只能遵循已路由 type 的 workflow；common SDK skill 不定义执行流程。
- 去功能点的分类、保留边界与依赖判断参考 [feature-removal-strategy-skill](./skills/common/feature-removal-strategy-skill/SKILL.md)；具体修改、脚本选择和第 07/08 阶段验收只能遵循已路由 type 的 workflow。
- 功能点领域的跨 type 私有经验写入该 common skill 的 `experiences.md`；type 专属实现限制写对应 type 的 `experiences.md`；项目事实仍只写项目记录。
- 汉化的分类、质量边界与经验参考 [hanization-strategy-skill](./skills/common/hanization-strategy-skill/SKILL.md)；字体、文本、图片处理及第 10–15 阶段验收只能遵循已路由 type 的 workflow。
- 新的可跨项目 SDK/native 特征追加到该 common skill 的 references；SDK 清理领域私有问题写其 `experiences.md`；项目事实不得写入经验库。

---

## 9. 与其他文档的边界

| 文件 | 角色 |
|------|------|
| **AGENTS.md（本文件）** | **agent 行为约束**：怎么读环境、跑脚本、记录、协同、维护工具与经验库 |
| [STRATEGY.md](./STRATEGY.md) | **策略路由表**：类型识别、嗅探、难度评级、通用策略、风险模式 |
| [WORKFLOW.md](./WORKFLOW.md) | **工作流操作手册**：4 大主阶段、15 子阶段、验证命令、中断与恢复 |
| [OBJECTIVES.md](./OBJECTIVES.md) | **产出约束**：交付物长什么样、六条验收硬指标、阶段产物清单、风险与回退 |
| [EXPERIENCES.md](./EXPERIENCES.md) | **跨 type 通用逆向问题经验库**：只记录可复用的问题、根因、处理与验证，不记录项目事实 |
| **`skills/strategy/<type>-strategy-skill/`** | **每个类型的完整工作流与私有经验库**（SKILL.md + strategy.md + workflow.md + tools-index.md + experiences.md + scripts/{workflow,common}/ + assets/）；其中 `experiences.md` 只记录该 type 私有经验 |
| **`skills/REGISTRY.md`** | **Skills 注册表**：工作区 skill + 全局 skill 索引 |

**调用顺序**：Agent 接到逆向任务 →
1. 读 **AGENTS.md**（本文件，约束 + 索引） →
2. 读 [STRATEGY.md](./STRATEGY.md)（sniff + 评级 + 路由到 skill） →
3. 读 [WORKFLOW.md](./WORKFLOW.md)（4 大主阶段 + 15 子阶段流程） →
4. 按需加载注册表 `skills/REGISTRY.md` →
5. 加载对应 skill：`skills/strategy/<type>-strategy-skill/`（SKILL.md → strategy.md → workflow.md → tools-index.md；遇到 type 私有问题再读 experiences.md） →
6. 遇到可复用逆向问题时先检索 [EXPERIENCES.md](./EXPERIENCES.md)，再按归属写入根经验库或 type 私有经验库；工作中对照 [OBJECTIVES.md](./OBJECTIVES.md)（产物清单 + 验收清单） → 随用随查 `tools/crack-intergration-tools/docs/TOOLS.md`（工具注册表）。

---

## 10. 项目级 git 集成（REQUIRED · 子阶段提交 + 远程推送）

> **一句话约束**：每个 `crackings/<type>/<Name>/` 项目**自带一个嵌套独立 git 仓库**，
> 父仓库整棵忽略 `crackings/`（见 `.gitignore`）。Agent 在每个子阶段完成后**必须**调用
> `commit-project-stage.py` 提交一次（形成可回滚节点）；全项目跑完后**等待用户填入
> remote URL** 再调用 `push-project-remote.py` **仅推 `project/` 子目录**到远程协作仓库；
> 每个主阶段（M1/M2/M3/M4）结束时**必须**调用 `verify-commit-push-major-stage.py`
> 做提交 + 推送的双重校验。

### 10.1 硬约束（REQUIRED）

- **每个处理项目自带独立 git 仓库**：`crackings/<type>/<Name>/.git/`（嵌套）。
  - 父仓库 `.gitignore` 已 `crackings/` 整棵忽略 → 项目仓库与父仓库互不干扰。
  - 项目级 `.gitignore` 由 `init-project-git.py` 生成：忽略 `raw/` / `project/build/` /
    `project/.gradle/` / `project/app/src/main/jniLibs/` 等体积产物与构建产物；
    只追踪 `status.yaml` / `findings.md` / `dir-index.yaml` / `stages/` 阶段产物 / 脚本 / 报告。
- **每个子阶段完成后必须 commit 一次**——调用：

  ```bash
  python3 skills/common/scripts/commit-project-stage.py --name <Name> --stage <stage-id> [--type <type>] [--message "备注"] [--dry-run]
  ```
  - 提交信息格式：`stage: <stage-id> — 备注`（脚本自动生成）。
  - `--stage` 必填（与 `stages/sub-stage-register.yaml` 的 `id` 对齐，如 `01-sniff` / `05-image-device-verify`）。
  - 提交前有"工作区无变更"短路；不污染历史。
- **主阶段（M1/M2/M3/M4）结束后必须做提交 + 推送校验**：
  ```bash
  python3 skills/common/scripts/verify-commit-push-major-stage.py --name <Name> [--type <type>]
  ```
  - 校验两件事：
    1. **`sub-stage-register.yaml` 的每个 stage id 都至少 1 个 commit**（按提交信息首段 `stage: <id>` 匹配）
    2. **`remote origin` 已设置 + `origin/<branch>` 至少 1 个 commit**（即已真推送到远程）
  - 校验失败时给出每个缺失 stage 的修复命令 + remote 设置命令。
- **全项目跑完后等待用户填入 remote URL 才能推送**（脚本不内置任何 remote）：
  ```bash
  python3 skills/common/scripts/push-project-remote.py \
    --name <Name> [--type <type>] \
    --remote <user-provided-url> [--branch main] [--dry-run]
  ```
  - **仅推 `crackings/<type>/<Name>/project/` 子目录**——技术方案：临时启用
    `git sparse-checkout`（非 cone + `project/*`）→ `git push origin HEAD:refs/heads/<branch>`
    → `sparse-checkout disable` 恢复完整工作区视图（先生拍板方案，零额外存储）。
  - 推送前 `git ls-files project/` 列出真正要推送的文件清单；为空则拒绝推送（防误清空）。
  - 推送前 `git ls-remote <url>` 探测远程可达性；失败立即返回。
  - 推送完成后**询问是否恢复完整视图**（默认 Y）——`--yes` 跳过询问。
  - 异常中断恢复：`--restore-only`（脚本入口）。
  - **冲突时推送策略**：`--force-with-lease`（拒绝硬覆盖未被本机看到的新远程 commit）。
- **项目级 `.gitignore` 由 `init-project-git.py` 自动生成**——禁止人工手写覆盖（除非追加白名单）。

### 10.2 三个脚本的分工与依赖

| 脚本 | 何时调用 | 角色 |
|------|---------|------|
| `skills/common/scripts/init-project-git.py` | 项目初始化（首次进入 `crackings/<type>/<Name>/` 时） | `git init` + 项目级 `.gitignore` + 剥离内嵌 `.git` + 首次基线 commit |
| `skills/common/scripts/commit-project-stage.py` | **每完成一个子阶段** | `git add -A` + `git commit -m "stage: <id>"` + 显示 HEAD hash + 回滚命令 |
| `skills/common/scripts/verify-commit-push-major-stage.py` | **每个主阶段（M1–M4）结束** | 读 register 阶段 id 列表 → 校验每个 id 都 commit 过 + remote 已设 + 已推 |
| `skills/common/scripts/push-project-remote.py` | 全项目跑完、用户填入 remote URL 后 | sparse-checkout 临时切到 `project/*` → set remote → push → 恢复 |

### 10.3 标准流程（嵌入到主流程）

```bash
# 1. 项目初始化（一次性）
python3 skills/common/scripts/init-project-git.py --name <Name> [--type <type>]

# 2. 每个子阶段完成后（loop）
python3 skills/common/scripts/commit-project-stage.py --name <Name> --stage <stage-id> [--message "备注"]

# 3. 每个主阶段结束后（loop）
python3 skills/common/scripts/verify-commit-push-major-stage.py --name <Name> [--type <type>]
#   → 若校验失败：按脚本输出补 commit + 设 remote + 重推

# 4. 全项目跑完 → 等待用户填入 remote URL → 仅推 project/
python3 skills/common/scripts/push-project-remote.py --name <Name> --remote <url> [--branch main] [--dry-run]
```

### 10.4 禁止行为（FORBIDDEN）

- ❌ 在 `crackings/<type>/<Name>/` 内手工 `git add` / `git commit` 阶段产物——必须调 `commit-project-stage.py`（保证提交信息格式统一，校验脚本才能匹配）。
- ❌ 直接把 `crackings/` 全棵推到父仓库的某个分支——父仓库 `.gitignore` 整棵忽略，提交了也会被忽略；项目仓库必须独立 init。
- ❌ 把 `raw/` / `project/build/` / `project/.gradle/` / `project/app/src/main/jniLibs/` 等体积产物 commit 入库——项目级 `.gitignore` 已经拦，但仍要主动检查 `git ls-files`。
- ❌ 推送时**不传 `--remote`**或绕过 `push-project-remote.py`——脚本内置 ls-remote 探测、sparse-checkout 复位、推送失败保留现场三项安全机制。
- ❌ 推送完不调用 `verify-commit-push-major-stage.py` 二次校验——可能 remote 已 set 但实际 0 commit 推送成功。
- ❌ 推送前不与用户沟通直接选 `--branch`——默认 `main`，但用户可能指定其他分支名。
- ❌ 用 `--force` 而非 `--force-with-lease`——本脚本默认 `--force-with-lease`，禁止临时改成 `--force`（会覆盖远程未被本机感知的 commit）。

---

## 1.14 用户说"应用"时的快速操作

| 触发词 | 动作 | 命令 |
|--------|------|------|
| "应用底部随机提示" / "应用 tip banner" | 给当前项目加 installTipBanner() | `python3 skills/strategy/il2cpp-strategy-skill/scripts/common/add-random-tip-banner.py <Name> --type <type>`（已存在则跳过） |
| "应用 frida 侦察" | 启动 frida 侦察 GameObject 名 | `python3 skills/strategy/il2cpp-strategy-skill/scripts/common/frida-recon-gameobjects.py --device <serial> --package <pkg>` |
| "应用 Realme 闪退止血" | 应用 patch-firebase-realme-fix 一键修复 | `python3 skills/strategy/il2cpp-strategy-skill/scripts/common/patch-firebase-realme-fix.py <Name> --type <type>` |

"应用"语义：**重新跑 build 让上一次的 Java/Kotlin 改动生效**，不是仅"加 import"。

执行后必须:
1. `python3 skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-as-build.py <Name>` 编译
2. `source tools/environments/env.sh && $ADB_BIN install -r -d crackings/<type>/<Name>/project/patched.apk` 安装
3. 截图确认（如有视觉改动）

## 1.15 检索逻辑：用户说"处理 / 继续处理"指定项目时

> **所有项目定位必须通过脚本 `skills/common/scripts/find-project.py`，禁止手工 `ls apks/` / `grep` 检索。**
> 该脚本按关键词归一匹配 `apks/` 的 APK 与 `crackings/` 已有工程，读 `status.yaml` 给出断点与续跑入口。

### 场景 A：用户说"处理 XX"（处理指定项目，可能为新工程）

1. **优先在 `apks/` 检索 XX**：`python3 skills/common/scripts/find-project.py --name XX`
   - `apks/` 命中 APK → **从该 APK 开始处理**：走完整主流程
     （`run-pipeline.py <apk> <Name>` → M1 sniff→M2 assess→M3 final-check→M4 cleanup）
2. `apks/` 未命中 → **在 `crackings/` 检索 XX**（同脚本自动转入）：
   - 命中工程 → 读 `crackings/<type>/<Name>/status.yaml`，**根据记录的子阶段重新处理**，从断点继续走剩下子阶段
   - 未命中 → 提示用户核对项目名 / APK 池
3. `apks/` 与 `crackings/` 都命中时：默认按 `apks/` 新跑，但需提示用户已有工程（新跑 or 断点续跑二选一）。

### 场景 B：用户说"继续处理 XX"（继续处理指定项目）

1. **优先在 `crackings/` 检索 XX**：`python3 skills/common/scripts/find-project.py --name XX --resume`
2. 命中 → 读 `crackings/<type>/<Name>/status.yaml`，**根据记录的子阶段继续处理**，走完剩下子阶段
3. 未命中 → 降级回场景 A：查 `apks/` 是否能当新工程处理；仍无则提示用户。

### 检索与断点规则

- **名称匹配**：`find-project.py` 归一化匹配（去版本/来源后缀、CamelCase、大小写/空格不敏感）。
- **断点依据**：`crackings/<type>/<Name>/status.yaml` 的
  `current_stage` / `completed_stages` / `failed_stages` / `skipped`。
- **续跑动作**：先重跑 `failed_stages`，再从 `current_stage` 继续剩余子阶段；
  遵循 [WORKFLOW.md §4](./WORKFLOW.md) 断点续做约束（失败阶段仅重跑失败 + 依赖阶段）。
- **续跑入口**：[register 驱动] `python3 skills/strategy/<type>-strategy-skill/stages/sub_stage-dispatcher.py`；完全重跑 `python3 skills/common/scripts/crack.py <apk> --from-start`。
- 每个续跑的阶段完成后照常更新 `status.yaml`（§1.4）并逐阶段编译/真机验证（§1.5）。
