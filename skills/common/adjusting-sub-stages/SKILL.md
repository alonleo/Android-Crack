---
name: adjusting-sub-stages
description: Use when adding, removing, reordering, renaming, or replacing Android reverse-engineering sub-stages globally or for one existing engine type.
---

# 调整子阶段

## 核心原则

先按 `name` 确定阶段身份，再按最终顺序生成连续 `id`。注册表修改只是入口；完成标准是路由、实现、消费者、状态编号、文档和验证全部一致。

开始前读取根 `AGENTS.md`、`WORKFLOW.md`、`skills/common/scripts/SCRIPTS-INDEX.md`，再读取目标 register、`strategy-config.yaml` 和相关 type workflow。仓库维护脚本放 `tools/maintenance/scripts/`，不登记逆向脚本索引。

## 判断范围

| 请求 | 变更范围 |
|---|---|
| 替换一个 type 某阶段的 script、action 或 steps | 只改该 type register、阶段目录、strategy config 中该 type 的详情、type workflow 和消费者 |
| 一个 type 对已有公共阶段改变顺序或是否参与 | 改目标 type register 与该 type 的 routing/details；同时验证公共 `id → name` 路由仍能表达该顺序 |
| 新增、删除、重命名或重排所有 type 的阶段 | 改主表、公共 fallback、所有 type register、所有 routing/details 和根工作流 |
| 新增仅一个 type 拥有的新阶段名 | 当前主表仍是公共 `id → name` 事实源；先扩展路由模型或将能力放入现有阶段的 type-specific action，不能复用冲突 ID |

## 影响面清单

按以下顺序建立改动清单，不要看到文本命中就直接批量替换：

1. **事实源**：`skills/common/scripts/strategy/sub-stages.yaml`、公共 `stages/sub-stage-register.yaml`、目标 type 的 register。
2. **配置层**：`skills/common/scripts/strategy/strategy-config.yaml` 的 `stage_routing`、`mandatory`、`stage_details`。
3. **实现层**：`stages/<name>/action-register.yaml`、action driver、step register、steps，以及注册的 `sub-stage-*.py`。
4. **消费者**：用 `rg` 搜索阶段名、`NN-name`、脚本名、输出目录、`stage_path("name")`、报告中的 `stage` 和 `stage_id`。判断消费者应迁移、内聚到相邻阶段、兼容读取历史产物，还是删除。
5. **说明层**：根 `WORKFLOW.md`、`AGENTS.md` 中的数量和验收编号、type workflow、`skills/REGISTRY.md`。只有逆向脚本增删时才更新 `SCRIPTS-INDEX.md` 和对应 scripts README。
6. **历史层**：默认不改 `crackings/`、`EXPERIENCES.md`、type `experiences.md` 和历史重构文档；它们记录当时事实。需要兼容旧项目时显式读取旧目录，不再通过已删除阶段的路由查询。

## 实施规则

- 全局变更先写可重入的 Python 维护脚本，必须有 preview、apply、check；小范围定点修改使用 `apply_patch`。
- 删除阶段前先处理下游输入。若后续阶段仍需要其产物，把必要分析并入最早的实际消费者或定义新的稳定输入来源。
- 重新编号时同时更新产物目录、日志标签、报告字段、设备验证 `stage_id`、测试期望和文档交叉引用。
- 保留工作区已有修改。只删除已确认属于目标阶段的目录和文件。
- 脚本索引用于查找逆向脚本；不要枚举脚本目录寻找替代实现。

## 验证合同

完成前必须验证：

1. YAML 可解析；作用域内阶段名称符合预期，ID 为 `01..N` 连续且唯一。
2. `stage_routing`、`mandatory`、`stage_details` 与对应 register 一致。
3. `routing.id_to_name()`、按 name/ID 查脚本、`list_all_stages(type)` 返回预期结果。
4. 每个已注册阶段目录、action driver、action/step register 和声明脚本存在。
5. 修改过的 Python 可编译，相关契约测试通过。
6. `rg` 只在明确保留的历史记录或兼容读取中找到旧阶段名/编号；代码中的报告 ID 与新 register 一致。
7. 再运行一次维护脚本 preview，结果必须为零改动。

结构迁移只需做静态与契约验证。只有同时处理具体 APK 项目时，才执行构建、安装和真机阶段，并按 `AGENTS.md` 写 `status.yaml`。

## 常见遗漏

| 现象 | 原因 | 处理 |
|---|---|---|
| register 是新编号，报告仍写旧编号 | 只改了路由 | 搜索 `stage`、`stage_id`、日志标签并按阶段名校准 |
| 删除阶段后后续流程失败 | 消费者仍依赖旧产物 | 迁移生产逻辑或定义兼容输入，不能只删目录 |
| 单 type 调度按 name 成功，按 ID 错误 | 公共 ID 表无法表达 type 独占拓扑 | 调整路由模型或复用已有公共阶段名 |
| 批量替换改坏经验和项目记录 | 未区分规范与历史 | 排除历史层，仅添加必要兼容说明 |
