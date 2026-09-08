# 01 项目概览

## 基本信息

| 字段 | 值 |
|------|----|
| 仓库 | `LuigiVampa92/xapk-to-apk` |
| 项目类型 | 独立 CLI 工具 |
| 主文件 | `xapktoapk.py`（单文件，623 行） |
| 语言 | Python 3 |
| Python 第三方依赖 | **无**（仅标准库：`json / os / platform / shutil / sys / zipfile / subprocess`） |
| 运行时外部依赖 | `apktool`、`zipalign`、`apksigner`（必须存在于 `$PATH`） |
| 平台 | 跨平台（Windows / macOS / Linux） |
| 入口 | `python xapktoapk.py PATH_TO_FILE.xapk` |

## 文件清单

```
xapk-to-apk/
├── .gitignore                                  # Python 忽略规则
├── LICENSE.md                                  # 许可证
├── README.md                                   # 使用说明（中文/英文混排，46 行）
├── xapktoapk.py                                # 主脚本（623 行）
└── xapktoapk.sign.properties.example           # 签名配置示例（12 行）
```

无 `requirements.txt`、无 `setup.py`、无测试目录 —— 这是个刻意保持极简的工具。

## 与 Android App Bundle 的关系

- **App Bundle（.aab）**：Google Play 上传的格式；服务端按设备维度（ABI / DPI / 语言）生成多个 **split APK**，最终用户下载的是一个跟设备匹配的瘦 APK
- **XAPK**：APKPure 等第三方分发渠道把 split APK + 公共资源打包成单一 zip，方便侧载。结构上是 `manifest.json` + 多个 split APK
- **APK**：传统 fat APK，包含全部 ABI / DPI / 资源，能在任何设备上跑

本工具做的事就是把 XAPK 的 split 包合并成传统 fat APK，**绕过 Google Play 的 split 分发**，常用于调试、离线分发、模拟器安装、CR 工具分析。

## 主要使用场景

| 场景 | 价值 |
|------|------|
| 老设备 / 模拟器无法识别 split APK | 合并成 fat APK 即可安装 |
| 离线分析 | IL2CPP / assetstudio 等工具需要单 APK 输入 |
| 修改后再分发 | 重新签名后可侧载 |
| 二次打包研究 | 看 split 是怎么拆的 |

## 与 `bundletool` 的对比

Google 官方 `bundletool` 也能 build universal APK，但需要 aab 输入 + Java + 复杂命令链。本工具：
- ✓ 输入 `.xapk`（不是 aab）
- ✓ Python 脚本，零依赖
- ✓ 单命令出 APK
- ✗ 不支持 .aab
- ✗ 不支持 Play Asset Delivery 的 stream-based 资产

## 约束 / 已知局限（基于源码）

| 约束 | 来源 |
|------|------|
| 不支持 Play Asset Delivery（asset pack 用 stream 方式分发的） | 代码仅处理 `assets/assetpack/` 目录型资产（行 274-310） |
| 不处理资源冲突（重复 res/ 资源仅跳过） | `merge_apk_resources` 显式 `continue`（行 263-265） |
| Locale 与 DPI 分片共享 `merge_apk_resources` 函数 | 行 605-608，未区分 |
| Windows 下调用 apktool / apksigner 用 `cmd /c` 的 `.bat` 包装 | 行 107-113, 322-326 |
| 临时目录 `.xapktoapk` 在 Windows 上设置 `attrib +h` | 行 96-97 |
| 修改 manifest 是字符串硬编码替换 | `update_main_manifest_file`（行 410-431） |