# Unity Mono Tools Index — 工具与脚本索引

> 本文件是 unity-mono-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **ILSpy** | `source-projects/ILSpy/` | .NET DLL 反编译（跨平台 Avalonia） | mono-03 |
| **dnSpy** | `source-projects/dnSpy/` | .NET DLL 反编译 + 调试 + 编辑（WPF） | mono-03 / DLL 替换 |
| **apktool** | `execable/apktool.jar` | APK 解包 / 打包 | 02 / 10 |
| **Frida** | 系统安装 | 动态 hook C# 函数 | 11 |

### 1.2 备选工具

| 工具 | 用途 | 何时使用 |
|------|------|---------|
| **dotPeek** | JetBrains .NET 反编译 | ILSpy 输出质量不佳时 |
| **de4dot** | .NET 反混淆 | 代码混淆 |

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-mono-static-analyze.py` | mono-03 | ILSpy / dnSpy DLL 反编译 |

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `dll-signature-bypass-frida.js` | DLL 包签名校验绕过（Frida 模板） |
| `ilspy-batch-export.py` | ILSpy 批量导出（命令行封装） |

## 4. Skill assets/ 资源

```
assets/
├── README.md
├── known-unity-mono-games.tsv   # 已知 Unity Mono 游戏列表
└── dll-deobfuscation-rules.md   # .NET DLL 反混淆规则
```

## 5. 工具调用示例

### 5.1 mono-03（DLL 反编译）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-mono-03

# 手动（ILSpy 命令行）
ilspycmd -p crackings/<type>/<Name>/raw/03-mono/Assembly-CSharp.dll \
         -o crackings/<type>/<Name>/raw/03-mono/Assembly-CSharp-decompiled/

# 手动（dnSpy GUI）
dnSpy.exe → File → Open → Assembly-CSharp.dll
```

### 5.2 DLL 替换

```bash
# 通过 dnSpy GUI：Edit Method → 编译 → 保存
# 然后注入到 APK：
zip -j crackings/<type>/<Name>/project/app-as-generated.apk \
     crackings/<type>/<Name>/raw/03-mono/Assembly-CSharp-modified.dll
```

### 5.3 DLL 签名校验绕过

```bash
frida -U -f <pkg> \
  -l skills/strategy/unity-mono-strategy-skill/scripts/common/dll-signature-bypass-frida.js \
  --no-pause
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

