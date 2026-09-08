# il2cpp global-metadata.dat 版本限制与替代方案

> 来源: TinkerIslandSurvivalStory (Unity 6 il2cpp) | 2026-07-30
> 作者: Agent

## 问题描述

Unity 6 (2024+) 项目生成的 `global-metadata.dat` 使用 **版本 39+**，原版 Il2CppDumper
（Perfare 维护版）**最多只支持 v38**。尝试 dump 会立即抛出：

```
System.NotSupportedException: ERROR: Metadata file supplied is not a supported version[39].
   at Il2CppDumper.Metadata..ctor(Stream stream)
```

## metadata.dat 版本号识别

`global-metadata.dat` 第 4-7 字节（little-endian uint32）为版本号：

```bash
xxd -l 16 global-metadata.dat
# 00000000: af1b b1fa 2700 0000 7c01 0000 ...
#                ^^^^ 版本号 0x27 = 39
```

| Unity 版本 | metadata 版本 |
|-----------|--------------|
| Unity 2019.x | 24-27 |
| Unity 2020.x | 27-28 |
| Unity 2021.x | 28-29 |
| Unity 2022.x | 29 |
| Unity 2023.x | 31-33 |
| Unity 6 (2024+) | **38-39+** |

## 解决方案

### 方案 A：升级 Il2CppDumper fork（推荐）

```bash
# 1. 升级到支持 v39 的 fork（如 nesrak1/Il2CppDumper 或 GitHub 最新 master）
cd tools/crack-intergration-tools/source-projects/Il2CppDumper
git fetch
git log --oneline --all | head -5  # 找支持 v39 的 commit
# 或用 Il2CppInspectorPro（更新且包含 CLI 模式）
```

### 方案 B：用 Unity 6 兼容工具（Il2CppInspector Redux）

```bash
# Il2CppInspector Redux 支持最新的 metadata 版本
cd tools/crack-intergration-tools/source-projects/Il2CppInspectorPro
dotnet build Il2CppInspector.Redux.CLI/Il2CppInspector.Redux.CLI.csproj -c Release -f net8.0
# 运行
dotnet Il2CppInspector.Redux.CLI/bin/Release/net8.0/Il2CppInspector.Redux.CLI.dll \
    --input libil2cpp.so \
    --metadata global-metadata.dat \
    --output out/
```

### 方案 C：strings + UnityPy 替代（已在本会话验证可行）

**无需 dump.cs，也能获得 95% 文本/类名信息**：

```bash
# 1. C# Metadata 字符串（90K 条，含所有字面量）
strings -n 6 global-metadata.dat | sort -u > metadata-strings.txt

# 2. libil2cpp.so C 字符串（9K 条）
strings -n 6 libil2cpp.so | sort -u > libil2cpp-strings.txt

# 3. C# 类名（从 MonoScript 对象，1478 类）
# 见 sub-stage-extract-unity-textures.py 输出 _manifest.json
```

**覆盖度**:
- ✅ 所有 C# 字面量字符串
- ✅ 所有 C# 命名空间/类名/方法签名（来自 metadata 字符串表）
- ✅ Unity 资源内 Texture2D/Sprite/MonoScript 元数据
- ❌ 函数体 RVA / 参数签名（需要 Il2CppInspector）

## 已知 APK metadata 版本对应

| APK | Unity 版本 | metadata v |
|-----|-----------|-----------|
| RealmDefenseHeroLegendsTD | Unity 2022 | 29 |
| WonkasWorldOfCandyMatch3 | Unity 2022 | 29 |
| TinkerIslandSurvivalStory | Unity 6 | **39** |
| FarmHeroesSuperSaga | (TBD) | TBD |

## 预防

- 新 APK 嗅探阶段，先 `xxd -s 4 -l 4 global-metadata.dat` 看版本
- 若 v > 38，立即跳过 Il2CppDumper，改用 strings + UnityPy 方案
- 若必须 hook C# 函数，需要 Il2CppInspector Redux

## 相关脚本

- `skills/common/general-strategy-skill/scripts/workflow/sub-stage-extract-all-strings.py` — 6 个数据源字符串提取（含 strings fallback）
- `skills/common/general-strategy-skill/scripts/workflow/sub-stage-extract-unity-textures.py` — UnityPy 资产提取（含 MonoScript 类名反推）
- `skills/strategy/il2cpp-strategy-skill/scripts/workflow/stage-03b-il2cpp-dump.py` — 旧 Il2CppDumper 调用（v > 38 时失败）
## [supersedes 部分内容] Flying Gorilla (2026-08-02)：v39 可用 Il2CppInspectorRedux 直接 dump

> 上述"预防"章节建议 v > 38 时跳过 Il2CppDumper 改用 strings。FlyingGorillaEndlessRunner
> (Unity 6000.3.0b1, metadata v39) 实测 **Il2CppInspectorRedux 可以直接完整 dump**，
> 无需 strings fallback。

### Il2CppInspectorRedux 用法（v39 实测）

```bash
INSPECTOR=tools/crack-intergration-tools/execable/Il2CppInspectorRedux/Il2CppInspector
# ⚠️ 必须先移走 plugins/（存在则启动即崩 ArgumentNullException 'con'）
mv "$(dirname $INSPECTOR)/plugins" /tmp/plugins_bak

$INSPECTOR -i <fat.apk> --select-outputs \
    --cs-out dump/dump.cs \
    --json-out dump/metadata.json \
    --cpp-out dump/cpp-out

mv /tmp/plugins_bak "$(dirname $INSPECTOR)/plugins"   # 恢复
```

### 输出差异（相对 Il2CppDumper）

| 产物 | Il2CppDumper | Il2CppInspectorRedux |
|------|-------------|---------------------|
| dump.cs | ✓ | ✓（`// 0xSTART-0xEND` RVA 格式，无 `// RVA:` 前缀） |
| il2cpp.h | ✓（聚合头） | ✗（改为 `cpp-out/appdata/{il2cpp-types,il2cpp-functions,il2cpp-api-functions,...}.h`） |
| DummyDll/ | ✓ | ✗ |
| stringliteral.json | ✓ | ✗（字符串在 `metadata.json → addressMap.stringLiterals[].string`） |
| metadata.json | ✗ | ✓（190MB 级，2.7M 行） |

### 对后续 stage 的影响（[FLOWFIX] 已适配 stage-05）

- stage-05 `verify_dump` / `install_headers` 已兼容两种输出（il2cpp.h 或 cpp-out/appdata）
- stage-09 汉化字符串提取：从 `metadata.json → addressMap.stringLiterals` 生成 stringliteral.json
- stage-06 hook 计划：RVA 正则需同时匹配 `// RVA: 0x...` 与 `// 0x...-0x...`
