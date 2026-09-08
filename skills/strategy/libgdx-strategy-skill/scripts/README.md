# libgdx-strategy-skill 脚本子索引

> 本文件是 libgdx-strategy-skill 的脚本子索引（SCRIPTS-INDEX.md 的精简版）。

## workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-libgdx-cleanup.py` | 09 | libGDX SDK 清理：manifest 清理 + 广告 .so 删除 + FB/Firebase/ThinkingData 桩化链 |

## assets/

| 文件 | 角色 |
|------|------|
| `frida-hook-assets.js` | hook AssetManager.open 探测资源加载 |
| `frida-hook-font.js` | hook Typeface.createFromAsset 探测字体 |

## 去功能点清单

`../stages/ui-hide/default-action/step-load-feature-checklist.py`：阶段首步委托统一 YAML 加载器；清单维护使用 common/feature-removal-strategy-skill 的 manage-feature-checklist.py。
