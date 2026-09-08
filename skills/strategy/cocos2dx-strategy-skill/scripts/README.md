# cocos2dx-strategy-skill scripts/ — 脚本子索引

> 完整索引见 [SCRIPTS-INDEX.md](../../skills/common/scripts/SCRIPTS-INDEX.md)（canonical）。本文件为该 skill 的脚本清单。
> 查找脚本先查索引表，禁止自行 `ls`（AGENTS.md §1.10）。

| 脚本 | 角色 |
|------|------|
| `workflow/sub-stage-cocos-static-analyze.py` | Cocos2d-x 静态分析 |
| `workflow/sub-stage-cocos-lua-extract.py` | Lua 提取 |
| `common/frida-cocos-text-capture.py` | 运行时捕获 Label::setString 动态文本（汉化清单/语言验证） |
| `common/lsposed-hook-scaffold/` | LSPosed hook 脚手架（PairIP 绕过 + IAP/广告转发 + 强制中文） |

## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
