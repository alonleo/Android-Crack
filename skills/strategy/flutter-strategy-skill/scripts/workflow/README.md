# Flutter Strategy Skill — Workflow Scripts

> 同步规则：本目录是 **canonical 副本**，`skills/common/scripts/` 也有同名副本供 `crack.py` 主驱动调度。

---

| 脚本 | 阶段 | 角色 | 调用方式 |
|------|------|------|---------|
| `sub-stage-flutter-static-analyze.py` | **flutter-03** | Flutter Dart AOT 静态分析（blutter/reFlutter 封装） | `crack.py <apk> stage-flutter-03` |