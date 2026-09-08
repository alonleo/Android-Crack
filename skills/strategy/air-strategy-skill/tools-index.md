# Adobe AIR Tools Index — 工具与脚本索引

> 本文件是 air-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **ffdec** | `tools/crack-intergration-tools/source-projects/ffdec/` | SWF 反编译 + 编辑 | air-03 / air-09 |
| **jadx** | `source-projects/jadx/` | Java 容器层反编译 | 03 |
| **apktool** | `execable/apktool.jar` | APK 解包 / 打包 | 02 / 10 |
| **AIR SDK** | `tools/crack-intergration-tools/` | AIR 应用构建 / 解包 | air-03 / 12 |

### 1.2 备选工具

| 工具 | 用途 | 何时使用 |
|------|------|---------|
| **jpexs-decompiler** | 开源 SWF 反编译备选 | ffdec 失败时 |
| **Flasm** | SWF 字节码操作 | Stage3D 不可 hook 时部分编辑 |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-air-static-analyze.py` | air-03 | ffdec SWF 反编译 + 静态分析 |
| `sub-stage-air-fonts.py` | air-09 | AIR 字体嵌入到 SWF（中文字体替换） |

> **同步规则**：这些脚本同步保留在 `skills/common/scripts/`（供 `crack.py` 主驱动调度），canonical 副本在 `skills/strategy/air-strategy-skill/scripts/workflow/`。修改时必须**双向同步**。

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `swf-text-import.sh` | SWF 文本批量导入（继承自原 air-localization skill） |
| `swf-resource-extract.py` | SWF 资源提取（图片 / 字体 / 音频） |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-air-games.tsv         # 已知 AIR 项目列表
├── swf-deobfuscation-rules.md  # SWF 反混淆规则
└── ffdec-batch-script.xml      # ffdec 批处理配置样例
```

## 5. 工具调用示例

### 5.1 air-03（SWF 反编译）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-air-03

# 手动
java -jar tools/crack-intergration-tools/source-projects/ffdec/ffdec.jar \
     -export script \
     crackings/<type>/<Name>/raw/05-air-swf \
     crackings/<type>/<Name>/raw/01-apktool/assets/main.swf
```

### 5.2 air-09（字体嵌入）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-air-09

# 手动
java -jar ffdec.jar -replace \
     skills/common/scripts/template-files/LXGWWenKai-Regular.ttf \
     crackings/<type>/<Name>/project/app/src/main/assets/main.swf
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

