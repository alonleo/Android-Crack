# libGDX 引擎策略详述

> 识别特征 / 工具链 / 坑位 / 静态+动态分析重点。来源: JungleMarbleBlast (com.cooyostudio.marble.blast) | 2026-08-06

## 1. 识别特征

| 特征 | 值 |
|------|-----|
| 引擎库 | `lib/<abi>/libgdx.so`（armeabi-v7a/arm64-v8a/x86/x86_64 四 ABI 常同时打入） |
| Java 框架 | `com.badlogic.gdx.{activity,backends.android,graphics,utils,math,...}` |
| 入口 | 自定义 `*GameActivity extends AndroidApplication`（或 `AndroidFragmentApplication`）；典型如 CooYoGameActivity（CooyoStudio fork）/ VantageGameActivity 等 |
| 资源格式（明文） | `.atlas`（纹理集）+ `.png`、`.pack`（libGDX 容器）/ `.tmx`（Tiled 地图）/ `.fnt`（位图字体）/ `.ttf`（TrueType 字体）/ `.ogg` + `.mp3`（音频） |
| 字体 | `com/badlogic/gdx/utils/lsans-15.{fnt,png}`（内置默认字体）；用户字体走 `assets/<name>.ttf` |
| ABI | 标准 EGL/GLES2/GLES3 调用，无 NDK 强 ABI 依赖 |
| targetSdk/minSdk | 多版本共存；Java 层保持 7+ 兼容（游戏常升 target 33–35） |

## 2. 工具链

| 用途 | 工具 |
|------|------|
| 解包/重打包 | apktool 2.11.1 |
| Java 静态分析 | jadx（class 入口 + 业务类引用） |
| .so 引擎分析 | `strings` / `readelf`（libgdx.so 内常有版本字符串 + EGL/GLES 调用） |
| 资源解析（atlas/打包） | libGDX TexturePacker 工具链（或自写 Python 读取 .atlas 文本） |
| 资源解包（.pack） | libgdx-pack（GitHub 现成）或自写 |
| 汉化（ttf 路径） | 解压 assets/，替换同路径 .ttf 文件 |
| 动态验证 | adb + logcat（libGDX 自有日志 tag 多为 `GLSurfaceView`/`GLThread`） + Frida（如需 hook Java 层） |

## 3. 坑位

### 3.1 业务代码高度混淆：A/B/A0/p000a
- libGDX 项目中发行方常对业务代码（与游戏逻辑相关的 helper / model / util 类）做包名混淆，呈现为 `A, B, A0, A1, ..., p000a, p001a0, ...`。
- 这是 **Jadx 的默认行为**（dex 中 package/class name 被短名化）。**不要尝试通过反混淆找回业务名**，因为名称已被 mangle，写文件时就丢了可读性。
- 替代：**按行为定位**——入口 `MBApplication` / `GameActivity` 引用是可见的；通过它反查的方法/字段是稳定锚点。

### 3.2 发行方二次加密：assets 下 hash 文件（⚠️ 核心资源）

实现要点见 [去第三方 SDK：libgdx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#libgdx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 3.3 PGL（Bytedance）DEX 部分加密

实现要点见 [去第三方 SDK：libgdx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#libgdx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 3.7 CooYo fork 的 Facebook/Firebase 硬依赖（启动桩化链）

实现要点见 [去第三方 SDK：libgdx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#libgdx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

### 3.4 多 dex + MultiDex
- `classes.dex` + `classes2.dex` + ... + `classesN.dex` + `assets/audience_network/classes*.dex`（额外 dex）。
- `MBApplication.attachBaseContext` 调用 `MultiDex.install(this)`（标准 androidx.multidex）→ 主 dex 是入口 dex，附 dex 按需加载。
- 重打包后**不要拆分 dex**——apktool 默认会按 smali 重新打包，按 dex 文件夹结构识别。

### 3.5 汉化 path：libGDX Typeface 加载 vs Bitmap Font
- libGDX 文字渲染两条路径：
  - **FreeType + Typeface (`Typeface.createFromAsset`)**：Java 层加载 `assets/<font>.ttf`，传入 libGDX BitmapFontCache 渲染 → 替换 ttf 即可。
  - **预渲染 Bitmap Font（`.fnt` + `.png` 贴图）**：引擎内置默认字体（`lsans-15.fnt`），不能在 ttf 级别动 → 需要替换贴图。
- 绝大多数发行方 libGDX 游戏（如 JungleMarbleBlast）走 ttf 路径 → 重置同名 ttf 即可。
- 验证：jadx 搜索 `Typeface.createFromAsset` → 找到传入的字体文件名 → 替换 `assets/<name>.ttf`。

### 3.6 第三方 SDK 海量（多广告聚合）

实现要点见 [去第三方 SDK：libgdx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#libgdx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

## 4. 静态分析重点

1. **类型嗅探**：`unzip -l` 命中 `libgdx.so` + `com/badlogic/gdx/` → libgdx。
2. **入口确认**：`AndroidManifest.xml` → `application android:name` + 主 `activity android:name` → jadx 看 `extends AndroidApplication` / `extends *GameActivity`。
3. **资源确认**：`unzip -l assets/` 列出子目录（`sound/`, `template/`, `adimages/`, `audience_network/`, `dexopt/`），可明文 vs 加密。
4. **海量子 SDK + 混淆**：
   - 以 `applovin`, `mbridge`, `bytedance`, `facebook`, `vungle`, `fyber`, `inmobi`, `unity3d`, `ironsource`, `digitalturbine`, `tiktok` 作为 grep 关键字，定位 Manifest 注册项 + .so 文件名 + assets 子目录。
   - 绝大多数类名在 jadx 输出中混淆（`A, B, A0, ...`），正常——不影响 manifest/smali/so 层处理。
5. **发布者 fork**：CooYoGameActivity（CooyoStudio）、VantageGameActivity、RoboVM 自定义——快速过即可，重点在 manifest。

## 5. 动态分析重点

- `adb logcat -s AndroidRuntime System.err GLSurfaceView` —— 启动崩溃多见 ANR / ClassNotFound。
- `adb shell dumpsys window | grep mCurrentFocus` —— 确认 Activity 名称。
- `adb shell pm list packages | grep cooyostudio` —— 验证安装。
- 飞行模式验证：在移除全部网络 SDK / 桩化后，关网启动 → 验证游戏不联网也能进入主玩法。

## 6. 已知 APK 示例

- **JungleMarbleBlast**（com.cooyostudio.marble.blast）3.8.0，2026-08-06 —— 首个 libGDX 项目。
  - 引擎：libGDX 1.x（CooYoStudio fork 自定义 `CooYoGameActivity`）。
  - 入口：`com.cooyostudio.marble.blast.MBApplication` + `com.cooyostudio.marble.blast.GameActivity`。
  - 发行商：CooyoStudio（coolstudios/marblelab 系列），典型「小厂出海 + 多广告聚合」。
  - 加固：Pangle PGL 部分 DEX 加密（libpglarmor.so），但游戏入口类未加密。
  - SDK：8+ 广告 SDK + Firebase Analytics + Facebook Analytics + 推送。
  - 内购：41 个商品 mb_buyitem* / mb_giftitem* / mb_christitem* / mb_supersale* 等，定价 $0.99–$79.99。
