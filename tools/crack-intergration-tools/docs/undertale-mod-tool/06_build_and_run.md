# UndertaleModTool — 构建与运行

## 环境要求

- dotnet（≥ 8，本环境 10.0.301）
- git（克隆子模块）

## 构建

### 从源码构建（UnderminersTeam 官方仓库）

```bash
source tools/environments/env.sh
# 克隆（含子模块 Underanalyzer）
git clone --recursive https://github.com/UnderminersTeam/UndertaleModTool.git \
  tools/crack-intergration-tools/source-projects/UndertaleModTool

# 如克隆时未拉子模块
cd tools/crack-intergration-tools/source-projects/UndertaleModTool
git submodule update --init --recursive

# 构建 CLI
dotnet build UndertaleModCli/UndertaleModCli.csproj -c Release

# 拷贝到 execable
rm -rf tools/crack-intergration-tools/execable/undertale-mod-tool
mkdir -p tools/crack-intergration-tools/execable/undertale-mod-tool
cp -r UndertaleModCli/bin/Release/net10.0/* tools/crack-intergration-tools/execable/undertale-mod-tool/
```

## 验证

```bash
dotnet tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll --version
# 输出: 0.9.1.2+...
dotnet ...UndertaleModCli.dll info <game.droid>
# 输出: GMS2 版本/房间数/对象数/字符串数
```

## 常用命令

```bash
CLI=tools/crack-intergration-tools/execable/undertale-mod-tool/UndertaleModCli.dll

dotnet $CLI info <datafile>                                    # 基本信息
dotnet $CLI load <datafile> -s <script.csx> -o <out> -f       # 加载+运行C#脚本+保存
dotnet $CLI dump <datafile> -s gml_Object_oPlay_Create_0       # 转储代码
dotnet $CLI project <datafile> -s <scripts.csx> -o <outdir>    # 反编译工程
```

## 移除按钮（.droid 编辑）示例

```bash
# remove.csx
# var targets = new HashSet<string> { "oMore", "oPrivacyPolicy", "oShare" };
# foreach (var room in Data.Rooms)
#   foreach (var layer in room.Layers)
#     if (layer.InstancesData != null)
#       for (int i = layer.InstancesData.Instances.Count - 1; i >= 0; i--)
#         if (targets.Contains(layer.InstancesData.Instances[i].ObjectDefinition?.Name?.Content))
#           layer.InstancesData.Instances.RemoveAt(i);

dotnet $CLI load game.droid -s remove.csx -o game-modified.droid -f
```

> 封装脚本: `skills/strategy/gamemaker-strategy-skill/scripts/workflow/remove-gamemaker-buttons.py`

## 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 构建报 IGameContext 缺失 | Underanalyzer 子模块未初始化 | `git submodule update --init --recursive` |
| C# 脚本 `??` 报错 | `room.Name?.Content` 返回 UndertaleString | 用 `room.Name != null ? room.Name.Content : "?"` |
| `-o` 输出已存在 | 默认不覆盖 | 加 `-f`（overwrite） |
| CODE chunk 反编译受限 | 部分 GMS2 项目加密 | 换 dump 特定 entry / 用 GUI |