# Unreal Strategy Skill — Workflow Scripts

> 同步规则：本目录是 **canonical 副本**，`skills/common/scripts/` 也有同名副本供 `crack.py` 主驱动调度。

---

| 脚本 | 阶段 | 角色 | 调用方式 |
|------|------|------|---------|
| `sub-stage-unreal-static-analyze.py` | **unreal-03** | UE .pak 资源包提取分析（UE dumper/FModel 封装） | `crack.py <apk> stage-unreal-03` |