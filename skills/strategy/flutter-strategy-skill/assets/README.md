# Flutter Strategy Skill — Assets 资源索引

> 本目录包含 flutter-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md
├── known-flutter-apps.tsv          # 已知 Flutter 应用列表
└── flutter-engine-rvas.md          # Flutter 引擎常用 RVA 段注释
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-flutter-apps.tsv` | 启发式预判 | 只追加不删改 |
| `flutter-engine-rvas.md` | libflutter.so 分析 | IAP / 广告 / 反作弊 RVA |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程