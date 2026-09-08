# Xamarin Tools Index — 工具与脚本索引

> 本文件是 xamarin-strategy-skill 的"工具索引"。
>
> 加载顺序：strategy.md → workflow.md → **[tools-index.md（本文件）]**

---

## 1. 外部工具

### 1.1 强制工具（与 unity-mono 复用）

| 工具 | 路径 | 用途 | 阶段 |
|------|------|------|------|
| **ILSpy** | `source-projects/ILSpy/` | .NET DLL 反编译（跨平台 Avalonia） | mono-03 |
| **dnSpy** | `source-projects/dnSpy/` | .NET DLL 反编译 + 调试 + 编辑 | mono-03 / DLL 替换 |
| **apktool** | `execable/apktool.jar` | APK 解包 / 打包 | 02 / 10 |
| **Frida** | 系统安装 | 动态 hook managed code | 11 |

> **复用提示**：Xamarin 与 Unity Mono 使用同一套工具链（ILSpy/dnSpy），详细文档见 [unity-mono-strategy-skill/tools-index.md](../unity-mono-strategy-skill/tools-index.md)。

## 2. 模板文件

| 模板 | 路径 | 用途 |
|------|------|------|
| `my.keystore.jks` | `skills/common/scripts/template-files/my.keystore.jks` | 统一签名密钥 |

## 3. Skill 内部脚本

### 3.1 scripts/workflow/

| 脚本 | 阶段 | 角色 |
|------|------|------|
> **脚本**：`sub-stage-mono-static-analyze.py`（复用 [unity-mono-strategy-skill](../../unity-mono-strategy-skill/scripts/workflow/) 同一脚本）
> **调用**：`crack.py <apk> stage-mono-03`

> 复用 [unity-mono-strategy-skill/scripts/workflow/](../unity-mono-strategy-skill/scripts/workflow/) 同一脚本即可。

### 3.2 scripts/common/

| 脚本 | 角色 |
|------|------|
| `dll-signature-bypass-frida.js` | DLL 包签名校验绕过（Frida 模板） |

> 复用 [unity-mono-strategy-skill/scripts/common/](../unity-mono-strategy-skill/scripts/common/) 同一脚本即可。

## 4. Skill assets/ 资源

```
assets/
├── README.md
└── known-xamarin-apps.tsv    # 已知 Xamarin 应用列表
```

## 5. 工具调用示例

### 5.1 mono-03（DLL 反编译）

```bash
# 通过 crack.py 主驱动
./skills/common/scripts/crack.py <apk> stage-mono-03

# 直接调用
ilspycmd -p crackings/<type>/<Name>/raw/01-apktool/assemblies/<app>.dll \
         -o crackings/<type>/<Name>/raw/03-mono/
```

### 5.2 DLL 签名校验绕过

```bash
frida -U -f <pkg> \
  -l skills/strategy/xamarin-strategy-skill/scripts/common/dll-signature-bypass-frida.js \
  --no-pause
```

## 6. 关联阅读

- [strategy.md](./strategy.md) — 类型策略
- [workflow.md](./workflow.md) — 阶段流程
- [EXPERIENCES.md](../../EXPERIENCES.md) — 经验沉淀
- [../unity-mono-strategy-skill/](../unity-mono-strategy-skill/) — 工具链复用
- [../../AGENTS.md §6](../../AGENTS.md) — 主仓库工具路径速查表

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |

