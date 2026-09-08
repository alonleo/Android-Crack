# 清单与 SDK 清理故障处理

清单以 [YAML](third-party-sdk-removal-registry.yaml)为唯一数据源，[同名 MD](third-party-sdk-removal-registry.md)为自动生成的阅读视图。CRUD、字段和同步操作集中在 [脚本说明](../scripts/README.md)。本页只维护判断与故障处理，不重复命令手册。

## 输入与判断

扫描只给候选。Agent 先读策略和引擎差异，逐项确定保留/停用/桩化/删除，再通过管理器修改 YAML；项目原因、采用的清单路径和验证证据写入对应项目。不能只修改 MD/findings 而遗漏执行输入，也不能让脚本解析 MD 决定删除目标。

共享清单含历史匹配规则，执行前核对核心组件、引擎库、资源解码与动态加载依赖。使用项目副本时，管理命令与实际 worker 必须指向同一文件；编辑后重跑加载和分析。

## 常见故障

| 现象 | 优先核对 | 处理 |
|---|---|---|
| MD 与 YAML 不一致 | 是否绕过管理器或同步写入失败 | validate 检查，sync-doc 从 YAML 重建；不手工修生成 MD |
| 清单未生效 | CLI/worker 路径、显式参数、loader 字段 | 修复实际输入，重新加载；不回退硬编码名单 |
| 写入失败 | 写锁、读后文件变化、格式/重名 | 核对正在执行的写入；重新读取和修正输入，保留错误记录 |
| Manifest XML 损坏 | 正则删除多行 Provider/Service | 用结构化 XML 处理，保留嵌套 meta-data，解析通过后构建 |
| Firebase 缺组件/RemoteConfig 空对象 | InitProvider、ComponentDiscoveryService、registrar | 仍有依赖则保留注册，定点停用上报，不全删 Firebase |
| 资源编译失败 | 删除 res 后的 public.xml 和其他 XML 引用 | 联动维护声明/引用，重跑资源、smali 与整包构建 |
| ClassNotFound/DllNotFound/JNI abort | Java、托管、反射、native 调用 | 恢复必要接口，保持方法描述符、返回类型和初始化 |
| NPE/加载卡住 | 字段初始化丢失、异步结果未完成 | 保留必要状态和失败/完成回调，不全局宣称有网络 |
| CMP/TOS 弹窗仍出现 | public API 外的内部显示路径 | 从日志/调用链定位；混淆名逐版本确认，停用采集不代表用户已同意 |
| 修改未进入 APK | smali→jar/DEX/构建输入仍旧 | 重跑实际注册步骤，核对最终产物 |

每次修改后按 [03/04 共用要求](stage-contract.md)构建、记录和验收。目录、输入加载、语法或文档验证通过不代表 APK/真机通过。

## King 适配层

com.king.abm 的 network 适配器与对应 SDK 联动检查；adprovider/internal 是核心桥接候选。com.king.usdk 按模块职责判定，firebaseanalytics 与 Firebase 调用链一起核对。历史版本存在 try-catch 不证明新版本安全；构造、直接引用、反射和回调都需检查。
