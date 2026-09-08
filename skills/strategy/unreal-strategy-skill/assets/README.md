# Unreal Strategy Skill — Assets 资源索引

> 本目录包含 unreal-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md
├── known-unreal-games.tsv   # 已知 UE 项目列表
└── libue4-common-rvas.md    # libUE4.so 常用 RVA 段注释
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-unreal-games.tsv` | 启发式预判 | 只追加不删改 |
| `libue4-common-rvas.md` | libUE4.so 分析 | IAP / 广告 / 反作弊 RVA |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程