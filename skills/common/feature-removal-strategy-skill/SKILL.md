---
name: feature-removal-strategy-skill
description: Use when an Android game reverse-engineering task must assess optional UI entries, popups, branding, or language selectors for removal without damaging core gameplay.
---

# 去功能点策略参考

**Agent 阅读：[feature-removal-checklist.md](references/feature-removal-checklist.md)**。
**脚本数据：[feature-removal-checklist.yaml](references/feature-removal-checklist.yaml)**（功能点、弹窗、语言及验收项）。

YAML 为唯一数据源。清单增删改查必须使用 [manage-feature-checklist.py](scripts/manage-feature-checklist.py)，写入时自动生成同名 Markdown；不要手工编辑生成文档。CLI 参数和字段约束见 [脚本使用说明](scripts/README.md)。

本 skill 集中维护去功能点的分类、保留边界、依赖判断、各 type 实现要点与 07/08 阶段共用接口。实际脚本仍由已路由 type 的注册表选择；阶段位置以该 type 的 workflow 为准。

## 使用边界

- 适用于非核心玩法的推广、联网、账户、广告、付费引导、品牌与冗余语言入口，以及阻断核心玩法的相关弹窗。
- 不把“清单命中”视为删除授权：先按 [strategy.md](./strategy.md) 判断该项是否影响核心玩法或必要设置。
- 引擎差异统一记录在 [engine-notes.md](references/engine-notes.md)，不要在各 type 重新维护一份去功能点清单。引擎脚本保留在原 type，由注册表调度。
- 本目录不记录具体 APK、项目过程、日期、命令或临时方案；功能点领域私有问题写入 [experiences.md](./experiences.md)，跨 type 问题写仓库根 `EXPERIENCES.md`。

## 加载顺序

1. [feature-removal-checklist.md](references/feature-removal-checklist.md) 与 [strategy.md](./strategy.md)：逐项检查、保留边界及依赖判断。
2. [engine-notes.md](references/engine-notes.md)：按 android、il2cpp、unity-mono、cocos2dx、cocos-creator、unreal、flutter、xamarin、air、defold、gamemaker、libgdx 选择实现说明。
3. [stage-contract.md](references/stage-contract.md)：08 计划/操作/构建与 09 真机验收的共同要求。
4. [tools-index.md](./tools-index.md) 与 [experiences.md](./experiences.md)：索引与去功能点经验。
