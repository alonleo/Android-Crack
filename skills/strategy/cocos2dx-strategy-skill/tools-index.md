# Cocos2d-x Tools Index — 工具与脚本索引

> 本文件是 cocos2dx-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **apktool** | `execable/apktool.jar` | APK 解包 / 打包 | 02 / 10 |
| **readelf** | 系统 | ELF 分析 | cocos-03 |
| **objdump** | 系统 | 反汇编 | cocos-03 |
| **Frida** | 系统 | 动态 hook | cocos-03 / 11 |
| **jadx** | `source-projects/jadx/` | Java 层反编译 | 03 |
| **IDA / Ghidra** | 可选 | so 深度分析 | cocos-03 |

### 1.2 Lua 工具

| 工具 | 路径 | 用途 | 何时使用 |
|------|------|------|---------|
| **cocos-lua-extract** | `source-projects/` | Lua 解密（常见 .mt / .luac） | cocos-05 |
| 自写解密脚本 | `scripts/common/lua-decrypt.py` | XXTEA / 自定义加密 | 密钥已知 |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-cocos-static-analyze.py` | cocos-03 | readelf + objdump 分析 libMyGame.so（so 结构 + Lua 注册函数） |
| `sub-stage-cocos-lua-extract.py` | cocos-05 | Lua 提取 / 解密（.luac / .mt / XXTEA） |

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `lua-decrypt.py` | XXTEA / 自定义 Lua 解密 |
| `so-function-export.py` | .so 函数符号提取（readelf + objdump 包装） |
| `cocos-bridge-analyze.py` | Java↔Lua↔C++ 桥接调用图生成 |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-cocos2dx-games.tsv      # 已知 Cocos2d-x 游戏列表
├── lua-encryption-patterns.md    # Lua 加密模式汇总（.mt / .luac / 自定义）
└── apktool-yaml-template.yml     # Cocos2d-x 专用 apktool.yml 模板
```

## 5. 工具调用示例

### 5.1 cocos-03（so 分析）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-cocos-03

# 手动
readelf -a crackings/<type>/<Name>/raw/01-apktool/lib/arm64-v8a/libMyGame.so \
  > crackings/<type>/<Name>/raw/03-cocos-so/readelf-output.txt
objdump -d libMyGame.so | grep "luaopen_" \
  > crackings/<type>/<Name>/raw/03-cocos-so/luaopen-functions.txt
```

### 5.2 cocos-05（Lua 解密）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-cocos-05

# 手动
python3 skills/strategy/cocos2dx-strategy-skill/scripts/common/lua-decrypt.py \
  --key <XXTEA_KEY> \
  --input crackings/<type>/<Name>/raw/01-apktool/assets/ \
  --output crackings/<type>/<Name>/raw/05-cocos-lua/decrypted/
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


## LSPosed / PairIP 绕过工具

| 工具/脚本 | 路径 | 用途 |
|----------|------|------|
| LSPosed 模块配置 | `skills/common/scripts/lsposed-config.py` | 启用 LSPosed 模块 + 添加作用域（修改 modules_config.db） |
| LSPosed hook 脚手架 | `scripts/common/lsposed-hook-scaffold/` | PairIP 绕过 + IAP/广告转发 + 强制中文（完整模板） |
| Frida 文本捕获 | `scripts/common/frida-cocos-text-capture.py` | 运行时捕获 Label::setString 文本 |
