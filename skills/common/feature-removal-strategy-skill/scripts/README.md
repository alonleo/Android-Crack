# 去功能点清单脚本

| 脚本 | 职责 |
|---|---|
| `manage-feature-checklist.py` | YAML 增删改查、严格校验、锁定写入、自动同步同名 Markdown |
| `step-load-feature-checklist.py` | 去功能点首步：按 type 读取 YAML 快照、候选项与 SHA-256 |
| `sync-feature-checklist-stages.py` | 将共同加载步骤接入各 type 注册表，默认预览、--apply 应用 |
| `verify-feature-checklist.py` | 独立临时 YAML 上验证 CRUD、非法数据拒绝、文档同步与阶段数据读取 |

统一索引：[SCRIPTS-INDEX.md](../../scripts/SCRIPTS-INDEX.md)。

## 数据与调用

默认数据是 `../references/feature-removal-checklist.yaml`，同名 `.md` 自动生成供 Agent 阅读。下面均为仓库根目录下的正式脚本调用，不执行 APK 修改。

```text
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py list
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py list --type il2cpp --kind feature --enabled-only
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py get F01
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py add --data-file <item.yaml>
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py update F01 --data-file <changes.yaml>
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py delete F01
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py validate
python skills/common/feature-removal-strategy-skill/scripts/manage-feature-checklist.py sync-doc
```

修改会立即写入；`delete F01` 仅演示语法，不是默认操作。用 `--registry <项目副本.yaml>`（放在子命令之前）切换目标；Markdown 写到该文件的同名 `.md`。输入补丁可为 YAML 或 JSON，stdout 为 JSON、日志走 stderr，失败退出非零。

新增条目须包含全部字段；更新仅提供要改变的字段，ID 不可变：

```yaml
id: F28
key: community_link
kind: feature
name: 社区推广入口
keywords: [Community, JoinCommunity]
types: ['*']
enabled: true
strategy: review
notes: 确认不承载核心玩法、存档或必要设置，再判断是否移除。
```

`kind` 为 feature/popup/language/verification，ID 前缀对应 F/P/L/V；`key` 使用唯一小写英文下划线标识。`types` 为 `['*']` 或实际 type 列表。feature/popup 的 keywords 非空。`strategy` 支持 review、hook_container、hook_method、hide_node、static_hide，均须经过项目依赖判断；默认新条目使用 review。

更新补丁示例（停用规则但保留 ID）：

```yaml
enabled: false
notes: 该规则暂不参与自动候选扫描，待核对适用条件。
```

## 阶段接口

12 个 type 的 `ui-hide/default-action` 首步通过本地适配器调用共同加载器。输出保存在 `ui-hide.default-action.load-feature-checklist`，包括 items、targets、registry_path、registry_sha256；IL2CPP 扫描/计划直接消费快照，旧 worker 也已改读 YAML。

加载器读取 `FEATURE_REMOVAL_CHECKLIST` 环境变量指定的项目副本，否则使用共享清单；该变量不会改变管理 CLI 的默认文件，编辑副本时仍显式传 `--registry`。修改数据后重跑加载和扫描，避免混用版本。无 APK/设备时只运行清单验证，不能声称完整去功能点或真机阶段通过。

旧 IL2CPP worker 读取 YAML 后生成待审核计划；共享清单的建议策略不能替代项目依赖审查。未审核时它停止注入并返回非零，Agent 应检查计划后通过当前 type 的实施方案处理，不把候选生成当作阶段通过。
