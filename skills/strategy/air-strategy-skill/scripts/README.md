# air-strategy-skill scripts/ — 脚本子索引

> 完整索引见 [SCRIPTS-INDEX.md](../../skills/common/scripts/SCRIPTS-INDEX.md)（canonical）。本文件为该 skill 的脚本清单。
> 查找脚本先查索引表，禁止自行 `ls`（AGENTS.md §1.10）。

| 脚本 | 角色 |
|------|------|
| `workflow/sub-stage-air-static-analyze.py` | AIR 静态分析 |
| `workflow/sub-stage-air-fonts.py` | AIR 字体 |
| `common/extract-swf-text.py` | SWF 文本提取 |
| `common/filter-swf-strings.py` | SWF 字符串过滤 |
| `common/inject-as-text.py` | AS 文本注入 |
| `common/patch-swf-translations.py` | SWF 翻译 patch |
| `common/verify-swf-text.py` | SWF 文本验证 |
| `common/swf-gui-edit.py` | SWF GUI 编辑 |
| `common/swf-xml-edit.py` | SWF XML 编辑 |
| `common/install-ffdec.py` | ffdec 安装 |
| `common/install-swfmill.py` | swfmill 安装 |

## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
