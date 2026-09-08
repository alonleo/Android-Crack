# Cocos2d-x Strategy Skill — Workflow Scripts

> 同步规则：本目录是 **canonical 副本**，`skills/common/scripts/` 也有同名副本供 `crack.py` 主驱动调度。
> 修改时必须**双向同步**。

---

| 脚本 | 阶段 | 角色 | 调用方式 |
|------|------|------|---------|
| `sub-stage-cocos-static-analyze.py` | **cocos-03** | so + Lua 静态分析（readelf + objdump） | `crack.py <apk> stage-cocos-03` |
| `sub-stage-cocos-lua-extract.py` | **cocos-05** | Lua 提取 / 解密 | `crack.py <apk> stage-cocos-05` |

## 同步规则

见 [AGENTS.md §1.3](../../../../AGENTS.md#13-脚本硬规范)。