# OBJECTIVES.md — 逆向交付与验收契约

> 本文件定义每个 APK 项目的最终交付物、构建约束和验收标准。
>
> **不包含**：Agent 行为规则（见 `AGENTS.md`）、type 路由（见 `STRATEGY.md`）、阶段执行步骤（见 `WORKFLOW.md` 与 type workflow）、引擎实现细节（见 type strategy skill）、问题经验（见根或 type `experiences.md`）。

## 1. 交付目标

处理对象是可离线游玩核心玩法的单机游戏或含可选联网功能的单机游戏；不处理纯网游、MMO 或强联机竞技项目。

每个项目的主交付物是完整、可继续开发的 Android Studio 工程：

```text
crackings/<type>/<Name>/project/
├── app/                         # 承载全部修改的工程源码
├── gradle/、gradlew、settings.gradle* 等工程文件
├── my.keystore.jks              # 项目签名密钥
└── patched.apk                  # 由工程 release 构建生成的可安装产物
```

`patched.apk` 必须是同一工程 release 构建产物的副本；不得以仅能一次性重打包、无法从工程重建的 APK 代替交付。

## 2. 硬性约束

1. 当前 type register 定义的全部阶段与主阶段均已完成；最终验收前不得以跳过代替修复。
2. 全部修改都必须进入工程源码或受工程构建控制的输入，支持后续二次开发和重构建。
3. 交付 APK 必须可验证签名、安装、启动并进入目标核心玩法。
4. 新发现的 SDK 和 native 特征必须按第三方 SDK reference skill 的格式沉淀；项目级判断和证据留在项目记录。

## 3. 签名与构建产物

| 项 | 约束 |
|---|---|
| 密钥位置 | `crackings/<type>/<Name>/project/my.keystore.jks` |
| 别名与口令 | `jy` / `Ab123145` |
| 签名方案 | v1、v2、v3 均启用 |
| release 输出 | `app/build/outputs/apk/release/` 下的 release APK |
| 交付一致性 | `patched.apk` 与 release 输出可按哈希核对一致 |

签名生成、构建和校验必须通过当前 type workflow 的已登记入口完成。

## 4. 工具链产出约束

| 组件 | 固定要求 |
|---|---|
| JDK | 11（项目环境提供） |
| Android Gradle Plugin | 7.4.2 |
| Gradle | 7.5.1 |
| compileSdk | 33 |
| build-tools | 34.0.0 |
| APKTool | 2.11.1 |

工程必须使用项目环境提供的工具链。工具路径、环境加载和脚本调用纪律见 `AGENTS.md`。

## 5. 验收标准

### 5.1 工程与 APK

- release 构建成功，且预期 APK 非空。
- APK 通过 v1/v2/v3 签名校验。
- APK 可安装、可启动，启动后无当前应用的致命 Java 或 native 错误。
- 工程 release 输出与 `patched.apk` 一致。

### 5.2 核心玩法与离线可用性

- 可进入主菜单或目标主场景。
- 无网络时不因强制网络检测、远程配置或可选服务失败而阻断核心玩法。
- type 私有功能集成不破坏启动、导航与核心玩法状态。

### 5.3 本地化

- 已处理的文本显示正确，无乱码、占位符破坏或关键 UI 漏译。
- 已处理的图片文字、字体与场景资源保持格式、尺寸和加载兼容性。
- 通过当前 type workflow 定义的设备验证取得证据。

### 5.4 第三方 SDK

- 已判定应移除或停用的 SDK 不再以自动初始化或副作用阻断核心玩法。
- SDK 变更后无类缺失、JNI 异常、资源缺失或加载卡死。
- 新特征已写入第三方 SDK reference skill 的通用特征库；具体取舍与证据已写入项目记录。

## 6. 验收证据

最终验收必须能追溯到：工程构建结果、签名校验、安装/启动证据、阶段设备验证报告、项目状态记录与工程文件索引。具体命令、截图和报告路径由当前 type workflow 定义。

## 7. 文档边界

| 文档 | 职责 |
|---|---|
| [AGENTS.md](./AGENTS.md) | Agent 行为、环境、目录与记录约束 |
| [STRATEGY.md](./STRATEGY.md) | type 识别、评级与路由 |
| [WORKFLOW.md](./WORKFLOW.md) | 通用阶段合同、通过条件与恢复 |
| `skills/strategy/<type>-strategy-skill/` | type 专属实现、执行和验证 |
| [EXPERIENCES.md](./EXPERIENCES.md) | 跨 type 通用逆向问题经验 |
