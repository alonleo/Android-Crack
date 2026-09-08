# Android Strategy Skill — Common Scripts 索引

> 本目录是 android-strategy-skill 的**通用脚本**（跨阶段工具）。

---

## 目录结构

```
scripts/common/
├── grep-dex-smali.py
├── filter-dex-jar.sh
└── apksigner-verify.py
```

## 脚本说明

| 脚本 | 角色 |
|------|------|
| `grep-dex-smali.py` | smali 目录中 grep 任意模式（按 SDK 名 / 类名） |
| `filter-dex-jar.sh` | 过滤 dex-jar 中的 R 类冲突 |
| `apksigner-verify.py` | 统一 apksigner verify 输出格式 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具索引
- [../../workflow/README.md](../../workflow/README.md) — 流程脚本索引