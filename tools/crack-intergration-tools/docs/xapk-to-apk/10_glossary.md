# 10 术语表

| 术语 | 解释 |
|------|------|
| **XAPK** | APKPure 等第三方分发渠道使用的包格式。本质是 zip，内含一个 `manifest.json` + 多个 split APK + 公共资源。Google Play 不直接生成 xapk，是分包平台自行打包的结果。 |
| **App Bundle (AAB)** | Google Play 上传的官方包格式。Play 商店在分发时按设备维度（ABI / DPI / 语言）动态生成多个 split APK。 |
| **Split APK** | App Bundle 分发时的单个分包。可以按 ABI（架构）、DPI（屏幕密度）、locale（语言）拆分，每个 split 只包含该维度的特定资源。 |
| **Main APK** | split 分包中一定存在的、包含公共代码和资源的基础 APK。其文件名通常是 `<package_name>.apk` 或 `base.apk`。 |
| **apktool** | 第三方 APK 反编译/重打包工具（https://github.com/iBotPeaches/Apktool）。把 APK 的 dex 反编译成 smali、把 resources.arsc / AndroidManifest.xml 解码成可读文本。脚本中作为 blackbox 使用。 |
| **zipalign** | Android 官方工具，4 字节对齐 zip 条目偏移，提升运行时 mmap 效率。 |
| **apksigner** | Android 官方工具，对齐后的 APK 做 V1/V2/V3 签名。 |
| **STAMP_TYPE_DISTRIBUTION_APK** | App Bundle 中的标记值，表示当前 APK 是为分发优化的 split 包。重打包为 fat APK 时需改为 `STAMP_TYPE_STANDALONE_APK`。 |
| **isSplitRequired** | AndroidManifest 中的属性，标识 APK 是否要求 split 分发模式。合并后应去除。 |
| **requiredSplitTypes** | AndroidManifest 中声明当前 APK 依赖哪些 split 类型（如 `base__abi, base__density`）。合并后应去除。 |
| **splitTypes** | 标识当前 APK 包含的 split 类型。 |
| **doNotCompress** | apktool.yml 中声明不需要以 deflate 压缩的文件类型列表。合并时需要把分片的列表合并到 main 的列表中。 |
| **lib/** | APK 中的 native 库目录，按 ABI 分目录（`arm64-v8a/`、`armeabi-v7a/`、`x86/` 等）。apktool 解包后保留此结构。 |
| **res/** | APK 中的编译后资源目录（drawable、values、layout 等）。 |
| **assets/** | APK 中的原始资源目录，开发者可自由组织结构。`assets/assetpack/` 是 Play Asset Delivery 的目录型资产。 |
| **apktool.yml** | apktool 反编译后生成的元数据文件，记录版本、压缩选项等信息。重打包时被 apktool 读取。 |
| **stamp-cert-sha256** | apktool 在反编译时可能生成的文件，记录原始 APK 的签名证书 sha256。脚本中已注释掉删除逻辑（新版本 apktool 不再生成）。 |
| **BNDLTOOL.RSA / .SF / MANIFEST.MF** | META-INF 下的签名文件。重新打包时必须删除，否则 apksigner 签名会失败。 |
| **Android Vending Splits** | Google Play 用于识别 split APK 的 meta-data。合并为 fat APK 时需移除。 |
| **Firebase Messaging default_notification_icon** | 部分 xapk 中包含的 FCM 默认通知图标 meta-data，重打包时可移除（默认值为 `@null`，不影响功能）。 |
| **values/public.xml** | APK 资源索引文件，多个 split 都有此文件但内容不同，合并时必须跳过以避免冲突。 |
| **drawable/** | res 下的可绘制资源目录。多 split 的 drawable 可能冲突，脚本当前策略是**第一个出现的 drawable 胜出**，不覆盖。 |
| **debug.keystore** | Android SDK 自带的调试签名证书（密码 `android`，别名 `androiddebugkey`），脚本示例配置使用它签名。 |
| **list2cmdline** | Python `subprocess` 模块的工具，把 argv 列表转成 Windows 命令行的字符串形式（含引号转义）。 |
| **DEVNULL** | Python 3.3+ 的 `subprocess.DEVNULL` 常量，旧版本需要 fallback。脚本行 12-16 做了兼容处理。 |
| **Python 脚本入口** | `if __name__ == '__main__': main()`（行 622-623）。允许 `python xapktoapk.py` 或 `import` 两种使用方式。 |

## 缩写速查

| 缩写 | 全称 |
|------|------|
| FCM | Firebase Cloud Messaging |
| APK | Android Package |
| AAB | Android App Bundle |
| ABI | Application Binary Interface |
| DPI | Dots Per Inch |
| RC | Return Code |
| cwd | Current Working Directory |
| PSP | Path Separator |
| PKG | Package name |