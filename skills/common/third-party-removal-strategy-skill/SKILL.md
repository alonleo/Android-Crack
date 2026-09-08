---
name: third-party-removal-strategy-skill
description: Use when static analysis finds advertising, analytics, attribution, push, login, consent, crash-reporting, or cloud-service SDKs whose removal may affect an Android game's startup or core gameplay.
---

# 第三方 SDK 移除策略参考

**Agent 阅读：[third-party-sdk-removal-registry.md](references/third-party-sdk-removal-registry.md)**。
**脚本数据：[third-party-sdk-removal-registry.yaml](references/third-party-sdk-removal-registry.yaml)**。

YAML 为执行清单的唯一数据源。增删改查使用 [manage-sdk-registry.py](scripts/manage-sdk-registry.py)，写入时自动生成同名 Markdown；不要手工编辑生成文档。CLI 参数、字段及加载方式见 [脚本说明](scripts/README.md)。

本 skill 集中维护 SDK 分类、依赖边界、12 个 type 的实现要点与 03/04 阶段共用要求。实际执行由 type 注册表选择脚本，阶段位置见其 workflow。

## 使用边界

- 覆盖广告、分析、归因、推送、崩溃上报、同意管理、社交登录与云服务 SDK。
- 清单命中不等于可删除：先依据 [strategy.md](strategy.md) 判断核心玩法、初始化、JNI、反射、资源及异步回调依赖。
- 引擎差异集中在 [engine-notes.md](references/engine-notes.md)；引擎识别、专属脚本仍由 type 维护。
- 生成清单展示当前 YAML 规则；SDK/native 特征库提供判断背景，不是第二份执行名单。
- 项目事实与验证证据保留在 crackings 对应项目；经验按 [experiences.md](experiences.md) 和仓库经验归属规则记录。

## 加载顺序

1. [生成清单](references/third-party-sdk-removal-registry.md)与 [strategy.md](strategy.md)：当前规则、分类与保留边界。
2. [engine-notes.md](references/engine-notes.md)：只读当前 type 的实现差异。
3. [stage-contract.md](references/stage-contract.md)：04 清单维护/清理/构建与 05 真机验收。
4. [tools-index.md](tools-index.md)、[SDK 特征](references/sdks.md)、[native 特征](references/native-libs.md)：按需定位工具和依赖证据。
5. [故障处理](references/registry-and-troubleshooting.md)与 [experiences.md](experiences.md)：遇到失败时查阅。
