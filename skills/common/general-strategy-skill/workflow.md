# 创建新 type skill 的工作流

本文件描述如何构建策略。待创建 type 的 APK 处理阶段以根 [WORKFLOW.md](../../../WORKFLOW.md) 为来源，交付约束以 [OBJECTIVES.md](../../../OBJECTIVES.md) 为来源。

## Agent 生成入口

正式脚本：[scripts/create-type-skill.py](scripts/create-type-skill.py)。依赖 Python 3、PyYAML，输出目录固定为仓库 `skills/strategy/<type>-strategy-skill/`。

```text
python skills/common/general-strategy-skill/scripts/create-type-skill.py --type <type> --label <显示名>
python skills/common/general-strategy-skill/scripts/create-type-skill.py --type <type> --label <显示名> --apply
python skills/common/general-strategy-skill/scripts/create-type-skill.py --type <type> --verify
```

- 默认预览，返回计划中的文件列表；`--apply` 一次生成整个 skill 草稿，拒绝覆盖已有目录；`--verify` 静态检查现有生成结果。
- stdout 为单个 JSON 对象，stderr 为日志。`status` 为 `preview`、`created_draft`、`scaffold_valid` 或 `error`；失败退出码为 1。
- 脚本读取根 WORKFLOW.md 的主阶段和子阶段表，生成文档、全部阶段注册表、action/step 调度脚本及明确失败的待实现 worker。
- 生成结果的 `runtime_validated` 为 false。未实现 worker 返回 `implementation_required`，退出码为 2；不写成功状态，也不跳过该阶段。
- 新引擎识别规则不能从 type 名称推导，因此生成器不会激活生产 sniff 路由。Agent 必须继续读取生成的 `registration.md`，完成实现后更新其中列出的注册文件。
- 重复运行 `--apply` 会失败以保护 Agent 已修改的文件；中断后应检查现有目录，不使用强制覆盖。

脚本合同自检：`python tools/maintenance/scripts/verify-type-skill-generator.py`。自检在临时隔离目录生成示例，不在生产策略目录注册示例 type。

## 1. 确定 type 和识别证据

读取 [STRATEGY.md](../../../STRATEGY.md)、[策略配置](../scripts/strategy/strategy-config.yaml) 和 [REGISTRY.md](../../REGISTRY.md)。核对 APK 的 native 库、资源签名、Manifest 和运行时特征，区分新引擎、已知引擎变体和真正的原生 Android。

确定小写连字符 type 名称，检查目录和配置冲突。已存在时修订对应策略，不覆盖已有工作。项目证据写入对应 `crackings/<type>/<Name>/`；通用技能文档只保留适用特征及可复用结论。

## 2. 逐阶段形成设计

完整读取根 `WORKFLOW.md` 的主阶段表、子阶段表、验证及恢复章节。对每个阶段，在新 type 的 workflow 中写明：

| 内容 | 必须回答的问题 |
|---|---|
| 阶段对应 | 根工作流中的 ID、name、目的和通过条件是什么？ |
| 输入和前置条件 | 需要哪些上一阶段产物、环境、工具和设备？ |
| type 实现 | 该引擎的代码或资产格式如何处理，哪些公共实现可复用？ |
| 调用链 | register 指向哪个 action-driver、step-driver 和正式脚本？ |
| 产物 | 文件路径、格式、状态记录以及判断有效性的证据是什么？ |
| 验证和恢复 | 如何构建、安装和验证，失败后从哪里恢复？ |

当前根流程包含 M1–M4 和子阶段 01–15。创建时重新读取文档，不从本段数字推导阶段内容。不能删掉困难阶段；某项功能不存在时也要提供判定证据，并执行该阶段要求的验证。

SDK、去功能点及汉化阶段分别按需读取相应公共 skill。借鉴已有 type 时只复用经过检查的框架和公共接口，重新确定新引擎的函数定位、资源处理与验证方法。

## 3. 建立规范目录

```text
skills/strategy/<type>-strategy-skill/
├── SKILL.md
├── strategy.md
├── workflow.md
├── tools-index.md
├── experiences.md
├── stages/
│   ├── sub-stage-register.yaml
│   ├── sub_stage-dispatcher.py
│   └── <stage>/
│       ├── action-driver.py
│       ├── action-register.yaml
│       └── <action>/
│           ├── step-driver.py
│           ├── step-register.yaml
│           └── step-<name>.py
├── scripts/
│   ├── README.md
│   ├── workflow/
│   └── common/
└── assets/
```

- `SKILL.md`：合法 YAML frontmatter、适用特征、范围、加载顺序和真实存在的相对链接。
- `strategy.md`：引擎识别、格式、工具选择、技术约束和差异处理。
- `workflow.md`：完整的 type 阶段执行权威文档，包含第 2 节的逐阶段设计。
- `tools-index.md` 与 `scripts/README.md`：真实工具、脚本、用途和依赖；不得登记不存在的实现。
- `experiences.md`：仅 type 私有经验；没有经验时说明尚未积累，不编造成功案例。
- `assets/`：实际需要的模板或资源；脚本在各自职责目录落位。

先通过统一脚本索引查找可复用的 dispatcher、action、step 基础设施，并读取注册表消费者确认字段。不要根据旧注释猜测 schema，也不要把其他 type 名称替换后就视为实现完成。

## 4. 接入脚本与注册

按根 AGENTS 的脚本规则，通过正式 Python 脚本完成重复性生成或迁移操作；新增工具先登记到统一脚本索引和子索引。

1. 实现每个阶段的 action 和 step。公共逻辑可复用本 skill 的脚本，但必须先确认目标文件存在、接口适配。
2. 建立 `stages/sub-stage-register.yaml`，按根工作流顺序声明阶段；它是当前 type 的唯一子阶段事实来源，必须校验默认 action、step 顺序及目标路径。
3. 确认 dispatcher 和公共路由器均读取 `stages/sub-stage-register.yaml`；不得再创建 type 根级 `sub-stages.yaml`，避免两套阶段定义。
4. 在 `skills/common/scripts/strategy/strategy-config.yaml` 中登记 type、识别模式、skill、阶段与工具，并检查 sniff 优先级及现有类型冲突。
5. 同步根 `STRATEGY.md` 类型表和 `skills/REGISTRY.md`；更新 `tools-index.md`、统一 `SCRIPTS-INDEX.md` 与脚本子索引。
6. 主阶段由 Agent 负责判断、记录和验收；具体子阶段通过注册的调度链执行，不以公共默认路径覆盖引擎差异。

## 5. 验证后交付

先完成静态检查：frontmatter、相对链接、目录命名、Python 语法、注册 schema、阶段顺序、verify 标记、action/step 路径以及默认方案存在性。与根工作流逐项核对阶段目的和通过条件，不能只数目录数量。

使用新引擎样本检验 sniff 正确路由，并使用已知 type 样本检查识别冲突。实际项目从 M1 开始，按 type workflow 完成全部阶段，逐阶段检查真实产物及状态；每次真机验证成功后固化经验。

工具、输入或设备不满足条件时，准确记录尚未验证的部分。设备验证不得降级或跳过；暂停在失败阶段并保留恢复信息。仅创建规范 skill 并通过静态检查时，交付结论必须写明“未完成完整 APK/真机验证”。
