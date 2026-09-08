# Air Strategy Skill — Workflow Scripts

> 同步规则：本目录是 **canonical 副本**，`skills/common/scripts/` 也有同名副本供 `crack.py` 主驱动调度。
> 修改时必须**双向同步**。

---

| 脚本 | 阶段 | 角色 | 调用方式 |
|------|------|------|---------|
| `sub-stage-air-static-analyze.py` | **air-03** | ffdec SWF 反编译 + 静态分析 | `crack.py <apk> stage-air-03` |
| `sub-stage-air-fonts.py` | **air-09** | AIR SWF 字体嵌入（中文字体替换） | `crack.py <apk> stage-air-09` |

## 同步规则

见 [AGENTS.md §1.3](../../../../AGENTS.md#13-脚本硬规范)。