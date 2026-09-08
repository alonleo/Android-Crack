# Cocos2d-x Strategy Skill — Assets 资源索引

> 本目录包含 cocos2dx-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md
├── known-cocos2dx-games.tsv      # 已知 Cocos2d-x 游戏列表
├── lua-encryption-patterns.md    # Lua 加密模式汇总（.mt / .luac / 自定义）
└── apktool-yaml-template.yml     # Cocos2d-x 专用 apktool.yml 模板
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-cocos2dx-games.tsv` | 启发式预判 | 只追加不删改 |
| `lua-encryption-patterns.md` | 阶段 cocos-05 | XXTEA / .mt / 自定义 |
| `apktool-yaml-template.yml` | 阶段 02 后 | Cocos2d-x 专用配置 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程