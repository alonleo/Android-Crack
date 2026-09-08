# Cocos Creator Strategy Skill — Common Scripts 索引

> 本目录是 cocos-creator-strategy-skill 的**通用脚本**（跨阶段工具）。

---

## 目录结构

```
scripts/common/
├── cocos2d-dec.py         # XXTEA .jsc / .lua 批处理解密
├── jsc-decrypt.py         # JSC-PyDecrypt-Tool 包装
├── xxtea-key-extract.py   # 从 reverse / frida 输出提取 XXTEA 密钥
└── ccon-decode.py         # .cconb / .ccon 二进制解码（v1 JSON / v2 notepack）
```

## 脚本说明

| 脚本 | 角色 |
|------|------|
| `cocos2d-dec.py` | XXTEA .jsc / .lua 批处理解密 |
| `jsc-decrypt.py` | JSC-PyDecrypt-Tool 包装（xxtea+base64 模式） |
| `xxtea-key-extract.py` | 从 reverse / frida 输出提取 XXTEA 密钥 |
| `ccon-decode.py` | .cconb / .ccon 二进制解码（v1 JSON / v2 notepack） |

## 关联阅读

- [../tools-index.md](../tools-index.md) — 工具索引
- [../../workflow/README.md](../../workflow/README.md) — 流程脚本索引