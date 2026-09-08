# Unreal Tools Index — 工具与脚本索引

> 本文件是 unreal-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **UE dumper** | `tools/crack-intergration-tools/` | .pak 资源包解包 | unreal-03 |
| **FModel** | `tools/crack-intergration-tools/` | .pak GUI 解包 | unreal-03 |
| **IDA** / **Ghidra** | 系统 / `tools/` | libUE4.so 反汇编（100-500 MB） | 03b-style 分析 |
| **And64InlineHook** | `source-projects/And64InlineHook/` | ARM64 inline hook | 08b-style 集成 |
| **Frida** | 系统安装 | 动态 hook | 11 |

### 1.2 备选工具

| 工具 | 用途 | 何时使用 |
|------|------|---------|
| **Radare2** | 轻量级反汇编 | 快速分析 |
| **Ghidra** | 开源反汇编 | 无 IDA license |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-unreal-static-analyze.py` | unreal-03 | UE .pak 资源包提取分析（UE dumper/FModel 封装） |

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `ue-pak-decrypt.py` | .pak 加密资源包解包（已知密钥） |
| `ue-symbol-recovery-ida.py` | IDA 反射类名恢复脚本 |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-unreal-games.tsv   # 已知 UE 项目列表
└── libue4-common-rvas.md    # libUE4.so 常用 RVA 段注释
```

## 5. 工具调用示例

### 5.1 unreal-03（.pak 解包）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-unreal-03

# UE dumper
ue-dumper --input crackings/<type>/<Name>/raw/01-apktool/assets/<Project>/Content/Paks \
          --output crackings/<type>/<Name>/raw/03-unreal-pak

# FModel GUI
FModel → Open Directory → 选 Paks 目录 → 全部导出
```

### 5.2 .pak 加密解包

```bash
python3 skills/strategy/unreal-strategy-skill/scripts/common/ue-pak-decrypt.py \
  --key <KEY> \
  --input crackings/<type>/<Name>/raw/01-apktool/assets/<Project>/Content/Paks \
  --output crackings/<type>/<Name>/raw/03-unreal-pak-decrypted
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

