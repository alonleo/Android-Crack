# GameMaker Studio 工具索引

> GameMaker Studio 引擎 APK 逆向使用的工具与脚本索引。

## 1. 系统工具（来自 `tools/environments/env.sh`）

| 工具 | 变量 | 用途 |
|------|------|------|
| apktool | `$APKTOOL` | 解包/重打包 APK |
| jadx | `$JADX` | Java 反编译 |
| aapt2 | `$AAPT2` | APK 资源查看 |
| apksigner | `$APKSIGNER` | APK 签名（v1+v2+v3） |
| zipalign | `$ZIPALIGN` | APK 对齐 |
| keytool | `$KEYTOOL` | keystore 生成 |

## 2. 命令行工具

| 工具 | 用途 |
|------|------|
| `unzip` / `zip` | APK 内文件提取/重打包 |
| `strings` | .so 内字符串提取（**YYObjectBase** / **RValue** / **Java_com_yoyogames_runner_RunnerJNILib**） |
| `readelf` | .so 符号表（导出 JNI 入口定位） |
| `hexdump` | .droid magic 校验（FORM..GEN8） |
| `adb` / `logcat` | 真机验证（yoyo/runner/GameMaker tag） |

## 3. GameMaker 专用工具

| 工具 | 来源 | 用途 |
|------|------|------|
| **UndertaleModTool (UndertaleModCli)** | UnderminersTeam 官方 | **.droid 编辑（房间实例移除/按钮隐藏）** — 源码 `source-projects/UndertaleModTool/`，可执行 `execable/undertale-mod-tool/UndertaleModCli.dll`，`load -s <script.csx> -o out -f` |
| **GameMaker Studio 2 IDE** | YoYo Games 官方 | 仅供开发参考（运行我们的 patch 需要本地有 GMS2 + 项目源） |
| **Android Studio + NDK** | Google | AS 工程化 + native hook 编译 |

## 4. 已沉淀脚本（workflow/）

| 脚本路径 | 角色 |
|---------|------|
| `scripts/workflow/inspect-gamemaker-rooms.py` | 探索：列出房间/图层/实例/对象/代码引用（`--rooms` / `--objects` / `--code <name>`） |
| `scripts/workflow/remove-gamemaker-buttons.py` | 移除按钮/对象实例：三处实例列表全清（layer + GameObjects + 创建顺序）+ `--replace` 代码重编译动态创建 |

## 5. JNI 桩化脚本（待实现）

| 脚本路径 | 状态 | 角色 |
|---------|------|------|
| `scripts/common/build-gamemaker-hook-native-lib.py` | **TODO** | 编译 libnative-lib.so（hook RunnerJNILib 关键 JNI） |
| `scripts/common/inject-gamemaker-hook.py` | **TODO** | 注入 native-lib 到 RunnerActivity.onCreate |

## 6. SDK 移除脚本（共用）

| 脚本路径 | 角色 |
|---------|------|
| `skills/common/third-party-removal-strategy-skill/scripts/workflow/sub-stage-defold-manifest-clean.py` | manifest 清理（GameMaker 可复用） |

## 7. .droid 编辑关键操作（UndertaleModCli）

| 操作 | 命令 |
|------|------|
| 看基本信息 | `dotnet UndertaleModCli.dll info <game.droid>` |
| 运行 C# 脚本 | `dotnet UndertaleModCli.dll load <droid> -s <script.csx> -o <out> -f` |
| 重编译代码 | `dotnet UndertaleModCli.dll replace <droid> -c 'gml_...=./new.gml' -o <out>` |
| 转储代码 | `dotnet UndertaleModCli.dll dump <droid> -c gml_... -o <dir>` |

> **坑位**: 引擎 VM 从 `room.GameObjects` 扁平列表创建实例，移除实例必须三处全清
> （`layer.InstancesData.Instances` + `room.GameObjects` + `room.InstanceCreationOrderIDs`）。