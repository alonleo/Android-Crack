# Cocos Creator Tools Index — 工具与脚本索引

> 本文件是 cocos-creator-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具（6 个）

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **cc-reverse** | `source-projects/cc-reverse/` + `execable/cc-reverse` | ⭐ 自动检测版本 + 解密 + 项目重建 | cocos-03 |
| **reverse** | `source-projects/reverse-tool/` + `execable/reverse` | Cocos ARM64 静态分析 + XXTEA 密钥提取 | cocos-03 |
| **cocos2d-dec** | `source-projects/cocos2d-dec/` | Python 批处理解密 .jsc / .lua | cocos-05 |
| **JSC-PyDecrypt-Tool** | `source-projects/JSC-PyDecrypt-Tool/` | 命令行 JSC 解密（xxtea+base64） | cocos-05 |
| **frida-cocosjs** | `source-projects/frida-cocosjs/` | Frida 动态 Hook Cocos JS 引擎 | cocos-03 / cocos-05 |
| **il2Fusion** | `source-projects/il2Fusion/` | Android 侧 Unity/Cocos2d-x Lua 运行时代理 | cocos-05 |

### 1.2 备选工具

| 工具 | 用途 | 何时使用 |
|------|------|---------|
| **jsvmp-deobfuscator** | JS 混淆还原 | 还原 JS 仍混淆时 |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/（流程脚本）

> Cocos Creator 类型**无专用流程脚本**。阶段 cocos-03 / cocos-05 复用 [cocos2dx-strategy-skill](../../cocos2dx-strategy-skill/scripts/workflow/) 的脚本：
>
> | 调用方式 | 实际脚本 |
> |---------|---------|
> | `crack.py <apk> stage-cocos-03` | `skills/strategy/cocos2dx-strategy-skill/scripts/workflow/sub-stage-cocos-static-analyze.py` |
> | `crack.py <apk> stage-cocos-05` | `skills/strategy/cocos2dx-strategy-skill/scripts/workflow/sub-stage-cocos-lua-extract.py` |

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `cocos2d-dec.py` | XXTEA .jsc / .lua 批处理解密 |
| `jsc-decrypt.py` | JSC-PyDecrypt-Tool 包装 |
| `xxtea-key-extract.py` | 从 reverse / frida 输出提取 XXTEA 密钥 |
| `ccon-decode.py` | .cconb / .ccon 二进制解码（v1 JSON / v2 notepack） |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-cocos-creator-games.tsv    # 已知 Cocos Creator 游戏列表
├── xxtea-key-patterns.md            # XXTEA 密钥在 .so 中的位置模式
└── jsc-encryption-modes.md          # .jsc 加密模式汇总
```

## 5. 工具调用示例

### 5.1 cocos-03（cc-reverse 自动分析）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-cocos-03

# 直接调用
cc-reverse --path crackings/<type>/<Name>/raw/01-apktool --verbose

# 强制指定版本
cc-reverse --path ... --version-hint 3.x
```

### 5.2 XXTEA 密钥提取（密钥未知时）

```bash
# 静态（reverse 从 .so 提取）
reverse libcocos2djs.so --extract-xxtea-key

# 动态（frida-cocosjs 运行时钩取）
frida -U -f <pkg> \
  -l tools/crack-intergration-tools/source-projects/frida-cocosjs/hook-cocos.js \
  --no-pause
```

### 5.3 cocos-05（批量解密 .jsc）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-cocos-05

# 手动
python3 skills/strategy/cocos-creator-strategy-skill/scripts/common/cocos2d-dec.py \
  --key <XXTEA_KEY> \
  --input crackings/<type>/<Name>/raw/01-apktool/assets/src \
  --output crackings/<type>/<Name>/raw/05-cocos-decrypted
```

## 6. 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [workflow.md](./workflow.md) — 阶段流程
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../../AGENTS.md §6](../../AGENTS.md) — 主仓库工具路径速查表

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |

