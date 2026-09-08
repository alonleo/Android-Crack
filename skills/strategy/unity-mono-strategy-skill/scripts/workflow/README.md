# Unity Mono Strategy Skill — Workflow Scripts

> 同步规则：本目录是 **canonical 副本**，`skills/common/scripts/` 也有同名副本供 `crack.py` 主驱动调度。

---

| 脚本 | 阶段 | 角色 | 调用方式 |
|------|------|------|---------|
| `sub-stage-mono-static-analyze.py` | **mono-03** | .NET DLL 静态分析（ILSpy/dnSpy 封装） | `crack.py <apk> stage-mono-03` |

> **注意**：xamarin-strategy-skill 与 unity-mono 使用同一套工具链，共享此脚本。