# 06 编译与运行（Build & Run）

## 1. 编译

### 1.1 CLI

```bash
dotnet build AssetStudio/AssetStudio.sln -c Release
```

或单独构建：

```bash
dotnet build AssetStudio.CLI/AssetStudio.CLI.csproj -c Release
```

### 1.2 GUI

GUI 端依赖 WinForms + OpenTK + FMOD 等原生库，仅在 Windows 上能编译：

```bash
dotnet build AssetStudio.GUI/AssetStudio.GUI.csproj -c Release -p:Platform=x64
```

> 注意：`AssetStudio.FBXNative` 需要 MSBuild + vcxproj 工具链；若在 Linux 上 build，需要 mono 或 Wine。

### 1.3 单模块

| 模块 | 命令 |
|---|---|
| AssetStudio 核心库 | `dotnet build AssetStudio/AssetStudio.csproj -c Release` |
| AssetStudio.Utility | `dotnet build AssetStudio.Utility/AssetStudio.Utility.csproj -c Release` |
| AssetStudio.FBXWrapper | `dotnet build AssetStudio.FBXWrapper/AssetStudio.FBXWrapper.csproj -c Release` |
| AssetStudio.PInvoke | `dotnet build AssetStudio.PInvoke/AssetStudio.PInvoke.csproj -c Release` |
| AssetStudio.FBXNative | `msbuild AssetStudio.FBXNative/AssetStudio.FBXNative.vcxproj /p:Configuration=Release /p:Platform=x64` |

## 2. 运行

### 2.1 GUI

```bash
./AssetStudio.GUI/bin/Release/net8.0-windows/AssetStudio.GUI.exe
```

或双击运行。GUI 是 WinForms 程序，**仅在 Windows 上可运行**。

### 2.2 CLI

```bash
./AssetStudio.CLI/bin/Release/net8.0-windows/AssetStudio.CLI.exe <input> <output> [options...]
```

> 由于使用了 `System.CommandLine`，无参调用会输出 help。

## 3. CLI 参数详解

`AssetStudio.CLI/Components/CommandLine.cs` 中定义（参见 `OptionsBinder.cs:95..208`）。

### 3.1 位置参数

| 参数 | 说明 |
|---|---|
| `<input_path>` | 输入文件或文件夹（FileInfo） |
| `<output_path>` | 输出目录（DirectoryInfo） |

### 3.2 选项

| 选项 | 说明 | 默认值 |
|---|---|---|
| `--game <Name>` **(REQUIRED)** | 游戏类型，取值见 `GameManager.GetGameNames()`（38 项） | — |
| `--types <ClassID:Parse\|Export\|Both>` | 按类型过滤，可多次出现 | — |
| `--names <regex>` | 资产名正则过滤；也支持 `file.txt`（每行一个） | — |
| `--containers <regex>` | 容器路径正则过滤；同上 | — |
| `--image_format Png\|Jpeg\|Bmp\|Webp` | 纹理/Sprite 输出格式 | `Png` |
| `--map_op None\|Load\|CABMap\|AssetMap\|Both` | 资源图谱构建/加载模式 | `None` |
| `--map_type XML\|JSON` | AssetMap 输出格式 | `XML` |
| `--map_name <name>` | AssetMap 文件名 | `assets_map` |
| `--group_assets ByType\|ByContainer\|BySource` | 导出分组方式 | `ByType` |
| `--export_type Raw\|Dump\|Convert\|JSON` | 资产导出方式 | `Convert` |
| `--unity_version <X.Y.ZfN>` | 强制 Unity 版本（覆盖自动检测） | — |
| `--key 0xNN` | XOR key 解密 MiHoYoBinData | — |
| `--key_index <N>` | UnityCN keys 索引 | 0 |
| `--ai_file <path>` | `asset_index.json` 文件路径（GI 系列） | — |
| `--dummy_dlls <folder>` | MonoBehaviour 反序列化的 dummy DLL 目录 | — |
| `--silent` | 静默（隐藏 log） | false |
| `--logger_flags Verbose\|Debug\|Info\|Warning\|Error` | 日志级别，可多次出现 | Debug/Info/Warning/Error |

### 3.3 游戏类型（`--game`）

`AssetStudio/GameManager.cs:14..52` 注册了 38 种游戏：

