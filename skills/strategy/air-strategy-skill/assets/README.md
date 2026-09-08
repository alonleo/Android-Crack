# AIR Strategy Skill — Assets 资源索引

> 本目录包含 air-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md                  # 本文件
├── known-air-games.tsv        # 已知 AIR 项目列表
├── swf-deobfuscation-rules.md # SWF 反混淆规则
└── ffdec-batch-script.xml     # ffdec 批处理配置样例
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-air-games.tsv` | 启发式预判 | 只追加不删改 |
| `swf-deobfuscation-rules.md` | 阶段 air-03 反编译失败时 | 启发式正则 |
| `ffdec-batch-script.xml` | 批量处理多个 SWF | 多 module 项目 |

## 扩展规则

- 新增资源前必须评估：是项目级（→ `crackings/<type>/<Name>/raw/`）还是 skill 级（→ `assets/`）
- skill 级资源须被 2 个以上项目复用
- 命名 `<scope>-<format>`（如 `swf-deobfuscation-rules.md`）

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程