# 去功能点参考索引

本 skill 集中维护去功能点知识和共用阶段接口；实际脚本由 type 注册表路由。

| 资源 | 用途 |
|---|---|
| [references/feature-removal-checklist.md](references/feature-removal-checklist.md) | Agent 阅读的逐项清单，由 YAML 生成 |
| [references/feature-removal-checklist.yaml](references/feature-removal-checklist.yaml) | 脚本唯一数据源；稳定 ID、关键词、type、启用状态和建议策略 |
| [scripts/README.md](scripts/README.md) | 增删改查、同步文档、阶段加载与验证用法 |
| [strategy.md](./strategy.md) | 功能分类、保留边界、依赖判断与验收关注点 |
| [experiences.md](./experiences.md) | 去功能点领域的跨 type 私有经验 |
| [references/engine-notes.md](references/engine-notes.md) | 12 个 type 的实现方案、定位方法和限制 |
| [references/stage-contract.md](references/stage-contract.md) | 07/08 阶段的共同步骤、产物与验收 |
| `skills/strategy/<type>-strategy-skill/workflow.md` | 阶段位置与注册表执行入口 |
| [统一脚本索引](../scripts/SCRIPTS-INDEX.md) | 查找正式脚本，禁止手工拼接阶段命令 |
