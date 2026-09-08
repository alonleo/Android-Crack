# 第三方 SDK 移除策略

## 目标

移除不影响单机核心玩法的第三方副作用，同时保持启动、核心玩法、必要桥接和本地状态机完整。

## 分类与默认判断

| 分类 | 常见用途 | 默认处理 |
|---|---|---|
| 广告与广告聚合 | 横幅、插屏、激励、交叉推广 | 候选移除；激励奖励须保留本地可验证的替代状态机 |
| 分析、归因、崩溃上报 | 行为统计、归因、远程诊断 | 候选移除或停用初始化 |
| 同意管理与隐私弹窗 | GDPR、CMP、consent | 候选移除或桩化，避免阻断启动 |
| 推送与远程配置 | 消息、实验、配置下发 | 默认停用；先确认不参与核心状态机 |
| 登录、云存档、排行榜 | 账号、同步、社交功能 | 仅在核心玩法可独立运行时处理；保留本地状态路径 |
| 支付与账单桥接 | 内购、订阅、恢复购买 | 不直接物理删除；先由对应 type skill 确认本地替代或兼容路径 |
| 引擎与核心运行库 | 引擎加载、JNI bridge、资源解码 | 不属于第三方 SDK 移除目标，除非有完整依赖分析证据 |

## A/B/C 策略

| 策略 | 做法 | 适用条件 | 风险 |
|---|---|---|---|
| A：桩化 | 保留类、方法或桥接入口，停止副作用并返回兼容结果 | 仍有 Java、JNI 或反射调用 | 最低；需保证返回值和生命周期一致 |
| B：停用初始化 | 清理 manifest 自动组件、初始化入口和资源引用 | SDK 可保留但不应在启动时执行 | 中等；残留业务调用仍可能触发 |
| C：物理删除 | 删除类、native 库、资源和 manifest 组件 | 已证明无 Java、JNI、反射、字符串加载或资源依赖 | 最高；必须完整回归验证 |

默认从 A 或 B 开始。只有静态和运行时证据均显示无依赖时，才能选择 C。

## 依赖判断规则

公共基础库（AndroidX、Kotlin、okhttp/okio、Google Play Services base/common）、游戏专有代码和共享资源优先保留；ExoPlayer/Glide/ZXing 等“工具库”也需逐调用方判定。King 适配层及资源/初始化故障的具体核对见 [清单与故障处理](references/registry-and-troubleshooting.md)。

1. 同时检查 AndroidManifest、DEX/Smali、native 库导出、assets、资源与动态加载字符串。
2. JNI glue、`System.loadLibrary`、`dlopen`、反射、Provider 和 Service 都是阻断物理删除的证据。
3. manifest 清理只会停止自动初始化，不能消除 Java 或 native 调用。
4. 删除后出现 `ClassNotFoundException`、`DllNotFoundException`、JNI abort 或加载卡死时，回到依赖分析；不要以继续删除替代定位。

## 记录边界

- SDK 特征写入 [references/sdks.md](./references/sdks.md)。
- native 库特征写入 [references/native-libs.md](./references/native-libs.md)。
- SDK 清理领域的可复用问题写入 [experiences.md](./experiences.md)。
- 具体 APK 的发现、取舍和验证证据只写入其 `crackings/<type>/<Name>/` 记录。
