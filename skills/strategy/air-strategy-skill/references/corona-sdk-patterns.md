# Corona SDK (Solar2D) 逆向模式

> 来源: RimeEscapeRoomGame | 2026-07-28
> Corona SDK 是已停产的移动游戏引擎 (现为 Solar2D 开源继承)。
> 游戏逻辑使用 Lua，编译为 `.lu` 字节码打包在 `resource.car` 中。

## 识别特征

- `lib/arm64-v8a/libcorona.so` — 引擎核心 (4MB+)
- `lib/arm64-v8a/liblua.so` — Lua 运行时
- `lib/arm64-v8a/libjnlua5.1.so` — Java ↔ Lua JNI 桥接
- `assets/resource.car` — 资源归档 (含 Lua 字节码 + 图片 + 音频)
- `res/raw/corona_*` — 内置 widget 主题资源
- 主 Activity: `com.ansca.corona.CoronaActivity`
- 标准插件命名: `plugin.<name>.LuaLoader`

## APK 结构陷阱

### XAPK 扩展数据缺失
Corona 游戏的 XAPK 经常有 `preloadedAssets.apk` (60-200MB) 包含所有游戏资源。
xapk-to-apk 可能漏合并此文件，导致游戏启动后立即崩溃:
```
ERROR: Runtime error
bad argument #1 to 'open' (string expected, got nil)
stack traceback:
    [C]: in function 'open'
    ?: in function 'jsonToTable'
    ?: in function 'new'
    ?: in main chunk
```
**解决**: 使用 `sub-stage-xapk-merge.py` 确保所有 split APK 被合并。

### apktool 兼容性
- `resource.car` 必须保持原始 CRC 和压缩方式 (Deflate:70%)
- `resources.arsc` 重编译后可能导致 resource ID 变更 → Corona 无法加载资源
- 处理资源时避免不必要的重编译: 优先用 `apktool d -s -r` (不解码源码和资源)

## Native 插件系统

Corona 插件可以是纯 Java (.smali) 或纯 Native (.so)，或混合:

| 类型 | 文件 | 移除策略 |
|------|------|---------|
| 纯 Java | `smali*/plugin/<name>/LuaLoader.smali` | 策略 C (物理删除) |
| 纯 Native | `lib/arm64-v8a/lib<name>.so` | 策略 C (物理删除) |
| 混合 | 两者都有 | 策略 A (stub Java) + 策略 C (删除 .so) |

### Corona 原生插件导出符号
```bash
readelf -Ws lib<name>.so | grep "FUNC.*GLOBAL"
# 关键导出:
#   CoronaPluginLuaLoad_<name>  — 插件加载入口
#   luaopen_<name>              — Lua open 函数
```

## 许可校验 (License)

Corona 游戏通常有 2 层许可校验:

### 1. pairip LicenseCheck (第三方加固)
- 通过 `ContentProvider.onCreate()` 自动启动
- 连接 Google Play ILicensingService
- 失败时: 弹错误对话框 → System.exit(0)
- **移除**: 物理删除 `smali/com/pairip/` + 移除 manifest 中 provider/activity

### 2. Corona Google Licensing (引擎内置)
- `CoronaProvider.licensing.google.LuaLoader`
- 使用 Google LVL LicenseChecker
- 通过 Lua 事件回调报告结果
- **移除**: 策略 A — 修改 `MyLicenseCheckerCallback` 的 `dontAllow()` 和 `applicationError()` 重定向到 `allow()`
  - 注意: 修改后需确保 `setLastCheckedAppVersion()` 行为正常

## 常见 SDK/插件列表

| SDK | Java 包 | .so | 可移除 |
|-----|---------|-----|--------|
| AdMob | `plugin.admob.LuaLoader` | — | ✅ |
| Ads | — | `libads.so` | ✅ |
| Analytics | — | `libanalytics.so` | ✅ |
| Game Network | — | `libgameNetwork.so` | ✅ |
| Licensing | — | `liblicensing.so` | ✅ |
| Corona Engine | `com.ansca.corona.*` | `libcorona.so` | ❌ 核心 |