| 索引 | Name | 类型 |
|---|---|---|
| 0 | Normal | Game |
| 1 | UnityCN | Game |
| 2 | GI | Mhy（米哈游） |
| 3 | GI_Pack | Mr0k |
| 4 | GI_CB1 | Mr0k |
| 5 | GI_CB2 | Blk |
| 6 | GI_CB3 | Blk |
| 7 | GI_CB3Pre | Mhy |
| 8 | BH3 | Mr0k（崩坏 3） |
| 9 | BH3Pre | Mr0k |
| 10 | BH3PrePre | Mr0k |
| 11 | SR_CB2 | Mr0k（星穹铁道） |
| 12 | SR | Mr0k |
| 13 | ZZZ_CB1 | Mr0k（绝区零） |
| 14 | TOT | Mr0k |
| 15 | Naraka | Game（永劫无间） |
| 16 | EnsembleStars | Game |
| 17 | OPFP | Game |
| 18 | FakeHeader | Game |
| 19 | FantasyOfWind | Game |
| 20 | ShiningNikki | Game |
| 21 | HelixWaltz2 | Game |
| 22 | NetEase | Game |
| 23 | AnchorPanic | Game |
| 24 | DreamscapeAlbireo | Game |
| 25 | ImaginaryFest | Game |
| 26 | AliceGearAegis | Game |
| 27 | ProjectSekai | Game |
| 28 | CodenameJump | Game |
| 29 | GirlsFrontline | Game |
| 30 | Reverse1999 | Game |
| 31 | ArknightsEndfield | Game |
| 32 | JJKPhantomParade | Game |
| 33 | MuvLuvDimensions | Game |
| 34 | PartyAnimals | Game |
| 35 | LoveAndDeepspace | Game |
| 36 | SchoolGirlStrikers | Game |
| 37 | ExAstris | Game |
| 38 | PerpetualNovelty | Game |

## 4. 常用示例

### 4.1 导出 GI 的所有 Texture2D 和 Shader

```bash
AssetStudio.CLI.exe "D:/Games/GI/Data" "D:/Export" --game GI --types Texture2D:Both,Shader:Both --export_type Convert
```

### 4.2 导出 BH3 的所有 GameObject 为 FBX

```bash
AssetStudio.CLI.exe "D:/Games/BH3" "D:/Models" --game BH3 --types GameObject:Export --export_type Convert
```

### 4.3 仅做 Bundle 解包（不解密 .data）

```bash
# 在 CLI 没有自动 extract 模式，但可以通过自定义脚本调用 Studio.ExtractFolder
# 或者直接用 7zip / quickbms 处理
```

### 4.4 构建 CABMap + AssetMap

```bash
AssetStudio.CLI.exe "D:/Games/SR" "D:/Maps" --game SR --map_op Both --map_name sr_map --map_type JSON
```

### 4.5 加载已有 AssetMap 重新导出

```bash
AssetStudio.CLI.exe "D:/Maps/sr_map.json" "D:/Export" --game SR --map_op Load --map_name sr_map --types Texture2D:Both
```

### 4.6 GI + asset_index

```bash
AssetStudio.CLI.exe "D:/Games/GI" "D:/Export" --game GI --ai_file "D:/asset_index.json" --types Texture2D:Export --image_format Webp
```

### 4.7 强制 Unity 版本

```bash
AssetStudio.CLI.exe "D:/Games" "D:/Export" --game Normal --unity_version 2022.3.10f1 --types Texture2D:Both
```

### 4.8 MIHOYO BinData + XOR key

```bash
AssetStudio.CLI.exe "D:/Games" "D:/Export" --game GI --key 0xAB --types MiHoYoBinData:Both --export_type JSON
```

## 5. 日志与进度

- 通过 `Logger.Verbose / Debug / Info / Warning / Error` 输出
- `--logger_flags` 控制启用的日志级别
- `Progress.Report(current, total)` 用于 GUI 进度条；CLI 也会输出到控制台

## 6. 已知限制

- GUI 依赖 Windows（WinForms）
- 部分解码格式（DXT3）未实现，标记为 `// TODO`
- 部分 SubShader / Pass 选项不导出（如 `m_InstancingOptions`）
- ARM64 / WebAssembly 等部分 il2cpp 平台的 GameType 未注册（AssetStudio 不解析 il2cpp，这部分功能请用 Il2CppDumper）