# STRATEGY.md — APK 类型识别、难度评级与策略路由

> 本文件是根级路由文档，负责回答三个问题：APK 属于什么 type、逆向难度如何、应加载哪个 strategy skill。
>
> **不包含**：阶段执行步骤和脚本参数（见 type workflow）、引擎实现与 Hook 细节（见 type strategy）、SDK 清理操作（见 type workflow，分类参考见 third-party-removal skill）、问题经验（见根或 type `experiences.md`）。

## 单一事实来源

| 事实 | 权威位置 |
|---|---|
| 机器可读 sniff 规则、type 与 skill 映射 | `skills/common/scripts/strategy/strategy-config.yaml` |
| 阶段顺序、通过条件与恢复 | [WORKFLOW.md](./WORKFLOW.md) |
| 引擎专属策略与执行 | `skills/strategy/<type>-strategy-skill/` |
| SDK 分类和依赖参考 | `skills/common/third-party-removal-strategy-skill/` |

## 1. 路由模型

```text
APK 输入 → sniff 判定 type → assess 计算 grade → type 路由到 skill → type workflow 执行
```

`type` 决定工具链和 skill；`grade` 仅描述风险与投入预期，不能用于跳过 [WORKFLOW.md](./WORKFLOW.md) 定义的必经阶段。

## 2. 类型识别

嗅探由对应主阶段脚本读取 `strategy-config.yaml` 完成。下表是人工审阅用的特征概览，不替代配置文件。

| 特征组合 | type | 目标 skill |
|---|---|---|
| `assets/META-INF/AIR/application.xml` | `air` | `air-strategy-skill` |
| `libil2cpp.so` 与 `global-metadata.dat` | `il2cpp` | `il2cpp-strategy-skill` |
| `GameAssembly.dll` 与 managed DLL | `unity-mono` | `unity-mono-strategy-skill` |
| `libcocos2d*.so` 与 Lua assets | `cocos2dx` | `cocos2dx-strategy-skill` |
| `libcocos2djs.so`、Cocos settings/config | `cocos-creator` | `cocos-creator-strategy-skill` |
| `libUE4.so` 或 `libUnreal*.so` | `unreal` | `unreal-strategy-skill` |
| `libflutter.so` 与 `libapp.so` | `flutter` | `flutter-strategy-skill` |
| MonoDroid/Xamarin native 库 | `xamarin` | `xamarin-strategy-skill` |
| `libgdx.so` 与 `com/badlogic/gdx` | `libgdx` | `libgdx-strategy-skill` |
| `libdmengine.so` 与 Defold assets | `defold` | `defold-strategy-skill` |
| `libyoyo.so` 与 `game.droid` | `gamemaker` | `gamemaker-strategy-skill` |
| 仅标准 Android DEX，且无引擎特征 | `android` | `android-strategy-skill` |

### 2.1 冲突与未知类型

- 多个特征命中时，以 `strategy-config.yaml` 的 `sniff_order` 为准，并在项目 findings 记录歧义和判断依据。
- 未知引擎不得降级为 `android`。加载 [general-strategy-skill](./skills/common/general-strategy-skill/SKILL.md)，逐阶段读取根 `WORKFLOW.md`，建立规范的 `<type>-strategy-skill`、注册 type，并完成一次完整工作流验证。
- `android` 只适用于确无引擎或专属运行时特征的 Java/Kotlin APK。

## 3. 难度评级

评级输出用于安排分析深度、风险预期和人工复核优先级；不改变工作流的必经阶段。

| 维度 | 关注点 | 最高分 |
|---|---|---|
| 代码复杂度 | 引擎、语言、混淆和 native 比例 | 20 |
| 代码体积 | DEX、资源和 native 库规模 | 15 |
| 加密与加固 | 壳、签名绑定、metadata 或资源加密 | 25 |
| 反调试 | 调试检测、完整性校验和运行时保护 | 15 |
| 第三方 SDK | 数量、初始化深度和依赖链 | 10 |
| 运行时约束 | 网络、设备、协议和服务依赖 | 15 |

| grade | 分值 | 说明 |
|---|---:|---|
| S | 80–100 | 多层保护或强 native/服务依赖 |
| A | 60–79 | 高混淆、加密或多项运行时约束 |
| B | 40–59 | 标准引擎项目且含较多 SDK/资源 |
| C | 20–39 | 中等复杂度的 Java 或轻量引擎项目 |
| D | 10–19 | 保护较少、结构简单 |
| F | 0–9 | 基础 DEX/资源结构 |

评级必须写入 `difficulty.json` 与项目状态记录，并说明各维度证据。

## 4. 策略配置与路由

`strategy-config.yaml` 中每个 type 至少包含：

| 字段 | 含义 |
|---|---|
| `label` | 人类可读 type 名称 |
| `sniff_patterns` | 引擎和格式识别模式 |
| `skill` | 对应 strategy skill 目录 |
| `stages` | type 的阶段注册引用 |
| `tools` | 静态、动态和构建工具描述 |
| `notes` | 路由备注与限制 |

配置由路由器消费。Agent 不得在根文档、driver 或项目状态中复制配置逻辑；需要修改时同时更新配置、类型表、`skills/REGISTRY.md` 和对应 skill。

## 5. 风险路由

| 风险 | 路由处理 |
|---|---|
| 静态内容不完整 | 交由当前 type skill 的加固/动态分析策略处理 |
| native 或 JNI 依赖 | 交由当前 type skill 分析，不据 manifest 结论直接删除 |
| SDK 清理副作用 | 参考 third-party-removal skill，执行以当前 type workflow 为准 |
| 资源或签名兼容性 | 交由当前 type workflow 的构建和验证阶段处理 |
| 可复用故障模式 | 记录到根或 type 私有 `experiences.md` |

## 6. 文档边界

| 文档 | 职责 |
|---|---|
| [AGENTS.md](./AGENTS.md) | Agent 行为、目录、状态和文档加载约束 |
| [OBJECTIVES.md](./OBJECTIVES.md) | 交付物与验收契约 |
| [WORKFLOW.md](./WORKFLOW.md) | 通用阶段顺序、通过条件和恢复 |
| `skills/strategy/<type>-strategy-skill/` | type 专属策略、执行和私有经验 |
| `skills/common/third-party-removal-strategy-skill/` | SDK 分类、依赖和特征库参考 |
| [EXPERIENCES.md](./EXPERIENCES.md) | 跨 type 通用逆向问题经验 |
