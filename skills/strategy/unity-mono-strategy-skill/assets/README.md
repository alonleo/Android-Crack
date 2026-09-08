# Unity Mono Strategy Skill — Assets 资源索引

> 本目录包含 unity-mono-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md
├── known-unity-mono-games.tsv   # 已知 Unity Mono 游戏列表
└── dll-deobfuscation-rules.md   # .NET DLL 反混淆规则
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-unity-mono-games.tsv` | 启发式预判 | 只追加不删改 |
| `dll-deobfuscation-rules.md` | DLL 反编译失败时 | de4dot + 反混淆规则 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程