# TOOLS_DEPS.md — tools/crack-intergration-tools/ 项目反向引用清单

> **本文件由 `gen-tools-deps-doc.py` 自动生成**——扫描仓库所有 .py/.md/.yaml 对
> `tools/crack-intergration-tools/{source-projects,execable,docs}/` 项目的引用。
> 
> **何时加载**：Agent 需新增工具引用 / 排查工具缺失 / 升级工具版本 /
> 清理孤立工具时**先查本文件**再操作（AGENTS.md §1.13 严禁误删）。
> **来源**：仓库自维护工具库（AGENTS.md §6）。
> **写入规则**（AGENTS.md §1.6）：**只追加不删改**；新增引用时在本文件
> 对应项目下追加引用条目；删工具时在原条加 `[supersedes: <原条目>]`。

---

## 1. 概览

- **仓库项目总数**：71（含 source-projects / execable / docs 三类）
- **被引用项目数**：33
- **未被引用项目数**：16（孤立工具，谨慎删除前确认）
- **引用总条数**：1760
- **覆盖范围**：`skills/common/scripts/` + `skills/strategy/<type>-strategy-skill/scripts/` + 根文档（AGENTS / WORKFLOW / OBJECTIVES / STRATEGY / EXPERIENCES）

---

## 2. 被引用的项目（按类型分组）

### 2.1 源码

#### `tools/crack-intergration-tools/source-projects/And64InlineHook` — ARM64 inline hook 库（fix-fakerandroid-cmakelists 等用）

**引用计数**：4 处


**引用详情**：

- `crackings/il2cpp/RealmDefenseHeroLegendsTD/tool-calls.md`
  - `cp tools/crack-intergration-tools/source-projects/And64InlineHook/And64InlineHook.cpp app/src/main/cpp/And64InlineHook/`
  - `cp tools/crack-intergration-tools/source-projects/And64InlineHook/And64InlineHook.hpp app/src/main/cpp/include/`
- `skills/strategy/il2cpp-strategy-skill/scripts/workflow/sub-stage-template-integration.py`
  - `源：tools/crack-intergration-tools/source-projects/And64InlineHook/`
- `tools/android-reverse/README.md`
  - `| And64InlineHook | 见子目录 | `tools/crack-intergration-tools/source-projects/And64InlineHook/` | GitHub | ARM64 inline hoo`

#### `tools/crack-intergration-tools/source-projects/Android_Inline_Hook_ARM64` — ARM64 inline hook 替代实现

**引用计数**：2 处


**引用详情**：

- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **Android_Inline_Hook_ARM64** | `tools/crack-intergration-tools/source-projects/Android_Inline_Hook_ARM64/` | ARM64 in`
- `tools/android-reverse/README.md`
  - `| Android_Inline_Hook_ARM64 | 见子目录 | `tools/crack-intergration-tools/source-projects/Android_Inline_Hook_ARM64/` | GitHu`

#### `tools/crack-intergration-tools/source-projects/ILSpy` — .NET 反编译器（unity-mono DLL）

**引用计数**：1 处


**引用详情**：

- `tools/android-reverse/README.md`
  - `| ILSpy | 见子目录 | `tools/crack-intergration-tools/source-projects/ILSpy/` | GitHub | .NET 反编译 | MIT | 已纳入 |`

#### `tools/crack-intergration-tools/source-projects/Il2CppDumper` — Il2CppDumper（dump.cs + il2cpp.h 生成）

**引用计数**：73 处


**引用详情**：

- `crackings/il2cpp/AltosAdventure/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/BattleTank/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/CrowdCity/raw/tool-calls-history.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/DinoBashDinosaurBattle/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/FormulaCarStuntCarGames/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/GangsterGamesCrimeSimulator/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/HeroWarsAllianceRpgLegend/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/HighwayBikeAttackRaceGame/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/MiniCarRacingGameLegends/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/RealmDefenseHeroLegendsTD/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `crackings/il2cpp/TopHeroes/stages/05-il2cpp-dump/report.md`
  - `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/net8.0/Il2CppDumper \`
- `crackings/il2cpp/TopHeroes/tool-calls.md`
  - `dumper=/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/n`
- `skills/strategy/il2cpp-strategy-skill/references/il2cpp-metadata-version-limit.md`
  - `cd tools/crack-intergration-tools/source-projects/Il2CppDumper`
- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **Il2CppDumper** | `tools/crack-intergration-tools/source-projects/Il2CppDumper/` | libil2cpp.so + global-metadata.dat`
- `tools/android-reverse/README.md`
  - `| Il2CppDumper | 见子目录 | `tools/crack-intergration-tools/source-projects/Il2CppDumper/` | GitHub | il2cpp → C# 桩 | MIT | `
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Il2CppDumper.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/Il2CppDumper.csproj`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/Il2CppDumper.csproj`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumpe`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/Il2CppDumper.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/I`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/I`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/I`
  - ...（共 30 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/Il2CppDumper.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/*":"https://raw.gi`
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/PublishOutputs.16c789cfa0.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/Il2CppDu`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/config.j`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/ghidra.p`
  - ...（共 17 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumpe`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/Il2C`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/"`

#### `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro` — Il2CppInspectorPro（Il2CppDumper 备选）

**引用计数**：1016 处


**引用详情**：

- `skills/strategy/il2cpp-strategy-skill/references/il2cpp-metadata-version-limit.md`
  - `cd tools/crack-intergration-tools/source-projects/Il2CppInspectorPro`
- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **Il2CppInspectorPro** | `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/` | 工业级 il2cpp 反编译（含插件系统） `
- `tools/android-reverse/README.md`
  - `| Il2CppInspectorPro | 见子目录 | `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/` | GitHub | il2cpp 工业级`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/Bin2Object.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/Debug/net10.0/Bin2Object.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/D`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/D`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/D`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/Debug/net10.0/Bin2Object.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/Release/net10.0/Bin2Object.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/R`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/R`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/bin/R`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/Release/net10.0/Bin2Object.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/B`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/obj/Il2CppInspector.CLI.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/Il2Cpp`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - ...（共 23 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/obj/Release/net10.0/linux-x64/Il2CppInspector.CLI.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - ...（共 216 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/obj/Release/net10.0/linux-x64/Il2CppInspector.CLI.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/obj/Release/net10.0/linux-x64/PublishOutputs.0aa1f9edbc.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/bin/Rel`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.CLI/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2Cp`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspec`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/Debug/net10.0/Il2CppInspector.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/bin/`
  - ...（共 21 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/Debug/net10.0/Il2CppInspector.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/Il2CppInspector.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/Il2`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - ...（共 17 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/Release/net10.0/Il2CppInspector.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/`
  - ...（共 21 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/Release/net10.0/Il2CppInspector.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Common/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2Cp`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspec`
  - ...（共 7 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Debug/net10.0/Il2CppInspector.Redux.CLI.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - ...（共 59 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Debug/net10.0/Il2CppInspector.Redux.CLI.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Debug/net10.0/staticwebassets.build.json`
  - `{"Version":1,"Hash":"Ghyzgox3OzJsPVvYTZw4tAoxCW6AwK5eoX+i2NllwoA=","Source":"Il2CppInspector.Redux.CLI","BasePath":"/","`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Il2CppInspector.Redux.CLI.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - ...（共 31 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Release/net10.0/linux-x64/Il2CppInspector.Redux.CLI.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - ...（共 387 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Release/net10.0/linux-x64/Il2CppInspector.Redux.CLI.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Release/net10.0/linux-x64/PublishOutputs.6dd65b8dae.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/b`
  - ...（共 8 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Release/net10.0/linux-x64/staticwebassets.build.json`
  - `{"Version":1,"Hash":"Ghyzgox3OzJsPVvYTZw4tAoxCW6AwK5eoX+i2NllwoA=","Source":"Il2CppInspector.Redux.CLI","BasePath":"/","`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/Release/net10.0/linux-x64/staticwebassets.publish.json`
  - `{"Version":1,"Hash":"O5QcySQ4vXBGigYHg5OCmR7aTDeupQfuzH4MJFsnru8=","Source":"Il2CppInspector.Redux.CLI","BasePath":"/","`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.CLI/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2Cp`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspec`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/Debug/net10.0/Il2CppInspector.Redux.FrontendCore.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - ...（共 32 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/Debug/net10.0/Il2CppInspector.Redux.FrontendCore.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/Il2CppInspector.Redux.FrontendCore.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Fron`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2Object/Bin2Object/Bin2`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Bin2O`
  - ...（共 25 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/Release/net10.0/Il2CppInspector.Redux.FrontendCore.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.Front`
  - ...（共 32 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/Release/net10.0/Il2CppInspector.Redux.FrontendCore.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspector.Redux.FrontendCore/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2Cp`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Il2CppInspec`
  - ...（共 7 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/Debug/netstandard2.0/VersionedSerialization.Generator.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - ...（共 11 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/Debug/netstandard2.0/VersionedSerialization.Generator.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/Release/netstandard2.0/VersionedSerialization.Generator.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gene`
  - ...（共 11 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/Release/netstandard2.0/VersionedSerialization.Generator.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/VersionedSerialization.Generator.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gen`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Gen`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Versi`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization.Generator/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Versi`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSer`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/Debug/net10.0/VersionedSerialization.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - ...（共 13 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/Debug/net10.0/VersionedSerialization.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/Release/net10.0/VersionedSerialization.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/bin/`
  - ...（共 13 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/Release/net10.0/VersionedSerialization.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/*":"https://`
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/VersionedSerialization.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/Ver`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/Ver`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Versi`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSerialization/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/Versi`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSe`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppInspectorPro/VersionedSer`

#### `tools/crack-intergration-tools/source-projects/UABEA` — UABEA（Unity Asset Bundle Extractor）

**引用计数**：4 处


**引用详情**：

- `EXPERIENCES.md`
  - `> 工具库 UABEA 的 **AssetsTools.NET**（`tools/crack-intergration-tools/source-projects/UABEA/Libs/`）能`
- `skills/common/scripts/assets-tools-haniz/README.md`
  - `- `tools/crack-intergration-tools/source-projects/UABEA/Libs/AssetsTools.NET.dll``
- `temp/merged-experiences/il2cpp-strategy-skill-experience.md`
  - `> 工具库 UABEA 的 **AssetsTools.NET**（`tools/crack-intergration-tools/source-projects/UABEA/Libs/`）能`
- `tools/android-reverse/README.md`
  - `| UABEA / UABEANext | 见子目录 | `tools/crack-intergration-tools/source-projects/UABEA{,Next}/` | GitHub | Unity 资源包编辑 | MIT`

#### `tools/crack-intergration-tools/source-projects/Underanalyzer` — Undertale 数据解/编译

**引用计数**：87 处


**引用详情**：

- `tools/crack-intergration-tools/docs/underanalyzer/INDEX.md`
  - `- **源码**: `tools/crack-intergration-tools/source-projects/Underanalyzer/`（READONLY）`
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/net10.`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/net10.`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/net10.`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/*":"https://raw.g`
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/Release/netstandard2.1/Underanalyzer.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/netsta`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/netsta`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/bin/Release/netsta`
  - ...（共 11 处，省略）
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/Release/netstandard2.1/Underanalyzer.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/*":"https://raw.g`
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/Underanalyzer.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/Underanalyzer.csp`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/Underanalyzer.csp`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanaly`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanaly`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/Un`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Underanalyzer/Underanalyzer/obj`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Underanalyzer.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/Release/net10.0/UndertaleModCli.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - ...（共 6 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/Release/net10.0/UndertaleModCli.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/*":"https://ra`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/UndertaleModCli.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`
  - ...（共 8 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/project.assets.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/Release/net10.0/UndertaleModLib.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - ...（共 6 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/Release/net10.0/UndertaleModLib.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/*":"https://ra`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/UndertaleModLib.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`
  - ...（共 6 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/project.assets.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`

#### `tools/crack-intergration-tools/source-projects/UndertaleModTool` — GameMaker 数据解/打包

**引用计数**：165 处


**引用详情**：

- `tools/crack-intergration-tools/docs/undertale-mod-tool/06_build_and_run.md`
  - `tools/crack-intergration-tools/source-projects/UndertaleModTool`
  - `cd tools/crack-intergration-tools/source-projects/UndertaleModTool`
- `tools/crack-intergration-tools/docs/undertale-mod-tool/INDEX.md`
  - `- **源码**: `tools/crack-intergration-tools/source-projects/UndertaleModTool/`（READONLY）`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/b`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Release/net10.0/Underanalyzer.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/Underanalyzer.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/Release/net10.0/UndertaleModCli.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/bin/Release/n`
  - ...（共 71 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/Release/net10.0/UndertaleModCli.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/*":"https://ra`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/UndertaleModCli.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/UndertaleMod`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - ...（共 19 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCli/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underta`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModC`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModCl`
  - ...（共 7 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/Release/net10.0/UndertaleModLib.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/bin/Release/n`
  - ...（共 26 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/Release/net10.0/UndertaleModLib.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/*":"https://ra`
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/UndertaleModLib.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/UndertaleMod`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underanalyzer/Underanalyzer/`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underan`
  - ...（共 11 处，省略）
- `tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLib/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/Underta`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModL`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/UndertaleModTool/UndertaleModLi`
  - ...（共 5 处，省略）

#### `tools/crack-intergration-tools/source-projects/Unlimited-OCR` — Unlimited-OCR（OCR 备））

**引用计数**：3 处


**引用详情**：

- `tools/android-reverse/README.md`
  - `| Unlimited-OCR | 见子目录 | `tools/crack-intergration-tools/source-projects/Unlimited-OCR/` | GitHub | SGLang OCR 长上下文识别 | `
- `tools/crack-intergration-tools/docs/tesseract/07_workflow_integration.md`
  - `| **Unlimited-OCR** | `tools/crack-intergration-tools/source-projects/Unlimited-OCR/` | 百度 LLM OCR（SGLang/vLLM server，GP`
  - `OCR_SCRIPT="$REPO_ROOT/tools/crack-intergration-tools/source-projects/Unlimited-OCR/infer.py"`

#### `tools/crack-intergration-tools/source-projects/assetstudio` — Unity 资产解包工具（.NET）

**引用计数**：290 处


**引用详情**：

- `crackings/il2cpp/HighwayBikeAttackRaceGame/findings.md`
  - `AssetStudio（工具库 `tools/crack-intergration-tools/source-projects/assetstudio`）：`
- `skills/common/scripts/assetstudio-haniz/README.md`
  - `> 用 AssetStudio 库（`tools/crack-intergration-tools/source-projects/assetstudio`）正确解析`
  - `cd tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio`
- `tools/android-reverse/README.md`
  - `| assetstudio | 见子目录 | `tools/crack-intergration-tools/source-projects/assetstudio/` | GitHub | Unity .assets / .bundle `
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/obj/AssetStudio.CLI.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/AssetStudio.CLI.c`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/AssetStudio.CLI.c`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - ...（共 45 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/obj/Release/net10.0/AssetStudio.CLI.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.GUI/bin/Release/net10.`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.GUI/bin/Release/net10.`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.GUI/bin/Release/net10.`
  - ...（共 19 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/obj/Release/net10.0/AssetStudio.CLI.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/As`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.CLI/obj`
  - ...（共 7 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/AssetStudio.FBXWrapper.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/AssetStudi`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/AssetStudi`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - ...（共 21 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/Release/net10.0/AssetStudio.FBXWrapper.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - ...（共 15 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/Release/net10.0/AssetStudio.FBXWrapper.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/Release/net8.0/AssetStudio.FBXWrapper.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/bin/Release`
  - ...（共 15 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/Release/net8.0/AssetStudio.FBXWrapper.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWra`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrap`
  - ...（共 11 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/AssetStudio.PInvoke.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/AssetStudio.P`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/AssetStudio.P`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/net10.0/AssetStudio.PInvoke.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/ne`
  - ...（共 10 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/net10.0/AssetStudio.PInvoke.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/net8.0/AssetStudio.PInvoke.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/ne`
  - ...（共 10 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/Release/net8.0/AssetStudio.PInvoke.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvok`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.PInvoke`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/AssetStudio.Utility.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/AssetStudio.U`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.FBXWrapper/AssetStudi`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - ...（共 37 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/Release/net10.0/AssetStudio.Utility.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - ...（共 16 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/Release/net10.0/AssetStudio.Utility.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/Release/net8.0/AssetStudio.Utility.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/bin/Release/ne`
  - ...（共 16 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/Release/net8.0/AssetStudio.Utility.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utilit`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio.Utility`
  - ...（共 15 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/AssetStudio.csproj.nuget.dgspec.json`
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/AssetStudio.csproj": `
  - `"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/AssetStudio.csproj": `
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/Release/net10.0/AssetStudio.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net10.0/Ke`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net10.0/As`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net10.0/As`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/Release/net10.0/AssetStudio.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/Release/net8.0/AssetStudio.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net8.0/Key`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net8.0/Ass`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/bin/Release/net8.0/Ass`
  - ...（共 12 处，省略）
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/Release/net8.0/AssetStudio.sourcelink.json`
  - `{"documents":{"/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/*":"https://raw.git`
- `tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/project.assets.json`
  - `"projectUniqueName": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/`
  - `"projectPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/AssetS`
  - `"outputPath": "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/assetstudio/AssetStudio/obj/",`

#### `tools/crack-intergration-tools/source-projects/cc-reverse` — cocos-creator application.js 解密（已编译版）

**引用计数**：2 处


**引用详情**：

- `skills/strategy/cocos-creator-strategy-skill/scripts/common/decrypt-jsc-assets.py`
  - `CC_REVERSE_DIR = "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/cc-reverse"`
- `skills/strategy/cocos-creator-strategy-skill/scripts/common/repack-jsc-assets.py`
  - `CC_REVERSE_DIR = "/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/cc-reverse"`

#### `tools/crack-intergration-tools/source-projects/dex2jar` — dex2jar 2.4（dex → class jar）

**引用计数**：14 处


**引用详情**：

- `crackings/defold/BananaKong/fix-dex-new-instance.py`
  - `依赖: JDK 11 + ASM 9.x（tools/crack-intergration-tools/execable/dex2jar/）`
- `skills/common/scripts/check-toolchain.py`
  - `DEX2JAR = f"{TOOLS}/crack-intergration-tools/execable/dex2jar"`
- `skills/common/scripts/convert-dex-to-jar.py`
  - `TOOL_DIR = Path(__file__).parent.parent / "crack-intergration-tools/execable/dex2jar"`
- `skills/common/scripts/convert-smali-to-jars.py`
  - `依赖: Java + smali jar（gradle cache 自动查找）+ dex2jar（tools/crack-intergration-tools/execable/dex2jar/）。`
- `skills/common/scripts/dex-dex2jar-classpath.py`
  - `- dex2jar 全套 jar: tools/crack-intergration-tools/execable/dex2jar/*.jar`
- `skills/common/scripts/fix-dex-jar-frames.py`
  - `- ASM 9.x jar（tools/crack-intergration-tools/execable/dex2jar/asm-*.jar）`
  - `d2j = ROOT / "tools/crack-intergration-tools/execable/dex2jar"`
- `skills/common/scripts/fix-dex-new-instance.py`
  - `依赖: JDK 11 + ASM 9.x（tools/crack-intergration-tools/execable/dex2jar/）`
- `skills/common/scripts/fix-dex-tools.py`
  - `DEX_TOOLS = "/home/leo/文档/android-crack/tools/crack-intergration-tools/execable/dex2jar/dex-tools"`
- `skills/common/scripts/strip-kotlin-metadata.py`
  - `d2j = ROOT / "tools/crack-intergration-tools/execable/dex2jar"`
- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **dex2jar** | `tools/crack-intergration-tools/execable/dex2jar/` | dex → 真 .class jar（smali 转 jar 引用，问题 7） | 输出项目装配 |`
- `tools/crack-intergration-tools/docs/dex2jar/README.md`
  - `- 源码: `tools/crack-intergration-tools/source-projects/dex2jar/``
  - `- 可执行: `tools/crack-intergration-tools/execable/dex2jar/`（lib/*.jar + d2j-dex2jar.sh）`
  - `java -cp "tools/crack-intergration-tools/execable/dex2jar/*" \`

#### `tools/crack-intergration-tools/source-projects/dnSpy` — .NET 反编译工具（unity-mono DLL）

**引用计数**：1 处


**引用详情**：

- `tools/android-reverse/README.md`
  - `| dnSpy | 见子目录 | `tools/crack-intergration-tools/source-projects/dnSpy/` | GitHub | .NET 反编译 + 调试 + 编辑 | GPL-3.0 | 已纳入 |`

#### `tools/crack-intergration-tools/source-projects/frida-cocosjs` — Frida + cocos-creator JS 字节码解密

**引用计数**：1 处


**引用详情**：

- `skills/strategy/cocos-creator-strategy-skill/tools-index.md`
  - `-l tools/crack-intergration-tools/source-projects/frida-cocosjs/hook-cocos.js \`

#### `tools/crack-intergration-tools/source-projects/ghidra` — Ghidra 反汇编器（native 分析）

**引用计数**：10 处


**引用详情**：

- `tools/crack-intergration-tools/docs/ghidra/01_overview.md`
  - `| **源码路径** | `tools/crack-intergration-tools/source-projects/ghidra/` |`
- `tools/crack-intergration-tools/docs/ghidra/06_build_and_run.md`
  - `cd tools/crack-intergration-tools/source-projects/ghidra`
- `tools/crack-intergration-tools/docs/ghidra/07_workflow_integration.md`
  - `cd tools/crack-intergration-tools/source-projects/ghidra`
- `tools/crack-intergration-tools/docs/ghidra/INDEX.md`
  - `> 路径: `tools/crack-intergration-tools/source-projects/ghidra/``
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/Il2CppDumper.csproj.FileListAbsolute.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/net8.0/g`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/net8.0/g`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/Release/net8.0/g`
- `tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/obj/Release/net8.0/PublishOutputs.16c789cfa0.txt`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/ghidra.p`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/ghidra_w`
  - `/home/leo/文档/android-crack/tools/crack-intergration-tools/source-projects/Il2CppDumper/Il2CppDumper/bin/publish/ghidra_w`

#### `tools/crack-intergration-tools/source-projects/il2Fusion` — il2Fusion（Unity IL2CPP 整合工具）

**引用计数**：1 处


**引用详情**：

- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **Il2Fusion** | `tools/crack-intergration-tools/source-projects/il2Fusion/` | Android 侧运行时代理（LSPosed + JNI Hook） | 需要在`

#### `tools/crack-intergration-tools/source-projects/jadx` — jadx（Android dex → java 反编译）

**引用计数**：2 处


**引用详情**：

- `skills/strategy/android-strategy-skill/strategy.md`
  - `| 静态反编译 | **jadx** | `tools/crack-intergration-tools/source-projects/jadx/` |`
- `tools/android-reverse/README.md`
  - `| jadx | 见子目录 | `tools/crack-intergration-tools/source-projects/jadx/` | GitHub | APK / Dex → Java 源码 | Apache-2.0 | 已纳入`

#### `tools/crack-intergration-tools/source-projects/rodroid-il2cppdumper` — rodroid-il2cppdumper（Tauri GUI 版 Il2CppDumper）

**引用计数**：2 处


**引用详情**：

- `skills/strategy/il2cpp-strategy-skill/tools-index.md`
  - `| **rodroid-il2cppdumper** | `tools/crack-intergration-tools/source-projects/rodroid-il2cppdumper/` | 跨平台 GUI（Tauri + Ru`
- `tools/android-reverse/README.md`
  - `| rodroid-il2cppdumper | 见子目录 | `tools/crack-intergration-tools/source-projects/rodroid-il2cppdumper/` | GitHub | il2cpp`

#### `tools/crack-intergration-tools/source-projects/tesseract` — Tesseract OCR

**引用计数**：13 处


**引用详情**：

- `tools/crack-intergration-tools/docs/VERIFICATION_REPORT.md`
  - `- **任务**：为 `tools/crack-intergration-tools/source-projects/tesseract/` 建立索引 + 工作流嵌入分析`
  - `- **源项目路径**：`tools/crack-intergration-tools/source-projects/tesseract/`（READONLY）`
  - `- **索引路径**：`tools/crack-intergration-tools/docs/tesseract/``
- `tools/crack-intergration-tools/docs/tesseract/.inventory/tesseract.md`
  - `> Inventory of `tools/crack-intergration-tools/source-projects/tesseract/``
  - `> root used throughout is `tools/crack-intergration-tools/source-projects/tesseract/``
- `tools/crack-intergration-tools/docs/tesseract/02_directory_tree.md`
  - `Annotated tree of `tools/crack-intergration-tools/source-projects/tesseract/`.`
- `tools/crack-intergration-tools/docs/tesseract/06_build_and_run.md`
  - `PREFIX=$HOME/文档/android-crack/tools/crack-intergration-tools/execable/tesseract`
  - `[`/home/leo/文档/android-crack/tools/crack-intergration-tools/docs/tesseract/`](../README.md).`
- `tools/crack-intergration-tools/docs/tesseract/07_workflow_integration.md`
  - `| **Tesseract** | `tools/crack-intergration-tools/source-projects/tesseract/` | CPU LSTM + Leptonica；纯离线 | Leptonica ≥ 1`
  - `| **没在 `tools/environments/env.sh` 注册** | `TESSERACT_BIN` 等变量未定义 | 在 `env.sh` 加：`export TESSERACT_BIN=$REPO_ROOT/tools/c`
  - `cd tools/crack-intergration-tools/source-projects/tesseract/tessdata`
  - ...（共 4 处，省略）
- `tools/crack-intergration-tools/docs/tesseract/README.md`
  - `> **Source root**: `tools/crack-intergration-tools/source-projects/tesseract/``

#### `tools/crack-intergration-tools/source-projects/txtrtool` — Unity TextAsset 工具（已编译）

**引用计数**：9 处


**引用详情**：

- `tools/crack-intergration-tools/docs/txtrtool/06_build_and_run.md`
  - `python3 tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py`
  - `tools/crack-intergration-tools/execable/txtrtool/txtrtool version`
- `tools/crack-intergration-tools/docs/txtrtool/INDEX.md`
  - `- **源码**: `tools/crack-intergration-tools/source-projects/txtrtool/`（READONLY）`
  - `- **可执行**: `tools/crack-intergration-tools/execable/txtrtool/txtrtool``
  - `- **构建脚本**: `tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py``
  - ...（共 4 处，省略）
- `tools/crack-intergration-tools/execable/txtrtool/build-txtrtool.py`
  - `<out>/txtrtool      ← 可执行（默认 tools/crack-intergration-tools/execable/txtrtool/）`
  - `SRC = REPO / "tools/crack-intergration-tools/source-projects/txtrtool"`
  - `DEFAULT_OUT = REPO / "tools/crack-intergration-tools/execable/txtrtool"`

#### `tools/crack-intergration-tools/source-projects/xapk-to-apk` — XAPK 拆分 → fat APK 合并工具

**引用计数**：1 处


**引用详情**：

- `tools/android-reverse/README.md`
  - `| xapk-to-apk | 见子目录 | `tools/crack-intergration-tools/source-projects/xapk-to-apk/` | 本工作区 | XAPK → fat APK | MIT | 已纳入`


### 2.2 可执行

#### `tools/crack-intergration-tools/execable/AssetRipper` — Unity 资产解包（替代 AssetStudio 的 .NET 实现）

**引用计数**：8 处


**引用详情**：

- `skills/common/scripts/asset-identify.py`
  - `assetripper_path = Path(repo_root()) / "tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free"`
- `skills/common/scripts/assetripper-extract.py`
  - `assetripper_path = Path(repo_root()) / "tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free"`
  - `log_info("并放到 tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free")`
- `tools/crack-intergration-tools/docs/AssetRipper/README.md`
  - `tools/crack-intergration-tools/execable/AssetRipper/`
  - `./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free`
  - `./tools/crack-intergration-tools/execable/AssetRipper/AssetRipper.GUI.Free --port 8080`
  - ...（共 5 处，省略）

#### `tools/crack-intergration-tools/execable/FakerAndroid-updated.jar` — FakerAndroid 升级版（捆绑 apktool 2.11.1 + dex2jar 2.4）

**引用计数**：1 处


**引用详情**：

- `crackings/il2cpp/CrowdCity/raw/tool-calls-history.md`
  - `java -jar tools/crack-intergration-tools/execable/FakerAndroid-updated.jar fake -o /home/leo/文档/android-crack/output-pro`

#### `tools/crack-intergration-tools/execable/Il2CppInspectorRedux` — Il2CppInspectorRedux（Il2CppDumper 备选）

**引用计数**：1 处


**引用详情**：

- `skills/strategy/il2cpp-strategy-skill/references/il2cpp-metadata-version-limit.md`
  - `INSPECTOR=tools/crack-intergration-tools/execable/Il2CppInspectorRedux/Il2CppInspector`

#### `tools/crack-intergration-tools/execable/apktool.jar` — apktool 2.11.1 + R8 定制 guava 捆绑版

**引用计数**：7 处


**引用详情**：

- `OBJECTIVES.md`
  - `| **apktool** | 2.11.1 | `tools/crack-intergration-tools/execable/apktool.jar` | `apktool --version` → 2.11.1 |`
- `skills/common/scripts/setup-local-tools.py`
  - `print(f"    \033[0;34mtools/crack-intergration-tools/execable/apktool.jar\033[0m")`
- `skills/strategy/android-strategy-skill/strategy.md`
  - `| 解包 / 打包 | **apktool** | `tools/crack-intergration-tools/execable/apktool.jar` |`
- `skills/strategy/android-strategy-skill/tools-index.md`
  - `java -jar tools/crack-intergration-tools/execable/apktool.jar d \`
  - `java -jar tools/crack-intergration-tools/execable/apktool.jar b \`
- `skills/strategy/defold-strategy-skill/tools-index.md`
  - `| apktool 2.11.1 | 解包/重打包 | `$APKTOOL` / `tools/crack-intergration-tools/execable/apktool.jar` |`
- `skills/third-party-removal-strategy-skill/workflow.md`
  - `java -jar tools/crack-intergration-tools/execable/apktool.jar b \`

#### `tools/crack-intergration-tools/execable/ffmpeg` — ffmpeg（音视频处理）

**引用计数**：9 处


**引用详情**：

- `tools/crack-intergration-tools/docs/ffmpeg/README.md`
  - `tools/crack-intergration-tools/execable/ffmpeg/`
  - `./tools/crack-intergration-tools/execable/ffmpeg/ffprobe input.mp4`
  - `./tools/crack-intergration-tools/execable/ffmpeg/ffmpeg -i input.mp4 output.avi`
  - ...（共 9 处，省略）

#### `tools/crack-intergration-tools/execable/gnirehtet` — gnirehtet（USB 反向 tethering 网络）

**引用计数**：7 处


**引用详情**：

- `skills/common/scripts/network-analyze/setup-reverse-tether.py`
  - `GNIREHTET = os.path.join(REPO_DIR, 'tools/crack-intergration-tools/execable/gnirehtet/gnirehtet')`
  - `GNIREHTET_APK = os.path.join(REPO_DIR, 'tools/crack-intergration-tools/execable/gnirehtet/gnirehtet.apk')`
- `tools/android-reverse/README.md`
  - `| gnirehtet | v2.5.1 | `tools/crack-intergration-tools/execable/gnirehtet/` | [GitHub](https://github.com/Genymobile/gni`
- `tools/crack-intergration-tools/docs/TOOLS_NETWORK.md`
  - `| **路径** | `tools/crack-intergration-tools/execable/gnirehtet/` |`
  - `adb install -r tools/crack-intergration-tools/execable/gnirehtet/gnirehtet.apk`
  - `tools/crack-intergration-tools/execable/gnirehtet/gnirehtet run`
  - ...（共 4 处，省略）

#### `tools/crack-intergration-tools/execable/ilspycmd` — ILSpy 命令行工具

**引用计数**：6 处


**引用详情**：

- `tools/crack-intergration-tools/docs/ILSpy/06_build_and_run.md`
  - `> `tools/crack-intergration-tools/execable/ilspycmd/`（net10.0, linux-x64, 自包含 false，依赖 dotnet 10 runtime）。`
  - `./tools/crack-intergration-tools/execable/ilspycmd/ilspycmd --version          # 11.0.0.9252`
  - `./tools/crack-intergration-tools/execable/ilspycmd/ilspycmd -l c <file>.dll     # 列出类`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/source-projects/ILSpy/CHECKSUM.md`
  - `-o <repo>/tools/crack-intergration-tools/execable/ilspycmd`

#### `tools/crack-intergration-tools/execable/reverse` — reverse-tool 二进制

**引用计数**：1 处


**引用详情**：

- `skills/strategy/cocos-creator-strategy-skill/references/cocos-jsc-decrypt-repack.md`
  - `tools/crack-intergration-tools/execable/reverse \`

#### `tools/crack-intergration-tools/execable/undertale-mod-tool` — UndertaleModTool（GameMaker 数据解/打包）

**引用计数**：13 处


**引用详情**：

- `EXPERIENCES.md`
  - `- 可执行 `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll``
- `skills/strategy/gamemaker-strategy-skill/scripts/README.md`
  - `- **按钮移除依赖工具**: `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll`（dotnet）`
- `skills/strategy/gamemaker-strategy-skill/scripts/workflow/inspect-gamemaker-rooms.py`
  - `- tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll`
  - `CLI_DLL = REPO / "tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll"`
- `skills/strategy/gamemaker-strategy-skill/scripts/workflow/remove-gamemaker-buttons.py`
  - `- tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll`
  - `CLI_DLL = REPO / "tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll"`
- `temp/merged-experiences/gamemaker-strategy-skill-experience.md`
  - `- 可执行 `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll``
- `tools/crack-intergration-tools/docs/undertale-mod-tool/06_build_and_run.md`
  - `rm -rf tools/crack-intergration-tools/execable/undertale-mod-tool`
  - `mkdir -p tools/crack-intergration-tools/execable/undertale-mod-tool`
  - `cp -r UndertaleModCli/bin/Release/net10.0/* tools/crack-intergration-tools/execable/undertale-mod-tool/`
  - ...（共 5 处，省略）
- `tools/crack-intergration-tools/docs/undertale-mod-tool/INDEX.md`
  - `- **可执行**: `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll``


### 2.3 文档

#### `tools/crack-intergration-tools/docs/TOOLS.md` — 工具注册表（AGENTS.md §6 维护）

**引用计数**：4 处


**引用详情**：

- `AGENTS.md`
  - `| 10 | Agent 在 `bash` 里手敲 `pip install ...` / `npm install ...` 临时安装 | 写入工具脚本并登记到 `tools/crack-intergration-tools/docs/T`
  - `| `tools/crack-intergration-tools/docs/TOOLS.md` | **工具注册表**：每工具一子目录（INDEX.md + 架构/API/工作流嵌入） | **MUST-LOAD**（新增工具只在此追加）`
  - `> **维护规则**：新增工具时，在 `tools/crack-intergration-tools/docs/TOOLS.md` 工具表中追加一行，并在 `docs/<tool>/` 下创建文档子目录。`
  - ...（共 4 处，省略）

#### `tools/crack-intergration-tools/docs/ha4t` — ha4t 工具集成文档

**引用计数**：1 处


**引用详情**：

- `skills/common/scripts/SCRIPTS-INDEX.md`
  - `> 文档详见 `tools/crack-intergration-tools/docs/ha4t/07_workflow_integration.md`。`

#### `tools/crack-intergration-tools/docs/swipium` — swipium 工具集成文档

**引用计数**：1 处


**引用详情**：

- `skills/common/scripts/SCRIPTS-INDEX.md`
  - `> 文档详见 `tools/crack-intergration-tools/docs/swipium/07_workflow_integration.md`。`


---

## 3. 未被引用的项目（孤立工具）


> 这些项目在仓库中存在但**未被任何脚本引用**。可能是预留 / 开发中 / 已弃用。
> 删除前请确认（AGENTS.md §1.13）：
> 1. 检查 `temp/` 备份里是否有迁移记录
> 2. `grep -r '<project>' --exclude-dir=.git` 确认 0 匹配（已扫描）
> 3. 手动跑一次工具确认是否真无用

| 项目 | 类型 | 描述 |
|------|------|------|
| `docs/ARMT64_HOOK_COMPARISON.md` | 文档 | （暂无描述） |
| `source-projects/FixStackmaps` | 源码 | dex2jar ASM FixStackmaps 工具（jar 编译期兼容） |
| `execable/FixStackmaps.jar` | 可执行 | ASM FixStackmaps 工具（jar 编译期兼容） |
| `docs/ILSPY_DNSPY_COMPARISON.md` | 文档 | （暂无描述） |
| `source-projects/Il2CppDecompiler` | 源码 | IL2CPP 反编译器 |
| `source-projects/JSC-PyDecrypt-Tool` | 源码 | JSC 字节码解密（cocos-creator JS） |
| `source-projects/LLM-image-translator` | 源码 | LLM 图片翻译工具 |
| `source-projects/PaddleOCR` | 源码 | PaddleOCR（OCR 文字识别） |
| `docs/TOOLS_DEPS.md` | 文档 | 本文件——工具项目反向引用清单（自动生成） |
| `docs/TOOLS_NETWORK.md` | 文档 | （暂无描述） |
| `source-projects/UABEANext` | 源码 | UABEANext（UABEA 继任） |
| `docs/VERIFICATION_REPORT.md` | 文档 | （暂无描述） |
| `source-projects/cocos2d-dec` | 源码 | cocos2d-x Lua 脚本解密 |
| `source-projects/reverse-tool` | 源码 | reverse-tool 二进制 |
| `execable/tcp-proxy` | 可执行 | TCP 代理（抓包） |
| `docs/underanalyzer` | 文档 | （暂无描述） |

---

## 4. 维护说明


**新增引用流程**：
1. 脚本/文档引用 `tools/crack-intergration-tools/<category>/<project>`
2. 重新跑 `gen-tools-deps-doc.py` —— 自动识别新引用并入清单
3. 若 DESCRIPTIONS 表里没有该项目的描述，手动添加（避免留空）

**删除/弃用流程**：
1. 在脚本中替换引用（指向替代工具）
2. 工具项目移到 `tools/crack-intergration-tools/source-projects/.deprecated/` 或删除
3. 重跑 `gen-tools-deps-doc.py` —— 孤立项目会自动移到 §3

**重新生成**：
```bash
python3 tools/maintenance/scripts/gen-tools-deps-doc.py
# 输出：tools/crack-intergration-tools/docs/TOOLS_DEPS.md
```

**关联文档**：
- `tools/crack-intergration-tools/docs/TOOLS.md` — 工具基础信息（API / 工作流嵌入 / 版本）
- `AGENTS.md §6` — 工具注册表
- `skills/common/scripts/SCRIPTS-INDEX.md` — 脚本索引
