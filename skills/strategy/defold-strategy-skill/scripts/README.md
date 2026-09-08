# Defold skill 脚本子索引

> 本表是 defold-strategy-skill 脚本的子索引（canonical 见 `skills/common/scripts/SCRIPTS-INDEX.md`）。

## workflow/

| 脚本 | 角色 | 位置 |
|------|------|------|
| `sub-stage-defold-manifest-clean.py` | Defold manifest SDK 清理 | 规范存放于 `skills/common/third-party-removal-strategy-skill/scripts/workflow/`（跨引擎通用），经 SCRIPTS-INDEX 引用 |

## common/

（暂无专用脚本；跨引擎通用脚本见 `skills/common/scripts/SCRIPTS-INDEX.md`）

Defold 采用 android 型阶段序列，复用 general-strategy-skill 跨 type 脚本（见 `tools-index.md`）。

## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
