# UndertaleModTool — 工具文档索引

> GameMaker .droid 数据文件编辑工具（GMS2 房间/实例/对象/代码）

## 基本信息

- **来源**: https://github.com/UnderminersTeam/UndertaleModTool（官方组织仓库，克隆于 2026-08-09）
- **源码**: `tools/crack-intergration-tools/source-projects/UndertaleModTool/`（READONLY）
- **可执行**: `tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll`
- **构建**: `dotnet build UndertaleModCli/UndertaleModCli.csproj -c Release`
- **版本**: 0.9.1.2
- **语言**: C# (.NET 10)
- **子模块**: `Underanalyzer`（Underanalyzer/，`git submodule update --init --recursive`）
- **用途**: 加载/编辑 GameMaker 数据文件（.droid/.win/.unx），支持房间实例编辑、代码反编译、纹理替换

## ⚠️ 重要说明

> **这是 GameMaker 逆向的关键工具**，可解决 GMS2 二进制格式复杂导致的 ROOM/OBJT chunk 无法手工解析的问题。
> 本工作区 FindTheDifferences 项目用它成功移除了 更多游戏/隐私政策/分享 按钮实例。

## CLI 用法

```
dotnet UndertaleModCli.dll info <datafile>                     # 基本信息
dotnet UndertaleModCli.dll load <datafile> -s <script.csx> -o <out> -f   # 加载+脚本+保存
dotnet UndertaleModCli.dll dump <datafile> -s <names>          # 转储
dotnet UndertaleModCli.dll project <datafile> -s <scripts.csx> -o <out>  # 反编译工程
```

### C# 脚本（.csx）关键 API

| API | 用途 |
|-----|------|
| `Data.Rooms` | 房间列表（`room.Name.Content`, `room.Width/Height`） |
| `room.Layers` | 图层列表（`layer.LayerName`, `layer.LayerType`） |
| `layer.InstancesData.Instances` | 图层实例列表（可 `RemoveAt`） |
| `inst.X / inst.Y / inst.InstanceID` | 实例坐标/ID |
| `inst.ObjectDefinition.Name.Content` | 实例对象名 |
| `Data.GameObjects` | 对象列表 |

## 使用场景（本工作区）

- **移除按钮/实例**：加载 .droid → 遍历房间图层实例 → 按对象名 `RemoveAt` → 保存
  - 见 `skills/strategy/gamemaker-strategy-skill/scripts/workflow/remove-gamemaker-buttons.py`
- **查看房间结构**：dump 所有房间/图层/实例（`dump-rooms.csx`）
- **反编译代码**：`project` 命令可反编译 GML（CODE chunk 加密时部分支持）

## 坑位

1. **构建需子模块**: `git submodule update --init --recursive`（Underanalyzer）
2. **C# 脚本**: `room.Name?.Content` 中 `?.` 会因 UndertaleString 类型导致 `??` 报错 → 用 `room.Name != null ? room.Name.Content : "?"`
3. **保存参数**: 需 `-f`（overwrite）否则输出已存在时报错
4. **CODE 加密**: 部分 GMS2 项目的 CODE chunk 加密，反编译受限（本游戏 OK）