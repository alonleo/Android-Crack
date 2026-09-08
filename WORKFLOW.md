# WORKFLOW.md — Android APK 逆向通用工作流

> 本文件定义所有 type 共享的阶段顺序、通过条件、恢复规则与调度合同。
>
> **不包含**：Agent 行为和目录纪律（见 `AGENTS.md`）、交付物技术细节（见 `OBJECTIVES.md`）、type 识别与路由（见 `STRATEGY.md`）、type 专属步骤和脚本参数（见对应 strategy skill workflow）、SDK 分类策略（见 third-party-removal reference skill）。

## 1. 调度合同

每个 type 的实际执行由其 `stages/sub-stage-register.yaml` 定义：register 决定子阶段顺序，action-driver 选择执行方案，step-driver 按 step register 的编号执行步骤。

```text
type register → sub-stage dispatcher → action-driver → step-driver → step result
```

- 根工作流定义阶段的目的与通过条件，不硬编码 type 专属脚本路径。
- 遇到尚未注册的新 type 时，加载 [general-strategy-skill](./skills/common/general-strategy-skill/SKILL.md)，读取本文件各阶段内容后创建对应的规范 type skill，再由该 type workflow 执行。
- type workflow 是该 type 的执行权威来源；根文档不替代其命令、工具或故障处理。
- 任一阶段失败必须定位原因、修复输入或脚本、重跑同一阶段；不得以 skip 规避失败。

## 2. 必经阶段

所有主阶段和当前 type register 定义的全部子阶段都必须完成。难度评级用于风险评估，不允许缩短正式流程。

| 主阶段 | 目的 | 通过条件 |
|---|---|---|
| M1 sniff | 识别输入格式与 type | type、特征和路由证据已记录 |
| M2 assess | 完成难度评估并执行子阶段 01–15 | grade 已记录，全部子阶段已按 register 验证 |
| M3 final-check | 汇总交付验收 | `OBJECTIVES.md` 的全部验收要求通过 |
| M4 cleanup | 清理临时材料并保留规定产物 | 临时目录已按规则清理，项目记录完整 |

### 2.1 子阶段 01–15

| ID | 名称 | 通用目的 | 通过条件 |
|---:|---|---|---|
| 01 | static-analyze | 建立代码、资源、native 与 SDK 基线 | 静态发现和关键入口已归档 |
| 02 | preprocess-build | 形成可处理的工程与构建基线 | 工程输入完整且基线构建结果已记录 |
| 03 | sdk-network-removal | 处理 SDK 副作用与强制网络依赖 | 决定、变更与依赖检查完成 |
| 04 | sdk-network-device-verify | 验证 SDK/网络阶段结果 | 冷启动、离线与核心路径通过 |
| 05 | revenue-forwarding | 处理 type 所需的奖励、购买或本地状态路径 | 对应功能路径可验证且不阻断玩法 |
| 06 | revenue-device-verify | 验证收益相关路径 | 设备验证证据完整 |
| 07 | ui-hide | 处理不属于目标交付的功能入口 | 修改计划和变更完整 |
| 08 | ui-hide-device-verify | 验证功能入口变化 | 目标 UI 状态和核心导航通过 |
| 09 | font-replace | 处理中文字体或 type 字体兼容 | 字体资源和调用路径有效 |
| 10 | font-device-verify | 验证字体渲染 | 目标页面无乱码或字体加载错误 |
| 11 | text-hanization | 处理文本本地化 | 文本来源、映射与替换结果完整 |
| 12 | text-device-verify | 验证文本本地化 | 目标页面显示正确 |
| 13 | image-hanization | 处理图片文字与纹理 | 替换资产满足格式和加载要求 |
| 14 | image-device-verify | 验证图片本地化 | 目标场景无纹理或布局错误 |
| 15 | record-project-files | 固化工程与交付清单 | 项目目录索引和最终记录完整 |

具体产物路径、type 例外、工具和步骤以当前 type skill 为准。

## 3. 阶段验证

每个阶段完成后，按当前 type workflow 执行与该阶段匹配的构建、安装或设备验证。验证必须覆盖：

1. 阶段声明的产物存在且可用。
2. 工程仍可重构建，若该阶段影响构建输入。
3. 影响运行时行为时，目标应用可启动且无当前应用的致命错误。
4. 设备验证阶段保留截图、报告或等价证据。

最终验收的交付条件只以 [OBJECTIVES.md](./OBJECTIVES.md) 为准。

## 4. SDK 与经验的分流

- SDK 的类别、依赖判断与特征库参考 [third-party-removal-strategy-skill](./skills/common/third-party-removal-strategy-skill/SKILL.md)。实际 SDK 清理仍由当前 type workflow 的第 03/04 阶段定义。
- 去功能点的分类、保留边界与依赖判断参考 [feature-removal-strategy-skill](./skills/common/feature-removal-strategy-skill/SKILL.md)。实际修改与第 07/08 阶段验收仍由当前 type workflow 定义。
- 汉化的对象分类、质量边界与经验参考 [hanization-strategy-skill](./skills/common/hanization-strategy-skill/SKILL.md)。字体、文本、图片与对应设备验收仍由当前 type workflow 的第 09–14 阶段定义。
- 每个真机验证阶段成功后，必须按 `AGENTS.md` 的经验归属规则固化可复用结论。
- 跨 type 问题写根 `EXPERIENCES.md`；type 私有问题写对应 type skill 的 `experiences.md`；具体 APK 事实只写项目记录。

## 5. 中断与恢复

1. 读取 `status.yaml` 的 `current_stage`、`completed_stages` 和 `failed_stages`。
2. 失败时先重跑失败阶段；未失败时从下一未完成阶段继续。
3. 重跑前检查环境、输入、脚本存在性和依赖；脚本故障必须先修脚本。
4. 重跑后重新验证阶段产物与状态记录，不以退出码单独作为通过结论。
5. 真机验收条件不可用时，记录阻塞原因并暂停在该阶段，条件恢复后续跑。

## 6. 文档边界

| 文档 | 职责 |
|---|---|
| [AGENTS.md](./AGENTS.md) | Agent 行为、脚本纪律、目录、状态与协同 |
| [OBJECTIVES.md](./OBJECTIVES.md) | 最终交付物、签名与验收契约 |
| [STRATEGY.md](./STRATEGY.md) | sniff、grade 与 type 路由 |
| `skills/strategy/<type>-strategy-skill/workflow.md` | 当前 type 的实际执行步骤、脚本与专属验证 |
| `skills/common/third-party-removal-strategy-skill/` | SDK 分类、依赖与特征库参考 |
| [EXPERIENCES.md](./EXPERIENCES.md) | 跨 type 通用问题经验 |
