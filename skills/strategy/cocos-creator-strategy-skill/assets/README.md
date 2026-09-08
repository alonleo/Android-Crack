# Cocos Creator Strategy Skill — Assets 资源索引

> 本目录包含 cocos-creator-strategy-skill 专用的资源文件。

---

## 目录结构

```
assets/
├── README.md
├── known-cocos-creator-games.tsv    # 已知 Cocos Creator 游戏列表
├── xxtea-key-patterns.md            # XXTEA 密钥在 .so 中的位置模式
└── jsc-encryption-modes.md          # .jsc 加密模式汇总
```

## 资源使用规则

| 资源 | 使用时机 | 备注 |
|------|---------|------|
| `known-cocos-creator-games.tsv` | 启发式预判 | 只追加不删改 |
| `xxtea-key-patterns.md` | cocos-03 密钥提取失败 | reverse / frida 启发式 |
| `jsc-encryption-modes.md` | cocos-05 | xxtea / xxtea-base64 / 自定义 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具与脚本索引
- [../strategy.md](../strategy.md) — 类型策略
- [../workflow.md](../workflow.md) — 阶段流程