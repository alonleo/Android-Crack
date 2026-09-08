---
name: general-strategy-skill
description: 当 APK 出现尚未注册的引擎或框架 type，或用户要求新增 type 策略时使用。读取根 WORKFLOW.md 各阶段要求，建立并注册规范的 type strategy skill，完成阶段、脚本和识别路由验证。已有 type 的普通项目处理使用对应 type skill。
---

# 新 type 策略构建规范

本 skill 指导 Agent 为新引擎创建 `skills/strategy/<type>-strategy-skill/`，将通用工作流落实为该 type 可执行、可验证的策略。现有 `scripts/` 和 `stages/sub-stage-register.yaml` 同时提供部分公共阶段实现与路由支持；这里不是未知引擎的替代执行 type。

## 读取顺序

1. 根 [AGENTS.md](../../../AGENTS.md)：脚本入口、环境、目录和状态约束。
2. 根 [STRATEGY.md](../../../STRATEGY.md)：识别证据、已有 type 与配置路由。
3. 根 [WORKFLOW.md](../../../WORKFLOW.md)：读取全部主阶段和每个子阶段的目的、通过条件及恢复规则。
4. 根 [OBJECTIVES.md](../../../OBJECTIVES.md)：交付物和验收契约。
5. [workflow.md](workflow.md)：按阶段创建、注册及验证新 type skill。
6. [REGISTRY.md](../../REGISTRY.md) 和 [SCRIPTS-INDEX.md](../scripts/SCRIPTS-INDEX.md)：确认已有能力及脚本位置；按需读取相近 type 的实际文件。

不要只读阶段标题就生成目录。以根工作流的当前内容为准，不将某个旧 type 的阶段编号、工具参数或成功状态当成新 type 的事实。

## 触发和判断

Agent 创建完整目录骨架时调用 `scripts/create-type-skill.py --type <type> --label <显示名> --apply`，具体参数和 JSON 返回值见 [workflow.md](workflow.md#agent-生成入口)。生成草稿后继续完成引擎实现、注册和实际验证，不将生成成功当作新 type 支持完成。

- 已有 type 能准确解释特征时，使用已有策略；同一引擎版本差异不自动成为新 type。
- 有独立引擎或运行时证据，且配置中没有对应 type 时，建立独立策略；不得降级为 `android`。
- 证据不足时先记录未知特征和需要补充的分析，不能编造引擎、识别模式或工具支持。
- 只要求创建 skill 时，交付规范与实现并说明验证范围；只有实际完成项目的全部阶段后，才能声明该 type 已经通过完整运行验证。

## 完成标准

- 新 type 有带 `name`、`description` 的 `SKILL.md`，明确触发条件、加载顺序和边界。
- 根工作流的所有阶段均有 type 对应实现、产物、验证和恢复说明，阶段注册、action 和 step 形成完整调用链。
- `strategy-config.yaml`、类型识别表、`REGISTRY.md` 和脚本索引同步登记。
- 路由指向存在的文件；没有使用空实现、无条件成功或复制其他引擎特征来伪造覆盖。
- 静态规范验证与实际 APK/真机验证分开报告；缺设备时按根工作流记录并暂停验收。

公共脚本的索引列举或路由声明不证明实现存在。复用前读取脚本并核对依赖、输入和输出；发现缺失时先补实现及索引，再接入新 type。
