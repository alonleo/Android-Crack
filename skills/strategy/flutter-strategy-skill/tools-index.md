# Flutter Tools Index — 工具与脚本索引

> 本文件是 flutter-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **blutter** | `tools/crack-intergration-tools/` | Dart AOT 反编译 | flutter-03 |
| **reFlutter** | `tools/crack-intergration-tools/` | Dart AOT 备选反编译 | flutter-03 |
| **Dart SDK** | `tools/crack-intergration-tools/` | `dart-disassemble` | flutter-03 |
| **IDA** / **Ghidra** | 系统 / `tools/` | libapp.so 反汇编 | flutter-03 |
| **Frida** | 系统安装 | 动态 hook Dart 函数 | 11 |

### 1.2 备选工具

| 工具 | 用途 | 何时使用 |
|------|------|---------|
| **Dart Snapshot Analyzer** | 旧版 Dart 反编译 | blutter 输出质量差 |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-flutter-static-analyze.py` | flutter-03 | Flutter Dart AOT 静态分析（blutter/reFlutter 封装） |

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `flutter-version-detect.py` | Flutter 引擎版本检测 |
| `dart-bridge-analyze.py` | Dart ↔ Java 桥接分析 |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-flutter-apps.tsv          # 已知 Flutter 应用列表
└── flutter-engine-rvas.md          # Flutter 引擎常用 RVA 段注释
```

## 5. 工具调用示例

### 5.1 flutter-03（Dart AOT dump）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-flutter-03

# blutter
blutter crackings/<type>/<Name>/raw/01-apktool/lib/arm64-v8a/libapp.so \
       --output crackings/<type>/<Name>/raw/03-flutter-blutter
```

### 5.2 Flutter 版本检测

```bash
python3 skills/strategy/flutter-strategy-skill/scripts/common/flutter-version-detect.py \
  crackings/<type>/<Name>/raw/01-apktool/lib/arm64-v8a/libflutter.so
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

