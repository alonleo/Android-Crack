# Cocos2d-x Strategy Skill — Common Scripts 索引

> 本目录是 cocos2dx-strategy-skill 的**通用脚本**（跨阶段工具）。

---

## 目录结构

```
scripts/common/
├── lua-decrypt.py             # XXTEA / 自定义 Lua 解密
├── so-function-export.py      # .so 函数符号提取（readelf + objdump 包装）
└── cocos-bridge-analyze.py    # Java↔Lua↔C++ 桥接调用图生成
```

## 脚本说明

| 脚本 | 角色 |
|------|------|
| `lua-decrypt.py` | XXTEA / 自定义 Lua 解密（接受 --key + --input + --output） |
| `so-function-export.py` | .so 函数符号提取（readelf + objdump 包装） |
| `cocos-bridge-analyze.py` | Java↔Lua↔C++ 桥接调用图生成 |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具索引
- [../../workflow/README.md](../../workflow/README.md) — 流程脚本索引