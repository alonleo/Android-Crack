# gamemaker-strategy-skill scripts

> 本目录脚本的子索引（**canonical 索引**见 `skills/common/scripts/SCRIPTS-INDEX.md`）。

## workflow/

> 阶段专用脚本（按 AGENTS.md §1.3 命名规范 `<verb>-<scope>.py`）

| 脚本 | 阶段 | 角色 | 状态 |
|------|------|------|------|
| `remove-gamemaker-buttons.py` | 13 去功能点 | 移除按钮/对象实例（三处实例列表全清 + 可选代码重编译） | 已沉淀（FindTheDifferences 2026-08-09） |
| `inspect-gamemaker-rooms.py` | 13 去功能点 | 探索：列出房间/图层/实例/对象/代码引用 | 已沉淀（FindTheDifferences 2026-08-09） |

## common/

> 通用脚本

| 脚本 | 角色 | 状态 |
|------|------|------|
| `setup-output-project.py` | 搭 AS 工程化骨架（smali→jar + 剥离 androidx + 生成 AS 工程 + md5 一致） | 已沉淀（FindTheDifferences 2026-08-09） |

## 维护规则

- 新增脚本必须按 AGENTS.md §1.3 命名
- 在 `skills/common/scripts/SCRIPTS-INDEX.md` 同步登记（AGENTS.md §1.10）
- 复用 Defold 基建时（manifest 清理、And64InlineHook 桩化），优先调用 `skills/common/third-party-removal-strategy-skill/scripts/workflow/sub-stage-defold-manifest-clean.py`（GameMaker 同样适用）
- **按钮移除依赖工具**: `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll`（dotnet）
## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
