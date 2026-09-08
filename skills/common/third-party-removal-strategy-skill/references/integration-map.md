# 旧 SDK skill 内容整合映射

统一入口是本 skill 的 [SKILL.md](../SKILL.md)。旧目录全部文件由 merge-sdk-skill.py 逐字节存档到 docs/migrations/legacy-sdk-skill/original/，manifest.json 记录每个原文件的 SHA-256 和去向。存档只供追溯，不作为当前操作规则。

| 旧内容 | 当前维护位置 | 处理 |
|---|---|---|
| SKILL.md、strategy.md | [strategy.md](../strategy.md)、[引擎差异](engine-notes.md) | 合并分类、A/B/C、保留边界、King 桥接；修正按类别无条件删除的结论 |
| workflow.md | [03/04 共用要求](stage-contract.md)、[清单与故障处理](registry-and-troubleshooting.md) | 保留 Agent 判断、清单写入、资源/残留校验、状态记录；旧 09/10 编号服从当前 type 注册表 |
| tools-index.md、scripts 各级 README | [tools-index.md](../tools-index.md)、[脚本索引](../scripts/README.md) | 实际脚本搬入本目录，区分现有工具与旧占位项；取消双份代码同步规则 |
| references/sdks.md、native-libs.md、sdk-patterns.md | [SDK 特征入口](sdks.md)、[native 特征入口](native-libs.md)、[识别模式](sdk-patterns.md) | 提炼可复用特征；历史项目日期、地址和全量原文只保留存档 |
| third-party-sdk-removal-registry.yaml | [共享清单](third-party-sdk-removal-registry.yaml) | 数据原样迁移，修改 loader/调用方位置，不擅自增删既有匹配规则 |
| scripts/**/*.py | [脚本目录](../scripts/) | 逐文件迁移；修复搬迁影响的根目录、common/loader 引用；不把语法检查当 APK 验收 |
| assets/README.md | [资源说明](../assets/README.md) | 搬迁并修正引用，旧目录没有额外二进制资源 |

## 旧结论冲突的处理

- A 为保留接口的桩化，B 为停用初始化，C 为依赖解除后的物理删除；不是 A/B 编译失败就自动选择 C。
- 反射、字符串加载、JNI 和 ART 验证均需检查，不能将字符串引用视为天然安全。
- PGL、AndroidX、Firebase、社交登录及工具库是否保留按实际依赖，不能由厂商或分类一刀切。
- 清理 SDK 副作用，不把修改同意状态当真实用户同意；CMP 弹窗应处理初始化及等待回调。
- 不将参数/字段类型统一替换为 Object，不对非 void 方法生成 return-void。
- 汉化、多语言清理转由汉化 skill 按任务范围处理，不并入 SDK 清理步骤；具体案例仍在原文存档。
