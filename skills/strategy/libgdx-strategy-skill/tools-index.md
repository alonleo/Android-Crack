# libGDX 引擎工具与脚本索引

## 工具

| 工具 | 用途 | 路径 |
|------|------|------|
| apktool 2.11.1 | 解包/重打包 | `$APKTOOL` |
| jadx | Java 反编译 | `$JADX` |
| adb | 真机验证 | `$ADB_BIN` |
| apksigner / zipalign | 签名/对齐 | `$APKSIGNER` / `$ZIPALIGN` |
| strings / readelf | .so 引擎判定 | 系统 binutils |
| keytool | keystore 生成 | `$KEYTOOL` |

## 脚本

> **libGDX 阶段脚本优先复用跨 type 通用脚本**（位于 `skills/common/general-strategy-skill/scripts/workflow/`）：
> `sub-stage-sniff.py` / `sub-stage-assess.py` / `sub-stage-preprocess.py` / `sub-stage-static-analyze.py` / `sub-stage-entry-points.py` / `sub-stage-strings.py` / `sub-stage-repack-sign.py` / `sub-stage-runtime-verify.py` / `sub-stage-final-check.py`。

### workflow/（libGDX 专用）

| 脚本 | 阶段 | 角色 |
|------|------|------|
| `sub-stage-libgdx-cleanup.py` | 09 | libGDX 专用 SDK 清理：manifest 清理（provider/activity/service/receiver/meta-data）+ 广告 .so 删除 + FB/Firebase/ThinkingData 桩化链（启动崩溃修复） |

> 首个 libGDX 项目（JungleMarbleBlast 2026-08-06）跑通并固化。

### common/（libGDX 通用辅助）

| 脚本 | 角色 |
|------|------|
| （占位）clean-libgdx-sdk-templates.py | 移除 assets/{template,adimages,audience_network}（Pangle 模板 + AppLovin AN 动态 dex） |
| （占位）inspect-libgdx-atlas.py | 解析 .atlas 文本 → 列出 textures/page，打印 PNG 路径 |

### assets/

| 文件 | 角色 |
|------|------|
| `known-libgdx-apks.md` | 已知 libGDX APK 清单（包名 / Activity / SDK 数量） |
| `libgdx-ttf-replace.md` | libGDX TTF 替换 SOP 速查 |
| `frida-hook-assets.js` | Frida hook `AssetManager.open` 探测游戏运行时加载的 assets（区分核心资源 vs 广告资源） |
| `frida-hook-font.js` | Frida hook `Typeface.createFromAsset` 探测游戏字体文件名（汉化评估） |

## 阶段脚本复用

libGDX 采用 android 型阶段序列，直接复用 general-strategy-skill 的跨 type 脚本。
本 skill 现阶段只新增少量专用脚本（hash 模板池清理 + atlas 解析）即可。

## 通用去功能点清单

| 文档 | 角色 |
|------|------|
| `../../common/feature-removal-strategy-skill/SKILL.md` | 去功能点统一参考（必须去除的按钮 + 实现方案 + 真机验收项） |

