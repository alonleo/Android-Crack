# 第三方 SDK 清单与工具脚本

| 脚本 | 职责 |
|---|---|
| [manage-sdk-registry.py](manage-sdk-registry.py) | YAML 增删改查、校验、锁定写入、自动同步同名 Markdown |
| [load_sdk_removal_registry.py](load_sdk_removal_registry.py) | 阶段读取共享 YAML，显式路径参数可读取项目副本 |
| [verify-sdk-registry.py](verify-sdk-registry.py) | 临时副本验证 CRUD、失败不写入、锁、幂等、文档同步 |
| [common/add-sdk-to-registry.py](common/add-sdk-to-registry.py) | 兼容旧追加参数，委托管理器 add |

统一索引：[SCRIPTS-INDEX.md](../../scripts/SCRIPTS-INDEX.md)。

## 数据与调用

默认数据是 ../references/third-party-sdk-removal-registry.yaml，同名 .md 自动生成供 Agent 阅读。操作前按项目规则加载环境。以下命令从仓库根运行，只管理清单，不修改 APK。

```text
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py list
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py list --section manifest_drop_exact
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py get --section manifest_drop_exact --name example.InitProvider
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py add --section manifest_drop_exact --name example.InitProvider --why 已核对依赖
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py update --section manifest_drop_exact --name example.InitProvider --why 更新后的依据
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py delete --section manifest_drop_exact --name example.InitProvider
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py validate
python skills/common/third-party-removal-strategy-skill/scripts/manage-sdk-registry.py sync-doc
```

示例名称不是默认删除目标。修改立即写入，--dry-run 只预览；--registry <项目副本.yaml> 指定文件，同名 MD 写在副本旁。参数可放在操作名前后。stdout 为 UTF-8 JSON，日志走 stderr，失败非零。

list/get 只读；add 同名时不覆盖，修改须用 update。update 只改指定字段；--new-name 修改规则键或字符串项，重名拒绝。delete 只删除清单规则，不删除 APK 文件。YAML CRUD 不受 MD 经验条目“只追加”规则限制。

## 字段约定

保留 schema_version=1，避免破坏现有清理脚本的数据接口。

| section | 条目形式 | 管理参数 |
|---|---|---|
| manifest_drop_exact / manifest_drop_keyword_contains / so_early_kill | name、可选 why | --name、--why |
| build_config_stubs | class_path、package、可选 why | --name、--package、--why |
| meta_data_force_value | name、value、可选 why | --name、--value、--why |
| so_keyword_contains / raw_apk_drop_entries / smali_exclude_prefixes / engine_so_keep | 字符串 | --name；update 用 --new-name |

显式指定 section；add 保留旧入口的自动推断以兼容调用方。字符串段不存附加原因，项目操作依据写 status.yaml。新增/修改前校验结构与重名；写锁和读取版本检查防止管理器互相覆盖。YAML 与 MD 分别原子替换；若文档写入失败，命令报错，修复后用 sync-doc 恢复阅读视图。validate 同时检查 YAML 结构与 MD 是否同步。

## 阶段接口

Agent 读生成清单和策略 → list/get 查规则 → add/update/delete 维护 YAML → loader 读取 → 当前 type 执行清理。具体要求见 [03/04 接口](../references/stage-contract.md)。

load_registry() 默认读取本 skill 的 references 清单，load_registry(path) 可读显式路径；管理 CLI 的 --registry 只影响本次管理，不自动切换所有旧 worker。使用项目副本时核对当前 worker 的 registry 参数，使编辑和执行指向同一文件。修改规则后重跑加载和分析，不能混用前后版本。

此处不宣称全部历史 worker 已实现统一快照协议，也不复制去功能点的 type/enabled 字段。无 APK/设备时只运行清单与文档验证，不宣称去 SDK 阶段通过。

## 实施辅助工具

| 实际文件 | 边界 |
|---|---|
| [common/clean-android-manifest.py](common/clean-android-manifest.py) | 结构化 XML 清理；preserve-firebase 按依赖选择 |
| [common/stub-sdk-methods.py](common/stub-sdk-methods.py) | 定点方法桩化，确认签名/返回类型/初始化 |
| [common/stub-applovin-consent.py](common/stub-applovin-consent.py) | 案例来源的 consent/CMP 处理，须复核内部调用与回调 |
| [common/remove-sdk-classes.py](common/remove-sdk-classes.py) | 物理删除与残留检查，反射/JNI 不能视为天然安全 |
| [workflow/sub-stage-defold-manifest-clean.py](workflow/sub-stage-defold-manifest-clean.py) | Defold 案例配置，核对具体前缀和核心 glue |
| [workflow/sub-stage-stub-sdks.py](workflow/sub-stage-stub-sdks.py) | 旧桩化 worker，由 type 决定是否采用 |
| [workflow/sub-stage-remove-sdks.py](workflow/sub-stage-remove-sdks.py) / [extra](workflow/sub-stage-remove-sdks-extra.py) | 固定宿主路径与占位 type 的历史实现，仅作参考 |
| [workflow/lib/common.py](workflow/lib/common.py) | 旧 worker 随附公共库；新工具用仓库统一 common |

旧文档中的 grep-sdk-residue.py、update-feature-library.py、validate-apktool-build.py 没有实际文件，不作为可调用工具；本目录不维护双份代码。

## 验证

运行 scripts/verify-sdk-registry.py，在临时 YAML/MD 副本上检查 CRUD 与同步；现有共享规则不因测试改变。默认清单用 manage-sdk-registry.py validate 只读检查。
