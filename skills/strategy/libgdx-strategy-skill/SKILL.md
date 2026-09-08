---
name: libgdx-strategy-skill
description: 处理 libGDX 引擎 APK 的专用逆向策略。libGDX 以 libgdx.so + com/badlogic/gdx/ Java 框架 + AndroidApplication/Activity 入口为特征；游戏逻辑在 classes.dex（Java 字节码），资源以 .atlas/.pack/.ttf 等明文打包到 assets/，部分发行方会做 assets 哈希加密。详见 STRATEGY.md §1.2 类型表 "libgdx" 行 + §4.4 新建流程。
when_to_use: 当 stage-00 嗅探判定 lib/<abi>/libgdx.so 存在 + jadx 输出含 com.badlogic.gdx.* 类，或可执行入口继承 AndroidApplication/AndroidFragmentApplication 时调用。
---

# libGDX 引擎逆向策略

> 处理 **libGDX 引擎** Android 游戏的专用工作流。游戏逻辑在 Java 字节码（classes.dex），
> 渲染走 OpenGL ES 2.0/3.0（通过 libgdx.so 调用 EGL/GLES），资源以 libGDX 专属格式
>（`.atlas` 纹理集 / `.pack` 二进制 PVR / `.tmx` 地图 / `.fnt` 位图字体 / `.ogg` 音频）打包到 `assets/`。
>
> **本 skill 遵循「引擎类型 ↔ 策略 skill 一对一」硬规则（AGENTS.md §1.12）**：
> libGDX 不应降级到 `android` 兜底，一律路由到本 skill。

---

## 0. Skill 目录结构

```
skills/strategy/libgdx-strategy-skill/
├── SKILL.md              ← 本文件
├── strategy.md           ← 识别特征 / 工具链 / 坑位
├── workflow.md           ← 阶段流程（命令 + 验证）
├── tools-index.md        ← 工具与脚本索引
├── ../../common/feature-removal-strategy-skill/SKILL.md  ← 通用去功能点清单（独立文档）
├── scripts/
│   ├── workflow/         ← 阶段专用脚本（命名 stage-<NN>-*.py）
│   └── common/           ← 通用脚本（命名 <verb>-<scope>.py）
└── assets/               ← 资源（已知项目列表 / 模板）
```

## 1. 加载顺序

1. **[SKILL.md](./SKILL.md)**（本文件）—— 总览 + 何时调用
2. **[strategy.md](./strategy.md)** —— 类型策略详述
3. **[workflow.md](./workflow.md)** —— 阶段流程 + 验证
4. **[tools-index.md](./tools-index.md)** —— 工具与脚本索引
5. **[EXPERIENCES.md](../../EXPERIENCES.md)** —— 经验沉淀
[../../common/feature-removal-strategy-skill/SKILL.md](../../common/feature-removal-strategy-skill/SKILL.md) — 通用去功能点清单

## 2. 何时调用

| 信号 | 检测方式 |
|------|---------|
| `lib/<abi>/libgdx.so` 存在 | `unzip -l <apk> \| grep libgdx.so` |
| jadx 输出含 `com/badlogic/gdx/**` | 在 jadx/sources/ 下确认 |
| 入口继承 `AndroidApplication` / `AndroidFragmentApplication` 或自定义 `*GameActivity` extends 同上 | jadx |
| `com/badlogic/gdx/utils/lsans-15.fnt` 之类资源 + `*.png` 字体贴图打包进 dex 或 `assets/` | unzip + strings |

## 3. 默认策略（阶段序列）

```
00 → 00a → 01 → 02 → 03 → 04 → 05 → 09 → 11 → 12 → 13 → 15
```

**与 android 兜底的关键差异**：
- **游戏逻辑 = 标准 Java 字节码**：脱壳后的 classes*.dex 用 jadx 直接可读；游戏代码混淆后多以单字母类名（A, B, A0, A1...）呈现，**不要尝试「反混淆」**，应通过 manifest 入口 `MBApplication` / `GameActivity` 反查业务类引用，按运行时行为定位 hook 点。
- **资源以 libGDX 格式打包到 assets/**：纹理集（`.atlas` + `.png`）、位图字体（`.fnt` + `.png`）、二进制包（`.pack`）、地图（`.tmx`）。明文，未加密。
- **发行方常见二次加密**：assets 顶层出现大量 hash 命名文件（`assets/000F73AF0FA36C6A6DCD1D2CDF5803FA` 等）——这是发行方对图像/音频的二次加密，Pangle `libpglarmor.so` 的 `PglCryptUtils` 提供解密，详见 strategy.md §3.2。
- **加固多是 PGL（Bytedance）**：dex 部分加密，**游戏入口类仍可在未加固的 dex 中读出**（manifest 类名直引）。物理删除 SDK smali 时必须先确认 JNI 回调链。
- **汉化两条路径**（按游戏实现）：
  - **A. 主流程在 Java 层用 Typeface**：用「`assets/<font>.ttf` 替换 + 路径不变」即可（libGDX 字体加载走 `AssetManager`）。
  - **B. 主流程在 .fnt 位图字体**：需要替换 atlas 贴图 + .fnt 引用——通常太重，不推荐。
  - 详见 strategy.md §4。

## 4. 验收清单

| 阶段 | 关键产物 | 验证命令 |
|------|---------|---------|
| 00 | 类型=libgdx | `unzip -l` 命中 `libgdx.so` + `com/badlogic/gdx/` |
| 00a | 难度评级 | `difficulty.json` 生成 |
| 03 | 入口定位 | jadx 看到 `GameActivity` → `super` → `AndroidApplication` 或 `*GameActivity` |
| 09 | manifest SDK 清理 | `grep -ci "applovin\|firebase\|mbridge" AndroidManifest.xml` = 0 |
| 11 | 重打包签名 | `apksigner verify patched.apk` 通过 |
| 12 | 运行时验证 | `adb logcat` 无 FATAL；启动后 5s 进入主菜单 |
| 13 | 飞行模式回归 | 关网后启动 + 进入玩法 |
| 15 | 汉化（若 A 路径） | OCR 主流程页面命中至少一处中文字符串 |

## 5. 已知项目

- **JungleMarbleBlast**（com.cooyostudio.marble.blast）2026-08-06 —— 首个 libGDX 项目，定义本 skill 基线。见 EXPERIENCES.md。

## 去第三方 SDK 统一参考

实现要点见 [去第三方 SDK：libgdx](../../common/third-party-removal-strategy-skill/references/engine-notes.md#libgdx)；处理、产物与验收见 [03/04 共用要求](../../common/third-party-removal-strategy-skill/references/stage-contract.md)。

执行由当前 type 注册表路由；保留必要引擎依赖，检查最终构建与真机证据后记录状态。

