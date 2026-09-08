# SDK/网络移除 04 与真机验收 05：共用要求

本页承接各 type 重复章节，不另建阶段调度。旧 04b/05b 的网络检测和飞行模式并入 03/04，历史 09/11 等 SDK 编号不作为路由依据。

## 入口与前置条件

Agent 阅读 [生成清单](third-party-sdk-removal-registry.md)，脚本读取同目录的 [YAML](third-party-sdk-removal-registry.yaml)。CRUD 自动同步阅读视图；命令和参数统一见 [脚本说明](../scripts/README.md)。MD 特征库补充依赖背景，不作为另一份执行清单。

1. APK 处理先加载 `tools/environments/env.sh`，确认工具、脚本和依赖。查脚本先读 [统一索引](../../scripts/SCRIPTS-INDEX.md)。
2. 读取当前 type 的 `stages/sub-stage-register.yaml`，由 sub_stage-dispatcher → action-driver → step-driver 调度。按名称 sdk-network-removal、sdk-network-device-verify 查询，不硬编码 worker 路径。
3. 当前 register 的 04：il2cpp 声明专用 worker，其他 type 声明 common worker；05 声明 common worker。实际委托继续读 action/step，不把旧“5/15 步”当当前顺序。
4. 读取 01/03 分析、入口信息、SDK 清单与 [引擎差异](engine-notes.md)。新增规则先证明分类和依赖；清单缺失/错误先修复，不静默回退硬编码名单。

## 04：决策、清理与构建

清单维护顺序：MD 给 Agent → Agent 判定 → 脚本 CRUD 更新 YAML → loader 读取 YAML → 执行清理。Agent 通过 manage-sdk-registry.py 的 list/get 复核，再用 add/update/delete 写入；检查最终结果，在 status.yaml 记录操作、理由和清单路径。接口见 [清单维护](registry-and-troubleshooting.md)。这是阶段前置约束，不表示旧 worker 扫描会自动代替 Agent 作 CRUD 决定。

| 检查面 | 共用要求 |
|---|---|
| 收集 | Manifest、全部 dex/smali、native 导出/动态加载、assets/资源、托管/脚本桥接一起分析，形成 3rd-party-sdk.yaml |
| 决策 | 每项记明特征、调用方、保留/停用/桩化/删除、原因和验证点；白名单覆盖实际引擎和核心解码库 |
| 初始化 | 清理 SDK Provider/Activity/Service/Receiver/meta-data、相关权限和 queries；共享组件逐项判断，保留游戏入口和必要权限。il2cpp 原约定保留 INTERNET，不能靠删网络权限代替停用 SDK |
| 类/库/资源 | 按依赖证据处理，保留 JNI/反射接口、MultiDex、编译和本地状态机所需类型；删库备份按契约放 third-party-libs/ |
| 桩化/网络 | 停副作用同时维持返回类型、字段初始化、异步完成/失败路径；核对 native/脚本层网络门槛，不将所有网络 API 统一返回成功 |
| 构建 | 注册步骤重建工作树、更新必要 smali→jar/BuildConfig stubs 并构建；检查最终 APK 包含修改。若 step-register 在构建后仍有修改步骤，先修复顺序并重跑，不能沿用修改前构建结果 |
| 报告/状态 | SDK 与网络处理分别记明，核对当前 register 全部 outputs、构建日志；完成即由 Agent 写 status.yaml，不只看退出码 |

关键词扫描用于发现残留；允许保留的桩类/核心依赖须明确列出。若当前 register 要求 Manifest SDK 关键词为 0，仍须满足；必要依赖与硬指标冲突时先解决规则/输入冲突，不擅自降级或删除核心依赖。

## 产物核对

所有文件归 `crackings/<type>/<Name>/`，具体路径以当前 register 为准。

| 阶段 | 共用检查 | type 补充 |
|---|---|---|
| 04 | stages/03-sdk-network-removal/ 下的 3rd-party-sdk.yaml、sdk-removal-report.yaml、清理备份及构建产物 | il2cpp 另核对 network-detection.yaml、sdk-network-report.yaml，以及 workflow 约定的 hook-plan.yaml；其他 type 按 register 和实际报告核对网络处理证据 |
| 05 | stages/04-sdk-network-device-verify/ 下的 verify-report.md 和普通/飞行两模式截图证据 | 文件名核对当前 register/脚本：旧 workflow 用 screenshot-normal.png、screenshot-airplane.png，部分 register 声明 screenshot.png；逐项满足已声明输出，并确保两段证据可区分、不相互覆盖 |

## 05：普通与飞行模式验收

- 通过 type 路由的真机脚本安装、冷启动最终 APK；普通和飞行模式均检查启动、场景加载、核心玩法、重复进入/返回及日志，结束恢复设备网络状态。
- 进程存在、多窗口存活、单张截图或数秒无 FATAL 只是部分证据；还要确认目标 SDK 副作用停止、相关失败分支能完成，无 JNI abort、缺类、ANR 或永久加载。
- **设备缺失、离线或验收条件不足时暂停在 sdk-network-device-verify**，在 status.yaml 的 current_stage / failed_stages 写阶段名和原因。恢复后从该阶段续跑，不用 --skip、编译通过或静态截图替代。
- 脚本错误先排除环境因素，再修复本体、重跑同一入口。通过后立即记录和固化：跨 type 问题写根 EXPERIENCES.md，引擎私有问题写 type experiences，APK 事实留项目目录。05 通过后才进入 06/07 激励与 IAP 处理。
